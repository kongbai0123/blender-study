"""Inspect extension menus in isolated Preferences without installing anything."""
import bpy
from common import Kit
def build(g):
 k=Kit(g)
 def key(n):k.key(n,x=700,y=500)
 def info():return {'section':bpy.context.preferences.active_section,'extensionsRoot':'isolated environment'}
 k.setup();k.do(lambda:key('F3'),.3);k.do(lambda:k.type_text('Preferences'),.4);k.do(lambda:key('RET'),2)
 k.do(lambda:k.click(75,188,win='PREFERENCES'),1)
 k.record('CAD-INSTALL','extensions','開啟 Get Extensions 分頁',info,win='PREFERENCES')
