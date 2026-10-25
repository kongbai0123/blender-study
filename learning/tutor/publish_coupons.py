"""Publish the measured 07-05 geometry draft, preserving learner progress."""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from publish_overhang import PROJECT, digest, read, write, fingerprint
from finalize_overhang import http_exact, jpeg_size

RUN_ID = '2026-10-25-lesson07-coupons-demo-v001'
REL = 'learning/evidence/07/' + RUN_ID
RUN = PROJECT / REL
UI = 'learning/evidence/ui/' + RUN_ID
NAMES = ('A_L19', 'B_L17', 'C_L21')


def fmt(value):
    return '0' if round(value, 3) == 0 else f'{value:.3f}'.rstrip('0').rstrip('.')


def vector(values):
    return ' × '.join(fmt(value) for value in values)


def invariant(catalog, baseline):
    changed = [step['id'] for lesson in catalog['lessons'] for step in lesson['steps']
               if fingerprint(step) != baseline['steps'][step['id']]]
    assert changed == ['07-05'] and len(baseline['steps']) == 52, changed
    assert digest(PROJECT / 'learning/progress.json') == baseline['progress_sha256']
    return changed


def validate():
    import import_run as importer
    run = read(RUN / 'run.json')
    catalog = read(PROJECT / 'learning/catalog.json')
    importer._validate_lesson07_coupons(run, RUN, importer.RUNS[RUN_ID])
    importer._validate_records(run, RUN, importer.RUNS[RUN_ID], {
        step['id']: step for lesson in catalog['lessons'] if lesson['id'] == '07'
        for step in lesson['steps']})
    v = read(RUN / 'verification.json')
    assert v['passed'] and v['reopened'] and v['independent_coupon_meshes']
    assert v['kind'] == 'snapfit_length_coupons_geometry_demo'
    assert not v['source_geometry_modified'] and v['coupon_geometry_modified']
    assert v['per_variant_geometry_modified'] == dict(A_L19=False, B_L17=True, C_L21=True)
    assert read(RUN / 'independent-coupon-audit-v001.json')['passed']
    assert read(RUN / 'automated-checks-v001.json')['passed']
    assert read(RUN / 'ui-technical-review-v001.json')['passed']
    for key in ['improvement_validated', 'material_grade', 'epsilon_allow', 'physical_measurements',
                'fit_results', 'qualified_strength_N', 'qualified_clearance_mm',
                'anchor_clamping_or_fixture', 'full_box_boundary_equivalence']:
        assert v[key] is None, key
    for key in ['improvement_assessed', 'strength_analysis_performed', 'deformation_analysis_performed',
                'fit_qualification', 'slicer_checked', 'printed', 'fit_tested', 'exported_stl',
                'full_box_modified', 'rotation_applied_to_mesh', 'mesh_analysis_overhang_checked']:
        assert v[key] is False, key
    return v, run


