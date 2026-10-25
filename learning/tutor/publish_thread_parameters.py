"""Publish the 08-01 reference inspection and pending thread parameter plan."""
import copy
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from publish_overhang import PROJECT, digest, read, write, fingerprint
from finalize_overhang import http_exact, jpeg_size

RUN_ID = '2026-10-25-lesson08-parameters-demo-v001'
REL = 'learning/evidence/08/' + RUN_ID
RUN = PROJECT / REL
UI = 'learning/evidence/ui/' + RUN_ID
PLAN = PROJECT / 'learning/plans/08-01-thread-parameters-v001.json'
FACTS = PROJECT / 'sources/engineering/thread-source-facts-v001.json'


def corrected_next_step(baseline):
    step = copy.deepcopy(next(s for s in baseline['prior_thread_lesson']['steps'] if s['id'] == '08-02'))
    step.update(
        action='若選列印螺紋路線，先定牙型、軸向、螺距P、線數n與導程l，再建立Screw幾何草案。Angle=360°且Object Screw關時Screw對應導程；只有單線時才等於螺距。間隙須另訂試驗草案，不能沿用第五單元為合格值。',
        success='後續實作時能核對牙型、P／n／l、Angle／Screw／Iterations、分段與試驗間隙的定義及實際讀值；本步目前尚未建模或實拍。',
        guide=[
            dict(mark='1', where='牙型與規格草案', do='先選路線、用途、牙型與內外徑，分開記螺距P、線數n、導程l=nP；牙側、軸向及徑向讓位各自定義。', see='參數仍為草案；第五單元未列印／試配，沒有可轉用的合格間隙。'),
            dict(mark='2', where='Screw 修改器（待實作）', do='核對Angle／軸／Object Screw，再填每段軸移與Iterations。整圈單線才可用Screw=P；Iterations不是線數。', see='分開核對掃掠圈數、軸向行程、整件外框及有效嚙合；Viewport與Render分段也要各自讀回。')],
        help='螺距、牙型、端部封口與間隙待選；0.4 mm噴嘴不決定這些值。先核對幾何草案，再另做切片與試印，不能由螺旋外觀或Non Manifold0推論配合合格。')
    step['contentReview'] = dict(status='source_definition_reviewed_only',
        summary='僅補正待實作內容的Screw／導程／螺距條件，以及第五單元沒有合格間隙可沿用；依官方文件與已安裝build實作核對定義，未執行08-02建模或取得其實拍。',
        references=step['contentReview']['references'] + ['sources/engineering/thread-source-facts-v001.json', 'learning/plans/08-01-thread-parameters-v001.json'])
    return step


def invariant(catalog, baseline):
    changed = [s['id'] for lesson in catalog['lessons'] for s in lesson['steps'] if fingerprint(s) != baseline['steps'][s['id']]]
    assert changed == ['08-01', '08-02'] and len(baseline['steps']) == 52, changed
    assert digest(PROJECT / 'learning/progress.json') == baseline['progress_sha256']
    source = PROJECT / baseline['source']['path']
    assert digest(source) == baseline['source']['sha256'] and source.stat().st_size == baseline['source']['bytes']
    lesson = next(l for l in catalog['lessons'] if l['id'] == '08')
    assert next(s for s in lesson['steps'] if s['id'] == '08-02') == corrected_next_step(baseline)
    return changed


def validate():
    import import_run as importer
    run = read(RUN / 'run.json')
    catalog = read(PROJECT / 'learning/catalog.json')
    importer._validate_lesson08_parameters(run, RUN, importer.RUNS[RUN_ID])
    importer._validate_records(run, RUN, importer.RUNS[RUN_ID], {s['id']: s for l in catalog['lessons'] if l['id'] == '08' for s in l['steps']})
    v = read(RUN / 'verification.json')
    assert v['passed'] and v['kind'] == 'thread_parameter_reference' and v['reopened']
    assert v['source_body_geometry_unchanged'] and v['scene_role'] == 'unmodified_box_thread_reference'
    for key in ['thread_modeled', 'boss_modeled', 'pilot_hole_modeled', 'counterpart_modeled', 'modifier_created',
                'screw_modifier_created', 'geometry_modified', 'calculations_performed', 'strength_analysis_performed',
                'fit_qualification', 'printed', 'fit_tested', 'slicer_checked', 'exported', 'exported_stl']:
        assert v[key] is False, key
    for key in ['thread_route_selected', 'thread_standard_selected', 'physical_measurements', 'fit_results',
                'material_grade', 'qualified_strength_N', 'qualified_clearance_mm', 'qualified_torque_Nm']:
        assert v[key] is None, key
    for name in ['independent-thread-reference-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json']:
        assert read(RUN / name)['passed'], name
    return v, run


