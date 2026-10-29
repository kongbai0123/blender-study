"""Probe a Preferences window in an isolated profile; does not install."""
from common import Kit,PARK
def build(g):
 k=Kit(g)
 def key(n):k.key(n,x=700,y=500)
 def info():
  return {'windows':[{'areas':[a.type for a in w.screen.areas]} for w in __import__('bpy').context.window_manager.windows]}
 k.setup();k.do(lambda:key('F3'),.3);k.do(lambda:k.type_text('Preferences'),.4);k.do(lambda:key('RET'),2)
 k.record('CAD-INSTALL','preferences','F3 開啟 Preferences 窗口',info,win='PREFERENCES')
