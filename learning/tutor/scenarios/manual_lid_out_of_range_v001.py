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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_lid_out_of_range_v001.py']:
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
        data=state(label); ob=bpy.data.objects.get('Cube')
        keys=ob.data.shape_keys if ob and ob.type=='MESH' else None
        data['shapeKeys']=[{'name':x.name,'value':x.value,'min':x.slider_min,'max':x.slider_max} for x in keys.key_blocks] if keys else []
        data['activeKeyIndex']=ob.active_shape_key_index if ob and ob.type=='MESH' else None
        data['shapeDrivers']=[{'path':f.data_path,'expression':f.driver.expression,'valid':f.driver.is_valid,'variables':[{'name':v.name,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path} for t in v.targets]} for v in f.driver.variables]} for f in keys.animation_data.drivers] if keys and keys.animation_data else []
        (out/(label+'-state.json')).write_text(json.dumps(data,indent=2),encoding='utf-8');return data
    def search(text):
        send('F3');k.do(lambda:k.type_text(text),.3);send('RET')
    def mc(x,y,button='LEFTMOUSE'):
        k.do(lambda:k.move(x,y),.4);k.do(lambda:k.click(x,y,button=button),1)
    def precise(label):
        import bmesh
        d=skstate(label); dg=bpy.context.evaluated_depsgraph_get(); results={}
        for name in ['Body','Body.001','Cube']:
            ob=bpy.data.objects[name]; ev=ob.evaluated_get(dg); me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
            points=[list(ev.matrix_world@v.co) for v in me.vertices];levels={}
            for v in points: levels.setdefault(str(round(v[2],3)),[]).append(v)
            results[name]={'vertices':len(me.vertices),'faces':len(me.polygons),'nonManifold':sum(not e.is_manifold for e in bm.edges),'levels':{z:{'x':sorted(set(round(v[0],4) for v in ps)),'y':sorted(set(round(v[1],4) for v in ps))} for z,ps in levels.items()}}
            bm.free();ev.to_mesh_clear()
        d['meshReadback']=results;(out/(label+'-state.json')).write_text(json.dumps(d,indent=2),encoding='utf-8');return d
    k.record('LINK','opened','重開雙形狀鍵及雙驅動草案',lambda:precise('opened'))
    send('H',alt=True);send('A',alt=True);mc(1320,75);send('H');mc(700,550)
    k.record('LINK','body-selected','隱藏上蓋並選外盒',lambda:skstate('body-selected'))
    def require_body():
        d=state('body-check')
        if d['active']!='Body':raise RuntimeError('body not selected')
    k.do(require_body,.2)
    mc(700,550,'RIGHTMOUSE');mc(805,549)
    k.record('LINK','outer-sketch','進入外框草圖',lambda:skstate('outer-sketch'))
    def require_outer():
        d=state('outer-check')
        if d['activeSketch']!='Body Sketch':raise RuntimeError('outer not selected')
    k.do(require_outer,.2)
    def field(y,value):
        k.do(lambda:k.click(1124,y,ctrl=True),.5);k.do(lambda:k.key('A',ctrl=True),.2)
        k.do(lambda:k.type_text(str(value)+'mm'),.3);k.do(lambda:k.key('RET'),1.5)
    field(641,110);field(657,50)
    k.record('LINK','outer-110x50','外框改110×50，讀回上蓋形狀鍵與內腔',lambda:precise('outer-110x50'))
    mc(1050,131);mc(785,510);mc(702,448,'RIGHTMOUSE');mc(820,467)
    k.record('LINK','inner-before-solve','進內腔草圖檢查修改後狀態',lambda:precise('inner-before-solve'))
    def require_inner():
        d=state('inner-check')
        if d['activeSketch']!='Body.001 Sketch':raise RuntimeError('inner not selected')
    k.do(require_inner,.2)
    mc(1180,131)
    k.record('LINK','inner-after-solve','更新內腔草圖，讀回各高度頂點',lambda:precise('inner-after-solve'))
    mc(1050,131);send('H',alt=True)
    k.record('LINK','assembly','顯示盒蓋並讀回',lambda:precise('assembly'))
    k.file_dialog(163,k.demo_dir,'manual_box_lid_110x50_v001.blend');k.confirm_dialog(wait=3)
    k.record('LINK','saved','另存雙軸修改版本',lambda:precise('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'manual_box_lid_110x50_v001.blend');k.confirm_dialog(wait=4)
    k.record('LINK','reopened','重開雙軸修改版本並讀回',lambda:precise('reopened'))
