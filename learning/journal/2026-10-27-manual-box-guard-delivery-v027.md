# 2026-10-27 手工盒受控尺寸防護及自動重算 v027

使用者要求手工盒尺寸防護、自動更新、盒蓋驗證、獨立 Blender 真實畫面及版本，實體結果留空。CAD Sketcher 0.32.1 的一般 depsgraph 處理活動草圖，不能假設非活動內腔自動更新；本次使用受控面板提交後明確求解指定草圖，並非常駐監聽原生欄位。所有 GUI 實驗使用獨立 Blender 5.2.1、系統 temp 假專案／假 progress；插件由程式啟用，檔案瀏覽器路徑由程式填入，面板選項與確認由原生事件完成。

## 本機程式

- `learning/tutor/guarded_manual_box_v001.py` SHA-256 `9dd50ba87227fc6ea77df4f6344b602ba245becfe4efe28d5343600a1282f067`；專屬手工模型的長寬受控提交，逐項核對 Scene/Key Driver、特定上蓋原始拓撲、形狀鍵及範圍；需個人副本在 `learning/workspaces/engineering-parametric`，已登記版本不能透過面板修改。
- 同目錄依賴 `manual_box_auto_update_v002.py` SHA-256 `cc39a2376c8abc41f61cb5beb796a83e22b63dc33b6b6aed5df9f135e83fc457`、`manual_box_reference_v001.json` SHA-256 `78f39a6ec422bb02b64fff64f70896c927a6ab449bcd84be9a03b6657bedae5c`。對應流程與設計邊界見 `learning/journal/2026-10-27-guarded-manual-box-v001.md`。
- 工具的 X60～100／Y30～70 是形狀鍵避免夾限的理論計算範圍；非已驗安全或製造範圍。直接改原生欄位不觸發防護／受控更新；原生保存與匯出不被攔截。工具不自動存檔，僅採樣盒和切割體的頂點層、點面數及非流形，無完整碰撞或實體判定。

## 可重現 GUI 與失敗紀錄

- v001 假專案 Text Editor Open + Alt+P；X110 被拒、X80→90 後 Body X0..90、cutter X2..88、蓋約90×50，未手動切內腔；原圖提示由人目視，幾何由程式讀值。安全摘要 `learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v001/guard-gui-one-x-verification-v001.json`。
- v002 寬度輸入焦點失敗未改尺寸，保留；v003 用欄位正確焦點後依序 80×50→90×50→90×60→70×60→70×40，受控更新各自核對三件外框，70×40 同一 Blender 執行期另存重開。其假登記步側欄被關、沒有看到拒絕，不可冒稱通過；摘要 `learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v003/guard-gui-xy-reopen-verification-v001.json`。
- v004 重新執行並修正側欄，GUARD-27 原圖顯示假已登記版本被拒，人工目視判定；程式讀回拒絕前後外框與約束一致。示範版 `learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/demo-files/manual_guard_trial_70x40_v003.blend` SHA-256 `9942f712fe5f7bf88daa9b144de0b29fbae5a9dd8217acdb96a3df0f3aacad3f` 為假專案副本非學員成果。摘要 `learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/guard-gui-registered-rejection-verification-v001.json`。
- 故障試驗僅在 fake project 移走 updater，再改X70；畫面提示回復未確認、勿存並重開。讀回尺寸／外框雖相同，重算及回滾均缺依賴，不能稱完整回復。摘要 `learning/evidence/parametric/2026-10-27-manual-box-guard-fault-trial-v001/guard-gui-fault-unconfirmed-rollback-v001.json`。
- 新 Blender 程序由70×40 假版開啟，Text Editor 的相對連結腳本以 Alt+P 主動執行後改80×40，程式讀回三件外框一致；沒有檢查執行前面板是否自動常駐。v001/v003 重啟探測因既有文本與側欄誤點失敗保留；有效摘要為 v026 所引用 `learning/evidence/parametric/2026-10-27-manual-box-guard-restart-trial-v004/guard-gui-restart-manual-script-verification-v002.json`，以其課程 journal 為精確路徑。
- Y80在假專案面板被拒，GUARD-10 原圖由人目視，程式讀回80×50外框與切割體不變；摘要 `learning/evidence/parametric/2026-10-27-manual-box-guard-y-reject-v001/guard-gui-y-out-of-range-verification-v001.json`。原圖中的工具提示 `sketcher.slvs_select` 仍原因未知。圖像有遮擋和標籤重疊，不能將程式尺寸當作從圖片量測。

## 整合與驗證

v022～v027 在 v021 的243步基礎上追加13步，共256；保留原有 ID 與完成事件。現行 `learning/web/engineering-curriculum-v027.json` SHA-256 `615b1ef2f3482b1f585548a82ab0cf86528c546e42a792cccaeaa0dbb935be2b`。每版 builder、測試、journal 與脫敏摘要留存；新版主頁的 ch04／05 快捷狀態已更正為手工示範已存在及原生欄位可繞過。

前端40測試、工程資料與進度85測試、server22測試、手工面板10項邏輯測試通過；diff check 通過。GUI 證據採只讀逐張核對，故障注入／超界錯誤文字為人工目視，另存重開和網格為程式讀回。瀏覽器實測 v027、256小步、revision8、圖片與限制顯示，524 px 寬無水平溢出、console warning/error 為空；頁面截圖 `learning/evidence/ui/2026-10-27-engineering-curriculum-v027/manual-guard-result-v001.png`。

個人練習應先另存已驗手工盒副本到指定工作區（不存在時先建立），保留同專案 progress 和三項工具；Text Editor 開啟腳本並 Alt+P 的步驟和條件見 ch05。未代使用者建立或登記學員檔；status 仍 revision8、原01-01，原盒／蓋與 catalog、progress hash 不變。實體列印、量測、試配及合格值均留空，不 commit／push。
