"""Engineering curriculum v030: add the detailed walkthrough (詳細步驟) to every chapter 01-06 main step.

The section page shows a brief version in the middle column and this walkthrough in the right-hand tabs.
v029 stays unchanged; path v003 is still current.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v029.json'
SOURCE_SHA = 'c042a30f169541b3087e1a9919320b689745cb170813a4f8ab0bf569b9a6edc1'
TEXT = ROOT / 'learning/engineering_v030_detail.py'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v030.json'
REWRITTEN = {'ch01', 'ch02', 'ch03', 'ch04', 'ch05', 'ch06'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('v029 changed')
    data = json.loads(raw.decode('utf-8-sig'))
    spec = importlib.util.spec_from_file_location('engineering_v030_detail', TEXT)
    text = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(text)
    targets = {step['id']: step for chapter in data['chapters'] if chapter['id'] in REWRITTEN
               for step in chapter['steps'] if not step.get('track')}
    if set(text.DETAIL) != set(targets):
        raise ValueError('detail coverage differs: missing %s, unknown %s' % (sorted(set(targets) - set(text.DETAIL)), sorted(set(text.DETAIL) - set(targets))))
    for step_id, detail in text.DETAIL.items():
        if not detail['steps'] or not all(isinstance(line, str) and line.strip() for line in detail['steps']):
            raise ValueError('empty walkthrough: ' + step_id)
        targets[step_id]['detail'] = copy.deepcopy(detail)
    data['version'] = 'v030 · 2026-10-28'
    data['description'] = data['description'] + ' v030 為第01～06章每個主線小步加上詳細步驟與理由，供小節頁右欄顯示。'
    data['sourceVersions'] = data['sourceVersions'] + [{'path': 'learning/web/engineering-curriculum-v029.json', 'sha256': SOURCE_SHA},
                                                       {'path': 'learning/engineering_v030_detail.py', 'sha256': sha(TEXT)}]
    data['contentReview'] = dict(data['contentReview'], reviewV030={
        'reviewedOn': '2026-10-28', 'reviewer': 'Claude Code（依學員選定的小節頁三欄版面）',
        'scope': '第01～06章 %d 個主線小步新增 detail（steps、why）；介面名稱沿用 reviewV029.uiEvidence 的讀回核對，未新增示範或原圖。' % len(text.DETAIL),
        'learnerProgressChanged': False})
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    OUTPUT.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n').encode('utf-8'))
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
