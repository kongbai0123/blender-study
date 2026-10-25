# 2026-10-22：實際完成 English (US) 設定 v001

使用者要求：「你要實際完成操作，並且一步步執行和記錄」。本次依其貼圖與持續討論的語言切換內容，由助教使用 Windows Computer Use 親自完成操作，不再要求使用者逐個點擊後回覆才繼續。

實際結果：Language 為 English (US)；已點 Save Preferences 並看到 Preferences saved；已關閉偏好設定，主視窗可見 File、Edit、Render、Window、Help 與 Object Mode。這次沒有建立、儲存或覆寫場景檔。

## 逐次實拍紀錄

### 1. 核對操作前畫面

時間：2026-10-22 13:12:52（Asia/Taipei）

實際結果：繁中介面，檔案選單原先已開啟。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-00-before-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 2. 點左上「編輯」

時間：2026-10-22 13:12:53（Asia/Taipei）

實際結果：原先開啟的檔案選單關閉；畫面尚未展開編輯選單。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-01-edit-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 3. 再次點左上「編輯」

時間：2026-10-22 13:13:03（Asia/Taipei）

實際結果：編輯選單展開，最下方可見「偏好設定…」。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-02-edit-open-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 4. 點「偏好設定…」

時間：2026-10-22 13:13:48（Asia/Taipei）

實際結果：設定視窗開啟，左側「介面」已選取，底部語言為「正體中文 - 繁體中文」。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-03-preferences-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 5. 點底部的語言下拉欄位

時間：2026-10-22 13:13:55（Asia/Taipei）

實際結果：語言清單展開，目前顯示清單較下方的項目。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-04-dropdown-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 6. 向上捲動語言清單

時間：2026-10-22 13:14:03（Asia/Taipei）

實際結果：清單向上移動；此時仍未看見英文選項。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-05-list-scroll-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 7. 繼續向上捲動語言清單

時間：2026-10-22 13:14:15（Asia/Taipei）

實際結果：清楚看見 English (UK) 與 English (US)，後者提示 locale 為 en_US。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-06-english-visible-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 8. 點 English (US)

時間：2026-10-22 13:14:24（Asia/Taipei）

實際結果：語言欄位顯示 English (US)，主視窗選單與設定內容隨即改為英文。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-07-english-selected-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 9. 點設定視窗左下角選單

時間：2026-10-22 13:14:31（Asia/Taipei）

實際結果：Auto-Save Preferences 已勾選，清單有 Save Preferences。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-08-save-menu-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 10. 點 Save Preferences

時間：2026-10-22 13:14:39（Asia/Taipei）

實際結果：主視窗底部實際出現「Preferences saved」訊息。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-09-preferences-saved-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

### 11. 關閉偏好設定視窗並核對主視窗

時間：2026-10-22 13:14:51（Asia/Taipei）

實際結果：File、Edit、Render、Window、Help 與 Object Mode 均可見；Camera、Cube、Light 仍在。

原始實拍：`learning/evidence/01/2026-10-22-01-02-language-10-main-verified-v001.jpg`；同名 JSON 保存來源、尺寸及 SHA-256。

## 資料與教學紀錄

完整機器可讀操作紀錄：`learning/evidence/01/2026-10-22-interface-language-v001.json`。教學頁 01-02 的「助教實際操作紀錄」引用同一批原圖，每個項目均可展開；所有實拍均保存未修改像素，沒有示意圖。

介面語言的實際狀態透過共用 CLI 記錄為 en；此設定紀錄不等同學員學習完成。未執行 confirm，不代學員完成 01-01 或 01-02。最新完成狀態一律讀取 `learning/progress.json`。
