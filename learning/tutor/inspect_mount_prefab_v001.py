"""Independently check prefab object data against original source blend objects."""
import bpy,json,hashlib,os
from pathlib import Path
root=Path(os.environ['MOUNT_AUDIT_ROOT']); out=root/'learning/evidence/08/2026-10-29-external-thread-mount-prefab-v001'; box=root/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'; thread=root/'learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/demo-files/u08_external_gui_draft_v003.blend'
def sig(o):
 return {'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'matrix':[[float(n) for n in row] for row in o.matrix_world], 'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale)}
actual={n:sig(bpy.data.objects[n]) for n in ('Body','Lid','Thread_Core')}; checks={}
for path,names in ((box,['Body','Lid']),(thread,['Thread_Core'])):
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=list(names)
 for n,o in zip(names,dst.objects):
  bpy.context.scene.collection.objects.link(o); bpy.context.view_layer.update(); s=sig(o); checks[n]={k:(actual[n][k]==s[k]) for k in s};checks[n]['vertexCount']=len(s['verts']);checks[n]['faceCount']=len(s['faces'])
  if not all(checks[n][k] for k in ('verts','faces','matrix','location','rotation','scale')):raise RuntimeError('mismatch '+n+' '+json.dumps(checks[n]))
old=json.loads(json.loads((root/'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/run.json').read_text(encoding='utf8'))['records'][0]['observed']); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=out/'demo-files/u11_mount_prefab_v001.blend'; result={'sceneSha256':sha(p),'sourceBoxSha256':sha(box),'sourceThreadSha256':sha(thread),'exactComparisonToSources':checks,'priorRunStep1':old,'limits':'獨立背景重開；精確比對局部網格索引與矩陣，原版第1步僅有三物件外框與牙條位置可對照，非該歷史場景完整逐點證明。未實印、量測或試配。','physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None};(out/'independent-audit-v001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(checks))


