import bpy,bmesh,hashlib,json,math,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['CAP_SCENE_SHA']
source=Path(os.environ['CAP_SOURCE_BOX']);assert hashlib.sha256(source.read_bytes()).hexdigest()=='df2108d06250807a9fa593ce966ae09e42d0fc3b2bfad97c98d0c40f77378c54'
cap=bpy.data.objects['Side_Cap_Blank'];body=bpy.data.objects['Body'];tool=bpy.data.objects['Cap_Cutter_020'];orig=bpy.data.objects['Thread_Core'];lid=bpy.data.objects['Lid']
def signature(o):
 d={'v':[[round(x,7) for x in o.matrix_world@v.co] for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons]};return hashlib.sha256(json.dumps(d,separators=(',',':')).encode()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Body','Lid','Thread_Core']

for x in dst.objects:bpy.context.scene.collection.objects.link(x)
bpy.context.view_layer.update()
sourceobjs={x.name.split('.')[0]:x for x in dst.objects};checks={o.name:signature(o)==signature(sourceobjs[o.name]) for o in (body,lid,orig)}
if not all(checks.values()):raise RuntimeError('source scene objects differ '+str(checks))
def geom(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
vs,ts,bt=geom(body);vc,tc,ct=geom(cap);vt,tt,ttree=geom(tool);bv=geom(orig)[0]
assert len(vt)==len(bv)
vertex_errors=[]
for a,b in zip(vt,bv):
 delta=math.hypot(a.y,a.z)-math.hypot(b.y,b.z);vertex_errors.append({'radialDiff':delta,'axialDiff':a.x-b.x})
bm=bmesh.new();bm.from_mesh(cap.data);remaining=set(bm.verts);comps=0
while remaining:
 comps+=1;stack=[remaining.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in remaining:remaining.remove(v);stack.append(v)
areas=[(vc[j]-vc[i]).cross(vc[k]-vc[i]).length/2 for i,j,k in tc];pairs={tuple(sorted((i,j))) for i,j in ct.overlap(ct) if i!=j and not set(tc[i])&set(tc[j])};non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
samples=[]
for x in (30.4,30.7,31,31.5,32,32.5,33,33.5,34):
 for deg in range(0,360,15):
  a=math.radians(deg);o=Vector((x,0,0));d=Vector((0,math.cos(a),math.sin(a)));hb=bt.ray_cast(o,d)[0];ht=ttree.ray_cast(o,d)[0];hc=ct.ray_cast(o,d)[0]
  if None in (hb,ht,hc):raise RuntimeError('ray miss '+str((x,deg)))
  rb=math.hypot(hb.y,hb.z);rt=math.hypot(ht.y,ht.z);rc=math.hypot(hc.y,hc.z)
  samples.append({'xMm':x,'angleDeg':deg,'bodyRadiusMm':rb,'toolRadiusMm':rt,'capInnerRadiusMm':rc,'bodyToCapRadialMm':rc-rb,'capToToolRadiusDeltaMm':rc-rt})
# One exact boolean intersection on a transient copy, no source mutation.
tmp=cap.copy();tmp.data=cap.data.copy();bpy.context.scene.collection.objects.link(tmp);bpy.ops.object.select_all(action='DESELECT');tmp.select_set(True);bpy.context.view_layer.objects.active=tmp
m=tmp.modifiers.new('Interference_Test','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=body;bpy.ops.object.modifier_apply(modifier=m.name);bm=bmesh.new();bm.from_mesh(tmp.data);inter={'vertices':len(bm.verts),'faces':len(bm.faces),'volumeMm3':abs(bm.calc_volume(signed=True)) if len(bm.faces) else 0};bm.free()
axialRays=[]
for y,z in [(0,0),(2,0),(-2,0),(0,2),(0,-2),(4,0),(-4,0),(0,4),(0,-4)]:
 h=ct.ray_cast(Vector((32,y,z)),Vector((1,0,0)))[0];assert h is not None
 axialRays.append({'y':y,'z':z,'bottomX':h.x,'endGapFromExternalTipMm':h.x-34.3})
report={'axialRays':axialRays,'sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'object':cap.name,'construction':'Tool from source mounted outer-thread mesh vertex-wise radial +0.2 mm in YZ; X unchanged; retained mesh and phase. Blank nominal radius 7.7 mm, 64 vertices, phase 2.8125 degrees, X=30.3..35.8 mm; GUI applied second Difference using program-prepared cylindrical relief at X=34.15..34.5, saved and reopened.','sourceMeshUnchanged':checks,'vertexCount':len(vc),'faceCount':len(cap.data.polygons),'boundsMm':[[min(q[i] for q in vc),max(q[i] for q in vc)] for i in range(3)],'nonManifoldEdges':non,'components':comps,'signedVolumeMm3':volume,'minimumTriangleAreaMm2':min(areas),'triangleCountBelow1eMinus5Mm2':sum(a<1e-5 for a in areas),'shortestOriginalMeshEdgeMm':min((vc[e.vertices[1]]-vc[e.vertices[0]]).length for e in cap.data.edges),'bvhNonSharedVertexCandidates':len(pairs),'vertexRadialDeltaMinMm':min(x['radialDiff'] for x in vertex_errors),'vertexRadialDeltaMaxMm':max(x['radialDiff'] for x in vertex_errors),'vertexAxialDeltaMaxAbsMm':max(abs(x['axialDiff']) for x in vertex_errors),'samples':samples,'sampleBodyToCapMinMm':min(s['bodyToCapRadialMm'] for s in samples),'sampleBodyToCapMaxMm':max(s['bodyToCapRadialMm'] for s in samples),'sampleCapToToolMaxAbsMm':max(abs(s['capToToolRadiusDeltaMm']) for s in samples),'booleanIntersection':inter,'limitations':['Nonzero δ is nominal vertex radial increase, not proven uniform normal clearance or physical fit.','9 axial slices × 24 angles and one static exact Boolean intersection cannot rule out all geometric interference, rotation path collision, or manufacturing issues.','1e-5 mm² is diagnostic only; a minimum above it does not imply no slender facets.','Material, standard, manufacturing, printing, measurement, clearance approval and fit remain undetermined.']}
out=Path(os.environ['CAP_AUDIT_OUTPUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False))
