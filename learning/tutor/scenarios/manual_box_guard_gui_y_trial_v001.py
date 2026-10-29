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
    source = PROJECT/'learning/evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend'
    expected = 'ddae8a3d3745146501d25527354352e6b71431b837c78c8269a43dc5e6a3dec6'
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
    send('H', alt=True)
    send('A', alt=True)
    mc(1320, 75)
    send('H')
    mc(700, 550)
    def require_body():
        d = state('selected-check')
        if d['active'] != 'Body':
            raise RuntimeError('Body was not selected')
    k.do(require_body, .2)
    mc(700, 550, 'RIGHTMOUSE')
    mc(805, 549)
    def require_outer():
        if state('outer-check')['activeSketch'] != 'Body Sketch':
            raise RuntimeError('outer sketch was not entered')
    k.do(require_outer, .3)
    k.record('GUARD', 'outer-sketch', 'GUI 選中 Body 並開啟外框草圖', lambda: state('outer-sketch'))
    send('F11', shift=True)
    k.do(lambda: k.click(650, 40), 1)
    k.fill_dialog(str(tutor)+'\\', 'guarded_manual_box_v001.py')
    k.confirm_dialog(wait=3)
    k.record('GUARD', 'script-open', '文字編輯器開啟隔離副本腳本；路徑由程式填入', lambda: state('script-open'))
    send('P', alt=True)
    k.record('GUARD', 'script-run', '在文字編輯器按 Alt+P 註冊面板', lambda: state('script-run'))
    send('F5', shift=True)
    k.record('GUARD', 'viewport', '返回 Blender 視圖，觀察面板位置', lambda: state('viewport'))

    mc(1213, 390)
    k.record('GUARD', 'panel', '切換手工盒預檢側欄', lambda: state('panel'))

    mc(1075, 173)
    k.record('GUARD', 'dialog', '開啟手工盒預檢尺寸對話框', lambda: state('dialog'))

    mc(1150, 182)
    k.record('GUARD', 'parameter-menu', '觀察尺寸參數選單', lambda: state('parameter-menu'))


    mc(1040,248)
    k.type_into(1150,206,'60')
    mc(910,256)
    k.record('GUARD','width-proposal','選寬度60並確認',lambda:state('width-proposal'))
    mc(1010,337)
    k.record('GUARD','width-result','提交寬度60後讀回',lambda:state('width-result'))
    def expect_width():
        d=state('width-assertion'); b=d['bounds']
        for name in ('Body','Cube'):
            if abs((b[name][1][1]-b[name][1][0])-60)>.003: raise RuntimeError('width did not update: '+name+str(b[name]))
        if abs(b['Body.001'][1][1]-58)>.003: raise RuntimeError('cavity did not update: '+str(b['Body.001']))
    k.do(expect_width,.5)
