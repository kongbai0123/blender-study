"""Compare prepared start tools with unmodified operands saved in GUI result."""
import bpy,hashlib,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];start,result,out=map(Path,args[:3])
names=['zz_Boss_Pillars','zz_Boss_Ribs_X','zz_Boss_Ribs_Y','zz_Boss_Pilot_Tools','zz_Boss_Lid_Tools']
def gather(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));data={}
 for name in names:
  obj=bpy.data.objects[name];pts=[obj.matrix_world@v.co for v in obj.data.vertices]
  faces=sorted(tuple(sorted(tuple(round(float(pts[i][j]),6) for j in range(3)) for i in f.vertices)) for f in obj.data.polygons)
  data[name]=hashlib.sha256(json.dumps(faces,separators=(',',':')).encode()).hexdigest()
 return data
a=gather(start);b=gather(result)
comparison={'startSha256':hashlib.sha256(start.read_bytes()).hexdigest(),'resultSha256':hashlib.sha256(result.read_bytes()).hexdigest(),
 'startToolFaceVertexFingerprints':a,'resultToolFaceVertexFingerprints':b,'allEqual':a==b,
 'limit':'Rounded world face vertices; not a material, print or fit check.'}
out.write_text(json.dumps(comparison,indent=2),encoding='utf8');print(json.dumps(comparison,indent=2))
if a!=b:raise RuntimeError('prepared start tools do not match GUI result operands')
