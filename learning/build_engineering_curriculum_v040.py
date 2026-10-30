"""Build one reviewed candidate: complete 85 pages; no learner-state mutations."""
import argparse
import copy
import hashlib
import html
import json
import struct
from pathlib import Path

from chapter_page_frontend_v002 import make_assets

ROOT = Path(__file__).resolve().parents[1]
LEARNING = ROOT / 'learning'
WEB = LEARNING / 'web'
SOURCE = WEB / 'engineering-curriculum-v039.json'
SOURCE_SHA = '495efda4dd94e59dcad7b68cdd408f1c3a0bfb9d1ff75d7112eae6a118540a12'
LEGACY_SOURCE_SHA = '9982e99ab03621766104df95b85d89f47fe716d9b123d72a0974a28f624afd09'
PATCH = LEARNING / 'patches/2026-10-30-chapter-completion-v040'
CANDIDATE = PATCH / 'candidate'
PHOTOS = LEARNING / 'evidence/chapters/2026-10-30-independent-step-reference-v005'
FAST = LEARNING / 'evidence/chapters/2026-10-30-efficient-duplicate-v003'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


def figure(source):
    """Only accept an actual, hash-matched PNG; preserve its native pixels."""
    name = source['path']
    path = ROOT / name if name.startswith('learning/') else LEARNING / name
    assert path.resolve().is_relative_to(LEARNING / 'evidence'), name
    assert sha(path) == source['sha256'], name
    raw = path.read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n', name
    width, height = struct.unpack('>II', raw[16:24])
    marks = []
    run = path.parent / 'run.json'
    if run.is_file():
        for record in read(run).get('records', []):
            if record.get('file') != path.name:
                continue
            for box in record.get('highlights', [])[:3]:
                x, y, w, h = [int(box[k]) for k in ['x', 'y', 'w', 'h']]
                if x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width and y+h <= height:
                    marks.append({'n': len(marks)+1, 'box': [x,y,w,h],
                                  'label': box.get('label', '操作位置').lstrip('123 ').strip()[:8]})
            break
    return {'path': path.relative_to(LEARNING).as_posix(), 'size': [width,height],
            'sha256': source['sha256'], 'caption': source.get('caption', '獨立 Blender 原始實拍。'),
            'marks': marks, 'evidenceRole': source.get('evidenceRole', 'existing_operation')}


def record_figure(folder, record, caption, role):
    return {'type': 'screenshot', 'path': (folder / record['file']).relative_to(ROOT).as_posix(),
            'sha256': record['sha256'], 'caption': caption, 'evidenceRole': role}


