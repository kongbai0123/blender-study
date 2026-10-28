"""Append an observed shape-key clamping counterexample without calling it a product."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v020.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v021.json'
SOURCE_SHA='ac7a28891c429416e5415d6a1aa2c6125ecd53c04a0528cf985aa4323cc2040c'
BASE='learning/evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/'
SUMMARY=BASE+'out-of-range-counterexample-v001.json'
SUMMARY_SHA='e5dd705c5dca1622909554b16f1c4ec2457be7d7c6742c96642589a55ab8e84e'


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
        raise ValueError('v020 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    if data['id']!='engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref=checked(SUMMARY,SUMMARY_SHA,'形狀鍵超界夾限反例摘要','verification-json')
    result=json.loads((ROOT/SUMMARY).read_text(encoding='utf-8-sig'))
    if result['kind']!='shape-key-clamping-counterexample':
        raise ValueError('unexpected trial')
    p=result['phases']['reopened']
    keys=p['shapeKeys']; lid=p['meshReadback']['Cube']['levels']; cavity=p['meshReadback']['Body.001']['levels']['30.0']
    if [k['value'] for k in keys]!=[1,2,0] or (keys[1]['min'],keys[1]['max'])!=(-2,2):
        raise ValueError('unexpected key clamp')
    if cavity!={'x':[2,108],'y':[2,48]} or lid['26.0']['x']!=[2.2005,4.2005,95.7995,97.7995] or lid['32.0']['x']!=[0.0005,99.9995]:
        raise ValueError('unexpected reopened geometry')
    if len(p['shapeDrivers'])!=2 or not all(d['valid'] for d in p['shapeDrivers']):
        raise ValueError('unexpected key drivers')
    if abs((cavity['x'][-1]-lid['26.0']['x'][-1])-10.2005)>0.00001:
        raise ValueError('unexpected right vertex difference')
    scene=result['scene']
    if scene['sha256']!='d213f5d11c1232cea59e547ba06664b3789dab253d5dbeb42393a3e9a09220e5' or scene['classification']!='超界反例，非完成品':
        raise ValueError('unexpected scene')
    scene_ref=checked(BASE+scene['file'],scene['sha256'],'110×50 超界反例（非完成品）','scene-blend')
    images=result['images']
    if len(images)!=9:
        raise ValueError('expected 9 original screenshots')
    lookup={}
    for item in images:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot')
        lookup[item['file']]=item
    if len(lookup)!=9:
        raise ValueError('duplicate screenshot')
    def fig(name,caption):
        item=lookup[name]
        return {'type':'screenshot','path':BASE+name,'sha256':item['sha256'],'caption':caption}
    common=[
        '此為獨立 Blender 的110×50 超界反例，不是完成品；原 run 的保存／重開動作文字沿用「雙軸修改」，實際只改 X80→110，Y 維持50。',
        '本例形狀鍵 X 公式在110時理論值3，但範圍 −2～2 使實際鍵值被夾為2，蓋板 X 約0～100而盒體 X0～110；Driver 有效不保證尺寸跟隨。',
        '內腔仍須手動更新。更新後盒口頂點 X 到108、唇外頂點到97.7995，右側界限差約10.2005 mm 為程式頂點讀值與推算，不是合格配合或完整截面檢查。',
        'X60～100／Y30～70 只是公式與鍵範圍換算的未夾限候選區間，不是已驗證全區、安全或製造範圍；舊 v007 尺寸防護不適用此手工盒。',
        '原圖可能遮擋及尺寸文字重疊；程式讀取鍵、Driver 與網格，插件啟用及檔案視窗路徑由程式處理，尺寸修改和更新由 GUI 事件進行。實體列印及試配留空。',
    ]
    sections=[
        ('ch05-manual-lid-clamp-01','觀察超界 X 尺寸','辨認公式與鍵值夾限','從80×50的獨立手工盒蓋試驗版出發。',
         ['選 Body 並進外框草圖，將 X80改110，Y保持50。','查看內腔草圖與本次 Driver／形狀鍵讀值。'],
         '外框欄位顯示110／50；X 公式的理論值為3，程式讀回 Key 1 因上限被夾為2。內腔尚未手動更新，不能視為正確幾何。',
         [('LINK-01-opened.png','原圖：開啟基準試驗版。'),('LINK-02-body-selected.png','原圖：選 Body。'),('LINK-03-outer-sketch.png','原圖：外框草圖基準80／50。'),('LINK-04-outer-110x50.png','原圖：僅 X 改為110，Y仍50。'),('LINK-05-inner-before-solve.png','原圖：內腔更新前；欄位和幾何須分別核對。')],[ref]),
        ('ch05-manual-lid-clamp-02','更新內腔後辨認失配','用實際讀值核對形狀鍵夾限的影響','110×50 反例場景，內腔草圖尚未手動更新。',
         ['點內腔草圖更新圖示，另存反例並重開。','比較摘要中盒口與唇邊的頂點界限。'],
         '重開後盒口 X2～108、唇外 X2.2005～97.7995，右側界限差約10.2005 mm；蓋長約100而盒長110。這是超界失配反例，非完成品。',
         [('LINK-06-inner-after-solve.png','原圖：內腔手動更新後。'),('LINK-07-assembly.png','原圖：更新後外觀；此角度不能直接量出界限差。'),('LINK-08-saved.png','原圖：反例另存；實際僅X改變。'),('LINK-09-reopened.png','原圖：反例重開；尺寸及鍵值依程式讀回。')],[scene_ref,ref]),
    ]
    steps=[{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name,caption) for name,caption in figures],'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in sections]
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=241 or any(s['id'] in old for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    ch=next(c for c in data['chapters'] if c['id']=='ch05')
    ch['steps'].extend(steps)
    ch['limitations'].append('v021 的 X110 超界反例中形狀鍵被夾2，上蓋未跟足盒體；候選鍵範圍不是安全範圍，v007 防護不適用。')
    data['version']='v021 · 2026-10-27'
    data['description']='12章詳細操作參照；v021追加形狀鍵夾限導致上蓋尺寸失配的實際反例。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v020.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualBoxLidClampingCounterexample']={'summary':ref,'scene':scene_ref,'shapeKeyComputedValue':3,
        'observedClampedValue':2,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV021']='核對9張原圖與程式讀值；原 run 雙軸標籤不符，此例僅改X，保留為非完成品反例。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v021')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v020 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v021 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
