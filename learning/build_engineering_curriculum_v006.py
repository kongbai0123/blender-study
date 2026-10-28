"""Correct ideal polygon calculation and blind-hole evidence wording without changing IDs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V005 = ROOT / 'learning/web/engineering-curriculum-v005.json'
V006 = ROOT / 'learning/web/engineering-curriculum-v006.json'
EXPECTED_V005 = '9cc2e9e54ac587669cd90cc19f5fe08cce8952af11cde412cb4674e648aaedff'


def main():
    before = V005.read_bytes()
    if hashlib.sha256(before).hexdigest() != EXPECTED_V005:
        raise ValueError('v005 differs from the documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch10')
    boss = {s['id']:s for s in chapter['steps'] if s['id'].startswith('ch10-boss-draft-')}
    expected = {'ch10-boss-draft-observe', 'ch10-boss-draft-diameter', 'ch10-boss-draft-depth', 'ch10-boss-draft-save'}
    if set(boss) != expected:
        raise ValueError('unexpected boss steps')
    corrections = []
    def change(step, field, value):
        previous = step[field]
        if previous != value:
            corrections.append({'stepId':step['id'], 'field':field, 'before':previous, 'after':value})
            step[field] = value

    for step in boss.values():
        limitations = list(step['limitations'])
        if len(limitations) != 4 or '精確對邊距根據網格數位讀值' not in limitations[3]:
            raise ValueError('unexpected original boss evidence limitation')
        limitations[1] = '示範柱與原盒是兩個獨立物件，沒有布林結合，也未驗證彼此無干涉；沒有螺紋或已選五金，不代表可自攻、安裝熱熔螺母、強度或配合合格。'
        limitations[3] = '截圖中盲孔底部不可見；孔深與底厚由網格 Z 邊界讀值推得，對頂尺寸來自網格讀值，對邊距是理想正32邊形公式推算，尚非實際投影量測。'
        change(step, 'limitations', limitations)

    diameter = boss['ch10-boss-draft-diameter']
    change(diameter, 'context', '對頂尺寸使用網格讀值；對邊距使用理想正32邊形公式，不當成實際投影量測。')
    change(diameter, 'actions', ['對照摘要中的外徑與孔徑對頂值，分別乘以 cos(π／32) 推算理想對邊距。'])
    change(diameter, 'success', '外／孔對頂網格讀值為8／4 mm；依理想正32邊形公式推算對邊約7.9615／3.9807 mm，非實際投影量測；4 mm不是已驗證的五金安裝孔徑。')

    depth = boss['ch10-boss-draft-depth']
    change(depth, 'goal', '由網格 Z 邊界讀值推得孔深與底厚')
    change(depth, 'context', '摘要 reopened 網格 Z 邊界讀值：孔Z1～8 mm、外框Z0～8 mm。')
    change(depth, 'actions', ['對照網格讀回的孔底Z、孔口Z與柱底Z，分別相減推得孔深與底厚。'])
    change(depth, 'success', '由網格 Z 邊界讀值推得孔深7 mm、底厚1 mm；網格 Non Manifold 邊數0。不是強度或配合結論。')
    saved = boss['ch10-boss-draft-save']
    change(saved, 'success', '保存前、保存後及重開後各7項數位檢查通過；柱與參照盒為獨立物件，未核對彼此是否干涉。')
    for sid in ('ch10-boss-draft-diameter', 'ch10-boss-draft-depth'):
        step = boss[sid]
        figures = [dict(f) for f in step['figures']]
        figures[0]['caption'] = '獨立 Blender 原圖：重開後的獨立柱體；截圖看不到孔底，孔深與底厚由網格 Z 邊界讀值推得。'
        change(step, 'figures', figures)

    data['version'] = 'v006 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v006釐清盲孔柱的理想對邊計算與網格Z邊界讀值，學員事件沿用穩定教材ID。'
    data['sourceVersions'].append({'path':'learning/web/engineering-curriculum-v005.json','sha256':EXPECTED_V005})
    data['contentReview']['supplementV006'] = '盲孔柱對邊改標為理想正32邊形公式推算；孔深與底厚由網格Z邊界讀值推得，柱與盒未驗證無干涉。'
    data['contentReview']['correctionsV006'] = corrections
    if V006.exists():
        raise FileExistsError('refusing to overwrite v006')
    if V005.read_bytes() != before:
        raise ValueError('v005 changed during build')
    V006.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {V006}: corrected {len(corrections)} fields across {len(boss)} boss steps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
