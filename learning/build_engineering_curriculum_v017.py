"""Append evidence-backed warnings about intermediate and stale sketch geometry."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v016.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v017.json'
SOURCE_SHA='48d24db06677fb74c6aec8f8c6f74c7d04a5317199cb6ddfae33b9d87d7d4a7a'
SUMMARY='learning/evidence/parametric/2026-10-27-manual-box-xy-safety-review-v001/xy-intermediate-review-v001.json'
SUMMARY_SHA='ee913fba4aebaeaec185d3be67c5c6592ec04ab8349eb91661a3d1ef929eade3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path,expected,label,kind):
    target=(ROOT/path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file() or sha(target)!=expected:
        raise ValueError('missing or changed: '+path)
    return {'path':path,'sha256':expected,'label':label,'type':kind}


def main():
    before=SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:
        raise ValueError('v016 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    ref=checked(SUMMARY,SUMMARY_SHA,'手工 X／Y 驅動中間狀態安全核對摘要','verification-json')
    result=json.loads((ROOT/SUMMARY).read_text(encoding='utf-8-sig'))
    if data['id']!='engineering-curriculum-v002' or result['kind']!='gui-driver-intermediate-and-stale-geometry-review':
        raise ValueError('unexpected baseline or review')
    if (result['paste']['outerY'],result['paste']['cutterY'],result['paste']['constraintY'])!=([0,40],[2,42],40):
        raise ValueError('unexpected pasted driver observation')
    if (result['formula']['outerY'],result['formula']['cutterY'],result['formula']['constraintY'])!=([0,40],[2,38],36):
        raise ValueError('unexpected formula observation')
    stale=result['beforeUpdate']
    if (stale['outerX'],stale['outerY'],stale['cutterX'],stale['cutterY'],stale['driverValues'],stale['solver'],stale['dof'])!=([0,80],[0,50],[2,68],[2,38],[76,46],'OKAY',0):
        raise ValueError('unexpected stale geometry observation')
    imgs=result['images']
    if len(imgs)!=3:
        raise ValueError('unexpected screenshots')
    for item in imgs:
        checked(item['path'],item['sha256'],item['path'],'screenshot')
    def fig(index,caption):
        item=imgs[index]
        return {'type':'screenshot','path':item['path'],'sha256':item['sha256'],'caption':caption}
    limitations=[
        '這些界限由程式讀回；圖中尺寸標籤有重疊，不能從畫面直接量得這些數值。',
        '貼 Driver 後修正公式前是暫時無效幾何，先完成公式、手動更新並核對，不要把中間狀態當完成品儲存、匯出或列印。',
        'Fully defined 僅表示當時草圖約束狀態；本次即使顯示 Fully defined，Driver 欄位變更後的切割體仍是舊尺寸，必須手動更新後再核對。',
        '此為特定 Blender 5.2.1／CAD Sketcher 0.32.1 隔離示範；僅測一次70×40→80×50，布林後壁厚、閉合性及上蓋連動未驗。',
        '0.4 mm 總間隙仍為試驗值；實體列印、量測與試配結果留空。',
    ]
    steps=[
        {'id':'ch04-xy-safety-01','title':'貼上 Driver 後先核對公式','goal':'辨認暫時越出盒體的切割體',
         'context':'外框 Y40；內腔 Y 欄位剛貼上來源 Driver，尚未編輯公式。',
         'actions':['觀察紫色 Y 欄位暫顯40 mm。','完成本例來源變數減4的公式，再對照摘要中的幾何界限。'],
         'success':'程式讀回貼上時盒體 Y0～40、切割體 Y2～42；公式修正後切割體 Y2～38。前者超出盒體，屬暫時無效幾何。',
         'figures':[fig(0,'原圖：剛貼上 Driver，Y 欄位顯示40 mm；界限依程式讀值。'),fig(1,'原圖：公式減4後 Y 欄位顯示36 mm；界限依程式讀值。')]},
        {'id':'ch04-xy-safety-02','title':'Fully defined 仍要更新並核對','goal':'區分草圖約束狀態與實際幾何更新',
         'context':'外框由70×40改為80×50，進入內腔草圖但尚未按更新。',
         'actions':['查看 Fully defined 及紫色 Driver 欄76／46 mm。','按草圖更新後，再對照更新後摘要與實際幾何。'],
         'success':'更新前雖顯示 Fully defined，程式仍讀回舊切割體 X2～68／Y2～38；前一步示範的手動更新後才讀回 X2～78／Y2～48。',
         'figures':[fig(2,'原圖：更新前顯示 Fully defined 與76／46 mm；切割體舊界限依程式讀值。')]},
    ]
    for step in steps:
        step.update({'shortcuts':[],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(limitations),'artifacts':[ref]})
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=226 or any(s['id'] in old for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter=next(c for c in data['chapters'] if c['id']=='ch04')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('本次 Y Driver 剛貼上且公式未修正時切割體暫時超出盒體；Fully defined 也不保證 Driver 修改後幾何已更新，需核對讀值。')
    data['version']='v017 · 2026-10-27'
    data['description']='12章詳細操作參照；v017追加 Driver 暫時無效幾何與手動更新前狀態的證據警示。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v016.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualXYIntermediateReview']={'summary':ref,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV017']='以實際 UI 原圖與去識別讀值區分公式修正前越界和 Fully defined 但幾何未更新，不根據面數推斷拓樸。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v017')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v016 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v017 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
