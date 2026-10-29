"""Independent world-space comparison of GUI-triangulated scene to source.

Meshes are compared by topology, bounds, volume and bidirectional samples;
sampled maximum is not a bound on all surface differences or a fit certificate.
"""
import bpy,bmesh,hashlib,json,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];name,source,out=args[0],Path(args[1]),Path(args[2])
new=bpy.data.objects[name]
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=[name]
old=dst.objects[0];bpy.context.scene.collection.objects.link(old);bpy.context.view_layer.update()
def run(obj):
 bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.index_update();p=[obj.matrix_world@v.co for v in bm.verts]
 tri=[tuple(l.vert.index for l in t) for t in bm.calc_loop_triangles()]
 seen=set();duplicates=0
 for t in tri:
  key=tuple(sorted(t));duplicates+=int(key in seen);seen.add(key)
 tree=BVHTree.FromPolygons(p,tri,all_triangles=True,epsilon=0)
 overlaps={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tri[a])&set(tri[b])}
 rem=set(bm.verts);components=0
 while rem:
  components+=1;stack=[rem.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in rem:rem.remove(v);stack.append(v)
 result={'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(tri),'exactDuplicateTrianglesByIndices':duplicates,
 'components':components,'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),
 'nonAdjacentBvhCandidates':len(overlaps),'worldBoundsMm':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],
 'signedVolumeMm3':bm.calc_volume(signed=True)*obj.matrix_world.determinant()}
 samples=p+[(p[a]+p[b]+p[c])/3 for a,b,c in tri];bm.free();return result,tree,samples
n,nt,ns=run(new);o,ot,os=run(old)
def dist(samples,tree):
 values=[tree.find_nearest(p)[3] for p in samples];return {'sampleCount':len(values),'maxMm':max(values),'meanMm':sum(values)/len(values)}
result={'newSceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'sourceSceneSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'object':name,'source':o,'triangulated':n,
 'newToSource':dist(ns,ot),'sourceToNew':dist(os,nt),
 'limitations':['Non-planar polygons can change shape with triangulation; source not overwritten.',
  'Sampled maximum is not a global surface deviation bound or proof of fit; zero BVH candidates is not proof of no intersection.',
  'No print, dimensional measurement, fit or strength qualification.']}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
