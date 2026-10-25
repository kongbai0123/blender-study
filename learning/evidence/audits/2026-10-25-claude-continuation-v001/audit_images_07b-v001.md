# 07-04／07-05 逐圖審查 v001

2026-10-25，Codex `/root/audit_images_07b` 實際以 `view_image` 逐張看完 85 張不重複原圖：07-04 25 張；07-05 STL 36 張；07-05 `previousOperationRuns` 幾何版 24 張。全部另行重算 SHA-256，85／85 符合 inventory。逐圖路徑、hash、event 說明與觀察見同目錄 `audit_images_07b-v001.json`。

沒有看到可見 UI 數值、選取或匯出選項與文字矛盾。來源 Body Item 為 60×44.5×30／Ry90，STL 重匯入為 30×44.5×60／R0；三試片來源 Item 為 9×4.6×24／22／26／Ry90，重匯入為 24／22／26×4.6×9／R0，畫面均有相符依據。五件原生匯出設定圖皆能看到 Selection Only 開、Scale 1、Scene Unit 關、ASCII／Batch 關、Y Forward／Z Up。A/B/C 上端選取圖能看到選取區沒有包括根部／anchor，B/C 的 Item 高度分別改成 22／26 mm。

發現 4 項呈現改善建議，並非已證實幾何錯誤：

- 07-05 幾何版 #2 說讀取 SnapTool，但配圖是 Body／Lid 候選總覽、active Body，SnapTool 隱藏。應明列 SnapTool 規格為程式讀回；若要教學員重做，另補選 SnapTool 的真實畫面。
- 07-04 #3／#18 使用「剖面」一詞，但圖是沿世界 X 的 Right Orthographic 外輪廓，外壁遮住內腔，沒有剖切。建議改稱側視／輪廓。
- 匯出／保存／總覽圖支持可見結果，不能單靠它證明 bytes、tri、hash、閉殼、精確接床面積與離床值、有效力學 L 或改善。部分相近總覽應持續標示「畫面」和「讀回」的不同證據範圍。
- 07-04 #9 active 為 Lid，附帶 note 卻仍在解釋 Body 尺寸與 Ry90；內容本身正確但容易錯認，建議補明 Lid Rx180／60×46×7。

本分工沒有執行 Blender／STL 重算或外部來源核對。85 張視覺相符不能替代數值重算，更不代表強度、列印、配合或改善合格。沒有修改 catalog、progress 或既有 evidence。
