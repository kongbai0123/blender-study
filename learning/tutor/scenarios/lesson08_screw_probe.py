"""Explore Screw modifier UI for an explicitly open, non-printable thread surface.

The three-vertex input contour and scene visibility are programmatic setup;
modifier creation is requested through the native F3 search UI.
"""
import json
from pathlib import Path
import bpy
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'

def build(g):
    k=Kit(g);out=Path(g['OUT']); snapshot=out/'source-snapshot';snapshot.mkdir()
    files=[]
    for rel in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_screw_probe.py'):
        p=snapshot/Path(rel).name;p.write_bytes((PROJECT/rel).read_bytes())
        files.append({'source':rel,'snapshot':p.name,'sha256':g['sha256'](p)})
    (snapshot/'manifest.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
    if g['sha256'](SOURCE)!=SOURCE_HASH: raise RuntimeError('reference scene hash differs')
    source_copy=Path(k.demo_dir)/SOURCE.name;source_copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](source_copy)!=SOURCE_HASH: raise RuntimeError('reference copy differs')
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.5)
    def read():
        obj=bpy.data.objects.get('Thread_Profile')
        if obj is None:return {'profile':None}
        data={'sourceVertices':[list(v.co) for v in obj.data.vertices], 'sourceEdges':len(obj.data.edges),
              'modifiers':[{'name':m.name,'type':m.type,'angle':m.angle,'screwOffset':m.screw_offset,
                            'iterations':m.iterations,'steps':m.steps,'renderSteps':m.render_steps,
                            'axis':m.axis,'useObjectScrewOffset':m.use_object_screw_offset,
                            'useMergeVertices':m.use_merge_vertices} for m in obj.modifiers if m.type=='SCREW']}
        (out/'latest-readback.json').write_text(json.dumps(data,indent=2),encoding='utf-8');return data
    def prepare():
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
        scene.unit_settings.length_unit='MILLIMETERS'
        bpy.data.objects['Body_Reference'].hide_set(True)
        mesh=bpy.data.meshes.new('Open_Profile_Mesh')
        mesh.from_pydata([(5,0,0),(6,0,.5),(5,0,1)],[(0,1),(1,2)],[])
        obj=bpy.data.objects.new('Thread_Profile',mesh);scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.context.view_layer.update()
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3)
    k.do(prepare,1)
    k.record('08-PROBE','profile','程式建立半徑 5→6→5 mm、軸向 0→0.5→1 mm 的開放牙型線；隱藏原盒（不是 GUI 建模）',read)
    send('F3');k.do(lambda:k.type_text('Add Screw Modifier'),.5);send('RET')
    k.do(lambda:k.click(1246,k.props_y(300)),.8)
    k.record('08-PROBE','screw-added','F3 搜尋 Add Screw Modifier，讀回實際修改器設定',read)
