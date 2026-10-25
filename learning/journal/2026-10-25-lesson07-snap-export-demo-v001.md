# 07-04：卡扣 Body／Lid STL 數位準備 v001

日期：2026-10-25（Asia/Taipei）。由助教在獨立Blender將07-03的一組既有卡扣方向候選分成Body／Lid兩份STL，解析實檔並實際重新匯入核對。**只完成數位匯出準備，沒有製作2–3種臂長／厚度試片、切片、列印或試扣。** 支撐、最終列印方向、材料與強度／實體合格結果仍待定；不代學員確認完成。

## 來源與輸出版本

固定07-03 `learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/demo-files/u07_print_orientation_v001.blend`，106,462 bytes，SHA-256 `360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d`。本次讀取 `demo-files/sources/u07_print_orientation_v001.blend`同hash副本；方向紀錄 `print-orientation-record-v001.json` SHA-256 `b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986`，連同來源verification及兩份candidate raw的固定hash皆未改。原Body Ry90／Lid Rx180候選旋轉、位置和網格形狀保留，未Apply Rotation，兩Tools始終隱藏；**沒有另存新blend**。

| 原生匯出首次版本 | bytes／三角形 | 實檔world外框mm | SHA-256 |
|---|---|---|---|
| u07_snap_body_v001.stl | 5884／116 | [30.0, 44.5, 60.0] | `6ee4b13556db93196189604a96a0dbf3074fcaf6dd3423b3fc86cc2421910ff8` |
| u07_snap_lid_v001.stl | 2484／48 | [60.0, 46.0, 7.000004887580872] | `c80ea7d584a2f71cc0b2619ff903bdff57d8c97441d61111a0e8c7b839f55c21` |

Body bounds `{'min': [-55.0, -24.5, 0.0], 'max': [-25.0, 20.0, 60.0]}`、體積 `15888.784523791977` mm³；Lid bounds `{'min': [10.0, -26.0, -1.0728836059570312e-06], 'max': [70.0, 20.0, 7.000003814697266]}`、體積 `5602.19990320802` mm³。兩件實檔與重匯入均非空、一體閉合／單殼／Non Manifold0／genus0。約1e-6 mm的負Z是浮點重建讀值，1e-4 mm僅作數值核對，不是製造公差、穿床允差或附著證據。

`stl-export-record-v001.json` SHA-256 `b3b3745d714a628b5155b01fbfeca81cda50855aaeb95aa757f616ea58ee268a`綁定原場景／方向紀錄、兩STL路徑／hash／bytes、原生選項／operator與實際重匯入。`export-manifest-v001.json`再連結四份raw、十份腳本、四份資料快照、25張原圖與空白試配表；journal僅以路徑連結，避免後續發布註記造成循環hash。

## 25筆實際操作

```text
python -X utf8 learning/tutor/run_demo.py lesson07_snap_export learning/evidence/07/2026-10-25-lesson07-snap-export-demo-v001
```

Blender 5.2.1 LTS（build `9e2066aef7ef`），English (US)、出廠設定及獨立設定／暫存；Window.event_simulate操作，不搶用學員視窗或實體滑鼠。runner **2026-10-25T17:08:56.916+08:00～2026-10-25T17:11:03.012+08:00**，completed／exit0／runErrors空白。

1. 每件匯出前重新Open固定候選副本，Outliner只選目標成品、隱藏另一件及Tools，讀回來源姿態與Item／world尺寸，實拍斜視及剖面。
2. File > Export > STL，**Selection Only開、Scale1、Scene Unit關、Binary、Batch關、Apply Modifiers開、Y Forward／Z Up**，DAG_EVAL_RENDER；確認新檔路徑後原生匯出，讀實檔hash／bytes／拓樸與完整形狀。
3. File > New > General清空，設Metric／Millimeters／Unit Scale0.001；分別Import STL，Scale1／Scene Unit關／Y Forward／Z Up。用UI命名Body_STL／Lid_STL，首件匯入後只切一次Item，實拍Dimensions／剖面並Select Non Manifold選到0邊。
4. 顯示兩件實際重匯入成品，保留原候選分件位置，核對最低Z≈0與X投影距 `35.0` mm；無Tools，未改成扣合裝配，也未檢查特定機型床幅。

25張PNG逐檔核對尺寸與SHA-256、像素未修改。STL無單位標記，本次座標數字按mm解讀。來源N面板Body仍是物件軸Dimensions `[60.0, 44.5, 30.0]`，不能當Ry90後world外框；實際重匯入的origin／rotation0、Scale1，其Item Dimensions才與約30 × 44.5 × 60的world外框一致。Location0代表原點，不表示頂點已移到世界原點。

## 原生operator證據與幾何查核

原生STL operator在本次window_manager.operators沒有歷程項，四次export／import的operator_history_available均false；沒有補造history。證據是**確認前live File Browser的實際id／選項／目標**、UI按確認後的新二進位檔或新匯入mesh。若將來history有值，匯入器仍須逐欄比對。ui-probe-v001因假設必有history而中止（6圖及已產生Body檔保留），修正記錄方式後ui-probe-v002成功25圖；兩者均非本次正式輸出來源，main v001另跑並固定十腳本／四資料快照。

