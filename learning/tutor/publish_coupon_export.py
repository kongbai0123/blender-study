"""Publish 07-05's three STL outputs; retain the original geometry demonstration."""
import copy
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from publish_overhang import PROJECT, digest, read, write, fingerprint
from finalize_overhang import http_exact, jpeg_size

RUN_ID = '2026-10-25-lesson07-coupon-export-demo-v001'
REL = 'learning/evidence/07/' + RUN_ID
RUN = PROJECT / REL
UI = 'learning/evidence/ui/' + RUN_ID
NAMES = ('A_L19', 'B_L17', 'C_L21')


def fmt(number):
    return '0' if round(number, 3) == 0 else f'{number:.3f}'.rstrip('0').rstrip('.')


def vector(values):
    return ' × '.join(fmt(value) for value in values)


def geometry_review(baseline):
    review = copy.deepcopy(baseline['prior_step']['couponReview'])
    review['physicalRecordPath'] = REL + '/trial-fit-record-v001.json'
    assert review['notes'][-1].startswith('本次沒有STL')
    review['notes'][-1] = '上一階段僅建立幾何草案；本階段已匯出三份STL，版本與新空白試配表見上方STL核對。舊場景及舊空白表保留不改。'
    return review


def invariant(catalog, baseline, check_history=True):
    changed = [s['id'] for lesson in catalog['lessons'] for s in lesson['steps']
               if fingerprint(s) != baseline['steps'][s['id']]]
    assert changed == ['07-05'] and len(baseline['steps']) == 52, changed
    assert digest(PROJECT / 'learning/progress.json') == baseline['progress_sha256']
    for item in baseline['protected_prior_files']:
        path = PROJECT / item['path']
        assert digest(path) == item['sha256'] and path.stat().st_size == item['bytes'], item['path']
    if check_history:
        step = next(s for lesson in catalog['lessons'] for s in lesson['steps'] if s['id'] == '07-05')
        assert step['previousOperationRuns'][-1] == baseline['prior_step']['operationRun']
        assert step['couponReview'] == geometry_review(baseline)
    return changed


def validate():
    import import_run as importer
    run = read(RUN / 'run.json')
    catalog = read(PROJECT / 'learning/catalog.json')
    importer._validate_lesson07_coupon_export(run, RUN, importer.RUNS[RUN_ID])
    importer._validate_records(run, RUN, importer.RUNS[RUN_ID], {
        s['id']: s for lesson in catalog['lessons'] if lesson['id'] == '07' for s in lesson['steps']})
    v = read(RUN / 'verification.json')
    assert v['passed'] and v['kind'] == 'cantilever_coupon_stl_exports'
    assert v['exported_stl'] and v['reimport_verified']
    assert v['reimport_mesh_datablocks_created'] is True and v['new_specimen_design_created'] is False
    assert {entry['variant'] for entry in v['exports']} == set(NAMES)
    for key in ['saved_new_scene', 'geometry_modified', 'rotation_applied_to_mesh', 'strength_analysis_performed',
                'deformation_analysis_performed', 'fit_qualification', 'improvement_assessed', 'slicer_checked', 'printed', 'fit_tested']:
        assert v[key] is False, key
    for key in ['material_grade', 'epsilon_allow', 'physical_measurements', 'fit_results', 'support_required',
                'final_print_orientation_approved', 'qualified_strength_N', 'qualified_clearance_mm', 'improvement_validated']:
        assert v[key] is None, key
    for name in ['independent-coupon-export-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json']:
        assert read(RUN / name)['passed'], name
    return v, run


