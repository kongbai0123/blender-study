import bpy, json, hashlib, os
from pathlib import Path
scene=Path(bpy.data.filepath)
expected='a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80'
assert hashlib.sha256(scene.read_bytes()).hexdigest()==expected
obj=bpy.data.objects['Cube']; assert obj.type=='MESH' and not obj.modifiers
mesh=obj.data; mesh.calc_loop_triangles()
verts=[list(obj.matrix_world @ v.co) for v in mesh.vertices]
triangles=[list(t.vertices) for t in mesh.loop_triangles]
data={'source':'learning/evidence/08/2026-10-28-inner-boolean-trial-v003/demo-files/u08_inner_boolean_trial_v003.blend','sourceSha256':expected,'object':'Cube','unit':'mm','vertices':verts,'triangles':triangles,'bounds':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],'method':'World-space mesh vertices and loop triangles; no modifier; Blender 5.2.1'}
out=Path(os.environ['INNER_DRAWING_OUT'])
with out.open('x',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print('vertices',len(verts),'triangles',len(triangles),'bounds',data['bounds'])
