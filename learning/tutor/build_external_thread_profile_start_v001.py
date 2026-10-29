import bpy,hashlib,os
from pathlib import Path
source=Path(bpy.data.filepath)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'
out=Path(os.environ['THREAD_PROFILE_OUTPUT']);assert not out.exists()
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.data.objects['Body_Reference'].hide_set(True)
assert not bpy.data.objects.get('Thread_Triangle_Profile')
mesh=bpy.data.meshes.new('Thread_Triangle_Profile');mesh.from_pydata([(4.8,0,0),(6,0,.3),(4.8,0,.6)],[(0,1),(1,2),(2,0)],[]);mesh.update()
obj=bpy.data.objects.new('Thread_Triangle_Profile',mesh);scene.collection.objects.link(obj)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
