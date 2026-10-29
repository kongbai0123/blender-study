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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-manual-lid-driver-x-v006/demo-files/manual_lid_shape_x_driver_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_lid_driver_y_v001.py']:
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
    def skstate(label):
        data=state(label); ob=bpy.context.object
        keys=ob.data.shape_keys if ob and ob.type=='MESH' else None
        data['shapeKeys']=[{'name':x.name,'value':x.value,'min':x.slider_min,'max':x.slider_max} for x in keys.key_blocks] if keys else []
        data['activeKeyIndex']=ob.active_shape_key_index if ob and ob.type=='MESH' else None
        data['shapeDrivers']=[{'path':f.data_path,'expression':f.driver.expression,'valid':f.driver.is_valid,'variables':[{'name':v.name,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path} for t in v.targets]} for v in f.driver.variables]} for f in keys.animation_data.drivers] if keys and keys.animation_data else []
        (out/(label+'-state.json')).write_text(json.dumps(data,indent=2),encoding='utf-8');return data
    def search(text):
        send('F3');k.do(lambda:k.type_text(text),.3);send('RET')
    k.record('LINK','opened','開啟雙形狀鍵蓋板試驗',lambda:skstate('opened'))
    send('H',alt=True);send('A',alt=True);k.do(lambda:k.click(1320,95),1);send('H');k.do(lambda:k.click(700,550),1)
    k.record('LINK','body-selected','隱藏上蓋並點選盒體',lambda:skstate('body-selected'))
    def require_body():
        d=state('body-check')
        if d['active']!='Body':raise RuntimeError('body not selected '+str(d['active']))
    k.do(require_body,.2)
    k.do(lambda:k.click(700,550,button='RIGHTMOUSE'),1)
    k.record('LINK','body-menu','查看盒體草圖清單',lambda:skstate('body-menu'))
    k.do(lambda:k.click(805,549),1.5)
    k.record('LINK','outer-sketch','選外框草圖',lambda:skstate('outer-sketch'))
    def require_outer():
        d=state('outer-check')
        if d['activeSketch']!='Body Sketch':raise RuntimeError('outer sketch not entered')
    k.do(require_outer,.2)
    k.do(lambda:k.click(1125,657,button='RIGHTMOUSE'),1)
    k.record('LINK','source-menu','右鍵 X80 欄位',lambda:skstate('source-menu'))
    k.do(lambda:k.move(1030,884),.4);k.do(lambda:k.click(1030,884),1)
    k.do(lambda:k.click(1050,131),1)
    send('H',alt=True)
    k.do(lambda:k.click(1320,75),1)
    k.record('LINK','lid-selected','顯示上蓋並在 Outliner 選取 Cube',lambda:skstate('lid-selected'))
    def require_lid():
        d=skstate('lid-check')
        if d['active']!='Cube':raise RuntimeError('Cube not selected '+str(d['active']))
    k.do(require_lid,.2)
    k.do(lambda:k.click(1244,615),1)
    k.do(lambda:k.click(1320,522),1)
    k.record('LINK','x-key-selected','選上蓋 X 形狀鍵',lambda:skstate('x-key-selected'))
    k.do(lambda:k.move(1400,640),.4);k.do(lambda:k.click(1400,640,button='RIGHTMOUSE'),1)
    k.record('LINK','target-menu','右鍵 X 形狀鍵 Value 欄位',lambda:skstate('target-menu'))
    k.do(lambda:k.move(1290,686),.4);k.do(lambda:k.click(1290,686),1)
    k.record('LINK','x-pasted','將外框驅動器貼至上蓋 X 形狀鍵',lambda:skstate('x-pasted'))
    k.do(lambda:k.move(1400,640),.4);k.do(lambda:k.click(1400,640,button='RIGHTMOUSE'),1)
    k.record('LINK','x-edit-menu','右鍵已驅動 X 形狀鍵',lambda:skstate('x-edit-menu'))
    k.do(lambda:k.move(1290,680),.4);k.do(lambda:k.click(1290,680),1)
    k.record('LINK','x-popup','開啟 X 形狀鍵驅動器',lambda:skstate('x-popup'))
    k.do(lambda:k.move(1250,682),.4);k.do(lambda:k.click(1250,682),1)
    k.record('LINK','x-type-menu','選擇驅動類型',lambda:skstate('x-type-menu'))
    k.do(lambda:k.move(1230,749),.4);k.do(lambda:k.click(1230,749),1)
    k.record('LINK','x-script','選 Scripted Expression',lambda:skstate('x-script'))
    k.type_into(1250,705,'slvs_c_854e8777cfe2608d/10-5')
    k.record('LINK','x-formula','設定 (外框X−80)/10 並讀回',lambda:skstate('x-formula'))
    k.do(lambda:k.click(600,450),1)
    k.file_dialog(163,k.demo_dir,'manual_lid_shape_xy_driver_v001.blend');k.confirm_dialog(wait=3)
    k.record('LINK','x-saved','保存 X 鍵驅動試驗',lambda:skstate('x-saved'))