def publish():
    v, run = validate()
    baseline = read(RUN / 'publication-baseline-v001.json')
    plan, facts = read(PLAN), read(FACTS)
    manifest = read(RUN / 'parameter-manifest-v001.json')
    manifest['publication_audits'] = [dict(path=REL + '/' + name, sha256=digest(RUN / name)) for name in [
        'independent-thread-reference-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json']]
    write(RUN / 'parameter-manifest-v001.json', manifest)
    catalog_path = PROJECT / 'learning/catalog.json'
    original = catalog_path.read_bytes()
    catalog = json.loads(original)
    lesson = next(l for l in catalog['lessons'] if l['id'] == '08')
    step = next(s for s in lesson['steps'] if s['id'] == '08-01')
    assert step['operationRun']['id'] == RUN_ID
    step.update(title='螺紋規格與建模參數',
        action='沿用原04小盒建立螺紋參照分支，實際核對原盒尺寸、盒口與底面，另存重開新v001；分開整理尚未選定的路線、24個尺寸／配合草案欄位及Screw參數映射。',
        success='原盒60×40×30、內腔56×36×28、壁底2 mm未改，三個面選取與Non Manifold0已有實拍讀值；新參照場景另存重開並綁定參數紀錄。螺紋路線、標準、尺寸、間隙及材料仍待定，沒有建立螺紋／柱／導孔、計算、STL或實體合格判定。',
        guide=[
            dict(mark='1', where='原04盒同hash副本 · Object Mode', do='只用原小盒作參照，隱藏Camera／Light，命名Body_Reference並核對Item尺寸、Scale與毫米單位。', see='外形60×40×30、內腔56×36×28、壁與底2 mm；沒有繼承卡扣、定位柱或燕尾候選幾何。'),
            dict(mark='2', where='Edit Mode · Face Select', do='依實際視角逐次選盒口前環面、內底及外底，讀回所選面的世界座標，再檢查Select Non Manifold。', see='盒口前壁Y−20～−18、頂Z15；內底Z−13、外底Z−15，差2 mm。這些是盒體實測，並不是螺紋、柱或孔的設計值。'),
            dict(mark='3', where='File > Save As / Open · 參數表', do='另存u08_thread_reference_v001.blend並Open重驗；把螺距、導程、線數、各徑、牙型、端部與間隙定義分欄記錄。', see='新場景只有未改原盒；24個草案欄位未填數值、修改器未配置，材料與列印／試鎖結果留空。')],
        help='路線未選前不指定M規格或硬體孔徑；矩形盒也不是現成旋蓋。Angle=360°且Object Screw關、單線時才可寫Screw=螺距；Iterations不是線數。第五單元沒有可沿用的合格間隙。所有後續幾何、切片及實體驗證須各自留證。',
        evidence=['檔案檢查', '學員回報'])
    step['threadPlan'] = dict(stage=plan['stage'], referenceBoxSummary=plan['reference_box_summary'],
        routeSummary='路線待你選擇；「自訂列印螺紋」僅為助教優先候選，尚未成為你的決定，沒有選定標準或硬體型號。',
        routes=plan['route']['options'], parameters=plan['draft_parameters'], relationships=plan['blender_mapping']['relationships'],
        conditions=plan['conditions'], sources=facts['sources'], recordPath=REL + '/parameter-record-v001.json',
        recordSha256=v['parameter_record_sha256'], physicalRecordPath=REL + '/trial-fit-record-v001.json')
    captions = {
        'reference-overview.png': '原04盒的螺紋參照分支：Item Dimensions60×40×30 mm，只有原盒形狀；此畫面沒有螺紋、螺絲柱或配對件。',
        'inner-floor.png': '實際選內底面並讀回世界Z−13 mm，內腔基準56×36；這是原盒讀值，不是導孔或螺紋尺寸。',
        'outer-floor.png': '實際選外底面並讀回世界Z−15 mm，與內底差2 mm；原盒沒有為螺紋加工或修改。'}
    step['figures'] = []
    for suffix, caption in captions.items():
        event = next(e for e in step['operationRun']['events'] if e['figure']['path'].endswith(suffix))
        figure = dict(event['figure'])
        figure['caption'] = '2026-10-25 · 助教獨立 Blender 原始實拍：' + caption
        step['figures'].append(figure)
    step['operationRun']['outputFiles'] = [dict(path=Path(v['scene_path']).relative_to(PROJECT).as_posix(), sha256=v['scene_sha256'], bytes=v['scene_bytes'],
        dimensionsLabel='原盒60 × 40 × 30 mm參照；尚未建牙或柱', sourcePath=Path(v['source_scene_path']).relative_to(PROJECT).as_posix(), sourceSha256=v['source_scene_sha256'])]
    review = step['contentReview']
    review['summary'] = '已核對原04盒、獨立UI面選取與完整網格、另存重開、24個未實作草案欄位及官方Screw／螺紋定義。實測盒體與尚未配置的參數分開，沒有指定標準尺寸、硬體孔徑或合格間隙；未建牙、列印或試鎖。'
    review['references'] = list(dict.fromkeys(review['references'] + ['learning/plans/08-01-thread-parameters-v001.json',
        'sources/engineering/thread-source-facts-v001.json'] + [REL + '/' + name for name in [
        'parameter-record-v001.json', 'parameter-manifest-v001.json', 'trial-fit-record-v001.json',
        'independent-thread-reference-audit-v001.json', 'automated-checks-v001.json', 'ui-technical-review-v001.json', 'publication-checks-v001.json']] + [UI + '.json']))
    lesson['steps'][1] = corrected_next_step(baseline)
    invariant(catalog, baseline)
    downloads = [Path(v['scene_path'])] + [RUN / name for name in ['parameter-record-v001.json', 'parameter-manifest-v001.json', 'trial-fit-record-v001.json']] + [PROJECT / step['operationRun']['journal']]
    checks = dict(recordedAt=datetime.now(timezone.utc).isoformat(), evidencePassed=True, publicationPending=True, browserProofPending=True,
        images=[http_exact(RUN / item['file']) for item in run['records']], downloads=[http_exact(path) for path in downloads])
    assert catalog_path.read_bytes() == original
    write(catalog_path, catalog)
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(changedSteps=['08-01', '08-02'], images=len(checks['images']), downloads=len(checks['downloads']), draftParameters=24, browserProofPending=True), ensure_ascii=False))


