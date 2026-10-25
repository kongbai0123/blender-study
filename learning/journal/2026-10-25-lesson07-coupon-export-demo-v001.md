# 07-05：三件既有臂長試片的STL匯出與數位核對 v001

日期：2026-10-25（Asia/Taipei）。本次從已保存的A_L19／B_L17／C_L21候選分件原生匯出STL，再於空白毫米場景實際重匯入。**仍屬07-05，沒有增加課程步數；只完成數位準備，未改試片設計／原盒蓋、未Apply Rotation、未另存blend，沒有切片、列印、試扣或改善／強度／配合合格結果。** 重匯入確實建立三個新mesh datablocks；「沒有新幾何」限指沒有新試片設計，不能解讀成沒有新網格資料。

## 來源、版本與原生操作

固定來源 `u07_cantilever_length_coupons_v001.blend`，108,728 bytes，SHA-256 `22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8`；本run `demo-files/sources/`副本同hash，兩者未改。來源coupon紀錄 `1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d`、單參數plan `35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33`、原verification／SnapTool及三candidate raw均固定版本；12份Py與7份資料快照完整綁定。原七物件local mesh／data name／matrix不變，四原件Body／Lid／SnapTool／FlangeTool保持hidden。舊幾何版、manifest、空白表等6個protected files均與本run發布基線一致，未覆寫。

Blender 5.2.1 LTS（build `9e2066aef7ef`），獨立出廠設定／暫存與Window.event_simulate，沒有搶用學員視窗。runner UTC `2026-10-25T09:54:04.071Z`～`2026-10-25T09:57:04.150Z`（台北17:54:04～17:57:04），completed／exit0、runErrors空白。

1. 每件重新Open同hash副本，Outliner單選目標；其餘兩試片與四原件hidden。先實拍來源Item物件軸尺寸、Ry90及Front Orthographic輪廓。
2. File > Export > STL，明確核對Selection Only開、Scale1、Scene Unit關、Binary、Batch關、Y Forward／Z Up、Apply Modifiers開；沒有實際修改器。分別新建 `u07_A_L19_v001.stl`／`u07_B_L17_v001.stl`／`u07_C_L21_v001.stl`，解析實檔、完整有向來源面覆蓋及逆姿態／逆長度語義。
3. File > New > General，清空並設Metric／Millimeters／Unit Scale0.001。逐件Import STL，UI改名A_L19_STL／B_L17_STL／C_L21_STL；第一件後才切一次Item，每件核對Dimensions／正視輪廓／Select Non Manifold實選0邊，最後三件合看。

三件匯出與匯入均沒有window_manager operator history entry（`operator_history_available=false`）；id／options／filepath來自確認前**live File Browser active_operator**，再用真正新STL與新匯入mesh證明執行。沒有捏造歷程，也沒有把temporary checker封裝fixture當正式檔。probe-v001成功36圖但保留未發布；正式main是本run獨立36圖，不混入probe圖或快照。

## 三件正式實檔與實際重匯入

| 試片 | STL逆回幾何L mm | 全臂高／整件高 mm | STL world外框 mm | 重匯入Item尺寸 mm | bytes／triangles | SHA-256 |
|---|---|---|---|---|---|---|
| A_L19 | 18.999999841 | 20.999999841／24.000000238 | 24.000000238 × 4.600000381 × 9.000000000 | 24, 4.6, 9 | 4084／80 | `bb40b5f669601e11bc97d41f48e8a65552bfe99bb21645d47d359098c62af168` |
| B_L17 | 16.999999841 | 18.999999841／22.000000238 | 22.000000238 × 4.599999905 × 9.000000000 | 22, 4.6, 9 | 4084／80 | `ac0f9ca920197544f7c47465901beb98059b69b99d5aa9ad88ac9d73d16d017a` |
| C_L21 | 20.999999841 | 22.999999841／26.000000238 | 26.000000238 × 4.600000381 × 9.000000000 | 26, 4.6, 9 | 4084／80 | `1e3bb7cb883fd5d00319ebd9f44b761843b3c1b8f4c644e3333ac7a463083788` |

