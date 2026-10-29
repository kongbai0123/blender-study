"""Create an optional v010 lesson from the preserved earlier lesson and evidence."""
import json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
old=json.loads((root/'learning/lesson11_external_optional_steps_v001.json').read_text(encoding='utf8'))
summary=json.loads((root/'learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/safe-summary-v001.json').read_text(encoding='utf8'))
if len(old['steps'])!=14 or len(summary['records'])!=14:raise ValueError('Unexpected step count')
old.update({'title':'第 11 章選修：修訂外牙的 GUI 幾何示範','scope':'修正試作；僅有數位幾何檢查，不更新學員進度，未驗證製造或配合。',
 'demonstrationScene':summary['scene'],'demonstrationSceneSha256':summary['sceneSha256'],
 'limitations':['三角截面為程式預建，並非 GUI 手繪；之後在獨立 Blender 以 GUI 事件建立與另存。',
 '修正版柱芯旋轉 5.625° 並延長至約 4.8 mm，改變多邊形局部輪廓及整體高度；請與保留的 v005 風險案例比較。',
 '獨立 BVH 候選為 0、診斷門檻以下薄面為 0，不證明完全沒有自交或可製造；10⁻⁵ mm² 為診斷門檻而非合格標準。',
 '此為獨立示範，不是 ISO 標準牙形；材料、配合、實際列印與量測均未驗證。',
 '畫面部分視角較小，須配合讀值；檔案對話框路徑及檔名由程式填入。']})
for idx,(step,r) in enumerate(zip(old['steps'],summary['records']),1):
 p=root/r['image'];h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=r['sha256']:raise ValueError('Image hash mismatch')
 step['id']=f'11-external-repaired-{idx:02}'
 step['screenshot']={'path':r['image'],'sha256':h}
steps=old['steps']
steps[0].update(operation='開啟既有參考場景的保護副本，示範以程式準備 Thread_Triangle_Profile 三點三邊輪廓。',context='程式在載入副本後建立輪廓、隱藏盒體；此步不是 GUI 手繪。',programReadback='程式讀回 3 點、3 邊、0 面；三點為 (4.8,0,0)、(6,0,0.3)、(4.8,0,0.6) mm。')
steps[6].update(operation='Tab 回物件模式；F3 搜尋 Add Cylinder。依序 S 0.005、S Z 0.48、G Z 2.3 mm、R Z 5.625°；F3 執行 Apply Scale 與 Apply Rotation，F2 命名 Thread_Core。',context='此係數僅用於本場景預設圓柱；芯柱上下端各伸出牙條約 0.1 mm，旋轉改變多邊形輪廓。',visibleConfirmation='選中 Thread_Core，畫面尺寸欄約 9.95 × 9.95 × 4.8 mm。',programReadback='程式依實際頂點讀回旋轉後世界 X/Y 範圍約 ±4.9759 mm，Z 約 -0.1～4.7 mm；套用後旋轉欄為 0、Scale 為 1。')
steps[10].update(context='確認 Union、Exact 與正確工具後套用；接著還需另行獨立稽核。',programReadback='程式讀回 707 點、419 面、單連通體、非流形邊 0、外框約 12 × 12 × 4.8 mm；這些讀值不證明無自交。')
steps[11]['programReadback']='外框讀值維持約 12 × 12 × 4.8 mm；畫面不足以判定所有細節。'
steps[12]['programReadback']='另存場景 SHA-256 為 '+summary['sceneSha256']+'；自行建立的檔案雜湊會不同。'
steps[13].update(operation='重開另存草案並檢查尺寸，再以獨立 Blender 腳本檢查拓樸、三角面積及 BVH。',programReadback='獨立讀回非流形邊 0、BVH 候選 0，低於 10⁻⁵ mm² 面 0，最小三角面約 0.028674 mm²；不證明完全無自交或列印合格。')
out=root/'learning/lesson11_external_repaired_optional_steps_v001.json'
if out.exists():raise FileExistsError('Preserve existing lesson version')
out.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Verified',len(steps),'revised screenshot hashes and wrote optional lesson')
