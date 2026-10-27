# 快速方法情境與模式誤按修正交接 v002

2026-10-27。使用者轉交 Claude：快速方法 v001 審查通過，要求 Codex 修正兩處意見，再交 Claude 審查。本文件只記本輪實作與核對，不代 Claude 核准 v002。變更仍留工作樹，未 stage、commit、push 或學員 confirm。

## 接續與分工

開工依 AGENTS 讀最新 shortcuts-handoff-v001、README、catalog、progress、相關04／05／07 journal與runtime交接，再 status：revision6、01-01、確認0、登記檔案0；收工維持同狀態。助教示範仍到08-01，08-02未做。

Codex/root唯一整合v002註記、catalog、AGENTS、候選清單及本交接；mode_error_runtime唯一執行獨立Blender、新劇本／原圖／核驗索引；mode_template_audit只新增修正前v001的逐項範本審查，之後只讀核對四項新文字；mode_annotation_tests改套用工具與測試。沒有同時執行會重建catalog／metadata的程式。

## 範本核對及修改範圍

[範本審查](../annotations/shortcut-template-audit-v002.json)逐項讀75個快捷方法與常規where／do／see，158次既有引用SHA皆相符。頂面effect只出現04-04第2項及04-06第2項：前者正確，後者修正；沒有找到額外實質錯置。其他71項情境無問題，三項依本輪要求補誤按提醒。

[guide-shortcuts-v002.json](../annotations/guide-shortcuts-v002.json)另存新版本，v001原bytes及其清單不改；entries仍75、coverage仍142（含67項未加），只修改四個guide的shortcut。舊來源／證據全部保留，新增Object Mode原生操作證據、版控review及逐項前後changeSet；每份文件／原圖均綁SHA。套用工具預設改讀v002，v002缺檔或驗證失敗不退回歷史v001。常規方法、成功條件、舊operationRun／previousOperationRuns及工程尺寸完全不改。

以下逐字列出本輪文字欄位前後；完整evidence新增明細與SHA在v002的changeSet，不覆寫舊證據。

### 04-06 第 2 項

`effect` 修改前：

- 在 Edit Mode 取消目前網格選取；本步若要點頂面，接著依常規方法只選頂面。

`effect` 修改後：

- 在 Edit Mode、邊選取模式按 Alt+A，取消全部網格選取；確認沒有反白，再接下一項 Select Non Manifold 檢查。

`requirements` 修改前：

- 滑鼠停在 3D Viewport 內，沒有文字／數值欄位正在編輯；先核對模式及選取。
- Edit Mode；先確認是本步指定的網格。

`requirements` 修改後：

- 滑鼠停在 3D Viewport 內，沒有文字／數值欄位正在編輯；先核對模式及選取。
- Edit Mode、邊選取（主鍵盤上排 2；Emulate Numpad 關閉）；先確認是本步指定的網格。

### 05-05 第 2 項

`cautions` 修改前：

- 新 probe 在獨立 Cube 用 I 0.2 m／E 0.4 m 驗鍵與拓樸讀回，不是重新製作上蓋或卡扣；原工程毫米尺寸仍以既有示範為依據。
- E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。

`cautions` 修改後：

- 新 probe 在獨立 Cube 用 I 0.2 m／E 0.4 m 驗鍵與拓樸讀回，不是重新製作上蓋或卡扣；原工程毫米尺寸仍以既有示範為依據。
- E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。
- 先確認左上是 Edit Mode。若仍在 Object Mode 按 I，本次出廠 Cube 實測會插入關鍵影格：Transform 欄變黃、時間軸出現菱形，並非 Inset。若剛誤按且尚未做其他操作，立即 Ctrl+Z，再核對欄位與時間軸回到誤按前；本次原本無動畫的 Cube 已實測復原。原本有動畫時需保留既有影格，不要整份刪除動畫。
- 本次出廠鍵位、3D Viewport、Object Mode 的 Cube 按 E，未找到對應啟用鍵位，實測網格、Transform、動畫及渲染範圍均未改變，也沒有擠出。沒反應時先核對模式再操作；沒有發生變更時不盲按 Undo。自訂鍵位或其他編輯區以實況為準。

證據：保留原 3 筆，新增 4 筆原圖／核驗引用。

### 07-02 第 1 項

`cautions` 修改前：

- 新 probe 在獨立 Cube 用 I 0.2 m／E 0.4 m 驗鍵與拓樸讀回，不是重新製作上蓋或卡扣；原工程毫米尺寸仍以既有示範為依據。
- E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。

`cautions` 修改後：

- 新 probe 在獨立 Cube 用 I 0.2 m／E 0.4 m 驗鍵與拓樸讀回，不是重新製作上蓋或卡扣；原工程毫米尺寸仍以既有示範為依據。
- E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。
- 先確認左上是 Edit Mode。若仍在 Object Mode 按 I，本次出廠 Cube 實測會插入關鍵影格：Transform 欄變黃、時間軸出現菱形，並非 Inset。若剛誤按且尚未做其他操作，立即 Ctrl+Z，再核對欄位與時間軸回到誤按前；本次原本無動畫的 Cube 已實測復原。原本有動畫時需保留既有影格，不要整份刪除動畫。
- 本次出廠鍵位、3D Viewport、Object Mode 的 Cube 按 E，未找到對應啟用鍵位，實測網格、Transform、動畫及渲染範圍均未改變，也沒有擠出。沒反應時先核對模式再操作；沒有發生變更時不盲按 Undo。自訂鍵位或其他編輯區以實況為準。

