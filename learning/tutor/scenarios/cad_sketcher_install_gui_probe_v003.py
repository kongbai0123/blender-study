"""Inspect Install from Disk menu in isolated Preferences without installing."""
import bpy
from common import Kit
def build(g):
 k=Kit(g)
 def key(n):k.key(n,x=700,y=500)
 def info():return {'section':bpy.context.preferences.active_section,'installPerformed':False}
 k.setup();k.do(lambda:key('F3'),.3);k.do(lambda:k.type_text('Preferences'),.4);k.do(lambda:key('RET'),2)
 k.do(lambda:k.click(75,188,win='PREFERENCES'),.8);k.do(lambda:k.click(822,18,win='PREFERENCES'),.7)
 k.record('CAD-INSTALL','menu','展開 Extensions 選單',info,win='PREFERENCES')
