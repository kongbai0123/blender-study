"""CAD Sketcher triangle GUI probe: environment bootstrap and view setup only are programmatic."""
import bpy,addon_utils,importlib,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from common import Kit

def build(g):
 k=Kit(g);out=Path(g['OUT']);memo={}
 def bootstrap():
  name='bl_ext.user_default.CAD_Sketcher';addon_utils.enable(name,default_set=True,persistent=True)
  if name not in bpy.context.preferences.addons:raise RuntimeError('CAD Sketcher not enabled')
  bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.001;bpy.context.scene.unit_settings.length_unit='MILLIMETERS';memo['ref']=importlib.import_module(name+'.model.sketch_ref')
 def state():
  s=memo['ref'].get_active_sketch(bpy.context);r={'active':bool(s),'mode':bpy.context.mode}
  if s:
   obj=s.target_object;r.update({'name':s.name,'dof':s.dof,'solver':s.solver_state,'solved':s.geometry_solved,'constraints':[{'type':c.type,'name':c.name,'value':getattr(c,'value',None),'uid':c.constraint_uid} for c in s.constraints.all], 'sceneProps':{key:val for key,val in bpy.context.scene.items() if key.startswith('slvs:c:') and isinstance(val,(int,float))},'positions':[list(p.vector) for p in obj.data.attributes['position'].data] if 'position' in obj.data.attributes else [],'attrs':[a.name for a in obj.data.attributes], 'fixedFlags':[v.value for v in obj.data.attributes['fixed'].data]})
  return json.dumps(r)
 def send(key,**kw):k.do(lambda:k.key(key,x=600,y=450,**kw),.6)
 def frame():
  a=k.area('VIEW_3D');s=a.spaces.active.region_3d;s.view_location=(5.3,.3,0);s.view_distance=3.0;s.view_perspective='ORTHO'
 def at(x,y,click=True):
  a=k.area('VIEW_3D');region=next(r for r in a.regions if r.type=='WINDOW');p=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector((x,y,0)))
  if p is None:raise RuntimeError('projection failed')
  xx=int(region.x+p.x);yy=int(k.window().height-region.y-p.y)
  if not(180<xx<900 and 80<yy<850):raise RuntimeError('offscreen '+str((xx,yy)))
  k.move(xx,yy)
  if click:k.click(xx,yy)
 k.setup();k.do(bootstrap,2);send('A');send('X');send('RET');send('A',ctrl=True,shift=True);send('Z');k.do(frame,1);k.record('CADTRI','blank','GUI 建立 XY 草圖，程式僅設定工作區與視角。',state)
 send('L');k.do(lambda:at(4.8,0),.8);k.record('CADTRI','first-point','GUI Line 第一點',state)
 k.do(lambda:at(6,.3),.8);k.record('CADTRI','second-point','GUI Line 第二點',state)
 k.do(lambda:at(4.8,.6),.8);k.record('CADTRI','third-point','GUI Line 第三點',state)
 k.do(lambda:at(4.8,0),.8);send('ESC');k.record('CADTRI','triangle','GUI Line 閉合三角輪廓',state)


 send('N');k.do(lambda:k.click(1214,264),.7)
 send('D');k.do(lambda:at(4.8,.3),.7);k.do(lambda:at(4.65,.3,False),.5);k.record('CADTRI','base-placement','GUI Dimension 基準邊的標註放置預覽',state);k.do(lambda:at(4.65,.3),.6);send('ESC');k.record('CADTRI','base-dimension','GUI 放置基準邊尺寸，讀回實際值與自由度',state)
 send('D');k.do(lambda:at(5.4,.15),.7);k.do(lambda:at(5.45,.05,False),.5);k.do(lambda:at(5.45,.05),.6);send('ESC');k.record('CADTRI','slope-dimension','GUI 放置斜邊尺寸，讀回約束',state)

 send('E',shift=True);k.do(lambda:at(5.4,.15),.6);k.do(lambda:at(5.4,.45),.6);send('ESC');k.record('CADTRI','equal-sides','GUI 建立兩斜邊相等約束',state)

 k.do(lambda:at(4.8,0),.7);k.record('CADTRI','anchor-selected','GUI 選取定位頂點，準備固定',state)
 k.do(lambda:k.click(471,560,button='RIGHTMOUSE'),.7);k.record('CADTRI','anchor-menu','GUI 開啟頂點內容選單，查看固定選項',state)

 k.do(lambda:k.click(462,563,ctrl=True),.5);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text('4.8'),.4);send('RET');k.record('CADTRI','anchor-coordinate','GUI 將定位點 X 改為 4.8',state)
 k.do(lambda:k.click(471,560,button='RIGHTMOUSE'),.7);k.record('CADTRI','anchor-menu-again','GUI 重新開啟定位點內容選單',state)
 k.menu_item(380,633,1.0);k.record('CADTRI','anchor-fixed','GUI 設定定位點 Fixed，讀回自由度',state)

 k.do(lambda:k.click(471,560,button='RIGHTMOUSE'),.7);k.record('CADTRI','fixed-reopened','再開定位點選單檢查 Fixed 狀態',state)
