"""Append fixed-box saved copy and outer-dimension non-linkage counterexample."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v012.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v013.json'
SOURCE_SHA = '896c59c8fff8debd641f70e1b466afa422354b58c1cbb2a72073fd51b2187f1d'
EVIDENCE = 'learning/evidence/parametric/'
BASE = EVIDENCE + '2026-10-27-cad-sketcher-outer-edit-probe-v004/'
FIXED = EVIDENCE + '2026-10-27-cad-sketcher-cavity-saved-probe-v001/'
SUMMARY_SHA = '37a505f8394fc1e96cda6f1a6120f4e18bccc8072ec2df0204709b34ecefa329'


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
        raise ValueError('v012 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    summary_ref = checked(BASE + 'outer-dimension-linkage-negative-v001.json', SUMMARY_SHA, '固定盒尺寸變更反例摘要', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    if summary['kind'] != 'fixed-box-saved-and-linkage-negative-test':
        raise ValueError('unexpected trial scope')
    expected = [('opened',60,40,[[2,2],[2,2]]), ('x70',70,40,[[2,12],[2,2]]),
                ('x70y50',70,50,[[2,12],[2,12]]), ('reopened',70,50,[[2,12],[2,12]])]
    if len(summary['phases']) != len(expected):
        raise ValueError('unexpected phases')
    for phase, (name,x,y,walls) in zip(summary['phases'], expected):
        if (phase['phase'] != name or phase['boxBounds'] != [[0,x],[0,y],[0,30]] or
            phase['cutterBounds'] != [[2,58],[2,38],[2,30]] or phase['wallWidthsXY'] != walls):
            raise ValueError('unexpected readback for ' + name)
    fixed_scene = checked(EVIDENCE + summary['fixedScene']['path'], summary['fixedScene']['sha256'], '固定尺寸盒體副本 v001', 'scene-blend')
    trial_scene = checked(EVIDENCE + summary['trialScene']['path'], summary['trialScene']['sha256'], '70×50 未連動反例 v001', 'scene-blend')
    if fixed_scene['sha256'] != '087589e91d1f2cffc52e8b2fa6893be1b4a9b4332d165f97a9510b4729ca8918' or trial_scene['sha256'] != '479a7e29e3dc65c0da8e3e51608e7f86cd15b4954eda9f1f3e35523b56326cc7':
        raise ValueError('unexpected scenes')
    images = summary['images']
    if len(images) != 8:
        raise ValueError('expected eight counterexample screenshots')
    for i, f in enumerate(images, 1):
        if f['seq'] != i or not f['file'].startswith(f'EDIT-{i:02d}-'):
            raise ValueError('unexpected image sequence')
        checked(BASE + f['file'], f['sha256'], str(i), 'screenshot')
    captions = [
        '獨立 Blender 原圖：已儲存重開的固定尺寸盒體外觀；尺寸依程式讀值。',
        '原圖：右鍵選單的 Edit Sketch 子選單同時列出 Body Sketch 與 Body.001 Sketch。',
        '原圖：進入 Body Sketch 的外框草圖，圖上顯示60 mm。',
        '原圖：側欄列出60／40 mm 草圖尺寸。',
        '原圖：側欄顯示 X70／Y40；切割體界限與邊界差需看程式讀值。',
        '原圖：側欄顯示 X70／Y50；切割體界限與邊界差需看程式讀值。',
        '原圖：顯示反例副本已另存，非完成品。',
        '原圖：重開反例副本，側欄顯示70／50；切割體與邊界差由程式核對。',
    ]
    figures = [{'type': 'screenshot', 'path': BASE + f['file'], 'sha256': f['sha256'], 'caption': caption} for f, caption in zip(images, captions)]
    save_specs = [
        ('SAVE-01-saved.png', 'a201849891ba6ccd6740dbc0b8349897a96266f72571adf74bf6a36c860843ed', '較早獨立示範原圖：固定尺寸副本另存完成。'),
        ('SAVE-02-reopened.png', '29d494f64e6b5cd4d977be94580e9c65753f51a3367b6bf2c8bfe2c00cca1b5f', '較早獨立示範原圖：固定尺寸副本重開；尺寸須看程式讀值。'),
    ]
    save_figs = []
    for name, hash_value, caption in save_specs:
        item = checked(FIXED + name, hash_value, caption, 'screenshot')
        save_figs.append({'type': 'screenshot', 'path': item['path'], 'sha256': item['sha256'], 'caption': caption})
    common = [
        '獨立 Blender 示範：固定版本和修改反例分別另存；插件由程式啟用，檔案視窗路徑和名稱由程式填入，另存／重開確認使用 GUI。',
        '這個手工固定草圖模型中，外框 X／Y 改變後切割體尺寸及位置不跟隨；本次未建立 GUI 驅動器，不推論此技術無法實現連動。',
        '盒體與切割體界限、2／12 mm 為評估後網格界限的差值；圖片無法直接量出這些數字，布林後實際內腔壁厚、封閉性尚未充分驗證。',
        'v012 的「尚未另存」描述屬當時試驗；本次另行產生固定版與70×50反例版，未覆寫舊證據或學員檔案。',
        '70×50 反例並非完成品；上蓋未建立，實體列印、量測、試配及合格值未取得。',
    ]
    sections = [
        ('ch04-link-counterexample-01', '另存固定尺寸示範', '保留後續比較的原始版本', '60×40×30 手工固定盒獨立副本；原圖另存於較早的保存試驗。', ['對照固定版另存和重開畫面，記錄版本。'], '原圖顯示固定版已另存；後續開啟時程式讀回外框60×40×30及切割體界限 X2～58／Y2～38／Z2～30 mm。', save_figs + figures[:1], [fixed_scene, summary_ref]),
        ('ch04-link-counterexample-02', '進入外框草圖', '辨認可修改的外框尺寸', 'Object Mode，選取 Body；這是固定版的獨立副本。', ['右鍵 Body，選 Edit Sketch > Body Sketch。', '對照 Sketcher 側欄兩個 Distance：60／40 mm。'], '原圖顯示 Body Sketch 及60／40 mm；這些欄位是本次外框尺寸，其他場景需另行確認。', figures[1:4], [summary_ref]),
        ('ch04-link-counterexample-03', '將 X 從60改成70', '觀察外框修改後切割體是否跟隨', 'Body Sketch；右側第一個 Distance 為本次 X。', ['將第一個 Distance 設為70 mm，維持第二個40 mm。', '對照摘要中外框與切割體界限。'], '畫面顯示70／40；程式讀回外框 X0～70、切割體仍 X2～58，X兩側界限差由2／2變為2／12 mm。', figures[4:5], [summary_ref]),
        ('ch04-link-counterexample-04', '將 Y 從40改成50', '辨認兩個方向都沒有內部連動', 'Body Sketch；本次第二個 Distance 為 Y。', ['將第二個 Distance 改為50 mm，第一個維持70 mm。', '比較摘要中的 X／Y 兩側界限差。'], '畫面顯示70／50；程式讀回切割體仍 X2～58／Y2～38，X與Y各兩側界限差皆為2／12 mm。', figures[5:6], [summary_ref]),
        ('ch04-link-counterexample-05', '另存並重開反例', '保存反例以核對連動問題', '70×50 反例；以不同檔名另存，保留固定版。', ['對照另存與重開畫面，再核對摘要。'], '畫面重開顯示70／50；程式讀回外框、固定切割體及 X／Y 兩側2／12 mm 界限差與保存前一致。', figures[6:8], [trial_scene, summary_ref]),
    ]
    steps = [{'id': id, 'title': title, 'goal': goal, 'context': context, 'actions': actions, 'success': success,
              'shortcuts': [], 'figures': figs, 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
              'limitations': list(common), 'artifacts': artifacts} for id,title,goal,context,actions,success,figs,artifacts in sections]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch04')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 206 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('v012 當時的切割體試驗未另存；後續另存固定版並重開測試，手工模型外框改 X／Y 時切割體未連動，非技術不可連動的結論。')
    data['version'] = 'v013 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v013追加固定版保存與外框尺寸變更未連動反例，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v012.json', 'sha256': SOURCE_SHA}, {'path': summary_ref['path'], 'sha256': SUMMARY_SHA}])
    data['outerLinkageNegativeVerification'] = {'summary': summary_ref, 'fixedScene': fixed_scene, 'trialScene': trial_scene,
        'scope': '固定版與70×50反例另存重開；反例外框改動未帶動切割體，不推論工具無法連動。',
        'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV013'] = '追加固定版本保存原圖及八張尺寸變更反例原圖，區分外框與切割體界限差、未驗布林後壁厚。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v013')
    if SOURCE.read_bytes() != before:
        raise ValueError('v012 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
