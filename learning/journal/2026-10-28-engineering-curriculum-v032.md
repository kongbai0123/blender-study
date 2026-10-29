# 2026-10-28 工程教材 v032：審查 Codex v031 後的修正、原教材查閱頁收合、練習題單一介面

使用者請 Claude Code 審查 Codex 這階段的成果（v031、12 章練習題 v001～v004、第 03 章試教頁與 GIF、第 11 章兩個 Blender 探測），並評估「原教材查閱」是否還需要保留。審查後使用者指示「直接完成」全部建議。本輪由 Claude Code 實作；未改 catalog、progress、evidence 原始檔、v002～v031 教材與 builder、challenges v001～v004，未建立學員工作區，沒有推送。

## 審查結論（摘要）

- 全部測試通過，progress 未被改動；題圖由實際 STL 產生且可逐位元重生、試驗值與合格值的界線清楚、失敗證據有保留。
- 問題：第 11 章有小步內文寫著「尚不能依現有教學完成」卻在主線計數；CI 沒跑練習題與試教頁的前端測試與語法檢查；第 07～12 章詳細步驟每步重複同一句免責說明，且多處寫「以可用工具核對」沒說是哪裡；題目一天出了 v001～v004、題圖各 v001～v003 且舊版經網頁提供；試教頁與練習題頁是兩套介面，第 03 章有兩個入口；原始影格與執行紀錄含本機路徑。
- 原教材：`catalog.json` 是 168 個新版小步的示範紀錄與排解說明來源（52 步都被引用），資料必須保留；獨立的查閱頁、側欄舊進度條與總覽頁與新版進度矛盾，可收掉，但要先把參數表、幾何審查與原圖標示框搬進新版。

## 教材 v032

- `learning/build_engineering_curriculum_v032.py`（核對 v031 `96a3304f…`，拒絕覆寫）：
  - 第 11 章 6 個小步改為 `track: "pending"`（待製作）：`ch11-08-02-02`、`ch11-08-03-01`、`ch11-08-03-02`、`ch11-08-04-02`、`ch11-08-05-01`、`ch11-08-05-02`；節 11-05、11-07 只有這類小步，整節標待製作。`trackDefinitions.pending` 說明其意義。主線 245 → 239。
  - 第 07～12 章 110 個 `detail.verification`（同一句）移到章層級 `detailNote`，節頁標題下顯示一次。
  - 6 行「以可用工具核對／可用世界座標」改為具體位置：N 側欄 Item 分頁的 Dimensions，或 Median 切 Global 讀世界座標；ch09 改為對照「示範紀錄」分頁的讀值。
- `manage.py`：指標改 v032；`engineering-confirm` 拒絕待製作小步；`status` 的主線數不含待製作。
- 網頁：待製作小步在節內可選取閱讀、標「待製作」，沒有確認與筆記表單、不計入章／節／全課進度，「前往下一小步」跳過；整節待製作時目錄顯示「—」。
- 第 07～12 章詳細步驟仍待學到該章時實際操作後改寫（同第 01～06 章的做法），本輪沒有假裝重寫。

## 原教材查閱頁收合

- 「示範紀錄」分頁改用主程式提供的 `sourceRecord`：與原教材頁相同的完整紀錄，含原圖標示框、參數表、幾何草案、方向／STL／試片審查、螺紋計畫、稽核摘要與舊版示範；「注意」分頁不再寫「另有參數表…請到原教材頁看」。
- 移除：側欄「回查原教材（9 單元）」與舊進度條、「原教材查閱」「原單元總覽」頁籤、進度卡的「查閱原教材」按鈕、`renderOverview` 與 `#overview` 路由。原教材原頁仍可從「注意」分頁與章頁「本章補充」的參照按鈕開啟（`#lesson`），只供查閱來源。
- 檔案版本頁原本靠原教材側欄切換單元，改為頁內單元按鈕；「回到目前步驟」改為「回到新版下一小步」。`manage.py status --lesson` 保留給助教。

## 練習題單一介面（challenges v005）

