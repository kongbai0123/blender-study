"""Publish-safe metadata and step lesson for program-prepared four-boss tools."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def collect(relative,scene,auditname):
 e=root/relative;run=read(e/'run.json');status=read(e/'runner-status.json');audit=read(e/auditname);f=e/'demo-files'/scene
 if status['status']!='completed' or audit['sceneSha256']!=sha(f):raise ValueError('status or scene hash differs')
 records=[]
 for r in run['records']:
  p=e/r['file'];h=sha(p)
  if h!=r['sha256']:raise ValueError('screenshot hash mismatch')
  try:obs=json.loads(r['observed'])
  except (ValueError,TypeError):obs=None
  records.append({'seq':r['seq'],'slug':r['slug'],'image':p.relative_to(root).as_posix(),'sha256':h,'observed':obs})
 if 'body' in audit:
  for name in ('body','lid'):
   audit[name].pop('allTriangleAreasMm2',None);audit[name].pop('allTriangleAltitudesMm',None)
 safe={'scene':f.relative_to(root).as_posix(),'sceneSha256':sha(f),'blenderVersion':run['blender'],
       'runStatus':status['status'],'workspacesSnapshotUnchanged':status['workspacesUnchanged'],
       'audit':audit,'records':records,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,
       'notes':['工具由 Python 預建；GUI 執行 Boolean 操作、另存及重開。','原始 runner-status 含 Windows Recent 私人路徑，不可原樣上傳。',
                '量測是數位局部抽樣；非實體量測、配合、ISO 螺紋、列印或結構合格。']}
 (e/'safe-summary-v001.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return safe
start=collect('learning/evidence/08/2026-10-28-four-insert-boss-start-gui-v001','u11_four_insert_boss_start_v001.blend','independent-audit-v001.json')
result=collect('learning/evidence/08/2026-10-28-four-insert-boss-gui-v001','u11_four_insert_boss_box_v001.blend','independent-audit-v002.json')
cmp=read(root/'learning/evidence/08/2026-10-28-four-insert-boss-start-gui-v001/tool-comparison-v001.json')
if not cmp['allEqual'] or cmp['startSha256']!=start['sceneSha256'] or cmp['resultSha256']!=result['sceneSha256']:raise ValueError('tool mismatch')
content=[
('開啟可跟做副本','開啟另存的起始檔，確認 Body 可見、Lid 與五組工具隱藏。','柱、肋及刀具由 Python 預建，不是本單元 GUI 從零建模；起始副本尚未做布林。','看到開口盒體；工具因隱藏而不可見。','獨立驗證 Body 和 Lid 的面頂點指紋與原檔一致；五個工具各含 4 個分離構件。'),
('預覽四柱聯集','選 Body，F3 搜尋 Add Boolean Modifier，選 Union、Exact，Object 選 zz_Boss_Pillars。','以起始檔中預建的四柱工具操作；中心為 X±21、Y±11 mm。','修改器顯示 Union／Exact；物件欄名稱可能因欄寬截斷。','程式讀回 UNION、EXACT 與 zz_Boss_Pillars。'),
('套用四柱聯集','在 Boolean 修改器選單按 Apply。','確認正確工具後套用；預建柱底 Z=-13.5、頂 Z=15 mm。','可見盒內四柱，但部分柱體下部被盒壁遮住。','Body 讀回 272 點、148 面、1 連通體、非流形邊 0。'),
('預覽 X 向連壁肋','選 Body，新增加 Boolean，選 Union／Exact，Object 選 zz_Boss_Ribs_X。','每個柱體的 X 向肋為預建工具，頂部 Z=10 mm。','修改器顯示聯集設定；肋的局部可能受盒壁遮擋。','程式讀回 UNION、EXACT 與 zz_Boss_Ribs_X。'),
('套用 X 向肋','確認後在修改器選單按 Apply。','肋與柱、盒壁有名義重疊；仍未做強度判定。','盒內仍可見柱體；此角度未能顯出每條肋。','Body 讀回 304 點、164 面、1 連通體、非流形邊 0。'),
('預覽 Y 向連壁肋','選 Body，新增加 Boolean，選 Union／Exact，Object 選 zz_Boss_Ribs_Y。','預建工具為四條 Y 向肋，與柱及側壁相交。','修改器顯示聯集設定；工具名稱可能截斷。','程式讀回 UNION、EXACT 與 zz_Boss_Ribs_Y。'),
('套用 Y 向肋','確認後在修改器選單按 Apply。','肋厚為名義 2 mm、頂面 Z=10 mm。','盒內可見四柱，部分肋體被遮擋。','Body 讀回 336 點、180 面、1 連通體、非流形邊 0。'),
('預覽柱孔切割','選 Body，新增加 Boolean，選 Difference／Exact，Object 選 zz_Boss_Pilot_Tools。','四個預建切割工具名義 Ø4 mm，底 Z=6、頂延伸至 15.5 mm 以穿過柱頂。','修改器顯示 Difference／Exact；可能不能由預覽辨認孔深。','程式讀回 DIFFERENCE、EXACT 與 zz_Boss_Pilot_Tools。'),
('套用四個柱盲孔','確認後在修改器選單按 Apply。','柱頂 Z=15、孔底 Z=6，名義孔深 9 mm。','畫面可看到柱頂孔；前側部分受盒壁遮擋。','Body 讀回 592 點、316 面、1 連通體、非流形邊 0；獨立抽樣四孔底 Z≈6 mm。'),
('顯示既有上蓋','在 Outliner 找到 Lid，點眼睛顯示原上蓋。','上蓋位於原本名義關閉位置；不要移動它。','畫面顯示上蓋並遮住盒內柱體。','劇本以 hide_get() 確認上蓋顯示；尚未打蓋孔。'),
('預覽蓋穿孔','選 Lid，新增加 Boolean，選 Difference／Exact，Object 選 zz_Boss_Lid_Tools。','名義 Ø3.4 mm 為本案試驗值，不是已驗證公差。','可見上蓋及布林預覽；名稱可能因欄寬截斷。','程式讀回 DIFFERENCE、EXACT 與 zz_Boss_Lid_Tools。'),
('套用蓋穿孔','確認後在修改器選單按 Apply。','刀具穿過蓋板上下表面；未建真實螺絲或熱熔螺母。','上蓋畫面可看到四個孔。','Lid 讀回 280 點、154 面、1 連通體、非流形邊 0；四孔軸向射線無命中。'),
('聚焦觀察盒體','選 Body，F3 搜尋 Frame Selected 並調整視角。','圖像可能從盒底方向觀看，需配合之前上蓋及柱孔圖片。','此實拍主要顯示盒體外底，無法看見所有內部孔肋。','Body 外框約 60 × 40 × 30 mm；此圖不證明內部尺寸。'),
('另存新版本','File > Save As，另存新場景，保留原始盒與起始檔。','示範檔案視窗路徑及檔名由程式填入。','另存後保留盒體畫面，這不是檔案對話框截圖。','示範檔 SHA-256 見 demonstrationSceneSha256；實體結果未填。'),
('重開並獨立核對','重開另存的新檔，以另一個 Blender 讀回網格與局部射線。','檔案欄位由程式填入；重新開啟不等於學員完成。','重開畫面從盒底視角觀看，四孔及肋並非都可見。','Body/Lid 均 1 連通體、非流形邊 0、BVH 候選 0；四孔在各自主軸和四個徑向抽樣，並不保證所有方向或實體尺寸。'),
]
assert len(content)==len(result['records'])==15
steps=[]
for i,(item,r) in enumerate(zip(content,result['records']),1):
 goal,op,ctx,vis,readback=item
 steps.append({'id':f'11-four-inserts-{i:02}','goal':goal,'operation':op,'context':ctx,'visibleConfirmation':vis,
               'programReadback':readback,'screenshot':{'path':r['image'],'sha256':r['sha256']}})
lesson={'schemaVersion':1,'title':'第 11 章選修：四熱熔螺母柱與蓋孔幾何草案',
 'scope':'原盒與蓋副本上的數位示範；不更新學員進度，實體列印、量測與試配待定。',
 'status':'數位幾何草案，尚未實體驗證',
 'sourceScene':start['scene'],'sourceSha256':start['sceneSha256'],
 'startingScene':{'path':start['scene'],'sha256':start['sceneSha256'],
  'verification':'learning/evidence/08/2026-10-28-four-insert-boss-start-gui-v001/independent-audit-v001.json',
  'construction':'程式預備五組工具；原始 Body/Lid 尚未做布林，已另存與重開核對。'},
 'upstreamReference':{'path':'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend',
  'sha256':'ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'},
 'demonstrationScene':result['scene'],'demonstrationSceneSha256':result['sceneSha256'],
 'hardware':{'insert':'Ruthex RX-M3x5.7','insertLengthMm':5.7,'insertOuterDiameterMm':4.6,'insertTipDiameterMm':3.9,
  'manufacturerPilotDiameterMm':4.0,'manufacturerMinimumPilotDepthMm':6.7,'manufacturerMinimumWallMm':1.6,
  'screw':'ETTINGER 001.16.342 ISO4762 M3x10 A2/AISI304','screwLengthMm':10,'headDiameterMm':5.5,'headHeightMm':3,'hexMm':2.5},
 'nominalDraft':{'centresMm':[[-21,-11],[-21,11],[21,-11],[21,11]],'pillarOuterDiameterMm':8,'pillarBottomZMm':-13.5,
  'pillarTopZMm':15,'pillarHeightMm':28.5,'floorOverlapMm':0.5,'pilotDiameterMm':4,'pilotDepthMm':9,'pilotBottomZMm':6,
  'lidHoleDiameterExperimentalMm':3.4,'ribThicknessMm':2,'ribTopZMm':10,'lidLowestZMm':11,'nominalRibVerticalBoundingGapMm':1,
  'insertTopZMm':14.8,'insertBottomZMm':9.1,'screwBottomZMm':7,'nominalScrewBottomToBlindHoleBottomMm':1,
  'headEnvelopeDiameterMm':5.5,'headEnvelopeBottomZMm':17,'headEnvelopeTopZMm':20},
 'limitations':['柱、肋與切割工具由 Python 預建；後續 Boolean、新檔及重開為隔離 Blender GUI。',
  '起始檔是另一次重演，五個工具的世界面頂點指紋與成品中的刀具一致；不得說成同一場次。',
  '四個蓋孔 3.4 mm 是我方試驗名義值，未經列印或試配，並非 ISO 已選公差或合格間隙。',
  '無螺絲與嵌件實體網格，螺絲頭為尺寸包絡，未模擬螺紋、安裝、干涉或扭矩。',
  '柱、肋和原盒的材料、製程、列印方向、熱熔與結構強度未驗證；非流形和 BVH 指標不保證無自交。',
  '32 方向壁厚與孔徑射線為特定高度的數位局部抽樣；肋與蓋間距僅靜態外框距離。',
  '末幾張畫面主要為盒底視角，孔與肋需參考第 9、12 步及讀值。'],
 'material':None,'torque':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,'steps':steps}
out=root/'learning/lesson11_four_insert_bosses_optional_steps_v001.json'
if out.exists():raise FileExistsError('choose new version')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('15 steps, lesson SHA-256',sha(out),'start SHA-256',start['sceneSha256'],'result SHA-256',result['sceneSha256'])
