"""07-04: actual selection-only STL exports of the two orientation candidates.

All geometry, transforms and source checkpoints remain unchanged.  The native
STL importer is used in a new millimetre scene to expose the world-coordinate
dimensions in Item.  Printed fit, supports and strength remain unqualified.
"""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from overhang_checks import read_analysis_mesh_data, validate_layout
from stl_checks import read_stl
from snapfit_stl_checks import validate_snapfit_stl, validate_snapfit_export_mesh

SOURCE_RUN=PROJECT/'learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001'
SOURCE=SOURCE_RUN/'demo-files/u07_print_orientation_v001.blend'
SOURCE_SHA='360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d'
ORIENTATION_RECORD=SOURCE_RUN/'print-orientation-record-v001.json'
ORIENTATION_SHA='b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986'
PRIOR_SHA='ab84fcc47ee59d2303a1174a8b67c27c898255c5c556e3b0deaee616741b9dc7'
PARTS=(dict(kind='body',name='Body',other='Lid',imported='Body_STL',filename='u07_snap_body_v001.stl'),
       dict(kind='lid',name='Lid',other='Body',imported='Lid_STL',filename='u07_snap_lid_v001.stl'))
EXPORT_OPTIONS=dict(only_selected=True,global_scale=1.0,use_scene_unit=False,apply_modifiers=True,
                    forward_axis='Y',up_axis='Z',ascii_format=False,use_batch=False,evaluation_mode='DAG_EVAL_RENDER')
IMPORT_OPTIONS=dict(global_scale=1.0,use_scene_unit=False,forward_axis='Y',up_axis='Z')


def build(g):
    return _build(g,False)


def build_probe(g):
    return _build(g,True)


