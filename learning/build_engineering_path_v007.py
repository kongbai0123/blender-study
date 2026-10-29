"""Learning path v007: add chapter 00 (common functions and shortcuts) as a reference chapter.

The outline entry comes from learning/engineering_v038_ch00.json. A reference chapter has no
challenge, never counts toward progress and is not the prerequisite of chapter 01.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-path-v006.json'
SOURCE_SHA = 'c5deb3aa4ecede22bfd8b283f632000114202d2b32b198a3ea2887a102c33c99'
CONTENT = ROOT / 'learning/engineering_v038_ch00.json'
CONTENT_SHA = 'd77b15115d995aad363bae69762c959cb2fd35cadfa7c09d3f15d7a5bb9153eb'
CATALOG = ROOT / 'learning/catalog.json'
OUTPUT = ROOT / 'learning/web/engineering-path-v007.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('v006 changed')
    if sha(CONTENT) != CONTENT_SHA:
        raise ValueError('chapter 00 content changed')
    data = json.loads(SOURCE.read_text(encoding='utf8'))
    chapter = copy.deepcopy(json.loads(CONTENT.read_text(encoding='utf8'))['pathChapter'])
    catalog = json.loads(CATALOG.read_text(encoding='utf-8-sig'))
    known = {(lesson['id'], step['id']) for lesson in catalog['lessons'] for step in lesson['steps']}
    if any((item['lessonId'], item['stepId']) not in known for item in chapter['references']):
        raise ValueError('unknown original reference')
    if chapter['kind'] != 'reference' or any(item['id'] == 'ch00' for item in data['chapters']):
        raise ValueError('unexpected chapter 00')
    data['chapters'].insert(0, chapter)
    data['intro'] += ' 第 00 章是常用功能與快捷鍵速查，可隨時回查，不計入進度。'
    data['version'] = 'v007 · 2026-10-29'
    data['previousVersion'] = {'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA}
    data['contentReview']['revisionV007'] = {
        'reviewedOn': '2026-10-29',
        'scope': '新增第 00 章速查（kind: reference），對應教材 v038；第 01～12 章不變，無學員或實體完成變更。',
        'contentSource': {'path': CONTENT.relative_to(ROOT).as_posix(), 'sha256': CONTENT_SHA},
        'learnerCompletionChanged': False,
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
