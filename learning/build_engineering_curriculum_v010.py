"""Append isolated GUI dimension guard evidence without changing v009."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v009.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v010.json'
SOURCE_SHA = 'b56aa41943bd4bfd67cbe53287f7fdb6bb216c1efa625fbf5caebebeb0a680d0'
BASE = 'learning/evidence/parametric/2026-10-27-box-guard-v005-gui-trial-v001/'
SUMMARY_SHA = 'c0ddca8eae92eec6bdfb8725d091035f76e6857e7bb27b3c5bc6461691498a5f'
SCRIPT_SHA = 'e084d0e5a041528863c1b82e5674ebc5a2b218e105632709f0cd442572d25b24'
SCENE_SHA = 'cb0652ae0a45183345039d291ffc8f1c3ef303819104413c34d5489ea2dac415'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path: str, expected: str, label: str, kind: str) -> dict:
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file() or sha(target) != expected:
        raise ValueError('missing, invalid or changed: ' + path)
    return {'path': path, 'sha256': expected, 'label': label, 'type': kind}


def main() -> None:
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v009 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    summary_ref = checked(BASE + 'guard-v005-gui-verification-v001.json', SUMMARY_SHA, '尺寸防護 GUI 試驗摘要', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    if summary['runner']['status'] != 'completed' or summary['runner']['exitCode'] != 0:
        raise ValueError('guard GUI trial did not complete')
    if any(summary[k] is not None for k in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm')):
        raise ValueError('physical results must remain empty')
    script_ref = checked(summary['guardScript']['path'], SCRIPT_SHA, '尺寸防護面板程式 v005（本機路徑）', 'python-script')
    scene_ref = checked(summary['fixtureScene']['path'], SCENE_SHA, '隔離測試專案場景 v002', 'scene-blend')
    shots = summary['screenshots']
    if len(shots) != 20:
        raise ValueError('expected 20 GUI screenshots')
    for i, item in enumerate(shots, 1):
        if not Path(item['path']).name.startswith(f'GUARD-{i:02d}-'):
            raise ValueError('unexpected screenshot order')
        checked(item['path'], item['sha256'], str(i), 'screenshot')
    cases = {c['stage']: c for c in summary['cases']}
    if set(cases) != {'empty-assertion', 'switch-assertion', 'unack-assertion', 'width-assertion', 'invalid-assertion', 'length-assertion', 'reopened-assertion', 'registered-assertion'}:
        raise ValueError('case set differs from expected')
    for case in cases.values():
        checked(case['path'], case['sha256'], 'readback', 'verification-json')
    for k in ('empty-assertion', 'switch-assertion', 'unack-assertion'):
        if cases[k]['values']['L'] != 80 or cases[k]['values']['W'] != 40:
            raise ValueError('rejected case altered dimensions')
    expected = {'width-assertion': (80, 50), 'invalid-assertion': (80, 50), 'length-assertion': (70, 50), 'reopened-assertion': (70, 50)}
    for stage, (length, width) in expected.items():
        c = cases[stage]
        if (c['values']['L'], c['values']['W'], c['values']['D']) != (length, width, 4):
            raise ValueError('unexpected numerical readback: ' + stage)
        if c['bodyBounds'] != [[0, length], [0, width], [0, 30]] or c['lidBounds'] != [[0, length], [0, width], [26, 32]]:
            raise ValueError('unexpected body or lid bounds: ' + stage)
    if '已登記' not in cases['registered-assertion']['guardError']:
        raise ValueError('registered rejection absent')
    captions = [
        '隔離 Blender 原圖：測試專案 Body Sketch 顯示80／40 mm。',
        '原圖：3D視圖側欄「盒尺寸預檢 v005」面板。',
        '原圖：預檢對話框，參數尚未選擇且數值空白。',
        '原圖：未選參數送出，介面提示先明確選擇。',
        '原圖：選寬度 W、填70並勾選核對。',
        '原圖：切換至長度 L 後數值清空、核對取消勾選。',
        '原圖：未核對送出時介面拒絕。',
        '原圖：修改數值之前，核對已勾選。',
        '原圖：數值由70改90後核對被取消。',
        '原圖：未重新核對時提交被拒絕。',
        '原圖：選擇 W、新數值50並勾選核對。',
        '原圖：成功修改後的草圖畫面；盒蓋數值須看程式讀值。',
        '原圖：提出唇深 D=29，原值4 mm。',
        '原圖：拒絕並提示 H−D≥B，以避免該方向重疊。',
        '原圖：提出 L=70，原值80 mm。',
        '原圖：修改後草圖外觀；盒蓋數值須看程式讀值。',
        '原圖：Blender 顯示測試場景 v002 已儲存。',
        '原圖：重開場景，底部顯示 sketcher.slvs_select 工具未找到警告。',
        '原圖：隔離測試專案的已登記場景。',
        '原圖：對已登記場景操作時顯示先另存新檔的拒絕提示。',
    ]
    figures = [{'type': 'screenshot', 'path': f['path'], 'sha256': f['sha256'], 'caption': caption} for f, caption in zip(shots, captions)]
    common = [
        '只測試 v004 對應的盒蓋模型、Blender 5.2.1、CAD Sketcher 0.32.1 與 Metric Unit Scale 0.001；不代表其他模型或環境適用。',
        '面板由程式 runpy 載入，未示範手動 Text Editor 載入；本機程式路徑 learning/tutor/guarded_box_parameters_v005.py，可與摘要中的 SHA-256 核對。',
        '所有操作均在 evidence 內隔離的假專案與示範副本；不是學員 workspace 或學員進度。檔案視窗路徑及名稱由程式填入，確認透過 GUI。',
        '預檢只檢查必要數值條件及取樣的幾何，不保證完整干涉檢查或實體合格；Blender／CAD Sketcher 原生欄位可繞過此面板。',
        '面板不自動存檔；需另存新版本。1000 mm 是工具保守的數值上限，不是製造公差。',
        '程式讀值與畫面區分；0.4 mm 總間隙是試驗值，實體列印、量測、試配與合格值均未取得。',
        'GUARD-07 與 GUARD-10 是不同操作階段、原圖雜湊相同；操作歷程與尺寸需結合各自讀值及摘要，不能只由相同畫面推定過程。',
    ]
    sections = [
        ('ch05-guard-01', '辨認預檢面板與空白拒絕', '辨認面板與未選參數的處置', '助教已程式載入面板，3D 視圖在 Body Sketch。', ['查看「盒尺寸預檢 v005」及「預檢後修改一項尺寸」。', '對照未選參數且空白送出的拒絕提示。'], '未選參數被拒；程式讀回 L80、W40 未變。', 0, 4),
        ('ch05-guard-02', '切換參數會重置確認', '避免把舊參數的新值用到另一個參數', '預檢對話框；先前選 W 並填70、勾選。', ['對照切換 W 至 L 前後的欄位。', '觀察未重新核對送出時的提示。'], '切換後數值清空、核對取消；送出被拒，讀值維持 L80、W40。', 4, 7),
        ('ch05-guard-03', '改數值後重新核對', '避免套用尚未重新核對的數值', '預檢對話框中 W 已選、填70並勾選。', ['比較數值70改為90前後的核對欄。', '觀察未重新勾選送出的提示。'], '改值後核對取消；未重新確認遭拒，讀值維持 L80、W40。', 7, 10),
        ('ch05-guard-04', '觀察寬度 W 修改', '觀察一次修改一個參數及盒蓋連動', '預檢對話框；起始 L80、W40。', ['對照 W50 與勾選核對後提交的畫面。'], '畫面顯示已修改；程式讀回盒體與上蓋外框均為80×50 mm，不能只憑畫面量取。', 10, 12),
        ('ch05-guard-05', '觀察唇深不合理值被拒絕', '理解限制只是一項必要條件', '此例 H30、B2、原唇深 D4 mm。', ['對照 D29 提案與拒絕提示。'], 'H−D=1，小於 B=2，因此本例拒絕；程式讀回 D 維持4 mm。滿足該條件也不代表無其他干涉。', 12, 14),
        ('ch05-guard-06', '觀察長度 L 修改', '觀察另一個合法輸入與數位外框', '前例 W50，當前 L80。', ['對照 L70 與勾選核對後提交的畫面。'], '畫面顯示已修改；程式讀回盒體與上蓋外框均為70×50 mm。', 14, 16),
        ('ch05-guard-07', '保存並重開測試版本', '將尺寸讀回與檔案版本關聯', '隔離假專案，面板不自動存檔。', ['對照另存 v002 與重開後的原圖。', '留意底部工具警告，再對照讀值摘要。'], '重開後程式讀回 L70、W50、D4；畫面底部顯示工具未找到警告。', 16, 18),
        ('ch05-guard-08', '觀察已登記版本的保護', '理解已登記場景應另存', '隔離假專案中的測試登記，並非學員的版本紀錄。', ['對照已登記測試場景與面板拒絕提示。'], '介面拒絕編輯並要求先用新檔名另存；此結果僅針對本次面板和隔離測試。', 18, 20),
    ]
    steps = []
    for id, title, goal, context, actions, success, lo, hi in sections:
        limits = list(common)
        if id == 'ch05-guard-07':
            limits.append('重開圖顯示 Tool sketcher.slvs_select not found for space VIEW_3D；原因未知，不證明其他草圖工具正常。若你的畫面出現該提示，先停下並回報畫面。')
        steps.append({'id': id, 'title': title, 'goal': goal, 'context': context, 'actions': actions,
                      'success': success, 'shortcuts': [], 'figures': figures[lo:hi], 'sourceSteps': [],
                      'evidenceStatus': 'existing_demo', 'limitations': limits,
                      'artifacts': [summary_ref, script_ref] + ([scene_ref] if id in {'ch05-guard-07', 'ch05-guard-08'} else [])})
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch05')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 183 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected baseline or duplicate steps')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('尺寸防護 v005 已在特定 v004 模型隔離專案以 GUI 測試；腳本由程式載入，原生欄位可繞過，手動載入與完整干涉未驗。')
    data['version'] = 'v010 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v010追加隔離尺寸預檢面板 GUI 測試，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v009.json', 'sha256': SOURCE_SHA}, {'path': summary_ref['path'], 'sha256': SUMMARY_SHA}])
    data['dimensionGuardVerification'] = {'summary': summary_ref, 'script': script_ref, 'scene': scene_ref,
        'scope': 'v004 對應模型與隔離假專案；程式載入面板、GUI 操作，非手動載入或學員進度。',
        'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV010'] = '新增20張原圖所示尺寸預檢 GUI 測試、腳本與場景雜湊；區分數位檢查、原生欄位繞過與實體結果。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v010')
    if SOURCE.read_bytes() != before:
        raise ValueError('v009 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
