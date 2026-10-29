"""Append independently verified Y-dimension GUI steps without changing v007."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v007.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v008.json'
SOURCE_SHA = '479e9a60679a091079f0a6011019338bbd4e8ff0ba4ccd89f6c616ee1571ec86'
BASE = 'learning/evidence/parametric/2026-10-27-cad-sketcher-y-dimension-v001/'
SUMMARY_SHA = '0a311ba7571fddb2fc5e91036a81f53200bd25624f2f4f4f72970ec36649ef2f'
WARNING_SHA = '4336c07476aac36dca167bb8ed1f22e4e620c9bfabb72bca922adaf7642e21cb'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path: str, expected: str, label: str, kind: str) -> dict:
    item = (ROOT / path).resolve()
    if not item.is_relative_to(ROOT.resolve()) or not item.is_file():
        raise ValueError('missing or invalid source: ' + path)
    actual = digest(item)
    if actual != expected:
        raise ValueError('source hash mismatch: ' + path)
    return {'path': path, 'sha256': actual, 'label': label, 'type': kind}


def figure(path: str, expected: str, caption: str) -> dict:
    item = reference(BASE + path, expected, caption, 'screenshot')
    return {'type': 'screenshot', 'path': item['path'], 'sha256': item['sha256'], 'caption': caption}


def main() -> None:
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v007 differs from the documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary_ref = reference(BASE + 'y-dimension-verification-v001.json', SUMMARY_SHA,
                            'Y方向GUI試驗與六組數位核對摘要', 'verification-json')
    warning_ref = reference(BASE + 'y-reopen-warning-v001.json', WARNING_SHA,
                            'Y50重開畫面工具提示補充紀錄', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    if summary.get('runner', {}).get('status') != 'completed' or summary.get('runner', {}).get('exitCode') != 0:
        raise ValueError('Y trial did not complete')
    if len(summary.get('cases', [])) != 6 or any(case.get('checksPassed') != 12 for case in summary['cases']):
        raise ValueError('Y trial cases incomplete')
    reference(summary['source']['path'], summary['source']['sha256'], 'Y試驗來源場景', 'scene-blend')
    for item in summary.get('files', []):
        reference(item['path'], item['sha256'], item['path'], 'evidence')
    for case in summary['cases']:
        verification = json.loads((ROOT / case['verificationPath']).read_text(encoding='utf-8-sig'))
        checks = verification.get('checks', {})
        if len(checks) != 12 or not all(value is True for value in checks.values()):
            raise ValueError('Y trial case failed: ' + case['label'])
    if any(summary.get(key) is not None for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm')):
        raise ValueError('physical results must remain unfilled')
    scene_50 = reference(BASE + 'demo-files/parametric_box_80x50_y_v001.blend',
                         'ddccdbec04f61cb9017c40d3df0c6cdfe6b474c5e851f5c6759a6f8bece773d4',
                         'Y50 場景 v001（助教示範原檔）', 'scene-blend')
    scene_45 = reference(BASE + 'demo-files/parametric_box_80x45_y_v002.blend',
                         '7c7474156869de6b169be6eea8764be000c626b43021e51399889b1b0b591477',
                         'Y45 場景 v002（助教示範原檔）', 'scene-blend')
    img_50 = figure('CAD-Y-02-changed-80x50.png',
                    'e07bbfe8640a2a56f0d903d8861cff1254e67044e69af95b3d0e50d032fd7913',
                    '獨立 Blender 原圖：Body Sketch 側欄顯示80／50 mm及 Fully defined；盒蓋內腔與間隙須另看數位讀值，不能從這張圖直接量取。')
    img_reopen = figure('CAD-Y-04-reopened-80x50.png',
                        'ab5d2a09d5b580e8e612263fc5e8aa7d73f3cc9048fb3acfbc40cceddd6e13b4',
                        '獨立 Blender 原圖：重開後側欄顯示80／50 mm；畫面底部出現 sketcher.slvs_select 工具未找到的黃色提示，原因與影響尚待核對。')
    img_45 = figure('CAD-Y-05-reopened-changed-80x45.png',
                    'c4b6fd33111449e44f061c9a6c836756301db294782376b1f051175c0f3851c2',
                    '獨立 Blender 原圖：重開後將第二個尺寸改為45 mm，側欄顯示80／45 mm及 Fully defined；幾何尺寸由程式另行讀值。')
    img_saved = figure('CAD-Y-06-saved-80x45.png',
                       '4119b508504f89b1b13894777f54c411906597b9f94d90d6bf4f4fca497fa71e',
                       '獨立 Blender 原圖：Y45版本保存後的視窗；檔案內容與數位尺寸另依驗證摘要核對。')
    common = [
        '起始盒體／上蓋網格與驅動器由程式建立；這次只有第二個草圖尺寸的改動透過 Blender GUI 事件，並非手工完成盒蓋建模。',
        '只驗證本次80×40→80×50與重開後80×45 mm等指定數位案例；不能推論其他任意尺寸或所有參數組合有效。',
        '名義0.4 mm水平總間隙只屬幾何試驗值；實體列印、量測、試配與合格間隙均尚未取得。',
        '場景另存／開啟的檔案瀏覽器路徑及名稱由程式填入、確認以 GUI 事件送出。',
        '畫面中尺寸標註延伸線部分超出視區；可以看右側尺寸，內腔及唇邊須以網格讀回核對。',
        '在使用者個人副本修改前先另存新版本；個人操作及結果須自己重新核對，不直接代入助教讀值。',
    ]
    steps = [
        {'id': 'ch05-linked-y-01', 'title': '將草圖 Y 從40改為50 mm',
         'goal': '觀察共用草圖的 Y 尺寸改變如何影響盒體與上蓋',
         'context': '獨立 Blender 5.2.1、CAD Sketcher 0.32.1；Body Sketch 為活動草圖，右側 Sketcher > Constraints > Dimensional。此試作第二個 Distance 是 Y；其他場景須先確認對應。',
         'actions': ['將第二個 Distance 從40 mm改為50 mm，第一個 Distance 保持80 mm。'],
         'success': '畫面顯示80／50 mm及 Fully defined。助教數位讀回盒體80×50×30 mm、內腔76×46×28 mm、唇外75.6×45.6 mm；四側水平間隙約0.2 mm。',
         'shortcuts': [], 'figures': [img_50], 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
         'limitations': list(common), 'artifacts': [summary_ref]},
        {'id': 'ch05-linked-y-02', 'title': '另存並重開 Y50 版本',
         'goal': '確認草圖尺寸與盒蓋數位關係在保存重開後保留',
         'context': '仍在 Body Sketch；另存自己的新版本後重新開啟。',
         'actions': ['使用 File > Save As 另存 Y50 新版本，重開後對照右側兩個尺寸。'],
         'success': '助教重開畫面顯示80／50 mm；獨立讀回 solver OKAY、DoF 0，盒蓋及間隙的12項數位檢查通過。畫面同時出現工具提示，不稱無警告。',
         'shortcuts': [], 'figures': [img_reopen], 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
         'limitations': list(common) + ['重開原圖底部顯示「Tool sketcher.slvs_select not found for space VIEW_3D」；原因未知。後續改為Y45及數位讀值成功，不證明其他草圖工具正常。若你的畫面也出現此提示，先停下並回報畫面，核對工具與擴充套件狀態。'],
         'artifacts': [scene_50, summary_ref, warning_ref]},
        {'id': 'ch05-linked-y-03', 'title': '重開後改成 Y45 並另存',
         'goal': '確認重開後仍能修改 Y 尺寸並追溯新檔',
         'context': '重開 Y50 版本的活動 Body Sketch，右側第二個 Distance 是本次 Y 尺寸。',
         'actions': ['將第二個 Distance 從50 mm改為45 mm，第一個保持80 mm。', '另存不同版本並保留來源；再核對自己的讀值。'],
         'success': '助教畫面顯示80／45 mm及 Fully defined；數位讀回盒體80×45×30 mm、內腔76×41×28 mm、唇外75.6×40.6 mm，保存後12項數位檢查通過。',
         'shortcuts': [], 'figures': [img_45, img_saved], 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
         'limitations': list(common) + ['Y45本次已另存及數位讀回；目前安全摘要未列另一次重開Y45的結果，不將它說成已重開。'],
         'artifacts': [scene_45, summary_ref]},
    ]
    chapter = next(chapter for chapter in data['chapters'] if chapter['id'] == 'ch05')
    existing = {step['id'] for section in data['chapters'] for step in section['steps']}
    if any(step['id'] in existing for step in steps):
        raise ValueError('new step IDs conflict')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('Y方向已有40→50 mm、重開後50→45 mm的隔離GUI試驗；特定尺寸的數位結果與實體配合分開，重開圖中的工具提示仍待釐清。')
    data['version'] = 'v008 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v008追加Y方向草圖操作與保存驗證，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v007.json', 'sha256': SOURCE_SHA},
                                   {'path': summary_ref['path'], 'sha256': summary_ref['sha256']},
                                   {'path': warning_ref['path'], 'sha256': warning_ref['sha256']}])
    data['yDimensionVerification'] = {'summary': summary_ref, 'warning': warning_ref, 'scenes': [scene_50, scene_45],
                                      'scope': 'Y草圖尺寸以GUI事件修改；起始盒蓋與驅動器為程式建置；Y50重開圖有工具提示。',
                                      'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV008'] = '新增Y尺寸GUI讀值、保存與重開後再次修改；明示畫面工具提示及程式建置來源。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v008')
    if SOURCE.read_bytes() != before:
        raise ValueError('v007 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f"Created {OUTPUT}: {sum(len(c['steps']) for c in data['chapters'])} microsteps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
