"""Real GUI rejection from the exact 70 x 40 checkpoint in an isolated fixture.

Scene/script copies, addon enable and Text-block loading are programmatic
preparation. Alt+P, panel selection, proposed value and submission use GUI events.
"""
import importlib
import json
import shutil
from pathlib import Path
import addon_utils
import bpy
from common import Kit, PROJECT

SOURCE = PROJECT/'learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/demo-files/manual_guard_trial_70x40_v003.blend'
SOURCE_SHA = '9942f712fe5f7bf88daa9b144de0b29fbae5a9dd8217acdb96a3df0f3aacad3f'
NAMES = ('guarded_manual_box_v001.py', 'manual_box_auto_update_v002.py', 'manual_box_reference_v001.json')


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    base = out/'isolated-fixture'
    folder = base/'learning/workspaces/engineering-parametric'
    tutor = base/'learning/tutor'
    folder.mkdir(parents=True); tutor.mkdir(parents=True)
    progress = base/'learning/progress.json'
    progress.write_text(json.dumps({'fileVersions': []}), encoding='utf-8')
    if g['sha256'](SOURCE) != SOURCE_SHA:
        raise RuntimeError('source SHA changed')
    copy = folder/'manual_guard_unregistered_70x40_v001.blend'
    shutil.copyfile(SOURCE, copy)
    for name in NAMES:
        shutil.copyfile(PROJECT/'learning/tutor'/name, tutor/name)
    script_hashes = {name: g['sha256'](tutor/name) for name in NAMES}
    def send(key, **kw):
        k.do(lambda: k.key(key, x=600, y=450, **kw), .7)
    def mc(x, y):
        k.do(lambda: k.move(x,y), .3)
        k.do(lambda: k.click(x,y), .8)
    def state():
        ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk = ref.get_active_sketch(bpy.context)
        d = {'sourceSha256': SOURCE_SHA, 'scriptHashes': script_hashes,
             'fixtureFileRegistered': bool(json.loads(progress.read_text(encoding='utf8'))['fileVersions']),
             'activeSketch': sk.name if sk else None, 'bounds': {}}
        dg = bpy.context.evaluated_depsgraph_get()
        for name in ('Body','Body.001','Cube'):
            obj = bpy.context.scene.objects[name].evaluated_get(dg)
            mesh = obj.to_mesh()
            points = [obj.matrix_world@v.co for v in mesh.vertices]
            d['bounds'][name] = [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
            obj.to_mesh_clear()
        return d
    def assert_shape():
        d = state(); bounds = d['bounds']
        for name in ('Body','Cube'):
            for axis, length in ((0,70),(1,40)):
                if abs(bounds[name][axis][1]-bounds[name][axis][0]-length)>.003:
                    raise RuntimeError('unexpected evaluated outer size: '+json.dumps(d))
        for axis, lo, hi in ((0,2,68),(1,2,38)):
            if max(abs(bounds['Body.001'][axis][0]-lo),abs(bounds['Body.001'][axis][1]-hi))>.003:
                raise RuntimeError('unexpected cavity: '+json.dumps(d))
        if d['fixtureFileRegistered'] or d['activeSketch']!='Body Sketch':
            raise RuntimeError('invalid fixture context')
        return json.dumps(d, ensure_ascii=False)
    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher', default_set=True, persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons:
            raise RuntimeError('CAD addon unavailable')
    k.setup(); k.do(enable,2)
    send('O',ctrl=True); k.fill_dialog(str(folder)+'\\',copy.name); k.confirm_dialog(wait=4)
    k.record('G7040','opened','GUI 開啟未登記的70×40隔離副本，先核對盒、蓋及內腔。',assert_shape)
    send('F11',shift=True)
    def load_script():
        for old in list(bpy.data.texts):
            if old.name.startswith('guarded_manual_box_v001.py'):
                bpy.data.texts.remove(old)
        text = bpy.data.texts.load(str(tutor/'guarded_manual_box_v001.py'))
        k.area('TEXT_EDITOR').spaces.active.text = text
    k.do(load_script,1)
    k.record('G7040','text-prepared','程式載入隔離外部腳本；不是GUI開啟腳本的示範。',assert_shape)
    send('P',alt=True)
    k.do(lambda: None if hasattr(bpy.types,'MANUAL_BOX_PT_guard_v001') else (_ for _ in ()).throw(RuntimeError('panel unavailable')), .3)
    send('F5',shift=True)
    k.record('G7040','panel-ready','GUI Alt+P 註冊後回到3D Viewport，模型仍70×40。',assert_shape)
    # The source saved this sidebar category as active; verify its real screenshot
    # before treating any coordinates as reusable teaching instructions.
    mc(1075,173); mc(1150,182); mc(1040,248)
    mc(1040,206); mc(1040,206)
    k.do(lambda:k.key('A',ctrl=True),.3)
    k.do(lambda:k.type_text('80'),.4)
    k.do(lambda:k.key('RET'),.7)
    mc(910,256)
    k.record('G7040','y80-proposal','GUI 選寬度W並輸入80 mm，勾選確認；提交前外框仍70×40。',assert_shape)
    mc(1010,337)
    k.record('G7040','y80-refused','GUI 提交W80；核對拒絕訊息及盒、蓋70×40與內腔66×36保持。',assert_shape)
    send('ESC')
    k.record('G7040','after-refusal','關閉訊息後再次讀值；未保存、未登記或修改學員工作區。',assert_shape)
