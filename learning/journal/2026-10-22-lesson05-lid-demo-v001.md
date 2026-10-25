# 05-05：上蓋與環形唇邊幾何示範（v001）

日期：2026-10-22（Asia/Taipei）。使用者要求沿用既有盒體尺寸，先完成上蓋與唇邊的幾何示範，保留實際操作、原圖、讀值及檔案版本；配合間隙仍是試驗值，正式合格值等實際試配。

## 既有盒體與本次示範尺寸

本次先開啟第四單元盒體的同雜湊工作副本，從實際網格重新量測：外形 **60 × 40 × 30 mm**，內腔 **56 × 36 × 28 mm**，四側壁及底厚均 **2 mm**；盒口 world Z 15、內底 Z −13、外底 Z −15 mm，體積 15552 mm³。原檔沒有完整的 verification，所以本次 `source-body-verification.json` 另存重新驗證的實際結果，沒有只採用歷史圖片文字。

助教從既有 0.1～0.6 mm 總間隙試驗點中，先選 **0.4 mm 總量、置中時每側 0.2 mm** 作幾何示範，已在聊天說明。這不是使用者指定的合格尺寸，也沒有根據尚未執行的 05-04 實體試配填入正式間隙。蓋板厚 2、定位環壁厚 2、深度 4 mm 均為本次示範尺寸。

| 幾何項目 | 設計計算／本次結果 mm |
|---|---|
| 蓋板外形與厚度 | 60 × 40 × 2 |
| 唇邊外形 X / Y | 56 − 2 × 0.2 = 55.6；36 − 2 × 0.2 = 35.6 |
| 唇邊內形 X / Y | 55.6 − 2 × 2 = 51.6；35.6 − 2 × 2 = 31.6 |
| 唇邊環壁／深度 | 2 / 4 |
| Lid 整個物件 Dimensions | 60 × 40 × 6（板厚 2 + 向下唇深 4） |
| 名義位置 | 蓋板 Z 15～17；定位環 Z 11～15 |
| 幾何嵌入／距內底餘量 | 4 / 24 |

最終網格實測唇外 **55.599998474 × 35.599998474 mm**、唇內 **51.599998474 × 31.599998474 mm**，環壁 2、深度 4；四側實際數位間隙各 **0.200000763 mm**，XY 總間隙各 **0.400001526 mm**。Lid 體積 **6195.199951172 mm³**，與 `60×40×2 + (55.6×35.6−51.6×31.6)×4 = 6195.2 mm³` 一致。

Body 和 Lid 各為非空、單一連通封閉殼，Non Manifold 邊 0、Euler 2、genus 0、Scale 1；Lid 有 24 頂點、44 個三角面（evaluated loop-triangulated representation）。多處平面、中心／環壁／外緣垂直射線與正體積共同確認環形唇邊和盲內凹，避免以實心塞或空網格冒充。名義擺位的數位幾何沒有體積交疊；實體干涉與配合尚無結果。

## 真實操作與實拍

```text
python -X utf8 learning/tutor/run_demo.py lesson05_lid learning/evidence/05/2026-10-22-lesson05-lid-demo-v001
```

獨立 Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、出廠設定、獨立偏好及暫存資料夾，以 `Window.event_simulate()` 執行選單、選面、數值輸入及視角。不使用學員的系統滑鼠或 Blender 視窗。只有檔案瀏覽器路徑與檔名直接安全填入；Python 讀取網格作驗證，不直接建立幾何。

共 **16 筆操作與 16 張原始 PNG**，依序保存：

