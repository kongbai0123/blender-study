import bpy,bmesh,hashlib,os,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['MOUNT_DRAWING_SOURCE_SHA256']
o=bpy.data.objects['Body'];assert not o.modifiers;m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles];bvh=BVHTree.FromPolygons(pts,tris,all_triangles=True)
bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table();bm.verts.index_update(); directions={'top':Vector((0,0,1)),'front':Vector((0,-1,0)),'right':Vector((1,0,0))}; lines={key:[] for key in directions}
for e in bm.edges:
 if len(e.link_faces)==2 and e.link_faces[0].normal.dot(e.link_faces[1].normal)>0.999999:continue
 a=o.matrix_world@e.verts[0].co;b=o.matrix_world@e.verts[1].co;mid=(a+b)/2
 for key,dr in directions.items():
  if len(e.link_faces)==2 and all(f.normal.dot(dr)<-1e-7 for f in e.link_faces):continue
  hit,normal,index,distance=bvh.ray_cast(mid+dr*150,-dr)
  if hit is not None and (hit-mid).length<0.0001:lines[key].append([list(a),list(b)])
bm.free()
cut=0.123456;segments=set()
for tri in tris:
 hits=[]
 for i in range(3):
  a,b=pts[tri[i]],pts[tri[(i+1)%3]];da,db=a.y-cut,b.y-cut
  if da*db<0:
   f=da/(da-db);q=a+(b-a)*f;hits.append((q.x,q.z))
  elif abs(da)<1e-9:hits.append((a.x,a.z))
 u=[]
 for h in hits:
  if all(math.dist(h,t)>1e-7 for t in u):u.append(h)
 if len(u)==2:segments.add(tuple(sorted(tuple(round(i,6) for i in h) for h in u)))
 elif len(u)>2:raise RuntimeError('coplanar cut ambiguity')
report={'sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'object':'Body','boundsMm':[[min(q[i] for q in pts),max(q[i] for q in pts)] for i in range(3)],'method':'Mesh world-space edges; front, top and right orthographic projection, visibility by midpoint ray against triangulated mesh and coplanar edges suppressed. Section from all triangles intersecting Y=0.123456 mm. Midpoint occlusion is approximate, not formal hidden-line processing.','projections':lines,'cutYmm':cut,'section':list(segments)}
out=Path(os.environ['MOUNT_DRAWING_MESH']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,separators=(',',':'))
print('projection edge counts',[(k,len(v)) for k,v in lines.items()],'section',len(segments),'sha',hashlib.sha256(out.read_bytes()).hexdigest())
