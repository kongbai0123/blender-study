import bpy,addon_utils,json,os
from pathlib import Path
addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True);bpy.ops.wm.open_mainfile(filepath=os.environ['CAD_TRI_SOURCE']);bpy.context.view_layer.update()
for o in bpy.context.scene.objects:
 x={'name':o.name,'type':o.type,'modifiers':[(m.name,m.type) for m in o.modifiers],'hideViewport':o.hide_get()}
 if o.type=='MESH':
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();x['evaluated']={'vertices':[list(e.matrix_world@v.co) for v in m.vertices],'edges':[list(v.vertices) for v in m.edges],'faces':[list(p.vertices) for p in m.polygons]};e.to_mesh_clear()
 print(json.dumps(x))
