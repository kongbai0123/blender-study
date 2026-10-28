"""Observe native CAD Sketcher Extrude UI on a previously drawn sketch.

This is a probe, not a completed box or lid. The input sketch was constructed
with native events in a previous independent run; the Python used here only
loads a copy, enables the extension, and inspects Blender state.
"""
import importlib
import json
import shutil
from pathlib import Path
import addon_utils
import bpy
from common import Kit, PROJECT


def build(g):
    k=Kit(g); out=Path(g['OUT'])
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/demo-files/cad_rectangle_60x40_v001.blend'
    copied=Path(k.demo_dir)/'source_rectangle_60x40.blend'
    shutil.copyfile(source,copied)
    if g['sha256'](source)!=g['sha256'](copied): raise RuntimeError('source copy mismatch')
    folder=out/'source-snapshot';folder.mkdir()
    snapshots=[]
    for rel in ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/cad_sketcher_manual_extrude_probe.py']:
        p=folder/Path(rel).name;p.write_bytes((PROJECT/rel).read_bytes());snapshots.append({'source':rel,'snapshot':p.name,'sha256':g['sha256'](p)})
    (folder/'manifest.json').write_text(json.dumps(snapshots,indent=2),encoding='utf-8')
    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons: raise RuntimeError('addon unavailable')
    def send(key,**kw): k.do(lambda:k.key(key,x=600,y=450,**kw),.7)
    def state(label):
        ref=importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk=ref.get_active_sketch(bpy.context)
        dg=bpy.context.evaluated_depsgraph_get()
        items=[]
        for o in bpy.context.scene.objects:
            item={'name':o.name,'type':o.type,'hidden':o.hide_get(),'selected':o.select_get(),
                  'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]}
            if o.type in ('MESH','CURVES','CURVE'):
                try:
                    ev=o.evaluated_get(dg); mesh=ev.to_mesh()
                    points=[ev.matrix_world @ v.co for v in mesh.vertices]
                    item['evaluated']={'vertices':len(points),'faces':len(mesh.polygons),'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None}
                    ev.to_mesh_clear()
                except Exception as e: item['evaluationError']=str(e)
            items.append(item)
        v={'label':label,'mode':bpy.context.mode,'active':bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
           'activeSketch':sk.name if sk else None,'objects':items}
        (out/(label+'-state.json')).write_text(json.dumps(v,indent=2),encoding='utf-8');return v
    k.setup();k.do(enable,2)
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,copied.name);k.confirm_dialog(wait=4)
    k.record('EXTRUDE','opened-sketch','開啟先前原生事件建立的 60×40 完全約束草圖',lambda:state('opened-sketch'))
    send('A',ctrl=True,shift=True)
    k.record('EXTRUDE','left-sketch','Ctrl+Shift+A 離開草圖，準備測試外部 Extrude 工具',lambda:state('left-sketch'))
    send('E',ctrl=True,shift=True)
    k.record('EXTRUDE','tool-invoked','Ctrl+Shift+E 呼叫 CAD Sketcher Extrude 工具；檢查當時 UI',lambda:state('tool-invoked'))
    k.do(lambda:k.click(600,450),1)
    k.record('EXTRUDE','after-pick','點擊草圖位置，檢查工具狀態',lambda:state('after-pick'))
    k.do(lambda:k.type_text('30mm'),.5)
    send('RET')
    k.record('EXTRUDE','after-offset','在工具內嘗試輸入 30 mm，讀回評估幾何（探測，未宣稱成功）',lambda:state('after-offset'))
