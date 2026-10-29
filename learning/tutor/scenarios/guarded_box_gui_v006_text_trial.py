"""Probe guarded-box panel on a fake project, never the learner workspace.

The fixture is created programmatically under system temporary storage; Text Editor
Open and Alt+P and panel interactions are native GUI events. File-dialog fields
are populated programmatically. No learner workspace or progress is touched.
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
    k=Kit(g);out=Path(g['OUT']);base=Path(tempfile.mkdtemp(prefix='blender-guard-v006-fixture-',dir=str(Path(os.environ['USERPROFILE'])/'AppData'/'Local'/'Temp')))
    folder=base/'learning'/'workspaces'/'engineering-parametric';folder.mkdir(parents=True)
    tutor=base/'learning'/'tutor';tutor.mkdir(parents=True)
    fixture=base/'learning'/'progress.json';fixture.write_text(json.dumps({'fileVersions':[]}),encoding='utf-8')
    source=PROJECT/'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/demo-files/parametric_box_80x40_v003.blend'
    expected='a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2'
    if g['sha256'](source)!=expected: raise RuntimeError('source mismatch')
    copied=folder/'guard_trial_v001.blend';shutil.copyfile(source,copied)
    addon_src=PROJECT/'learning/tutor/guarded_box_parameters_v006.py'
    addon=tutor/'guarded_box_parameters_v006.py';shutil.copyfile(addon_src,addon)
    snap=out/'source-snapshot';snap.mkdir()
    refs=[]
    for path in (PROJECT/'learning/tutor/run_demo.py',PROJECT/'learning/tutor/blender_demo.py',PROJECT/'learning/tutor/scenarios/common.py',PROJECT/'learning/tutor/scenarios/guarded_box_gui_v006_text_trial.py',addon_src):
        target=snap/path.name;shutil.copyfile(path,target);refs.append({'source':str(path.relative_to(PROJECT)),'snapshot':target.name,'sha256':g['sha256'](target)})
    (snap/'manifest.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons: raise RuntimeError('addon unavailable')
    def send(key,**kw): k.do(lambda:k.key(key,x=600,y=450,**kw),.6)
    def state(label):
        ref=importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sk=ref.get_active_sketch(bpy.context)
        d={'label':label,'file':bpy.data.filepath,'activeSketch':sk.name if sk else None,
           'panelRegistrationMethod':'native Text Editor Open and Alt+P; dialog path filled programmatically',
           'values':{key:float(bpy.context.scene[key]) for key in ('box_height_mm','box_wall_mm','box_bottom_mm','lid_plate_mm','lid_depth_mm','gap_total_mm','lid_lip_wall_mm') if key in bpy.context.scene}}
        if sk:d['sketch']={'solver':sk.solver_state,'dof':sk.dof,'constraints':{c.constraint_uid:float(c.value) for c in sk.constraints.all if c.type=='DISTANCE'}}
        if sk:
            d['guardRead']={'L':float(next(c.value for c in sk.constraints.all if c.constraint_uid=='b596b36138076155')), 'W':float(next(c.value for c in sk.constraints.all if c.constraint_uid=='854e8777cfe2608d')), 'D':float(bpy.context.scene['lid_depth_mm'])}
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
    k.record('GUARD','fixture-opened','系統暫存區假專案開啟假個人副本',lambda:state('fixture-opened'))
    send('F11',shift=True)
    k.do(lambda:k.click(650,40),1)
    k.fill_dialog(str(tutor)+'\\',addon.name);k.confirm_dialog(wait=3)
    k.record('GUARD','script-opened','在 Text Editor 開啟 v006；路徑由程式填入',lambda:state('script-opened'))
    send('P',alt=True)
    k.record('GUARD','script-run','Alt+P 執行受控面板腳本',lambda:state('script-run'))
    send('F5',shift=True)
    k.do(lambda:k.click(1213,320),1)
    k.record('GUARD','panel-click','以原生事件點擊側欄分頁並觀察面板位置',lambda:state('panel-click'))

    k.do(lambda:k.move(1076,173),.8)
    k.do(lambda:k.click(1076,173),1)
    k.record('GUARD','dialog-open','以原生事件開啟尺寸預檢對話框',lambda:state('dialog-open'))
    def move_click(x,y):
        k.do(lambda:k.move(x,y),.4);k.do(lambda:k.click(x,y),.8)
    def type_field(value):
        k.do(lambda:k.move(1150,206),.4);k.type_into(1150,206,str(value))
    def confirm_dialog():
        move_click(916,256);move_click(1010,337)
    def assert_after(label, width, depth):
        d=state(label)
        vals=d.get('guardRead')
        if not vals or abs(vals['L']-width)>1e-4 or abs(vals['W']-depth)>1e-4:
            raise RuntimeError('guard values not expected: '+json.dumps(d,ensure_ascii=False))
        if label == 'invalid-assertion' and abs(vals['D']-4)>1e-4:
            raise RuntimeError('invalid edit changed D')
        for name in ('Parametric Box','Parametric Lid'):
            b=d['evaluated'][name]['bounds']
            if abs(b[0][1]-b[0][0]-width)>1e-4 or abs(b[1][1]-b[1][0]-depth)>1e-4:
                raise RuntimeError('dependent bounds not expected: '+json.dumps(d,ensure_ascii=False))
    # An explicit tick with no field must not change the model.
    move_click(916,256);move_click(1010,337)
    k.record('GUARD','empty-attempt','未選參數／未填值而提交，應遭拒絕',lambda:state('empty-attempt'))
    k.do(lambda:assert_after('empty-assertion',80,40),.5);send('ESC')
    # Switch W to L after filling and acknowledging; both edit and acknowledgement must reset.
    move_click(1076,173);move_click(1150,182);move_click(1040,247)
    type_field(70);move_click(916,256)
    k.record('GUARD','switch-before','選 W 並輸入 70、勾選，切換前記錄',lambda:state('switch-before'))
    move_click(1150,182);move_click(1040,225)
    k.record('GUARD','switch-after','改選 L 後觀察值與勾選是否清空',lambda:state('switch-after'))
    move_click(1010,337)
    k.record('GUARD','switch-attempt','切換後未重新輸入及確認而提交，預期被拒',lambda:state('switch-attempt'))
    k.do(lambda:assert_after('switch-assertion',80,40),.5);send('ESC')
    # Editing the numeric value after acknowledgement must remove acknowledgement.
    move_click(1076,173);move_click(1150,182);move_click(1040,247)
    type_field(70);move_click(916,256)
    k.record('GUARD','value-before','輸入 W=70 並勾選後，記錄切換前狀態',lambda:state('value-before'))
    type_field(90)
    k.record('GUARD','value-after','將 W 新值改為 90；檢查確認是否自動取消',lambda:state('value-after'))
    move_click(1010,337)
    k.record('GUARD','unack-attempt','更改數值後未重新勾選而提交，預期拒絕',lambda:state('unack-attempt'))
    k.do(lambda:assert_after('unack-assertion',80,40),.5);send('ESC')
    # Valid W=50.
    move_click(1076,173);move_click(1150,182);move_click(1040,247)
    type_field(50);move_click(916,256)
    k.record('GUARD','width-proposal','選 W，輸入50並勾選確認',lambda:state('width-proposal'))
    move_click(1010,337)
    k.record('GUARD','width-changed','提交 W=50，讀回草圖及盒蓋幾何',lambda:state('width-changed'))
    k.do(lambda:assert_after('width-assertion',80,50),.5)
    # D=29 fails H-D >= B; original D=4 and dimensions must remain intact.
    move_click(1076,173);move_click(1150,182);move_click(1040,357)
    type_field(29);move_click(916,256)
    k.record('GUARD','invalid-proposal','選 D=29，H−D 小於底厚，預期被拒絕',lambda:state('invalid-proposal'))
    move_click(1010,337)
    k.record('GUARD','invalid-attempt','提交 D=29，觀察錯誤提示及讀回值',lambda:state('invalid-attempt'))
    k.do(lambda:assert_after('invalid-assertion',80,50),.5);send('ESC')
    # Explicitly select L each time; never assume a remembered enum value.
    move_click(1076,173);move_click(1150,182);move_click(1040,225)
    type_field(70);move_click(916,256)
    k.record('GUARD','length-proposal','選 L=70 並勾選確認',lambda:state('length-proposal'))
    move_click(1010,337)
    k.record('GUARD','length-changed','提交 L=70，讀回草圖與盒蓋',lambda:state('length-changed'))
    k.do(lambda:assert_after('length-assertion',70,50),.5)
    k.file_dialog(163,str(folder)+'\\','guard_trial_v002.blend');k.confirm_dialog(wait=2)
    k.record('GUARD','saved','在隔離測試專案另存 v002',lambda:state('saved'))
    send('O',ctrl=True);k.fill_dialog(str(folder)+'\\','guard_trial_v002.blend');k.confirm_dialog(wait=4)
    k.record('GUARD','reopened','重開隔離測試副本，檢查尺寸及兩件幾何',lambda:state('reopened'))
    k.do(lambda:assert_after('reopened-assertion',70,50),.5)
    def register_fixture():
        fixture.write_text(json.dumps({'fileVersions':[{'path':'learning/workspaces/engineering-parametric/guard_trial_v002.blend'}]}),encoding='utf-8')
    k.do(register_fixture,.3)
    k.record('GUARD','registered-fixture','程式在隔離測試 progress 登記同一版本；未更動真實進度',lambda:state('registered-fixture'))
    move_click(1076,173)
    k.record('GUARD','registered-attempt','對已登記的隔離測試版本嘗試開啟面板，確認拒絕',lambda:state('registered-attempt'))
    def verify_registered():
        d=state('registered-assertion')
        if '已登記' not in d.get('guardError',''): raise RuntimeError('registered fixture not rejected: '+json.dumps(d,ensure_ascii=False))
    k.do(verify_registered,.5)
