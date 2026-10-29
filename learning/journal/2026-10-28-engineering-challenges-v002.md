# 12 章練習題與工程教材 v031

使用者要求依前次 LeetCode 式試教、工程題圖、真實畫面與共用資料管理完成後續章節。此輪整理各章練習、補原教材詳細文字，並將尚未取得的操作／實體證據明示待補；不將草案稱為已驗證成果。

## 課程與題目

- `learning/web/engineering-curriculum-v031.json` SHA-256 `96a3304fee401b61cc59b6764eaa31b6a22e31e9865b873534299f8eb42c5b92`；以來源 v030 雜湊為基礎的 `learning/build_engineering_curriculum_v031.py` 拒絕覆寫，保留所有舊教材。第 07～12 章 110 個主線小步補 1～3 條詳細文字與原因，來自兩份 `engineering_v031_ch07_ch09.json`、`engineering_v031_ch10_ch12.json`；不是新錄製的逐步示範，介面明示尚未逐步重新實拍。
- 跨代理交叉檢核修正了原生單位輸入、保存時避免覆寫、Fully defined、Auto Boolean、燕尾工具座標與相對位移、卡扣 SnapTool/FlangeTool、根部與鉤頂倒角、落床分隔及試片來源等。四個尚缺完整螺紋／柱結構實作的小步在主欄與詳述均明示待製作，不能依現有教材假裝完成。
- `learning/web/challenges/challenges-v002.json` SHA `e828ccc01320a417b655fd29fee53f093b81891ef47343e38b535d973871d126`，12 章各一題，第 03 章沿用既有 pilot；新版由 `learning/build_challenges_v002.py` 校驗 v001 與題圖雜湊產生，原 v001 保留。每題包含目標、條件、提示、原小節連結、畫面證據狀態及待驗限制；不把圖片或助教示範當學員完成。
- 網頁 `/challenges/index.html?chapter=chNN`；主章頁提供入口，pilot 有題目目錄。題目確認與筆記用同一 `progress.json` 的 `challenge_confirmed`／`challenge_note` 事件，與主線小步及 pilot 確認分開；CLI `challenge-status`、`challenge-confirm`、`challenge-note` 供聊天使用。`.blend` 登記使用現有工作區與 SHA-256，07／08 依 `engineering-parametric`；選關聯檔時重新計算雜湊。輸入及 revision 衝突不自動重送。

## 可追溯工程題圖

- 02 環唇及盒口：`lip-clearance-drawing-v001.svg` SHA `b82736f3ac2380219dd37f6b77be2704df82183810bf0204339a7079957a117f`；原盒及上蓋 STL Y=0 實際交線、沿原世界座標，圖內局部僅放大。0.4 mm 總／0.2 mm 單側為名義試驗。
- 03 原盒：沿用 `pilot/box-drawing-v002.svg`；05／06 孔板與插銷：`fit-trial-drawing-v003.svg` SHA `2b8cdd5d8724c76d0a5a410c25a7d45e9c1eac03d53f714bb66c076420738bd5`；0.1～0.6 mm 為總間隙試驗點，非合格值。
- 09 燕尾：`dovetail-trial-drawing-v002.svg` SHA `8eda077de7b4944fba3cd975102047483ede2a9d2547f45a5fabb30ffc6fc421`，盒／蓋 STL X=0 截面保留原世界位置，非定位柱圖；既有 0.4 mm 水平總間隙為試驗值。
- 10 A/B/C 卡扣試片：`snapfit-coupons-drawing-v003.svg` SHA `0f6c6a0bfe6ed2aad58f54f3b2061684bb8df361a5fb6bddc3da0f305905b129`，三件 STL Z=4.5 mm 實際交線，為圖面排版對齊 Y，未修改零件。L19／L17／L21 為幾何長，不代表力學有效長或改善。v002 文字重疊已改版；舊版本保留。
- 圖源 STL 及生成程式各核雜湊／實際幾何，独立審查尺寸、方向及瀏覽器版面；`learning.tests.test_challenge_drawing_evidence` 確認四張新增題圖均可逐位元重生。圖面為教學草案，未宣稱符合完整製圖標準、切片、列印、配合或強度合格。其他章未建立專屬圖，網頁明示待補。