1. File > Open 既有盒體副本，命名 Body 並重驗來源。
2. 暫隱藏 Body；新增 Cube，Dimensions 60 × 40 × 2 mm，G Z 16mm，Apply Scale，命名 Lid。
3. Ctrl + Numpad 7 底視，Tab、面選取、Select None，點選唯一底面。
4. I 2.2mm 得 55.6 × 35.6 mm；E 4mm 下到 world Z 11；I 2mm 留環壁；E −4mm 把中心面推回 world Z 15，形成一體的定位環與盲內凹。
5. 底部斜視量最終網格；Edit Mode 的 Select Non Manifold 操作讀回 0。
6. Lid 暫上移 12 mm 拍攝與盒口分離的實際檢視，再下移 12 mm 回名義位置重新核對。暫時位置沒有保存為最終模型。
7. Save As 上蓋場景 v001，讀磁碟檔案與雜湊；File > Open 同檔重驗 Body、Lid、試驗間隙與來源不變。

座標教學註記：Edit Mode 側欄目前選 **Local**。圖中 Median Z **−1／−5**，因 Lid 物件 Location Z 16，分別對應腳本讀取的 **world Z 15／11**；文字中的 world Z 不是畫面 Local Median 的直接抄值。第 11、12、16 張作用中物件是 Body，側欄 **60 × 40 × 30** 屬盒體；第 9 張 Lid 底部斜視才顯示上蓋整高 **6 mm**。

圖像均由 Blender 原生 screenshot 保存，像素未修改；網頁疊框不寫進原圖。分離圖和組裝位置圖都來自實際 Blender，不是示意圖，也不代表實體試配成功。

## 來源與檔案版本

- 原盒：`learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend`，97,880 bytes；SHA-256 `b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530`。
- 本次逐位元組讀取副本：run 內 `demo-files/sources/u04_box_v001.blend`，相同 hash；原檔與副本均未覆寫。Body 幾何指紋在建模與重開後一致。
- 新場景：`demo-files/u05_lid_v001.blend`，**99,064 bytes**，含既有 Body 與一體的 Lid。
- 新場景 SHA-256：`ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff`。
- run 與場景均首次 v001，另存後重新開啟通過；`scene-manifest-v001.json` 關聯來源與新版本，`source-snapshot/manifest.json` 保存五份實際腳本與各 hash。
- `run.json` 保存每步動作、UTC 時間、實際讀值及每張圖的尺寸／hash；`verification.json` 保存原盒、上蓋、名義擺位與幾何試驗範圍；`runner-status.json` 記 completed、exit 0、runErrors 空白、工作區前後不變及 Recent 清理無警告。

數值驗證的 `1e-4 mm` 與體積相對 `1e-5` 門檻只處理浮點重建誤差，不是製造公差或列印配合驗收條件。

## 正式試配仍待執行

本次沒有匯出上蓋 STL、切片、列印、實體量測或試配。`printed=false`、`fit_tested=false`，`physical_measurements`、`fit_results`、`qualified_clearance_mm` 皆為 null。環壁、深度及間隙均未成為正式合格規格；待後續實體試配再調整與另存版本。

`trial-fit-record-v001.json` 保留本次設計及數位讀值，列印條件、實測與試配結果留空。學員完成狀態以共用 `learning/progress.json` 為準，本次不執行 confirm，也不把助教示範檔登記成學員成果。

## 發布核對

執行器、匯入器與網格驗證共 68 項測試無失敗（1 項 symlink 權限測試跳過），教學頁 API／CLI 17 項通過，前端 JavaScript 語法檢查通過。另核對全部 16 張原始 PNG 的尺寸、SHA-256 與 HTTP 回傳位元組，以及新場景下載的位元組／attachment 標頭、來源及副本 hash、五份腳本快照與空白的實體結果欄位。

05-05 已發布 16 筆操作、場景下載與來源版本、底部與暫分離原圖，並補 Local/world 座標及作用中物件註記。瀏覽器已開啟 05-05，頁面原始截圖為 `learning/evidence/ui/2026-10-22-lesson05-lid-demo-v001.jpg`，同名 JSON 記錄尺寸與 hash；完整核對表為 `learning/evidence/05/2026-10-22-lesson05-lid-publication-checks-v001.json`。

發布後共用 `progress.json` SHA-256 仍為 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`，未改學員完成步驟、工作區或學員檔案登記。
