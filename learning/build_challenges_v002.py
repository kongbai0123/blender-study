"""由凍結的題目 v001 增補第 02／09／10 章專屬工程圖；拒絕覆寫。"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'learning/web/challenges/challenges-v001.json'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v002.json'
EXPECTED = '35c2a7f45ff03b1d6eeaaa1aed2a01851452abceae50ae49213674b1a56f02fa'
DRAWINGS = {
    'ch02': {
        'path': '/challenges/lip-clearance-drawing-v001.svg',
        'sha256': 'b82736f3ac2380219dd37f6b77be2704df82183810bf0204339a7079957a117f',
        'title': '小盒與環唇中央剖面；0.4 mm 為名義總間隙試驗值',
    },
    'ch09': {
        'path': '/challenges/dovetail-trial-drawing-v002.svg',
        'sha256': '8eda077de7b4944fba3cd975102047483ede2a9d2547f45a5fabb30ffc6fc421',
        'title': '燕尾滑蓋草案截面圖；獨立滑蓋分支，非定位柱或實體配合驗證',
    },
    'ch10': {
        'path': '/challenges/snapfit-coupons-drawing-v003.svg',
        'sha256': '0f6c6a0bfe6ed2aad58f54f3b2061684bb8df361a5fb6bddc3da0f305905b129',
        'title': '三件卡扣對照試片名義幾何圖；臂長非已驗證力學有效長，未證調整改善',
    },
}
STATUS = {
    'ch02': '名義總間隙 0.4 mm 為試驗值，置中時理論單邊 0.2 mm；未經實體試配或合格判定。',
    'ch09': '獨立燕尾滑蓋分支的截面圖；不代表定位柱圖、實體列印、試配或配合合格。',
    'ch10': '三件僅為卡扣幾何試片；標註臂長不等於已驗證力學有效長，未證調整改善或強度合格。',
}


def build():
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED:
        raise ValueError('題目 v001 雜湊不符；停止並核對。')
    original = json.loads(raw)
    if original.get('schemaVersion') != 1 or original.get('version') != 'v001':
        raise ValueError('題目來源版本不符。')
    result = deepcopy(original)
    if len(result.get('chapters', [])) != 12:
        raise ValueError('來源題目章數不符。')
    for chapter_id, definition in DRAWINGS.items():
        drawing_file = ROOT / 'learning/web' / definition['path'].lstrip('/')
        if sha256(drawing_file.read_bytes()).hexdigest() != definition['sha256']:
            raise ValueError('題圖尚未凍結或雜湊不符：' + chapter_id)
        matches = [item for item in result['chapters'] if item.get('chapterId') == chapter_id]
        if len(matches) != 1 or matches[0].get('drawing') is not None:
            raise ValueError('來源題目圖欄位不符合預期：' + chapter_id)
        matches[0]['drawing'] = deepcopy(definition)
        matches[0]['drawingStatus'] = STATUS[chapter_id]
    result['version'] = 'v002'
    result['previousVersion'] = {'path': 'learning/web/challenges/challenges-v001.json', 'sha256': EXPECTED}
    return result


def main():
    if OUTPUT.exists():
        raise FileExistsError('拒絕覆寫現有題目版本：' + str(OUTPUT))
    result = build()
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('saved', OUTPUT, 'sha256', sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
