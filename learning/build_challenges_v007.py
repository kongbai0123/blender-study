"""Preserve v006; add the corrected external thread and box-side GUI evidence."""
from pathlib import Path
from hashlib import sha256
import copy, json, re

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'learning/web/challenges/challenges-v006.json'
OUTPUT=ROOT/'learning/web/challenges/challenges-v007.json'
ASSETS=ROOT/'learning/web/challenges'
SRC_HASH='014ce34a25ded95cd982c0efcfb4c7a95ab582700b1f93f18968207f40a00241'
REPAIRED_HASH='73220a37067b84b8ad614ab28af9759cd2758d7213fbf69748eb17407d39c0da'
MOUNT_V001_HASH='645a1febf20f566adc36b7c15f56758dce0ee84822134984052d0d07a5cae992'
MOUNT_V002_HASH='eb3b58b3763a7922dd5afc1a83b58a3e8c85f3445353ae07f12c2cdcc1309a6a'
CURRICULUM='learning/web/engineering-curriculum-v034.json'
CURRICULUM_HASH='119432ade0437a1c1d8063ad4d4d8cb368faa4351a21da6975164b2f69dbafd5'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def checked(path,expected):
    p=ROOT/path
    if sha(p)!=expected:raise ValueError('hash mismatch: '+str(path))
    return p
def img(source,expected,name):
    if not re.fullmatch(r'[a-z0-9-]+\.png',name):raise ValueError('unsafe filename')
    src=checked(source,expected);dst=ASSETS/name
    if dst.exists() and sha(dst)!=expected:raise FileExistsError(dst)
    if not dst.exists():dst.write_bytes(src.read_bytes())
    return {'path':'/challenges/'+name,'sha256':expected}
def load(path,expected):return json.loads(checked(path,expected).read_text(encoding='utf-8'))
def steps(doc,prefix):
    output=[]
    for i,s in enumerate(doc['steps'],1):
        im=s['screenshot'];picture=img(im['path'],im['sha256'],f'{prefix}-{i:02}.png')
        output.append({'id':s['id'],'goal':s['goal'],'context':s['context'],'operation':[s['operation']],'success':s['visibleConfirmation'],'readings':[s['programReadback']],'limits':doc['limitations'],'screenshot':picture})
    return output
def scene(label,path,digest):
    checked(path,digest)
    return {'label':label,'path':path,'sha256':digest}
