"""Read-only, separate-process save/reopen dependency check for box proof.

Run in Blender background with isolated CAD Sketcher extension path, e.g.
blender --background --factory-startup --python this_file -- <scene> <output.json>
The in-memory parameter edit uses Python, NOT a GUI operation. Never saves.
"""
import json
import sys
from pathlib import Path

import addon_utils
import bpy

argv=sys.argv[sys.argv.index('--')+1:]
source,out=(Path(p).resolve() for p in argv)
addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
keys=[k for k in scene.keys() if k.startswith('slvs:c:')]
width=next(k for k in keys if abs(scene[k]-80)<1e-5)
def dimensions(name):
    o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=o.to_mesh()
    points=[o.matrix_world@v.co for v in mesh.vertices]
    result=[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
    o.to_mesh_clear()
    return result
def read(label):
    bpy.context.view_layer.update()
    return {'label':label,'width':scene[width],'box':dimensions('Parametric Box'),
            'lid':dimensions('Parametric Lid')}
before=read('loaded')
scene[width]=70.0
scene.update_tag()
after=read('in-memory-edit-only')
result={'checks':{'loadedBox':abs(before['box'][0]-80)<1e-4,
                  'loadedLid':abs(before['lid'][0]-80)<1e-4,
                  'editedBox':abs(after['box'][0]-70)<1e-4,
                  'editedLid':abs(after['lid'][0]-70)<1e-4},
        'before':before,'after':after,'method':'programmatic read and in-memory edit; no GUI, no save',
        'sourceSaved':False}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
if not all(result['checks'].values()): raise RuntimeError(str(result['checks']))
