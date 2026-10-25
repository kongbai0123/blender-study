# 06-01：定位柱與對應穿孔幾何示範（執行 v006／場景 v001）

日期：2026-10-25（Asia/Taipei）。本次在 05-05 已保存的盒身與上蓋上，實際完成 **單一定位柱、蓋板穿孔、另存新場景及重開核對**。使用者要求沿用獨立 Blender 逐步操作、原始實拍、讀值及版本紀錄；本次不匯出 STL、不做切片或實體試配，也不代學員確認完成。

## 來源、執行及版本

原場景 `learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend` 為 **99,064 bytes**，SHA-256 `ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff`，與既有 05-05 `verification.json` 的檢查點一致。本次只讀取逐位元組副本 `demo-files/sources/u05_lid_v001.blend`，其大小與 hash 相同；原場景與副本均未改寫。改前的 Body／Lid 也重新讀取網格，分別保存在 `source-geometry-verification.json` 和最終 verification 的 `source_body`／`source_lid`。

```text
python -X utf8 learning/tutor/run_demo.py lesson06_tenon learning/evidence/06/2026-10-25-lesson06-tenon-demo-v006
```

成功執行版為 **v006**，新建模場景仍是首次 **v001**：`demo-files/u06_locating_tenon_v001.blend`，**105,466 bytes**，SHA-256 `f94dc6c5d342f04c41dddc37a4682805a5f7d87b5cf7a8b7bda37cd8ec51040f`。透過 File > Save As 另存，再 File > Open 重開，檔案 hash 與幾何讀值一致。

獨立 Blender 5.2.1 LTS（build `9e2066aef7ef`）、English (US)、出廠設定、獨立偏好與暫存資料夾，以 `Window.event_simulate()` 執行介面事件，不使用學員的視窗或系統滑鼠。新增柱、切割體及 Boolean Apply 由實際介面操作；Python 讀取實際網格並保存證據，不直接建立最終幾何。檔案瀏覽器的路徑與檔名安全填入程式欄位。

runner 自 **2026-10-25T13:57:39+08:00** 至 **2026-10-25T14:00:03+08:00**（Asia/Taipei）；狀態 completed、exit 0、runErrors 空白、reopened=true。

## 真實操作與 20 張原始實拍

1. 開啟既有盒蓋同雜湊副本，改前重驗盒殼／內腔／壁厚及原蓋子。
2. F3 Add Cylinder，設 4 × 4 × 30 mm、Apply Scale，中心 (23,13,1.5)，命名 TenonTool；讀回 32 段及 Z −13.5～16.5。
3. 選 Body 新增 Boolean，Operation 改 Union，Object 滴管指定 TenonTool；隱藏工具並 Apply。從最終網格核對與盒底連為一體，再實際執行 Select Non Manifold。
4. 新增 HoleTool，設 4.4 × 4.4 × 10 mm、Apply Scale，中心 (23,13,16)，讀回 32 段及 Z 11～21。
5. 選 Lid 新增 Boolean，先拍實際 Difference／Object 空欄。移動滑鼠、等待事件回合後點 Object 欄，輸入 HoleTool 並確認；第 10 張搜尋原圖仍顯示尚未指定，第 11 張才讀回 Difference／HoleTool。
6. `operand-attempts.json` 本次只記 **attempt 0：DIFFERENCE／HoleTool**，第一次指定即成功，**沒有使用局部重試**。隱藏 HoleTool、Apply，從最終孔壁與射線驗證蓋板貫穿，再實際執行 Select Non Manifold。
7. 拍攝 Lid 底部斜視，保留 Item Dimensions。暫把 Lid 上抬 12 mm 拍攝柱孔分離檢視，再下移 12 mm 回名義位置，重新核對間距、相位及嵌入量。暫時分離位置沒有保存成最終幾何。
8. Save As 新場景 v001、讀取大小與 hash、重新 Open；重讀 Body／Lid／兩工具，保存四份世界座標網格與最終 verification。

主流程共 **20 筆操作、20 張原始 PNG**；每張圖的尺寸與 SHA-256 已核對 `run.json`。原像素未修改，網頁疊框不寫進原圖。`source-snapshot/manifest.json` 中 **七份實際腳本快照**也逐檔核對 hash。最終 Body、Lid 可見、Scale 全為 1、修改器數 0；保留的 TenonTool、HoleTool 均隱藏。這些是實際 Blender 的觀察，不是示意圖或實體裝配照片。

## 幾何讀值：原盒殼與含柱外形分開

