"""Observe native CAD Sketcher Extrude UI on a previously drawn sketch.

This is a probe, not a completed box or lid. The input sketch was constructed
with native events in a previous independent run; the Python used here only
loads a copy, enables the extension, and inspects Blender state.
"""
import importlib
import json
import shutil
from pathlib import Path
import addon_utils
import bpy
from common import Kit, PROJECT


def build(g):
    k=Kit(g); out=Path(g['OUT'])
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/demo-files/manual_sketch_extrude_60x40x30_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/cad_sketcher_cavity_saved_probe.py']:
        p=folder/Path(rel).name;p.write_bytes((PROJECT/rel).read_bytes());snapshots.append({'source':rel,'snapshot':p.name,'sha256':g['sha256'](p)})
    (folder/'manifest.json').write_text(json.dumps(snapshots,indent=2),encoding='utf-8')
    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons: raise RuntimeError('addon unavailable')
    def send(key,**kw): k.do(lambda:k.key(key,x=600,y=450,**kw),.7)
    def state(label):
        ref=importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk=ref.get_active_sketch(bpy.context)
        dg=bpy.context.evaluated_depsgraph_get()
        items=[]
        for o in bpy.context.scene.objects:
            item={'name':o.name,'type':o.type,'hidden':o.hide_get(),'selected':o.select_get(),
                  'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]}
            if o.type in ('MESH','CURVES','CURVE'):
                try:
                    ev=o.evaluated_get(dg); mesh=ev.to_mesh()
                    points=[ev.matrix_world @ v.co for v in mesh.vertices]
                    item['evaluated']={'vertices':len(points),'faces':len(mesh.polygons),'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None}
                    ev.to_mesh_clear()
                except Exception as e: item['evaluationError']=str(e)
            items.append(item)
        v={'label':label,'mode':bpy.context.mode,'active':bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
           'activeSketch':sk.name if sk else None,'objects':items}
        if sk:
            obj=sk.target_object
            v['sketch']={'solver':sk.solver_state,'dof':sk.dof,'positions':[list(p.vector) for p in obj.data.attributes['position'].data] if 'position' in obj.data.attributes else [],'constraints':[{'type':c.type,'value':getattr(c,'value',None)} for c in sk.constraints.all]}
        (out/(label+'-state.json')).write_text(json.dumps(v,indent=2),encoding='utf-8');return v
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    from mathutils import Vector
    def at_world(co, click=False):
        a=k.area("VIEW_3D"); region=next(r for r in a.regions if r.type=="WINDOW")
        point=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(co))
        if point is None: raise RuntimeError("point projects behind camera")
        x,y=int(region.x+point.x),int(k.window().height-region.y-point.y)
        if not (region.x<x<region.x+region.width and k.window().height-(region.y+region.height)<y<k.window().height-region.y):
            raise RuntimeError("point outside viewport "+str((co,x,y)))
        (k.click if click else k.move)(x,y)
    k.setup();k.do(enable,2)
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,copied.name);k.confirm_dialog(wait=4)
    k.record('LINEDIM','opened-solid','開啟原生草圖與 Extrude 建出的 60×40×30 實心體副本',lambda:state('opened-solid'))
    send('N');k.wheel_out(2)
    send('A',ctrl=True,shift=True)
    k.do(lambda:k.click(17,65),.8)
    k.record('LINEDIM','pick-workplane','Ctrl+Shift+A 開始選擇草圖工作平面',lambda:state('pick-workplane'))
    k.do(lambda:at_world((30,20,30),True),1.5)
    k.record('LINEDIM','picked-top-face','在頂面點選工作平面（探測）',lambda:state('picked-top-face'))
    send('R')
    k.do(lambda:at_world((2,2,30),True),.7)
    k.do(lambda:at_world((58,38,30),True),.7);send('ESC')
    k.record('LINEDIM','rectangle','以兩點畫出近似內矩形，尺寸與位置尚未驗證',lambda:state('rectangle'))
    send('D')
    k.do(lambda:at_world((30,2,30),True),.6)
    k.do(lambda:at_world((30,-4,30)),.4)
    k.do(lambda:k.type_text('56'),.4);send('RET');send('ESC')
    k.record('LINEDIM','width','選內矩形水平邊，嘗試加 56 mm 長度約束',lambda:state('width'))
    send('D')
    k.do(lambda:at_world((58,20,30),True),.6)
    k.do(lambda:at_world((64,20,30)),.4)
    k.do(lambda:k.type_text('36'),.4);send('RET');send('ESC')
    k.record('LINEDIM','height','選內矩形垂直邊，嘗試加 36 mm 長度約束',lambda:state('height'))
    # The selected top-face workplane origin is world (30,20,30), confirmed by
    # its local (0,0) sketch point and center placement in the previous run.
    send('H',alt=True)
    k.do(lambda:at_world((1.861125946,2.138874054,30),True),.6)
    k.do(lambda:at_world((30,20,30),True),.6)
    k.do(lambda:at_world((20,10,30)),.4)
    k.do(lambda:k.type_text('28'),.4);send('RET');send('ESC')
    k.record('CENTER','horizontal','嘗試以矩形角點與頂面草圖原點建立 28 mm 水平定位',lambda:state('center-horizontal'))
    send('V',alt=True)
    k.do(lambda:at_world((1.861125946,2.138874054,30),True),.6)
    k.do(lambda:at_world((30,20,30),True),.6)
    k.do(lambda:at_world((20,10,30)),.4)
    k.do(lambda:k.type_text('18'),.4);send('RET');send('ESC')
    k.record('CENTER','vertical','嘗試以矩形角點與頂面草圖原點建立 18 mm 垂直定位',lambda:state('center-vertical'))
    send('A',ctrl=True,shift=True)
    k.record('LINEDIM','left-inner-sketch','離開內部草圖並讀回實際狀態',lambda:state('left-inner-sketch'))
    send('E',ctrl=True,shift=True)
    k.record('LINEDIM','extrude-tool','呼叫 Extrude 並觀察 Auto Boolean 狀態',lambda:state('extrude-tool'))
    k.do(lambda:k.type_text('-28'),.7);send('RET')
    k.record('LINEDIM','after-cut','嘗試向下 28 形成內腔；結果須依讀值判定',lambda:state('after-cut'))
    def assert_cavity(label):
        v=state(label)
        cutter=next(x for x in v['objects'] if x['name']=='Body.001')['evaluated']['bounds']
        if not all(abs(a-b)<1e-5 for pair,expect in zip(cutter,[[2,58],[2,38],[2,30]]) for a,b in zip(pair,expect)):
            raise RuntimeError('wrong cavity bounds: '+json.dumps(cutter))
    k.do(lambda:assert_cavity('pre-save-check'),.3)
    k.file_dialog(163,k.demo_dir,'manual_fixed_box_60x40x30_v001.blend');k.confirm_dialog(wait=2)
    k.record('SAVE','saved','另存固定尺寸箱體：內腔定位值尚未與外形連動',lambda:state('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'manual_fixed_box_60x40x30_v001.blend');k.confirm_dialog(wait=4)
    k.record('SAVE','reopened','重開示範副本，讀回幾何邊界',lambda:state('reopened'))
    k.do(lambda:assert_cavity('reopened-check'),.3)
    k.do(lambda:k.click(702,448,button='RIGHTMOUSE'),1)
    k.record('SAVE','context-menu','觀察盒體右鍵 Edit Sketch，準備檢查原始草圖',lambda:state('context-menu'))
