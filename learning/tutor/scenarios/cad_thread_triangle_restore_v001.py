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
 def verify(label,want):
  data=json.loads(state());values=sorted(c['value'] for c in data['constraints'] if c['type']=='DISTANCE');v=data['positions'];xs=[p[0] for p in v if p[0]>4];ys=[p[1] for p in v if p[0]>4];actual={'label':label,'solver':data['solver'],'dof':data['dof'],'dimensionValues':values,'minX':min(xs),'maxX':max(xs),'minY':min(ys),'maxY':max(ys),'fixedFlags':data['fixedFlags'],'constraints':data['constraints']};checks={'solverOkay':data['solver']=='OKAY','fullyDefined':data['dof']==0,'twoDimensions':len(values)==2,'baseDimension':abs(values[0]-want)<1e-5,'baseHeight':abs((max(ys)-min(ys))-want)<1e-4,'fixedAnchorX':abs(min(xs)-4.8)<1e-4,'expectedApexX':abs(max(xs)-(4.8+(values[1]**2-(want/2)**2)**.5))<.0001,'equalAndVertical':sorted(c['type'] for c in data['constraints'])==['DISTANCE','DISTANCE','EQUAL','VERTICAL']};actual['checks']=checks;(out/(label+'-verification.json')).write_text(json.dumps(actual,indent=2),encoding='utf8')
  if not all(checks.values()):raise RuntimeError('verify failed '+json.dumps(actual))

 from common import PROJECT
 source=PROJECT/'learning/evidence/parametric/2026-10-28-cad-thread-triangle-trial-v001/demo-files/cad_thread_triangle_080_v002.blend'
 if g['sha256'](source)!='8811cfc5223560a5397324dc0d1a61657a42efd301c038c69c7d259fc36c9c70':raise RuntimeError('source hash mismatch')
 copy=Path(k.demo_dir)/source.name;copy.write_bytes(source.read_bytes())
 k.setup();k.do(bootstrap,2);send('O',ctrl=True);k.fill_dialog(k.demo_dir,source.name);k.confirm_dialog(wait=4);k.record('CADREST','source-080','GUI 開啟 0.8 mm 尺寸副本',state);k.do(lambda:verify('source-080',.8),.3)
 k.do(lambda:k.click(1124,641,ctrl=True),.5);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text('0.6mm'),.4);k.do(lambda:k.key('RET'),1.2)
 k.record('CADREST','restored-060','GUI 將基邊尺寸還原為 0.6 mm',state);k.do(lambda:verify('restored-060',.6),.3)
 k.file_dialog(163,k.demo_dir,'cad_thread_triangle_060_restored_v003.blend');k.confirm_dialog(wait=3);k.record('CADREST','saved','GUI 另存還原的 0.6 mm 版本',state)
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,'cad_thread_triangle_060_restored_v003.blend');k.confirm_dialog(wait=4);k.record('CADREST','reopened','GUI 重開還原版，再次核對草圖',state);k.do(lambda:verify('reopened-060',.6),.3)
