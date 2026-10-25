# 06-02：燕尾滑蓋幾何示範（執行 v002／場景 v001）

日期：2026-10-25（Asia/Taipei）。本次以獨立 Blender 實際完成 **導軌加厚、兩端貫通燕尾槽、一體滑蓋、X 方向移動檢視、另存與重開**。使用者要求實際介面操作、原始實拍、讀值及版本紀錄；本次只完成數位幾何範圍，Overhang 介面分析、STL 匯出、切片、列印及實體試配仍未做，不代學員確認完成。

## 來源分支與檔案版本

本次從第四單元原盒另做滑蓋分支。06-01 的定位柱與第五單元環形唇邊會阻擋平移，因此未直接修改定位柱場景。固定來源為 `learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend`，**97,880 bytes**，SHA-256 `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530`。原04檢查點沒有獨立 verification.json；本次先實際開啟同 hash 副本並重新讀取原盒網格，保存 `source-geometry-verification.json` 與 `source_body_mesh.json`。

讀取副本為當次 `demo-files/sources/u04_box_v001.blend`，bytes／hash 與來源相同，兩者都未改寫。改前原盒為 60 × 40 × 30 mm，內腔 56 × 36 × 28、四壁與底厚 2 mm；原物件 Cube 讀值完成後才更名 Body。

```text
python -X utf8 learning/tutor/run_demo.py lesson06_dovetail learning/evidence/06/2026-10-25-lesson06-dovetail-demo-v002
```

成功執行版為 **v002**，新幾何場景仍為首次 **v001**：`demo-files/u06_dovetail_slide_v001.blend`，**106,782 bytes**，SHA-256 `b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e`。實際 File > Save As 另存，再 File > Open 重開，檔案 hash、Body／SlidingLid 與三組工具重讀一致，最終滑蓋已回 X0。

執行環境為 Blender 5.2.1 LTS（build `9e2066aef7ef`）、English (US)、出廠設定及獨立設定／暫存資料夾。以 `Window.event_simulate()` 將事件送進獨立實例，不使用學員的視窗或系統滑鼠。新增方塊、Edit Mode 複製／縮放頂面、Boolean 指定／Apply、平移及檔案操作均透過實際 UI；Python 只讀網格、檢查結果與保存證據，檔案瀏覽器欄位安全填入程式欄位。

runner 自 **2026-10-25T14:32:27.202000+08:00** 至 **2026-10-25T14:36:01.851000+08:00**；completed、exit 0、runErrors 空白、reopened=true。

## 24 張原始實拍與操作

1. 開啟原04同 hash 副本，改前核對盒殼、內腔及壁底厚。
2. 建立單條 60 × 6 × 5 mm 加厚方塊，中心 Y17／Z12.5；Edit Mode 複製並移 Y−34 mm，形成 Y±17 兩條 GuideTool。Body Boolean Union、隱藏工具、Apply。
3. 建立長62、底寬3.6、高4 mm 的 GrooveTool，Edit Mode 將頂面沿 Y 縮至寬2，再複製到另一側。Body Boolean Difference、隱藏工具、Apply；拍斜視與沿X的 Right Orthographic 實際端面，核對兩端入口及斜面。沒有重畫剖面。
4. Body 實際執行 Select None > Select Non Manifold，選到0條邊，與網格讀回一致。
5. 新增 60 × 40 × 2 mm 蓋板，中心 Z16.2；建立兩條 MaleTool，底寬3.12／頂寬1.76、高3.4，中心 Z13.7／Y±17。SlidingLid Boolean Union、隱藏工具、Apply；拍底斜視與端面，實際檢查 Non Manifold 0。
6. 回到名義組裝位置，從實際剖面讀取水平差、法向間距及垂直間距。三次 Boolean 指定在 `operand-attempts.json` 均為 **attempt 0**，分別讀回 Body/UNION/GuideTool、Body/DIFFERENCE/GrooveTool、SlidingLid/UNION/MaleTool，沒有使用局部重試。
7. 滑蓋沿 X 先移 +30，再 +32 到累計 +62 mm，分別保存實際 world mesh 及照片；移 −62 回 X0 後重讀。最後另存並重開新場景。

主流程 **24 筆完整操作、24 張原始 PNG**，逐張核對尺寸與 SHA-256。原像素未修改；網頁疊框不寫入原圖。**八份腳本快照**及 **八份世界座標網格**也逐檔核對 hash。Body、SlidingLid 可見；GuideTool、GrooveTool、MaleTool 隱藏；五件物件 Scale 全1、修改器數0。

工具為各含兩個獨立封閉殼的成對建構物，因此 Item Dimensions 顯示成對總外框：GuideTool 約60 × 40 × 5、GrooveTool 約62 × 37.6 × 4、MaleTool 約60 × 37.12 × 3.4 mm。Y 向總外框不是單條寬度；Location Y17 是第一條建立時的物件原點，兩條幾何中心實測為 Y±17。

## 完整工具與最終材料邊界分開