def main():
    if OUTPUT.exists():raise FileExistsError(OUTPUT)
    if sha(SRC)!=SRC_HASH:raise ValueError('v006 source changed')
    checked(CURRICULUM,CURRICULUM_HASH)
    checked('learning/web/challenges/box-external-thread-drawing-v003.svg','a18d1db95af220e0fda6dcc63d67f0d23c80fd8134525a68f057bd31a151f63f')
    repair=load('learning/lesson11_external_repaired_optional_steps_v001.json',REPAIRED_HASH)
    mount_old=load('learning/lesson11_external_mount_optional_steps_v001.json',MOUNT_V001_HASH)
    mount=load('learning/lesson11_external_mount_optional_steps_v002.json',MOUNT_V002_HASH)
    rsteps=steps(repair,'external-gui-v010');msteps=steps(mount,'mount-gui-v002');old_msteps=steps(mount_old,'mount-gui-v001')
    if (len(rsteps),len(msteps),len(old_msteps))!=(14,11,10):raise ValueError('incorrect step count')
    repaired={'title':'修訂外牙 GUI 幾何示範（14 步）','section':'11-11',
      'description':'三角輪廓由程式預建，其餘為獨立 Blender GUI 示範；柱芯旋轉 5.625°、高度約 4.8 mm。BVH 候選及診斷門檻下薄面數為零並不能證明無自交或可製造；非 ISO，尚未實印或試配。',
      'startingScene':repair['startingScene'], 'sourceVersions':[scene('原盒參考',repair['source']['path'],repair['source']['sha256']),scene('修訂外牙新版本',repair['demonstrationScene'],repair['demonstrationSceneSha256'])], 'steps':rsteps}
    mounted={'title':'盒側外牙接口 GUI 示範 v002（11 步）','section':'11-12',
      'description':'由程式將修訂牙條載入原盒與唇邊上蓋副本，再以獨立 Blender GUI 旋轉、移動、布林、另存及重開。保留 0.5 mm 名義嵌入並沿牙條自身 X 軸旋轉 11.25°；仍有細長三角面，最小三角高約 0.001126 mm，三角高不是物理壁厚。原內牙試塊不是已匹配對件；局部射線與上蓋靜態外框距離不是完整干涉或實體試配。',
      'sourceVersions':[scene('原盒及上蓋',mount['sourceScene'],mount['sourceSha256']),scene('修訂牙條',mount['threadScene'],mount['threadSceneSha256']),scene('v002 接合新版本',mount['demonstrationScene'],mount['demonstrationSceneSha256']),scene('v002 獨立網格覆核','learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/independent-audit-v001.json','910d06dd2f4a6f430b6e94c7246f7c1b560364b90eb2217998ebd65e596e97b5')], 'steps':msteps}
    old_mount={'title':'歷史問題案例：盒側接合 v001（10 步）','section':'11-12','historical':True,
      'description':'獨立覆核發現三角化結果中高約 0.0004642 mm 的細長三角形，此高度不是物理壁厚；一部分源於七邊面三角化，影響待評估。v002 調整接合相位，不代表已驗證改善或合格。',
      'sourceVersions':[scene('v001 接合版本',mount_old['demonstrationScene'],mount_old['demonstrationSceneSha256']),scene('獨立細長三角覆核','learning/evidence/08/2026-10-28-thread-mount-independent-review-v001/mount-v001.json','02eb87948192701591918278f1560ebfb4004349ed624056505d8a1b164c0980'),scene('來源七邊面覆核','learning/evidence/08/2026-10-28-thread-mount-independent-review-v001/mount-triangle-parent-polygon-v001.json','adf0ed47b47110d2911d3951c2116a3f65d491dd4ee86c0fb6c02b9bf5f5af7c')], 'steps':old_msteps}
    d=copy.deepcopy(json.loads(SRC.read_text(encoding='utf-8')));c=next(x for x in d['chapters'] if x['chapterId']=='ch11')
    boss_drawing=c['drawing'];boss_drawing['description']='獨立盲孔柱的網格投影與剖面，不是盒側螺紋接合或指定五金的正式柱。'
    c['drawing']={'path':'/challenges/box-external-thread-drawing-v003.svg','title':'盒側外牙接合草案的網格工程圖','sha256':'a18d1db95af220e0fda6dcc63d67f0d23c80fd8134525a68f057bd31a151f63f'}
    c['drawingStatus']='以新版盒側接合網格製作的工程題圖；三視圖及剖切為數位草案，可見邊取樣並非完整標準隱線；不含上蓋，不代表完整干涉、製造或配合合格。'
    c['supplementalDrawings'].insert(0,boss_drawing)
    boss,old,inner=c['demonstrations'];old['title']='歷史問題案例：外牙 v005（14 步）';old['historical']=True
    c['demonstrations']=[repaired,mounted,boss,inner,old,old_mount]
    c['sourceSteps'].extend([{'chapterId':'ch11','sectionId':'11-11','label':'修訂外牙'},{'chapterId':'ch11','sectionId':'11-12','label':'盒側外牙接口'}])
    c['screenshot']={**msteps[-1]['screenshot'],'caption':'獨立 Blender 原圖：修訂外牙接合盒側後的重開畫面；不是實體試配或本題完整驗證。'}
    c['requirements'][1]='觀察修訂外牙與盒側接合、獨立盲孔柱及內牙試塊；分辨程式準備與 GUI 操作。'
    c['checks'][1]='比較 v005 候選交疊與修正版的有限數位檢查；記錄牙形、對件、材料及實體試配仍待驗。'
    c['limitations'].append('v010 柱芯旋轉 5.625°、高約 4.8 mm，改變幾何；數位診斷不等於無自交、ISO 符合、可列印或配合合格。')
    c['limitations'].append('盒側接口不是螺旋上蓋；內牙試塊不是已核准對件，靜態外框與局部射線不構成完整動態干涉檢查；另有細長三角形待評估。')
    c['physicalResults']={'material':None,'print':None,'measurement':None,'fit':None,'qualifiedClearance':None,'qualifiedStrength':None}
    c['evidenceStatus']='修訂與接合為獨立 Blender 示範；v005 保留為問題案例，均不代表學員完成或實體驗證。'
    d['version']='v007';d['source']={'path':CURRICULUM,'sha256':CURRICULUM_HASH};d['previousVersion']={'path':'learning/web/challenges/challenges-v006.json','sha256':SRC_HASH}
    OUTPUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(sha(OUTPUT))
if __name__=='__main__':main()
