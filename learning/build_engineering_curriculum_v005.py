"""Append the blind-boss draft and repair one inaccurate v004 context."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V004 = ROOT / 'learning/web/engineering-curriculum-v004.json'
V005 = ROOT / 'learning/web/engineering-curriculum-v005.json'
EXPECTED_V004 = 'fb8ce0cbbf4606ad9d83498756ad891a0b2bbaaf747c65ca307da5d5f93825ec'
EVIDENCE = 'learning/evidence/08/2026-10-27-lesson08-boss-draft-v002/'
SUMMARY_SHA = '0cad6bd604a3170cc2946f766dc6904f5692afc24b2be420c7f71ae783ecd552'
SCENE_SHA = '4df306ac6b7e3f57108cb0221fad62480ca47c80f77d5ccd3e91632a6d5c7320'
FIX_STEP = 'ch10-screw-surface-inspect'
FIX_CONTEXT = '已新增 Screw 修改器並顯示評估結果；修改器未套用（Apply）。'
BOOLEAN_WARNING = '本次未封端的開放曲面不可直接當成已驗證的 Boolean 切割體；須先建立並驗證可用的封閉工具。'


def reference(rel, expected, label):
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('source escapes project')
    found = hashlib.sha256(path.read_bytes()).hexdigest()
    if found != expected:
        raise ValueError('source hash mismatch: ' + rel)
    return {'path': rel, 'sha256': found, 'label': label}


def picture(filename, expected, caption):
    item = reference(EVIDENCE + filename, expected, caption)
    return {'type':'screenshot', 'path':item['path'], 'sha256':item['sha256'], 'caption':caption}


def main():
    before = V004.read_bytes()
    if hashlib.sha256(before).hexdigest() != EXPECTED_V004:
        raise ValueError('v004 differs from the documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary = reference(EVIDENCE+'boss-draft-verification-v002.json', SUMMARY_SHA, '盲孔柱草案：操作方式及網格讀值摘要')
    scene = reference(EVIDENCE+'demo-files/u08_blind_boss_draft_v001.blend', SCENE_SHA, '獨立盲孔柱示範場景 v001')
    fig_before = picture('08-04-01-boss-draft.png', '73f87e8383b44db72ef06401537a653f74b742d0b413f3a4dcc4916a534787cf', '獨立 Blender 原圖：程式建立的柱體草案；作用中物件與外框8×8×8 mm可見，盲孔底部不在視野內。')
    fig_saved = picture('08-04-02-saved.png', '2d26b28a85c10822c74620625540115057f3bd66cbc615111ca0577a1f6962f1', '獨立 Blender 原圖：示範另存後；檔名與場景雜湊另依驗證紀錄核對。')
    fig_open = picture('08-04-03-reopened.png', '98a98a08f6e3f0e72ca315d7ef7701182ae3203038eeafa27870c3c3dac82c66', '獨立 Blender 原圖：重開後的獨立柱體；孔底無法由此圖確認，依網格讀值核對。')
    common = [
        '柱子由程式建模；GUI 原生事件用於視角觀察、另存與重開，檔案瀏覽器路徑由程式填入。',
        '示範為獨立柱，沒有與原盒結合；沒有螺紋或已選五金，不代表可自攻、安裝熱熔螺母、強度或配合合格。',
        '0.4 mm 噴嘴不能推定線寬、材料或合格孔徑；尚無切片、列印、實測、安裝或試鎖結果。',
        '截圖中盲孔底部不可見；孔深、底厚與精確對邊距根據網格數位讀值，不由圖像量取。',
    ]
    items = [
      ('observe','辨識獨立盲孔柱','先分清柱體與參照盒','獨立 Blender；Object Mode，作用中為 Boss_Blind_Polygon32，原盒 Body_Reference 隱藏。',
       '觀察柱體、上方孔口與右側外框尺寸。','圖上可見柱與孔口，外框為8×8×8 mm；原盒沒有與柱結合，盲孔底不在本視角內。',fig_before),
      ('diameter','分清對頂尺寸與對邊距','理解32邊形孔的數位尺寸','以同一個32邊形柱的網格讀值為準。',
       '對照摘要中外徑與孔徑的對頂值，再比較各自對邊距。','外／孔的對頂為8／4 mm，對邊分別約7.9615／3.9807 mm；4 mm並非已驗證的五金安裝孔徑。',fig_open),
      ('depth','讀取孔深與底厚','從網格檢查盲孔而非推測','摘要 reopened 檢查：孔Z1～8 mm、外框Z0～8 mm。',
       '對照摘要的孔底Z、孔口Z與柱底Z，算出孔深及底厚。','孔深7 mm、底厚1 mm；網格 Non Manifold 邊數0。這些是數位幾何讀值，不是強度或配合結論。',fig_open),
      ('save','另存並重開核對','保留不同檔案版本','File > Save As／Open；檔案路徑及名稱程式填入、確認與視角使用GUI原生事件。',
       '觀察示範保存與重開的原圖，再對照三組各七項網格檢查。','保存前、保存後及重開後各7項數位檢查通過；獨立柱與參照盒保持分離。',fig_saved),
    ]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch10')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    existing = next(s for s in chapter['steps'] if s['id'] == FIX_STEP)
    old_context = existing['context']
    if old_context != '獨立 Blender 的 Thread_Profile 已套用螺旋修改器顯示結果。':
        raise ValueError('expected original context changed; audit before correcting')
    existing['context'] = FIX_CONTEXT
    boolean_steps = [s for s in chapter['steps'] if any(ref.get('stepId') == '08-03' for ref in s['sourceSteps'])]
    if len(boolean_steps) != 2:
        raise ValueError('unexpected number of original 08-03 steps')
    for step in boolean_steps:
        step['limitations'].append(BOOLEAN_WARNING)
    for ident,title,goal,context,action,success,fig in items:
        step_id = 'ch10-boss-draft-'+ident
        if step_id in old_ids:
            raise ValueError('new ID conflicts with existing step')
        entry = {'id':step_id,'title':title,'goal':goal,'context':context,'actions':[action],
                 'success':success,'shortcuts':[],'figures':[fig],'sourceSteps':[],
                 'evidenceStatus':'existing_demo','limitations':list(common)}
        if ident == 'observe':
            entry['artifacts'] = [scene, summary]
        chapter['steps'].append(entry)
    # Preserve all IDs, but teach evidence first and leave the original
    # prospective 08-02..05 notes after the actual open-surface/boss examples.
    intro = [s for s in chapter['steps'] if any(r.get('stepId') == '08-01' for r in s['sourceSteps'])]
    surface = [s for s in chapter['steps'] if s['id'].startswith('ch10-screw-surface-')]
    boss = [s for s in chapter['steps'] if s['id'].startswith('ch10-boss-draft-')]
    used = {s['id'] for s in intro + surface + boss}
    pending = [s for s in chapter['steps'] if s['id'] not in used]
    chapter['steps'] = intro + surface + boss + pending
    chapter['limitations'] = [
        '原08-02／08-04待實作文字保留歷史狀態；v004補獨立開放曲面，v005補未接盒體的盲孔柱草案，完整可列印螺紋、配套五金及08-03／08-05仍待實作與驗證。',
        'Angle 360° 且 Object Screw 關閉時 Screw 對應導程；僅單線時導程等於螺距。',
    ]
    data['version'] = 'v005 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v005補入獨立盲孔柱數位草案並修正修改器未Apply，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v004.json', 'sha256':EXPECTED_V004},
                                   {'path':summary['path'], 'sha256':summary['sha256']}])
    data['bossDraftVerification'] = {'summary':summary, 'scene':scene, 'scope':'程式建立、GUI觀察及另存重開的獨立32邊形盲孔柱；無牙、無五金、不與盒體結合。',
        'physicalMeasurements':None, 'fitResults':None, 'qualifiedHoleDiameterMm':None, 'strengthQualified':None}
    data['contentReview']['supplementV005'] = '08-04補充獨立盲孔柱數位草案；ch10-screw-surface-inspect僅修正context中的修改器Apply誤述。'
    data['contentReview']['correctionV005'] = {'stepId':FIX_STEP,'field':'context','before':old_context,'after':FIX_CONTEXT,
        'reason':'實際示範的 Screw 修改器仍存在；僅取得 evaluated mesh，沒有執行 Apply。'}
    data['contentReview']['booleanWarningV005'] = {'stepIds':[s['id'] for s in boolean_steps], 'field':'limitations', 'added':BOOLEAN_WARNING}
    data['contentReview']['orderV005'] = 'ch10依序為原08-01、已示範開放曲面、獨立柱草案、原08-02～05待實作步驟；舊ID不變。'
    if V005.exists():
        raise FileExistsError('refusing to overwrite v005')
    if V004.read_bytes() != before:
        raise ValueError('v004 changed during build')
    V005.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {V005}: {sum(len(c['steps']) for c in data['chapters'])} microsteps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
