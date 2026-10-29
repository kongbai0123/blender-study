"""Independently inspect saved GUI-edited profile without modifying it."""
import bpy,json,hashlib,sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);obj=bpy.data.objects['Thread_Hand_Profile'];m=obj.data
points=[obj.matrix_world@v.co for v in m.vertices]
degrees=[0]*len(points)
for e in m.edges:
    for i in e.vertices:degrees[i]+=1
expected=sorted(((4.8,0,0),(6,0,.3),(4.8,0,.6)))
got=sorted(tuple(float(c) for c in v) for v in points)
maximum=max(abs(a-b) for p,q in zip(got,expected) for a,b in zip(p,q)) if len(got)==3 else None
result={'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'blenderVersion':bpy.app.version_string,'object':obj.name,'worldVerticesMm':got,
 'edgeVertexIndices':[list(e.vertices) for e in m.edges],'vertexDegrees':degrees,'faceCount':len(m.polygons),
 'maxCoordinateDeviationMm':maximum,'connectedTriangle':len(got)==3 and len(m.edges)==3 and degrees==[2,2,2] and len(m.polygons)==0,
 'physicalPrint':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
if not result['connectedTriangle'] or maximum is None or maximum>1e-4: raise RuntimeError('profile does not match')
