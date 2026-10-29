"""Prepare portable teaching records from the verified GUI evidence; no progress mutation."""
from hashlib import sha256
from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
source = root / 'learning/evidence/08/2026-10-28-manual-boss-gui-trial-v003/safe-summary-v001.json'
target = root / 'learning/lesson11_boss_optional_steps_v001.json'
expected = 'fca3e4165b653cb517b1516e42f57cff2c3b6b2771490e329e5c9e035bb6981c'
if sha256(source.read_bytes()).hexdigest() != expected:
    raise ValueError('安全摘要來源已變更')
if target.exists():
    raise FileExistsError(target)
evidence = json.loads(source.read_text(encoding='utf-8'))
specs = [
    {
        'goal':'以副本開啟既有小盒參照',
        'context':'請先保留原檔，將來源 blend 複製到自己的練習資料夾；在 Blender 3D 視窗以 Ctrl+O 開啟該副本。示範以獨立 Blender 及隔離資料夾執行。',
        'operation':['在檔案管理器複製來源 blend，不要覆蓋原檔。','切換至 Blender，按 Ctrl+O，選擇副本並開啟。'],
        'success':'場景顯示小盒參照，Outliner 活動物件為 Body_Reference；尺寸讀回約 X 60、Y 40、Z 30 mm。',
        'readings':[{'location':'Blender Object Properties 或 3D View 側欄 Item 的 Dimensions；數值另由 Blender 程式讀回','value':'60 × 40 × 30 mm','source':'safe-summary.records[0].observed.dims'}],
        'limits':['若來源不存在，需先取得專案中的來源檔；不可默認用不同場景。','此時尚未建構螺絲柱。']
    },
    {
        'goal':'隱藏盒體並新增 32 邊圓柱',
        'context':'確定 Object Mode 且 Body_Reference 已選取；本示範 Unit Scale 為 0.001，Blender 版本為 5.2.1 LTS。',
        'operation':['滑鼠移至 3D View，按 H 隱藏已選盒體。','按 F3，搜尋 Add Cylinder，按 Enter。'],
        'success':'Outliner 的活動物件變成 Cylinder；數位尺寸約 2000 × 2000 × 2000 mm，原盒只是隱藏。',
        'readings':[{'location':'Blender 3D View 側欄 Item → Dimensions；數值由 Blender 程式讀回','value':'1999.999878 × 1999.999878 × 1999.999878 mm','source':'safe-summary.records[1].observed.dims'}],
        'limits':['若預設圓柱尺寸、邊數、單位或場景設定不同，停止並先確認，不可直接套用下一步的縮放倍率。']
    },
    {
        'goal':'將圓柱設為 8 mm 外形',
        'context':'仍在 Object Mode，Cylinder 已選取，且上一個 2000 mm 的前提已確認。',
        'operation':['在 3D View 依序按 S、輸入 0.004、Enter。','按 F3，搜尋 Apply Scale，按 Enter。','依序按 G、Z，輸入 4mm，按 Enter。'],
        'success':'側欄 Dimensions 約 8 × 8 × 8 mm，Scale 為 1、1、1，Location Z 為 4 mm。',
        'readings':[{'location':'3D View 側欄 Item → Transform；數值由 Blender 程式讀回','value':'Dimensions 約 8.000015 × 8.000015 × 8.000015 mm；Scale 1、1、1；Location Z 4 mm','source':'safe-summary.records[2].observed'}],
        'limits':['畫面常將小數四捨五入為 8 mm；此為數位草案尺寸。']
    },
    {
        'goal':'選取圓柱頂面',
        'context':'保持 Cylinder 已選取，滑鼠在 3D View；數字鍵盤 7 使用頂視，面選取使用主鍵盤 3。',
        'operation':['按 F3 搜尋 Frame Selected 並確認；按數字鍵盤 7 切頂視。','按 Tab 進入 Edit Mode，按主鍵盤 3 切面選取。','按 Alt+A 取消所有選取，再點擊圓柱頂面。'],
        'success':'只有柱頂單一面被選取；Blender 腳本讀回選取面數 1，該面中心 Z 約 8 mm。',
        'readings':[{'location':'示範截圖可看選取；面數與世界座標是 Blender 程式讀回，不是畫面直接顯示','value':'selectedFaces = 1；faceCenterZ = 8.000007629 mm','source':'safe-summary.records[3].observed'}],
        'limits':['若選到側面或多個面，先取消選取並重新確認，勿繼續內插。']
    },
    {
        'goal':'內插建立孔口輪廓',
        'context':'在 Edit Mode 且僅有柱頂面被選取。',
        'operation':['按 I，輸入 2mm，按 Enter。'],
        'success':'頂面產生內側輪廓並保留單一內側面；擷取網格的孔口對頂點距離約 3.980661 mm。',
        'readings':[{'location':'畫面可見頂面內插輪廓；對頂距離由 Blender 網格頂點程式讀回','value':'3.980661392 mm（32 邊形對頂點）','source':'safe-summary.geometryReadback.oppositeVertexHoleWidthMm'}],
        'limits':['內插 2 mm 不等於孔口精確 4 mm。此值不是已確認的五金孔徑或公差。']
    },
    {
        'goal':'向下擠出形成盲孔',
        'context':'Edit Mode 下保留內插出的內側面為選取狀態。',
        'operation':['按 E，輸入 -7mm，按 Enter。','按 Tab 回 Object Mode；可旋轉到斜視，確認看見孔口。'],
        'success':'畫面可見盲孔外觀，側欄 Dimensions 約 8 mm；程式射線讀回孔底 Z 約 1 mm、頂面 Z 約 8 mm。',
        'readings':[{'location':'側欄 Item → Dimensions 顯示圓柱外框；孔底及頂面由 Blender 腳本射線讀回','value':'外框各約 8.000015 mm；孔底 Z 1.000007629 mm；頂面 Z 8.000007629 mm','source':'safe-summary.records[5].observed'},{'location':'Blender 程式網格檢查','value':'128 頂點、98 面、非流形邊 0','source':'safe-summary.records[5].observed'}],
        'limits':['畫面不能單獨證明孔底深度；射線及非流形邊檢查也不能證明無自相交或可製造。','這是獨立柱，未與盒體接合。']
    },
    {
        'goal':'以新名稱另存草案',
        'context':'盲孔柱已完成數位草案；選擇自己的練習資料夾，不覆蓋原參照。',
        'operation':['在 Blender 選 File → Save As，選練習資料夾並輸入新的 .blend 名稱。','按 Save As Blender File；若有另存確認，核對新檔名後確認。'],
        'success':'新檔存在且柱仍保留；示範另存後的外框、孔底射線和非流形邊檢查均有讀回。',
        'readings':[{'location':'示範另存後 Blender 程式檢查；檔案名稱及雜湊見 outputScene','value':'8.000015 mm 外框；孔底 Z 1.000007629 mm；非流形邊 0','source':'safe-summary.records[6].observed'}],
        'limits':['示範的路徑與檔名由自動化程式填入；手動操作請自行選擇。','勿覆蓋既有檔案；你的檔案雜湊不必與示範相同。']
    },
    {
        'goal':'重開新版本並確認',
        'context':'已另存自己的新檔。',
        'operation':['按 Ctrl+O，選擇剛另存的檔案並開啟。','確認場景仍有柱，側欄顯示外框尺寸；保留你的檔案版本紀錄。'],
        'success':'柱與孔口仍可見、側欄尺寸約 8 mm；示範重開後由程式再次核對幾何與孔底。',
        'readings':[{'location':'側欄 Item → Dimensions；其餘為重開後 Blender 程式讀回','value':'外框各 8.000015 mm；孔底 Z 1.000007629 mm；非流形邊 0','source':'safe-summary.records[7].observed'}],
        'limits':['重開示範讀值只證明該示範檔，學員需自行確認自己的檔案。','實體列印、量測、試配、材料、五金、公差與強度均未確認。']
    }
]
records = evidence['records']
if len(records) != len(specs):
    raise ValueError('畫面數量與步驟不符')
steps = []
for i, (spec, record) in enumerate(zip(specs, records), 1):
    pic = root / record['relativePath']
    if sha256(pic.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('截圖 hash 不符')
    steps.append({'id': f'11-BOSS-OPT-{i:02}', **spec, 'screenshot': {'relativePath': record['relativePath'], 'sha256': record['sha256'], 'capture': 'isolated Blender original screenshot'}, 'confirmed': False})
result = {'schemaVersion':1, 'id':'lesson11-boss-optional-v001', 'title':'獨立盲孔柱：GUI 逐步練習草案', 'status':'optional-draft-not-learner-progress', 'sourceSummary':{'relativePath':source.relative_to(root).as_posix(), 'sha256':expected}, 'sourceScene':evidence['sourceScene'], 'demoOutputScene':evidence['outputScene'], 'blenderVersion':evidence['blenderVersion'], 'scope':'獨立盲孔柱幾何練習；盒體隱藏，尚未接合。此模型不是依指定五金選型的正式設計。', 'physicalResults':{'material':None, 'hardware':None, 'print':None, 'measurement':None, 'fit':None, 'strengthQualification':None}, 'steps':steps}
target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(target.relative_to(root).as_posix(), sha256(target.read_bytes()).hexdigest())
