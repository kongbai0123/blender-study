"""Read the actual five station meshes from source and rendering scenes.

Record world-space vertices/edges and compare face-coordinate fingerprints.
Ground is a plane; objects are scene references, not physical printable parts.
"""
import bpy,hashlib,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];source,render,out=map(Path,args[:3])
names=['Ground','Platform','BeaconBase','Post','Signal']
def capture(path,include_mesh):
 bpy.ops.wm.open_mainfile(filepath=str(path));objects={}
 for name in names:
  o=bpy.data.objects[name];m=o.data;pts=[o.matrix_world@v.co for v in m.vertices]
  face_coords=sorted(tuple(sorted(tuple(round(float(pts[i][j]),6) for j in range(3)) for i in f.vertices)) for f in m.polygons)
  d={'verticesCount':len(m.vertices),'edgesCount':len(m.edges),'facesCount':len(m.polygons),
     'worldBoundsM':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
     'worldFaceVertexSetSha256':hashlib.sha256(json.dumps(face_coords,separators=(',',':')).encode()).hexdigest()}
  if include_mesh:d.update(worldVerticesM=[[float(c) for c in p] for p in pts],edges=[list(e.vertices) for e in m.edges])
  objects[name]=d
 return {'sceneSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'unitSystem':bpy.context.scene.unit_settings.system,
         'unitScaleLength':bpy.context.scene.unit_settings.scale_length,'stationCollectionObjects':sorted(o.name for o in bpy.data.collections['Station'].objects),'objects':objects}
a=capture(source,True);b=capture(render,False)
result={'sourceScene':'learning/evidence/02/2026-10-22-lesson02-demo-v001/demo-files/u02_station_v002.blend',
 'renderScene':'learning/evidence/03/2026-10-22-lesson03-demo-v001/demo-files/u03_render_v001.blend',
 'source':a,'render':b,
 'sameWorldMeshFingerprints':{name:a['objects'][name]['worldFaceVertexSetSha256']==b['objects'][name]['worldFaceVertexSetSha256'] for name in names},
 'limitations':['Raw object mesh transformed to world coordinates; modifiers were not evaluated.',
  'Orthographic edge projections are actual mesh edges, not a complete standard hidden-line drawing.',
  'Dimensions are illustrative Blender scene units in metres, not toleranced manufacturing or print specifications.']}
out.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'sourceSha':a['sceneSha256'],'renderSha':b['sceneSha256'],'matching':result['sameWorldMeshFingerprints'],
 'objects':{n:a['objects'][n]['worldBoundsM'] for n in names}},indent=2))
