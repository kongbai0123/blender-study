"""Append verified manual sketch-to-solid trial, preserving v008."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v008.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v009.json'
SOURCE_SHA = '2c6944b7a00da650286628298942cd4fe69a7ee5af87f14cba89f68088626443'
BASE = 'learning/evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/'
SUMMARY_SHA = '520daefc24ad6b46c502cca242684c55529fd0ff6c8c27f8eb331c325d1064ba'
SCENE_SHA = '688a06f588bbe0728a7d0c866acbc307c44fa7cc1c71e467b0aa807af2084c2d'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before = SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest() != SOURCE_SHA:
        raise ValueError('v008 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary_path = ROOT / (BASE + 'manual-extrude-verification-v002.json')
    if digest(summary_path) != SUMMARY_SHA:
        raise ValueError('trial summary hash mismatch')
    summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
    if summary['runner']['status'] != 'completed' or summary['runner']['exitCode'] != 0:
        raise ValueError('trial did not complete')
    if summary['unitScale'] != 0.001 or len(summary['cases']) != 2:
        raise ValueError('unexpected trial context')
    expected_modifiers = [('CAD Sketcher Convert', 'NODES'), ('CAD_Sketcher Extrude', 'NODES')]
    for case in summary['cases']:
        if (case['bounds'] != [[0.0, 60.0], [0.0, 40.0], [0.0, 30.0]] or
                case['vertices'] != 8 or case['faces'] != 6 or
                [(m['name'], m['type']) for m in case['modifiers']] != expected_modifiers):
            raise ValueError('unexpected readback: ' + case['stage'])
    if {c['stage'] for c in summary['cases']} != {'confirmed-state.json', 'reopened-state.json'}:
        raise ValueError('confirmed/reopened trial states missing')
    if any(summary.get(k) is not None for k in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm')):
        raise ValueError('physical results must remain unfilled')
    files = {}
    for item in summary['files']:
        path = (ROOT / item['path']).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file() or digest(path) != item['sha256']:
            raise ValueError('missing or changed source: ' + item['path'])
        files[Path(item['path']).name] = item
    scene_name = 'manual_sketch_extrude_60x40x30_v001.blend'
    if files[scene_name]['sha256'] != SCENE_SHA:
        raise ValueError('scene hash mismatch')

    def figure(name: str, caption: str) -> dict:
        f = files[name]
        return {'type': 'screenshot', 'path': f['path'], 'sha256': f['sha256'], 'caption': caption}

    figs = [figure(n, c) for n, c in [
        ('EXTRUDE-01-opened-sketch.png', '隔離 Blender 原圖：草圖約束欄顯示60、40 mm與 Fully defined；底部有工具未找到警告。'),
        ('EXTRUDE-02-left-sketch.png', '原圖：退出草圖後 Body 被選取，平面仍可見。'),
        ('EXTRUDE-03-tool-invoked.png', '原圖：啟動拉伸後的暫時預覽；這不是最後高度。'),
        ('EXTRUDE-04-numeric-entry.png', '原圖：數字輸入中的實心預覽；底部狀態列顯示 DISTANCE: [*30]。'),
        ('EXTRUDE-05-confirmed.png', '原圖：確認後看到實心外形；確切尺寸須看程式讀值。'),
        ('EXTRUDE-06-saved.png', '原圖：Blender 顯示場景已儲存。'),
        ('EXTRUDE-07-reopened.png', '原圖：重新開啟後的實心外形；確切尺寸及修改器由程式讀值。'),
    ]]
    summary_ref = {'path': BASE + 'manual-extrude-verification-v002.json', 'sha256': SUMMARY_SHA,
                   'label': '手工草圖拉伸試驗、讀值和失敗版本摘要', 'type': 'verification-json'}
    scene_ref = {'path': files[scene_name]['path'], 'sha256': SCENE_SHA,
                 'label': '手工草圖拉伸實心體 v001（助教示範）', 'type': 'scene-blend'}
    common = [
        '本例使用先前 GUI 手繪且約束完成的60×40 mm草圖副本，環境與擴充套件由程式配置；場景是隔離示範，不是學員成果。',
        '本例 Blender 5.2.1、CAD Sketcher 0.32.1、Unit Scale 0.001：模態輸入不帶單位的30才得到本次30 mm讀值；前次輸入30mm讀回0.03 mm，不能推廣到其他版本或工具。',
        '得到的是實心體，不是有內腔的盒體、上蓋，也不是手工完成的雙件參數連動；數字尺寸及修改器由程式讀回，不能僅憑照片量得。',
        '另存與開啟的檔案瀏覽器路徑及檔名由程式填入，確認由 GUI 事件送出；實體列印、量測與試配尚未執行。',
        '開啟原圖底部出現 Tool sketcher.slvs_select not found for space VIEW_3D，原因未知；本次後續拉伸成功不證明其他工具正常。若個人操作出現此警告，先停止並回報畫面。',
    ]
    def step(id: str, title: str, goal: str, context: str, actions: list[str], success: str, pictures: list[dict], shortcuts: list[dict] | None = None, artifacts: list[dict] | None = None) -> dict:
        return {'id': id, 'title': title, 'goal': goal, 'context': context, 'actions': actions,
                'success': success, 'shortcuts': shortcuts or [], 'figures': pictures, 'sourceSteps': [],
                'evidenceStatus': 'existing_demo', 'limitations': list(common), 'artifacts': artifacts or [summary_ref]}
    steps = [
        step('ch04-solid-01', '確認60×40草圖並離開', '從受約束草圖開始實心拉伸',
             '使用先前60×40 mm草圖副本；Body Sketch 活動，3D 視圖中操作。',
             ['核對側欄 Distance 60 mm、40 mm及 Fully defined；先另存個人副本。', '在3D視圖按 Ctrl+Shift+A 離開草圖。'],
             '助教畫面離開草圖後 Body 已選取、平面仍可見。若出現工具警告先停下回報。', figs[:2],
             [{'keys': 'Ctrl+Shift+A', 'effect': '本次離開活動草圖。', 'requirements': ['本次測試為活動 Body Sketch、3D 視圖焦點。'], 'cautions': ['版本或其他狀態快捷鍵可能不同；先核對畫面。'], 'evidence': [{'path': figs[1]['path'], 'sha256': figs[1]['sha256'], 'method': 'native_gui_event', 'label': '離開草圖後原圖，事件依摘要'}]}]),
        step('ch04-solid-02', '啟動拉伸預覽', '由平面進入拉伸操作',
             'Object Mode，Body 已選取，焦點在3D視圖。', ['按 Ctrl+Shift+E 啟動本次 CAD Sketcher 拉伸；先不要點擊確認。'],
             '助教畫面出現暫時有厚度的預覽；此時不應將預覽厚度當作目標值。', figs[2:3],
             [{'keys': 'Ctrl+Shift+E', 'effect': '啟動 CAD Sketcher Extrude。', 'requirements': ['本例物件模式、Body 已選取且3D視圖有焦點。'], 'cautions': ['預覽數值尚非確認結果；本次早期試探點擊曾提前接受約3.9 mm。'], 'evidence': [{'path': figs[2]['path'], 'sha256': figs[2]['sha256'], 'method': 'native_gui_event', 'label': '拉伸預覽原圖，事件依摘要'}]}]),
        step('ch04-solid-03', '輸入30並確認拉伸', '以模態數字輸入建立本例高度',
             '本次拉伸工具仍在等待輸入；Blender 5.2.1、CAD Sketcher 0.32.1、Unit Scale 0.001。',
             ['直接輸入 30（不加 mm），觀察預覽與狀態列；按 Enter 確認。'],
             '畫面顯示實心形狀；本次程式讀回外框60×40×30 mm、8頂點6面，具 CAD Sketcher Convert 與 CAD_Sketcher Extrude 修改器。這些數值不可由圖片直接確認。', figs[3:5]),
        step('ch04-solid-04', '另存並重開實心體', '保留可追溯的拉伸成果',
             '確認實心體後，在 Blender 另存自己獨立的新版本，再重新開啟。',
             ['另存新版本，保留草圖來源。', '重開後檢查模型；並以可用工具另行核對尺寸。'],
             '助教重開畫面仍有實心外形；程式讀回仍為60×40×30 mm、8頂點6面及兩個修改器。', figs[5:], artifacts=[scene_ref, summary_ref]),
    ]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch04')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 179 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected v008 steps or duplicate IDs')
    chapter['steps'].extend(steps)
    chapter['limitations'][0] = '矩形草圖已驗證尺寸與平面網格聯動；尺寸標註延伸線部分出視區。'
    chapter['limitations'].append('另有60×40草圖的GUI實心拉伸及保存重開示範；此單獨實心體尚非手工內腔、上蓋或雙件連動。')
    data['version'] = 'v009 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v009追加手工草圖的實心拉伸與保存重開，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v008.json', 'sha256': SOURCE_SHA}, {'path': summary_ref['path'], 'sha256': SUMMARY_SHA}])
    data['manualExtrudeVerification'] = {'summary': summary_ref, 'scene': scene_ref,
        'scope': '先前手繪草圖副本，GUI離開及拉伸；僅本機實心體，內腔和上蓋未完成。',
        'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV009'] = '新增先前GUI手繪約束草圖拉伸、程式讀值及保存重開；記錄單位失敗與工具警告。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v009')
    if SOURCE.read_bytes() != before:
        raise ValueError('v008 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