def publish():
    v, run = validate()
    baseline = read(RUN / 'publication-baseline-v001.json')
    manifest = read(RUN / 'export-manifest-v001.json')
    manifest['publication_audits'] = [dict(path=REL + '/' + name, sha256=digest(RUN / name)) for name in [
        'independent-coupon-export-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json']]
    write(RUN / 'export-manifest-v001.json', manifest)
    catalog_path = PROJECT / 'learning/catalog.json'
    original = catalog_path.read_bytes()
    catalog = json.loads(original)
    step = next(s for lesson in catalog['lessons'] for s in lesson['steps'] if s['id'] == '07-05')
    assert step['operationRun']['id'] == RUN_ID
    prior = baseline['prior_step']
    step['previousOperationRuns'] = copy.deepcopy(prior.get('previousOperationRuns', []) + [prior['operationRun']])
    step['couponReview'] = geometry_review(baseline)
    step.update(title='卡扣對照試片與 STL 數位核對',
        action='沿用A_L19、B_L17、C_L21幾何草案及Ry90候選位置，逐件Selection Only匯出新v001 STL；解析實檔，再在空白毫米場景實際重匯入核對。原臂長幾何示範保留在下方歷史紀錄。',
        success='三份STL實檔與實際重匯入的世界外框、完整有向表面、逆回原建模軸的臂長與根部／扣鉤幾何皆在數值門檻內與來源一致；各一體閉合、Non Manifold0。原場景、副本與幾何草案紀錄未改。沒有驗證改善、強度或實體配合合格。',
        guide=[
            dict(mark='1', where='07-05同hash副本 · Object Mode',
                 do='每件重開來源副本，只選A_L19、B_L17或C_L21，隱藏其餘兩試片；原Body／Lid及兩工具保持隱藏。',
                 see='來源仍Ry90、Scale1，物件軸Dimensions約9×4.6×24／22／26 mm；世界外框另算約24／22／26×4.6×9。沒有Apply Rotation、重建或再改臂長。'),
            dict(mark='2', where='File > Export > STL (.stl)',
                 do='核對Selection Only開、Scale1、Scene Unit關、Binary、Y Forward／Z Up，逐件匯出u07_A_L19_v001.stl、u07_B_L17_v001.stl、u07_C_L21_v001.stl。',
                 see='每檔只有指定試片，沒有盒、蓋或其他試片。STL沒有單位標記，這次數字以毫米解讀；原生選項與實際新檔都讀回記錄。'),
            dict(mark='3', where='空白毫米場景 · Import STL',
                 do='設Metric／Millimeters／Unit Scale0.001，逐件實際重匯入，核對N面板、世界頂點與Select Non Manifold；最後合看三件。',
                 see='重匯入Rotation0／Scale1，N面板外框約24×4.6×9、22×4.6×9、26×4.6×9 mm。保留候選world位置與約7.4 mm的Y投影分隔；只有錨座側面接數位Z0。')],
        help='三件仍是獨立錨座＋臂＋鉤草案，沒有整盒邊界等效、指定對件、夾持或相對定位基準。來源幾何L19／17／21不是整件外框或力學有效長度。直臂與部分根部離床，支撐及方向仍為候選；尚未切片、列印或試扣。數位比較門檻只處理浮點重建，不是製造公差、改善或合格界線。',
        evidence=['檔案檢查', '學員回報'])
    events = step['operationRun']['events']
    step['figures'] = []
    for name in NAMES:
        event = next(e for e in events if e['figure']['path'].endswith(name + '-reimport-dimensions.png'))
        figure = dict(event['figure'])
        entry = next(e for e in v['exports'] if e['variant'] == name)
        figure['caption'] = '2026-10-25 · 助教獨立 Blender 原始實拍：' + name + '的STL實際重匯入，Item XYZ約' + vector(entry['stl_dimensions_mm']) + ' mm，Rotation0／Scale1。世界座標已在頂點中，與原Ry90的物件軸Dimensions定義不同；這是數位核對。'
        step['figures'].append(figure)
    comparisons = []
    for name in NAMES:
        entry = next(e for e in v['exports'] if e['variant'] == name)
        imported = read(RUN / ('reimport_' + name + '_mesh.json'))
        metrics = [
            ('來源Item（物件軸mm）', vector(entry['source_item_dimensions_mm'])),
            ('STL世界XYZ（mm解讀）', vector(entry['stl_dimensions_mm'])),
            ('重匯入Item XYZ（mm）', vector(imported['cad_metadata']['object_axis_dimensions_mm'])),
            ('STL三角形／殼／非流形邊', f"{entry['stl_triangles']}／{entry['stl_connected_shells']}／{entry['stl_non_manifold_edges']}")]
        comparisons.append(dict(title=name + ' · 尺寸草案', metrics=[dict(label=label, value=value) for label, value in metrics]))
    step['stlReview'] = dict(stage='digital_stl_comparison_only',
        summary='三件各自單檔匯出，解析STL，再於空白毫米場景實際重匯入。來源世界外框、完整幾何與候選位置均核對；原尺寸調整仍未驗證改善。',
        comparisons=comparisons, recordPath=REL + '/export-manifest-v001.json', recordSha256=digest(RUN / 'export-manifest-v001.json'),
        physicalRecordPath=REL + '/trial-fit-record-v001.json')
    source_rel = Path(v['source_scene_path']).relative_to(PROJECT).as_posix()
    step['operationRun']['outputFiles'] = [dict(path=Path(e['stl_path']).relative_to(PROJECT).as_posix(),
        sha256=e['stl_sha256'], bytes=e['stl_bytes'], dimensionsLabel=vector(e['stl_dimensions_mm']) + ' mm · ' + e['variant'] + '幾何草案',
        sourcePath=source_rel, sourceSha256=v['source_scene_sha256']) for e in v['exports']]
    review = step['contentReview']
    review['summary'] = '已核對07-05來源與原幾何紀錄、三件單選與原生匯出選項、三STL實檔、完整有向表面與逆姿態／逆臂長幾何、真實重匯入和版本。原24筆幾何示範完整保留；只追加STL數位準備，不判改善、支撐、強度或實體配合合格。'
    review['references'] = list(dict.fromkeys(prior['contentReview']['references'] + review['references'] + [REL + '/' + name for name in [
        'coupon-stl-export-record-v001.json', 'export-manifest-v001.json', 'trial-fit-record-v001.json',
        'independent-coupon-export-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json', 'publication-checks-v001.json']] + [UI + '.json']))
    invariant(catalog, baseline)
    downloads = [Path(e['stl_path']) for e in v['exports']] + [RUN / name for name in [
        'coupon-stl-export-record-v001.json', 'export-manifest-v001.json', 'trial-fit-record-v001.json']] + [PROJECT / step['operationRun']['journal']]
    checks = dict(recordedAt=datetime.now(timezone.utc).isoformat(), evidencePassed=True, publicationPending=True,
        browserProofPending=True, images=[http_exact(RUN / r['file']) for r in run['records']], downloads=[http_exact(path) for path in downloads])
    assert catalog_path.read_bytes() == original
    write(catalog_path, catalog)
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(changedSteps=['07-05'], images=len(checks['images']), downloads=len(checks['downloads']), retainedGeometryEvents=len(prior['operationRun']['events']), browserProofPending=True), ensure_ascii=False))