| 項目 | 本次幾何範圍與剖面（mm，近似閱讀值） |
|---|---|
| 加厚導軌 | 每條長60／寬6／高5，Y±17，Z10～15，Union 後不增加原盒外框 |
| 完整槽切割工具 | X−31～31，Z11.8～15.8；底寬約3.6、頂寬2 |
| 最終盒體燕尾槽 | X−30～30，Z11.8～15；底寬約3.6、盒頂槽口寬約2.32，實際槽深約3.2 |
| 完整榫工具 | X−30～30，Z12～15.4；底寬約3.12、頂寬約1.76，高約3.4 |
| 最終外露燕尾榫 | Z12～15.2；底寬約3.12、板底接合處寬約1.84，外露深約3.2 |
| 蓋板 | 60 × 40 × 2，world Z約15.2～17.2 |
| 整個 SlidingLid | 約60 × 40 × **5.2**，world Z12～約17.2；不是蓋板厚5.2 |

GrooveTool 高4的上段超出 Body 的 Z15 盒頂；最終槽不能抄成工具的頂寬2或深4。MaleTool 上端與蓋板交入約0.2 mm，Union 後該段內部表面消失，最終外露榫到板底Z15.2，不能把工具頂寬1.76抄成最終接合處寬度。完整工具與最終斜面均從各自實際網格量測；精確未四捨五入數值保存在 verification、manifest 及 trial-fit JSON。

Body 外框仍 **60 × 40 × 30 mm**，體積 **16655.36032775877 mm³**，**64 頂點／124 三角形**，單一封閉殼、Non Manifold0、Euler2／genus0。原內腔 **56 × 36 × 28** 僅為來源基準；加厚導軌改動上方 Z10～15，中央局部盒口縮為 **56 × 28**。下方原內壁仍保留，不能把最後腔體寫成全高度均維持56 × 36 × 28。最小導軌側肉厚 **1.200000286102295 mm**，槽底到導軌下緣餘量 **1.8000001907348633 mm**。

SlidingLid 體積 **5752.3201428222455 mm³**，**36 頂點／68 三角形**，單一封閉殼、Non Manifold0、Euler2／genus0。網格檢查同時核對實際斜面、軸向面積、端面、材料區間射線、正體積與拓樸，沒有只靠外框或Non Manifold0認定成功。

## 試驗名義值、理想參考與實網格最小值

助教選用同高度 **水平總差0.4／每側0.2 mm** 作幾何試驗，並非使用者指定的合格值。斜面設計斜率為0.2（距垂直約11.3099°），水平間距與垂直於斜面的間距不同。

| 項目 | 數值（mm） |
|---|---|
| 名義水平總差／每側 | 0.4／0.2；助教試驗 |
| 理想設計法向參考 `0.2 / sqrt(1+0.2²)` | **0.19611613513818402** |
| 實際最小水平單邊間距 | **0.19999793767925667** |
| 實際最小斜面法向間距 | **0.19611411961014766** |
| 實際槽底／榫底垂直間距 | **0.19999980926513672** |
| 實際盒頂／板底間距 | **0.20000076293945312** |
| 斜面共同覆蓋的垂直範圍 | Z12～15，高3 |

**第17筆原始 observed 的「法向間距約0.196116 mm」是理想設計的近似參考，不是實際網格最小值。** 精確最小值為 **0.19611411961014766 mm**；本紀錄明確補註，保留原始 run.json 與照片，不覆寫原始紀錄。實際四面、兩個高度端點的水平／法向間距與微小斜率差均保存在 `trial-fit-record-v001.json`。以上差異是 CAD 浮點讀值，未據此提出製造公差或實體驗收結果。

## 數位滑動路徑與限制

| 實際滑蓋 X 位移 | X 外框 | 沿X重疊長度 | 脫離／端部餘量 |
|---|---|---|---|
| 0 | −30～30 | 60 | 尚未脫離 |
| +30 | 0～60 | 30 | 部分重疊 |
| +62 | 32～92 | 0 | 完全脫離，與盒端間隔2 |

+30／+62 的實際網格減去平移後，仍通過同一滑蓋剖面檢查且 oriented-triangle signature 一致。兩端槽口、沿X全長均勻剖面及正橫向間距共同支持 **X0～62的名義剛體平移路徑無幾何相交**；不是只看三個畫面就推定所有中間位置。最終場景回到X0。

這版沒有端擋、止退或鎖定結構。此證據未量測摩擦、變形、保持力、列印粗糙度或實體可滑動性；`physical_interference` 仍null。

## v001 中止與短 probe

`2026-10-25-lesson06-dovetail-demo-v001` 保留 **7張成功原始PNG，加第8筆error紀錄**；Apply Difference後已保存 `body_mesh.json`，但未另存最終場景，也未完成整體教學。舊驗證器 expected X planes漏列原盒保留的 **x=−28／+28內端壁，各面積968 mm²**，所以報 `unexpected X face-plane count`。程序exit0但runner正確記failed；這是驗證器漏列面平面的假設，不能寫成Boolean操作失敗或實體試配失敗。

