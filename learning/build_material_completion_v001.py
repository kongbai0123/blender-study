"""Inventory teaching-content evidence, never learner completion or physical results."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'learning/journal/2026-10-28-material-content-inventory-v001.json'
CURRICULUM = ROOT / 'learning/web/engineering-curriculum-v036.json'
PATH = ROOT / 'learning/web/engineering-path-v005.json'
CHALLENGES = ROOT / 'learning/web/challenges/challenges-v009.json'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    data, challenges = read(CURRICULUM), read(CHALLENGES)
    if challenges['source']['sha256'] != digest(CURRICULUM):
        raise ValueError('challenge curriculum mismatch')
    refs = {(l['id'], s['id']): s for l in read(ROOT/'learning/catalog.json')['lessons'] for s in l['steps']}
    chapters = []
    for chapter in data['chapters']:
        exercise = next(c for c in challenges['chapters'] if c['chapterId'] == chapter['id'])
        drawing = exercise['drawing']
        pic = ROOT / ('learning/web/' + drawing['path'].lstrip('/'))
        if drawing.get('sha256') and digest(pic) != drawing['sha256']:
            raise ValueError('drawing mismatch')
        items = []
        for step in chapter['steps']:
            sources = []
            for ref in step.get('sourceSteps', []):
                original = refs[(ref['lessonId'], ref['stepId'])]
                sources.append({'lessonId': ref['lessonId'], 'stepId': ref['stepId'],
                                'sharedRun': original.get('operationRun', {}).get('runId'),
                                'evidenceScope': 'original-step shared evidence; not a new photo of every split step'})
            files = []
            for artifact in step.get('figures', []) + step.get('artifacts', []):
                if artifact.get('path') and artifact.get('sha256'):
                    if digest(ROOT / artifact['path']) != artifact['sha256']:
                        raise ValueError('evidence mismatch')
                    files.append({'path': artifact['path'], 'sha256': artifact['sha256']})
            items.append({'id': step['id'], 'section': step.get('section'), 'track': step.get('track', 'main'),
                          'contentEvidence': step['evidenceStatus'], 'files': files, 'sharedSources': sources})
        chapters.append({'chapter': chapter['id'], 'title': chapter['title'], 'engineeringDrawing': drawing,
                         'digitalLessonsAndFieldMethodsReady': True,
                         'evidenceCounts': dict(Counter(s['contentEvidence'] for s in items if s['track'] != 'appendix')),
                         'items': items})
    inventory = {'schemaVersion': 1, 'title': '教材製作內容與證據索引', 'reviewedOn': '2026-10-28',
                 'scope': '本機現行12章數位教材與現場方法；不是學員進度、全圖逐張視覺審核或實體合格清單。',
                 'sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in (CURRICULUM, PATH, CHALLENGES)],
                 'chapters': chapters,
                 'physicalPrint': None, 'physicalMeasurement': None, 'physicalInstallation': None, 'physicalFit': None,
                 'qualifiedClearance': None, 'qualifiedStrength': None, 'learnerProgressChanged': False,
                 'excludedHistoricalAppendix': {'count': 30, 'unverifiedInteractiveLauncher': 'ch08-linked-01',
                                                'reason': '開發附錄，非現行主線；未把未測互動啟動器算成已完成 GUI 教學。'},
                 'remaining': ['實際列印、量測、五金安裝、試配及依用途判定',
                               '公開前針對本輪新檔重建與審查發布清單；本輪未commit/push'],
                 'knownLimits': ['CAD 工具警告根因未修，11-20 僅驗證限定恢復操作。',
                                 'CAD 轉 mesh 後副本不連動；11-19 開口牙條不在可匯出封閉實體清單。',
                                 '修訂三角化改變局部表面；六件 STL 的有限檢查不證可製造或旋合。']}
    OUT.write_text(json.dumps(inventory, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(digest(OUT))


if __name__ == '__main__':
    main()
