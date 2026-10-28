# Blender 引導式學習規範

以繁體中文教學。主線是學員 2026-10-28 選定的「小盒工程學習路徑」方案 B，12 章依序：01 基本操作與小盒用途、02 公差與量測觀念、03 毫米建模與必要編輯（含 Edit Mode 基礎、原盒、固定上蓋）、04 訊號站材質燈光渲染、05 配合試片、06 匯出列印量測與試配、07 草圖與約束、08 參數連動（受控面板為選修）、09 定位榫與燕尾、10 卡扣、11 螺紋、12 尺寸鏈交付與成品渲染。每章分節（章 → 節 → 小步）。學習進度以新版小步為準；原 9 單元 52 步只供查閱圖文與示範紀錄。以下規範生效；[2026-10-27 改寫前的完整位元組快照](learning/journal/2026-10-27-agents-history-v002.md)與[更早的原文快照](learning/journal/2026-10-27-agents-history-v001.md)只保存歷史，不取代本檔、最新 journal 或當前進度。[逐項搬移映射](learning/annotations/agents-requirements-map-v001.json)列原文、位置及保留方式。

## 公開版接續

- 新 clone 先執行 `python learning/bootstrap.py`；合法既有 progress 只讀保留，不重設、不抄作者筆記。English (US)、revision 6 與歷史示範不是新讀者的畫面、選擇或完成狀態，以該 clone 的 progress／實際畫面為準。
- 最近一次已發布的候選邊界見 [快速方法修正清單](docs/publication-manifest-2026-10-27-shortcuts-v002.json)；較早清單留作歷史基線。不得為補引用重新加入 Recent 清單、private 基線或第三方 PDF 快取。原始證據不正規化換行，保留 `.gitattributes` 的 `* -text`；修改既有追蹤檔時沿用原本的換行格式，不整檔轉換。
- GitHub 目前停在 fa76461；工程教材 v002～v032、手工盒面板與本檔改寫都是本機未提交工作。發布前要重產發布清單，`prepare_publication.py --verify` 目前會因已修改的追蹤檔而失敗，屬預期。

## 目前接續位置：工程教材 v032（方案 B，章頁與節頁分開）

