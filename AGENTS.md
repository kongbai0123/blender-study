# Blender 引導式學習規範

以繁體中文教學。先做三單元基礎課（第二單元加入毫米尺寸方塊），再做通用小盒與螺紋、卡扣、卡榫、公差。以下規範生效；[原 AGENTS 完整位元組快照](learning/journal/2026-10-27-agents-history-v001.md)只保存歷史，內文「目前／最新／未做」及舊範圍不得取代本檔、最新 journal 或當前進度。[逐項搬移映射](learning/annotations/agents-requirements-map-v001.json)列原文、位置及保留方式。

## 公開版接續

- 新 clone 先執行 `python learning/bootstrap.py`；合法既有 progress 只讀保留，不重設、不抄作者筆記。English (US)、revision 6 與歷史示範不是新讀者的畫面、選擇或完成狀態，以該 clone 的 progress／實際畫面為準。
- 本輪候選邊界見 [快速方法修正清單](docs/publication-manifest-2026-10-27-shortcuts-v002.json)；[快速方法 v001](docs/publication-manifest-2026-10-27-shortcuts-v001.json)、[語義修正清單](docs/publication-manifest-2026-10-27.json)及[2026-10-26 清單](docs/publication-manifest-2026-10-26.json)留作歷史基線。不得為補引用重新加入 Recent 清單、private 基線或第三方 PDF 快取。原始證據不正規化換行，保留 `.gitattributes` 的 `* -text`。

## 目前授權與接續位置

- 本輪修正快速方法審查的兩項意見：04-06 取消選取範本、I／E／Ctrl+B 在 Object Mode 誤按的結果與復原；並盤點同範本項目。保留常規方法與既有 operationRun，既有 Blender 5.2.1 證據足夠就沿用，僅缺證據處用獨立 Blender 補驗／補拍，輸出到新 evidence 資料夾。不改原圖、舊 run／metadata、既有場景／STL、progress 或學員狀態，不寫 workspaces、不 confirm、不 stage／commit／push。每個快捷鍵列模式、焦點、單位與相對／絕對差別，未驗不寫成已驗；新註記／清單另存 v002，舊版本不回填。
- **助教示範位置：** 已示範至 08-01 參數整理；08-02 尚未建模或實拍。原學員「1.2.憶起」被助教理解為兩路線並學，僅屬教材歷史，未定標準、尺寸、間隙、材料或硬體。見 [08-01](learning/journal/2026-10-25-lesson08-parameters-demo-v001.md)、[路線紀錄](learning/journal/2026-10-25-thread-route-decision-v001.md)。
- **學員確認位置：** 本 clone 於 2026-10-27 開工 `manage.py status` 讀得 revision 6、單元 01／01-01、未確認任何步驟、未登記學員檔案；這只是一次讀值，不維護另一份進度，也不代表新 clone。每次接續重讀 progress/status；本次不改。
- 最新交接：[2026-10-27 快速方法情境修正](learning/journal/2026-10-27-shortcuts-handoff-v002.md)；前輪：[快速方法補充](learning/journal/2026-10-27-shortcuts-handoff-v001.md)、[語義與分類修正](learning/journal/2026-10-27-evidence-semantics-handoff-v001.md)。Claude 轉交的快速方法審查通過及兩項修正意見記於新交接，不改歷史紀錄。

## 協作規則

1. 開工先讀最新交接 journal、README、catalog、progress 及相關 journal，再執行 `python learning/manage.py status`，以最新狀態與學員畫面為準。
2. 本次 Codex 負責實作、測試與單一發布窗口，Claude 負責審查；Codex/root 統整註記與 catalog，模式驗證負責人執行獨立 Blender，盤點負責人只寫新審查註記，測試負責人改套用工具／測試；各範圍與實際檔案寫入交接。
3. catalog 只由 Codex/root 這一位負責者整合發布；本次發布僅限工作樹，未獲新指示不得 commit 或 push。
4. 寫入前重讀最新檔案及所需 revision；遇衝突先停、核對，不盲目重試，不覆寫對方變更。
5. 不同時執行會重建 catalog 或 metadata 的匯入／發布程式；先完成並核對版本化註記，再依序更新匯入器、catalog、前端及驗證。
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
- 延續對應幾何時必讀下列 journal 的原始讀值、限制與失敗原因：數值門檻不是製造公差；不可放寬 EPS、用凸包／任意點數隱藏缺陷。檢查實際 facet／原生 miter 與完整語義剖面，允許合法細分／重索引，不硬綁三角面數或用理想 fixture 冒充實體輸出；checker fixture 不等於正式 STL。
- UI N 面板／物件軸、Local Median、world 外框、幾何長度／力學有效長度及理想值／實讀值須分欄；baseline 讀值不冒充變體。File Browser 確認前 live options 加實檔／真重匯入作證，不補造 operator history，不把重匯入 R0 當來源 Apply Rotation。

