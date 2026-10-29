"""Build a separate teaching reference from the frozen v001 path and current catalog.

It never modifies learner progress, catalog, source evidence, or the v001 path.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / 'learning/catalog.json'
PATH_V1 = ROOT / 'learning/web/engineering-path-v001.json'
OUT = ROOT / 'learning/web/engineering-curriculum-v002.json'

MAPPING = {
    'ch01': ['01-01', '01-02', '01-03', '01-05', '01-06', '01-08', '05-05'],
    'ch02': ['04-01', '05-01', '04-08'],
    'ch03': ['01-07', '02-05', '02-06', '02-07', '04-02', '04-03', '04-04', '04-05', '04-06'],
    'ch04': [],
    'ch05': ['05-05'],
    'ch06': ['05-02', '05-03'],
    'ch07': ['04-07', '05-04', '05-06', '04-08'],
    'ch08': ['06-01', '06-02', '06-03'],
    'ch09': ['07-01', '07-02', '07-03', '07-04', '07-05'],
    'ch10': ['08-01', '08-02', '08-03', '08-04', '08-05'],
    'ch11': ['01-04', '01-09', '09-01', '09-02', '09-03'],
    'ch12': ['02-01', '02-02', '02-03', '02-04', '03-01', '03-02', '03-03', '03-04', '03-05', '03-06'],
}

LIMITS = {
    'ch01': ['組裝分離圖為暫抬上蓋；圖片本身不能量出間隙。'],
    'ch02': ['名義尺寸、允許偏差、總間隙、單邊間隙與實測分開；0.4 mm 總間隙只是試驗值。', '0.4 mm 噴嘴不推定線寬、材料或合格間隙。'],
    'ch03': ['Object Mode／Edit Mode、作用中物件與欄位焦點先確認；快捷鍵為對應情境而非萬用。'],
    'ch04': ['本章草圖只證明隔離環境的矩形、尺寸與平面網格聯動；尺寸標註延伸線部分出視區。'],
    'ch05': ['既有上蓋為靜態幾何示範；除非另有實際版本證據，不能稱作盒蓋參數連動。', '0.4 mm 總間隙是試驗，不代表合格。'],
    'ch06': ['0.1～0.6 mm 是總間隙試驗點，不是經驗證可用範圍。', '孔板凹點間最窄剩肉約 0.399994 mm，與 0.4 mm 噴嘴接近；是否可辨仍待切片／列印。'],
    'ch07': ['STL 本身不記錄單位；教材依 mm 解讀，重匯入及切片尺寸須逐一核對。', '輸出、讀回、列印、量測、試配與合格為不同證據。'],
    'ch08': ['環唇與定位柱共同定位可能對尺寸誤差敏感；細長柱列印穩定性待試。', '06-02 原幾何中盒內導軌朝下懸面合計約 448 mm²；方向與支撐需切片確認。'],
    'ch09': ['材料、允許應變待定；方向及支撐為候選。', 'A_L19、B_L17、C_L21 是尺寸對照草案，不表示已證改善或強度、配合合格。'],
    'ch10': ['08-01 是規格與參數紀錄；08-02～08-05 尚無逐步建模原圖，僅作待實作參考。', 'Angle 360° 且 Object Screw 關閉時 Screw 對應導程；僅單線時導程等於螺距。'],
    'ch11': ['09-01～09-03 尚待實體結果；不能用數位尺寸推定補償或合格。'],
    'ch12': ['可在第05章後穿插；既有渲染示範為訊號站，小盒渲染需另行製作。'],
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def figure(path: str, caption: str, expected: str | None = None) -> dict:
    p = ROOT / path
    if not p.is_file() or p.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        raise ValueError(f'Not a readable original image: {path}')
    actual = sha(p)
    if expected and actual.lower() != expected.lower():
        raise ValueError(f'Image hash mismatch: {path}')
    return {'type': 'screenshot', 'path': path, 'sha256': actual, 'caption': caption}

def catalog_figure(step: dict) -> list[dict]:
    original = step.get('figures') or []
    if original:
        f = original[0]
        if f.get('type') == 'screenshot' and f.get('sha256'):
            return [figure(f['path'], '原步驟實拍參照（請對照本圖原說明，未必顯示此小步的全部操作）：' + f.get('caption', ''), f['sha256'])]
    # Existing operation events are linked by step in the catalog; avoid selecting
    # arbitrary screenshots from a file dialog or implying an unrelated event.
    return []

def source_mini_steps(chapter: str, source: dict) -> list[dict]:
    sid = source['id']
    lesson = sid[:2]
    guides = source.get('guide') or [{'where': '原步驟', 'do': source['action'], 'see': source['success']}]
    run = source.get('operationRun') or {}
    has_demo = run.get('status') == 'completed' and bool(run.get('events'))
    kind = 'existing_demo' if has_demo else 'draft_pending_demo'
    limitations = ['既有示範的觀察、數位讀值與學員實作分開；不表示實體結果或學員完成。'] if has_demo else ['此原步驟尚無完整逐步 Blender 操作證據；文字作學習／實作指引，不冒稱已示範。']
    figures = catalog_figure(source)
    result = []
    for idx, guide in enumerate(guides, 1):
        shortcuts = [guide['shortcut']] if isinstance(guide.get('shortcut'), dict) else []
        local_figures = figures if idx == 1 else []
        if not local_figures:
            for shortcut in shortcuts:
                for item in shortcut.get('evidence', []):
                    image_path = item.get('path', '')
                    if image_path.lower().endswith(('.png', '.jpg', '.jpeg')) and item.get('sha256'):
                        local_figures = [figure(image_path, '快捷操作原圖參照，圖中操作以原始註記為準：' + item.get('label', ''), item['sha256'])]
                        break
                if local_figures:
                    break
        # 04-07 demonstrates STL export, but its final guide also asks to open
        # a slicer, which was not demonstrated in this source run.
        step_kind = 'draft_pending_demo' if sid == '04-07' and idx == 3 else kind
        step_limits = limitations if step_kind == kind else ['STL 匯出有既有數位證據；切片軟體實際操作尚待完成。']
        result.append({
            'id': f'{chapter}-{sid}-{idx:02d}',
            'title': f"{source['title']} · {idx}",
            'goal': source['action'],
            'context': guide.get('where', '依原步驟核對工作區、模式與選取。'),
            'actions': [guide['do']],
            'success': guide.get('see', source['success']),
            'shortcuts': shortcuts,
            'figures': local_figures,
            'sourceSteps': [{'lessonId': lesson, 'stepId': sid}],
            'evidenceStatus': step_kind,
            'limitations': step_limits,
        })
    return result

def bespoke(chapter, ident, title, goal, context, actions, success, *, figs=(), status='concept_only', limits=(), sources=()):
    return {'id': f'{chapter}-{ident}', 'title': title, 'goal': goal, 'context': context,
            'actions': list(actions), 'success': success, 'shortcuts': [], 'figures': list(figs),
            'sourceSteps': list(sources), 'evidenceStatus': status, 'limitations': list(limits)}

def main():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    path = json.loads(PATH_V1.read_text(encoding='utf-8'))
    old = {step['id']: step for lesson in catalog['lessons'] for step in lesson['steps']}
    assert set().union(*(set(v) for v in MAPPING.values())) == set(old), 'Mapping must retain every source step.'
    cad = 'learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/'
    cad_limit = ('原圖來自隔離 Blender；環境與單位由程式 bootstrap，幾何與尺寸由原生事件操作。', '尺寸標註延伸線部分出視區；平面網格沒有厚度。')
    sketch = [
      bespoke('ch04','sketch-01','建立 XY 草圖','在隔離環境建立草圖並辨識平面','3D Viewport；CAD Sketcher 已啟用；Unit Scale 0.001、Millimeters', ['Ctrl+Shift+A 開啟 Add Sketch；在平面選擇時按 Z 選 XY。'], '實際出現 XY 草圖；空草圖完全約束不代表後續矩形已完全約束。', figs=[figure(cad+'CAD-ENV-03-origin-sketch.png','獨立 Blender 原圖：XY 草圖。')],status='existing_demo',limits=cad_limit),
      bespoke('ch04','sketch-02','建立數值矩形','辨認輸入尺寸與約束的差別','XY 草圖內、矩形工具作用中', ['R 矩形；以原點為起點輸入 60、40 mm；再查看側欄自由度。'], '矩形點座標形成 60×40 mm；數值輸入本身尚未替寬高加尺寸約束。', figs=[figure(cad+'CAD-ENV-06-rectangle.png','獨立 Blender 原圖：數值矩形及草圖側欄。')],status='existing_demo',limits=cad_limit),
      bespoke('ch04','sketch-03','標註寬度與高度','建立可修改的尺寸約束','草圖內，確認選對矩形邊線', ['D Dimension 選邊，加上 60 mm 寬度；再選高度邊，加 40 mm。'], '側欄可讀 60、40 mm 且 Fully defined；數值與自由度由讀回核對。', figs=[figure(cad+'CAD-ENV-08-height-dimension.png','獨立 Blender 原圖：側欄 60／40 與 Fully defined。')],status='existing_demo',limits=cad_limit),
      bespoke('ch04','sketch-04','變更尺寸並重開','驗證尺寸驅動及存檔','草圖側欄中的尺寸約束；另存新版本', ['將寬度約束由 60 改為 80 mm；另存後重新開啟。'], '草圖與生成平面網格為 80×40 mm，重開仍為 DoF 0。', figs=[figure(cad+'CAD-ENV-12-reopened-80.png','獨立 Blender 原圖：重開後的 80／40、Fully defined。')],status='existing_demo',limits=cad_limit),
    ]
    for entry, keys, effect in zip(sketch[:3], ['Ctrl+Shift+A → Z', 'R', 'D'],
            ['啟動 Add Sketch，再選 XY 平面。', '在草圖工作階段啟動矩形工具。', '在草圖工作階段啟動 Dimension 約束工具。']):
        image = entry['figures'][0]
        entry['shortcuts'] = [{'keys': keys, 'effect': effect,
            'requirements': ['CAD Sketcher 已啟用，滑鼠焦點位於 3D Viewport；先核對草圖及目前工具狀態。'],
            'cautions': ['此鍵位為隔離 Blender 5.2.1 與 CAD Sketcher 0.32.1 的試驗；先對照實際畫面，未核對替代選單路徑。'],
            'evidence': [{'path': image['path'], 'sha256': image['sha256'], 'method': 'native_events_and_readback', 'label': '獨立 Blender 原圖與隔離草圖試驗記錄'}]}]
    concept = {
       'ch01': [bespoke('ch01','fit-surfaces','辨認配合表面','辨認會彼此配合的位置','觀察 05-05 分離圖；上蓋暫抬高',['找出環形唇邊外側與盒口內壁。'], '指出比較的是唇邊外側與盒口內壁。',figs=[figure('learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png','獨立 Blender 分離原圖；暫抬上蓋，不可從圖量細縫。')],status='existing_demo',limits=['上蓋暫抬；細縫不能由圖量出。'],sources=[{'lessonId':'05','stepId':'05-05'}])],
       'ch02': [bespoke('ch02','gap-terms','先分清總間隙與單側','學習間隙定義與置中條件','同一 X 方向，先區分兩件名義尺寸',['比較 56 mm 盒口內寬和 55.6 mm 唇邊外寬。'], '名義差 0.4 mm 為總間隙；置中時每側 0.2 mm，兩者都是草案數位計算。',figs=[figure('learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png','獨立 Blender 分離原圖用以辨認盒口與唇邊；尺寸依幾何讀值，不能從圖量得。')],status='concept_only',limits=['不是實體實測或合格配合。'])],
       'ch04': sketch,
       'ch05': [bespoke('ch05','param-plan','安排單一尺寸來源','讓盒與蓋能依同一主控尺寸更新','另建副本；參數模型技術示範需另行核對',['將盒長與盒寬設為同一主控；側壁、底厚、板厚、唇深與總間隙分開命名。'], '寫出內腔＝外寬−2×側壁，唇外＝內腔−總間隙；保存與改尺寸的實測另記。',status='draft_pending_demo',limits=['此小步是參數設計安排，尚不代表已完成盒蓋連動。'])],
       'ch11': [bespoke('ch11','dimension-chain','從尺寸鏈查設計變更','追溯配合與版本','保留模型來源、名義尺寸、試驗值與實測的分欄', ['列出盒口內寬＝外寬−2×側壁；唇外＝內寬−總間隙。'], '可區分設計關係、數位讀值與實際測量，未驗證欄位留空。',status='concept_only',limits=['不由單一試片結果推定批量能力。'])],
    }
    chapters = []
    for chapter in path['chapters']:
        cid = chapter['id']
        items = list(concept.get(cid, []))
        for sid in MAPPING[cid]:
            items.extend(source_mini_steps(cid, old[sid]))
        chapters.append({'id': cid, 'number': chapter['number'], 'title': chapter['title'],
            'goal': chapter['goal'], 'deliverable': chapter['deliverable'],
            'limitations': LIMITS[cid], 'steps': items})
    data = {'schemaVersion': 1, 'id': 'engineering-curriculum-v002', 'version': 'v002 · 2026-10-27',
        'description': '12章詳細操作參照；示範狀態、草案與學員進度分開，不取代原 catalog 或 progress。',
        'sourceVersions': [{'path':'learning/catalog.json','sha256':sha(CATALOG)}, {'path':'learning/web/engineering-path-v001.json','sha256':sha(PATH_V1)}],
        'evidenceStatusDefinitions': {'existing_demo':'來源原步有助教示範，個別小步需對照原始事件；非學員完成及實體驗收。', 'concept_only':'概念與計算引導，不冒充新 Blender 操作。', 'draft_pending_demo':'實作指引草案，尚無完整對應操作與畫面。'},
        'contentReview': {'sources':['learning/catalog.json','learning/web/engineering-path-v001.json','learning/annotations/guide-shortcuts-v002.json','learning/journal/2026-10-22-lesson05-lid-demo-v001.md','learning/journal/2026-10-25-claude-continuation-audit-v001.md','learning/journal/2026-10-27-cad-sketcher-environment-trial-v001.md'], 'scope':'12章對應所有原52步；依原步 guide 拆小步；CAD Sketcher 四步依隔離試驗記錄。', 'learnerProgressChanged':False},
        'chapters':chapters}
    if OUT.exists():
        raise FileExistsError(f'Refusing to overwrite version: {OUT}')
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {OUT}: {len(chapters)} chapters, {sum(len(c['steps']) for c in chapters)} microsteps.")

if __name__ == '__main__':
    main()
