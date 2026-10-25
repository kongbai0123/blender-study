"""07-03: native Overhang UI and rigid baseline/candidate orientation comparison."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy

from common import Kit, PARK, PROJECT
from overhang_checks import read_analysis_mesh_data, validate_orientation, validate_layout

SOURCE = PROJECT/'learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/demo-files/u07_cantilever_snap_v001.blend'
SOURCE_SHA = '5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305'
GEOMETRY_RECORD = PROJECT/'learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/geometry-draft-record-v001.json'
GEOMETRY_SHA = '4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a'
PLAN = PROJECT/'learning/plans/07-03-print-orientation-draft-v001.json'
PLAN_SHA = '33831347ce131a3f29c107d18f24f0015b3314e8e8672dc2159b1d9badd4f6ac'
FACTS = PROJECT/'sources/engineering/overhang-source-facts-v001.json'
FACTS_SHA = 'a2fa8d6c556cacb533b94648a994e2cb92baa33fccd4b513d9681d34187d8c05'
FILENAME = 'u07_print_orientation_v001.blend'


def build(g):
    return _build(g,False)


def build_probe(g):
    return _build(g,True)


def _build(g,probe):
    k=Kit(g)
    do,click,key,move,record=k.do,k.click,k.key,k.move,k.record
    out=Path(g['OUT'])
    sources=Path(k.demo_dir)/'sources'
    sources.mkdir()
    copy=sources/SOURCE.name
    fixed=((SOURCE,SOURCE_SHA),(GEOMETRY_RECORD,GEOMETRY_SHA),(PLAN,PLAN_SHA),(FACTS,FACTS_SHA))
    for p,h in fixed:
        if g['sha256'](str(p))!=h:
            raise RuntimeError('Protected orientation input changed: '+str(p))
    copy.write_bytes(SOURCE.read_bytes())
    snaps=out/'source-snapshot'
    snaps.mkdir()
    files=[]
    paths=['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
           'learning/tutor/scenarios/lesson07_overhang.py','learning/tutor/scenarios/overhang_checks.py',
           'learning/tutor/scenarios/snapfit_checks.py','learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py']
    if probe:
        paths.append('learning/tutor/scenarios/lesson07_overhang_full_probe.py')
    for relative in paths:
        target=snaps/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    bindings=[]
    for original,name in ((PLAN,'print-orientation-plan-v001.json'),(FACTS,'overhang-source-facts-v001.json'),
                          (PROJECT/'sources/engineering/snapfit-source-facts-v001.json','snapfit-source-facts-v001.json'),
                          (GEOMETRY_RECORD,'source-geometry-record-v001.json')):
        target=snaps/name
        target.write_bytes(original.read_bytes())
        bindings.append(dict(source=original.relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+name,sha256=g['sha256'](str(target))))
    (snaps/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),files=files,dataBindings=bindings,
        sourceScene=str(SOURCE),sourceCopy=str(copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    plan=json.loads((snaps/'print-orientation-plan-v001.json').read_text('utf-8'))
    state=dict(poses={},settings_by_pose={},analysis_contexts={})
    hidden_expected={'Body':False,'Lid':False,'SnapTool':True,'FlangeTool':True}

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        for p,h in fixed+((copy,SOURCE_SHA),):
            if g['sha256'](str(p))!=h:
                raise RuntimeError('Original, copy or source record changed: '+str(p))

    def obj(name):
        return bpy.data.objects[name]

    def raw(name,filename):
        d=read_analysis_mesh_data(obj(name))
        d['cad_metadata']['matrix_world']=[list(row) for row in obj(name).matrix_world]
        d['cad_metadata']['object_rotation_euler_degrees']=[math.degrees(a) for a in obj(name).rotation_euler]
        write(filename,d)
        return d

    def tool_inventory():
        result={}
        for name in ('SnapTool','FlangeTool'):
            o=obj(name)
            shape=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
            result[name]=dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),location=list(o.location),rotation=list(o.rotation_euler),
                modifier_count=len(o.modifiers),matrix_world=[list(row) for row in o.matrix_world],
                local_mesh_sha256=hashlib.sha256(json.dumps(shape,separators=(',',':')).encode()).hexdigest())
        return result

    def visibility(name,hide):
        hidden_expected[name]=hide
        expected=dict(hidden_expected)
        def hide_target(target):
            do(lambda:click(1340,k.outliner_y(target)) if not obj(target).hide_get() else None,.3)
            def press():
                if not obj(target).hide_get():
                    if bpy.context.view_layer.objects.active!=obj(target):
                        raise RuntimeError('Wrong active object before Hide '+target)
                    key('H',x=700,y=600)
            do(press,.4)
        if hide:
            hide_target(name)
        else:
            do(lambda:key('H',alt=True,x=700,y=600),.4)
            for n,flag in expected.items():
                if flag:
                    hide_target(n)
        do(lambda:check_visibility(expected),.1)

    def check_visibility(expected):
        if {n:obj(n).hide_get() for n in expected}!=expected:
            raise RuntimeError('Expected solo finished part and hidden tools')

    def transform(axis,value,rotation=False):
        do(lambda:key('R' if rotation else 'G',x=700,y=600),.2)
        do(lambda:key(axis),.2)
        do(lambda:k.type_text(str(value) if rotation else str(value)+'mm'),.2)
        do(lambda:key('RET'),.5)

    def frame():
        if_edit=lambda:bpy.context.mode=='EDIT_MESH'
        do(lambda:click(236 if if_edit() else 184,38),.3)
        do(lambda:move(288 if if_edit() else 236,168),.3)
        do(lambda:click(288 if if_edit() else 236,168),.5)
        k.wheel_out(1)

    def viewing(kind,pose):
        if kind=='body' and pose=='candidate':
            do(lambda:key('NUMPAD_3',x=700,y=600),.3)
        else:
            do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.3)
        do(lambda:key('NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_6',x=700,y=600),.3)

    def native_settings():
        unchanged()
        view=k.view3d()
        s=bpy.context.scene.tool_settings.statvis
        settings=dict(type=s.type,axis=s.overhang_axis,minimum_radians=float(s.overhang_min),maximum_radians=float(s.overhang_max),
            minimum_deg=math.degrees(s.overhang_min),maximum_deg=math.degrees(s.overhang_max),
            show_statvis=bool(view.overlay.show_statvis),show_overlays=bool(view.overlay.show_overlays),
            shading=view.shading.type,xray=bool(view.shading.show_xray))
        if settings['type']!='OVERHANG' or settings['axis']!='NEG_Z' or not settings['show_statvis'] or not settings['show_overlays'] or settings['shading']!='SOLID' or settings['xray']:
            raise RuntimeError('Native Overhang UI is not enabled correctly: '+str(settings))
        if abs(settings['minimum_deg'])>1e-4 or abs(settings['maximum_deg']-45)>1e-4:
            raise RuntimeError('Actual native angular display range differs')
        return settings

    def analysis(name,kind,pose):
        label=kind+'_'+pose
        do(lambda:key('TAB',x=700,y=600),.3)
        do(lambda:key('THREE',x=700,y=600),.2)
        do(lambda:key('A',alt=True,x=700,y=600),.2)
        do(lambda:key('Z',alt=True,x=700,y=600) if k.view3d().shading.show_xray else None,.3)
        do(lambda:click(1076,38),.4)
        do(lambda:click(940,253) if not k.view3d().overlay.show_statvis else None,.4)
        def controls():
            settings=native_settings()
            if bpy.context.mode!='EDIT_MESH' or bpy.context.view_layer.objects.active!=obj(name):
                raise RuntimeError('Analysis must run on intended active Edit mesh')
            check_visibility({n:n!=name for n in ('Body','Lid','SnapTool','FlangeTool')})
            state['settings_by_pose'][label]=settings
            state['analysis_contexts'][label]=dict(mode=bpy.context.mode,active_object=name,only_finished_part_visible=name,
                source_tools_hidden=True,native_popover_checked=True)
            write('analysis-settings-by-pose.json',state['settings_by_pose'])
            return '%s：原生Mesh Analysis開／Overhang／世界−Z，Min %.9g°（%.9g rad）、Max %.9g°（%.9g rad）；Solid、Xray關。'%(label,settings['minimum_deg'],settings['minimum_radians'],settings['maximum_deg'],settings['maximum_radians'])
        record('07-03',label+'-controls','Edit Mode > 專用Overlays > Mesh Analysis：實拍並核對同一組原生設定',controls,
               note='0～45°只是本次顯示範圍，不是材料或列印可接受角度。')
        do(lambda:key('ESC'),.3)
        viewing(kind,pose)
        def measured():
            settings=native_settings()
            pose_raw=raw(name,label+'_mesh.json')
            result=validate_orientation(state['source_'+kind],pose_raw,kind,settings,pose=pose)
            state['poses'][label]=result
            write('pose-verification.json',state['poses'])
            summary=result['derived_polygon_statistics']['summary']
            bed,raised=summary['bed_contact'],summary['downward_not_bed_contact']
            return ('%s 實網格外框 %s mm、最低Z %.9g mm；床接觸朝下面 %d面／%.6g mm²，離床朝下面 %d面／%.6g mm²。'
                    '這些是另算polygon角度／面積，非GPU面數或切片支撐結論。')%(label,[round(v,6) for v in result['dimensions_mm']],result['minimum_world_z_mm'],bed['count'],bed['area_mm2'],raised['count'],raised['area_mm2'])
        record('07-03',label+'-analysis','關閉popover，以原生Overhang著色視角檢查；保存polygon／loop triangle讀值',measured,park=PARK,
               note='紅色床接觸面與離床朝下面分開記錄；未分析橋接、前層承托、支撐移除、附著或強度。')
        if kind=='lid' and pose=='candidate':
            do(lambda:key('NUMPAD_3',x=700,y=600),.3)
            record('07-03','lid-candidate-profile','右視查看翻面蓋板與高處凸緣的真實高度關係',measured,park=PARK,
                   note='側視不保證看見每個著色面；高處朝下面仍以實際polygon法線與Z範圍逐面記錄。')
        do(lambda:key('TAB',x=700,y=600),.3)

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',copy.name)
    record('07-03','source-dialog','File > Open，開啟07-02卡扣幾何草案同hash副本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def source_read():
        unchanged()
        if Path(bpy.data.filepath).resolve()!=copy.resolve():
            raise RuntimeError('Wrong source copy opened')
        for name in ('Body','Lid'):
            state['source_'+name.lower()]=raw(name,'source_'+name.lower()+'_mesh.json')
        state['source_tools']=tool_inventory()
        if not all(v['hidden'] for v in state['source_tools'].values()):
            raise RuntimeError('Construction tools must remain hidden')
        write('source-tool-inventory.json',state['source_tools'])
        return '原Body／Lid與07-02來源hash一致，先保存原world polygons／loop triangles／polygon normals；工具保持隱藏，不更動形狀。'
    record('07-03','source-geometry','改姿態前保存原幾何與原生polygon法線讀值',source_read,park=PARK)
    visibility('Lid',True)
    k.click_outliner('Body')
    transform('X',-40)
    transform('Z',15)
    frame()
    analysis('Body','body','baseline')
    transform('Y',90,rotation=True)
    transform('Z',15)
    frame()
    analysis('Body','body','candidate')
    visibility('Body',True)
    visibility('Lid',False)
    k.click_outliner('Lid')
    transform('X',40)
    transform('Z',-10.2)
    frame()
    analysis('Lid','lid','baseline')
    transform('X',180,rotation=True)
    transform('Z',-5)
    frame()
    analysis('Lid','lid','candidate')
    if probe:
        return

    visibility('Body',False)
    k.click_outliner('Lid')
    k.click_outliner('Body',ctrl=True)
    do(lambda:key('NUMPAD_7',x=700,y=600),.3)
    do(lambda:key('NUMPAD_2',x=700,y=600),.2)
    do(lambda:key('NUMPAD_2',x=700,y=600),.2)
    do(lambda:key('NUMPAD_6',x=700,y=600),.3)
    frame()
    def layout_read():
        unchanged()
        if tool_inventory()!=state['source_tools']:
            raise RuntimeError('Hidden construction tools changed')
        for kind,name in (('body','Body'),('lid','Lid')):
            d=raw(name,kind+'_candidate_mesh.json')
            state['poses'][kind+'_candidate']=validate_orientation(state['source_'+kind],d,kind,native_settings(),pose='candidate')
        state['layout']=validate_layout(state['poses']['body_candidate'],state['poses']['lid_candidate'])
        return '兩件候選均以world Z0為床面基準、X投影分開 %.6g mm；工具未移動、未納入分析。此處不是指定機型的床幅或已核准列印配置。'%state['layout']['x_projection_gap_mm']
    record('07-03','candidate-layout','Object Mode顯示兩件獨立候選方向，核對落床與分離距離',layout_read,park=PARK)
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('07-03','save-dialog','File > Save As，另存方向與Overhang比較草案u07_print_orientation_v001.blend',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    def safe_target():
        folder,name=k.browser()
        target=(Path(folder)/name).resolve()
        if target.parent!=Path(k.demo_dir).resolve() or name!=FILENAME or target.exists():
            raise RuntimeError('Unsafe orientation save target')
        unchanged()
    do(safe_target,.1)
    k.confirm_dialog(1.8)
    def saved():
        p=Path(bpy.data.filepath).resolve()
        if p!=(Path(k.demo_dir)/FILENAME).resolve() or not p.is_file():
            raise RuntimeError('New orientation version not saved')
        state.update(scene_path=str(p),scene_sha256=g['sha256'](str(p)),scene_bytes=p.stat().st_size)
        return '已另存%d bytes，SHA-256 %s；原幾何來源與副本未覆寫。'%(state['scene_bytes'],state['scene_sha256'])
    record('07-03','saved','Save As後讀回新檔名／bytes／hash',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('07-03','open-saved','File > Open，重開同一方向比較版本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def reopened():
        p=Path(bpy.data.filepath).resolve()
        if str(p)!=state['scene_path'] or g['sha256'](str(p))!=state['scene_sha256']:
            raise RuntimeError('Reopened orientation version differs')
        layout_read()
        final={n:dict(object_name=n,type=obj(n).type,hidden=obj(n).hide_get(),modifier_count=len(obj(n).modifiers),scale=list(obj(n).scale),
            location_mm=list(obj(n).location),rotation_euler_radians=list(obj(n).rotation_euler),matrix_world=[list(row) for row in obj(n).matrix_world]) for n in ('Body','Lid','SnapTool','FlangeTool')}
        if set(bpy.data.objects.keys())!=set(final) or any(v['hidden']!=(n.endswith('Tool')) or v['modifier_count'] or v['scale']!=[1,1,1] for n,v in final.items()):
            raise RuntimeError('Final inventory or finished/tool states differ')
        settings=native_settings()
        record_path=out/'print-orientation-record-v001.json'
        write(record_path.name,dict(plan,recordedAt=datetime.now(timezone.utc).isoformat(),source_scene=dict(path=str(SOURCE),sha256=SOURCE_SHA),
            reference_scene=dict(path=str(p),sha256=state['scene_sha256'],bytes=state['scene_bytes'],scene_role='print_orientation_comparison_draft'),
            analysis_settings=settings,poses=state['poses'],layout=state['layout']))
        result=dict(passed=True,kind='snapfit_print_orientation_demo',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_geometry_draft_path=str(GEOMETRY_RECORD),source_geometry_draft_sha256=GEOMETRY_SHA,source_geometry_draft_unchanged=True,
            scene_path=str(p),scene_sha256=state['scene_sha256'],scene_bytes=state['scene_bytes'],reopened=True,
            draft_plan_path=str(PLAN),draft_plan_sha256=PLAN_SHA,orientation_record_path=str(record_path),orientation_record_sha256=g['sha256'](str(record_path)),
            analysis_settings=settings,analysis_settings_by_pose=state['settings_by_pose'],analysis_contexts=state['analysis_contexts'],poses=state['poses'],layout=state['layout'],
            source_tools=state['source_tools'],final_tools=tool_inventory(),final_objects=final,
            rigid_geometry_only=True,geometry_modified=False,rotation_applied_to_mesh=False,mesh_analysis_overhang_checked=True,
            strength_analysis_performed=False,fit_qualification=False,exported_stl=False,slicer_checked=False,printed=False,fit_tested=False,
            material_grade=None,epsilon_allow=None,Q=None,required_deflection_mm=None,delta_allow_mm=None,forces=None,
            physical_measurements=None,fit_results=None,physical_interference=None,qualified_strength_N=None,qualified_clearance_mm=None,
            support_required=None,support_generation_performed=False,final_print_orientation_approved=None,slicer_support_settings=None,bridge_or_support_qualified=None,
            numericComparison=dict(dimensionsAbsMm=1e-4,angleBoundaryBandDeg=1e-4,purpose='Floating point geometry/angle comparison only; not manufacturing, printability or strength qualification'))
        write('verification.json',result)
        return '重開後兩候選剛體姿態、原形狀、Z0／間距與原生設定一致；4次原生分析已記錄。床接觸與離床朝下面分開，支撐／橋接／切片／材料／強度／試配仍待定。'
    record('07-03','reopened-verified','Open後重驗候選mesh、四姿態統計、設定與版本，保存比較紀錄',reopened,park=PARK)