- 目前頁面 `learning/web/engineering-curriculum-v032.json` 與 `learning/web/engineering-path-v003.json`：12 章 81 節，主線小步 239 個、選修 11 個（第 08 章 08-08 受控尺寸面板）、待製作 6 個（第 11 章螺紋與螺絲柱，`track: "pending"`）、附錄 30 個（第 08 章）；穩定教材 ID 仍為 `engineering-curriculum-v002`。v031 依使用者要求為第 07～12 章 110 個主線小步補 `detail`，沿用既有證據而未逐步重新實拍；四個螺紋待實作步驟同步標明未完成。第 01～06 章的 135 個主線小步 detail 沿用 v030。v032 把第 11 章 6 個缺模型或示範、無法照做的小步改為待製作（可閱讀、不能確認、不計入、「前往下一小步」跳過），重複的「尚未逐步重新實拍」改為章層級 `detailNote`，「以可用工具核對」改為具體讀值位置（N 側欄 Item 的 Dimensions／Global 座標）。第 07～12 章的詳細步驟仍待學到該章時實際操作後改寫，做法同第 01～06 章。移動、改寫與拆分的對照見 `stepIdChanges`、`replacedSteps`、`contentReview.reviewV029`～`reviewV032`。
- 網頁版面（使用者選定，只做桌面版）：每章一頁 `#engineering/chNN`（精簡總覽「學什麼／做出／接續」＋小節目錄；實作、功能與快捷、限制、原教材參照、附錄收在「本章補充」，沒有表單）；每節一頁 `#engineering/chNN/NN-NN`，左為側欄（章連章頁、節連節頁），中為本節小步清單，一次只展開一步（目標、操作、成功畫面、確認與卡關筆記），右欄跟著所選小步顯示 6 個分頁：詳細步驟、原圖、快捷鍵、示範紀錄、注意、找不到按鈕。分頁數量待使用者看過後再定。「示範紀錄」分頁顯示原教材的完整紀錄（含原圖標示框、參數表、幾何與審查），與原教材頁相同。
- 方案 B 的關鍵順序：存檔在第 01 章；Edit Mode 基礎（點／邊／面、G、I、E、H、底部視角）在第 03 章原盒與上蓋之前；第 05～06 章先做試片、列印、量測、逐孔試配並選定自己的總間隙，第 07～08 章 CAD Sketcher 與參數上蓋才使用這個間隙（還沒試配時沿用 0.4 mm 試驗值）。新版第 01～06 章不需要第三方外掛。
- 新增步驟沒有實拍者標 `draft_pending_demo`（Edit Mode 基礎、Post／Signal、保存原盒、試片列印試配等）；拆自原教材的步驟標 `source_step_demo`，網頁從 catalog 顯示原步的排解說明與完整示範紀錄。介面名稱依 Blender 5.2.1 讀回核對，見 `reviewV029.uiEvidence`。
- 學習進度以新版小步為主：網頁頂端「前往下一小步」指向第一個未確認的主線小步；`python learning/manage.py status` 預設顯示新版主線進度與下一小步，`status --lesson <單元>` 才看原教材。網頁不再有原教材側欄、「原教材查閱」與「原單元總覽」頁籤；原教材頁只從小步「注意」分頁或章頁「本章補充」的參照按鈕開啟，只供查閱來源。`learning/catalog.json` 仍是 168 個新版小步的示範紀錄與排解說明來源，不能刪。檔案版本頁自己選單元工作區。選修可確認但不計入主線，待製作與附錄不能確認。
- 手工盒受控面板 `learning/tutor/guarded_manual_box_v001.py`（依賴 `manual_box_auto_update_v002.py`、`manual_box_reference_v001.json`）只接受指定示範盒 `manual_lid_shape_xy_driver_v001.blend` 的副本；原生欄位可繞過，原生 Save／Export 不受攔截，不自動存檔。X60～100／Y30～70 是形狀鍵未夾限的理論範圍，不是製造或配合合格範圍。面板版本及假專案測試維持凍結；使用者後續要求完成章節內容，因此新增教材 v031、v032，但未擴充面板。
- 學員共用進度：revision 8，新版 0／239。2026-10-27 第一題回答「是下方的環形唇邊」記在原 01-01 的筆記中，由 `manage.py` 的舊格式規則辨認，顯示在第 01 章章末「辨認蓋板與唇邊」（`legacyActivity`），不算 01-01 筆記也未確認任何小步；新回答一律用 `engineering-note`。
- 每章有一題課程練習（`learning/web/challenges/challenges-v005.json`），由 `/challenges/manifest.json` 提供，資料來源由 `manage.CHALLENGES` 指定；12 章都在同一個練習題頁 `/challenges/index.html?chapter=chNN`。第 03 章原試教頁已併入（`/pilot/box-lesson.html` 只轉址），題目資料以 `progressKind: "pilot"` 沿用原 `pilot_challenge_*` 事件與 `pilot-*` 指令，並附 G、X、5、Enter 動畫。其餘題目的確認與筆記保存在同一 `progress.json` 的 challenge 事件，與主線小步分開；`challenge-status` 供聊天讀取，僅學員明確回報才 `challenge-confirm`。第 02／03／05／06／07／08／09／10 章有已核對來源的題圖，其餘專屬題圖待補；題圖不是 Blender 操作截圖或實體合格證據。
- 最新交接：[v032 審查修正](learning/journal/2026-10-28-engineering-curriculum-v032.md)；前輪：[v031 章節練習與詳細文字](learning/journal/2026-10-28-engineering-challenges-v002.md)、[v030 章頁與節頁](learning/journal/2026-10-28-engineering-curriculum-v030.md)、[v029 方案 B](learning/journal/2026-10-28-engineering-curriculum-v029.md)、[v028 整體整理](learning/journal/2026-10-27-engineering-curriculum-v028.md)、[手工盒受控防護 v027](learning/journal/2026-10-27-manual-box-guard-delivery-v027.md)、[手工盒蓋 v021](learning/journal/2026-10-27-manual-box-delivery-v021.md)、[工程學習路徑 v001](learning/journal/2026-10-27-engineering-path-v001.md)、[快速方法修正](learning/journal/2026-10-27-shortcuts-handoff-v002.md)。

