"""07-05: actual selection-only STL exports of the three standalone length coupons.

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
from overhang_checks import read_analysis_mesh_data
from stl_checks import read_stl
from coupon_stl_checks import validate_coupon_stl, validate_coupon_export_mesh, validate_export_layout

SOURCE_RUN=PROJECT/'learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001'
SOURCE=SOURCE_RUN/'demo-files/u07_cantilever_length_coupons_v001.blend'
SOURCE_SHA='22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8'
COUPON_RECORD=SOURCE_RUN/'coupon-record-v001.json'
COUPON_SHA='1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d'
PRIOR_SHA='ecea0a82400931113ad34f9c1fe054d6711835558d268973680a029ea656950b'
PLAN=PROJECT/'learning/plans/07-05-coupon-length-draft-v001.json'
PLAN_SHA='35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33'
RAW_HASHES={'A_L19':'5646200083769661833503b5177306fa0d80e0117597dad691b83f97b7b7530c',
            'B_L17':'dc7cb34b232c1853fad6ae67f5de3149a63f0da2bbf7eac595fa062ef4acbcc7',
            'C_L21':'0a40675dd41b0c8d6eb96376295ca0aaa090696b3349360187b3f0e23bcfc8c2'}
ORIGINALS=('Body','Lid','SnapTool','FlangeTool')
PARTS=tuple(dict(kind=n,name=n,others=[other for other in RAW_HASHES if other!=n],imported=n+'_STL',filename='u07_'+n+'_v001.stl') for n in RAW_HASHES)
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
    fixed=((SOURCE,SOURCE_SHA),(COUPON_RECORD,COUPON_SHA),(SOURCE_RUN/'verification.json',PRIOR_SHA),(PLAN,PLAN_SHA),
        (SOURCE_RUN/'source_snap_tool_mesh.json','cb01f749d093467ec90742d38f90243067cdec00eee545c6c81f3f7b20a6aee7'))+tuple(
            (SOURCE_RUN/(name+'_candidate_mesh.json'),digest) for name,digest in RAW_HASHES.items())
    for p,h in fixed:
        if g['sha256'](str(p))!=h:raise RuntimeError('Protected coupon checkpoint changed: '+str(p))
    prior=json.loads((SOURCE_RUN/'verification.json').read_text('utf-8'))
    if prior.get('passed') is not True or prior.get('scene_sha256')!=SOURCE_SHA:
        raise RuntimeError('Coupon geometry source did not pass')
    copy.write_bytes(SOURCE.read_bytes())
    snaps=out/'source-snapshot';snaps.mkdir();files=[]
    dependencies=['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
        'learning/tutor/scenarios/lesson07_coupon_export.py','learning/tutor/scenarios/overhang_checks.py',
        'learning/tutor/scenarios/snapfit_checks.py','learning/tutor/scenarios/tenon_checks.py',
        'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
        'learning/tutor/scenarios/snapfit_stl_checks.py','learning/tutor/scenarios/coupon_checks.py',
        'learning/tutor/scenarios/coupon_stl_checks.py']
    if probe:dependencies.append('learning/tutor/scenarios/lesson07_coupon_export_probe.py')
    for relative in dependencies:
        target=snaps/Path(relative).name;target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    bindings=[]
    for original,name in ((COUPON_RECORD,'source-coupon-record-v001.json'),(PLAN,'coupon-plan-v001.json'),
        (SOURCE_RUN/'verification.json','source-coupon-verification.json'),
        (SOURCE_RUN/'source_snap_tool_mesh.json','source-snap-tool-reference.json'))+tuple(
            (SOURCE_RUN/(n+'_candidate_mesh.json'),'source-'+n+'-candidate-mesh.json') for n in RAW_HASHES):
        target=snaps/name;target.write_bytes(original.read_bytes())
        bindings.append(dict(source=original.relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+name,
                             sha256=g['sha256'](str(target))))
    write_manifest=dict(recordedAt=datetime.now(timezone.utc).isoformat(),files=files,dataBindings=bindings,
        sourceScene=str(SOURCE),sourceCopy=str(copy),sourceSha256=SOURCE_SHA)
    (snaps/'manifest.json').write_text(json.dumps(write_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    expected_raw={p['kind']:json.loads((snaps/('source-'+p['kind']+'-candidate-mesh.json')).read_text('utf-8')) for p in PARTS}
    source_snap_raw=json.loads((snaps/'source-snap-tool-reference.json').read_text('utf-8'))
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

    def inventory():
        result={}
        for o in bpy.data.objects:
            shape=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
            result[o.name]=dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),location_mm=list(o.location),
                rotation_euler_radians=list(o.rotation_euler),object_axis_dimensions_mm=list(o.dimensions),modifier_count=len(o.modifiers),
                matrix_world=[list(row) for row in o.matrix_world],mesh_data_name=o.data.name,data_name=o.data.name,
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
        if k.area('OUTLINER').height<250:raise RuntimeError('Source Outliner must show all seven object rows')
        if Path(bpy.data.filepath).resolve()!=copy.resolve():raise RuntimeError('Wrong source copy opened')
        if set(bpy.data.objects.keys())!=set(ORIGINALS+tuple(RAW_HASHES)):raise RuntimeError('Unexpected source objects')
        if active_mesh().name!=part['name'] or [o.name for o in bpy.context.selected_objects]!=[part['name']]:
            raise RuntimeError('Exactly the intended coupon must be selected')
        if any(not bpy.data.objects[n].hide_get() for n in ORIGINALS+tuple(part['others'])):
            raise RuntimeError('Four original objects and other coupons must stay hidden')
        current=inventory()
        for name,metadata in current.items():
            expected=prior['final_objects'][name]
            for field in ('type','scale','modifier_count','matrix_world','local_mesh_sha256','mesh_data_name'):
                if metadata[field]!=expected[field]:raise RuntimeError('Protected seven-object source geometry/transform/datablock changed: '+name+'/'+field)
        state['source_objects']=current
        for p in PARTS:
            mesh=raw(p['name'],'source_'+p['kind']+'_mesh.json');expect=expected_raw[p['kind']]
            for field in ('vertices','triangles','polygons','triangle_polygon_indices','polygon_normals_world'):
                if mesh[field]!=expect[field]:raise RuntimeError('Source candidate world mesh changed: '+field)
            for field in ('scale','modifier_count','object_location_mm','object_rotation_euler_radians','matrix_world'):
                if mesh['cad_metadata'][field]!=expect['cad_metadata'][field]:raise RuntimeError('Source candidate object pose changed: '+field)
            state['source_raw'][p['kind']]=mesh;state['source'][p['kind']]=prior['candidates'][p['kind']]
        mesh=state['source_raw'][part['kind']]
        return '%s：來源Item物件軸Dimensions %s mm；world外框%s mm、Ry90保留。只選本件，另兩件與四原件hidden；七物件local mesh／matrix／data name均與幾何版一致。'%(part['name'],mesh['cad_metadata']['object_axis_dimensions_mm'],world_dimensions(mesh))

    def ensure_outliner():
        area=k.area('OUTLINER')
        if area.height<270:
            divider=k.window().height-area.y
            k.drag_slow([(1305,divider),(1305,divider+100)],button='LEFTMOUSE')

    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    for part in PARTS:
        k.file_dialog(56,str(copies)+'\\',copy.name)
        record('07-05',part['kind']+'-source-dialog','File > Open，開啟07-05三試片候選姿態同hash副本，準備分件匯出 '+part['name'],
            lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
        k.confirm_dialog(2)
        do(ensure_outliner,.2)
        for other in part['others']:
            k.click_outliner(other);do(lambda:key('H',x=700,y=600),.4)
        k.click_outliner(part['name']);oblique();frame(1)
        record('07-05',part['kind']+'-source-selected','只選 '+part['name']+'，核對物件軸尺寸、世界外框與保留的旋轉',
            lambda p=part:source_read(p),park=PARK,highlights=[B(963,383,228,77,'來源 Item 物件軸尺寸；非世界外框')],
            note='來源Item為9×4.6×24／22／26；Ry90後world為24／22／26×4.6×9。幾何L19／17／21另由根平面至承接面讀回。')
        do(lambda:key('NUMPAD_1',x=700,y=600),.4);frame(1)
        record('07-05',part['kind']+'-source-profile','由世界−Y正視 '+part['name']+' 的實際候選臂長輪廓與外框',lambda p=part:source_read(p),park=PARK)
        do(lambda:click(40,13),.5);do(lambda:move(73,317),.6);do(lambda:move(288,436),.4)
        record('07-05',part['kind']+'-export-menu','File > Export > STL (.stl)，目前只選 '+part['name'],lambda:k.selection(),
            highlights=[B(28,307,202,20,'Export'),B(236,426,244,20,'STL (.stl)')])
        k.menu_item(288,436,1.2);k.fill_dialog(str(exports)+'\\',part['filename'])
        record('07-05',part['kind']+'-export-before','核對 '+part['filename']+' 路徑／新版本與原生匯出欄位',
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
            return '只匯出%s；Selection Only開、Scale1、Scene Unit關、Binary、Batch關、Y Forward／Z Up。座標按mm解讀，保留原試片候選world位置。'%p['name']
        record('07-05',part['kind']+'-export-options','勾選並實讀 Selection Only／Scale1／Scene Unit關／Binary，核對新檔目標',checked,
            win='FILE_BROWSER',park=(300,400),highlights=lambda:[B(920,148,135,22,'Selection Only 開'),B(920,170,135,43,'Scale1／Scene Unit關'),k.fb_box('confirm','Export STL')],
            note='STL沒有單位標記；本次保留07-05三件候選的world擺位，未做切片或支撐資格判定。')
        k.confirm_dialog(1.5)
        def exported(p=part):
            unchanged();path=exports/p['filename'];actual=executed_operator(True,p)
            if actual['options']!=EXPORT_OPTIONS or Path(actual['filepath']).resolve()!=path.resolve():raise RuntimeError('Executed export operator differs')
            st=validate_coupon_stl(path,p['kind'],prior,state['source_raw'][p['kind']],source_snap_raw);mesh=read_stl(path)
            entry=dict(kind=p['kind'],variant=p['kind'],source_object=p['name'],selected_names=[p['name']],stl_path=str(path),stl_sha256=mesh['stl_sha256'],
                stl_bytes=mesh['byte_size'],stl_dimensions_mm=mesh['dimensions_mm'],stl_bounds_mm=mesh['bounds_mm'],stl_triangles=mesh['triangle_count'],
                stl_non_manifold_edges=mesh['non_manifold_edges'],stl_connected_shells=mesh['connected_shells'],stl_genus=mesh['genus'],
                stl_volume_mm3=mesh['volume_mm3'],source_item_dimensions_mm=state['source_raw'][p['kind']]['cad_metadata']['object_axis_dimensions_mm'],
                export_options=state['export_options'][p['kind']],export_operator=actual,stl_verification=st)
            state['exports'].append(entry);write(p['kind']+'-stl-verification.json',st)
            return '%s：實檔%d bytes／%d三角形，世界外框%s mm、最小Z %.9g mm；單殼／Non Manifold0，SHA-256 %s。'%(p['filename'],mesh['byte_size'],mesh['triangle_count'],mesh['dimensions_mm'],mesh['bounds_mm']['min'][2],mesh['stl_sha256'])
        record('07-05',part['kind']+'-stl-checked','按Export STL，解析原生匯出實檔並核對完整world幾何、尺寸與來源',exported,park=PARK,
            note='約1e-6 mm的負Z屬浮點重建；EPS1e-4 mm只作數值核對，不是製造公差。數位檔通過不代表可直接列印或試配合格。')

    do(lambda:click(40,13),.4);do(lambda:move(67,36),.5);k.menu_item(285,35,1.5)
    do(lambda:key('A',x=700,y=600),.3);do(lambda:key('X',x=700,y=600),.4);do(lambda:key('RET'),.8)
    do(lambda:click(1245,k.props_y(167)),.5);do(lambda:click(1302,k.props_y(226)),.5);do(lambda:click(1418,k.props_y(350)),.5);do(lambda:move(1397,k.props_y(461)),.3);do(lambda:click(1397,k.props_y(461)),.5)
    do(lambda:click(1417,k.props_y(281)),.4);do(lambda:key('A',ctrl=True),.2);do(lambda:k.type_text('0.001'),.3);do(lambda:key('RET'),.5);k.open_sidebar()
    def empty():
        unchanged();u=bpy.context.scene.unit_settings
        if bpy.data.objects or u.system!='METRIC' or u.length_unit!='MILLIMETERS' or abs(u.scale_length-.001)>1e-9:raise RuntimeError('Expected new empty mm scene')
        return '獨立新場景物件0；Metric／Millimeters／Unit Scale0.001。空場景沒有Item，不先點分頁。'
    record('07-05','empty-mm-scene','File > New > General，清空並設mm，準備真實重匯入三份STL',empty,park=PARK)

    def imported(part):
        unchanged();o=active_mesh()
        if o.name!=part['imported'] or not k.view3d().show_region_ui:raise RuntimeError('Wrong imported active object or hidden sidebar')
        if any(abs(a)>1e-7 for a in o.location) or any(abs(a)>1e-7 for a in o.rotation_euler) or list(o.scale)!=[1,1,1] or o.modifiers:
            raise RuntimeError('Reimport must have world-baked vertices, Location0/Rotation0, Scale1 and no modifiers')
        actual=executed_operator(False,part)
        path=exports/part['filename']
        if actual['options']!=IMPORT_OPTIONS or Path(actual['filepath']).resolve()!=path.resolve():raise RuntimeError('Executed import operator differs')
        mesh=raw(part['imported'],'reimport_'+part['kind']+'_mesh.json')
        result=validate_coupon_export_mesh(mesh['vertices'],mesh['triangles'],part['kind'],prior,state['source_raw'][part['kind']],source_snap_raw)
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
        record('07-05',part['kind']+'-reimport-non-manifold','Tab > Edge Select > Select None > Select Non Manifold，核對 '+part['imported'],read,park=PARK)
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
        record('07-05',part['kind']+'-import-dialog','F3 > Import STL，選剛匯出的 '+part['filename']+' 並讀回實際選項',checked_import,
            win='FILE_BROWSER',park=(300,400),highlights=lambda:[k.fb_box('name','本次 STL v001'),k.fb_box('confirm','Import STL')])
        k.confirm_dialog(1.5);k.rename_active(part['imported'])
        if index==0:do(lambda:click(1213,102),.5)
        oblique();frame(1)
        record('07-05',part['kind']+'-reimport-dimensions','實際重匯入後'+('才切一次Item；' if index==0 else '')+'核對 '+part['imported']+' 尺寸／世界外框',
            lambda p=part:imported(p),park=PARK,highlights=[B(963,383,228,77,'重匯入 Item 尺寸＝世界外框')])
        do(lambda:key('NUMPAD_1',x=700,y=600),.4);frame(1)
        record('07-05',part['kind']+'-reimport-profile','由世界−Y正視實際STL '+part['imported']+' 的臂長輪廓',lambda p=part:imported(p),park=PARK)
        non_manifold(part)
        if index<len(PARTS)-1:do(lambda:key('H',x=700,y=600),.4)

    do(lambda:key('H',alt=True,x=700,y=600),.5)
    for index,part in enumerate(PARTS):k.click_outliner(part['imported'],ctrl=index>0)
    oblique();frame(1)
    def layout():
        unchanged()
        expected={p['imported'] for p in PARTS}
        if set(bpy.data.objects.keys())!=expected or any(o.hide_get() for o in bpy.data.objects):raise RuntimeError('Final scene must contain exactly three visible imported coupons')
        for p in PARTS:
            mesh=raw(p['imported'],'reimport_'+p['kind']+'_mesh.json');o=bpy.data.objects[p['imported']]
            if any(abs(a)>1e-7 for a in o.location) or any(abs(a)>1e-7 for a in o.rotation_euler) or list(o.scale)!=[1,1,1] or o.modifiers:
                raise RuntimeError('Actual imported coupons must retain native Location0/Rotation0/Scale1/no modifiers')
            state['reimport_raw'][p['kind']]=mesh
            state['reimport'][p['kind']]=validate_coupon_export_mesh(mesh['vertices'],mesh['triangles'],p['kind'],prior,state['source_raw'][p['kind']],source_snap_raw)
        state['reimport_layout']=validate_export_layout(state['reimport'],prior)
        return '三個實際STL保留07-05獨立候選world位置與Y列距12mm／外框間距約7.4mm。接床僅anchor側面；beam與根部仍離床，支撐待定。只有A_L19_STL／B_L17_STL／C_L21_STL，無來源工具或完整盒體。'
    record('07-05','reimport-layout','顯示三件真實重新匯入STL，核對世界位置／數值Z0與原幾何L對照',layout,park=PARK,
        note='active為C_L21_STL，Item尺寸26×4.6×9屬C的world外框；新場景三件R0，來源Ry90仍未Apply。未切片、列印或驗證改善。')
    def verified():
        layout();stl_results={}
        for entry in state['exports']:
            kind=entry['kind'];actual=validate_coupon_stl(entry['stl_path'],kind,prior,state['source_raw'][kind],source_snap_raw)
            if actual!=entry['stl_verification']:raise RuntimeError('STL changed after actual UI reimport')
            stl_results[kind]=actual
        stl_layout=validate_export_layout(stl_results,prior)
        record_path=out/'coupon-stl-export-record-v001.json'
        export_record=dict(schema_version=1,lesson_step='07-05',stage='standalone_coupon_digital_stl_export_only',recordedAt=datetime.now(timezone.utc).isoformat(),
            source_scene=dict(path=str(SOURCE),sha256=SOURCE_SHA),source_coupon_record=dict(path=str(COUPON_RECORD),sha256=COUPON_SHA),
            draft_plan=dict(path=str(PLAN),sha256=PLAN_SHA),exports=state['exports'],reimport=state['reimport'],reimport_layout=state['reimport_layout'],
            saved_new_scene=False,geometry_modified=False,full_box_modified=False,exported_stl=True,printed=False,fit_tested=False,slicer_checked=False,
            geometry_scope='No new specimen design or source shape edit; actual STL reimport creates three new mesh datablocks from the retained world vertices.',
            reimport_mesh_datablocks_created=True,new_specimen_design_created=False,
            material_grade=None,epsilon_allow=None,effective_mechanical_length_mm=None,improvement_validated=None,physical_measurements=None,fit_results=None,
            qualified_clearance_mm=None,qualified_strength_N=None,support_required=None,final_print_orientation_approved=None)
        write(record_path.name,export_record)
        result=dict(passed=True,kind='cantilever_coupon_stl_exports',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_coupon_record_path=str(COUPON_RECORD),source_coupon_record_sha256=COUPON_SHA,source_coupon_record_unchanged=True,
            draft_plan_path=str(PLAN),draft_plan_sha256=PLAN_SHA,source_candidates=state['source'],source_layout=prior['layout'],source_objects=state['source_objects'],
            exports=state['exports'],stl_layout=stl_layout,reimport_verified=True,reimport=state['reimport'],reimport_layout=state['reimport_layout'],final_objects=inventory(),
            export_record_path=str(record_path),export_record_sha256=g['sha256'](str(record_path)),exported_stl=True,saved_new_scene=False,geometry_modified=False,
            source_geometry_modified=False,new_geometry_created=False,full_box_modified=False,rotation_applied_to_mesh=False,mesh_analysis_overhang_checked=False,
            geometry_scope='new_geometry_created=false refers to no new specimen design; native STL reimport creates three new mesh datablocks with the unchanged source world geometry.',
            reimport_mesh_datablocks_created=True,new_specimen_design_created=False,
            improvement_assessed=False,strength_analysis_performed=False,deformation_analysis_performed=False,fit_qualification=False,slicer_checked=False,printed=False,fit_tested=False,
            material_grade=None,epsilon_allow=None,Q=None,effective_mechanical_length_mm=None,full_box_boundary_equivalence=None,anchor_clamping_or_fixture=None,
            required_deflection_mm=None,delta_allow_mm=None,forces=None,physical_measurements=None,fit_results=None,physical_interference=None,qualified_strength_N=None,
            qualified_clearance_mm=None,improvement_validated=None,support_required=None,support_generation_performed=False,final_print_orientation_approved=None,
            slicer_support_settings=None,bridge_or_support_qualified=None,
            stl_unit_interpretation='STL is unitless; numeric coordinates interpreted as millimetres; original 07-05 standalone candidate world vertices retained',
            numericComparison=dict(dimensionsAbsMm=1e-4,coordinateWeldMm=1e-5,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing, mechanical L, improvement, support, printability or fit acceptance'))
        write('verification.json',result)
        return '三份coupon v001 STL實檔與真實UI重匯入皆核對；七原物件local mesh／matrix未改，來源／副本／plan／舊record hash維持。未重建或修改試片形狀；真重匯入建立三個新mesh資料，不另存blend。材料、支撐、有效力學L、改善、列印與試配仍未驗證。'
    record('07-05','coupon-exports-verified','保存三份STL版本／來源關聯、六份raw與最終verification及coupon STL export record',verified,park=PARK,
        note='追加本步數位匯出，不覆寫原07-05幾何版或舊STL；A/B/C仍為助教草案，沒有實體合格或改善判定，不代學員confirm。')
