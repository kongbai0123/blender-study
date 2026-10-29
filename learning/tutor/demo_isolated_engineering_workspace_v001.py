"""Exercise workspace CLI in a deliberately fake project; never write learner progress."""
from pathlib import Path
from hashlib import sha256
import json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'learning/evidence/parametric/2026-10-28-workspace-isolated-cli-v001'
BASE_REL='learning/evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend'
BASE_HASH='ddae8a3d3745146501d25527354352e6b71431b837c78c8269a43dc5e6a3dec6'
if OUT.exists():raise FileExistsError(OUT)
OUT.mkdir(parents=True);fake=OUT/'fake-project';learn=fake/'learning';learn.mkdir(parents=True)
shutil.copy2(ROOT/'learning/manage.py',learn/'manage.py')
base=ROOT/BASE_REL
if sha256(base.read_bytes()).hexdigest()!=BASE_HASH:raise ValueError('baseline hash mismatch')
target=fake/BASE_REL;target.parent.mkdir(parents=True);shutil.copy2(base,target)
catalog={'schemaVersion':1,'lessons':[{'id':'01','title':'測試','steps':[{'id':'01-01','title':'測試','action':'測試','success':'測試'}]}]}
progress={'schemaVersion':1,'revision':1,'updatedAt':'synthetic','activeLesson':'01','lessons':{'01':{'status':'in_progress','currentStep':'01-01','completedSteps':[],'notes':[],'workspace':'learning/workspaces/01'}},'fileVersions':[],'events':[]}
for name,value in [('catalog.json',catalog),('progress.json',progress)]:
 (learn/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(learn/'workspaces/01').mkdir(parents=True)
def run(*args):
 p=subprocess.run([sys.executable,'-X','utf8',str(learn/'manage.py'),*args],cwd=fake,capture_output=True,text=True,encoding='utf8')
 return {'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
before=sha256((learn/'progress.json').read_bytes()).hexdigest()
create=run('engineering-workspace')
copied=run('engineering-workspace','--copy-manual-box','my_manual_box_v001.blend')
after_copy=sha256((learn/'progress.json').read_bytes()).hexdigest()
duplicate=run('engineering-workspace','--copy-manual-box','my_manual_box_v001.blend')
rel='learning/workspaces/engineering-parametric/my_manual_box_v001.blend'
copy_sha=sha256((fake/rel).read_bytes()).hexdigest()
register=run('register-file','--workspace','engineering-parametric','--revision','1','--path',rel,'--role','source_scene')
p=json.loads((learn/'progress.json').read_text(encoding='utf8'));version=p['fileVersions'][-1]
if create['code']!=0 or copied['code']!=0 or duplicate['code']==0 or register['code']!=0 or before!=after_copy or copy_sha!=BASE_HASH or version['sha256']!=copy_sha or p['revision']!=2:raise RuntimeError('fake workspace checks failed')
result={'schemaVersion':1,'kind':'isolated-synthetic-project','status':'completed','limitations':['全為隔離假專案及合成進度，非學員工作區、學員成果或配合驗證。','假專案 runner 與原始命令輸出可能含本機路徑，不公開。'],
 'checks':{'workspaceCreated':True,'copySha256':copy_sha,'progressUnchangedByWorkspaceAndCopy':True,'duplicateNameRefused':True,'registerReturnCode':register['code'],'syntheticRevisionBefore':1,'syntheticRevisionAfter':p['revision'],'registeredPath':version['path'],'registeredSha256':version['sha256'],'registeredRole':version['role']},
 'source':{'path':BASE_REL,'sha256':BASE_HASH},'commands':['engineering-workspace','engineering-workspace --copy-manual-box my_manual_box_v001.blend','register-file --workspace engineering-parametric --revision 1 --path learning/workspaces/engineering-parametric/my_manual_box_v001.blend --role source_scene']}
path=OUT/'safe-summary-v001.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('isolated workspace evidence',path.relative_to(ROOT).as_posix(),sha256(path.read_bytes()).hexdigest())
