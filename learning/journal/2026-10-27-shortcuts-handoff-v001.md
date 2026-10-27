# 快速方法補充與三項審查意見交接 v001

2026-10-27。依本輪轉交的使用者要求實作，候選留工作樹供 Claude 審查；沒有 stage、commit、push 或學員 confirm。使用者轉交「上一項審查通過」是上輪結果，不是本輪新功能的審查核准。

## 接續狀態及分工

開工讀 AGENTS、上輪交接、README、catalog、progress 及相關單元紀錄；開工／收工 manage.py status 均為 revision 6、01-01、確認 0、登記檔案 0。助教示範仍到 08-01，08-02 未建模，未以快捷鍵測試推進學員或工程位置。

Codex/root 唯一編輯 catalog、整合版控註記與候選發布清單；shortcut_existing 盤點既有原圖、實作只加 guide.shortcut 的工具／測試並審閱文字；shortcut_runtime 唯一執行隔離 Blender、凍結來源與新證據；shortcut_frontend 負責 app.js／CSS／前端測試及 CI。沒有同時執行重建 catalog／metadata 的程式。

## 三項意見的處理及理由

1. AGENTS 現行規範補六行常用命令（status、confirm --evidence、note --author、register-file、add-lessons、run_demo），解釋 --revision 用最新 status 值來拒絕過期寫入，衝突先停而非盲目重試。命令範例不構成本輪執行 confirm 的授權，歷史快照僅留歷史。
2. 工作區已有 workspaceEvidenceNote 時，前端只顯示「一致／不同／未知」及原註記一次；沒有註記時仍完整說明快照比較限制。仍不把內容一致反推未寫入或判定寫入者。已增加重複句回歸檢查。
3. AGENTS 授權改成本輪快速方法／缺證補驗與三項意見修正，保留所有原件、進度與不提交／推送限制，最新交接指到本檔。

## 新資料及畫面

逐項核對 01～09 共 142 個 guide，38 個步驟的 75 個 guide 新增選用 shortcut；其餘 67 個逐項記原因。原 do／where／see／成功條件及整份 operationRun／previousOperationRuns 完全不改。快速方法呈現在常規方法之後，有按鍵、效果、模式／焦點、注意事項、可展開的驗證依據及完整 SHA-256。

版本化資料為 [guide-shortcuts-v001.json](../annotations/guide-shortcuts-v001.json)。entries 用 step、零起算 guideIndex、原常規 guide 的 canonical SHA-256 綁定；coverage 包含每個加入或略過項及理由。五份來源文件與所有 evidence 均綁雜湊。scripts/apply_guide_shortcuts.py 預設只讀核對，只有 --write 才只更新受註記綁定的 guide.shortcut，先核對檔案／路徑及寫前 catalog bytes，衝突停止。

9 張既有選單原圖支持 18 種鍵標，盤點另有 2 張因沒有鍵標而未使用；[既有原圖盤點](../annotations/shortcut-existing-evidence-v001.json)明確標 menu_label_visual，只證畫面標示，不冒稱本次按鍵。新三個成功隔離 run 共 53 原始 PNG，43 個程式斷言通過、9 個觀察案例另列；詳 [新證據核驗](../annotations/shortcut-runtime-review-v001.json)及[執行交接](2026-10-27-shortcut-runtime-verification-v001.md)。被核的 Blender 為 5.2.1 LTS／9e2066aef7ef；沒有改學員 Blender。

01-07 明列 G X 0.5 是再移 0.5 m；0→0.5、1→1.5、負數向負方向；欄位則直接設定絕對值。無軸 G .5 在這次 Object Mode／Global／出廠透視確實改 X，但教學仍明寫 X。Esc／右鍵在 Enter 前取消直接用 G 實測，不把未測的其他取消情境當成同樣已測。01-08 的 S X 1.5 是倍率、2→3 m，不是設成絕對尺寸 1.5。

R 為相對旋轉，並未將通用 Cube 測試冒充 Camera 或工程候選重新驗證。06-02 特別說 X0→30→62→0 的位移差是 +30／+32／−62 mm；不能連加30和62。I／E／Ctrl+B 的新 probe 是 Metric、Unit Scale 1 的公尺測試，工程毫米參數與段數仍引用原常規方法／原 operationRun，沒有重跑工程幾何或推定改善。

數字鍵盤與主鍵盤分欄說明：Numpad . 為 Frame Selected；主句點實拍開 Pivot Point。Numpad 0 切相機，主 2／3 在 Emulate Numpad 關閉的 Edit Mode 為邊／面選取。01-06 提示筆電可在 Preferences > Input > Keyboard 找 Emulate Numpad；原生 tooltip 說明主 1～0 用作數字鍵盤。隔離環境 checkbox 讀回 true，但模擬 plain／unicode ONE 未產生 Front View，故實體鍵盤重映射仍未驗證，保留 View > Frame Selected 方法，沒有把 UI 已勾當成效果已通。

## 每個加入位置（操作編號從 1 起算）

