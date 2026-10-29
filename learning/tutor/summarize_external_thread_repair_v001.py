"""Build privacy-safe, hash-verified summaries and optional mount lesson."""
import hashlib, json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(root).as_posix()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def collect(folder,scene):
    e=root/folder;run=load(e/'run.json');status=load(e/'runner-status.json');audit=load(e/'independent-audit-v001.json')
    if status['status']!='completed' or audit['sceneSha256']!=sha(e/'demo-files'/scene):raise ValueError('run or scene SHA mismatch')
    records=[]
    for r in run['records']:
        p=e/r['file'];h=sha(p)
        if h!=r['sha256']:raise ValueError('screenshot checksum mismatch: '+str(p))
        try:readback=json.loads(r['observed'])
        except (ValueError,TypeError):readback=None
        records.append({'seq':r['seq'],'slug':r['slug'],'image':rel(p),'sha256':h,'observed':readback})
    audit_short={k:v for k,v in audit.items() if k!='triangleAreasMm2InTessellationOrder'}
    return e,{'blenderVersion':run['blender'],'scenario':rel(root/'learning/tutor/scenarios'/Path(run['scenario']).name),
              'scene':rel(e/'demo-files'/scene),'sceneSha256':audit['sceneSha256'],
              'status':status['status'],'workspacesSnapshotUnchanged':status['workspacesUnchanged'],
              'independentAudit':audit_short,'independentAuditPath':rel(e/'independent-audit-v001.json'),
              'records':records,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,
              'qualifiedClearance':None,'qualifiedStrength':None}
