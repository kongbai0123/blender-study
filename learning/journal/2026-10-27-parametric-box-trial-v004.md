# 參數式小盒與上蓋連動試作 v004

2026-10-27。依學員要求完成此前討論，建立獨立參數式版本並保留原盒和上蓋。這是助教試作，不是學員作品或學員課程完成紀錄。安全摘要：`learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/parametric-box-verification-v004.json`，SHA-256 `50d3691ddef18f08f6c82712514aa1841a9660e07577a06592357424533f193d`。原始 runner-status 含 Recent 清單，不公開、不由網頁連結。

## 方法與可編輯性

使用 Blender 5.2.1 LTS（build `9e2066aef7ef`）、隔離環境及官方 CAD Sketcher 0.32.1。由[先前實拍建立的60×40完全約束草圖](2026-10-27-cad-sketcher-environment-trial-v001.md)拷貝起始檔並驗雜湊。**本次盒體、上蓋網格與頂點驅動器是以 Python 程式建立；不可表述為手動 GUI 逐步建模。** 草圖尺寸修改則由 `window.event_simulate()` 實際操作側欄欄位；截圖為 Blender 原生 PNG。開／存對話框路徑和檔名以程式填入、確認以事件送出。

草圖的長、寬尺寸約束屬單一驅動來源：兩件網格的頂點驅動器引用相同 Scene 內 CAD Sketcher 約束 ID 屬性。盒高、側壁、底厚、蓋板厚、唇邊深度、總間隙及唇壁厚是各自獨立的 Scene 自訂屬性（以 mm 的場景數值表示）。本版不是 SolidWorks 原生特徵樹；修改或刪除約束、驅動器、頂點可能破壞關聯。輸入尚無自動有效範圍防護，只在 `L,W > 2*(側壁+總間隙/2+唇壁)`、`高度>底厚≥0`、`高度≥唇深>0` 且使用本次具體草案值的範圍檢查；不要以此推定任意其他參數組合均正確。

本試作將原盒尺寸重建於原點起算的正XY區間、Z=0～30，原盒的實際場景座標為置中範圍；尺寸與結構參照原盒，**座標沒有相同宣稱**。盒與蓋是不同網格，各為封閉單殼。

## 本次實際動作與數位驗證

原生UI在草圖側欄修改 60→80 mm，另存並重新開啟80版；重開後再以UI修改80→70→80 mm，另存第三版。五組：原60、80、重新開啟80、重開後改70、恢復80，各14項檢查通過，包括 solver OKAY、DoF0、盒蓋外框、內腔、唇外框、四側數位間隙、非流形邊及體積。長度比較閾值1e-4 mm；體積採05-05原驗證的相對1e-5，均只處理浮點數值，不是製造公差。

| 草圖X | 盒外 X×Y×Z | 腔內 X×Y×Z | 唇外 X×Y | 數位間隙 |
|---|---|---|---|---|
| 60 mm | 60×40×30 | 56×36×28 | 55.6×35.6 | 置中每側約0.2 mm |
| 80 mm | 80×40×30 | 76×36×28 | 75.6×35.6 | 置中每側約0.2 mm |
| 70 mm（重開後） | 70×40×30 | 66×36×28 | 65.6×35.6 | 置中每側約0.2 mm |

所有值為數位模型，浮點讀值詳見摘要；0.4 mm是每軸的草案總間隙，不是已驗證合格值。僅實際變動X；Y及其他獨立自訂參數尚未逐項變更測試。無列印、切片、實體量測或試配，physicalMeasurements／fitResults／qualifiedClearanceMm 均 null，不能判配合或強度合格。

獨立全新背景 Blender 程序再載入最終版，驗證盒蓋均為80×40，程式內存中改70後兩件都變70，沒有存檔；這是**程式編輯**而非GUI操作。另以背景程序測試與啟動器相同的 addon 啟用／載入參數順序，成功讀到addon、兩件與80 mm；尚未代學員從啟動器執行互動GUI。

## 場景與真實畫面

全部位於 `learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/`，完整圖及檔案雜湊見摘要。

