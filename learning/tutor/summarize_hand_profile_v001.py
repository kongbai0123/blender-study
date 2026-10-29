"""Hash-verify actual GUI profile and follow-on thread; write safe lesson."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def collect(relative,scene):
    e=root/relative; run=read(e/'run.json'); status=read(e/'runner-status.json'); audit=read(e/'independent-audit-v001.json'); file=e/'demo-files'/scene
    if status['status']!='completed' or audit['sceneSha256']!=sha(file):raise ValueError('run/audit/scene mismatch')
    records=[]
    for r in run['records']:
        p=e/r['file'];h=sha(p)
        if h!=r['sha256']:raise ValueError('image hash mismatch '+str(p))
        try:obs=json.loads(r['observed'])
        except (ValueError,TypeError):obs=None
        records.append({'sequence':r['seq'],'slug':r['slug'],'image':p.relative_to(root).as_posix(),'sha256':h,'observed':obs})
    filtered={k:v for k,v in audit.items() if k!='triangleAreasMm2InTessellationOrder'}
    safe={'blenderVersion':run['blender'],'scene':file.relative_to(root).as_posix(),'sceneSha256':sha(file),
          'scenario':'learning/tutor/scenarios/'+Path(run['scenario']).name,'scenarioSha256':sha(root/'learning/tutor/scenarios'/Path(run['scenario']).name),
          'runStatus':status['status'],'workspacesSnapshotUnchanged':status['workspacesUnchanged'],
          'independentAudit':filtered,'records':records,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedStrength':None,'qualifiedClearance':None,
          'notes':['GUI 事件建構頂點和邊；Python 僅準備場景隱藏參考、核驗讀值及填檔案欄位。',
                   '原始 runner-status 含私人 Windows Recent，請勿直接上傳；本摘要不含。',
                   '畫面與數值是數位幾何示範，非 ISO、實體列印、強度或配合合格。']}
    (e/'safe-summary-v001.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return safe
v004=collect('learning/evidence/08/2026-10-28-external-thread-hand-profile-gui-v004','u11_hand_profile_v001.blend')
v005=collect('learning/evidence/08/2026-10-28-external-thread-hand-profile-gui-v005','u11_hand_profile_v001.blend')
thread=collect('learning/evidence/08/2026-10-28-external-thread-from-hand-profile-gui-v001','u11_hand_thread_draft_v001.blend')
if v004['independentAudit']['worldVerticesMm']!=v005['independentAudit']['worldVerticesMm']:raise ValueError('two profile rehearsals differ')
if not v004['independentAudit']['connectedTriangle'] or not v005['independentAudit']['connectedTriangle']:raise ValueError('not triangle edge loop')

# Each tuple: objective, concrete GUI operation, precondition, actual image, readback.
content=[
('新增平面','開啟參考場景複本；F3 搜尋 Add Plane，再以 F2 命名 Thread_Hand_Profile。','單位為毫米；程式隱藏參考盒體，未建立網格。','平面因預設尺寸太大而超出畫面；N 側欄顯示約 2000 × 2000 mm。','程式讀回 4 點、4 邊、1 面；此平面接下來會合併成單點。'),
('將平面合併為一點','Tab 進入 Edit Mode，按 1 切換頂點、A 全選，F3 搜尋 Merge at Center，再按 A 確認選到單點；數字鍵盤 1 看前視圖。','須在頂點選取模式，否則合併後可能沒有選中點。','前視圖中平面變成單個點，尺度較遠。','程式讀回單點 (0,0,0)，0 邊、0 面；選取數為 1。'),
('定位第一點','按 G、X、輸入 4.8mm、Enter，將單點移至 X=4.8 mm。','先確認只有該點被選取。','N 側欄顯示 X 4.8、Y 0、Z 0 mm；單點在原圖中較小。','程式讀回約 (4.80000019,0,0) mm。'),
('擠出第二點','按 E、X、輸入 1.2mm、Enter，再按 G、Z、輸入 0.3mm、Enter。','第一點保持選取；輸入的是相對位移。','N 側欄顯示選中點 X 6、Y 0、Z 0.3 mm；畫面中的線段較小。','程式讀回兩點、一邊、0 面；第二點約 (6,0,0.30000001) mm。'),
('擠出第三點','按 E、X、輸入 -1.2mm、Enter，再按 G、Z、輸入 0.3mm、Enter。','確認僅第二點被選取；第三點位移也是相對值。','N 側欄顯示選中點 X 4.8、Y 0、Z 0.6 mm；線段較小。','程式讀回三點、兩邊、0 面；第三點約 (4.80000019,0,0.60000002) mm。'),
('全選並放大','按 A 選取全部，F3 搜尋 Frame Selected，調整視圖。','仍在 Edit Mode 頂點模式。','可看到放大的 V 形兩條邊；N 欄是多點中位數，不是單點座標。','讀回 3 點、2 邊、0 面；此時尚未閉合第三邊。'),
('補上閉合邊','保持三點全選，按 F 暫時建立三角面。','三點均已選中。','前視圖中三角區域被填滿。','讀回 3 點、3 邊、1 面；此面只是建立閉合邊的中間步驟。'),
('刪除面保留輪廓','F3 搜尋 Only Faces；只刪除面，保留三條邊。','操作於剛建立的三角面；若看不到 Only Faces，先確認 Edit Mode。','放大後可見三角閉合邊線；未選取時邊線為深色。','讀回 3 點、3 邊、0 面；這是邊輪廓，不是已封閉的實體。'),
('近景核對第一點','Alt+A 取消選取，在放大輪廓左下角單選第一點。','保持頂點選取模式；依自己畫面選點，不套用示範座標。','輪廓放大，N 側欄可見 X 4.8、Y 0、Z 0 mm。','程式確認恰好選中第一點 (4.80000019,0,0) mm。'),
('近景核對第二點','Alt+A 取消選取，單選輪廓右側牙頂。','保持頂點選取模式。','輪廓放大，N 側欄可見 X 6、Y 0、Z 0.3 mm。','程式確認恰好選中第二點 (6,0,0.30000001) mm。'),
('近景核對第三點','Alt+A 取消選取，單選輪廓左上角。','保持頂點選取模式。','輪廓放大，N 側欄可見 X 4.8、Y 0、Z 0.6 mm。','程式確認恰好選中第三點 (4.80000019,0,0.60000002) mm。'),
('另存輪廓','Tab 回物件模式，使用 Save As 另存 u11_hand_profile_v001.blend。','本示範的路徑與檔名由程式填入檔案對話框；保留參考原檔。','另存後仍可看見輪廓物件；此圖不是檔案對話框截圖。','另存後讀回 3 點、3 邊、0 面；示範檔 SHA-256 列於 demonstrationSceneSha256。'),
('重開並獨立核對','重新開啟另存檔；另以背景 Blender 讀回頂點與邊連接。','重開對話框路徑與檔名由程式填入；未更新學員進度。','重新開啟後可見輪廓物件。','獨立重讀：3 點、3 邊、0 面，每點度數 2；相對名義座標最大差約 1.91×10⁻⁷ mm。'),
]
assert len(content)==len(v005['records'])==13
steps=[]
for i,(item,r) in enumerate(zip(content,v005['records']),1):
    goal,op,context,visible,readback=item
    steps.append({'id':f'11-hand-profile-{i:02}','goal':goal,'operation':op,'context':context,'visibleConfirmation':visible,'programReadback':readback,
                  'screenshot':{'path':r['image'],'sha256':r['sha256']}})
lesson={'schemaVersion':1,'title':'第 11 章選修：手工繪製三角牙型邊輪廓','scope':'以獨立 Blender 實際 GUI 逐點建模；未更新學員進度。',
 'sourceScene':'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend',
 'sourceSha256':'9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f',
 'demonstrationScene':v005['scene'],'demonstrationSceneSha256':v005['sceneSha256'],
 'followOnActualProfileScene':v004['scene'],'followOnActualProfileSceneSha256':v004['sceneSha256'],
 'followOnThreadScene':thread['scene'],'followOnThreadSceneSha256':thread['sceneSha256'],
 'limitations':['此為無幾何約束的 Blender mesh 邊輪廓，不是 CAD Sketcher 約束草圖；數值依名義設計輸入。',
  '這 13 張畫面來自 GUI v005 重複試作；後續完整外牙實際使用另次 GUI v004 輪廓，兩次獨立讀值的頂點座標一致，不是同一場次。',
  '本輪廓是三角草案，不宣稱 ISO 螺紋；全程建點與邊為 GUI，場景隱藏、讀值與檔案欄位由程式處理。',
  '只有三條邊不代表已封閉的實體；Screw、封端和與芯柱聯集需另行完成與檢查。',
  '材料、列印、量測、配合、合格間隙及強度均待定。'],
 'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,'steps':steps}
out=root/'learning/lesson11_hand_profile_optional_steps_v001.json'
if out.exists():raise FileExistsError('Preserve lesson version')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('13-step lesson SHA-256',sha(out),'profile',v005['sceneSha256'],'follow-on thread',thread['sceneSha256'])
