"""Copy v002 as v003, append verified parametric-box teaching, preserve IDs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V002 = ROOT / 'learning/web/engineering-curriculum-v002.json'
V003 = ROOT / 'learning/web/engineering-curriculum-v003.json'
EXPECTED_V002 = 'bb02ba7511162d1de1ae08ce710274b8839568af485da7a8ed8a621b2a64d495'
SUMMARY = 'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/parametric-box-verification-v004.json'
EXPECTED_SUMMARY = '50d3691ddef18f08f6c82712514aa1841a9660e07577a06592357424533f193d'
SWEEP = 'learning/evidence/parametric/2026-10-27-cad-sketcher-parameter-sweep-v001/parameter-sweep-verification-v001.json'
EXPECTED_SWEEP = '1d41fae0c2551564f327d653c0fb4b0a3c6ca823db7cd587fbe06b8654774c01'


def digest(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def ref(rel, expected, label):
    actual = digest(rel)
    if actual != expected:
        raise ValueError(f'hash mismatch: {rel}')
    return {'path': rel, 'label': label, 'sha256': actual}


def picture(rel, expected, caption):
    result = ref(rel, expected, caption)
    return {'type': 'screenshot', 'path': result['path'], 'sha256': result['sha256'], 'caption': caption}


def microstep(ident, title, goal, context, actions, success, image, evidence_status, limits, artifacts=()):
    return {'id': ident, 'title': title, 'goal': goal, 'context': context, 'actions': actions,
            'success': success, 'shortcuts': [], 'figures': [image], 'sourceSteps': [],
            'evidenceStatus': evidence_status, 'limitations': limits, 'artifacts': list(artifacts)}


def main():
    before = V002.read_bytes()
    if hashlib.sha256(before).hexdigest() != EXPECTED_V002:
        raise ValueError('v002 differs from the documented baseline; inspect before building.')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary = ref(SUMMARY, EXPECTED_SUMMARY, '參數盒 v004 安全驗證摘要')
    sweep = ref(SWEEP, EXPECTED_SWEEP, '八組單參數程式掃描與數位讀值（未保存）')
    source = 'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/'
    scenes = [
        ref(source+'demo-files/parametric_box_80x40_v003.blend', 'a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2', '80×40 場景 v003（獨立示範原檔）'),
        ref(source+'demo-files/parametric_box_60x40_v001.blend', '4c938ccfb74c5a88a6dc6d2fc73ebb670a132d54400ebe63e78b82b9182468be', '60×40 場景 v001（獨立示範原檔）'),
    ]
    image70 = picture(source+'CAD-BOX-07-reopened-edit-70.png', 'aefd3e693d14afd5b7d5060f682be85f2b0b776972a888c408deaf38492beb9b', '獨立 Blender 原圖：重開後以 Sketcher 側欄改為 70×40 mm；側欄可見尺寸與 Fully defined。')
    image80 = picture(source+'CAD-BOX-04-changed-80.png', '29537f86d3385d37c7398beb233403e5c66c481c98c807951ae66d91103f860a', '獨立 Blender 原圖：原試驗由60改至80 mm的側欄結果；此圖本身不顯示實體間隙。')
    model = picture(source+'CAD-BOX-09-model-80.png', '229488b76819ae55b86bf62d51e6a51d18471591894d916e892dc7ddf6f30862', '獨立 Blender 原圖：80 mm 名義尺寸的盒蓋組裝外觀；圖片不能證明內腔或間隙的尺寸。')
    reopened = picture(source+'CAD-BOX-06-reopened-80.png', '53d7b4073d8bf4659496bd8fc213184fb335a94c277d05f3e7d566ce4c548fcc', '獨立 Blender 原圖：已重開的80×40草圖，側欄顯示Fully defined。')
    common = ['盒體／上蓋網格與頂點驅動由程式建立；只有草圖尺寸變更是 Blender GUI 原生事件，不是完整手工建模。',
              '只有 X 長度做過 GUI 變更；另有八組其他參數的單變數程式掃描，非 GUI 操作、非草圖Y求解或保存重開，不代表任意參數組合皆有效。',
              '0.4 mm 水平總間隙是數位草案；實際列印、量測與試配均未執行，不是合格間隙。',
              '使用自動頂點驅動而非 CAD 特徵樹；更改約束ID、刪除草圖或直接改網格可能破壞連動。']
    launch_limit = common + ['啟動器僅在這台已具隔離 CAD Sketcher 0.32.1 環境的電腦可用；目前只測過背景 bootstrap，尚未驗證使用者互動啟動。',
                             '若目標檔名已存在，改用未使用的新版本名稱；先保存來源原檔。']
    steps = [
      microstep('ch05-linked-01', '開啟可編輯的隔離副本', '保護示範原檔，準備自己的80 mm副本',
        'Windows PowerShell；工作目錄是 Blender-Learning 專案根目錄；目標檔名不可已存在。',
        ['在 PowerShell 執行：python learning/tutor/open_parametric_box.py --copy-to learning/workspaces/engineering-parametric/my_box_v001.blend'],
        '預期建立80×40 mm個人副本並開啟 Blender；互動啟動結果仍待實際操作確認。', model, 'draft_pending_demo', launch_limit, [*scenes, summary, sweep]),
      microstep('ch05-linked-02', '將草圖 X 長度改為70 mm', '用已存在的驅動尺寸變更盒體與上蓋',
        '隔離 Blender 5.2.1、CAD Sketcher 0.32.1；已開啟個人副本及 Body Sketch；右側 Sketcher > Constraints > Dimensional。',
        ['將第一個 Distance 從80 mm改成70 mm，確認第二個 Distance仍為40 mm。'],
        '側欄顯示70／40與Fully defined；助教重開後的數位讀值為盒體70×40×30 mm。', image70, 'existing_demo', common),
      microstep('ch05-linked-03', '改回80 mm並查看連動', '比較相同草圖主控變更後的模型',
        'Body Sketch，右側 Sketcher > Constraints > Dimensional；作用中為第一個 Distance。',
        ['將第一個 Distance 改為80 mm，再點 Leave: Body Sketch 觀察模型。'],
        '草圖側欄80／40且 Fully defined；數位讀回盒體80×40×30、內腔76×36×28、唇外75.6×35.6 mm、四側約0.2 mm。', image80, 'existing_demo', common + ['80尺寸截圖來自原試驗60→80的操作；70→80的後續恢復另由重開試驗讀回核對。', '內腔與四側數值由程式讀值，並非這張截圖可直接量取。']),
      microstep('ch05-linked-04', '另存並重新開啟', '將尺寸變更與場景版本分開保留',
        '自己的工程副本；File > Save As，選新名稱，並保留來源場景。',
        ['另存新的 .blend 版本，再重新開啟，查看 Body Sketch 尺寸與模型。'],
        '助教示範重開後80／40及 DoF 0 仍成立，數位盒與蓋的讀值一致；你的檔案仍須自己核對。', reopened, 'existing_demo', common + ['原試驗的檔案視窗路徑由程式填入、確認透過 GUI 事件；不是逐字手動輸入。'])]
    ch05 = next(c for c in data['chapters'] if c['id'] == 'ch05')
    if any(s['id'] in {x['id'] for x in ch05['steps']} for s in steps):
        raise ValueError('new IDs conflict with existing steps')
    ch05['steps'].extend(steps)
    data['version'] = 'v003 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v003補入程式生成與驅動的參數盒實證，原學員事件仍沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v002.json', 'sha256': EXPECTED_V002},
                                   {'path': summary['path'], 'sha256': summary['sha256']},
                                   {'path': sweep['path'], 'sha256': sweep['sha256']}])
    data['parametricBoxVerification'] = {'summary': summary, 'parameterSweep': sweep, 'scenes': scenes, 'scope': '草圖X長度60→80及重開後80→70→80的GUI數位連動；其餘八組是程式單參數掃描，非GUI、非草圖Y求解或保存重開，不證明任意組合。',
        'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV003'] = '新增參數盒實證教學；程式生成網格／驅動與 GUI 尺寸變更分開，啟動器互動待驗。'
    if V003.exists():
        raise FileExistsError('refusing to overwrite v003')
    if V002.read_bytes() != before:
        raise ValueError('v002 changed during build')
    V003.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {V003}: {sum(len(c['steps']) for c in data['chapters'])} microsteps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
