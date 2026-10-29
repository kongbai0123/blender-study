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
    for path in (PROJECT/'learning/tutor/run_demo.py',PROJECT/'learning/tutor/blender_demo.py',PROJECT/'learning/tutor/scenarios/common.py',PROJECT/'learning/tutor/scenarios/guarded_box_text_editor_probe.py',addon_src):
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
           'panelRegistrationMethod':'Text Editor Open and Alt+P; file dialog path filled programmatically',
           'values':{key:float(bpy.context.scene[key]) for key in ('box_height_mm','box_wall_mm','box_bottom_mm','lid_plate_mm','lid_depth_mm','gap_total_mm','lid_lip_wall_mm') if key in bpy.context.scene}}
        if sk:d['sketch']={'solver':sk.solver_state,'dof':sk.dof,'constraints':{c.constraint_uid:float(c.value) for c in sk.constraints.all if c.type=='DISTANCE'}}
        d['evaluated']={}
        dg=bpy.context.evaluated_depsgraph_get()
        for name in ('Parametric Box','Parametric Lid'):
            obj=bpy.data.objects[name].evaluated_get(dg); mesh=obj.to_mesh()
            points=[obj.matrix_world@v.co for v in mesh.vertices]
            d['evaluated'][name]={'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)], 'vertices':len(points)}
            obj.to_mesh_clear()
        (out/(label+'-state.json')).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8');return d
    k.setup();k.do(enable,2)
    send('O',ctrl=True);k.fill_dialog(str(folder)+'\\',copied.name);k.confirm_dialog(wait=4)
    k.record('TEXTGUARD','fixture-opened','開啟隔離的假專案模型；插件以程式啟用',lambda:state('fixture-opened'))
    send('F11',shift=True)
    k.record('TEXTGUARD','text-editor','以 Shift+F11 切換 Text Editor，觀察 Open 位置',lambda:state('text-editor'))
    k.do(lambda:k.click(650,40),1)
    k.fill_dialog(str(tutor)+'\\',addon.name);k.confirm_dialog(wait=3)
    k.record('TEXTGUARD','script-opened','GUI 以 Text Editor 開啟隔離副本中的腳本；檔案路徑欄由程式填入',lambda:state('script-opened'))
    send('P',alt=True)
    k.record('TEXTGUARD','run-script','以 Alt+P 執行 Text Editor 內腳本',lambda:state('run-script'))
    send('F5',shift=True)
    k.do(lambda:k.click(1213,320),1)
    k.record('TEXTGUARD','panel','切回 3D View 並點擊側欄分頁；核對面板',lambda:state('panel'))
    k.do(lambda:k.move(1076,173),.8);k.do(lambda:k.click(1076,173),1)
    k.record('TEXTGUARD','dialog','按尺寸預檢並核對對話框',lambda:state('dialog'))
    def mc(x,y):
        k.do(lambda:k.move(x,y),.4);k.do(lambda:k.click(x,y),.8)
    mc(1150,182);mc(1040,247)
    k.do(lambda:k.move(1150,206),.4);k.type_into(1150,206,'50')
    mc(916,256);mc(1010,337)
    k.record('TEXTGUARD','valid-width','選 W=50、確認並提交；讀回草圖及盒蓋幾何',lambda:state('valid-width'))
    def verify_width():
        d=state('width-check')
        for name in ('Parametric Box','Parametric Lid'):
            b=d['evaluated'][name]['bounds']; assert abs(b[1][1]-b[1][0]-50)<.0001, (name,b)
    k.do(verify_width,.4)