| 項目 | 實際／名義幾何（mm） |
|---|---|
| 原矩形盒殼 | 60 × 40 × 30 |
| 原內腔外框基準 | 56 × 36 × 28；四壁與底厚 2，內部新增定位柱 |
| 含柱的 Body 整體外形 | **60 × 40 × 31.5**；world Z −15～16.5 |
| 建構柱 | 32 段、名義外接直徑 4；中心 XY (23,13)，Z −13.5～16.5，高 30 |
| 建構時與底板重疊 | 0.5 |
| Union 後可量測的柱側壁 | Z **−13～16.5**，外露高 **29.5**；埋入底板的內面已消失 |
| 孔切割體 | 32 段、名義外接直徑 4.4；Z 11～21，高 10 |
| 最終蓋板穿孔 | 中心 XY (23,13)，Z **15～17** 真正貫穿 |
| Lid 整體外形／板厚 | 60 × 40 × 6／2；原環唇深 4、四側環壁均 2 |

原盒殼高 **30 mm** 與含柱 Body 高 **31.5 mm** 是不同讀值。建構柱下端 **−13.5** 來自單獨工具實測；最終 Union 網格能看到的柱側壁下端是 **−13**，不把已刪掉的內部面冒充最終網格讀值。最終 Body 有 **80 頂點／156 三角形**，體積 **15920.330541274525 mm³**，單一封閉殼、Non Manifold 0、Euler 2、genus 0。

新增穿孔後 Lid 有 **89 頂點／178 三角形**，體積 **6164.984350685121 mm³**，仍為單一封閉材料殼、Non Manifold 0，但拓樸變成 **Euler 0、genus 1**；不能沿用原無穿孔 Lid 的 genus 0。外形、環唇、孔壁、面積、正體積及多個材料區間射線共同核對，避免僅由 Bounding Box 或 Non Manifold 0 推定幾何成功。

## 名義間隙與實際 32 邊形間距分欄

助教沿用 **名義外接直徑總差 0.4 mm、名義徑向間隙 0.2 mm** 作數位試驗；這不是使用者指定的合格值。從最終柱、孔的 32 邊輪廓讀回相位與各孔邊法向，使用柱在該法向的最大支承值計算實際間距：

| 項目 | 本次數位實際值 |
|---|---|
| 柱／孔名義外接直徑 | 4／4.4 mm |
| 實際柱外接直徑 | 4.000000072261473 mm |
| 實際孔外接直徑 | 4.400000831756877 mm |
| 32 條孔邊中最小法向間隙 | **0.1990362137307402 mm** |
| 實際對邊總差 | **0.3980749428174466 mm** |
| 實際相位差 | **0.0 rad** |
| 柱伸入蓋板孔／柱頂到蓋頂餘量 | **1.5／0.5 mm** |

32 邊形的邊到邊距離不同於外接圓半徑差，不能把名義 **0.2 mm** 直接抄成實際最小距離。理想同相 32 邊形的法向參考值為 `0.2 × cos(π/32)`，本次仍以實際網格逐邊計算。完整 32 條法向間距與支承值、原矩形環唇的數位擺位 `ringfit` 另存於 `trial-fit-record-v001.json`。

這只是名義 CAD 幾何：單一圓柱定位點**不能完全限制旋轉**；沒有據此宣稱實體干涉、保持力或定位精度合格。

## 失敗執行版、probe 與共線分割點修正

下列早期版本均保留原資料、**未另存最終 u06 場景、未發布為完成示範**。雖然 Blender 程序 exit code 都是 0，runner 仍依內部錯誤正確記為 failed；程序結束碼不能取代幾何與操作驗證。

| 執行版 | 保留 PNG | 中止原因 |
|---|---|---|
| v001 | 8 | Lid 顯示／Boolean operand 的介面操作未符合預期；眼睛顯示點擊後視覺狀態不符，Boolean 指定檢查中止。 |
| v002 | 2 | 新的隱藏操作 guard 誤用僅接受 active mesh 的函式處理 Camera；相機不是網格而中止，屬 guard 型態限制。 |
| v003 | 9 | 前置 Boolean 選項已有實際原圖，Lid 為 Difference，但滴管未指定 HoleTool，實際 operand=None 而中止。 |
| v004 | 10 | Object 名稱搜尋在完整流程中的焦點／點擊時序不同，清單未打開；實際 operand=None，未因短 probe 成功就繼續。 |
| v005 | 11 | operand-attempt 0 已讀回 Difference/HoleTool；Apply 後舊 checker 要求邊界恰有 32 個樣本，未辨識 Exact Boolean 額外的共線分割點而中止。後續實際 raw mesh 分析確認不是第 33 個角，驗證器已修正，EPS 未放寬。 |

兩個獨立 probe 另作排查證據，不與 v006 的主幾何完成混算：

- `2026-10-25-tenon-operand-probe-v001`：**4 張原始圖**，實際打開 Object 清單、輸入 HoleTool、確認後讀回 Difference／HoleTool；沒有另存場景，只證明該次短流程的介面選取成功。
- `2026-10-25-tenon-operand-probe-v002`：**5 張原始圖**，Apply 後保存實際 `lid_mesh.json`（89 頂點／178 三角形）及 `u06_hole_diagnostic_v001.blend` 診斷檔；後者不當作教學主場景。raw mesh SHA-256 為 `4ae28e1981fa44e9be4d504a2d62b5fcecda16ec9634c84127aaa8191e797d9a`，固定為回歸樣本。

