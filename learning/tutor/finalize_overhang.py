"""Final evidence/API/browser-publication checks for the 07-03 v001 example."""
import json
import struct
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import import_run as importer
import publish_overhang as pub

RUN_ID='2026-10-25-lesson07-overhang-demo-v001'
REL='learning/evidence/07/'+RUN_ID
ROOT=pub.PROJECT
RUN=ROOT/REL

def jpeg_size(data):
    assert data[:2]==b'\xff\xd8'
    i=2
    while i<len(data):
        if data[i]!=255:
            i+=1
            continue
        while data[i]==255:
            i+=1
        marker=data[i]
        i+=1
        if marker in (1,216,217) or 208<=marker<=215:
            continue
        length=struct.unpack('>H',data[i:i+2])[0]
        if marker in (192,193,194,195):
            h,w=struct.unpack('>HH',data[i+3:i+7])
            return w,h
        i+=length
    raise ValueError('JPEG dimensions not found')

def http_exact(path):
    rel=path.relative_to(ROOT).as_posix()
    url='http://127.0.0.1:8766/files/'+urllib.parse.quote(rel,safe='/')
    with urllib.request.urlopen(url,timeout=20) as response:
        data=response.read()
        status=response.status
        disposition=response.headers.get('Content-Disposition')
    assert status==200 and data==path.read_bytes(),rel
    result=dict(path=rel,status=status,sha256=pub.digest(path),bytes=len(data),exactBytes=True)
    if data[:8]==b'\x89PNG\r\n\x1a\n':
        result.update(zip(('width','height'),struct.unpack('>II',data[16:24])))
        result['originalPixelsPreserved']=True
    if path.suffix=='.blend':
        assert disposition and 'attachment' in disposition
        result['contentDisposition']=disposition
    return result

def main():
    baseline=pub.read(RUN/'publication-baseline-v001.json')
    run=pub.read(RUN/'run.json')
    verification=pub.read(RUN/'verification.json')
    catalog=pub.read(ROOT/'learning/catalog.json')
    progress=pub.read(ROOT/'learning/progress.json')
    lesson_steps={s['id']:s for l in catalog['lessons'] if l['id']=='07' for s in l['steps']}
    importer._validate_lesson07_overhang(run,RUN,importer.RUNS[RUN_ID])
    importer._validate_records(run,RUN,importer.RUNS[RUN_ID],lesson_steps)
    manifest=pub.read(RUN/'print-orientation-manifest-v001.json')
    manifest['publication_audits']=[dict(path=REL+'/'+name,sha256=pub.digest(RUN/name)) for name in ['independent-audit-v001.json','automated-checks-v001.json']]
    pub.write(RUN/'print-orientation-manifest-v001.json',manifest)
    assert pub.digest(ROOT/'learning/progress.json')==baseline['progress_sha256']
    changed=[s['id'] for l in catalog['lessons'] for s in l['steps'] if pub.fingerprint(s)!=baseline['steps'][s['id']]]
    assert changed==['07-03'] and len(baseline['steps'])==52
    with urllib.request.urlopen('http://127.0.0.1:8766/api/bootstrap',timeout=20) as response:
        api=json.load(response)
    assert api['catalog']==catalog and api['progress']==progress
    assert progress['revision']==5 and not progress['fileVersions']
    proofs=[]
    for role in ['overview','comparison','conditions']:
        path=ROOT/'learning/evidence/ui'/(RUN_ID+'-final-'+role+'.jpg')
        data=path.read_bytes()
        w,h=jpeg_size(data)
        assert (w,h)==(304,848)
        proofs.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=pub.digest(path),bytes=len(data),width=w,height=h,pixelEdits=False,role=role,fileRecordedAt=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()))
    ui_path=ROOT/'learning/evidence/ui'/(RUN_ID+'.json')
    ui=dict(recordedAt=datetime.now(timezone.utc).isoformat(),url='http://127.0.0.1:8766/',browser='ChatGPT in-app browser',lesson='07',step='07-03',captureMethod='Browser getScreenshot original JPEG bytes; no pixel modifications',screenshots=proofs,sourceFiles=[dict(path=path,sha256=pub.digest(ROOT/path)) for path in ['learning/catalog.json','learning/web/app.js','learning/web/app.css']],verifiedVisibleText=['列印方向與 Overhang 檢查','材料／允許應變：待定','11 面／1057.534 mm²','1 面／12 mm²','focus-v002','支撐需求仍待切片'],learnerCompletionConfirmed=False,progressRevision=5,progressSha256=baseline['progress_sha256'])
    pub.write(ui_path,ui)
    checks=pub.read(RUN/'publication-checks-v001.json')
    for item in checks['images']:
        assert pub.digest(ROOT/item['path'])==item['sha256']
    checks['downloads']=[http_exact(ROOT/item['path']) for item in checks['downloads']]
    focus=ROOT/'learning/evidence/07/2026-10-25-lesson07-overhang-focus-v002'
    checks['supplementaryImages']=[http_exact(focus/'07-03-06-elevated-ledge-closeup.png')]
    checks['supplementaryReadback']=http_exact(focus/'focus-image-review-v001.json')
    checks['browserProof']=dict(path=ui_path.relative_to(ROOT).as_posix(),sha256=pub.digest(ui_path),screenshots=proofs)
    checks['automatedChecks']=dict(path=REL+'/automated-checks-v001.json',sha256=pub.digest(RUN/'automated-checks-v001.json'))
    checks.update(recordedAt=datetime.now(timezone.utc).isoformat(),passed=True,publicationPending=False,browserProofPending=False,changedSteps=changed,stepFingerprintsCompared=52,catalogSha256=pub.digest(ROOT/'learning/catalog.json'),apiCatalogMatchesDisk=True,apiProgressMatchesDisk=True,progressSha256=baseline['progress_sha256'],progressRevision=5,sourceSceneUnchanged=True,newSceneReopened=True,learnerCompletionConfirmed=False)
    assert pub.digest(Path(verification['source_scene_path']))==verification['source_scene_sha256']
    assert pub.digest(Path(verification['scene_path']))==verification['scene_sha256']
    assert pub.digest(ROOT/'learning/progress.json')==baseline['progress_sha256']
    pub.write(RUN/'publication-checks-v001.json',checks)
    print(json.dumps(dict(passed=True,formalImages=len(checks['images']),supplementaryImages=len(checks['supplementaryImages']),browserProofs=len(proofs),changedSteps=changed,progressRevision=5,sceneSha256=verification['scene_sha256']),ensure_ascii=False))

if __name__=='__main__':
    main()
