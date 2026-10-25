# Blender 引導式學習與工程幾何實驗

以繁體中文、真實 Blender 操作畫面，從基本操作、建模與渲染，逐步學到小盒、配合試片、卡榫、卡扣與螺紋。教學頁提供逐步操作、完成確認、卡關筆記與檔案版本紀錄；聊天與網頁透過同一份本機進度接續。

本專案重視資料管理：來源可追溯，原圖保留像素，場景與輸出綁定版本及 SHA-256，未知條件保持空白。**助教已做示範、數位幾何已核對、學員已完成、實體配合合格，是四種不同狀態。**

目前課綱有 **9 單元、52 步**；包含待實作與待實體驗證的步驟，並非 52 步均已完成。工程範例是教學草案，尚無列印、試配或強度合格結果。

## 開始使用

已核對的示範環境為 **Windows、Blender 5.2.1 LTS，build `9e2066aef7ef`、English (US)**。本機教學服務需要 **Python 3.10 以上**，使用 Python 標準函式庫；閱讀既有截圖與紀錄不需要啟動 Blender。其他 Blender 版本或版面可能需要調整操作位置。

1. 下載或複製本儲存庫，進入專案根目錄。
2. 初始化自己的本機進度與練習資料夾：

   ```powershell
   python learning/bootstrap.py
   ```

3. 在 Windows 執行 `Start-Learning.cmd`，或於 PowerShell 輸入：

   ```powershell
   .\Start-Learning.cmd
   ```

啟動器會開啟本機教學頁，優先使用 `http://127.0.0.1:8766/`；若已被占用，會在 8766～8775 尋找可用連接埠。停止服務執行 `Stop-Learning.cmd`。GitHub 首頁可閱讀文件與證據；互動進度功能需在自己的電腦啟動服務。

公開儲存庫不帶入原學員的 `learning/progress.json`、`learning/workspaces/` 或 `.history`。初次初始化建立 revision 1，停在 01-01；完成步驟、筆記、事件、檔案版本與個人選擇均為空，Blender 版本及介面語言也未代填。第一單元顯示「進行中」只表示目前入口，不表示已確認完成。啟動器在新開服務前也會執行初始化檢查；合法的既有 `progress.json` 保留原內容，格式錯誤則停止，不會重設。

## 課程範圍與目前狀態

