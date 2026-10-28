"""Append partial native GUI driver trial without advancing its failed checks."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v013.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v014.json'
SOURCE_SHA = 'bc2a3c04290ba7ee5db56ffa14b7045549b6e4a2ec456a72b96da75246382103'
BASE = 'learning/evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/'
SUMMARY_SHA = 'bcf1fda35c8305f7de44fe7931c7986522e257bc40e4018d346f6dc0cb16bda2'
RETRY_BASE = 'learning/evidence/parametric/2026-10-27-cad-sketcher-x-driver-resize-v001/'
RETRY_SHA = '43556bc29e0a039d45538ecf677b20f113ac43e9cf7f7b9676e1c91ae6b1046c'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path: str, expected: str, label: str, kind: str) -> dict:
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file() or sha(target) != expected:
        raise ValueError('missing, invalid or changed: ' + path)
    return {'path': path, 'sha256': expected, 'label': label, 'type': kind}


def main() -> None:
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v013 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    summary_ref = checked(BASE + 'native-driver-xy-partial-verification-v001.json', SUMMARY_SHA, '原生 Driver 部分成功與失敗試驗摘要', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    retry_ref = checked(RETRY_BASE + 'x-driver-resize-failed-verification-v001.json', RETRY_SHA, 'X Driver 後續尺寸重試失敗摘要', 'verification-json')
    retry = json.loads((ROOT / retry_ref['path']).read_text(encoding='utf-8-sig'))
    if retry['runnerStatus'] != 'failed' or retry['activeObject'] != 'Body.001' or retry['activeSketch'] is not None:
        raise ValueError('unexpected X retry state')
    retry_img = checked(RETRY_BASE + 'EDIT-02-context-menu.png', '2886d03599476788deb7d712dba949cfdb3ecdf1b721ae88d0c62904fd605745', 'X 重試時 Edit Sketch 停用原圖', 'screenshot')
    if summary['kind'] != 'partial-native-driver-gui-probe' or not summary['overallXYValidation'].startswith('failed'):
        raise ValueError('unexpected trial scope')
    driver = summary['xDriver']
    if (driver['expression'] != 'slvs_c_b596b36138076155-4' or driver['valid'] is not True or
        driver['baseOuterLengthMm'] != 60 or driver['baseCavityLengthMm'] != 56 or
        driver['savedAndReopened'] is not True or driver['testedOuterDimensionChange'] is not False):
        raise ValueError('unexpected X driver result')
    if (summary['reopened']['outerBoundsMm'] != [[0,60],[0,40],[0,30]] or
        summary['reopened']['cutterBoundsMm'] != [[2,58],[2,38],[2,30]] or summary['reopened']['driverCount'] != 1):
        raise ValueError('unexpected reopened geometry')
    scene_hashes = ['0d697fdf4d20bd6ff6999be64296949e8bcb0f90e7245079c9c0ce4e76bca0ec', 'fe77918de7c1eb80bc9e2bfa17371b879e0ba1b33eef8451ad398ba61c8bd04e']
    if len(summary['scenes']) != 2:
        raise ValueError('unexpected scenes')
    scenes = []
    for f, expected in zip(summary['scenes'], scene_hashes):
        if f['sha256'] != expected or f['actualOuterMm'] != [60,40,30]:
            raise ValueError('unexpected saved scene result')
        label = 'X 單一 Driver 草案；實際60×40×30 mm' if not scenes else '70x50 名稱但實際60×40×30 mm 的失敗探測'
        scenes.append(checked(BASE + f['file'], expected, label, 'scene-blend'))
    images = summary['images']
    if len(images) != 29:
        raise ValueError('expected 29 screenshots')
    lookup = {}
    for f in images:
        if f['file'] in lookup:
            raise ValueError('duplicate screenshot name')
        checked(BASE + f['file'], f['sha256'], f['file'], 'screenshot')
        lookup[f['file']] = f
    def fig(name: str, caption: str) -> dict:
        f = lookup[name]
        return {'type': 'screenshot', 'path': BASE + name, 'sha256': f['sha256'], 'caption': caption}
    def figures(items):
        return [fig(name, caption) for name,caption in items]
    common = [
        '獨立 Blender 的固定盒複本；CAD Sketcher 由程式啟用、檔案視窗路徑及名稱由程式填入；欄位選單及 Driver 以 GUI 事件操作。',
        '已建立的只有 X 內部尺寸的一個 Driver：本例外長60、內長56，表達式為 slvs_c_b596b36138076155-4；變數名稱取決於該來源，不能硬套其他場景。',
        '此 Driver 初值有效且已另存重開，但未成功改變外框尺寸驗證其動態跟隨；Y Driver 未建立，X70／Y50 未生效，上蓋未建立。',
        '切回外框草圖未成功，XY-01 畫面與程式狀態均顯示無活動草圖；原 run 後續預期標籤不能當成成功紀錄。',
        '第二個場景檔名含70x50，但實際重開外框仍60×40×30 mm，為失敗探測而非完成品；讀值與圖片分開。',
        '布林後內腔、閉合性、實體列印、量測及試配尚未驗證；0.4 mm 總間隙仍是試驗值。',
    ]
    sections = [
        ('ch04-driver-partial-01','選取 X 驅動來源','辨認外框來源尺寸','固定盒獨立副本；Object Mode、選取 Body。',
         ['右鍵 Body，選 Edit Sketch > Body Sketch，觀察側欄第一個 Distance。','右鍵 X60 mm 欄位，選 Copy as New Driver。'],
         '畫面顯示60／40及來源欄位選單；選單操作由本次 GUI 事件紀錄。',
         figures([('EDIT-01-opened.png','原圖：固定盒副本。'),('EDIT-02-context-menu.png','原圖：Body 的 Edit Sketch 子選單。'),('EDIT-03-body-sketch.png','原圖：外框 Body Sketch。'),('EDIT-04-sidebar.png','原圖：側欄顯示60／40 mm。'),('DRIVER-01-source-context.png','原圖：來源欄位選單含 Copy as New Driver。'),('DRIVER-02-copy-source.png','原圖：複製後欄位畫面；複製動作依事件紀錄。')]),[summary_ref]),
        ('ch04-driver-partial-02','進入內部草圖','辨認本次 Driver 目標','離開外框草圖；選取本次 Body。',
         ['右鍵 Body，選 Edit Sketch > Body.001 Sketch。','查看本次內部草圖側欄中的56／36／28／18 mm。'],
         '畫面顯示 Body.001 Sketch 及其尺寸；本次第一個 Distance 為內部 X 長度。',
         figures([('DRIVER-03-select-cutter-menu.png','原圖：Edit Sketch 子選單。'),('DRIVER-04-cutter-sketch.png','原圖：內部草圖四個尺寸欄位。')]),[summary_ref]),
        ('ch04-driver-partial-03','貼上來源 Driver','觀察來源貼到內部 X 欄位','Body.001 Sketch，右側第一個 Distance 本次原值56 mm。',
         ['右鍵內部 X 尺寸，選 Paste Driver。','對照欄位顏色和此時的數值。'],
         '畫面顯示欄位變紫、暫時為60 mm；此刻尚未輸入減4公式。',
         figures([('DRIVER-05-target-context.png','原圖：目標欄位選單含 Paste Driver。'),('DRIVER-06-pasted.png','原圖：貼上後目標欄位顯示60 mm。')]),[summary_ref]),
        ('ch04-driver-partial-04','編輯 X Driver 公式','設定此試驗的外長減4','在已貼上的內部 X 欄位操作；此例生成的變數名稱須依實際 Driver。',
         ['右鍵目標欄位選 Edit Driver，在 Type 選 Scripted Expression。','依此例變數名稱加上 −4；核對輸入後的值。'],
         '畫面可見 Scripted Expression 與56 mm；程式讀回一個有效 X Driver，初值60−4=56，不等於已測變尺寸後的連動。',
         figures([('DRIVER-07-edit-context.png','原圖：目標選單含 Edit Driver。'),('DRIVER-08-edit-popup.png','原圖：初始 Driver 編輯視窗。'),('DRIVER-09-type-menu.png','原圖：Type 選單中的 Scripted Expression。'),('DRIVER-10-script-type.png','原圖：Scripted Expression 的變數。'),('DRIVER-11-formula-attempt.png','原圖：本例輸入減4後 Driver Value 56、欄位56 mm。')]),[summary_ref]),
        ('ch04-driver-partial-05','辨認切回草圖失敗','停止後續未完成的 Y 與動態試驗','試圖從內部草圖返回外框草圖之後。',
         ['對照失敗畫面及摘要的活動草圖讀值。'],
         '畫面未進入外框草圖，程式讀回 activeSketch null；後續未建立 Y Driver，X70／Y50 未生效。另一次獨立重試中 Body.001 活動、Edit Sketch 灰色停用，原因未確認，X70 仍未生效。',
         figures([('XY-01-outer-sketch.png','原圖：嘗試切回後並未進入草圖；不可依檔名認為切回成功。')]) + [{'type':'screenshot','path':retry_img['path'],'sha256':retry_img['sha256'],'caption':'另一次獨立重試原圖：Body.001 活動時 Edit Sketch 灰色停用；未進外框草圖，原因未知。'}],[summary_ref,retry_ref]),
        ('ch04-driver-partial-06','保存失敗探測並核對','以實際讀值辨認檔名與結果的差異','本次隔離示範，保留初始及後續兩份草案。',
         ['對照另存與重開原圖，核對摘要與兩個檔案雜湊。','以程式讀值確認尺寸與 Driver 數量。'],
         '兩次另存，後續重開時程式讀回一個 X Driver、外框仍60×40×30；雖第二檔名含70x50，尺寸變更並未成功。',
         figures([('XY-10-before-change-saved.png','原圖：單一 X Driver 草案另存。'),('XY-11-x70.png','原圖：預期 X70 未生效，畫面未顯示外框尺寸輸入。'),('XY-12-x70y50.png','原圖：與前圖相同；預期 Y50 未生效。'),('XY-13-after-change-saved.png','原圖：名稱含70x50 的探測檔已另存，但不能由名稱推定尺寸。'),('XY-14-reopened.png','原圖：重開畫面；實際尺寸由程式讀值。')]),scenes+[summary_ref]),
    ]
    steps = [{'id':id,'title':title,'goal':goal,'context':context,'actions':actions,'success':success,
              'shortcuts':[],'figures':figs,'sourceSteps':[],'evidenceStatus':'existing_demo',
              'limitations':list(common),'artifacts':artifacts} for id,title,goal,context,actions,success,figs,artifacts in sections]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch04')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 211 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('後續原生 GUI Driver 試驗僅建立 X 單 Driver，外框變動與 Y 尚未成功；名稱含70x50的試驗檔實際仍60×40。')
    data['version'] = 'v014 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v014追加原生 GUI 單一 Driver 的部分成果與失敗探測，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v013.json','sha256':SOURCE_SHA}, {'path':summary_ref['path'],'sha256':SUMMARY_SHA}, {'path':retry_ref['path'],'sha256':RETRY_SHA}])
    data['nativeDriverPartialVerification'] = {'summary':summary_ref, 'retrySummary':retry_ref, 'scenes':scenes,
        'scope':'X 單 Driver 初值與重開；切回外框失敗，未測外框變更，Y Driver 未建。',
        'physicalMeasurements':None, 'fitResults':None, 'qualifiedClearanceMm':None}
    data['contentReview']['supplementV014'] = '記錄真實 X 單 Driver GUI 操作、未完成與錯誤檔名；不採原 run 預期標籤作為已完成。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v014')
    if SOURCE.read_bytes() != before:
        raise ValueError('v013 changed during build')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
