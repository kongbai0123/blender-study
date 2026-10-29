# CAD Sketcher 重開警告：限定 GUI 操作恢復探測

原來的 CAD 草圖重開圖確實顯示 `Tool 'sketcher.slvs_select' not found for space 'VIEW_3D'`，未斷言錯誤根因。在隔離 Blender 5.2.1／CAD Sketcher 0.32.1 中開啟 SHA `f45cb87cb9084bb9ca92612d6dc8726c28f7abfd099954e14ea4964975dd8508` 的 0.6 mm 草圖副本，GUI 點 Leave Sketch，再點 Sketcher 清單上的 Body 草圖進入圖示；按 L 啟動 Line，點左側 CAD Select 圖示，點既有下方斜邊。畫面斜邊呈橘色，讀回工具 ID `sketcher.slvs_select`、選取集合一個 ID；程式未獨立辨識該 ID 的曲線類別。

GUI 將基邊 Distance 0.6→0.8→0.6 mm，讀回尖點 X 6→5.97047→6、solver OKAY／DoF0；另存並重開後及獨立背景 Blender 均讀回還原的草圖。新本機場景 SHA `3104b2e01e10150a451d236039044efaa60c45e612afa424121847c8858bcc76`。重進草圖後視野回到原點，成功探測由程式設定視角以看到牙型，不能說這次已示範 GUI 對焦；檔案對話路徑由程式填入。

七小步 `learning/lesson11_cad_tool_recovery_optional_steps_v001.json` SHA `02cdc1d6f6f0065306986335872cc52c79a9db58d696f6aaef159a12c4a28d49`；九張原圖與真讀值摘要 `learning/evidence/parametric/2026-10-28-cad-thread-tool-recovery-probe-v002/safe-summary-v001.json` SHA `bbc76870784912a72994db73f35b780e0da018232a0853e8cbf20cbd6abc4ac1`。第一次 `...-probe-v001` 在視野不見牙型、L 後一次 Esc 仍留在 Line 時沒選中邊，依斷言中止；失敗證據保留。

此結果僅顯示上述檔案與版本、這幾項操作可行，不代表已修復插件警告、所有工具可用、再次開檔絕不警告或任何列印與配合合格。最後截圖沒有可見警告不能證明提示根因已消除；本機場景與原始 runner 尚未公開隱私審查，未更改學員進度。
