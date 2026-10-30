"""Verify useful default-keymap operations in isolated Blender; transforms use events."""
import json
from pathlib import Path
import bpy
from common import Kit

def build(g):
 k=Kit(g);out=Path(g['OUT']);checks=[]
 def key(name,**kw):k.do(lambda:k.key(name,x=650,y=450,**kw),.35)
 def text(t):k.do(lambda:k.type_text(t),.25)
 def search(t):key('F3');text(t);key('RET')
 def typed(op,axis,value):key(op);key(axis);text(value);key('RET')
 def state():
  w=k.window();s=w.scene;meshes=sorted([o for o in s.objects if o.type=='MESH'],key=lambda o:o.location.x)
  return {'objects':[{'name':o.name,'mesh':o.data.name,'location':list(o.location),'dimensions':list(o.dimensions),'scale':list(o.scale)} for o in meshes],'blender':bpy.app.version_string,'unitScale':s.unit_settings.scale_length}
 def shot(slug,action,test=None):
  def observe():
   d=state();passed=True if test is None else bool(test(d));checks.append({'case':slug,'passed':passed,'readback':d});assert passed,(slug,d);return d
  k.record('EFF',slug,action,observe,note='Factory Blender default keymap; only unit display and initial selection prepared with Python. Geometry, duplicates and transforms performed through simulated UI events.')
 k.setup()
 def setup():
  w=k.window();w.scene.unit_settings.system='METRIC';w.scene.unit_settings.scale_length=.001;w.scene.unit_settings.length_unit='MILLIMETERS'
 k.do(setup,.4)
 key('F2');text('Test_Pin');key('RET');shot('rename-f2','Object Mode 按 F2 更名 Test_Pin；不用逐層找物件選單。',lambda d:d['objects'][0]['name']=='Test_Pin')
 typed('S','X','5');typed('S','Y','5');typed('S','Z','4')
 search('Apply Scale');search('Frame Selected');key('N');shot('numeric-size','數值縮放建立 10×10×8 mm 試片，F3 Apply Scale 後核對 Scale 1。',lambda d:all(abs(a-b)<1e-4 for a,b in zip(d['objects'][0]['dimensions'],[10,10,8])) and all(abs(v-1)<1e-6 for v in d['objects'][0]['scale']))
 key('D',shift=True);key('X');text('14mm');key('RET');shot('duplicate-shift-d','Shift+D → X → 14mm → Enter；建立獨立網格副本，方便之後改各自孔寬。',lambda d:len(d['objects'])==2 and len(set(o['mesh'] for o in d['objects']))==2 and abs(d['objects'][1]['location'][0]-14)<1e-5)
 key('R',shift=True);key('NUMPAD_7');key('HOME');shot('repeat-shift-r','Shift+R 重複剛才的複製位移，核對三件中心 X 為 0、14、28 mm。',lambda d:len(d['objects'])==3 and all(abs(o['location'][0]-x)<1e-5 for o,x in zip(d['objects'],[0,14,28])))
 key('F9');shot('adjust-f9','F9 開啟最後一次操作的調整面板；只觀察，不任意改已核對數值。');key('ESC')
 key('Z');key('ESC');shot('cancel-modal','Esc 取消 Z shading pie，保留原幾何與數值。',lambda d:len(d['objects'])==3)
 def finish():
  assert all(c['passed'] for c in checks)
  with bpy.context.temp_override(window=k.window(),area=k.area('VIEW_3D')):bpy.ops.wm.save_as_mainfile(filepath=str(out/'demo-files/efficient-pin-array-v001.blend'))
  (out/'verification.json').write_text(json.dumps({'checks':checks,'keymap':'Blender default','physicalPrint':None,'physicalFit':None},ensure_ascii=False,indent=2)+'\n','utf8')
 k.do(finish,.6)
