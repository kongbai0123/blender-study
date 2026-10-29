"""Explore mount depths/phases without editing input; report triangle altitudes.

One triangle altitude is 2*area / longest edge. This is a numerical mesh
diagnostic, not a manufacture or slicer acceptance criterion. BVH excludes
shared-index triangle pairs; zero candidates is not a proof of no intersection.
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index('--')+1:]
thread,out=map(Path,args[:2])
with bpy.data.libraries.load(str(thread),link=False) as (src,dst): dst.objects=['Thread_Core']
tool=dst.objects[0];bpy.context.scene.collection.objects.link(tool);tool.hide_set(False)
bpy.context.view_layer.update();original=tool.matrix_world.copy()
body_source=bpy.data.objects['Body'];body_source.hide_set(False)
results=[]
for depth in (0.55,0.56,0.57,0.58,0.59,0.6,0.61,0.62,0.63,0.64,0.65):
 for phase in (0,):
    tool.matrix_world=Matrix.Translation(Vector((32.4-depth,0,0))) @ Matrix.Rotation(math.radians(phase),4,'X') @ Matrix.Rotation(math.pi/2,4,'Y') @ Matrix.Translation(Vector((0,0,-2.3))) @ original
    body=body_source.copy();body.data=body_source.data.copy();bpy.context.scene.collection.objects.link(body)
    bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
    mod=body.modifiers.new('test','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=tool
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(body.data);bm.verts.index_update()
    pts=[body.matrix_world@v.co for v in bm.verts]
    loops=bm.calc_loop_triangles();tris=[tuple(l.vert.index for l in t) for t in loops]
    areas=[];alts=[];longs=[]
    for a,b,c in tris:
        lengths=[(pts[a]-pts[b]).length,(pts[b]-pts[c]).length,(pts[c]-pts[a]).length]
        longest=max(lengths);area=((pts[b]-pts[a]).cross(pts[c]-pts[a])).length/2
        areas.append(area);longs.append(longest);alts.append(2*area/longest if longest else 0)
    idx=min(range(len(alts)),key=alts.__getitem__);tri=tris[idx]
    tree=BVHTree.FromPolygons(pts,tris,all_triangles=True,epsilon=0)
    overlaps={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tris[a])&set(tris[b])}
    remaining=set(bm.verts);components=0
    while remaining:
        components+=1;stack=[remaining.pop()]
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in remaining:remaining.remove(v);stack.append(v)
    hits=[]
    for y,z in ((0,0),(2,2),(-2,-2),(8,4),(-8,-4)):
        p,_,_,_=tree.ray_cast(Vector((0,y,z)),Vector((1,0,0)),100);hits.append(list(p) if p else None)
    results.append({'depthMm':depth,'phaseDegrees':phase,'bodyBoundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
      'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,
      'nonAdjacentBvhCandidates':len(overlaps),'triangleCount':len(tris),'minimumTriangleAreaMm2':min(areas),
      'minimumTriangleAltitudeMm':min(alts),'shortestMeshEdgeMm':min((pts[e.verts[0].index]-pts[e.verts[1].index]).length for e in bm.edges),
      'minimumAltitudeTriangle':{'pointsMm':[[float(c) for c in pts[i]] for i in tri], 'areaMm2':areas[idx], 'longestEdgeMm':longs[idx], 'faceSideCount':len(loops[idx][0].face.verts), 'parentFaceNormal':list(loops[idx][0].face.normal)},
      'triangleAltitudesBelow001Mm':sum(a<.001 for a in alts),'interiorRayHitsMm':hits})
    bm.free();bpy.data.objects.remove(body,do_unlink=True)
result={'results':results,'limits':'Screening only; no manufacturing qualification; subthreshold counts do not diagnose self-intersection or mechanical suitability.'}
out.write_text(json.dumps(result,indent=2),encoding='utf8')
for r in results:
 print('DEPTH_PHASE',r['depthMm'],r['phaseDegrees'],'ALT',r['minimumTriangleAltitudeMm'],'AREA',r['minimumTriangleAreaMm2'],'SMALL',r['triangleAltitudesBelow001Mm'],'BVH',r['nonAdjacentBvhCandidates'],'MANIFOLD',r['nonManifoldEdges'],'SHELLS',r['components'])
