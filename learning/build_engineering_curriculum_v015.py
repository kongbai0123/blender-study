"""Append the observed manual X sketch refresh, preserving v014 and learner state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v014.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v015.json'
SOURCE_SHA = '2cdac81abf6bd8163069846a837a2c8d78b48438b0eda01e8c2ba5481d058db1'
BASE = 'learning/evidence/parametric/'
SUMMARY = BASE + '2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json'
SUMMARY_SHA = '939576faf65242bffdafbe873116df6378811f19a06694165668f288c0fa216d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path, expected, label, kind):
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file() or sha(target) != expected:
        raise ValueError('missing or changed: ' + path)
    return {'path': path, 'sha256': expected, 'label': label, 'type': kind}


def main():
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v014 baseline changed')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    ref = checked(SUMMARY, SUMMARY_SHA, 'X 尺寸與手動更新驗證摘要', 'verification-json')
    result = json.loads((ROOT / SUMMARY).read_text(encoding='utf-8-sig'))
    if result['kind'] != 'x-driver-requires-manual-sketch-solve':
        raise ValueError('unexpected demonstration')
    if result['saved_x70_before_solve']['outerX'] != [0,70] or result['saved_x70_before_solve']['cutterX'] != [2,58] or result['saved_x70_before_solve']['wallBoundaryDifferences'] != [2,12]:
        raise ValueError('unexpected pre-refresh geometry')
    if result['after_manual_sketch_update']['cutterX'] != [2,68] or result['after_manual_sketch_update']['wallBoundaryDifferences'] != [2,2] or result['after_manual_sketch_update']['constraintX'] != 66:
        raise ValueError('unexpected post-refresh geometry')
    scene = result['scene']
    scene_ref = checked(BASE + scene['file'], scene['sha256'], 'X70、尚未手動更新的試驗場景（非完成品）', 'scene-blend')
    images = result['images']
    if len(images) != 14:
        raise ValueError('expected 14 raw screenshots')
    lookup = {}
    for item in images:
        path = BASE + item['file']
        checked(path, item['sha256'], item['file'], 'screenshot')
        lookup[Path(item['file']).name] = item
    if len(lookup) != 14:
        raise ValueError('duplicate screenshot')
    def fig(name, caption):
        item = lookup[name]
        return {'type':'screenshot', 'path':BASE+item['file'], 'sha256':item['sha256'], 'caption':caption}
    common = [
        '獨立 Blender 5.2.1／CAD Sketcher 0.32.1；插件由程式啟用，檔案瀏覽器路徑由程式填入；選取、草圖欄位及更新由 GUI 事件操作。',
        '改外框後 Driver 欄位可顯示66 mm，但切割體仍是舊幾何；必須進內腔草圖手動按更新，這次讀回幾何才跟隨，不能當成全自動同步。',
        '兩側2／12及2／2 mm為程式讀回外框與切割體界限之差，並非直接從圖片量得，也未驗證布林後實際壁厚或閉合性。',
        'X70 場景存檔重開時仍是手動更新前的舊切割體；更新後狀態此次沒有另存。Y Driver、上蓋及盒蓋連動未完成。',
        '重開畫面有 sketcher.slvs_select 工具未找到提示，原因未知；若自己的畫面出現提示，先停下並回報。實體列印、量測和試配尚未進行。',
    ]
    steps = [
        ('ch04-x-refresh-01','點選盒體並進入外框草圖','確認活動物件及外框草圖','Object Mode；畫面可見盒體的側面。',
         ['點盒體可見側面，確認活動物件為 Body。','右鍵選 Edit Sketch，再選 Body Sketch。'],
         '原圖可見 Body 為活動物件與外框草圖；使用側面避開本次被截切的 Outliner 列。',
         [('EDIT-01-opened.png','原圖：開啟 X driver 場景，起初活動物件為 Body.001。'),('EDIT-02-select-body.png','原圖：點選盒體側面後 Body 被選取。'),('EDIT-03-context-menu.png','原圖：Body 的 Edit Sketch 選單。'),('EDIT-04-body-sketch.png','原圖：進入 Body Sketch，側欄顯示60／40 mm。')],[ref]),
        ('ch04-x-refresh-02','將 X 改為70並另存','觀察外框尺寸與存檔','Body Sketch；第一個 Distance 是本次 X 尺寸。',
         ['將第一個 Distance 由60改為70 mm。','另存本次獨立示範版本，再重新開啟。'],
         '圖中欄位顯示70 mm；另存重開後外框 X0～70，切割體仍 X2～58，兩側界限差2／12 mm；幾何界限依程式讀值。',
         [('EDIT-06-x70.png','原圖：外框 X 改為70 mm。'),('EDIT-07-saved.png','原圖：獨立試驗場景已另存。'),('EDIT-08-reopened.png','原圖：重開場景；具體界限以讀值為準。')],[scene_ref,ref]),
        ('ch04-x-refresh-03','進入內腔草圖','區分欄位更新與幾何更新','重開 X70 試驗場景並確認 Body。',
         ['離開外框草圖，右鍵選 Edit Sketch 中的 Body.001 Sketch。','核對紫色 Driver 尺寸欄位及摘要中的切割體界限。'],
         '畫面顯示內部 Driver 欄位66 mm，但更新前切割體仍為 X2～58；欄位值不是幾何已同步的證據。',
         [('UPDATE-01-opened.png','原圖：重開 X70 場景，底部出現工具未找到提示。'),('UPDATE-02-leave-outer.png','原圖：離開外框草圖。'),('UPDATE-03-context-menu.png','原圖：選擇 Body.001 Sketch。'),('UPDATE-04-enter-inner.png','原圖：內部草圖的 Driver 欄位顯示66 mm；更新前界限依程式讀值。')],[ref]),
        ('ch04-x-refresh-04','手動更新內腔草圖','驗證這次 X 尺寸的手動更新','Body.001 Sketch；欄位顯示66 mm。',
         ['點 Sketcher 面板頂端 Leave 按鈕右邊的更新圖示。','離開內腔草圖，對照程式讀回的切割體界限。'],
         '本次更新後切割體 X2～68，兩側界限差2／2 mm；讀值結果只適用本次 X70 試驗。',
         [('UPDATE-05-solve-inner.png','原圖：點更新後的內腔草圖；66 mm 欄位與幾何界限應分開看。'),('UPDATE-06-leave-inner.png','原圖：離開內腔草圖；界限由程式讀回。')],[ref]),
    ]
    new = [{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
            'shortcuts':[],'figures':[fig(name, caption) for name,caption in figures], 'sourceSteps':[],
            'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts}
           for id,title,goal,context,actions,success,figures,artifacts in steps]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch04')
    old = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old) != 217 or any(s['id'] in old for s in new):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(new)
    chapter['limitations'].append('X70 的內腔切割體須手動更新草圖才跟隨；結果尚未另存，Y／上蓋待驗，布林後壁厚與閉合性未驗。')
    data['version'] = 'v015 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v015追加 X Driver 的手動草圖更新與數位界限驗證。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v014.json','sha256':SOURCE_SHA}, {'path':SUMMARY,'sha256':SUMMARY_SHA}])
    data['manualXRefreshVerification'] = {'summary':ref,'sceneBeforeRefresh':scene_ref,'automaticSync':False,
        'savedAfterRefresh':False,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV015'] = '原圖、程式讀值及手動草圖更新分列；X70場景保存於更新之前，未將此例稱為全自動連動。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v015')
    if SOURCE.read_bytes() != before:
        raise ValueError('v014 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Created v015 with',sum(len(c['steps']) for c in data['chapters']),'steps')


if __name__ == '__main__':
    main()
