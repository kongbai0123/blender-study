"""Correct image/operation correspondence without rewriting the released v040."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from build_engineering_curriculum_v040 import figure, record_figure
from chapter_page_frontend_v003 import make_assets

ROOT = Path(__file__).resolve().parents[1]
L = ROOT/'learning'
WEB = L/'web'
SOURCE = WEB/'engineering-curriculum-v040.json'
SOURCE_SHA = '39afb9cf02fcdc659de07e7d8535aa9aa5692be9fbc63e9c54c4c276d8b92c59'
PATCH = L/'patches/2026-10-30-v040-correspondence-audit-v001'
CANDIDATE = PATCH/'candidate'
RUN = L/'evidence/chapters/2026-10-30-efficient-plate-coordinates-v002'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')


def build():
    assert sha(SOURCE)==SOURCE_SHA
    status=read(RUN/'runner-status.json')
    assert status['status']=='completed' and status['workspacesUnchanged']
    checks=read(RUN/'verification.json')['checks']
    assert len(checks)==4 and all(c['passed'] for c in checks)
    raw=read(RUN/'run.json')
    records={r['slug']:r for r in raw['records']}
    assert len(records)==4
    # A portable readback derivative; the raw run and workspace/Recent inventories stay local.
    summary={'kind':'redacted_public_derivative','redacted_public_derivative':True,
             'originalAvailableInPublicPackage':False,
             'source':{'path':(RUN/'run.json').relative_to(ROOT).as_posix(),'sha256':sha(RUN/'run.json')},
             'blender':raw['blender'],'records':[{k:r[k] for k in ['step','slug','action','observed','file','sha256','width','height']}
                                              for r in records.values()],
             'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None}
    summary_path=RUN/'operation-summary-v001.json'
    payload=encoded(summary)
    if summary_path.exists():
        assert summary_path.read_bytes()==payload
    else:
        summary_path.write_bytes(payload)
    source={'path':summary_path.relative_to(ROOT).as_posix(),'sha256':sha(summary_path)}
    data=read(SOURCE)
    data['chapterPages']['evidenceRoles']={
        'version_reference':{'label':'版本來源參考','description':'本圖供核對場景來源；不證明已完成網頁登記或文件記錄。'},
        'digital_preparation':{'label':'數位準備／來源參考','description':'供核對名義幾何與來源；不是表格、紙上或現場作業的完成證據。'},
        'physical_preparation':{'label':'實體操作前的數位參考','description':'尚未列印、實體量測或試配；結果欄保持空白。'},
        'related_reference':{'label':'相關場景參考','description':'不是本步操作的獨立實拍；依正文另行執行並記錄。'},
        'shortcut_verification':{'label':'獨立快捷試驗','description':'依圖說核對試驗座標及階段，不直接當作完成本節的證據。'},
        'direct_operation':{'label':'本步操作實拍','description':'操作與讀值來自同場；不代表學員完成或實體合格。'},
    }
    mapping={
        'ch05-05-03-03':['first-cutter'],
        'ch05-05-03-04':['six-equal','first-three-widths'],
        'ch05-05-03-05':['six-varied'],
    }
    titles={'first-cutter':'第一件尺寸與位置','six-equal':'先完成等距複製',
            'first-three-widths':'再改第2、3件','six-varied':'六件不同孔寬'}
    page=data['chapterPages']['sections']['05-02']
    old_steps={s['id']:s for c in data['chapters'] for s in c['steps']}
    for card in page['steps']:
        sid=card['stepId']
        if sid not in mapping:
            continue
        fs=[];raw_figures=[];readings=[];artifacts=[]
        for slug in mapping[sid]:
            record=records[slug]
            f=record_figure(RUN,record,record['action']+' 本圖與正文使用相同座標。','direct_operation')
            raw_figures.append(f)
            converted=figure(f);converted['tab']=titles[slug];fs.append(converted)
            readings.append({'kind':'readback','label':titles[slug],'value':record['observed']})
            scene=record['observed']['savedScene']
            assert sha(ROOT/scene['path'])==scene['sha256']
            artifacts.append({**scene,'label':titles[slug]+'：助教場景檢查點'})
        card.pop('figure',None)
        card['figures']=fs;card['readings']=readings
        card['cautions']=[x for x in card.get('cautions',[]) if '原實拍保留逐件新增' not in x]
        card['cautions'].append('本次示範以程式設定毫米單位、隱藏Camera/Light及存檔；新增、複製、選取與尺寸輸入使用實際模擬事件。Plate為已隱藏的空白板，本階段尚未執行Boolean。')
        card['references']=[{'path':source['path'].removeprefix('learning/'),'label':'同場操作與讀值摘要'},
                            *[{'path':a['path'].removeprefix('learning/'),'label':a['label']} for a in artifacts]]
        step=old_steps[sid]
        step['figures']=raw_figures
        step['demonstration']={'recordId':mapping[sid][-1],'source':source,
            'scope':'與正文相同座標的獨立Blender同場操作；資料準備與存檔由Python執行，幾何與選取使用實際事件。尚未對Plate執行Boolean。',
            'readings':copy.deepcopy(readings),'figures':copy.deepcopy(raw_figures)}
        step.setdefault('artifacts',[]).extend([dict(source,label='同場操作與讀值摘要'),*artifacts])
        step.setdefault('limitations',[]).append('v041快捷重演與正文同為X=-35,-21,-7,7,21,35mm、Y=2mm；v040的X=0原理試驗留作歷史。')
    # Naming and active-object checks prevent Camera/Light being edited by mistake.
    actions={
        'ch05-05-03-03':['F3搜尋Add Cube，F2改名Cut_01；N輸入Dimensions <code>10.1mm</code>、<code>10.1mm</code>、<code>8mm</code>，F3搜尋Apply Scale。',
                         '用G X <code>-35mm</code>、G Y <code>2mm</code>到中心(-35,2,0)mm，核對作用中物件為Cut_01後才開始複製。'],
        'ch05-05-03-04':['只選Cut_01，Shift+D → X → <code>14mm</code> → Enter，立刻Shift+R四次先完成六件等距副本。',
                         '複製後逐一核對Cut_01.001／.002（X=-21／-7mm），再把N的X/Y尺寸改為<code>10.2mm</code>／<code>10.3mm</code>，Z維持8mm並Apply Scale。'],
        'ch05-05-03-05':['逐一選Cut_01.003～.005，先核對作用中物件及X位置，再把N的X/Y尺寸設為<code>10.4mm</code>、<code>10.5mm</code>、<code>10.6mm</code>，Z維持8mm並Apply Scale。',
                         '核對六件中心X=-35,-21,-7,7,21,35mm、Y=2mm；勿選到Camera／Light。各件為獨立網格，不用Alt+D，也不在改尺寸後以Shift+R複製。'],
    }
    import re
    for card in page['steps']:
        if card['stepId'] in actions:
            card['actions']=actions[card['stepId']]
            step=old_steps[card['stepId']]
            step['actions']=[re.sub('<[^>]+>','',a) for a in card['actions']]
            step.setdefault('detail',{})['steps']=list(step['actions'])
    intents={
        'ch05-05-03-03':('建立第一件切割體','Object Mode · Plate已隱藏 · 建立Cut_01並核對尺寸及位置。',
                         '在3D Viewport用F3 Add Cube；N的Item可直接填Dimensions及核對Location。',
                         '尺寸與Scale','輸入Dimensions後再Apply Scale；Scale1不是尺寸本身。'),
        'ch05-05-03-04':('先複製六件，再調第2、3件','Object Mode · Cut_01已選取 · 先完成等距複製再改寬度。',
                         '先Shift+D X14mm，再立即Shift+R四次；複製完才選Cut_01.001及.002改寬。',
                         '先複製，後改尺寸','不要在改尺寸後把Shift+R當成複製指令。'),
        'ch05-05-03-05':('調整第4～6件並核對六件','Object Mode · 六件已建立 · 第2、3件已改寬，接著調第4～6件。',
                         '先在Outliner核對Cut_01.003～.005，N的Location X應為7、21、35mm，再改Dimensions。',
                         '核對作用中物件','不要選到Camera／Light；輸入尺寸前核對物件名稱及Location X。'),
    }
    for card in page['steps']:
        if card['stepId'] in intents:
            title,lead,locate,pitfall,explanation=intents[card['stepId']]
            card.update(title=title,lead=lead,locate=locate,pitfalls=[{'title':pitfall,'text':explanation}])
            step=old_steps[card['stepId']]
            step['title']=title;step['context']=lead
            step['goal']=title+'，以本步相同座標的實拍與讀值核對。'
            step['detail']['why']=explanation
    data['version']='v041 · 2026-10-30'
    data['sourceVersions'].append({'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA})
    data['contentReview']['correspondenceV041']={'correctedSteps':list(mapping),
        'referencePhotosReviewed':30,'referencePhotosAreActionCompletion':False,
        'sameCoordinatesRun':source,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None}
    assert data['id']==read(SOURCE)['id']
    return data


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--promote',action='store_true');args=parser.parse_args()
    data=build();CANDIDATE.mkdir(exist_ok=True)
    h,c,j=make_assets((L/'drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
    files={}
    for name,text in [('index.html',h),('chapter-pages-v001.css',c),('chapter-pages-v001.js',j)]:
        eol='\r\n' if b'\r\n' in (WEB/name).read_bytes() else '\n'
        files[name]=text.replace('\r\n','\n').replace('\n',eol).encode('utf8')
    files['engineering-curriculum-v041.json']=encoded(data)
    if args.promote:
        if (WEB/'engineering-curriculum-v041.json').exists():raise FileExistsError('refuse overwrite v041')
        baseline=read(PATCH/'before.json')
        for name in ['learning/manage.py','learning/web/index.html','learning/web/chapter-pages-v001.js','learning/web/chapter-pages-v001.css']:
            assert sha(ROOT/name)==baseline[name],name
        proof=read(PATCH/'smoke/results.json');assert proof['sections']==proof['passed']==85
        for name,payload in files.items():
            assert proof['releaseHashes'][name]==hashlib.sha256(payload).hexdigest(),name
            (WEB/name).write_bytes(payload)
        path=L/'manage.py';raw=path.read_bytes();assert raw.count(b'engineering-curriculum-v040.json')==1
        path.write_bytes(raw.replace(b'engineering-curriculum-v040.json',b'engineering-curriculum-v041.json'))
    else:
        for name,payload in files.items():(CANDIDATE/name).write_bytes(payload)
    print(json.dumps({'version':data['version'],'promoted':args.promote}))


if __name__=='__main__':main()
