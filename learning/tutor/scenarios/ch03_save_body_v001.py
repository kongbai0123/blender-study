"""Rename and save an isolated original-box copy using real Blender GUI."""
import json
from pathlib import Path
import bpy
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend'
SHA='b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530'


def build(g):
    k=Kit(g)
    if g['sha256'](SOURCE)!=SHA:raise RuntimeError('source changed')
    copy=Path(k.demo_dir)/'box_reference_copy.blend'
    copy.write_bytes(SOURCE.read_bytes())
    def key(name,**kw):k.do(lambda:k.key(name,x=700,y=500,**kw),.6)
    def stats():
        o=bpy.context.view_layer.objects.active
        d={'active':o.name,'mode':o.mode,'dimensions':list(o.dimensions),'scale':list(o.scale),'sourceSha256':SHA}
        if o.type!='MESH' or any(abs(a-b)>1e-4 for a,b in zip(o.dimensions,(60,40,30))):raise RuntimeError('unexpected box '+json.dumps(d))
        return json.dumps(d)
    k.setup();key('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3)
    k.record('SAVE','source','GUI 開啟原盒的隔離副本並核對活動物件與尺寸。',stats)
    key('F2');k.do(lambda:k.type_text('Body'),.4);key('RET')
    k.record('SAVE','renamed','GUI F2 將盒體改名 Body。',stats)
    k.file_dialog(163,k.demo_dir,'u03_body_saved_v001.blend');k.confirm_dialog(wait=2)
    k.record('SAVE','saved','GUI Save As 保存新版本；檔名與資料夾欄由程式填入。',stats)
    key('O',ctrl=True);k.fill_dialog(k.demo_dir,'u03_body_saved_v001.blend');k.confirm_dialog(wait=3)
    k.record('SAVE','reopened','GUI 重開新版本，核對 Body 及原盒外框。',stats)