## 驗證與界線

- `python -m unittest discover -s learning/tests`：317 項通過、9 跳過；新增題圖來源再生測試另 1 項通過。前端工程頁、pilot 與挑戰頁測試共 36 項通過；`node --check`、`git diff --check` 通過。隔離服務覆蓋題目確認、筆記、舊 revision、重複確認及已登記檔被修改後拒絕；無任何實際學員資料寫入。
- 瀏覽器於 8777 測試題目、工程圖與工作區空值；8766 服務重啟後檢查 v002 題目、第 02 章圖、v031 的 11-05 待製作標記與詳述。試教及主線 0／245、revision 8；`progress.json` 雜湊 `b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1` 未改。
- 尚未提交或推送。完整螺紋實體、導孔五金適配、逐步重新實拍、實體列印／量測／試配及各題缺圖仍待製作；所有試驗間隙均非合格值。使用者詢問是否保留原教材，答覆現階段保留為來源與歷史參照，沒有刪除或搬移。

## 後續補充：題目 v004 與第 11 章兩個獨立 Blender 探測

- 依原始讀值新增第 07 章草圖題圖 `sketch-constraint-drawing-v002.svg` SHA `53741eccd9b255b36503f131b26c06ef38dd4e0e5c6a6cdebfb9d7c4505adcfe`（60×40 與 80×40 為同草圖的不同階段）、第 08 章 `parametric-box-drawing-v003.svg` SHA `9ec89fec47a4ac5fd7e7a97569d720398ffb30011bbc3fd15218580dd952616d`（80×50 固定基準，不能證明連動；0.4 為試驗值）。來源雜湊、讀值與圖面獨立核對並實際渲染目視；圖面不代表實體合格。
- 第 11 章外螺紋：`learning/evidence/08/2026-10-28-closed-external-thread-probe-v001/` 的網格由程式建立，獨立 Blender GUI 觀察、Non Manifold 檢查、另存與重開。邊界及非流形為 0、BVH 初步結果無非鄰接重疊，但不足以證明完全無自交或可列印；端部牙形不完整、無對件，完整 GUI 手工建模尚待製作。安全摘要 `safe-summary-v001.json`；[journal](2026-10-28-closed-external-thread-probe-v001.md)。
- 第 11 章盲孔柱：`learning/evidence/08/2026-10-28-boss-box-join-trial-v002/` 的柱由程式預建，獨立 Blender GUI 移位並 Boolean Union/Exact、另存與重開；第一次 operand 選取失敗後重試，v001 及重試證據保留。實讀單殼、非流形邊 0，無蓋孔或五金；材料、孔徑、強度與試配仍待定。安全摘要 `public-summary-v001.json`；[journal](2026-10-28-boss-box-union-trial-v002.md)。
- 版本 `challenges-v003.json` 在 v002 增 07／08 題圖及上述兩筆示範資料，`challenges-v004.json` 在 v003 基礎上釐清舊獨立柱與新接合柱為不同版本；最終 v004 SHA `c17a274a4e70ccd82463bd83f76a58f7a9821bafaa09fad402cc5766aa8a1af0`，由 `manage.CHALLENGES` 作為目前資料源。v001～v003 均保留；新版拒絕覆寫。試教頁第 11 章顯示原始實拍及已去識別的摘要，但原始 runner 含本機路徑／Recent，發布前仍要逐項審查。
- 本階段補充測試：v004／v003、挑戰資料交易、六張新題圖來源重生、v031 合計 19 項通過；三個前端測試共 37 項通過，含示範資源路徑保護。正式 8766 頁面實測 v004，08 張章節題圖路由及第 11 章兩圖／摘要可讀；進度仍 revision 8。第 01／04／11／12 題的專屬工程圖依各題性質與證據尚未製作；實體與完整手工操作仍待驗。