三件STL皆單殼、閉合、Non Manifold0／genus0；source-surface與完整inverse coupon檢查及實際重匯入均通過。STL重建體積A／B／C為 `339.48476649747744`／`320.2847191896239`／`358.6847710751142` mm³。來源R0編輯的幾何L19／17／21、承接面Z11／9／13與臂頂Z13／11／15另有原紀錄；上表為STL世界頂點逆算，細小差異屬浮點。`held_geometry_readback`恢復原形的L19不能當B／C變更值，這裡使用coupon結果頂層L／全臂／整件欄位。

來源未Apply，Item物件軸Dimensions是9×4.6×24／22／26，不能當world XYZ。STL無單位或自身rotation標記，本次數字按mm；world坐標保留Ry90候選。實際重匯入R0／Location0／Scale1、identity矩陣、修改器0，所以Item約24／22／26×4.6×9；Location0不是把零件移至原點，三個分列位置已烘在頂點。helper中的reference_pose_metadata／geometry_readback CAD只供逆幾何參考，不是STL或實際重匯入的Ry90。

三件數值最小Z均0，Y列距12、相鄰外框淨隔 `7.3999998569488525` mm。只有anchor側面兩個loop triangles接床，面積A／B／C約13.800001／13.800000／13.800001 mm²；直臂最低約1.499999、root／miter最低約0.900000、鉤也離床。沒有補底座、重做Overhang、產生支撐或核機型床幅；不能說整件貼床、免支撐或可直接列印。

## 新空白實體表與待定邊界

新 `trial-fit-record-v001.json`只綁這三個新STL版本、原場景／coupon紀錄／計畫與CAD幾何，未改填舊07-04或07-05空白表。mating_counterpart、relative_positioning_datum、clamping_conditions、anchor_clamping_or_fixture、full_box_boundary_equivalence、effective_mechanical_length_mm及共同試驗protocol均null。B／C承接面改為Z9／13，原Lid未改；舊Body／Lid／STL不是已指定試扣對件，也未求三變體與整盒裝配路徑。

僅已知學員噴嘴0.4 mm，引用原print-conditions證據；機型、材料／批號、線寬、層高、切片與支撐設定仍待定。材料、ε、Q、δ_req、δ_allow、力、實測、試配、合格強度／間隙與improvement_validated全null。方向／支撐候選，printed／fit_tested／slicer_checked／strength／deformation／improvement_assessed均false。未來實測另建新版本，先明定夾持、對件、相對定位及共同邊界，不能從幾何L推成有效力學L或改善。

## 查核、進度與36張原圖

實際 `_validate_records`及`_validate_lesson07_coupon_export`純驗證通過，未由本文件執行正式匯入。新增10個匯入tests；相關31項全通過（含合法三角細分／重新索引、native float identity、來源／選項／實體空值等拒絕）。root提供全tutor260項：259通過、1項Windows symlink權限略過；server17通過。全套之後補入三欄「建立重匯入mesh／沒有新設計」語義，再以31項focused補驗通過，log SHA `95685fa76f7dae6797cabf4074bf9fe98c692bc20ace7a561e3ff8a57f235224`；完整測試紀錄見 `automated-checks-v001.json`。1e−4 mm／weld1e−5 mm／volume相對1e−5僅浮點重建，不是製造公差、支撐、強度、配合或改善門檻。

`coupon-stl-export-record-v001.json` SHA-256 `21b7b935add72f1bce455882222079b6abc13591bc4c6b7f2c23e02927772b80`。`export-manifest-v001.json`逐件綁3STL、6raw、12Py／7data、36PNG與版本；manifest預留publication_audits給root追加不可變獨立查核／tests／UI技術核讀，HTTP／browser發布結果由外部publication-checks引用，避免hash循環。journal不綁當前hash；此時尚不宣稱網頁已發布。

獨立標準庫audit也通過，見 `independent-coupon-export-audit-v001.json`，SHA-256 `056ebabefae4ff81bb989ec3e6969abef5a2bee63deddaf7b792d080684ad0c3`；另驗binary長度／stored normals／有向雙向面覆蓋、逆回42個原角點、六raw、七source保護、三件fresh R0及layout。STL本次最小Z實值都是0，未沿用來源raw微負Z當作STL讀值。

