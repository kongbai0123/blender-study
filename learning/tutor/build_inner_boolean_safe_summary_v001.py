"""由本輪 run 建立不含絕對路徑／Recent 資訊的逐步摘要；不改原始證據。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'learning/evidence/08/2026-10-28-inner-boolean-trial-v003'
OUTPUT=RUN/'safe-summary-v001.json'
SCENE_SHA='a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80'
SOURCE_SHA='dadb268dce5836f46d877d90a7ca0113de5280790f6d9611ce9a551422c4c700'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build():
    run=json.loads((RUN/'run.json').read_text(encoding='utf8'))
    status=json.loads((RUN/'runner-status.json').read_text(encoding='utf8'))
    audit=json.loads((RUN/'independent-audit-v001.json').read_text(encoding='utf8'))
    if status.get('status')!='completed' or len(run.get('records',[]))!=7 or not all(audit['checks'].values()):raise ValueError('run 或獨立抽樣複核不符')
    items=[]
    for record in run['records']:
        image=RUN/record['file'];digest=sha(image)
        if digest!=record['sha256']:raise ValueError('原圖 hash 不符')
        items.append({'sequence':record['seq'],'action':record['action'],
                      'path':image.relative_to(ROOT).as_posix(),'sha256':digest,'observed':record['observed']})
    checks={}
    for name in ('applied','saved','reopened'):
        detail=json.loads((RUN/(name+'-verification.json')).read_text(encoding='utf8'))
        if not all(detail['checks'].values()):raise ValueError('數位驗證失敗：'+name)
        checks[name]=detail
    scene=RUN/'demo-files/u08_inner_boolean_trial_v003.blend'
    if sha(scene)!=SCENE_SHA:raise ValueError('示範場景 hash 不符')
    return {'schemaVersion':1,'title':'程式預建外牙工具與 GUI 差集內牙試塊草案',
            'method':'來源外牙由程式建網；本輪 GUI 新增並縮放試塊、設定及套用 Boolean Difference/Exact、存檔與重開。檔案對話欄由程式填入。',
            'sourceSha256':SOURCE_SHA,'sourceScene':'learning/evidence/08/2026-10-28-closed-external-thread-probe-v001/demo-files/u08_closed_external_thread_probe_v001.blend',
            'outputScene':scene.relative_to(ROOT).as_posix(),'outputSceneSha256':SCENE_SHA,
            'steps':items,'verification':checks,'independentAudit':audit,
            'limitations':['16×16×3 mm 試塊並非盒蓋','來源外牙由程式生成、端部不完整，未設配合間隙',
                           '非流形0和局部射線不能證明無自交或可列印','材料、標準、切片、實印、量測、試配與強度待定'],
            'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
def main():
    if OUTPUT.exists():raise FileExistsError('拒絕覆寫既有摘要')
    result=build();OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(sha(OUTPUT))
if __name__=='__main__':main()
