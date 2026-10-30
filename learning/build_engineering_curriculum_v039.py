"""Promote smoke-verified chapter pages; preserve the legacy renderer and stable step IDs."""
import copy,hashlib,json,re
from pathlib import Path
from chapter_page_frontend_v001 import make_assets

ROOT=Path(__file__).resolve().parent.parent
WEB=ROOT/'learning/web'
SOURCE=WEB/'engineering-curriculum-v038.json'
SOURCE_SHA='7f0150607d736a6bbd2b43767fba09ffb4f3bbc8aaf6228a4c08aec54dddf4df'
OUTPUT=WEB/'engineering-curriculum-v039.json'
PRODUCTION=ROOT/'learning/drafts/ux-chapter-01-v001/checks/production'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def data_file(p):
    t=p.read_text('utf8');return json.loads(t[t.index(' = {')+3:].strip().rstrip(';'))

def build():
    if OUTPUT.exists() or (WEB/'legacy.html').exists():raise FileExistsError('refusing to overwrite an existing release')
    if sha(SOURCE)!=SOURCE_SHA:raise ValueError('v038 source changed')
    protected=read(PRODUCTION.parent/'protected-before.json')
    for name in ['learning/manage.py','learning/server.py','learning/web/index.html']:
        if sha(ROOT/name)!=protected[name]:raise ValueError('concurrent change: '+name)
    smoke=read(PRODUCTION/'live-v015/results.json')
    if smoke['sections']!=85 or smoke['passed']!=85:raise ValueError('complete draft smoke required before promotion')
    verified={r['section']:r for r in smoke['results']}
    sections={};sources=[]
    for n in range(1,13):
        folder=ROOT/f'learning/drafts/ux-chapter-{n:02}-v001'
        for p in sorted((folder/'sections').glob('*.js')):
            s=data_file(p);r=verified[s['id']]
            if r['dataSha256']!=sha(p) or r['pageSha256']!=sha(folder/'index.html'):raise ValueError('smoke source drift: '+s['id'])
            sections[s['id']]=s;sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    t=(ROOT/'learning/drafts/ux-chapter-01-v001/course-outline.js').read_text('utf8')
    outline=json.loads(t[t.index('=')+1:].strip().rstrip(';'))
    data=read(SOURCE);old=copy.deepcopy(data)
    ids=[c['stepId'] for s in sections.values() for c in ([s['prep']] if s.get('prep') else [])+s['steps']]
    expected=[s['id'] for ch in data['chapters'] for s in ch['steps'] if s.get('track') not in ['reference','appendix','optional','pending']]
    if len(ids)!=243 or len(set(ids))!=243 or set(ids)!=set(expected):raise ValueError('stable mainline IDs changed')
    def verify(x):
        if isinstance(x,list):
            for v in x:verify(v)
        elif isinstance(x,dict):
            if x.get('path','').startswith('evidence/') and 'size' in x:
                p=ROOT/'learning'/x['path']
                if sha(p)!=x['sha256']:raise ValueError('original image changed: '+x['path'])
            for v in x.values():verify(v)
    verify(list(sections.values()))
    for section in sections.values():
        if not section.get('prep') and not section['steps']:
            section['keyPoint']='本節保留原版完整教材；請從下方入口查看操作、實拍與既有紀錄。'
            section['scope']='選修、附錄或實體待執行項目沿用原版呈現；不因頁面改版變更確認與合格判定。'
    data['chapterPages']={'schemaVersion':1,'outline':outline,'sections':sections,'sources':sources,
        'scope':'70主線小節頁、243小步；15個選修／附錄／實體待執行節保留原版完整教材入口。',
        'progress':'Read existing learner engineering events; no automatic confirmations or new progress store.'}
    data['version']='v039 · 2026-10-30'
    data['description']+=' v039接入已核對的整節式主線教材頁，原版教材及進度ID保留。'
    data['sourceVersions'].append({'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA})
    data.setdefault('contentReview',{})['chapterPagesV039']={'sections':85,'mainlineSteps':243,'smoke':'learning/drafts/ux-chapter-01-v001/checks/production/live-v015/results.json','physicalPrint':None,'physicalMeasurement':None,'physicalFit':None}
    assert data['chapters']==old['chapters'] and data['id']==old['id']
    html,css,script=make_assets((ROOT/'learning/drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
    # All preparation/validation above is read-only. Promote only after the draft smoke passes.
    (WEB/'legacy.html').write_bytes((WEB/'index.html').read_bytes())
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (WEB/'index.html').write_bytes(html.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
    (WEB/'chapter-pages-v001.css').write_text(css,encoding='utf8')
    (WEB/'chapter-pages-v001.js').write_text(script,encoding='utf8')
    p=ROOT/'learning/manage.py';b=p.read_bytes();needle=b'ENGINEERING_CURRICULUM = LEARNING / "web" / "engineering-curriculum-v038.json"';assert b.count(needle)==1;p.write_bytes(b.replace(needle,needle.replace(b'v038',b'v039')))
    p=ROOT/'learning/server.py';b=p.read_bytes();needle=b'("/", "/index.html", "/app.js", "/app.css", "/engineering-path.js")';assert b.count(needle)==1;p.write_bytes(b.replace(needle,b'("/", "/index.html", "/legacy.html", "/chapter-pages-v001.js", "/chapter-pages-v001.css", "/app.js", "/app.css", "/engineering-path.js")'))
    print(json.dumps({'version':data['version'],'sections':len(sections),'mainlineSteps':len(ids),'sha256':sha(OUTPUT)},ensure_ascii=False))

if __name__=='__main__':build()