- `demo-files/parametric_box_60x40_v001.blend`：SHA-256 `4c938ccfb74c5a88a6dc6d2fc73ebb670a132d54400ebe63e78b82b9182468be`。
- `demo-files/parametric_box_80x40_v002.blend`：SHA-256 `97c0236091da77a279d87dbb6a3198087d668fc3247bb8c9abafa7bdfa409e4f`。
- `demo-files/parametric_box_80x40_v003.blend`：重開並改70再恢復80後保存，SHA-256 `a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2`。
- `CAD-BOX-04-changed-80.png`：側欄 80／40 與 Fully defined；`CAD-BOX-07-reopened-edit-70.png`：重開後改70；`CAD-BOX-09-model-80.png`：離開草圖、程式建立的盒蓋外形。草圖尺寸標註線的位置仍待改善，整合課程時不能用圖片冒充內腔數位量測。

原盒與上蓋檔案未動；此輪沒有手動修改學員 progress、catalog、學員工作區，也未登記學員作品。runner 的 workspacesUnchanged 只代表執行前後內容端點一致，不證明中間沒有其他程序寫入。

## 學員建立自己的可編輯副本

本機提供 `learning/tutor/open_parametric_box.py`，用獨立 config、scripts、datafiles 和暫存資料夾，並指向上述隔離 extension profile，**不開啟 event simulation**，所以使用者可正常操作。啟動時需安裝於原路徑的 Blender 與 CAD Sketcher 0.32.1 profile；該第三方套件未加入公開教材，其他電腦須先建立相容隔離環境。

在專案根目錄執行以下命令，由使用者明確選擇新副本路徑；已有同名檔會拒絕覆寫：

```powershell
python learning/tutor/open_parametric_box.py --copy-to learning/workspaces/engineering-parametric/my_box_v001.blend
```

下次重開個人副本使用：

```powershell
python learning/tutor/open_parametric_box.py --open-existing learning/workspaces/engineering-parametric/my_box_v001.blend
```

啟動器拒絕以 evidence 路徑為可編輯目的地；這些命令只有使用者執行時才建立副本或啟動GUI。隔離偏好不永久保留。修改尺寸前確認 Blender 側欄 Sketcher 已在活動草圖、兩個尺寸與 Fully defined；修改後要核對兩個物件再另存新版本。啟動器3項單元測試通過：新副本內容與隔離環境、拒覆寫／保護 evidence、重開既存個人副本。

## 失敗版本與接續

- run v001：60→80、存檔重開和基本閉殼測試通過，但舊成果保存時隱藏兩件，缺內腔／唇邊驗證；保留並以v004取代，不稱完整交付。
- run v002：錯將1e-4 mm長度絕對門檻套到mm³體積，6195.1998947對6195.2相差0.0001053 mm³而失敗；幾何位置與四側間隙均通過。後續使用已記載的原05-05體積相對門檻，而非忽略體積檢查。
- run v003：60→80、重開80→70→80以及完整幾何檢查成功；最後離開草圖拍照後，觀察函式仍要求活動草圖，runner因而失敗。v004改為離開後僅記模型可視狀態，之前已分別核對幾何。
- 接續將本試作作為第05章可查證示範，明示程式建立，不能把其宣稱為手工操作教學。待改進獨立參數變更測試、越界輸入防護、尺寸標籤與更清晰的人手建置流程；任何列印與實測留待實際取得結果。

## 後續數位參數掃描（補充 v001）

在 v004 完成並凍結安全摘要之後，另用全新背景 Blender 程序、以 Python 單次逐一修改八個不同主控的**記憶體值**，每次復原，不保存場景。參數與試值：草圖Y對應ID屬性50、盒高35、側壁3、底厚3、蓋板厚3、唇深5、總間隙0.6、唇壁3 mm。每種核對盒／蓋外框、腔內、唇內外、底板高度及兩個閉殼，共8×7=56項通過。此處直接改 Scene ID 屬性，不代表已透過GUI操作Y約束或驗證草圖求解更新，也不代表可任意組合各參數、切片或實體配合合格。

補充結果獨立保存於 `learning/evidence/parametric/2026-10-27-cad-sketcher-parameter-sweep-v001/parameter-sweep-verification-v001.json`，SHA-256 `1d41fae0c2551564f327d653c0fb4b0a3c6ca823db7cd587fbe06b8654774c01`；程式為 `learning/tutor/scenarios/cad_sketcher_parametric_sweep.py`。此前 v004 摘要的「其他參數尚未測試」按當時時點理解，不回填舊摘要；目前已有上述有限的程式掃描，仍缺各項的GUI與跨參數組合驗證。
