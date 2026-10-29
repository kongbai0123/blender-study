# 本輪教材補齊與驗證

使用者要求繼續完成所有教材；指教材製作，不是學員的完成進度。本輪完成目前 12 章規劃的數位補課與現場方法；實體工作仍需現場資料，結果不代填。本輪沒有 commit 或 push。

## 目前入口與版本

- 本機新版：[教學頁](http://127.0.0.1:8767/#engineering/ch11)／[章節練習題](http://127.0.0.1:8767/challenges/index.html?chapter=ch11)。8767 與原服務使用同一個 progress.json；原 8766 服務仍載入先前版本的常數。
- [教材 v036](../web/engineering-curriculum-v036.json)：`fceaf4cc951316bfa5e827cd2a4d2bebb713318ecb7f909ad646ba216975db09`。
- [路徑 v005](../web/engineering-path-v005.json)：`57cc0206dedeec11888e51ab2ac1703f53ba99ae8b993fffdb9d933748af18aa`。
- [題目 v009](../web/challenges/challenges-v009.json)：`ad6479e8425daa86674de9e1ed90bf7725dff905d3a1aa0b2789ff820da6047b`。
- [逐項教材證據索引](2026-10-28-material-content-inventory-v001.json)：12 章、主線 243／選修 202／實體待執行 2／開發歷史附錄 30；不是第二份學員進度。

## 本輪交付

| 範圍 | 教材與可核對的成果 |
|---|---|
| 01、03 | 18 個編輯模式 GUI 檢查點：單位、20 mm 方塊、點邊面、移動與 Undo、Inset／Extrude、Hide／Show、底視；原盒改名、另存與重開；沿用 Post／Signal 真實原圖並標原日期 |
| 02、06 | 名義／實測／總差／單側觀念；六孔名義 CSV 與空白實測欄；切片、量具零點、重複量測、試配辨識及記錄方法，沒有捏造切片器或實體圖片 |
| 07、08 | CAD Sketcher 隔離安裝 GUI、啟用狀態；既有手工盒連動與防護的準備／檢查點；假專案版本登記實驗，明標 fixture 並非真實模型匯出 |
| 11 | STL 44 步、CAD 真約束 16 步、CAD 副本轉 mesh 與 Screw 12 步、工具警告後限定恢復 7 步，共 79 個新增選修小步 |
| 12 | 尺寸鏈、量測彙整、證據支持後才用的補償、組裝追溯空表；安全副本的另存與渲染輸出路徑實拍 |
| 題圖 | 新增原盒蓋辨認題圖、訊號站三視投影、CAD 截面兩個約束狀態；12 章都有來源題圖，並非重畫 Blender 介面 |

版本化來源：[01–06 patch](../patches/ch01-ch06-teaching-v001.json)、[07／08／12 patch](../patches/ch07-ch08-ch12-teaching-v001.json)、[16 項共用來源更正](../patches/shared-source-review-v001.json)、[61 項來源鏈索引](../patches/shared-source-review-index-v001.json)。更正包括原孔板是逐件新增方塊而非 Shift+D、原盒舊 STL 圖的 Selection Only 未勾、網頁登記不屬於原 Blender 場次等。

## 重要實作發現

側盒、側帽原 n-gon 匯出各有 4／2 組反向重複三角形，重匯入會丟面；已用 GUI Ctrl+T BEAUTY 建立新修訂副本。六件 STL 經實檔解析、實際 GUI 重匯入及獨立背景重匯入。兩件修訂改變非平面面片的三角化與局部表面，沒有稱原幾何完全不變，也沒有以零非流形推定實體合格。見 [STL 完整紀錄](2026-10-28-ch11-stl-export-v001.md)。

CAD 草圖由 Equal、Vertical、兩個 Distance 及固定點達 DoF0；0.6→0.8→0.6 為截面高度改動。還原版重開顯示 `sketcher.slvs_select` 工具警告；另做離開、重新進入、L→Esc→CAD Select、選邊、改值、另存與重開的限定恢復。視角由程式調整，不能稱 GUI 對焦已示範，也未修復警告根因。轉成 mesh 的副本不再連動，Screw 評估有 6 條開口邊，不能當可列印實體。見 [CAD 與 Screw 紀錄](2026-10-28-cad-thread-constraint-and-screw-v001.md)。恢復 7 步 JSON 最終 SHA 為 `3049c4e184be12305a0efe1866dbd73a4376eec63aab2e252d42cafcc98bc2b9`。

原始操作圖像素未改。新 STL 的 12 張檔案視窗另做實際 GUI 重拍：系統快捷側欄收起、公共暫存路徑、SHA 相同的 STL bytes；不以裁切／遮蓋偽裝原圖。新 79 張候選圖有分工逐張審查與 PNG metadata 核對，但本輪沒有重新逐張目視全部歷史圖片，更未完成所有 .blend／raw runner 的公開隱私審查。

## 檢查與保留界線

- Python 教材／服務測試：374 項，9 項條件略過；原始失敗為新 CSV 測試 fixture 在 Windows 產生 CRLF，而期待 LF，改用明確 bytes 建立測試資料後全量通過，伺服器不改寫 CSV 內容。
- tutor／幾何／執行器測試：307 項，1 項條件略過；前端測試 61 項通過。最後標示與圖片／讀值文字修訂後另跑相應資料、下載與前端回歸。
- [實際 HTTP 檢查摘要](../evidence/08/2026-10-28-curriculum-v036-live-smoke/http-smoke-summary-v001.json)：225 項題圖／原圖資產、六件 STL、空白 CSV 的實際回應與 SHA，並檢查目前版本一致。
- 瀏覽器實際核對 CAD 題圖、約束改尺寸小步原圖、現場待執行說明、空白 CSV／STL 連結與第 12 章方法；沒有送出學員確認或筆記。
- 學員 revision 8、進度 SHA `b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1` 保持。示範、內容製作、學員確認及實體合格分開。
- 重新啟動 8766 服務前的 Stop-Process 操作被自動審查阻擋；改開 8767 完成驗證，沒有換另一方式強行停止原 PID。

## 尚需現場與後續交付

材料、機台設定、實際線寬、列印、量測、熱熔安裝、扭矩、試配與用途合格判定仍無資料。0.1～0.6 mm、0.4 mm、端隙與孔尺寸仍為名義試驗值。方孔插銷的結果只能作同條件下盒蓋候選起點，環形唇仍要實際盒蓋試配。

開發附錄的互動啟動器未測能力沒有算入本輪完成；CAD 工具警告仍有已知限制。未推 GitHub；公開時須以目前指標重產並審查發布清單，排除 raw runner、Recent、私人路徑與第三方快取，不能直接把整個 evidence 上傳。
