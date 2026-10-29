"""Update chapter 11's overview after the recorded geometric workflows exist."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-path-v003.json'
OUTPUT = ROOT / 'learning/web/engineering-path-v004.json'
SOURCE_SHA = '9cb08486d3de4c3225aebb9de1ff8471b5902026c84320f4b97a42a5d64962b0'


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('v003 changed')
    data = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch11')
    chapter['practice'] = ['以原生 mesh 逐點建立三角輪廓，續做 Screw、封端及芯柱外牙。',
                           '沿用盒側外牙做匹配保護蓋，分別記錄徑向與軸向試驗間隙。',
                           '依已選 M3 螺絲及熱熔螺母建立四柱、肋、導孔與原平面上蓋穿孔。']
    chapter['shortcuts'][0]['status'] = '手工輪廓、封端外牙、匹配盒側帽與五金柱孔已有獨立 Blender 示範；工具預建與 GUI 操作分列，實體結果待進行。'
    for ref in chapter['references']:
        if ref['stepId'] in ('08-02', '08-03', '08-04'):
            ref['label'] = {'08-02': '原單元外牙規劃（新版操作見小節）', '08-03': '原單元內牙規劃（新版為匹配盒側帽）', '08-04': '原單元五金規劃（已選 M3，見新版）'}[ref['stepId']]
    chapter['notes'] = ['原生 mesh 輪廓不是 CAD 尺寸約束草圖；原平面上蓋保留，由金屬固定分支補柱孔。',
                        '0.4 mm 名義直徑差與 0.2 mm 名義端隙只作試驗；局部數位檢查不代表完整旋合、實印或強度合格。']
    chapter['availabilityLabel'] = '幾何教學已有示範；實體試驗待進行'
    data['version'] = 'v004 · 2026-10-28'
    data['previousVersion'] = {'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA}
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
