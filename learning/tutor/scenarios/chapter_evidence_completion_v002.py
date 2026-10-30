"""Independent digital preparation photos; never claims physical or web actions occurred.
Sources are copied/opened with Python and selection/context prepared with RNA.
Actual viewport navigation, sidebar and framing use simulated Blender input.
"""
import hashlib,json,shutil
from pathlib import Path
import bpy
from common import Kit,PROJECT

def build(g):
 k=Kit(g);out=Path(g['OUT']);plan=PROJECT/'learning/patches/2026-10-30-chapter-completion-v040/capture-plan.json'
 jobs=json.loads(plan.read_text('utf8'))['jobs'];memory={};results=[];copies=out/'demo-files';copies.mkdir(exist_ok=True)
 def send(name,**kw):k.do(lambda:k.key(name,x=650,y=450,**kw),.22)
 def search(text):
  send('F3');k.do(lambda:k.type_text(text),.22);send('RET')
 def prepare(job):
  source=PROJECT/job['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==job['sourceSha256']
  target=copies/(job['stepId']+'-reference.blend');shutil.copyfile(source,target)
  bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
  bpy.context.preferences.view.language='en_US';bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
  w=k.window();scene=w.scene;layer=w.view_layer
  scene.name=job['stepId']+' (digital reference)'
  if layer.objects.active and layer.objects.active.mode!='OBJECT':
   with bpy.context.temp_override(window=w,area=k.area('VIEW_3D')):bpy.ops.object.mode_set(mode='OBJECT')
  objects=[o for o in scene.objects if o.type=='MESH' and not o.hide_get()]
  assert objects,'no visible geometry'
  objects.sort(key=lambda o:(-float(o.dimensions.x*o.dimensions.y*o.dimensions.z),o.name))
  for o in layer.objects:
   if o.select_get():o.select_set(False)
  obj=objects[0];obj.select_set(True);layer.objects.active=obj
  a=k.area('VIEW_3D');a.spaces.active.overlay.show_stats=True
  memory.update(job=job,target=target,active=obj.name)
 def observe():
  j=memory['job'];w=k.window();scene=w.scene;o=w.view_layer.objects.active;u=scene.unit_settings
  result={'stepId':j['stepId'],'role':j['role'],'purpose':j['purpose'],'source':j['source'],'sourceSha256':j['sourceSha256'],'copy':memory['target'].name,'active':o.name,'mode':o.mode,'dimensionsMM':[float(v*u.scale_length*1000) for v in o.dimensions],'scale':list(o.scale),'objects':sorted(o.name for o in scene.objects),'view':k.area('VIEW_3D').spaces.active.region_3d.view_perspective,'unitSystem':u.system,'unitScale':u.scale_length,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'preparation':'Python copies and opens unchanged source, selects mesh and labels scene; viewport keys are simulated UI events.'}
  results.append(result);return result
 k.setup()
 for i,job in enumerate(jobs):
  k.do(lambda j=job:prepare(j),1.0)
  send(job['view']);search('Frame Selected')
  k.do(lambda:k.key('N',x=650,y=450) if not k.area('VIEW_3D').spaces.active.show_region_ui else None,.35)
  k.record(job['stepId'],'independent-reference',job['purpose']+' 以數字鍵盤正交視角、F3 Frame Selected 與 N 側欄核對。',observe,
   highlights=lambda:[k.rect('OUTLINER','物件來源')],note='本圖是獨立 Blender 的數位準備／來源參考，不是網頁登記、實體量測、列印或試配證據。來源開啟、物件選取及場景名稱由程式準備；未建立或修改學員工作檔。')
 def finish_manifest():
  assert len(results)==30
  (out/'step-evidence.json').write_text(json.dumps({'blender':bpy.app.version_string,'steps':results,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None},ensure_ascii=False,indent=2)+'\n','utf8')
 k.do(finish_manifest,.2)
