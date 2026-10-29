# 2026-10-28 工程教材 v029：方案 B 章序、章節兩層與前六章改寫

使用者請 Claude Code 先檢查整體內容與教學順序、討論後再執行；評估指出技能先用後教、實際量測排在最難的 CAD Sketcher 之後、試片沒有列印試配步驟、第 04／05／10 章多為示範報告。使用者選定：

- 章序採**方案 B**；受控尺寸面板改為**選修**；以**新版小步為主要進度**；**先改寫第 01～06 章**；頂部觀察題**併入第 01 章章末**。
- 補充要求「保留之前的主章節與次章節的顯示」，確認為**新版也分兩層**（章 → 節 → 小步，側欄可展開到節），原教材 9 單元回查保留。

本輪由 Claude Code 實作；未改 catalog、progress、evidence、v002～v028 教材與 builder、面板程式，未建立學員工作區，未 commit／push。

## 新章序（12 章 81 節）

| 章 | 內容 | 主線小步 |
|---|---|---:|
| 01 基本操作與小盒用途 | 原單元 01 全部（含 v001／v002 存檔）；章末兩題觀察（辨認蓋板與唇邊、配合表面） | 27 |
| 02 公差、間隙與量測觀念 | 間隙觀念、列印條件與量具、自己的紀錄表 | 5 |
| 03 毫米建模與必要編輯 | 訊號站（補 Post、Signal）、毫米方塊、**Edit Mode 基礎 7 步**、原盒（補保存登記）、**固定上蓋 8 步**（原 05-05 拆分） | 53 |
| 04 訊號站材質、燈光與渲染 | 原單元 03 | 18 |
| 05 配合試片與試驗設計 | 插銷 3 步、六孔孔板 12 步（原 05-03 拆分，含孔位與凹點座標） | 15 |
| 06 匯出、列印、量測與試配 | 原盒、試片、上蓋 STL；**列印試片 → 量測 → 逐孔試插 → 選定總間隙**（新增 4 步）；原盒列印量測 | 17 |
| 07 草圖、標尺寸與約束 | CAD Sketcher 安裝、草圖、拉伸、內腔 | 17 |
| 08 盒體與上蓋參數連動 | 固定內腔反例、內腔 X／Y Driver、手工上蓋形狀鍵與 Driver、多尺寸與超界；**08-08 受控面板（選修 11 步）**；附錄 30 項 | 36 |
| 09～11 | 定位榫與燕尾、卡扣、螺紋（沿用 v028 文字，加節與短標題） | 10／15／23 |
| 12 尺寸鏈、交付與成品渲染 | 原 09-01～09-03 與小盒渲染 | 9 |

合計主線 245、選修 11、附錄 30。v028 每一步都有去處：改號見 `stepIdChanges`，拆分見 `replacedSteps`（05-05 → 03-14 的 8 步、05-03 前兩步 → 05-02 的 11 步、05-04 的「先不填」→ 06-03 的 4 步），新增 37 步列於 `contentReview.reviewV029.newSteps`。

## 改寫依據

- 介面名稱由 Blender 5.2.1（9e2066aef7ef）讀回：Select All by Trait > Non Manifold、View > Viewpoint > Bottom、Object > Show/Hide > Hide Selected、Add Modifier > Generate > Solidify／Boolean、Object > Apply > Scale、Preferences > Interface 的 Language 面板、Save Preferences／Auto-Save Preferences、渲染視窗 Image > Save As...、Export／Import STL 選項名稱。出廠鍵位由 GUI 實例讀出：H、Alt+H、Shift+D、Ctrl+J、I、E、1／2／3、Ctrl+Numpad 7（Emulate Numpad 預設關閉）。
- 孔板尺寸、孔中心 X −35～35／Y 2 mm、凹點 1.2 × 1.2 × 2 mm（Y −8.5、Z 2.2）與同組間距 1.6 mm 取自 `learning/evidence/05/2026-10-22-lesson05-holes-demo-v002/trial-plan.json` 與 `learning/tutor/scenarios/lesson05_holes.py`；合併後 Cutters 約 80.35 × 16.4 × 8 mm 取自同一劇本的核對值。上蓋內插與擠出的輸入格式（2.2mm、4mm、2mm、-4mm）取自 `lesson05_lid.py`。Post 0.12 × 0.12 × 1.2 m（Z 1.1）、Signal 直徑 0.5 m（Z 1.95）取自 catalog 02-03 的 help。
- 沒有示範原圖的新步驟一律標 `draft_pending_demo`；拆自原步者標 `source_step_demo`，網頁顯示原步的排解說明與完整示範紀錄。已改寫的第 01～06 章每步 1～3 個操作，並由測試檢查不含「程式讀回／摘要／助教畫面／觀察示範」字樣。

