# 07-03：剛體列印方向比較與原生 Overhang v001

日期：2026-10-25（Asia/Taipei）。由助教在獨立Blender實際比較Body／Lid原向與候選方向、開原生Mesh Analysis／Overhang、讀回四姿態與另存重開。**完成的是方向草案、原生視覺檢查及另算幾何統計；支撐方案與最終列印方向仍待切片，不是可列印、層間強度或實體試配合格結論。** 未代學員確認。

## 來源、草案與版本

07-02來源 `learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/demo-files/u07_cantilever_snap_v001.blend`，106,700 bytes，SHA-256 `5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305`。本次讀取 `demo-files/sources/u07_cantilever_snap_v001.blend`同hash副本，來源／副本未改。來源 `geometry-draft-record-v001.json` SHA-256 `4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a`保持不變；原臂、鉤、圓角、蓋裙／承接凸緣形狀與所有材料／力學待定值都延續07-02。

固定計畫 `learning/plans/07-03-print-orientation-draft-v001.json` SHA-256 `33831347ce131a3f29c107d18f24f0015b3314e8e8672dc2159b1d9badd4f6ac`。本次 `print-orientation-record-v001.json` SHA-256 `b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986`；保存計畫及實際資料，其中source_scene改為path/hash binding、poses改為四組實際讀值，原宣告姿態仍由計畫快照保留。

新 `demo-files/u07_print_orientation_v001.blend`：**106,462 bytes**，SHA-256 `360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d`；角色print_orientation_comparison_draft。兩件候選方向已Save As／Open重開，Body、Lid可見、兩建構Tools隱藏；Scale1／modifier0，未Apply Rotation，未修改網格形狀。工具位置、旋轉、matrix與local mesh hash前後完全相同，沒有納入Overhang分析。

## 原生操作與16張原圖

```text
python -X utf8 learning/tutor/run_demo.py lesson07_overhang learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001
```

Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、出廠設定及獨立設定／暫存，使用Window.event_simulate，不搶用學員視窗或實體滑鼠。runner **2026-10-25T16:21:04.172+08:00～2026-10-25T16:22:26.501+08:00**，completed／exit0／runErrors空白。

1. Open固定來源同hash副本，改前保存兩成品world polygons／loop triangles／法線及工具inventory。
2. Body原向平移落到Z0，再繞全局Y+90°側放；Lid原向裙底落床，再繞全局X180°翻面讓原板頂面朝床。四次各自單獨顯示成品、隱藏另一件與Tools，進Edit Mode，開Mesh Analysis並實拍設定／著色。
3. 回Object Mode顯示兩候選，核對Z0與分離距離；Save As新檔，Open重開，重算候選、工具狀態及版本hash。16筆主流程／16張原始PNG尺寸與hash核對通過，像素未修改。

六份raw保留world頂點、native polygon rings、triangle-to-polygon indices、polygon normals與CAD metadata；八份Py／四份資料快照、所有原圖及版本關係見 `print-orientation-manifest-v001.json`。UI probes保留但不混入主流程：ui-probe-v001 completed／4圖；ui-probe-v002 completed／4圖；ui-probe-v003 completed／5圖；full-probe-v001 completed／11圖。後續若有唯讀focus視角，須另列補證，不修改本run的events或腳本快照。

## 四姿態與尺寸的座標脈絡

| 姿態 | Object Rotation／Location名義mm | source-world剛體映射translation名義mm | world外框跨度約mm |
|---|---|---|---|
| Body baseline | (0,0,0)／(−40,0,15) | (−40,0,15) | 60 × 44.5 × 30 |
| Body candidate | (0,90°,0)／(−40,0,30) | (−40,0,30) | 30 × 44.5 × 60 |
| Lid baseline | (0,0,0)／(40,−3,6) | (40,0,−10.2) | 60 × 46 × 7 |
| Lid candidate | (180°,0,0)／(40,−3,1) | (40,−6,17.2) | 60 × 46 × 7 |

