"""Engineering curriculum v038: add chapter 00, a reference chapter of common functions and shortcuts.

The cards come from learning/engineering_v038_ch00.json and only reuse existing evidence: the 2026-10-27
shortcut demos, the 2026-10-28 chapter 03 edit-mode GUI practice and the original lesson menu screenshots.
Readback values are copied from the recorded JSON by case name, never typed by hand.
Reference steps (track "reference") can be read and noted, but never confirmed or counted.
v037 stays unchanged; chapters 01-12 are copied as they are.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v037.json'
SOURCE_SHA = '79522345aef709d92f5eb28b47176c54e3a45dbc728beacf9c1420dd21d1248a'
CONTENT = ROOT / 'learning/engineering_v038_ch00.json'
CONTENT_SHA = 'd77b15115d995aad363bae69762c959cb2fd35cadfa7c09d3f15d7a5bb9153eb'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v038.json'
LIMITATION = '速查卡取自既有快捷鍵實測（Blender 5.2.1 出廠鍵位、獨立示範環境）與原圖；圖與讀值是助教示範，不是你的完成紀錄。'
TRACK = '速查：只供閱讀與查找的參考卡；可以留卡關筆記，但不能確認，也不計入主線進度。'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('v037 changed')
    if sha(CONTENT) != CONTENT_SHA:
        raise ValueError('chapter 00 content changed')
    data, content = read(SOURCE), read(CONTENT)
    if any(chapter['id'] == 'ch00' for chapter in data['chapters']):
        raise ValueError('chapter 00 already exists')
    aliases = content['aliases']

    def expand(path):
        alias, _, rest = path.partition(':')
        full = aliases[alias] + rest
        if not full.startswith('learning/evidence/') or not (ROOT / full).is_file():
            raise ValueError('missing evidence ' + full)
        return full

    def pinned(path, **extra):
        full = expand(path)
        return {'path': full, 'sha256': sha(ROOT / full), **extra}

    chapters = {chapter['id']: chapter for chapter in data['chapters']}
    targets = {step['id']: (chapter, step) for chapter in data['chapters'] for step in chapter['steps']}

    def practice(step_id):
        chapter, step = targets[step_id]
        if step.get('track') in ('appendix', 'pending') or not step.get('section'):
            raise ValueError('practice must be a doable step: ' + step_id)
        return {'chapterId': chapter['id'], 'stepId': step_id, 'sectionId': step['section'],
                'label': '第 %s 章 %s %s' % (chapter['number'], step['section'], step['title'])}

    def readback(record, field):
        value = record
        for key in field.split('.'):
            value = value[key]
        return value

    def demonstration(spec):
        source = content['readingSources'][spec['source']]
        path = expand(source['path'])
        document = read(ROOT / path)
        records = {item['case']: item['actual'] for item in document.get('cases', [])}
        records.update({item['slug']: item['observed'] for item in document.get('records', [])})
        readings = [{'label': item['label'], 'kind': 'readback',
                     'value': json.dumps({field: readback(records[item['case']], field) for field in item['fields']}, ensure_ascii=False)}
                    for item in spec['items']]
        return {'source': {'path': path, 'sha256': sha(ROOT / path)}, 'scope': source['scope'], 'readings': readings}

    section_ids = [section['id'] for section in content['sections']]
    steps = []
    for card in content['cards']:
        if card['section'] not in section_ids or not 1 <= len(card['actions']) <= 3 or not card['figures']:
            raise ValueError('incomplete card ' + card['id'])
        if not card['detail']['steps'] or not card['detail']['why'] or not card['help'] or not card['practice']:
            raise ValueError('incomplete card ' + card['id'])
        step = {key: copy.deepcopy(card[key]) for key in ('id', 'title', 'goal', 'context', 'actions', 'success')}
        step['shortcuts'] = [dict(copy.deepcopy(item), evidence=[pinned(entry['path'], method=entry['method'], label=entry['label'])
                                                              for entry in item['evidence']]) for item in card['shortcuts']]
        step['figures'] = [pinned(figure['path'], type='screenshot', caption=figure['caption']) for figure in card['figures']]
        step['sourceSteps'] = []
        step['evidenceStatus'] = 'existing_demo'
        step['limitations'] = [LIMITATION] + card.get('limitations', [])
        step['section'] = card['section']
        step['detail'] = copy.deepcopy(card['detail'])
        step['track'] = 'reference'
        step['help'] = list(card['help'])
        step['practice'] = [practice(step_id) for step_id in card['practice']]
        if 'readings' in card:
            step['demonstration'] = demonstration(card['readings'])
        steps.append(step)
    chapter = dict(copy.deepcopy(content['chapter']), sections=[dict(section, track='reference') for section in content['sections']], steps=steps)
    data['chapters'].insert(0, chapter)
    data['trackDefinitions'] = dict(data['trackDefinitions'], reference=TRACK)
    data['version'] = 'v038 · 2026-10-29'
    data['description'] += ' v038 新增第 00 章「常用功能與快捷操作」速查：%d 張卡片整理既有快捷鍵實測與原圖，不計入主線、不能確認，各卡連到正式練習的小步。' % len(steps)
    data['sourceVersions'] += [{'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA},
                               {'path': CONTENT.relative_to(ROOT).as_posix(), 'sha256': CONTENT_SHA}]
    data['contentReview']['reviewV038'] = {
        'reviewedOn': '2026-10-29', 'reviewer': 'Claude Code（依使用者要求新增第 00 章）',
        'scope': '新增第 00 章速查 %d 張卡片；原圖、證據檔與讀值由 builder 依路徑和案例名稱取自既有實測並核對雜湊。沒有新的 Blender 示範；第 01～12 章內容不變。' % len(steps),
        'referenceStepIds': [step['id'] for step in steps],
        'evidenceSources': sorted({source['path'] for source in content['readingSources'].values()}),
        'learnerProgressChanged': False,
        'learnerProgressSha256': 'b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1',
    }
    if [c['id'] for c in data['chapters'][1:]] != list(chapters):
        raise ValueError('chapter order changed')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    print(sha(OUTPUT), 'reference steps', len(steps))


if __name__ == '__main__':
    main()
