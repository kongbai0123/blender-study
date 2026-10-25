"""05-04: actual isolated UI STL export/reimport; physical tests stay unfilled."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from holeplate_checks import read_and_validate
from stl_checks import validate_export

SOURCES = (
    dict(kind='pin', name='FitPin', filename='u05_fit_coupon_v001', dimensions=[10, 10, 8],
         run='2026-10-22-lesson05-demo-v002',
         sha256='c2f3edd915324ba66bbd3fb8c6ad1ea0214a539f74cbc732e37adc35f7325162'),
    dict(kind='hole_plate', name='Plate', filename='u05_hole_plate_v001', dimensions=[96, 26, 4],
         run='2026-10-22-lesson05-holes-demo-v002',
         sha256='10bfffd651d1583d8704164288aa0757fa617f67a30e21176d7fc892aef3e692'),
)


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    out = Path(g['OUT'])
    sources_dir = Path(k.demo_dir) / 'sources'
    exports_dir = Path(k.demo_dir) / 'exports'
    sources_dir.mkdir()
    exports_dir.mkdir()
    entries = []
    options = {}
    source_paths = {}
    source_metadata = {}
    snapshots = []
    for item in SOURCES:
        source_run = PROJECT / 'learning/evidence/05' / item['run']
        source = source_run / 'demo-files' / (item['filename']+'.blend')
        if g['sha256'](str(source)) != item['sha256']:
            raise RuntimeError('Verified source changed: '+str(source))
        metadata = json.loads((source_run/'verification.json').read_text(encoding='utf-8'))
        if not metadata['passed'] or metadata['scene_sha256'] != item['sha256']:
            raise RuntimeError('Source verification/hash mismatch')
        copy = sources_dir / source.name
        copy.write_bytes(source.read_bytes())
        source_paths[item['kind']] = (source, copy)
        source_metadata[item['kind']] = metadata
    snapshot_dir = out / 'source-snapshot'
    snapshot_dir.mkdir()
    for relative in ('learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py', 'learning/tutor/scenarios/lesson05_export.py',
                     'learning/tutor/scenarios/holeplate_checks.py', 'learning/tutor/scenarios/stl_checks.py'):
        source = PROJECT / relative
        target = snapshot_dir / source.name
        target.write_bytes(source.read_bytes())
        snapshots.append(dict(source=relative, snapshot='source-snapshot/'+source.name,
                              sha256=g['sha256'](str(target))))
    (snapshot_dir/'manifest.json').write_text(json.dumps(dict(
        recordedAt=datetime.now(timezone.utc).isoformat(), files=snapshots,
        sources=[dict(kind=i['kind'], original=str(source_paths[i['kind']][0]),
                      copy=str(source_paths[i['kind']][1]), sha256=i['sha256']) for i in SOURCES]
    ), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    def unchanged():
        for item in SOURCES:
            for p in source_paths[item['kind']]:
                if g['sha256'](str(p)) != item['sha256']:
                    raise RuntimeError('Source or opened copy was modified')
        k.guard()

    def active_mesh():
        obj = bpy.context.view_layer.objects.active
        if not obj or obj.type != 'MESH':
            raise RuntimeError('Active object is not a mesh')
        return obj

    def geometry(obj, expected):
        factor = bpy.context.scene.unit_settings.scale_length * 1000
        dims = [float(v)*factor for v in obj.dimensions]
        u = bpy.context.scene.unit_settings
        if u.system != 'METRIC' or u.length_unit != 'MILLIMETERS' or not math.isclose(u.scale_length, .001, abs_tol=1e-9):
            raise RuntimeError('Millimetre scene units do not match')
        if any(not math.isclose(a,b,abs_tol=1e-4) for a,b in zip(dims,expected)):
            raise RuntimeError('Actual dimensions differ: '+str(dims))
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            if not bm.verts or not bm.faces:
                raise RuntimeError('Empty mesh')
            count = sum(not e.is_manifold for e in bm.edges)
            if count:
                raise RuntimeError('Non Manifold edges '+str(count))
        finally:
            bm.free()
        return dict(dimensions_mm=dims, non_manifold_edges=count,
                    scale=[float(v) for v in obj.scale], vertices=len(obj.data.vertices),
                    faces=len(obj.data.polygons))

    def operator_properties():
        return k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator.properties

    def export_options():
        p = operator_properties()
        return dict(only_selected=bool(p.export_selected_objects), global_scale=float(p.global_scale),
                    use_scene_unit=bool(p.use_scene_unit), apply_modifiers=bool(p.apply_modifiers),
                    forward_axis=p.forward_axis, up_axis=p.up_axis, ascii_format=bool(p.ascii_format),
                    use_batch=bool(p.use_batch), evaluation_mode=p.evaluation_mode)

    def search(text):
        do(lambda: key('F3', x=700, y=600), .35)
        do(lambda: k.type_text(text), .35)
        do(lambda: key('RET'), 1.0)

    k.setup()
    # Only this isolated process: File > New must not prompt to save source copies.
    do(lambda: setattr(bpy.context.preferences.view, 'use_save_prompt', False), .1)

    for item in SOURCES:
        kind, name = item['kind'], item['name']
        original, copy = source_paths[kind]
        k.file_dialog(56, str(sources_dir)+'\\', copy.name)
        record('05-04', kind+'-open-dialog', 'File > Open…，開啟來源 '+copy.name+' 的同雜湊副本',
               lambda: '資料夾 %s；檔名 %s。' % k.browser(), win='FILE_BROWSER',
               highlights=lambda: [k.fb_box('name','來源場景 v001'), k.fb_box('confirm','Open')])
        k.confirm_dialog(2.0)
        k.click_outliner(name)
        do(lambda: click(184,38),.4)
        k.menu_item(236,168,.6)
        k.wheel_out(3 if kind=='pin' else 1)

        def source_read(i=item, path=copy):
            unchanged()
            if Path(bpy.data.filepath).resolve() != path.resolve():
                raise RuntimeError('Opened scene path differs')
            obj = active_mesh()
            if obj.name != i['name'] or [o.name for o in bpy.context.selected_objects] != [i['name']]:
                raise RuntimeError('Exactly one intended source object must be selected')
            geo = geometry(obj, i['dimensions'])
            if i['kind'] == 'hole_plate':
                read_and_validate(obj)
                if not bpy.data.objects['Cutters'].hide_get():
                    raise RuntimeError('Construction cutters must remain hidden')
            return '%s；Dimensions %s mm；Scale %s；Non Manifold 0；來源及副本 SHA-256 相同。' % (obj.name,geo['dimensions_mm'],geo['scale'])

        record('05-04', kind+'-source-checked', '只選 '+name+'，核對原來源與副本雜湊、尺寸及網格',
               source_read, highlights=k.boxes(k.outliner_box(name,'只選 '+name)), park=PARK)
        do(lambda: click(40,13), .5)
        do(lambda: move(73,317), .6)
        do(lambda: move(288,436), .4)
        record('05-04', kind+'-export-menu', 'File > Export，指到 STL (.stl)',
               lambda: k.selection(), highlights=[B(28,307,202,20,'Export'),B(236,426,244,20,'STL (.stl)')])
        k.menu_item(288,436,1.2)
        k.fill_dialog(str(exports_dir)+'\\',item['filename']+'.stl')
        record('05-04', kind+'-export-before', '核對 STL 匯出路徑、檔名與目前選項',
               lambda: '目標 %s / %s；選項 %s。' % (k.browser()+ (export_options(),)), win='FILE_BROWSER',
               highlights=lambda: [k.fb_box('name','匯出 v001'),B(920,148,135,22,'Selection Only'),B(920,170,135,43,'Scale 1 / Scene Unit')],park=(300,400))

        def enable_selection():
            if not operator_properties().export_selected_objects:
                click(929,159,win='FILE_BROWSER')
        do(enable_selection,.6)

        def checked_options(i=item):
            unchanged()
            actual = export_options()
            desired = dict(only_selected=True,global_scale=1.0,use_scene_unit=False,apply_modifiers=True,
                           forward_axis='Y',up_axis='Z',ascii_format=False,use_batch=False,evaluation_mode='DAG_EVAL_RENDER')
            if actual != desired:
                raise RuntimeError('Export options differ: '+str(actual))
            folder, filename = k.browser()
            target = (Path(folder)/filename).resolve()
            if target.parent != exports_dir.resolve() or target.name != i['filename']+'.stl' or target.exists():
                raise RuntimeError('Unsafe export path or existing version')
            if [o.name for o in bpy.context.selected_objects] != [i['name']]:
                raise RuntimeError('Export selection changed')
            options[i['kind']] = actual
            return 'Selection Only 開；Scale 1；Scene Unit 關；Apply Modifiers 開；Y Forward / Z Up；Binary；只匯出 '+i['name']+'。'

        record('05-04',kind+'-export-options','核對並勾選 Selection Only，其餘保持 Scale 1、Scene Unit 不勾，再驗證安全目標',
               checked_options,win='FILE_BROWSER', highlights=lambda:[B(920,148,135,22,'Selection Only 開'),B(920,170,135,43,'Scale 1 / Scene Unit 關'),k.fb_box('confirm','Export STL')],
               note='這兩份場景的 Unit Scale 已是 0.001，匯出數字以毫米解讀。STL 本身沒有單位標記；這些設定由實際視窗讀回。',park=(300,400))
        k.confirm_dialog(1.5)

        def exported(i=item):
            unchanged()
            stl = exports_dir/(i['filename']+'.stl')
            result = validate_export(stl,i['kind'],source_metadata[i['kind']])
            (out/(i['kind']+'-stl-verification.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            original, copied = source_paths[i['kind']]
            entry = dict(kind=i['kind'],source_scene_path=str(original),source_scene_sha256=i['sha256'],
                         opened_scene_path=str(copied),opened_scene_sha256=i['sha256'],opened_copy_unchanged=True,
                         source_unchanged=True,source_object=i['name'],source_dimensions_mm=i['dimensions'],
                         stl_path=str(stl),stl_sha256=result['stl_sha256'],stl_bytes=stl.stat().st_size,
                         stl_dimensions_mm=result['dimensions_mm'],stl_triangles=result['triangle_count'],
                         stl_non_manifold_edges=result['non_manifold_edges'],stl_connected_shells=result['connected_shells'],
                         stl_genus=result['genus'],stl_volume_mm3=result['volume_mm3'],
                         stl_verification_path=str(out/(i['kind']+'-stl-verification.json')),**options[i['kind']])
            if i['kind']=='hole_plate':
                entry.update(stl_hole_widths_mm=result['measured_hole_widths_mm'],stl_through_holes=result['through_holes'],stl_marker_counts=result['marker_counts'])
            entries.append(entry)
            return '%s：%d bytes、%d 三角形、檔內外形 %s（按 mm 解讀）；Non Manifold 0、單殼、genus %d；SHA-256 %s。' % (
                stl.name,entry['stl_bytes'],entry['stl_triangles'],entry['stl_dimensions_mm'],entry['stl_genus'],entry['stl_sha256'])

        record('05-04',kind+'-stl-checked','按 Export STL，再直接解析磁碟 STL 的三角形、尺寸及拓樸，與來源網格比較',exported,park=PARK,
               note='這是數位檔案檢查；尚未匯入切片軟體、列印、實體量測或試配。')

    # Independently reimport both actual files into an empty millimetre scene.
    do(lambda: click(40,13),.4)
    do(lambda: move(67,36),.5)
    k.menu_item(285,35,1.5)
    do(lambda: key('A',x=700,y=600),.3)
    do(lambda: key('X',x=700,y=600),.4)
    do(lambda: key('RET'),.8)
    do(lambda: click(1245,374),.5)
    do(lambda: click(1302,433),.5)
    do(lambda: click(1418,557),.5)
    k.menu_item(1397,668,.5)
    k.type_into(1417,488,'0.001')
    k.open_sidebar()
    do(lambda:click(1213,102),.4)
    record('05-04','empty-mm-scene','File > New > General，清空獨立場景，設毫米單位以重新匯入 STL 核對',
           lambda:'本次新場景物件 %d；Unit Scale %g；Length %s。' % (len(bpy.data.objects),bpy.context.scene.unit_settings.scale_length,bpy.context.scene.unit_settings.length_unit),park=PARK)

    for item in SOURCES:
        search('Import STL')
        k.fill_dialog(str(exports_dir)+'\\',item['filename']+'.stl')

        def import_options():
            p=operator_properties()
            if p.global_scale != 1 or p.use_scene_unit or p.forward_axis != 'Y' or p.up_axis != 'Z':
                raise RuntimeError('STL import scale/axes differ')
            return '從本次 exports 讀取 '+k.browser()[1]+'；Scale 1、Scene Unit 關、Y Forward / Z Up。'

        record('05-04',item['kind']+'-import-dialog','F3 搜尋 Import STL，選剛產出的實際 STL，核對匯入 Scale 與方向',import_options,win='FILE_BROWSER',
               highlights=lambda:[k.fb_box('name','剛匯出的 STL'),k.fb_box('confirm','Import STL')])
        k.confirm_dialog(1.5)
        def ensure_sidebar():
            if not k.view3d().show_region_ui:
                key('N',x=700,y=600)
        do(ensure_sidebar,.4)
        do(lambda: click(184,38),.4)
        k.menu_item(236,168,.7)
        k.wheel_out(3 if item['kind']=='pin' else 1)
        if item['kind']=='hole_plate':
            do(lambda:key('NUMPAD_7',x=700,y=600),.4)
            for _ in range(3):
                do(lambda:key('NUMPAD_2',x=700,y=600),.3)
            do(lambda:key('NUMPAD_6',x=700,y=600),.4)

        def imported(i=item):
            unchanged()
            obj=active_mesh()
            geo=geometry(obj,i['dimensions'])
            if i['kind']=='hole_plate':
                read_and_validate(obj)
            entry=next(e for e in entries if e['kind']==i['kind'])
            entry.update(stl_reimport_verified=True,stl_reimport_dimensions_mm=geo['dimensions_mm'],
                         stl_reimport_non_manifold_edges=geo['non_manifold_edges'],stl_reimport_object=obj.name)
            return '從 STL 重新匯入 '+obj.name+'；Dimensions %s mm；Non Manifold 0；與原來源及 STL 解析讀值一致。' % geo['dimensions_mm']

        record('05-04',item['kind']+'-reimported','實際匯入 STL 後 Frame Selected，讀 Dimensions 與網格；孔板改斜視辨認六孔及凹點',
               imported, highlights=[B(963,383,228,77,'重新匯入後的 Dimensions')],park=PARK)
        if item['kind']=='pin':
            do(lambda:key('H',x=700,y=600),.4)

    def finish_verification():
        unchanged()
        if len(entries)!=2 or any(not e.get('stl_reimport_verified') for e in entries):
            raise RuntimeError('Both exports and reimports must pass')
        result=dict(passed=True,kind='fit_coupon_stl_exports',exports=entries,source_unchanged=True,
                    printed=False,fit_tested=False,physical_measurements=None,fit_results=None,
                    qualified_clearance_mm=None,trial_total_clearances_mm=[.1,.2,.3,.4,.5,.6],
                    slicer_checked=False,stl_unit_interpretation='STL is unitless; exported coordinate values interpreted as millimetres',
                    numericComparison=dict(purpose='Floating point reconstruction only, not manufacturing tolerance or printed fit acceptance',dimensionsAbsMm=1e-4,volumeRelative=1e-5))
        (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '插銷 STL 10 × 10 × 8、孔板 STL 96 × 26 × 4（數值按 mm）；兩檔讀回及重新匯入通過。原 .blend 與副本雜湊不變；實際列印、量測、試配與合格間隙全部未填。'

    record('05-04','exports-verified','保存兩份 STL 與來源版本關聯、完整讀值及 verification.json',finish_verification,park=PARK,
           note='本次完成的是 05-04 的 STL 匯出與數位尺寸核對部分；沒有完成列印／試配，也不更新學員完成進度。0.1～0.6 mm 全部保留為試驗點。')
