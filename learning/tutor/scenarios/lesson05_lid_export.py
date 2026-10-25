"""05-06 isolated UI-only lid STL export and actual reimport; no physical fit claims."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from lid_checks import read_body_and_validate, read_lid_and_validate
from lid_stl_checks import validate_lid_stl

SOURCE_RUN = PROJECT / 'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001'
SOURCE = SOURCE_RUN / 'demo-files/u05_lid_v001.blend'
SOURCE_SHA = 'ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
STL_NAME = 'u05_lid_v001.stl'


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    out = Path(g['OUT'])
    copies = Path(k.demo_dir) / 'sources'
    exports = Path(k.demo_dir) / 'exports'
    copies.mkdir()
    exports.mkdir()
    source_copy = copies / SOURCE.name
    if g['sha256'](str(SOURCE)) != SOURCE_SHA:
        raise RuntimeError('Verified lid source checkpoint changed')
    prior = json.loads((SOURCE_RUN/'verification.json').read_text(encoding='utf-8'))
    if prior.get('passed') is not True or prior['scene_sha256'] != SOURCE_SHA:
        raise RuntimeError('Prior checkpoint verification differs')
    source_copy.write_bytes(SOURCE.read_bytes())
    state = {}
    snapshot_dir = out/'source-snapshot'
    snapshot_dir.mkdir()
    snapshots = []
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson05_lid_export.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
                     'learning/tutor/scenarios/lid_stl_checks.py'):
        original = PROJECT/relative
        target = snapshot_dir/original.name
        target.write_bytes(original.read_bytes())
        snapshots.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snapshot_dir/'manifest.json').write_text(json.dumps(dict(
        recordedAt=datetime.now(timezone.utc).isoformat(),files=snapshots,
        sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),
        ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        if any(g['sha256'](str(p)) != SOURCE_SHA for p in (SOURCE,source_copy)):
            raise RuntimeError('Original or opened source copy changed')
        k.guard()

    def active_mesh():
        obj = bpy.context.view_layer.objects.active
        if not obj or obj.type != 'MESH':
            raise RuntimeError('Active object is not a mesh')
        return obj

    def frame(notches=2):
        do(lambda:click(184,38),.4)
        k.menu_item(236,168,.7)
        k.wheel_out(notches)

    def underside():
        do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.5)
        do(lambda:key('NUMPAD_2',x=700,y=600),.4)
        do(lambda:key('NUMPAD_2',x=700,y=600),.4)
        do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def operator_properties():
        return k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator.properties

    def export_options():
        p = operator_properties()
        return dict(only_selected=bool(p.export_selected_objects),global_scale=float(p.global_scale),
                    use_scene_unit=bool(p.use_scene_unit),apply_modifiers=bool(p.apply_modifiers),
                    forward_axis=p.forward_axis,up_axis=p.up_axis,ascii_format=bool(p.ascii_format),
                    use_batch=bool(p.use_batch),evaluation_mode=p.evaluation_mode)

    k.setup()
    # Applies only to this isolated process, so temporary selection/visibility is never saved over a source.
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(copies)+'\\',source_copy.name)
    record('05-06','source-open-dialog','File > Open…，開啟 05-05 上蓋 v001 的同雜湊副本',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','上蓋來源 v001'),k.fb_box('confirm','Open')])
    k.confirm_dialog(2.0)
    k.click_outliner('Body')
    do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Lid')
    underside()
    frame(2)

    def source_read():
        unchanged()
        if Path(bpy.data.filepath).resolve() != source_copy.resolve():
            raise RuntimeError('Wrong opened checkpoint')
        if active_mesh().name != 'Lid' or [o.name for o in bpy.context.selected_objects] != ['Lid']:
            raise RuntimeError('Exactly Lid must be selected, excluding Body')
        bd = read_body_and_validate(bpy.data.objects['Body'])
        ld = read_lid_and_validate(active_mesh(),bd)
        state.update(source_body=bd,source_lid=ld)
        (out/'source-geometry-verification.json').write_text(json.dumps(dict(passed=True,body=bd,lid=ld),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '只選 Lid；整體 %s mm、板厚 %g、唇深 %g、環壁 %g mm；來源與副本 SHA-256 一致。Body 暫隱藏但未改幾何。'%(
            ld['dimensions_mm'],ld['plate_thickness_mm'],ld['ring_depth_mm'],ld['ring_wall_mm'])

    record('05-06','lid-selected','只選 Lid，底部斜視核對 Dimensions、板厚與環形唇邊，排除 Body',
           source_read,park=PARK,highlights=k.boxes(k.outliner_box('Lid','只選 Lid'),B(963,383,228,77,'Lid 整體 60 × 40 × 6 mm')),
           note='板厚 2 mm 加向下唇深 4 mm，整體高 6 mm。0.4 mm 總間隙／每側 0.2 mm 仍是幾何試驗值。')
    do(lambda:click(40,13),.5)
    do(lambda:move(73,317),.6)
    do(lambda:move(288,436),.4)
    record('05-06','export-menu','File > Export，指到 STL (.stl)',lambda:k.selection(),
           highlights=[B(28,307,202,20,'Export'),B(236,426,244,20,'STL (.stl)')])
    k.menu_item(288,436,1.2)
    k.fill_dialog(str(exports)+'\\',STL_NAME)
    record('05-06','export-before','核對 STL 匯出檔名、路徑及目前選項',
           lambda:'資料夾 %s；檔名 %s；選項 %s。'%(k.browser()+(export_options(),)),
           win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','u05_lid_v001.stl'),B(920,148,135,22,'Selection Only'),B(920,170,135,43,'Scale / Scene Unit')])

    def selection_only():
        if not operator_properties().export_selected_objects:
            click(929,159,win='FILE_BROWSER')
    do(selection_only,.6)

    def checked_options():
        unchanged()
        options = export_options()
        expected = dict(only_selected=True,global_scale=1.0,use_scene_unit=False,apply_modifiers=True,
                        forward_axis='Y',up_axis='Z',ascii_format=False,use_batch=False,evaluation_mode='DAG_EVAL_RENDER')
        if options != expected or [o.name for o in bpy.context.selected_objects] != ['Lid']:
            raise RuntimeError('Export options or only-Lid selection differ: '+str(options))
        folder,name = k.browser()
        target = (Path(folder)/name).resolve()
        if target.parent != exports.resolve() or name != STL_NAME or target.exists():
            raise RuntimeError('Unsafe STL output path or existing version')
        state['options'] = options
        return 'Selection Only 開、Scale 1、Scene Unit 關、Apply Modifiers 開、Binary、Batch 關、Y Forward / Z Up；只匯出 Lid。'

    record('05-06','export-options','勾選並核對 Selection Only，再核對 Scale 1、Scene Unit 不勾與本次新檔路徑',
           checked_options,win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[B(920,148,135,22,'Selection Only 開'),B(920,170,135,43,'Scale 1 / Scene Unit 關'),k.fb_box('confirm','Export STL')],
           note='本場景 Unit Scale 0.001。STL 沒有長度單位標記，本次匯出數字按毫米解讀；尚未核對切片擺放。')
    k.confirm_dialog(1.6)

    def exported():
        unchanged()
        stl = exports/STL_NAME
        actual_source = dict(passed=True,body=state['source_body'],lid=state['source_lid'])
        st = validate_lid_stl(stl,actual_source)
        state['stl'] = st
        (out/'stl-verification.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '%s：%d bytes、%d 三角形；檔內外形 %s（按 mm 解讀）、板厚 2／唇深 4、單殼、Non Manifold 0；SHA-256 %s。'%(
            STL_NAME,st['byte_size'],st['triangle_count'],st['dimensions_mm'],st['stl_sha256'])

    record('05-06','stl-checked','按 Export STL，解析磁碟 STL 的尺寸、拓樸、唇內外平面與盲內凹，對照來源',
           exported,park=PARK,
           note='STL 保留原場景 world Z 11～17 mm。這是數位檔案核對，尚未進行切片、落床方向、列印或試配。')
    # New empty millimetre scene; do not click Item until an actual imported object exists.
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
    record('05-06','empty-mm-scene','File > New > General，清空獨立場景，設 Metric / Millimeters / Unit Scale 0.001',
           lambda:'場景物件 %d；Unit Scale %g；Length %s。'%(len(bpy.data.objects),bpy.context.scene.unit_settings.scale_length,bpy.context.scene.unit_settings.length_unit),park=PARK)
    do(lambda:key('F3',x=700,y=600),.35)
    do(lambda:k.type_text('Import STL'),.35)
    do(lambda:key('RET'),1.0)
    k.fill_dialog(str(exports)+'\\',STL_NAME)

    def import_options():
        p = operator_properties()
        if p.global_scale != 1 or p.use_scene_unit or p.forward_axis != 'Y' or p.up_axis != 'Z':
            raise RuntimeError('Import options differ')
        state['import_options'] = dict(global_scale=float(p.global_scale),use_scene_unit=bool(p.use_scene_unit),forward_axis=p.forward_axis,up_axis=p.up_axis)
        return '實際 STL：%s；Scale 1、Scene Unit 關、Y Forward / Z Up。'%k.browser()[1]

    record('05-06','import-dialog','F3 搜尋 Import STL，選本次剛匯出的上蓋 STL，讀回匯入選項',
           import_options,win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','本次 STL v001'),k.fb_box('confirm','Import STL')])
    k.confirm_dialog(1.6)
    do(lambda:click(1213,102),.5)
    frame(2)

    def imported():
        unchanged()
        if len([o for o in bpy.data.objects if o.type=='MESH']) != 1:
            raise RuntimeError('Expected exactly one imported lid, no Body')
        obj = active_mesh()
        if not k.view3d().show_region_ui:
            raise RuntimeError('Item Sidebar must be visible')
        ld = read_lid_and_validate(obj,state['source_body'])
        if not math.isclose(ld['volume_mm3'],state['stl']['volume_mm3'],rel_tol=1e-5,abs_tol=1e-4):
            raise RuntimeError('Actual reimport/STL volume mismatch')
        state['reimport_lid'] = ld
        return '實際重新匯入 '+obj.name+'；Item Dimensions %s mm，Scale 1、Non Manifold 0；板厚 %g、唇深 %g mm，來源與 STL 幾何一致。'%(
            ld['dimensions_mm'],ld['plate_thickness_mm'],ld['ring_depth_mm'])

    record('05-06','reimport-dimensions','實際匯入後才切 Item 分頁，Frame Selected，核對 Dimensions 60 × 40 × 6 mm',
           imported,park=PARK,highlights=[B(963,383,228,77,'STL 重新匯入：60 × 40 × 6 mm')])
    underside()
    record('05-06','reimport-underside','底部斜視，從實際重新匯入的 STL 核對一體定位環與盲內凹',
           imported,park=PARK,highlights=[B(963,383,228,77,'整高 6 = 板厚 2 + 唇深 4 mm')],
           note='0.4 mm 總間隙仍為幾何試驗值。STL 重新匯入成功不等於實際列印或試配合格。')
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('TWO',x=700,y=600),.3)
    do(lambda:click(280,38),.3)
    k.menu_item(303,81,.4)
    do(lambda:key('F3',x=700,y=600),.3)
    do(lambda:k.type_text('Select Non Manifold'),.3)
    do(lambda:key('RET'),.6)

    def nm_selected():
        bm = bmesh.from_edit_mesh(active_mesh().data)
        if not bm.verts or not bm.faces or any(not e.is_manifold for e in bm.edges) or any(e.select for e in bm.edges):
            raise RuntimeError('Reimported mesh Non Manifold UI check failed')
        return '非空上蓋網格，Select Non Manifold 選到邊 0；程式讀回 Non Manifold 0。'

    record('05-06','non-manifold','Tab > 邊選取 > Select None，再 F3 搜尋 Select Non Manifold',nm_selected,park=PARK)
    do(lambda:key('TAB',x=700,y=600),.4)

    def verified():
        imported()
        stl = exports/STL_NAME
        st = validate_lid_stl(stl,dict(passed=True,body=state['source_body'],lid=state['source_lid']))
        if st['stl_sha256'] != state['stl']['stl_sha256']:
            raise RuntimeError('Exported STL changed after reimport')
        result=dict(passed=True,kind='lid_stl_export',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
                    opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
                    source_object='Lid',source_lid=state['source_lid'],source_body=state['source_body'],
                    stl_path=str(stl),stl_sha256=st['stl_sha256'],stl_bytes=st['byte_size'],stl_dimensions_mm=st['dimensions_mm'],
                    stl_triangles=st['triangle_count'],stl_non_manifold_edges=st['non_manifold_edges'],stl_connected_shells=st['connected_shells'],
                    stl_genus=st['genus'],stl_volume_mm3=st['volume_mm3'],stl_verification=st,
                    reimport_verified=True,reimport_lid=state['reimport_lid'],import_options=state['import_options'],
                    trial_total_clearance_mm=.4,trial_per_side_clearance_mm=.2,trial_status='experimental_geometry_only',
                    printed=False,fit_tested=False,physical_measurements=None,fit_results=None,qualified_clearance_mm=None,
                    slicer_checked=False,saved_new_scene=False,
                    numericComparison=dict(purpose='Floating point reconstruction only; not manufacturing tolerance or printed fit acceptance',dimensionsAbsMm=1e-4,volumeRelative=1e-5),
                    **state['options'])
        (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '上蓋 STL 匯出、實檔解析、實際重新匯入皆通過；外形 60 × 40 × 6、板厚 2、唇深 4 mm；來源 hash 不變。尚未列印／實測／試配，合格間隙空白。'

    record('05-06','verified','保存 STL 與來源版本關聯、數位讀值及 verification.json',verified,park=PARK,
           note='本次只完成 05-06 的匯出與數位核對部分；實體結果保持 null，不代學員確認完成。')
