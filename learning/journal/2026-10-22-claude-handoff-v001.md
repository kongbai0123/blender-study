# 2026-10-22：接續 Claude 獨立 Blender 示範

使用者提供 Claude 的操作說明，要求先讀取其作業內容與操作方式，再接續後面的內容。

## 已核對的既有內容

已閱讀 AGENTS、README、目前 catalog／progress、第一至第四單元 journal、`learning/tutor/run_demo.py`、`blender_demo.py`、`scenarios/common.py`、第四單元劇本及匯入器。四份正式 run.json 均沒有 error；逐張重新計算原圖 SHA-256：第一單元 26／26、第二單元 37／37、第三單元 24／24、第四單元 20／20 相符，共 107 張。

Claude 示範做到 04-07 的 STL 檔案尺寸檢查：開口盒 60 × 40 × 30 mm，示範壁厚 2 mm，STL 28 個三角形；尚無切片、實際列印或裝配證據。04-06 的正式 catalog 與實拍範圍是 Apply Solidify、Non Manifold 檢查；不把舊草案中的薄壁分析當作已執行。

目前單元已擴充至 01～09，共 52 步。`progress.json` 在接手時為 revision 5、目前 01-01、學員完成 0 步；助教示範與學員完成狀態分開。本次不執行 confirm。

## 操作機制與沿用方式

- `run_demo.py` 啟動另一個 Blender 程序，指定出廠啟動、獨立設定／scripts／datafiles／TEMP／TMP，並開啟 `--enable-event-simulate`。
- `blender_demo.py` 用該程序自己的 `Window.event_simulate()` 送移動、按下、放開與文字事件；不呼叫系統滑鼠輸入、不接管學員的 Blender。啟動時仍會出現可見的獨立視窗。
- `record()` 經 Blender `screen.screenshot` 儲存原始 PNG，記錄時間、尺寸及 SHA-256；數值由劇本的 observe 函式讀回。某些「選單已展開」是文字觀察描述，仍需對照原圖；不能宣稱每一句都是獨立機器量測。
- 檔案瀏覽器路徑與檔名以程式直接寫入欄位，避免未進編輯狀態時觸發快捷鍵；本次只以示範的 demo-files 作為存檔目標。
- 網頁標示框是座標疊加，原圖像素不改。示範記錄從 run.json 匯入 operationRun，不寫學員完成度。

## 本次補強

執行器新增輸出範圍與非空目錄檢查，避免覆寫舊版本；讀回 run.json 以辨識 Blender 正常結束但劇本失敗的情況。工作區防護改由執行前後遞迴路徑與 SHA-256 比對，結果保存 runner-status.json。此為異動偵測，存檔前仍由劇本核對目的地在本次 demo-files。

Windows Recent 清理縮小為「本次新增、且目標位於本次輸出」的捷徑；不再清理整個 evidence 的既有捷徑。匯入器先核對每張圖的存在、路徑、PNG 尺寸與雜湊；第五單元另核對幾何驗證與 runner-status，全部通過才原子替換 catalog。

## 下一個實作與列印條件

接續既有 05-02：方形插銷 10 × 10 × 8 mm、Unit Scale 0.001、Apply Scale、另存及重開檔核對。這個幾何練習不需要先決定配合間隙。

使用者本次提供「噴嘴為 0.4 mm」，已保存至 `learning/evidence/05/2026-10-22-print-conditions-v001.json`；其他列印條件與正式間隙仍待定。05-01 的空白實測表另存 `learning/evidence/05/2026-10-22-fit-measurements-template-v001.csv`，實測欄位留空，不填假資料。

噴嘴直徑不必等於切片線寬；材料收縮、列印方向與設定會影響實際配合，不能單由 0.4 mm 噴嘴決定間隙。外部核對來源：[Prusa：Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)。其機型範例與數值不作為學員設備的合格保證。

本次新示範的結果與證據另見 `learning/journal/2026-10-22-lesson05-demo-v002.md`（v001 的浮點比較過嚴而中止，失敗資料原樣保留）；這份接手紀錄不維護另一套完成進度。
