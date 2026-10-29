"""Append X/Y comparison cases and distinguish stale geometry from valid results."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v019.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v020.json'
SOURCE_SHA='2de69df17f7faff8b2c048a50f26c1af95e045a45264e5d2ff32572cdcd6ec30'
BASE='learning/evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/'
SUMMARY=BASE+'manual-lid-multicase-verification-v001.json'
SUMMARY_SHA='ae82d010881d8e8884a4ff2be468848b1cfe7f2cec31c32d69c66e23bef97d35'


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
        raise ValueError('v019 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    if data['id']!='engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref=checked(SUMMARY,SUMMARY_SHA,'盒蓋多組尺寸手動更新驗證摘要','verification-json')
    result=json.loads((ROOT/SUMMARY).read_text(encoding='utf-8-sig'))
    if result['kind']!='manual-box-lid-shape-driver-multicase-gui':
        raise ValueError('unexpected trial')
    phases=result['phases']
    expected={
        'x90y50-before':([2,78],[2,48],[1,0]),'x90y50-after':([2,88],[2,48],[1,0]),
        'x80y60-before':([2,88],[2,48],[0,1]),'x80y60-after':([2,78],[2,58],[0,1]),
        'x70y40-before':([2,78],[2,58],[-1,-1]),'x70y40-after':([2,68],[2,38],[-1,-1]),
        'reopened':([2,68],[2,38],[-1,-1])}
    for name,(xs,ys,vals) in expected.items():
        p=phases[name]
        cutter=p['meshReadback']['Body.001']['levels']['30.0']
        if (cutter['x'],cutter['y'],[k['value'] for k in p['shapeKeys'][1:]])!=(xs,ys,vals):
            raise ValueError('unexpected phase '+name)
        if len(p['shapeDrivers'])!=2 or not all(d['valid'] for d in p['shapeDrivers']):
            raise ValueError('unexpected Key drivers '+name)
    for name,outer in [('x90y50-after',(88,48)),('x80y60-after',(78,58)),('x70y40-after',(68,38)),('reopened',(68,38))]:
        level=phases[name]['meshReadback']['Cube']['levels']['26.0']
        if abs((outer[0]-level['x'][-1])-0.2005)>0.00001 or abs((outer[1]-level['y'][-1])-0.2003)>0.00001:
            raise ValueError('unexpected vertex difference '+name)
    if phases['x80y60-before']['meshReadback']['Body']['nonManifold']!=0 or phases['x70y40-before']['meshReadback']['Body']['nonManifold']!=0:
        raise ValueError('unexpected intermediate non-manifold result')
    scene=result['scene']
    if scene['sha256']!='688e2c22458547599ab1ac7f065ae90ae08af47cabd05036b512aaa8015293ce':
        raise ValueError('unexpected scene')
    scene_ref=checked(BASE+scene['file'],scene['sha256'],'70×40 手動更新後重開試驗版本','scene-blend')
    images=result['images']
    if len(images)!=11:
        raise ValueError('expected 11 screenshots')
    lookup={}
    for item in images:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot')
        lookup[item['file']]=item
    if len(lookup)!=11:
        raise ValueError('duplicate screenshot')
    def fig(name,caption):
        item=lookup[name]
        return {'type':'screenshot','path':BASE+name,'sha256':item['sha256'],'caption':caption}
    common=[
        '本次實際順序為80×50→90×50→80×60→70×40；80×60相對80×50基準是 Y 單軸對照，但實際該步由90×50同時改 X 和 Y。',
        '上蓋形狀鍵隨外框變更，內腔須進草圖手動更新；更新前仍為舊切割體，不可作完成品匯出或列印。',
        '本次80×60更新前切割體 X 到88已超出外框80；70×40更新前切割體 X 到78、Y 到58均超外框。此時 Body non-manifold 邊數仍為0，不能以此證明幾何正確，也不能由面數推論拓樸。',
        '三組更新後各側約0.2 mm為同高度頂點界限推算，並非完整截面、碰撞或實體配合檢驗；0.4 mm 總間隙仍為試驗值。',
        '本次鍵值僅測 −1、0、1；−2～2鍵範圍和公式換算的 X60～100／Y30～70 僅未夾限理論區間，不是安全或製造範圍。舊 v007 防護不適用本手工盒。',
        '照片中尺寸文字部分重疊，頂點界限、Driver 及鍵值由程式讀回；未列印或試配。插件啟用和檔案對話框路徑由程式處理，其餘操作由 GUI 事件進行。',
    ]
    sections=[
        ('ch05-manual-lid-cases-01','從基準改為90×50','比較相對基準的 X 方向改變','雙 Driver 試驗場景，基準80×50。',
         ['選 Body 並進 Body Sketch，將 X80改90，Y維持50。','進 Body.001 Sketch 手動更新，再核對摘要。'],
         '更新前切割體仍 X2～78／Y2～48；更新後讀回 X2～88／Y2～48，Key 1／2 為1／0，同高度頂點界限推算各側約0.2 mm。',
         [('LINK-01-opened.png','原圖：開啟基準盒蓋。'),('LINK-02-body-selected.png','原圖：選 Body。'),('LINK-03-outer-sketch.png','原圖：進入外框草圖。'),('CASES-01-x90y50-before.png','原圖：外框90／50，內腔尚未手動更新。'),('CASES-02-x90y50-after.png','原圖：內腔草圖手動更新後；界限依讀值。')],[ref]),
        ('ch05-manual-lid-cases-02','由90×50改為80×60','比較相對基準的 Y 方向變化','前一步已更新90×50內腔；重新進 Body Sketch。',
         ['將 X90改回80、同時將 Y50改為60。','進 Body.001 Sketch 手動更新，再核對摘要。'],
         '此結果相對80×50基準只差 Y，但此步實際改了兩軸。更新前切割體 X 到88已超出外框80；更新後 X2～78／Y2～58，Key 1／2 為0／1。',
         [('CASES-03-x80y60-before.png','原圖：外框80／60，內腔仍舊；界限依程式讀回。'),('CASES-04-x80y60-after.png','原圖：內腔手動更新後；兩側界限依讀值。')],[ref]),
        ('ch05-manual-lid-cases-03','雙軸縮小並保存','核對負形狀鍵值與重開','前一步已更新80×60內腔；重新進 Body Sketch。',
         ['將外框改為70×40，再進內腔草圖手動更新。','另存獨立試驗版本並重開，對照摘要。'],
         '更新前舊切割體 X 到78／Y 到58均超外框；更新並重開後讀回 X2～68／Y2～38，兩個鍵值均−1，各側頂點界限差約0.2 mm。',
         [('CASES-05-x70y40-before.png','原圖：外框70／40，內腔仍舊；界限依程式讀回。'),('CASES-06-x70y40-after.png','原圖：內腔手動更新後。'),('CASES-07-saved.png','原圖：70×40 試驗版另存。'),('CASES-08-reopened.png','原圖：重開後外觀；尺寸與鍵值依程式讀回。')],[scene_ref,ref]),
    ]
    steps=[{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name,caption) for name,caption in figures],'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in sections]
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=238 or any(s['id'] in old for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter=next(c for c in data['chapters'] if c['id']=='ch05')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('v020 追加90×50、80×60、70×40三組數位對照；每次必須手動更新內腔，重開僅驗70×40，未實體試配或判全面無干涉。')
    data['version']='v020 · 2026-10-27'
    data['description']='12章詳細操作參照；v020追加手工盒蓋三組尺寸、手動更新與縮小版本重開。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v019.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualBoxLidMulticaseVerification']={'summary':ref,'scene':scene_ref,'testedSequenceMm':[[80,50],[90,50],[80,60],[70,40]],
        'cavityRequiresManualUpdate':True,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV020']='逐圖核對及程式讀值；Y對照相對基準但實際同時操作X與Y，避免以non-manifold或面數代替幾何驗證。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v020')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v019 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v020 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