實際 Exact Boolean 在孔底 **Z 15** 形成 **33 個邊界樣本、32 個真角、1 個共線分割點**；孔頂 **Z 17** 為 **32 樣本／32 角、無多餘分割**。額外點到原邊約 **7.48e-8 mm**，不是第 33 個角。修正後驗證器保留原始樣本證據，仍要求 32 真角／32 側平面，並逐點檢查分割點確實落回已有線段；不以凸包隱藏凹陷。

尺寸 EPS **仍為 1e-4 mm，沒有放寬**。回歸測試保留固定 SHA 的實際樣本，並拒絕 31／33 個真角、向內或向外 **0.001 mm** 的非共線擾動。v005 因舊 checker 的邊界樣本假設中止，不寫成列印失敗或實體配合失敗。

## 可重算證據、實體空值與共用進度

四份 dump 都是實際物件的世界座標 mm 頂點／三角形及 CAD metadata，可由純標準函式庫重新核對工具、最終 Body、Lid 及名義擺位：

| 檔案 | 頂點／三角形 | SHA-256 |
|---|---|---|
| `body_mesh.json` | 80 / 156 | `930fcafdf6e09ba60bf7ea20e3e448f3cbdac9056d7a44e98e4369ca75ffde08` |
| `lid_mesh.json` | 89 / 178 | `4ae28e1981fa44e9be4d504a2d62b5fcecda16ec9634c84127aaa8191e797d9a` |
| `pin_tool_mesh.json` | 64 / 124 | `6174d4ab03382dab5f78e5c64a03420d5159ee2731ec8cafa9169e77d4595f4c` |
| `hole_tool_mesh.json` | 64 / 124 | `265695b0ddce711a6cfeaf3aa9942a4f73b3f03ae450b94a49d07eec6a4a5cd7` |

`scene-manifest-v001.json` 關聯來源、副本、新場景、四份網格、七份腳本快照與 operand 原始證據；journal 僅記路徑，避免後續補發布紀錄影響已凍結的場景／raw hash。`trial-fit-record-v001.json` 將名義值、實際 CAD 讀值與實體試配欄位分開。

學員僅提供 **0.4 mm 噴嘴**；列印方式、機型、材料、切片線寬、層高、方向與切片軟體仍待定。`exported_stl=false`、`slicer_checked=false`、`printed=false`、`fit_tested=false`；`physical_measurements`、`fit_results`、`physical_interference`、`qualified_clearance_mm` 全為 null。沒有把第五單元的試驗值當成既有實體合格間隙。

runner 的工作區前後快照相同（11 個目錄項、0 個學員檔案），沒有變更。工作區 canonical JSON 指紋前後均為 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`；本次沒有學員檔案可比對內容 hash。共用進度維持 **revision 5**，`progress.json` SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`；不執行 confirm、不更改完成度、不登記為學員成果。

數值比較 `1e-4 mm` 與體積相對 `1e-5` 只處理浮點重建誤差，**不是製造公差或實體配合驗收門檻**。本次發布前工具測試共 112 項（111 通過、1 項 Windows symlink 權限測試跳過），教學服務測試 17 項通過，前端 JavaScript 語法檢查通過。此處只記已取得的實作與檔案結果，教學頁發布／瀏覽器核對另行追加。

## 網頁發布與共用狀態核對

06-01 已正式匯入 20 筆助教操作、20 張原始實拍，補入三項操作指引、場景 v001 下載及來源 hash 表格，並以 Body 已 Union 的定位柱與 Lid 差集後的穿孔原圖作重點圖。第六單元目標移除已由本次要求釐清的「卡榫解讀待確認」措辭；其餘 51 步內容未改。教學頁已開啟 06-01 預覽，核對新場景連結、實際讀值與試驗間隙註記。

20 張 PNG 的 HTTP bytes／SHA-256 與磁碟原圖一致，新場景下載為 attachment 且 bytes／hash 完全一致。API 課程及共用進度與磁碟相同；progress.json 仍 revision 5，SHA-256 與基線 d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef 一致。未執行 confirm 或登記助教場景為學員成果。

最終 tutor 測試執行 112 項，111 項通過、1 項因 Windows symlink 權限跳過；教學伺服器 17 項通過，app.js 語法檢查通過。正式匯入前，實際 v006 的完整 validator 與獨立四份網格重算均通過。

完整發布檢查見同 run 的 `publication-checks-v001.json`。網頁原始截圖為 `learning/evidence/ui/2026-10-25-lesson06-tenon-demo-v006.jpg`，同名 JSON 保存拍攝方式、尺寸與 SHA-256；像素未修改。頁面與紀錄仍只確認數位幾何，未匯出 STL、切片、列印或實際試配，合格間隙與實體結果留空。
