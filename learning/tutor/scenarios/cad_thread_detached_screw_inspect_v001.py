"""GUI inspect detached screw draft, no model save."""
import bpy,addon_utils,json
from pathlib import Path
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/parametric/2026-10-28-cad-thread-detached-screw-trial-v001/demo-files/cad_triangle_detached_screw_v001.blend';SHA='b1e5edf32e231e3c0910702a140431383eae9b8d7ccd35808c1cdee35deae495'
def build(g):
 k=Kit(g)
 if g['sha256'](SOURCE)!=SHA:raise RuntimeError('source mismatch')
 copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
 def send(key,**kw):k.do(lambda:k.key(key,x=600,y=450,**kw),.55)
 def state():
  o=bpy.data.objects['Body.001'];m=next(m for m in o.modifiers if m.type=='SCREW');return json.dumps({'object':o.name,'screwOffset':m.screw_offset,'iterations':m.iterations,'steps':m.steps,'axis':m.axis,'inputEdges':len(o.data.edges),'inputFaces':len(o.data.polygons),'note':'GUI 只改視角，牙端仍開口且非實體合格'})
 k.setup();k.do(lambda:addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True),2);send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=4)
 send('N');send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET');send('NUMPAD_2');send('NUMPAD_2');k.record('C2MV','full-view','GUI 調整視角查看螺旋草案，未改存檔',state)
