"""Demonstrate a Screw modifier on an explicitly open, non-printable thread surface.

The three-vertex input contour and scene visibility are programmatic setup;
modifier creation is requested through the native F3 search UI.
"""
import json
import math
from pathlib import Path
import bpy
import bmesh
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'

def build(g):
    k=Kit(g);out=Path(g['OUT']); snapshot=out/'source-snapshot';snapshot.mkdir()
    files=[]
    for rel in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_screw_trial.py'):
        p=snapshot/Path(rel).name;p.write_bytes((PROJECT/rel).read_bytes())
        files.append({'source':rel,'snapshot':p.name,'sha256':g['sha256'](p)})
    (snapshot/'manifest.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
    if g['sha256'](SOURCE)!=SOURCE_HASH: raise RuntimeError('reference scene hash differs')
    source_copy=Path(k.demo_dir)/SOURCE.name;source_copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](source_copy)!=SOURCE_HASH: raise RuntimeError('reference copy differs')
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.5)
    def read():
        obj=bpy.data.objects.get('Thread_Profile')
        if obj is None:return {'profile':None}
        data={'sourceVertices':[list(v.co) for v in obj.data.vertices], 'sourceEdges':len(obj.data.edges),
              'modifiers':[{'name':m.name,'type':m.type,'angle':m.angle,'screwOffset':m.screw_offset,
                            'iterations':m.iterations,'steps':m.steps,'renderSteps':m.render_steps,
                            'axis':m.axis,'useObjectScrewOffset':m.use_object_screw_offset,
                            'useMergeVertices':m.use_merge_vertices} for m in obj.modifiers if m.type=='SCREW']}
        (out/'latest-readback.json').write_text(json.dumps(data,indent=2),encoding='utf-8');return data
    def prepare():
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
        scene.unit_settings.length_unit='MILLIMETERS'
        bpy.data.objects['Body_Reference'].hide_set(True)
        mesh=bpy.data.meshes.new('Open_Profile_Mesh')
        mesh.from_pydata([(5,0,0),(6,0,.3),(5,0,.6)],[(0,1),(1,2)],[])
        obj=bpy.data.objects.new('Thread_Profile',mesh);scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.context.view_layer.update()
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3)
    k.do(prepare,1)
    k.record('08-02','profile','程式建立半徑 5→6→5 mm、軸向 0→0.3→0.6 mm 的開放牙型線；隱藏原盒（不是 GUI 建模）',read)
    send('F3');k.do(lambda:k.type_text('Add Screw Modifier'),.5);send('RET')
    k.do(lambda:k.click(1246,k.props_y(300)),.8)
    k.record('08-02','screw-added','F3 搜尋 Add Screw Modifier，讀回預設的實際修改器設定',read)
    def edit_field(x,y,text):
        k.do(lambda:k.click(x,y,ctrl=True),.4)
        k.do(lambda:k.key('A',ctrl=True),.2)
        k.do(lambda:k.type_text(text),.4)
        k.do(lambda:k.key('RET'),.8)
    edit_field(1400,372,'1mm')
    k.record('08-02','lead-one','修改器 Screw 欄位輸入 1 mm；Angle 為 360°、Object Screw 關閉',read)
    edit_field(1400,393,'4')
    k.record('08-02','four-iterations','Iterations 輸入 4，這是重複圈數而非線數',read)
    edit_field(1400,510,'32')
    edit_field(1400,530,'32')
    k.record('08-02','resolution','Viewport 與 Render Steps 各輸入 32',read)
    send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET')
    send('NUMPAD_2');send('NUMPAD_2')
    def verify(label):
        obj=bpy.data.objects['Thread_Profile'];screw=next(m for m in obj.modifiers if m.type=='SCREW')
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        points=[evaluated.matrix_world@v.co for v in mesh.vertices]
        radii=[math.hypot(v.x,v.y) for v in points];zs=[v.z for v in points]
        bm=bmesh.new();bm.from_mesh(mesh)
        boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
        bm.free()
        phase=sorted(v.z for v in points if abs(v.y)<1e-4 and abs(v.x-6)<1e-4)
        result={'label':label,'settings':read()['modifiers'][0],
                'evaluated':{'vertices':len(points),'edges':len(mesh.edges),'faces':len(mesh.polygons),
                             'radiusMinMaxMm':[min(radii),max(radii)],'zMinMaxMm':[min(zs),max(zs)],
                             'positiveXOuterPhaseZMm':phase,'boundaryEdges':boundary,'nonManifoldEdges':nonmanifold},
                'semantic':{'demonstrationOnly':True,'claimsISO':False,'starts':1,'singleProfile':True,
                            'angleDegrees':360,'screwDisplacementPerRotationMm':1,
                            'leadMm':1,'pitchMm':1,'iterationsIsStarts':False,
                            'revolutionTravelMm':4,'profileHeightMm':.6,'overallZSpanMm':4.6,
                            'effectiveEngagementMm':None,'isWatertight':False,
                            'printed':False,'fitTested':False,'qualifiedClearanceMm':None},
                'sourceSceneSha256':SOURCE_HASH}
        checks={'angle360':math.isclose(screw.angle,2*math.pi,abs_tol=1e-5),
                'offset1':math.isclose(screw.screw_offset,1,abs_tol=1e-5),
                'iterations4':screw.iterations==4,'axisZ':screw.axis=='Z',
                'objectScrewOff':not screw.use_object_screw_offset,
                'resolution32':screw.steps==32 and screw.render_steps==32,
                'radii5to6':math.isclose(min(radii),5,abs_tol=1e-4) and math.isclose(max(radii),6,abs_tol=1e-4),
                'zSpan':math.isclose(min(zs),0,abs_tol=1e-4) and math.isclose(max(zs),4.6,abs_tol=1e-4),
                'fourTurnsPhase':len(phase)==5 and all(math.isclose(a,b,abs_tol=1e-4) for a,b in zip(phase,[.3,1.3,2.3,3.3,4.3])),
                'isOpen':boundary>0 and nonmanifold>0}
        result['checks']=checks;evaluated.to_mesh_clear()
        (out/(label+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
        if not all(checks.values()):raise RuntimeError('Screw geometry mismatch: '+json.dumps(checks))
        return result
    k.record('08-02','surface-verified','顯示非標準單線螺旋牙型曲面並讀值；開放邊界故不可作可列印閉殼',lambda:verify('screw-surface'))
    k.file_dialog(163,k.demo_dir,'u08_screw_surface_v001.blend')
    k.confirm_dialog(wait=2)
    k.record('08-02','saved','另存螺旋曲面示範 v001，不覆寫盒體或參照檔',lambda:verify('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u08_screw_surface_v001.blend');k.confirm_dialog(wait=3)
    k.record('08-02','reopened','重新開啟 v001 並核對修改器與曲面實際結果',lambda:verify('reopened'))
