"""Read existing boss scene in background Blender and record actual vertex rings for an engineering draft."""
import hashlib, json, math, sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'learning/evidence/08/2026-10-27-lesson08-boss-draft-v002/demo-files/u08_blind_boss_draft_v001.blend'
EXPECTED='4df306ac6b7e3f57108cb0221fad62480ca47c80f77d5ccd3e91632a6d5c7320'
OUT=ROOT/'learning/evidence/08/2026-10-28-boss-drawing-v001/geometry-readback-v001.json'
if bpy.data.filepath!=str(SOURCE): raise RuntimeError('scene path differs')
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED: raise RuntimeError('source scene hash differs')
if OUT.exists():raise FileExistsError('拒絕覆寫原始讀值')
obj=bpy.data.objects.get('Boss_Blind_Polygon32')
if not obj or obj.type!='MESH' or obj.modifiers:raise RuntimeError('source boss is absent or modified')
points=[tuple(float(x) for x in obj.matrix_world@v.co) for v in obj.data.vertices]
rings={}
for x,y,z in points:
    radius=math.hypot(x,y); key=(round(radius),round(z))
    rings.setdefault(key,[]).append((x,y,z))
expected={(4,0),(4,8),(2,8),(2,1)}
if set(rings)!=expected or any(len(r)!=32 for r in rings.values()):raise RuntimeError('ring structure differs')
def ext(a):return [[min(p[i] for p in a),max(p[i] for p in a)] for i in range(3)]
result={'schemaVersion':1,'sourceScene':'learning/evidence/08/2026-10-27-lesson08-boss-draft-v002/demo-files/u08_blind_boss_draft_v001.blend','sourceSha256':EXPECTED,'blenderVersion':bpy.app.version_string,'buildHash':bpy.app.build_hash.decode(),'object':obj.name,'unitScale':bpy.context.scene.unit_settings.scale_length,'unitInterpretation':'mm','vertexCount':len(points),'faceCount':len(obj.data.polygons),'boundsMm':ext(points),'rings':{str(r)+'@'+str(z):sorted(ring,key=lambda p:math.atan2(p[1],p[0])) for (r,z),ring in rings.items()},'nominalDraft':True,'manufacturer':None,'hardware':None,'material':None,'tolerance':None,'process':None,'physicalFit':None}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('readback',OUT,'sha256',hashlib.sha256(OUT.read_bytes()).hexdigest())
