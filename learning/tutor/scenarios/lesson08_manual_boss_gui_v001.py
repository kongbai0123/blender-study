"""GUI-only standalone blind boss drafting from a cylinder; isolated source and output."""
import json, math
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import Kit, PARK, PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'
NAME='u08_manual_boss_gui_v001.blend'

def build(g):
    k=Kit(g);out=Path(g['OUT']);demo=Path(k.demo_dir);source=demo/SOURCE.name
    if g['sha256'](str(SOURCE))!=SOURCE_HASH:raise RuntimeError('來源 hash 不符')
    source.write_bytes(SOURCE.read_bytes())
    if g['sha256'](str(source))!=SOURCE_HASH:raise RuntimeError('副本 hash 不符')
    def do(fn, wait=.5):k.do(fn,wait)
    def key(name,**flags):k.key(name,x=600,y=475,**flags)
    def send(name,wait=.5,**flags):do(lambda:key(name,**flags),wait)
    def search(text):send('F3',.3);do(lambda:k.type_text(text),.4);send('RET',.8)
    def text(txt):do(lambda:k.type_text(txt),.35)
    def scene():
        o=bpy.context.view_layer.objects.active
        return {'active':o.name if o else None,'mode':bpy.context.mode,'unitScale':bpy.context.scene.unit_settings.scale_length,
                'dims':list(o.dimensions) if o else None,'scale':list(o.scale) if o else None,
                'location':list(o.location) if o else None}
    def check_obj(dims,scale=None,mode='OBJECT'):
        s=scene()
        if s['mode']!=mode or not s['active'] or any(abs(a-b)>1e-3 for a,b in zip(s['dims'],dims)):
            raise RuntimeError('場景狀態不符 '+str(s))
        if scale and any(abs(a-b)>1e-3 for a,b in zip(s['scale'],scale)):raise RuntimeError('Scale 不符 '+str(s))
    def selected_top():
        o=bpy.context.view_layer.objects.active;bm=bmesh.from_edit_mesh(o.data);sel=[f for f in bm.faces if f.select]
        s=scene();s['selectedFaces']=len(sel);s['faceCenterZ']=float((o.matrix_world@sel[0].calc_center_median()).z) if len(sel)==1 else None
        return s
    def check_top():
        s=selected_top()
        if s['selectedFaces']!=1 or abs(s['faceCenterZ']-8)>1e-4:raise RuntimeError('未選到頂面 '+str(s))
    def check_inset():
        o=bpy.context.view_layer.objects.active;bm=bmesh.from_edit_mesh(o.data);sel=[f for f in bm.faces if f.select]
        if len(sel)!=1:raise RuntimeError('內插後面選取數不符')
        pts=[o.matrix_world@v.co for v in sel[0].verts]
        bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
        (out/'inset-readback.json').write_text(json.dumps({'boundsMm':bounds,'vertices':len(pts)},indent=2)+'\n',encoding='utf8')
        if len(pts)!=32 or abs(bounds[0][1]-bounds[0][0]-4)>0.03:raise RuntimeError('內插的孔口尺寸與預期不符 '+str(bounds))
    def verify(label):
        o=bpy.context.view_layer.objects.active;dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);mesh=ev.to_mesh()
        bm=bmesh.new();bm.from_mesh(mesh);bm.transform(o.matrix_world);bm.verts.ensure_lookup_table();bm.verts.index_update()
        vertices=list(bm.verts);closed=sum(not e.is_manifold for e in bm.edges); volume=bm.calc_volume(signed=True)
        points=[v.co.copy() for v in vertices];bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
        tree=BVHTree.FromBMesh(bm); rays={}
        for name,x,expected in [('holeFloor',0,1),('bossTop',3,8),('outside',5,None)]:
            hit,normal,idx,dist=tree.ray_cast(Vector((x,0,20)),Vector((0,0,-1)),100)
            rays[name]={'x':x,'z':float(hit.z) if hit else None,'expectedZ':expected}
        result={'mode':bpy.context.mode,'boundsMm':bounds,'dimensionsMm':list(o.dimensions),'vertices':len(vertices),'faces':len(bm.faces),
                'nonManifoldEdges':closed,'signedVolumeMm3':volume,'rays':rays,'sourceSha256':SOURCE_HASH,
                'material':None,'hardware':None,'print':None,'fit':None,'qualifiedStrength':None}
        checks={'bounds':all(abs(a-b)<1e-3 for row,exp in zip(bounds,[[-4,4],[-4,4],[0,8]]) for a,b in zip(row,exp)),
                'closed':closed==0,'positiveVolume':volume>0,'holeFloor':rays['holeFloor']['z'] is not None and abs(rays['holeFloor']['z']-1)<1e-3,
                'bossTop':rays['bossTop']['z'] is not None and abs(rays['bossTop']['z']-8)<1e-3,'outside':rays['outside']['z'] is None}
        result['checks']=checks;bm.free();ev.to_mesh_clear()
        (out/(label+'-readback.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        if not all(checks.values()):raise RuntimeError('盲孔柱驗證失敗 '+str(result))
        return result
    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    send('O',1.2,ctrl=True);k.fill_dialog(k.demo_dir,source.name);k.confirm_dialog(wait=3)
    k.record('08-BOSS-GUI','source','開啟獨立原盒參照副本，材料及五金待定',scene,park=PARK)
    send('H',.5);search('Add Cylinder')
    k.record('08-BOSS-GUI','cylinder','隱藏原盒，F3 新增預設 32 邊圓柱',scene,park=PARK)
    do(lambda:check_obj((2,2,2)),.1)
    send('S',.2);text('4');send('RET',.6);search('Apply Scale')
    send('G',.2);send('Z',.2);text('4mm');send('RET',.5)
    k.record('08-BOSS-GUI','scaled','S 4，Apply Scale，G Z 4 mm：外框 8 × 8 × 8 mm',scene,park=PARK)
    do(lambda:check_obj((8,8,8),(1,1,1)),.1)
    search('Frame Selected');send('NUMPAD_7',.7)
    send('TAB',.5);send('THREE',.5);send('A',.2,alt=True);do(lambda:k.click(614,475),.8)
    k.record('08-BOSS-GUI','top-selected','頂視 Edit Mode 面選取，取消選取後點柱頂面',selected_top,park=PARK)
    do(check_top,.1)
    send('I',.2);text('2mm');send('RET',.6)
    k.record('08-BOSS-GUI','inset','柱頂 I 2 mm 內插出孔口草案',selected_top,park=PARK)
    do(check_inset,.1)
    send('E',.2);text('-7mm');send('RET',.8);send('TAB',.5)
    k.record('08-BOSS-GUI','blind-hole','內插面 E −7 mm 建立盲孔；數位讀回',lambda:verify('blind-hole'),park=PARK)
    k.file_dialog(163,k.demo_dir,NAME);k.confirm_dialog(wait=2)
    k.record('08-BOSS-GUI','saved','以新檔名另存 GUI 手工柱草案',lambda:verify('saved'),park=PARK)
    send('O',1.2,ctrl=True);k.fill_dialog(k.demo_dir,NAME);k.confirm_dialog(wait=3)
    k.record('08-BOSS-GUI','reopened','重開新版本並讀回孔底與外框',lambda:verify('reopened'),park=PARK)