Lid原點在(0,−3,16.2)，所以Object Location不等同把原world頂點映射到候選的translation；raw與helper各保留實際值。Body候選world外框從 `[-55.0, -24.5, -6.556708171956416e-07]` 到 `[-24.999998092651367, 20.0, 60.0]`，跨度 `[30.000001907348633, 44.5, 60.00000065567082]`；Lid候選最低Z `-1.05704953057284e-06` mm。微小負Z約1e-6屬浮點，1e-4落床讀值門檻不是穿床允差或附著合格證據。

**N面板在未Apply Rotation時仍顯示Body物件軸向Dimensions 60 × 44.5 × 30。** 本紀錄30 × 44.5 × 60的world X/Y/Z外框由evaluated世界頂點另算，不能宣稱是直接從N面板讀到。候選Body原臂長+Z轉world+X、名義彎曲+Y仍為world+Y，兩方向平行XY僅是幾何條件，不保證不沿層間剝開、耐疲勞或強度合格。

兩候選X投影距 `34.99999809265137` mm、幾何分開；床面只是world XY的Z0，未指定機型、床幅、切片原點或真平台，未查容量／附著。

## Overhang角度、床接觸與離床面

四次原生設定均為OVERHANG／世界NEG_Z、show_statvis及show_overlays開、SOLID、Xray關。實際Min `0.0` rad／`0.0`°，Max `0.7853981852531433` rad／`45.00000125223908`°，保留RNA浮點值，沒有以UI四捨五入45°取代。