def _build(g,probe):
    k=Kit(g)
    do,click,key,move,record=k.do,k.click,k.key,k.move,k.record
    B=k.box
    out=Path(g['OUT'])
    copies,exports=Path(k.demo_dir)/'sources',Path(k.demo_dir)/'exports'
    copies.mkdir();exports.mkdir()
    copy=copies/SOURCE.name
    fixed=((SOURCE,SOURCE_SHA),(ORIENTATION_RECORD,ORIENTATION_SHA),(SOURCE_RUN/'verification.json',PRIOR_SHA),
        (SOURCE_RUN/'body_candidate_mesh.json','e87e0387385977798febd880956379e5e9694928cac1f20d43a94d92f03caec8'),
        (SOURCE_RUN/'lid_candidate_mesh.json','99e7b3aced9fb8892f37d5480c1d7326cb48a11c987ff7ceee8f809ce1d27573'))
    for p,h in fixed:
        if g['sha256'](str(p))!=h:raise RuntimeError('Protected 07-03 checkpoint changed: '+str(p))
    prior=json.loads((SOURCE_RUN/'verification.json').read_text('utf-8'))
    if prior.get('passed') is not True or prior.get('scene_sha256')!=SOURCE_SHA:
        raise RuntimeError('07-03 candidate source did not pass')
    copy.write_bytes(SOURCE.read_bytes())
    snaps=out/'source-snapshot';snaps.mkdir();files=[]
    dependencies=['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
        'learning/tutor/scenarios/lesson07_snap_export.py','learning/tutor/scenarios/overhang_checks.py',
        'learning/tutor/scenarios/snapfit_checks.py','learning/tutor/scenarios/tenon_checks.py',
        'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
        'learning/tutor/scenarios/snapfit_stl_checks.py']
    if probe:dependencies.append('learning/tutor/scenarios/lesson07_snap_export_probe.py')
    for relative in dependencies:
        target=snaps/Path(relative).name;target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    bindings=[]
    for original,name in ((ORIENTATION_RECORD,'source-orientation-record-v001.json'),
        (SOURCE_RUN/'verification.json','source-orientation-verification.json'),
        (SOURCE_RUN/'body_candidate_mesh.json','source-body-candidate-mesh.json'),
        (SOURCE_RUN/'lid_candidate_mesh.json','source-lid-candidate-mesh.json')):
        target=snaps/name;target.write_bytes(original.read_bytes())
        bindings.append(dict(source=original.relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+name,
                             sha256=g['sha256'](str(target))))
    write_manifest=dict(recordedAt=datetime.now(timezone.utc).isoformat(),files=files,dataBindings=bindings,
        sourceScene=str(SOURCE),sourceCopy=str(copy),sourceSha256=SOURCE_SHA)
    (snaps/'manifest.json').write_text(json.dumps(write_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    expected_raw={p['kind']:json.loads((snaps/('source-'+p['kind']+'-candidate-mesh.json')).read_text('utf-8')) for p in PARTS}
    state=dict(exports=[],source_raw={},source={},export_options={},import_options={},reimport={},reimport_raw={},
               export_operator_before_confirm={},import_operator_before_confirm={})

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        for p,h in fixed+((copy,SOURCE_SHA),):
            if g['sha256'](str(p))!=h:raise RuntimeError('Protected original, copy or record changed: '+str(p))

    def active_mesh():
        o=bpy.context.view_layer.objects.active
        if o is None or o.type!='MESH':raise RuntimeError('Expected active mesh')
        return o

    def raw(name,filename):
        obj=bpy.data.objects[name]
        result=read_analysis_mesh_data(obj)
        result['cad_metadata']['matrix_world']=[list(row) for row in obj.matrix_world]
        result['cad_metadata']['object_rotation_euler_degrees']=[math.degrees(a) for a in obj.rotation_euler]
        result['cad_metadata']['object_axis_dimensions_mm']=list(obj.dimensions)
        write(filename,result)
        return result

    def world_bounds(mesh):
        return {side:[fn(p[a] for p in mesh['vertices']) for a in range(3)]
                for side,fn in (('min',min),('max',max))}

    def world_dimensions(mesh):
        b=world_bounds(mesh)
        return [b['max'][i]-b['min'][i] for i in range(3)]

    def export_layout(body,lid):
        measured=[]
        for part,kind in ((body,'body'),(lid,'lid')):
            bounds=world_bounds(part)
            measured.append(dict(passed=True,pose='candidate',part_kind=kind,
                bounds_mm=bounds,minimum_world_z_mm=bounds['min'][2]))
        return validate_layout(*measured)

    def inventory():
        return {o.name:dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),
            location_mm=list(o.location),rotation_euler_radians=list(o.rotation_euler),
            object_axis_dimensions_mm=list(o.dimensions),modifier_count=len(o.modifiers),
            matrix_world=[list(row) for row in o.matrix_world]) for o in bpy.data.objects}

    def tools():
        result={}
        for name in ('SnapTool','FlangeTool'):
            o=bpy.data.objects[name]
            shape=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
            result[name]=dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),location=list(o.location),
                rotation=list(o.rotation_euler),modifier_count=len(o.modifiers),matrix_world=[list(row) for row in o.matrix_world],
                local_mesh_sha256=hashlib.sha256(json.dumps(shape,separators=(',',':')).encode()).hexdigest())
        return result

    def frame(notches=1):
        do(lambda:click(184,38),.35);k.menu_item(236,168,.6);k.wheel_out(notches)

    def oblique():
        do(lambda:key('NUMPAD_1',x=700,y=600),.4)
        do(lambda:key('NUMPAD_6',x=700,y=600),.3)
        do(lambda:key('NUMPAD_8',x=700,y=600),.4)

    def search(text):
        do(lambda:key('F3',x=700,y=600),.3);do(lambda:k.type_text(text),.3);do(lambda:key('RET'),1)

    def op_properties():
        return k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator.properties

    def options(p,export):
        result=dict(global_scale=float(p.global_scale),use_scene_unit=bool(p.use_scene_unit),forward_axis=p.forward_axis,up_axis=p.up_axis)
        if export:result.update(only_selected=bool(p.export_selected_objects),apply_modifiers=bool(p.apply_modifiers),
            ascii_format=bool(p.ascii_format),use_batch=bool(p.use_batch),evaluation_mode=p.evaluation_mode)
        return result

    def dialog_operator(export):
        op=k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator
        folder,name=k.browser()
        expected='WM_OT_stl_export' if export else 'WM_OT_stl_import'
        if op.bl_idname!=expected:raise RuntimeError('Wrong live native file-browser operator: '+op.bl_idname)
        return dict(idname=op.bl_idname,options=options(op.properties,export),filepath=str((Path(folder)/name).resolve()),
                    captured_at='live_file_browser_before_native_confirm')

    def executed_operator(export,part):
        expected='WM_OT_stl_export' if export else 'WM_OT_stl_import'
        ops=[op for op in bpy.context.window_manager.operators if op.bl_idname==expected]
        captured=state['export_operator_before_confirm' if export else 'import_operator_before_confirm'][part['kind']]
        result=dict(captured,operator_history_available=bool(ops),
            execution_verified_by='native UI confirmation and new binary STL readback' if export else 'native UI confirmation and newly created mesh readback')
        if ops:
            op=ops[-1]
            actual=dict(idname=op.bl_idname,options=options(op.properties,export),filepath=str(Path(op.properties.filepath).resolve()))
            if any(actual[key]!=captured[key] for key in ('idname','options','filepath')):
                raise RuntimeError('Registered native operator differs from captured dialog operator')
            result['operator_history_entry']=actual
        return result

    def source_read(part):
        unchanged()
        if Path(bpy.data.filepath).resolve()!=copy.resolve():raise RuntimeError('Wrong source copy opened')
        if set(bpy.data.objects.keys())!={'Body','Lid','SnapTool','FlangeTool'}:raise RuntimeError('Unexpected source objects')
        if active_mesh().name!=part['name'] or [o.name for o in bpy.context.selected_objects]!=[part['name']]:
            raise RuntimeError('Exactly the intended finished part must be selected')
        if any(not bpy.data.objects[n].hide_get() for n in ('SnapTool','FlangeTool',part['other'])):
            raise RuntimeError('Tools and counterpart must stay hidden')
        t=tools()
        if t!=prior['final_tools']:raise RuntimeError('Hidden source tools moved or changed')
        state['source_tools']=t;state['source_objects']=inventory()
        for p in PARTS:
            mesh=raw(p['name'],'source_'+p['kind']+'_mesh.json')
            expect=expected_raw[p['kind']]
            for field in ('vertices','triangles','polygons','triangle_polygon_indices','polygon_normals_world'):
                if mesh[field]!=expect[field]:raise RuntimeError('Source candidate world mesh changed: '+field)
            for field in ('scale','modifier_count','object_location_mm','object_rotation_euler_radians','matrix_world'):
                if mesh['cad_metadata'][field]!=expect['cad_metadata'][field]:raise RuntimeError('Candidate object pose changed: '+field)
            state['source_raw'][p['kind']]=mesh
            state['source'][p['kind']]=prior['poses'][p['kind']+'_candidate']
        mesh=state['source_raw'][part['kind']]
        return '%s：來源Item物件軸Dimensions %s mm；頂點世界外框 %s mm，bounds %s。旋轉保留、沒有Apply；兩Tools與另一件隱藏。'%(part['name'],mesh['cad_metadata']['object_axis_dimensions_mm'],world_dimensions(mesh),world_bounds(mesh))

    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    for part in PARTS:
        k.file_dialog(56,str(copies)+'\\',copy.name)
        record('07-04',part['kind']+'-source-dialog','File > Open，開啟07-03候選姿態同hash副本，準備分件匯出 '+part['name'],
            lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
        k.confirm_dialog(2)
        k.click_outliner(part['other']);do(lambda:key('H',x=700,y=600),.4)
        k.click_outliner(part['name']);oblique();frame(1)
        record('07-04',part['kind']+'-source-selected','只選 '+part['name']+'，核對物件軸尺寸、世界外框與保留的旋轉',
            lambda p=part:source_read(p),park=PARK,highlights=[B(963,383,228,77,'來源 Item 物件軸尺寸；非世界外框')],
            note='Body來源Item仍約60×44.5×30；Ry90後世界外框約30×44.5×60。數值定義不同，沒有偷偷Apply Rotation。')
        do(lambda:key('NUMPAD_3',x=700,y=600),.4);frame(1)
        record('07-04',part['kind']+'-source-profile','沿世界X觀看 '+part['name']+' 的實際候選姿態剖面',lambda p=part:source_read(p),park=PARK)
        do(lambda:click(40,13),.5);do(lambda:move(73,317),.6);do(lambda:move(288,436),.4)
        record('07-04',part['kind']+'-export-menu','File > Export > STL (.stl)，目前只選 '+part['name'],lambda:k.selection(),
            highlights=[B(28,307,202,20,'Export'),B(236,426,244,20,'STL (.stl)')])
        k.menu_item(288,436,1.2);k.fill_dialog(str(exports)+'\\',part['filename'])
        record('07-04',part['kind']+'-export-before','核對 '+part['filename']+' 路徑／新版本與原生匯出欄位',
            lambda:'資料夾 %s；檔名 %s；原生選項 %s。'%(k.browser()+(options(op_properties(),True),)),win='FILE_BROWSER',park=(300,400))
        def selection_only():
            if not op_properties().export_selected_objects:click(929,159,win='FILE_BROWSER')
        do(selection_only,.6)
        def checked(p=part):
            unchanged();actual=options(op_properties(),True)
            if actual!=EXPORT_OPTIONS or [o.name for o in bpy.context.selected_objects]!=[p['name']]:raise RuntimeError('STL export options or selection changed: '+str(actual))
            folder,name=k.browser();target=(Path(folder)/name).resolve()
            if target.parent!=exports.resolve() or name!=p['filename'] or target.exists():raise RuntimeError('Unsafe or existing STL version target')
            state['export_options'][p['kind']]=actual
            state['export_operator_before_confirm'][p['kind']]=dialog_operator(True)
            return '只匯出%s；Selection Only開、Scale1、Scene Unit關、Binary、Batch關、Y Forward／Z Up。座標按mm解讀，保留原候選world位置。'%p['name']
        record('07-04',part['kind']+'-export-options','勾選並實讀 Selection Only／Scale1／Scene Unit關／Binary，核對新檔目標',checked,
            win='FILE_BROWSER',park=(300,400),highlights=lambda:[B(920,148,135,22,'Selection Only 開'),B(920,170,135,43,'Scale1／Scene Unit關'),k.fb_box('confirm','Export STL')],
            note='STL沒有單位標記；本次保留07-03兩件候選的world擺位，未做切片或支撐資格判定。')
        k.confirm_dialog(1.5)
        def exported(p=part):
            unchanged();path=exports/p['filename'];actual=executed_operator(True,p)
            if actual['options']!=EXPORT_OPTIONS or Path(actual['filepath']).resolve()!=path.resolve():raise RuntimeError('Executed export operator differs')
            st=validate_snapfit_stl(path,p['kind'],prior,state['source_raw'][p['kind']]);mesh=read_stl(path)
            entry=dict(kind=p['kind'],source_object=p['name'],selected_names=[p['name']],stl_path=str(path),stl_sha256=mesh['stl_sha256'],
                stl_bytes=mesh['byte_size'],stl_dimensions_mm=mesh['dimensions_mm'],stl_bounds_mm=mesh['bounds_mm'],stl_triangles=mesh['triangle_count'],
                stl_non_manifold_edges=mesh['non_manifold_edges'],stl_connected_shells=mesh['connected_shells'],stl_genus=mesh['genus'],
                stl_volume_mm3=mesh['volume_mm3'],source_item_dimensions_mm=state['source_raw'][p['kind']]['cad_metadata']['object_axis_dimensions_mm'],
                export_options=state['export_options'][p['kind']],export_operator=actual,stl_verification=st)
            state['exports'].append(entry);write(p['kind']+'-stl-verification.json',st)
            return '%s：實檔%d bytes／%d三角形，世界外框%s mm、最小Z %.9g mm；單殼／Non Manifold0，SHA-256 %s。'%(p['filename'],mesh['byte_size'],mesh['triangle_count'],mesh['dimensions_mm'],mesh['bounds_mm']['min'][2],mesh['stl_sha256'])
        record('07-04',part['kind']+'-stl-checked','按Export STL，解析原生匯出實檔並核對完整world幾何、尺寸與來源',exported,park=PARK,
            note='約1e-6 mm的負Z屬浮點重建；EPS1e-4 mm只作數值核對，不是製造公差。數位檔通過不代表可直接列印或試配合格。')

    do(lambda:click(40,13),.4);do(lambda:move(67,36),.5);k.menu_item(285,35,1.5)
    do(lambda:key('A',x=700,y=600),.3);do(lambda:key('X',x=700,y=600),.4);do(lambda:key('RET'),.8)
    do(lambda:click(1245,374),.5);do(lambda:click(1302,433),.5);do(lambda:click(1418,557),.5);k.menu_item(1397,668,.5)
    k.type_into(1417,488,'0.001');k.open_sidebar()
    def empty():
        unchanged();u=bpy.context.scene.unit_settings
        if bpy.data.objects or u.system!='METRIC' or u.length_unit!='MILLIMETERS' or abs(u.scale_length-.001)>1e-9:raise RuntimeError('Expected new empty mm scene')
        return '獨立新場景物件0；Metric／Millimeters／Unit Scale0.001。空場景沒有Item，不先點分頁。'
    record('07-04','empty-mm-scene','File > New > General，清空並設mm，準備真實重匯入兩份STL',empty,park=PARK)

    def imported(part):
        unchanged();o=active_mesh()
        if o.name!=part['imported'] or not k.view3d().show_region_ui:raise RuntimeError('Wrong imported active object or hidden sidebar')
        if any(abs(a)>1e-7 for a in o.location) or any(abs(a)>1e-7 for a in o.rotation_euler) or list(o.scale)!=[1,1,1] or o.modifiers:
            raise RuntimeError('Reimport must have world-baked vertices, Location0/Rotation0, Scale1 and no modifiers')
        actual=executed_operator(False,part)
        path=exports/part['filename']
        if actual['options']!=IMPORT_OPTIONS or Path(actual['filepath']).resolve()!=path.resolve():raise RuntimeError('Executed import operator differs')
        mesh=raw(part['imported'],'reimport_'+part['kind']+'_mesh.json')
        result=validate_snapfit_export_mesh(mesh['vertices'],mesh['triangles'],part['kind'],prior,state['source_raw'][part['kind']])
        state['reimport_raw'][part['kind']]=mesh;state['reimport'][part['kind']]=result
        entry=next(e for e in state['exports'] if e['kind']==part['kind'])
        entry.update(reimport_object=part['imported'],import_options=state['import_options'][part['kind']],import_operator=actual)
        return '%s實際重匯入：Item Dimensions %s mm＝世界外框%s mm；物件旋轉0／Scale1／修改器0。原world座標在頂點中，物件Location0不代表零件位於原點。'%(part['imported'],mesh['cad_metadata']['object_axis_dimensions_mm'],world_dimensions(mesh))

    def non_manifold(part):
        do(lambda:key('TAB',x=700,y=600),.4);do(lambda:key('TWO',x=700,y=600),.3);do(lambda:key('A',alt=True,x=700,y=600),.3)
        search('Select Non Manifold')
        def read(p=part):
            bm=bmesh.from_edit_mesh(active_mesh().data)
            if not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):raise RuntimeError('Actual imported Non Manifold check failed')
            return p['imported']+'：非空網格，原生Select Non Manifold選到0條邊，程式讀回非流形邊0。'
        record('07-04',part['kind']+'-reimport-non-manifold','Tab > Edge Select > Select None > Select Non Manifold，核對 '+part['imported'],read,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.4)

    for index,part in enumerate(PARTS):
        search('Import STL');k.fill_dialog(str(exports)+'\\',part['filename'])
        def checked_import(p=part):
            actual=options(op_properties(),False)
            if actual!=IMPORT_OPTIONS:raise RuntimeError('Native STL import options changed')
            if k.browser()[1]!=p['filename']:raise RuntimeError('Wrong import version')
            state['import_options'][p['kind']]=actual
            state['import_operator_before_confirm'][p['kind']]=dialog_operator(False)
            return '實際檔名'+p['filename']+'；Scale1、Scene Unit關、Y Forward／Z Up；沒有自動移動或套用縮放。'
        record('07-04',part['kind']+'-import-dialog','F3 > Import STL，選剛匯出的 '+part['filename']+' 並讀回實際選項',checked_import,
            win='FILE_BROWSER',park=(300,400),highlights=lambda:[k.fb_box('name','本次 STL v001'),k.fb_box('confirm','Import STL')])
        k.confirm_dialog(1.5);k.rename_active(part['imported'])
        if index==0:do(lambda:click(1213,102),.5)
        oblique();frame(1)
        record('07-04',part['kind']+'-reimport-dimensions','實際重匯入後'+('才切一次Item；' if index==0 else '')+'核對 '+part['imported']+' 尺寸／世界外框',
            lambda p=part:imported(p),park=PARK,highlights=[B(963,383,228,77,'重匯入 Item 尺寸＝世界外框')])
        do(lambda:key('NUMPAD_3',x=700,y=600),.4);frame(1)
        record('07-04',part['kind']+'-reimport-profile','沿世界X觀看實際STL '+part['imported']+' 剖面',lambda p=part:imported(p),park=PARK)
        non_manifold(part)
        if index==0:do(lambda:key('H',x=700,y=600),.4)

    do(lambda:key('H',alt=True,x=700,y=600),.5)
    k.click_outliner('Lid_STL');k.click_outliner('Body_STL',ctrl=True);oblique();frame(1)
    def layout():
        unchanged()
        if set(bpy.data.objects.keys())!={'Body_STL','Lid_STL'} or any(o.hide_get() for o in bpy.data.objects):raise RuntimeError('Only two visible imported finished parts may exist')
        for p in PARTS:
            mesh=raw(p['imported'],'reimport_'+p['kind']+'_mesh.json')
            state['reimport_raw'][p['kind']]=mesh
            state['reimport'][p['kind']]=validate_snapfit_export_mesh(mesh['vertices'],mesh['triangles'],p['kind'],prior,state['source_raw'][p['kind']])
        state['reimport_layout']=export_layout(state['reimport_raw']['body'],state['reimport_raw']['lid'])
        b,l=(world_bounds(state['reimport_raw'][kind]) for kind in ('body','lid'))
        gap=l['min'][0]-b['max'][0]
        return '兩件實際STL保持07-03分件候選擺位：X投影分隔 %.9g mm，各自最低Z≈0；沒有改成扣合裝配。只含Body_STL／Lid_STL，無Tools，不代表床幅或支撐已核對。'%gap
    record('07-04','reimport-layout','顯示兩件真實重匯入STL，核對世界位置／落床數值與35mm分隔',layout,park=PARK,
        note='目前active是Body_STL，側欄Dimensions約30×44.5×60屬盒體。此擺位沿用方向候選，非最終列印方向與支撐核准。')
    def verified():
        layout()
        stl_raw={}
        for entry in state['exports']:
            kind=entry['kind']
            actual=validate_snapfit_stl(entry['stl_path'],kind,prior,state['source_raw'][kind])
            if actual!=entry['stl_verification']:raise RuntimeError('Exported STL changed after reimport')
            stl_raw[kind]=read_stl(entry['stl_path'])
        stl_layout=export_layout(stl_raw['body'],stl_raw['lid'])
        state['final_objects']=inventory()
        result=dict(passed=True,kind='snapfit_stl_exports',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_orientation_record_path=str(ORIENTATION_RECORD),source_orientation_record_sha256=ORIENTATION_SHA,source_orientation_record_unchanged=True,
            source_body=state['source']['body'],source_lid=state['source']['lid'],source_layout=prior['layout'],source_tools=state['source_tools'],
            source_objects=state['source_objects'],exports=state['exports'],stl_layout=stl_layout,reimport_verified=True,
            reimport_body=state['reimport']['body'],reimport_lid=state['reimport']['lid'],reimport_layout=state['reimport_layout'],final_objects=state['final_objects'],
            exported_stl=True,saved_new_scene=False,geometry_modified=False,rotation_applied_to_mesh=False,source_overhang_comparison_completed=True,
            mesh_analysis_overhang_checked=False,strength_analysis_performed=False,fit_qualification=False,slicer_checked=False,printed=False,fit_tested=False,
            material_grade=None,epsilon_allow=None,Q=None,required_deflection_mm=None,delta_allow_mm=None,forces=None,physical_measurements=None,
            fit_results=None,physical_interference=None,qualified_strength_N=None,qualified_clearance_mm=None,support_required=None,support_generation_performed=False,
            final_print_orientation_approved=None,slicer_support_settings=None,bridge_or_support_qualified=None,
            stl_unit_interpretation='STL is unitless; coordinate values interpreted as millimetres; unchanged 07-03 world candidate poses retained',
            numericComparison=dict(dimensionsAbsMm=1e-4,coordinateWeldMm=1e-5,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing tolerance, printability or printed fit acceptance'))
        export_record=dict(schema_version=1,lesson_step='07-04',stage='digital_stl_export_only',recordedAt=datetime.now(timezone.utc).isoformat(),
            source_scene=dict(path=str(SOURCE),sha256=SOURCE_SHA),source_orientation_record=dict(path=str(ORIENTATION_RECORD),sha256=ORIENTATION_SHA),
            exports=state['exports'],reimport_body=state['reimport']['body'],reimport_lid=state['reimport']['lid'],reimport_layout=state['reimport_layout'],
            saved_new_scene=False,printed=False,fit_tested=False,slicer_checked=False,physical_measurements=None,fit_results=None,qualified_clearance_mm=None,
            qualified_strength_N=None,support_required=None,final_print_orientation_approved=None)
        write('stl-export-record-v001.json',export_record)
        result.update(export_record_path=str(out/'stl-export-record-v001.json'),export_record_sha256=g['sha256'](str(out/'stl-export-record-v001.json')))
        write('verification.json',result)
        return 'Body／Lid兩份v001 STL實檔與實際重匯入核對通過；07-03原scene／副本／record hash未變。保留world候選、兩檔SHA與版本紀錄，不另存blend；切片、支撐、列印、實測、試配與合格值仍留空。'
    record('07-04','exports-verified','保存兩份STL版本、來源與方向記錄關聯、四份raw及最終verification／export record',verified,park=PARK,
        note='本次完成助教數位匯出示範，不代學員確認完成；07-02間隙仍為試驗幾何，STL不是已驗證可直接列印或試配的合格件。')