thread_dir,thread=collect('learning/evidence/08/2026-10-28-external-thread-gui-trial-v010','u08_external_gui_draft_v003.blend')
mount_dir,mount=collect('learning/evidence/08/2026-10-28-external-thread-mount-gui-v001','u11_box_external_thread_draft_v001.blend')
for e,data in ((thread_dir,thread),(mount_dir,mount)):
    data['warnings']=['僅為幾何草案；不是 ISO 螺紋、列印或配合合格證明。',
       '零非流形邊與零 BVH 候選不能證明沒有自交；面積門檻是診斷用而非合格標準。',
       'raw runner-status 含機器私有 Recent 路徑，不得公開；本摘要未包含。',
       '部分原始 action 欄位因編碼損壞，人工重新整理文字，原始證據未覆寫。']
    (e/'safe-summary-v001.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

items=[
('載入已檢查牙條','開啟小盒和上蓋原檔的複本；示範以程式載入已完成的 Thread_Core 物件，顯示盒體與上蓋，選取牙條。','程式只載入既有物件、不重新生成牙條；不是 GUI Append 教學。','Outliner 顯示 Body、Lid 與 Thread_Core；牙條此時位於盒內，可能被盒體遮住。','程式讀回牙條 Z 約 -0.1～4.7 mm；盒體外框 60 × 40 × 30 mm，蓋子 Z 11～17 mm。'),
('轉向盒側','在 3D 視窗對牙條按 R、Y、90、Enter，將原本 Z 軸牙條轉至 X 軸。','先確認 Thread_Core 被選中；旋轉是繞物件原點。','畫面以盒體為主，牙條可能被遮擋，不能僅憑畫面確認完整旋轉。','程式讀回牙條 X 約 -2.4～2.4 mm，原點 Z 仍約 2.3 mm。'),
('移動到右側外壁','對牙條依序輸入 G X 31.9 mm、G Z -2.3 mm。','沿用前一步旋轉的原點；名義根部需與盒壁重疊，而不是只相切。','右側外壁可見牙條；畫面無法精確判斷嵌入深度。','世界座標讀回牙條 X 約 29.5～34.3 mm、Y/Z 均約 ±6 mm；與外壁 X=30 有約 0.5 mm 重疊。'),
('檢查布林工具欄','選中 Body，F3 搜尋 Add Boolean Modifier，選 Union、Exact，嘗試指定 Thread_Core。','Outliner 必須選盒體 Body，不是選上蓋或牙條。','修改器 Object 欄仍空白，為保留的第一次失敗畫面。','程式讀回 UNION、EXACT，但 operand 為空；不可在此時套用。'),
('選擇牙條工具','在 Object 欄位搜尋 Thread_Core，從候選清單點選。','接續上一步；輸入文字後必須確認選取生效。','修改器 Object 欄顯示工具名稱，視欄寬可能截斷。','程式讀回 operation UNION、solver EXACT、operand Thread_Core。'),
('隱藏工具','在 Outliner 的 Thread_Core 旁點眼睛，保留工具資料並觀察布林預覽。','先確認修改器物件欄正確；座標以自己的 Blender 版面為準。','工具顯示為隱藏，盒體上的牙條預覽仍可見。','劇本以 hide_get() 確認工具被隱藏；不代表工具被刪除。'),
('套用布林','在 Body 的 Boolean 修改器選單選 Apply，將外牙與盒體合併。','再次確認 Union、Exact 與工具對象；操作於示範副本。','盒側顯示外牙；單張畫面不能證明所有牙面品質。','程式讀回 712 點、420 面、1 連通體、非流形邊 0；五條盒內壁射線命中 X≈28 mm。'),
('聚焦檢視','按 F3 搜尋 Frame Selected，檢視盒側接口與上蓋。','選中已合併的 Body；牙條為盒側接口，並非螺旋上蓋。','畫面可見外側牙條及名義關閉位置的上蓋。','盒體外框 X 約 -30～34.3 mm，Y ±20 mm、Z ±15 mm。'),
('另存草案','使用 Save As，另存新版本；示範的檔案路徑與名稱由程式填入。','保存原始小盒及牙條源檔；新草案仍需實際驗證。','另存後畫面為盒側接口，這不是檔案對話框截圖。','另存場景 SHA-256 見 demonstrationSceneSha256；未執行實體列印或試配。'),
('重開並獨立檢查','重開新場景；另以獨立 Blender 讀取網格、檢查邊界、連通、三角面和 BVH。','檔案欄位由程式填入，重開後才進行獨立讀值；不更新學員進度。','重開後畫面仍有盒體、上蓋與盒側外牙。','獨立檢查 BVH 候選 0、面積 < 10⁻⁵ mm² 為 0、最小三角面 5.434×10⁻⁵ mm²、最短邊 0.01469 mm；僅是檢查結果，不保證無自交或可製造。'),
]
assert len(items)==len(mount['records'])==10
steps=[]
for idx,(item,r) in enumerate(zip(items,mount['records']),1):
    goal,op,context,visible,readback=item
    steps.append({'id':f'11-mount-{idx:02}','goal':goal,'operation':op,'context':context,
                  'visibleConfirmation':visible,'programReadback':readback,'screenshot':{'path':r['image'],'sha256':r['sha256']}})
lesson={'schemaVersion':1,'title':'第 11 章選修：盒側外牙介面幾何草案','scope':'已用獨立 Blender 示範；不代表學員完成，也不代表製造或配合合格。',
 'sourceScene':'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend',
 'sourceSha256':'ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff',
 'threadScene':thread['scene'],'threadSceneSha256':thread['sceneSha256'],
 'demonstrationScene':mount['scene'],'demonstrationSceneSha256':mount['sceneSha256'],
 'limitations':['牙形是示範草案，非 ISO 螺紋，既有內牙試塊不是匹配對件。',
 '初始截面與把牙條載入盒場景是程式處理；旋轉、移動、布林、另存及重開為 GUI 操作，檔案欄位由程式填寫。',
 '修正版改變多邊形相位與芯柱高度，須保留 v005 原始問題與修訂紀錄。',
 '零 BVH 候選與零非流形邊不能證明無自交；五條射線只是局部抽樣，蓋子間距僅為靜態外框距離。',
 '材料、允許間隙、切片、實體列印、量測、試配與強度均待定。'],
 'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,'steps':steps}
out=root/'learning/lesson11_external_mount_optional_steps_v001.json'
if out.exists():raise FileExistsError('Choose new version; existing optional lesson must not be overwritten.')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Validated',len(thread['records']),'thread and',len(mount['records']),'mount screenshots; wrote optional lesson.')
