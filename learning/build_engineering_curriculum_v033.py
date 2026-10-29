"""Build v033 from v032 and verified isolated-Blender demonstrations.

The demonstrated objects are draft exercises, not the unfinished full box tasks.
Never writes learner progress or overwrites an existing curriculum.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v032.json'
DEST = ROOT / 'learning/web/engineering-curriculum-v033.json'
SOURCE_HASH = '7e123574e4687f2e6aca8b262dac7dcdadfe94cd080e854ca0f7703a3e24075b'
INNER = ROOT / 'learning/lesson11_inner_optional_steps_v001.json'
BOSS = ROOT / 'learning/lesson11_boss_optional_steps_v001.json'
EXTERNAL = ROOT / 'learning/lesson11_external_optional_steps_v001.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def figure(image, caption):
    path = image.get('relativePath', image.get('path'))
    if not path or not path.startswith('learning/evidence/') or '..' in Path(path).parts:
        raise ValueError('invalid screenshot path')
    if digest(ROOT / path) != image['sha256']:
        raise ValueError('screenshot hash mismatch: ' + path)
    return {'type': 'screenshot', 'path': path, 'sha256': image['sha256'], 'caption': caption}


def lesson_step(s, section, limitations, kind):
    if kind == 'boss':
        actions = s['operation']
        success = s['success']
        readings = [r['location'] + '：' + r['value'] for r in s['readings']]
        warnings = limitations + s['limits']
        image = s['screenshot']
    else:
        actions = [s['operation']]
        success = s['visibleConfirmation']
        readings = [s['programReadback']]
        warnings = limitations
        image = s['screenshot']
    return {
        'id': 'ch11-' + s['id'].lower(), 'title': s['goal'], 'goal': s['goal'],
        'context': s['context'], 'actions': actions,
        'success': success, 'shortcuts': [],
        'figures': [figure(image, '獨立 Blender 實際畫面；示範紀錄，不代表學員完成。')],
        'sourceSteps': [], 'evidenceStatus': 'existing_demo', 'limitations': warnings,
        'section': section, 'track': 'optional',
        'detail': {'steps': actions + ['示範讀值：' + item for item in readings],
                   'why': '這是獨立 Blender 的幾何練習；讀值與學員實作及實體結果分開紀錄。'},
    }


def main():
    if DEST.exists():
        raise FileExistsError('refusing to overwrite ' + DEST.name)
    if digest(SOURCE) != SOURCE_HASH:
        raise ValueError('v032 source changed')
    inner, boss, external = read(INNER), read(BOSS), read(EXTERNAL)
    assert len(inner['steps']) == 6 and len(boss['steps']) == 8 and len(external['steps']) == 14
    data = read(SOURCE)
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch11')
    section_specs = [
        ('11-04', {'id': '11-08', 'title': '外牙操作與待修幾何（選修草案）', 'track': 'optional'}),
        ('11-05', {'id': '11-09', 'title': '內牙試塊操作（選修草案）', 'track': 'optional'}),
        ('11-06', {'id': '11-10', 'title': '獨立盲孔柱操作（選修草案）', 'track': 'optional'}),
    ]
    for anchor, item in section_specs:
        index = next(i for i, section in enumerate(chapter['sections']) if section['id'] == anchor)
        chapter['sections'].insert(index + 1, item)
    boss_limits = [boss['scope'], '材料、五金、列印、量測及試配待定；數位讀值不是合格判定。']
    external_steps = [lesson_step(s, '11-08', external['limitations'], 'inner') for s in external['steps']]
    external_steps[0]['context'] += ' 起始副本：learning/evidence/08/2026-10-28-external-thread-profile-start-v001/u08_external_thread_profile_start_v001.blend（SHA-256 a9083cb26d87ff9d6d8d18ea81309f932812127cd468fb58659baf504609271c）。'
    inner_steps = [lesson_step(s, '11-09', inner['limitations'], 'inner') for s in inner['steps']]
    boss_steps = [lesson_step(s, '11-10', boss_limits, 'boss') for s in boss['steps']]
    inner_steps[0]['context'] += ' 示範來源：' + inner['sourceScene'] + '（SHA-256 ' + inner['sourceSha256'] + '）；請先複製再操作。'
    boss_steps[0]['context'] += ' 示範來源：' + boss['sourceScene']['relativePath'] + '（SHA-256 ' + boss['sourceScene']['sha256'] + '）；請先複製再操作。'
    chapter['steps'].extend(external_steps + inner_steps + boss_steps)
    data['version'] = 'v033 · 2026-10-28'
    data['description'] += ' v033 新增外牙、內牙試塊及盲孔柱的選修 GUI 實拍；外牙幾何待修，原待製作的盒蓋、五金選型與實體試配步驟仍待完成。'
    data['sourceVersions'] += [
        {'path': 'learning/web/engineering-curriculum-v032.json', 'sha256': SOURCE_HASH},
        {'path': INNER.relative_to(ROOT).as_posix(), 'sha256': digest(INNER)},
        {'path': BOSS.relative_to(ROOT).as_posix(), 'sha256': digest(BOSS)},
        {'path': EXTERNAL.relative_to(ROOT).as_posix(), 'sha256': digest(EXTERNAL)},
    ]
    data['contentReview']['reviewV033'] = {
        'reviewedOn': '2026-10-28', 'scope': '外牙十四步、內牙試塊六步、獨立盲孔柱八步；均為選修示範草案，外牙幾何待修。原六項待製作狀態維持。',
        'learnerProgressChanged': False, 'physicalPrint': None, 'physicalMeasurement': None,
        'physicalFit': None, 'qualifiedClearance': None, 'qualifiedStrength': None,
    }
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(digest(DEST))


if __name__ == '__main__':
    main()
