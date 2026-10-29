"""Describe learning prerequisites separately from file/geometry continuity."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-path-v005.json'
SOURCE_SHA='57cc0206dedeec11888e51ab2ac1703f53ba99ae8b993fffdb9d933748af18aa'
OUTPUT=ROOT/'learning/web/engineering-path-v006.json'


def main():
    if OUTPUT.exists():raise FileExistsError('refusing to overwrite '+OUTPUT.name)
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('v005 changed')
    data=json.loads(SOURCE.read_text(encoding='utf8'))
    for previous,chapter in zip(data['chapters'],data['chapters'][1:]):
        chapter['prerequisiteLabel']='先備學習'
        chapter['prerequisiteSummary']='第 '+previous['number']+' 章 '+previous['title']+' 的觀念與操作；本章模型依各節指定的起始副本，不將上一章最後開啟的檔案視為通用起點。'
    chapter=next(c for c in data['chapters'] if c['id']=='ch09')
    chapter['prerequisiteSummary']='第08章參數連動作觀念參照；本章定位榫與燕尾使用原盒／既有蓋的60×40×30 mm獨立固定尺寸分支，未與參數盒自動連動。'
    chapter['notes'].append('題目另附定位柱／蓋穿孔及燕尾分支各自的工程圖，不以其中一圖替代另一分支。')
    chapter=next(c for c in data['chapters'] if c['id']=='ch10')
    chapter['notes'].append('整盒卡扣／蓋裙與獨立三試片是不同模型分支；各自有來源網格工程圖與幾何長度定義。')
    chapter=next(c for c in data['chapters'] if c['id']=='ch08')
    chapter['notes'].append('跨節先保存並重開指定基準；第08-08的70×40超界測試已另用同尺寸副本重演，已登記檔案後續須另存未登記版本。')
    data['version']='v006 · 2026-10-29'
    data['previousVersion']={'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA}
    data['contentReview']['revisionV006']={'reviewedOn':'2026-10-29','scope':'修正先備學習與檔案分支銜接；對應教材v037與本輪逐項審查，無學員或實體完成變更。','learnerCompletionChanged':False}
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__=='__main__':main()