本run `publication-baseline-v001.json`的52步指紋已保留；progress revision5／SHA `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`不變，沒有confirm或將助教STL登記為學員成果。工作區前後11項目相同，canonical SHA `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`，workspacesUnchanged=true。

全部36張為未修改原始PNG，尺寸與hash通過；動作與結果原文保留於run.json，逐檔SHA見manifest：

01. `07-05-01-A_L19-source-dialog.png`
02. `07-05-02-A_L19-source-selected.png`
03. `07-05-03-A_L19-source-profile.png`
04. `07-05-04-A_L19-export-menu.png`
05. `07-05-05-A_L19-export-before.png`
06. `07-05-06-A_L19-export-options.png`
07. `07-05-07-A_L19-stl-checked.png`
08. `07-05-08-B_L17-source-dialog.png`
09. `07-05-09-B_L17-source-selected.png`
10. `07-05-10-B_L17-source-profile.png`
11. `07-05-11-B_L17-export-menu.png`
12. `07-05-12-B_L17-export-before.png`
13. `07-05-13-B_L17-export-options.png`
14. `07-05-14-B_L17-stl-checked.png`
15. `07-05-15-C_L21-source-dialog.png`
16. `07-05-16-C_L21-source-selected.png`
17. `07-05-17-C_L21-source-profile.png`
18. `07-05-18-C_L21-export-menu.png`
19. `07-05-19-C_L21-export-before.png`
20. `07-05-20-C_L21-export-options.png`
21. `07-05-21-C_L21-stl-checked.png`
22. `07-05-22-empty-mm-scene.png`
23. `07-05-23-A_L19-import-dialog.png`
24. `07-05-24-A_L19-reimport-dimensions.png`
25. `07-05-25-A_L19-reimport-profile.png`
26. `07-05-26-A_L19-reimport-non-manifold.png`
27. `07-05-27-B_L17-import-dialog.png`
28. `07-05-28-B_L17-reimport-dimensions.png`
29. `07-05-29-B_L17-reimport-profile.png`
30. `07-05-30-B_L17-reimport-non-manifold.png`
31. `07-05-31-C_L21-import-dialog.png`
32. `07-05-32-C_L21-reimport-dimensions.png`
33. `07-05-33-C_L21-reimport-profile.png`
34. `07-05-34-C_L21-reimport-non-manifold.png`
35. `07-05-35-reimport-layout.png`
36. `07-05-36-coupon-exports-verified.png`

## 後續網頁發布核對

正式匯入36筆操作並更新同一07-05頁面，保留原24筆幾何示範於「先前助教示範」展開區，原場景下載與journal仍可存取。原couponReview的幾何讀值不改，只釐清前階段「未STL」的歷史時態並連結本次新空白試配表；沒有新增課程步數、沒有把助教示範當成學員完成。

完整tutor測試260項（259通過、1項因Windows帳戶不能建立symlink而略過），server17項通過；最後增補「重匯入確有新mesh資料／未新增試片設計／geometry_scope」三欄斷言後，另跑相關31項全通過。完整與補充測試有重疊，不相加當成獨立案例總數；實際logs與最終importer/test檔案SHA見 `automated-checks-v001.json`。JavaScript及發布腳本語法檢查亦通過。

36張原始PNG與7個下載（3份STL、export record、manifest、新空白試配表、journal）HTTP逐位元核對成功。內嵌瀏覽器實際預覽07-05，目視檢查原生實拍、A/B/C三組尺寸、材料／允許應變待定、新STL下載以及展開的原24筆紀錄；保存4張304×848原始JPEG，無像素修改。瀏覽器證據見 `learning/evidence/ui/2026-10-25-lesson07-coupon-export-demo-v001.json`。

API catalog／progress與磁碟一致；52步指紋只有07-05變更，來源幾何版六個保護檔案SHA／bytes均不變，progress仍revision5／SHA `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`。未confirm、未登記助教檔為學員成果。最終發布狀態由 `publication-checks-v001.json`保存並由catalog引用；manifest只綁不可變audit／測試／UI技術紀錄，避免journal與發布檢查互綁hash。所有材料、力學、支撐、實體試配與改善／強度／配合合格結果維持空白或待定。
