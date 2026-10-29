"""Independent, read-only geometry audit of the saved GUI screw experiment.

Usage: blender -b <scene.blend> --python this_file.py -- <output.json>.
The triangle overlap query ignores triangles sharing any vertex; zero findings is
not a proof that no geometric self intersections or manufacturing defects exist.
"""
import bpy
import bmesh
import json
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

out = Path(sys.argv[sys.argv.index('--') + 1])
obj = bpy.data.objects['Thread_Core']
mesh = obj.data
bm = bmesh.new()
bm.from_mesh(mesh)
bm.verts.ensure_lookup_table()
bm.verts.index_update()
points = [obj.matrix_world @ v.co for v in bm.verts]
tris = [tuple(loop.vert.index for loop in tri) for tri in bm.calc_loop_triangles()]
bvh = BVHTree.FromPolygons(points, tris, all_triangles=True, epsilon=0.0)
pairs = set()
for a, b in bvh.overlap(bvh):
    if a == b or set(tris[a]) & set(tris[b]):
        continue
    pairs.add(tuple(sorted((a, b))))
remaining = set(bm.verts)
components = 0
while remaining:
    components += 1
    stack = [remaining.pop()]
    while stack:
        for edge in stack.pop().link_edges:
            for vert in edge.verts:
                if vert in remaining:
                    remaining.remove(vert)
                    stack.append(vert)
result = {
    'blenderVersion': bpy.app.version_string,
    'object': obj.name,
    'vertices': len(bm.verts),
    'edges': len(bm.edges),
    'faces': len(bm.faces),
    'triangles': len(tris),
    'boundaryEdges': sum(e.is_boundary for e in bm.edges),
    'nonManifoldEdges': sum(not e.is_manifold for e in bm.edges),
    'connectedComponents': components,
    'signedVolumeObjectUnitsCubed': bm.calc_volume(signed=True),
    'worldBoundsMm': [[min(v[i] for v in points), max(v[i] for v in points)] for i in range(3)],
    'samePhaseCrestZMm': sorted(set(round(float(v.z), 5) for v in points if abs(v.x - 6) < 1e-4 and abs(v.y) < 1e-4)),
    'nonAdjacentTriangleOverlapPairs': len(pairs),
    'candidatePairs': [],
    'overlapTestLimitation': 'BVH candidate intersections exclude triangles sharing vertices; this is not a proof of freedom from all geometric defects.',
    'unitScaleLength': bpy.context.scene.unit_settings.scale_length,
    'meshScale': list(obj.scale),
}
for a, b in sorted(pairs):
    ta, tb = [[points[i] for i in tris[t]] for t in (a, b)]
    segments = []
    for source, target in ((ta, tb), (tb, ta)):
        for i in range(3):
            start, end = source[i], source[(i + 1) % 3]
            direction = end - start
            p = intersect_ray_tri(*target, direction, start, True)
            if p is not None and direction.length_squared:
                t = (p - start).dot(direction) / direction.length_squared
                if 0 <= t <= 1:
                    segments.append([float(c) for c in p])
    result['candidatePairs'].append({
        'triangles': [list(tris[a]), list(tris[b])],
        'coordinatesMm': [[[float(c) for c in points[i]] for i in tris[t]] for t in (a, b)],
        'minimumCrossTriangleVertexDistanceMm': min((va - vb).length for va in ta for vb in tb),
        'triangleAreasMm2': [((v[1]-v[0]).cross(v[2]-v[0])).length / 2 for v in (ta, tb)],
        'segmentTriangleIntersectionPointsMm': segments,
        'note': 'Floating-point triangle intersections, especially on degenerate triangles, need further investigation; do not infer absence of defects from empty points.',
    })
bm.free()
out.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