修正版補上這兩片既有內端壁，並維持外端入口證據只取x±30的兩片外端面。尺寸EPS仍 **1e-4 mm，未放寬**。原v001 Body raw經修正版重算已通過，體積 **16655.36032775877 mm³**、單殼／Non Manifold0／genus0；原失敗資料不覆寫、不發布完成旗標。

先前 `2026-10-25-dovetail-ui-probe-v001` 為獨立短probe，**6張原圖、84.614秒**，驗證加厚導軌、Boolean UI及GrooveTool完整工具剖面。它沒有完整滑蓋、最終另存或重開，不與v002主流程完成混算，也未發布為完成示範。

## 可重算證據、實體空值與共用進度

| 世界mm網格 | 頂點／三角形 | SHA-256 |
|---|---|---|
| `source_body_mesh.json` | 16 / 28 | `e0ec94210bff5cd7f113f32eb4a213e75553e40fb64bdf30ad3ece672a1d61bd` |
| `guide_tool_mesh.json` | 16 / 24 | `aedbd25b5cae2d97bdc19cfd400048daa15b016914108d98ae2916148b8e1bce` |
| `groove_tool_mesh.json` | 16 / 24 | `0cca5863d62cd43661302fea7cf94d2e0a86b35209af0283de99787134b9f0b5` |
| `male_tool_mesh.json` | 16 / 24 | `7377acc23ce77bcb73d9bde09c15c76c136b99404292ac997d90df53615bdcd4` |
| `body_mesh.json` | 64 / 124 | `5784246ccc9ff4d1dcab5414fde1186a44855c5b5ed9635a3d38691fd3e812eb` |
| `lid_mesh.json` | 36 / 68 | `e8e796e8c63402966fbf51963544ebd1bc77027230b3b077390cecb8f59ade9b` |
| `travel_30_lid_mesh.json` | 36 / 68 | `72e68840b1dc7df0575ba30d18998a17ac5ae4fa47c6e444a4f9bb312f5618ec` |
| `travel_62_lid_mesh.json` | 36 / 68 | `031782e98521b6c83139e90612ef6a39e3572abccd71cf7848919b7b9ce3c39d` |

`scene-manifest-v001.json` 關聯原來源、副本、新場景、八份raw網格、八份執行腳本、24張原圖及Boolean operand紀錄；journal只記路徑，不凍結目前journal hash，供稍後追加發布核對。`trial-fit-record-v001.json` 將名義試驗、理想參考、實際CAD讀值及尚無結果的實體欄位分開。

學員目前只提供 **0.4 mm噴嘴**；列印方式、機型、材料、線寬、層高、方向與切片軟體仍待定。`mesh_analysis_overhang_checked=false`、`exported_stl=false`、`slicer_checked=false`、`printed=false`、`fit_tested=false`。`physical_measurements`、`fit_results`、`physical_interference`、`qualified_clearance_mm` 全null。尚未使用 Mesh Analysis > Overhang，不能宣稱已標出懸空區域、確認列印方向或選定支撐策略。

runner工作區前後快照相同：**11個目錄項、0個學員檔案**，canonical JSON SHA-256均為 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。本次沒有學員檔案可比較內容hash；沒有寫入workspaces。共用進度仍 **revision5**，progress.json SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`，不confirm、不登記助教檔為學員成果。

數值比較尺寸 **1e-4 mm**、體積相對 **1e-5**只處理浮點重建，**不是製造公差或實體配合合格門檻**。實際v002的完整網格／來源／快照純驗證及24張PNG完整性已通過；相關匯入測試69項通過。主流程最終工具測試133項（132通過、1項Windows symlink權限測試跳過）、教學服務17項通過、前端JavaScript語法通過。此處只記已取得的檔案與數位結果，正式匯入、頁面發布及瀏覽器／HTTP檢查尚待後續另記。

## 網頁發布核對（2026-10-25，同日後續）

上述待發布記錄之後，已正式匯入v002並發布06-02。52個步驟canonical摘要比對只有06-02改變；網頁包含24筆操作、三張重點原圖、場景下載與來源hash，且補註理想法向參考與實網格最小值、行程圖active Body側欄的歸屬。Overhang及實體階段維持未執行，不代學員確認。

HTTP逐張取得24張PNG，回應內容與磁碟原圖逐位元組相同，尺寸及hash匹配；場景下載106782 bytes、Content-Disposition attachment，與新場景hash相符。/api/bootstrap的catalog與progress均等於磁碟；progress hash仍為baseline，revision5、學員完成與檔案登錄不變。

既有教學分頁已開到STEP06-02並核對內容、下載與原圖顯示。瀏覽器原始發布實拍：`learning/evidence/ui/2026-10-25-lesson06-dovetail-demo-v002.jpg`，304 × 848，SHA-256 `33c0f459d16a86c8ec9fade505492c735d290d9cc23a010c6ab16b22bd077051`；原像素未修改。完整發布結果見本run的`publication-checks-v001.json`，passed=true、publicationPending=false、browserProofPending=false。
