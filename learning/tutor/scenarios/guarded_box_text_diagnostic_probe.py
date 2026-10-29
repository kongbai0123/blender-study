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
    addon=tutor/'guard_path_diagnostic.py'
    diag = """import bpy, json, os, stat, traceback
from pathlib import Path
scratch = Path(SCRATCH_LITERAL).resolve()
file_repr = repr(__file__)
text_path = bpy.context.space_data.text.filepath
absolute = bpy.path.abspath(text_path)
resolved = Path(__file__).resolve()
root = resolved.parents[2]
info = {'file_repr': file_repr, 'text_filepath': text_path, 'blender_abspath': absolute, 'resolved': str(resolved), 'root': str(root)}
for name, target in [('computed_workspace',root/'learning'/'workspaces'/'engineering-parametric'),('computed_progress',root/'learning'/'progress.json'),('actual_workspace',scratch/'learning'/'workspaces'/'engineering-parametric'),('actual_progress',scratch/'learning'/'progress.json'),('scene',Path(bpy.data.filepath))]:
    entry={'target':str(target)}
    try:
        target.relative_to(scratch)
        current=scratch
        entry['parts']=[]
        for part in target.relative_to(scratch).parts:
            current=current/part
            try:
                st=current.lstat();entry['parts'].append({'part':part,'exists':True,'is_link':stat.S_ISLNK(st.st_mode),'attributes':getattr(st,'st_file_attributes',0)})
            except Exception as e:
                entry['parts'].append({'part':part,'exists':False,'exception':repr(e)});raise
        entry['exists']=target.exists()
    except Exception as e:
        entry['exception']=repr(e)
    info[name]=entry
try:
    p=Path(os.path.abspath(bpy.data.filepath)); p.relative_to(root)
except Exception as e:
    info['original_exception']=repr(e)
Path(OUTPUT_LITERAL).write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
""".replace('SCRATCH_LITERAL',repr(str(base))).replace('OUTPUT_LITERAL',repr(str(out/'text-path-diagnostic.json')))
    addon.write_text(diag,encoding='utf-8')
    snap=out/'source-snapshot';snap.mkdir()
    refs=[]
    for path in (PROJECT/'learning/tutor/run_demo.py',PROJECT/'learning/tutor/blender_demo.py',PROJECT/'learning/tutor/scenarios/common.py',PROJECT/'learning/tutor/scenarios/guarded_box_text_diagnostic_probe.py',addon_src):
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
