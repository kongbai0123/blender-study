"""Chapter 11/12 challenge evidence. Copies only verified, publishable original images."""
from pathlib import Path
from hashlib import sha256
import copy, json, re

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'learning/web/challenges/challenges-v005.json'
OUTPUT=ROOT/'learning/web/challenges/challenges-v006.json'
ASSETS=ROOT/'learning/web/challenges'
SOURCE_HASH='6e73f7990434fb84631c98f4b6941967d01ce49d9513ff099b8cf79017fa34f2'
BOSS_HASH='23e051245359fcec7672c36ff981ad69e8afbc716488271518e42e80a68879ea'
INNER_HASH='a0e204c29ec27c4be91c081c39e9d16bf4cac7e8a8f18be83b1e8abffd3b1655'
EXTERNAL_HASH='ba4ee05fa739354717201f20d7502fc8c39201982fa0344e4cbe9714658599e8'
CURRICULUM_HASH='a5688b2abaad001a60c193a187784c8a67ec88c9862fd5fade7bfa8ce1d3bfa6'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def checked(path, expected):
    p=ROOT/path
    if sha(p)!=expected:raise ValueError('hash mismatch: '+str(path))
    return p
def image(source, expected, name):
    if not re.fullmatch(r'[a-z0-9-]+\.png',name):raise ValueError('unsafe asset name')
    src=checked(source,expected); dst=ASSETS/name
    if dst.exists() and sha(dst)!=expected:raise FileExistsError(dst)
    if not dst.exists():dst.write_bytes(src.read_bytes())
    return {'path':'/challenges/'+name,'sha256':expected}
