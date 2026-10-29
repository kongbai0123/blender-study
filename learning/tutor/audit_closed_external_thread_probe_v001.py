"""Read-only independent background audit of the saved helical draft; no changes to the .blend."""
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils.bvhtree import BVHTree

obj = bpy.data.objects.get('External_Thread_Draft')
if obj is None or obj.type != 'MESH':
    raise RuntimeError('draft object missing')
mesh = obj.data
mesh.calc_loop_triangles()
vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0.0)
pairs = tree.overlap(tree)
unique = {tuple(sorted((a,b))) for a,b in pairs if a != b}
nonadjacent = [(a,b) for a,b in unique if not (set(triangles[a]) & set(triangles[b]))]
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not e.is_manifold for e in bm.edges)
boundary = sum(e.is_boundary for e in bm.edges)
volume = bm.calc_volume(signed=True)
bm.free()
def radius_at(zi,j):
    p=vertices[zi*32+j]
    return math.hypot(p.x,p.y)
samples = {str(j): [radius_at(zi,j) for zi in range(81)] for j in (0,8,16,24)}
# Four crest radii per angle at expected phase; z sampling is 0.05 mm so half-step
# angle offsets do not necessarily land exactly on crest; values are read directly.
near_crests={str(j):max(samples[str(j)][n:n+20]) for j in (0,8,16,24) for n in (0,)}
result={'object': obj.name, 'boundsZ': [min(p.z for p in vertices),max(p.z for p in vertices)],
        'vertices':len(vertices),'triangles':len(triangles),'nonManifoldEdges':nonmanifold,
        'boundaryEdges':boundary,'signedVolumeMm3':volume,'bvhPairCountIncludingAdjacency':len(unique),
        'nonAdjacentBvhOverlaps':len(nonadjacent),'nonAdjacentExamples':nonadjacent[:10],
        'nearCrestMaxByQuarterTurn':near_crests,
        'limitations':['BVH overlap excludes triangle pairs sharing vertices; it is not a complete proof of no self-intersection',
                       'mesh normal, printability, tolerance and fit require separate checks',
                       'no physical result or user completion implied']}
output=Path(sys.argv[sys.argv.index('--')+1])
output.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
