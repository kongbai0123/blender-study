# 2026-10-27 手工盒及上蓋的尺寸連動試驗 v001

## 環境與來源

全部是獨立 Blender 5.2.1 / CAD Sketcher 0.32.1 原生模擬事件；程式作插件啟用、來源複製、檔案視窗路徑填入、圖像及 Blender 資料讀回。原檔和真實學員工作區保留；範例未登記為學員成果，沒有確認進度或填實體列印、試配。啟用插件需提供本機隔離擴充套件目錄；首次因環境變數缺少而失敗的 `2026-10-27-manual-box-select-body-v001` 保留。

## 外框草圖與內腔

在視窗點可見盒側面，讀到 active Body，右鍵 Body Sketch 成功解決前輪選到 Body.001 的問題。X60→70 並存檔重開時，內腔 X 約束讀66，但切割體仍 X2..58。進 Body.001 Sketch 點右上更新後，切割體變 X2..68；上蓋尚未加入。安全摘要 `learning/evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json` SHA-256 `939576faf65242bffdafbe873116df6378811f19a06694165668f288c0fa216d`；此輪更新後狀態未另存，已存的是更新前 X70 版本。

GUI 複製外框 Y40 Driver 到內腔尺寸後，切割體曾到 Y42、超出盒體；不能當完成狀態。驅動器彈窗第一次點選錯位增加無效變數而保留於 `manual-box-y-driver-v001`；v002 正確設 Y−4 後，另存重開，外框70×40、內腔X2..68/Y2..38。後改80×50，內腔尺寸欄更新但幾何仍舊；進內腔草圖按更新後，內腔X2..78/Y2..48，存檔重開保持。兩個 scene driver valid；摘要 `learning/evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json` SHA-256 `1b8ed3dc2ccbdfffc2220d890f32256fd209fd774d607d72054c1980a24429d7`。初開圖出現 `sketcher.slvs_select` 未找到提示，原因未查明；Fully defined／driver valid 不代表已重算幾何。

## 固定上蓋及形狀鍵

第一輪方塊預設尺寸為 2000 mm、誤縮造成巨大蓋板，前置斷言停止於 `manual-box-lid-geometry-v001`。v002 GUI 先縮放，再底面 I 2.2、E 4、I 2、E −4，形成固定 80×50 的環唇上蓋，保存並重開。`learning/evidence/parametric/2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json` SHA-256 `3c4829f5b1ac01010dc1e4e98a3220388f3fc139e96b5e79c3b898736decf599` 列各高度世界頂點、兩件各 non-manifold 0；頂點推得各側約0.2 mm 的試驗間隙，仍非全面交集或物理試配。

在蓋板添加 X/Y 形狀鍵；分別 GUI 框選正側12頂點、各移10 mm，將兩鍵範圍設 −2..2。由外框欄 GUI Copy as New Driver、貼到鍵值後選 Scripted Expression，Key1 為 Scene X/10−8，Key2 為 Scene Y/10−5。剛貼時鍵值由80或50夾為2、蓋子暫時超大；設定公式後80×50基準鍵值回0。X driver v005 的模擬輸入不支援括號而失敗；v006 用等價的 X/10−8 成功。Y run 原始預定動作標籤部分沿用 X 字樣；實際 Key2 來源、目標和公式以原圖、state及安全摘要為準，不修改原 run。

## 實測尺寸與限制

80×50→90×60、更新內腔後盒口 X2..88/Y2..58、唇外 X2.2005..87.7995/Y2.2003..57.7997；兩 Key driver valid、值各1，保存重開保持。摘要 `learning/evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json` SHA-256 `35edd16270c9a9760dbc6d95e9302c1ce9f5c220051bc5e209274b7668494d80`。更新前 lid 已跟外框而 cavity 停舊值，可能暫時重疊；先重算再核對。

後續 GUI 依序90×50、80×60、70×40；以80×50為基準，分別為 X 單軸、Y 單軸和雙軸縮小。每次前後均讀回，手動更新後盒口與唇頂點各側約0.2 mm，Key 值分別 (1,0)、(0,1)、(−1,−1)；70×40另存重開。摘要 `learning/evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/manual-lid-multicase-verification-v001.json` SHA-256 `ae82d010881d8e8884a4ff2be468848b1cfe7f2cec31c32d69c66e23bef97d35`。以頂點邊界推算不能取代全模型碰撞、單殼或實體配合。

超界反例 X110/Y50：公式值3被 Key1 上限2夾住，更新內腔後盒框長110、蓋板約100，盒內 X2..108、唇外 X2.2005..97.7995，右側界限差約10.2005 mm，另存重開一致。摘要 `learning/evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/out-of-range-counterexample-v001.json` SHA-256 `e5dd705c5dca1622909554b16f1c4ec2457be7d7c6742c96642589a55ab8e84e`。此反例不能當成完成品。Key ±2 換算 X60..100/Y30..70 是理論未夾取候選區間，並非全區間驗證或製程安全範圍；v007 預檢專用既有程式盒，不能保護此手工版。0.4 mm 總間隙及約0.2 mm/側僅試驗值，實體列印、量測、試配及合格值均留空。
