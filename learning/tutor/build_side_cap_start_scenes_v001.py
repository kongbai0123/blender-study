import bpy,hashlib,math,os
from pathlib import Path
from mathutils import Quaternion
source=Path(bpy.data.filepath);expected=os.environ['CAP_START_SOURCE_SHA'];assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
out=Path(os.environ['CAP_START_OUTPUT']);assert not out.exists()
if os.environ['CAP_START_TYPE']=='thread':
 src=bpy.data.objects['Thread_Core'];body=bpy.data.objects['Body'];assert len(src.data.vertices)==707
 cut=bpy.data.objects.new('Cap_Cutter_020',src.data.copy());body.users_collection[0].objects.link(cut);cut.matrix_world=src.matrix_world.copy();inv=cut.matrix_world.inverted()
 for v in cut.data.vertices:
  w=cut.matrix_world@v.co;r=math.hypot(w.y,w.z);assert r>1e-6
  w.y*=1+.2/r;w.z*=1+.2/r;v.co=inv@w
 cut.data.update();cut.hide_set(False);src.hide_set(True)
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=7.7,depth=5.5,location=(33.05,0,0),rotation=(0,math.pi/2,0));cap=bpy.context.object;cap.name='Side_Cap_Blank';cap.rotation_mode='QUATERNION';cap.rotation_quaternion=Quaternion((1,0,0),math.radians(2.8125))@Quaternion((0,1,0),math.pi/2);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
elif os.environ['CAP_START_TYPE']=='relief':
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=5.3,depth=.35,location=(34.325,0,0),rotation=(0,math.pi/2,0));cut=bpy.context.object;cut.name='A_Relief_Cutter';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.object.select_all(action='DESELECT');cap=bpy.data.objects['Side_Cap_Blank'];cap.select_set(True);bpy.context.view_layer.objects.active=cap
else:raise RuntimeError('unknown mode')
bpy.context.view_layer.update();assert bpy.context.view_layer.objects.active==cap and not cap.modifiers
bpy.ops.wm.save_as_mainfile(filepath=str(out))
