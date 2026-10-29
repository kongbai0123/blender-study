# 工程學習路徑與草圖前置驗證 v001

2026-10-27，Asia/Taipei。使用者於討論公差與量測前置、同一小盒串起草圖／參數連動／配合試驗後，指示「開始進行上述的討論內容」。本輪落實新閱讀路徑、第一個觀察小步與草圖環境技術驗證；沒有把12章規劃當成12章正式教材已完成。

## 本輪交付

- 新入口：<http://127.0.0.1:8766/#engineering/ch01>。新增「工程學習路徑」頁籤，保留原9單元52步及原學員進度。
- `learning/web/engineering-path-v001.json` 保存12章的目標、實作、功能、快捷操作情境、既有參照、預期產出與待補項目。順序為用途與基準、公差與量測、毫米操作、約束草圖、盒蓋連動、試片、匯出與實測、定位與燕尾、卡扣、螺紋、尺寸鏈與交付、渲染。渲染可在第05章後穿插。
- 第一小步 `path-01-observe-lip` 使用05-05的分離視圖與底面原圖，辨認蓋板及唇邊。圖片逐張檢查，版本與SHA-256附於頁面。未重畫、未合成、未修改原圖。
- 頁面只讀共用進度，無新完成資料庫、無自動confirm；點選參照只打開原步驟預覽。新觀察題不能當成原01-01或05-05的操作完成。
- 草圖最小試驗通過，見[獨立交接](2026-10-27-cad-sketcher-environment-trial-v001.md)及 `learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/environment-verification-v001.json`。網頁只連安全摘要，不連含Recent清單的原始runner-status。

## 參數與工程界線

沿用原盒60×40×30 mm、內腔56×36×28 mm；側壁厚與底厚各2 mm，保持獨立參數。原蓋板60×40×2 mm，唇邊外框55.6×35.6 mm、壁厚2 mm、深4 mm。水平總間隙0.4 mm，在置中條件下單側0.2 mm，維持草案試驗值。

規劃以草圖長寬作主控，盒高、側壁厚、底厚、蓋板厚、唇邊深度及間隙各自具名。JSON只作快照與核對，不和草圖同時成為可各自改寫的尺寸來源。60→80 mm後內腔76 mm、唇邊75.6 mm只是後續整盒試驗的預期值，並非本輪盒蓋的實測。

0.4 mm噴嘴不推定線寬或製程能力。材料、允許應變仍待定；列印、實體量測、試配、合格間隙欄位留空。網站及數位草圖驗證不能代替這些結果。

## 實際草圖驗證

隔離Blender 5.2.1 LTS＋官方CAD Sketcher 0.32.1，以原生事件建立矩形、增加60／40 mm驅動尺寸達到DoF0，再改80 mm、另存、重新開啟。三個案例共12項檢查通過，平面網格跟隨尺寸更新。環境安裝與單位設定為程式bootstrap，和GUI幾何操作分開記錄。

產生兩個新場景版本及12張Blender原圖。尺寸延伸線有部分超出視區；側欄尺寸與Fully defined可讀，完整草圖課須改善標註位置。平面網格沒有厚度，並非可列印盒體。本輪尚未完成完整參數盒／上蓋連動。

探測v001～v004與rectangle-v001失敗版本保留，具體原因見專屬交接。下載包及擴充套件只存本機私有目錄，不加入公開教材。移動暫存下載後殘留空的 `learning/.runtime`；額外清理命令收到自動審核 `blocked by policy`，未重試，改以保留空資料夾完成驗證，不影響功能。

## 修改分工

- root：路徑JSON、server精確資源白名單、server測試、README、AGENTS、整合驗證與本交接。
- engineering_path_frontend：新 `engineering-path.js`、前端測試及 `app.js`／`app.css`／`index.html` 的頁籤和路由整合。
- parametric_environment_trial：新 `cad_sketcher_environment_probe.py`／`cad_sketcher_rectangle_trial.py`、獨立環境與實拍讀值；未改共用runner／common。
- path_evidence_review：只讀核對引用、原圖與尺寸語義。所提缺少快捷來源的5個參照已補入，合計50個章節參照。

原server只新增兩個明列靜態資源路徑 `/engineering-path.js` 和 `/engineering-path-v001.json`，沒有新增寫入端點或擴大任意檔案服務。工程路徑時隱藏原教材側欄以改善窄視窗閱讀，回原教材即恢復；窄視窗的章節選擇預設收合，按「開始第一小步」可直接到原圖。

## 驗證與版本紀錄

- server完整21個測試通過；補齊參照後再跑2個工程路徑針對測試，通過。
- 前端工程路徑24個測試通過，JavaScript語法檢查通過。
- 兩支新Blender劇本AST解析通過；安全摘要所連17個檔案雜湊一致。
- 實際IAB檢查：章節切換、05-05參照預覽、原教材側欄恢復、新路徑窄視窗收合、第一小步跳轉、原圖載入、環境摘要顯示；console無warning／error。
- 網頁原始實拍保存於 `learning/evidence/ui/2026-10-27-engineering-path-v001/first-activity-web-v001.png`。只記當時325px實際視窗，未為截圖改動使用者視窗大小。
- `git -c core.whitespace=cr-at-eol diff --check`通過；保留既有CRLF／原證據位元組規則。
- 本輪檔案、原圖、摘要、進度與原盒基線雜湊見同UI目錄的 `version-manifest-v001.json`。這是本機版本紀錄，上一輪公開版manifest仍只代表其原候選範圍。

最終讀取manage.py status：revision6，單元01／目前01-01，尚無學員確認或登記檔案。開工與收工下列雜湊一致：

| 保留項目 | SHA-256 |
|---|---|
| catalog | `17ca75ebd865e36e75d069ab074cae121b96178d2a5ae95d68cc8ec369e4bfd6` |
| progress | `26130175ef80a9fb83699f93a8c33de7b098b17ffa2c10aef794808390d19325` |
| 原盒u04_box_v001.blend | `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530` |
| 原上蓋u05_lid_v001.blend | `ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff` |

未stage／commit／push；起始HEAD為 `fa764617122e27a96385301bc043b589ecf22684`。沒有更改既有場景、STL、圖片、catalog或progress。新證據與journal遵循既有本機忽略規則；未為本輪強制加入公開候選。

## 停留位置與接續

頁面停在第一小步原圖，問學員：「組裝時，哪個部分伸入盒口、限制上蓋左右移動：整片蓋板，還是下方的環形唇邊？」等待回覆再處理理解紀錄；不預先給學員完成狀態，也不以此回答confirm舊步驟。

接續先判讀學員回答、用實際原圖釐清接觸與定位。後續正式草圖章節須改善標註顯示並安排1～3動作小步，再建同一主控下的盒體／上蓋，做尺寸變更、保存重開及原盒保護驗證。原列印與試配欄位繼續留空。
