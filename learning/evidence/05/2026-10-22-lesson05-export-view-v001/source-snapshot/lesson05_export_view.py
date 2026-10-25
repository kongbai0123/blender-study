"""05-04 supplementary actual STL reimport views with readable Item Dimensions."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from holeplate_checks import read_and_validate
from stl_checks import validate_export

SOURCE_RUN = '2026-10-22-lesson05-export-demo-v003'
ITEMS = (
    dict(kind='pin', filename='u05_fit_coupon_v001.stl', dimensions=[10, 10, 8],
         sha256='bc10342c54a94d87c15eccb050fb9b30a7ae00bf4079d4c7869ac53d199db784'),
    dict(kind='hole_plate', filename='u05_hole_plate_v001.stl', dimensions=[96, 26, 4],
         sha256='8105d1ebdc04ed12a2b7f98cc3b728db74063c453961c33d165ac50e694c7c8b'),
)


def build(g):
    k = Kit(g)
    do, click, key, record = k.do, k.click, k.key, k.record
    out = Path(g['OUT'])
    copies = Path(k.demo_dir) / 'sources'
    copies.mkdir()
    sources = []
    for item in ITEMS:
        original = PROJECT / 'learning/evidence/05' / SOURCE_RUN / 'demo-files/exports' / item['filename']
        if g['sha256'](str(original)) != item['sha256']:
            raise RuntimeError('Authoritative STL hash changed')
        target = copies / item['filename']
        target.write_bytes(original.read_bytes())
        sources.append(dict(kind=item['kind'], original=str(original), copy=str(target), sha256=item['sha256']))
    snapshot_dir = out / 'source-snapshot'
    snapshot_dir.mkdir()
    snapshots = []
    for relative in ('learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py', 'learning/tutor/scenarios/lesson05_export_view.py',
                     'learning/tutor/scenarios/holeplate_checks.py', 'learning/tutor/scenarios/stl_checks.py'):
        original = PROJECT / relative
        target = snapshot_dir / original.name
        target.write_bytes(original.read_bytes())
        snapshots.append(dict(source=relative, snapshot='source-snapshot/'+target.name, sha256=g['sha256'](str(target))))
    (snapshot_dir/'manifest.json').write_text(json.dumps(dict(
        recordedAt=datetime.now(timezone.utc).isoformat(), files=snapshots, sources=sources,
        scope='Supplementary views only; authoritative export run remains '+SOURCE_RUN),
        ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    readings = []

    def unchanged():
        k.guard()
        for source in sources:
            if any(g['sha256'](source[field]) != source['sha256'] for field in ('original', 'copy')):
                raise RuntimeError('Original STL or demonstration copy changed')

    def search(text):
        do(lambda:key('F3', x=700, y=600), .35)
        do(lambda:k.type_text(text), .35)
        do(lambda:key('RET'), 1.0)

    def mesh_read(item):
        unchanged()
        obj = bpy.context.view_layer.objects.active
        if not obj or obj.type != 'MESH':
            raise RuntimeError('Expected imported mesh')
        u = bpy.context.scene.unit_settings
        if u.system != 'METRIC' or u.length_unit != 'MILLIMETERS' or not math.isclose(u.scale_length, .001, abs_tol=1e-9):
            raise RuntimeError('Expected millimetre scene')
        if not k.view3d().show_region_ui:
            raise RuntimeError('Sidebar is not shown')
        factor = u.scale_length * 1000
        dimensions = [float(v)*factor for v in obj.dimensions]
        if any(not math.isclose(a,b,rel_tol=0,abs_tol=1e-4) for a,b in zip(dimensions,item['dimensions'])):
            raise RuntimeError('Imported dimensions differ')
        if any(not math.isclose(float(v),1,rel_tol=0,abs_tol=1e-6) for v in obj.scale):
            raise RuntimeError('Imported scale differs from 1')
        bm=bmesh.new()
        try:
            bm.from_mesh(obj.data)
            if not bm.verts or not bm.faces:
                raise RuntimeError('Empty imported mesh')
            non_manifold=sum(not e.is_manifold for e in bm.edges)
            if non_manifold:
                raise RuntimeError('Imported mesh is not closed')
            bm.transform(obj.matrix_world)
            volume=bm.calc_volume(signed=True)*factor**3
        finally:
            bm.free()
        stl=validate_export(copies/item['filename'],item['kind'])
        if not math.isclose(volume,stl['volume_mm3'],rel_tol=1e-5,abs_tol=1e-4):
            raise RuntimeError('Imported/STL volume mismatch')
        result=dict(kind=item['kind'],filename=item['filename'],object_name=obj.name,
                    dimensions_mm=dimensions,scale=[float(v) for v in obj.scale],
                    non_manifold_edges=non_manifold,volume_mm3=volume,
                    stl_sha256=item['sha256'],stl_unchanged=True,
                    stl_dimensions_mm=stl['dimensions_mm'])
        if item['kind']=='hole_plate':
            result['actual_mesh_verification']=read_and_validate(obj)
        readings.append(result)
        return '重新匯入 %s；Item > Dimensions %s mm；Scale 1、1、1；Non Manifold 0；原 STL 與副本 SHA-256 一致。' % (obj.name,dimensions)

    k.setup()
    do(lambda:key('A',x=700,y=600),.3)
    do(lambda:key('X',x=700,y=600),.4)
    do(lambda:key('RET'),.8)
    do(lambda:click(1245,374),.5)
    do(lambda:click(1302,433),.5)
    do(lambda:click(1418,557),.5)
    k.menu_item(1397,668,.5)
    k.type_into(1417,488,'0.001')
    k.open_sidebar()
    record('05-04','empty-mm-scene','清空獨立出廠場景，設 Metric / Millimeters / Unit Scale 0.001；空場景不點 Item',
           lambda:'場景物件 %d；Unit Scale %g；Length %s。' % (len(bpy.data.objects),bpy.context.scene.unit_settings.scale_length,bpy.context.scene.unit_settings.length_unit),park=PARK)

    for item in ITEMS:
        search('Import STL')
        k.fill_dialog(str(copies)+'\\',item['filename'])
        def import_options():
            p=k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator.properties
            if p.global_scale != 1 or p.use_scene_unit or p.forward_axis != 'Y' or p.up_axis != 'Z':
                raise RuntimeError('Import options differ')
            return '本次 sources / '+k.browser()[1]+'；Scale 1、Scene Unit 關、Y Forward / Z Up。'
        record('05-04',item['kind']+'-import-dialog','F3 Import STL，選主匯出 v003 的同雜湊副本，核對匯入選項',
               import_options,win='FILE_BROWSER',park=(300,400),
               highlights=lambda:[k.fb_box('name','同雜湊 STL 副本'),k.fb_box('confirm','Import STL')])
        k.confirm_dialog(1.5)
        if item['kind']=='pin':
            do(lambda:click(1213,102),.5)
        do(lambda:click(184,38),.4)
        k.menu_item(236,168,.7)
        k.wheel_out(3 if item['kind']=='pin' else 1)
        if item['kind']=='hole_plate':
            do(lambda:key('NUMPAD_7',x=700,y=600),.4)
            for _ in range(3):
                do(lambda:key('NUMPAD_2',x=700,y=600),.3)
            do(lambda:key('NUMPAD_6',x=700,y=600),.4)
        record('05-04',item['kind']+'-dimensions','實際匯入 STL：在 Item 的 Dimensions 欄核對 '+('10 × 10 × 8 mm' if item['kind']=='pin' else '96 × 26 × 4 mm，斜視辨認六孔與 1～6 點'),
               lambda i=item:mesh_read(i),park=PARK,
               highlights=[k.box(963,383,228,77,'STL 重新匯入後的 Dimensions')],
               note='這是主匯出 v003 相同 STL 的補充實拍；沒有重新匯出或修改來源，也沒有列印、試配或判定合格間隙。')
        if item['kind']=='pin':
            do(lambda:key('H',x=700,y=600),.4)

    def verified():
        unchanged()
        if len(readings)!=2:
            raise RuntimeError('Both imported views must pass')
        result=dict(passed=True,kind='fit_coupon_stl_supplementary_views',authoritative_export_run=SOURCE_RUN,
                    sources=sources,imports=readings,source_stls_unchanged=True,saved_scene=False,
                    printed=False,fit_tested=False,physical_measurements=None,fit_results=None,
                    qualified_clearance_mm=None,slicer_checked=False,
                    trial_total_clearances_mm=[.1,.2,.3,.4,.5,.6],
                    numericComparison=dict(purpose='Floating point reconstruction only; not manufacturing tolerance or fit acceptance',dimensionsAbsMm=1e-4,volumeRelative=1e-5))
        (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '插銷與孔板重新匯入讀值通過；原 STL 和本次副本雜湊不變。未儲存場景，未列印／實體量測／試配，合格間隙為空。'
    record('05-04','supplement-verified','保存補充實拍讀值與 verification.json；主匯出證據仍為 v003',verified,park=PARK)
