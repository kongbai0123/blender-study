# 07-05：三件單參數幾何臂長試片 v001

日期：2026-10-25（Asia/Taipei）。助教從固定隱藏SnapTool分別獨立複製A_L19／B_L17／C_L21，僅改幾何根平面至扣鉤承接面長度，做候選擺位並另存重開。**本次只有獨立anchor＋臂＋鉤的三件幾何，不是全盒變體或已驗證改善；沒有指定對件／夾持、材料／力學、STL、切片、列印或實體試配。** 不代學員確認。

## 來源與版本

原07-03 `u07_print_orientation_v001.blend`，106,462 bytes，SHA-256 `360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d`；本次讀取 `demo-files/sources/u07_print_orientation_v001.blend`同hash副本，原檔／副本均未改。來源SnapTool原點(0,−22.200000762939453,−9.5)、R0／Scale1，42頂點、41原生polygons、80 loop triangles；其07-02參考raw SHA-256 `c60a6ed737f426277e0157ad1f7554a3070ba4395aec319693d6a2d9104c6140`，local mesh指紋70aa7799…bae2b2。原生根部三段弦面與12片miter端面保留。

固定 `learning/plans/07-05-coupon-length-draft-v001.json` SHA-256 `35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33`。07-02幾何紀錄與07-04匯出紀錄分別按固定hash保留；07-04兩STL與舊空白表也已逐檔對照其原manifest，**未覆寫**，只作版本沿革，不指定為本次對件。

新 `demo-files/u07_cantilever_length_coupons_v001.blend`：**108,728 bytes**，SHA-256 `22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8`；Save As／Open實際重開。`coupon-record-v001.json` SHA-256 `1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d`，綁計畫、新場景、source_tool／三source-frame／三candidate／layout與修改範圍。

新檔保留Body／Lid／SnapTool／FlangeTool四原件且全hidden，mesh、data、matrix均不動；另有三visible coupon各自獨立mesh，不與來源或彼此共享。**source_geometry_modified=false；coupon_geometry_modified=true；A=false、B/C=true。** 原盒／蓋未套用這些變體，不能將原件未改寫成新試片也未修改。

## 原生操作與24張原圖

```text
python -X utf8 learning/tutor/run_demo.py lesson07_coupons learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001
```

Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、出廠設定及獨立設定／暫存；以Window.event_simulate操作，不搶用學員視窗或實體滑鼠。runner **2026-10-25T17:29:48.813+08:00～2026-10-25T17:32:22.046+08:00**，completed／exit0／runErrors空白。

1. Open原場景副本，保存SnapTool及四原件inventory；加高Outliner，讓保留來源與三新件可見。
2. 每件都從原SnapTool執行Shift+D／Esc，取消位移但保留獨立副本，UI改名。實際關閉原先Mesh Analysis checkbox，show_statvis=false；本步沒有重做Overhang。
3. Front Orthographic／Vertex／Xray／B框選原source Z≥11的**14點**，原Z分別11／12.2／13；A保留、B GZ−2、C GZ+2 mm。逐點比對其餘**28點不動**，三件最大coordinate residual皆0，polygon拓樸不變。
4. Object Mode Ry90，不Apply；Location依序(0,−12,4.5)、(0,0,4.5)、(0,12,4.5)。三件各作Select Non Manifold實選0邊，合看分離候選；Save As新檔、Open重開再驗。

24筆／24張原始PNG的尺寸與SHA-256通過，像素未改。七raw、十一Py／五資料快照、選點／移動／duplicate proofs及來源inventory逐檔綁於 `geometry-manifest-v001.json`。完整probe-v001有20圖，成功但未存正式新場景，保留未發布，不混入main的24事件與快照。

## 實際變更尺寸與保留條件

下表全部從**coupon結果頂層**讀取source-frame實值；world候選外框另由旋轉後頂點計算。Edit Mode N面板Local Median不是L或world Z，Object Mode未Apply的物件軸Dimensions也不是world外框。

| 試片 | 幾何L mm | source承接面Z／臂頂Z mm | 全臂高／整件高mm | source-frame體積mm³ | 候選world外框mm |
|---|---|---|---|---|---|
| A_L19 | 19.0 | 11.0／13.0 | 21.0／24.0 | 339.4844908728352 | [24.00000023841858, 4.600000381469727, 9.000000065567079] |
| B_L17 | 17.0 | 9.0／11.0 | 19.0／22.0 | 320.28450918338206 | [22.00000023841858, 4.599999904632568, 9.000000065567079] |
| C_L21 | 21.0 | 13.0／15.0 | 23.0／26.0 | 358.6844725622883 | [26.00000023841858, 4.600000381469727, 9.000000065567079] |

幾何L從根平面Z−8到承接面計算；全臂高再含承接面上方2 mm，整件高另含anchor。Ry90候選逆算的L約18.999999841／16.999999841／20.999999841，與R0編輯讀值相差約1.6e−7 mm，屬浮點重建。

