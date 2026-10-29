import bpy,bmesh,hashlib,math,json,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()=='5a0aea1af13f46e9bff1b14327aa199b6b34f421936fd5a516226fc13072ec04'
reference=bpy.data.objects['Thread_Core'];original=bpy.data.objects['Thread_Triangle_Profile'];assert len(original.data.vertices)==387
# The saved tooth is program-prepared for this probe by exact radial-only displacement of v010 tooth vertices.
def make_tool(delta):
 mesh=original.data.copy(); tooth=bpy.data.objects.new('ProbeTooth',mesh);bpy.context.scene.collection.objects.link(tooth);tooth.location=original.location;tooth.rotation_euler=original.rotation_euler;tooth.scale=original.scale
 for v in mesh.vertices:
  r=math.hypot(v.co.x,v.co.y);assert r>0;v.co.x*=1+delta/r;v.co.y*=1+delta/r
 tooth.hide_set(False)
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=5+delta,depth=4.8,location=(0,0,2.3),rotation=(0,0,math.radians(5.625)))
 core=bpy.context.object;core.name='ProbeTool';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 m=core.modifiers.new('Union','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=tooth;bpy.ops.object.modifier_apply(modifier=m.name)
 return core,tooth
def bvh(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];return BVHTree.FromPolygons(v,t,all_triangles=True),v,t
def measure(o):
 tree,v,t=bvh(o);bm=bmesh.new();bm.from_mesh(o.data);edges=sum(not e.is_manifold for e in bm.edges);remaining=set(bm.verts);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for q in e.verts:
     if q in remaining:remaining.remove(q);stack.append(q)
 areas=[(v[y]-v[x]).cross(v[z]-v[x]).length/2 for x,y,z in t];pairs={tuple(sorted((x,y))) for x,y in tree.overlap(tree) if x!=y and not set(t[x])&set(t[y])};bm.free()
 return {'bounds':[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)],'vertices':len(v),'faces':len(o.data.polygons),'nonManifoldEdges':edges,'components':components,'minimumTriangleArea':min(areas),'countTrianglesBelow1eMinus5':sum(x<1e-5 for x in areas),'bvhCandidates':len(pairs)}
def ray(tree,z,angle):
 hit,normal,index,dist=tree.ray_cast(Vector((0,0,z)),Vector((math.cos(angle),math.sin(angle),0)));assert hit is not None
 return math.hypot(hit.x,hit.y)
r=bvh(reference)[0]; runs=[]
for delta in (0,0.2):
 core,tooth=make_tool(delta);t=bvh(core)[0];samples=[]
 for z in (0.2,0.3,0.7,1.3,2.3,3.3,4.3,4.5):
  for deg in range(0,360,11):
   angle=math.radians(deg);rv=ray(r,z,angle);tv=ray(t,z,angle);samples.append({'z':z,'angleDeg':deg,'referenceRadius':rv,'toolRadius':tv,'radialDifference':tv-rv})
 diffs=[s['radialDifference'] for s in samples];runs.append({'delta':delta,'tool':measure(core),'samplesCount':len(samples),'minimumRadialDifference':min(diffs),'maximumRadialDifference':max(diffs),'maxDeviationFromTarget':max(abs(v-delta) for v in diffs),'samples':samples})
 bpy.data.objects.remove(core,do_unlink=True);bpy.data.objects.remove(tooth,do_unlink=True)
report={'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'At retained v010 tooth vertices add delta to radial coordinates only; rebuild 32-vertex cylinder radius 5+delta, depth 4.8, axial center 2.3, phase 5.625°, Exact Union; local radial rays from axis, 8 heights × 33 angles. No axial scale or pitch modification.','runs':runs,'limitations':['Sampled rays only; do not prove uniform clearance, surface offset, freedom from self-intersection, manufacturability, or fit.','Nominal 0.4 mm diameter change at corresponding vertices is an experiment, not approved clearance.','This background numerical probe does not perform GUI or produce a usable deliverable.']}
out=Path(os.environ['CAP_PROBE_OUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
for run in runs:print({k:v for k,v in run.items() if k!='samples'})
