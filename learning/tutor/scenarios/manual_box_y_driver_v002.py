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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-manual-box-select-body-v002/demo-files/x_driver_resize_probe_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_box_y_driver_v002.py']:
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
        anim=bpy.context.scene.animation_data
        v['drivers']=[{'dataPath':f.data_path,'expression':f.driver.expression,'isValid':f.driver.is_valid} for f in anim.drivers] if anim else []
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
    def mc(x,y,button='LEFTMOUSE'):
        k.do(lambda:k.move(x,y),.4);k.do(lambda:k.click(x,y,button=button),.8)
    k.record('Y','opened','開啟已存 X70 驅動器副本',lambda:state('opened'))
    mc(1125,657,'RIGHTMOUSE')
    k.record('Y','source-menu','右鍵外框 Y40 欄位',lambda:state('source-menu'))
    mc(1030,884)
    k.record('Y','copied','複製 Y 來源驅動器',lambda:state('copied'))
    mc(1050,131)
    mc(785,510)
    mc(702,448,'RIGHTMOUSE')
    k.record('Y','sketch-menu','選取內腔草圖',lambda:state('sketch-menu'))
    mc(820,467)
    k.record('Y','inner-sketch','進入內腔草圖',lambda:state('inner-sketch'))
    def require_inner():
        d=state('inner-check')
        if d['activeSketch']!='Body.001 Sketch':raise RuntimeError('inner sketch missing')
    k.do(require_inner,.2)
    mc(1125,657,'RIGHTMOUSE')
    k.record('Y','target-menu','右鍵內腔 Y36 欄位',lambda:state('target-menu'))
    mc(1002,703)
    k.record('Y','pasted','貼上 Y 來源',lambda:state('pasted'))
    mc(1125,657,'RIGHTMOUSE')
    k.record('Y','edit-context','觀察 Y 驅動器選單',lambda:state('edit-context'))
    mc(1003,698)
    k.record('Y','edit-popup','開啟 Y 驅動器編輯視窗',lambda:state('edit-popup'))
    mc(965,683)
    k.record('Y','type-menu','開啟驅動器類型',lambda:state('type-menu'))
    mc(970,749)
    k.record('Y','script-type','設定 Scripted Expression',lambda:state('script-type'))
    k.type_into(970,705,'slvs_c_854e8777cfe2608d-4')
    k.record('Y','formula','輸入 Y 來源減4',lambda:state('formula'))
    mc(600,450)
    mc(1180,131)
    k.record('Y','solve','更新內腔草圖並讀回',lambda:state('solve'))
    k.file_dialog(163,k.demo_dir,'manual_box_xy_drivers_v001.blend');k.confirm_dialog(wait=3)
    k.record('Y','saved','另存實驗版；結果以實際讀值為準',lambda:state('saved'))
