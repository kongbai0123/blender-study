"""Attempt UI install of verified CAD Sketcher ZIP into an isolated extensions profile."""
import bpy,os
from pathlib import Path
from common import Kit,PROJECT
SRC=PROJECT/'learning/.publication-private/cad-sketcher-0.32.1-v001/CAD_Sketcher-0.32.1-windows_x64.zip'
HASH='b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59'
def build(g):
 k=Kit(g);demo=Path(k.demo_dir);out=Path(g['OUT']);ext=Path(os.environ['BLENDER_USER_EXTENSIONS']).resolve()
 if not ext.is_relative_to(PROJECT/'learning/evidence/parametric'):raise RuntimeError('extensions profile is not isolated')
 if g['sha256'](SRC)!=HASH or SRC.stat().st_size!=1283581:raise RuntimeError('zip hash or size mismatch')
 z=demo/SRC.name;z.write_bytes(SRC.read_bytes())
 def key(n):k.key(n,x=700,y=500)
 def info():return {'activeSection':bpy.context.preferences.active_section,'addons':[a.module for a in bpy.context.preferences.addons if 'sketch' in a.module.lower()],'zipSha256':HASH,'isolatedExtensions':True}
 k.setup();k.do(lambda:key('F3'),.3);k.do(lambda:k.type_text('Preferences'),.4);k.do(lambda:key('RET'),2)
 k.do(lambda:k.click(75,188,win='PREFERENCES'),.8);k.do(lambda:k.click(822,18,win='PREFERENCES'),.7)
 k.record('CAD-INSTALL','menu','確認 Install from Disk 選單',info,win='PREFERENCES')
 k.do(lambda:k.click(720,135,win='PREFERENCES'),1)
 k.fill_dialog(str(demo),z.name);k.confirm_dialog(wait=6)
 k.record('CAD-INSTALL','after-install','確認安裝後隔離 Preferences 狀態',info,win='PREFERENCES')
