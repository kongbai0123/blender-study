"""Test explicit mesh triangulation in memory, no saved changes or STL output."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];objname,out=args[0],Path(args[1]);obj=bpy.data.objects[objname]
def analyse(bm):
 bm.verts.index_update();points=[obj.matrix_world@v.co for v in bm.verts]
 loops=bm.calc_loop_triangles();tris=[tuple(l.vert.index for l in t) for t in loops]
 seen={};duplicates=[]
 for i,t in enumerate(tris):
  sig=tuple(sorted(t))
  if sig in seen:duplicates.append([seen[sig],i])
  else:seen[sig]=i
 tree=BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0)
 pairs={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tris[a])&set(tris[b])}
 remaining=set(bm.verts);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   for edge in stack.pop().link_edges:
    for v in edge.verts:
     if v in remaining:remaining.remove(v);stack.append(v)
 samples=points+[(points[a]+points[b]+points[c])/3 for a,b,c in tris]
 return {'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(tris),'duplicateTrianglesByExactIndices':len(duplicates),
  'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'components':components,
  'nonAdjacentBvhCandidates':len(pairs),'signedVolumeMm3':bm.calc_volume(signed=True),'boundsMm':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]},tree,samples
original=bmesh.new();original.from_mesh(obj.data);reference,ref_tree,ref_samples=analyse(original);tests=[]
for method in ('BEAUTY','EAR_CLIP'):
 bm=original.copy();bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method=method)
 details,tree,samples=analyse(bm)
 a=[ref_tree.find_nearest(p)[3] for p in samples];b=[tree.find_nearest(p)[3] for p in ref_samples]
 details.update(method=method,newToSourceSampleMaxMm=max(a),sourceToNewSampleMaxMm=max(b),sampleCounts=[len(a),len(b)])
 tests.append(details);bm.free()
original.free();result={'object':objname,'source':reference,'tests':tests,'limitations':'In-memory numerical experiment, not GUI, no saved files; zero BVH and sampled distances are not proof of printability or complete surface equivalence.'}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
