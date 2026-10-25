# 08-01 後續螺紋路線選擇 v001

2026-10-25，學員回覆先前的路線問題，原話為「1.2.憶起」。助教理解為「1、2 一起」：自訂列印螺紋，以及金屬螺絲／熱熔螺母兩條路線都學。這是對原話的解讀，沒有推定先後順序，也沒有選定硬體型號或安裝方式。

本次以新的 route-decision-v001.json 保存原話、問題、助教解讀與選擇來源。catalog 只更新單元08的目標及08-01目前顯示的路線文字，清單顯示兩支線；原operationRun、plan、parameter-record、24個待定參數、來源、實拍及場景均保留不覆寫。原紀錄的「路線待定」屬收到回覆前的狀態，頁面明示其歷史時態。

透過 manage.py note --lesson 08 --step 08-01 --author tutor --revision 5 寫入一則包含學員原話與助教解讀的筆記，共用紀錄revision由5變6。只新增筆記及事件；activeLesson、各currentStep、completedSteps、learner、decisions與fileVersions都未改。沒有confirm、未執行08-02、未啟動Blender或新增模型。

標準、尺寸、間隙、材料及硬體型號待定，列印與試配結果留空，沒有強度或配合合格判定。兩條支線後續各自保存規格、草案與試驗結果，不共用未驗證的合格值。

版本依據：
- learning/evidence/08/2026-10-25-thread-route-decision-v001/route-decision-v001.json
- 同資料夾baseline-v001.json保留更新前catalog／progress及45個受保護檔案雜湊；validation-v001.json記錄本次核對。
- learning/evidence/ui/2026-10-25-thread-route-decision-v001.jpg：內嵌瀏覽器原始截圖，304×848，未修改像素；同名JSON記來源與雜湊。頁面已實際顯示兩條路線、待定項目與舊紀錄時態，並已保留開啟。

本次是可回復的選擇與文字更新，沒有修改程式，不重跑Blender示範或與變更無關的測試；以狀態差異、歷史檔雜湊、API逐值一致及瀏覽器實際顯示核對。
