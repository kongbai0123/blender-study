"""GUI Screw and boundary-fill probe; only the closed triangle input is scripted."""
import json
import math
from pathlib import Path
import bpy
import bmesh
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'

def build(g):
    k=Kit(g);out=Path(g['OUT'])
    if g['sha256'](SOURCE)!=SOURCE_HASH: raise RuntimeError('reference hash differs')
    source_copy=Path(k.demo_dir)/SOURCE.name; source_copy.write_bytes(SOURCE.read_bytes())
    def send(key,**kw): k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
    def prepare():
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
        bpy.data.objects['Body_Reference'].hide_set(True)
        mesh=bpy.data.meshes.new('Thread_Triangle_Profile');mesh.from_pydata([(4.8,0,0),(6,0,.3),(4.8,0,.6)],[(0,1),(1,2),(2,0)],[]);mesh.update()
        obj=bpy.data.objects.new('Thread_Triangle_Profile',mesh);scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.context.view_layer.update()
    def stats():
        obj=bpy.data.objects['Thread_Triangle_Profile']; obj.update_from_editmode()
        m=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh() if obj.mode=='OBJECT' else obj.data
        bm=bmesh.new();bm.from_mesh(m); boundary=[e for e in bm.edges if e.is_boundary]
        result={'object':obj.name,'mode':obj.mode,'vertices':len(m.vertices),'edges':len(m.edges),'polygons':len(m.polygons),
          'boundary':len(boundary),'nonManifold':sum(not e.is_manifold for e in bm.edges),
          'modifier':[{'type':v.type,'screw':v.screw_offset,'iterations':v.iterations,'steps':v.steps} for v in obj.modifiers if v.type=='SCREW'],
          'boundaryCenters':[[round(float(c),4) for c in ((e.verts[0].co+e.verts[1].co)/2)] for e in boundary[:10]]}
        bm.free();return json.dumps(result)
    def checked_stats(stage):
        raw=stats();result=json.loads(raw)
        if stage=='screw':
            valid=(len(result['modifier'])==1 and result['modifier'][0]['screw']==1 and result['modifier'][0]['iterations']==4 and result['modifier'][0]['steps']==32 and result['boundary']==6)
        elif stage=='converted':valid=not result['modifier'] and result['boundary']==6
        else:valid=result['boundary']==0 and result['nonManifold']==0
        if not valid:raise RuntimeError(stage+' failed: '+raw)
        return raw
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3);k.do(prepare,1)
    k.record('XTH','profile','程式建立三角閉合邊輪廓；GUI 實作 Screw，不是手動畫輪廓。',stats)
    send('F3');k.do(lambda:k.type_text('Add Screw Modifier'),.5);send('RET')
    k.do(lambda:k.click(1246,k.props_y(300)),.8)
    def field(x,y,value):
        k.do(lambda:k.click(x,y,ctrl=True),.4);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text(value),.4);k.do(lambda:k.key('RET'),.8)
    field(1400,372,'1mm');field(1400,393,'4');field(1400,510,'32');field(1400,530,'32')
    k.record('XTH','screw','GUI Screw 360°/1mm/4圈/32段。',lambda:checked_stats('screw'))
    send('F3');k.do(lambda:k.type_text('Convert Mesh'),.5);send('RET')
    k.record('XTH','converted','GUI Convert Mesh 應用修改器並讀回邊界。',lambda:checked_stats('converted'))
    send('TAB');send('TWO');send('A',alt=True);send('F3');k.do(lambda:k.type_text('Select Non Manifold'),.4);send('RET')
    k.record('XTH','selected-boundary','GUI 選取全部非流形邊。',stats)
    send('F');k.record('XTH','filled','GUI F 嘗試封閉兩端；讀回邊界。',lambda:checked_stats('filled'))
    send('A');send('N',shift=True);k.record('XTH','normals','GUI 選取全部並重新計算法線。',stats)
    send('TAB');send('F3');k.do(lambda:k.type_text('Add Cylinder'),.5);send('RET')
    def typed_seq(keys,value):
        for key in keys: send(key)
        k.do(lambda:k.type_text(value),.35);send('RET')
    typed_seq(['S'],'.005');typed_seq(['S','Z'],'.46');typed_seq(['G','Z'],'2.3mm')
    send('F3');k.do(lambda:k.type_text('Apply Scale'),.5);send('RET')
    send('F2');k.do(lambda:k.type_text('Thread_Core'),.5);send('RET')
    def core_stats():
        obj=bpy.context.view_layer.objects.active
        actual={'active':obj.name,'location':list(obj.location),'dimensions':list(obj.dimensions),'scale':list(obj.scale),'selected':[v.name for v in bpy.context.selected_objects]}
        if obj.name!='Thread_Core' or any(abs(a-b)>1e-4 for a,b in zip(obj.dimensions,(10,10,4.6))) or abs(obj.location.z-2.3)>1e-4:
            raise RuntimeError('Cylinder does not match intended draft: '+json.dumps(actual))
        return json.dumps(actual)
    k.record('XTH','core','GUI 新增圓柱、縮放為直徑 10 mm、高 4.6 mm，沿 Z 上移 2.3 mm，套用縮放並重新命名。',core_stats)
    send('F3');k.do(lambda:k.type_text('Add Boolean Modifier'),.5);send('RET')
    k.do(lambda:k.click(1369,350),.4)
    k.do(lambda:k.click(1380,400),.4);k.do(lambda:k.type_text('Thread_Triangle_Profile'),.4);send('RET')
    def assignment():
        o=bpy.data.objects.get('Thread_Core'); mods=[m for m in o.modifiers if m.type=='BOOLEAN'] if o else [];m=mods[0] if len(mods)==1 else None
        return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
    k.record('XTH','boolean-probe','首次 GUI 指定 Boolean Union 物件，讀回欄位。',lambda:json.dumps(assignment()))
    def try_assigned(attempt=0):
        actual=assignment()
        if actual=={'operation':'UNION','operand':'Thread_Triangle_Profile','solver':'EXACT'}:return
        if attempt>=2:raise RuntimeError('Boolean UI 指定失敗 '+str(actual))
        g['queue'][0:0]=[(lambda:k.move(1380,400),.3),(lambda:k.click(1380,400),.4),
          (lambda:k.key('A',ctrl=True,x=700,y=500),.2),(lambda:k.type_text('Thread_Triangle_Profile'),.4),
          (lambda:k.move(1310,432),.3),(lambda:k.click(1310,432),.6),(lambda:try_assigned(attempt+1),.1)]
    k.do(try_assigned,.1)
    k.record('XTH','boolean-preview','GUI 選擇 Union／Exact 與牙條，讀回設定。',lambda:json.dumps(assignment()))
    k.do(lambda:k.click(1424,320),.4);k.menu_item(1331,343,.9)
    def union_stats():
        obj=bpy.data.objects['Thread_Core']; bm=bmesh.new();bm.from_mesh(obj.data)
        remaining=set(bm.verts);components=0
        while remaining:
            stack=[remaining.pop()];components+=1
            while stack:
                v=stack.pop()
                for e in v.link_edges:
                    other=e.other_vert(v)
                    if other in remaining:remaining.remove(other);stack.append(other)
        world=[obj.matrix_world@v.co for v in bm.verts]
        result={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary':sum(e.is_boundary for e in bm.edges),'nonManifold':sum(not e.is_manifold for e in bm.edges),'components':components,'volume':bm.calc_volume(signed=True),'bounds':[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]}
        bm.free();(out/'union-probe.json').write_text(json.dumps(result,indent=2),encoding='utf8')
        expected=[[-6,6],[-6,6],[0,4.6]]
        if result['boundary'] or result['nonManifold'] or result['components']!=1 or not 350<result['volume']<600 or any(abs(a-b)>1e-3 for got,want in zip(result['bounds'],expected) for a,b in zip(got,want)):
            raise RuntimeError('Union did not pass geometric checks: '+json.dumps(result))
        return json.dumps(result)
    k.record('XTH','union','GUI 套用 Boolean Union，讀回拓樸及尺寸；此為幾何探測。',union_stats)
