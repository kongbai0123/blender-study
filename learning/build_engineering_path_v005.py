"""Reflect completed digital lessons and ready field protocols, not learner progress."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'learning/web/engineering-path-v004.json'
SOURCE_SHA = '956aaf67f86cc90a5aa864fe559221985244f66d3f5850adf52d6fb6528e12ed'
OUTPUT = ROOT / 'learning/web/engineering-path-v005.json'


def main():
    if OUTPUT.exists():
        raise FileExistsError('refusing to overwrite ' + OUTPUT.name)
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('v004 changed')
    data = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    labels = {
        'ch01': '操作教材與目標零件題圖已備妥',
        'ch02': '公差觀念與空白量測紀錄已備妥',
        'ch03': '毫米盒蓋與編輯模式已有實拍',
        'ch04': '材質、渲染示範與實際場景題圖已備妥',
        'ch05': '六孔試片已有幾何與讀值；實體結果空白',
        'ch06': '匯出示範與現場方法已備妥；實體結果空白',
        'ch07': '隔離安裝與約束草圖已有實拍',
        'ch08': '尺寸連動、防護與版本方法已有示範',
        'ch09': '定位榫與燕尾已有示範；實體結果空白',
        'ch10': '卡扣與對照試片已有示範；強度與試配未驗證',
        'ch11': 'CAD 約束、幾何與六件 STL 已補齊；實體試驗待進行',
        'ch12': '尺寸鏈、交付方法與安全渲染副本已備妥',
    }
    for c in data['chapters']:
        c['availability'] = 'digital_lessons_and_field_protocols_ready'
        c['availabilityLabel'] = labels[c['id']]
    ch11 = next(c for c in data['chapters'] if c['id'] == 'ch11')
    ch11['practice'] = [
        '分別練習原生 mesh 三點輪廓與 CAD 真尺寸約束；CAD 轉 mesh 的副本不再連動。',
        '沿用盒側外牙與匹配側帽、已選 M3 螺絲與嵌件的四柱分支。',
        '實際匯出六件 STL、核對尺寸與重匯入；側盒和側帽先保存三角化修訂副本。',
    ]
    ch11['shortcuts'][0]['status'] = '11-17 為六件 STL；11-18 為真約束；11-19 為開口 Screw 銜接。原始 CAD 重開有工具警告，限制逐步標明；數位檢查不代實體合格。'
    ch11['notes'] = [
        '原生 mesh 與 CAD 約束為兩條路線；Convert Mesh 後的副本不再與原 CAD 尺寸連動。',
        '側盒／側帽修訂三角化改變局部表面，保留原檔；STL 尺寸及零非流形不證明可印或可旋合。',
        '0.4 mm 名義直徑差與 0.2 mm 端隙只作試驗；材料、實體量測、試配與強度均待驗證。',
    ]
    ch12 = next(c for c in data['chapters'] if c['id'] == 'ch12')
    ch12['references'][0]['label'] = '量測彙整方法（現場結果空白）'
    ch12['references'][1]['label'] = '補償方法（實測支持後才套用）'
    ch12['references'][2]['label'] = '組裝與版本追溯方法（實體組裝空白）'
    data['environment']['summary'] = '隔離 Blender 5.2.1＋CAD Sketcher 0.32.1 已有安裝實拍、草圖約束、盒蓋 Driver 與防護面板示範；檔案欄位和起始條件的程式準備均分列。CAD 約束還原版重開出現工具警告，需依步驟限制核對；不是學員的安裝或完成紀錄。'
    data['version'] = 'v005 · 2026-10-28'
    data['previousVersion'] = {'path': SOURCE.relative_to(ROOT).as_posix(), 'sha256': SOURCE_SHA}
    data['contentReview']['revisionV005'] = {
        'scope': '對應教材 v036 的數位補課與現場空白方法，不聲稱所有歷史圖片重新目視、不確認學員進度。',
        'learnerCompletionChanged': False, 'physicalPrint': None, 'physicalMeasurement': None, 'physicalFit': None,
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