def publish():
    v, run = validate()
    baseline = read(RUN / 'publication-baseline-v001.json')
    manifest = read(RUN / 'geometry-manifest-v001.json')
    manifest['publication_audits'] = [dict(path=REL + '/' + name, sha256=digest(RUN / name)) for name in [
        'independent-coupon-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json']]
    write(RUN / 'geometry-manifest-v001.json', manifest)
    catalog_path = PROJECT / 'learning/catalog.json'
    original = catalog_path.read_bytes()
    catalog = json.loads(original)
    step = next(s for lesson in catalog['lessons'] for s in lesson['steps'] if s['id'] == '07-05')
    assert step['operationRun']['id'] == RUN_ID
    step.update(
        title='卡扣臂長對照試片（幾何草案）',
        action='從原SnapTool各自建立獨立試片，只改根平面至承接面的幾何臂長L；A19為原草案參照，B17／C21為調整草案。逐點讀回、候選側放，另存並重開新版本。',
        success='三件獨立網格的幾何L約19／17／21 mm，其餘28點、錨座、寬厚、扣鉤與原生根部保持；各自單殼、Non Manifold0。新v001已另存重開，原Body／Lid與來源版本未改。這是幾何對照，沒有驗證改善、強度或配合合格。',
        guide=[
            dict(mark='1', where='Object Mode · 原SnapTool',
                 do='每件重新選原SnapTool，用Shift+D建立獨立mesh，再命名A_L19、B_L17、C_L21。原Body／Lid及建構工具最後隱藏保留。',
                 see='A是19 mm原草案參照；臂寬6、厚1.6、鉤突出1.2、錨座及原生根部形狀保持。原盒沒有套用這些尺寸變更。'),
            dict(mark='2', where='Edit Mode · Vertex Select · Front Orthographic · X-Ray',
                 do='取消全選，再用B框選原source Z≥11的14個上端頂點；A不移動，B用G Z −2 mm，C用G Z +2 mm。返回Object Mode讀回所有頂點。',
                 see='只動14點，其餘28點不動；承接面原建模Z為11／9／13，幾何L為19／17／21。實拍Local Median約21.529是選取平均局部座標，不是world Z或幾何L。'),
            dict(mark='3', where='Object Mode · N面板 · File > Save As / Open',
                 do='三件各繞Y90°作候選側放，Location分別(0,−12,4.5)、(0,0,4.5)、(0,12,4.5) mm；逐件檢查Non Manifold，再另存新v001並Open重驗。',
                 see='世界XYZ外框約24×4.6×9／22×4.6×9／26×4.6×9 mm。旋轉未Apply，N面板物件軸Dimensions另為9×4.6×24／22／26；最後實拍active C，側欄尺寸屬C。')],
        help='獨立錨座試片沒有重現整盒邊界；夾持、配對件與相對定位基準仍待定，舊Lid不能直接當B／C的既定配對件。幾何L不等於力學有效長度；只有錨座側面接數位Z0，臂與部分根部離床，方向和支撐待切片及實體證據。1e-4 mm只為浮點核對，不是製造公差。本次未匯出STL、切片、列印或試配，未判定改善。',
        evidence=['檔案檢查', '學員回報'])
    captions = {
        'reopened-verified.png': '新v001實際重開：由上到下為C_L21、B_L17、A_L19；active C的N面板9×4.6×26 mm為物件軸尺寸。三件為獨立錨座幾何草案，來源四件隱藏保留，沒有套用至整盒。',
        'B_L17-upper-selection.png': 'B在調整前只框選14個上端頂點（橘色），28個根部／錨座點不動；Local Median是選取平均局部座標。之後實際G Z −2 mm，逐點核對位移。',
        'B_L17-source-frame.png': 'B完成原建模軸G Z −2 mm後：N面板整件高22 mm，包含錨座3 mm；全臂高19 mm、根平面至承接面幾何L17 mm，三者定義分開。'}
    step['figures'] = []
    for suffix, caption in captions.items():
        event = next(e for e in step['operationRun']['events'] if e['figure']['path'].endswith(suffix))
        figure = dict(event['figure'])
        figure['caption'] = '2026-10-25 · 助教獨立 Blender 原始實拍：' + caption
        step['figures'].append(figure)
    step['couponReview'] = dict(
        stage='parameter_comparison_geometry_draft',
        summary='一次只改幾何臂長：A19為原草案參照，B17與C21為未驗證的尺寸調整。三件分開讀值，沒有以長短推定較好、較強或較合適。',
        heldGeometrySummary='固定草案：臂寬6、厚1.6、鉤突出1.2、鉤端高2、錨座9×4.6×3 mm；原生根部弦面及12個miter端面保留。',
        boundarySummary='這是獨立錨座＋臂＋鉤試片。整盒邊界等效性、夾持、配對件及定位基準待定；原Body／Lid未修改。',
        variants=[dict(name=name, geometryLengthMm=fmt(v['candidates'][name]['L_geometry_mm']),
                       armHeightMm=fmt(v['candidates'][name]['total_arm_height_mm']),
                       wholeHeightMm=fmt(v['candidates'][name]['whole_coupon_height_mm']),
                       worldDimensionsLabel=vector(v['candidates'][name]['dimensions_mm'])) for name in NAMES],
        notes=[
            '原建模承接面Z依A／B／C為11／9／13 mm；扣鉤整組平移，原根平面Z−8保持。這些是幾何座標，尚未求力學有效長度或變形。',
            '側放候選只有錨座側面接數位Z0，接觸面積約13.8 mm²；直臂最低約1.5、部分根部最低約0.9 mm，沒有另加底座。這不是床附著或免支撐判定。',
            'Y中心列距12 mm，鄰件Y投影間隔約' + fmt(v['layout']['minimum_y_projection_gap_mm']) + ' mm；未核定列印床幅。',
            'Mesh Analysis沿用顯示已用原生checkbox關閉；本步未重做Overhang、生成支撐或切片。候選Ry90未Apply Rotation。',
            '各件42頂點、41原生polygon、80 loop triangles，一體閉合、Non Manifold0；數值比較門檻不是製造公差或實體合格門檻。',
            '本表依三件各自的實際變體讀值取至小數三位，完整精度與逆回原形的參考數值分欄保存在JSON。',
            '本次沒有STL；新場景及空白試配表另存版本，原07-04 STL與試配表保留不改。'],
        recordPath=REL + '/coupon-record-v001.json', recordSha256=v['coupon_record_sha256'],
        physicalRecordPath=REL + '/trial-fit-record-v001.json')
    step['operationRun']['outputFiles'] = [dict(path=Path(v['scene_path']).relative_to(PROJECT).as_posix(),
        sha256=v['scene_sha256'], bytes=v['scene_bytes'], sourcePath=Path(v['source_scene_path']).relative_to(PROJECT).as_posix(),
        sourceSha256=v['source_scene_sha256'], dimensionsLabel='獨立臂長對照草案 A19／B17／C21 mm；不是整盒修正版或已驗證改善')]
    step['contentReview']['summary'] = '已核對固定來源、每件獨立mesh、14個上端點／28點保持、原生根部、實際長度與候選世界外框、錨座接床／離床部位、另存重開與獨立audit。新B／C確有尺寸修改，來源四件原形與matrix保持；沒有整盒／力學或改善合格結論。'
    refs = step['contentReview']['references']
    for path in ['learning/plans/07-05-coupon-length-draft-v001.json'] + [REL + '/' + name for name in [
        'coupon-record-v001.json', 'geometry-manifest-v001.json', 'trial-fit-record-v001.json',
        'independent-coupon-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json',
        'publication-checks-v001.json']] + [UI + '.json']:
        if path not in refs:
            refs.append(path)
    invariant(catalog, baseline)
    downloads = [Path(v['scene_path'])] + [RUN / name for name in [
        'coupon-record-v001.json', 'geometry-manifest-v001.json', 'trial-fit-record-v001.json']] + [PROJECT / step['operationRun']['journal']]
    checks = dict(recordedAt=datetime.now(timezone.utc).isoformat(), evidencePassed=True,
        publicationPending=True, browserProofPending=True,
        images=[http_exact(RUN / r['file']) for r in run['records']], downloads=[http_exact(path) for path in downloads])
    assert catalog_path.read_bytes() == original
    write(catalog_path, catalog)
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(changedSteps=['07-05'], images=len(checks['images']), downloads=len(checks['downloads']), browserProofPending=True), ensure_ascii=False))


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
    for role in ['overview', 'comparison', 'conditions']:
        path = PROJECT / (UI + '-final-' + role + '.jpg')
        width, height = jpeg_size(path.read_bytes())
        assert (width, height) == (304, 848)
        proofs.append(dict(path=path.relative_to(PROJECT).as_posix(), sha256=digest(path), bytes=path.stat().st_size,
                           width=width, height=height, pixelEdits=False, role=role))
    ui = dict(recordedAt=datetime.now(timezone.utc).isoformat(), url='http://127.0.0.1:8766/',
        browser='ChatGPT in-app browser', lesson='07', step='07-05',
        captureMethod='Browser getScreenshot original JPEG bytes; no pixel modifications', screenshots=proofs,
        sourceFiles=[dict(path=path, sha256=digest(PROJECT / path)) for path in ['learning/catalog.json', 'learning/web/app.js', 'learning/web/app.css']],
        learnerCompletionConfirmed=False, progressRevision=progress['revision'], progressSha256=baseline['progress_sha256'])
    write(PROJECT / (UI + '.json'), ui)
    checks = read(RUN / 'publication-checks-v001.json')
    for item in checks['images']:
        assert digest(PROJECT / item['path']) == item['sha256']
    checks['downloads'] = [http_exact(PROJECT / item['path']) for item in checks['downloads']]
    for path, sha in [(v['source_scene_path'], v['source_scene_sha256']), (v['scene_path'], v['scene_sha256']),
                      (v['source_tool_mesh_path'], v['source_tool_mesh_sha256']), (v['continuity_reference_path'], v['continuity_reference_sha256'])]:
        assert digest(Path(path)) == sha
    prior = read(Path(v['continuity_reference_path']))
    history = []
    for entry in prior['exports']:
        path = Path(entry['stl_path'])
        assert digest(path) == entry['stl_sha256'] and path.stat().st_size == entry['stl_bytes']
        history.append(dict(path=path.relative_to(PROJECT).as_posix(), sha256=digest(path), unchanged=True))
    old_trial = Path(v['continuity_reference_path']).parent / 'trial-fit-record-v001.json'
    assert digest(old_trial) == '3064067712844dca829fdcd9a58e68223dba5c63b3ee66b1cb8825db841e2670'
    history.append(dict(path=old_trial.relative_to(PROJECT).as_posix(), sha256=digest(old_trial), unchanged=True))
    checks.update(recordedAt=datetime.now(timezone.utc).isoformat(), passed=True,
        publicationPending=False, browserProofPending=False, changedSteps=changed, stepFingerprintsCompared=52,
        catalogSha256=digest(PROJECT / 'learning/catalog.json'), apiCatalogMatchesDisk=True, apiProgressMatchesDisk=True,
        progressSha256=baseline['progress_sha256'], progressRevision=progress['revision'], learnerCompletionConfirmed=False,
        sourceSceneUnchanged=True, newSceneReopened=True, previousExportFiles=history,
        automatedChecks=dict(path=REL + '/automated-checks-v001.json', sha256=digest(RUN / 'automated-checks-v001.json')),
        browserProof=dict(path=UI + '.json', sha256=digest(PROJECT / (UI + '.json')), screenshots=proofs))
    assert digest(PROJECT / 'learning/progress.json') == baseline['progress_sha256']
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(passed=True, formalImages=len(checks['images']), downloads=len(checks['downloads']),
        browserProofs=len(proofs), changedSteps=changed, progressRevision=progress['revision'], sceneSha256=v['scene_sha256']), ensure_ascii=False))


if __name__ == '__main__':
    finalize() if '--finalize' in sys.argv else publish()