def methods():
    keys = 'https://docs.blender.org/manual/en/latest/interface/keymap/blender_default.html'
    ops = 'https://docs.blender.org/manual/en/latest/interface/operators.html'
    duplicate = 'https://docs.blender.org/manual/en/latest/scene_layout/object/editing/duplicate.html'
    return {
        '01-07': ('直接輸入位移，欄位作為核對', 'Object Mode 只選 Cube，滑鼠在 3D Viewport：G → X → 0.5m → Enter；N 的 Location X 用來核對。Ctrl+Z 取消這次已確認的位移。', '只在起始 X=0 時，位移 0.5m 才得到 X=0.5m；改絕對座標仍使用 N 欄位。', [keys,ops]),
        '03-03': ('F3 新增、F2 命名，尺寸保留精確輸入', '在 3D Viewport 用 F3 搜尋 Add Cube／Add UV Sphere，Enter 執行，F2 命名；在 N 的 Dimensions／Location 輸入本節指定數值。', 'F3 受游標所在編輯區及模式影響；不更動本章的單位與尺寸。', [keys,ops]),
        '03-08': ('在正確模式使用快捷操作', 'Tab 進 Edit Mode；上排 1／2／3 選點／邊／面，再用 G、I、E 配合數字。Esc 取消尚未確認的操作。', '數字鍵盤 1／3／7 是視角；上排數字是選取模式，兩者不同。', [keys,ops]),
        '04-04': ('複製幾何時先辨認共用材質', '同型零件可用 Shift+D 複製；更改各件材質前先查看材質使用者數，需獨立外觀時建立材質單用戶副本。', 'Shift+D 複製網格，仍可能共用材質；改色可能一起改。', [duplicate]),
        '05-02': ('先等距複製，再調各自孔寬', '只選第一件切割體：Shift+D → X → 14mm → Enter；立刻 Shift+R 四次得到六件，再逐一改 X/Y 寬為 10.1～10.6mm、Z維持8mm。切割體位置仍依本節 -35～35mm，最後核對並 Apply Scale。', 'Shift+R 只重複最近可重複的操作：必須先完成複製，再編輯尺寸。不要在改尺寸後用 Shift+R 當成複製；不要用 Alt+D 共用網格。不同孔寬不適合直接套同尺寸 Array。', [duplicate,keys]),
        '06-02': ('用重新匯入核對輸出，不重建幾何', 'STL 匯出後，在獨立空白副本用 F3 搜尋 Import STL，N 核對尺寸，再對照來源及輸出雜湊。', 'STL 不攜帶長度單位；本案用毫米解讀，數位尺寸不能當實際列印尺寸。', [ops,keys]),
        '07-02': ('原生搜尋與外掛約束分工', 'F3 用於原生檢視／檔案操作；CAD Sketcher 的草圖、尺寸及約束依本節外掛工具面板執行，先確認活動草圖。', '原生 Mesh 快捷鍵不能替代 CAD 尺寸約束；外掛快捷是否可用依隔離環境核對。', [ops]),
        '08-03': ('數值來源只建立一次', 'Driver 用同一組外長／外寬作來源，先核對變數路徑與表達式，再改主尺寸驗證內腔；不用手動重填每個結果尺寸。', '已含 Shape Keys 或 Driver 的模型，不隨意套用 Scale 或重建網格；先保存副本。', [keys]),
        '09-02': ('靠視角檢查，不為了看清而移動零件', '只選導軌／滑蓋，用 F3 Frame Selected，再用數字鍵盤 1／3／7 查看配合方向與底面。', 'Frame Selected 只改視角；不要用 G 移動已完成的配合幾何來取代檢查。', [keys,ops]),
        '10-02': ('相同卡扣先複製，參數對照保留獨立網格', '同形卡扣用 Shift+D；改梁長的對照件各自保留網格，F2 命名，再核對 N 的位置與尺寸。', '僅對同一幾何分支複製；不得把改長或複製視為已驗證的強度改善。', [duplicate,keys]),
        '11-13': ('三點輪廓使用數值輸入，取消誤操作', 'Edit Mode 的 G 配合 X/Z 和數字輸入輪廓位置；F3 搜尋必要原生操作。輸錯時尚未確認用 Esc，已確認才 Ctrl+Z。', '這是數值網格建點；不冒充 CAD 約束，也不把截面高度當成螺距。', [keys,ops]),
        '12-05': ('保留場景版本後一次輸出', '在渲染副本核對相機與輸出路徑後，用 F12 渲染當前影格、F11 查看 Render；保留來源 .blend 和輸出關聯。', '渲染圖只表達外觀，不作尺寸量測或配合合格證據。', [keys]),
    }


