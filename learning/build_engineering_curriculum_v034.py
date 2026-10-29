"""Record the repaired thread and side mount without completing learner steps."""
import hashlib
import json
from pathlib import Path
from build_engineering_curriculum_v033 import lesson_step

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v033.json'
DEST = ROOT / 'learning/web/engineering-curriculum-v034.json'
SOURCE_HASH = 'a5688b2abaad001a60c193a187784c8a67ec88c9862fd5fade7bfa8ce1d3bfa6'
REPAIRED = ROOT / 'learning/lesson11_external_repaired_optional_steps_v001.json'
MOUNT = ROOT / 'learning/lesson11_external_mount_optional_steps_v002.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    if DEST.exists():
        raise FileExistsError('refusing to overwrite ' + DEST.name)
    if sha(SOURCE) != SOURCE_HASH:
        raise ValueError('v033 source changed')
    data, repaired, mount = read(SOURCE), read(REPAIRED), read(MOUNT)
    for path, expected in [(repaired['demonstrationScene'], repaired['demonstrationSceneSha256']),
                           (mount['demonstrationScene'], mount['demonstrationSceneSha256'])]:
        if sha(ROOT / path) != expected:
            raise ValueError('demonstration scene changed: ' + path)
    if len(repaired['steps']) != 14 or len(mount['steps']) != 11:
        raise ValueError('incomplete step list')
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch11')
    for section in chapter['sections']:
        if section['id'] == '11-08':
            section['title'] = '歷史外牙問題案例（選修）'
    index = next(i for i, section in enumerate(chapter['sections']) if section['id'] == '11-08')
    chapter['sections'][index + 1:index + 1] = [
        {'id': '11-11', 'title': '修訂外牙操作與幾何檢查（選修草案）', 'track': 'optional'},
        {'id': '11-12', 'title': '盒側外牙接合（選修草案）', 'track': 'optional'},
    ]
    thread_steps = [lesson_step(s, '11-11', repaired['limitations'], 'inner') for s in repaired['steps']]
    mount_steps = [lesson_step(s, '11-12', mount['limitations'], 'inner') for s in mount['steps']]
    start = repaired['startingScene']
    thread_steps[0]['context'] += ' 可複製起始檔：' + start['path'] + '（SHA-256 ' + start['sha256'] + '）。'
    mount_steps[0]['context'] += ' 盒蓋來源：' + mount['sourceScene'] + '（SHA-256 ' + mount['sourceSha256'] + '）；牙條來源：' + mount['threadScene'] + '（SHA-256 ' + mount['threadSceneSha256'] + '）。請先複製，保留原檔。'
    mount_steps[-1]['limitations'] = mount_steps[-1]['limitations'] + ['接合後仍有最短邊約 0.01469 mm 與最小三角高約 0.001126 mm 的細小三角形；三角高不是壁厚，診斷門檻不是合格尺寸。']
    chapter['steps'].extend(thread_steps + mount_steps)
    chapter['detailNote'] = '舊主線文字沿用既有教材；選修 11-09～11-12 另有本次獨立 Blender 實拍與讀值，11-08 保存修正前問題案例。材料、實體量測與試配尚未完成。'
    # These original goals are broader than the fixed-parameter demonstration.
    for step in chapter['steps']:
        if step['id'] == 'ch11-08-02-02':
            step['title'] = '自訂截面與 Screw 參數（完整草圖路線待補）'
            step['actions'] = ['固定草案的修訂外牙已有選修 11-11；本步完整自訂規格路線仍需補上由草圖建立截面與對應參數的操作。']
            step['limitations'] = ['選修 11-11 有固定參數的實拍；其截面由程式預建，不能代替自行畫草圖或指定螺紋規格的完整流程。']
            step['detail']['steps'] = step['actions'] + ['可先跟做 11-11 與 11-12，辨認 5.625° 相位、4.8 mm 高度與數位檢查的用途與限制。']
            step['detail']['why'] = '固定參數草案已有實拍；自行繪製截面、指定規格及全面驗證仍需另行完成。'
        if step['id'] in ('ch11-08-03-01', 'ch11-08-03-02'):
            step['actions'] = ['完整盒蓋配套內牙仍待製作；選修 11-09 已有獨立試塊差集，11-11 為另一修訂外牙，兩者未配套。']
            step['limitations'] = ['內牙試塊不是盒蓋；其程式工具端部與間隙尚未設為修訂外牙的匹配件。']
            step['detail']['steps'] = step['actions'] + ['先取得對件、軸向定位、規格及試驗間隙來源，再建完整盒蓋與全面幾何檢查。']
            step['detail']['why'] = '獨立試塊的差集練習已有實拍；它與修訂外牙尚未設成匹配件，不能直接當完整盒蓋。'
        if step['id'] == 'ch11-08-04-02':
            step['actions'] = ['獨立盲孔柱已有選修 11-10；指定五金的柱、蓋孔與裝配路線仍待選型後製作。']
            step['limitations'] = ['盲孔柱尺寸為幾何草案，無指定五金資料或合格孔徑；不可由示範直接推定正式規格。']
            step['detail']['steps'] = step['actions'] + ['先取得所選螺絲或熱熔螺母資料，分別核對導孔、孔深、壁厚及蓋孔。']
            step['detail']['why'] = '獨立盲孔柱的幾何練習已有實拍；正式柱孔尺寸仍取決於實際五金、材料與裝配條件。'
    data['version'] = 'v034 · 2026-10-28'
    data['description'] += ' v034 加入修訂外牙 14 步及盒側接合 11 步，保留舊問題案例；記錄相位與高度改變、檢查門檻及細小幾何限制。'
    data['sourceVersions'] += [
        {'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_HASH},
        {'path': REPAIRED.relative_to(ROOT).as_posix(), 'sha256': sha(REPAIRED)},
        {'path': MOUNT.relative_to(ROOT).as_posix(), 'sha256': sha(MOUNT)},
    ]
    data['contentReview']['reviewV034'] = {
        'reviewedOn': '2026-10-28', 'scope': '固定參數修訂外牙及盒側介面；幾何檢查支持已列項目，並非全面自交或製造證明。',
        'learnerProgressChanged': False, 'physicalPrint': None, 'physicalMeasurement': None,
        'physicalFit': None, 'qualifiedClearance': None, 'qualifiedStrength': None,
    }
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(sha(DEST))


if __name__ == '__main__':
    main()
