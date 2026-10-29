"""Extract actual box/lid orthographic edge samples and a world-space section."""
import bpy,bmesh,hashlib,json,math,sys,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:]
if len(args)!=3:raise ValueError('Expected object name, source SHA, new output path')
name,expected,output=args
scene=Path(bpy.data.filepath).resolve();scene.relative_to(ROOT)
if hashlib.sha256(scene.read_bytes()).hexdigest()!=expected:raise ValueError('scene SHA mismatch')
out=(ROOT/output).resolve();out.relative_to(ROOT/'learning/evidence')
if out.exists():raise FileExistsError(out)
o=bpy.data.objects.get(name)
if not o or o.type!='MESH' or o.modifiers:raise ValueError('Expected baked mesh with no modifiers')
if abs(bpy.context.scene.unit_settings.scale_length-.001)>1e-7:raise ValueError('Unexpected unit scale')
m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles]
if not pts or not tris:raise ValueError('empty mesh')
bvh=BVHTree.FromPolygons(pts,tris,all_triangles=True);bm=bmesh.new();bm.from_mesh(m);bm.transform(o.matrix_world);bm.normal_update()
directions={'top':Vector((0,0,1)),'bottom':Vector((0,0,-1)),'front':Vector((0,-1,0)),'right':Vector((1,0,0))};lines={key:[] for key in directions}
for e in bm.edges:
 if len(e.link_faces)==2 and e.link_faces[0].normal.dot(e.link_faces[1].normal)>0.999999:continue
 a,b=e.verts[0].co,e.verts[1].co;mid=(a+b)/2
 for key,dr in directions.items():
  visible=False
  for face in e.link_faces:
   if face.normal.dot(dr)<=1e-7:continue
   center=face.calc_center_median()
   for amount in (0.0001,0.001):
    sample=mid+(center-mid)*amount;hit,_,_,_=bvh.ray_cast(sample+dr*150,-dr)
    if hit is not None and (hit-sample).length<0.0002:visible=True;break
   if visible:break
  if visible:lines[key].append([list(a),list(b)])
bm.free()
# The highest horizontal faces are unobstructed when viewed from +Z. Include
# triangle-boundary edges exactly so round-hole outlines are not lost in sampling.
zmax=max(p.z for p in pts)
top_faces=[t for t in tris if all(abs(pts[i].z-zmax)<1e-5 for i in t)]
counts=collections.Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in top_faces for i in range(3))
boundary=[edge for edge,count in counts.items() if count==1]
if not boundary:raise ValueError('no top face boundary')
lines['top'].extend([[list(pts[a]),list(pts[b])] for a,b in boundary])
cut=.123456;segments=set()
for tri in tris:
 hits=[]
 for i in range(3):
  a,b=pts[tri[i]],pts[tri[(i+1)%3]];da,db=a.y-cut,b.y-cut
  if da*db<0:
   q=a+(b-a)*(da/(da-db));hits.append((q.x,q.z))
  elif abs(da)<1e-9:hits.append((a.x,a.z))
 unique=[]
 for h in hits:
  if all(math.dist(h,t)>1e-7 for t in unique):unique.append(h)
 if len(unique)==2:segments.add(tuple(sorted(tuple(round(v,6) for v in h) for h in unique)))
 elif len(unique)>2:raise ValueError('ambiguous coplanar triangle')
if not segments or any(not edges for edges in lines.values()):raise ValueError('no projection/section data')
d={'schemaVersion':1,'sourceScene':scene.relative_to(ROOT).as_posix(),'sceneSha256':expected,'object':name,'boundsMm':[[min(q[i] for q in pts),max(q[i] for q in pts)] for i in range(3)],'method':'World-space mesh edges sampled for visibility; top-plane triangle boundary included directly. Approximate occlusion, not formal hidden-line view. Section is triangle intersections with Y=0.123456 mm.','topPlaneBoundaryCount':len(boundary),'projections':lines,'cutYmm':cut,'section':sorted(segments)}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
print('box-lid-drawing-readback',out.relative_to(ROOT).as_posix(),hashlib.sha256(out.read_bytes()).hexdigest())
