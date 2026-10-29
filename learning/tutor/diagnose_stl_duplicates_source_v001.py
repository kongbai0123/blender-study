"""Trace exact opposite-winding STL triangles to evaluated source mesh polygons."""
import bpy,hashlib,json,struct,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];objname,stl,out=args[0],Path(args[1]),Path(args[2])
obj=bpy.data.objects[objname];m=obj.data;m.calc_loop_triangles();p=[obj.matrix_world@v.co for v in m.vertices]
f32=lambda n:struct.unpack('<f',struct.pack('<f',float(n)))[0]
source={}
for tri in m.loop_triangles:
 points=tuple(tuple(f32(c) for c in p[i]) for i in tri.vertices);key=tuple(sorted(points))
 source.setdefault(key,[]).append({'polygonIndex':tri.polygon_index,'polygonVertexCount':len(m.polygons[tri.polygon_index].vertices),
  'meshVertexIndices':list(tri.vertices),'pointsMm':points,'normal':list(tri.normal)})
raw=stl.read_bytes();n=struct.unpack_from('<I',raw,80)[0];seen={};duplicates=[]
for i in range(n):
 vals=struct.unpack_from('<12fH',raw,84+i*50);tri=tuple(tuple(vals[k:k+3]) for k in (3,6,9));key=tuple(sorted(tri))
 if key in seen:
  j,prior,normal=seen[key];same=any(tuple(tri[(k+t)%3] for t in range(3))==prior for k in range(3))
  duplicates.append({'firstStlTriangle':j,'duplicateStlTriangle':i,'sameWinding':same,
   'firstStlNormal':normal,'duplicateStlNormal':vals[:3],'pointsMm':key,'matchingSourceTriangleRecords':source.get(key,[])})
 else:seen[key]=(i,tri,vals[:3])
result={'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'object':objname,
 'stlSha256':hashlib.sha256(raw).hexdigest(),'duplicates':duplicates,
 'method':'Exact STL float32 coordinates, with transformed source coordinates rounded to float32 for direct mapping.',
 'limitations':'Triangulation mapping does not establish whether alternate triangulation is valid, watertight, printable, or fit.'}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
