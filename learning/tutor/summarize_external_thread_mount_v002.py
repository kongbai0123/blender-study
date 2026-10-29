"""Hash-check v002 evidence, retain old lesson, create an optional new version."""
import copy,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
e=root/'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002'
run=json.loads((e/'run.json').read_text(encoding='utf8'))
status=json.loads((e/'runner-status.json').read_text(encoding='utf8'))
audit=json.loads((e/'independent-audit-v001.json').read_text(encoding='utf8'))
scene=e/'demo-files/u11_box_external_thread_draft_v002.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if status['status']!='completed' or audit['sceneSha256']!=sha(scene) or audit['toolExpectedPhase11Point25DegreesMaxMatrixDelta']>1e-5:raise ValueError('run, scene or phase differs from audited result')
records=[]
for r in run['records']:
    image=e/r['file'];digest=sha(image)
    if digest!=r['sha256']:raise ValueError('screenshot hash mismatch '+str(image))
    try:obs=json.loads(r['observed'])
    except (ValueError,TypeError):obs=None
    records.append({'seq':r['seq'],'slug':r['slug'],'image':image.relative_to(root).as_posix(),'sha256':digest,'observed':obs})
assert len(records)==11
safe_audit={k:v for k,v in audit.items() if k not in ('triangleAreasMm2InTessellationOrder','triangleAltitudesMmInTessellationOrder')}
safe={'scenario':'learning/tutor/scenarios/external_thread_mount_gui_trial_v002.py',
      'scenarioSha256':sha(root/'learning/tutor/scenarios/external_thread_mount_gui_trial_v002.py'),
      'scene':scene.relative_to(root).as_posix(),'sceneSha256':sha(scene),'status':status['status'],
      'workspaceSnapshotUnchanged':status['workspacesUnchanged'],'independentAudit':safe_audit,
      'independentAuditPath':(e/'independent-audit-v001.json').relative_to(root).as_posix(),
      'records':records,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None,
      'notes':['三角形高是三角面幾何量，不是壁厚；細長面仍存在，禁止聲稱完全無薄面。',
               '零 BVH 候選不是無自交證明；該版本不代表已改善製造、強度或配合。',
               '原始 runner-status 含 Windows 最近使用路徑，不得直接公開；本摘要不含之。',
               '原始 run.json 部分中文動作因編碼損壞，選修文件依照劇本與圖像整理，不改原始證據。']}
(e/'safe-summary-v001.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
old=json.loads((root/'learning/lesson11_external_mount_optional_steps_v001.json').read_text(encoding='utf8'))
lesson=copy.deepcopy(old)
lesson['title']='第 11 章選修：盒側外牙相位調整與接合幾何草案'
lesson['scope']='獨立 Blender 相位調整的幾何示範；不更新學員進度，未驗證製造或配合。'
lesson['demonstrationScene']=safe['scene'];lesson['demonstrationSceneSha256']=safe['sceneSha256']
lesson['limitations'] += ['保留名義嵌入 0.5 mm，牙條繞自身 X 軸轉 11.25°；比舊版更改接合相位，但仍有細長面。',
 '三角形最小高度不是材料壁厚；數值對照與 BVH 不能證明更容易列印、配合或強度合格。']
phase={'goal':'調整牙條繞軸相位','operation':'在轉向後的牙條上按 R、X、11.25、Enter，繞世界 X 軸調整牙條相位。',
       'context':'先完成繞 Y 旋轉 90°；X 軸是此時牙條的軸向。這會改變牙條與盒壁的相對角位置。',
       'visibleConfirmation':'牙條仍可能被盒體遮住，無法僅憑此圖準確量角。',
       'programReadback':'重開後獨立讀回物件旋轉矩陣，與 X 11.25°、Y 90° 的預期矩陣最大差約 1.14×10⁻⁷。'}
steps=lesson['steps'];steps.insert(2,phase)
for idx,(step,r) in enumerate(zip(steps,records),1):
    step['id']=f'11-mount-v002-{idx:02}'
    step['screenshot']={'path':r['image'],'sha256':r['sha256']}
steps[-1]['programReadback']='獨立讀回單連通體、非流形邊 0、BVH 候選 0；最小三角高 0.00112596 mm、最短 mesh 邊 0.0146923 mm。細長面仍存在；三角形高不是壁厚，亦非製造或配合合格證明。'
out=root/'learning/lesson11_external_mount_optional_steps_v002.json'
if out.exists():raise FileExistsError('Preserve existing v002 lesson')
out.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('wrote lesson v002 with',len(steps),'verified PNGs; did not change old lesson')
