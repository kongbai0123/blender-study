# 2026-10-27 原生草圖尺寸驅動器隔離探測

`learning/evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/native-driver-xy-partial-verification-v001.json` 摘要 SHA-256 `bcf1fda35c8305f7de44fe7931c7986522e257bc40e4018d346f6dc0cb16bda2`，附 29 張原圖雜湊與兩個示範檔雜湊。

GUI 從 60 mm 外框欄位 Copy as New Driver，貼到內腔 X 欄位並開啟 Edit Driver，選 Scripted Expression，輸入 `slvs_c_b596b36138076155-4`；在外長60時讀回表達式有效、內腔長56，X範圍 2～58。這是 X 初始尺寸的局部成果，不是外尺寸變動的連動驗證。程式僅啟用插件、複製場景、填檔案對話框及讀值；UI 事件建立驅動器。

續測時切回外框草圖失敗：`XY-01-outer-sketch.png` 和讀值均顯示沒有活動草圖。之後沒有建立 Y 驅動器，所謂改 X70、Y50 的事件未達預期；即使 runner 結束狀態是 completed，也不能當作測試成功。run.json 原本為預定流程而填寫的這些動作標籤不符事實，請以安全摘要和讀值為準。

GUI 另存後重開的實際外框是 60×40×30、只有 X 的一個驅動器。檔名 `manual_drivers_box_70x50_v002.blend` 和真實尺寸不符，明確為失敗探測，不能當 70×50 示範成品；`manual_drivers_box_60x40_v001.blend` 也只是局部草案。尚未完成 X 改值驗證、Y 連動、上蓋、封閉性檢驗、實體列印或試配。真實學員工作區未變。

## 已存 X driver 場景外長修改重試

獨立複本 `2026-10-27-cad-sketcher-x-driver-resize-v001/` 開啟後，活動物件讀回 `Body.001`；依先前外框探測的右鍵步驟，`EDIT-02-context-menu.png` 顯示 Edit Sketch 灰色停用。後續 `EDIT-03-body-sketch.png` 與讀回顯示仍無活動草圖，前置斷言因此停止；原因尚未獨立證明。沒有實際更改 X70 或另存修改版本，X 的變更連動仍未驗證。runner 失敗，不代表 Blender 出現崩潰。

`x-driver-resize-failed-verification-v001.json` SHA-256 `43556bc29e0a039d45538ecf677b20f113ac43e9cf7f7b9676e1c91ae6b1046c`，附三張原圖 hash；run.json 的 body-sketch 動作為預定敘述，不是實際完成。真實學員工作區未變。

## Outliner 指定 Body 的一次嘗試

獨立複本 `2026-10-27-cad-sketcher-x-driver-outliner-v001/` 以 GUI 點選 Outliner 內預估 Body 位置，活動物件讀回仍為 Body.001，前置檢查停止；未進入草圖或更改 X。畫面顯示 Outliner 下緣物件列被截切；該座標未選中不等於 Blender UI 無法選擇。原始 run.json 的 select-body 動作是預定敘述，不代表成功。脫敏摘要 `outliner-selection-failed-verification-v001.json` SHA-256 `803046e21d9c6744341e67e1f65d7b2a2ac2ebc4e829b379dd9e03f1d9dc05b3`；學員工作區未變。
