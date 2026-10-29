# CAD Sketcher Y 方向與 GUI 拉伸試驗

2026-10-27。依學員要求以獨立 Blender 5.2.1 LTS、隔離 CAD Sketcher 0.32.1 補 Y 方向草圖操作，並試做由草圖手工拉伸。程式僅作獨立環境啟用、對話框路徑填入、原檔複製、原圖保存與讀值；尺寸欄和拉伸操作透過 Blender 原生模擬事件。未操作學員視窗、未登記學員完成、未寫真實學員工作區。

## Y 方向 GUI 變更

來源為參數盒 v004 的80×40場景，源SHA-256 `a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2`，來源盒與上蓋網格、驅動器係前次**程式建立**，不是本次手工建模。開啟副本後以 Sketcher 側欄第二個 Distance 改40→50 mm，另存 v001、重新開啟，再以同一欄改50→45 mm並另存 v002。六組各12項檢查（含原值、修改、保存、重開、重開後再改、再保存）通過，含 solver OKAY／DoF0、盒蓋外框、內腔、唇外框、四側名義間隙與兩件 Non Manifold 0。

| 草圖 mm | 盒體 mm | 內腔 XY mm | 唇外 XY mm |
|---|---|---|---|
| 80×40 | 80×40×30 | 76×36 | 75.6×35.6 |
| 80×50 | 80×50×30 | 76×46 | 75.6×45.6 |
| 80×45 | 80×45×30 | 76×41 | 75.6×40.6 |

四側數位間隙約0.2 mm／總量0.4 mm是草案，非實體試配或合格值。長度比較1e-4 mm僅為數位讀值比較，不是製造公差。圖 `CAD-Y-02-changed-80x50.png` 為 Blender 真實畫面；右側可見80／50及 Fully defined，內腔／間隙數值來自讀回，不可從該圖直接量測。

**重開警告：**`CAD-Y-04-reopened-80x50.png` 底部出現 `Tool 'sketcher.slvs_select' not found for space 'VIEW_3D'`；原因尚未知。下一步數值45 mm修改及讀值成功，不代表其他繪圖工具或所有操作都可正常使用；遇警告應停下核對。原試驗摘要保持原樣，另存 `y-reopen-warning-v001.json` SHA `4336c07476aac36dca167bb8ed1f22e4e620c9bfabb72bca922adaf7642e21cb`。

安全摘要 `learning/evidence/parametric/2026-10-27-cad-sketcher-y-dimension-v001/y-dimension-verification-v001.json` SHA `0a311ba7571fddb2fc5e91036a81f53200bd25624f2f4f4f72970ec36649ef2f`；此摘要須與上述警告補充共同閱讀，原始 runner-status 含 Recent 清單，不公開。60→80→70等先前X實驗保持獨立，Y測試不代表任意參數組合都有效。

## 原生草圖拉伸：實心長方體，非盒蓋完成

用先前GUI建立並完全約束的60×40草圖副本，離開草圖後 Ctrl+Shift+E 呼叫此版本 CAD Sketcher 的 Extrude；在互動工具輸入無單位 `30`，確認後由實際評估網格讀得60×40×30 mm、8頂點、6面，保存並重開核對相同外框。工具新增 `CAD_Sketcher Extrude` 幾何節點修改器；目前是**實心長方體**，尚無內腔、上蓋或兩件連動，不可稱完成盒體。

探測 `cad-sketcher-extrude-probe-v001` 誤以滑鼠點擊先確認，結果拉伸約3.90186 mm；`cad-sketcher-extrude-trial-v001` 模態輸入 `30mm` 讀回只有0.03 mm，未通過預期30 mm檢查。兩次失敗保留，不以runner結束代替成功；`cad-sketcher-extrude-trial-v002` 以無單位 `30` 在該特定 Blender／CAD Sketcher 版本及 Unit Scale 0.001 場景讀回30 mm。不可泛化至其他工具／版本；實際使用仍須核對讀值。

原圖及結果 `learning/evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/`；後續內腔、上蓋與Y連動需要各自操作和證據，不依實心拉伸結果推定。
