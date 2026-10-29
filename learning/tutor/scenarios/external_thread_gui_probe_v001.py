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
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3);k.do(prepare,1)
    k.record('XTH','profile','程式建立三角閉合邊輪廓；GUI 實作 Screw，不是手動畫輪廓。',stats)
    send('F3');k.do(lambda:k.type_text('Add Screw Modifier'),.5);send('RET')
    k.do(lambda:k.click(1246,k.props_y(300)),.8)
    def field(x,y,value):
        k.do(lambda:k.click(x,y,ctrl=True),.4);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text(value),.4);k.do(lambda:k.key('RET'),.8)
    field(1400,372,'1mm');field(1400,393,'4');field(1400,510,'32');field(1400,530,'32')
    k.record('XTH','screw','GUI Screw 360°/1mm/4圈/32段。',stats)
    send('F3');k.do(lambda:k.type_text('Convert Mesh'),.5);send('RET')
    k.record('XTH','converted','GUI Convert Mesh 應用修改器並讀回邊界。',stats)
    send('TAB');send('TWO');send('A',alt=True);send('F3');k.do(lambda:k.type_text('Select Non Manifold'),.4);send('RET')
    k.record('XTH','selected-boundary','GUI 選取全部非流形邊。',stats)
    send('F');k.record('XTH','filled','GUI F 嘗試封閉兩端；讀回邊界。',stats)