## 工程教材的版本與維護

- 目前版本只在 `learning/manage.py` 的 `ENGINEERING_CURRICULUM`、`ENGINEERING_PATH` 指定；伺服器以固定網址 `/engineering-curriculum.json`、`/engineering-path.json` 提供，網頁與測試不寫版本號，歷史版本不經網頁提供。換版只改這兩個常數。
- 新版本以 `learning/build_engineering_curriculum_vNNN.py` 從上一版產生，核對來源雜湊、拒絕覆寫，並附對應測試；歷史版本、builder 與測試保留原位（journal 有引用路徑），不刪不搬。只在學員可見內容改變時出新版本，不為每一次試驗出一版。
- 網頁顯示文字（章節狀態、備註、快捷狀態、環境摘要、步驟更正）寫在資料裡，不在前端程式依版本號或步驟 ID 替換。
- 題目與題圖同樣「只在學員可見內容改變時出新版本」：同一輪的多次修正併成一個版本，學員還沒看過的草稿直接改，不為每次小修出新號。伺服器只提供目前題目資料引用的題圖與動畫（`server.challenge_assets`），歷史版本留在原位但不經網頁提供。
- 發布：原始動畫影格、`frames.json`、`run.json`、`runner-status.json` 與 Blender log 含本機路徑或 Recent，由 `scripts/prepare_publication.py` 排除；公開 GIF、前後原圖與去識別摘要。失敗的 `2026-10-28-pilot-box-move-record-v001` 整個留在本機。
- 結構規則（`test_engineering_curriculum_v029.py`～`v032.py` 檢查）：章依方案 B 順序；每章分節，節 ID 為「章號-流水號」，主線與選修小步都屬於某一節並依節的順序排列；原單元 01／02／03 各自只在第 01／03／04 章；技能先教後用（例如 I、H、底部視角在第 03 章 Edit Mode 基礎之後才出現）；試片列印試配在 CAD Sketcher 之前；開發、失敗或假專案測試標 `track: "appendix"`、選修標 `track: "optional"`、缺模型或示範而無法照做的標 `track: "pending"`（不得留在主線）；`existing_demo` 必須有本步原圖或讀值檔；已改寫的第 01～06 章每步 1～3 個操作、不寫成示範報告。

## 協作規則

1. 開工先讀最新交接 journal、README、catalog、progress 及相關 journal，再執行 `python learning/manage.py status`，以最新狀態與學員畫面為準。
2. 每輪由使用者指定實作者與審查者（可為 Codex 或 Claude Code）；實作者負責實作、測試與單一發布窗口，審查者獨立核對。各範圍與實際檔案寫入交接。
3. catalog 與工程教材只由該輪實作者整合；未獲使用者新指示不得 commit 或 push。
4. 寫入前重讀最新檔案及所需 revision；遇衝突先停、核對，不盲目重試，不覆寫對方變更。
5. 不同時執行會重建 catalog、教材或 metadata 的匯入／發布程式；先完成並核對版本化註記，再依序更新匯入器、catalog、前端及驗證。
6. 收工寫交接 journal，列實際變更、驗證範圍、未完成、失敗版本與下一步；改到對方程式時另列修改理由。
7. 截圖、程式讀回、幾何檢查、學員理解與實體合格分別列依據；未分類顯示「觀察紀錄」，固定文字顯示「文字描述，請對照原圖」，混合紀錄另標，不靠句型猜測。

## 教學與真實畫面

