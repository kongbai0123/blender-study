"""Prepare the optional lesson from the verified v005 local demonstration."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
evidence = root / 'learning/evidence/08/2026-10-28-external-thread-gui-trial-v005'
summary = json.loads((evidence / 'safe-summary-v001.json').read_text(encoding='utf-8'))
audit = summary['independentAudit']
if summary['runnerStatus'] != 'completed' or audit['nonAdjacentTriangleOverlapPairs'] != 3:
    raise ValueError('Evidence status has changed; review before rebuilding lesson.')

# goal, action, prerequisites, visual, readback: each explicitly describes the
# actual screenshot and observed data, including the unsuccessful attempt.
items = [
    ('確認預建截面', '開啟來源的保護副本；本次劇本以程式建立三頂點、三邊的三角輪廓並選取，隱藏盒體參考。這不是 GUI 手畫輪廓。', 'Blender 5.2.1 LTS；場景單位設定為毫米，保留原始小盒。', 'Outliner 顯示 Thread_Triangle_Profile；截面在此視角很小。', '程式讀回 3 頂點、3 條邊、0 面；輪廓無面，不是封閉實體。'),
    ('建立螺旋牙條', '物件模式按 F3 搜尋 Add Screw Modifier；在修改器輸入 Screw 1 mm、Iterations 4、Steps View 32、Render 32。', '選中預建的 Thread_Triangle_Profile。', '右側修改器顯示 Angle 360°、Screw 1 mm、Iterations 4、Z 軸與 32 段；牙條顯示較小。', '程式讀回位移 1 mm、4 圈、32 顯示段；評估網格 387 頂點、384 面、6 條邊界。角度與 Z 軸由畫面佐證。'),
    ('轉換修改器結果', '按 F3 搜尋 Convert Mesh，將螺旋修改器結果轉成網格。', '確認 Screw 數值及對象後再轉換；此步對示範複本操作。', '修改器區不再列出 Screw；牙條在視窗中央。', '程式讀回修改器列表空，網格仍有 6 條邊界。'),
    ('選取開口邊', 'Tab 進入編輯模式，切換邊選取，Alt+A 取消全選，以 F3 搜尋 Select Non Manifold。', '已將牙條轉為網格。', '左上角顯示 Edit Mode，中央可見網格；視角小，不足以辨認每條選取邊。', '程式讀回 6 條邊界與 6 條非流形邊；此紀錄未計數實際選取邊。'),
    ('封閉牙條兩端', '維持前一步選取，按 F 補面。', '必須選中兩端邊界；選取無法單憑此截圖逐邊判讀。', '畫面仍顯示編輯模式的牙條網格；前後畫面很相近。', '程式讀回 386 面、邊界 0、非流形邊 0；此數值不能證明無自交。'),
    ('重新計算法線', '在編輯模式按 A 全選，Shift+N 重新計算法線；Tab 回到物件模式。', '封端已完成；法線需在選取的網格上操作。', '畫面為編輯模式網格；法線方向未直接可視化，Tab 是緊接此畫面之後的動作。', '程式讀回 386 面、邊界 0、非流形邊 0；未以截圖證明每片法線方向。'),
    ('建立圓柱芯', '物件模式按 F3 搜尋 Add Cylinder；S 輸入 0.005，S Z 輸入 0.46，G Z 輸入 2.3mm；F3 搜尋 Apply Scale，F2 命名 Thread_Core。', '此毫米場景的預設圓柱直徑約 2000 mm；比例僅適用同樣初始尺寸，需先看實際物件尺寸。', '右側可見 Thread_Core，尺寸顯示約 10 × 10 × 4.6 mm，位置 Z 約 2.3 mm。', '程式讀回約 9.99999 × 9.99999 × 4.599996 mm，Scale 為 1、Z 約 2.3 mm。'),
    ('檢查首次布林對象指定', '選圓柱按 F3 搜尋 Add Boolean Modifier，選 Union、Exact，嘗試輸入 Thread_Triangle_Profile。', '物件模式選中 Thread_Core。', '修改器顯示 Union 和 Exact，但 Object 欄位仍空白；牙條與圓柱仍重疊顯示。', '程式讀回 UNION、EXACT、operand 為空，故首次指定失敗；不要在此時套用。'),
    ('重新指定牙條對象', '在 Object 欄位再次搜尋並從候選清單選 Thread_Triangle_Profile。', '承接上一步空白欄位；須點選候選，而不只是輸入文字。', 'Object 欄位已有名稱，畫面可能因欄寬而截斷。', '程式讀回 UNION、EXACT、operand 為 Thread_Triangle_Profile。'),
    ('隱藏工具以查看結果', '在 Outliner 隱藏 Thread_Triangle_Profile；保留工具物件，觀察布林預覽。', '已確認 Boolean 的對象設定；眼睛圖示位置依版面而異。', 'Outliner 的牙條物件顯示為隱藏；畫面呈現圓柱和牙條預覽。', '劇本讀取 hide_get() 驗證已隱藏；此步沒有量測物理尺寸。'),
    ('套用布林並檢查', '在 Thread_Core 的 Boolean 修改器選單按 Apply。', '必須再次確認 Union、Exact 和正確工具對象；隱藏工具不代表刪除。', '修改器不再列出 Boolean，物件尺寸顯示約 12 × 12 × 4.6 mm。', '程式讀回 711 頂點、428 面、1 連通體、邊界與非流形邊均 0；獨立檢查另有 3 組候選交疊，待修正。'),
    ('放大並觀察草案', 'F3 搜尋 Frame Selected，再按數字鍵盤 2 兩次調整視角。', '物件模式選中布林結果 Thread_Core；無數字鍵盤可使用視圖控制。', '畫面放大後可見外牙與頂面；不能從單一視角證明整體無自交。', '讀回外框 X/Y 約 ±6 mm、Z 0 至 4.6 mm；同相位牙頂高度為 0.3、1.3、2.3、3.3、4.3 mm。'),
    ('另存版本', '使用 Save As 另存新檔，保留原始小盒和參考場景。示範的檔案對話框路徑與檔名由程式填入。', '確認儲存至示範專用新檔，勿覆寫來源；草案仍待修正。', '另存後可見牙條草案；這張不是檔案視窗的截圖。', '保存後讀回拓樸和外框與前一步相同；示範檔 SHA-256 見本文件 demonstrationSceneSha256。'),
    ('重開檔案核對', '開啟剛另存的新檔，重新檢查場景與物件。示範的路徑和檔名由程式填入。', '確定新版本已保存；此步不代表使用者完成該課。', '重開後視窗顯示 Thread_Core，尺寸約 12 × 12 × 4.6 mm。', '重開後讀回 711 頂點、428 面、1 連通體、非流形邊 0；仍有 3 組候選交疊待查。'),
]
assert len(items) == len(summary['records']) == 14
steps = []
for idx, ((goal, operation, context, visual, readback), record) in enumerate(zip(items, summary['records']), 1):
    path = root / record['image']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != record['imageSha256']:
        raise ValueError(f'Screenshot mismatch: {path.name}')
    steps.append({'id': f'11-external-{idx:02}', 'goal': goal, 'operation': operation,
                  'context': context, 'visibleConfirmation': visual, 'programReadback': readback,
                  'screenshot': {'path': record['image'], 'sha256': digest}})
lesson = {
    'schemaVersion': 1,
    'title': '第 11 章選修：外牙 GUI 操作草案與待修正風險',
    'scope': '選修實驗示範，幾何待修正；不更新學員或課程進度。',
    'sourceScene': summary['source']['path'], 'sourceSha256': summary['source']['sha256'],
    'demonstrationScene': summary['model']['path'], 'demonstrationSceneSha256': summary['model']['sha256'],
    'limitations': [
        '三角截面由程式預先建立，非 GUI 手工畫草圖；從 Screw 後使用獨立 Blender 模擬 GUI 事件。',
        '獨立 BVH 自檢發現 3 組非共頂點候選交疊及極薄三角面，無法確定是實際穿越或數值接觸；待修正，不能稱為可靠封閉模型。',
        '非流形邊 0、單一連通體與正體積不代表沒有自交或可列印。',
        '此為獨立三角齒形草案，沒有接到原小盒，不宣稱 ISO 螺紋、製造、配合或強度合格。',
        '檔案對話框欄位由程式填寫；原圖視角部分較遠，細節需輔以讀值，不可自行推斷畫面所未呈現的細節。',
        '材料、切片、實際列印、量測、試配和允許間隙仍待實證。',
    ],
    'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None,
    'qualifiedClearance': None, 'qualifiedStrength': None,
    'steps': steps,
}
out = root / 'learning/lesson11_external_optional_steps_v001.json'
if out.exists():
    raise FileExistsError('Preserve existing lesson version; choose a new filename.')
out.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Wrote {out.relative_to(root)} with {len(steps)} verified original screenshots.')