## 網頁與管理工具

- 側欄：目前章展開到節（節號、節名、確認數），點節捲到該節；章內有「本章各節」索引，節標題下為編號小步，小步內顯示代號供聊天引用。
- 頂端「前往下一小步」指向全課第一個未確認的主線小步（跨章）；頂部獨立觀察面板移除，你先前的聊天回答顯示在第 01 章章末「辨認蓋板與唇邊」。
- 新版為主要進度：進度卡只顯示主線小步數；原教材頁移除確認與筆記表單，改列「由本步拆出的新版小步」按鈕；複製給聊天的接續訊息改寫新版下一小步。選修可確認但不計入；附錄不能確認。
- `python learning/manage.py status` 預設顯示新版主線進度、下一小步與其操作；`status --lesson <單元>` 顯示原教材。教材檔不存在時（例如只複製核心檔的測試）退回原教材顯示。

## 檔案

- 新增：`learning/build_engineering_curriculum_v029.py` SHA `001a867b9b5712f6f3f8b00efee074c00d475b9b474dffe849d9562f82717c0a`、文字資料 `learning/engineering_v029_text.py` SHA `fb28c710b203565baf2337f99cb25ebf07959ab1705bc8a7ece7edb87253ebfd`；輸出 `learning/web/engineering-curriculum-v029.json` SHA `c042a30f169541b3087e1a9919320b689745cb170813a4f8ab0bf569b9a6edc1`、`learning/web/engineering-path-v003.json` SHA `9cb08486d3de4c3225aebb9de1ff8471b5902026c84320f4b97a42a5d64962b0`（核對 v028 `f7ff4030…`、path v002 `28cfa695…` 後產生，拒絕覆寫）。
- 新增測試 `learning/tests/test_engineering_curriculum_v029.py`（8 項）；更新 `test_engineering_curriculum_v028.py`（只核歷史雜湊）、`test_engineering_workspace.py`（預設 status）、`test_server.py`（讀 manage 指標、章末觀察題原圖）、`engineering_path.test.js`（章節、下一小步、選修、原教材只供查閱、聊天回答顯示）。
- 修改：`learning/manage.py`（指標、status）、`learning/web/engineering-path.js`、`learning/web/app.js`、`learning/web/app.css`、`learning/web/index.html`、`AGENTS.md`、`README.md`。app.js、test_server.py 維持 CRLF。

## 驗證

- `python -m unittest discover -s learning/tests`：288 項通過、9 項跳過（本機無建立 symlink 權限）；`learning/tutor/tests`：307 項通過、1 項跳過；前端三個測試檔 45／45；兩個 `node --check` 通過；`apply_evidence_semantics.py`、`apply_guide_shortcuts.py` exit 0，catalog 雜湊仍 `17ca75eb…`；`git -c core.whitespace=cr-at-eol diff --check` 無誤。
- 瀏覽器：v029 載入、側欄節列表、本章各節索引、節內編號小步、前往下一小步開到 01-01、章末觀察題顯示聊天回答、主控台無錯誤。
- `learning/progress.json` 雜湊整輪維持 `b66a08f1…`（revision 8）。

## 未完成與限制

- 第 07～12 章仍是 v028 的示範紀錄式文字（只加節與短標題），學員學到前要逐章改寫並實際操作驗證。
- 新增的 Edit Mode 基礎、Post／Signal、保存原盒、試片列印試配等步驟沒有實拍；試配與選定間隙要由學員實物完成。
- 面板工具凍結延至學員進入第 07 章；發布前仍需重產發布清單並取得使用者授權。
- 下一步：從第 01 章 01-01 開始陪練。
