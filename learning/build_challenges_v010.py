"""Align chapter exercises with v037 corrections and missing branch drawings."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/challenges/challenges-v009.json'
SOURCE_SHA='ad6479e8425daa86674de9e1ed90bf7725dff905d3a1aa0b2789ff820da6047b'
CURRICULUM=ROOT/'learning/web/engineering-curriculum-v037.json'
CURRICULUM_SHA='79522345aef709d92f5eb28b47176c54e3a45dbc728beacf9c1420dd21d1248a'
OUTPUT=ROOT/'learning/web/challenges/challenges-v010.json'
DRAWINGS=[
    ('ch09','tenon-box-lid-drawing-v001.svg','640367de51cdf7b0bd7abb7b3713af6f5181e6749747835665147c15745af6a8','定位柱與上蓋穿孔分支工程圖','既有06-01實際網格；含柱外框、柱心剖面與局部間隙，29.5 mm側壁外露高度不是力學有效長。間隙僅為試驗值，實體未驗證。'),
    ('ch10','snapfit-box-lid-drawing-v001.svg','03487ffba97d93abe83cce10c283cc0687d9ecbc2574434af88ad890374b5e59','整盒卡扣與蓋裙分支工程圖','既有07-02實際網格的三方向投影與X=0剖面；所有三角邊包括遮蔽線，非標準隱線圖。L19為幾何長而非力學有效長；此圖與三件獨立試片不同分支。'),
]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():raise FileExistsError('refusing to overwrite '+OUTPUT.name)
    if sha(SOURCE)!=SOURCE_SHA or sha(CURRICULUM)!=CURRICULUM_SHA:raise ValueError('source changed')
    data=json.loads(SOURCE.read_text(encoding='utf8'))
    curriculum=json.loads(CURRICULUM.read_text(encoding='utf8'))
    steps={s['id']:s for c in curriculum['chapters'] for s in c['steps']}
    for cid,name,digest,title,description in DRAWINGS:
        if sha(ROOT/'learning/web/challenges'/name)!=digest:raise ValueError('drawing changed')
        chapter=next(c for c in data['chapters'] if c['chapterId']==cid)
        chapter.setdefault('supplementalDrawings',[]).append({'path':'/challenges/'+name,'sha256':digest,'title':title,'description':description})
    ch9=next(c for c in data['chapters'] if c['chapterId']=='ch09')
    ch9['requirements']=[('匯出燕尾分支的盒體與滑蓋 STL，重新匯入核對尺寸；定位柱分支在本章為幾何示範。' if line=='匯出示範分支並重新匯入核對尺寸。' else line) for line in ch9['requirements']]
    # The initial 0.6 CAD file is a saved result, not an empty-scene input.
    ch11=next(c for c in data['chapters'] if c['chapterId']=='ch11')
    count=0
    for demo in ch11.get('demonstrations',[]):
        for record in demo['steps']:
            step=steps.get('ch11-'+record['id'].lower())
            if not step:continue
            record.update(goal=step['title'],context=step['context'],operation=step['actions'],success=step['success'],limits=step['limitations'])
            count+=1
        if demo.get('section')=='11-18':
            demo['sourceVersions'][0]['label']='第12步0.6 mm草圖保存結果（非空白起始場景）'
            demo['description']+=' 從自己的新空白場景開始；所列0.6 mm檔是第12步保存的結果。'
        if demo.get('section')=='11-17':
            demo['description']+=' 六組來源副本與SHA已在正式小步就地標明；「讀取STL實檔」另提供標準Python唯讀指令，並非GUI直接解析二進位。原有盒側圖源自三角化修訂前，不證明新版幾何完全等同。'
        if demo.get('section')=='11-12':
            prefab=next(a for a in steps['ch11-11-mount-v002-01']['artifacts'] if a['path'].endswith('/u11_mount_prefab_v001.blend'))
            demo['startingScene']={'path':prefab['path'],'sha256':prefab['sha256']}
            demo['sourceVersions'].insert(0,{'label':'可跟做起始副本：程式載入既有三物件，尚未做盒側變換','path':prefab['path'],'sha256':prefab['sha256']})
            demo['description']+=' 新提供接合前的三物件起始檔，程式載入既有物件後另存；獨立GUI重開與背景讀回均已核對，不冒充手工Append教學。'
    ch7=next(c for c in data['chapters'] if c['chapterId']=='ch07')
    ch7['limitations']=[('本章已有草圖／尺寸及布林內腔實拍；基準副本切換和另存方式依正式小節核對，實際列印及量測未執行。' if '詳細文字與操作仍須逐步改寫' in line else line) for line in ch7['limitations']]
    data['version']='v010'
    data['source']={'path':CURRICULUM.relative_to(ROOT).as_posix(),'sha256':CURRICULUM_SHA}
    data['previousVersion']={'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA}
    data['correspondenceReview']={'reviewedOn':'2026-10-29','updatedWalkthroughSteps':count,'scope':'同步正式教材的操作與來源說明，補兩個缺圖分支；實際瀏覽、程式渲染及原圖抽查分別留證，非全歷史圖逐張目視。','learnerProgressChanged':False,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None}
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(sha(OUTPUT),'updated walkthrough records',count)


if __name__=='__main__':main()
