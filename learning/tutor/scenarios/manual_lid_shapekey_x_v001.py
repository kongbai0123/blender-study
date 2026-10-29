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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/demo-files/manual_box_lid_fixed_80x50_v001.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_lid_shapekey_x_v001.py']:
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
        (out/(label+'-state.json')).write_text(json.dumps(data,indent=2),encoding='utf-8');return data
    def search(text):
        send('F3');k.do(lambda:k.type_text(text),.3);send('RET')
    k.record('KEY','opened','重開固定尺寸蓋',lambda:skstate('opened'))
    k.do(lambda:k.click(1244, 615),1)
    k.record('KEY','panel','觀察物件資料屬性面板',lambda:skstate('panel'))
    k.do(lambda:k.click(1467,473),1)
    k.record('KEY','basis','建立 Basis 形狀鍵',lambda:skstate('basis'))
    k.do(lambda:k.click(1467,473),1)
    k.record('KEY','key-one','建立第一個相對形狀鍵',lambda:skstate('key-one'))
    send('TAB');send('ONE');send('A',alt=True);send('Z',alt=True)
    k.record('KEY','edit-vertices','進入形狀鍵編輯並顯示穿透選取',lambda:skstate('edit-vertices'))
    send('B');k.do(lambda:k.drag_slow([(760,460),(930,680)]),1)
    def selected():
        import bmesh
        ob=bpy.context.object; bm=bmesh.from_edit_mesh(ob.data);coords=[list(ob.matrix_world@v.co) for v in bm.verts if v.select]
        d=skstate('selected');d['selectedCoords']=coords
        (out/'selected-state.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        return d
    k.record('KEY','select-right','框選上蓋右半邊頂點',selected)
    def ensure_selection():
        import bmesh
        ob=bpy.context.object; bm=bmesh.from_edit_mesh(ob.data); vs=[ob.matrix_world@v.co for v in bm.verts if v.select]
        if len(vs)!=12 or any(v.x<40 for v in vs):raise RuntimeError('incorrect right-half selection '+str([list(v) for v in vs]))
    k.do(ensure_selection,.2)
    send('G');send('X');k.do(lambda:k.type_text('10mm'),.3);send('RET')
    k.record('KEY','x-shape','右半邊沿 X 移動10 mm 形成 X 形狀鍵',lambda:skstate('x-shape'))
    send('TAB')
    k.record('KEY','x-object','離開編輯，查看 X 形狀鍵幾何',lambda:skstate('x-object'))
    k.file_dialog(163,k.demo_dir,'manual_lid_shape_x_v001.blend');k.confirm_dialog(wait=3)
    k.record('KEY','saved','保存 X 形狀鍵試驗版',lambda:skstate('saved'))