def finalize():
    v, _ = validate()
    baseline = read(RUN / 'publication-baseline-v001.json')
    catalog, progress = read(PROJECT / 'learning/catalog.json'), read(PROJECT / 'learning/progress.json')
    changed = invariant(catalog, baseline)
    with urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap', timeout=20) as response:
        api = json.load(response)
    assert api['catalog'] == catalog and api['progress'] == progress
    proofs = []
    for role in ['overview', 'parameters', 'conditions', 'mapping']:
        path = PROJECT / (UI + '-final-' + role + '.jpg')
        width, height = jpeg_size(path.read_bytes())
        assert (width, height) == (304, 848)
        proofs.append(dict(path=path.relative_to(PROJECT).as_posix(), sha256=digest(path), bytes=path.stat().st_size, width=width, height=height, pixelEdits=False, role=role))
    ui = dict(recordedAt=datetime.now(timezone.utc).isoformat(), url='http://127.0.0.1:8766/', browser='ChatGPT in-app browser', lesson='08', step='08-01',
        captureMethod='Browser getScreenshot original JPEG bytes; no pixel modifications', screenshots=proofs,
        sourceFiles=[dict(path=name, sha256=digest(PROJECT / name)) for name in ['learning/catalog.json', 'learning/web/app.js', 'learning/web/app.css']],
        learnerCompletionConfirmed=False, progressRevision=progress['revision'], progressSha256=baseline['progress_sha256'])
    write(PROJECT / (UI + '.json'), ui)
    checks = read(RUN / 'publication-checks-v001.json')
    for item in checks['images']:
        assert digest(PROJECT / item['path']) == item['sha256']
    checks['downloads'] = [http_exact(PROJECT / item['path']) for item in checks['downloads']]
    assert digest(Path(v['source_scene_path'])) == v['source_scene_sha256'] and digest(Path(v['scene_path'])) == v['scene_sha256']
    checks.update(recordedAt=datetime.now(timezone.utc).isoformat(), passed=True, publicationPending=False, browserProofPending=False,
        changedSteps=changed, stepFingerprintsCompared=52, catalogSha256=digest(PROJECT / 'learning/catalog.json'), apiCatalogMatchesDisk=True,
        apiProgressMatchesDisk=True, progressSha256=baseline['progress_sha256'], progressRevision=progress['revision'], learnerCompletionConfirmed=False,
        referenceSceneReopened=True, originalBoxUnchanged=True, threadModeled=False, unconfiguredDraftParameters=24,
        automatedChecks=dict(path=REL + '/automated-checks-v001.json', sha256=digest(RUN / 'automated-checks-v001.json')),
        browserProof=dict(path=UI + '.json', sha256=digest(PROJECT / (UI + '.json')), screenshots=proofs))
    write(RUN / 'publication-checks-v001.json', checks)
    print(json.dumps(dict(passed=True, formalImages=len(checks['images']), downloads=len(checks['downloads']), browserProofs=len(proofs), changedSteps=changed, progressRevision=progress['revision']), ensure_ascii=False))


if __name__ == '__main__':
    finalize() if '--finalize' in sys.argv else publish()
