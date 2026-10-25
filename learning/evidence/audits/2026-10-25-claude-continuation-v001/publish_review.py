"""Publish additive audit notes; keep all original demonstrations and progress."""
import copy
import hashlib
import html
import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
REL=OUT.relative_to(ROOT).as_posix()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def new_json(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
baseline=read(OUT/'baseline-v001.json')
catalog=read(ROOT/'learning/catalog.json')
assert catalog==baseline['catalog'], 'catalog changed since audit baseline; inspect before publishing'
assert read(ROOT/'learning/progress.json')==baseline['progress']
assert all(sha(ROOT/p)==h for p,h in baseline['protectedFiles'].items())
inventory=read(OUT/'image-inventory-v001.json')
report_names=['audit_images_05a-v001.json','audit_images_05b_06a-v001.json','audit_images_06_08-v001.json','audit_images_07a-v001.json','audit_images_07b-v001.json']
seen={}
for name in report_names:
    report=read(OUT/name)
    for image in report['images']:
        path=image['path'];assert path not in seen, 'path reviewed twice in ledger'
        assert image['sha256']==sha(ROOT/path)
        assert image.get('viewed') or image.get('inspection') or image.get('visual_review')
        seen[path]={'sha256':image['sha256'],'review':REL+'/'+name}
assert set(seen)=={i['path'] for i in inventory['images']}
assert len(seen)==311
assert len({i['sha256'] for i in seen.values()})==288
stl=read(OUT/'stl-and-geometric-checks-v001.json')
blender=read(OUT/'blender-readback-v001.json')
formula=read(OUT/'source-formulas-review-v001.json')
numeric_peer=read(OUT/'audit_numeric_review-v001.json')
definitions=read(OUT/'source-definition-review-v001.json')

risks=[
 {'id':'R01','step':'05-03','severity':'medium','title':'凹點之間約0.4 mm薄肉，辨識性尚待切片／實印',
  'detail':'21個直徑約1.2 mm的凹點，同組相鄰中心距約1.6 mm；實網格最小間隔約0.399994 mm。這是細節風險，尚未證明會糊在一起。已知噴嘴0.4 mm，但實際線寬待定，不能稱為「剛好一條線寬」。'},
 {'id':'R02','step':'06-01','severity':'medium','title':'環唇與圓柱同時定位，存在尺寸偏差互相牽制的風險',
  'detail':'既有矩形環唇與柱／孔都用了名義單邊0.2 mm試驗間隙；不能因此保證可同時裝入。柱建構高30 mm，內底以上幾何露出約29.5 mm、名義直徑4 mm；這不是已確認的力學有效長度。需再檢查裝配路徑、各定位特徵的讓位、層向與列印穩定性，尚無卡住或晃動的實測結果。'},
 {'id':'R03','step':'06-02','severity':'medium','title':'盒內導軌有兩片水平朝下懸空面，合計約448 mm²',
  'detail':'實際露出面每側約56×4 mm，位於原場景Z10；盒體開口朝上並以外底落床時，這些面約在床面上25 mm。60 mm是建構工具長度，不能拿來算露出面積480 mm²。應在切片核對支撐／方向，或另作斜面改版；本次未指定支撐、未改模型，也未認定可免支撐。'}
]
presentation=[
 {'id':'P01','step':'05-03','title':'補足#2與#4之前的操作脈絡','detail':'#2之前劇本已新增Cube；#4之前已隱藏Plate。舊圖與run保留，讀者應把這兩個準備動作算進步驟。'},
 {'id':'P02','step':'05-03','title':'80.4與80.35是顯示精度差異','detail':'獨立Blender讀回Cutters X80.3500099 mm，名義80.35以一位小數顯示為80.4；沒有發現這項幾何尺寸錯誤。小凹點及孔寬不能只由總覽圖讀出，精值應查raw與補充圖。'},
 {'id':'P03','step':'05-04','title':'#15泛用尾句與尺寸補圖的閱讀方式','detail':'#15重匯入插銷時混入「孔板改斜視」尾句，應只按本件插銷理解。主流程#15/#17沒有顯示Item Dimensions，尺寸請交叉查看兩張補充原圖；不能把未顯示欄位當成畫面證據。'},
 {'id':'P04','step':'06-01','title':'#15定位柱被蓋板遮住','detail':'該圖能看上抬的蓋板與孔，不能直接看到長定位柱。查看柱形請回看#3或#6原圖；本次不重畫或改寫歷史照片。'},
 {'id':'P05','step':'06-02','title':'#3隱藏盒體與#17量值來源需說清楚','detail':'#3建構導軌工具前已隱藏Body。#17是組裝概觀，沒有剖切，不能從照片直接讀取0.2 mm級間隙；數值來自實網格截面讀回。#12側欄37.1對文字37.12也有顯示精度差異。'},
 {'id':'P06','step':'06-03','title':'#3只展示Body的槽','detail':'該圖是盒體槽的外觀，沒有同時展示蓋榫。槽／榫對照應連同後續Lid來源圖及網格資料閱讀。'},
 {'id':'P07','step':'07-02','title':'Edit Mode的Local Median不等於world座標','detail':'例如#5側欄Local Z22.5 mm，加物件Location Z−9.5 mm，才是本次world Z13 mm。Flange圖也需核對其transform；組裝圖active Body時側欄屬Body，不能用來當Lid抬升讀值。'},
 {'id':'P08','step':'07-04','title':'側視輪廓、剖切與作用中物件需區分','detail':'#3/#18是Right側視的外輪廓，沒有做剖切；精確剖面仍靠raw。#9作用中Lid，舊note卻沿用Body提示，應按Lid的來源與後續重匯入尺寸解讀。匯出照片不能單獨證明bytes／hash或拓撲。'},
 {'id':'P09','step':'07-05','title':'隱藏SnapTool的讀值不在#2側欄中','detail':'原幾何run #2畫面active Body、SnapTool隱藏；記錄的SnapTool數值來自程式讀回，請連同#4工具選取圖閱讀。總覽不能證明精確L、接床面積或離床量；幾何L19／17／21尚未成為力學有效L。'}
]
all_evidence=report_names+['blender-readback-v001.json','stl-and-geometric-checks-v001.json','audit_numeric_review-v001.json','source-formulas-review-v001.json','source-definition-review-v001.json','source-cache/sources-v002.json','recompute_blender.py','recompute_stl.py']
record={'schemaVersion':1,'id':OUT.name,'reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'handoff':'以學員貼出的Claude部分審查摘要交接；本次重新核對全部已發布路徑，不把約120張／287張摘要當成本次逐圖證據。',
 'scope':{'lessons':['05','06','07','08'],'publishedSteps':14,'imagePathsReviewed':311,'distinctSha256Images':288,'pathCountVsPixelCount':'311個路徑中有23個額外相同SHA引用，含跨步驟重用；不是漏看23張。未發布probe／失敗run不在本次逐圖結論範圍。','imageLedger':seen,'blenderScenes':11,'stlFiles':10,'sourcePdfPages':6},
 'conclusion':'未發現所能直接觀察內容的重大圖文矛盾，或本次外框／體積／邊連接數值不一致。確認三項工程風險，需補充切片與實體驗證；九組呈現說明已追加到教學頁，保留原圖及操作紀錄。',
 'engineeringRisks':risks,'presentationClarifications':presentation,
 'displayRounding':{'cuttersXReadback_mm':80.35000991993613,'nominalX_mm':80.35,'uiOneDecimal_mm':80.4,'mismatch':False},
 'keyMeasurements':{'dimpleLigamentMin_mm':stl['holeplate']['nearest_recess_pair']['gap_from_x_radii_mm'],'dovetailDownwardAreaBlender_mm2':blender['dovetail_inward_ledge']['area_total_mm2'],'dovetailDownwardAreaStl_mm2':448.0,'dovetailExposedLengthNominal_mm':56,'dovetailOverhangWidthNominal_mm':4,'tenonConstructionHeightNominal_mm':30,'tenonGeometricExposureAboveInnerFloorNominal_mm':29.5,'mechanicallyEffectiveLength':None},
 'stlDimensions':[{k:v for k,v in o.items() if k in ['path','sha256','bytes','triangles','bounds_mm','source_scene','source_scene_sha256','max_bounds_error_mm','volume_difference_mm3','dimensions_and_topology_consistent']} for o in stl['stls']],
 'numericScopeLimits':['本次STL核對外框、體積、round-grid 1e-5 mm邊連接／分量與法向，未以此宣稱完整表面等價、自交皆排除或可列印。','1e-4／1e-5 mm是浮點重建門檻，不是製造公差。','內底以上幾何露出高不等於已驗證的力學有效長度。','Screw本次查官方手冊與精確build原始碼；沒有新增Screw模型或runtime案例。','ISO僅查公開摘要，未取得完整標準、公差或尺寸表。'],
 'sourceReview':{'formulaPageAudit':REL+'/source-formulas-review-v001.json','definitionAudit':REL+'/source-definition-review-v001.json','fullStandardsRead':False,'manufacturerStrainValuesAppliedToFdm':False},
 'physicalPrintResult':None,'physicalFitResult':None,'qualifiedStrength':None,'qualifiedFit':None,
 'progressRevisionBefore':baseline['progress']['revision'],'progressRevisionAfter':baseline['progress']['revision'],'progressChanged':False,
 'sourceFilesChanged':False,'modelsModified':False,'slicerPerformed':False,'evidence':[{ 'path':REL+'/'+p,'sha256':sha(OUT/p)} for p in all_evidence]}
new_json('report-v001.json',record)

E=html.escape
def local(path,label):return '<a href="/files/'+E(path,quote=True)+'">'+E(label)+'</a>'
def findings(items):return ''.join('<article class="finding"><span class="tag">'+E(x['step'])+'</span><h3>'+E(x['title'])+'</h3><p>'+E(x['detail'])+'</p></article>' for x in items)
rows=''.join('<tr><td>'+E(Path(x['path']).name)+'</td><td>'+E(' × '.join(f'{n:.6g}' for n in x['bounds_mm']['dimensions']))+'</td><td>'+str(x['triangles'])+'</td></tr>' for x in record['stlDimensions'])
sources=[('Covestro原廠手冊，第9／24頁','https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557218421.pdf'),('BASF原廠著作的第三方存放副本，第9／11／12／14頁','https://productdesignonline.com/wp-content/uploads/2019/08/Snap-Fit-Design-Manual.pdf'),('BASF署名文章：Improving Snapfit Design (Part 3)','https://ulprospector.ul.com/1248/pe-snapfit-3/'),('Blender 5.2 Screw手冊','https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/screw.html'),('已安裝build的Screw原始碼','https://github.com/blender/blender/blob/9e2066aef7ef/source/blender/modifiers/intern/MOD_screw.cc'),('ISO68-1:2023公開摘要','https://www.iso.org/standard/85107.html'),('ISO5408:2009公開摘要','https://www.iso.org/standard/44424.html')]
source_links=''.join('<li><a href="'+E(url,quote=True)+'" target="_blank" rel="noopener">'+E(label)+'</a></li>' for label,url in sources)
doc='<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blender 專案獨立審查 v001</title><link rel="stylesheet" href="audit-report-v001.css"></head><body><main><p class="eyebrow">BLENDER · 05–08 · 2026-10-25 · v001</p><h1>逐圖與工程審查</h1><p class="lead">311 個圖片路徑／288 個不同 SHA 全數核對；獨立重讀11個場景、解析10份STL。</p><div class="status"><strong>確認3項工程風險，已補入教學頁</strong><p>沒有實際列印或試配；強度與配合合格結果留空。</p></div><p>'+E(record['conclusion'])+'</p><p class="muted">'+E(record['scope']['pathCountVsPixelCount'])+'</p><h2>先看工程風險</h2>'+findings(risks)+'<h2>80.4 mm與80.35 mm</h2><p>Cutters獨立讀回X=80.3500099 mm；名義80.35以一位小數顯示為80.4。這項不是幾何尺寸錯誤。</p><h2>STL尺寸核對（mm）</h2><div class="table-scroll"><table><thead><tr><th>檔案</th><th>世界XYZ外框</th><th>三角形</th></tr></thead><tbody>'+rows+'</tbody></table></div><p>10件的外框、體積與新Blender讀回一致，邊連接檢查為單一閉合分量。本次沒有把外框與體積一致當成完整表面等價或可列印的證明；數值容差只處理浮點重建。</p><h2>圖說與畫面限制</h2>'+findings(presentation)+'<h2>公式與定義來源</h2><p>已看原PDF的6個完整頁面：Covestro均勻矩形懸臂係數0.67、應變百分比除100；BASF古典反解係數2/3，Q對應根部／牆面柔度及L/t，並非安全係數。倒扣量、所需撓度與允許撓度分開。原冊語義與圖號細節見獨立公式審查；不採原廠射出材料的數值作FDM合格值。</p><p>Screw定義另核精確build原始碼：Object Screw關閉、Angle360°時Screw才等於每轉導程；單線才再等於螺距。Iterations不是線數。ISO只核公開摘要，未取得完整標準或公差表。</p><ul>'+source_links+'</ul><h2>檔案、原圖與進度</h2><p>原場景、STL、截圖、已凍結參數與來源未改；教學頁採追加審查卡，原operationRun保持。共用進度revision6未變，沒有代學員確認完成。</p><p>'+local(REL+'/report-v001.json','完整資料與逐圖證據索引（JSON）')+' · '+local(REL+'/stl-and-geometric-checks-v001.json','STL／幾何讀值')+' · '+local(REL+'/source-formulas-review-v001.json','公式逐頁審查')+'</p><p><a href="http://127.0.0.1:8766/">回教學頁</a></p></main></body></html>'
with (OUT/'report-v001.html').open('x',encoding='utf-8',newline='\n') as f:f.write(doc+'\n')
css=':root{font-family:"Segoe UI","Microsoft JhengHei",sans-serif;color:#20374c;background:#eef2f5}*{box-sizing:border-box}body{margin:0}main{max-width:960px;margin:24px auto;padding:32px;background:white;border-radius:14px;line-height:1.8}h1{font-size:32px;margin:4px 0 12px}h2{margin-top:36px;border-bottom:1px solid #dbe3e9;padding-bottom:8px}h3{font-size:18px;margin:8px 0}.eyebrow,.tag{font-size:12px;color:#506c80}.lead{font-size:18px}.status{padding:18px;border-left:4px solid #ad7739;background:#fff5e8}.status p{margin-bottom:0}.muted{color:#627486;font-size:13px}.finding{padding:16px 0;border-bottom:1px solid #e8edf1}.finding p{margin-bottom:6px}a{color:#2168a3;overflow-wrap:anywhere}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:12px 8px;text-align:left;border-bottom:1px solid #dbe3e9;white-space:nowrap}td:first-child{font-family:monospace}@media(max-width:600px){main{margin:0;padding:20px 16px;border-radius:0}h1{font-size:27px}.lead{font-size:16px}h2{font-size:22px}.finding h3{font-size:17px}}@media print{body{background:white}main{max-width:none;margin:0;padding:0}.table-scroll{overflow:visible}.finding{break-inside:avoid}a{color:inherit}}'
with (OUT/'audit-report-v001.css').open('x',encoding='utf-8',newline='\n') as f:f.write(css+'\n')

# Add present-day review cards without rewriting frozen demonstrations.
by_step={}
for item in risks+presentation:by_step.setdefault(item['step'],[]).append(item)
by_step['08-01']=[{'title':'定義已複核，路線選擇與舊紀錄時態分開','detail':'官方Screw手冊／精確build與ISO公開摘要已複核，原參數24欄待定保留。後續兩條一起學的選擇另有route-decision v001；舊照片及參數的路線待定為選擇前狀態。沒有建牙、選硬體或取得合格值。'}]
for lesson in catalog['lessons']:
    for step in lesson['steps']:
        sid=step['id']
        if sid not in by_step:continue
        step['auditReview']={'status':'reviewed_with_limits','reviewedOn':'2026-10-25','summary':'本步已納入05～08逐圖與獨立數值審查；下列是目前閱讀與工程風險補充，原圖及歷史操作保留。實際列印與試配結果仍留空。','findings':by_step[sid],'reportPath':REL+'/report-v001.html','recordPath':REL+'/report-v001.json'}
        step['contentReview']['references'].append(REL+'/report-v001.json')
        if sid in ['05-03','06-01','06-02']:
            risk=next(r for r in risks if r['step']==sid)
            step['help']+=' 審查補充：'+risk['detail']
        if sid=='06-03':
            step['help']+=' 盒體開口朝上時，導軌兩側各約56×4 mm水平朝下懸空面（合計約448 mm²）；支撐或方向仍須切片核對，不能從STL數位檢查通過推論可免支撐。'

old_steps={s['id']:s for l in baseline['catalog']['lessons'] for s in l['steps']}
for lesson in catalog['lessons']:
    for step in lesson['steps']:
        old=old_steps[step['id']]
        assert step.get('operationRun')==old.get('operationRun')
        assert step.get('previousOperationRuns')==old.get('previousOperationRuns')
        assert step.get('figures')==old.get('figures')
assert len(old_steps)==52
with (ROOT/'learning/catalog.json').open('w',encoding='utf-8',newline='\n') as f:f.write(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
new_json('catalog-publication-v001.json',{'changedSteps':sorted(by_step),'totalSteps':52,'operationRunsUnchanged':True,'figuresUnchanged':True,'progressSha256':sha(ROOT/'learning/progress.json'),'catalogSha256':sha(ROOT/'learning/catalog.json'),'sourceFilesProtected':len(baseline['protectedFiles'])})
print('PUBLISHED_AUDIT image_paths=311 distinct_SHA=288 scenes=11 STL=10 cards='+str(len(by_step)))
