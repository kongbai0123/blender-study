# 05-06：蓋子 STL 匯出與 CAD 重新匯入（v001）

日期：2026-10-25（Asia/Taipei）。本次延續 05-05 已保存的上蓋場景，完成 **STL 匯出、實檔解析與 Blender 實際重新匯入**；切片、列印、實體量測與試配仍未執行。0.4 mm 總間隙／0.2 mm 單邊沿用助教選用的幾何試驗值，沒有成為合格間隙，也不是使用者指定的合格尺寸。

## 實際操作與原始圖

```text
python -X utf8 learning/tutor/run_demo.py lesson05_lid_export learning/evidence/05/2026-10-25-lesson05-lid-export-demo-v001
```

獨立 Blender 5.2.1 LTS（build `9e2066aef7ef`）、English (US)、出廠設定、獨立偏好與暫存資料夾，以 `Window.event_simulate()` 操作選單、勾選、鍵盤與視角。檔案瀏覽器的路徑和檔名由程式安全填入；Python 讀取實際物件與磁碟 STL 作驗證，沒有重建或修改蓋子幾何。操作不使用學員的 Blender 視窗或實體滑鼠。

runner 自 **2026-10-25T05:23:44.603Z** 至 **2026-10-25T05:24:47.823Z**；狀態 completed、exit 0、runErrors 為空。共 **12 筆操作、12 張原始 PNG**：

1. File > Open 05-05 v001 的同雜湊讀取副本。
2. 暫隱藏 Body，只選 Lid，底部斜視核對 Item 尺寸與中空定位環。
3. File > Export > STL (.stl)。
4. 核對本次 `demo-files/exports/u05_lid_v001.stl` 及匯出前選項。
5. 實際勾選 Selection Only；核對 Scale 1、Scene Unit 不勾、Apply Modifiers 開、Binary、Batch 關、Y Forward／Z Up。
6. 按 Export STL，解析磁碟檔案與實際環唇幾何。
7. File > New > General；清空獨立場景，設定 Metric／Millimeters／Unit Scale 0.001。
8. F3 搜尋 Import STL，選本次剛匯出的檔案；核對 Scale 1、Scene Unit 關、Y Forward／Z Up。
9. 實際匯入後切 Item、Frame Selected，讀回 Dimensions 與網格。
10. 拍攝重新匯入的底部斜視，核對一體定位環與盲內凹。
11. Edit Mode、邊選取、Select None、Select Non Manifold；實際選到 0 條邊。
12. 保存驗證 JSON 與來源版本關聯。重新匯入的獨立場景沒有另存為新的 `.blend`，原來源與副本保持不變。

原圖由 Blender 原生 screenshot 保存；12 張 PNG 的尺寸與 SHA-256 已逐一對照 `run.json`，像素未修改。網頁疊框不寫進原圖。`source-snapshot/manifest.json` 保存實際執行的七份腳本快照與各 hash，快照檔均已核對。

## 來源、STL 與版本關聯

- 原場景：`learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend`，**99,064 bytes**，含 Body 與 Lid。
- 原場景 SHA-256：`ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff`，與既有 05-05 `verification.json` 的檢查點一致。
- 讀取副本：本 run 的 `demo-files/sources/u05_lid_v001.blend`，99,064 bytes，SHA-256 與原場景相同；原場景與副本均未覆寫。
- 新 STL：本 run 的 `demo-files/exports/u05_lid_v001.stl`，**2,284 bytes、44 個三角形**，首次輸出 v001。
- STL SHA-256：`0b226cf405bc70f42b5ce28fee9f46cb55eff67b84c6d786c091a2043f5f2408`。
- 僅選取 **Lid** 並啟用 Selection Only，**Body 未匯出**。STL 選項為 Scale 1、Scene Unit 關、Apply Modifiers 開、Binary、Batch 關、Y Forward／Z Up。

STL 沒有長度單位標記；本流程將檔案中的數字按 **mm** 解讀。`exports-manifest-v001.json` 關聯原場景、副本、STL、實際選項與證據，沒有把讀取副本當成新的建模版本。

## 實檔與重新匯入的數位結果

