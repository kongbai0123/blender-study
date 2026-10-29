"""Build challenge v009 from v008 and frozen GUI evidence, protecting file-browser privacy."""
from pathlib import Path
from hashlib import sha256
import argparse,copy,json,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'learning/web/challenges/challenges-v008.json'
SOURCE_HASH='8e427536a604d1867a73bb1d7bcf0b2c2572110edd5066d2f0fed68c57c0094c'
OUT=ROOT/'learning/web/challenges/challenges-v009.json';WEB=ROOT/'learning/web/challenges'
CAD=('learning/lesson11_cad_thread_optional_steps_v001.json','446bc2fad2630e47a9a547baf338b43eb7b1da31eb9de3ac74db9a5ed6c8890b')
CAD_SCREW=('learning/lesson11_cad_detached_screw_optional_steps_v001.json','4e3dfac6c5f1f7977896d294d3e8c97522c0b0fefa7e178feab381f3560aa82c')
CAD_RECOVERY=('learning/lesson11_cad_tool_recovery_optional_steps_v001.json','3049c4e184be12305a0efe1866dbd73a4376eec63aab2e252d42cafcc98bc2b9')
STL=('learning/lesson11_stl_export_optional_steps_v002.json','012952c6764ef6c7ef6dd5a410a617390f0fd7cb194a2630963d00fdeb9a7b40')
def sha(path):return sha256(path.read_bytes()).hexdigest()
def checked(rel,digest):
 p=(ROOT/rel).resolve();p.relative_to(ROOT)
 if sha(p)!=digest:raise ValueError('source hash changed: '+rel)
 return p
def load(ref):return json.loads(checked(*ref).read_text(encoding='utf8'))
def picture(path,digest,name,private=False):
 source=checked(path,digest)
 if private:return {'path':path,'sha256':digest}
 if not re.fullmatch(r'[a-z0-9-]+\.png',name):raise ValueError('bad asset name')
 dest=WEB/name
 if dest.exists() and sha(dest)!=digest:raise FileExistsError(dest)
 if not dest.exists():dest.write_bytes(source.read_bytes())
 return {'path':'/challenges/'+name,'sha256':digest}
def steps(doc,prefix,private_dialogs=False):
 out=[]
 for i,s in enumerate(doc['steps'],1):
  raw=s['screenshot'];private=private_dialogs and '-options.png' in raw['path'].lower()
  photo=picture(raw['path'],raw['sha256'],f'{prefix}-{i:02}.png',private)
  reading=s['programReadback'];reading=reading if isinstance(reading,str) else json.dumps(reading,ensure_ascii=False,separators=(',',':'))
  limits=list(doc['limitations'])
  if private:limits.append('此原圖含本機檔案瀏覽器路徑與個人捷徑，僅供本機查閱；公開版若未收錄不顯示。')
  out.append({'id':s['id'],'goal':s['goal'],'context':s['context'],'operation':[s['operation']],'success':s['visibleConfirmation'],'readings':[reading],'limits':limits,'screenshot':photo})
 return out