證據：保留原 3 筆，新增 4 筆原圖／核驗引用。

### 07-02 第 2 項

`cautions` 修改前：

- Ctrl+B 只做網格邊 Bevel，不等於新增 Bevel 修改器。這次新 Cube probe 用 0.1 m、預設段數驗鍵，沒有重新核卡扣 0.6 mm／3 段的工程結果；看原 operationRun。
- 倒角量是草案，不能由 Bevel 成功推定強度改善或合格。

`cautions` 修改後：

- 在 Edit Mode，Ctrl+B 做網格邊 Bevel，不等於新增 Bevel 修改器。這次新 Cube probe 用 0.1 m、預設段數驗鍵，沒有重新核卡扣 0.6 mm／3 段的工程結果；看原 operationRun。
- 倒角量是草案，不能由 Bevel 成功推定強度改善或合格。
- 若仍在 Object Mode 按 Ctrl+B，會進入 Render Region（渲染範圍）框選，出現十字虛線，而非邊倒角。尚在框選時按 Esc 或滑鼠右鍵取消；本次一般透視與相機視圖均已實測，取消後保留原邊框設定。
- 若已完成框選，本次一般透視下 Ctrl+Z 未還原視圖渲染範圍；相機視圖下立即 Ctrl+Z 則恢復原場景邊框。兩種視圖都已實測可按 Ctrl+Alt+B 清除 Render Region，停用範圍並將邊界重設為 0～1。清除也會移除原有範圍，若本來有設定，需依誤按前紀錄核對還原，不能當作保留原設定的取消。

證據：保留原 3 筆，新增 14 筆原圖／核驗引用。


## 獨立 Blender 實測及證據

出廠設定、隔離設定目錄、Blender5.2.1 LTS／build9e2066aef7ef，透過既有run_demo.py與Window.event_simulate執行。Python只讀狀態與寫本次evidence，不直接變更幾何／動畫／邊框冒充按鍵。沒有使用學員視窗或實體滑鼠，沒有存Preferences、.blend、STL或workspaces。

新證據位於 learning/evidence/01/2026-10-27-shortcut-mode-errors-demo-v001/（16張）及同前綴v002/（20張）；每個目錄的 shortcut-mode-errors-verification-v001.json 保存events、expected、actual、passed與每張原圖SHA，factory-keymap-mode-errors-v001.json是實際出廠鍵位表。全部36張由runtime代理逐張view_image；root另查看I插幀、Undo及Ctrl+B模態原圖。原生來源快照、run、JSON及PNG雜湊均核對。

| 行為 | 實讀及可教的處理 | 主要case與原圖 |
| --- | --- | --- |
| Object I | CubeAction；location／rotation_euler／scale各3軸，共9通道各1個key點，全部在frame1。Transform變黃、時間軸出現第1格菱形；不是9個不同時間格。 | v001 object-i-keyframe；shortcut-mode-02-object-i-keyframe.png |
| I後立即Ctrl+Z | animationData=false、action=null、allActions=[]；欄位恢復灰色、時間軸標記消失，原網格／Transform不變。只核原本無動畫的Cube與立即Undo，不教整份刪動畫。 | v001 object-i-undo；shortcut-mode-03-object-i-undo.png |
| Object E | 未修飾E在本次出廠3DViewport／Object Cube情境沒有對應啟用鍵位；實送後mesh、Transform、animation、選取、模式及模態無變化。不得推及其他編輯器／自訂鍵位。 | v001 object-e；shortcut-mode-04-object-e.png |
| Ctrl+B未完成框選 | 原生modal為VIEW3D_OT_render_border，畫面白色虛線十字，狀態列Esc Cancel。透視與相機各自Esc／右鍵取消後modal清空、原邊框不變。 | v001 perspective-border-invoke-esc／esc／rmb；camera-border-invoke／esc／rmb |
| 透視完成框選及Undo | 改viewRenderBorder；Ctrl+Z後enabled仍true，四邊值完全相同，沒有還原。 | v002 perspective-border-complete／undo |
| 相機完成框選及Undo | 改sceneRenderBorder；立即Ctrl+Z後false且四邊回0／1。 | v002 camera-border-complete／undo |
| 完成框選後Ctrl+Alt+B | 從實際出廠Clear Render Region鍵位送鍵；透視及相機均有true→false、邊界回0／1的前後對照。這會清除已有範圍，不能當保留舊設定的取消。 | v002 perspective-border-before-clear／clear；camera-border-before-clear／clear |

