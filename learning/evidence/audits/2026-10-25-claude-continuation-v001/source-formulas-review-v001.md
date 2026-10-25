# 卡扣來源公式審查 v001

2026-10-25，已依 PDF skill 逐頁使用 `view_image` 看完整渲染原頁：Covestro PDF 9、24；BASF PDF 9、11、12、14，共 6 頁。另讀對應文字輔助。與凍結的 `sources/engineering/snapfit-source-facts-v001.json` 比對，並重新計算兩 PDF、六 PNG、facts 與來源收據的 SHA-256。完整逐項結果與 hash 見 `source-formulas-review-v001.json`。

四項核心內容準確：

- Covestro 第 9 頁 Table 1 的矩形等截面式為 `y=0.67*epsilon*L^2/h`；符號表明示 epsilon 為百分數除 100 後的小數。不可直接代入百分比數字。
- BASF 第 9 頁 III-2／Figure III-3 的均勻樑式為 `epsilon=1.50*t*Y/L^2`。用專案 h=t、delta=Y 後，反解係數為精確 `2/3`。0.67 與 2/3 的相對差為 0.5%，不是精確相等；這是代數比較，並非實體試驗差。
- BASF 第 14 頁 IV-4 的根部應變式為 `epsilon=1.5*t*Y/(L^2*Q)`，因此反解允許撓度時 Q 在分子。Q 是依截面／根部牆配置及 L/t 的撓度放大修正，不是安全係數。facts 將 Q 留空正確。
- Covestro 第 24 頁 Section E／Figure 29 中，兩件均彈性時的總變形克服倒扣；剛性對件簡化才讓柔性件承擔全部。專案把 u、delta_required、delta_allow 分欄正確，沒有把幾何鉤突出量直接當材料允許撓度。

原冊有兩點應保留語義界線：

1. BASF IV-1 文字談古典模型低估 beam/wall 介面應變，IV-4 除 Q 的公式在固定 Y、Q>1 時則降低公式應變。不能從這幾頁概括成古典模型對本盒一律高估或低估應變；facts 目前只寫忽略牆柔度及短樑偏差，沒有擴寫方向，這樣合理。
2. BASF IV-4 符號表讓 Q 參照 Figure IV-2；但 IV-1 說 Figure IV-1 是均勻樑，Figure IV-2 是端厚減半樑。實看的 PDF 第 12 頁就是標明 Uniform Beam 的 Figure IV-1。應依實際截面和根部配置選圖，不能只照通用交叉引用套錯曲線。facts 在均勻矩形範圍引用 Figure IV-1 合適，本案 Q 仍待定。

來源身分分開記：Covestro 下載 URL 位於原廠官方網域；BASF 檔案是原廠著作的第三方網站鏡像，不能稱為 BASF 官方託管。舊 facts 的未下載狀態是歷史時點；本次兩份 cache 實檔都存在且 hash 與 `sources-v002.json` 相符。未重查 UL Prospector 文章，不能把本次六頁核對擴稱全部網路來源皆複查。

本審查不採用原冊材料應變表認定 FDM 許用值，不給 Q、力或允許撓度數字；材料、層向、製程、有效力學 L、壽命與實體強度／配合仍待驗證。僅新增審查報告，沒有修改舊 facts、catalog、progress 或 evidence。
