import bpy,bmesh,json,os,hashlib,math
from mathutils.bvhtree import BVHTree
from pathlib import Path
scene=Path(bpy.data.filepath);assert hashlib.sha256(scene.read_bytes()).hexdigest()=='afdefc6f01947e0a6ecb11cd77ffbb1f1e36dc4c12f06ef9132c4b087fd99baf'
tooth=bpy.data.objects['Thread_Triangle_Profile'];tooth.hide_set(False)
assert len(tooth.data.vertices)==387 and len(tooth.data.polygons)==386
out=[]
for n,r,angle in [(32,5,0),(32,5,5.625),(32,5,2.8125),(32,5.05,0),(32,5.05,5.625),(48,5,0),(64,5,0),(64,5,2.8125)]:
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=4.6,location=(0,0,2.3),rotation=(0,0,math.radians(angle)))
 o=bpy.context.object;o.name='Diagnostic_Core';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 mod=o.modifiers.new('Diagnostic_Union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=tooth
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
 pts=[o.matrix_world @ v.co for v in bm.verts];tris=[tuple(l.vert.index for l in t) for t in bm.calc_loop_triangles()]
 bvh=BVHTree.FromPolygons(pts,tris,all_triangles=True,epsilon=0);pairs=set()
 for a,b in bvh.overlap(bvh):
  if a!=b and not set(tris[a])&set(tris[b]):pairs.add(tuple(sorted((a,b))))
 areas=[((pts[t[1]]-pts[t[0]]).cross(pts[t[2]]-pts[t[0]])).length/2 for t in tris]
 edges=[(o.matrix_world @ e.verts[0].co-o.matrix_world @ e.verts[1].co).length for e in bm.edges]
 unseen=set(bm.verts);components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in unseen:unseen.remove(v);stack.append(v)
 result={'coreVertices':n,'coreRadiusMm':r,'coreRotationDeg':angle,'vertices':len(bm.verts),'faces':len(bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,'minimumTriangleAreaMm2':min(areas),'triangleAreaBelow1eMinus5Count':sum(a<1e-5 for a in areas),'minimumEdgeMm':min(edges),'bvhCandidatePairs':len(pairs),'signedVolumeMm3':bm.calc_volume(signed=True),'boundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]}
 out.append(result);print(json.dumps(result))
 bm.free();bpy.data.objects.remove(o,do_unlink=True)
report={'source':'learning/evidence/08/2026-10-28-external-thread-gui-trial-v005/demo-files/u08_external_gui_draft_v001.blend','sourceSha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'method':'Independent Blender background; repeated Boolean Union Exact using retained GUI-produced triangle-thread as operand and regenerated cylinder; current scene not saved. Core rotations applied. BVH ignores triangle pairs sharing vertex indices.','runs':out,'limitations':['Candidates are not proof of true crossing; BVH zero does not prove no intersection.','Small triangles can result from boolean; threshold is diagnostic, not manufacturing standard.','Changed core geometry changes the model; no tolerance, ISO thread, physical fit, strength or printing claim.','Normals, orientation, disconnected nested shells, mesh cross-sections, more robust independent intersection, and physical processes require further validation.']}
p=Path(os.environ['THREAD_DIAGNOSTICS_OUTPUT'])
with p.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
