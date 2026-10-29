"""Reorganise the engineering curriculum for the learner (v028) and move page text into data (path v002).

v027 and path v001 stay unchanged. Each original lesson is kept whole and in order inside one
chapter, duplicated steps are removed, development trials become a chapter appendix that is not
counted as learner work, and steps without their own screenshot get an honest evidence status.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v027.json'
SOURCE_SHA = '615b1ef2f3482b1f585548a82ab0cf86528c546e42a792cccaeaa0dbb935be2b'
PATH_SOURCE = ROOT / 'learning/web/engineering-path-v001.json'
PATH_SOURCE_SHA = '6dcc77a613a905f35cd793e96c6d20ad0c39bb4cf915a30de5f0fddd1e1dca5f'
CATALOG = ROOT / 'learning/catalog.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v028.json'
PATH_OUTPUT = ROOT / 'learning/web/engineering-path-v002.json'
VERSION = 'v028 · 2026-10-27'

# Verified copy source for the controlled panel (the panel pins its sketch constraint UIDs and lid topology).
MANUAL_BOX_BASE = ('learning/evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend',
                   'ddae8a3d3745146501d25527354352e6b71431b837c78c8269a43dc5e6a3dec6')
CAD_SKETCHER_ZIP_SHA = 'b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59'

# Steps that sat in a different chapter from the rest of their original lesson.
MOVED = {f'ch11-01-04-0{n}': f'ch01-01-04-0{n}' for n in (1, 2, 3)}
MOVED.update({f'ch11-01-09-0{n}': f'ch01-01-09-0{n}' for n in (1, 2, 3)})
MOVED.update({f'ch03-01-07-0{n}': f'ch01-01-07-0{n}' for n in (1, 2, 3)})
MOVED.update({f'ch12-02-0{k}-0{n}': f'ch03-02-0{k}-0{n}' for k in (1, 2, 3, 4) for n in (1, 2, 3)})
# Byte-for-byte copies (apart from the ID) of steps that remain in their own chapter.
DUPLICATES = {f'ch01-05-05-0{n}': f'ch05-05-05-0{n}' for n in (1, 2, 3)}
DUPLICATES.update({f'ch02-04-08-0{n}': f'ch07-04-08-0{n}' for n in (1, 2, 3)})

CH04_APPENDIX = ['ch04-driver-partial-05', 'ch04-driver-partial-06']
CH05_LEARNER = (['ch05-param-plan', 'ch05-05-05-01', 'ch05-05-05-02', 'ch05-05-05-03']
                + [f'ch05-manual-lid-fixed-0{n}' for n in range(1, 5)]
                + [f'ch05-manual-lid-link-0{n}' for n in range(1, 7)]
                + [f'ch05-manual-lid-cases-0{n}' for n in range(1, 4)]
                + ['ch05-manual-lid-clamp-01', 'ch05-manual-lid-clamp-02',
                   'ch05-guard-prepare-01', 'ch05-manual-guard-restart-01',
                   'ch05-manual-guard-01', 'ch05-manual-guard-02', 'ch05-manual-guard-03', 'ch05-manual-guard-04',
                   'ch05-manual-guard-xy-01', 'ch05-manual-guard-xy-02', 'ch05-manual-guard-y-reject-01',
                   'ch05-guard-checkpoint-01', 'ch05-manual-guard-restart-02'])
CH05_APPENDIX = (['ch05-linked-01', 'ch05-linked-02', 'ch05-linked-03', 'ch05-linked-04',
                  'ch05-linked-y-01', 'ch05-linked-y-02', 'ch05-linked-y-03']
                 + [f'ch05-guard-0{n}' for n in range(1, 9)]
                 + [f'ch05-guard-v007-0{n}' for n in range(1, 10)]
                 + ['ch05-manual-guard-xy-03', 'ch05-manual-guard-xy-04',
                    'ch05-manual-guard-registered-01', 'ch05-manual-guard-fault-01'])
APPENDIX = {
    'ch04': {'title': '附錄：失敗探測紀錄',
             'summary': '保留原生 Driver 首次試驗中切回草圖失敗與保存失敗探測的紀錄，供查核示範過程；不需操作，也不計入學員小步。'},
    'ch05': {'title': '附錄：舊版工具與測試紀錄',
             'summary': '程式建立的參數盒範本、舊版預檢面板（v005／v007）與受控面板的另存、已登記拒絕、故障注入等假專案測試。保留原圖與讀值供查核；不需操作，也不計入學員小步。'},
}

# Display text that app code used to inject per step ID now lives on the step.
NOTICES = {
    'ch05-linked-': {'label': '尺寸範圍更正', 'source': '/read/learning/journal/2026-10-27-parametric-range-correction-v001.md',
                     'text': '模型尚無自動防護。盒高 H、底厚 B、唇深 D 須至少滿足 H−D ≥ B 才不會在高度方向重疊；等號是接觸，這只是必要條件，不保證其他幾何或實體配合。啟動器關閉自動存檔，修改已登記檔案前請先另存新版本；若 CAD Sketcher 未成功啟用，不可假設連動有效。表內數字屬助教前次示範，個人副本修改後須另行讀值，不可直接沿用。'},
    'ch10-boss-draft-': {'label': '對邊距更正', 'source': '/read/learning/journal/2026-10-27-boss-polygon-correction-v001.md',
                         'text': '對邊距依理想正32邊形公式推算，並非對邊投影實測；盲底與孔深由網格 Z 邊界推得。'},
}

TEXT_CORRECTIONS = [
    ('ch01-01-04-01', 'actions', 0, '（完整路徑可在本頁「我的練習檔案」複製）', '（完整路徑可在原教材 01-04 頁的「我的練習檔案」複製）',
     '本步已移到工程章節，工程頁沒有「我的練習檔案」面板。'),
    ('ch07-05-04-01', 'success', None, '下方表格可下載並核對來源版本與雜湊。', '原教材 05-04 頁的表格可下載並核對來源版本與雜湊。',
     '工程頁沒有該表格。'),
    ('ch05-manual-guard-restart-01', 'actions', 0,
     '個人練習先將已驗證手工盒另存至專案 learning/workspaces/engineering-parametric/；若資料夾不存在先建立。',
     '確認上一步複製的個人副本位於 learning/workspaces/engineering-parametric/；在 Blender 用 File > Open 開啟它，不要開啟或另存 evidence 內的原檔。',
     '個人副本改由上一步的命令建立並核對雜湊。'),
]

NEW_STEPS = {
    'ch04-setup-01': {
        'id': 'ch04-setup-01', 'title': '取得 CAD Sketcher 安裝檔', 'goal': '下載固定版本的草圖擴充套件，並核對檔案沒有變動。',
        'context': '瀏覽器與 Windows PowerShell；本章使用 CAD Sketcher 0.32.1。',
        'actions': ['到官方發布頁 https://github.com/hlorus/CAD_Sketcher/releases/tag/v0.32.1 下載 CAD_Sketcher-0.32.1-windows_x64.zip，保留 ZIP 不要解壓。',
                    '在 PowerShell 執行 Get-FileHash <ZIP 的完整路徑> -Algorithm SHA256，對照下方的 SHA-256。'],
        'success': f'ZIP 為 1,283,581 bytes，SHA-256 為 {CAD_SKETCHER_ZIP_SHA}；不同時先停下回報，不安裝。',
        'shortcuts': [], 'figures': [], 'sourceSteps': [], 'evidenceStatus': 'draft_pending_demo',
        'limitations': ['檔名、大小與 SHA-256 取自助教 2026-10-27 下載並與 GitHub asset digest 相符的紀錄；學員下載畫面尚無實拍。',
                        'CAD Sketcher 是第三方擴充套件（GPL-3.0-or-later），本教材不收錄安裝包；下載由學員自行進行。']},
    'ch04-setup-02': {
        'id': 'ch04-setup-02', 'title': '從磁碟安裝並啟用 CAD Sketcher', 'goal': '在自己的 Blender 安裝已核對的 ZIP，確認擴充套件可用。',
        'context': 'Blender 5.2.1：Edit > Preferences > Get Extensions。',
        'actions': ['在 Get Extensions 右上角的向下箭頭選單選 Install from Disk...，選取上一步核對過的 ZIP 並安裝。',
                    '到 Add-ons 確認 CAD Sketcher 已勾選啟用；回到 3D Viewport 按 N，確認側欄出現 Sketcher 分頁。'],
        'success': '側欄有 Sketcher 分頁；安裝失敗或出現相依套件錯誤時先停下回報畫面，不重複安裝。',
        'shortcuts': [], 'figures': [], 'sourceSteps': [], 'evidenceStatus': 'draft_pending_demo',
        'limitations': ['Get Extensions／Add-ons 分頁名稱與 Install from Disk 指令由 Blender 5.2.1 程式讀回，選單位置依同版 bl_pkg 介面原始碼核對；尚無學員畫面實拍。',
                        '助教示範以程式安裝到隔離的擴充套件資料夾並啟用，不是這兩步的 GUI 示範。',
                        'Windows ZIP 隨附 slvs 求解器 wheel；其他平台、其他 Blender 版本或線上更新後的版本未核對。']},
    'ch04-setup-03': {
        'id': 'ch04-setup-03', 'title': '建立工程工作區與毫米草圖檔', 'goal': '讓本章草圖與第 05 章盒蓋練習都存在固定的個人工作區。',
        'context': 'Windows PowerShell（專案根目錄）與 Blender 5.2.1。',
        'actions': ['在 PowerShell 執行 python learning/manage.py engineering-workspace，建立並顯示 learning/workspaces/engineering-parametric/。',
                    '在 Blender 依第 03 章「建立毫米工作檔」的設定新開檔：Scene 的 Units 把 Length 改為 Millimeters、Unit Scale 改為 0.001。',
                    '另存為 learning/workspaces/engineering-parametric/sketch_practice_v001.blend。'],
        'success': '命令顯示工作區的完整路徑；Blender 標題列顯示 sketch_practice_v001.blend，預設 Cube 顯示 2 mm。',
        'shortcuts': [], 'figures': [], 'sourceSteps': [{'lessonId': '04', 'stepId': '04-02'}], 'evidenceStatus': 'draft_pending_demo',
        'limitations': ['命令只建立資料夾，不寫入學習進度；工作區已存在時不變更內容。',
                        '單位設定沿用原教材 04-02 的示範；本步的工程工作區操作尚無學員畫面。']},
    'ch05-guard-prepare-01': {
        'id': 'ch05-guard-prepare-01', 'title': '複製指定示範盒作個人副本', 'goal': '取得受控面板能辨認的手工盒副本，不動到示範原檔。',
        'context': 'Windows PowerShell，工作目錄是 Blender-Learning 專案根目錄。',
        'actions': ['執行 python learning/manage.py engineering-workspace --copy-manual-box my_manual_box_v001.blend。',
                    '核對畫面顯示的路徑與 SHA-256；同名檔已存在時命令會拒絕，換新檔名再執行。'],
        'success': f'learning/workspaces/engineering-parametric/my_manual_box_v001.blend 存在，SHA-256 與示範基準 {MANUAL_BOX_BASE[1]} 相同。',
        'shortcuts': [], 'figures': [], 'sourceSteps': [], 'evidenceStatus': 'draft_pending_demo',
        'limitations': ['受控面板只接受這個示範手工盒的副本（草圖約束 UID 與上蓋拓撲簽章固定）；前面各步你自己建立的盒子會被面板拒絕。',
                        f'來源是助教示範檔 {MANUAL_BOX_BASE[0]}（80×50 mm、上蓋 X／Y Driver），不是學員成果；命令以雜湊核對後才複製。',
                        '本步命令有自動測試，尚無學員畫面實拍。']},
    'ch05-guard-checkpoint-01': {
        'id': 'ch05-guard-checkpoint-01', 'title': '另存並登記檢查點', 'goal': '把目前尺寸的副本保存為不可覆寫的版本，之後在新檔名上繼續。',
        'context': 'Blender（個人副本、Object Mode）；本機教學頁「檔案版本」或 PowerShell。',
        'actions': ['File > Save As，存成 learning/workspaces/engineering-parametric/ 內的新檔名，例如 my_manual_box_v002.blend。',
                    '在教學頁「檔案版本」的「工程參數盒工作區」選這個檔案、用途選場景 .blend 後登記；或執行 python learning/manage.py register-file --workspace engineering-parametric --revision <n> --path learning/workspaces/engineering-parametric/my_manual_box_v002.blend --role source_scene。',
                    '要繼續修改時，先另存一個未登記的新檔名，例如 my_manual_box_v003.blend。'],
        'success': '版本表出現此檔與 SHA-256；在已登記檔案上提交預檢面板時，面板要求先以新檔名另存。',
        'shortcuts': [], 'figures': [], 'sourceSteps': [], 'evidenceStatus': 'draft_pending_demo',
        'limitations': ['「登記紀錄 → 面板拒絕」已用純 Python 測試串接核對；畫面上的拒絕只在助教假專案示範過（見附錄），尚無學員畫面。',
                        '登記只保存檔案指紋與用途，不代表幾何、實體或配合合格。']},
}

LIMITATIONS = {
    'ch04': ['CAD Sketcher 0.32.1 是第三方擴充套件；助教示範在隔離 Blender 以程式安裝與啟用，本章安裝步驟尚無學員畫面。',
             '外框草圖改尺寸時，內腔切割體不會自動跟隨；即使顯示 Fully defined，也要進內腔草圖按更新並核對讀值。',
             '外框、切割體界限與自由度是程式讀值，不能從圖片量得；布林後壁厚與閉合性未完整驗證。',
             '數位幾何不代表可列印或配合合格；實體列印、量測與試配尚未進行。'],
    'ch05': ['學員路徑：先在自己的手工盒做固定上蓋、形狀鍵與 Driver，再用指定示範盒的副本練習受控尺寸面板。',
             '受控面板只接受指定示範手工盒的副本；你自己建立的盒子會被拒絕。',
             '直接修改 Blender／CAD Sketcher 原生欄位可繞過面板與自動更新；面板不攔截原生存檔與匯出，也不自動存檔。',
             'X60～100／Y30～70 mm 是形狀鍵未夾限的理論範圍，不是製造或配合合格範圍；0.4 mm 總間隙仍是試驗值。',
             '面板各步的原圖來自助教在隔離假專案的示範；你在自己副本上的讀值要自行核對。'],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_checked(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('source changed: ' + path.name)
    return json.loads(raw.decode('utf-8-sig'))


def body(step):
    return {key: value for key, value in step.items() if key != 'id'}


def references(step):
    refs = list(step.get('figures', [])) + list(step.get('artifacts', []))
    for shortcut in step.get('shortcuts', []):
        refs += shortcut.get('evidence', [])
    return refs


def check_refs(refs):
    for ref in refs:
        path = (ROOT / ref['path']).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file() or sha(path) != ref['sha256']:
            raise ValueError('missing or changed: ' + ref['path'])


def build_curriculum(source, catalog):
    data = copy.deepcopy(source)
    steps = {step['id']: step for chapter in data['chapters'] for step in chapter['steps']}
    if len(steps) != 256:
        raise ValueError('unexpected v027 baseline')
    for duplicate, kept in DUPLICATES.items():
        if body(steps[duplicate]) != body(steps[kept]):
            raise ValueError('not an exact duplicate: ' + duplicate)
    for old, new in MOVED.items():
        steps[new] = dict(steps.pop(old), id=new)
    for duplicate in DUPLICATES:
        del steps[duplicate]
    steps.update(copy.deepcopy(NEW_STEPS))

    corrections = []
    for step_id, field, index, before, after, reason in TEXT_CORRECTIONS:
        step = steps[step_id]
        current = step[field][index] if index is not None else step[field]
        if before not in current:
            raise ValueError('correction target missing: ' + step_id)
        if index is None:
            step[field] = current.replace(before, after)
        else:
            step[field][index] = current.replace(before, after)
        corrections.append({'stepId': step_id, 'field': field, 'before': before, 'after': after, 'reason': reason})

    for step in steps.values():
        for prefix, notice in NOTICES.items():
            if step['id'].startswith(prefix):
                step['notices'] = [dict(notice)]
    reclassified = []
    for step in steps.values():
        if step['evidenceStatus'] == 'existing_demo' and not step.get('figures') and not step.get('artifacts'):
            if not step.get('sourceSteps'):
                raise ValueError('demo status without figure or source step: ' + step['id'])
            step['evidenceStatus'] = 'source_step_demo'
            reclassified.append(step['id'])
    for step_id in CH04_APPENDIX + CH05_APPENDIX:
        steps[step_id]['track'] = 'appendix'

    lesson_order = [step['id'] for lesson in catalog['lessons'] for step in lesson['steps']]

    def from_lesson(chapter_prefix, lesson_id):
        found = [step_id for step_id, step in steps.items()
                 if step_id.startswith(chapter_prefix) and [ref['lessonId'] for ref in step.get('sourceSteps', [])] == [lesson_id]
                 and step.get('track') != 'appendix' and step_id not in NEW_STEPS]
        return sorted(found, key=lambda step_id: (lesson_order.index(steps[step_id]['sourceSteps'][0]['stepId']), step_id))

    old_order = {chapter['id']: [step['id'] for step in chapter['steps']] for chapter in source['chapters']}
    order = {
        'ch01': ['ch01-fit-surfaces'] + from_lesson('ch01-01-', '01'),
        'ch02': [step_id for step_id in old_order['ch02'] if step_id not in DUPLICATES],
        'ch03': from_lesson('ch03-02-', '02') + [step_id for step_id in old_order['ch03'] if step_id.startswith('ch03-04-')],
        'ch04': ['ch04-setup-01', 'ch04-setup-02', 'ch04-setup-03'] + [s for s in old_order['ch04'] if s not in CH04_APPENDIX] + CH04_APPENDIX,
        'ch05': CH05_LEARNER + CH05_APPENDIX,
        'ch11': [step_id for step_id in old_order['ch11'] if step_id not in MOVED],
        'ch12': [step_id for step_id in old_order['ch12'] if step_id not in MOVED],
    }
    for chapter in data['chapters']:
        ids = order.get(chapter['id'], old_order[chapter['id']])
        chapter['steps'] = [steps.pop(step_id) for step_id in ids]
        if chapter['id'] in APPENDIX:
            chapter['appendix'] = dict(APPENDIX[chapter['id']])
        if chapter['id'] in LIMITATIONS:
            chapter['limitationHistory'] = chapter['limitations']
            chapter['limitations'] = list(LIMITATIONS[chapter['id']])
    if steps:
        raise ValueError('unplaced steps: ' + ', '.join(sorted(steps)))

    data['version'] = VERSION
    data['description'] = '12章詳細操作參照；v028依學習順序整理：原單元各自完整放在一章、移除重複步驟、開發測試改列附錄，並補 CAD Sketcher 安裝與工程工作區步驟。'
    data['evidenceStatusDefinitions'] = dict(data['evidenceStatusDefinitions'],
        existing_demo='本小步附有助教示範原圖或讀值檔；非學員完成及實體驗收。',
        source_step_demo='所屬原教材步驟有助教示範，本小步沒有單獨原圖；請開啟原教材步驟核對。')
    data['trackDefinitions'] = {'appendix': '開發與驗證紀錄；保留原圖與讀值供查核，不需操作、不計入學員小步，也不能確認。'}
    data['sourceVersions'] = data['sourceVersions'] + [
        {'path': 'learning/web/engineering-curriculum-v027.json', 'sha256': SOURCE_SHA},
        {'path': 'learning/web/engineering-path-v001.json', 'sha256': PATH_SOURCE_SHA},
        {'path': MANUAL_BOX_BASE[0], 'sha256': MANUAL_BOX_BASE[1]}]
    data['stepIdChanges'] = dict(sorted(MOVED.items()))
    data['contentReview'] = dict(data['contentReview'], reviewV028={
        'reviewedOn': '2026-10-27', 'reviewer': 'Claude Code（依 Codex v027 審查意見整理）',
        'scope': '章節順序、重複步驟、附錄分類、證據狀態、CAD Sketcher 安裝與工程工作區步驟；不新增 Blender 示範或原圖。',
        'removedDuplicates': dict(sorted(DUPLICATES.items())), 'textCorrections': corrections,
        'statusReclassified': sorted(reclassified), 'appendixSteps': CH04_APPENDIX + CH05_APPENDIX,
        'newSteps': sorted(NEW_STEPS), 'stepIdChangesReason': '移動的步驟沒有任何學員工程事件（progress 中 engineering_step_* 為 0 筆），v027 也未發布；ID 改為所在章節，舊 ID 對照見 stepIdChanges。',
        'cadSketcherUiEvidence': 'Blender 5.2.1 背景讀回：Preferences.active_section 的 EXTENSIONS 名稱 Get Extensions、ADDONS 名稱 Add-ons；extensions.package_install_files 名稱 Install from Disk；bl_pkg/bl_extension_ui.py 的 USERPREF_MT_extensions_settings 選單含 Install from Disk...。',
        'learnerProgressChanged': False})
    return data


def build_path(path, curriculum):
    data = copy.deepcopy(path)
    data['id'] = 'engineering-path-v002'
    data['version'] = 'v002 · 2026-10-27'
    data['intro'] = '從功能與量測出發，用同一個小盒串起公差、草圖、尺寸連動與配合試驗。第01章含基本操作與可靠存檔，第03章含毫米建模，第12章為材質、燈光與渲染。原9單元52步保留可回查；閱讀不等於完成。'
    data['courseLabel'] = '工程教學章節'
    data['learningPolicy'] = [item.replace('新課綱的觀察問題可先在聊天回覆；待確認如何對應後才透過既有管理工具記錄，不能代替原01-01等操作完成。',
                                           '新版小步的確認與筆記用本頁表單或 manage.py engineering-confirm／engineering-note 記錄；不能代替原教材步驟完成。')
                              for item in data['learningPolicy']]
    data['environment'] = dict(data['environment'], status='manual_box_and_guard_demonstrated',
        summary='隔離 Blender 5.2.1＋CAD Sketcher 0.32.1 已示範草圖、手工盒內腔、盒蓋形狀鍵與 Driver 連動，以及受控尺寸面板；示範中的插件啟用與檔案路徑由程式處理。你自己的安裝步驟見第 04 章（尚無學員畫面）。')
    data['followUpActivity'] = {
        'title': '下一小步：辨認間隙的兩個表面', 'goal': '先找出可能配合的表面，這一步不量尺寸。',
        'actions': ['先看分離圖：上蓋暫時抬高，留意板下的環形唇邊。', '再看盒體原圖：找到盒口內側壁與盒體外壁。'],
        'question': '水平配合間隙要看環形唇邊外側面與盒口內側壁，還是盒體外壁？',
        'success': '能指出想比較的兩個表面；這是觀察與理解，不能代表實體試配。',
        'curriculumStep': 'ch01-fit-surfaces',
        'figures': [
            {'type': 'screenshot', 'path': 'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png',
             'sha256': 'bc12d5f81fd5424cef7dd64c295941c8a31de430a45818782e249f8b1d2fec64',
             'caption': '2026-10-22 獨立 Blender 原圖：上蓋暫時抬高以便觀察，右側 60 × 40 × 30 mm 是作用中盒體 Body 的外形。這張圖不能直接量出細縫。'},
            {'type': 'screenshot', 'path': 'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-02-source-body-checked.png',
             'sha256': 'b04ade7f0a4f5ec5056fb76406b887b04e6f1e9527198d8281ffeb30e1d0e49d',
             'caption': '2026-10-22 獨立 Blender 原圖：盒體 Body 的開口與內側壁；右側 60 × 40 × 30 mm 是盒體外形。'}]}
    labels = {'existing_reference': '有既有教材可參照', 'new_content_pending': '新內容待製作', 'mixed': '既有參照＋待補內容'}
    shortcut_status = {
        'ch04': '手工草圖、內腔與盒蓋已有隔離 Blender 示範；原生欄位直接修改時仍須手動更新內腔。',
        'ch05': '手工盒蓋及受控面板已有隔離 Blender 示範；原生欄位可繞過預檢，另存快捷沿用既有證據。',
        'ch10': 'Screw 開放曲面已在隔離 Blender 示範；封閉螺紋與配合仍待驗證。'}
    notes = {
        'ch01': ['新路徑第一小步為原圖觀察；不需要先重做小盒。', '本章包含原單元01全部步驟：先學會選取、視角、Transform 與另存版本，再進入建模。',
                 '建模原點與實際零件的功能基準需要建立對應，不能自動視為相同。'],
        'ch03': ['原單元02（訊號站與毫米方塊）完整放在本章，接著是原盒的毫米建模。', 'Object Mode的I會插入關鍵影格，不能當Inset。'],
        'ch05': ['手工盒的固定上蓋、形狀鍵、Driver 與多尺寸核對已有隔離示範；實際列印和試配仍待測。',
                 '受控面板只接受指定示範盒的副本；舊版面板與測試紀錄移到本章附錄。',
                 '上蓋裝配高度與為了展示而抬高的位移分開。'],
        'ch10': ['原教材保留08-01及後續草案；本章另有獨立開放曲面與盲孔柱示範，完整可列印螺紋與試鎖仍待驗證。', '旋合外觀不能代替規格、配合或強度判定。'],
        'ch11': ['原01-04／01-09的另存與重開已移回第01章；本章處理實測後的補償、總裝與交付。', '不由單次成功試配推定整批或不同材料都適用。',
                 '幾何公差與製程能力進階內容依具體功能和量測資料展開。'],
        'ch12': ['渲染課可穿插；小盒已有獨立 Blender 渲染示範，布景以程式準備，完整手工布景教學待補。',
                 '訊號站建模已移到第03章；本章沿用該場景練習相機、燈光與材質。'],
    }
    practice = {
        'ch01': ['觀察既有盒體與上蓋，指出蓋板、盒口及唇邊。', '練習選取、視角、精確變換與 Dimensions；另存 v001／v002 並重開。',
                 '列出拆裝、定位及可用內腔的需求；選定量測位置，再討論建模座標。'],
    }
    refs = {
        'ch01': [{'lessonId': '01', 'stepId': '01-04', 'label': '第一次另存'}, {'lessonId': '01', 'stepId': '01-05', 'label': '選取與模式'},
                 {'lessonId': '01', 'stepId': '01-06', 'label': '視角與找回物件'}, {'lessonId': '01', 'stepId': '01-07', 'label': '精確變換'},
                 {'lessonId': '01', 'stepId': '01-08', 'label': '側欄與尺寸'}, {'lessonId': '05', 'stepId': '05-05', 'label': '既有盒體與唇邊原圖'}],
        'ch11': [{'lessonId': '09', 'stepId': '09-01', 'label': '待實測彙整'}, {'lessonId': '09', 'stepId': '09-02', 'label': '待證據支持的補償'},
                 {'lessonId': '09', 'stepId': '09-03', 'label': '待總組裝'}],
    }
    for chapter in data['chapters']:
        cid = chapter['id']
        chapter['availabilityLabel'] = '已有新示範＋待補內容' if cid in ('ch04', 'ch05') else labels.get(chapter.get('availability'), '內容狀態待核對')
        if cid in shortcut_status:
            chapter['shortcuts'] = [dict(item, status=shortcut_status[cid]) for item in chapter['shortcuts']]
        if cid in notes:
            chapter['notes'] = notes[cid]
        if cid in practice:
            chapter['practice'] = practice[cid]
        if cid == 'ch03':
            chapter['references'] = [ref for ref in chapter['references'] if ref['stepId'] != '01-07'] + [{'lessonId': '02', 'stepId': '02-04', 'label': 'F2命名與整理'}]
        if cid in refs:
            chapter['references'] = refs[cid]
    chapter_ids = [chapter['id'] for chapter in curriculum['chapters']]
    if [chapter['id'] for chapter in data['chapters']] != chapter_ids:
        raise ValueError('path and curriculum chapters differ')
    data['contentReview'] = dict(data['contentReview'], reviewedOn='2026-10-27', revisionV002={
        'scope': '把網頁程式中依版本號替換的章節狀態、備註、快捷狀態、環境摘要與接續觀察題移入資料；依 v028 更新章節參照。',
        'curriculum': {'path': 'learning/web/engineering-curriculum-v028.json'}, 'learnerCompletionChanged': False})
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
    if source['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum id')
    catalog = json.loads(CATALOG.read_text(encoding='utf-8-sig'))
    if not (ROOT / MANUAL_BOX_BASE[0]).is_file() or sha(ROOT / MANUAL_BOX_BASE[0]) != MANUAL_BOX_BASE[1]:
        raise ValueError('manual box base changed')
    curriculum = build_curriculum(source, catalog)
    for chapter in curriculum['chapters']:
        for step in chapter['steps']:
            check_refs(references(step))
    check_refs(curriculum['sourceVersions'])
    outline = build_path(path, curriculum)
    check_refs(outline['followUpActivity']['figures'])
    print(write(OUTPUT, curriculum))
    print(write(PATH_OUTPUT, outline))


if __name__ == '__main__':
    main()
