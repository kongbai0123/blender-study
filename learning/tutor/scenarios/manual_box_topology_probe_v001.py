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
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_box_topology_probe_v001.py']:
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
    k.record('META','opened','開啟示範副本並讀回幾何',lambda:precise('opened'))
    def dump():
        scene=bpy.context.scene;ob=scene.objects['Cube'];me=ob.data;keys=me.shape_keys
        def drv(f):
            return {'path': f.data_path, 'expr':f.driver.expression,'valid':f.driver.is_valid,
                    'variables':[{'name':v.name,'type':v.type,'targets':[{'idType':x.id_type,'id':x.id.name if x.id else None,'path':x.data_path} for x in v.targets]} for v in f.driver.variables]}
        data={'unit':{'system':scene.unit_settings.system,'scale':scene.unit_settings.scale_length},
              'object':{'name':ob.name,'type':ob.type,'matrixWorld':[list(row) for row in ob.matrix_world], 'scale':list(ob.scale)},
              'mesh':{'vertices':[list(v.co) for v in me.vertices], 'edges':[list(e.vertices) for e in me.edges], 'faces':[list(p.vertices) for p in me.polygons]},
              'keys':[{'name':s.name,'relative':s.relative_key.name,'min':s.slider_min,'max':s.slider_max,'values':[list(p.co) for p in s.data]} for s in keys.key_blocks],
              'keyDrivers':[drv(f) for f in keys.animation_data.drivers] if keys.animation_data else [],
              'sceneDrivers':[drv(f) for f in scene.animation_data.drivers] if scene.animation_data else []}
        data['evaluatedObjects'] = {}
        for name in ('Body', 'Body.001', 'Cube'):
            ob=scene.objects[name]; ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=ev.to_mesh()
            data['evaluatedObjects'][name]={'matrixWorld':[list(row) for row in ev.matrix_world], 'vertices':[list(v.co) for v in m.vertices], 'edges':[list(e.vertices) for e in m.edges], 'faces':[list(p.vertices) for p in m.polygons]}
            ev.to_mesh_clear()
        (out/'topology-and-drivers.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        return {'name':'safe topology and drivers only','keyCount':len(keys.key_blocks),'meshVertices':len(me.vertices)}
    k.record('META','topology','程式只讀網格拓撲、形狀鍵和 driver targets',dump)