- 每回合一個小目標、1–3 個操作及可見成功條件；學員回報後才往下，這是學習節奏而非重新索權。初次請學員開 Blender 並回報畫面，不假設首次設定、預設場景或已存檔；保留既有作品與未存內容。
- 操作前交代編輯區、模式、選取物件與輸入位置；卡關縮為一個操作，核對模式、選取、視角、焦點。按鈕名稱依當前截圖，不猜翻譯；未核對名稱明示以學員截圖為準。
- 不製作或引用示意圖。`figures` 只用 evidence 內真實存在的 `type: screenshot` 原圖，保留日期、原始像素、版本、來源 metadata；無圖只寫文字。局部放大或座標框須連回原圖，不重畫介面；看到圖不代表已操作或理解。
- 步驟依可讀聊天、catalog、journal、progress、evidence 及 sources/manifest.json 交叉核對；更新前讀相關文件與所有相關 journal、來源及實際畫面，`contentReview` 列範圍與依據。不將未實作寫成全驗證，或把助教建議寫成學員決定。
- 原則由學員操作；未經要求不代建模型、不外部改寫正開啟的 .blend、不把助教檔當學員成果。已授權的助教逐步實作須把一個目標做到可核對結果，不每按鈕索取回覆；逐次保存動作、原圖、結果，完成後更新 `operationRun`／journal。示範操作、介面觀察、學員確認分開，不由示範授權推定語言選擇、學員完成或可覆寫檔案。

## 獨立 Blender 與證據

- 示範預設走 `learning/tutor/`：`python learning/tutor/run_demo.py <劇本> <新 evidence 資料夾>`，獨立 Blender 事件模擬，不搶實體滑鼠；第二單元起共用 `scenarios/common.py`。僅學員要求核對自己的視窗或個別卡關時才考慮 Windows Computer Use。
- 逐步原生截圖與讀回，匯入器驗證後才寫 `operationRun`。輸出限 evidence 且拒非空資料夾；失敗資料保留，新執行版不覆寫舊圖。檔案瀏覽器欄位直接設值，實際存檔前驗證在本次 demo-files；禁止示範寫 workspaces，不截個人預設資料夾。
- runner 前後遞迴比對工作區路徑與雜湊並存 runner-status；變更先查來源，可能是學員同時儲存。`workspaceContentsUnchanged`／舊 `workspacesUnchanged` 只表示前後內容比較，不證明未曾寫入或辨認寫入者，不反推 `learnerWorkspaceWrites`。01～04 舊執行器僅比第一層檔名、未存前後雜湊，無證據欄位為 null；另留版本化更正、不回填原 run／metadata。
- Windows Recent 僅清理本次新增且目標在本次 run 的捷徑，保留候選與清理結果，不掃整個 evidence。分類註記綁 run、step、原圖路徑／SHA-256、理由及來源程式位置；保留原證據與舊基線，新修改另驗證。
- 延續對應幾何時必讀相關 journal 的原始讀值、限制與失敗原因：數值門檻不是製造公差；不可放寬 EPS、用凸包／任意點數隱藏缺陷。檢查實際 facet／原生 miter 與完整語義剖面，允許合法細分／重索引，不硬綁三角面數或用理想 fixture 冒充實體輸出；checker fixture 不等於正式 STL。
- UI N 面板／物件軸、Local Median、world 外框、幾何長度／力學有效長度及理想值／實讀值須分欄；baseline 讀值不冒充變體。File Browser 確認前 live options 加實檔／真重匯入作證，不補造 operator history，不把重匯入 R0 當來源 Apply Rotation。

## 唯一進度與版本

- `learning/progress.json` 是唯一完成狀態；journal 記脈絡、catalog／工程教材記定義，其他文件／對話不維護獨立完成度。網頁與聊天共用 manage.py；`Start-Learning.cmd`／`Stop-Learning.cmd` 啟停，預設 8766（避開 KiCad 8765）。網頁已確認時讀最新狀態、不重複確認。
- 初始建立後只用 manage.py 鎖、revision、原子寫入，不手編 progress。寫鎖最多等 3 秒，仍忙不寫（網頁 503），稍後 status。新增 catalog 單元用 `add-lessons` 同步進度與工作區，未補前網頁會略過工作區。
- 只有學員明確回報當前小步完成才 `engineering-confirm --evidence`；如實記回報，僅取得實際截圖／檔案時才記該證據。資料夾、檔案、示範或工具核對不能代替確認，檔案驗證與理解分開。原教材 `confirm` 保留給歷史紀錄，不再作為主要進度。
- 練習放 `learning/workspaces/<單元>/`（新版各步寫明資料夾，例如原盒在 04、上蓋與試片在 05）；第 07～08 章的工程練習放 `learning/workspaces/engineering-parametric/`（`engineering-workspace` 建立，`register-file --workspace engineering-parametric` 登記）。重大檢查點先在 Blender 存 v001／v002，再 `register-file` 登記既有檔 SHA-256（命令不寫 .blend）。未登記工作版可續存，已登記版另存新版本；圖像／列印輸出關聯同一工作區的場景版本，場景改版後重產。
- 重學、封存／搬移依要求保留可恢復資料；備份位置未定不自行上雲。自動存檔／.blend1 非正式備份。`note` 預設 tutor，僅逐字記學員原話才 `--author learner`；網頁筆記為 learner，舊無 author 顯示「未標示作者」。01-02 confirm 依 setsLearner 記語言，`set-interface-language` 僅更正、不確認步驟。

