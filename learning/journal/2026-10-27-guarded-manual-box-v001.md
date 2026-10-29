# 手工盒受控尺寸預檢 v001 原型

範圍：僅支援已知手工盒個人副本、特定 Scene X/Y 及內腔 Driver UID，以及特定的上蓋 Shape Keys。受控操作只變更一個輸入，先拒絕非有限數和超出 X60～100 / Y30～70 的候選範圍，調用同專案固定 SHA 的 `manual_box_auto_update_v002.py` 更新草圖，再讀回驅動及評估幾何。該區間僅是形狀鍵未夾取的理論範圍，不能稱製造或實體配合合格範圍；程序不攔截 Blender／CAD Sketcher 原生欄位、不攔截另存或輸出，並不自動存檔。

原型 `learning/tutor/guarded_manual_box_v001.py` SHA-256 `9dd50ba87227fc6ea77df4f6344b602ba245becfe4efe28d5343600a1282f067`，上蓋原始網格及兩形狀鍵簽章 `learning/tutor/manual_box_reference_v001.json` SHA `78f39a6ec422bb02b64fff64f70896c927a6ab449bcd84be9a03b6657bedae5c`，內腔更新 helper `learning/tutor/manual_box_auto_update_v002.py` SHA `cc39a2376c8abc41f61cb5beb796a83e22b63dc33b6b6aed5df9f135e83fc457`；內容變動拒絕修改。文本編輯器需開已存外部腳本並核對磁碟內容；只准受預期 `learning/workspaces/engineering-parametric` 個人未登記 `.blend`，拒絕 evidence 及已登記版本。未授權寫入學員工作區。

靜態原始蓋體矩陣、頂點、邊與面排序、Basis 及兩形狀鍵每頂點和相對基礎/範圍均核對；場景及形狀鍵各兩條 Driver 的公式、值、UID、變數和目標均核對。動態盒體/切割體/蓋的評估幾何則核每高度 X/Y 座標集合、點面數與 non-manifold，這不是全面面拓撲、所有碰撞、完整實體配合或打印能力驗證。

失敗處理：錯誤後嘗試還原原參數，再次求解且核對狀態與頂點；如還原不能驗證，報告「回復未確認，請勿存檔，重開原副本」。該字樣不能攔截使用者直接存檔。`learning/tests/test_guarded_manual_box_v001.py` 十項純 Python 測試通過，含超限拒絕不寫、失敗回滾和回滾失敗告警、簽章面連接/頂點/矩陣變更拒絕；純 mock 不是 Blender GUI 實證。此原型是否能在具體 Blender 實際執行，需讀後續隔離示範與獨立審查，不以此紀錄宣稱已驗證。
