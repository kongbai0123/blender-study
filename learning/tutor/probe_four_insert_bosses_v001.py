"""Background preflight of optional 4-boss/insert-hole geometry; no save.

Meshes/tools are explicitly built by Python. GUI demonstration is separate.
Rib and pillar unions and holes are checked separately. No physical or fit claim.
"""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index('--')+1]);centres=[(x,y) for x in (-21,21) for y in (-11,11)]
def mesh_group(name,objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name=name;return objs[0]
def cyls(name,r,zmin,zmax):
    objs=[]
    for x,y in centres:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=zmax-zmin,location=(x,y,(zmin+zmax)/2))
        objs.append(bpy.context.object)
    return mesh_group(name,objs)
def ribs(name,axis):
    objs=[]
    for x,y in centres:
        if axis=='X': center=((1 if x>0 else -1)*25.75,y,-1.75); dims=(5.5,2,23.5)
        else:center=(x,(1 if y>0 else -1)*15.75,-1.75);dims=(2,5.5,23.5)
        bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.dimensions=dims
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);objs.append(o)
    return mesh_group(name,objs)
def boolean(target,tool,operation):
    bpy.ops.object.select_all(action='DESELECT');target.hide_set(False);target.select_set(True);bpy.context.view_layer.objects.active=target
    m=target.modifiers.new('preflight','BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=tool
    bpy.ops.object.modifier_apply(modifier=m.name)
def audit(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.index_update()
    p=[o.matrix_world@v.co for v in bm.verts];tri=[tuple(l.vert.index for l in t) for t in bm.calc_loop_triangles()]
    tree=BVHTree.FromPolygons(p,tri,all_triangles=True,epsilon=0)
    overlaps={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tri[a])&set(tri[b])}
    areas=[((p[b]-p[a]).cross(p[c]-p[a])).length/2 for a,b,c in tri]
    remain=set(bm.verts);components=0
    while remain:
        components+=1;stack=[remain.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remain:remain.remove(v);stack.append(v)
    info={'vertices':len(bm.verts),'faces':len(bm.faces),'boundsMm':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],
          'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'components':components,
          'nonAdjacentBvhCandidates':len(overlaps),'minimumTriangleAreaMm2':min(areas),
          'trianglesAreaBelow1eMinus5Mm2':sum(a<1e-5 for a in areas)}
    bm.free();return info,tree
body=bpy.data.objects['Body'];lid=bpy.data.objects['Lid']
body.hide_set(False);lid.hide_set(False)
tools=[cyls('Pillars',4,-13.5,15),ribs('Ribs_X','X'),ribs('Ribs_Y','Y'),cyls('Pilot',2,6,15.5),cyls('Lid_Holes',1.7,10.5,17.5)]
for t,op in zip(tools,['UNION','UNION','UNION','DIFFERENCE']):boolean(body,t,op)
boolean(lid,tools[4],'DIFFERENCE')
b,bt=audit(body);l,lt=audit(lid)
body_hits=[];lid_hits=[]
for x,y in centres:
    p,_,_,_=bt.ray_cast(Vector((x,y,15.25)),Vector((0,0,-1)),40);body_hits.append({'center':[x,y],'hit':list(p) if p else None})
    p,_,_,_=lt.ray_cast(Vector((x,y,18)),Vector((0,0,-1)),15);lid_hits.append({'center':[x,y],'hit':list(p) if p else None})
result={'centresMm':centres,'body':b,'lid':l,'bodyPilotAxisHits':body_hits,'lidHoleAxisHits':lid_hits,
 'nominalPillarOuterDiameterMm':8,'pilotDiameterMm':4,'pilotBottomZMm':6,'pilotToolTopZMm':15.5,
 'lidHoleDiameterMm':3.4,'ribTopZMm':10,'lidLowestZMm':11,'ribToLidZBoundsGapMm':1,
 'caveat':'Background geometry preflight only; nominal dimensions, no material, print, heat-set insert, fit or structural qualification.'}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
