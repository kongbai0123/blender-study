"""Probe the manual-box guard UI in a fake isolated project.

The fake project, progress and .blend are created under system temp.  CAD
Sketcher is enabled by Python, file-dialog paths are filled by the runner;
selection, Text Editor Open and Run Script use Blender UI events.
"""
import importlib
import json
import os
import shutil
import tempfile
from pathlib import Path
import addon_utils
import bpy
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    base = Path(tempfile.mkdtemp(prefix='manual-box-guard-fixture-', dir=str(Path(os.environ['USERPROFILE'])/'AppData'/'Local'/'Temp')))
    folder = base/'learning'/'workspaces'/'engineering-parametric'
    folder.mkdir(parents=True)
    tutor = base/'learning'/'tutor'
    tutor.mkdir(parents=True)
    (base/'learning'/'progress.json').write_text(json.dumps({'fileVersions': []}), encoding='utf-8')
    source = PROJECT/'learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/demo-files/manual_guard_trial_70x40_v003.blend'
    expected = '9942f712fe5f7bf88daa9b144de0b29fbae5a9dd8217acdb96a3df0f3aacad3f'
    if g['sha256'](source) != expected:
        raise RuntimeError('source hash mismatch')
    copied = folder/'guard_manual_trial_v001.blend'
    shutil.copyfile(source, copied)
    filenames = ['guarded_manual_box_v001.py', 'manual_box_auto_update_v002.py', 'manual_box_reference_v001.json']
    for name in filenames:
        shutil.copyfile(PROJECT/'learning'/'tutor'/name, tutor/name)
    snap = out/'source-snapshot'
    snap.mkdir()
    manifest = []
    for path in [PROJECT/'learning/tutor/run_demo.py', PROJECT/'learning/tutor/blender_demo.py',
                 PROJECT/'learning/tutor/scenarios/common.py', Path(__file__),
                 *(PROJECT/'learning'/'tutor'/name for name in filenames)]:
        target = snap/path.name
        shutil.copyfile(path, target)
        manifest.append({'source': str(path.relative_to(PROJECT)), 'snapshot': target.name, 'sha256': g['sha256'](target)})
    (snap/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher', default_set=True, persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons:
            raise RuntimeError('CAD Sketcher unavailable')

    def send(key, **kw):
        k.do(lambda: k.key(key, x=600, y=450, **kw), .7)

    def mc(x, y, button='LEFTMOUSE'):
        k.do(lambda: k.move(x, y), .4)
        k.do(lambda: k.click(x, y, button=button), 1)

    def state(label):
        ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk = ref.get_active_sketch(bpy.context)
        result = {'label': label, 'active': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
                  'activeSketch': sk.name if sk else None, 'mode': bpy.context.mode}
        if sk:
            result['constraints'] = {c.constraint_uid: float(c.value) for c in sk.constraints.all if c.type == 'DISTANCE'}
        result['bounds'] = {}
        dg = bpy.context.evaluated_depsgraph_get()
        for name in ('Body', 'Body.001', 'Cube'):
            obj = bpy.context.scene.objects[name].evaluated_get(dg)
            mesh = obj.to_mesh()
            points = [obj.matrix_world @ v.co for v in mesh.vertices]
            result['bounds'][name] = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
            obj.to_mesh_clear()
        (out/(label+'-state.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
        return result

    k.setup()
    k.do(enable, 2)
    send('O', ctrl=True)
    k.fill_dialog(str(folder)+'\\', copied.name)
    k.confirm_dialog(wait=4)
    k.record('GUARD', 'opened', '開啟隔離假專案手工盒副本', lambda: state('opened'))
    def require_outer():
        if state('outer-check')['activeSketch'] != 'Body Sketch':
            raise RuntimeError('saved outer sketch not active')
    k.do(require_outer,.3)
    k.record('GUARD','outer-sketch','新 Blender 執行期重開70×40測試副本',lambda:state('outer-sketch'))
    send('F11', shift=True)
    k.do(lambda: k.click(650, 40), 1)
    k.fill_dialog(str(tutor)+'\\', 'guarded_manual_box_v001.py')
    k.confirm_dialog(wait=3)
    k.record('GUARD', 'script-open', '文字編輯器開啟隔離副本腳本；路徑由程式填入', lambda: state('script-open'))
    send('P', alt=True)
    k.record('GUARD', 'script-run', '在文字編輯器按 Alt+P 註冊面板', lambda: state('script-run'))
    send('F5', shift=True)
    k.record('GUARD', 'viewport', '返回 Blender 視圖，觀察面板位置', lambda: state('viewport'))

    mc(1213,390);mc(1075,173);mc(1150,182);mc(1040,225)
    mc(1040,206);mc(1040,206)
    k.do(lambda:k.key('A',ctrl=True),.3);k.do(lambda:k.type_text('80'),.4);k.do(lambda:k.key('RET'),1)
    mc(910,256)
    k.record('GUARD','restart-proposal','重新載入面板後選 L80 並核對',lambda:state('restart-proposal'))
    mc(1010,337)
    k.record('GUARD','restart-result','提交80後讀回盒蓋及內腔',lambda:state('restart-result'))
    def check():
        d=state('restart-assertion');b=d['bounds']
        if abs(b['Body'][0][1]-80)>.003 or abs(b['Body'][1][1]-40)>.003 or abs(b['Body.001'][0][1]-78)>.003 or abs(b['Body.001'][1][1]-38)>.003 or abs(b['Cube'][0][1]-80)>.003: raise RuntimeError('restart result mismatch '+str(b))
    k.do(check,.5)
