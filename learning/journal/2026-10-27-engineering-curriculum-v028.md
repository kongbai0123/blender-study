# 2026-10-27 工程教材 v028：依審查意見整體整理

使用者先請 Claude Code 審查 Codex 的 v027 交付，再指示「由你進行整體優化，上述內容整體完成才叫完成」。過程中使用者另問「為何基礎章節的一些操作或是說明都不見了」，一併查明並修正。本輪由 Claude Code 實作；未改 catalog、progress、既有 evidence、v002～v027 教材與 builder、手工盒面板程式，未建立學員工作區，未 commit／push。

## 審查發現與處理

| 發現 | 處理 |
|---|---|
| 存檔（01-04、01-09）排在第 11 章，第 03 章卻假設 v001 已存在；原單元 02 的新增物件／命名／Collection 排在第 12 章；第 02 章要印第 07 章才匯出的 STL | 每個原單元完整放在一章並依原順序：單元 01 全在第 01 章、單元 02 全在第 03 章、單元 03 留第 12 章；第 02 章的 04-08 列印量測移除（第 07 章已有相同步驟）。測試檢查單元完整、順序與跨章引用。 |
| 6 個步驟與他章內容完全相同（ch01／ch05 的 05-05 三步、ch02／ch07 的 04-08 三步） | 核對逐欄相同後移除第 01、02 章的副本；v027 的 256 步實際只有 250 個不同步驟。 |
| 第 05 章 56 步混入三代工具與假專案、故障、失敗測試 | 學員路徑 30 步：既有 05-05、手工固定上蓋、形狀鍵／Driver、多尺寸、超界反例，再以指定示範盒副本練受控面板；程式建立範本、v005／v007 面板與 4 項假專案測試共 28 項標 `track: "appendix"`。第 04 章原生 Driver 失敗探測 2 項同樣列附錄。附錄照常顯示原圖與讀值，不計入進度、不能確認（manage.py 拒絕）。ch04／ch05 的逐版限制改列 `limitationHistory`，本章限制改寫成目前狀態。 |
| 「已登記版本不能改」對真實學員無效：面板只認 `workspaces/engineering-parametric`，但 `register-file` 只能登記單元 01～09 工作區 | `register-file --workspace engineering-parametric`（CLI 與網頁「檔案版本」新面板），紀錄寫 `workspace` 不寫 `lesson`；`engineering-workspace` 建立資料夾，`--copy-manual-box` 以雜湊核對後複製面板接受的示範盒 `manual_lid_shape_xy_driver_v001.blend`（SHA `ddae8a3d…`），同名拒絕、不寫進度。純 Python 測試串接「manage 登記 → 面板 `workspace_error` 拒絕」。 |
| 唇邊回答記在原 01-01，`status` 顯示程式標記，前端以字串比對辨認 | 不改 progress。`manage.py` 以單一規則辨認舊格式（第一行 `engineering:<activity>:answered` 的助教標記，加上同時間、同步驟的學員原話），`status` 不再把它當 01-01 筆記，`engineering-status` 列出回答；伺服器把分類交給網頁，網頁不再比對文字，原教材筆記區排除、學習紀錄頁加標註。新回答用 `engineering-note`。 |
| 「已有示範」標籤過寬：45 個拆分小步沒有圖卻標 `existing_demo` | 新狀態 `source_step_demo`（所屬原步有示範、本小步沒有單獨原圖）；`existing_demo` 必須有本步原圖或讀值檔，由測試檢查。 |
| 沒有 CAD Sketcher 安裝步驟；來源未進 `sources/manifest.json` | 第 04 章新增 3 步（下載與 SHA-256 核對、Install from Disk 與啟用、工程工作區與毫米檔），標 `draft_pending_demo`。介面名稱由 Blender 5.2.1 背景讀回：分頁 `Get Extensions`／`Add-ons`、指令 `Install from Disk`，選單位置對照同版 `bl_pkg/bl_extension_ui.py`。私有副本 ZIP 1,283,581 bytes、SHA-256 `b456070e…a59` 再次核對相符；寫入 `sources/manifest.json` 的 `softwareDependencies`。 |
| 一天 26 版、每版要改 server／manage／app 三處；前端版本號替換文字；新前端測試不在 CI | 版本只在 `manage.py` 的 `ENGINEERING_CURRICULUM`／`ENGINEERING_PATH` 指定，伺服器改以 `/engineering-curriculum.json`、`/engineering-path.json` 提供，移除 26 個版本路由。章節狀態、備註、快捷狀態、環境摘要、接續觀察題與步驟更正移入資料（path v002、步驟 `notices`），前端刪除依版本號或步驟 ID 的替換。CI 加入 `engineering-path.js` 語法檢查與 `engineering_path.test.js`（分開步驟，避免前一命令失敗被蓋過）。歷史 builder／測試／JSON 保留原位：23 份 journal 引用其路徑。 |
| app.js、test_server.py 被整檔轉成 LF，差異顯示 1104／950 行 | 恢復 CRLF，與索引一致；實際差異 221／71 行。CRLF 檔的新增行在一般 `git diff --check` 會被當成行尾空白，以 `git -c core.whitespace=cr-at-eol diff --check` 檢查無誤。 |
| AGENTS 累積四段前輪位置、首行仍寫三單元基礎課 | 改寫前位元組快照存 [agents-history-v002](2026-10-27-agents-history-v002.md)（SHA `a2e6d8a4…`）；本檔改為 12 章主線、v028 位置、版本維護規則、第 05 章面板凍結、工程工作區命令，協作角色改為每輪由使用者指定。README 同步。 |
| 使用者問：基礎章節的操作或說明不見了 | 比對 52 個原步：142 個操作項目（位置／做法／看到什麼）與 75 個快捷鍵都有帶過來；但 v027 起拆分時沒有帶「畫面不同，或找不到按鈕？」（52 步 0 則）與助教示範紀錄（原 406 張原圖只帶 22 張；第 01 章 38→3、第 03 章 54→4、第 12 章 24→1）。網頁現在由 catalog 直接顯示每個拆分小步的原步排解說明與完整示範紀錄（動作、觀察分類、原圖；越界路徑不顯示），不在教材 JSON 複製；05-03～08-01 另有的參數表等審查內容提示改按「原教材」按鈕查看。 |

