# 2026-10-29 工程教材 v038：新增第 00 章「常用功能與快捷操作」

使用者要求「新增一個 0 章節，說明常用功能與快捷操作」。本輪由 Claude Code 實作，接在 Codex 的 v037／路徑 v006／題目 v010 之後；第 01～12 章、題目、catalog、progress、evidence 原始檔都沒有改，沒有新的 Blender 示範，沒有 commit 或 push。

## 設計決定

- 第 00 章是「速查」，不是練習章：第 01～06 章已經有這些按鍵的正式練習並計入主線，再計一次會重複。卡片 `track: "reference"`：可閱讀、可留卡關筆記；不能確認、不計入任何進度，「前往下一小步」與章頁接續都略過。路徑項目 `kind: "reference"`：沒有練習題、不是第 01 章的先備學習。
- 每張卡說明用途、在哪裡按、操作、看到什麼算對、按錯怎麼復原、找不到按鈕時的選單位置（`help`），以及「正式練習」連到第 01～12 章實際操作的小步（`practice`）。
- 「技能先教後用」維持：00-06 編輯模式與 00-07 按錯模式的節名與卡片都標明第 03 章 03-08 起才用；速查卡不要求學員先操作。

## 內容（7 節、29 張卡）

00-01 按鍵規則、取消與撤回、F3 搜尋、沒有數字鍵盤；00-02 開新檔／開啟、存檔／另存、F12；00-03 對焦、正側底視、相機視角、側欄 N；00-04 全選／取消、Shift+A、X、Shift+D／Ctrl+J、F2／M、H／Alt+H；00-05 G、R、S、Ctrl+A → Scale；00-06 Tab 與點邊面、I／E、Ctrl+B、X → Faces、Select Non Manifold；00-07 Object Mode 誤按 I／E、Ctrl+B、主鍵盤句點。

證據只取既有紀錄：`learning/evidence/01/2026-10-27-shortcuts-demo-v001`、`shortcuts-keyboard-demo-v002`、`shortcuts-mesh-demo-v001`、`shortcut-mode-errors-demo-v001／v002`，`learning/evidence/03/2026-10-28-edit-practice-gui-v001`，以及原單元 01～04 的選單鍵標原圖。注意事項大多沿用 `guide-shortcuts-v002.json` 已審核的文字。本輪逐張看過主要原圖再寫圖說（預設畫面、File／Edit／Object／Render 選單、G 後側欄、正視、Pivot Point 選單、X 確認框、誤按 I、Ctrl+B 框、Add 選單、Move to Collection、F2 改名框、相機視角、倒角、隱藏、底視、Preferences Input）。

照實寫明的限制：
- Shift+D／Ctrl+J、X → Faces、F12、Ctrl+N／O／S、Ctrl+, 只有選單鍵標原圖，沒有逐步實拍按鍵後的畫面。
- Emulate Numpad：勾選框由關變開有實拍，但勾選後模擬按主鍵盤 1 沒有切到正視（`emulateEffectViaSimulatedOneVerified: false`），卡片不保證效果。
- 主鍵盤句點跳出的 Pivot Point 選單，按 Esc 離開沒有實拍；卡片已註明。
- 示範多在單位 m 的出廠 Cube；卡片提醒不要把數字直接搬到毫米工程場景。

## 檔案

- 新增 `learning/engineering_v038_ch00.json`（卡片內容，SHA `d77b15115d995aad363bae69762c959cb2fd35cadfa7c09d3f15d7a5bb9153eb`）。路徑用別名（SV、KV、MV、EV1、EV2、ES、L01～L04），builder 展開並核對檔案存在。
- 新增 `learning/build_engineering_curriculum_v038.py`（核對 v037 `79522345…` 與內容 SHA，拒絕覆寫）→ `learning/web/engineering-curriculum-v038.json` SHA `7f0150607d736a6bbd2b43767fba09ffb4f3bbc8aaf6228a4c08aec54dddf4df`。builder 計算每張原圖與證據檔的 SHA-256；「示範紀錄」的讀值依案例名稱從實測 JSON（`cases.actual` 或 `records.observed`）取出，不手抄。第 01～12 章逐字複製；新增 `trackDefinitions.reference` 與 `contentReview.reviewV038`。
- 新增 `learning/build_engineering_path_v007.py`（核對 v006 `c5deb3aa…`）→ `learning/web/engineering-path-v007.json` SHA `513803e0b08be50f824b7e5919a1c710540bc2ba3294d627ce1126cebf8d23cc`；第 00 章項目 `kind: "reference"`，`intro` 加一句說明。
- `learning/manage.py`：指標改 v038／v007；`engineering-confirm` 拒絕速查卡（筆記照收）；status 說明加「第 00 章速查」。
- `learning/web/engineering-path.js`：速查章章頁以「速查表」取代小節目錄（按鍵、功能、在哪裡按、正式練習），不顯示練習題與確認數，「做出」標籤改用資料的 `deliverableLabel`；章頁「接續」略過速查章；速查卡沒有確認表單，顯示「正式練習」連結與卡關筆記；「找不到按鈕」分頁先顯示卡片自己的 `help`；「注意」分頁與節頁顯示速查說明。
- `learning/web/app.js`（維持 CRLF）：側欄對沒有主線小步的章顯示 `availabilityLabel`，節列不計速查卡。`learning/web/app.css`（維持 CRLF）：速查表與正式練習按鈕樣式。
- 測試：新增 `learning/tests/test_engineering_curriculum_v038.py`（6 項：雜湊與指標、只多第 00 章、卡片完整且不計數、讀值與實測 JSON 一致、manage 拒絕確認但收筆記、builder 拒絕覆寫）；`test_server.py` 原本假設第一章是 ch01，改為依 ID 找 ch01；`engineering_path.test.js` 加 3 項（速查表與先備、速查卡沒有確認表單、側欄與正式練習連結）。
- 文件：AGENTS.md（目前接續位置、結構規則、GitHub 狀態）、README.md。

## 驗證

- `learning/tests`：397 項通過、9 項略過（本機無建立 symlink 權限）；`learning/tutor/tests`：311 項通過、1 項略過；CI 列的四個前端測試檔 66／66；三個 `node --check` 通過；`git -c core.whitespace=cr-at-eol diff --check` 無誤；CRLF／LF 維持原樣。
- 以真實 v038／v007 在 Node 渲染第 00 章 29 張卡 × 6 分頁：沒有確認表單、都有筆記表單，原圖、讀值、`help` 與速查說明都在。
- 用專案啟動器 `Start-Learning.ps1 -NoBrowser` 開出 `http://127.0.0.1:8770/`（舊的 8766～8769 服務沒有停止，仍載入舊指標）。瀏覽器實測：側欄 13 章、第 00 章顯示「速查：不需確認，不計入進度」、進度 0／243；速查表 29 列可點、正式練習按鈕可連到該步；29 張卡的原圖全部載入、無確認表單；第 01 章沒有「接續」列、練習題連結仍在、「前往下一小步」仍是 01-01；主控台沒有錯誤。
- `learning/progress.json` 整輪維持 revision 8、SHA `b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1`。

## 未完成與後續

- 速查卡沒有新示範；若要補 Shift+D／Ctrl+J、X → Faces、F12 或 Pivot Point 選單按 Esc 的實拍，需另開獨立 Blender 示範並出新版本。
- 推送前要重產發布清單；第 00 章引用的 2026-10-27／28 證據要在清單內，並照既有規則排除 raw runner、frames、run.json 等本機路徑檔。
