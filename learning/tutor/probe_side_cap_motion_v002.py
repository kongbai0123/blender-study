import bpy,json,math,hashlib,os,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['CAP_SCENE_SHA']
cap=bpy.data.objects['Side_Cap_Blank'];body=bpy.data.objects['Body'];results=[]
for sign in (1,-1):
 for angle in (0,45,90,135,180,225,270,315,360,450,540):
  q=cap.copy();q.data=cap.data.copy();bpy.context.scene.collection.objects.link(q)
  # one nominal 1 mm axial displacement per revolution, away from the wall.
  q.matrix_world=Matrix.Translation(Vector((angle/360,0,0)))@Matrix.Rotation(math.radians(sign*angle),4,'X')@cap.matrix_world
  bpy.ops.object.select_all(action='DESELECT');q.select_set(True);bpy.context.view_layer.objects.active=q
  mod=q.modifiers.new('Motion_Intersection_Test','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=body;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(q.data);v=abs(bm.calc_volume(signed=True)) if len(bm.faces) else 0
  record={'direction':sign,'rotationDeg':sign*angle,'axialDisplacementMm':angle/360,'intersectionVertices':len(bm.verts),'intersectionFaces':len(bm.faces),'absoluteSignedVolumeMm3':v}
  results.append(record);bm.free();bpy.data.objects.remove(q,do_unlink=True);print(record)
report={'sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'22 discrete Boolean Exact intersections of rigid cap and box. Rotation about +X, accompanied by 1 mm axial outward movement per turn, both angular directions. This does not test continuous motion, contact forces, actual clearance, material deformation or printing.','samples':results,'limits':['Finite samples only; empty intersections cannot prove continuous collision-free motion.','Tiny intersections may be numerical; nonzero results require inspection, not automatic physical collision conclusion.','Axial relief has 0.2 mm nominal clearance at the center; only discrete samples are checked and actual fit is unverified.','Not a physical fit or manufacturing acceptance test.']}
out=Path(os.environ['CAP_MOTION_OUTPUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
