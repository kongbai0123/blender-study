# 06-03：燕尾盒／滑蓋 STL 匯出與數位讀回（執行 v001）

日期：2026-10-25（Asia/Taipei）。本次實際完成 **Body 與 SlidingLid 分別只選單件的 STL 匯出、二進位實檔解析、在空白毫米場景重新匯入及組裝間距核對**。兩個輸出均由 Blender 原生 File > Export > STL 介面產生，後續驗證器唯讀解析。這只是06-03的數位階段；未匯出06-01定位榫STL，Overhang介面分析、落床安排、切片、列印及實體試配尚未做，也不代學員確認完成。

## 來源與首次 STL 版本

固定來源為 `learning/evidence/06/2026-10-25-lesson06-dovetail-demo-v002/demo-files/u06_dovetail_slide_v001.blend`（場景v001），**106,782 bytes**，SHA-256 `b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e`，與已驗證06-02檢查點相符。每件匯出前重新開啟本次 `demo-files/sources/u06_dovetail_slide_v001.blend` 同hash副本；原檔與副本均未改寫。**本次不另存新 .blend，也不把讀取副本登記為新場景檢查點。**

兩份首次版本v001位於本run的 `demo-files/exports/`：

| 實際原生匯出檔案 | 大小／三角形 | 尺寸（mm解讀） | SHA-256 |
|---|---|---|---|
| `u06_dovetail_body_v001.stl` | **6284 bytes／124** | 60 × 40 × 30 | `747e6186876f0e00c5c0617f0631de890a610696e42a930d5f7a0452f8ab4586` |
| `u06_dovetail_lid_v001.stl` | **3484 bytes／68** | 60 × 40 × **5.200000762939453** | `436597611a951ead9878cb330bda8a4a306f014cb70183c894987666113ee713` |

每份均單殼、Non Manifold0、Euler2／genus0，體積分別 **16655.36032775877／5752.3201428222455 mm³**。SlidingLid 整高約5.2，蓋板本身厚2、外露榫深約3.2 mm。

## 實際操作與25張原始實拍

```text
python -X utf8 learning/tutor/run_demo.py lesson06_dovetail_export learning/evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001
```

獨立 Blender 5.2.1 LTS（build `9e2066aef7ef`）、English (US)、出廠設定及獨立設定／暫存資料夾；以 `Window.event_simulate()` 驅動介面，不使用學員視窗或系統滑鼠。runner時間 **2026-10-25T14:49:38.632000+08:00～2026-10-25T14:51:46.352000+08:00**，completed、exit0、runErrors空白。

1. 開啟來源副本，只選Body，隱藏SlidingLid及三組建構工具，拍實際Dimensions和端面；File > Export > STL，核對路徑、檔名，再勾Selection Only後匯出。
2. 重新開啟來源副本，只選SlidingLid，重做選取／隱藏與尺寸核對，再另行匯出上蓋STL。第5／12張是Selection Only尚未勾的前置畫面；第6／13張才是實際確認後選項，不把前置狀態當成最終匯出設定。
3. 兩次最終選項均為 **Selection Only開、Scale1、Scene Unit關、Apply Modifiers開、Binary、Batch關、Y Forward／Z Up**；evaluation_mode為DAG_EVAL_RENDER。GuideTool、GrooveTool、MaleTool均未混入輸出。
4. File > New > General，清成0物件，設Metric／Millimeters／Unit Scale0.001。實際匯入兩份剛產生的STL，選項Scale1、Scene Unit關、Y Forward／Z Up，透過UI分別命名Body_STL、SlidingLid_STL。
5. 第一件匯入後才切Item，拍Dimensions及端面；兩件各執行Select None > Select Non Manifold，均選到0邊。兩件實際重匯入物在同一場景顯示並核對原world組裝位置，再保存四份world mesh與verification，場景未存檔。

共 **25筆完整操作／25張原始PNG**，尺寸與SHA-256均核對run.json，原像素未修改。九份實際執行腳本快照也逐檔驗hash；實際STL、來源與重匯入網格均以非空拓樸、實際斜面、端面面積、材料射線及體積交叉核對。不同合法三角化可保留同樣幾何，驗證未硬綁來源三角形signature或預定三角形數。

## 世界座標、剖面與試驗間距

STL沒有單位標記，本次數值**按mm解讀**。保留Body world Z **−15～15**、Lid world Z **12～17.200000762939453**；尚未落床平移、排版或選定列印方向。STL已烘焙世界座標，重新匯入物件Location為(0,0,0)，不重套原SlidingLid的Z16.2；Scale全1、修改器0。