`held_geometry_readback`是**反算回原形的baseline profile**，B/C裡面恢復的L19、bearing11、armTop13不是B/C新尺寸；只用它核對固定h／b／u／root等。實際保留臂寬6、臂厚約1.6、鉤突出約1.2、上端2、鉤offset0.8／1段及根部offset0.6／3段；offset與弦端點擬合半徑分開，未改native miter。一般checker的連續逆映射可接受合法面細分／重新索引；本run另用原生42點、14上端／28保留點與實選座標證明真實UI動作，不能把一般surface等價當成已做過選點操作。

三件皆非空閉合、單殼／Non Manifold0／genus0；Y列距12 mm，兩相鄰外框淨隔 `7.3999998569488525` mm，純幾何分離，不代表機型床幅、夾治具或測試邊界合格。

## 只有anchor接床，對件與夾持未定

Ry90後只有anchor原+X側面以兩個loop triangles接觸數值Z0，三件面積約13.8 mm²；不是整件貼床。直臂world最低約1.499999 mm，root／miter最低約0.900000 mm，鉤也離床。沒有補底座、重做Overhang、產生支撐、橋接／附著或切片判定；方向僅候選、support pending_slicer_review。

這些是standalone anchor試片，尚無夾持方式、相對定位基準、共同載入protocol或已指定對件。B/C來源承接面Z改成9／13，原Lid未跟著設計；原Lid及07-04兩STL**不是三件試片已指定的試扣對件**。沒有把三變體套回全盒、求裝配路徑或證明可扣合。幾何L不是力學有效L，更沒有實測依據可稱縮短／加長帶來改善。

## 新空白試驗表、查核與進度

本次另建 `trial-fit-record-v001.json`，只綁新場景、coupon紀錄及三個物件的CAD幾何實值，不改填07-04舊空白表。mating_counterpart、relative_positioning_datum、clamping_conditions、anchor_clamping_or_fixture、full_box_boundary_equivalence、effective_mechanical_length_mm全null；共同比較protocol與各試片實測／載重位移／裝拆力／循環／破壞位置／夾具滑動等皆空白。已知噴嘴0.4僅引用學員原話，其餘材料、機型、線寬、層高、切片、方向與支撐待定。

材料、ε、Q、δ_req、δ_allow、力量、實體結果、合格強度／間隙及improvement_validated全null；improvement_assessed／strength_analysis_performed／deformation_analysis_performed／fit_qualification／exported_stl／mesh_analysis_overhang_checked／slicer_checked／printed／fit_tested皆false。未來有實際測試時另建版本，先記明夾持／對件／定位與共同邊界，再比較結果；本次沒有改善評分。

實際main純import validator及24原圖完整性通過；新增10項focused匯入測試通過。獨立標準庫audit也通過，見 `independent-coupon-audit-v001.json`，SHA-256 `81ecd99f47ed9e7d569bb729d82cf10ecb626f6a8a8ed0f7e32c4b489ed99c35`。位置1e-4 mm／體積相對1e-5僅作浮點幾何重建，不是製造公差、允許應變、支撐或強度／配合／改善合格門檻。

本run `publication-baseline-v001.json`的52步canonical基線已核對：progress仍revision5，SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`；工作區11目錄項／0學員檔案前後一致，canonical指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。未confirm，未將助教新場景登記為學員成果。manifest留publication_audits給發布代理追加正式HTTP／瀏覽器檢查後凍結hash，journal不綁當前hash以免後續發布段循環；本文件尚不宣稱網頁發布完成。

## 後續網頁發布核對

助教示範已正式匯入24筆操作，並將07-05原來的「套到小盒」改成此次已執行的臂長對照幾何草案；沒有實體試片結果，因此沒有選參數更新整盒。網頁列出A19／B17／C21的實際變體幾何L、全臂／整件高、候選世界外框、原始實拍、新場景下載及新空白試配表。來源、未驗證改善、材料／允許應變、夾持與支撐待定條件均保留。

正式全套tutor測試242項（241通過、1項因Windows帳戶不能建立symlink而略過），server17項通過；JavaScript及發布腳本語法檢查通過。最初測試探索路徑沒有找到測試，保留v001紀錄；正確的tests目錄執行結果見v002 logs及 `automated-checks-v001.json`，不把0項測試算成通過。

24原圖與5個下載（blend、coupon紀錄、manifest、空白表、journal）已經HTTP逐位元核對；內嵌瀏覽器實際預覽07-05，核對304×848窄畫面原圖、三件表格與展開條件，保存3張未修改JPEG及 `learning/evidence/ui/2026-10-25-lesson07-coupons-demo-v001.json`。API catalog／progress與磁碟一致，52步指紋只有07-05變更；progress revision5及SHA保持，學員確認／登記均未寫入。原07-04兩STL與舊空白表SHA也再次核對不變。

不可變的獨立audit、測試及UI技術核讀SHA已加入manifest；最終HTTP與瀏覽器發布狀態另見 `publication-checks-v001.json`，由catalog引用，避免manifest／journal互相綁hash造成循環。以上為本段新增時的數位示範與頁面核對，列印／試配結果及改善／強度／配合合格判定仍空白。
