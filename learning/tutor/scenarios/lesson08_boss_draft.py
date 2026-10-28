"""Closed standalone blind-hole boss: programmatically built, GUI observed and saved.

No hardware has been chosen; this is not a pilot-hole recommendation, a
print/fit/strength result, or a boss joined to the existing reference box.
"""
import json, math
from pathlib import Path
import bmesh
import bpy
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'

def build(g):
    k=Kit(g);out=Path(g['OUT']); snapshot=out/'source-snapshot';snapshot.mkdir()
    snapshots=[]
    for rel in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_boss_draft.py'):
        dst=snapshot/Path(rel).name;dst.write_bytes((PROJECT/rel).read_bytes())
        snapshots.append({'source':rel,'snapshot':dst.name,'sha256':g['sha256'](dst)})
    (snapshot/'manifest.json').write_text(json.dumps(snapshots,indent=2),encoding='utf-8')
    if g['sha256'](SOURCE)!=SOURCE_HASH:raise RuntimeError('reference SHA mismatch')
    copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](copy)!=SOURCE_HASH:raise RuntimeError('source copy differs')
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.5)
    def make_boss():
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
        scene.unit_settings.length_unit='MILLIMETERS';bpy.data.objects['Body_Reference'].hide_set(True)
        n=32
        ring=lambda radius,z:[(radius*math.cos(2*math.pi*i/n),radius*math.sin(2*math.pi*i/n),z) for i in range(n)]
        verts=ring(4,0)+ring(4,8)+ring(2,8)+ring(2,1)
        def side(a,b):return [(a+i,a+(i+1)%n,b+(i+1)%n,b+i) for i in range(n)]
        faces=[tuple(reversed(tuple(range(n))))]+side(0,n)+side(n,2*n)+side(2*n,3*n)+[tuple(range(3*n,4*n))]
        mesh=bpy.data.meshes.new('Boss_Blind_Polygon32_Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('Boss_Blind_Polygon32',mesh);scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.context.view_layer.update()
    def verify(label):
        obj=bpy.data.objects['Boss_Blind_Polygon32'];dg=bpy.context.evaluated_depsgraph_get()
        ev=obj.evaluated_get(dg);mesh=ev.to_mesh();pts=[ev.matrix_world@v.co for v in mesh.vertices]
        bm=bmesh.new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
        outer=pts[:64];inner=pts[64:]
        bounds=lambda a,i:[min(v[i] for v in a),max(v[i] for v in a)]
        result={'label':label,'outerBounds':[bounds(outer,i) for i in range(3)],
                'holeBounds':[bounds(inner,i) for i in range(3)],'vertices':len(pts),
                'faces':len(mesh.polygons),'nonManifoldEdges':nonmanifold,'signedVolumeMm3':vol,
                'segments':32,'outerVertexDiameterMm':8,'holeVertexDiameterMm':4,
                'outerFlatToFlatMm':8*math.cos(math.pi/32),
                'holeFlatToFlatMm':4*math.cos(math.pi/32),'bottomMm':1,'holeDepthMm':7,
                'mechanicalHardware':None,'physicalFit':None,'qualifiedHoleDiameter':None,
                'sourceSceneSha256':SOURCE_HASH,'standaloneNotJoinedToBox':True}
        expectedVolume=16*math.sin(math.pi/16)*(16*8-4*7)
        close=lambda a,b:math.isclose(a,b,abs_tol=1e-4)
        checks={'outerBounds':all(close(x,y) for row,expect in zip(result['outerBounds'],[[-4,4],[-4,4],[0,8]]) for x,y in zip(row,expect)),
                'holeBounds':all(close(x,y) for row,expect in zip(result['holeBounds'],[[-2,2],[-2,2],[1,8]]) for x,y in zip(row,expect)),
                'closed':nonmanifold==0,'positiveVolume':vol>0,
                'polygonVolume':abs(vol-expectedVolume)<abs(expectedVolume)*1e-5,
                'sourceReferenceExists':bpy.data.objects.get('Body_Reference') is not None,
                'separateNotJoined':len([o for o in bpy.context.scene.objects if o.type=='MESH'])==2}
        result['checks']=checks;ev.to_mesh_clear()
        (out/(label+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
        if not all(checks.values()):raise RuntimeError('Boss geometry mismatch: '+json.dumps(checks))
        return result
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3)
    k.do(make_boss,1)
    send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET')
    send('NUMPAD_7');send('NUMPAD_2');send('NUMPAD_2');send('NUMPAD_6');k.wheel_out(2)
    k.record('08-04','boss-draft','程式建立獨立盲孔柱草案，Blender實際視圖觀察；沒有選擇五金規格',lambda:verify('before-save'))
    k.file_dialog(163,k.demo_dir,'u08_blind_boss_draft_v001.blend');k.confirm_dialog(wait=2)
    k.record('08-04','saved','另存盲孔柱草案 v001；保持原盒獨立且隱藏',lambda:verify('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u08_blind_boss_draft_v001.blend');k.confirm_dialog(wait=3)
    k.record('08-04','reopened','重新開啟並核對外徑、孔徑、盲底與封閉網格',lambda:verify('reopened'))
