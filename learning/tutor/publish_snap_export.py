"""Publish the checked 07-04 digital-export example without learner confirmation."""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from publish_overhang import PROJECT, digest, read, write, fingerprint
from finalize_overhang import http_exact, jpeg_size

RUN_ID='2026-10-25-lesson07-snap-export-demo-v001'
REL='learning/evidence/07/'+RUN_ID
RUN=PROJECT/REL
UI='learning/evidence/ui/'+RUN_ID

def fmt(value):
    return '0' if round(value,3)==0 else f'{value:.3f}'.rstrip('0').rstrip('.')

def vector(values):
    return ' × '.join(fmt(v) for v in values)

def invariant(catalog,baseline):
    changed=[s['id'] for l in catalog['lessons'] for s in l['steps'] if fingerprint(s)!=baseline['steps'][s['id']]]
    assert changed==['07-04'] and len(baseline['steps'])==52,changed
    assert digest(PROJECT/'learning/progress.json')==baseline['progress_sha256']
    return changed

def publish():
    baseline=read(RUN/'publication-baseline-v001.json')
    v=read(RUN/'verification.json')
    assert v['passed'] and v['kind']=='snapfit_stl_exports' and v['reimport_verified'] and v['exported_stl']
    assert not any(v[k] for k in ['saved_new_scene','geometry_modified','rotation_applied_to_mesh','strength_analysis_performed','fit_qualification','slicer_checked','printed','fit_tested'])
    assert all(v[k] is None for k in ['material_grade','epsilon_allow','physical_measurements','fit_results','support_required','final_print_orientation_approved','qualified_strength_N','qualified_clearance_mm'])
    assert read(RUN/'independent-stl-audit-v001.json')['passed']
    assert {e['kind'] for e in v['exports']}=={'body','lid'}
    manifest=read(RUN/'export-manifest-v001.json')
    manifest['publication_audits']=[dict(path=REL+'/'+name,sha256=digest(RUN/name)) for name in ['independent-stl-audit-v001.json','automated-checks-v001.json']]
    write(RUN/'export-manifest-v001.json',manifest)
    catalog_path=PROJECT/'learning/catalog.json'
    original=catalog_path.read_bytes()
    catalog=json.loads(original)
    step=next(s for l in catalog['lessons'] for s in l['steps'] if s['id']=='07-04')
    assert step['operationRun']['id']==RUN_ID
    step.update(title='卡扣 STL 匯出與數位核對',
        action='沿用07-03既有候選方向，只匯出Body與Lid各一份STL；解析實檔，再在空白毫米場景實際重匯入核對。這次完成數位準備部分，沒有改臂長／厚度或列印參數試片。',
        success='兩份STL實檔與實際重匯入的世界外框、完整表面與卡扣／凸緣幾何在數值門檻內與來源一致；兩件均一體閉合、Non Manifold0。來源、副本及方向紀錄hash未改，不另存blend。方向與支撐仍為候選，材料及允許應變待定，列印／試配留空，沒有強度或配合合格判定。',
        guide=[
            dict(mark='1',where='07-03候選方向副本 · Object Mode',do='每件重開同hash副本；分別只選Body或Lid，隱藏另一件與建構工具，保留旋轉與世界座標。',see='來源Body N面板仍60×44.5×30mm／Y旋轉90°；世界外框約30×44.5×60mm。沒有Apply Rotation或重新建模。'),
            dict(mark='2',where='File > Export > STL (.stl)',do='確認Selection Only、Scale1、Scene Unit關、Binary、Y Forward／Z Up；各匯出新的v001檔。',see='兩個成品各一檔，沒有建構工具。STL沒有單位標記，本次座標以mm解讀；匯出前原生選項與匯出後新檔讀值一併記錄。'),
            dict(mark='3',where='空白毫米場景 · Import STL',do='在Metric／Millimeters／Unit Scale0.001的空場景，逐件實際重匯入，核對Item尺寸、world外框及Select Non Manifold。',see='重匯入後旋轉0／Scale1，Body約30×44.5×60、Lid約60×46×7mm；兩件保持約35mm分隔，各自最低Z≈0。這是候選擺位的數位一致性，尚未切片或試配。')],
        help='本次只有既有單一草案的Body與Lid，沒有印2–3種臂長或厚度試片，也沒有量測手感、裝拆力、斷裂或循環壽命。約1e-6mm負Z與1e-4mm核對門檻只屬浮點重建，不能當製造公差或落床附著證據。原卡扣間距仍為試驗幾何；試片比較、列印、試扣及修正留待實體證據。',
        evidence=['檔案檢查','學員回報'])
    events=step['operationRun']['events']
    captions={
        'body-reimport-dimensions.png':'實際重匯入Body_STL：Item Dimensions約30×44.5×60mm、Rotation0／Scale1；這是保留候選世界頂點後的讀值，與來源N面板60×44.5×30mm定義不同。',
        'lid-reimport-dimensions.png':'實際重匯入Lid_STL：Item Dimensions約60×46×7mm、Rotation0／Scale1，保留翻面候選與裙／凸緣幾何。',
        'body-export-options.png':'原生STL匯出視窗：只選Body、Selection Only開、Scale1、Scene Unit關、Binary及Y Forward／Z Up。確認選項後匯出新檔，兩份STL的版本與來源可在下方核對。'}
    step['figures']=[]
    for suffix,caption in captions.items():
        event=next(e for e in events if e['figure']['path'].endswith(suffix))
        figure=dict(event['figure'])
        figure['caption']='2026-10-25 · 助教獨立 Blender 原始實拍：'+caption
        step['figures'].append(figure)
    comparisons=[]
    for entry in sorted(v['exports'],key=lambda e:e['kind']):
        kind=entry['kind']
        imported=read(RUN/('reimport_'+kind+'_mesh.json'))
        bounds=entry['stl_bounds_mm']
        metrics=[
            ('來源N面板尺寸（物件軸mm）',vector(entry['source_item_dimensions_mm'])),
            ('來源世界XYZ外框（mm）',vector(v['source_'+kind]['dimensions_mm'])),
            ('STL XYZ外框（mm解讀）',vector(entry['stl_dimensions_mm'])),
            ('重匯入Item XYZ（mm）',vector(imported['cad_metadata']['object_axis_dimensions_mm'])),
            ('STL世界Z範圍（mm）',fmt(bounds['min'][2])+'～'+fmt(bounds['max'][2])),
            ('STL三角形／殼／非流形邊',f"{entry['stl_triangles']}／{entry['stl_connected_shells']}／{entry['stl_non_manifold_edges']}"),
            ('STL數位體積（mm³）',fmt(entry['stl_volume_mm3']))]
        comparisons.append(dict(title='盒體／卡扣 Body' if kind=='body' else '上蓋／凸緣 Lid',metrics=[dict(label=k,value=value) for k,value in metrics]))
    step['stlReview']=dict(stage='digital_stl_comparison_only',summary='沿用07-03側放盒體與翻面上蓋，各自單件匯出，再以實際重匯入核對完整幾何與候選世界位置；未改成組裝姿態。',comparisons=comparisons,recordPath=REL+'/export-manifest-v001.json',recordSha256=digest(RUN/'export-manifest-v001.json'),physicalRecordPath=REL+'/trial-fit-record-v001.json')
    source_rel=Path(v['source_scene_path']).relative_to(PROJECT).as_posix()
    step['operationRun']['outputFiles']=[dict(path=Path(e['stl_path']).relative_to(PROJECT).as_posix(),sha256=e['stl_sha256'],bytes=e['stl_bytes'],dimensionsMm=e['stl_dimensions_mm'],sourcePath=source_rel,sourceSha256=v['source_scene_sha256']) for e in v['exports']]
    review=step['contentReview']
    review['summary']='已核對07-03候選來源、單件選取與隱藏工具、原生匯出前選項、兩份STL實檔、完整有向表面／逆姿態卡扣幾何及空mm場景實際重匯入。只完成既有單一草案的數位匯出；方向、支撐、材料與實體合格條件仍待定。'
    for path in [REL+'/'+name for name in ['stl-export-record-v001.json','export-manifest-v001.json','trial-fit-record-v001.json','independent-stl-audit-v001.json','automated-checks-v001.json','publication-checks-v001.json']]+[UI+'.json']:
        if path not in review['references']:review['references'].append(path)
    invariant(catalog,baseline)
    checks=dict(recordedAt=datetime.now(timezone.utc).isoformat(),evidencePassed=True,publicationPending=True,browserProofPending=True,images=[http_exact(RUN/r['file']) for r in read(RUN/'run.json')['records']],downloads=[])
    downloads=[Path(e['stl_path']) for e in v['exports']]+[RUN/name for name in ['stl-export-record-v001.json','export-manifest-v001.json','trial-fit-record-v001.json']]+[PROJECT/step['operationRun']['journal']]
    checks['downloads']=[http_exact(path) for path in downloads]
    assert catalog_path.read_bytes()==original
    write(catalog_path,catalog)
    write(RUN/'publication-checks-v001.json',checks)
    print(json.dumps(dict(changedSteps=['07-04'],images=len(checks['images']),downloads=len(checks['downloads']),browserProofPending=True),ensure_ascii=False))