def main():
    if OUTPUT.exists():raise FileExistsError(OUTPUT)
    if sha(SOURCE)!=SOURCE_HASH:raise ValueError('v005 source changed')
    checked('learning/web/engineering-curriculum-v033.json',CURRICULUM_HASH)
    boss=json.loads(checked('learning/lesson11_boss_optional_steps_v001.json',BOSS_HASH).read_text(encoding='utf-8'))
    inner=json.loads(checked('learning/lesson11_inner_optional_steps_v001.json',INNER_HASH).read_text(encoding='utf-8'))
    external=json.loads(checked('learning/lesson11_external_optional_steps_v001.json',EXTERNAL_HASH).read_text(encoding='utf-8'))
    checked(external['startingScene']['path'], external['startingScene']['sha256'])
    checked('learning/web/challenges/manual-boss-drawing-v002.svg','04bcaff5010e9fa84699690d3457836001f7cff2b3e31a0aabe39d5d4716a1c3')
    checked('learning/web/challenges/inner-thread-block-drawing-v002.svg','7850f62e1f28bb2bfc2793af86f0fdf6561c2541ece6911ba3fe7a4eb9399125')
    data=copy.deepcopy(json.loads(SOURCE.read_text(encoding='utf-8')))
    bsteps=[]
    for i,step in enumerate(boss['steps'],1):
        pic=step['screenshot']; copied=image(pic['relativePath'],pic['sha256'],f'boss-gui-v003-{i:02}.png')
        bsteps.append({'id':step['id'],'goal':step['goal'],'context':step['context'],'operation':step['operation'],'success':step['success'],'readings':[r['location']+'：'+r['value'] for r in step['readings']],'limits':step['limits'],'screenshot':copied})
    isteps=[]
    for i,step in enumerate(inner['steps'],1):
        pic=step['screenshot'];copied=image(pic['path'],pic['sha256'],f'inner-gui-v003-{i:02}.png')
        isteps.append({'id':step['id'],'goal':step['goal'],'context':step['context'],'operation':[step['operation']],'success':step['visibleConfirmation'],'readings':[step['programReadback']],'limits':inner['limitations'],'screenshot':copied})
    esteps=[]
    for i,step in enumerate(external['steps'],1):
        pic=step['screenshot'];copied=image(pic['path'],pic['sha256'],f'external-gui-v005-{i:02}.png')
        esteps.append({'id':step['id'],'goal':step['goal'],'context':step['context'],'operation':[step['operation']],'success':step['visibleConfirmation'],'readings':[step['programReadback']],'limits':external['limitations'],'screenshot':copied})
    ch11=next(c for c in data['chapters'] if c['chapterId']=='ch11')
    ch11['drawing']={'path':'/challenges/manual-boss-drawing-v002.svg','title':'獨立盲孔柱的實際網格題圖（草案）','sha256':'04bcaff5010e9fa84699690d3457836001f7cff2b3e31a0aabe39d5d4716a1c3'}
    ch11['drawingStatus']='獨立盲孔柱的網格投影與剖面，不是接合後盒體或指定五金的正式柱。尺寸、公差及實體配合均未核准。'
    ch11['supplementalDrawings']=[{'path':'/challenges/inner-thread-block-drawing-v002.svg','title':'內牙試塊的實際網格題圖（草案）','description':'16 × 16 × 3 mm 試塊，不是盒蓋；程式預建切割工具的牙端截斷、無間隙補償，非 ISO 牙型，未完成實體驗證。','sha256':'7850f62e1f28bb2bfc2793af86f0fdf6561c2541ece6911ba3fe7a4eb9399125'}]
    ch11['demonstrations']=[{'title':'獨立盲孔柱 GUI 操作（8 步）','description':'獨立 Blender 實拍。保護副本並逐步形成盲孔，獨立柱不等於指定五金的正式柱；示範的檔案瀏覽器路徑與名稱由程式填入。','steps':bsteps},{'title':'外牙 GUI 研究草案（14 步，待修）','description':'輪廓由程式預建，GUI 操作修改器與接合。三組候選交疊及極薄三角形尚待排查，未連盒體；不可視為可列印、ISO 牙型或合格配合。','startingScene':external['startingScene'],'steps':esteps},{'title':'程式預建工具與 GUI 內牙試塊（6 步）','description':'程式先建外牙工具，再在獨立 Blender 透過 GUI 操作差集；這是試塊，不是盒蓋。材料、製程、間隙與實際列印試配待定。','steps':isteps}]
    for demo,section,label in zip(ch11['demonstrations'],['11-10','11-08','11-09'],['獨立盲孔柱','外牙待修研究草案','內牙試塊']):
        demo['section']=section
        ch11['sourceSteps'].append({'chapterId':'ch11','sectionId':section,'label':label})
    ch11['requirements'][1]='觀察 Screw 開放曲面、獨立盲孔柱及內牙試塊示範；分辨程式準備與 GUI 操作。'
    ch11['checks'][1]='記錄外牙草案及內牙試塊的建模方式、局部檢查限制，以及尚未完成的配套五金與實體試鎖。'
    ch11['limitations'].append('內牙試塊並非盒蓋；工具由程式建立、牙端截斷且無間隙補償，未宣稱 ISO 牙型或配合合格。')
    ch11['evidenceStatus']='兩組 GUI 操作是獨立示範，不是學員完成或實體驗證；工程圖依數位網格生成，並非 Blender 操作截圖。'
    # Avoid evidence/ exclusion for these new examples; older demonstration links retain their original meaning.
    ch11['screenshot']={**bsteps[5]['screenshot'],'caption':'獨立 Blender 原圖：手工建立的獨立柱盲孔；並非本題完整示範或盒體接合結果。'}
    ch12=next(c for c in data['chapters'] if c['chapterId']=='ch12')
    ch12['drawing']={'path':'/challenges/lip-clearance-drawing-v001.svg','title':'原盒唇邊名義尺寸鏈參照圖'}
    ch12['drawingStatus']='此圖只作原盒與唇邊尺寸鏈參照：56 − 55.6 = 0.4 mm 名義總間隙，置中時理論單側 0.2 mm；不代表完整交付圖、量測或合格。'
    ch12['limitations'].append('本圖僅涵蓋原盒口與唇邊名義尺寸；不能代替完整交付圖或實體量測。')
    data['version']='v006';data['source']={'path':'learning/web/engineering-curriculum-v033.json','sha256':CURRICULUM_HASH};data['previousVersion']={'path':'learning/web/challenges/challenges-v005.json','sha256':SOURCE_HASH}
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(sha(OUTPUT))
if __name__=='__main__':main()
