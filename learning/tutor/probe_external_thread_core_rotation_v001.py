"""Explore core phase offset as an exact-Boolean degeneracy remedy.

Background probe, not GUI evidence. Reads a saved v005 scene and writes only
diagnostic JSON; it does not modify or save the scene. BVH counts are candidate
overlaps excluding triangles sharing a vertex; zero is not proof of no defects.
"""
import bpy
import bmesh
import math
import json
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree

out = Path(sys.argv[sys.argv.index('--') + 1])
source = bpy.data.objects['Thread_Triangle_Profile']
source.hide_set(False)
results = []
for angle in (0, 2.8125, 5.625, 8.4375):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=5, depth=4.6, location=(0, 0, 2.3), rotation=(0, 0, math.radians(angle)))
    obj = bpy.context.object
    mod = obj.modifiers.new('exact_union', 'BOOLEAN')
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    mod.object = source
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.index_update()
    verts = [obj.matrix_world @ v.co for v in bm.verts]
    tris = [tuple(loop.vert.index for loop in tri) for tri in bm.calc_loop_triangles()]
    areas = [((verts[b]-verts[a]).cross(verts[c]-verts[a])).length / 2 for a,b,c in tris]
    bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True, epsilon=0.0)
    overlaps = {tuple(sorted((a,b))) for a,b in bvh.overlap(bvh) if a != b and not set(tris[a]).intersection(tris[b])}
    remaining = set(bm.verts)
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remaining:
                        remaining.remove(v)
                        stack.append(v)
    results.append({'coreRotationDegrees': angle, 'vertices': len(bm.verts), 'edges': len(bm.edges), 'faces': len(bm.faces),
                    'boundaryEdges': sum(e.is_boundary for e in bm.edges), 'nonManifoldEdges': sum(not e.is_manifold for e in bm.edges),
                    'connectedComponents': components, 'volumeMm3': bm.calc_volume(signed=True),
                    'boundsMm': [[min(p[i] for p in verts), max(p[i] for p in verts)] for i in range(3)],
                    'nonAdjacentBvhCandidatePairs': len(overlaps), 'minimumTriangleAreaMm2': min(areas),
                    'areaBelow1e-5Mm2': sum(a < 1e-5 for a in areas)})
    bm.free()
    bpy.data.objects.remove(obj, do_unlink=True)
out.write_text(json.dumps({'tests': results, 'caveat': 'Exploratory diagnostic, not GUI; no-print/fit conclusion; zero candidate overlaps does not prove no geometric defects.'}, indent=2), encoding='utf-8')
print(json.dumps(results, indent=2))
