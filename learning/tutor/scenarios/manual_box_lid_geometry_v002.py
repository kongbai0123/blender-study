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
    source=PROJECT/'learning/evidence/parametric/2026-10-27-manual-box-xy-verify-v001/demo-files/manual_box_xy_80x50_v002.blend'
    copied=Path(k.demo_dir)/'source_solid_60x40x30.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/manual_box_lid_geometry_v002.py']:
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
        k.do(lambda:k.move(x,y),.4);k.do(lambda:k.click(x,y,button=button),1)
    def keyseq(letter,axis,val):
        send(letter);send(axis);k.do(lambda:k.type_text(str(val)),.2);send('RET')
    def modal(letter,val):
        send(letter);k.do(lambda:k.type_text(str(val)+'mm'),.2);send('RET')
    k.record('LID','opened','重開手工參數盒試驗版',lambda:state('opened'))
    mc(1050,131);mc(785,510)
    k.record('LID','body-selected','離開內腔草圖並選取盒體',lambda:state('body-selected'))
    def require_body():
        d=state('body-check')
        if d['active']!='Body' or d['activeSketch'] is not None:raise RuntimeError('body not selected')
    k.do(require_body,.2)
    send('H'); k.add_mesh(80,.8)
    k.record('LID','cube','隱藏盒體，以 GUI 新增方塊作蓋板',lambda:state('cube'))
    send('S');k.do(lambda:k.type_text('0.001'),.2);send('RET')
    keyseq('S','X',40);keyseq('S','Y',25)
    send('F3');k.do(lambda:k.type_text('Apply Scale'),.3);send('RET')
    keyseq('G','X',40);keyseq('G','Y',25);keyseq('G','Z',31)
    k.record('LID','plate','方塊變為80×50×2蓋板並移至盒口',lambda:state('plate'))
    def require_plate():
        d=state('plate-check'); o=next((x for x in d['objects'] if x['name']=='Cube'),None)
        if not o or not o.get('evaluated'):raise RuntimeError('cube missing')
        b=o['evaluated']['bounds']; expected=[[0,80],[0,50],[30,32]]
        if any(abs(a-c)>.001 for ab,cd in zip(b,expected) for a,c in zip(ab,cd)):raise RuntimeError('plate bounds differ '+str(b))
    k.do(require_plate,.2)
    send('NUMPAD_7',ctrl=True);send('TAB');send('THREE');send('A',alt=True)
    k.do(lambda:at_world((40,25,30),click=True),1)
    k.record('LID','bottom-face','底視選取蓋板底面',lambda:state('bottom-face'))
    modal('I',2.2);k.record('LID','inset-outer','底面內插2.2 mm',lambda:state('inset-outer'))
    modal('E',4);k.record('LID','lip-extrude','沿底面向外拉伸4 mm',lambda:state('lip-extrude'))
    modal('I',2);k.record('LID','inset-inner','再內插2 mm環壁',lambda:state('inset-inner'))
    modal('E',-4);k.record('LID','lip-recess','中心面推回4 mm形成環形唇邊',lambda:state('lip-recess'))
    send('TAB');send('H',alt=True)
    k.record('LID','assembly','顯示盒體並讀取蓋板幾何',lambda:state('assembly'))
    k.file_dialog(163,k.demo_dir,'manual_box_lid_fixed_80x50_v001.blend');k.confirm_dialog(wait=3)
    k.record('LID','saved','另存固定尺寸上蓋試驗版',lambda:state('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'manual_box_lid_fixed_80x50_v001.blend');k.confirm_dialog(wait=4)
    k.record('LID','reopened','重開固定尺寸上蓋試驗版',lambda:state('reopened'))