## 唯一進度與版本

- `learning/progress.json` 是唯一完成狀態；journal 記脈絡、catalog 記定義，其他文件／對話不維護獨立完成度。網頁與聊天共用 manage.py；`Start-Learning.cmd`／`Stop-Learning.cmd` 啟停，預設 8766（避開 KiCad 8765）。網頁已確認時讀最新狀態、不重複確認。
- 初始建立後只用 manage.py 鎖、revision、原子寫入，不手編 progress。寫鎖最多等 3 秒，仍忙不寫（網頁 503），稍後 status。新增 catalog 單元用 `add-lessons` 同步進度與工作區，未補前網頁會略過工作區。
- 只有學員明確回報當前步完成才 `confirm --evidence`；如實記回報，僅取得實際截圖／檔案時才記該證據。資料夾、檔案、示範或工具核對不能代替確認，檔案驗證與理解分開。
- 練習放 `learning/workspaces/<單元>/`；重大檢查點先在 Blender 存 v001／v002，再 `register-file` 登記既有檔 SHA-256（命令不寫 .blend）。未登記工作版可續存，已登記版另存新版本；圖像／列印輸出關聯該場景版本，場景改版後重產。
- 重學、封存／搬移依要求保留可恢復資料；備份位置未定不自行上雲。自動存檔／.blend1 非正式備份。`note` 預設 tutor，僅逐字記學員原話才 `--author learner`；網頁筆記為 learner，舊無 author 顯示「未標示作者」。01-02 confirm 依 setsLearner 記語言，`set-interface-language` 僅更正、不確認步驟；常用命令見下方，[原文快照](learning/journal/2026-10-27-agents-history-v001.md)另留歷史範例。

常用命令如下（範例不是本輪執行授權）。`--revision <n>` 必須用剛從 `status` 讀得的 revision，讓寫入拒絕過期狀態；衝突先停下核對，不盲目重試。`--author tutor` 用於助教筆記，只有逐字記學員原話才改為 `learner`。

```text
python learning/manage.py status
python learning/manage.py confirm --lesson 01 --step 01-01 --revision <n> --evidence "學員明確回報完成的原話"
python learning/manage.py note --lesson 01 --revision <n> --author tutor --note-file <UTF8筆記檔>
python learning/manage.py register-file --lesson 01 --revision <n> --path learning/workspaces/01/u01_basics_v001.blend --role source_scene
python learning/manage.py add-lessons --revision <n> --reason "加入單元的依據"
python learning/tutor/run_demo.py <劇本名稱> <全新的learning/evidence輸出資料夾>
```

## 來源與工程判定

- SECourses 第一講只作基本操作、場景建模與渲染來源；毫米方塊、盒體及 04～09 是學員核准自編工程補充，不冒稱原講內容。原教材／個人練習分開，下載時更新 sources/manifest.json 的實際來源、commit、時間、雜湊、授權；未下載／開啟不稱已驗證。
- 分清名義尺寸、允許偏差、配合間隙、實測尺寸；間隙標總量／單邊，水平／法向／直徑差不混。工程場景 Unit Scale 0.001，STL Scene Unit 不勾；STL 無單位標記，本教材按 mm 解讀，須核尺寸與來源。0.4 mm 噴嘴不推線寬、材料或合格間隙；0.1～0.6／0.4 mm 僅草案試驗點，不是待重選或已合格範圍。
- 列印法、材料、方向、校正、規格與待定值等有依據再填，不代通用值。圖像、讀回、幾何、切片、列印、量測、試配、理解、改善與強度／配合合格各需證據；實體及合格欄位留空，方向／支撐仍候選，不由渲染、閉合網格或數位匯出推定可印／合格。
- 卡扣 u／δ_req／δ_allow、幾何 L／有效 L 分開，ε 用小數比例，根部 Q 待定且非安全係數，盒壁厚不代臂厚；原廠條件不直接判列印件合格。獨立試片不等同完整夾持／對件，舊上蓋不自動成變體對件；調參非已證改善。
- Screw 的總角／位移、lead／pitch／starts／Iterations 分清；只在 Angle 360° 且單線等對應條件下 Screw=lead=pitch，Merge 非自動封非零 lead 牙端、Smooth 不加幾何，分段／封口待實讀。ISO 僅核摘要，不稱完整標準或已選公差表。
- 審查指出凹點薄肉、環唇加柱重複定位與燕尾朝下懸面風險；風險不等於已印失敗。舊「未做」按當時時點讀；新增 auditReview 不覆寫歷史 operationRun。作者報告只走 `/reports` 靜態路由，`/files` 仍拒 HTML／CSS，不擴大任意檔執行。