v001有9個斷言通過、7個觀察，v002有12個斷言通過、8個觀察，合計21過、15觀察、0失敗。passed:null未計為通過。兩次runner completed／exit0／runErrors空白，前後工作區內容一致；此比較不證明期間未寫入或判定寫入者，learnerWorkspaceWrites保持未知。原始runner-status含Recent清單，留本機，候選公開包只用另存的刪節摘要。

## 補驗版本與限制

v001最後的Clear發生於相機Undo已將region關閉之後，只能證沒有範圍時執行該指令，不足以證明清除已啟用範圍。保留整份v001及其有效I／E／取消證據，不將整個run標失敗或改寫passed。v002補上透視Undo及兩種視圖真正啟用→清除的對照；縮小補驗訊息抵達前完整版v002已啟動，因此重複部分I／E。重複如實保留，沒有覆寫v001，也沒有再開第三個run。

runtime的完整核對與來源SHA見 [新核驗索引](../annotations/shortcut-mode-errors-runtime-review-v001.json)及[執行交接](2026-10-27-shortcut-mode-errors-runtime-v001.md)。這些是助教模式誤按probe，不能代工程幾何重驗、學員完成或實體合格。

## 檔案變更及理由

- learning/catalog.json：只更新04-06第2項effect／requirements；05-05第2項、07-02第1／2項cautions／evidence，其他欄不變。
- learning/annotations/guide-shortcuts-v002.json：保留v001另建修正註記，逐欄前後對照及新來源SHA。
- learning/annotations/shortcut-template-audit-v002.json：固定修正前v001的75項範本盤點，不事後改寫成新版本已審核。
- learning/annotations/shortcut-mode-errors-runtime-review-v001.json：兩新run的原圖／讀值／來源核驗與限制。
- learning/tutor/scenarios/shortcut_mode_errors_probe.py：新增原生誤按、取消／Undo／Clear事件劇本；未修改舊劇本或共用runner。
- learning/evidence/01/2026-10-27-shortcut-mode-errors-demo-v001/與v002/：新run、36原PNG、兩核驗JSON、實讀keymap與凍結來源。逐檔公開／省略見新清單。
- scripts/apply_guide_shortcuts.py：預設選v002，修改共用工具是為使用本輪更正註記；舊註記不覆寫。
- learning/tutor/tests/test_guide_shortcuts.py：原13項不放寬，另加v002無效不回退v001，共14項。
- learning/tutor/tests/test_shortcut_mode_cautions.py：新增10項，核四項窄delta、情境、提醒、原圖SHA、I／E／Border實讀及Clear前提。
- scripts/prepare_publication.py：本輪改產shortcuts-v002候選manifest／pathspec，v001及更早清單原bytes保留。
- AGENTS.md：更新本輪授權、負責範圍、交接及候選清單連結；核心教學與原件保護規範保留。
- docs/shortcuts-checks-2026-10-27-v002.json、本交接、新runtime交接、新候選manifest／pathspec：本輪測試、逐字前後、資料邊界及交接。

本輪沒有修改Claude的原有劇本、原始run／metadata，亦未修改前端app.js／CSS或舊observedKind政策。

## 驗證

server／bootstrap30：28過、2skip；tutor307：306過、1skip；前端14／14，Node語法通過。skip均為本Windows帳戶缺symlink建立權限，junction檢查另過。使用本機Python3.12.14，沒有聲稱已跑hosted CI的3.10／3.13矩陣。快捷註記及既有語義verifier皆只讀通過。正式renderShortcut離線渲染75／75，180筆證據連結及完整SHA皆呈現，不連網或寫progress；本輪未新增瀏覽器畫面／console抽查，不把Claude轉交的v001畫面審查當v002結果。

對開工基線比對2,193個受保護既有檔（其中2,077 evidence檔），0不符。catalog只有指定四個shortcut不同；常規方法、成功條件與所有operationRun／previousOperationRuns完全一致。progress SHA仍26130175ef80a9fb83699f93a8c33de7b098b17ffa2c10aef794808390d19325；HEAD仍4b613f47c91f8eca51cf357097670718d8d31a77，index空，未stage／commit／push。以命令限定cr-at-eol做git diff --check通過，未修改Git設定或正規化原檔。

候選清單另存為 docs/publication-manifest-2026-10-27-shortcuts-v002.json 及同版pathspec，保留全部舊清單。新候選1,288路徑（1,286個雜湊檔，manifest／pathspec自我雜湊排除）；原工作樹只讀verify通過。只複製allowlist到新隔離公開副本，沒有progress或原始runner-status；公開副本的發布雜湊、快捷註記、既有語義verifier皆通過，新增模式回歸10／10也通過，未補回Recent或private原件。

## 接續

Claude審查本輪四項文字及新證據，特別核對立即Undo的前提、E的情境限制、Ctrl+B取消／Undo／清除差異。先讀本交接與AGENTS，再status；只讀執行scripts/apply_guide_shortcuts.py、scripts/apply_evidence_semantics.py及scripts/prepare_publication.py --verify。學員仍在01-01，工程08-02仍未做，不由助教probe推進。推送與否由使用者決定。
