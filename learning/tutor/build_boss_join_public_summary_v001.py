"""匯出不含絕對路徑與 Recent 清單的盲孔柱接合示範摘要；不覆寫原紀錄。"""
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'learning/evidence/08/2026-10-28-boss-box-join-trial-v002'
OUT=RUN/'public-summary-v001.json'
EXPECTED_SCENE='66f1f79fbf509573426b055f6ad5cee25ee7d21e6b23eced613e0e77f00ad4b4'

def fingerprint(path):
    data=path.read_bytes()
    return {'path':path.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':sha256(data).hexdigest()}

def main():
    if OUT.exists():raise FileExistsError('拒絕覆寫既有摘要')
    run=json.loads((RUN/'run.json').read_text(encoding='utf-8'))
    summary=json.loads((RUN/'trial-summary.json').read_text(encoding='utf-8'))
    results=[json.loads((RUN/(label+'-verification.json')).read_text(encoding='utf-8')) for label in ('union','saved','reopened')]
    if len(run.get('records',[]))!=7 or not all(all(v['checks'].values()) for v in results):raise ValueError('原始操作或幾何檢查不完整')
    scene=fingerprint(RUN/'demo-files/u08_box_boss_trial_v001.blend')
    if scene['sha256']!=EXPECTED_SCENE:raise ValueError('結果場景 hash 與完成證據不符')
    screenshots=[]
    for record in run['records']:
        img=fingerprint(RUN/record['file'])
        if img['sha256']!=record['sha256']:raise ValueError('原圖 hash 不符')
        screenshots.append({'seq':record['seq'],'slug':record['slug'],'action':record['action'],
                            'observed':record['observed'],'image':img,'width':record['width'],'height':record['height']})
    data={'schemaVersion':1,'id':'boss-box-join-public-summary-v001',
          'description':'獨立 Blender 原盒中央盲孔柱接合；數位幾何示範草案。',
          'blenderVersion':run['blender'],'buildHash':run['buildHash'],
          'sourceScene':{'path':'learning/evidence/08/2026-10-27-lesson08-boss-draft-v002/demo-files/u08_blind_boss_draft_v001.blend',
                         'sha256':'4df306ac6b7e3f57108cb0221fad62480ca47c80f77d5ccd3e91632a6d5c7320'},
          'scene':scene,'screenshots':screenshots,'operandAttempts':summary['operandAttempts'],
          'sourceMethod':'柱本身由前次程式建立；本次顯示、平移、Boolean 及另存重開為 Blender 視窗模擬事件。',
          'failedAttempt':'v001 operand 未選入而中止、未存成果；v002 首次亦為空值，GUI 重選一次後成功。',
          'geometry':results,'limitations':['中央柱僅為幾何草案；沒有對應蓋孔與裝配驗證。',
                       '32 邊形 8／4 mm 為頂點對頂點，非正式螺絲或嵌件孔徑。',
                       '材料、五金、列印、量測、配合及強度均待定；射線與單殼不是完整幾何或實體合格檢查。'],
          'publicationStatus':'去除絕對路徑與 Recent 清單的衍生摘要；發布前仍需審查來源、隱私及授權。'}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(fingerprint(OUT),ensure_ascii=False))

if __name__=='__main__':main()
