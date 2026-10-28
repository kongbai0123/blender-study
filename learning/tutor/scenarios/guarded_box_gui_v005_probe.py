"""Probe guarded-box panel on a fake project, never the learner workspace.

The fixture and registration are programmatic; the panel interactions are
native GUI events. The fake project's entire root is inside this run's
demo-files, including a scratch progress.json and scratch personal copy.
"""
import importlib
import json
import runpy
import shutil
from pathlib import Path
import addon_utils
import bpy
from common import Kit, PROJECT


def build(g):
    k=Kit(g);out=Path(g['OUT']);base=Path(k.demo_dir)/'scratch-project'
    folder=base/'learning'/'workspaces'/'engineering-parametric';folder.mkdir(parents=True)
    tutor=base/'learning'/'tutor';tutor.mkdir(parents=True)
    fixture=base/'learning'/'progress.json';fixture.write_text(json.dumps({'fileVersions':[]}),encoding='utf-8')
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/demo-files/parametric_box_80x40_v003.blend'
    expected='a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2'
    if g['sha256'](source)!=expected: raise RuntimeError('source mismatch')
    copied=folder/'guard_trial_v001.blend';shutil.copyfile(source,copied)
    addon_src=PROJECT/'learning/tutor/guarded_box_parameters_v005.py'
    addon=tutor/'guarded_box_parameters_v005.py';shutil.copyfile(addon_src,addon)
    snap=out/'source-snapshot';snap.mkdir()
    refs=[]
    for path in (PROJECT/'learning/tutor/run_demo.py',PROJECT/'learning/tutor/blender_demo.py',PROJECT/'learning/tutor/scenarios/common.py',PROJECT/'learning/tutor/scenarios/guarded_box_gui_v005_probe.py',addon_src):
        target=snap/path.name;shutil.copyfile(path,target);refs.append({'source':str(path.relative_to(PROJECT)),'snapshot':target.name,'sha256':g['sha256'](target)})
    (snap/'manifest.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
    memo={}
    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons: raise RuntimeError('addon unavailable')
    def register(): memo['guard']=runpy.run_path(str(addon),run_name='__main__')
    def send(key,**kw): k.do(lambda:k.key(key,x=600,y=450,**kw),.6)
    def state(label):
        ref=importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk=ref.get_active_sketch(bpy.context)
        d={'label':label,'file':bpy.data.filepath,'activeSketch':sk.name if sk else None,
           'panelRegistrationMethod':'programmatic runpy of copied guard v003',
           'values':{key:float(bpy.context.scene[key]) for key in ('box_height_mm','box_wall_mm','box_bottom_mm','lid_plate_mm','lid_depth_mm','gap_total_mm','lid_lip_wall_mm') if key in bpy.context.scene}}
        if sk:d['sketch']={'solver':sk.solver_state,'dof':sk.dof,'constraints':{c.constraint_uid:float(c.value) for c in sk.constraints.all if c.type=='DISTANCE'}}
        try:
            _,_,_,vals=memo['guard']['_blender_state'](bpy.context);d['guardRead']=vals
        except Exception as exc:d['guardError']=str(exc)
        (out/(label+'-state.json')).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8');return d
    k.setup();k.do(enable,2)
    send('O',ctrl=True);k.fill_dialog(str(folder)+'\\',copied.name);k.confirm_dialog(wait=4)
    k.do(register,1)
    k.record('GUARD','fixture-opened','在 demo-files 的隔離測試專案開啟假個人副本；程式註冊受控面板',lambda:state('fixture-opened'))
    k.do(lambda:k.click(1213,320),1)
    k.record('GUARD','panel-click','以原生事件點擊側欄分頁並觀察面板位置',lambda:state('panel-click'))

    k.do(lambda:k.move(1076,173),.8)
    k.do(lambda:k.click(1076,173),1)
    k.record('GUARD','dialog-open','以原生事件開啟尺寸預檢對話框',lambda:state('dialog-open'))
    k.do(lambda:k.move(1150,182),.5)
    k.do(lambda:k.click(1150,182),.7)
    k.record('GUARD','field-menu','展開 v004 的參數下拉選單',lambda:state('field-menu'))
    k.do(lambda:k.move(1040,247),.5)
    k.do(lambda:k.click(1040,247),.7)
    k.record('GUARD','selected-w','選擇寬度 W',lambda:state('selected-w'))
    k.do(lambda:k.move(1150,182),.5)
    k.do(lambda:k.click(1150,182),.7)
    k.record('GUARD','menu-from-w','從 W 再次展開選單，觀察切換位置',lambda:state('menu-from-w'))
