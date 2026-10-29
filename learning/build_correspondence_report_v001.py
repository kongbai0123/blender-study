"""Aggregate the scoped 2026-10-29 material audit; never update learner state."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'learning/journal/2026-10-29-material-correspondence-report-v001.json'
PROGRESS_SHA = 'b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1'
DATA = {
    'learning/web/engineering-curriculum-v037.json': '79522345aef709d92f5eb28b47176c54e3a45dbc728beacf9c1420dd21d1248a',
    'learning/web/engineering-path-v006.json': 'c5deb3aa4ecede22bfd8b283f632000114202d2b32b198a3ea2887a102c33c99',
    'learning/web/challenges/challenges-v010.json': '45bc3007a61efdbab5327e1b21dec4901ed1c92f36d6058d1389e13d2d3e90fa',
}
AUDITS = [
    'learning/patches/2026-10-29-ch01-ch04-audit-v001.json',
    'learning/patches/2026-10-29-ch05-ch08-audit-v001.json',
    'learning/patches/2026-10-29-ch09-ch12-audit-v001.json',
    'learning/patches/2026-10-29-ch11-remaining-part-a-v001.json',
    'learning/patches/2026-10-29-ch11-remaining-part-b-v001.json',
]
AUDIT_DIR = 'learning/evidence/audits/2026-10-29-correspondence-v001/'


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def ref(path: str) -> dict:
    return {'path': path, 'sha256': sha(path)}


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def main() -> None:
    if OUT.exists():
        raise SystemExit('Refusing to overwrite existing audit report')
    for path, expected in DATA.items():
        if sha(path) != expected:
            raise SystemExit(f'Frozen source mismatch: {path}')
    progress_before = sha('learning/progress.json')
    if progress_before != PROGRESS_SHA:
        raise SystemExit('Learner progress changed; stop and inspect')
    curriculum, path_data, challenges = [read(path) for path in DATA]
    expected_ids = {s['id'] for c in curriculum['chapters'] for s in c['steps'] if s.get('track') != 'appendix'}
    observed_ids: set[str] = set()
    browser_sources = []
    for index, path in enumerate(AUDITS):
        data = read(path)
        if index in (0, 3):
            ids = [x['id'] for x in data['items']]
        elif index == 1:
            ids = [x['id'] for x in data['steps']]
        elif index == 2:
            ids = [sid for section in data['sections'] for sid in section['stepIds']]
        else:
            ids = [sid for section in data['sections'].values() for sid in section['selectedStepIds']]
        observed_ids.update(ids)
        browser_sources.append({**ref(path), 'observedStepCount': len(ids)})
    missing_ids = sorted(expected_ids - observed_ids)
    extra_ids = sorted(observed_ids - expected_ids)
    if missing_ids or extra_ids or len(expected_ids) != 447:
        raise SystemExit(f'Browser coverage mismatch: missing={missing_ids}, extra={extra_ids}')
    review = curriculum['contentReview']['reviewV037']
    corrected_ids = review['correctedStepIds']
    live_path = 'learning/patches/2026-10-29-v037-corrected-live-review-v001.json'
    live = read(live_path)
    if set(x['id'] for x in live['details']) != set(corrected_ids):
        raise SystemExit('Corrected-step live regression ID mismatch')
    if live['issues'] or live['matchedStepCount'] != len(corrected_ids) or len(corrected_ids) != 61:
        raise SystemExit('Corrected-step live regression has unresolved findings')
    rendered = read(AUDIT_DIR + 'render-final-v001.json')
    http = read(AUDIT_DIR + 'http-final-v001.json')
    if rendered['counts']['stepsWithFindings'] or rendered['counts']['steps'] != len(expected_ids):
        raise SystemExit('Renderer structural findings remain')
    if challenges['source']['sha256'] != DATA[next(iter(DATA))]:
        raise SystemExit('Challenge curriculum binding mismatch')
    progress_after = sha('learning/progress.json')
    if progress_after != progress_before:
        raise SystemExit('Learner progress changed during report aggregation')
    track_counts = Counter(s.get('track', 'main') for c in curriculum['chapters'] for s in c['steps'])
    physical_values = [*path_data['physicalResults'].values()]
    for chapter in path_data['chapters']:
        physical_values.extend(chapter.get('physicalResults', {}).values())
    if any(v is not None for v in physical_values):
        raise SystemExit('Unexpected non-null physical result; inspect rather than classify as qualified')
    report = {
        'schemaVersion': 1,
        'createdAtUtc': datetime.now(timezone.utc).isoformat(),
        'title': '教材內容對應與缺漏補正審查 v037',
        'sources': [ref(p) for p in DATA],
        'scope': {
            'chapters': len(curriculum['chapters']),
            'sections': sum(len(c['sections']) for c in curriculum['chapters']),
            'nonAppendixSteps': len(expected_ids),
            'tracksIncludingHistoricalAppendix': dict(track_counts),
            'browserMethod': '五份分工紀錄合併後涵蓋全部小步的主操作與詳細步驟；原圖及其他分頁採各報告所列範圍，不是所有歷史圖片逐張目視。',
            'finalRevisionMethod': live['scope'],
            'rendererMethod': rendered['scope'],
            'httpMethod': http['scope'],
        },
        'browserCoverage': {
            'sources': browser_sources,
            'uniqueObservedStepCount': len(observed_ids),
            'missingStepIds': missing_ids,
            'extraStepIds': extra_ids,
            'observedStepIds': sorted(observed_ids),
            'correctedStepRegression': ref(live_path),
            'correctedStepCount': len(corrected_ids),
            'correctedStepIds': corrected_ids,
        },
        'structuralVerification': {
            'render': ref(AUDIT_DIR + 'render-final-v001.json'),
            'counts': rendered['counts'],
            'liveHttp': ref(AUDIT_DIR + 'http-final-v001.json'),
            'responseByteHashChecks': http['assetCount'],
        },
        'newAndReclassifiedContent': {
            'missingDetailedInstructionsAdded': 9,
            'explicitHistoricalDemonstrationBindings': 191,
            'newGuardDemonstrationBindings': 1,
            'newBranchDrawings': [ref('learning/web/challenges/tenon-box-lid-drawing-v001.svg'), ref('learning/web/challenges/snapfit-box-lid-drawing-v001.svg')],
            'independentDrawingReview': ref('learning/patches/2026-10-29-two-drawings-independent-review-v001.json'),
            'guard70x40ActualReadback': ref('learning/evidence/parametric/2026-10-29-manual-guard-70x40-reject-v004/safe-summary-v001.json'),
            'mountPrefabReadback': ref('learning/evidence/08/2026-10-29-external-thread-mount-prefab-v001/safe-summary-v001.json'),
            'readOnlyStlCli': ref('learning/tutor/inspect_stl_v001.py'),
            'sixActualCliReadbacks': ref('learning/evidence/08/2026-10-29-stl-cli-readback-v001/safe-summary-v002.json'),
        },
        'testRuns': [
            {**ref(AUDIT_DIR + 'python-tests-final-v002.log'), 'discovered': 389, 'skipped': 9, 'failed': 0},
            {**ref(AUDIT_DIR + 'tutor-tests-final-v001.log'), 'discovered': 307, 'skipped': 1, 'failed': 0},
            {**ref(AUDIT_DIR + 'node-tests-final-v001.log'), 'passed': 63, 'failed': 0},
        ],
        'browserScreenshots': [ref(AUDIT_DIR + p) for p in ['v037-final-live.png', 'tenon-drawing-live.png', 'snapfit-drawing-live.png']],
        'learnerProgress': {'beforeSha256': progress_before, 'afterSha256': progress_after, 'revision': read('learning/progress.json')['revision'], 'changed': progress_before != progress_after},
        'physicalStatus': {'listedResultFieldsAllNull': all(v is None for v in physical_values), 'checkedNullFieldCount': len(physical_values), 'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None, 'qualifiedClearance': None, 'qualifiedStrength': None},
        'interpretation': {
            'detailsPresentAndStructurallyRenderable': not missing_ids and rendered['counts']['stepsWithFindings'] == 0,
            'allHistoricalPixelsVisuallyReviewedThisRound': False,
            'allBlenderActionsReexecutedThisRound': False,
            'manufacturingOrFitQualified': False,
            'remainingLimitations': [
                '六分頁全量檢查使用實際 renderer；不能稱為每一小步六分頁均由瀏覽器點開目視。',
                '已更正61個小步實頁回歸；其餘內容的人工審查來源版本與範圍見各分工報告。',
                '工程圖由實際網格擷取；可見性抽樣或三角邊投影不等於完整標準隱線製造圖。',
                '70×40拒絕案例僅證明指定草案面板與這一候選輸入的拒絕，未涵蓋所有原生欄位繞過方式。',
                '教材仍有程式預備場景或幾何的步驟，逐一明示範圍；沒有冒充每個起點均手工建立。',
                'CAD工具重開警告根因、曲面開口及細小幾何等既有工程限制沒有由這次教材修補消除。',
                '尚未做新一輪完整公開差異與私人資料發布審查，未commit或push。',
            ],
        },
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='')
    print(json.dumps({'report': OUT.relative_to(ROOT).as_posix(), 'browserStepCount': len(observed_ids), 'correctedStepCount': len(corrected_ids), 'assetCount': http['assetCount'], 'progressUnchanged': progress_before == progress_after}))


if __name__ == '__main__':
    main()
