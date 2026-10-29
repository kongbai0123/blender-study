# CAD Sketcher 隔離環境與最小草圖試驗 v001

2026-10-27，Asia/Taipei。依使用者「開始進行上述的討論內容」，本輪由 root 建立新版學習路徑；parametric_environment_trial 僅負責第 04／05 章前置技術驗證。未改 catalog、progress、workspaces、原盒／上蓋或共用 runner，未 commit／push。

## 結果與範圍

Blender 5.2.1 LTS，build `9e2066aef7ef`，Python 3.13.13，可在隔離目錄啟用官方穩定 CAD Sketcher 0.32.1 與隨附 slvs 3.2 cp313 Windows wheel。原生事件建立 XY 草圖與矩形，新增 60、40 mm 兩個驅動尺寸後 solver=OKAY、DoF=0；改寬度為 80 mm，生成的平面 mesh 跟隨變成 80×40×0 mm。60×40 另存 v001，80×40 另存 v002，重新開啟 v002 後兩個尺寸、DoF0 與生成 mesh 尺寸仍相符。

這是最小矩形與擴充套件可行性試驗，不是參數小盒、盒蓋連動或第 04 章正式教學定稿。未重建原盒、未印試片、未做實體量測或配合／強度合格判定。

安全公開摘要與原圖索引：`learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/environment-verification-v001.json`。此摘要省略原始 runner-status 的 Recent 清單，只摘錄狀態與工作區端點比較；不得將原始 runner-status 當成公開索引。

## 官方版本與來源

- release：<https://github.com/hlorus/CAD_Sketcher/releases/tag/v0.32.1>，2026-09-28，非預覽版。
- commit：`e7db7e6f94ad9dcaf2be03e849e1d3a2ac82e7a4`。
- Windows ZIP：`CAD_Sketcher-0.32.1-windows_x64.zip`，1,283,581 bytes，SHA-256 `b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59`，與 GitHub asset digest 相符。
- manifest 最低 Blender 5.0.0，license `GPL-3.0-or-later`；cp313 wheel SHA-256 `86159bc0c5e749eb04d94cbf28b6d38ace795e802b8131be36870502e336f4fa`。
- 官方 0.32.0 release 已記載 parts／assemblies、實際 mesh body 與 sketch conversion；本輪實驗使用修正版 0.32.1，而非把 main 文件功能直接當穩定版已支援。
- 安裝包、解包原始碼、隔離 extension profile 與 bootstrap 診斷只存 `learning/.publication-private/cad-sketcher-0.32.1-v001/`。沒有將第三方包加入公開教材。

## 操作方法與分類

環境 bootstrap 用 `bpy.ops.extensions.package_install_files` 安裝到專案私有 profile，啟動獨立 runner 時以 `BLENDER_USER_EXTENSIONS` 指到該 profile 的 extensions；runner 繼續使用自己的獨立 config/scripts/datafiles/temp。劇本啟用擴充套件並設定 Metric、Unit Scale 0.001、Millimeters，這些是程式環境設定，明確分類，不冒充 UI 點選。

幾何操作透過既有 `window.event_simulate()`：刪除出廠物件；`Ctrl+Shift+A` 啟動 Add Sketch，工具內按 `Z` 選 XY；開 Sketcher 側欄；`R` 矩形、原點點選及數值輸入；`D` Dimension 選邊加入 60／40 mm；在側欄將第一尺寸改成 80 mm。位置取自已見原圖或只讀投影計算。Python 只讀草圖點、約束、solver、DoF 與 evaluated mesh，不直接建立矩形或寫尺寸值。

存檔使用原生 Save As 操作；檔案瀏覽器路徑／檔名依既有 Kit 直接填入本次 demo-files，再模擬確認。重開使用 `Ctrl+O` 與同樣的安全填欄。未操作使用者的實體滑鼠或既有 Blender 視窗。

## 保留的探測與失敗

- `cad-sketcher-probe-v001`：F3 找不到工具限定的 Add Sketch on Origin Plane。runner completed 只能代表腳本結束，不能證明新增草圖成功；此版不作教學通過證據。
- `probe-v002`：確認 `Ctrl+Shift+A → Z` 有效，建立空 XY 草圖。空草圖的 Fully defined 不能推定後續矩形已約束。
- `probe-v003`：矩形數值輸入後點座標為 60×40，但只有水平／垂直約束，DoF2。需要另加尺寸約束。
- `probe-v004`：寬度約束成功，DoF1；右邊太靠近側欄導致高度點選未完成。
- `rectangle-v001`：60／80 尺寸、DoF0 與保存均成功，但重開時 File 選單位置錯誤；runner failed，保留原件。
- `rectangle-v002`：增加視野與平移，補上兩個 Dimension，以 Ctrl+O 重開；3 組各 4 個檢查全部通過，runner completed，exit0。

最終 v002 的 12 張原生 PNG 均已逐張 view_image。尺寸標註的延伸線仍超出視區；右側 60／40、80／40 與 Fully defined 清楚可讀。此限制寫入摘要，正式課程需另改善標籤位置，不修改本次原圖，也不聲稱已完成排版。

## 檔案與核對

新正式試驗目錄：`learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/`。

| 檔案 | SHA-256 |
|---|---|
| `demo-files/cad_rectangle_60x40_v001.blend` | `a7ad848278d2a09ce1006139d98e401e0cfde6b77cc83d14d50a6b65c76a7cd4` |
| `demo-files/cad_rectangle_80x40_v002.blend` | `cc9346a6e505fb261d7134b72646ba2717689fe806d7d3c015e79273e65cb5bb` |

`rectangle-60-verification.json`、`rectangle-80-verification.json`、`reopened-80-verification.json` 保存各自的真實狀態。檢查 solver OKAY、DoF0、2 個驅動尺寸、生成 mesh 外框。數值門檻 1e-5 是數位比較精度，不是製造公差。生成 mesh 有 4 頂點、1 面，沒有厚度，不可當成可列印實體。

新腳本只有 `learning/tutor/scenarios/cad_sketcher_environment_probe.py` 與 `cad_sketcher_rectangle_trial.py`；每個 run 已凍結當次 runner、blender_demo、common 及劇本來源。兩支新腳本均通過 Python AST 語法解析。未更改共用 Kit／runner。

執行前後 workspace 內容相同，只表示端點比較。原盒 SHA `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530`、原上蓋 SHA `ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff`、progress SHA `26130175ef80a9fb83699f93a8c33de7b098b17ffa2c10aef794808390d19325` 與既有基線相符。

## 接續

root 可將安全摘要與最後原圖接到新版路徑的環境驗證區，維持「完整草圖章節、盒蓋參數連動待製作」。正式草圖示範需整理尺寸標籤的原生擺放，明確展示原點關係及兩個尺寸約束。下一階段才建立共享草圖／參數的盒體與上蓋，不把此平面測試當成整盒已完成。
