# 外牙修正試作：v006 與 v007 均保留，尚未准許接合

## 發現及探測方法

v005 獨立檢查發現三組不共頂點索引的 BVH 候選交疊，並有極薄三角形。對照探測讀取既有封端牙條，使用 32 邊芯圓柱與 Exact Union，改變芯圓柱 Z 軸相位：0° 對照有 5 組候選交疊、496 個小於 10⁻⁵ mm² 的三角面；5.625° 有 0 組、0 個小於該面積的三角面，最小三角面積約 0.00417 mm²。檢查閾值 10⁻⁵ mm² 是**診斷報告門檻，不是修復容差或工程合格標準**。原始資料 `learning/evidence/08/2026-10-28-external-thread-gui-trial-v005/core-rotation-probe-v001.json`，程式 `learning/tutor/probe_external_thread_core_rotation_v001.py`。數據支持相位對齊與退化有關的假設，未證明唯一根因。旋轉改變 32 邊多邊形局部輪廓，並非完全相同的幾何。

## GUI v006：驗證規則不當而停止

`learning/evidence/08/2026-10-28-external-thread-gui-trial-v006/` 保留真實事件與原圖，執行器狀態 failed。劇本將 Blender 的 Object.dimensions 視為旋轉後實際網格世界包圍盒，期待 9.95185 mm；GUI 讀回 10 mm 而停止。獨立測試發現此處 Object.dimensions 與直接從旋轉網格頂點算出的世界範圍不同，後者為 ±4.9759235 mm。v006 是判定方式錯誤，並非據此證明 GUI 旋轉沒有生效；不能作完成案例。

## GUI v007：零候選但仍有極薄面，未通過

`learning/tutor/scenarios/external_thread_gui_trial_v007.py` 使用 GUI 將芯圓柱旋轉 5.625°，並以頂點世界座標和旋轉角確認；另存後 GUI 重開。十四張原始實拍與讀值在 `learning/evidence/08/2026-10-28-external-thread-gui-trial-v007/`。輸出 `demo-files/u08_external_gui_draft_v002.blend` SHA-256 `497dae214b1fc41e5a5dfc9d2c3cf68d863712fab9df4e4c242a294af692425`。輪廓依然是程式預先建立，不是完整手畫。

獨立背景 Blender 重開檔案，以 `learning/tutor/audit_external_thread_gui_v006.py` 計算，`independent-audit-v001.json` 保存全部三角面積與檢查值：717 頂點、427 面、非流形 0、1 連通體、X/Y 約 ±6 mm、Z 約 0～4.6 mm；BVH 不共頂點候選 0，卻有 **15 個三角面小於 10⁻⁵ mm²**，最小面積約 9.21×10⁻¹² mm²、最短網格邊約 0.000002146 mm。故不能以零候選就宣稱修復成功；本版本仍不可接合、列印或作配合合格判定。原檔、實拍與稽核輸出保留，下一版本繼續調查 GUI 數值和變換流程。

材料、列印、實體量測、試配、合格間隙與強度均待定；不更新學員進度。完整 runner-status 含機器最近使用路徑，不應原樣公開。

## GUI v008、v009：仍有薄面

v008 嘗試在 5.625° 旋轉後再透過 GUI 套用旋轉；v009 額外嘗試從尺寸欄輸入 Z=4.6 mm。兩者均另存、重開並以相同獨立稽核，仍各有 15 個小於 10⁻⁵ mm² 的三角面、最短邊約 0.000002146 mm。v009 圓柱讀回高度仍約 4.5999956 mm，需考慮 GUI 數值精度；不可假設畫面顯示 4.6 mm 就等於所有頂點符合該值。`learning/evidence/08/2026-10-28-external-thread-gui-trial-v008/` 與 `...-v009/` 保留原圖和獨立稽核。這兩版均不得作完成修復或接合之依據。