常用命令如下（範例不是本輪執行授權）。`--revision <n>` 必須用剛從 `status` 讀得的 revision，讓寫入拒絕過期狀態；衝突先停下核對，不盲目重試。`--author tutor` 用於助教筆記，只有逐字記學員原話才改為 `learner`。

```text
python learning/manage.py status
python learning/manage.py status --lesson 01
python learning/manage.py engineering-confirm --chapter ch01 --step ch01-01-01-01 --revision <n> --evidence "學員明確回報完成的原話"
python learning/manage.py engineering-note --chapter ch01 --step ch01-01-01-01 --revision <n> --author tutor --note-file <UTF8筆記檔>
python learning/manage.py engineering-status
python learning/manage.py register-file --lesson 01 --revision <n> --path learning/workspaces/01/u01_basics_v001.blend --role source_scene
python learning/manage.py add-lessons --revision <n> --reason "加入單元的依據"
python learning/manage.py engineering-workspace --copy-manual-box my_manual_box_v001.blend
python learning/manage.py register-file --workspace engineering-parametric --revision <n> --path learning/workspaces/engineering-parametric/my_manual_box_v002.blend --role source_scene
python learning/tutor/run_demo.py <劇本名稱> <全新的learning/evidence輸出資料夾>
```

## 來源與工程判定

- SECourses 第一講只作基本操作、場景建模與渲染來源；毫米方塊、盒體及 04～09 是學員核准自編工程補充，不冒稱原講內容。原教材／個人練習分開，下載時更新 sources/manifest.json 的實際來源、commit、時間、雜湊、授權（CAD Sketcher 0.32.1 見 `softwareDependencies`）；未下載／開啟不稱已驗證。
- 分清名義尺寸、允許偏差、配合間隙、實測尺寸；間隙標總量／單邊，水平／法向／直徑差不混。工程場景 Unit Scale 0.001，STL Scene Unit 不勾；STL 無單位標記，本教材按 mm 解讀，須核尺寸與來源。0.4 mm 噴嘴不推線寬、材料或合格間隙；0.1～0.6／0.4 mm 僅草案試驗點，不是待重選或已合格範圍。
- 列印法、材料、方向、校正、規格與待定值等有依據再填，不代通用值。圖像、讀回、幾何、切片、列印、量測、試配、理解、改善與強度／配合合格各需證據；實體及合格欄位留空，方向／支撐仍候選，不由渲染、閉合網格或數位匯出推定可印／合格。
- 卡扣 u／δ_req／δ_allow、幾何 L／有效 L 分開，ε 用小數比例，根部 Q 待定且非安全係數，盒壁厚不代臂厚；原廠條件不直接判列印件合格。獨立試片不等同完整夾持／對件，舊上蓋不自動成變體對件；調參非已證改善。
- Screw 的總角／位移、lead／pitch／starts／Iterations 分清；只在 Angle 360° 且單線等對應條件下 Screw=lead=pitch，Merge 非自動封非零 lead 牙端、Smooth 不加幾何，分段／封口待實讀。ISO 僅核摘要，不稱完整標準或已選公差表。
- 審查指出凹點薄肉、環唇加柱重複定位與燕尾朝下懸面風險；風險不等於已印失敗。舊「未做」按當時時點讀；新增 auditReview 不覆寫歷史 operationRun。作者報告只走 `/reports` 靜態路由，`/files` 仍拒 HTML／CSS，不擴大任意檔執行。

