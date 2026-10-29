"""Complete the current digital lessons without inventing physical evidence.

Frozen source hashes, raw screenshot validation, no learner-state writes.
"""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v035.json'
SOURCE_SHA = 'd40ffc3102585947f1a19d2e50d072f343cf25685df9d7e8555dfd702bc4fa91'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v036.json'
PATCHES = [
    ('learning/patches/ch01-ch06-teaching-v001.json', '7c500efabc93f22fa528d59957f77aad105f8edf8eb0fcf45a7cdcc5b857530e'),
    ('learning/patches/ch07-ch08-ch12-teaching-v001.json', '11a96a78f6d26cd30b9cbccfd237c56709a7d0dd16cac057b3abe8cbb26c4c2c'),
    ('learning/patches/shared-source-review-v001.json', '9a47e9880128579c26b2e890bf386fd926a6341f3b0fbd4938c1fdb13abce23d'),
]
SPECS = [
    ('11-17', '六件 STL 匯出、三角化修訂與重匯入', 'learning/lesson11_stl_export_optional_steps_v002.json', '012952c6764ef6c7ef6dd5a410a617390f0fd7cb194a2630963d00fdeb9a7b40', 44),
    ('11-18', 'CAD 牙型草圖：真約束與尺寸改動', 'learning/lesson11_cad_thread_optional_steps_v001.json', '446bc2fad2630e47a9a547baf338b43eb7b1da31eb9de3ac74db9a5ed6c8890b', 16),
    ('11-19', 'CAD 副本轉 mesh 與開口 Screw', 'learning/lesson11_cad_detached_screw_optional_steps_v001.json', '4e3dfac6c5f1f7977896d294d3e8c97522c0b0fefa7e178feab381f3560aa82c', 12),
    ('11-20', 'CAD 重開工具警告：限定恢復操作', 'learning/lesson11_cad_tool_recovery_optional_steps_v001.json', '3049c4e184be12305a0efe1866dbd73a4376eec63aab2e252d42cafcc98bc2b9', 7),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def verified(path, expected):
    actual = sha(ROOT / path)
    if actual != expected:
        raise ValueError('source changed: ' + path)
    return {'path': path, 'sha256': actual}


def artifact(path, label, expected=None):
    return {**verified(path, expected or sha(ROOT / path)), 'label': label}


def step_from_record(record, section, limits):
    image = record['screenshot']
    path = image.get('path', image.get('relativePath'))
    if not path.startswith('learning/evidence/') or '..' in Path(path).parts:
        raise ValueError('not raw evidence')
    verified(path, image['sha256'])
    actions = record['operation']
    if not isinstance(actions, list):
        actions = [actions]
    observed = record['programReadback']
    if not isinstance(observed, str):
        observed = json.dumps(observed, ensure_ascii=False)
    return {
        'id': 'ch11-' + record['id'].lower(), 'title': record['goal'], 'goal': record['goal'],
        'section': section, 'track': 'optional', 'context': record['context'],
        'actions': actions, 'success': record['visibleConfirmation'], 'shortcuts': [],
        'sourceSteps': [], 'evidenceStatus': 'existing_demo',
        'figures': [{'type': 'screenshot', 'path': path, 'sha256': image['sha256'],
                     'caption': '獨立 Blender 原始實拍；操作與程式讀值分列，不代表學員完成。'}],
        'limitations': list(limits),
        'detail': {'steps': actions + ['示範程式讀值：' + observed],
                   'why': '以本步原圖及讀值交叉核對；數位示範與實體量測及合格判定分開。'},
    }


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    verified(SOURCE.relative_to(ROOT).as_posix(), SOURCE_SHA)
    data = read(SOURCE)
    steps = {s['id']: s for c in data['chapters'] for s in c['steps']}
    sources = []
    replaced = []
    for path, expected in PATCHES:
        sources.append(verified(path, expected))
        patch = read(ROOT / path)
        for identifier, changes in patch['patches'].items():
            if identifier not in steps or steps[identifier].get('track') == 'appendix':
                raise ValueError('invalid active patch ' + identifier)
            steps[identifier].update(copy.deepcopy(changes))
            replaced.append(identifier)
    record_path = 'learning/lesson11_parameter_records_v001.json'
    sources.append(verified(record_path, '5124d40d506b8a4a01ea024f21e33203107045f104114f2b252b9a1fde15be87'))
    records = read(ROOT / record_path)
    record_copy = ROOT / 'learning/evidence/08/2026-10-28-ch11-parameter-records-v001/parameter-records-v001.json'
    record_copy.parent.mkdir(parents=True, exist_ok=True)
    if record_copy.exists() and sha(record_copy) != sha(ROOT / record_path):
        raise FileExistsError('different parameter record copy')
    if not record_copy.exists():
        record_copy.write_bytes((ROOT / record_path).read_bytes())
    for identifier, section in [('ch11-08-02-01', '11-04'), ('ch11-08-04-01', '11-06')]:
        record = next(r for r in records['sections'] if r['id'] == section)
        step = steps[identifier]
        step.update(evidenceStatus='documented_lesson', sourceSteps=[],
                    actions=[record['studentAction']], success='用途、名義參數、來源與未確認欄位分列，實體結果保持空白。',
                    artifacts=[artifact(record_copy.relative_to(ROOT).as_posix(), '螺紋／已選五金參數與官方來源表')],
                    limitations=record['limitations'],
                    detail={'steps': [p['name'] + '：' + str(p['value']) + (' ' + p['unit'] if p.get('unit') else '') + '；' + p['classification'] for p in record['parameters']],
                            'why': '設計名義值、供應商建議及實測值不能混用。'})
        replaced.append(identifier)
    steps['ch11-08-04-01']['goal'] = '核對已選料號的原廠規格與名義導孔；實際購入、材料、安裝與實測待確認。'
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch11')
    generated = {}
    for section, title, path, expected, count in SPECS:
        sources.append(verified(path, expected))
        doc = read(ROOT / path)
        if len(doc['steps']) != count:
            raise ValueError('unexpected step count')
        own = [step_from_record(s, section, doc['limitations']) for s in doc['steps']]
        summary_path = doc.get('sourceSummary') or 'learning/evidence/08/2026-10-28-ch11-stl-summary-v002/safe-summary-v001.json'
        own[0]['artifacts'] = [artifact(summary_path, '本節逐步實拍、來源與讀值安全摘要')]
        start = doc.get('startingScene')
        if isinstance(start, dict):
            verified(start['path'], start['sha256'])
            own[0]['context'] += ' 起始副本：' + start['path'] + '；SHA-256 ' + start['sha256'] + '。'
            own[0]['artifacts'].append(artifact(start['path'], '起始場景副本（保留原檔）', start['sha256']))
        final_scene = doc.get('demonstrationScene')
        if isinstance(final_scene, dict):
            verified(final_scene['path'], final_scene['sha256'])
            own[-1]['artifacts'] = [artifact(final_scene['path'], '示範另存場景（不是學員成果）', final_scene['sha256'])]
        if doc.get('sourceSummarySha256'):
            verified(doc['sourceSummary'], doc['sourceSummarySha256'])
        generated[section] = own
        chapter['sections'].append({'id': section, 'title': title, 'track': 'optional'})
        chapter['steps'].extend(own)
    generated['11-18'][12]['success'] = '畫面標註基邊 0.8 mm、草圖 Fully defined；尖點 X 約 5.97047 mm 為獨立幾何讀值，不是本圖直接顯示。'
    generated['11-18'][12]['limitations'].append('尖點 X 的數值須對照獨立場景幾何讀值；本步側欄主要顯示約束尺寸。')
    physical_section = next(s for s in chapter['sections'] if s['id'] == '11-07')
    physical_section.update(pendingLabel='實體待執行',
                            pendingReason='數位 STL 與現場方法已備妥；實際列印與試配尚未進行，結果留空，不能由數位示範代為確認。')
    # Readable, verifiable download links accompany the actual export evidence.
    stl_doc = read(ROOT / SPECS[0][2])
    for item in stl_doc['items']:
        target = next(s for s in generated['11-17'] if s['id'] == 'ch11-11-stl-' + item['id'] + '-06')
        target['artifacts'] = [artifact(item['stl'], item['title'] + '：實際 STL（按 mm 解讀）', item['stlSha256']),
                               artifact(item['independentAudit'], '獨立 Blender 重匯入檢查')]
    generated['11-19'][5]['limitations'] += ['本圖的灰色面來自未隱藏的原 CAD Body；副本 0 面由程式讀值核對，不能只憑此角度判定。']
    for index in (8, 9, 10):
        generated['11-19'][index]['limitations'] += ['本圖近景不能看到完整牙條；完整視圖見本節最後一步。']
    # Existing source models remain original; their later export repair is explicit.
    repair = ('後續實際 STL 檢查發現原場景 n-gon 三角化有反向重複三角形；'
              '匯出請接 11-17 的新三角化副本，原檔保留。修訂表面有微小改變，不能宣稱完全等同或已改善實體配合。')
    for step in chapter['steps']:
        if step['section'] in ('11-12', '11-15'):
            step.setdefault('limitations', []).append(repair)
    protocol = 'learning/journal/templates/printing-measurement-protocol-v001.json'
    for identifier in ('ch11-08-05-01', 'ch11-08-05-02'):
        step = steps[identifier]
        step.update(evidenceStatus='field_protocol_ready',
                    pendingLabel='實體待執行',
                    pendingReason='數位教材與現場方法已備妥；本步需要實際列印或試配，尚未執行。結果保持空白，現在只供查閱，不確認也不計入主線。',
                    artifacts=[artifact(protocol, '現場列印與試配方法（實體結果空白）')],
                    limitations=['現場方法已編寫；本步仍需實際材料、設備及零件，尚未執行，不由數位示範解除待辦。',
                                 '11-17 已提供六件數位 STL 與尺寸核對；11-19 開口 Screw 不在匯出實體清單內。'])
    steps['ch11-08-05-01'].update(title='實際列印螺紋對件', context='實際切片與列印，材料及設定先確認',
        actions=['依 11-17 核對修訂場景、STL SHA 及 mm 尺寸，再依第 06 章核對切片、方向與支撐候選。',
                 '實際列印後記錄材料、設定、來源與零件；尚未列印時不填結果。'],
        success='已有實際零件與可追溯條件，才能記錄本現場步驟。',
        detail={'steps': ['六件 STL 的實際匯出已在 11-17 完成；側盒與側帽須使用該節修訂版本。',
                          '按第 06 章流程核對切片與設備條件；材料、溫度及速度沒有依據時不編造。',
                          '列印、量測及試配結果保持空白，待實際操作後才填。'],
                'why': '數位檔案檢查不能替代製造與實體檢驗。'})
    steps['ch11-08-05-02'].update(actions=['取得實際件後，記錄旋入方向、起始位置、能否旋入與退出、鬆緊及損傷；遇卡住時停止強鎖。',
                                         '金屬五金分支另記嵌件安裝條件與螺絲版本；尚未試驗保持結果空白。'],
        detail={'steps': ['分清列印盒側帽與金屬五金兩個分支，記錄各自零件與來源。',
                          '保留每次旋入／退出的觀察與損傷紀錄；沒有扭矩或用途規格時不判定強度合格。'],
                'why': '名義間隙及零候選交疊不代表實際螺紋可旋合。'})
    order = [s['id'] for s in chapter['sections'] if s['id'] not in generated]
    order[order.index('11-13'):order.index('11-13')] = ['11-18', '11-19']
    order.insert(order.index('11-07'), '11-17')
    if '11-20' in generated:
        order.insert(order.index('11-19'), '11-20')
    chapter['sections'].sort(key=lambda s: order.index(s['id']))
    chapter['detailNote'] = '先學兩路輪廓：CAD 真約束在 11-18，副本轉 mesh 的開口 Screw 在 11-19；可匯出的封閉草案另走 11-13～17。11-17 六件 STL 已實際匯出與重匯入；側盒／側帽另存三角化修訂，實體試驗未進行。'
    for c in data['chapters']:
        if c['id'] in ('ch07', 'ch08', 'ch12'):
            c['detailNote'] = '本輪補齊安裝、版本、參數與現場方法；實拍及既有讀值逐步標示來源。量測、列印與試配結果仍空白；示範不是學員完成。'
    all_steps = [s for c in data['chapters'] for s in c['steps']]
    if len({s['id'] for s in all_steps}) != len(all_steps):
        raise ValueError('duplicate step identifiers')
    active_drafts = [s['id'] for s in all_steps if s.get('track') not in ('pending', 'appendix') and s.get('evidenceStatus') in ('draft_pending_demo', 'concept_only')]
    if active_drafts:
        raise ValueError('unresolved active lessons: ' + repr(active_drafts))
    for s in all_steps:
        if s.get('evidenceStatus') == 'existing_demo' and not s.get('figures') and not s.get('artifacts'):
            raise ValueError('unsupported demo ' + s['id'])
        for f in s.get('figures', []) + s.get('artifacts', []):
            if f.get('path') and f.get('sha256'):
                verified(f['path'], f['sha256'])
    data['version'] = 'v036 · 2026-10-28'
    data['pendingLabel'] = '實體待執行'
    data['evidenceStatusDefinitions'].update(
        documented_lesson='方法、參數、來源或空白表格已整理核對；本步為文件教學，不冒稱 GUI 或實體試驗。',
        field_protocol_ready='現場方法與空白紀錄已備妥；列印、量測、試配及合格結果仍未執行。')
    data['description'] += ' v036 補齊本輪數位教材、現場空白方法表、CAD 約束與獨立 mesh 銜接、六件 STL 的修訂匯出；實體結果仍未執行。'
    data['sourceVersions'] += [{'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA}] + sources
    data['contentReview']['reviewV036'] = {
        'reviewedOn': '2026-10-28', 'scope': '現行12章的缺課補齊；原圖/hash/讀值/來源與現場方法分別核對，沒有宣稱重拍或人工逐看全部歷史證據。',
        'updatedSteps': sorted(set(replaced)), 'addedOptionalSteps': sum(s[-1] for s in SPECS),
        'counts': dict(Counter(s.get('track', 'main') for s in all_steps)),
        'learnerProgressChanged': False, 'learnerProgressSha256': 'b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1',
        'physicalPrint': None, 'physicalMeasurement': None, 'physicalInstallation': None,
        'physicalFit': None, 'qualifiedClearance': None, 'qualifiedStrength': None,
        'remainingPhysicalSteps': ['ch11-08-05-01', 'ch11-08-05-02'],
        'sharedSourceReview': verified('learning/patches/shared-source-review-index-v001.json', 'ec0360421370fb982ecc6bdaf024a7365d53ebb134f82a60c4b19e5f97fcd8bf'),
        'publication': '本機教材整合；本輪未 commit 或 push。公開前仍須按排除規則重建並審查發布清單。',
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
