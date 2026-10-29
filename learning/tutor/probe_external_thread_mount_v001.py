"""Exploratory background exact union; no edits to input scene, no save.

This diagnostic is not GUI teaching evidence or a manufacturing qualification.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

thread=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2])
with bpy.data.libraries.load(str(thread),link=False) as (src,dst): dst.objects=['Thread_Core']
tool=dst.objects[0];bpy.context.scene.collection.objects.link(tool)
bpy.context.view_layer.update()
tool.matrix_world=Matrix.Translation(Vector((31.9,0,0))) @ Matrix.Rotation(math.pi/2,4,'Y') @ Matrix.Translation(Vector((0,0,-2.3))) @ tool.matrix_world
bpy.context.view_layer.update()
body=bpy.data.objects['Body'];body.hide_set(False);tool.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('mount_probe','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=tool
bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.index_update()
points=[body.matrix_world@v.co for v in bm.verts]
tris=[tuple(l.vert.index for l in t) for t in bm.calc_loop_triangles()]
areas=[((points[b]-points[a]).cross(points[c]-points[a])).length/2 for a,b,c in tris]
tree=BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0)
pairs={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tris[a])&set(tris[b])}
remaining=set(bm.verts);components=0
while remaining:
    components+=1;stack=[remaining.pop()]
    while stack:
        for e in stack.pop().link_edges:
            for v in e.verts:
                if v in remaining:remaining.remove(v);stack.append(v)
hits=[]
for y,z in [(0,0),(2,2),(-2,-2),(8,4),(-8,-4)]:
    pt,_,_,_=tree.ray_cast(Vector((0,y,z)),Vector((1,0,0)),100);hits.append(list(pt) if pt else None)
result={'vertices':len(bm.verts),'faces':len(bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),
 'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,
 'boundsMm':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
 'bvhNonAdjacentCandidatePairs':len(pairs),'minimumTriangleAreaMm2':min(areas),
 'triangleAreasBelow1eMinus5Mm2':sum(x<1e-5 for x in areas),
 'shortestMeshEdgeMm':min((points[e.verts[0].index]-points[e.verts[1].index]).length for e in bm.edges),
 'interiorWallRayHitsMm':hits,'limits':'diagnostic only; zero BVH is not proof of no self-intersection'}
bm.free();out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