def finalize():
    import import_run as importer
    baseline=read(RUN/'publication-baseline-v001.json')
    catalog=read(PROJECT/'learning/catalog.json')
    progress=read(PROJECT/'learning/progress.json')
    run=read(RUN/'run.json')
    importer._validate_lesson07_snap_export(run,RUN,importer.RUNS[RUN_ID])
    importer._validate_records(run,RUN,importer.RUNS[RUN_ID],{s['id']:s for l in catalog['lessons'] if l['id']=='07' for s in l['steps']})
    changed=invariant(catalog,baseline)
    with urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap',timeout=20) as response:api=json.load(response)
    assert api['catalog']==catalog and api['progress']==progress
    proofs=[]
    for role in ['overview','comparison','conditions']:
        path=PROJECT/(UI+'-final-'+role+'.jpg')
        w,h=jpeg_size(path.read_bytes())
        assert (w,h)==(304,848)
        proofs.append(dict(path=path.relative_to(PROJECT).as_posix(),sha256=digest(path),bytes=path.stat().st_size,width=w,height=h,pixelEdits=False,role=role))
    ui=dict(recordedAt=datetime.now(timezone.utc).isoformat(),url='http://127.0.0.1:8766/',browser='ChatGPT in-app browser',lesson='07',step='07-04',captureMethod='Browser getScreenshot original JPEG bytes; no pixel modifications',screenshots=proofs,sourceFiles=[dict(path=path,sha256=digest(PROJECT/path)) for path in ['learning/catalog.json','learning/web/app.js','learning/web/app.css']],learnerCompletionConfirmed=False,progressRevision=progress['revision'],progressSha256=baseline['progress_sha256'])
    write(PROJECT/(UI+'.json'),ui)
    checks=read(RUN/'publication-checks-v001.json')
    for item in checks['images']:assert digest(PROJECT/item['path'])==item['sha256']
    checks['downloads']=[http_exact(PROJECT/item['path']) for item in checks['downloads']]
    checks.update(recordedAt=datetime.now(timezone.utc).isoformat(),passed=True,publicationPending=False,browserProofPending=False,changedSteps=changed,stepFingerprintsCompared=52,catalogSha256=digest(PROJECT/'learning/catalog.json'),apiCatalogMatchesDisk=True,apiProgressMatchesDisk=True,progressSha256=baseline['progress_sha256'],progressRevision=progress['revision'],learnerCompletionConfirmed=False,browserProof=dict(path=UI+'.json',sha256=digest(PROJECT/(UI+'.json')),screenshots=proofs))
    v=read(RUN/'verification.json')
    assert digest(Path(v['source_scene_path']))==v['source_scene_sha256']
    assert digest(PROJECT/'learning/progress.json')==baseline['progress_sha256']
    write(RUN/'publication-checks-v001.json',checks)
    print(json.dumps(dict(passed=True,formalImages=len(checks['images']),downloads=len(checks['downloads']),browserProofs=len(proofs),changedSteps=changed,progressRevision=progress['revision']),ensure_ascii=False))

if __name__=='__main__':
    finalize() if '--finalize' in sys.argv else publish()
