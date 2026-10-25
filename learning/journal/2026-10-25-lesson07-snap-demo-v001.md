# 07-02：懸臂卡扣幾何草案 v001

日期：2026-10-25（Asia/Taipei）。本次由助教實際完成獨立 Blender 的 anchor／直臂／扣鉤／根部 Bevel、盒體 Union、蓋裙與承接凸緣 Union，另存重開核對。**只完成幾何草案與未變形靜態擺位，未證實可裝入、可彎曲、可拆卸或強度／配合合格。** 不代學員確認完成。

## 來源與新版本

07-01 原盒參考來源 `learning/evidence/07/2026-10-25-lesson07-parameters-demo-v001/demo-files/u07_snap_reference_v001.blend`，97,962 bytes，SHA-256 `6a6b6c03295c8b6047b97c3efdea9884954b714da87b45b7aa36b4d2b612d3a9`。本次讀取 `demo-files/sources/u07_snap_reference_v001.blend` 同hash副本，來源與副本均未改。原盒60 × 40 × 30、內腔56 × 36 × 28、壁底2 mm在改前重驗通過；這個分支未繼承燕尾軌或定位柱。

新場景 `demo-files/u07_cantilever_snap_v001.blend`：**106,700 bytes**，SHA-256 `5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305`，角色experimental_cantilever_geometry；Save As後實際Open重開，再讀網格及物件狀態。Body／Lid可見，SnapTool／FlangeTool隱藏，四者Scale1／modifier0，Camera／Light在本次副本中經UI刪除。Body原盒核心保留，但外掛卡扣已改變整體幾何，不能寫成Body完全未變。

07-01 空白 `parameter-record-v001.json` 保持SHA-256 `57d411f24486aad351056854b8eb427aae853b99f290372c9d0294d367ac6ead`，沒有事後填成已選材料或完成計算。新幾何由助教另選草案，計畫 `learning/plans/07-02-cantilever-geometry-draft-v001.json` SHA-256 `f4f0fab02a47eaade189c3b1c6cb8094753b435fe1a3ab570843af65fb2044be`；本次 `geometry-draft-record-v001.json` SHA-256 `4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a`，綁定原來源／新場景及body、lid、assembly實際讀值。草案數字不是材料／實體試配的合格規格。

## 實際操作與26張原圖

```text
python -X utf8 learning/tutor/run_demo.py lesson07_snap learning/evidence/07/2026-10-25-lesson07-snap-demo-v001
```

Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、出廠設定及獨立設定／暫存，透過Window.event_simulate送入UI事件，沒有搶用學員視窗或實體滑鼠。runner **2026-10-25T15:44:35.527+08:00～2026-10-25T15:47:45.160+08:00**，completed／exit0／runErrors空白。

1. 開07-01同hash副本、改前量測；建anchor9 × 4.6 × 3，頂面Inset1.5形成6 × 1.6直臂，E19再E2，選最高2 mm外側面E1.2成鉤。
2. Xray精選鉤外頂一邊、根部兩條凹邊；Ctrl+B分別輸入offset0.8／1段與offset0.6／3段，profile0.5、OFFSET／EDGES，立即讀原生operator。Exact Union指定SnapTool後Apply並查Body Non Manifold0。
3. 建60 × 46 × 2蓋板及裙／承接凸緣，以FlangeTool Exact Union；Apply並查Lid Non Manifold0。兩次operand均attempt0實際讀到正確物件，未用局部重試。
4. Lid僅抬12 mm展示部件，隨後回原位置讀靜態間距，Save As新版本、Open重開核對。抬高畫面不是接觸、彎曲或插入路徑模擬。

26筆操作／26張PNG的尺寸與SHA-256完整核對，像素未修改；每筆動作、讀值及原圖見run.json。五份世界mm raw mesh、七份Py腳本、三份資料快照與UI選邊／Bevel／operand紀錄，由 `geometry-manifest-v001.json`逐檔綁定hash／bytes。

| 部件 | 最終尺寸mm | 頂點／三角形 | 體積mm³ |
|---|---|---|---|
| Body含卡扣 | 60 × 44.5 × 30 | 60／116 | 15888.784532071566 |
| Lid含裙／凸緣 | 60 × 46 × 7.000000953674316 | 26／48 | 5602.200023460391 |
| SnapTool建構體 | 9 × 4.599998474121094 × 24 | 42／80 | 339.4844908728352 |
| FlangeTool建構體 | 10 × 2.700000762939453 × 5.199999809265137 | 16／28 | 85.2000062942534 |

四件均單殼、Non Manifold0／頂點link0／winding0、Euler2／genus0。Body的44.5包含向外anchor，原盒核心Y仍40；Lid整高約7包含裙／凸緣，**蓋板本身厚2**。

## 臂、圓角與靜態間距

