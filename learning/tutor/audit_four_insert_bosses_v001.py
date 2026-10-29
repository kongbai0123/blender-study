"""Independent read-only audit of the saved four-boss GUI demonstration.

Axial/radial rays are samples; mesh thresholds are diagnostics, not ISO or
manufacturing criteria. Does not model threaded inserts, screw or heat setting.
"""
import bpy,bmesh,hashlib,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index('--')+1]);centres=[(x,y) for x in (-21,21) for y in (-11,11)]
def audit(name):
    obj=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.index_update()
    pts=[obj.matrix_world@v.co for v in bm.verts]
    tris=[tuple(l.vert.index for l in tri) for tri in bm.calc_loop_triangles()]
    tree=BVHTree.FromPolygons(pts,tris,all_triangles=True,epsilon=0)
    candidates={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tris[a])&set(tris[b])}
    areas=[((pts[b]-pts[a]).cross(pts[c]-pts[a])).length/2 for a,b,c in tris]
    edges=[(pts[e.verts[0].index]-pts[e.verts[1].index]).length for e in bm.edges]
    alt=[2*area/max((pts[a]-pts[b]).length,(pts[b]-pts[c]).length,(pts[c]-pts[a]).length) for area,(a,b,c) in zip(areas,tris)]
    remaining=set(bm.verts);components=0
    while remaining:
        components+=1;stack=[remaining.pop()]
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in remaining:remaining.remove(v);stack.append(v)
    result={'object':name,'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'triangles':len(tris),
      'worldBoundsMm':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],
      'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),
      'components':components,'nonAdjacentBvhCandidatePairs':len(candidates),'minimumTriangleAreaMm2':min(areas),
      'minimumTriangleAltitudeMm':min(alt),'shortestMeshEdgeMm':min(edges),'triangleAreasBelow1eMinus5Mm2':sum(a<1e-5 for a in areas),
      'allTriangleAreasMm2':areas,'allTriangleAltitudesMm':alt}
    bm.free();return result,tree
body,bt=audit('Body');lid,lt=audit('Lid')
def shoot(tree,origin,direction,distance):
    p,n,idx,d=tree.ray_cast(Vector(origin),Vector(direction),distance)
    return {'hit':list(p) if p else None,'distanceMm':d if p else None}
measure=[]
for x,y in centres:
    item={'centerMm':[x,y],'pilotBottom':shoot(bt,(x,y,15.25),(0,0,-1),40),
          'lidThroughAxis':shoot(lt,(x,y,18),(0,0,-1),15),
          'pilotRadial':{},'lidRadial':{}}
    for label,dx,dy in [('positiveX',1,0),('negativeX',-1,0),('positiveY',0,1),('negativeY',0,-1)]:
        item['pilotRadial'][label]=shoot(bt,(x,y,14.9),(dx,dy,0),10)
        item['lidRadial'][label]=shoot(lt,(x,y,16),(dx,dy,0),10)
    measure.append(item)
result={'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'blenderVersion':bpy.app.version_string,'body':body,'lid':lid,'perCenterMeasurements':measure,
 'nominalHardware':{'insert':'Ruthex RX-M3x5.7','insertLengthMm':5.7,'insertOuterDiameterMm':4.6,'insertTipDiameterMm':3.9,
                    'manufacturerPilotDiameterMm':4.0,'manufacturerMinDepthMm':6.7,'manufacturerMinimumWallMm':1.6,
                    'screw':'ETTINGER 001.16.342 ISO4762 M3x10 A2/AISI304','screwLengthMm':10,'headDiameterMm':5.5,'headHeightMm':3,'hexMm':2.5},
 'nominalDraft':{'centresMm':centres,'pillarOuterDiameterMm':8,'pillarBottomZMm':-13.5,'pillarTopZMm':15,
                 'pilotDiameterMm':4,'pilotBottomZMm':6,'pilotDepthMm':9,'lidHoleDiameterExperimentalMm':3.4,
                 'insertTopZMm':14.8,'insertBottomZMm':9.1,'screwBottomZMm':7,'nominalScrewToHoleBottomMm':1,
                 'ribTopZMm':10,'lidLowestZMm':11,'ribToLidBoundingBoxVerticalGapMm':1,
                 'headEnvelopeBottomZMm':17,'headEnvelopeTopZMm':20,'headEnvelopeRadiusMm':2.75,
                 'headToLidOuterEdgeMarginMm':6.25,'headToHeadMinimumPlanarGapMm':16.5},
 'limitations':['Head and insert dimensions are nominal envelopes, not modeled hardware or contact tests.',
  'Hole diameters derived from four radial rays per hole; other directions, tolerance and post-print results not verified.',
  '1 mm rib clearance is static bounding-box separation; not an assembly or thermal deformation test.',
  'Minimum triangle altitude and edges are mesh properties, not wall thickness; BVH candidates do not establish no self-intersections.',
  'No material, torque, mechanical strength, print, fit, measured dimensions or certified clearance result.'],
 'material':None,'torque':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedStrength':None,'qualifiedClearance':None}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k not in ('body','lid')},indent=2))
