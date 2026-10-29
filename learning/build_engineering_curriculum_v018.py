"""Append a fixed GUI-made lid, and date historical chapter-level limitations."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v017.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v018.json'
SOURCE_SHA='6d5d6ceff53825429a18207cc96fe19994a2068b1b6e1322d9a7a68ccb211448'
BASE='learning/evidence/parametric/'
SUMMARY=BASE+'2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json'
SUMMARY_SHA='3c4829f5b1ac01010dc1e4e98a3220388f3fc139e96b5e79c3b898736decf599'


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
        raise ValueError('v017 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    if data['id']!='engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref=checked(SUMMARY,SUMMARY_SHA,'固定尺寸上蓋幾何與讀值摘要','verification-json')
    result=json.loads((ROOT/SUMMARY).read_text(encoding='utf-8-sig'))
    if result['kind']!='manual-gui-fixed-lid-on-manual-box':
        raise ValueError('unexpected trial')
    objects=result['bodyAndLidEvaluation']
    if objects['Body']['nonManifoldEdges']!=0 or objects['Cube']['nonManifoldEdges']!=0:
        raise ValueError('unexpected non-manifold result')
    expected={'2.0':([2,78],[2,48]),'0.0':([0,80],[0,50])}
    for z,(xs,ys) in expected.items():
        if objects['Body']['levels'][z]['x']!=xs or objects['Body']['levels'][z]['y']!=ys:
            raise ValueError('unexpected body vertex levels')
    levels=objects['Cube']['levels']
    if (levels['26.0']['x']!=[2.2005,4.2005,75.7995,77.7995] or
        levels['26.0']['y']!=[2.2003,4.2003,45.7997,47.7997] or
        levels['32.0']['x']!=[0.0005,79.9995] or levels['32.0']['y']!=[0.0003,49.9997]):
        raise ValueError('unexpected lid vertex levels')
    if not all(k in levels for k in ['26.0','30.0','32.0']):
        raise ValueError('missing vertex level')
    scene=result['scene']
    if scene['sha256']!='c870ffe0366bee23e44f1a13d12259460f100a723f7753de0f28f8e84c43f508':
        raise ValueError('unexpected scene')
    scene_ref=checked(BASE+scene['file'],scene['sha256'],'固定80×50盒蓋示範場景（未連動）','scene-blend')
    images=result['images']
    if len(images)!=14:
        raise ValueError('expected 14 original screenshots')
    lookup={}
    for item in images:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot')
        lookup[Path(item['file']).name]=item
    if len(lookup)!=14:
        raise ValueError('duplicate screenshots')
    def fig(name,caption):
        item=lookup[name]
        return {'type':'screenshot','path':BASE+item['file'],'sha256':item['sha256'],'caption':caption}
    common=[
        '此上蓋是獨立 Blender GUI 以一般網格手工製作的固定80×50 mm 示範；尚未建立盒蓋參數連動，改外框後不可假設上蓋跟隨。',
        '插件由程式啟用、檔案對話框路徑由程式填入；蓋板、I／E 建模、保存與重開使用 GUI 事件。模型與操作屬示範，非學員完成。',
        'Body 與 Cube 的 non-manifold 邊數0、各層頂點座標和體積均由程式讀回；沒有實際截面、單殼或盒蓋交集檢查，不可推定無干涉或合格。',
        '唇外各側約0.2 mm是頂點座標推算的數位試驗值；GUI 縮放造成約0.0005 mm 座標偏差，總間隙0.4 mm不等於實體合格值。',
        '重開畫面有 sketcher.slvs_select 工具未找到提示，原因未知；實際列印、量測與試配尚未進行。',
    ]
    sections=[
        ('ch05-manual-lid-fixed-01','新增並定位蓋板','建立固定尺寸的上蓋板','獨立試驗盒80×50×30 mm，離開草圖並選取 Body。',
         ['H 隱藏盒體，新增 Cube。','依本次單位設定縮放為約80×50×2 mm，套用縮放，再移至盒口 Z30～32 mm。'],
         '畫面可見新 Cube 與蓋板形狀；各座標為程式讀值，不是從圖上量得。',
         [('LID-01-opened.png','原圖：開啟手工盒，底部顯示工具提示。'),('LID-02-body-selected.png','原圖：離開草圖並選取盒體。'),('LID-03-cube.png','原圖：隱藏盒體後新增 Cube；初始方塊超出目前視野。'),('LID-04-plate.png','原圖：縮放、移動後的固定蓋板。')],[ref]),
        ('ch05-manual-lid-fixed-02','在蓋板底面形成唇外緣','觀察唇邊外側的兩個操作','Cube 的 Edit Mode、面選取；切底視並選取底面。',
         ['底面 I 內插2.2 mm。','對選定面 E 拉伸4 mm。'],
         '底視原圖顯示內插輪廓；深度與頂點座標依程式讀值，不可直接由照片量得。',
         [('LID-05-bottom-face.png','原圖：底視選取底面。'),('LID-06-inset-outer.png','原圖：底面 I 內插2.2 mm。'),('LID-07-lip-extrude.png','原圖：E 拉伸後底視；高度依讀值。')],[ref]),
        ('ch05-manual-lid-fixed-03','形成環形唇邊','完成固定蓋的環唇網格','保持 Edit Mode、所選中心面與底視。',
         ['I 再內插2 mm。','E 輸入 −4 mm，將中心面推回。'],
         '底視顯示環形輪廓；程式按頂點 Z 分組讀得唇邊 Z26、蓋板底 Z30、蓋板頂 Z32 mm。這不是截面檢查。',
         [('LID-08-inset-inner.png','原圖：再次內插形成內緣。'),('LID-09-lip-recess.png','原圖：中心面推回後的底視。')],[ref]),
        ('ch05-manual-lid-fixed-04','保存固定尺寸上蓋','保留可重開的固定幾何示範','Object Mode；顯示已隱藏的盒體。',
         ['顯示盒體，另存獨立版本，再重新開啟。','對照安全摘要中的頂點座標、non-manifold 邊數與檔案 SHA。'],
         '重開後程式讀得 Body／Cube 的 non-manifold 邊數均0；蓋板與唇頂點座標依摘要。這不代表盒蓋無干涉，也不是實體試配。',
         [('LID-10-assembly.png','原圖：恢復顯示後的底視；此角度不能看出全部配合面。'),('LID-11-saved.png','原圖：固定尺寸上蓋另存。'),('LID-12-reopened.png','原圖：重開後畫面；網格數值依讀回摘要。')],[scene_ref,ref]),
    ]
    steps=[{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name,caption) for name,caption in figures],'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in sections]
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=228 or any(s['id'] in old for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    ch04=next(c for c in data['chapters'] if c['id']=='ch04')
    limits=ch04['limitations']
    replacements={
        '另有60×40草圖的GUI實心拉伸及保存重開示範；此單獨實心體尚非手工內腔、上蓋或雙件連動。':'v009 當時：60×40草圖的GUI實心拉伸及保存重開僅為單獨實心體，非當時已完成內腔、上蓋或雙件連動。',
        '新增固定外形下的內矩形約束與切割體探測；布林結果、尺寸連動、上蓋及另存仍未充分驗證。':'v012 當時：固定外形下的內矩形約束與切割體探測尚未充分驗證布林結果、尺寸連動、上蓋及另存。',
        '後續原生 GUI Driver 試驗僅建立 X 單 Driver，外框變動與 Y 尚未成功；名稱含70x50的試驗檔實際仍60×40。':'v014 當時：原生 GUI Driver 試驗僅建立 X 單 Driver，外框變動與 Y 尚未成功；名稱含70x50的試驗檔實際仍60×40。',
        'X70 的內腔切割體須手動更新草圖才跟隨；結果尚未另存，Y／上蓋待驗，布林後壁厚與閉合性未驗。':'v015 當時：X70 的內腔切割體須手動更新草圖才跟隨；該次更新結果未另存，當時 Y／上蓋待驗。後續雙軸驗證見 v016。',
    }
    for a,b in replacements.items():
        if limits.count(a)!=1:
            raise ValueError('chapter history limit missing or duplicated')
        limits[limits.index(a)]=b
    ch05=next(c for c in data['chapters'] if c['id']=='ch05')
    ch05['steps'].extend(steps)
    ch05['limitations'].append('v018 手工示範另存固定80×50上蓋；盒蓋尺寸連動仍待驗，頂點座標推算的約0.2 mm各側間隙是試驗值，未查盒蓋交集或實體試配。')
    data['version']='v018 · 2026-10-27'
    data['description']='12章詳細操作參照；v018追加手工固定上蓋及其頂點和非流形邊讀值。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v017.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualFixedLidVerification']={'summary':ref,'scene':scene_ref,'lidParametricLinkageVerified':False,
        'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV018']='依本次真實 GUI 圖與頂點分組讀值記錄固定蓋；non-manifold 邊數不推論單殼或相交結果。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v018')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v017 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v018 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
