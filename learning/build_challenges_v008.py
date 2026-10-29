"""Build v008 from frozen instructional records; preserve v007 and learner progress."""
from pathlib import Path
from hashlib import sha256
import argparse,copy,json,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'learning/web/challenges/challenges-v007.json'
SOURCE_SHA='dca05a09cbca482c426bba3aaa606a1142105f78f68eacda1fc1ac57bdfa6721'
OUTPUT=ROOT/'learning/web/challenges/challenges-v008.json'
WEB=ROOT/'learning/web/challenges'
RECORDS={
 'profile':('learning/lesson11_hand_profile_optional_steps_v001.json','20616cfe3ff36bfd78ddaa479adc6aca3321d772a1b441e665768870e5648ef1'),
 'thread':('learning/lesson11_hand_thread_optional_steps_v002.json','1627aef1d6c8ddc0ec311136e7207ee8c87de6696d68ef44aceebfb059d567bd'),
 'cap':('learning/lesson11_side_cap_optional_steps_v002.json','3f043de3151a7723015ccbb24f78d1745d542cabbbbaafd5a63893bb3342c633'),
 'hardware':('learning/hardware-selection-v001.json','f6b3f32cff1a6e7a0396353960a81087055859e4b399751e4991362b13f4c6dc')}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def checked(rel,digest):
 p=(ROOT/rel).resolve();p.relative_to(ROOT)
 if sha(p)!=digest:raise ValueError('hash mismatch '+rel)
 return p
def load(rel,digest):return json.loads(checked(rel,digest).read_text(encoding='utf8'))
def version(label,path,digest):checked(path,digest);return {'label':label,'path':path,'sha256':digest}
def images_and_steps(doc,prefix):
 result=[]
 for i,s in enumerate(doc['steps'],1):
  pic=s['screenshot'];expected=pic['sha256'];src=checked(pic['path'],expected);name=f'{prefix}-{i:02}.png'
  if not re.fullmatch(r'[a-z0-9-]+\.png',name):raise ValueError('bad image filename')
  dest=WEB/name
  if dest.exists() and sha(dest)!=expected:raise FileExistsError(dest)
  if not dest.exists():dest.write_bytes(src.read_bytes())
  result.append({'id':s['id'],'goal':s['goal'],'context':s['context'],'operation':[s['operation']],'success':s['visibleConfirmation'],'readings':[s['programReadback']],'limits':doc['limitations'],'screenshot':{'path':'/challenges/'+name,'sha256':expected}})
 return result
