"""Verify six GUI STL exports and assemble a privacy-safe teaching record."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def rel(p):return p.relative_to(root).as_posix()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
jobs=[
 {'id':'hand-thread','title':'手工輪廓外牙','dir':'hand-v001','file':'u11_hand_thread_v001.stl','source':'learning/evidence/08/2026-10-28-external-thread-from-hand-profile-gui-v001/demo-files/u11_hand_thread_draft_v001.blend'},
 {'id':'side-box-body-repaired','title':'盒側外牙盒體（三角化修訂）','dir':'repaired-sidebox-v001','file':'u11_side_box_body_triangulated_v001.stl','source':'learning/evidence/08/2026-10-28-ch11-triangulate-sidebox-v001/demo-files/u11_side_box_triangulated_v001.blend','repair':'sidebox'},
 {'id':'side-box-lid','title':'盒側外牙原平面蓋','dir':'sidebox-v002','file':'u11_side_box_lid_v002.stl','source':'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/demo-files/u11_box_external_thread_draft_v002.blend'},
 {'id':'side-cap-repaired','title':'盒側保護帽（三角化修訂）','dir':'repaired-cap-v001','file':'u11_side_cap_triangulated_v001.stl','source':'learning/evidence/08/2026-10-28-ch11-triangulate-cap-v001/demo-files/u11_side_cap_triangulated_v001.blend','repair':'cap'},
 {'id':'four-boss-body','title':'四嵌件柱盒體','dir':'fourboss-v001','file':'u11_four_boss_body_v001.stl','source':'learning/evidence/08/2026-10-28-four-insert-boss-gui-v001/demo-files/u11_four_insert_boss_box_v001.blend'},
 {'id':'four-boss-lid','title':'四嵌件柱穿孔蓋','dir':'fourboss-v001','file':'u11_four_boss_lid_v001.stl','source':'learning/evidence/08/2026-10-28-four-insert-boss-gui-v001/demo-files/u11_four_insert_boss_box_v001.blend'},
]
repairs={
 'sidebox':{'title':'盒側盒體','original':'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/demo-files/u11_box_external_thread_draft_v002.blend'},
 'cap':{'title':'盒側帽','original':'learning/evidence/08/2026-10-28-side-cap-relief-gui-v001/demo-files/u11_side_thread_cap_draft_v002.blend'},
}
def image_record(r,folder):
 path=folder/r['file'];digest=sha(path)
 if digest!=r['sha256']:raise ValueError('image changed '+str(path))
 return {'path':rel(path),'sha256':digest}
steps=[];items=[];repair_records={}
for j in jobs:
 if 'repair' in j:
  name=j['repair'];folder=root/f'learning/evidence/08/2026-10-28-ch11-triangulate-{name}-v001';run=read(folder/'run.json');status=read(folder/'runner-status.json');cmp=read(folder/'independent-comparison-v001.json')
  if status['status']!='completed' or cmp['newSceneSha256']!=sha(root/j['source']) or cmp['sourceSceneSha256']!=sha(root/repairs[name]['original']):raise ValueError('repair comparison mismatch')
  if cmp['triangulated']['exactDuplicateTrianglesByIndices'] or cmp['triangulated']['nonManifoldEdges']:raise ValueError('repair remains defective')
  labels=[('檢查原始重複三角形','在保護副本中選取目標，核對原始 mesh 的三角化；不要覆寫來源。','畫面是 GUI 選中的原模型；重複三角形本身未在此圖可視化。',f"原模型讀回 {cmp['source']['exactDuplicateTrianglesByIndices']} 組同頂點索引的重複三角形，來自反向 n-gon 三角化。"),
   ('明確重三角化','Tab 進 Edit Mode、A 全選、Ctrl+T；將多邊形明確三角化。','可見 Edit Mode 的三角網格；此步可能改變非共面多邊形的表面。',f"讀回重複 {cmp['triangulated']['exactDuplicateTrianglesByIndices']}、非流形邊 {cmp['triangulated']['nonManifoldEdges']}；不能只憑此判斷可製造。"),
   ('另存修訂副本','Tab 回物件模式，Save As 另存新的 .blend。','畫面為修訂網格；示範的檔案路徑和名稱由程式填入。',f"修訂檔 SHA-256 {cmp['newSceneSha256']}；原檔未覆寫。"),
   ('重開並比較','重開修訂檔，另以背景 Blender 比較原始與修訂幾何。','畫面顯示重開後的物件；雙向取樣差異需看讀值。',f"雙向頂點與三角形重心取樣最大距 {cmp['newToSource']['maxMm']:.8g} / {cmp['sourceToNew']['maxMm']:.8g} mm；這不是全表面最大差或合格公差。")]
  if len(run['records'])!=4:raise ValueError('repair step count')
  for n,(r,(goal,op,vis,back)) in enumerate(zip(run['records'],labels),1):
   steps.append({'id':f'11-stl-{name}-repair-{n:02}','goal':repairs[name]['title']+'：'+goal,'operation':op,
     'context':'源模型與修訂模型另存；此三角化改變非平面 n-gon 的表示，不宣稱幾何完全不變。',
     'visibleConfirmation':vis,'programReadback':back,'screenshot':image_record(r,folder)})
  repair_records[name]={'source':repairs[name]['original'],'sourceSha256':cmp['sourceSceneSha256'],'revised':j['source'],
    'revisedSha256':cmp['newSceneSha256'],'comparison':rel(folder/'independent-comparison-v001.json'),
    'originalDuplicateGroups':cmp['source']['exactDuplicateTrianglesByIndices'],'revisedDuplicateGroups':cmp['triangulated']['exactDuplicateTrianglesByIndices'],
    'sourceVolumeMm3':cmp['source']['signedVolumeMm3'],'revisedVolumeMm3':cmp['triangulated']['signedVolumeMm3'],
    'bidirectionalSampleMaxMm':[cmp['newToSource']['maxMm'],cmp['sourceToNew']['maxMm']]}
 folder=root/('learning/evidence/08/2026-10-28-ch11-stl-'+j['dir']);run=read(folder/'run.json');status=read(folder/'runner-status.json');v=read(folder/(j['id']+'-verification.json'));audit=read(folder/(j['id']+'-independent-audit-v001.json'))
 if status['status']!='completed' or v['sourceSceneSha256']!=sha(root/j['source']):raise ValueError('source mismatch')
 stl=folder/'demo-files/exports'/j['file']
 if sha(stl)!=v['stl']['sha256'] or sha(stl)!=audit['stlSha256']:raise ValueError('STL hash mismatch')
 if audit['binaryExactDuplicateTriangles'] or audit['binaryTriangles']!=audit['reimport']['triangles'] or audit['reimport']['nonManifoldEdges']:raise ValueError('STL has outstanding numerical issue')
 records=[r for r in run['records'] if r['slug'].startswith(j['id']+'-')]
 if len(records)!=6:raise ValueError('wrong step count '+j['id'])
 b=v['stl']['boundsMm'];dim=[row[1]-row[0] for row in b]
 data={'id':j['id'],'title':j['title'],'sourceScene':j['source'],'sourceSha256':v['sourceSceneSha256'],
       'sourceObject':v['source']['object'],'stl':rel(stl),'stlSha256':sha(stl),'stlBytes':v['stl']['bytes'],
       'binaryTriangles':audit['binaryTriangles'],'binaryExactDuplicateTriangles':audit['binaryExactDuplicateTriangles'],
       'boundsMm':b,'dimensionsMm':dim,'guiReimport':v['reimport'],'independentAudit':rel(folder/(j['id']+'-independent-audit-v001.json')),
       'independentReimport':audit['reimport'],'exportOptions':v['exportOptions'],'importOptions':v['importOptions']}
 items.append(data)
 labels=[('選取來源物件',f"開啟來源保護副本，在 Outliner 只選 {v['source']['object']} 並聚焦。",'畫面顯示選中的來源；Item 尺寸和世界外框在旋轉情況可能不同。',f"程式確認只選 {v['source']['object']}；世界外框約 {dim[0]:.6g} × {dim[1]:.6g} × {dim[2]:.6g} mm。"),
 ('開啟 STL 匯出','GUI 選 File > Export > STL。','畫面顯示實際 Blender 檔案選單。','匯出前仍維持單物件選取。'),
 ('確認匯出選項','在檔案視窗確認 Selection Only 勾選、Scale 1、Scene Unit 不勾，按 Export STL。','原圖顯示檔名及實際選項；檔案路徑與名稱由程式填入。','讀回二進位、Selection Only、Scale 1、Scene Unit 關、Apply Modifiers、Y Forward／Z Up。'),
 ('讀取 STL 實檔','匯出後直接解析二進位 STL 並比對來源世界外框。','畫面返回 Blender；三角形及雜湊由程式讀檔，不由照片推定。',f"STL {audit['binaryTriangles']} 個三角形、精確重複 {audit['binaryExactDuplicateTriangles']}；SHA-256 {sha(stl)}。"),
 ('開啟重新匯入','GUI 隱藏原物件，F3 搜尋 Import STL，選剛才的檔案。','實際匯入對話框顯示 Scale 1、Scene Unit 不勾；路徑與檔名由程式填入。','程式讀回 Y Forward／Z Up；這是以本次假定的 mm 數值重匯入。'),
 ('實際重匯入核對','確認 Import STL，選中新網格並聚焦，核對世界尺寸。','畫面顯示新匯入物件；其軸向尺寸不一定等同原物件旋轉前 Item 值。',f"GUI 重匯入 {v['reimport']['triangles']} 三角形、非流形邊 {v['reimport']['nonManifoldEdges']}；另一獨立 Blender 重匯入 {audit['reimport']['triangles']}、非流形邊 {audit['reimport']['nonManifoldEdges']}。")]
 for n,(r,(goal,op,vis,back)) in enumerate(zip(records,labels),1):
  steps.append({'id':f"11-stl-{j['id']}-{n:02}",'goal':j['title']+'：'+goal,'operation':op,
   'context':'STL 沒有單位標記；示範以毫米解讀數字，保留來源世界座標。數位核對不代表列印、尺寸公差或試配合格。',
   'visibleConfirmation':vis,'programReadback':back,'screenshot':image_record(r,folder)})

result={'schemaVersion':1,'title':'第 11 章：六件 STL 匯出、修訂與重新匯入',
 'scope':'六個獨立 Blender GUI 選取及匯出、實際 GUI 重匯入，再以另一個 Blender 背景重匯入；不更新學員進度。',
 'status':'已完成數位匯出與有限檢查，實體未驗證','items':items,'repairRecords':repair_records,
 'failureHistory':[{'kind':'side-box-body','file':'learning/evidence/08/2026-10-28-ch11-stl-sidebox-v002/demo-files/exports/u11_side_box_body_v002.stl','exactOppositeWindingDuplicateTriangles':4,'nativeReimportNonManifoldEdges':12},
                   {'kind':'side-cap','file':'learning/evidence/08/2026-10-28-ch11-stl-cap-v002/demo-files/exports/u11_side_cap_v002.stl','exactOppositeWindingDuplicateTriangles':2,'nativeReimportNonManifoldEdges':6}],
 'limitations':['原始盒側 Body 與側帽各有反向重複三角形；新 STL 來自明確三角化的新 .blend，原版和失敗記錄保留。',
  '重三角化改變部分非平面 n-gon 的表面；頂點與三角形重心的雙向取樣不是完整形狀或旋合等同性證明。',
  '本次 STL 保留場景世界擺位且 STL 無內嵌長度單位；切片時需自行核對單位、位置與方向。',
  '精確重複 0、非流形 0、有限 BVH 結果與檔案尺寸皆非列印或配合合格保證。',
  '帽的徑向 0.2 mm／名義直徑差 0.4 mm、軸向 0.2 mm 均為草案試驗值；四柱蓋孔 Ø3.4 mm 亦未實體試配。',
  '原始 v002 verification 的固定英文 interpretation 無論計數為何都寫 retains duplicates，是程式通用說明錯誤；以原檔精確數量與獨立稽核為準。',
  '原始 runner-status 含使用者 Windows Recent 路徑，不可原樣公開。'],
 'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,'steps':steps}
out=root/'learning/lesson11_stl_export_optional_steps_v001.json'
if out.exists():raise FileExistsError('preserve version')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
safe=root/'learning/evidence/08/2026-10-28-ch11-stl-summary-v001';safe.mkdir(exist_ok=False)
(safe/'safe-summary-v001.json').write_text(json.dumps({k:v for k,v in result.items() if k!='steps'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('STL',len(items),'steps',len(steps),'lesson SHA-256',sha(out),'summary',rel(safe/'safe-summary-v001.json'))
