"""Engineering curriculum v029 / path v003: learner-approved order B with chapter sections.

Order: basics → tolerance concepts → mm modelling (with Edit Mode basics and the fixed lid) → signal-station render →
fit coupons → export, print, measure and choose a clearance → CAD Sketcher → parametric box and lid (guard panel
optional) → tenon/dovetail → snap fit → threads → dimension chain, delivery and finished render.
Every chapter is split into sections (節) holding the small steps. Chapters 01-06 are rewritten as instructions the
learner can follow; 07-12 keep v028 text with short titles. v028 and path v002 stay unchanged.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v028.json'
SOURCE_SHA = 'f7ff40301a86d9eea544f02f6a7f006f31345f84f1781ad81052de220294a188'
PATH_SOURCE = ROOT / 'learning/web/engineering-path-v002.json'
PATH_SOURCE_SHA = '28cfa6959794d6e6423459cd7ab5e7b376e4c487adc23432078c8be4bfdadf95'
TEXT = ROOT / 'learning/engineering_v029_text.py'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v029.json'
PATH_OUTPUT = ROOT / 'learning/web/engineering-path-v003.json'
VERSION = 'v029 · 2026-10-28'

# v028 steps whose content is now carried by several rewritten steps.
REPLACED = {
    'ch05-05-05-01': ['ch03-05-05-01', 'ch03-05-05-02', 'ch03-05-05-03'],
    'ch05-05-05-02': ['ch03-05-05-04', 'ch03-05-05-05', 'ch03-05-05-06'],
    'ch05-05-05-03': ['ch03-05-05-07', 'ch03-05-05-08'],
    'ch06-05-03-01': ['ch05-05-03-01', 'ch05-05-03-02', 'ch05-05-03-03', 'ch05-05-03-04', 'ch05-05-03-05'],
    'ch06-05-03-02': ['ch05-05-03-06', 'ch05-05-03-07', 'ch05-05-03-08', 'ch05-05-03-09', 'ch05-05-03-10', 'ch05-05-03-11'],
    'ch07-05-04-03': ['ch06-fit-01', 'ch06-fit-02', 'ch06-fit-03', 'ch06-fit-04'],
}
APPENDIX_CHAPTER = 'ch08'

PATH_OVERRIDES = {
    'ch01': {'availabilityLabel': '有既有教材可參照',
             'practice': ['開啟 Blender、確認畫面並切換英文介面。', '練習選取、視角、精確移動與 Dimensions，另存 v001／v002 並重開。',
                          '最後看示範原圖，辨認蓋板、唇邊與配合的兩個表面。'],
             'notes': ['先學操作，再看要做的小盒；兩題觀察放在章末。', '建模原點與零件的功能基準需要另外對應，不能自動視為相同。']},
    'ch02': {'notes': ['畫面小數位數、浮點誤差門檻、量具解析度與製造公差是不同概念。', '先教可觀察的差異，完整尺寸鏈留第 12 章。']},
    'ch03': {'availabilityLabel': '既有參照＋新補基礎',
             'practice': ['訊號站：新增物件、尺寸、位置與命名。', '毫米方塊與 Edit Mode 基礎：點／邊／面選取、G、I、E、H 與底部視角。',
                          '原盒 60 × 40 × 30 mm，以及固定尺寸上蓋與環形唇邊。'],
             'functions': ['毫米單位設定', '點／邊／面選取', 'Transform、Inset、Extrude、Solidify 與 Apply Scale'],
             'notes': ['Object Mode 的 I 會插入關鍵影格，不能當 Inset；內插要先進 Edit Mode。',
                       'Edit Mode 基礎一節沒有示範原圖，依介面名稱操作，畫面不同先回報。']},
    'ch04': {'title': '訊號站材質、燈光與渲染',
             'practice': ['用第 03 章的訊號站安排相機、燈光與材質。', '輸出第一張圖，重開場景再渲染一次。'],
             'notes': ['原課程第三單元；放在建模之後，及早看到完整成果。', '小盒成品渲染在第 12 章。']},
    'ch06': {'practice': ['匯出原盒、插銷、孔板與上蓋 STL，重新匯入核對尺寸。', '列印試片、量測、逐孔試配並選定自己的總間隙。',
                          '列印原盒並量測；上蓋等第 08 章用選定間隙更新後再印。'],
             'notes': ['STL 沒有單位標記，本專案按毫米解讀並核尺寸。', '選定間隙只適用你的設備、材料與設定；換條件要重新試配。']},
    'ch07': {'practice': ['安裝 CAD Sketcher 0.32.1，建立工程工作區。', '畫 60 × 40 mm 矩形並標尺寸、改成 80 mm，拉伸成實心體，再畫內腔草圖切割。'],
             'notes': ['求解成功不等於完全約束；要核對自由度。', '讓內腔跟著外框變的 Driver 在第 08 章。',
                       '本章沿用 v028 的示範紀錄文字，學到本章前會逐步改寫並實測。']},
    'ch08': {'practice': ['先看固定內腔不會跟著外框變的反例，再用 Driver 讓內腔跟著變。',
                          '用形狀鍵與 Driver 讓上蓋跟著盒體尺寸變；總間隙用第 06 章選定的值。',
                          '選修：受控尺寸面板（只接受指定示範盒的副本）。'],
             'notes': ['受控面板是選修，不計入主線進度，也不擋住後面章節。', '原生欄位可繞過面板；面板不攔截存檔與匯出。',
                       '本章沿用 v028 的示範紀錄文字，學到本章前會逐步改寫並實測。']},
    'ch12': {'practice': ['分析內腔、唇邊及位置偏差的最不利組合，區分尺寸間隙與形狀／位置問題。',
                          '彙整實測證據、補償理由、適用條件與版本，完成總組裝。', '用第 04 章學到的相機、燈光與材質渲染小盒成品。'],
             'notes': ['不由單次成功試配推定整批或不同材料都適用。', '幾何公差與製程能力進階內容依具體功能和量測資料展開。']},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_checked(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('source changed: ' + path.name)
    return json.loads(raw.decode('utf-8-sig'))


def load_text():
    spec = importlib.util.spec_from_file_location('engineering_v029_text', TEXT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refs_of(step):
    refs = list(step.get('figures', [])) + list(step.get('artifacts', []))
    for shortcut in step.get('shortcuts', []):
        refs += shortcut.get('evidence', [])
    return refs


def check_refs(refs):
    for ref in refs:
        path = (ROOT / ref['path']).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file() or sha(path) != ref['sha256']:
            raise ValueError('missing or changed: ' + ref['path'])


def as_list(value):
    return [value] if isinstance(value, str) else list(value or [])


def build_curriculum(source, path, text):
    old = {step['id']: step for chapter in source['chapters'] for step in chapter['steps']}
    old_chapters = {chapter['id']: chapter for chapter in source['chapters']}
    first, follow = path['firstActivity'], path['followUpActivity']
    used, changes, rewritten = set(), {}, []

    def borrowed(field, ids):
        items = []
        for step_id in as_list(ids):
            for item in old[step_id].get(field, []):
                if item not in items:
                    items.append(copy.deepcopy(item))
        return items

    def make(item, chapter_id):
        if item['kind'] == 'keep':
            step = copy.deepcopy(old[item['old']])
            step['id'] = item.get('new') or chapter_id + item['old'][4:]
            step['title'] = item['title']
            changed = [field for field in ('goal', 'context', 'actions', 'success') if field in item]
            for field in changed:
                step[field] = copy.deepcopy(item[field])
            if 'replace' in item:
                before, after = item['replace']
                if not any(before in action for action in step['actions']):
                    raise ValueError('replace target missing: ' + item['old'])
                step['actions'] = [action.replace(before, after) for action in step['actions']]
                changed.append('actions')
            if item.get('addLimitations'):
                step['limitations'] = list(step.get('limitations', [])) + item['addLimitations']
            if item.get('addFiguresFromFollowUp'):
                step['figures'] += [copy.deepcopy(f) for f in follow['figures'] if f['path'] not in {g['path'] for g in step['figures']}]
            used.add(item['old'])
            if step['id'] != item['old']:
                changes[item['old']] = step['id']
            if changed:
                rewritten.append(step['id'])
            return step
        step = {'id': item['new'], 'title': item['title'], 'goal': item['goal'], 'context': item['context'],
                'actions': list(item['actions'] or []), 'success': item['success'],
                'shortcuts': borrowed('shortcuts', item.get('shortcutsFrom')),
                'figures': borrowed('figures', item.get('figuresFrom')),
                'sourceSteps': [{'lessonId': s[:2], 'stepId': s} for s in item['source']],
                'evidenceStatus': item['status'], 'limitations': list(item['limitations'])}
        if item.get('fromFirstActivity'):
            step.update(goal=first['goal'], actions=list(first['actions']) + ['回答：' + first['question']],
                        success=first['success'], figures=copy.deepcopy(first['figures']))
        if item.get('legacyActivity'):
            step['legacyActivity'] = item['legacyActivity']
        if step['evidenceStatus'] == 'source_step_demo' and step['figures']:
            step['evidenceStatus'] = 'existing_demo'
        return step

    chapters = []
    for spec in text.CHAPTERS + text.LATER:
        base = old_chapters[spec['from']]
        chapter = {'id': spec['id'], 'number': spec['id'][2:], 'title': spec['title'],
                   'goal': spec.get('goal', base['goal']), 'deliverable': spec.get('deliverable', base['deliverable']),
                   'limitations': list(spec.get('limitations', base['limitations'])), 'sections': [], 'steps': []}
        for section_id, section_title, items in spec['sections']:
            section = {'id': section_id, 'title': section_title}
            if section_id in text.OPTIONAL_SECTIONS:
                section['track'] = 'optional'
            chapter['sections'].append(section)
            for item in items:
                step = make(item, spec['id'])
                step['section'] = section_id
                if section_id in text.OPTIONAL_SECTIONS:
                    step['track'] = 'optional'
                chapter['steps'].append(step)
        chapters.append(chapter)

    appendix = [sid for chapter in source['chapters'] for sid in [s['id'] for s in chapter['steps']] if old[sid].get('track') == 'appendix']
    target = next(chapter for chapter in chapters if chapter['id'] == APPENDIX_CHAPTER)
    for step_id in appendix:
        step = copy.deepcopy(old[step_id])
        step['id'] = APPENDIX_CHAPTER + step_id[4:]
        changes[step_id] = step['id']
        used.add(step_id)
        target['steps'].append(step)
    target['appendix'] = {'title': '附錄：失敗探測、舊版工具與測試紀錄',
                          'summary': '原生 Driver 首次試驗的失敗探測、程式建立的參數盒範本、舊版預檢面板（v005／v007）與受控面板的假專案測試。保留原圖與讀值供查核；不需操作，也不計入學員小步。'}
    target['limitationHistory'] = old_chapters['ch04'].get('limitationHistory', []) + old_chapters['ch05'].get('limitationHistory', [])
    target['limitations'] = [line for line in old_chapters['ch05']['limitations'] if not line.startswith('學員路徑')] + [
        '外框草圖改尺寸時，內腔切割體不會自動跟隨；即使顯示 Fully defined，也要進內腔草圖按更新並核對讀值。']
    ch07 = next(chapter for chapter in chapters if chapter['id'] == 'ch07')
    ch07['limitations'] = [line for line in old_chapters['ch04']['limitations'] if not line.startswith('外框草圖改尺寸時')]

    used.update(REPLACED)
    produced = {step['id'] for chapter in chapters for step in chapter['steps']}
    missing = set(old) - used
    if missing:
        raise ValueError('v028 steps not placed: ' + ', '.join(sorted(missing)))
    for old_id, new_ids in REPLACED.items():
        if not set(new_ids) <= produced:
            raise ValueError('replacement missing for ' + old_id)
    ids = [step['id'] for chapter in chapters for step in chapter['steps']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate step IDs')
    for chapter in chapters:
        sections = {section['id'] for section in chapter['sections']}
        for step in chapter['steps']:
            if step.get('track') != 'appendix' and step.get('section') not in sections:
                raise ValueError('step outside a section: ' + step['id'])
            if not step['id'].startswith(chapter['id'] + '-'):
                raise ValueError('step ID does not match chapter: ' + step['id'])
            if step['evidenceStatus'] == 'existing_demo' and not (step.get('figures') or step.get('artifacts')):
                raise ValueError('existing_demo without own evidence: ' + step['id'])
            check_refs(refs_of(step))

    data = copy.deepcopy(source)
    data['chapters'] = chapters
    data['version'] = VERSION
    data['description'] = '12章詳細操作參照；v029依學員選定的方案 B 調整章序（基礎→公差→毫米建模→渲染→試片→列印量測→草圖→參數連動→結構→尺寸鏈），每章分節，第01～06章改寫為可照做的指示。'
    data['trackDefinitions'] = dict(data['trackDefinitions'],
                                    optional='選修：可以照做並確認，但不計入主線進度，也不擋住後面章節。')
    data['sourceVersions'] = data['sourceVersions'] + [{'path': 'learning/web/engineering-curriculum-v028.json', 'sha256': SOURCE_SHA},
                                                       {'path': 'learning/web/engineering-path-v002.json', 'sha256': PATH_SOURCE_SHA}]
    data['stepIdChanges'] = dict(sorted(changes.items()))
    data['replacedSteps'] = REPLACED
    data['contentReview'] = dict(data['contentReview'], reviewV029={
        'reviewedOn': '2026-10-28', 'reviewer': 'Claude Code（依學員 2026-10-28 選定的方案 B 與四項決定）',
        'decisions': ['章序採方案 B', '受控尺寸面板改為選修', '以新版小步為主要進度', '先改寫第 01～06 章', '頂部觀察題併入第 01 章章末', '新版章節分兩層（章／節）'],
        'rewrittenSteps': sorted(rewritten), 'newSteps': sorted(produced - set(changes.values()) - {s for s in old}),
        'uiEvidence': 'Blender 5.2.1（9e2066aef7ef）讀回：Select All by Trait > Non Manifold、View > Viewpoint > Bottom、Object > Show/Hide > Hide Selected、Add Modifier > Generate > Solidify／Boolean、Object > Apply > Scale、Preferences Interface 的 Language 面板與 Save Preferences／Auto-Save Preferences、Image > Save As...；出廠鍵位 H、Alt+H、Shift+D、Ctrl+J、I、E、1／2／3、Ctrl+Numpad 7。',
        'sourceFacts': '孔板孔位與凹點排列取自 learning/evidence/05/2026-10-22-lesson05-holes-demo-v002/trial-plan.json 與 learning/tutor/scenarios/lesson05_holes.py；Post／Signal 尺寸取自 catalog 02-03 help；上蓋輸入值取自 learning/tutor/scenarios/lesson05_lid.py。',
        'learnerProgressChanged': False})
    return data


def build_path(path, curriculum, text):
    data = copy.deepcopy(path)
    for key in ('firstActivity', 'followUpActivity'):
        data.pop(key, None)
    data['id'] = 'engineering-path-v003'
    data['version'] = 'v003 · 2026-10-28'
    data['intro'] = '先學基本操作與毫米建模，做出原盒與上蓋並渲染第一張圖；接著印試片、量測並選定自己的配合間隙，再進入草圖與參數連動。每章分節，節底下是一次做一小步的操作。原9單元52步保留可回查；閱讀不等於完成。'
    data['environment'] = dict(data['environment'], summary=data['environment']['summary'].replace('第 04 章', '第 07 章'))
    old = {chapter['id']: chapter for chapter in path['chapters']}
    chapters = []
    for spec in text.CHAPTERS + text.LATER:
        chapter = copy.deepcopy(old[spec['from']])
        built = next(c for c in curriculum['chapters'] if c['id'] == spec['id'])
        chapter.update(id=spec['id'], number=spec['id'][2:], title=spec['title'], goal=built['goal'], deliverable=built['deliverable'])
        chapter.update(copy.deepcopy(PATH_OVERRIDES.get(spec['id'], {})))
        if spec['id'] == 'ch12':
            chapter['shortcuts'] = chapter['shortcuts'] + copy.deepcopy(old['ch12']['shortcuts'])
        chapters.append(chapter)
    data['chapters'] = chapters
    data['contentReview'] = dict(data['contentReview'], reviewedOn='2026-10-28', revisionV003={
        'scope': '依方案 B 重排章節並更新各章目標、實作、備註；接續觀察題併入教材第 01 章章末，路徑不再另列觀察面板。',
        'curriculum': {'path': 'learning/web/engineering-curriculum-v029.json'}, 'learnerCompletionChanged': False})
    return data


def write(path, data):
    if path.exists():
        raise FileExistsError('refusing to overwrite ' + path.name)
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    path.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
    return sha(path)


def main():
    source = read_checked(SOURCE, SOURCE_SHA)
    path = read_checked(PATH_SOURCE, PATH_SOURCE_SHA)
    text = load_text()
    curriculum = build_curriculum(source, path, text)
    outline = build_path(path, curriculum, text)
    if [c['id'] for c in outline['chapters']] != [c['id'] for c in curriculum['chapters']]:
        raise ValueError('path and curriculum chapters differ')
    print(write(OUTPUT, curriculum))
    print(write(PATH_OUTPUT, outline))


if __name__ == '__main__':
    main()
