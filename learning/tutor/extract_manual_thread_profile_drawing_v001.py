"""Extract the actual three-edge GUI profile to a new portable drawing readback."""
from hashlib import sha256
from pathlib import Path
import json, sys, bpy

ROOT=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:]
if len(args)!=3:raise ValueError('Expected object name, source SHA-256, new output path')
name,expected,out_relative=args
scene=Path(bpy.data.filepath).resolve()
relative=scene.relative_to(ROOT).as_posix()
raw=scene.read_bytes()
if sha256(raw).hexdigest()!=expected:raise ValueError('Scene SHA mismatch')
output=(ROOT/out_relative).resolve()
output.relative_to(ROOT/'learning/evidence')
if output.exists():raise FileExistsError(output)
obj=bpy.data.objects.get(name)
if not obj or obj.type!='MESH':raise ValueError('Mesh object missing')
if abs(bpy.context.scene.unit_settings.scale_length-.001)>1e-7:raise ValueError('Expected millimetre scene scale')
mesh=obj.data
if len(mesh.vertices)!=3 or len(mesh.edges)!=3 or len(mesh.polygons)!=0:raise ValueError('Expected three-point three-edge profile with no faces')
vertices=[list(obj.matrix_world@v.co) for v in mesh.vertices]
edges=[list(e.vertices) for e in mesh.edges]
if any(abs(p[1])>1e-4 or p[0]<=0 for p in vertices):raise ValueError('Expected positive-X profile in XZ plane')
if sorted(sum(1 for edge in edges if i in edge) for i in range(3))!=[2,2,2]:raise ValueError('Profile is not a closed triangle')
d={'schemaVersion':1,'sourceScene':relative,'sourceSha256':expected,'blenderVersion':bpy.app.version_string,'unitScale':bpy.context.scene.unit_settings.scale_length,'object':name,'coordinateSystem':'world mm; X radius, Y=0, Z axial','verticesMm':vertices,'edges':edges,'faces':0,'material':None,'hardware':None,'tolerance':None,'print':None,'measurement':None,'fit':None}
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('drawing-readback',output.relative_to(ROOT).as_posix(),sha256(output.read_bytes()).hexdigest())