- `learning/build_challenges_v005.py`（核對 v004 `c17a274a…` 與 GIF 雜湊，拒絕覆寫）：第 03 章移除 `pilotPath`，加 `progressKind: "pilot"`（沿用原 `pilot_challenge_*` 事件與 `pilot-*` 指令，既有紀錄不必搬移）與 `animation`（GIF、說明、動作前後原圖；不連 `run.json`，因含本機路徑）；`source` 指向 v032。其餘 11 章內容不變（測試逐題比對）。
- `challenges/app.js` 處理第 03 章（pilot 動作、動畫、目錄不再跳到試教頁）；`pilot/box-lesson.html` 改為無程式的轉址頁；刪除 `pilot/box-lesson.js` 與 `tests/pilot_box.test.js`（功能已由練習題頁與其測試涵蓋）。
- 伺服器：練習題頁只提供固定頁面檔與「目前題目資料引用」的題圖與動畫（`server.challenge_assets`）；舊版題目 JSON、未引用的題圖、`box-lesson.js` 回 404。AGENTS.md 加入題目與題圖的版本規則。

## CI 與發布

- `verify.yml` 加 `node --check learning/web/challenges/app.js`，並把 `challenges_ui.test.js` 加進前端測試。
- `scripts/prepare_publication.py`：2026-10-28 的動畫採樣與兩個 Blender 探測，原始影格（`frame-*`、`gif-*`）、`frames.json`、`run.json` 排除為本機；失敗的 `pilot-box-move-record-v001` 整個留本機；`runner-status.json` 與 `.log` 原本就排除。公開 GIF、前後原圖與去識別摘要。`public-summary-v001.json` 只在說明文字提到 "Recent"，沒有本機路徑。

## 檔案

- 新增：`learning/build_engineering_curriculum_v032.py` SHA `b2e577083f6f439fde95a3cb9ef794f42dab7ff0ee93410a991dbb42aab07d6a` → `learning/web/engineering-curriculum-v032.json` SHA `7e123574e4687f2e6aca8b262dac7dcdadfe94cd080e854ca0f7703a3e24075b`；`learning/build_challenges_v005.py` SHA `38bed146eb591ddf8139a7656825b262810dc9330058d42ffe207fbce762f223` → `learning/web/challenges/challenges-v005.json` SHA `6e73f7990434fb84631c98f4b6941967d01ce49d9513ff099b8cf79017fa34f2`。
- 新增測試：`test_engineering_curriculum_v032.py`（6 項）、`test_challenges_v005.py`（3 項）；更新 `test_server.py`、`test_challenge_progress.py`（白名單）、`engineering_path.test.js`（移除舊側欄／總覽假設，新增待製作、完整示範紀錄、檔案版本頁、第 03 章入口 4 項）、`challenges_ui.test.js`（v005、第 03 章 pilot 動作與動畫 2 項）。
- 修改：`learning/manage.py`、`learning/server.py`、`learning/web/engineering-path.js`、`learning/web/app.js`（維持 CRLF）、`learning/web/app.css`、`learning/web/index.html`、`learning/web/challenges/app.js`、`learning/web/pilot/box-lesson.html`、`.github/workflows/verify.yml`、`scripts/prepare_publication.py`、`AGENTS.md`、`README.md`。刪除：`learning/web/pilot/box-lesson.js`、`learning/web/tests/pilot_box.test.js`。

## 驗證

- `learning/tests`：334 項通過、9 項跳過（本機無建立 symlink 權限）；`learning/tutor/tests`：307 項通過、1 項跳過；CI 列的四個前端測試檔 53／53；三個 `node --check` 通過；`apply_evidence_semantics.py`、`apply_guide_shortcuts.py` exit 0，catalog 仍 `17ca75eb…`；`git -c core.whitespace=cr-at-eol diff --check` 無誤。
- 8766 重啟後瀏覽器實測：頁籤只剩「新版教學章節／學習紀錄／檔案版本」、側欄無原教材；側欄進度 0／239；11-05 兩步標待製作、無表單、節顯示「待製作」；01-04「示範紀錄」分頁顯示 6 個標示框（位置已套用）；`/pilot/box-lesson.html` 轉到 `/challenges/index.html?chapter=ch03`，顯示動畫與「本題尚未由學員確認」；檔案版本頁可切換單元；`/pilot/box-lesson.js`、`/pilot/box-drawing.svg`、`/challenges/challenges-v001.json` 回 404。主控台無錯誤。
- `learning/progress.json` 雜湊整輪維持 `b66a08f1…`（revision 8）。

## 未完成與限制

- 第 07～12 章詳細步驟待逐章實作後改寫；第 11 章待製作的螺紋、螺絲柱與試鎖仍需先做出模型與示範。
- 舊 CSS（原教材側欄、總覽卡片）仍留在 `app.css` 的壓縮行內，沒有影響畫面，之後整理樣式時再清。
- 推送前需重產發布清單並取得使用者授權；本輪只在本機 commit。
