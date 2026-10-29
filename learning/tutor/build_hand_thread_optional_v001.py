"""Adapt the prior Screw lesson to an honestly sourced GUI hand profile."""
import copy,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
old=json.loads((root/'learning/lesson11_external_repaired_optional_steps_v001.json').read_text(encoding='utf8'))
e=root/'learning/evidence/08/2026-10-28-external-thread-from-hand-profile-gui-v001'
safe=json.loads((e/'safe-summary-v001.json').read_text(encoding='utf8'))
cmp=json.loads((e/'compare-v010-v001.json').read_text(encoding='utf8'))
assert len(old['steps'])==len(safe['records'])==14
lesson=copy.deepcopy(old)
profile='learning/evidence/08/2026-10-28-external-thread-hand-profile-gui-v004/demo-files/u11_hand_profile_v001.blend'
lesson.update({'title':'第 11 章選修：從手繪輪廓建立外牙草案',
 'status':'數位幾何草案，未經實體列印或試配驗證',
 'scope':'以 GUI 手繪的 v004 邊輪廓續做獨立 GUI 示範；不更新學員進度。',
 'sourceScene':profile,'sourceSha256':'1bfb2d15269fbb1debe325e18904cec6ee654a91a611ee177dbb1c89b7b713c6',
 'demonstrationScene':safe['scene'],'demonstrationSceneSha256':safe['sceneSha256'],
 'startingScene':{'path':profile,'sha256':'1bfb2d15269fbb1debe325e18904cec6ee654a91a611ee177dbb1c89b7b713c6',
  'verification':'learning/evidence/08/2026-10-28-external-thread-hand-profile-gui-v004/independent-audit-v001.json',
  'construction':'以獨立 Blender GUI 從平面建立輪廓，另存並獨立重讀。'},
 'limitations':['來源輪廓在獨立 Blender 以 GUI 建立，屬無 CAD 約束的 mesh；本次只以程式填檔案欄位與讀取數值。',
  'Screw 圖像因沿用放大草圖視角而局部超出畫面，不能由這張圖判斷完整牙形；後續有聚焦及重開畫面。',
  '與 v010 的雙向比較採網格頂點和三角形重心抽樣，最大表面距離約 7.15×10⁻⁷ mm，不能證明完整表面完全相同。',
  '草案不是 ISO 螺紋，零非流形邊和零 BVH 候選不能證明無自交、可列印或配合合格。',
  '材料、列印、實體量測、試配、合格間隙及強度均待定。']})
lesson['upstreamReference']=lesson.get('source')
lesson['source']={'path':profile,'sha256':lesson['sourceSha256']}
for i,(s,r) in enumerate(zip(lesson['steps'],safe['records']),1):
 p=root/r['image'];digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if digest!=r['sha256']:raise ValueError('screenshot hash mismatch')
 s['id']=f'11-hand-thread-{i:02}';s['screenshot']={'path':r['image'],'sha256':digest}
lesson['steps'][0].update(goal='開啟 GUI 手繪輪廓',operation='開啟已另存的 GUI v004 手繪輪廓副本，F2 將 Thread_Hand_Profile 改名為 Thread_Triangle_Profile。',
 context='此輪廓原先以平面合併單點、E/G 逐點建立、F 與 Only Faces 關閉輪廓；本次沒有使用 Python 建立輪廓。',
 visibleConfirmation='畫面顯示放大的閉合輪廓，Outliner 顯示重新命名的物件。',
 programReadback='載入的副本為 3 點、3 邊、0 面；來源 SHA-256 見 sourceSha256。')
lesson['steps'][1]['visibleConfirmation']='Screw 面板可見 360°、1 mm、4 次、Z 軸和 32 段；放大視角使牙條局部超出畫面。'
lesson['steps'][1]['context']='輪廓由 GUI 手工逐點建立；這裡是單頭三角牙草案，非 ISO。'
lesson['steps'][2]['visibleConfirmation']='修改器消失，牙條局部可見，其餘超出畫面。'
lesson['steps'][3]['visibleConfirmation']='畫面為邊選取模式，牙條部分超出畫面；無法單憑照片辨認所有選中邊。'
lesson['steps'][4]['operation']='維持邊界選取後按 F 封端，以讀值檢查結果。'
lesson['steps'][4]['visibleConfirmation']='畫面可見局部牙條網格，無法由此圖完整辨識兩端。'
lesson['steps'][8]['visibleConfirmation']='修改器 Object 欄已顯示工具名稱，欄寬使名稱可能截斷。'
lesson['steps'][9]['programReadback']='程式以 hide_get() 確認工具已隱藏；不是刪除物件。'
lesson['steps'][12]['programReadback']='另存示範 SHA-256 '+safe['sceneSha256']+'；自行建模的檔案雜湊會不同。'
lesson['steps'][13]['programReadback']='重開後獨立讀回 707 點、419 面、1 連通體、非流形 0、BVH 候選 0；與 v010 雙向各 2117 點抽樣最大距約 7.15×10⁻⁷ mm，不是完整幾何等同性或製造合格證明。'
out=root/'learning/lesson11_hand_thread_optional_steps_v001.json'
if out.exists():raise FileExistsError('Preserve version')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('14 steps; lesson sha',hashlib.sha256(out.read_bytes()).hexdigest())
