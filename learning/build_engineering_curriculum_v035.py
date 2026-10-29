"""Versioned native mesh, mating side-cap and selected M3 hardware lessons.

This updates content availability only. Never writes the learner's progress.
"""
import copy
import hashlib
import json
from pathlib import Path
from build_engineering_curriculum_v033 import lesson_step

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-curriculum-v034.json'
SOURCE_SHA = '119432ade0437a1c1d8063ad4d4d8cb368faa4351a21da6975164b2f69dbafd5'
OUTPUT = ROOT / 'learning/web/engineering-curriculum-v035.json'
SPECS = [
    ('11-13', '手工建立牙型 mesh 輪廓', 'learning/lesson11_hand_profile_optional_steps_v001.json', 13),
    ('11-14', '從手工輪廓建立外牙', 'learning/lesson11_hand_thread_optional_steps_v002.json', 14),
    ('11-15', '匹配盒側保護蓋與兩種間隙', 'learning/lesson11_side_cap_optional_steps_v002.json', 17),
    ('11-16', 'M3 熱熔螺母柱與蓋孔', 'learning/lesson11_four_insert_bosses_optional_steps_v001.json', 15),
]
READY = {'ch11-08-02-02', 'ch11-08-03-01', 'ch11-08-03-02', 'ch11-08-04-02'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def verify_scene(record, path_key, sha_key):
    if record.get(path_key) and sha(ROOT / record[path_key]) != record[sha_key]:
        raise ValueError('scene changed: ' + record[path_key])


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if sha(SOURCE) != SOURCE_SHA:
        raise ValueError('v034 changed')
    data = read(SOURCE)
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch11')
    documents = {}
    generated = {}
    sources = [{'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA}]
    for section, title, path, count in SPECS:
        document = read(ROOT / path)
        documents[section] = document
        if count is not None and len(document['steps']) != count:
            raise ValueError('unexpected steps: ' + path)
        if not document['steps']:
            raise ValueError('no evidence: ' + path)
        verify_scene(document, 'demonstrationScene', 'demonstrationSceneSha256')
        verify_scene(document, 'scene', 'sceneSha256')
        own = [lesson_step(step, section, document['limitations'], 'inner') for step in document['steps']]
        generated[section] = own
        chapter['steps'].extend(own)
        chapter['sections'].append({'id': section, 'title': title, 'track': 'optional'})
        sources.append({'path': path, 'sha256': sha(ROOT / path)})
        for start in document.get('startingScenes', []):
            verify_scene(start, 'path', 'sha256')
        starts = document.get('startingScenes', [])
        if not starts and isinstance(document.get('startingScene'), dict):
            starts = [document['startingScene']]
        for start in starts:
            verify_scene(start, 'path', 'sha256')
            own[0]['context'] += ' 起始副本：' + start['path'] + '（SHA-256 ' + start['sha256'] + '）。'
    # The handmade profile photographs and the follow-on thread use two runs.
    profile = documents['11-13']
    generated['11-13'][0]['context'] += ' 原始場景：' + profile['sourceScene'] + '；請另存副本。'
    generated['11-14'][0]['context'] += ' 外牙示範實際來源是 GUI v004；13 步輪廓照片來自另一次 GUI v005，同座標但不是同一檔案或場次。'
    hardware_path = ROOT / 'learning/hardware-selection-v001.json'
    hardware = read(hardware_path)
    sources.append({'path': hardware_path.relative_to(ROOT).as_posix(), 'sha256': sha(hardware_path)})
    steps = {s['id']: s for s in chapter['steps']}

    def ready(identifier, title, goal, section, evidence_index, actions, success, limits):
        step = steps[identifier]
        if step.get('track') != 'pending':
            raise ValueError('unexpected availability: ' + identifier)
        step.pop('track')
        step.update(title=title, goal=goal, context='先依本章 ' + section + ' 的逐步實拍操作，保留原檔；現在只做本檢查點。',
                    actions=actions, success=success, sourceSteps=[], evidenceStatus='existing_demo',
                    limitations=limits,
                    figures=copy.deepcopy(generated[section][evidence_index]['figures']),
                    detail={'steps': actions, 'why': '示範與來源已有記錄，現在可核對自己的副本；此步仍須學員明確完成確認。'})

    ready('ch11-08-02-02', '核對手工輪廓與外牙', '依原生 mesh 輪廓和 Screw 流程建立幾何草案。', '11-14', -1,
          ['在自己的外牙副本中核對輪廓來源與 Screw 設定：Z 軸、360°、每圈位移 1 mm、4 圈、32 段。',
           '核對另存與重開結果，記下約 12 × 12 × 4.8 mm 的外框及限制。'],
          '能指出三點輪廓、數值輸入與外牙版本來源，並記錄實際讀值。',
          ['本路線為無 CAD 尺寸約束的原生 mesh；非 ISO 牙型。零候選或局部表面取樣不能證明所有自交或製造合格。'])
    ready('ch11-08-03-01', '建立匹配盒側保護蓋', '由已提供的起始副本做徑向間隙與端隙差集。', '11-15', 12,
          ['依 11-15 開啟起始副本並確認帽體與刀具名稱，沿 Difference 流程另存。',
           '保留 v001 零端隙對照與 v002 端隙版本，確認原平面上蓋仍保留。'],
          '盒側帽有內牙及端部 relief，來源與兩版檔案可追溯。',
          ['刀具及毛坯為程式準備；它是盒側保護蓋，原平面上蓋採另一路五金固定。徑向與軸向均為試驗值。'])
    ready('ch11-08-03-02', '核對保護蓋網格與試驗間隙', '分清徑向、直徑與軸向端隙及有限數位檢查。', '11-15', -1,
          ['核對帽體版本與讀值；記錄徑向展開 0.2 mm、名義直徑差 0.4 mm、名義中心端隙 0.2 mm。',
           '查閱非流形、射線及離散旋轉檢查，說明它們沒有涵蓋的範圍。'],
          '可分別指出兩種間隙與檢查範圍，未將數位結果填成實體合格。',
          ['細長三角面仍存在；部分射線差異原因未證。11 個正向離散姿態不代表連續旋合或實際試配。'])
    ready('ch11-08-04-02', '核對已選 M3 柱與蓋孔', '以已選螺絲及熱熔螺母的來源資料建立名義幾何草案。', '11-16', -1,
          ['對照 ETTINGER 001.16.342 M3×10 與 ruthex RX-M3x5.7 的資料，核對柱孔、蓋穿孔及版本。',
           '核對柱孔名義 Ø4、深 9 mm、蓋孔名義 Ø3.4 mm，分清原廠建議與自訂試驗值；另記螺絲末端的名義空間。'],
          '柱、肋及蓋孔有實際場景及來源讀值，材料與安裝試驗仍待進行。',
          hardware['limitations'])
    steps['ch11-08-04-01']['actions'] = ['記錄已選 ETTINGER 001.16.342（M3×10、A2）與 ruthex RX-M3x5.7，核對原廠連結；材料、熱熔溫度與扭矩待定。']
    steps['ch11-08-04-01']['detail']['steps'] = steps['ch11-08-04-01']['actions']
    steps['ch11-08-04-01']['limitations'] = ['五金選型已由學員委託選定，實際購買、安裝與性能尚未驗證。']
    for section in chapter['sections']:
        if section['id'] == '11-05':
            section.pop('track', None)
            section['title'] = '匹配內牙對件（盒側保護蓋）'
    order = ['11-01', '11-02', '11-03', '11-04', '11-13', '11-14', '11-11', '11-12',
             '11-05', '11-15', '11-06', '11-10', '11-16', '11-07', '11-08', '11-09']
    chapter['sections'].sort(key=lambda item: order.index(item['id']))
    chapter['detailNote'] = '11-13／14 為原生 mesh 手工輪廓與外牙，11-15 為匹配盒側保護蓋，11-16 為已選 M3 五金的柱與蓋孔；各有實際畫面與讀值。預建工具和 GUI 動作分列，實體試驗尚未執行。'
    data['version'] = 'v035 · 2026-10-28'
    data['description'] += ' v035 補齊手工 mesh 輪廓、續作外牙、匹配盒側保護蓋及已選 M3 五金柱孔；4 個幾何檢查點已有示範，實體列印與試配仍待進行。'
    data['sourceVersions'] += sources
    data['contentReview']['reviewV035'] = {
        'reviewedOn': '2026-10-28', 'scope': '採既有盒側外牙的匹配保護蓋，原平面上蓋走金屬固定分支。原生 mesh 不冒稱 CAD 尺寸約束草圖。',
        'contentNowAvailable': sorted(READY), 'learnerProgressChanged': False,
        'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None,
        'qualifiedClearance': None, 'qualifiedStrength': None,
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(sha(OUTPUT))


if __name__ == '__main__':
    main()