def version(label,path,digest):checked(path,digest);return {'label':label,'path':path,'sha256':digest}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--curriculum',required=True);parser.add_argument('--curriculum-sha',required=True);args=parser.parse_args()
 if OUT.exists():raise FileExistsError(OUT)
 if sha(SOURCE)!=SOURCE_HASH:raise ValueError('v008 source changed')
 checked(args.curriculum,args.curriculum_sha)
 cad=load(CAD);screw=load(CAD_SCREW);stl=load(STL);recovery=load(CAD_RECOVERY);csteps=steps(cad,'cad-thread-v001');screwsteps=steps(screw,'cad-screw-v001');ssteps=steps(stl,'chapter11-stl-v002');rsteps=steps(recovery,'cad-recovery-v001')
 if [len(csteps),len(screwsteps),len(ssteps),len(rsteps)]!=[16,12,44,7]:raise ValueError('step count changed')
 csteps[12]['success']='畫面標註基邊 0.8 mm、草圖 Fully defined；尖點 X 約 5.97047 mm 為獨立幾何讀值，不是本圖直接顯示。'
 csteps[12]['limits'].append('尖點 X 約 5.97047 mm 為獨立幾何讀值，不是本圖直接顯示。')
 screwsteps[5]['limits'].append('此原圖中灰色面是重疊且未隱藏的原 CAD Body；副本零面來自程式讀值，不可只憑圖確認刪面。')
 for s in screwsteps[8:11]:s['limits'].append('視角過近無法辨認完整螺旋；另以第 12 步的完整視角觀察，仍不能推定可列印。')
 data=copy.deepcopy(json.loads(SOURCE.read_text(encoding='utf8')))
 first=next(c for c in data['chapters'] if c['chapterId']=='ch01')
 graphic1={'path':'/challenges/box-lid-identification-drawing-v001.svg','title':'原盒、蓋板與下方環形唇邊工程目標圖','sha256':'26da9f1187fd9b8dbb8c08d1d968803ac4f72eb1d3b2497047dc7c8a2478fd12'}
 checked('learning/web/challenges/'+graphic1['path'].rsplit('/',1)[1],graphic1['sha256'])
 first['drawing']=graphic1;first['drawingStatus']='依實際原盒／原蓋網格投影及截線製作的工程目標參照，不是 Blender 操作畫面或學員模型；間隙僅為名義試驗值。'
 fourth=next(c for c in data['chapters'] if c['chapterId']=='ch04')
 graphic4={'path':'/challenges/station-render-drawing-v001.svg','title':'訊號站渲染練習工程參照圖','sha256':'c158c22edf55faac39ca301869958565e8ccbd617932a96650f649d782a7d85c'}
 checked('learning/web/challenges/'+graphic4['path'].rsplit('/',1)[1],graphic4['sha256'])
 fourth['drawing']=graphic4;fourth['drawingStatus']='依既有訊號站真實網格生成的各物件正投影凸包，非完整標準隱線；單位為 m，Ground 零厚度，供渲染練習，非 3D 列印圖。'
 ch=next(c for c in data['chapters'] if c['chapterId']=='ch11')
 cad_graphic={'path':'/challenges/cad-thread-constraint-drawing-v001.svg','title':'CAD Sketcher 兩個約束截面狀態','description':'依 0.6 還原及 0.8 已存場景的實際 XY 頂點與約束製圖；兩者是截面高度而非螺距，未製作 XZ 螺旋或 3D 實體。','sha256':'243f81c9b74d2cc290b2ad69613482018d6bd1286a053d27a197acb0cbe72db6'}
 checked('learning/web/challenges/cad-thread-constraint-drawing-v001.svg',cad_graphic['sha256']);ch['supplementalDrawings'].insert(0,cad_graphic)
 cad_demo={'title':'CAD Sketcher 約束截面（16 步）','section':'11-18','description':'獨立 Blender GUI 建立 XY 牙型截面，兩個 Distance、Equal、Vertical 與固定點形成 DoF 0；0.6/0.8 mm 是截面高度，不是螺距。此示範尚未建立 XZ 螺旋或 3D 實體。','sourceVersions':[version('0.6 mm 中間基準',cad['startingScene']['path'],cad['startingScene']['sha256'])],'steps':csteps}
 screw_demo={'title':'CAD 副本轉網格與 Screw 開口牙（12 步）','section':'11-19','description':'另存的 CAD 草圖生成物複製後轉為獨立 mesh、旋轉至 XZ 再使用 Screw；原草圖仍在，但該網格不跟 CAD 參數連動。六條非流形邊為開口端，不能視為可列印實體。','startingScene':screw['startingScene'],'sourceVersions':[version('0.6 草圖來源',screw['startingScene']['path'],screw['startingScene']['sha256']),version('獨立開口牙草案',screw['demonstrationScene']['path'],screw['demonstrationScene']['sha256'])],'steps':screwsteps}
 versions=[]
 for item in stl['items']:
  versions.append(version(item['title']+' 來源',item['sourceScene'],item['sourceSha256']))
  versions.append(version(item['title']+' STL',item['stl'],item['stlSha256']))
 stl_demo={'title':'六件 STL 匯出、修訂與重匯入（44 步）','section':'11-17','description':'分件 GUI 匯出並重匯入；有重複面的兩件先另存三角化修訂，再匯出。STL 保留世界座標且無內嵌單位；三角化改變部分非平面面片，有限抽樣不證明完整等同性或實體配合。檔案視窗使用程式隱藏系統側欄並填入公共暫存路徑的獨立 Blender 實拍；圖片未修改。','sourceVersions':versions,'steps':ssteps}
 recovery_demo={'title':'CAD 重開警告後重新進入與選取探測（7 步）','section':'11-20','description':'在隔離環境重新進入草圖、選回 Select、選取線並改回尺寸後另存重開；視角由程式調整。僅驗證此檔案與這些操作，並未修復警告根因或證明所有工具正常。','startingScene':recovery['startingScene'],'sourceVersions':[version('0.6 草圖來源',recovery['startingScene']['path'],recovery['startingScene']['sha256']),version('探測保存副本',recovery['demonstrationScene']['path'],recovery['demonstrationScene']['sha256'])],'steps':rsteps}
 ch['demonstrations']=[cad_demo,screw_demo,stl_demo,recovery_demo,*ch['demonstrations']]
 ch['sourceSteps'].extend([{'chapterId':'ch11','sectionId':'11-17','label':'六件 STL 匯出與重匯入'},{'chapterId':'ch11','sectionId':'11-18','label':'CAD Sketcher 約束截面'},{'chapterId':'ch11','sectionId':'11-19','label':'CAD 副本與 Screw 開口牙'}])
 ch['sourceSteps'].append({'chapterId':'ch11','sectionId':'11-20','label':'CAD 重開警告後的有限恢復探測'})
 ch['requirements'].append('辨認 CAD 的 XY 約束截面與原生 mesh 外牙是不同操作；0.6／0.8 mm 不是螺距。')
 ch['limitations'].append('兩件 STL 經三角化修訂且可能改變非平面表面；重匯入與有限抽樣不代表實際列印、旋合或幾何完全等同。')
 data['version']='v009';data['source']={'path':args.curriculum,'sha256':args.curriculum_sha};data['previousVersion']={'path':'learning/web/challenges/challenges-v008.json','sha256':SOURCE_HASH}
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');print(sha(OUT))
if __name__=='__main__':main()