背景對照顯示：當芯圓柱上、下端接近牙條端點但存在微小偏差時，出現極薄面；明確將芯柱高度改成約 4.8 mm、中心 Z 2.3 mm，使兩端各超出牙條約 0.1 mm，另將 32 邊柱旋轉 5.625°，此參數組候選 0、低於上述面積門檻 0。此法改變芯柱高度與多邊形輪廓，不是刪面或放寬容差，仍須由 GUI 重建後獨立再核對。結果保存於 `learning/evidence/08/2026-10-28-external-thread-gui-trial-v008/core-rotation-probe-v005.json`。

## GUI v010：修正版牙條與獨立重讀

場景 `learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/demo-files/u08_external_gui_draft_v003.blend` SHA-256 `5a0aea1af13f46e9bff1b14327aa199b6b34f421936fd5a516226fc13072ec04`；同目錄 14 張 PNG 與讀值，以 `safe-summary-v001.json` 保存相對路徑和各圖雜湊。沿用程式預建三角輪廓，GUI 新增 Screw、封端、建立芯柱（Z 縮放 0.48，中心 Z 2.3 mm，Z 旋轉 5.625°，套用旋轉與縮放）、布林合併、另存及重開。檔案欄位由程式填入。

`independent-audit-v001.json` 為獨立 Blender 重讀新檔，記錄全部三角面積、網格最短邊與檔案雜湊：707 頂點、419 面、1 連通體、邊界與非流形 0，外框約 12 × 12 × 4.8 mm；BVH 不共頂點候選 0，低於 10⁻⁵ mm² 的三角面 0，最小三角面約 0.028674 mm²，最短邊約 0.17094 mm。這支持在所檢項目上排除了 v005 的疑點與 v007 的極薄面，不證明絕對無自交或可製造。

## GUI 盒側接合與獨立重讀

盒蓋來源 `learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend` SHA-256 `ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff`。開啟保護副本後，以程式載入 v010 的 Thread_Core 物件；旋轉、定位、Exact Union、另存與重開由獨立 Blender GUI 執行。對牙條 GUI 按 R Y 90、G X 31.9 mm、G Z -2.3 mm；根部 X 約 29.5 mm，與盒外壁 X=30 mm 重疊約 0.5 mm，末端 X 約 34.3 mm。此為盒右側外牙介面，既有內牙試塊不是其匹配件，並非螺旋上蓋。

第一次背景預探測因在物件矩陣更新前取值，錯誤將工具放入內腔，五條射線部分命中 X≈27.2 mm，保留 `learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/mount-probe-v001.json`，不採用。更新矩陣後重新試算（`mount-probe-v002.json`），工具正確置於外側，五條射線均命中內壁 X≈28 mm，才進入 GUI 示範。

成品示範 `learning/evidence/08/2026-10-28-external-thread-mount-gui-v001/demo-files/u11_box_external_thread_draft_v001.blend` SHA-256 `b97a021c1422ced95b17a80893195df1907a725eb2e53789e0992a23793320ce`；十張真實 GUI 截圖及雜湊在同目錄 `safe-summary-v001.json`，完整教學草案 `learning/lesson11_external_mount_optional_steps_v001.json`。步驟 04 顯示首次工具欄仍為空白，05 才成功指定；未掩蓋此過程。

GUI 另存、重開後由 `learning/tutor/audit_external_thread_mount_gui_v001.py` 獨立重讀，`independent-audit-v001.json` 保存全部三角面積：Body 712 頂點、420 面、1 連通體、邊界及非流形 0；BVH 不共頂點候選 0，低於 10⁻⁵ mm² 的三角面 0，最小三角面約 5.434×10⁻⁵ mm²，最短邊約 0.01469 mm，仍須留意細小幾何。Body 世界外框 X -30～34.3、Y ±20、Z ±15 mm；五條內腔抽樣射線均命中右側內壁 X≈28 mm，此為局部抽樣而非完整內腔證明。

重讀後的 Lid 世界面頂點集合指紋 `95fe03fdbe5e99141156cbb018cca4407c275b06359930d43776ccec69241c00` 與來源一致，牙條上緣 Z=6 mm 至上蓋最低 Z=11 mm 的靜態外框間距 5 mm；這不是動態裝配干涉、材料強度、列印或配合合格判定。仍無材料、實印、量測、試配或合格間隙。
