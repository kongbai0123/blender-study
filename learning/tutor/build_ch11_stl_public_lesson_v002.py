"""Rebind STL lesson to independently re-recorded privacy-safe GUI sessions.

Real Blender file browser hides its OS shortcut panel, and exports/reimports to
a public temporary folder. The actual STL bytes are SHA-verified when copied
to evidence. PNG screenshots are unedited, not cropped or composited.
"""
import copy,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lesson=copy.deepcopy(read(root/'learning/lesson11_stl_export_optional_steps_v001.json'))
jobs={
 'hand-thread':('hand','u11_hand_thread_public_v001.stl'),
 'side-box-body-repaired':('sidebox','u11_side_box_body_triangulated_public_v001.stl'),
 'side-box-lid':('sidelid','u11_side_box_lid_public_v001.stl'),
 'side-cap-repaired':('cap','u11_side_cap_triangulated_public_v001.stl'),
 'four-boss-body':('fourboss','u11_four_boss_body_public_v001.stl'),
 'four-boss-lid':('fourboss','u11_four_boss_lid_public_v001.stl')}
for item in lesson['items']:
 id=item['id'];directory,name=jobs[id];folder=root/f'learning/evidence/08/2026-10-28-ch11-stl-public-{directory}-v001'
 run=read(folder/'run.json');status=read(folder/'runner-status.json');verification=read(folder/(id+'-verification.json'))
 audit=read(folder/(id+'-independent-audit-v001.json'));stl=folder/'demo-files/exports'/name
 if status['status']!='completed' or sha(stl)!=verification['evidenceCopyVerifiedSha256'] or sha(stl)!=audit['stlSha256']:
  raise ValueError('run or evidence sha differs: '+id)
 if audit['binaryExactDuplicateTriangles'] or audit['binaryTriangles']!=audit['reimport']['triangles'] or audit['reimport']['nonManifoldEdges']:
  raise ValueError('independent audit failed: '+id)
 records=[r for r in run['records'] if r['slug'].startswith(id+'-')]
 steps=[s for s in lesson['steps'] if s['id'].startswith('11-stl-'+id+'-')]
 if len(records)!=6 or len(steps)!=6:raise ValueError('unexpected step count '+id)
 item.update(stl=stl.relative_to(root).as_posix(),stlSha256=sha(stl),stlBytes=len(stl.read_bytes()),
   guiReimport=verification['reimport'],independentReimport=audit['reimport'],
   independentAudit=(folder/(id+'-independent-audit-v001.json')).relative_to(root).as_posix(),
   exportOptions=verification['exportOptions'],importOptions=verification['importOptions'])
 for n,(step,r) in enumerate(zip(steps,records),1):
  p=folder/r['file'];digest=sha(p)
  if digest!=r['sha256']:raise ValueError('source screenshot changed '+id)
  step['screenshot']={'path':p.relative_to(root).as_posix(),'sha256':digest}
  if n==3:step['visibleConfirmation']='未修圖的真實 Blender 檔案視窗顯示選項；系統快捷側欄已由程式收起，使用公共臨時路徑。'
  if n==5:step['visibleConfirmation']='未修圖的真實 Blender 匯入視窗顯示 Scale 1／Scene Unit 關；系統快捷側欄已由程式收起。'
  if n==6:step['context']+=' 實際 GUI 匯出與重匯入使用公共臨時資料夾；結束後 STL 原始 bytes 複製至 evidence，SHA 已核對並刪除暫存。'
lesson['title']='第 11 章：六件 STL 匯出、修訂與重新匯入（清潔場次）'
lesson['scope']='重新以獨立 Blender GUI 實際選取、匯出及匯入六件；檔案瀏覽器側欄隱藏且使用公共暫存位置，不更新學員進度。'
lesson['limitations'].append('這是與 v001 分開的真實 GUI 重演；程式收起系統快捷側欄並填公共臨時路徑，未修改原圖像素。STL 經 SHA 驗證為相同 bytes，之後清除本次暫存。')
out=root/'learning/lesson11_stl_export_optional_steps_v002.json'
if out.exists():raise FileExistsError('preserve lesson version')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
safe=root/'learning/evidence/08/2026-10-28-ch11-stl-summary-v002'
if safe.exists():raise FileExistsError('preserve summary version')
safe.mkdir();(safe/'safe-summary-v001.json').write_text(json.dumps({k:v for k,v in lesson.items() if k!='steps'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('STL',len(lesson['items']),'steps',len(lesson['steps']),'lesson SHA-256',sha(out))
