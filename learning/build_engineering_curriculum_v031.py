"""Add draft detailed guidance for chapters 07–12, preserving v030 and learner progress."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'learning/web/engineering-curriculum-v030.json'
SOURCE_SHA = '55d0cc4c731a550fbe2c17635426dd14efca2894cf99455b322d0ed9f8d8515b'
TEXTS = [ROOT / 'learning/engineering_v031_ch07_ch09.json', ROOT / 'learning/engineering_v031_ch10_ch12.json']
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v031.json'
TARGETS = {'ch07', 'ch08', 'ch09', 'ch10', 'ch11', 'ch12'}
PENDING = {
    'ch11-08-02-02': '封閉外螺紋的逐步建模尚待製作，現有開放曲面僅供觀察。',
    'ch11-08-03-01': '內螺紋封閉切割體及 Boolean 的逐步實作尚待製作。',
    'ch11-08-03-02': '須先完成並核對內螺紋實體，才能對實際結果檢查。',
    'ch11-08-04-02': '螺絲柱與導孔的完整手工操作尚待示範；目前只有獨立柱草案。',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('v030 source changed')
    data = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    targets = {step['id']: step for chapter in data['chapters'] if chapter['id'] in TARGETS
               for step in chapter['steps'] if not step.get('track')}
    descriptions = {}
    for path in TEXTS:
        items = json.loads(path.read_text(encoding='utf-8-sig'))
        if isinstance(items, dict) and 'details' in items:
            if items.get('sourceSha256') != SOURCE_SHA:
                raise ValueError('detail source version differs: ' + path.name)
            items = items['details']
        if not isinstance(items, dict) or set(items) & set(descriptions):
            raise ValueError('duplicate or invalid detail source: ' + path.name)
        descriptions.update(items)
    if set(descriptions) != set(targets):
        raise ValueError('detail coverage differs: missing %s; unknown %s' %
                         (sorted(set(targets)-set(descriptions)), sorted(set(descriptions)-set(targets))))
    for step_id, detail in descriptions.items():
        if (set(detail) != {'steps', 'why'} or not isinstance(detail['steps'], list)
                or not 1 <= len(detail['steps']) <= 3
                or any(not isinstance(text, str) or not text.strip() for text in detail['steps'])
                or not isinstance(detail['why'], str) or not detail['why'].strip()):
            raise ValueError('invalid detail: ' + step_id)
        targets[step_id]['detail'] = copy.deepcopy(detail)
        targets[step_id]['detail']['verification'] = '本步詳細文字依既有教材與示範整理，尚未逐步重新實拍；請對照自己的實際 Blender 畫面。'
        if step_id in PENDING:
            target = targets[step_id]
            target['actions'] = [PENDING[step_id] + ' 請先閱讀右側限制；這項操作尚不能依現有教學完成。']
            target['success'] = '待後續實作及驗證後，才能核對原目標：' + target.get('success', '')
    data['version'] = 'v031 · 2026-10-28'
    data['description'] += ' v031 為第07～12章主線補充詳細文字，沿用既有證據；未逐步重新實拍，未執行實體試驗。'
    data['sourceVersions'] += [{'path':'learning/web/engineering-curriculum-v030.json','sha256':SOURCE_SHA}]
    data['sourceVersions'] += [{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)} for path in TEXTS]
    data['contentReview'] = dict(data['contentReview'], reviewV031={
        'reviewedOn':'2026-10-28','reviewer':'Codex（依現有 v030 與示範記錄整理）',
        'scope':'第 07～12 章 %d 個主線小步補詳細文字；4 個螺紋待實作步驟的摘要及成功條件同步標明待製作。未新增逐步實拍或實體試驗，原本證據狀態及限制保留。' % len(targets),
        'clarifiedPendingSteps':list(PENDING),
        'learnerProgressChanged':False})
    OUTPUT.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode('utf-8'))
    print(sha(OUTPUT))

if __name__ == '__main__':
    main()
