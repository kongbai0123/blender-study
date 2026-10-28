"""從凍結的題目 v002 補充 07／08 圖與獨立 Blender 螺紋證據；拒絕覆寫。"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'learning/web/challenges/challenges-v002.json'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v003.json'
EXPECTED = 'e828ccc01320a417b655fd29fee53f093b81891ef47343e38b535d973871d126'
DRAWINGS = {
    'ch07': {
        'path': '/challenges/sketch-constraint-drawing-v002.svg',
        'sha256': '53741eccd9b255b36503f131b26c06ef38dd4e0e5c6a6cdebfb9d7c4505adcfe',
        'title': 'XY 草圖尺寸題圖：60×40、80×40 為不同保存階段，不是同時存在的兩件零件',
    },
    'ch08': {
        'path': '/challenges/parametric-box-drawing-v003.svg',
        'sha256': '9ec89fec47a4ac5fd7e7a97569d720398ffb30011bbc3fd15218580dd952616d',
        'title': '80×50 固定基準盒與上蓋：名義幾何，不是自動連動或實體配合驗證',
    },
}
DRAWING_STATUS = {
    'ch07': '同一草圖兩個不同保存階段；此圖不代表內腔、上蓋或拉伸結果已完成。',
    'ch08': '固定基準幾何圖，不代表圖中已建立自動連動；0.4 mm 為試驗總間隙，完整干涉和實體試配待驗。',
}
EXTRA_DEMOS = [
    {
        'title': '外螺紋封閉網格草案：程式建立、GUI 檢視',
        'description': '輪廓與封閉網格由程式建立；獨立 Blender GUI 示範觀察、非流形檢查、另存與重開，不是 GUI 手工建模。兩端牙形不完整；材料、配合、切片、實印與強度未驗。',
        'screenshot': {
            'path': 'learning/evidence/08/2026-10-28-closed-external-thread-probe-v001/08-CLOSED-02-framed.png',
            'sha256': '7369128ddf8ef7e784b15fe4ca357676b3948811a95bde4c438048aa9029253a',
            'caption': '獨立 Blender GUI 使用 Frame Selected 與視角鍵觀察程式建立的草案；封閉性與尺寸另依摘要讀值。',
        },
        'summaryPath': 'learning/evidence/08/2026-10-28-closed-external-thread-probe-v001/safe-summary-v001.json',
        'summarySha256': 'b9b8f812696d78200bc9692cd002ca1b6cb899e24f9bb07db9ec0184b21d1a6b',
    },
    {
        'title': '盲孔柱與盒體接合：GUI Boolean Union 草案',
        'description': '盲孔柱由程式建立；獨立 Blender GUI 示範移位、Boolean Union、檢查、另存及重開。尚無蓋孔、指定五金或實體強度、配合及試配結果。',
        'screenshot': {
            'path': 'learning/evidence/08/2026-10-28-boss-box-join-trial-v002/08-boss-07-reopened.png',
            'sha256': 'e16ab17615e5115f09931019d127d451cd37bdc5f8e1f0f701333a84a9212e45',
            'caption': '獨立 Blender 重開合併後的盒體及柱；網格數值與限制另依摘要，不代表實體合格。',
        },
        'summaryPath': 'learning/evidence/08/2026-10-28-boss-box-join-trial-v002/public-summary-v001.json',
        'summarySha256': 'abb0284919bbfac43492cdd61889ea161ef4113316f30c9b1e56e355691eea83',
    },
]


def build():
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED:
        raise ValueError('題目 v002 雜湊不符；停止並核對。')
    data = deepcopy(json.loads(raw))
    if data.get('schemaVersion') != 1 or data.get('version') != 'v002' or len(data.get('chapters', [])) != 12:
        raise ValueError('題目來源版本或章數不符。')
    for chapter_id, drawing in DRAWINGS.items():
        path = ROOT / 'learning/web' / drawing['path'].lstrip('/')
        if sha256(path.read_bytes()).hexdigest() != drawing['sha256']:
            raise ValueError('題圖尚未凍結或雜湊不符：' + chapter_id)
        found = [row for row in data['chapters'] if row.get('chapterId') == chapter_id]
        if len(found) != 1 or found[0].get('drawing') is not None:
            raise ValueError('來源題目圖欄位不符合預期：' + chapter_id)
        found[0]['drawing'] = deepcopy(drawing)
        found[0]['drawingStatus'] = DRAWING_STATUS[chapter_id]
    matches = [row for row in data['chapters'] if row.get('chapterId') == 'ch11']
    if len(matches) != 1 or 'extraDemos' in matches[0]:
        raise ValueError('第 11 章資料與預期不符。')
    for demo in EXTRA_DEMOS:
        for path, expected in ((demo['screenshot']['path'], demo['screenshot']['sha256']),
                               (demo['summaryPath'], demo['summarySha256'])):
            if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise ValueError('螺紋示範來源或摘要雜湊不符：' + path)
    matches[0]['extraDemos'] = deepcopy(EXTRA_DEMOS)
    data['version'] = 'v003'
    data['previousVersion'] = {'path': 'learning/web/challenges/challenges-v002.json', 'sha256': EXPECTED}
    return data


def main():
    if OUTPUT.exists():
        raise FileExistsError('拒絕覆寫現有題目版本：' + str(OUTPUT))
    data = build()
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('saved', OUTPUT, 'sha256', sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