下表每項的各別證據原圖、SHA-256、方法及模式條件都在版控註記及對應 guide.shortcut 中；不是只有共同的一份未綁定清單。

| 步驟 | 操作編號：快速方法 |
| --- | --- |
| 01-02 | 1：Ctrl+, |
| 01-03 | 1：Ctrl+N → General |
| 01-04 | 1：Shift+Ctrl+S |
| 01-05 | 1：Tab |
| 01-06 | 3：Numpad . |
| 01-07 | 1：Shift+Ctrl+S<br>2：G → X → 0.5 → Enter；取消：Esc／滑鼠右鍵；側欄：N<br>3：Ctrl+Z |
| 01-08 | 1：N<br>2：S → X → 1.5 → Enter |
| 01-09 | 1：Ctrl+S<br>3：Ctrl+O |
| 02-01 | 2：X → 核對 Delete 確認<br>3：Shift+Ctrl+S |
| 02-02 | 1：Shift+A → Mesh → Plane<br>2：Shift+A → Mesh → Cube |
| 02-03 | 1：Shift+A → Mesh → Cube |
| 02-04 | 1：F2 → BeaconBase → Enter<br>2：M → New Collection<br>3：Shift+Ctrl+S |
| 02-05 | 1：Ctrl+N → General；Shift+Ctrl+S |
| 02-06 | 1：N |
| 02-07 | 1：Ctrl+S<br>2：Ctrl+S<br>3：Ctrl+O |
| 03-01 | 1：Ctrl+O<br>2：Shift+Ctrl+S |
| 03-02 | 2：Numpad 0<br>3：G → X／Y／Z → 位移量 → Enter；R → X／Y／Z → 角度 → Enter |
| 03-05 | 1：Ctrl+S<br>2：F12 |
| 03-06 | 1：Ctrl+O<br>3：F12 |
| 04-02 | 1：Ctrl+N → General<br>3：Shift+Ctrl+S |
| 04-03 | 1：N<br>2：Ctrl+A → Scale |
| 04-04 | 1：Tab → 主鍵盤上排 3<br>2：Alt+A<br>3：X → Faces |
| 04-05 | 1：Tab |
| 04-06 | 2：Alt+A<br>3：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 05-02 | 1：Shift+Ctrl+S<br>2：Ctrl+A → Scale |
| 05-03 | 1：Shift+A → Mesh → Cube<br>2：Shift+D；Ctrl+J<br>3：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 05-04 | 1：Ctrl+O<br>2：Numpad .；N |
| 05-05 | 1：Shift+A → Mesh → Cube<br>2：I → 厚度 → Enter；E → 沿面法向位移 → Enter<br>3：Shift+Ctrl+S |
| 05-06 | 1：Ctrl+O<br>3：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 06-01 | 1：Shift+A → Mesh → Cylinder<br>2：Shift+A → Mesh → Cylinder<br>3：Shift+Ctrl+S |
| 06-02 | 4：G → X → 位移差（本場景 mm）→ Enter |
| 06-03 | 1：Ctrl+O<br>2：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 07-01 | 1：N |
| 07-02 | 1：I → 厚度 → Enter；E → 沿面法向位移 → Enter<br>2：主鍵盤上排 2；Ctrl+B → 0.6 → Enter<br>3：Shift+Ctrl+S |
| 07-03 | 1：R → Y → 90 → Enter；R → X → 180 → Enter<br>2：Tab<br>3：Shift+Ctrl+S |
| 07-04 | 1：Ctrl+O<br>3：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 07-05 | 1：Ctrl+O<br>3：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold |
| 08-01 | 1：F2 → Body_Reference → Enter；N<br>2：主鍵盤上排 2 → Alt+A → F3 → 搜尋 Select Non Manifold<br>3：Shift+Ctrl+S |


## 未加入與失敗版本

辨認畫面、特定欄位、絕對 Dimensions、來源／登記、實體量測及規格決策沒有等效的本批快捷鍵，不硬塞；08-02～08-05 尚未有相應實作，09 為實測／總組裝，不宣稱補成已完成。A 全選雖已測，但只選 Cube 的步驟不能用全選代替。Numpad 5、Home 雖有鍵標，與本步 Frame Selected 目的不同，未作等效替代。Edit Mode 複製、Rendered 快捷鍵及 PNG 的 Image Save As 沒有本輪足夠證據，維持原方法；Object Mode Shift+D 的證據不冒充 Edit Mode 複製。Ctrl+A 只開 Object Apply，不能當修改器 Apply；Ctrl+J 也不是 Boolean Union。

keyboard-demo-v001 的 Emulate Numpad 主 ONE 應轉 Front 的嚴格斷言失敗，原件保留。v002 不把該要求放寬為通過，只記 plain／unicode 都未重現，另完成主句點與 Numpad . 對照；失敗 run 不列成功示範，原始 runner-status／Recent 等仍只在本機。沒有刪除、改舊截圖或補回舊證據。

## 本輪變更檔案及理由

