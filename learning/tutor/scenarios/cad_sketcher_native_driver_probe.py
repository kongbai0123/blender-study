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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-saved-probe-v001/demo-files/manual_fixed_box_60x40x30_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/cad_sketcher_native_driver_probe.py']:
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
        animation=bpy.context.scene.animation_data
        v['drivers']=[{'dataPath':f.data_path,'expression':f.driver.expression,'isValid':f.driver.is_valid,'variables':[{'name':x.name,'targets':[{'idType':t.id_type,'dataPath':t.data_path} for t in x.targets]} for x in f.driver.variables]} for f in animation.drivers] if animation else []
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
    k.record('EDIT','opened','開啟固定尺寸盒體的獨立副本，確認原始幾何',lambda:state('opened'))
    k.do(lambda:k.click(702,448,button='RIGHTMOUSE'),1)
    k.record('EDIT','context-menu','右鍵查看盒體的草圖清單',lambda:state('context-menu'))
    k.do(lambda:k.click(800,446),1.5)
    k.record('EDIT','body-sketch','選取 Body Sketch 進入外框草圖',lambda:state('body-sketch'))
    send('N')
    k.record('EDIT','sidebar','觀察外框尺寸約束欄位位置',lambda:state('sidebar'))
    k.do(lambda:k.click(1124,641,button='RIGHTMOUSE'),1)
    k.record('DRIVER','source-context','右鍵外框 60 mm 尺寸欄位，觀察 Blender 原生驅動器選項',lambda:state('source-context'))
    k.do(lambda:k.move(1030,868),.5);k.do(lambda:k.click(1030,868),.8)
    k.record('DRIVER','copy-source','點選 Copy as New Driver，將外框長度作為來源',lambda:state('copy-source'))
    k.do(lambda:k.move(1050,131),.5);k.do(lambda:k.click(1050,131),1)
    k.do(lambda:k.move(702,448),.4);k.do(lambda:k.click(702,448,button='RIGHTMOUSE'),1)
    k.record('DRIVER','select-cutter-menu','開啟盒體 Edit Sketch 清單',lambda:state('select-cutter-menu'))
    k.do(lambda:k.click(820,467),1)
    k.record('DRIVER','cutter-sketch','選擇內腔 Body.001 Sketch',lambda:state('cutter-sketch'))
    k.do(lambda:k.move(1125,641),.4);k.do(lambda:k.click(1125,641,button='RIGHTMOUSE'),1)
    k.record('DRIVER','target-context','在內腔 56 mm 尺寸右鍵，檢查能否貼上來源驅動器',lambda:state('target-context'))
    k.do(lambda:k.move(1002,687),.4);k.do(lambda:k.click(1002,687),1.2)
    k.record('DRIVER','pasted','貼上外框長度驅動器至內腔長度，讀回表達式與幾何；尚未扣除壁厚',lambda:state('pasted'))
    k.do(lambda:k.move(1125,641),.4);k.do(lambda:k.click(1125,641,button='RIGHTMOUSE'),1)
    k.record('DRIVER','edit-context','觀察內腔長度驅動器編輯選項',lambda:state('edit-context'))
    k.do(lambda:k.move(1003,682),.4);k.do(lambda:k.click(1003,682),1)
    k.record('DRIVER','edit-popup','開啟原生 Edit Driver，確認可編輯表達式',lambda:state('edit-popup'))
    k.do(lambda:k.move(965,683),.4);k.do(lambda:k.click(965,683),.8)
    k.record('DRIVER','type-menu','觀察驅動器 Type 選項',lambda:state('type-menu'))
    k.do(lambda:k.move(970,749),.4);k.do(lambda:k.click(970,749),.8)
    k.record('DRIVER','script-type','切換至 Scripted Expression，觀察輸入欄位',lambda:state('script-type'))
    k.type_into(970,705,'slvs_c_b596b36138076155-4')
    k.record('DRIVER','formula-attempt','嘗試輸入外框長度減 4 mm 的表達式；以讀回結果判斷',lambda:state('formula-attempt'))
