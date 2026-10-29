"""Engineering curriculum v032: move chapter 11 steps that cannot be done yet out of the main line and tidy the ch07-12 walkthroughs.

- Six chapter 11 steps depend on thread or boss geometry that has not been built: they become track "pending"
  (visible, cannot be confirmed, not counted). Sections 11-05 and 11-07 hold only such steps and are marked pending too.
- The same "not re-recorded" sentence was stored on all 110 ch07-12 walkthroughs; it moves to one chapter-level detailNote.
- Walkthrough lines that said "check with an available tool" now name the panel to read.
v031 stays unchanged; path v003 is still current.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v031.json'
SOURCE_SHA = '96a3304fee401b61cc59b6764eaa31b6a22e31e9865b873534299f8eb42c5b92'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v032.json'
PENDING = ['ch11-08-02-02', 'ch11-08-03-01', 'ch11-08-03-02', 'ch11-08-04-02', 'ch11-08-05-01', 'ch11-08-05-02']
PENDING_SECTIONS = ['11-05', '11-07']
OLD_NOTE = '本步詳細文字依既有教材與示範整理，尚未逐步重新實拍；請對照自己的實際 Blender 畫面。'
DETAIL_NOTE = '本章詳細步驟依既有教材與示範整理，尚未逐步重新實拍；畫面和文字不同時，以自己的 Blender 畫面為準並用卡關筆記回報。'
DIMENSIONS = '按 N 開側欄，在 Item 分頁讀 Dimensions'
# (小步, 詳細步驟行號, 原文, 新文)
LINES = [
    ('ch07-solid-03', 1, '按 Enter 確認；以可用工具另行讀回外框尺寸，若非 60×40×30 mm 先停下核對。',
     f'按 Enter 確認；{DIMENSIONS}，若不是 60 × 40 × 30 mm 先停下核對。'),
    ('ch07-solid-04', 1, '重開後檢查模型，並用可用工具核對外框。',
     f'重開後選取模型，{DIMENSIONS}，核對外框 60 × 40 × 30 mm。'),
    ('ch07-cavity-06', 2, '觀察結果並另以可用工具核對；布林後內腔與封閉性尚待驗證。',
     f'觀察結果，{DIMENSIONS} 核對外框；布林後內腔與封閉性尚待驗證。'),
    ('ch08-xy-safety-02', 1, '按更新圖示，再以可用工具對照更新後幾何。',
     f'按更新圖示，再{DIMENSIONS}，對照更新後的尺寸。'),
    ('ch09-06-03-02', 1, '核對兩件 Dimensions、端面與 Select Non Manifold；再比較可用讀值紀錄。',
     '核對兩件 Dimensions、端面與 Select Non Manifold；再和本步「示範紀錄」分頁的讀值比較。'),
    ('ch11-08-01-02', 1, '以可用世界座標讀值核對各面位置；再切邊選取、Alt+A 取消選取，以 F3 搜尋 Select Non Manifold。',
     '選取一個面後按 N，在 Item 分頁把 Median 切到 Global，讀世界座標核對各面位置；再切邊選取、Alt+A 取消選取，以 F3 搜尋 Select Non Manifold。'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('v031 changed')
    data = json.loads(raw.decode('utf-8-sig'))
    steps = {step['id']: (chapter, step) for chapter in data['chapters'] for step in chapter['steps']}
    for step_id in PENDING:
        chapter, step = steps[step_id]
        if chapter['id'] != 'ch11' or step.get('track'):
            raise ValueError('unexpected pending step ' + step_id)
        step['track'] = 'pending'
    ch11 = next(chapter for chapter in data['chapters'] if chapter['id'] == 'ch11')
    for section in ch11['sections']:
        if section['id'] in PENDING_SECTIONS:
            if any(step['section'] == section['id'] and step.get('track') != 'pending' for step in ch11['steps']):
                raise ValueError('section has doable steps: ' + section['id'])
            section['track'] = 'pending'
    moved = 0
    for chapter in data['chapters']:
        notes = {step['detail'].pop('verification', None) for step in chapter['steps'] if 'detail' in step}
        notes.discard(None)
        if notes:
            if notes != {OLD_NOTE}:
                raise ValueError('unexpected verification text in ' + chapter['id'])
            chapter['detailNote'] = DETAIL_NOTE
            moved += 1
    for step_id, index, old, new in LINES:
        detail = steps[step_id][1]['detail']
        if detail['steps'][index] != old:
            raise ValueError('walkthrough line changed: %s %d' % (step_id, index))
        detail['steps'][index] = new
    data['trackDefinitions'] = dict(data['trackDefinitions'], pending='待製作：所需的模型或示範還沒完成；可以閱讀，不能確認，也不計入主線進度。')
    data['version'] = 'v032 · 2026-10-28'
    data['description'] = data['description'] + ' v032 把第 11 章 6 個尚無法完成的小步改為待製作（不計入主線），並整理第 07～12 章詳細步驟的說明位置與讀值方式。'
    data['sourceVersions'] = data['sourceVersions'] + [{'path': 'learning/web/engineering-curriculum-v031.json', 'sha256': SOURCE_SHA}]
    data['contentReview'] = dict(data['contentReview'], reviewV032={
        'reviewedOn': '2026-10-28', 'reviewer': 'Claude Code（審查 Codex v031 後的修正）',
        'pendingSteps': PENDING, 'pendingSections': PENDING_SECTIONS,
        'scope': '第 11 章待製作小步移出主線；%d 章的重複驗證句改為章層級 detailNote；%d 行「可用工具」改為具體讀值位置。未新增示範或原圖。' % (moved, len(LINES)),
        'learnerProgressChanged': False})
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    OUTPUT.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode('utf-8'))
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