最終盒體槽Z約11.8～15、底寬約3.6／槽口約2.32；上蓋外露榫Z12～約15.2、底寬約3.12／接板處約1.84。這些是最終材料邊界，完整建構工具的頂寬／高度仍見06-02紀錄。原56 × 36 × 28內腔是來源設計基準；上方加厚後中央盒口為56 × 28，不能推成全高度內腔未變。

助教沿用 **水平總差0.4／每側0.2 mm** 作試驗。來源、兩份STL及實際重匯入組裝各自重算後，以下數值一致：

| 數位實際讀值 | mm |
|---|---|
| 最小水平單邊間距 | **0.19999793767925667** |
| 最小斜面法向間距 | **0.19611411961014766** |
| 槽底／榫底垂直間距 | **0.19999980926513672** |
| 板底／盒頂間距 | **0.20000076293945312** |

水平0.2與法向間距不同；理想設計法向參考約0.19611613513818402，不替代本次實網格最小值0.19611411961014766。以上皆CAD讀值，沒有實體合格間隙或摩擦／保持力結果。

## 證據與共用進度

| 世界mm網格 | 頂點／三角形 | SHA-256 |
|---|---|---|
| `source_body_mesh.json` | 64 / 124 | `5784246ccc9ff4d1dcab5414fde1186a44855c5b5ed9635a3d38691fd3e812eb` |
| `source_lid_mesh.json` | 36 / 68 | `e8e796e8c63402966fbf51963544ebd1bc77027230b3b077390cecb8f59ade9b` |
| `reimport_body_mesh.json` | 64 / 124 | `58a546be74e16177d5d5056d9909b15b56a8601e39ac2606b0d54b876f7b5f7b` |
| `reimport_lid_mesh.json` | 36 / 68 | `e59cafe99f5cc5e6b01530544531d390edc2d6b99eb78b671fe5b646fbf9558a` |

`export-manifest-v001.json`關聯固定來源、副本、兩份原生STL、四份raw、九份快照、25張原圖的run記錄及匯出／匯入選項；journal僅關聯路徑，供稍後另加發布檢查。`trial-fit-record-v001.json`分開保存名義試驗、來源／STL／實際重匯入CAD量測與空白實體欄位。

學員目前僅提供 **0.4 mm噴嘴**，機型、列印方式、材料、線寬、層高、方向與切片軟體仍待定。`exported_stl=true`；`saved_new_scene=false`、`mesh_analysis_overhang_checked=false`、`slicer_checked=false`、`printed=false`、`fit_tested=false`。`physical_measurements`、`fit_results`、`physical_interference`、`qualified_clearance_mm`全null；未做Overhang分析或選定支撐策略。

工作區前後快照一致（11目錄項、0學員檔案），canonical JSON指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`；沒有學員檔案內容可比對，未寫入workspaces。共用progress仍 **revision5**，SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`，不confirm、不把助教輸出登記為學員成果。

尺寸比較 **1e-4 mm**、體積相對 **1e-5**僅處理浮點重建，**不是製造公差或實體驗收門檻**。本次實際run純驗證及25張PNG完整性通過；相關匯入測試80項通過。最終工具測試155項（154通過、1項Windows symlink權限測試跳過）、教學服務17項與前端JavaScript語法通過。此處不宣稱頁面已發布，正式匯入與HTTP／瀏覽器核對由後續發布紀錄補充。

## 網頁發布核對（2026-10-25，同日後續）

上述待發布紀錄之後，已正式匯入v001並更新06-03。52個步驟canonical摘要比對只有06-03改變；頁面含25筆操作、兩張重匯入重點原圖、兩份STL下載、來源hash及試配空值範圍。僅完成燕尾兩件STL數位階段，未代學員確認。

HTTP取得25張PNG，回應與磁碟原圖逐位元組相同，尺寸與hash匹配；兩STL下載分別6284／3484 bytes、Content-Disposition attachment，內容及hash皆正確。/api/bootstrap的catalog與progress等於磁碟；progress hash仍為baseline，revision5，沒有新增學員完成或檔案登錄。

既有分頁已開到STEP06-03並核對兩個下載、讀值及原圖顯示。原始網頁發布實拍`learning/evidence/ui/2026-10-25-lesson06-dovetail-export-demo-v001.jpg`，304 × 848，SHA-256 `84df2e63dd7dcdcd06b70fbb7a756f69bd54ba5625abd34670b0f40d79a42a96`；未修改像素。完整發布檢查見本run的`publication-checks-v001.json`：passed=true、publicationPending=false、browserProofPending=false。
