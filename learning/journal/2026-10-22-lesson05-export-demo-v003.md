# 05-04：STL 匯出與數位尺寸核對（執行版本 v003）

日期：2026-10-22（Asia/Taipei）。使用者本次指定先完成插銷與孔板 STL 匯出及尺寸核對，實際列印與試配結果留空。原步驟「匯出、列印、試配」的後續部分仍未執行；本次完成的是助教匯出示範，不是學員已完成整步。

## 已產出的檔案與實際讀值

主 run 位於 `learning/evidence/05/2026-10-22-lesson05-export-demo-v003/`，兩份 STL 在 `demo-files/exports/`。

| STL 版本 | 實際檔內外形（按 mm 解讀） | bytes | 三角形 | 體積 mm³ | 連通殼 / Non Manifold / genus |
|---|---|---|---|---|---|
| u05_fit_coupon_v001.stl | 10 × 10 × 8 | 684 | 12 | 800 | 1 / 0 / 0 |
| u05_hole_plate_v001.stl | 96 × 26 × 4 | 142,784 | 2,854 | 7393.4816018 | 1 / 0 / 6 |

插銷 STL SHA-256：`bc10342c54a94d87c15eccb050fb9b30a7ae00bf4079d4c7869ac53d199db784`。

孔板 STL SHA-256：`8105d1ebdc04ed12a2b7f98cc3b728db74063c453961c33d165ac50e694c7c8b`。

孔板直接從 STL 三角面讀回六個貫穿方孔，X/Y 孔寬依序為 `10.1000061/10.0999990`、`10.2000008/10.1999989`、`10.2999954/10.2999992`、`10.3999996/10.3999987`、`10.5000019/10.4999995`、`10.5999985/10.5999999`。每孔下方盲凹點分別為 1～6 點，共 21 點，圓形邊界、凹點底面、深度及通孔射線均與來源幾何一致。

STL 本身沒有長度單位欄位。本次來源場景 Metric / Millimeters / Unit Scale 0.001，匯出 Scale 1、Scene Unit 不勾；核對 STL 座標範圍後按毫米解讀。匯入切片軟體的尺寸核對尚未執行，不能由這些結果宣稱切片設定正確。

## 操作、讀值與來源關聯

沿用 `learning/tutor/`，以獨立 Blender 5.2.1 LTS（build `9e2066aef7ef`）、出廠設定、English (US)、獨立偏好及暫存資料夾執行。模型選取、開檔、匯出選單、Selection Only、重新匯入及視角均透過 `Window.event_simulate()`；只有檔案瀏覽器的路徑與檔名欄位由程式直接填入。沒有使用學員的滑鼠或 Blender 視窗。

```text
python -X utf8 learning/tutor/run_demo.py lesson05_export learning/evidence/05/2026-10-22-lesson05-export-demo-v003
```

主流程共 18 筆動作與 Blender 原生 PNG：分別開啟插銷／孔板副本，選 FitPin／Plate，展開 File > Export > STL，記錄選項前後，勾 Selection Only，按 Export STL 後讀實檔，再於空白毫米場景 F3 搜尋 Import STL，重新匯入並讀取尺寸與網格。孔板只選 Plate，隱藏的 Cutters 沒有被匯出。匯出選項實際讀回為 Binary、Batch 關、Selection Only 開、Scale 1、Scene Unit 關、Apply Modifiers 開、Y Forward / Z Up。

重新匯入 Blender 的原始浮點讀值為：插銷 `10.000000475 × 10.000000475 × 8.000000380 mm`，孔板 `96.000004560 × 26.000001235 × 4.000000190 mm`，兩者 Non Manifold 邊為 0。檔內數字和重新匯入讀值的微小差異是數值重建誤差；比較門檻不是製造公差或配合驗收條件。

原始場景關聯：

- 插銷：`learning/evidence/05/2026-10-22-lesson05-demo-v002/demo-files/u05_fit_coupon_v001.blend`，SHA-256 `c2f3edd915324ba66bbd3fb8c6ad1ea0214a539f74cbc732e37adc35f7325162`。
- 孔板：`learning/evidence/05/2026-10-22-lesson05-holes-demo-v002/demo-files/u05_hole_plate_v001.blend`，SHA-256 `10bfffd651d1583d8704164288aa0757fa617f67a30e21176d7fc892aef3e692`。

先把原檔逐位元組複製到本次 run 的 `demo-files/sources/`，核對同一雜湊後由 UI Open。原檔與讀取副本在前後均維持相同雜湊，不存回來源、不新增假場景版本。執行版本 v003 和 STL 首次成果 v001 分別命名；`exports-manifest-v001.json` 關聯場景、來源 hash、STL hash、bytes、尺寸及實際選項。`source-snapshot/manifest.json` 保存本次實際腳本副本與 hash。