前三單元依 [SECourses 第一講](https://github.com/FurkanGozukara/Blender-Full-Tutorial-Lecture-2026-2027/tree/main/week01)的 README 章節與檔案說明改編，毫米尺寸方塊為自編補充。第 04～09 單元是本專案另行設計的工程練習，不能歸為第一講原有內容。完整步驟與成功條件以 [課程定義](learning/catalog.json)為準。

| 單元 | 內容 | 步數 | 發布範圍與後續 |
|---|---|---:|---|
| 01 | 基本操作與可靠存檔 | 9 | 介面、模式、選取、變換、尺寸與版本存檔 |
| 02 | 訊號站建模與毫米尺寸方塊 | 7 | 基礎建模與自編尺寸練習；上游 `.blend` 尚未下載驗證 |
| 03 | 第一次渲染與重現 | 6 | 相機、燈光、材質與重開渲染流程 |
| 04 | 通用小盒：開口盒 | 8 | 已有原盒幾何示範；列印與量測仍待進行 |
| 05 | 上蓋與配合間隙 | 6 | 已有插銷、孔板、環唇上蓋及 STL 數位核對；未實印試配 |
| 06 | 定位榫與燕尾滑蓋 | 3 | 已有幾何示範、燕尾件 STL 與尺寸核對；支撐及實體配合待驗 |
| 07 | 懸臂卡扣 | 5 | 已有參數條件、幾何草案、方向比較及三種臂長試片 STL；未驗強度或改善 |
| 08 | 螺紋 | 5 | 已完成 08-01 原盒參照與參數整理；08-02 建模尚未做 |
| 09 | 尺寸公差與實測總整理 | 3 | 待實測後彙整補償與總組裝 |

本教學後續螺紋採兩條路線：**自訂列印螺紋**，以及 **金屬螺絲／熱熔螺母與螺絲柱**。標準、尺寸、配合間隙、材料及硬體型號仍待定。08-01 的凍結參數表保留選擇前的空值，原試教學員的選擇另以[路線紀錄](learning/evidence/08/2026-10-25-thread-route-decision-v001/route-decision-v001.json)保存；這是教材沿革，不會寫入新使用者的個人選擇或完成狀態。

## 如何學習與記錄

每次聚焦一個小目標，依實際畫面核對編輯區、模式、作用中物件與輸入位置。先讀操作與可見成功條件，再自己執行；完成後才在頁面確認。遇到問題，先保存卡關畫面與筆記，縮小到一個操作核對。

`learning/progress.json` 是本機唯一完成狀態。網頁與 `learning/manage.py` 共用鎖定、revision 與原子寫入機制，journal 保存脈絡，catalog 保存課程定義。若由聊天助教接續，先執行：

```powershell
python learning/manage.py status
```

不得因資料夾、示範圖或模型存在而代替學員確認。練習場景先在 Blender 另存 `v001`、`v002`，再由頁面或 `register-file` 登記檔案；已登記的檢查點不覆寫。登記的 SHA-256 證明檔案版本，不能單獨證明尺寸、可列印性或學習理解。帶學規範見 [AGENTS.md](AGENTS.md)。

## 真實畫面與獨立示範機制

教材不使用重畫介面、示意圖或 AI 生成操作圖。教學圖來自實際 Blender 視窗；網頁可以疊座標框、放大局部，但原圖不修改，並可回看完整原圖。圖中細節若無法直接辨認，必須查實際網格、讀值或其他角度，不能把計算結果稱為照片可見。

`learning/tutor/` 的 Python 劇本會啟動另一個 Blender，使用 `--factory-startup`、獨立設定／暫存目錄及 `--enable-event-simulate`，再透過 `window.event_simulate()` 送入滑鼠和鍵盤事件。檔案瀏覽器的資料夾與檔名欄位另以程式設定；每個檢查點保存原生截圖與狀態讀值。這些是助教示範，並非學員開著的 Blender，也不使用實體滑鼠操作學員視窗。

執行器以固定視窗與出廠版面重現操作；按鈕位置不能直接套用到任意版面。輸出必須使用 `learning/evidence/` 內新的 run 資料夾；匯入器檢查證據後才更新 `operationRun`，不自動確認學員進度。來源場景、腳本快照、原始網格與輸出檔分開留證。需要重跑時，先閱讀 [run_demo.py](learning/tutor/run_demo.py) 與對應 journal；Blender 非預設安裝位置可用環境變數 `BLENDER_EXE` 指定。

## 工程草案與已知風險

原盒外形為 60 × 40 × 30 mm、內腔 56 × 36 × 28 mm、壁／底厚 2 mm；不同工程結構另建分支，不能把各分支視為同一件已完成產品。STL 不含單位標記，本專案匯出數字按毫米解讀，並以實檔解析與重新匯入核對；部分輸出保留來源世界位置，仍需在切片器核對尺寸、落床、方向與支撐。

已知噴嘴為 0.4 mm，**不因此推定線寬、材料或合格間隙**。孔板的 0.1～0.6 mm 是總間隙試驗點；上蓋、定位榫與燕尾使用的名義 0.4 mm 總間隙也只是幾何試驗。水平間距、法向間距與直徑差分欄記錄，不能互換。

審查已確認三項需要後續處理的風險：

- **05-03 凹點薄肉約 0.400 mm。** 辨識細節能否保留，需切片及實印確認；尚未證明會糊在一起。
- **06-01 環唇與定位柱共同定位。** 尺寸偏差可能互相牽制；直徑 4 mm、內底以上約 29.5 mm 的柱也需核對列印穩定性。幾何露出長度不等於力學有效長度。
- **06-02 燕尾導軌有水平朝下露出面。** 每側約 56 × 4 mm，合計約 448 mm²；開口朝上且外底落床時，約在床上 25 mm。方向、支撐或斜面改版需另驗證，尚未指定方案。

卡扣材料、允許應變、根部柔度 Q、所需／允許撓度與裝拆力仍待定。A_L19、B_L17、C_L21 只是臂長幾何對照，尚未證明調整改善。方向與支撐仍為候選，實際列印、量測、試配、強度與配合合格欄位維持空白。

## 審查證據與限制

2026-10-25 接續 Claude 部分審查，重新核對 05-02～08-01 的 **311 個已發布圖片路徑、288 個不同 SHA-256**，獨立讀回 **11 個 Blender 場景**、解析 **10 件 STL**，並目視核對 Covestro／BASF 手冊的 **6 個 PDF 頁面**。額外同 SHA 引用屬跨步驟重用，不是額外不同畫面。

審查未發現可直接觀察內容的重大圖文矛盾或本次外框／體積／邊連接數值不一致；已追加九組閱讀說明，保留歷史原圖與操作紀錄。05-03 的 80.35／80.4 mm 差異已確認是 UI 顯示精度，非該項幾何錯誤。

- [正式報告 HTML](learning/web/reports/2026-10-25-claude-continuation-v001.html)：啟動本機服務後，也可從 `/reports/2026-10-25-claude-continuation-v001.html` 閱讀。
- [報告索引與逐項證據](learning/evidence/audits/2026-10-25-claude-continuation-v001/report-v001.json)
- [公式與六頁查核](learning/evidence/audits/2026-10-25-claude-continuation-v001/source-formulas-review-v001.json)
- [Screw／螺紋定義與 ISO 摘要查核](learning/evidence/audits/2026-10-25-claude-continuation-v001/source-definition-review-v001.json)
- [本次審查紀錄](learning/journal/2026-10-25-claude-continuation-audit-v001.md)

這次 STL 審查核對外框、體積、邊連接、分量及法向，不能據此宣稱完整表面等價、自交全數排除或可列印。`1e-4`／`1e-5` mm 是浮點重建門檻，不是製造公差。Screw 查核涵蓋官方文件與對應 build 原始碼，尚未新增螺紋 runtime 建模案例；ISO 僅讀公開摘要，未取得完整標準、尺寸或公差表。原廠塑膠卡扣估算條件沒有直接套作本專案 FDM 強度判定。

## 資料位置與公開範圍

| 位置 | 用途 |
|---|---|
| `learning/catalog.json` | 課綱、成功條件、原圖及示範／審查索引 |
| `learning/web/`、`learning/server.py` | 本機教學介面與服務 |
| `learning/tutor/` | 事件劇本、匯入驗證器與幾何檢查 |
| `learning/evidence/` | 已發布原圖、場景、STL、原始讀值與審查 JSON |
| `learning/journal/`、`learning/plans/` | 操作脈絡、版本與待定條件 |
| `sources/` | 教材來源清單、簡短事實擷取與定義依據 |
| `learning/progress.json`、`learning/workspaces/` | 初始化後產生的個人狀態與練習，不發布 |

公開包包含已發布示範與審查資料，**不是整棵本機專案的鏡像**。個人狀態／工作區、含私人資訊的執行紀錄、基線、第三方來源 cache，以及未發布的失敗／探測 run 留在本機。授權未確認的第三方 PDF 與其渲染頁也不發布。

[發布清單](docs/publication-manifest-2026-10-26.json)列出實際納入檔案的雜湊、有意省略的內容與原因。部分執行 metadata 以移除私人資訊的衍生摘要發布，位於 `learning/evidence/public-metadata/`；摘要標明來源與變更範圍，不冒充原始紀錄。凍結歷史 JSON 保留原引用與雜湊，其中指向的檔案未必都包含在公開包內；下載本儲存庫不等於取得完整本機證據鏈，也不保證所有歷史流程可直接重跑。

首頁重編前的完整紀錄原樣保存在 [專案歷史快照](docs/project-history-2026-10-25.md)。其中「目前」「未做」及本機路徑屬各次記錄時點；舊相對路徑以當時專案根目錄解讀。接續操作請優先讀現行 catalog、對應新版 journal 與自己的進度。

## 來源與授權

- [SECourses 課程儲存庫](https://github.com/FurkanGozukara/Blender-Full-Tutorial-Lecture-2026-2027)、[第一講檔案與章節](https://github.com/FurkanGozukara/Blender-Full-Tutorial-Lecture-2026-2027/tree/main/week01)、[第一講影片](https://www.youtube.com/watch?v=Sk-4ol8IvQc)：來源 README 的事實擷取已記錄；上游 `.blend` 未下載／開啟驗證，素材再散布授權待核對。
- [Blender 5.2：Screw 修改器](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/screw.html)、[對應 build 實作](https://github.com/blender/blender/blob/9e2066aef7ef/source/blender/modifiers/intern/MOD_screw.cc)：Angle、Screw、Iterations 與線數需分清楚；單線及指定設定下，Screw 才可對應螺距。
- [Covestro 卡扣手冊](https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557218421.pdf)：原廠託管。BASF 著作手冊本次使用[第三方鏡像](https://productdesignonline.com/wp-content/uploads/2019/08/Snap-Fit-Design-Manual.pdf)，不可稱為 BASF 官方下載。
- [來源清單](sources/manifest.json)、[卡扣定義擷取](sources/engineering/snapfit-source-facts-v001.json)、[螺紋定義擷取](sources/engineering/thread-source-facts-v001.json)：保留各自查核日期、範圍與來源。

第三方作品與本專案程式、文字、模型的權利範圍需分別確認；公開可讀不代表已取得任意再散布授權。詳見 [第三方來源與授權說明](THIRD_PARTY_NOTICES.md)。本次整理不自行套用 MIT 或替第三方素材新增授權。
