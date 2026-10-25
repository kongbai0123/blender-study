"""Publish only the verified 07-03 teacher example; never write learner progress."""
import copy
import hashlib
import json
import os
import struct
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
BASELINE = PROJECT/'learning/evidence/07/2026-10-25-lesson07-overhang-publication-baseline-v001.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    temporary = path.with_name(path.name+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temporary,path)

def fingerprint(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def publish(run_id):
    run_dir=PROJECT/'learning/evidence/07'/run_id
    baseline=read(BASELINE)
    assert digest(PROJECT/'learning/progress.json')==baseline['progress_sha256']
    verification=read(run_dir/'verification.json')
    audit=read(run_dir/'independent-audit-v001.json')
    assert verification['passed'] and audit['passed']
    assert verification['kind']=='snapfit_print_orientation_demo'
    assert verification['reopened'] and verification['rigid_geometry_only']
    assert not any(verification[k] for k in ['geometry_modified','rotation_applied_to_mesh','strength_analysis_performed','fit_qualification','exported_stl','slicer_checked','printed','fit_tested'])
    assert all(verification[k] is None for k in ['material_grade','epsilon_allow','physical_measurements','fit_results','support_required','final_print_orientation_approved','qualified_strength_N','qualified_clearance_mm'])
    catalog_path=PROJECT/'learning/catalog.json'
    original=catalog_path.read_bytes()
    catalog=json.loads(original)
    step=next(s for l in catalog['lessons'] for s in l['steps'] if s['id']=='07-03')
    assert step['operationRun']['id']==run_id
    relative=run_dir.relative_to(PROJECT).as_posix()
    events=step['operationRun']['events']
    def figure(suffix,caption):
        event=next(e for e in events if e['figure']['path'].endswith(suffix))
        result=copy.deepcopy(event['figure'])
        result['caption']='2026-10-25 · 助教獨立 Blender 原始實拍：'+caption
        return result
    step.update(
        title='列印方向與 Overhang 檢查',
        action='只旋轉及平移07-02既有卡扣幾何，比較盒體原向／側放及上蓋原向／翻面。用原生 Overhang 實拍、讀回設定，再分開床面接觸區與離床朝下面。',
        success='四姿態均保存原始實拍與世界座標讀值；兩件候選在Z0、Scale1，沒有改形狀或Apply Rotation，另存並重開通過。原生Overhang設定與另算polygon統計可追溯；材料、允許應變、最終方向、支撐、列印及試配結果仍待定，沒有強度或配合合格判定。',
        guide=[
            dict(mark='1',where='07-02草案副本 · Object Mode',
                 do='比較四種落床姿態：Body原向與繞Y90°側放；Lid原向與繞X180°翻面。只用R／G操作，保留Scale1，不套用旋轉。',
                 see='原盒核心與卡扣形狀保持；側放後臂長及名義彎曲方向都平行世界XY層平面。這只是方向關係，沒有證明層間強度。'),
            dict(mark='2',where='Edit Mode > Mesh Edit Mode Overlays > Mesh Analysis',
                 do='Solid、X-Ray關閉；啟用Mesh Analysis，核對Overhang／−Z／Minimum0°／Maximum45°，再轉視角觀察真實色帶。',
                 see='朝下的床面接觸面也可能顯紅；側放盒體的腔內頂壁及卡扣下方仍有朝下面。顯示角度不是列印可接受角度。'),
            dict(mark='3',where='方向比較表 · 另存與Open重開',
                 do='對照床接觸、非床接觸朝下面的polygon數與面積；檢查翻面上蓋的高處凸緣。候選各自落床、分開35mm後另存新版本並重開。',
                 see='面積是實網格另算，不能單獨決定支撐或橋接。最終擺向、支撐可移除性、附著與切片條件保留待核對。')],
        help='以世界Z0作數位床面基準，未假設實際機型床幅。原生Overhang只按面法線與有向軸夾角顯色，沒有平台、前層承托或支撐生成判斷。0～45°是顯示範圍；1e-4mm／度只處理浮點與邊界敏感性，不是製造公差。材料及允許應變仍待定，未切片、列印或試配。')
    step['figures']=[
        figure('body_candidate-analysis.png','側放Body：紅色可同時出現在落床外壁、腔內頂壁及卡扣下方；圖上顏色只描述本次角度範圍。'),
        figure('body_candidate-controls.png','原生Edit Mode Mesh Analysis控制項：Overhang、Minimum0°、Maximum45°、−Z；Solid、X-Ray關閉，沒有套用物件旋轉。')]
    lid_extra=[e for e in events if e['figure']['path'].endswith('lid-candidate-ledge.png')]
    step['figures'].append(figure('lid-candidate-ledge.png' if lid_extra else 'lid-candidate-profile.png',
        '翻面Lid的蓋板落在Z0，高處裙／凸緣仍在床面上方。實際色帶、側視高度與逐面讀值一起看；未判斷是否需要支撐。'))
    def number(value):
        if round(value,3)==0:
            return '0'
        return f'{value:.3f}'.rstrip('0').rstrip('.') or '0'
    def vector(values):
        return ' × '.join(number(v) for v in values)
    def group(result,key):
        g=result['derived_polygon_statistics']['summary'][key]
        return f"{g['count']} 面／{number(g['area_mm2'])} mm²"
    comparisons=[]
    for part,title,description in [
        ('body','盒體／卡扣：原向與側放','候選繞世界Y90°。臂長與名義彎曲方向平行XY層平面，但腔內頂壁及卡扣下方出現離床朝下面；側放只是比較候選。'),
        ('lid','上蓋：原向與翻面','候選繞世界X180°，蓋板外側大片面落床；高處凸緣仍有朝下面。不能由總面積較少推定免支撐。')]:
        base,candidate=[verification['poses'][part+'_'+pose] for pose in ('baseline','candidate')]
        rows=[]
        def row(label,fn):
            rows.append(dict(label=label,baseline=fn(base),candidate=fn(candidate)))
        row('世界外框 XYZ（mm）',lambda r:vector(r['dimensions_mm']))
        row('世界Z範圍（mm）',lambda r:'～'.join(number(r['bounds_mm'][k][2]) for k in ('min','max')))
        row('床接觸區（整面Z≈0）',lambda r:group(r,'bed_contact'))
        row('非床接觸的朝下面',lambda r:group(r,'downward_not_bed_contact'))
        row('其中整面離床的朝下面',lambda r:group(r,'fully_elevated_downward'))
        row('另算顯色範圍內非床接觸面',lambda r:group(r,'derived_native_visible_not_bed_contact'))
        row('單殼／Non Manifold邊',lambda r:f"{r['connected_shells']}／{r['non_manifold_edges']}")
        rows.append(dict(label='支撐／最終擺向判定',baseline=None,candidate=None))
        comparisons.append(dict(title=title,description=description,metrics=rows))
    step['orientationReview']=dict(stage='orientation_and_overhang_draft',
        settingsSummary='四姿態使用同一組原生設定：Overhang／世界−Z／名義0～45°；Solid、X-Ray關閉。每次實際radians／degrees與編輯模式讀值見JSON。',
        comparisons=comparisons,
        notes=[
            '角度以面外法線對世界−Z計：水平朝下0°、垂直面90°、水平朝上180°；0～45°為本次色帶範圍，超過Maximum顯灰。',
            '床接觸需整面所有頂點Z≈0；其餘朝下面包括整面離床及僅邊緣接觸床面。原生色帶本身沒有區分床面。',
            '原生著色按polygon/BMFace法線；本表另算polygon數與面積，loop triangle分項另存JSON，兩種面數不混用。',
            '表格的世界XYZ外框來自轉換後頂點。未Apply Rotation時，N面板Dimensions仍依物件軸顯示Body60×44.5×30；側放候選的世界外框約30×44.5×60，兩者定義不同。',
            '角度邊界帶1e-4度另記，避免把Python double分類冒稱GPU顏色精確讀值；落床1e-4mm也只是數值核對。',
            '側放能改變臂與層平面的幾何方向，但沒有材料、允許應變、層間附著或疲勞證據。',
            '兩件候選X投影距35mm；未核對機型床幅、附著、支撐生成與移除、橋接跨度、接觸面品質或切片預覽。',
            '原07-02幾何、名義試驗間距及來源版本未改；所有列印、實測、試配和合格欄位維持空值。'],
        sourceUrl='https://raw.githubusercontent.com/blender/blender/9e2066aef7ef/source/blender/draw/intern/mesh_extractors/extract_mesh_vbo_mesh_analysis.cc',
        recordPath=relative+'/print-orientation-record-v001.json',recordSha256=verification['orientation_record_sha256'])
    scene=Path(verification['scene_path'])
    step['operationRun']['outputFiles']=[dict(path=scene.relative_to(PROJECT).as_posix(),sha256=digest(scene),bytes=scene.stat().st_size,
        dimensionsLabel='候選方向場景；保留原形狀，不是已核准列印設定',sourcePath=Path(verification['source_scene_path']).relative_to(PROJECT).as_posix(),sourceSha256=verification['source_scene_sha256'])]
    review=step['contentReview']
    review['summary']='已交叉核對07-02來源幾何、四姿態剛體讀值、實際原生Overhang控制項及色帶、polygon與loop triangle分項、另存重開與版本雜湊。床接觸區與離床朝下面分開；角度、面積及臂的層平面方向不構成支撐、強度或配合合格判定。'
    for path in ['learning/plans/07-03-print-orientation-draft-v001.json','sources/engineering/overhang-source-facts-v001.json',
                 relative+'/print-orientation-record-v001.json',relative+'/independent-audit-v001.json',relative+'/print-orientation-manifest-v001.json',relative+'/publication-checks-v001.json','learning/evidence/ui/'+run_id+'.json']:
        if path not in review['references']: review['references'].append(path)
    changed=[s['id'] for l in catalog['lessons'] for s in l['steps'] if fingerprint(s)!=baseline['steps'][s['id']]]
    assert changed==['07-03'],changed
    assert catalog_path.read_bytes()==original
    write(catalog_path,catalog)
    assert digest(PROJECT/'learning/progress.json')==baseline['progress_sha256']
    checks=dict(recordedAt=datetime.now(timezone.utc).isoformat(),evidencePassed=True,publicationPending=True,browserProofPending=True,
                changedSteps=changed,progressSha256=baseline['progress_sha256'],learnerCompletionConfirmed=False,images=[],downloads=[])
    targets=[(run_dir/r['file'],'images') for r in read(run_dir/'run.json')['records']]
    targets.extend((p,'downloads') for p in [scene,run_dir/'print-orientation-record-v001.json',run_dir/'print-orientation-manifest-v001.json',PROJECT/step['operationRun']['journal']])
    for path,category in targets:
        rel=path.relative_to(PROJECT).as_posix()
        request=urllib.request.Request('http://127.0.0.1:8766/files/'+urllib.parse.quote(rel,safe='/'))
        with urllib.request.urlopen(request,timeout=20) as response:
            data=response.read();status=response.status
            disposition=response.headers.get('Content-Disposition')
        assert status==200 and data==path.read_bytes(),rel
        item=dict(path=rel,status=status,sha256=digest(path),bytes=len(data),exactBytes=True)
        if category=='images':
            assert data[:8]==b'\x89PNG\r\n\x1a\n'
            item.update(zip(('width','height'),struct.unpack('>II',data[16:24])))
            item['originalPixelsPreserved']=True
        if path.suffix=='.blend':
            assert disposition and 'attachment' in disposition
            item['contentDisposition']=disposition
        checks[category].append(item)
    write(run_dir/'publication-checks-v001.json',checks)
    print(json.dumps(dict(changedSteps=changed,images=len(checks['images']),downloads=len(checks['downloads']),browserProofPending=True),ensure_ascii=False))

if __name__=='__main__':
    publish(sys.argv[1])
