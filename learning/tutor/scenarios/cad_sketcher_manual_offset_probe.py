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
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/cad_sketcher_manual_offset_probe.py']:
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
    k.record('OFFSET','opened-solid','開啟原生草圖與 Extrude 建出的 60×40×30 實心體副本',lambda:state('opened-solid'))
    send('N');k.wheel_out(2)
    send('A',ctrl=True,shift=True)
    k.do(lambda:k.click(17,65),.8)
    k.record('OFFSET','pick-workplane','Ctrl+Shift+A 開始選擇草圖工作平面',lambda:state('pick-workplane'))
    k.do(lambda:at_world((30,20,30),True),1.5)
    k.record('OFFSET','picked-top-face','在頂面點選工作平面（探測）',lambda:state('picked-top-face'))
    send('J')
    k.do(lambda:at_world((30,20,30),True),1.5)
    k.record('OFFSET','projected-face','J 投影頂面作為定位參考，檢查實際畫面',lambda:state('projected-face'))
    send('O')
    k.do(lambda:at_world((30,0,30),True),1)
    k.do(lambda:k.type_text('2'),.7);send('RET')
    k.record('OFFSET','offset-two','嘗試以 2 mm 偏移頂面邊界；精度與方向須驗證',lambda:state('offset-two'))
    send('A',ctrl=True,shift=True)
    k.record('OFFSET','left-inner-sketch','離開內部草圖並讀回實際狀態',lambda:state('left-inner-sketch'))
    send('E',ctrl=True,shift=True)
    k.record('OFFSET','extrude-tool','呼叫 Extrude 並觀察 Auto Boolean 狀態',lambda:state('extrude-tool'))
    k.do(lambda:k.type_text('-28'),.7);send('RET')
    k.record('OFFSET','after-cut','嘗試向下 28 形成內腔；結果須依讀值判定',lambda:state('after-cut'))
