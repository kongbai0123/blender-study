"""Independent GUI axial-relief Difference for side cap; cutter created by Python."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/08/2026-10-28-side-thread-cap-gui-v001/demo-files/u11_side_thread_cap_draft_v001.blend'
SOURCE_SHA='453f6c4b9682098aaefea5cfb9501a74c70a562f14c5a0215709101b5b71871d'
FILENAME='u11_side_thread_cap_draft_v002.blend'
def build(g):
 k=Kit(g);out=Path(g['OUT'])
 if g['sha256'](SOURCE)!=SOURCE_SHA:raise RuntimeError('source mismatch')
 copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
 def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
 def prepare():
  bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=5.3,depth=.35,location=(34.325,0,0),rotation=(0,math.pi/2,0));cut=bpy.context.object;cut.name='A_Relief_Cutter';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  bpy.ops.object.select_all(action='DESELECT');cap=bpy.data.objects['Side_Cap_Blank'];cap.select_set(True);bpy.context.view_layer.objects.active=cap;bpy.context.view_layer.update()
 def bounds(o):
  p=[o.matrix_world@v.co for v in o.data.vertices];return [[min(q[i] for q in p),max(q[i] for q in p)] for i in range(3)]
 def prepared():
  return json.dumps({'sourceSha256':SOURCE_SHA,'cutterBoundsMm':bounds(bpy.data.objects['A_Relief_Cutter']),'radiusMm':5.3,'method':'程式新增端隙刀具，非 GUI 手工繪製；局部切除末端部分牙','nominalAxialGapMm':.2,'nominalWallThicknessMm':1.3})
 def assignment():
  o=bpy.data.objects['Side_Cap_Blank'];m=next((m for m in o.modifiers if m.type=='BOOLEAN'),None)
  return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
 def try_assigned(attempt=0):
  actual=assignment()
  if actual=={'operation':'DIFFERENCE','operand':'A_Relief_Cutter','solver':'EXACT'}:return
  if attempt>=2:raise RuntimeError('Boolean assignment failed '+str(actual))
  y=k.props_y(193);g['queue'][0:0]=[(lambda:k.move(1380,y),.3),(lambda:k.click(1380,y),.4),(lambda:k.key('A',ctrl=True,x=700,y=500),.2),(lambda:k.type_text('A_Relief_Cutter'),.4),(lambda:k.move(1310,y+32),.3),(lambda:k.click(1310,y+32),.6),(lambda:try_assigned(attempt+1),.1)]
 def check(stage):
  o=bpy.data.objects['Side_Cap_Blank'];bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);comps=0
  while remaining:
   comps+=1;stack=[remaining.pop()]
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in remaining:remaining.remove(v);stack.append(v)
  m=o.data;m.calc_loop_triangles();p=[o.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(p,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True);hit=tree.ray_cast(Vector((32,0,0)),Vector((1,0,0)))[0]
  result={'stage':stage,'vertices':len(bm.verts),'faces':len(bm.faces),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':comps,'boundsMm':bounds(o),'centerCavityBottomMm':list(hit) if hit else None,'material':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None};bm.free()
  (out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
  if result['nonManifoldEdges'] or comps!=1 or not hit or abs(hit.x-34.5)>.001:raise RuntimeError('cap relief unexpected '+json.dumps(result))
  return json.dumps(result)
 k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3);k.do(prepare,1)
 k.record('REL','prepared','程式建立端隙圓柱刀具，原帽、盒和平面上蓋保留。',prepared)
 send('F3');k.do(lambda:k.type_text('Add Boolean Modifier'),.5);send('RET')
 k.do(lambda:k.click(1380,k.props_y(193)),.4);k.do(lambda:k.type_text('A_Relief_Cutter'),.4);send('RET')
 k.record('REL','operand-probe','GUI 嘗試指定端隙刀具，讀回欄位。',lambda:json.dumps(assignment()))
 k.do(try_assigned,.1);k.record('REL','difference-preview','GUI 核對 Difference、Exact 與端隙工具。',lambda:json.dumps(assignment()))
 k.do(lambda:k.click(1452,k.outliner_y('A_Relief_Cutter')),.7)
 def hidden():
  if not bpy.data.objects['A_Relief_Cutter'].hide_get():raise RuntimeError('cutter not hidden')
  return 'GUI 隱藏端隙刀具。'
 k.record('REL','cutter-hidden','GUI 隱藏端隙刀具。',hidden)
 k.do(lambda:k.click(1424,k.props_y(113)),.4);k.menu_item(1331,k.props_y(136),1.2)
 k.record('REL','difference','GUI 套用端隙差集，讀回中央軸底面位置。',lambda:check('difference'))
 k.file_dialog(163,k.demo_dir,FILENAME);k.confirm_dialog(wait=3)
 k.record('REL','saved','GUI 另存新檔；路徑與檔名由程式填入。',lambda:check('saved'))
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,FILENAME);k.confirm_dialog(wait=4)
 k.record('REL','reopened','GUI 重開新檔並讀值；實際列印和試配留空。',lambda:check('reopened'))