def hardware_info(h):
 if h['status']!='selected-for-draft-design-not-physically-qualified':raise ValueError('unexpected hardware status')
 insert,screw,draft=h['insert'],h['screw'],h['designDraft']
 if insert['partNumber']!='RX-M3x5.7' or screw['partNumber']!='001.16.342':raise ValueError('hardware selection changed')
 return {'title':'已選五金與試驗尺寸','description':'以下是已選型與原廠數據，不代表已購買、已實印或強度／配合合格。平面上蓋固定與盒側自訂牙帽是不同分支。','items':[
  {'label':'熱熔螺母（已選）','value':f"ruthex {insert['partNumber']}，M3，長 {insert['lengthMm']} mm，最大外徑 {insert['outerMajorDiameterMm']} mm，尖端 {insert['tipDiameterMm']} mm"},
  {'label':'螺母孔（原廠建議）','value':f"孔徑 {insert['manufacturerRecommendedHoleDiameterMm']} mm；最低深度 {insert['manufacturerMinimumHoleDepthMm']} mm（L + 1）；最小周壁 W {insert['manufacturerMinimumWallWMm']} mm"},
  {'label':'螺絲（已選）','value':f"ETTINGER {screw['partNumber']}，ISO 4762 M3×{screw['underHeadLengthMm']}，{screw['material']}；頭徑 {screw['headDiameterMm']}、頭高 {screw['headHeightMm']}、內六角 {screw['hexKeyMm']} mm"},
  {'label':'小盒平面蓋（本案試驗值）','value':f"蓋板穿孔名義 {draft['coverClearanceHoleNominalDiameterMm']} mm；{screw['quantityForDraft']} 處。孔徑與列印配合未驗證。"},
  {'label':'待定及未驗證','value':'塑膠材料、安裝溫度、扭矩、實際量測、列印、安裝、試配及強度均待定。'}],
  'limitations':'原廠孔徑／深度／周壁為起始依據，不是 FDM 列印或配合合格證明；自訂穿孔與側帽間隙均為試驗值。',
  'sources':[{'title':'ruthex 原廠產品及尺寸','url':insert['source']},{'title':'ETTINGER 原廠螺絲資料','url':screw['source']}],
  'recordPath':'learning/hardware-selection-v001.json','recordSha256':RECORDS['hardware'][1]}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--curriculum',required=True);parser.add_argument('--curriculum-sha',required=True);parser.add_argument('--boss-steps',required=True);parser.add_argument('--boss-sha',required=True);args=parser.parse_args()
 if OUTPUT.exists():raise FileExistsError(OUTPUT)
 if sha(SOURCE)!=SOURCE_SHA:raise ValueError('v007 source changed')
 checked(args.curriculum,args.curriculum_sha)
 profile,thread,cap,hardware=(load(*RECORDS[k]) for k in ('profile','thread','cap','hardware'))
 boss=load(args.boss_steps,args.boss_sha)
 profile_steps=images_and_steps(profile,'hand-profile-v005');thread_steps=images_and_steps(thread,'hand-thread-v001');cap_steps=images_and_steps(cap,'side-cap-v002');boss_steps=images_and_steps(boss,'metal-box-v001')
 if [len(profile_steps),len(thread_steps),len(cap_steps),len(boss_steps)]!=[13,14,17,15]:raise ValueError('unexpected step count')
 data=copy.deepcopy(json.loads(SOURCE.read_text(encoding='utf8')));ch=next(c for c in data['chapters'] if c['chapterId']=='ch11')
 profile_demo={'title':'手工三點輪廓（13 步）','section':'11-13','description':'獨立 Blender GUI 逐點建立無約束 mesh 邊輪廓，非 CAD 約束草圖。圖片是 v005 另次實作；後續外牙與工程圖使用 v004，數值一致但非同一次執行。','startingScene':{'path':profile['sourceScene'],'sha256':profile['sourceSha256']},'sourceVersions':[version('v005 實拍輪廓',profile['demonstrationScene'],profile['demonstrationSceneSha256']),version('v004 續作輪廓',profile['followOnActualProfileScene'],profile['followOnActualProfileSceneSha256'])],'steps':profile_steps}
 thread_demo={'title':'由手工輪廓續作外牙（14 步）','section':'11-14','description':'以 v004 GUI 手工輪廓續作 Screw、端面與芯柱；尺寸及局部網格檢查不是 ISO 或實體配合合格證明。','startingScene':thread['startingScene'],'sourceVersions':[version('GUI 輪廓',thread['sourceScene'],thread['sourceSha256']),version('手工續作外牙',thread['demonstrationScene'],thread['demonstrationSceneSha256'])],'steps':thread_steps}
 cap_demo={'title':'盒側保護蓋與試驗間隙（17 步）','section':'11-15','description':'兩階段使用程式預建刀具及毛坯，再以獨立 Blender GUI 差集、另存與重開；保留原平面上蓋。徑向 0.2、直徑差 0.4 及中心軸向端隙 0.2 mm 均為試驗值。端牙局部改變，有限射線與離散旋轉不等於實體旋合。','startingScene':cap['startingScenes'][0],'sourceVersions':[version('內牙刀具起始場景',cap['startingScenes'][0]['path'],cap['startingScenes'][0]['sha256']),version('端隙刀具起始場景',cap['startingScenes'][1]['path'],cap['startingScenes'][1]['sha256']),version('端隙側帽 v002',cap['scene'],cap['sceneSha256'])],'steps':cap_steps}
 boss_demo={'title':boss['title'],'section':'11-16','description':boss['scope']+' 柱、肋及孔刀具由程式預建；布林、另存與重開是 GUI 操作。','startingScene':boss['startingScene'],'sourceVersions':[version('原盒及上蓋',boss['upstreamReference']['path'],boss['upstreamReference']['sha256']),version('GUI 跟做起始副本',boss['sourceScene'],boss['sourceSha256']),version('四柱蓋孔結果',boss['demonstrationScene'],boss['demonstrationSceneSha256'])],'steps':boss_steps}
 old=ch['demonstrations'];old[0]['historical']=True;old[0]['title']='歷史參照：程式預建輪廓的修訂外牙（14 步）'
 ch['demonstrations']=[profile_demo,thread_demo,cap_demo,boss_demo,*old]
 for section,label in [('11-13','手工三點輪廓'),('11-14','手工輪廓續作外牙'),('11-15','盒側保護蓋'),('11-16','已選五金與平面蓋')]:ch['sourceSteps'].append({'chapterId':'ch11','sectionId':section,'label':label})
 profile_svg={'path':'/challenges/manual-thread-profile-drawing-v001.svg','title':'手工牙型輪廓工程題圖','description':'源自 GUI v004 實際網格的無約束三點輪廓，與 13 步 v005 為不同場次。','sha256':'989e11e99b8d6ba10c4658aa7b5ce40c02b856d66fc05d955d73a3c39d557c7e'}
 cap_svg={'path':'/challenges/side-thread-cap-drawing-v002.svg','title':'側向保護蓋 v002 工程題圖','sha256':'a4f44ea14b7f4a9cbaf42dc112c35864683d2dbc872f64211aed2c187a0d1880'}
 m3_svg={'path':'/challenges/m3-four-boss-layout-drawing-v001.svg','title':'四柱與平面上蓋孔工程題圖','description':'已選金屬零件僅列原廠名義資料，未建金屬實體；蓋孔 Ø3.4 為試驗值，實體安裝及合格待驗。','sha256':'1c64559e52a5d59d616aa629c482b2e7bcfba9d5289c91af90272891601337e5'}
 for graphic in (profile_svg,cap_svg,m3_svg):checked('learning/web/challenges/'+graphic['path'].rsplit('/',1)[1],graphic['sha256'])
 prior=ch['drawing'];prior['description']=ch['drawingStatus'];ch['drawing']=cap_svg;ch['supplementalDrawings']=[m3_svg,prior,profile_svg,*ch['supplementalDrawings']]
 ch['drawingStatus']='側向保護蓋 v002 的三視圖與實際網格剖切；不是既有平面上蓋或完整標準隱線圖，徑向和軸向間隙均為試驗值。'
 ch['screenshot']={**cap_steps[-1]['screenshot'],'caption':'獨立 Blender 的保護蓋內部視角；局部影像不能證明完整牙形或實體旋合。'}
 ch['requirements'][1]='依序觀察手工牙型、續作外牙、盒側保護蓋與已選金屬五金的平面蓋分支。'
 ch['requirements'][2]='明列選型、原廠建議與自訂試驗值；塑膠材料、列印及實體試配維持待定。'
 ch['hardwareInformation']=hardware_info(hardware)
 ch['evidenceStatus']='獨立 Blender 示範與局部數位檢查，不代表學員完成或實體合格；工程題圖與操作原圖分開標示。'
 data['version']='v008';data['source']={'path':args.curriculum,'sha256':args.curriculum_sha};data['previousVersion']={'path':'learning/web/challenges/challenges-v007.json','sha256':SOURCE_SHA}
 OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(sha(OUTPUT))
if __name__=='__main__':main()
