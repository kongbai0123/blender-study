"""Append the single GUI box/lid linkage case without implying physical validation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v018.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v019.json'
SOURCE_SHA='8ea244cac879cc5cc30a556247da549b10b88a3b9eaa5b95db363957b2d49963'
BASE='learning/evidence/parametric/'
SUMMARY=BASE+'2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json'
SUMMARY_SHA='35edd16270c9a9760dbc6d95e9302c1ce9f5c220051bc5e209274b7668494d80'


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
        raise ValueError('v018 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    if data['id']!='engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref=checked(SUMMARY,SUMMARY_SHA,'手工盒蓋雙軸連動單組驗證摘要','verification-json')
    result=json.loads((ROOT/SUMMARY).read_text(encoding='utf-8-sig'))
    if result['kind']!='gui-manual-box-lid-shape-driver-one-case':
        raise ValueError('unexpected trial')
    phases=result['phases']
    pre=phases['inner-before-solve'];post=phases['reopened']
    if pre['meshReadback']['Body.001']['levels']['30.0']!={'x':[2.0,78.0],'y':[2.0,48.0]}:
        raise ValueError('unexpected stale cavity')
    if post['meshReadback']['Body.001']['levels']['30.0']!={'x':[2.0,88.0],'y':[2.0,58.0]}:
        raise ValueError('unexpected reopened cavity')
    lid=post['meshReadback']['Cube']['levels']['26.0']
    if lid['x']!=[2.2005,4.2005,85.7995,87.7995] or lid['y']!=[2.2003,4.2003,55.7997,57.7997]:
        raise ValueError('unexpected lid vertex levels')
    drivers=post['shapeDrivers'];keys=post['shapeKeys']
    if len(drivers)!=2 or not all(d['valid'] for d in drivers) or [k['value'] for k in keys]!=[1,1,1]:
        raise ValueError('unexpected shape drivers')
    if [d['expression'] for d in drivers]!=['slvs_c_b596b36138076155/10-8','slvs_c_854e8777cfe2608d/10-5']:
        raise ValueError('unexpected shape expressions')
    if any((k['min'],k['max'])!=(-2,2) for k in keys[1:]):
        raise ValueError('unexpected shape key range')
    raw=ROOT/BASE/'2026-10-27-manual-lid-xy-link-verify-v001/reopened-state.json'
    if sha(raw)!='efe3f4c4130a333de21e3c466ad36dca3de984763427bba265d3e2c924419f2d':
        raise ValueError('reopened raw state changed')
    scene_drivers=json.loads(raw.read_text(encoding='utf-8-sig'))['drivers']
    if len(scene_drivers)!=2 or not all(d['isValid'] for d in scene_drivers):
        raise ValueError('unexpected Scene drivers')
    scene_hashes=['583eb00b7c4a1b04fb42181a84cd02bf97818a97014cadb2dd89ccf592d831dd','467ee2ed91b49a14a2f610f291381249512c96653f5ae8cfb8621f87a62eb499','52cea78d8448eb0f2e132ec16f4d99041009af8f1a8c9ab8091142205c9c9152','ddae8a3d3745146501d25527354352e6b71431b837c78c8269a43dc5e6a3dec6','346260b15fdb87daf3481946adad029aedb9e9c5aeea94ad828117577e2703d6']
    scenes=result['scenes']
    if len(scenes)!=5 or [s['sha256'] for s in scenes]!=scene_hashes:
        raise ValueError('unexpected scene sequence')
    scene_refs=[checked(BASE+s['file'],s['sha256'],label,'scene-blend') for s,label in zip(scenes,['上蓋 X 形狀鍵示範','上蓋 X／Y 形狀鍵示範','上蓋 X Driver 示範','上蓋 X／Y Driver 示範','90×60 手動更新後保存重開示範'])]
    images=result['images']
    if len(images)!=56:
        raise ValueError('expected 56 screenshots')
    lookup={}
    for item in images:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot')
        lookup[item['file']]=item
    if len(lookup)!=56:
        raise ValueError('duplicate screenshots')
    def fig(path,caption):
        item=lookup[path]
        return {'type':'screenshot','path':BASE+path,'sha256':item['sha256'],'caption':caption}
    xkey='2026-10-27-manual-lid-shapekey-x-v001/'
    ykey='2026-10-27-manual-lid-shapekey-y-v001/'
    xdrv='2026-10-27-manual-lid-driver-x-v006/'
    ydrv='2026-10-27-manual-lid-driver-y-v001/'
    run='2026-10-27-manual-lid-xy-link-verify-v001/'
    common=[
        '本次僅實測80×50→90×60 mm；形狀鍵範圍 −2～2，本次鍵值0→1，不能推定任意尺寸或其他範圍均有效。',
        '由公式與形狀鍵範圍計得 X60～100／Y30～70 mm 僅是未觸及鍵值夾限的理論區間，不是已驗證的安全或製造範圍；超出時鍵值可能停止跟隨。舊 v007 防護面板不適用此手工盒，每次改尺寸須依操作手動更新並核對。',
        '外框改變時上蓋形狀鍵 Driver 先更新，內腔幾何仍為舊值；本次更新前右側 X／Y 頂點界限差各約 −9.8 mm，顯示暫時重疊風險。須進內腔草圖手動點更新並核對，中間狀態不可作完成品匯出或列印。',
        '本次貼來源 Driver 時上蓋鍵值暫被夾為2、蓋體尺寸暫不正確；公式修正並核對後才保存，勿把中間狀態當完成品。',
        '程式讀回的同高度頂點界限差約0.2 mm／側、總間隙0.4 mm是試驗值；未做完整交集或實體列印、量測及試配，不能認定配合合格。',
        '兩個內腔 Scene Driver 的被驅動路徑、公式及有效性，兩個上蓋 Key 資料 Driver 與重開幾何為程式讀值；本輪未直接列出 Scene Driver 各來源目標。照片有遮擋及部分尺寸標籤重疊，不可從照片量間隙。',
        'GUI 事件操作選取、形狀鍵、欄位與儲存；插件由程式啟用、檔案對話框路徑由程式填入。本次 Y 階段原 run 的部分 X 動作標籤有誤，本教材依畫面及讀值重述。',
    ]
    sections=[
        ('ch05-manual-lid-link-01','建立上蓋 X 形狀鍵','以頂點位移建立 X 方向變形','上蓋 Cube、Object Data Properties 的 Shape Keys；固定80×50版本。',
         ['新增 Basis 與 Key 1，選 Key 1 並進 Edit Mode。','選取 X 正側頂點，沿 X 移動10 mm，返回 Object Mode 並另存。'],
         '原圖顯示形狀鍵與選取、移動；頂點位置與尺寸依程式讀值。',
         [(xkey+'KEY-01-opened.png','原圖：開啟固定蓋。'),(xkey+'KEY-02-panel.png','原圖：Shape Keys 面板。'),(xkey+'KEY-03-basis.png','原圖：Basis。'),(xkey+'KEY-04-key-one.png','原圖：新增 Key 1。'),(xkey+'KEY-05-edit-vertices.png','原圖：編輯上蓋頂點。'),(xkey+'KEY-06-select-right.png','原圖：選取 X 正側頂點。'),(xkey+'KEY-07-x-shape.png','原圖：正側沿 X 移動後。'),(xkey+'KEY-08-x-object.png','原圖：返回 Object Mode 的 X 形狀。'),(xkey+'KEY-09-saved.png','原圖：X 形狀鍵版本另存。')],[scene_refs[0],ref]),
        ('ch05-manual-lid-link-02','建立上蓋 Y 形狀鍵','以獨立相對鍵建立 Y 方向變形','先將 Key 1 設回0，新增相對 Basis 的 Key 2。',
         ['選 Key 2，進 Edit Mode 選 Y 正側頂點，沿 Y 移動10 mm。','返回 Object Mode，將兩個鍵歸零、設定本次鍵範圍 −2～2，另存。'],
         '畫面顯示兩個鍵及兩方向頂點移動；這只是形狀鍵，尚未接上來源 Driver。',
         [(ykey+'KEY-01-opened.png','原圖：開啟 X 形狀鍵版本。'),(ykey+'KEY-02-x-zero.png','原圖：Key 1 歸零並顯示設定範圍。'),(ykey+'KEY-03-y-created.png','原圖：新增 Key 2。'),(ykey+'KEY-04-edit-vertices.png','原圖：編輯 Key 2 頂點。'),(ykey+'KEY-05-select-y.png','原圖：選取 Y 正側頂點。'),(ykey+'KEY-06-y-shaped.png','原圖：移動 Y 側並返回 Object Mode。'),(ykey+'KEY-07-both-zero.png','原圖：鍵值歸零及範圍。'),(ykey+'KEY-08-saved.png','原圖：X／Y 鍵草案另存。')],[scene_refs[1],ref]),
        ('ch05-manual-lid-link-03','連接上蓋 X Driver','讓 Key 1 引用本次外框 X','外框 Body Sketch 第一個 Distance 為本次 X80。',
         ['從外框 X 欄位 Copy as New Driver，貼到上蓋 Key 1 Value。','在 Edit Driver 選 Scripted Expression，依本次來源變數設為 X／10−8。'],
         '剛貼上時鍵值被夾為2、蓋暫變形；公式後本次80 mm 鍵值回0。變數識別名隨場景不同，不可直接照抄。',
         [(xdrv+'LINK-04-outer-sketch.png','原圖：Body Sketch 來源欄位80／50。'),(xdrv+'LINK-05-source-menu.png','原圖：來源欄位選單。'),(xdrv+'LINK-07-x-key-selected.png','原圖：上蓋選取 Key 1。'),(xdrv+'LINK-08-target-menu.png','原圖：上蓋目標欄位選單。'),(xdrv+'LINK-09-x-pasted.png','原圖：貼上後鍵值被夾為2，暫非正確蓋形。'),(xdrv+'LINK-11-x-popup.png','原圖：Driver 編輯視窗。'),(xdrv+'LINK-12-x-type-menu.png','原圖：選 Scripted Expression。'),(xdrv+'LINK-14-x-formula.png','原圖：本次 X 公式後鍵值回0。'),(xdrv+'LINK-15-x-saved.png','原圖：X Driver 版本另存。')],[scene_refs[2],ref]),
        ('ch05-manual-lid-link-04','連接上蓋 Y Driver','讓 Key 2 引用本次外框 Y','外框 Body Sketch 第二個 Distance 為本次 Y50。',
         ['從外框 Y 欄位 Copy as New Driver，貼到上蓋 Key 2 Value。','在 Edit Driver 選 Scripted Expression，依本次來源變數設為 Y／10−5，確認後另存。'],
         '畫面與 Key 讀值顯示本次 Y 來源50、貼上時鍵值暫為2、公式後回0；此階段原始檔名部分沿用 X，應以畫面與讀值辨認。',
         [(ydrv+'LINK-04-outer-sketch.png','原圖：Body Sketch 來源欄位80／50。'),(ydrv+'LINK-05-source-menu.png','原圖：Y 來源欄位選單。'),(ydrv+'LINK-07-x-key-selected.png','原圖：選 Key 2；原始檔名沿用 X。'),(ydrv+'LINK-08-target-menu.png','原圖：Key 2 欄位選單。'),(ydrv+'LINK-09-x-pasted.png','原圖：Key 2 貼上後被夾為2；原始檔名沿用 X。'),(ydrv+'LINK-11-x-popup.png','原圖：Key 2 Driver 視窗、來源50。'),(ydrv+'LINK-12-x-type-menu.png','原圖：Scripted Expression 類型選單。'),(ydrv+'LINK-14-x-formula.png','原圖：本次 Y 公式後鍵值回0。'),(ydrv+'LINK-15-x-saved.png','原圖：X／Y Driver 版本另存。')],[scene_refs[3],ref]),
        ('ch05-manual-lid-link-05','外框改為90×60','區分上蓋先動與內腔舊值','開啟 X／Y Driver 試驗場景；選 Body 並進外框草圖。',
         ['將 Body Sketch 外框改為90×60 mm。','進 Body.001 Sketch，先對照更新前的欄位及摘要。'],
         '圖上外框90／60、內腔欄86／56且 Fully defined；程式讀回上蓋鍵值已為1／1，但切割體仍 X2～78／Y2～48。更新前右側兩軸頂點界限差各約 −9.8 mm，顯示暫時重疊風險，不可作可用組裝。',
         [(run+'LINK-01-opened.png','原圖：開啟雙 Driver 試驗。'),(run+'LINK-02-body-selected.png','原圖：選 Body，畫面顯示上蓋暫隱藏。'),(run+'LINK-03-outer-sketch.png','原圖：進入 Body Sketch。'),(run+'LINK-04-outer-90x60.png','原圖：外框改為90／60。'),(run+'LINK-05-inner-before-solve.png','原圖：更新前內腔欄86／56，幾何界限依程式讀回。')],[ref]),
        ('ch05-manual-lid-link-06','更新內腔並保存重開','核對本次盒蓋連動的數位結果','Body.001 Sketch，尚未更新的90×60場景。',
         ['點內腔草圖頂端更新圖示。','另存並重開，對照摘要的盒體、唇邊頂點與 Driver。'],
         '重開後程式讀得盒口頂點 X2～88／Y2～58、唇外頂點約 X2.2005～87.7995／Y2.2003～57.7997；各側約0.2 mm 為頂點界限差，不是實體配合判定。',
         [(run+'LINK-06-inner-after-solve.png','原圖：手動更新內腔。'),(run+'LINK-07-assembly.png','原圖：盒蓋顯示外觀；這個角度不能直接量配合間隙。'),(run+'LINK-08-saved.png','原圖：90×60 示範場景另存。'),(run+'LINK-09-reopened.png','原圖：重開後外觀；頂點和 Driver 依程式讀回。')],[scene_refs[4],ref]),
    ]
    steps=[{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name,caption) for name,caption in figures],'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in sections]
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=232 or any(s['id'] in old for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    ch05=next(c for c in data['chapters'] if c['id']=='ch05')
    previous='v018 手工示範另存固定80×50上蓋；盒蓋尺寸連動仍待驗，頂點座標推算的約0.2 mm各側間隙是試驗值，未查盒蓋交集或實體試配。'
    if ch05['limitations'].count(previous)!=1:
        raise ValueError('missing historical fixed lid limit')
    ch05['limitations'][ch05['limitations'].index(previous)]='v018 當時：手工示範另存固定80×50上蓋，當時盒蓋尺寸連動待驗；頂點座標推算的約0.2 mm各側間隙是試驗值，未查盒蓋交集或實體試配。'
    ch05['limitations'].append('v019 單組80×50→90×60示範：上蓋形狀鍵隨外框尺寸更新，內腔仍須手動更新；頂點界限推算各側約0.2 mm，未完成實體試配或全面交集檢查。')
    ch05['steps'].extend(steps)
    data['version']='v019 · 2026-10-27'
    data['description']='12章詳細操作參照；v019追加手工盒蓋單組雙軸連動及手動更新後重開驗證。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v018.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualBoxLidLinkageVerification']={'summary':ref,'scenes':scene_refs,'testedChangeMm':[[80,50],[90,60]],
        'cavityRequiresManualUpdate':True,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV019']='核對56張原圖與數位讀值；僅記錄單組盒蓋雙軸及手動內腔更新，不依原 Y run 的 X 誤標描述。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v019')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v018 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v019 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