幾何L為根部平面Z−8至承接面Z11的19 mm，尚未證實為力學有效L；直臂到Z13總高21，含anchor工具總高24，三者分開。實測臂厚 `1.5999984741210938`、寬6、鉤突出 `1.2000007629394531` mm；導入45°、承接面對退出軸90°只描述幾何，沒有估裝拆力。

根部Bevel輸入offset約0.6，不直接等同半徑。從實際三段弦端點擬合外側R `0.6000015007472784`、內側R `0.600001500747171` mm；網格仍為分段平面。原生Bevel根部不是固定寬6 mm的理想拉伸，而是六片寬6～7.2 mm的弦面及**12片有限三角miter端面**。checker已改為逐facet法向、角點、面積及所有原sample查核，未放寬1e-4門檻。`native_root_volume_mm3`的1.2047076581449612是預期弦面／端口的解析參考積分，不是獨立量到的實際根部體積；實際總體積以上表與raw為準。

| 未變形名義位置的實網格讀值 | mm |
|---|---|
| 板底至盒口 | 0.20000076293945312 |
| 臂外側至凸緣內端 | 0.2999992370605469 |
| 鉤外端至蓋裙內側 | 0.2999992370605469 |
| 鉤／凸緣Y投影重疊 | 0.9000015258789062 |
| 鉤底至凸緣頂垂直空隙 | 0.19999980926513672 |
| 直臂內側至原盒外壁的靜態空隙 | 1.4000015258789062 |
| 內側根部圓角局部靜態空隙 | 0.8000011444091797 |

幾何未相交只限本次**未變形的名義擺位**。1.2鉤突出、約0.9投影重疊、所需撓度δ_req及允許撓度δ_allow不能互換；約1.4直臂空隙與約0.8根部局部空隙也不是已證實的可用行程。未求接觸／插入路徑、未分配兩件變形。

## 探測版本與檢查範圍

UI probes保留未發布為課程成果：v001有4圖，因選面0停止；v002有4圖，選面X18～24與目標不符停止；v003有7圖，讀出Bevel為DEPTH而非OFFSET停止；v004有11圖，僅原生SnapTool成功；full-v001有20圖，完整幾何探測及五raw／assembly通過，但沒有正式保存場景。正式課程只採本次main v001的26圖及重開場景。

實際native miter揭露原檢查器「固定寬根部拉伸」參考不符，修正為有限端面模型，仍使用原EPS；回歸測試拒絕移動miter端面，允許合法三角面細分／重編索引。材料牌號、ε_allow、Q、δ_req、δ_allow、力量、實體量測、試配結果、實體干涉、合格強度與合格間隙皆null。strength_analysis_performed／fit_qualification／exported_stl／slicer_checked／printed／fit_tested皆false。已知噴嘴0.4不推出材料、線寬或合格配合。

實run純匯入validator與26張PNG完整性通過，未由本次查核執行正式import。相關import測試100項通過；發布代理已回報全套186項（185通過、1項Windows symlink權限跳過）、server17項與JavaScript語法通過。mesh比較1e-4 mm、宣告參數1e-6 mm、體積相對1e-5只處理浮點重建，**不是製造公差、允許應變或強度／配合合格門檻**。

## 進度與資料保護

已對照本run的 `publication-baseline-v001.json`（52步canonical指紋／progress hash）。共用progress仍revision5，SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`。工作區前後一致，11目錄項／0學員檔案，canonical JSON指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。未confirm，也未登記助教場景為學員成果。

`geometry-manifest-v001.json`記來源／副本、新場景、草案、原空白條件表、五raw、七腳本、三dataBindings、26原圖及探測版本。此階段沒有STL、落床、切片、列印、實測、試配或強度結論；正式catalog匯入、HTTP與瀏覽器發布由發布代理另記，不以本文件宣稱已完成。

## 正式發布核對

2026-10-25 已正式匯入07-02的26筆助教操作，核對52步canonical指紋，只有07-02內容改變。頁面新增草案尺寸表、材料／允許應變待定提示、原始實拍、場景及草案JSON下載；原07-01內容／參數表與共用progress revision5保持不變，沒有勾選學員完成。

HTTP逐byte核對26原始PNG、新blend及geometry draft JSON均一致；另以獨立有向邊／連通性／Euler／signed volume重算五份raw網格，皆一體閉合且方向一致。實檔與API catalog/progress一致，版本與來源hash可追溯。

已在實際304×848瀏覽器開到07-02，核對[實拍與草案提示](../evidence/ui/2026-10-25-lesson07-snap-demo-v001-overview.jpg)及[尺寸表／材料待定](../evidence/ui/2026-10-25-lesson07-snap-demo-v001-parameters.jpg)，保存原始JPEG bytes與hash，沒有重畫或像素修改，分頁保留開啟。全tutor186項（185通過、1項Windows symlink權限跳過）、server17項及JavaScript語法通過；未作列印或力學驗證。完整發布核對見本run `publication-checks-v001.json`。
