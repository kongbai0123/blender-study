# 08-01：螺紋規格與建模參數參照 v001

日期：2026-10-25（Asia/Taipei）。助教以獨立Blender重新核對原04乾淨盒、另存並重開螺紋參照，保存12張真實原圖。**只有原盒與待定參數表，尚未選路線／規格／尺寸／五金，沒有Screw修改器、螺紋、柱、導孔、配對件或STL；沒有材料、強度、列印或試鎖合格結果。** 不代學員confirm。

## 來源與新版本

原 `learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend`，97,880 bytes，SHA-256 `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530`；本次 `demo-files/sources/u04_box_v001.blend`同hash副本。原檔／副本均未改，未繼承卡扣、定位柱、燕尾或任何合格間隙。

新 `demo-files/u08_thread_reference_v001.blend`：**97,955 bytes**，SHA-256 `9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f`，File > Save As／Open實際重開通過。scene_role=`unmodified_box_thread_reference`，只有Body_Reference一個mesh可見、Camera／Light hidden；Scale1、modifier0、matrix identity／rotation0。source/reference完整world頂點與triangles相同，local mesh SHA `7bdca49543ba3c35ed10f0ec8e5488cc28f8ff6d3e6f753739dfa29a9685ac26`、mesh data名Cube保持，只有名稱與教學檢視／隱藏狀態改變。

`parameter-record-v001.json` SHA-256 `0f858377bb80e173f00f3b39303c8f7d20f78d0f929446ae985a50fa7699229a`。紀錄完整保留模板的relative `source_scene`，另以absolute `source_scene_readback`記實際來源path/hash/bytes，`reference_scene`記新版本；`measured_box`／`face_measurements`只放真正網格與UI實選讀值，沒有用螺紋草案代替Blender量測。

## 真實操作與讀值

Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、獨立出廠設定／暫存，以Window.event_simulate執行。runner UTC `2026-10-25T12:28:52.474Z`～`2026-10-25T12:29:46.694Z`（台北20:28:52～20:29:46），completed／exit0／runErrors空；沒有操作學員正開的Blender或實體滑鼠。

1. Open原盒副本，Outliner選Cube，從實際mesh讀回外形／內腔。UI隱藏Camera／Light、改名Body_Reference，頂視／Frame Selected。
2. Edit Mode面選：分別取消前次選取並點前側盒口、內底、底視外底；每次實選1面／4頂點，保存world角點、bounds、spans。
3. Edge Select／Alt+A／F3 > Select Non Manifold，實選0邊；回Object Mode斜視，另存新參照版本、Open重開再重驗同一盒體。

| 實際量測項目 | Blender mesh／實選面讀值 |
|---|---|
| 盒外形 | 60 × 40 × 30 mm |
| 內腔 | 56 × 36 × 28 mm |
| 四側壁／底 | 各2／2 mm |
| 前側盒口面 | world Y −20～−18、Z15；跨度60 × 2 × 0 mm |
| 內底 | world Z−13；跨度56 × 36 mm |
| 外底 | world Z−15；跨度60 × 40 mm |
| 體積／拓撲 | 15,552 mm³，16頂點／28 loop triangles、NM0／單殼／genus0 |

盒壁2 mm只是原盒基準，不是已選螺紋柱肉厚或強度值。face-measurements.json保留Python unit factor造成的小量座標偏差；1e−4 mm僅浮點重建比較，不是牙型、製造公差、扭矩或配合合格門檻。

## 文件定義、草案與未設定項目

固定模板 `learning/plans/08-01-thread-parameters-v001.json` SHA-256 `92c0bf94ede81a48a5c16179ae1558bb8c61c521f960c79cd4ad05830f0d79bb`；官方來源facts `sources/engineering/thread-source-facts-v001.json` SHA-256 `78a0b7b1092287e7956b9a11da17f4b1ef838c7da50473e989d05cc759b67834`。六份Py／兩資料快照完整綁定，沒有使用來源示意圖。facts核對範圍含Blender 5.2手冊／API與已安裝build Screw實作、螺紋基本詞彙；ISO頁面僅官方摘要／標題，未取得完整標準與尺寸表，不宣稱標準符合性。

24個draft_parameters全部value=null、status=draft_pending，包含標準／公差／牙型、內外大中小徑、牙深、pitch／starts／lead、旋向、行程／嚙合、端部、間隙／相位／軸、柱與硬體孔。`route.selected=null`，三條路線（自訂列印、金屬螺絲／insert、兩者）仍未選；自訂列印只是助教first candidate，沒有寫成學員選擇。

`blender_mapping`是documented_mapping_only_not_configured：Angle、axis／axis object、Object Screw、Screw offset、Iterations、viewport／render steps、merge及export evaluation均null，modifier_created=false。文件說明pitch／lead／starts的區別與Angle360°、Object Screw關閉等映射條件，**不是已存在的RNA設定或實際螺旋讀值**；本步沒有代入公式、算螺旋或製作牙型。未將Screw通稱螺距、Iterations通稱線數，也沒有從盒體外框推定牙徑。

