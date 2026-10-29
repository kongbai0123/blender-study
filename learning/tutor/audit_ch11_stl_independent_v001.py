"""Independent background reimport of an actual GUI-exported binary STL.

This is an audit, not the GUI demonstration. Exact duplicate STL triangles are
counted without changing bytes or coordinate tolerances. Reimport uses Blender's
native validation and may remove duplicates; all changes remain visible.
"""
import bpy,bmesh,hashlib,json,struct,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];stl,out=map(Path,args[:2]);data=stl.read_bytes()
if len(data)<84:raise RuntimeError('truncated STL')
n=struct.unpack_from('<I',data,80)[0]
if len(data)!=84+50*n:raise RuntimeError('bad STL length')
raw_bounds=[[float('inf'),-float('inf')] for _ in range(3)];seen={};dups=[]
for i in range(n):
 vals=struct.unpack_from('<12fH',data,84+50*i)
 if not all(math.isfinite(v) for v in vals[:12]):raise RuntimeError('nonfinite data')
 pts=[tuple(vals[j:j+3]) for j in (3,6,9)];key=tuple(sorted(pts))
 if key in seen:dups.append({'firstTriangle':seen[key],'duplicateTriangle':i,'verticesMm':key})
 else:seen[key]=i
 for p in pts:
  for j in range(3):raw_bounds[j][0]=min(raw_bounds[j][0],p[j]);raw_bounds[j][1]=max(raw_bounds[j][1],p[j])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.001;bpy.context.scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.wm.stl_import(filepath=str(stl.resolve()),global_scale=1.0,use_scene_unit=False,forward_axis='Y',up_axis='Z',use_mesh_validate=True)
obj=bpy.context.view_layer.objects.active
if obj is None or obj.type!='MESH':raise RuntimeError('native importer did not create mesh')
bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.index_update()
pts=[obj.matrix_world@v.co for v in bm.verts];tris=[tuple(l.vert.index for l in tri) for tri in bm.calc_loop_triangles()]
tree=BVHTree.FromPolygons(pts,tris,all_triangles=True,epsilon=0)
pairs={tuple(sorted((a,b))) for a,b in tree.overlap(tree) if a!=b and not set(tris[a])&set(tris[b])}
areas=[((pts[b]-pts[a]).cross(pts[c]-pts[a])).length/2 for a,b,c in tris]
remaining=set(bm.verts);components=0
while remaining:
 components+=1;stack=[remaining.pop()]
 while stack:
  for edge in stack.pop().link_edges:
   for v in edge.verts:
    if v in remaining:remaining.remove(v);stack.append(v)
result={'stlSha256':hashlib.sha256(data).hexdigest(),'binaryTriangles':n,'binaryBoundsMm':raw_bounds,
 'binaryExactDuplicateTriangles':len(dups),'binaryExactDuplicateDetails':dups,
 'blenderVersion':bpy.app.version_string,'importOptions':{'globalScale':1,'useSceneUnit':False,'forwardAxis':'Y','upAxis':'Z','meshValidate':True},
 'reimport':{'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(tris),
  'boundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
  'signedVolumeMm3':bm.calc_volume(signed=True),'boundaryEdges':sum(e.is_boundary for e in bm.edges),
  'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,
  'nonAdjacentBvhCandidates':len(pairs),'minimumTriangleAreaMm2':min(areas)},
 'limitations':['Independent software audit; STL has no embedded length unit, coordinates interpreted in mm.',
  'Native validated import may remove duplicate triangles; exact duplicates remain in the original STL file.',
  'Zero BVH candidates does not prove no self-intersection; geometry is not verified for manufacture or fit.'],
 'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
bm.free();out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