def build():
    assert sha(SOURCE) == SOURCE_SHA, 'v039 history changed'
    data = read(SOURCE)
    old = copy.deepcopy(data)
    pages = data['chapterPages']['sections']
    missing = {c['stepId'] for s in pages.values() for c in [s.get('prep'), *s['steps']]
               if c and not (c.get('figure') or c.get('figures'))}
    plan = {j['stepId']: j for j in read(PATCH / 'capture-plan-v003.json')['jobs']}
    records = read(PHOTOS / 'run.json')['records']
    assert len(missing) == len(records) == 30 and set(plan) == missing
    for folder in [PHOTOS, FAST]:
        status = read(folder / 'runner-status.json')
        assert status['status'] == 'completed' and status['workspacesUnchanged']
    assert all(c['passed'] for c in read(FAST / 'verification.json')['checks'])
    snapshots = {}
    for record in records:
        job = plan[record['step']]
        dims = ' × '.join(f'{v:.4g}' for v in record['observed']['dimensionsMM'])
        caption = f"{job['purpose']} 本圖 {record['observed']['active']} 名義外框 {dims} mm。"
        snapshots[record['step']] = record_figure(PHOTOS, record, caption, job['role'])
    steps = {s['id']: s for ch in data['chapters'] for s in ch['steps']}
    for s in pages.values():
        for card in [s.get('prep'), *s['steps']]:
            if card and card['stepId'] in snapshots:
                f = snapshots[card['stepId']]
                card['figure'] = figure(f)
                card['readings'] = [{'kind': 'readback', 'label': '數位準備讀值',
                                     'value': next(r['observed'] for r in records if r['step'] == card['stepId'])}]
                card.pop('figureNote', None)
                reading = next(r['observed'] for r in records if r['step'] == card['stepId'])
                scene = reading['preparedScene']
                assert sha(ROOT / scene['path']) == scene['sha256']
                card.setdefault('references', []).append({'path': scene['path'].removeprefix('learning/'), 'label': '助教數位準備副本（不是學員成果）'})
                steps[card['stepId']].setdefault('artifacts', []).append({'path':scene['path'], 'sha256':scene['sha256'], 'label':'本次獨立 Blender 數位準備版本'})

                step = steps[card['stepId']]
                step['figures'] = [copy.deepcopy(f)]
                step['preparationEvidence'] = {'role': f['evidenceRole'], 'physicalPrint': None,
                                               'physicalMeasurement': None, 'physicalFit': None}
    converted = []
    for sid, page in pages.items():
        if page.get('prep') or page['steps']:
            continue
        source_steps = [s for s in steps.values() if s.get('section') == sid]
        assert source_steps, sid
        page['steps'] = []
        page['keyPoint'] = source_steps[0].get('goal', page['title'])
        page['scope'] = ('本節包含實體待執行方法；照片只作數位準備，實際列印與試配結果保持空白。'
                         if all(s.get('track') == 'pending' for s in source_steps)
                         else '本節選修草案沿用已綁定的實拍與讀值；不代表學員完成、材料或配合合格。')
        for step in source_steps:
            fs = step.get('figures') or step.get('demonstration', {}).get('figures', [])
            fs = list({f['path']: f for f in fs if f.get('type') == 'screenshot'}.values())
            if not fs:
                # CLI and physical methods get a labelled related digital reference, never fabricated evidence.
                reference = 'ch08-param-plan' if sid == '08-08' else 'ch11-08-02-01'
                f = copy.deepcopy(snapshots[reference])
                f['caption'] = '相關數位場景參考；本步的 CLI／實體操作尚不能由此照片證明。' + f['caption']
                f['evidenceRole'] = 'related_reference'
                fs = [f]
            readings = copy.deepcopy(step.get('demonstration', {}).get('readings', []))
            checks = [step['success']]
            value = next((str(r['value']) for r in readings if isinstance(r.get('value'), str)), None)
            extra = value or next(iter(step.get('limitations', [])), step.get('goal', step['title']))
            if extra != checks[0]:
                checks.append(extra)
            else:
                checks.append('核對作用中物件、模式與來源版本，保留本步原圖供對照。')
            context = str(step.get('context', step.get('goal', '')))
            card = {'stepId': step['id'], 'title': step['title'], 'track': step.get('track', 'optional'),
                    'lead': context.split('本組來源：')[0][:240],
                    'actions': [html.escape(a) for a in step['actions']], 'checks': [html.escape(c) for c in checks[:3]],
                    'figures': [figure(f) for f in fs], 'readings': readings,
                    'references': [{'path': a['path'].removeprefix('learning/'), 'label': a.get('label', '讀值與來源')}
                                   for a in step.get('artifacts', []) if Path(a['path']).suffix in ['.json', '.md']],
                    'cautions': [context, *step.get('limitations', []), step.get('detail', {}).get('why', '')],
                    'keys': []}
            assert 1 <= len(card['actions']) <= 3 and len(card['checks']) >= 2
            page['steps'].append(card)
        definitions = {
            'Driver': '以變數及表達式由來源數值計算目標屬性；需核對資料路徑與更新結果。',
            'CAD Sketcher': '提供幾何約束與尺寸求解的第三方擴充套件，與原生 mesh 編輯不同。',
            'Screw': '沿指定軸旋轉並平移截面的修改器；輸出不必然是封閉實體。',
            'STL': '儲存三角形表面的交換格式，不攜帶本案所需的毫米單位資訊。',
            'Boolean': '利用物件的聯集、差集或交集產生幾何；仍需核對拓樸與局部細節。',
            'Scale': '物件層級縮放；Dimensions 是尺寸，兩者不能互相替代。',
            '三角化': '把表面轉成三角形；非平面面的分割方式可能改變局部形狀。',
            '非流形': '需檢查的拓樸情況，例如開口或一條邊連接不合預期的面；不是單一製造合格判準。',
            '自交': '同一幾何的表面互相穿越；需指定方法與範圍檢查。',
            '外牙': '位於外側圓柱或相關表面的螺紋，需對照配套內牙及旋入方向。',
            '內牙': '位於孔內或保護蓋內側的螺紋；名義配合不等於已驗證旋合。',
            '螺距': '沿軸向相鄰對應牙型位置的距離；多頭螺紋的導程另行計算。',
            '盲孔': '沒有穿透零件的孔，需核對孔底厚度及有效深度。',
            '導孔': '依五金及製程選定的預備孔；原廠建議、設計值與實測需分列。',
            '總間隙': '本案相同方向上孔尺寸與軸尺寸的差；單側值須依置中關係判讀。',
            '約束': '限定草圖幾何的尺寸或幾何關係；需查看求解狀態及自由度。',
            '徑向': '相對螺紋軸線向外的方向；徑向差與直徑差數值不同。',
            '軸向': '沿螺紋中心軸線的方向；與徑向尺寸分開核對。',
        }
        text = html.unescape(json.dumps([{k: c.get(k) for k in ['lead', 'actions', 'checks', 'cautions']}
                                        for c in page['steps']], ensure_ascii=False))
        page['glossary'] = [{'term': term, 'label': term, 'text': definition}
                            for term, definition in definitions.items() if term in text][:4]
        converted.append(sid)
        for ch in data['chapterPages']['outline']['chapters']:
            for s in ch['sections']:
                if s['id'] == sid:
                    s['track'] = 'pending' if all(x.get('track') == 'pending' for x in source_steps) else 'optional'
                    s['taughtSteps'] = len(source_steps)
    assert len(converted) == 15
    for sid, (title, workflow, caution, urls) in methods().items():
        pages[sid]['efficiency'] = {'title': title, 'workflow': workflow, 'caution': caution, 'sources': urls}
        step = steps[pages[sid]['steps'][0]['stepId']]
        step.setdefault('shortcuts', []).append({'keys': title, 'effect': workflow, 'requirements': [step.get('context', '')], 'cautions': [caution]})
    # Change the actual instructions, not merely append a generic shortcut catalogue.
    pages['01-07']['steps'][0]['actions'] = [
        'Object Mode 只選 Cube，滑鼠在 3D Viewport：<kbd>G</kbd> → <kbd>X</kbd> → <code>0.5m</code> → Enter。',
        '按 <kbd>N</kbd> 在 Item 的 Location X 核對；起始 X=0 才應為 0.5m。要改絕對座標時直接輸入欄位。']
    basic = steps[pages['01-07']['steps'][0]['stepId']]
    basic['actions'] = ['Object Mode 只選 Cube，滑鼠在 3D Viewport：G → X → 0.5m → Enter。',
                        'N 的 Location X 核對結果；起始 X=0 才應為0.5m；絕對座標仍可直接填欄位。']
    basic.setdefault('detail', {})['steps'] = list(basic['actions'])
    updates = {
        'ch05-05-03-03': ['F3 搜尋 Add Cube，N 輸入 Dimensions <code>10.1mm</code>、<code>10.1mm</code>、<code>8mm</code>；F3 搜尋 Apply Scale。', '用 G X <code>-35mm</code>、G Y <code>2mm</code> 到中心 (-35,2,0) mm；此時再開始複製。'],
        'ch05-05-03-04': ['只選第一件切割體，<kbd>Shift+D</kbd> → X → <code>14mm</code> → Enter，立刻 <kbd>Shift+R</kbd> 四次先完成六件等距副本。', '完成全部複製後才逐一改孔寬：第2、第3件 N 的 X/Y Dimensions 為 <code>10.2mm</code>、<code>10.3mm</code>，Z維持8mm；Apply Scale。'],
        'ch05-05-03-05': ['逐一選第4～6件，把 N 的 X/Y Dimensions 設為 <code>10.4mm</code>、<code>10.5mm</code>、<code>10.6mm</code>，Z維持8mm；Apply Scale。', '核對六件中心 X=-35,-21,-7,7,21,35mm、Y=2mm。不同孔寬使用獨立網格，不用 Alt+D；此時不再以 Shift+R 複製。'],
    }
    for page in pages.values():
        for card in page['steps']:
            if card['stepId'] in updates:
                card['actions'] = updates[card['stepId']]
                steps[card['stepId']]['actions'] = [a.replace('<code>', '').replace('</code>', '').replace('<kbd>', '').replace('</kbd>', '') for a in card['actions']]
                steps[card['stepId']].setdefault('detail', {})['steps'] = list(steps[card['stepId']]['actions'])
                card.setdefault('cautions', []).append('原實拍保留逐件新增的歷史操作；新版快捷試驗另列。只比較對應名義幾何，不把兩場操作混成同一場。')
    fast_records = read(FAST / 'run.json')['records']
    extra_photos = [figure(record_figure(FAST, r, '快捷原理試驗從 X=0 起算；本節孔板須從 (-35,2,0)mm 開始。' + r['action'] + ' 尚未做孔板 Boolean。', 'shortcut_verification'))
                    for r in fast_records if r['slug'] in ['repeat-shift-r', 'six-varied-cutters']]
    assert len(extra_photos) == 2
    target = pages['05-02']['steps'][2]
    if target.get('figure'):
        target['figures'] = [target.pop('figure')]
    for old_figure in target.get('figures', []):
        old_figure['tab'] = '歷史幾何對照'
        old_figure['caption'] = '舊版逐件新增的幾何對照。' + old_figure['caption']
    for f in extra_photos:
        f['tab'] = '新版快捷實測'
    target['figures'] = extra_photos + target.get('figures', [])
    cards = [c for s in pages.values() for c in [s.get('prep'), *s['steps']] if c]
    assert len(cards) == len({c['stepId'] for c in cards}) == 447
    assert [s['id'] for ch in data['chapters'] for s in ch['steps']] == [s['id'] for ch in old['chapters'] for s in ch['steps']]
    data['version'] = 'v040 · 2026-10-30'
    data['sourceVersions'].append({'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA})
    data['chapterPages']['scope'] = '85節完整新版版型、447張教學卡：243主線、202選修、2實體待執行；歷史附錄與速查保留入口。'
    data['contentReview']['completionV040'] = {'photoReferences': 30, 'convertedSections': converted,
        'shortcutSources': (PATCH / 'shortcut-sources.json').relative_to(ROOT).as_posix(),
        'photoScope': 'Digital preparation/reference only; no physical or web-registration results claimed.',
        'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None}
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--promote', action='store_true')
    args = parser.parse_args()
    data = build()
    html_text, css, js = make_assets((LEARNING / 'drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
    CANDIDATE.mkdir(exist_ok=True)
    files = {'index.html': html_text, 'chapter-pages-v001.css': css, 'chapter-pages-v001.js': js}
    snapshot = PATCH / 'source-snapshot/engineering-path.js'
    if not snapshot.exists():
        snapshot.parent.mkdir(exist_ok=True)
        assert sha(WEB / 'engineering-path.js') == LEGACY_SOURCE_SHA
        snapshot.write_bytes((WEB / 'engineering-path.js').read_bytes())
    assert sha(snapshot) == LEGACY_SOURCE_SHA
    legacy = snapshot.read_text('utf8')
    # The user explicitly removed the cross-course next-step prompt from chapter pages.
    assert '${nextButton}</header>${renderProgress(bootstrap, curriculum)}' in legacy
    legacy = legacy.replace('${nextButton}</header>${renderProgress(bootstrap, curriculum)}', '</header>')
    legacy = legacy.replace('${resume}</section>${pilot}', '</section>${pilot}')
    files['engineering-path.js'] = legacy
    for name, text in list(files.items()):
        eol = '\r\n' if b'\r\n' in (WEB / name).read_bytes() else '\n'
        files[name] = text.replace('\r\n', '\n').replace('\n', eol).encode('utf8')
    if args.promote:
        output = WEB / 'engineering-curriculum-v040.json'
        if output.exists():
            raise FileExistsError('refusing to overwrite v040')
        baseline = read(PATCH / 'before.json')
        for name in ['learning/manage.py', 'learning/web/index.html', 'learning/web/engineering-path.js',
                     'learning/server.py', 'README.md', 'AGENTS.md']:
            assert sha(ROOT / name) == baseline[name], 'concurrent edit: ' + name
        proof = read(PATCH / 'smoke/results.json')
        assert proof['sections'] == proof['passed'] == 85
        for name, payload in files.items():
            assert proof['releaseHashes'][name] == hashlib.sha256(payload).hexdigest()
        encoded = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8')
        assert proof['releaseHashes']['engineering-curriculum-v040.json'] == hashlib.sha256(encoded).hexdigest()
        write_json(output, data)
        for name, payload in files.items():
            (WEB / name).write_bytes(payload)
        path = LEARNING / 'manage.py'
        raw = path.read_bytes()
        needle = b'engineering-curriculum-v039.json'
        assert raw.count(needle) == 1
        path.write_bytes(raw.replace(needle, b'engineering-curriculum-v040.json'))
    else:
        write_json(CANDIDATE / 'engineering-curriculum-v040.json', data)
        for name, payload in files.items():
            (CANDIDATE / name).write_bytes(payload)
    print(json.dumps({'version': data['version'], 'sections':85, 'cards':447, 'promoted':args.promote}))


if __name__ == '__main__':
    main()
