# 獨立數值重算的唯讀同儕審查 v001

2026-10-25，逐行核對 `recompute_blender.py`、`recompute_stl.py` 與兩份輸出 JSON，另直接用 raw 世界頂點／polygon 及 binary STL 做標量核算。沒有匯入舊 checker 或執行這兩份重算程式，沒有再開 Blender。本次僅新增此 JSON／MD，未改待審檔或舊 evidence。輸入雜湊見 JSON。

窄範圍內未發現阻斷性數值錯誤：

- 原場景讀取使用 `load_ui=False/use_scripts=False`，無 save 或幾何修改呼叫；11 個場景磁碟 hash 目前皆與 readback 的 after 相同。`calc_loop_triangles` 是記憶體三角化快取，不儲存原檔。
- 世界座標先 `matrix_world @ vertex`，再以 `scale_length × 1000` 換 mm，保留父層／旋轉／位移。所有來源的因子約 1.0000000475，浮點尾數與 STL 直接 mm 座標之差在既定數值門檻內。Item Dimensions 與 world AABB 分開正確。
- 導軌：world Z≈10 的兩個朝下四邊形，獨立 XY shoelace 面積各 **224.00002128 mm²**，共 **448.00004256 mm²**。每面實際露出 **56×4 mm**；60 mm 是建構工具長，端壁內的部分不計懸空。不是 480 mm²。
- 凹點：21 個底面均 32 頂點，中心同 Y；組內15對相鄰點中心距約1.59999283～1.60000236 mm，半徑約0.6。直接算相向 X 邊界的最薄肉 **0.39999391548 mm**，與 root 的中心距減 X 半徑公式一致。名義為 **1.6−1.2=0.4 mm**，此公式僅適用本次同 Y、同相位多邊形，不能泛當任意曲面最近距離。
- 定位柱工具 bounds 實測約 **4×4×30 mm**，Z−13.5～16.5；內底以上名義露出高 **29.5 mm**（30包含0.5mm入底）。實際內底浮點 Z−13.000000617，得到露出高29.500001401；root使用名義−13得到29.500000784，差6.17e−7mm不影響名義值。**露出高不等於已核准的力學有效自由長度**。

10 份 STL 重新解析的尺寸／體積及 root 的指定邊拓撲檢查無矛盾。限制必須保留：

- bounds、signed volume、edge incidence、單一 vertex graph component 都不能證明完整表面相等，也沒有檢查自交或完整 vertex link 流形條件。不要將 `dimensions_and_topology_consistent` 翻成已證整件等形、可印或配合合格。既有完整面覆蓋 audit 是另一份證據。
- `round(x/1e−5)` 是格點量化，並非嚴格歐氏距離 weld tolerance；任意資料可有跨格邊界或近點合併限制。
- root 的 stored normals 只用 dot>0 判同半球。此同儕另解析10件實檔，最大法線夾角約3.42e−6度、長度約0.999999912～1.000000090，沒有實際法線偏差問題，但原檢查器不能泛稱完整法線精度驗證。
- `obj.data` 是 base mesh，並非一般 evaluated modifier surface；目前比對的是既有已 Apply 成品。來源 readonly 與完整形狀等價是不同主張。

0.4mm噴嘴不能推成0.4mm線寬；細肉可能難辨識只是待切片／列印核對的工程風險。448mm²朝下面也不能單靠面積判定一定要支撐或列印失敗。定位唇邊與柱的重複定位屬潛在競爭，尚未證實實體卡死。材料、允許應變、物理結果、最終方向與合格判定仍空白。
