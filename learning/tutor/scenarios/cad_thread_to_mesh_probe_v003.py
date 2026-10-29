"""GUI probe: detach CAD Sketcher evaluated mesh copy, preserve sketch source."""
import bpy,addon_utils,json
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
