import bpy,bmesh,hashlib,math,json,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()=='df2108d06250807a9fa593ce966ae09e42d0fc3b2bfad97c98d0c40f77378c54'
body=bpy.data.objects['Body'];ref=bpy.data.objects['Thread_Core'];assert len(ref.data.vertices)==707
mesh=ref.data.copy();tool=bpy.data.objects.new('Cap_Cutter_Radial_020',mesh);bpy.context.scene.collection.objects.link(tool);tool.matrix_world=ref.matrix_world.copy();inv=tool.matrix_world.inverted()
for v in mesh.vertices:
 w=tool.matrix_world@v.co;r=math.hypot(w.y,w.z);assert r>0
 w.y*=1+.2/r;w.z*=1+.2/r;v.co=inv@w
mesh.update();tool.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=7.7,depth=5.7,location=(32.95,0,0),rotation=(0,math.pi/2,0));cap=bpy.context.object;cap.name='Cap_Blank';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
m=cap.modifiers.new('Difference','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name)
def geom(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];b=BVHTree.FromPolygons(v,t,all_triangles=True);return v,t,b
def checks(o):
 v,t,b=geom(o);bm=bmesh.new();bm.from_mesh(o.data);n=sum(not e.is_manifold for e in bm.edges);r=set(bm.verts);comps=0
 while r:
  comps+=1;st=[r.pop()]
  while st:
   for e in st.pop().link_edges:
    for x in e.verts:
     if x in r:r.remove(x);st.append(x)
 pairs={tuple(sorted((i,j))) for i,j in b.overlap(b) if i!=j and not set(t[i])&set(t[j])};areas=[(v[j]-v[i]).cross(v[k]-v[i]).length/2 for i,j,k in t];out={'vertices':len(v),'faces':len(o.data.polygons),'boundsMm':[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)],'nonManifoldEdges':n,'components':comps,'volume':bm.calc_volume(signed=True),'minTriangleArea':min(areas),'trianglesBelow1eMinus5':sum(a<1e-5 for a in areas),'bvhCandidates':len(pairs)};bm.free();return out
c=checks(cap);bv=geom(body)[2];tv=geom(tool)[2];samples=[]
for x in (30.2,30.5,31.0,31.5,32,32.5,33,33.5,34):
 for deg in range(0,360,15):
  a=math.radians(deg);origin=Vector((x,0,0));direction=Vector((0,math.cos(a),math.sin(a)))
  hp=bv.ray_cast(origin,direction)[0];ht=tv.ray_cast(origin,direction)[0]
  if hp is None or ht is None:raise RuntimeError('ray miss')
  samples.append({'xMm':x,'angleDeg':deg,'bodyRadiusMm':math.hypot(hp.y,hp.z),'toolRadiusMm':math.hypot(ht.y,ht.z),'radialGapMm':math.hypot(ht.y,ht.z)-math.hypot(hp.y,hp.z)})
# Exact Boolean intersection is a finite numerical test, not a complete physical fit test.
bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap
inter=cap.copy();inter.data=cap.data.copy();bpy.context.scene.collection.objects.link(inter);bpy.ops.object.select_all(action='DESELECT');inter.select_set(True);bpy.context.view_layer.objects.active=inter
m=inter.modifiers.new('BodyIntersection','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=body;bpy.ops.object.modifier_apply(modifier=m.name)
bm=bmesh.new();bm.from_mesh(inter.data);iv=abs(bm.calc_volume(signed=True)) if bm.faces else 0; inter_counts={'vertices':len(bm.verts),'faces':len(bm.faces),'absoluteSignedVolumeMm3':iv};bm.free()
report={'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Copy mounted v010 source tool preserving X axial position, phase and topology; radial expand every vertex by 0.2 mm in Y/Z; program-create 64-sided cylinder radius 7.7 mm X=30.1–35.8; apply Exact Difference; test 216 fixed X/angle rays between box Body and cutter plus one Exact Boolean Intersection of box and cap. This is a background numerical probe, not GUI demonstration.','cap':c,'radialSamples':samples,'minimumSampleRadialGapMm':min(s['radialGapMm'] for s in samples),'maximumSampleRadialGapMm':max(s['radialGapMm'] for s in samples),'boxCapBooleanIntersection':inter_counts,'limits':['Nominal radial expansion 0.2 mm is a trial, not a validated normal clearance.','Actual cavity surfaces can be nonplanar; ray samples and numerical Boolean do not prove global interference-free motion or physical fit.','No ISO claim, material, tolerance, strength, slicer, print, measured or fit result.']}
out=Path(os.environ['CAP_MOUNT_PROBE_OUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('cap',c,'gap range',report['minimumSampleRadialGapMm'],report['maximumSampleRadialGapMm'],'intersection',inter_counts)
