# 2026-10-28 工程教材 v030：章頁與節頁分開、右欄詳述分頁

v029 讓一章的所有內容擠在一頁。使用者要求「每個章節與小節都自己獨立一頁」，並先討論各區的內容與呈現方式。討論後使用者選定：

- **章頁**：精簡總覽（學什麼、做出、接續）加小節目錄；實作內容、必要功能與快捷、限制、原教材參照、教學安排與附錄收在「本章補充」，章頁不放表單。
- **節頁**：依使用者描述「章節 | 呈現與簡述操作、說明 | 詳述操作過程（tab sidebar）」排成三欄：左為側欄，中為本節小步清單，右為所選小步的詳述分頁。
- **小步只顯示做法**：小目標、操作、成功畫面、確認與卡關筆記；其餘移到右欄分頁。
- **側欄**：章連到章頁，節連到節頁；目前所在的節會標示。
- 看過草圖後：詳細步驟先照 Claude Code 的寫法；分頁數量等使用者看過成品再定（目前 6 個）；只做電腦桌面版；一次只展開一步，右欄跟著所選小步。

本輪由 Claude Code 實作；未改 catalog、progress、evidence、v002～v029 教材與 builder、path v003，未建立學員工作區，未 commit／push。

## 教材 v030

- `learning/build_engineering_curriculum_v030.py` 核對 v029 雜湊後，為第 01～06 章 135 個主線小步加上 `detail = {steps, why}`：`steps` 是逐個按鍵、選單與欄位的操作，`why` 說明這一步在小盒專案中的用途。builder 檢查 `detail` 的鍵與第 01～06 章主線小步完全一致、每行非空，並拒絕覆寫。除 `detail`、版本、`sourceVersions` 與 `contentReview.reviewV030` 外，內容與 v029 相同（測試逐步比對）。
- 介面名稱沿用 `reviewV029.uiEvidence` 已讀回核對的名稱；本輪沒有新增示範或原圖。第 07～12 章沒有 `detail`，分頁顯示「本章的詳細步驟還沒改寫」。

## 網頁

- 網址：章頁 `#engineering/ch03`；節頁 `#engineering/ch03/03-08`。「前往下一小步」與原教材頁的新版小步按鈕會直接開到該步所在的節頁並選取該步。
- 節頁：麵包屑回章頁；中欄每個小步一列，已確認的打勾，選取的小步展開並附確認與卡關筆記表單，其餘只顯示標題按鈕（預設選本節第一個未確認的主線小步）；下方有跨章的上一節／回本章／下一節。
- 右欄（捲動時固定在畫面內）6 個分頁：
  1. 詳細步驟：`detail.steps` 與「為什麼」。
  2. 原圖：本步原圖與 SHA-256。
  3. 快捷鍵：本步快捷鍵與實拍。
  4. 示範紀錄：拆自原教材時，從 catalog 顯示原步的助教示範紀錄，加上檔案版本與驗證；不安全路徑不顯示。
  5. 注意：狀態說明、更正提醒、限制、原教材參照與小步代號。
  6. 找不到按鈕：原步的排解說明。
- 移除 v029 的章內各節索引與章內全部展開的小步清單；選修節照常可確認、不計入；附錄只在章頁「本章補充」中，沒有表單。

## 檔案

- 新增：`learning/engineering_v030_detail.py` SHA `3d2542c5a66c38fc180edd44935ec5923e18975f4dd3516b2db8b4d7c97c8bf4`、`learning/build_engineering_curriculum_v030.py` SHA `acbe229ba430a40abe1385b796e3018d7d6f124f43e14042467b0fd3e975b5fd`；輸出 `learning/web/engineering-curriculum-v030.json` SHA `55d0cc4c731a550fbe2c17635426dd14efca2894cf99455b322d0ed9f8d8515b`。
- 新增測試 `learning/tests/test_engineering_curriculum_v030.py`（4 項）；`test_engineering_curriculum_v029.py` 改為只核 v029 雜湊與 path 指標；`engineering_path.test.js` 移除 15 項舊版面測試、新增 12 項章頁／節頁／分頁／路由測試。
- 修改：`learning/manage.py`（指標改 v030）、`learning/web/engineering-path.js`（章頁、節頁、詳述分頁）、`learning/web/app.js`（節與小步路由、分頁狀態、側欄節連結）、`learning/web/app.css`、`AGENTS.md`、`README.md`。修改的檔案維持原本 CRLF。

## 驗證

- `learning/tests`：292 項通過、9 項跳過（本機無建立 symlink 權限）；`learning/tutor/tests`：307 項通過、1 項跳過；前端三個測試檔 42／42；兩個 `node --check` 通過；`apply_evidence_semantics.py`、`apply_guide_shortcuts.py` exit 0，catalog 雜湊仍 `17ca75eb…`；`git -c core.whitespace=cr-at-eol diff --check` 無誤。
- 瀏覽器（1440 × 900）：第 03 章章頁目錄、`#engineering/ch03/03-08` 7 個小步與 6 個分頁、切換小步與分頁、跨章上一節／下一節，主控台無錯誤。
- `learning/progress.json` 雜湊整輪維持 `b66a08f1…`（revision 8）。

## 未完成與限制

- 分頁數量與命名待使用者看過後調整；第 07～12 章的詳細步驟待學到該章前改寫。
- 詳細步驟是依讀回介面名稱寫成的文字，沒有逐步實拍；學員照做時發現不符，記在該步卡關筆記，再修正下一版。
- 推送延後（使用者：稍後推送）；發布前需重產發布清單並取得授權。