`stl_checks.py` 以純 Python 直接解析 binary STL，檢查長度、三角形數、非有限值、退化面、封閉邊、頂點連結、相鄰面方向、單一連通殼、正體積及 genus；孔板另讀實際內壁與 21 個盲凹點。匯入器會再次從實檔重算尺寸與拓樸，不只採信劇本宣告。尺寸 `1e-4 mm`、座標合併 `1e-5 mm` 與體積相對 `1e-5` 皆只處理浮點誤差。

## 執行版本與實拍修正

v001、v002 的 STL 匯出、檔內數字及重新匯入檢查均通過，兩份 STL 雜湊也與 v003 一致，但沒有發布為本步操作紀錄。v001 重新匯入的側欄停在 Tool，且 Selection Only 提示遮住其他選項；v002 改善取景與游標位置，但反覆點 Item 會收合側欄。v003 保留清楚的匯出選項與主流程證據；重新匯入畫面仍未展開 Dimensions，原主 run 不改圖、不改讀值，發布頁會移除不正確的 Dimensions 疊框並補註。另以同一 STL 的補充實拍呈現真正可見的 Dimensions。

探測用 `probes/2026-10-22-fit-export-ui-v001` 因將 RNA 的 set 直接序列化而中止，沒有匯出；v002／v003 探測圖與實際 operator properties 用於核對介面與安全設定，不作完成證據。所有舊 run 與原始圖保留，不覆寫。

## 尚未執行的實體部分

只知道噴嘴為 0.4 mm；材料、線寬、層高、方向及切片設定尚待紀錄。本次 `trial-measurements-v001.csv` 填入設計／STL 數位值與來源關聯，實體尺寸、列印條件與試配結果保留空白。

**0.1～0.6 mm 全部是總間隙試驗點。沒有任何值被認定為合格。** `slicer_checked=false`、`printed=false`、`fit_tested=false`；`physical_measurements`、`fit_results`、`qualified_clearance_mm` 均為 null。後續需實際切片核對、列印、量測及逐孔試插，才能判斷適用間隙。

主 run 的 runner 狀態 completed、runErrors 空白、工作區遞迴路徑及雜湊未變，Recent 清理無警告。未執行 confirm，也沒有把助教 STL 或讀取副本登記成學員成果。學員的完成狀態仍以共用 `learning/progress.json` 為準。

## 補充尺寸欄實拍與發布

補充 run 為 `learning/evidence/05/2026-10-22-lesson05-export-view-v001/`，共 6 筆實際操作與 6 張原始 PNG：空白毫米場景、插銷 Import 對話框、插銷尺寸欄、孔板 Import 對話框、孔板尺寸欄、最後來源與結果核對。它複製並讀取主 run 的同雜湊 STL，沒有產生新模型版本或存 `.blend`。原 STL 雜湊與補充副本前後一致，工作區未變；verification 同樣不含實體結果或合格間隙。

第 03 張 `05-04-03-pin-dimensions.png` 可直接看到 Dimensions 10、10、8 mm；第 05 張 `05-04-05-hole_plate-dimensions.png` 可看到 96、26、4 mm、Scale 1 及斜視的六孔／凹點。空場景沒有 Item 分頁，補充流程在第一個 STL 匯入後才點 Item 一次，第二個匯入後維持該分頁。發布前已逐張目視核對，沒有用合成圖補欄位。

網頁 05-04 目前列出 18 筆主流程、兩份 STL 的下載／尺寸／來源場景 hash 表格，以及上述兩張補充原圖。主流程第 15、17 筆 Dimensions 的不正確疊框只在發布 catalog 中移除，原 run 與原圖保留；旁註說明從程式讀值，與補充圖交叉核對。操作完成標示只指本次匯出示範，頁面明寫整步的列印／試配部分仍未做。

執行器、匯入器及 STL 檢查共 53 項測試無失敗（1 項 symlink 權限測試跳過），教學頁 API／CLI 17 項通過；前端 JavaScript 語法檢查通過。學員共用進度 SHA-256 保持 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`。

發布前另核對主流程與補充共 24 張 PNG 的原始尺寸、雜湊及 HTTP 位元組；兩份 STL 下載位元組與原檔相同，回傳 attachment，重新解析幾何亦通過。6 列試驗表的實體尺寸、列印條件、試配與合格間隙欄位全空白，來源原檔／副本與腳本快照 hash 均一致。結果見 `learning/evidence/05/2026-10-22-lesson05-export-publication-checks-v001.json`。

本機服務已在 8766 啟動，瀏覽器停在 05-04；實際頁面可見兩份 STL、尺寸、來源版本 hash 及尚未列印／試配說明。頁面未修改原始截圖保存在 `learning/evidence/ui/2026-10-22-lesson05-export-demo-v003.jpg`（1234 × 712），同名 JSON 記錄 SHA-256。未更新學員完成狀態。