def finalize():
    v, _ = validate()
    baseline = read(RUN / 'publication-baseline-v001.json')
    catalog = read(PROJECT / 'learning/catalog.json')
    progress = read(PROJECT / 'learning/progress.json')
    changed = invariant(catalog, baseline)
    with urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap', timeout=20) as response:
        api = json.load(response)
    assert api['catalog'] == catalog and api['progress'] == progress
    proofs = []
    for role in ['overview', 'comparison', 'conditions', 'history']:
        path = PROJECT / (UI + '-final-' + role + '.jpg')
        width, height = jpeg_size(path.read_bytes())
        assert (width, height) == (304, 848)
        proofs.append(dict(path=path.relative_to(PROJECT).as_posix(), sha256=digest(path), bytes=path.stat().st_size,
                           width=width, height=height, pixelEdits=False, role=role))
    ui = dict(recordedAt=datetime.now(timezone.utc).isoformat(), url='http://127.0.0.1:8766/', browser='ChatGPT in-app browser', lesson='07', step='07-05',
        captureMethod='Browser getScreenshot original JPEG bytes; no pixel modifications', screenshots=proofs,
        sourceFiles=[dict(path=path, sha256=digest(PROJECT / path)) for path in ['learning/catalog.json', 'learning/web/app.js', 'learning/web/app.css']],
        learnerCompletionConfirmed=False, progressRevision=progress['revision'], progressSha256=baseline['progress_sha256'])
    write(PROJECT / (UI + '.json'), ui)
    checks = read(RUN / 'publication-checks-v001.json')
    for item in checks['images']:
        assert digest(PROJECT / item['path']) == item['sha256']
    checks['downloads'] = [http_exact(PROJECT / item['path']) for item in checks['downloads']]
    assert digest(Path(v['source_scene_path'])) == v['source_scene_sha256']
    checks.update(recordedAt=datetime.now(timezone.utc).isoformat(), passed=True, publicationPending=False, browserProofPending=False,
        changedSteps=changed, stepFingerprintsCompared=52, catalogSha256=digest(PROJECT / 'learning/catalog.json'),
        apiCatalogMatchesDisk=True, apiProgressMatchesDisk=True, progressSha256=baseline['progress_sha256'], progressRevision=progress['revision'],
        learnerCompletionConfirmed=False, previousGeometryRunPreserved=True, previousProtectedFilesUnchanged=baseline['protected_prior_files'],
        automatedChecks=dict(path=REL + '/automated-checks-v001.json', sha256=digest(RUN / 'automated-checks-v001.json')),
        browserProof=dict(path=UI + '.json', sha256=digest(PROJECT / (UI + '.json')), screenshots=proofs))
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(passed=True, formalImages=len(checks['images']), downloads=len(checks['downloads']), browserProofs=len(proofs), changedSteps=changed, progressRevision=progress['revision']), ensure_ascii=False))


if __name__ == '__main__':
    finalize() if '--finalize' in sys.argv else publish()
