"""GUI probe: detach CAD Sketcher evaluated mesh copy, preserve sketch source."""
import bpy,addon_utils,json,bmesh
from pathlib import Path
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/parametric/2026-10-28-cad-thread-triangle-restore-v001/demo-files/cad_thread_triangle_060_restored_v003.blend';HASH='f45cb87cb9084bb9ca92612d6dc8726c28f7abfd099954e14ea4964975dd8508'
def build(g):
 k=Kit(g)
 if g['sha256'](SOURCE)!=HASH:raise RuntimeError('source changed')
 copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
 def bootstrap():
  addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
 def send(key,**kw):k.do(lambda:k.key(key,x=600,y=450,**kw),.55)
 def state():
  o=bpy.context.view_layer.objects.active;d={'active':o.name if o else None,'mode':bpy.context.mode,'type':o.type if o else None,'objects':[(o.name,o.type) for o in bpy.context.scene.objects],'mods':[(m.name,m.type) for m in o.modifiers] if o else []}
  if o and o.type=='MESH':
   o.update_from_editmode();m=o.data;d['mesh']={'vertices':len(m.vertices),'edges':len(m.edges),'faces':len(m.polygons),'worldCoords':[list(o.matrix_world@v.co) for v in m.vertices]};e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();d['eval']={'vertices':len(me.vertices),'edges':len(me.edges),'faces':len(me.polygons)};e.to_mesh_clear()
  return json.dumps(d)
 k.setup();k.do(bootstrap,2);send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=4);k.record('C2M','source','開啟已完整約束的 CAD XY 牙型草圖',state)
 k.do(lambda:k.click(1145,38),1.2);k.record('C2M','leave-sketch','GUI 離開草圖，查看輸出物件',state)
 k.do(lambda:k.click(1340,182),.8);k.record('C2M','select-body','GUI 選擇生成的 Body',state)
 send('D',shift=True);send('ESC');k.record('C2M','duplicate','GUI 複製輸出，保留 CAD 原草圖與原 Body',state)
 send('F3');k.do(lambda:k.type_text('Convert Mesh'),.5);send('RET');k.record('C2M','converted','GUI 將副本轉成 mesh；不維持 CAD 參數連動',state)

 send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET')
 send('TAB');send('THREE');send('A');send('F3');k.do(lambda:k.type_text('Only Faces'),.4);send('RET');k.record('C2M','delete-face','GUI 只刪除副本的面，保留三角三邊',state)
 send('TAB');send('R');send('X');k.do(lambda:k.type_text('90'),.4);send('RET');k.record('C2M','rotated','GUI 將 XY 截面繞 X 旋轉 90 度至 XZ',state)
 send('F3');k.do(lambda:k.type_text('Apply Rotation'),.4);send('RET');k.record('C2M','apply-rotation','GUI 套用旋轉，核對三點 XZ 座標',state)

 def screw_state(stage):
  o=bpy.context.view_layer.objects.active
  if not o or o.name!='Body.001':raise RuntimeError('not detached copy')
  mod=next((m for m in o.modifiers if m.type=='SCREW'),None)
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();pts=[e.matrix_world@v.co for v in mesh.vertices];bm=bmesh.new();bm.from_mesh(mesh)
  result={'stage':stage,'object':o.name,'sourceMesh':{'vertices':len(o.data.vertices),'edges':len(o.data.edges),'faces':len(o.data.polygons)},'modifier':{'axis':mod.axis if mod else None,'angle':mod.angle if mod else None,'screwOffset':mod.screw_offset if mod else None,'iterations':mod.iterations if mod else None,'steps':mod.steps if mod else None},'evaluated':{'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'nonManifoldEdges':sum(not v.is_manifold for v in bm.edges),'boundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]},'material':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedStrength':None,'qualifiedClearance':None};bm.free();e.to_mesh_clear()
  expected={'axis':'Z','angle':6.283185307179586,'screwOffset':1.0,'iterations':4,'steps':32};checks={key:(abs(result['modifier'][key]-value)<1e-5 if isinstance(value,float) else result['modifier'][key]==value) for key,value in expected.items()};checks['closedProfileInput']=result['sourceMesh']=={'vertices':3,'edges':3,'faces':0};checks['endStillOpen']=result['evaluated']['nonManifoldEdges']>0;result['checks']=checks;(Path(g['OUT'])/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
  if not all(checks.values()):raise RuntimeError('screw verification failed '+json.dumps(result))
  return json.dumps(result)
 send('F3');k.do(lambda:k.type_text('Add Screw Modifier'),.4);send('RET');k.do(lambda:k.click(1246,k.props_y(300)),.8)
 def field(x,y,value):
  k.do(lambda:k.click(x,k.props_y(y),ctrl=True),.4);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text(value),.4);send('RET')
 field(1400,165,'1mm');field(1400,186,'4');field(1400,303,'32');field(1400,323,'32')
 k.record('C2M','screw','GUI Screw Z 軸、360°、每圈位移 1 mm、4 圈、每圈 32 段；牙端仍開口',lambda:screw_state('screw'))
 k.file_dialog(163,k.demo_dir,'cad_triangle_detached_screw_v001.blend');k.confirm_dialog(wait=3);k.record('C2M','saved','GUI 另存脫離參數的 Screw 草案',lambda:screw_state('saved'))
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,'cad_triangle_detached_screw_v001.blend');k.confirm_dialog(wait=4);k.record('C2M','reopened','GUI 重開 Screw 草案並讀回',lambda:screw_state('reopened'))
