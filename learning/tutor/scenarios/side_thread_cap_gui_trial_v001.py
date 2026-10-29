"""Independent GUI Difference for side cap; cutter and blank are prepared by Python."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/demo-files/u11_box_external_thread_draft_v002.blend'
SOURCE_SHA='df2108d06250807a9fa593ce966ae09e42d0fc3b2bfad97c98d0c40f77378c54'
FILENAME='u11_side_thread_cap_draft_v001.blend'
def build(g):
 k=Kit(g);out=Path(g['OUT'])
 if g['sha256'](SOURCE)!=SOURCE_SHA:raise RuntimeError('source mismatch')
 copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
 def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
 def prepare():
  src=bpy.data.objects['Thread_Core'];body=bpy.data.objects['Body'];assert len(src.data.vertices)==707
  cutter=bpy.data.objects.new('Cap_Cutter_020',src.data.copy());body.users_collection[0].objects.link(cutter);cutter.matrix_world=src.matrix_world.copy();inv=cutter.matrix_world.inverted()
  for v in cutter.data.vertices:
   w=cutter.matrix_world@v.co;r=math.hypot(w.y,w.z)
   if r<1e-6:raise RuntimeError('axis vertex radial undefined')
   w.y*=1+.2/r;w.z*=1+.2/r;v.co=inv@w
  cutter.data.update();cutter.hide_set(False);bpy.data.objects['Thread_Core'].hide_set(True)
  bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=7.7,depth=5.5,location=(33.05,0,0),rotation=(0,math.pi/2,0))
  cap=bpy.context.object;cap.name='Side_Cap_Blank';cap.rotation_mode='QUATERNION';cap.rotation_quaternion=Quaternion((1,0,0),math.radians(2.8125))@Quaternion((0,1,0),math.pi/2)
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.context.view_layer.update()
 def bounds(o):
  p=[o.matrix_world@v.co for v in o.data.vertices];return [[min(q[i] for q in p),max(q[i] for q in p)] for i in range(3)]
 def prepared():
  c=bpy.data.objects['Cap_Cutter_020'];o=bpy.data.objects['Side_Cap_Blank'];result={'cutterBoundsMm':bounds(c),'blankBoundsMm':bounds(o),'sourceSha256':SOURCE_SHA,'radialDeltaMm':.2,'nominalDiameterDeltaMm':.4,'pitchMm':1,'method':'程式複製已放置外牙並僅對 YZ 徑向加 0.2；程式準備圓柱毛坯，非 GUI 手工繪製','limitations':['間隙草案未驗證','非 ISO、牙端截斷','原盒上蓋不變']}
  if abs(result['blankBoundsMm'][0][0]-30.3)>.005 or abs(result['blankBoundsMm'][0][1]-35.8)>.005:raise RuntimeError('blank location incorrect')
  return json.dumps(result)
 def assignment():
  o=bpy.data.objects['Side_Cap_Blank'];m=next((m for m in o.modifiers if m.type=='BOOLEAN'),None)
  return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
 def try_assigned(attempt=0):
  actual=assignment()
  if actual=={'operation':'DIFFERENCE','operand':'Cap_Cutter_020','solver':'EXACT'}:return
  if attempt>=2:raise RuntimeError('Boolean assignment failed '+str(actual))
  y=k.props_y(193);g['queue'][0:0]=[(lambda:k.move(1380,y),.3),(lambda:k.click(1380,y),.4),(lambda:k.key('A',ctrl=True,x=700,y=500),.2),(lambda:k.type_text('Cap_Cutter_020'),.4),(lambda:k.move(1310,y+32),.3),(lambda:k.click(1310,y+32),.6),(lambda:try_assigned(attempt+1),.1)]
 def check(stage):
  o=bpy.data.objects['Side_Cap_Blank'];bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);comps=0
  while remaining:
   comps+=1;stack=[remaining.pop()]
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in remaining:remaining.remove(v);stack.append(v)
  result={'stage':stage,'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':comps,'signedVolumeMm3':bm.calc_volume(signed=True),'boundsMm':bounds(o),'material':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None};bm.free()
  (out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
  if result['nonManifoldEdges'] or comps!=1 or result['vertices']<700:raise RuntimeError('cap not expected topology '+json.dumps(result))
  return json.dumps(result)
 k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3);k.do(prepare,1)
 k.record('CAP','prepared','程式準備盒側等相位擴徑刀具與毛坯，兩者均非手工 GUI 生成。',prepared)
 send('F3');k.do(lambda:k.type_text('Add Boolean Modifier'),.5);send('RET')
 k.do(lambda:k.click(1380,k.props_y(193)),.4);k.do(lambda:k.type_text('Cap_Cutter_020'),.4);send('RET')
 k.record('CAP','operand-probe','GUI 嘗試指定差集對象並讀回欄位。',lambda:json.dumps(assignment()))
 k.do(try_assigned,.1);k.record('CAP','difference-preview','GUI 核對 Difference／Exact 與工具；這是未套用預覽。',lambda:json.dumps(assignment()))
 k.do(lambda:k.click(1452,k.outliner_y('Cap_Cutter_020')),.7)
 def hidden():
  if not bpy.data.objects['Cap_Cutter_020'].hide_get():raise RuntimeError('cutter not hidden')
  return 'GUI 隱藏工具，保留物件資料。'
 k.record('CAP','cutter-hidden','GUI 隱藏切割工具。',hidden)
 k.click_outliner('Side_Cap_Blank');k.do(lambda:k.click(1424,k.props_y(113)),.4);k.menu_item(1331,k.props_y(136),1.2)
 k.record('CAP','difference','GUI 套用差集，程式檢查非流形與範圍。',lambda:check('difference'))
 send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET')
 k.record('CAP','framed','GUI 聚焦帽體；實拍角度不證明完整內牙。',lambda:check('framed'))
 k.file_dialog(163,k.demo_dir,FILENAME);k.confirm_dialog(wait=3)
 k.record('CAP','saved','GUI 另存新檔；路徑與檔名以程式填入。',lambda:check('saved'))
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,FILENAME);k.confirm_dialog(wait=4)
 k.record('CAP','reopened','GUI 重開新檔並讀回；實體列印和試配留空。',lambda:check('reopened'))
