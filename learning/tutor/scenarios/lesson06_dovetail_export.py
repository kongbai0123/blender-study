"""06-03: two selection-only STL exports and actual UI reimports; no physical fit claims."""
import json
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from tenon_checks import read_mesh_data
from dovetail_checks import validate_body_mesh, validate_lid_mesh, validate_assembly
from dovetail_stl_checks import validate_dovetail_stl

SOURCE_RUN = PROJECT/'learning/evidence/06/2026-10-25-lesson06-dovetail-demo-v002'
SOURCE = SOURCE_RUN/'demo-files/u06_dovetail_slide_v001.blend'
SOURCE_SHA = 'b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e'
PARTS = (dict(kind='body',name='Body',imported='Body_STL',other='SlidingLid',filename='u06_dovetail_body_v001.stl'),
         dict(kind='lid',name='SlidingLid',imported='SlidingLid_STL',other='Body',filename='u06_dovetail_lid_v001.stl'))


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    out = Path(g['OUT'])
    copies, exports = Path(k.demo_dir)/'sources',Path(k.demo_dir)/'exports'
    copies.mkdir()
    exports.mkdir()
    source_copy = copies/SOURCE.name
    prior = json.loads((SOURCE_RUN/'verification.json').read_text('utf-8'))
    if g['sha256'](str(SOURCE)) != SOURCE_SHA or not prior.get('passed') or prior.get('scene_sha256') != SOURCE_SHA:
        raise RuntimeError('Verified 06-02 scene checkpoint changed')
    source_copy.write_bytes(SOURCE.read_bytes())
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    manifest = []
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson06_dovetail_export.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/tenon_checks.py',
                     'learning/tutor/scenarios/dovetail_checks.py','learning/tutor/scenarios/stl_checks.py',
                     'learning/tutor/scenarios/dovetail_stl_checks.py'):
        target = snapshots/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        manifest.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=manifest,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state = dict(exports=[],export_options={},import_options={},reimport={})

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        if any(g['sha256'](str(p)) != SOURCE_SHA for p in (SOURCE,source_copy)):
            raise RuntimeError('Source or opened scene copy changed')

    def active_mesh():
        o = bpy.context.view_layer.objects.active
        if not o or o.type != 'MESH':
            raise RuntimeError('Expected active mesh')
        return o

    def mesh_read(name,kind,filename):
        raw = read_mesh_data(bpy.data.objects[name])
        write(filename,raw)
        cad = raw['cad_metadata']
        if cad['scale'] != [1,1,1] or cad['modifier_count'] or cad['length_unit'] != 'MILLIMETERS' or abs(cad['unit_scale']-.001)>1e-9:
            raise RuntimeError('Mesh CAD metadata differs from applied millimetre scene')
        result = (validate_body_mesh if kind=='body' else validate_lid_mesh)(raw['vertices'],raw['triangles'])
        return result

    def frame(notches=1):
        do(lambda:click(184,38),.35)
        k.menu_item(236,168,.6)
        k.wheel_out(notches)

    def oblique(bottom=False):
        do(lambda:key('NUMPAD_7',ctrl=bottom,x=700,y=600),.4)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def search(text):
        do(lambda:key('F3',x=700,y=600),.3)
        do(lambda:k.type_text(text),.3)
        do(lambda:key('RET'),1)

    def operator_properties():
        return k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator.properties

    def export_options():
        p = operator_properties()
        return dict(only_selected=bool(p.export_selected_objects),global_scale=float(p.global_scale),
                    use_scene_unit=bool(p.use_scene_unit),apply_modifiers=bool(p.apply_modifiers),
                    forward_axis=p.forward_axis,up_axis=p.up_axis,ascii_format=bool(p.ascii_format),
                    use_batch=bool(p.use_batch),evaluation_mode=p.evaluation_mode)

    def source_read(part):
        unchanged()
        if Path(bpy.data.filepath).resolve() != source_copy.resolve():
            raise RuntimeError('Wrong source copy opened')
        expected = {'Body','SlidingLid','GuideTool','GrooveTool','MaleTool'}
        if set(bpy.data.objects.keys()) != expected:
            raise RuntimeError('Source object inventory differs')
        if active_mesh().name != part['name'] or [o.name for o in bpy.context.selected_objects] != [part['name']]:
            raise RuntimeError('Exactly the intended export object must be selected')
        if any(not bpy.data.objects[n].hide_get() for n in ('GuideTool','GrooveTool','MaleTool',part['other'])):
            raise RuntimeError('Construction tools and the other part must be hidden')
        state['source_body'] = mesh_read('Body','body','source_body_mesh.json')
        state['source_lid'] = mesh_read('SlidingLid','lid','source_lid_mesh.json')
        for role in ('body','lid'):
            if state['source_'+role] != prior[role]:
                raise RuntimeError('Source mesh readback differs from fixed 06-02 checkpoint: '+role)
        state['source_assembly'] = validate_assembly(state['source_body'],state['source_lid'])
        write('source-geometry-verification.json',dict(passed=True,body=state['source_body'],lid=state['source_lid'],assembly=state['source_assembly']))
        measured = state['source_'+part['kind']]
        details = '槽深3.2／槽口2.32 mm' if part['kind']=='body' else '板厚2／外露榫深3.2 mm'
        return '只選%s；實際Dimensions %s mm、%s、單殼／Non Manifold 0。三個建構工具與另一件隱藏；來源及副本hash未變。'%(part['name'],measured['dimensions_mm'],details)

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    for part in PARTS:
        # Reopening the immutable copy resets temporary visibility without Alt+H exposing tools.
        k.file_dialog(56,str(copies)+'\\',source_copy.name)
        record('06-03',part['kind']+'-source-dialog','File > Open，開啟06-02同hash副本，準備只匯出 '+part['name'],
               lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
        k.confirm_dialog(2)
        k.click_outliner(part['other'])
        do(lambda:key('H',x=700,y=600),.4)
        k.click_outliner(part['name'])
        oblique(bottom=part['kind']=='lid')
        frame(1)
        record('06-03',part['kind']+'-source-selected','只選 '+part['name']+'，核對來源、尺寸與隱藏工具',
               lambda p=part:source_read(p),park=PARK,highlights=[B(963,383,228,77,'本次單件來源 Dimensions')])
        do(lambda:key('NUMPAD_3',x=700,y=600),.4)
        frame(1)
        record('06-03',part['kind']+'-source-end-profile','沿X看 '+part['name']+' 真實端面，核對燕尾槽／榫與整體尺寸',
               lambda p=part:source_read(p),park=PARK)
        do(lambda:click(40,13),.5)
        do(lambda:move(73,317),.6)
        do(lambda:move(288,436),.4)
        record('06-03',part['kind']+'-export-menu','File > Export，指到 STL (.stl)，目前只選 '+part['name'],
               lambda:k.selection(),highlights=[B(28,307,202,20,'Export'),B(236,426,244,20,'STL (.stl)')])
        k.menu_item(288,436,1.2)
        k.fill_dialog(str(exports)+'\\',part['filename'])
        record('06-03',part['kind']+'-export-before','核對 '+part['filename']+' 路徑、檔名與目前匯出選項',
               lambda:'資料夾 %s；檔名 %s；選項 %s。'%(k.browser()+(export_options(),)),win='FILE_BROWSER',park=(300,400))
        def selection_only():
            if not operator_properties().export_selected_objects:
                click(929,159,win='FILE_BROWSER')
        do(selection_only,.6)
        def checked_options(p=part):
            unchanged()
            options = export_options()
            expected = dict(only_selected=True,global_scale=1.0,use_scene_unit=False,apply_modifiers=True,
                            forward_axis='Y',up_axis='Z',ascii_format=False,use_batch=False,evaluation_mode='DAG_EVAL_RENDER')
            if options != expected or [o.name for o in bpy.context.selected_objects] != [p['name']]:
                raise RuntimeError('Export options/selection differ: '+str(options))
            folder,name = k.browser()
            target = (Path(folder)/name).resolve()
            if target.parent != exports.resolve() or name != p['filename'] or target.exists():
                raise RuntimeError('Unsafe or existing STL output version')
            state['export_options'][p['kind']] = options
            return '只匯出 '+p['name']+'；Selection Only開、Scale1、Scene Unit關、Apply Modifiers開、Binary、Batch關、Y Forward／Z Up。'
        record('06-03',part['kind']+'-export-options','勾選並核對 Selection Only、Scale1、Scene Unit關，再驗證新檔目標',
               checked_options,win='FILE_BROWSER',park=(300,400),
               highlights=lambda:[B(920,148,135,22,'Selection Only 開'),B(920,170,135,43,'Scale 1 / Scene Unit 關'),k.fb_box('confirm','Export STL')],
               note='STL沒有單位標記，本次座標按毫米解讀。保留來源world座標，尚未落床或核對切片擺放。')
        k.confirm_dialog(1.5)
        def exported(p=part):
            unchanged()
            path = exports/p['filename']
            st = validate_dovetail_stl(path,p['kind'],prior)
            entry = dict(kind=p['kind'],source_object=p['name'],selected_names=[p['name']],stl_path=str(path),
                stl_sha256=st['stl_sha256'],stl_bytes=st['byte_size'],stl_dimensions_mm=st['dimensions_mm'],
                stl_triangles=st['triangle_count'],stl_non_manifold_edges=st['non_manifold_edges'],
                stl_connected_shells=st['connected_shells'],stl_genus=st['genus'],stl_volume_mm3=st['volume_mm3'],
                export_options=state['export_options'][p['kind']],stl_verification=st)
            state['exports'].append(entry)
            write(p['kind']+'-stl-verification.json',st)
            return '%s：%d bytes、%d三角形，實檔Dimensions %s（mm解讀）；燕尾剖面／端面／體積與來源一致，單殼、Non Manifold0；SHA-256 %s。'%(p['filename'],st['byte_size'],st['triangle_count'],st['dimensions_mm'],st['stl_sha256'])
        record('06-03',part['kind']+'-stl-checked','按 Export STL，直接解析實檔三角面、燕尾剖面與尺寸，再對照固定來源',
               exported,park=PARK,note='這是數位檔案核對，不代表列印尺寸或實體試配合格。')

    # A fresh empty millimetre scene. Item does not exist until the first mesh is imported.
    do(lambda:click(40,13),.4)
    do(lambda:move(67,36),.5)
    k.menu_item(285,35,1.5)
    do(lambda:key('A',x=700,y=600),.3)
    do(lambda:key('X',x=700,y=600),.4)
    do(lambda:key('RET'),.8)
    do(lambda:click(1245,374),.5)
    do(lambda:click(1302,433),.5)
    do(lambda:click(1418,557),.5)
    k.menu_item(1397,668,.5)
    k.type_into(1417,488,'0.001')
    k.open_sidebar()
    def empty_read():
        unchanged()
        u = bpy.context.scene.unit_settings
        if bpy.data.objects or u.system != 'METRIC' or u.length_unit != 'MILLIMETERS' or abs(u.scale_length-.001)>1e-9:
            raise RuntimeError('Expected empty millimetre scene')
        return '場景物件0；Metric／Millimeters／Unit Scale0.001；尚無Item分頁，不在空場景點它。'
    record('06-03','empty-mm-scene','File > New > General，清空獨立場景並設Metric／mm／0.001，準備讀回兩STL',empty_read,park=PARK)

    def imported_read(part):
        unchanged()
        name,kind = part['imported'],part['kind']
        if active_mesh().name != name or not k.view3d().show_region_ui:
            raise RuntimeError('Wrong active imported object or hidden Item Sidebar')
        geo = mesh_read(name,kind,'reimport_'+kind+'_mesh.json')
        entry = next(e for e in state['exports'] if e['kind']==kind)
        # Source, binary STL and actual imported meshes each undergo full profile validation.
        if abs(geo['volume_mm3']-entry['stl_volume_mm3'])>max(1e-4,entry['stl_volume_mm3']*1e-5):
            raise RuntimeError('Actual reimport/STL volume mismatch')
        state['reimport'][kind] = geo
        entry.update(reimport_object=name,import_options=state['import_options'][kind])
        return '實際重新匯入%s，Item Dimensions %s mm、Scale1／修改器0；燕尾剖面、體積、單殼／Non Manifold0與來源及STL一致。'%(name,geo['dimensions_mm'])

    def non_manifold(part):
        do(lambda:key('TAB',x=700,y=600),.4)
        do(lambda:key('TWO',x=700,y=600),.3)
        do(lambda:key('A',alt=True,x=700,y=600),.3)
        search('Select Non Manifold')
        def read(p=part):
            bm = bmesh.from_edit_mesh(active_mesh().data)
            if not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):
                raise RuntimeError('Actual STL reimport Non Manifold UI check failed')
            return p['imported']+'：非空網格，Select Non Manifold選到0條邊，程式讀回非流形邊0。'
        record('06-03',part['kind']+'-reimport-non-manifold','Tab > 邊選取 > Select None > Select Non Manifold，核對 '+part['imported'],read,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.4)

    for index,part in enumerate(PARTS):
        search('Import STL')
        k.fill_dialog(str(exports)+'\\',part['filename'])
        def import_options(p=part):
            op = operator_properties()
            actual = dict(global_scale=float(op.global_scale),use_scene_unit=bool(op.use_scene_unit),forward_axis=op.forward_axis,up_axis=op.up_axis)
            if actual != dict(global_scale=1.0,use_scene_unit=False,forward_axis='Y',up_axis='Z'):
                raise RuntimeError('Import options differ')
            state['import_options'][p['kind']] = actual
            return '實際檔名 '+k.browser()[1]+'；Scale1、Scene Unit關、Y Forward／Z Up。'
        record('06-03',part['kind']+'-import-dialog','F3搜尋 Import STL，選本次實際 '+part['filename']+' 並讀回匯入選項',
               import_options,win='FILE_BROWSER',park=(300,400),highlights=lambda:[k.fb_box('name','剛匯出的 STL v001'),k.fb_box('confirm','Import STL')])
        k.confirm_dialog(1.5)
        k.rename_active(part['imported'])
        if index == 0:
            do(lambda:click(1213,102),.5)
        oblique(bottom=part['kind']=='lid')
        frame(1)
        record('06-03',part['kind']+'-reimport-dimensions','實際匯入後'+('才切Item，' if index==0 else '')+'Frame Selected，核對 '+part['imported']+' Dimensions',
               lambda p=part:imported_read(p),park=PARK,highlights=[B(963,383,228,77,'STL 重新匯入的 Dimensions')],
               note='來源world座標已烘入STL頂點；匯入物件原點為0，不能把Location當作零件world外框。')
        do(lambda:key('NUMPAD_3',x=700,y=600),.4)
        frame(1)
        record('06-03',part['kind']+'-reimport-end-profile','沿X看實際重新匯入 '+part['imported']+' 的燕尾端面',
               lambda p=part:imported_read(p),park=PARK)
        non_manifold(part)
        if index==0:
            do(lambda:key('H',x=700,y=600),.4)

    # Only the two imported finished parts exist here; unhiding cannot expose construction tools.
    do(lambda:key('H',alt=True,x=700,y=600),.5)
    k.click_outliner('SlidingLid_STL')
    k.click_outliner('Body_STL',ctrl=True)
    oblique()
    frame(1)
    def assembly_read():
        unchanged()
        if set(bpy.data.objects.keys()) != {'Body_STL','SlidingLid_STL'} or any(o.hide_get() for o in bpy.data.objects):
            raise RuntimeError('Final imported assembly must contain exactly two visible finished parts')
        state['reimport_body'] = mesh_read('Body_STL','body','reimport_body_mesh.json')
        state['reimport_lid'] = mesh_read('SlidingLid_STL','lid','reimport_lid_mesh.json')
        state['reimport_assembly'] = validate_assembly(state['reimport_body'],state['reimport_lid'])
        a = state['reimport_assembly']
        return '兩個實際STL在來源world位置組合；最小水平單邊%.9f mm、斜面法向%.9f mm、板底／盒頂%.9f mm。名義水平總差0.4仍為試驗，未列印試配。'%(a['horizontal_side_gap_mm'],a['normal_side_gap_mm'],a['plate_rim_gap_mm'])
    record('06-03','reimport-assembly','顯示兩件實際重新匯入的STL，核對燕尾剖面間距及原world擺位',assembly_read,park=PARK,
           note='圖中active為Body_STL，Item Dimensions屬盒體。STL仍保留Body Z−15～15、SlidingLid Z12～17.2，尚未落床或核對列印方向。')
    def verified():
        assembly_read()
        for entry in state['exports']:
            actual = validate_dovetail_stl(entry['stl_path'],entry['kind'],prior)
            if actual != entry['stl_verification']:
                raise RuntimeError('STL changed after actual reimport')
        by_kind = {e['kind']:e['stl_verification']['geometry_readback'] for e in state['exports']}
        result = dict(passed=True,kind='dovetail_stl_exports',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_body=state['source_body'],source_lid=state['source_lid'],source_assembly=state['source_assembly'],exports=state['exports'],
            stl_assembly=validate_assembly(by_kind['body'],by_kind['lid']),reimport_verified=True,
            reimport_body=state['reimport_body'],reimport_lid=state['reimport_lid'],reimport_assembly=state['reimport_assembly'],
            trial=prior['trial'],exported_stl=True,saved_new_scene=False,mesh_analysis_overhang_checked=False,slicer_checked=False,
            printed=False,fit_tested=False,physical_measurements=None,fit_results=None,physical_interference=None,qualified_clearance_mm=None,
            stl_unit_interpretation='STL is unitless; exported coordinate values interpreted as millimetres; original world coordinates retained',
            numericComparison=dict(dimensionsAbsMm=1e-4,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing tolerance or physical fit acceptance'))
        write('verification.json',result)
        return 'Body與SlidingLid兩份STL實檔及實際重新匯入皆通過；來源與副本hash未變。已記兩檔版本、SHA-256及來源關聯，不另存新blend；切片、列印、實測、試配與合格間隙留空。'
    record('06-03','exports-verified','保存兩份STL版本、來源關聯、四份world mesh及最終 verification.json',verified,park=PARK,
           note='本次只完成06-03燕尾滑蓋與盒體的STL匯出及數位核對，沒有完成定位榫匯出或實體階段，不代學員確認完成。')