原生角度為面外法線與世界負Z的夾角：朝下0°、垂直90°、朝上180°。精確build原始碼用world軸轉回local；本課Scale1剛體旋轉不需Apply Rotation。低於Min為高端飽和，超過Max為灰色；本課0～45只是顯示範圍，不是材料、機型、橋接或支撐可接受角度。來源見 `sources/engineering/overhang-source-facts-v001.json`（SHA-256 `a2fa8d6c556cacb533b94648a994e2cb92baa33fccd4b513d9681d34187d8c05`）與[同build原生實作](https://raw.githubusercontent.com/blender/blender/9e2066aef7ef/source/blender/draw/intern/mesh_extractors/extract_mesh_vbo_mesh_analysis.cc)。未下載本地原始碼／PDF；本機UI source的實讀hash與版本範圍另列facts。

下表是從實網格**另算**的polygon面數／面積mm²，非原生面板提供的面數，也非GPU framebuffer顏色讀值。全polygon與loop triangle數分開，實際polygon法線及映射已核對；床接觸需整面落在Z0，離床朝下面另列。

| 姿態 | 全polygon／loop triangles | 床接觸朝下面：面數／mm² | 非床接觸朝下面：面數／mm² | 按原生標量定義在顯示範圍內且非床接觸：面數／mm² |
|---|---|---|---|---|
| body_baseline | 55／116 | 1面／2400 | 2面／47.7000046 | 2面／47.7000046 |
| body_candidate | 55／116 | 1面／1199.99992 | 11面／1057.53397 | 9面／1057.32414 |
| lid_baseline | 20／48 | 2面／27.0000076 | 1面／2745 | 1面／2745 |
| lid_candidate | 20／48 | 1面／2760 | 1面／12.0000076 | 1面／12.0000076 |

Body側放後的離床朝下面包含盒內壁、卡扣／根部等，與床接觸的側面不是同一組。Lid翻面雖讓大板面成床接觸，仍有約12.0000076 mm²的高處凸緣朝下面，不能說翻面免支撐。面數／面積不等於支撐體積或切片時間；沒有檢查橋接跨度、前層承托、內腔支撐移除、卡扣支撐痕或附著。

0°與45°附近1e-4°邊界帶逐面另列，包含端點的平面與浮點敏感斜面，不擴張原生remap範圍；Python double分類不宣稱逐GPU像素相同。polygon／loop triangle兩種統計及所有面索引、normal、angle、Z範圍可由verification追溯。

## 待定條件、查核及共用進度

support_strategy_status是pending_slicer_review；support_required、final_print_orientation_approved、slicer_support_settings、bridge_or_support_qualified皆null。材料、ε_allow、Q、δ_req、δ_allow、力量、實體量測／試配／干涉、合格強度與合格間隙也全null。strength_analysis_performed／fit_qualification／exported_stl／slicer_checked／printed／fit_tested／support_generation_performed皆false。已知0.4 mm噴嘴不推出材料、線寬、顯示角、間隙或強度。

實際main純validator與16原PNG紀錄通過；相關import tests **110項全過**（新增10項方向檢查），沒有由本次查核執行正式import。幾何1e-4 mm、體積相對1e-5、角度邊界1e-4°僅處理浮點重建，不是製造公差、可列印或支撐／強度合格門檻。

對照本run `publication-baseline-v001.json`的52步canonical基線，共用progress仍revision5，SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`；工作區前後一致，11目錄項／0學員檔案，canonical JSON指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。未confirm、未登記助教場景為學員成果。以下另記正式發布與補充focus視角。

## 唯讀淺視角補證

正式版本未改，另以 `2026-10-25-lesson07-overhang-focus-v002` 開啟同hash副本，只調視角、選面與Frame Selected。獨立設定內透過RNA設定navigation rotation_angle為3°，再送原生Numpad2事件；視線仰角實讀約−3.000006°，沒有直接寫view matrix或重畫畫面。選中並讀回Lid polygon18後取景，再取消橘色選取，圖06呈現Z約6.400003mm的凸緣底面紅色窄帶，以及下方Z0床接觸板的紅色大面。

主頁只引用該run的[圖06原圖](../evidence/07/2026-10-25-lesson07-overhang-focus-v002/07-03-06-elevated-ledge-closeup.png)，1494×1019，SHA-256 `39933f912508246987d4bf47773313b1d4ae312a60980c66c3cdda58faec799a`。原／副本hash、世界頂點／三角面／polygon及姿態與正式candidate完全一致；設定仍−Z／0～45°／Solid／Xray關，未另存模型，也未修改正式16筆events。六筆補證操作、原圖與11個程式／資料快照，另見[focus審閱紀錄](../evidence/07/2026-10-25-lesson07-overhang-focus-v002/focus-image-review-v001.json)。focus-v001的MMB未實際轉動，仰角0°，保留未公開，不當作成功紅面證據。

## 正式發布與獨立檢查

已正式匯入07-03的16筆助教操作，頁面提供四姿態比較、原生實拍、床接觸／非床接觸分項、待定提示及新場景／JSON下載，另附一張上述近照。52步canonical指紋只有07-03內容改變；共用progress hash、revision5及學員工作區不變，未代學員確認完成。

`audit_overhang.py`只用標準函式庫獨立重算有向邊閉合、單殼／Euler／正體積、剛體點及有向面保留、raw原生法線角度與映射三角面積，未呼叫既有geometry helper。四姿態均通過，分類mask／面積與主檢查一致；小miter面的raw原生法線與世界頂點重建角度最大差約0.000548°，明列於 `independent-audit-v001.json`，未放寬1e-4°邊界帶或冒稱逐GPU像素一致。

N面板Dimensions與world外框的區別也交叉核對[同build object.cc 3498～3513行](https://raw.githubusercontent.com/blender/blender/9e2066aef7ef/source/blender/blenkernel/intern/object.cc)：物件boundbox邊長乘scale的Dimensions不等於旋轉後世界XYZ外框。來源位置另記sources/manifest.json，沒有下載全文。

全套tutor **205項，204通過、1項Windows symlink權限跳過**；server **17項全過**，JavaScript語法通過。HTTP逐byte核對主流程16原PNG、新blend／JSON及補圖；最後頁面、檔案下載、API與progress／catalog一致性見 `publication-checks-v001.json`。瀏覽器原始實拍保存於 `learning/evidence/ui/2026-10-25-lesson07-overhang-demo-v001-*.jpg`；照片和數值均未作列印、支撐、力學或配合合格判定。
