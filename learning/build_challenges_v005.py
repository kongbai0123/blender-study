"""Challenges v005: the chapter 03 box challenge moves from the separate pilot page into the shared challenge page.

The pilot page's extra content (the timed-sample GIF and its before/after records) becomes the ch03 `animation`;
`progressKind: "pilot"` keeps using the existing pilot_challenge_* events so earlier records stay valid.
Source references now point at curriculum v032 (section IDs unchanged).
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'learning/web/challenges/challenges-v004.json'
SOURCE_SHA = 'c17a274a4e70ccd82463bd83f76a58f7a9821bafaa09fad402cc5766aa8a1af0'
CURRICULUM = ROOT / 'learning/web/engineering-curriculum-v032.json'
GIF = ROOT / 'learning/web/pilot/box-demo.gif'
GIF_SHA = '18f6811b12998d27ef49775a80405afe9799cb6909800f824d681264d147e875'
RUN = 'learning/evidence/04/2026-10-28-pilot-box-move-record-v002/'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v005.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('v004 source changed')
    if sha(GIF) != GIF_SHA:
        raise ValueError('pilot GIF changed')
    data = copy.deepcopy(json.loads(raw))
    item = next(x for x in data['chapters'] if x['chapterId'] == 'ch03')
    if item.pop('pilotPath') != '/pilot/box-lesson.html':
        raise ValueError('unexpected pilot path')
    item['progressKind'] = 'pilot'
    item['animation'] = {
        'path': '/pilot/box-demo.gif', 'sha256': GIF_SHA, 'title': '短動畫：沿 X 軸移動原盒',
        'description': '在獨立 Blender 選取原盒後，於 3D Viewport 依序按 G、X、5、Enter，將原盒沿 X 正向移動 5 mm。這是移動練習，並非完整建模流程。',
        'caption': 'GIF 由實際操作時定時採樣的原生截圖製作，經減色並合併相同影格；不是連續錄影。助教示範不代表學員已完成。',
        'records': [{'label': '動作前原圖', 'path': RUN + 'pilot-01-before.png'},
                    {'label': '動作後原圖', 'path': RUN + 'pilot-02-after.png'}]}
    for path in (ROOT / record['path'] for record in item['animation']['records']):
        if not path.is_file():
            raise FileNotFoundError(path)
    data['version'] = 'v005'
    data['source'] = {'path': 'learning/web/engineering-curriculum-v032.json', 'sha256': sha(CURRICULUM)}
    data['previousVersion'] = {'path': 'learning/web/challenges/challenges-v004.json', 'sha256': SOURCE_SHA}
    return data


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