STL checker核對有向共面來源三角面union的完整覆蓋、整個平面面積、閉合／winding／體積、world bounds／落床及逆回07-02的完整卡扣剖面、根部native miter、臂／鉤及蓋裙凸緣。**不硬綁來源三角面數、索引或native polygon數**；合法3倍細分／重編索引的回歸案例通過。STL／重匯入facet法線角度及面積是另算資料，不是原生polygon統計、GPU像素或支撐決策。本步沒有重跑原生Overhang；引用的是07-03既有方向比較。

來源與兩件STL／重匯入的layout都維持分件候選，不是最終列印方向核准。Body側放只證明臂長／名義彎曲方向平行層平面，不保證層間附著、疲勞或強度；Lid翻面仍有高處凸緣朝下面。STL通過不代表免支撐、可直接列印或實體可扣合。

實main純validator與25PNG通過，未由本文件任務執行正式import。較早完整相關import suite121項通過；真run後發現驗證器以int單位矩陣誤拒native float1.0／0.0，已只修正參考型別並讓valid fixture使用原生float矩陣，**未變更raw／STL或放寬EPS**；修正後11項focused全過並重驗真run通過。尺寸1e-4 mm、座標weld1e-5 mm、體積相對1e-5及有向覆蓋位置誤差帶皆只處理浮點，非製造、支撐、強度或配合合格門檻。

## 空白試片／試扣表與共用進度

`trial-fit-record-v001.json`是**尚未執行的空表**，綁定上述兩份正式STL版本／hash與來源方向及07-02草案。已知噴嘴0.4 mm引用學員原話紀錄；列印方法／機型／材料／線寬／層高／切片軟體／支撐／最終方向等仍null。實測尺寸、臂厚／鉤尺寸、裝拆力／手感、循環次數、破壞位置、白化／永久變形及支撐移除損傷皆待填新版本，不預填「通過」。

材料、ε、Q、δ_req、δ_allow、力量、實體干涉、合格強度及合格間隙維持null；printed／fit_tested／slicer_checked／strength_analysis_performed／fit_qualification／support_generation_performed皆false。沒有由斷裂位置推斷根因，也沒有不同參數試片比較。未來真實列印／量測請建立新紀錄版本，保留本次空白v001。

本run `publication-baseline-v001.json`的52步canonical基線已核對：共用progress仍revision5、SHA-256 `d92e4f2ee78a1cf41386816b8616bf635b89fb25f8bfd813ac00cd20ed20b4ef`；工作區前後一致，11目錄項／0學員檔案，canonical指紋 `4ad6905b1cef7594ff1bfed45b81e7794fdbf128011df09b4686bdb44d0a7d2f`。未confirm，未將助教STL登記為學員成果。manifest的publication_audits串連獨立幾何與軟體檢查；HTTP／瀏覽器證據另由publication-checks串連，避免循環hash。下列正式發布另記。

## 正式發布與獨立審核

已正式匯入07-04的25筆助教操作；主頁顯示原生重匯入尺寸及匯出選項實拍、來源N面板／世界外框／STL／重新匯入的尺寸比較、兩份STL下載、版本清單與空白試配表。只有07-04的canonical內容改變，其他51步與共用progress保持不變。頁面未把本次數位準備寫成實際列印或試扣完成。

`audit_snapfit_stl.py`未呼叫新的卡扣STL／semantic checker，以低階binary decode及獨立有向拓撲、三角面對應與體積核對兩STL、來源及實際重匯入。兩件均通過；STL對來源最大頂點差Body約0.0000038147mm、Lid約0.00000001583mm，仍使用原1e-4mm數值門檻。檔內normal欄皆有限、無零向量或反向；這只是檔案方向診斷，不是強度或列印品質。

修正native float identity參考後，全套tutor **223項：222通過、1項Windows symlink權限跳過**，server **17項全過**，JavaScript語法及新尺寸表的stage／null／0／文字轉義檢查通過。最終測試輸出保存在 `tutor-regression-final-v001.log`，檢查摘要與hash見 `automated-checks-v001.json`。

HTTP逐byte核對25張原PNG、兩STL、export record／manifest／空白trial JSON與本journal；檔案雜湊與API的catalog／progress一致。實際304×848瀏覽器已開至07-04，核看原始實拍、雙欄尺寸表、待定條件與下載連結，保存[實拍頁面](../evidence/ui/2026-10-25-lesson07-snap-export-demo-v001-final-overview.jpg)、[尺寸比較](../evidence/ui/2026-10-25-lesson07-snap-export-demo-v001-final-comparison.jpg)及[候選／待定條件](../evidence/ui/2026-10-25-lesson07-snap-export-demo-v001-final-conditions.jpg)原始JPEG，像素未改。最終公開核對見 `publication-checks-v001.json` 與 `learning/evidence/ui/2026-10-25-lesson07-snap-export-demo-v001.json`；頁面保留開啟，學員完成進度未代勾。
