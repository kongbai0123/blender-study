import bpy,bmesh,math,json,os,hashlib
from mathutils.bvhtree import BVHTree
from pathlib import Path
p=Path(bpy.data.filepath);sha=hashlib.sha256(p.read_bytes()).hexdigest();target={'5a0aea1af13f46e9bff1b14327aa199b6b34f421936fd5a516226fc13072ec04':'Thread_Core','b97a021c1422ced95b17a80893195df1907a725eb2e53789e0992a23793320ce':'Body'}[sha]
o=bpy.data.objects[target];mesh=o.data;assert not o.modifiers
mesh.calc_loop_triangles();points=[o.matrix_world@v.co for v in mesh.vertices];tris=[tuple(t.vertices) for t in mesh.loop_triangles]
areas=[]
for t in tris:
 a,b,c=[points[i] for i in t];area=(b-a).cross(c-a).length/2;lengths=[(b-a).length,(c-b).length,(a-c).length];areas.append((area,t,max(lengths),min(lengths)))
short=min(((points[e.vertices[1]]-points[e.vertices[0]]).length,list(e.vertices)) for e in mesh.edges)
bvh=BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0);pairs={tuple(sorted((i,j))) for i,j in bvh.overlap(bvh) if i!=j and not (set(tris[i])&set(tris[j]))}
bm=bmesh.new();bm.from_mesh(mesh);verts=set(bm.verts);components=0
while verts:
 components+=1;stack=[verts.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in verts:verts.remove(v);stack.append(v)
small=min(areas);area,idx,longest,mini=small
r={'sceneSha256':sha,'object':target,'blenderVersion':bpy.app.version_string,'meshCounts':{'vertices':len(mesh.vertices),'edges':len(mesh.edges),'faces':len(mesh.polygons),'loopTriangles':len(tris)},'worldBoundsMm':[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)],'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,'minimumTri':{'areaMm2':area,'vertexIndices':idx,'coordinatesMm':[list(points[i]) for i in idx],'longestEdgeMm':longest,'shortestSideMm':mini,'altitudeToLongestMm':2*area/longest},'trianglesBelowMm2':{str(t):sum(a[0]<t for a in areas) for t in (1e-5,1e-4,1e-3,1e-2)},'minimumOriginalMeshEdge':{'lengthMm':short[0],'vertexIndices':short[1],'coordinatesMm':[list(points[i]) for i in short[1]]},'bvhNonSharedVertexCandidateCount':len(pairs),'limitation':'Mesh loop triangle method; BVH excludes pairs sharing vertex indices. Zero candidates and threshold counts are not evidence that all self-intersections, thin features, manufacturing, tolerance or fit problems are absent.'}
bm.free();out=Path(os.environ['THREAD_REVIEW_OUT']);
with out.open('x',encoding='utf8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
print(json.dumps(r,ensure_ascii=False))