- AGENTS.md：現行六命令、revision、授權與新交接／候選清單。
- learning/catalog.json：僅新增 75 個 guide.shortcut。
- learning/web/app.js、app.css：快速方法呈現與工作區註記去重，修改共用前端是為落實本輪教材與審查意見；不改前輪 observedKind 政策。
- .github/workflows/verify.yml：保留所有檢查，新增只讀 shortcuts verifier，前端測試涵蓋兩檔。
- scripts/apply_guide_shortcuts.py、learning/tutor/tests/test_guide_shortcuts.py：完整 coverage／雜湊／路徑／協作防衝突與只改快捷欄位的 13 項測試。
- learning/web/tests/observation_labels.test.js、shortcuts.test.js：去重、常規方法保留、HTML 跳脫、安全證據連結與未驗證不顯示。
- learning/annotations/shortcut-existing-evidence-v001.json、shortcut-runtime-review-v001.json、guide-shortcuts-v001.json：既有鍵標、新事件核驗及逐項編輯註記。
- learning/tutor/scenarios/shortcut_probe.py、shortcut_keyboard_probe.py、shortcut_mesh_probe.py：只對缺證的鍵新增獨立 Blender 事件。
- learning/tutor/scenarios/shortcut_runtime_index.py：只讀本機完整原件的鑑識工具；需私有 runner-status 及失敗 run，公開 clone 缺檔即停，不加入 CI、不為它重新公開私人資料。
- learning/evidence/01/ 三個成功新 run、保留失敗 keyboard v001：原生 PNG／run／凍結來源／核驗 JSON；逐檔公開與省略邊界由新候選清單列明。
- scripts/prepare_publication.py：本輪改產 shortcuts-v001 新清單，保留 2026-10-26 及 2026-10-27 上輪 bytes，沿用原來私有資訊與摘要版本規則。
- 本交接、runtime 交接、docs/shortcuts-checks-2026-10-27-v001.json、新 publication manifest／pathspec：本輪交接、實際結果及候選雜湊。上輪交接、註記及原 evidence 不改。

## 驗證與界限

- server／bootstrap 30：28 過、2 skip；tutor 296：295 過、1 skip（新增13項全部通過）；skip 均為本 Windows 無 symlink 權限，junction 檢查另過。前端14／14，Node語法、兩份 annotation verifier 全過。使用本機 Python 3.12.14；沒有聲稱已在 hosted CI 的 Python 3.10／3.13 跑過。
- 離線使用正式 renderShortcut 對實際 catalog 的 75 個快捷欄位逐項渲染，75／75 顯示、158 個證據連結及完整 SHA 均存在；不連網、不啟動頁面或寫 progress。此檢查不取代瀏覽器外觀抽查。
- 本輪新候選清單 1,225 路徑（1,223 個雜湊檔，manifest／pathspec 自身排除雜湊）；原樹只讀 verify 通過。只複製 allowlist 到新隔離目錄，確認不含 progress／raw runner-status，再執行公開包雜湊、快捷註記及既有語義驗證，三項全過；沒有為了通過把 Recent、失敗 run 或 private 基線加入公開包。
- 原生 `git diff --check` 把現有 `* -text` 保留的 CRLF 判成 trailing whitespace；未正規化原檔。以本次命令限定的 `git -c core.whitespace=cr-at-eol diff --check` 重檢通過，沒有改 Git 設定，也未放寬行尾以外的空白檢查。
- 對開工私人基線重算 1,988 個受保護既有檔（其中 1,981 evidence 原檔），0 不符；把新 shortcut 欄移除後，完整 catalog 與本輪開工逐欄相等，故舊 operationRun／previousOperationRuns／常規教學完全一致。
- progress SHA-256 仍 26130175ef80a9fb83699f93a8c33de7b098b17ffa2c10aef794808390d19325；HEAD 仍 4b613f47c91f8eca51cf357097670718d8d31a77，index 無 stage，沒有 commit／push。工作區前後內容一致仍不是未寫入或寫入者證明。
- 瀏覽器 origin 權限檢查未核准 http://127.0.0.1:8766/ 的內容讀取，所以沒有瀏覽器畫面／console 抽查；未改走其他方式繞過此限制。前端驗證僅離線 renderer、Node 測試與隔離 server 測試，不稱已檢視實際網頁外觀。
- 本輪不做學員確認、列印、試配、強度／配合合格判定；材料與允許應變待定，工程草案與候選狀態未改。新圖片是助教鍵位 probe，不是學員成果。

## 交給審查者的下一步

先讀本檔及目前 AGENTS，再 status；用 scripts/apply_guide_shortcuts.py 與 scripts/apply_evidence_semantics.py 只讀核對，依新候選 manifest 做公開包雜湊檢查。請審查常規方法／快捷方法的目的是否對應、模式及單位是否充分、Emulate 的未驗效果是否如實標明；瀏覽器畫面抽查仍待授權可用時完成。學員位置維持01-01，不得以本輪鍵位測試 confirm。推送與否由使用者決定。
