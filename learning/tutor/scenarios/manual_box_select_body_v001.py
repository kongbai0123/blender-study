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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/demo-files/manual_drivers_box_60x40_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_box_select_body_v001.py']:
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
    k.record('EDIT','opened','開啟固定尺寸盒體的獨立副本，確認原始幾何',lambda:state('opened'))
    k.do(lambda:k.move(785,510),.4);k.do(lambda:k.click(785,510),1)
    k.record('EDIT','select-body','以 viewport 可見的盒體側面選取 Body；讀回活動物件',lambda:state('select-body'))
    def require_body():
        d=state('select-check')
        if d['active']!='Body':raise RuntimeError('Outliner did not select Body; got '+str(d['active']))
    k.do(require_body,.2)
    k.do(lambda:k.click(702,448,button='RIGHTMOUSE'),1)
    k.record('EDIT','context-menu','右鍵查看盒體的草圖清單',lambda:state('context-menu'))
    k.do(lambda:k.click(800,446),1.5)
    k.record('EDIT','body-sketch','選取 Body Sketch 進入外框草圖',lambda:state('body-sketch'))
    def ensure_sidebar():
        a=k.area('VIEW_3D')
        if not a.spaces.active.show_region_ui:k.key('N',x=600,y=450)
    k.do(ensure_sidebar,.8)
    def require_body_sketch():
        v=state('preedit-check')
        if v['activeSketch']!='Body Sketch':raise RuntimeError('Body Sketch was not entered')
        if len(v['drivers'])!=1 or not v['drivers'][0]['isValid']:raise RuntimeError('X driver unavailable')
    k.do(require_body_sketch,.2)
    k.record('EDIT','sidebar','觀察外框尺寸約束欄位位置',lambda:state('sidebar'))
    def field(y,value):
        k.do(lambda:k.click(1124,y,ctrl=True),.5)
        k.do(lambda:k.key('A',ctrl=True),.2)
        k.do(lambda:k.type_text(str(value)+'mm'),.3)
        k.do(lambda:k.key('RET'),1.5)
    field(641,70)
    k.record('EDIT','x70','將外框長度改為 70 mm；量測內腔是否隨動',lambda:state('x70'))
    k.file_dialog(163,k.demo_dir,'x_driver_resize_probe_v001.blend');k.confirm_dialog(wait=2)
    k.record('EDIT','saved','另存 X 改變的獨立試驗副本，實際尺寸以讀值為準',lambda:state('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'x_driver_resize_probe_v001.blend');k.confirm_dialog(wait=4)
    k.record('EDIT','reopened','重開試驗副本，量測外框及內腔並檢查驅動器',lambda:state('reopened'))
