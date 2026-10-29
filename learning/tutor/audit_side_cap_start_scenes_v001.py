import bpy,hashlib,math,json,os
from pathlib import Path
p=Path(bpy.data.filepath);expected=os.environ['CAP_START_KIND'];cap=bpy.data.objects['Side_Cap_Blank'];source=Path(os.environ['CAP_ORIGINAL_SCENE']);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();cut=bpy.data.objects['Cap_Cutter_020' if expected=='thread' else 'A_Relief_Cutter']
def bounds(o):
 v=[o.matrix_world@x.co for x in o.data.vertices];return [[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]
def sig(o):
 v=[[round(q,7) for q in o.matrix_world@x.co] for x in o.data.vertices];f=[list(x.vertices) for x in o.data.polygons];return hashlib.sha256(json.dumps([v,f],separators=(',',':')).encode()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Body','Lid','Thread_Core']+(['Side_Cap_Blank'] if expected=='relief' else [])
for o in dst.objects:bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update();sources={o.name.split('.')[0]:o for o in dst.objects}
unchanged={name:sig(bpy.data.objects[name])==sig(sources[name]) for name in sources}
if not all(unchanged.values()):raise RuntimeError('source content mismatch '+str(unchanged))
assert bpy.context.view_layer.objects.active==cap and cap.select_get() and len(cap.modifiers)==0
assert not cut.hide_get()
cb=bounds(cut);bb=bounds(cap)
if expected=='thread':
 o=bpy.data.objects['Thread_Core'];v=[o.matrix_world@x.co for x in o.data.vertices];t=[cut.matrix_world@x.co for x in cut.data.vertices];assert len(v)==len(t)
 rd=[math.hypot(y.y,y.z)-math.hypot(x.y,x.z) for x,y in zip(v,t)];ad=[y.x-x.x for x,y in zip(v,t)];detail={'radialDeltaRangeMm':[min(rd),max(rd)],'axialDeltaMaxAbsMm':max(map(abs,ad))};assert max(abs(x-.2) for x in rd)<1e-4 and max(map(abs,ad))<1e-4
 assert len(cap.data.vertices)==128 and abs(cb[0][0]-29.5)<.001 and abs(cb[0][1]-34.3)<.001
else:
 detail={'toolRadiusNominalMm':5.3,'toolAxialBoundsMm':cb[0]};assert len(cap.data.vertices)==806 and abs(cb[0][0]-34.15)<.001 and abs(cb[0][1]-34.5)<.001
report={'sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceSha256':source_sha,'kind':expected,'model':'Side_Cap_Blank','tool':cut.name,'activeSelected':True,'modelModifiers':0,'toolVisible':True,'capVertices':len(cap.data.vertices),'capFaces':len(cap.data.polygons),'toolVertices':len(cut.data.vertices),'boundsCapMm':bb,'boundsToolMm':cb,'sourceGeometryUnchanged':unchanged,'detail':detail,'method':'Independently reopened generated starting scene; checked geometry, active object and source hashes. Both tool/blank are prepared by script, not manually drawn in GUI.','limitations':['Starting files are local teaching assets only; privacy/publication safety has not been reviewed.','Models and nominal clearances are drafts; no physical measurement, print or fit has been performed.']}
out=Path(os.environ['CAP_START_AUDIT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
