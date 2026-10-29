"""Independent GUI inspection of saved cap; no model is saved or mutated."""
import bpy,json
from pathlib import Path
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/08/2026-10-28-side-thread-cap-gui-v001/demo-files/u11_side_thread_cap_draft_v001.blend';SOURCE_SHA='453f6c4b9682098aaefea5cfb9501a74c70a562f14c5a0215709101b5b71871d'
def build(g):
 k=Kit(g)
 if g['sha256'](SOURCE)!=SOURCE_SHA:raise RuntimeError('cap scene mismatch')
 copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
 def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
 def state():
  b=bpy.data.objects['Body'];l=bpy.data.objects['Lid'];c=bpy.data.objects['Side_Cap_Blank'];return json.dumps({'bodyHidden':b.hide_get(),'lidHidden':l.hide_get(),'capVertices':len(c.data.vertices),'capFaces':len(c.data.polygons),'sourceSha256':SOURCE_SHA,'note':'僅切換檢視、未儲存；牙型實際完整性需要其他數位檢查'})
 k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3)
 k.do(lambda:k.click(1452,k.outliner_y('Body')),.6);k.do(lambda:k.click(1452,k.outliner_y('Lid')),.6);k.click_outliner('Side_Cap_Blank')
 send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET');send('NUMPAD_3',ctrl=True)
 k.record('CAPV','opening','GUI 暫時隱藏盒體與上蓋，從 −X 檢視朝盒側的開口；不改存檔。',state)
 send('NUMPAD_2');send('NUMPAD_4');k.record('CAPV','interior','GUI 轉動視角觀察內牙；不代表配合已驗證。',state)
