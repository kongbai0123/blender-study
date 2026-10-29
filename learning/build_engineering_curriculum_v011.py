"""Append observed Text Editor and guarded panel trial; keep v010 intact."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v010.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v011.json'
SOURCE_SHA = '7c9d03e5d73ae5f8b64430b298713d125c7937c9102e58f7ad8ec27eab1bc1e7'
BASE = 'learning/evidence/parametric/2026-10-27-box-guard-v007-text-gui-v002/'
SUMMARY_SHA = 'f940df8fabb5262c474c88ab464630185969ab60b22ac6168238ff6e83ebdc16'
SCRIPT_SHA = 'd04a945e1fc8d60d0c6d3323774819c817860d91b1aaf8f0a06d7223eb4e7bf4'
SCENE_SHA = 'cab6d3d950fa87b94a0e40aa42c6a244e6f5270174a0e28803d47950f286543f'


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
        raise ValueError('v010 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    summary_ref = checked(BASE + 'guard-v007-text-gui-verification-v001.json', SUMMARY_SHA, 'v007 Text Editor 與尺寸防護 GUI 試驗摘要', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    if not summary['runnerCompleted'] or not summary['textReadback']['sameAsDisk'] or summary['textReadback']['isDirty']:
        raise ValueError('trial incomplete or script text differs')
    for key in ('W50BothObjects', 'D29RejectedAndUnchanged', 'L70BothObjects', 'saveAndReopen70x50', 'registeredFixtureUnchanged', 'registeredErrorNotMachineParsed'):
        if summary['checks'][key] is not True:
            raise ValueError('unexpected GUI check: ' + key)
    if summary['checks']['registeredErrorVisuallyConfirmedImage'] != 'GUARD-22-registered-attempt.png':
        raise ValueError('registered screenshot is unexpected')
    expected = {'width-assertion': (80,50,4), 'invalid-assertion': (80,50,4),
                'length-assertion': (70,50,4), 'reopened-assertion': (70,50,4), 'registered-assertion': (70,50,4)}
    for stage, values in expected.items():
        r = summary['readings'][stage]
        if (r['L'], r['W'], r['D']) != values:
            raise ValueError('unexpected numeric readback: ' + stage)
    script_ref = checked('learning/tutor/guarded_box_parameters_v007.py', SCRIPT_SHA, 'v007 面板程式（本機路徑）', 'python-script')
    scene_ref = checked(BASE + summary['fakeScene']['file'], SCENE_SHA, '隔離測試場景 v002', 'scene-blend')
    images = summary['images']
    if len(images) != 22:
        raise ValueError('expected 22 screenshots')
    for i, item in enumerate(images, 1):
        if item['seq'] != i or not item['file'].startswith(f'GUARD-{i:02d}-'):
            raise ValueError('unexpected image sequence')
        checked(BASE + item['file'], item['sha256'], str(i), 'screenshot')
    captions = [
        '隔離 Blender 原圖：測試副本草圖為80／40；底部出現工具未找到提示。',
        '原圖：Text Editor 中顯示 v007 腳本；檔案瀏覽器路徑由程式填入。',
        '原圖：執行 Alt+P 後畫面與前圖相同；執行事件依摘要，不能由畫面獨立判斷。',
        '原圖：回到3D視圖，側欄顯示「盒尺寸預檢 v007」。',
        '原圖：預檢對話框初始未選參數且值空白。',
        '原圖：未選參數提交顯示拒絕提示。',
        '原圖：選 W、新值70並勾選後。',
        '原圖：改選 L 後新值清空、取消勾選。',
        '原圖：未重新確認提交顯示拒絕。',
        '原圖：W70 已勾選核對。',
        '原圖：新值改90後核對取消。',
        '原圖：未重新勾選提交顯示拒絕；此圖與09相同，歷程依各自事件。',
        '原圖：W50 並勾選核對。',
        '原圖：W 修改後草圖；盒蓋外框的數值依程式讀值。',
        '原圖：提出 D29，原 D4。',
        '原圖：D29 被拒並提示 H−D≥B。',
        '原圖：提出 L70 並勾選核對。',
        '原圖：L 修改後草圖；盒蓋外框的數值依程式讀值。',
        '原圖：顯示隔離場景 v002 已儲存。',
        '原圖：重開場景底部顯示 sketcher.slvs_select 工具未找到警告。',
        '原圖：已在假 progress 登記的測試場景，登記來源依摘要。',
        '原圖：人工目視可見已登記拒絕提示；程式另驗測試副本與數值不變，未自動辨識訊息。',
    ]
    figures = [{'type': 'screenshot', 'path': BASE + f['file'], 'sha256': f['sha256'], 'caption': caption} for f, caption in zip(images, captions)]
    common = [
        '本次 GUI 示範為系統暫存區的假專案及假 progress；CAD Sketcher 由程式啟用，Text Editor Open 與 Alt+P 由 GUI 事件操作，檔案視窗路徑由程式填入。',
        '面板 v007 僅針對指定 v004 盒蓋副本及其兩個原始約束 ID，在本次 Blender 5.2.1／CAD Sketcher 0.32.1／Metric Unit Scale 0.001 隔離環境測試。',
        '本機程式 learning/tutor/guarded_box_parameters_v007.py；請以教材所附 SHA-256 核對。這是 Blender 本機腳本，網頁不會替你執行。',
        '腳本在本次 Blender 工作階段執行後註冊面板；退出 Blender 後是否保留或需重新載入尚未驗證。',
        '每次選參數後輸入並核對，切換參數會清值及取消勾選，改數值也取消勾選；面板不自動存檔，Blender／CAD Sketcher 原生欄位可以繞過。',
        '數位必要條件與取樣幾何不是完整干涉、切片、強度或實體配合判定；1000 mm 為工具保守上限，不是製程能力或製造公差。',
        '盒蓋外框、變更數值來自 Python 讀值，不能由草圖圖片直接量取；0.4 mm 總間隙為試驗值，實體列印、量測、試配及合格值均未取得。',
        '起始及重開圖有工具 sketcher.slvs_select 未找到的警告，原因未知；後續測試不證明其他工具正常。若個人畫面出現該提示，先停下並回報。',
    ]
    sections = [
        ('ch05-guard-v007-01', '在 Text Editor 載入面板', '理解實際載入步驟與執行範圍', '隔離草圖示範副本；本次將編輯區切到 Text Editor。', ['對照 Text Editor 已開啟的 v007 程式；本次開啟路徑由程式填入。', '焦點在 Text Editor 時按 Alt+P 執行，回到3D視圖對照側欄面板。'], '原圖02與03相同；執行事件依摘要，原圖04可見 v007 面板。', 0, 4),
        ('ch05-guard-v007-02', '觀察空白提交被拒', '確認先選參數與輸入值', '已載入的 v007 面板，Body Sketch 活動。', ['對照預檢對話框與空白提交後提示。'], 'GUI 顯示須先選參數；不表示學員已完成操作。', 4, 6),
        ('ch05-guard-v007-03', '切換參數後重新填寫', '避免把舊值套到另一參數', '選 W70 並勾選後，改選 L。', ['比較切換前後的值及核對欄。', '觀察未重新核對送出被拒。'], '切換後清值與取消勾選；介面拒絕未確認的提交。', 6, 9),
        ('ch05-guard-v007-04', '改值後重新核對', '理解數值變更會取消確認', 'W70 已核對，將新值改成90。', ['對照改值前後勾選狀態與未核對送出提示。'], '改值取消勾選；未重新確認被拒。原圖09與12雜湊相同，歷程依各次事件。', 9, 12),
        ('ch05-guard-v007-05', '觀察 W40 改為50', '觀察盒蓋寬度連動', '預檢一次一項，選 W、輸入50並核對。', ['對照 W50 提交前後畫面與摘要。'], '介面顯示修改；程式讀回盒與蓋在 W50、L80 的連動，並非從照片量出。', 12, 14),
        ('ch05-guard-v007-06', '觀察 D29 被拒絕', '理解唇深必要條件', 'H30、B2、當前 D4 mm；提出 D29。', ['對照 D29 提案與 H−D≥B 的拒絕提示。'], '本例 H−D=1 小於 B2；程式讀回 D4 未變。此條件不足以證明完整無干涉。', 14, 16),
        ('ch05-guard-v007-07', '觀察 L80 改為70', '觀察盒蓋長度連動', '前例 W50；選 L70 並核對。', ['對照提交前後畫面與摘要。'], '介面顯示修改；程式讀回兩件連動、L70／W50。', 16, 18),
        ('ch05-guard-v007-08', '另存及重開試驗副本', '分辨畫面、數值與版本', '隔離測試專案；面板不會自動存檔。', ['對照另存及重開原圖。', '查看警告並對照摘要讀值。'], '程式讀回重開後 L70／W50／D4；重開畫面有工具未找到警告。', 18, 20),
        ('ch05-guard-v007-09', '觀察已登記版本拒絕', '理解登記檔案須先另存', '隔離假 progress 登記的測試版本；不是學員紀錄。', ['查看最後一張原圖的拒絕提示，再對照摘要。'], '已登記拒絕文字是人工目視原圖確認，程式驗證 fixture 與模型值不變；未自動解析訊息。', 20, 22),
    ]
    steps = []
    for id, title, goal, context, actions, success, lo, hi in sections:
        shortcuts = []
        if id == 'ch05-guard-v007-01':
            shortcuts = [{'keys': 'Alt+P', 'effect': '在本次 Text Editor 執行已開啟的 v007 腳本。',
                'requirements': ['Text Editor 有焦點；核對程式路徑和 SHA-256，使用本次指定模型的隔離副本。'],
                'cautions': ['圖片02及03相同；事件依摘要，重啟 Blender 後面板狀態未驗。'],
                'evidence': [{'path': figures[2]['path'], 'sha256': figures[2]['sha256'], 'method': 'native_gui_event', 'label': '執行後原圖及摘要記錄'}]}]
        steps.append({'id': id, 'title': title, 'goal': goal, 'context': context, 'actions': actions, 'success': success,
                      'shortcuts': shortcuts, 'figures': figures[lo:hi], 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
                      'limitations': list(common), 'artifacts': [summary_ref, script_ref] + ([scene_ref] if id in {'ch05-guard-v007-08', 'ch05-guard-v007-09'} else [])})
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch05')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 191 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('先前 v005 內容為歷史示範，當時未驗 Text Editor 載入；v007 已在特定模型與隔離環境以 GUI 開啟並執行，本次以程式填入路徑。')
    data['version'] = 'v011 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v011追加 v007 Text Editor 載入及尺寸防護 GUI 試驗，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v010.json', 'sha256': SOURCE_SHA}, {'path': summary_ref['path'], 'sha256': SUMMARY_SHA}])
    data['textGuardVerification'] = {'summary': summary_ref, 'script': script_ref, 'scene': scene_ref,
        'scope': '隔離假專案；GUI 開啟 Text Editor 與執行、程式填路徑；僅指定 v004 模型。',
        'registeredMessage': '人工目視截圖；非程式自動解析', 'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV011'] = '新增 Text Editor GUI 載入 v007 及防護測試，區分原圖、程式讀值、人工目視、警告與限制。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v011')
    if SOURCE.read_bytes() != before:
        raise ValueError('v010 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