| 項目 | 本次結果（mm） |
|---|---|
| Lid 整體外形 | 60 × 40 × 6 |
| 蓋板外形／厚度 | 60 × 40 × 2；板厚 2 |
| 定位環深度／環壁 | 4／2 |
| 定位環外形 | 55.599998474 × 35.599998474（名義 55.6 × 35.6） |
| 定位環內形 | 51.599998474 × 31.599998474（名義 51.6 × 31.6） |
| world Z | 整體 11～17；定位環 11～15；蓋板 15～17 |
| 實際 CAD 四側間隙 | 各 0.20000076293945312 |
| 實際 CAD XY 總間隙 | 各 0.40000152587890625 |

**整高 6 mm 由板厚 2 mm 加向下環深 4 mm 構成，不能把整高當成蓋板厚度。** STL 體積 `6195.199951171875` mm³，與名義 6195.2 mm³ 相符。來源、實際二進位 STL 與重新匯入物件 `u05_lid_v001` 均核對非空網格、單一封閉連通殼、Non Manifold 邊 0、Euler 2、genus 0；重新匯入 Scale 1。

`lid_stl_checks.py` 從實際 STL 三角形重讀拓樸，再以蓋板／環唇平面、面積、中心與環壁垂直射線、體積，以及來源內腔交叉核對，避免以實心塞或其他同外形物件冒充。`stl-verification.json` 及 `verification.json` 保存完整實際證據；重新匯入後也再次透過 Blender 讀值。

STL **保留原組裝座標 world Z 11～17 mm，尚未為列印床平移或核對擺放方向**。本次未啟動切片檢查，不能由 CAD 匯入成功推定已正確落床、可列印或可配合。名義網格四側間隙與沒有體積交疊只描述數位幾何；實體干涉仍為 null。

數值門檻 `1e-4 mm`、體積相對 `1e-5` 僅處理浮點重建／讀回誤差，**不是製造公差、配合間隙或列印試配驗收條件**。名義 0.4／0.2 與實際 CAD 浮點讀值分欄記錄在 `trial-fit-record-v001.json`，不將兩者冒充實測列印結果。

## 實體條件與進度

學員目前僅提供 **0.4 mm 噴嘴**，來源為 `learning/evidence/05/2026-10-22-print-conditions-v001.json`。列印方式、機型、材料、切片線寬、層高、列印方向與切片軟體仍待定；噴嘴直徑不能直接推出這些條件或正式合格間隙。

`slicer_checked=false`、`printed=false`、`fit_tested=false`；`physical_measurements`、`fit_results`、`qualified_clearance_mm` 皆保持 null。正式試配及合格判定仍須後續實體證據。

runner 遞迴工作區前後快照相同（**11 個目錄項、0 個學員檔案**），`workspaceChanges=[]`。本次沒有學員檔案可比對內容 hash；工作區快照的 canonical JSON SHA-256 前後均為 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`，序列化方式記在 manifest。

共用進度基線 **revision 5**，`progress.json` SHA-256 為 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`；本次不執行 confirm、不改共用進度，也不把助教示範檔登記為學員成果。此紀錄只記錄已取得的操作與檔案結果，頁面與發布核對另行記錄。

## 發布核對

05-06 已正式匯入 12 筆助教操作紀錄，補入三項操作說明、STL 下載與來源版本表，以及實際重新匯入的底斜視原圖；其他 51 步內容未改。瀏覽器已開啟 05-06 預覽，核對下載表格、12 筆實拍、尺寸與試驗間隙註記；未送出完成確認或登記學員檔案。

12 張 PNG 的 HTTP 回傳 bytes 與磁碟原圖完全相同，STL 下載 bytes／SHA-256 一致且為 attachment；API 課程與共用進度與磁碟一致。來源場景與副本 hash 不變，共用進度仍 revision 5，hash 與基線相同。完整發布檢查見同 run 的 `publication-checks-v001.json`。

測試：tutor 全套執行 85 項，84 項通過、1 項因 Windows symlink 權限跳過；其後來源 metadata 形狀修正所影響的 importer 42 項全部通過；教學伺服器 17 項通過，app.js 語法檢查通過。STL 詳細驗證只帶來源 body/lid 幾何；完整來源路徑與 hash 由主 `verification.json` 與 `exports-manifest-v001.json` 保存及交叉核對。

網頁原始截圖：`learning/evidence/ui/2026-10-25-lesson05-lid-export-demo-v001.jpg`，同名 JSON 保存拍攝方法、尺寸與 SHA-256；像素未修改。實體列印、實測及試配結果仍為 null，沒有合格間隙。