## 已執行示範索引（助教歷史，不是學員完成表）

以下每項只列摘要；尺寸、雜湊、版本、空表、失敗 run 與檢查限制保留於連結 journal／evidence 及原文快照，延續前須讀。

- 01／02／03／04：基礎、毫米方塊、渲染及原盒；[01](learning/journal/2026-10-22-lesson01-demo-v001.md)、[02～03](learning/journal/2026-10-22-lesson02-03-demo-v001.md)、[04](learning/journal/2026-10-22-lesson04-demo-v001.md)。
- 介面語言：原學員 2026-10-22 切 English (US)、Preferences saved；[實際操作](learning/journal/2026-10-22-interface-language-execution-v001.md)，不是新讀者設定。
- 05-02～05-06：插銷、六孔總間隙試驗點、試片 STL、環唇上蓋與上蓋 STL，不含試配；[05-02](learning/journal/2026-10-22-lesson05-demo-v002.md)、[05-03](learning/journal/2026-10-22-lesson05-holes-demo-v002.md)、[05-04](learning/journal/2026-10-22-lesson05-export-demo-v003.md)、[05-05](learning/journal/2026-10-22-lesson05-lid-demo-v001.md)、[05-06](learning/journal/2026-10-25-lesson05-lid-export-demo-v001.md)。
- 06-01～06-03：定位榫、燕尾滑蓋與兩件 STL；[06-01](learning/journal/2026-10-25-lesson06-tenon-demo-v006.md)、[06-02](learning/journal/2026-10-25-lesson06-dovetail-demo-v002.md)、[06-03](learning/journal/2026-10-25-lesson06-dovetail-export-demo-v001.md)。
- 07-01～07-05：卡扣參數、幾何、方向、STL 與三臂長試片；[07-01](learning/journal/2026-10-25-lesson07-parameters-demo-v001.md)、[07-02](learning/journal/2026-10-25-lesson07-snap-demo-v001.md)、[07-03](learning/journal/2026-10-25-lesson07-overhang-demo-v001.md)、[07-04](learning/journal/2026-10-25-lesson07-snap-export-demo-v001.md)、[07-05 幾何](learning/journal/2026-10-25-lesson07-coupons-demo-v001.md)、[07-05 匯出](learning/journal/2026-10-25-lesson07-coupon-export-demo-v001.md)。
- 08-01：原盒參照、參數與兩路線歷史，08-02 仍未做；[參數](learning/journal/2026-10-25-lesson08-parameters-demo-v001.md)、[路線](learning/journal/2026-10-25-thread-route-decision-v001.md)。
- 工程路徑（2026-10-27）：CAD Sketcher 隔離環境、草圖／拉伸／內腔、原生 Driver、手工盒蓋形狀鍵與 Driver、受控面板；見[環境試驗](learning/journal/2026-10-27-cad-sketcher-environment-trial-v001.md)、[Y 與拉伸](learning/journal/2026-10-27-cad-sketcher-y-and-extrude-v001.md)、[原生 Driver](learning/journal/2026-10-27-native-sketch-driver-v001.md)、[手工盒蓋](learning/journal/2026-10-27-manual-box-lid-linked-v001.md)、[受控面板原型](learning/journal/2026-10-27-guarded-manual-box-v001.md)、[參數範圍更正](learning/journal/2026-10-27-parametric-range-correction-v001.md)、[柱體對邊距更正](learning/journal/2026-10-27-boss-polygon-correction-v001.md)、[渲染路徑更正](learning/journal/2026-10-27-render-output-path-correction-v001.md)。
- 05～08 審查：逐圖／場景／STL／來源核對與三項工程風險；[journal](learning/journal/2026-10-25-claude-continuation-audit-v001.md)（2026-10-25 由 Codex 接續學員貼上的 Claude 部分審查摘要完成）、[正式索引](learning/evidence/audits/2026-10-25-claude-continuation-v001/report-v001.json)。