## 已執行示範索引（助教歷史，不是學員完成表）

以下每項只列摘要；尺寸、雜湊、版本、空表、失敗 run 與檢查限制保留於連結 journal／evidence 及原文快照，延續前須讀。

- 01／02／03／04：基礎、毫米方塊、渲染及原盒；[01](learning/journal/2026-10-22-lesson01-demo-v001.md)、[02～03](learning/journal/2026-10-22-lesson02-03-demo-v001.md)、[04](learning/journal/2026-10-22-lesson04-demo-v001.md)。
- 介面語言：原學員 2026-10-22 切 English (US)、Preferences saved；[實際操作](learning/journal/2026-10-22-interface-language-execution-v001.md)，不是新讀者設定。
- 05-02：插銷幾何與重開驗證；[journal](learning/journal/2026-10-22-lesson05-demo-v002.md)。
- 05-03：六孔總間隙試驗點與凹點，不含試配；[journal](learning/journal/2026-10-22-lesson05-holes-demo-v002.md)。
- 05-04：插銷／孔板 STL 與補充尺寸實拍；[journal](learning/journal/2026-10-22-lesson05-export-demo-v003.md)。
- 05-05：環唇上蓋幾何草案；[journal](learning/journal/2026-10-22-lesson05-lid-demo-v001.md)。
- 05-06：上蓋 STL 數位核對，未落床切片；[journal](learning/journal/2026-10-25-lesson05-lid-export-demo-v001.md)。
- 06-01：定位榫幾何與孔間距，非旋轉全約束；[journal](learning/journal/2026-10-25-lesson06-tenon-demo-v006.md)。
- 06-02：燕尾滑蓋幾何與行程，無端擋／止退；[journal](learning/journal/2026-10-25-lesson06-dovetail-demo-v002.md)。
- 06-03：燕尾兩件 STL 數位核對；[journal](learning/journal/2026-10-25-lesson06-dovetail-export-demo-v001.md)。
- 07-01：懸臂卡扣參數與估算條件，材料／應變待定；[journal](learning/journal/2026-10-25-lesson07-parameters-demo-v001.md)。
- 07-02：單臂／局部上蓋幾何草案與原生根部；[journal](learning/journal/2026-10-25-lesson07-snap-demo-v001.md)。
- 07-03：方向與 Overhang 顯示比較，非免支撐判定；[journal](learning/journal/2026-10-25-lesson07-overhang-demo-v001.md)。
- 07-04：既有卡扣兩件 STL 數位核對；[journal](learning/journal/2026-10-25-lesson07-snap-export-demo-v001.md)。
- 07-05：三臂長試片幾何及 STL，非已證改善；[幾何](learning/journal/2026-10-25-lesson07-coupons-demo-v001.md)、[匯出](learning/journal/2026-10-25-lesson07-coupon-export-demo-v001.md)。
- 08-01：原盒參照、參數與兩路線歷史，08-02 仍未做；[參數](learning/journal/2026-10-25-lesson08-parameters-demo-v001.md)、[路線](learning/journal/2026-10-25-thread-route-decision-v001.md)。
- 05～08 審查：逐圖／場景／STL／來源核對與三項工程風險；[journal](learning/journal/2026-10-25-claude-continuation-audit-v001.md)、[正式索引](learning/evidence/audits/2026-10-25-claude-continuation-v001/report-v001.json)。
