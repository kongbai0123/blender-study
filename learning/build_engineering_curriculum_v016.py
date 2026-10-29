"""Append the observed X/Y driver trial with an explicit manual sketch update."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v015.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v016.json'
SOURCE_SHA = 'bda0d3bf053de582bfd359cc109abcdab52eda7f362e3c30cccb44423143693f'
BASE = 'learning/evidence/parametric/'
SUMMARY = BASE + '2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json'
SUMMARY_SHA = '1b8ed3dc2ccbdfffc2220d890f32256fd209fd774d607d72054c1980a24429d7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path, expected, label, kind):
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file() or sha(target) != expected:
        raise ValueError('missing or changed: ' + path)
    return {'path':path, 'sha256':expected, 'label':label, 'type':kind}


def main():
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v015 baseline changed')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref = checked(SUMMARY,SUMMARY_SHA,'X／Y 驅動與手動更新驗證摘要','verification-json')
    result = json.loads((ROOT / SUMMARY).read_text(encoding='utf-8-sig'))
    if (result['kind'] != 'manual-sketch-xy-drivers-manual-update' or result['sourceDimensionsMm'] != [70,40,30] or
        result['modifiedDimensionsMm'] != [80,50,30]):
        raise ValueError('unexpected trial scope')
    pre = result['beforeManualUpdate']
    post = result['afterManualUpdateAndReopen']
    if (pre['outerX'],pre['outerY'],pre['cutterX'],pre['cutterY']) != ([0,80],[0,50],[2,68],[2,38]):
        raise ValueError('unexpected pre-update geometry')
    if (post['outerX'],post['outerY'],post['cutterX'],post['cutterY']) != ([0,80],[0,50],[2,78],[2,48]):
        raise ValueError('unexpected reopened geometry')
    if post['boundaryDifferencesX'] != [2,2] or post['boundaryDifferencesY'] != [2,2] or post['driversValid'] != 2:
        raise ValueError('unexpected boundaries or driver state')
    scenes = result['scenes']
    expected_scenes = ['6f4f42aaef1fd9e071efa226008ca19d4298fae43fe3e83a4e8cb22bde722f3a','4a1f17587a8158567d4f85b232e7ff3772a1c1eeb663c0ccb44b21622ee614cc']
    if len(scenes) != 2 or [s['sha256'] for s in scenes] != expected_scenes:
        raise ValueError('unexpected scenes')
    scene_refs = [checked(BASE+s['file'],s['sha256'],label,'scene-blend') for s,label in zip(scenes,['X／Y 驅動初始示範場景','X80 Y50 手動更新後另存場景'])]
    images = result['images']
    if len(images) != 24:
        raise ValueError('expected 24 original screenshots')
    lookup = {}
    for item in images:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot')
        lookup[Path(item['file']).name] = item
    if len(lookup) != 24:
        raise ValueError('duplicate screenshot')
    def fig(name,caption):
        item=lookup[name]
        return {'type':'screenshot','path':BASE+item['file'],'sha256':item['sha256'],'caption':caption}
    common = [
        '獨立 Blender 5.2.1／CAD Sketcher 0.32.1；插件由程式啟用，檔案對話框路徑由程式填入；欄位選單、改值與更新由 GUI 事件操作。',
        '兩個 Driver 欄位變化不代表幾何已更新：本次必須進入內腔草圖手動按更新。此流程並非自動同步，適用範圍為這次示範的模型與測試尺寸。',
        '重開後外框與切割體邊界、2 mm 差值及兩個有效 Driver 由程式讀回，不是從畫面直接量得；尚未驗證布林後實際壁厚與閉合性。',
        '起始重開畫面有 sketcher.slvs_select 工具未找到提示，原因未知；若個人畫面出現此提示，先停下並回報。',
        '上蓋、盒蓋連動與實體列印、量測、試配尚未完成；0.4 mm 總間隙仍為試驗值，不是合格值。',
    ]
    steps = [
        ('ch04-xy-driver-01','複製外框 Y 尺寸作 Driver 來源','辨認 Y 尺寸來源','本次外框 Body Sketch 為70×40 mm；第二個 Distance 是 Y。',
         ['右鍵第二個 Distance，選 Copy as New Driver。','離開外框草圖，從 Body 的 Edit Sketch 選 Body.001 Sketch。'],
         '畫面顯示外框70／40 mm及來源選單；複製事件依本次 GUI 紀錄。',
         [('Y-01-opened.png','原圖：70×40 外框；底部顯示工具提示。'),('Y-02-source-menu.png','原圖：Y 欄位選單含 Copy as New Driver。'),('Y-03-copied.png','原圖：複製後外框畫面；複製動作依事件紀錄。'),('Y-04-sketch-menu.png','原圖：選取內腔草圖的選單。'),('Y-05-inner-sketch.png','原圖：進入內腔草圖。')],[ref]),
        ('ch04-xy-driver-02','建立內腔 Y Driver','讓 Y 欄位引用外框 Y','Body.001 Sketch；本例第二個 Distance 是內腔 Y。',
         ['右鍵第二個 Distance，選 Paste Driver。','選 Edit Driver，改為 Scripted Expression，使用本次來源變數減4。'],
         '貼上時內腔 Y 暫為40 mm；公式輸入後顯示36 mm。本例變數名稱由場景決定，不能硬套別的場景。',
         [('Y-06-target-menu.png','原圖：目標欄位選單含 Paste Driver。'),('Y-07-pasted.png','原圖：貼上後 Y 欄位暫顯40 mm。'),('Y-08-edit-context.png','原圖：目標欄位選單含 Edit Driver。'),('Y-09-edit-popup.png','原圖：Driver 編輯視窗。'),('Y-10-type-menu.png','原圖：Type 選單中的 Scripted Expression。'),('Y-11-script-type.png','原圖：Scripted Expression 與來源變數。'),('Y-12-formula.png','原圖：來源變數減4後 Driver Value 與欄位顯示36。')],[ref]),
        ('ch04-xy-driver-03','手動更新並保存驅動草案','保存本次 X／Y Driver 草案','Body.001 Sketch，兩個內腔欄位各有 Driver。',
         ['點草圖頂端 Leave 按鈕右邊的更新圖示。','另存獨立示範版本。'],
         '畫面顯示兩個紫色欄位及另存訊息；檔案 SHA 與讀值依摘要。',
         [('Y-13-solve.png','原圖：內腔草圖手動更新後。'),('Y-14-saved.png','原圖：X／Y Driver 草案另存。')],[scene_refs[0],ref]),
        ('ch04-xy-driver-04','外框改為80×50 mm','檢查外框與尚未更新的切割體','重開 X／Y Driver 草案；切換到 Body Sketch。',
         ['離開內腔草圖、點盒體側面選 Body，進入 Body Sketch。','將 X 改為80、Y 改為50 mm。'],
         '畫面顯示外框80／50；手動更新前程式讀回切割體仍為 X2～68、Y2～38，欄位跟隨不等於幾何跟隨。',
         [('VERIFY-01-opened.png','原圖：重開草案；底部顯示工具提示。'),('VERIFY-02-leave-inner.png','原圖：離開內腔草圖。'),('VERIFY-03-select-body.png','原圖：選取 Body。'),('VERIFY-04-sketch-menu.png','原圖：選擇 Body Sketch。'),('VERIFY-05-outer-sketch.png','原圖：外框草圖起始70／40 mm。'),('VERIFY-06-outer-80x50.png','原圖：外框欄位顯示80／50 mm。')],[ref]),
        ('ch04-xy-driver-05','手動更新並重開核對','核對 X／Y 兩軸切割體界限','外框80×50 mm；切換進入 Body.001 Sketch。',
         ['對照兩個 Driver 欄位，點頂端更新圖示。','另存獨立版本並重開，核對摘要。'],
         '重開後程式讀回切割體 X2～78／Y2～48，兩軸各側界限差2 mm，兩個 Driver 有效；限於本次80×50尺寸與手動更新流程。',
         [('VERIFY-07-inner-before-solve.png','原圖：更新前 Driver 欄位顯示76／46 mm；舊切割體界限依讀值。'),('VERIFY-08-inner-after-solve.png','原圖：點更新後內腔草圖。'),('VERIFY-09-saved.png','原圖：更新後試驗版本另存。'),('VERIFY-10-reopened.png','原圖：重開後內腔草圖；實際界限與 Driver 狀態依讀值。')],[scene_refs[1],ref]),
    ]
    new = [{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name,caption) for name,caption in figures],'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in steps]
    chapter=next(c for c in data['chapters'] if c['id']=='ch04')
    old={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old)!=221 or any(s['id'] in old for s in new):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(new)
    chapter['limitations'].append('本次 X／Y Driver 試驗從70×40改80×50，內腔草圖手動更新並另存重開後切割體兩軸各側界限差2 mm；不是自動同步，布林後壁厚與閉合性未驗。')
    data['version']='v016 · 2026-10-27'
    data['description']='12章詳細操作參照；v016追加 X／Y Driver 在手動更新及保存重開後的數位界限驗證。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v015.json','sha256':SOURCE_SHA},{'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualXYUpdateVerification']={'summary':ref,'scenes':scene_refs,'automaticSync':False,
        'testedOuterDimensionsMm':[[70,40,30],[80,50,30]],'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV016']='逐圖核對來源與目標欄位，區分 Driver 欄值、手動更新前後幾何和重開讀值；不聲稱實體配合。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v016')
    if SOURCE.read_bytes()!=before:
        raise ValueError('v015 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v016 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__=='__main__':
    main()
