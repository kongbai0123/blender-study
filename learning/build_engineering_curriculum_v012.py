"""Append fixed-size cavity cutter probe without modifying v011."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v011.json'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v012.json'
SOURCE_SHA = 'f39e7ecbcbf8c3371e06de697ac93abd53cd8a1390b9807c2ecb57e96fa130a4'
BASE = 'learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/'
SUMMARY_SHA = '2b980d31d86dcd82fa7c4f2f290ff70b1446ba92ceee0142da8098fd193c0c9d'
STATES = {
    'height-state.json': ('16060bff78c97774100ca22da01a26df685db63eaf6b55e94b020bad06a880fb', 2),
    'center-horizontal-state.json': ('97b82d988910396df9cc9bc9563876e482ae9ab9a3572c95f213dcf92afd1db4', 1),
    'center-vertical-state.json': ('ca2ef5d5836f985e7628957fdf8cd0ee5c2484ffb7b5b68a155a2f6878438b55', 0),
}


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
        raise ValueError('v011 differs from documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data['id'] != 'engineering-curriculum-v002':
        raise ValueError('unexpected curriculum ID')
    summary_ref = checked(BASE + 'center-constraints-fixed-probe-v001.json', SUMMARY_SHA, '固定尺寸內腔切割體探測摘要', 'verification-json')
    summary = json.loads((ROOT / summary_ref['path']).read_text(encoding='utf-8-sig'))
    if summary['kind'] != 'fixed-geometry-probe-not-parametric-box':
        raise ValueError('unexpected trial scope')
    if summary['sketch'] != {'solver': 'OKAY', 'degreesOfFreedom': 0, 'distanceConstraintsMm': [56,36,28,18]}:
        raise ValueError('unexpected final sketch readback')
    if summary['cutterBoundsMm'] != [[2,58],[2,38],[2,30]] or summary['cutterDimensionsMm'] != [56,36,28]:
        raise ValueError('unexpected cutter readback')
    # Stage files are used only for local verification, not added to the published index.
    for name, (expected, dof) in STATES.items():
        checked(BASE + name, expected, name, 'verification-json')
        state = json.loads((ROOT / (BASE + name)).read_text(encoding='utf-8-sig'))
        if state['sketch']['solver'] != 'OKAY' or state['sketch']['dof'] != dof:
            raise ValueError('unexpected staged solver readback: ' + name)
    checked(BASE + 'after-cut-state.json', 'a5eb891a6c7810f9533d385177b0ac4448690ea58e58a6ff4753a7fcb3012160', 'cut readback', 'verification-json')
    final = json.loads((ROOT / (BASE + 'after-cut-state.json')).read_text(encoding='utf-8-sig'))
    cutter = next(o for o in final['objects'] if o['name'] == 'Body.001')
    if cutter['evaluated']['bounds'] != [[2,58],[2,38],[2,30]]:
        raise ValueError('final cutter bounds differ')
    images = summary['images']
    if len(images) != 11:
        raise ValueError('expected eleven screenshots')
    for i, f in enumerate(images, 1):
        if f['seq'] != i:
            raise ValueError('unexpected image sequence')
        checked(BASE + f['file'], f['sha256'], str(i), 'screenshot')
    captions = [
        '獨立 Blender 原圖：既有 GUI 草圖拉伸實心體副本；外框數值由讀值提供。',
        '原圖：開始挑選草圖工作平面；頂面仍是下一步目標。',
        '原圖：點選頂面後進入 Body.001 Sketch。',
        '原圖：頂面以兩點畫出近似矩形；此時未確認準確尺寸與位置。',
        '原圖：水平邊加56 mm 約束，圖上可見56.000 mm。',
        '原圖：加入垂直邊長度約束；標註重疊，36 mm 與自由度須看讀值。',
        '原圖：加入28 mm 水平定位，標註重疊；數值與自由度須看讀值。',
        '原圖：加入18 mm 垂直定位；標註重疊，求解狀態須看讀值。',
        '原圖：離開內矩形草圖後，頂面草圖生成面被選取。',
        '原圖：啟動 Extrude；左上 Auto Boolean 勾選，畫面為操作預覽。',
        '原圖：輸入−28 並確認後外觀呈現凹陷；目前讀回確定的是切割體外框，尚未完成布林結果驗證。',
    ]
    figures = [{'type': 'screenshot', 'path': BASE + f['file'], 'sha256': f['sha256'], 'caption': caption} for f, caption in zip(images, captions)]
    common = [
        '獨立 Blender 5.2.1／CAD Sketcher 0.32.1；先前 GUI 草圖拉伸的60×40×30 mm 實心體副本，程式載入及啟用擴充套件並計算滑鼠座標、讀值；檔案開啟路徑由程式填入。',
        '本試驗為固定尺寸：內矩形56×36、角點到頂面草圖中心水平28／垂直18 mm；沒有驗證更改外草圖時尺寸連動。',
        '結果已讀回切割體，未充分驗證布林後內腔幾何及封閉性；不可將名義2 mm 四壁與底厚當作已確認結果。',
        '圖中的尺寸標註有重疊；自由度、切割體外框由程式讀回，不能只憑圖片量得。未建立上蓋或另存此場景。',
        '實體列印、量測、試配及合格值均未取得；數位幾何不代表可製造或配合合格。',
    ]
    sections = [
        ('ch04-cavity-01', '在實心體頂面建立草圖', '辨認固定實心體與頂面工作平面', 'Object Mode；Body 已選取；使用既有 60×40×30 mm 實心體副本。', ['在 3D 視圖按 Ctrl+Shift+A 進入挑選工作平面；點頂面。'], '畫面進入 Body.001 Sketch；外框數值來自程式讀值。', 0, 3),
        ('ch04-cavity-02', '畫近似內矩形', '建立後續尺寸約束的輪廓', 'Body.001 Sketch 活動、焦點在3D視圖。', ['按 R，在頂面內點選矩形兩個角點；按 Esc 結束工具。'], '原圖顯示近似矩形；此刻不將視覺位置當作準確尺寸。', 3, 4),
        ('ch04-cavity-03', '標註內矩形長寬', '以尺寸約束取代估計', 'Body.001 Sketch 中的矩形，3D視圖。', ['按 D 點選水平邊並輸入56，確認後結束工具。', '再按 D 點垂直邊輸入36並確認。'], '程式讀回56／36 mm 且 solver OKAY、DoF 2；重疊標註不可直接作為全部數值證據。', 4, 6),
        ('ch04-cavity-04', '用水平尺寸定位角點', '固定矩形的水平位置', 'Body.001 Sketch，選取工具依本次畫面；頂面草圖原點是面中心。', ['按 Alt+H，依序選內矩形角點與草圖原點，放置標註並輸入28；確認後退出工具。'], '程式讀回水平約束28 mm、solver OKAY、DoF 由2降為1；文字標註重疊。', 6, 7),
        ('ch04-cavity-05', '用垂直尺寸完成定位', '固定矩形的垂直位置', '仍在同一草圖，使用相同角點與頂面草圖原點。', ['按 Alt+V，依序選角點與草圖原點，放置標註並輸入18；確認後退出工具。'], '程式讀回垂直約束18 mm、solver OKAY、DoF 由1降為0。', 7, 8),
        ('ch04-cavity-06', '拉伸切割體並核對', '核對固定尺寸切割體的位置與範圍', '內矩形草圖完成；本次場景 Unit Scale 0.001。', ['按 Ctrl+Shift+A 離開草圖，按 Ctrl+Shift+E 啟動 Extrude。', '本次輸入 −28 並確認；觀察 Auto Boolean 勾選及結果。'], '畫面外觀呈現凹陷；程式讀回切割體 X2～58、Y2～38、Z2～30 mm。布林後內腔與封閉性尚未充分驗證。', 8, 11),
    ]
    steps = []
    for id, title, goal, context, actions, success, lo, hi in sections:
        steps.append({'id': id, 'title': title, 'goal': goal, 'context': context, 'actions': actions, 'success': success,
                      'shortcuts': [], 'figures': figures[lo:hi], 'sourceSteps': [], 'evidenceStatus': 'existing_demo',
                      'limitations': list(common), 'artifacts': [summary_ref]})
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch04')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if len(old_ids) != 200 or any(s['id'] in old_ids for s in steps):
        raise ValueError('unexpected baseline or duplicate IDs')
    chapter['steps'].extend(steps)
    chapter['limitations'].append('新增固定外形下的內矩形約束與切割體探測；布林結果、尺寸連動、上蓋及另存仍未充分驗證。')
    data['version'] = 'v012 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v012追加固定尺寸內矩形約束及切割體探測，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path': 'learning/web/engineering-curriculum-v011.json', 'sha256': SOURCE_SHA}, {'path': summary_ref['path'], 'sha256': SUMMARY_SHA}])
    data['fixedCavityCutterVerification'] = {'summary': summary_ref, 'scope': '固定尺寸內矩形與切割體探測；未充分驗證布林後內腔、尺寸連動、上蓋與另存。',
        'physicalMeasurements': None, 'fitResults': None, 'qualifiedClearanceMm': None}
    data['contentReview']['supplementV012'] = '追加11張實圖、局部自由度讀回與切割體範圍；不將布林結果、連動、上蓋或另存標為已驗。'
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite v012')
    if SOURCE.read_bytes() != before:
        raise ValueError('v011 changed during build')
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Created {OUTPUT}: {sum(len(c["steps"]) for c in data["chapters"])} microsteps.')


if __name__ == '__main__':
    main()