第五單元0.1～0.6 mm是未經列印／試配的總間隙幾何試驗點，未轉用為螺紋合格間隙。學員只提供噴嘴0.4 mm；不據此決定牙型、螺距、線寬、材料或導孔。硬體需實際型號與原廠孔／安裝條件，不能用通用值代填。

## 新空白試驗表與查核

新 `trial-fit-record-v001.json`綁這次參照scene／parameter record／template／facts，STL與part_versions列表空，沒有可列印的螺紋試片。對件／相對定位／夾持／protocol、選定規格／硬體、材料／列印／支撐、扭矩／拔出力／滑牙／循環／實測與qualified strength／clearance／torque全null；thread/boss/pilot/counterpart/modifier/calculation/STL/slicer/printed/fit/strength flags全false。這是新的08空白計畫，沒有把舊卡扣試片或盒蓋指定為對件，也未修改舊空白表。

實際main的 `_validate_records`與`_validate_lesson08_parameters`純驗證通過；新增10 meaningful匯入測試及既有07-01 10項，共20項通過。涵蓋24值／status、route與mapping不可冒稱已選／已配置、原盒local/world／面選取／hash、模板原source_scene與另欄readback、錯誤實體flags拒絕；沒有為尚未執行的數值公式新增假性計算測試。focused log SHA `1acd6db31830fbc5e4c32a4601c67f05a8eba83e7f0c23448a650302dcd26944`。正式全套tutor270項（269通過、1項Windows symlink權限略過）、server17項全通，JavaScript與publisher語法檢查通過，見automated-checks-v001.json。獨立標準庫audit也通過，含16原角點、有向平面面積／六條材質interval rays、三實選面與待定語義及來源，見independent-thread-reference-audit-v001.json，SHA-256 `61b6d3f726c9c2439e2424304f4c76e47491a95b6afcf7e19932fd3118084227`；沒有以本步未執行的螺紋／公式建模checker冒稱幾何成果。

`parameter-manifest-v001.json`綁新scene、參數表、空白表、2raw、三面紀錄、6Py／2data與12PNG；publication_audits預留給root，HTTP／browser結果另存publication-checks引用以避免hash循環，journal不綁當前hash。本段不宣稱網頁發布已完成。

基線保留52步，progress revision5／SHA `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`不變，未confirm或將助教檔登記為學員成果。工作區前後11項目相同，canonical SHA `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。允許root在08-01發布本次參照與參數內容，另僅補正08-02未來說明的Screw映射與第五單元未合格間隙時態；**08-02尚未建模**。

## 12張未修改原圖

完整動作／讀值在run.json；每張尺寸與hash核對通過，逐檔hash在manifest。probe-v001有12圖且通過，但保留未發布，未混入本main的事件、截圖或快照。

01. `08-01-01-source-open-dialog.png`
02. `08-01-02-source-checked.png`
03. `08-01-03-reference-top.png`
04. `08-01-04-rim-face.png`
05. `08-01-05-inner-floor.png`
06. `08-01-06-outer-floor.png`
07. `08-01-07-non-manifold.png`
08. `08-01-08-reference-overview.png`
09. `08-01-09-save-dialog.png`
10. `08-01-10-saved.png`
11. `08-01-11-open-saved.png`
12. `08-01-12-reopened-verified.png`

## 後續網頁發布核對

已正式匯入08-01的12筆助教操作，發布原盒實拍、24個待補參數欄位、路線選項、Screw條件映射及新參照場景下載。螺距／線數／導程、各種長度與間隙分欄；尚未選定規格或輸入修改器，未填的草案沒有冒稱為Blender已建牙的讀值。新空白試鎖表沒有可列印螺紋或STL，材料與實體結果仍留空。

同次只補正08-02的待實作定義：Object Screw關、Angle360°時Screw對應導程，單線才等於螺距，Iterations不是線數；第五單元沒有合格間隙可轉用。瀏覽器已預覽08-02確認其文字明示未執行建模／取得實拍，再回08-01。沒有執行08-02或修改其他課程內容。

12張PNG及5個下載（新blend、參數紀錄、manifest、新空白表、journal）HTTP逐位元核對成功。內嵌瀏覽器目視核對304×848畫面的原盒照片、材料與未建牙標示、路線待選、螺距／線數／導程與間隙欄位，以及Screw映射；保存4張未修改的原始JPEG與 `learning/evidence/ui/2026-10-25-lesson08-parameters-demo-v001.json`。原盒來源SHA保持、API catalog／progress與磁碟一致；52步指紋僅08-01與08-02的上述範圍改變，progress revision5／SHA `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`未變，沒有confirm或登記助教檔為學員成果。

不可變的獨立audit／測試／UI技術核讀已綁入manifest；最終HTTP與瀏覽器狀態由 `publication-checks-v001.json`保存並由catalog引用，避免與journal互綁hash。路線、標準、公差、尺寸、間隙、材料、扭矩／強度及實際列印／試鎖合格值均未選定或未驗證。
