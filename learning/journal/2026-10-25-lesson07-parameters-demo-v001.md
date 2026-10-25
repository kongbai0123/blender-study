# 07-01：卡扣參數與估算條件（原盒參考場景 v001）

日期：2026-10-25（Asia/Taipei）。本次實際完成原盒基準面選取／讀值、參考場景另存重開及空白參數表，**尚未建立卡扣臂或代入公式**。材料與允許應變待定，不估裝拆力，不作強度或配合判定，也不代學員確認完成。

## 來源與版本

原04來源 `learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend`：**97,880 bytes**，SHA-256 `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530`。本次讀取 `demo-files/sources/u04_box_v001.blend` 同hash副本，兩者均未改寫。

新檔 `demo-files/u07_snap_reference_v001.blend`：**97,962 bytes**，SHA-256 `6a6b6c03295c8b6047b97c3efdea9884954b714da87b45b7aa36b4d2b612d3a9`，角色 **unmodified_box_reference**。UI將Cube改名Body_Reference，Camera／Light保留且隱藏；唯一網格仍為原盒，沒有定位柱、燕尾導軌或卡扣臂。Save As後實際Open重開，hash與原盒幾何讀回一致。

`parameter-record-v001.json` SHA-256 `57d411f24486aad351056854b8eb427aae853b99f290372c9d0294d367ac6ead`，綁定來源、新參考場景path/hash/bytes、原盒量測與三個實選面。原盒壁厚2 mm沒有填成卡扣臂h，燕尾0.4 mm也沒有沿用為卡扣間隙。

## 12張原始實拍

```text
python -X utf8 learning/tutor/run_demo.py lesson07_parameters learning/evidence/07/2026-10-25-lesson07-parameters-demo-v001
```

獨立Blender 5.2.1 LTS（build `9e2066aef7ef`）、English (US)、出廠設定與獨立暫存，以Window.event_simulate送出UI事件，不使用學員視窗或實體滑鼠。runner **2026-10-25T15:12:53.866000+08:00～2026-10-25T15:13:48.242000+08:00**，completed／exit0／runErrors空白。

1. 開啟原盒副本，Object Mode選Cube，重驗外形60 × 40 × 30、內腔56 × 36 × 28、壁底2 mm。
2. UI隱藏Camera／Light、改名Body_Reference，頂視Frame Selected。Edit Mode實際選盒口前側環面、內底，再底視選外底，各1面／4頂點。
3. 邊選取、Alt+A，F3 > Select Non Manifold，實際選到0邊；回Object Mode讀回原盒未改。
4. Save As新參考版本、核對bytes/hash、Open重開，再保存參數表及面座標。

12筆操作／12張PNG逐張核對尺寸與SHA-256，像素未改。兩份raw的世界頂點／三角形完全相同，均16頂點／28三角形、體積15552 mm³、單殼／Non Manifold0／Euler2／genus0；差別為物件CAD名稱。六份腳本與兩份JSON資料快照可追溯。

| 實選基準 | 實際讀值（mm） |
|---|---|
| rim的Y跨度 | **2.0000000949949026**，約Y−20～−18 |
| inner_floor Z | **-13.000000617466867**，面跨度約56 × 36 |
| outer_floor Z | **-15.00000071246177**，面跨度約60 × 40 |
| 內外底Z差 | **2.0000000949949026** |

這些是盒壁／底厚參考，**不是臂厚h**；角落斜邊也不是2 mm厚度方向。面座標Python單位倍率保留約1e-6 mm浮點差，與raw以1e-4 mm絕對門檻比對，並非製造公差。

## 待定參數與公式來源

L、h、b、根部R、倒扣u、所需撓度δ_req、導入α、退出β、扣合重疊e、間隙g、讓位f全部null。材料牌號、ε_allow、應變來源、割線模數、層向、服務條件、Q及所有估值／合格結果也保持null。已知噴嘴僅0.4 mm，不據此指定材料、臂厚或線寬。

固定模板記 `δ_allow ≈ 0.67 × ε_allow × L² / h`，依據[Covestro原冊](https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557218421.pdf) PDF第9頁Table1。ε用小數比例，百分比須除100；原冊0.67是近似係數，與古典精確2/3分開。**本步沒有數值計算。**

u是倒扣幾何量；δ_req依組裝路徑、接觸及兩件變形分配決定；δ_allow由材料與適用模型估算，不能直接令三者相等。[BASF原廠手冊存放副本](https://productdesignonline.com/wp-content/uploads/2019/08/Snap-Fit-Design-Manual.pdf)核對短臂／根部柔度的Q修正；Q不是安全係數，也未指定本盒Q值。原頁標籤、PDF頁序與存放來源見 `sources/engineering/snapfit-source-facts-v001.json`。未下載本地PDF，未證實未來卡扣符合該模型。

模板SHA-256 `11d4ac441bb213c3f1b14aeecdb35f581cfcf7398a55ad0142a8f37972c74e36`；來源事實紀錄SHA-256 `291d1704ea12834969e74e79b948cf2677524fda7a852fa8434c017a674169f8`。dataBindings將原檔與同hash快照綁定。匯入器拒絕填未知數值、改係數、指定Q、虛報計算／強度及變更盒體或三個選面。

## 紀錄與共用進度

`reference-scene-manifest-v001.json`關聯來源／副本、新參考場景、參數表、三面座標、兩份raw、六份腳本與兩份資料綁定，保留待定與未執行範圍。原始網格hash：

- source_body_mesh.json：`e0ec94210bff5cd7f113f32eb4a213e75553e40fb64bdf30ad3ece672a1d61bd`
- reference_body_mesh.json：`b3101108787bd264bf95af51db1d5c23aff408a95b4c961f77a66bb37ad29370`

`snap_arm_modeled`、`calculations_performed`、`strength_analysis_performed`、`fit_qualification`、`printed`、`fit_tested`、`slicer_checked`、`exported`皆false；實體量測、試配結果、合格力、合格間隙全null。Non Manifold0不代表卡扣強度或實體配合合格。

工作區前後快照一致（11目錄項、0學員檔案），canonical JSON指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。共用進度仍revision5／SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`，已與本run在發布前記錄的 `publication-baseline-v001.json` 核對（內含52步canonical指紋及progress hash）；也保留前次會話基線來源。未confirm或登記助教檔為學員成果。

相關匯入測試90項通過；發布代理最終全套165項（164通過、1項Windows symlink權限跳過）、獨立audit10項、server17項及JavaScript語法通過。實際run純validator與12PNG完整性通過。正式匯入、HTTP及瀏覽器發布核對由發布代理另行追加。

## 正式發布核對

2026-10-25 已正式匯入07-01的12筆實際操作；52步canonical內容比較只有07-01變更，共用progress SHA及revision5不變。參數表、完整原盒重開實拍、新參考場景下載與來源hash已呈現在網頁，沒有勾選學員完成。

HTTP逐byte核對12張原始PNG、新blend及參數JSON，全部一致；API的catalog/progress與磁碟一致。窄版304 × 848頁面已實際開到07-01，核對實拍、待定欄位與尚未代入公式，保留[原盒與公式畫面](../evidence/ui/2026-10-25-lesson07-parameters-demo-v001-overview.jpg)及[參數待定畫面](../evidence/ui/2026-10-25-lesson07-parameters-demo-v001-parameters.jpg)，原像素未改；瀏覽器分頁保持開啟。完整結果見本run的 `publication-checks-v001.json`，新場景及參數版本關聯見 `reference-scene-manifest-v001.json`。