## 檔案

- 新增：`learning/build_engineering_curriculum_v028.py` SHA `8934809a30cfa9449ac4774658fe0e12ef72c88c09044e6652f00fe81affcf63`；輸出 `learning/web/engineering-curriculum-v028.json` SHA `f7ff40301a86d9eea544f02f6a7f006f31345f84f1781ad81052de220294a188`、`learning/web/engineering-path-v002.json` SHA `28cfa6959794d6e6423459cd7ab5e7b376e4c487adc23432078c8be4bfdadf95`（核對 v027 `615b1ef2…`、path v001 `6dcc77a6…` 後產生，拒絕覆寫）。移動步驟的舊 ID 對照在教材 `stepIdChanges`（progress 中工程事件 0 筆、v027 未發布，故改為所在章節的 ID）。
- 新增測試：`learning/tests/test_engineering_curriculum_v028.py`（9 項）、`learning/tests/test_engineering_workspace.py`（8 項，含隔離 HTTP 伺服器與面板拒絕串接）；`test_engineering_progress.py` 加附錄不可確認；`test_server.py`、`engineering_path.test.js` 依固定網址與資料化文字更新，新增附錄、原步說明、舊格式回答、工程工作區登記等前端測試。
- 修改：`learning/manage.py`、`learning/server.py`、`learning/web/engineering-path.js`、`learning/web/app.js`、`learning/web/app.css`、`.github/workflows/verify.yml`、`sources/manifest.json`、`AGENTS.md`、`README.md`。

## 驗證

- `python -m unittest discover -s learning/tests`：279 項通過、9 項跳過（皆為本機無建立 symlink 權限）；`learning/tutor/tests`：307 項通過、1 項跳過；前端三個測試檔 43／43；兩個 `node --check` 通過；`apply_evidence_semantics.py`、`apply_guide_shortcuts.py` exit 0，catalog 雜湊仍 `17ca75eb…`。
- 本機服務以 Stop／Start-Learning 重啟（bootstrap 保留 revision 8）。瀏覽器核對：v028 側欄 0／225、第 05 章學員 30 步與收合附錄 28 項（無確認表單）、第 01 章顯示學員原話接續題、原 01-01 筆記區不再出現標記、學習紀錄頁標註兩則為工程路徑、檔案版本頁有工程工作區面板；第 01、03、12 章每個拆分小步都有排解說明與示範紀錄，01-02 的 13 張原圖全部載入；375 px 寬四個頁面無水平溢出；主控台無訊息。
- `learning/progress.json` 雜湊整輪維持 `b66a08f1…`（revision 8）。

## 未完成與限制

- `prepare_publication.py --verify` 會因已修改的追蹤檔失敗，屬預期；發布時需新版發布清單、核對 v002～v028 新增證據的公開邊界（含可能有本機路徑的原始紀錄），並由使用者明確授權 commit／push。
- 新增 5 步（CAD Sketcher 安裝、工程工作區、示範盒副本、登記檢查點）沒有學員或助教 GUI 實拍，標 `draft_pending_demo`；登記與面板拒絕只做純 Python 串接，畫面上的拒絕仍只有助教假專案原圖（附錄）。
- 受控面板仍只接受指定示範盒副本，原生欄位可繞過、不攔截原生存檔／匯出；未改面板程式，也未做全面干涉、列印、量測或試配。
- 拆分小步標題仍是機械式「· 1／· 2／· 3」，第 04 章 link-counterexample 等步驟仍以對照示範摘要為主；未重新撰寫。原步示範圖的標示框只在原教材頁顯示。
- 下一步：讓學員從第 01 章（含 01-01）實際操作；學員到第 04 章前不再擴充第 05 章工具。
