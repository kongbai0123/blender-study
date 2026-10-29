import bpy,bmesh,hashlib,json,math,os
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()=='453f6c4b9682098aaefea5cfb9501a74c70a562f14c5a0215709101b5b71871d'
cap=bpy.data.objects['Side_Cap_Blank'];body=bpy.data.objects['Body'];n=int(os.environ.get('RELIEF_SEGMENTS','64'));phase=float(os.environ.get('RELIEF_PHASE','0'))
bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=5.3,depth=.35,location=(34.325,0,0),rotation=(0,math.pi/2,0));c=bpy.context.object;c.name='Relief_Cutter_Probe';c.rotation_mode='QUATERNION';c.rotation_quaternion=Quaternion((1,0,0),math.radians(phase))@Quaternion((0,1,0),math.pi/2);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap
mod=cap.modifiers.new('Relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=cap.data;mesh.calc_loop_triangles();v=[cap.matrix_world@q.co for q in mesh.vertices];t=[tuple(q.vertices) for q in mesh.loop_triangles];tree=BVHTree.FromPolygons(v,t,all_triangles=True)
areas=[(v[j]-v[i]).cross(v[k]-v[i]).length/2 for i,j,k in t];pairs={tuple(sorted((i,j))) for i,j in tree.overlap(tree) if i!=j and not set(t[i])&set(t[j])};bm=bmesh.new();bm.from_mesh(mesh);r=set(bm.verts);comps=0
while r:
 comps+=1;st=[r.pop()]
 while st:
  for e in st.pop().link_edges:
   for x in e.verts:
    if x in r:r.remove(x);st.append(x)
ray=tree.ray_cast(Vector((32,0,0)),Vector((1,0,0)))[0];assert ray is not None
report={'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'segments':n,'phaseDegrees':phase,'method':'Program-only probe: cylinder radius 5.3 mm, X 34.15–34.5 mm; Exact Difference from saved v001 cap. Source unchanged.','cap':{'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':comps,'minimumTriangleAreaMm2':min(areas),'triangleCountBelow1eMinus5Mm2':sum(x<1e-5 for x in areas),'shortestMeshEdgeMm':min((v[e.vertices[1]]-v[e.vertices[0]]).length for e in mesh.edges),'bvhCandidates':len(pairs),'axialCavityBottomRayX':ray.x,'bounds':[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)]},'limits':['Only 1 central ray verifies bottom; relief clips portion of thread near terminal end.','zero BVH/manifold checks do not prove no defects, fit, clearance, or printability.']};bm.free()
out=Path(os.environ['RELIEF_OUTPUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report))
