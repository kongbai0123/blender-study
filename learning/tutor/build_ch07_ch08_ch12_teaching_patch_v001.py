"""Generate step-ID keyed, independently evidenced curriculum edits from v035."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'learning/web/engineering-curriculum-v035.json'
BASE_SHA='d40ffc3102585947f1a19d2e50d072f343cf25685df9d7e8555dfd702bc4fa91'
OUT=ROOT/'learning/patches/ch07-ch08-ch12-teaching-v001.json'
if sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:raise ValueError('curriculum base changed')
if OUT.exists():raise FileExistsError(OUT)
curriculum=json.loads(BASE.read_text(encoding='utf8'));existing={s['id']:s for c in curriculum['chapters'] for s in c['steps']}
def artifact(path,label):
 p=ROOT/path
 return {'path':path,'sha256':sha256(p.read_bytes()).hexdigest(),'label':label,'type':'verification-json'}
def figure(path,caption):
 p=ROOT/path
 return {'type':'screenshot','path':path,'sha256':sha256(p.read_bytes()).hexdigest(),'caption':caption}
def detail(steps,why):return {'steps':steps,'why':why}
install='learning/evidence/parametric/2026-10-28-cad-install-gui-trial-v002/'
fake='learning/evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json'
render='learning/evidence/12/2026-10-28-render-safe-copy-gui-v003/'
measure='learning/journal/templates/engineering-measurement-fit-v001.json'
comp='learning/journal/templates/engineering-compensation-v001.json'
assembly='learning/journal/templates/engineering-assembly-trace-v001.json'
P={
'ch07-setup-01':{
 'actions':['從 CAD Sketcher 0.32.1 官方 release 下載 Windows x64 ZIP，保留原檔。','在 PowerShell 對該 ZIP 執行 Get-FileHash <檔案完整路徑> -Algorithm SHA256，並核對檔案大小。'],
 'success':'ZIP 為 1,283,581 bytes 且 SHA-256 為 b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59；不符先停止，不安裝。',
 'evidenceStatus':'documented_lesson','artifacts':[artifact(install+'safe-summary-v001.json','隔離安裝使用的 ZIP 來源與讀值')],
 'limitations':['2026-10-27 的來源摘要及本次隔離 GUI 使用相同 SHA 的 ZIP；沒有記錄學員下載或下載過程截圖。','第三方 ZIP 不隨教材發布；Windows x64 與 Blender 5.2.1 以外的安裝包需各自核對。'],
 'detail':detail(['到官方 0.32.1 release 頁下載 Windows x64 ZIP，保留原 ZIP。','對實際下載的檔案查大小及 SHA-256；任一不符先停止。'],'來源與位元組吻合是安裝前置條件，不代表擴充套件已可運作。')},
'ch07-setup-02':{
 'actions':['Edit > Preferences > Get Extensions，展開右上選單並選 Install from Disk...，選上一步核對過的 ZIP。','到 Add-ons 確認 CAD Sketcher 已啟用；回 3D Viewport 按 N，查看 Sketcher 分頁。'],
 'success':'Add-ons 中 CAD Sketcher 勾選；3D Viewport 的 N 側欄出現 Sketcher。失敗時停下並記錄錯誤。',
 'evidenceStatus':'existing_demo','figures':[figure(install+'CAD-INSTALL-01-menu.png','獨立 Blender 的 Install from Disk 選單；示範使用隔離擴充套件目錄。'),figure(install+'CAD-INSTALL-03-addons.png','獨立 Blender Add-ons 頁的 CAD Sketcher 啟用畫面。'),figure(install+'CAD-INSTALL-04-sidebar.png','獨立 Blender 3D Viewport 的 N 側欄顯示 Sketcher 分頁。')],
 'artifacts':[artifact(install+'safe-summary-v001.json','隔離 GUI 安裝、版本和啟用讀回')],
 'limitations':['ZIP 路徑和檔名由程式填入檔案對話框；選單與頁面切換透過獨立 Blender GUI 事件。','示範僅證明隔離環境，非學員電腦已安裝；示範的 extension profile 與個人設定分開。'],
 'detail':detail(['確認所選檔案為已核對的 ZIP，再以 Install from Disk... 執行安裝。','確認 Add-ons 勾選 CAD Sketcher，回 3D Viewport 用 N 查看 Sketcher 分頁。'],'安裝檔存在不等於外掛已成功啟用。')},
'ch07-setup-03':{
 'evidenceStatus':'existing_demo','artifacts':[artifact(fake,'假專案工作區建立與檔案登記 CLI 實證')],
 'limitations':['命令已在隔離假專案執行；其 synthetic progress 與資料夾不是學員成果。','毫米場景另參照原教材 04-02；既有不同場景或不同建立順序下新增物件尺寸可能不同，應核對實際畫面。','命令建立工作區不寫進度；使用者若已有同名練習檔，另存未使用的新版本。'],
 'detail':detail(['從專案根目錄執行 python learning/manage.py engineering-workspace，確認工作區路徑。','保留現有作品，依第 03 章設定 Millimeters 與 Unit Scale 0.001。','在自己的工作區另存新的 .blend；同名存在時改用未使用的新檔名。'],'工作區及個人場景分開管理；示範假專案不代替學員存檔。')},
'ch08-param-plan':{
 'evidenceStatus':'documented_lesson','actions':['列出盒長、盒寬、側壁、底厚、蓋板厚、唇深及同一方向的總間隙。','寫出內腔＝外寬−2×側壁、唇外＝內腔−總間隙；未完成個人試配時 0.4 mm 僅是試驗值。'],
 'success':'能寫出各尺寸來源及關係，區分總間隙、單側間隙與尚未取得的實測值。',
 'limitations':['參數表是設計關係；不代表模型已連動或實體試配合格。','例：60 mm 外寬、2 mm 側壁、0.4 mm 總間隙得到 56 mm 內寬、55.6 mm 唇外；均為名義示範而非實測。'],
 'detail':detail(['以相同方向分欄記外形、壁厚與總間隙。','先計內腔，再計唇外；只有置中時單側間隙才等於總間隙的一半。','寫明 0.4 mm 為尚未實體核准的試驗值。'],'先建立可追溯關係，再處理草圖和 Driver；紙上公式不代表自動更新。')},
'ch08-guard-prepare-01':{
 'evidenceStatus':'existing_demo','artifacts':[artifact(fake,'隔離假專案的建工作區、複製與重名拒絕紀錄')],
 'limitations':['本次只在假專案執行；副本及 synthetic progress 都不是學員的檔案與完成紀錄。','受控面板僅接受指定示範手工盒副本；與自己另建的盒子不可互相冒充。'],
 'detail':detail(['執行複製指令並核對目的地與來源 SHA。','如同名存在，換新檔名；不要覆寫。'],'已核對的來源副本才適用特定受控面板。')},
'ch08-guard-checkpoint-01':{
 'evidenceStatus':'existing_demo','figures':[figure('learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/GUARD-27-registered-attempt.png','舊獨立 Blender 假專案：面板對已登記版本拒絕；非學員畫面。')],
 'artifacts':[artifact(fake,'假專案 CLI 登記與面板拒絕邏輯核對')],
 'limitations':['另存、登記與受控面板圖分別來自示範和隔離假專案；不代表學員已登記。','原生 Save／Export 與原生尺寸欄位不受受控面板攔截；登記不證明幾何或配合合格。'],
 'detail':detail(['在 Blender 以新檔名另存，保留上個已登記版本。','讀取當前 revision，再以網頁或 register-file 登記此場景。','若要繼續改，先另存另一個未登記的檔案。'],'可回溯的檢查點與下一版修改檔必須分開。')},
'ch12-dimension-chain':{
 'evidenceStatus':'documented_lesson','actions':['分欄寫出外寬、側壁、盒口內寬、唇外寬與同方向總間隙。','計算內寬＝外寬−2×側壁；唇外＝內寬−總間隙。'],
 'success':'能指出名義關係、數位讀值、實測與總／單側間隙各自來源；沒有實測就留空。',
 'limitations':['名義尺寸關係不是實際列印量測或合格判定。','例：外寬60、側壁2、總間隙0.4 mm 得內寬56、唇外55.6 mm；全部是名義例子。'],
 'detail':detail(['先確認每個量所沿的軸向與來源版本。','依公式計算名義尺寸；如置中，單側名義間隙為總間隙的一半。','分開保留尚未取得的實測與試配結果。'],'每個尺寸變更可沿鏈回溯；一筆實測也不代表批量能力。')},
'ch12-09-01-01':{
 'evidenceStatus':'field_protocol_ready','actions':['複製空白量測與試配範本到自己的工作區。','分欄記來源版本、名義尺寸及條件；只有實際量測或試配後才填結果與日期。'],
 'success':'能說明每欄的來源與單位；尚未量測、列印或試配的欄位保持空白。',
 'artifacts':[artifact(measure,'實體量測與試配空白紀錄範本')],
 'limitations':['空白範本與方法不代表已量測、已試配或學員已完成。','總間隙、單側間隙、直徑差及法向間隙不可混填。'],
 'detail':detail(['先依零件及版本分欄，記錄列印與量具條件。','實物尚不存在時保留實測、差值與試配欄空白。'],'可追溯來源、條件和日期才能比較結果。')},
'ch12-09-02-01':{
 'evidenceStatus':'field_protocol_ready','actions':['複製補償空白範本到工作區，記下對應實測來源與製程條件。','有實測後依實測−名義記錄差值，再記補償草案；切片器和模型補償避免重複。'],
 'success':'有實測時能追溯計算及後續重印驗證；無實測時補償與合格欄保持空白。',
 'artifacts':[artifact(comp,'製程補償空白紀錄範本'),artifact(measure,'實體量測與試配空白紀錄範本')],
 'limitations':['沒有實際量測，不預填補償或宣稱已改善；線性初估需重印驗證。','單個試片不代表所有方向、材料或批量能力。'],
 'detail':detail(['分別記名義與實測；觀察差值定義為實測減名義。','將候選調整、切片器既有補償及其方向分開；僅有實際數據時填入。','對應機器、材料、方向與重印結果；未驗證不標合格。'],'補償不是從 0.4 mm 噴嘴或試驗間隙直接推定。')},
'ch12-09-03-01':{
 'evidenceStatus':'field_protocol_ready','actions':['複製組裝與版本關聯範本，先選定同一分支及對應零件。','取得相容實物後依選定設計試組，記日期與觀察；若尚未印製則留空。'],
 'success':'能分辨同分支對件；只有實際試組後才填開合、鎖附或損傷結果。',
 'artifacts':[artifact(assembly,'零件版本與組裝空白紀錄範本')],
 'limitations':['側向螺帽、平面蓋四柱、燕尾與卡扣為不同分支，不能自動視為相容。','目前沒有實際列印、組裝或強度／配合合格證據。'],
 'detail':detail(['核對來源、版本與對件，先不要把不同分支混裝。','實物到手後才試組並記錄；目前欄位保留空白。'],'數位幾何與有限碰撞抽樣不能代替實物試組。')},
'ch12-09-03-02':{
 'evidenceStatus':'existing_demo','actions':['在空白版本關聯表記場景及各匯出檔案路徑與 SHA-256。','在版本紀錄核對每個 export 或 render 的來源 .blend，內容變更後另存並重新輸出。'],
 'success':'每個實際匯出均對應正確場景版本；尚無的檔案留空。',
 'artifacts':[artifact(assembly,'零件與版本關聯空白紀錄範本'),artifact(fake,'隔離假專案的場景與合成 fixture 關聯紀錄')],
 'limitations':['假專案中 STL 是無網格的合成 fixture，只示範版本記錄連結，不是 Blender 匯出或可列印檔。','檔案雜湊與來源關聯不證明幾何或實體配合合格。'],
 'detail':detail(['先查現有 .blend 和匯出檔案、SHA 與所屬分支。','逐一核對 export 或 render 的來源；未匯出者保留空白。'],'追溯場景和輸出檔可避免誤用過時模型。')},
'ch12-box-render-safe-copy':{
 'evidenceStatus':'existing_demo','figures':[figure(render+'12-COPY-02-saved.png','獨立 Blender 已將場景另存至隔離假工作區；非學員檔案。'),figure(render+'12-COPY-03-output.png','GUI 選 Output Properties；顯示相對路徑 //render_output\\box_lid。')],
 'artifacts':existing['ch12-box-render-safe-copy'].get('artifacts',[])+[artifact(render+'safe-summary-v001.json','隔離另存、重開與輸出目的地讀回')],
 'limitations':existing['ch12-box-render-safe-copy']['limitations'][:-1]+['新示範在隔離假工作區執行另存與路徑核對，檔案對話框欄位由程式填入；並未操作學員 Blender 或替學員確認。','這次只核對路徑，未渲染或向該路徑寫入影像。'],
 'detail':detail(['File > Save As 到自己的工作區及未使用的新檔名，保留原示範場景。','Output Properties 查看輸出欄；// 相對於目前 .blend 所在資料夾，絕對路徑則核對位於個人工作區。','確認後可重開場景再檢查；有疑慮時先改為自己工作區內的輸出位置。'],'先另存再解析相對輸出位置，可避免誤寫示範 evidence。')}
}
for sid,p in P.items():
 if sid not in existing:raise ValueError('unknown step '+sid)
 if existing[sid].get('track')=='appendix':raise ValueError('appendix unexpectedly targeted '+sid)
result={'schemaVersion':1,'base':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':BASE_SHA},'purpose':'補齊第 07、08、12 章教學與證據；無學員進度變更','patches':P}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('patch',OUT.relative_to(ROOT).as_posix(),sha256(OUT.read_bytes()).hexdigest(),'steps',len(P))
