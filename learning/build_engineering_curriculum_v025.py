"""Append a GUI fault-injection result without calling rollback verified."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;SOURCE=ROOT/'learning/web/engineering-curriculum-v024.json';OUTPUT=ROOT/'learning/web/engineering-curriculum-v025.json'
SOURCE_SHA='a938a10207f53ac8643b273edf12dcae5f455b47da92ec921c39bc91e5d3afae';BASE='learning/evidence/parametric/2026-10-27-manual-box-guard-fault-trial-v001/';SUMMARY_SHA='a5ad902b84da85438048c0aa7945876ad0bf0b6a784f2b9770c4fd62f04146f3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path,expected,label,kind):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected:raise ValueError('missing or changed: '+path)
 return {'path':path,'sha256':expected,'label':label,'type':kind}
def main():
 before=SOURCE.read_bytes()
 if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:raise ValueError('v024 changed')
 d=json.loads(before.decode('utf-8-sig'))
 if d['id']!='engineering-curriculum-v002':raise ValueError('unexpected curriculum id')
 ref=checked(BASE+'guard-gui-fault-unconfirmed-rollback-v001.json',SUMMARY_SHA,'假專案更新工具缺失與回復未確認摘要','verification-json')
 evidence=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
 if evidence['kind']!='controlled-manual-box-updater-missing-fault-trial' or evidence['proposedL']!=70 or not evidence['missingHelperInjectedOnlyInFakeProject'] or not evidence['reportedUnconfirmedRollbackSeenByHuman']:raise ValueError('unexpected fault')
 beforep=evidence['phases']['helper-unavailable'];afterp=evidence['phases']['fault-result']
 if beforep!=afterp or beforep['outerMm']!=[90,50] or beforep['bounds']['Body.001'][0]!=[2,88]:raise ValueError('unexpected fault bounds')
 for p in evidence['programs']:checked(p['path'],p['sha256'],'本機程式','local-source')
 imgs={}
 for x in evidence['images']:checked(BASE+x['file'],x['sha256'],x['file'],'screenshot');imgs[x['file']]=x
 if len(imgs)!=15:raise ValueError('unexpected image count')
 def fig(name,caption):return {'type':'screenshot','path':BASE+name,'sha256':imgs[name]['sha256'],'caption':caption}
 step={'id':'ch05-manual-guard-fault-01','title':'觀察更新工具缺失時的停止訊息','goal':'辨認回復未確認時的處理','context':'獨立 Blender 的假專案，外框已由80×50改為90×50。','actions':['僅在假專案將更新工具暫時移開，模擬受控更新與回滾都找不到工具。','以面板嘗試 L=70，觀察錯誤；對照前後程式讀回的外框。'],'success':'原圖顯示「回復未確認、請勿存檔、重開原副本」；前後三件的外框讀值相同、尺寸仍為90×50，但這只核外框，不能證明完整回復或保存安全。','shortcuts':[],'figures':[fig('FAULT-01-helper-unavailable.png','原圖：假專案故障注入後；工具缺失依劇本而非照片辨認。'),fig('FAULT-02-proposal.png','原圖：假專案嘗試長度70。'),fig('FAULT-03-result.png','原圖：畫面提示回復未確認、勿存檔並重開原副本。')],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':[
 '這是獨立 Blender 5.2.1 與 CAD Sketcher 的假專案故障注入；僅假專案的 updater 被程式改名，真實專案與學員進度不以此操作。',
 '原圖錯誤文字由人工目視；程式只讀參數及三件評估外框，runner completed 只代表劇本結束，不能代替成功回復或安全判斷。',
 '本例更新與回滾都因 helper 缺失無法求解，回復沒有確認；外框雖相同，也不能證明完整拓撲與其他資料已還原，應勿存檔並重開原副本。',
 'v024 的回滾未實證屬當時狀態；v025 僅驗證此類工具缺失時會顯示回復未確認警告，沒有證明成功回滾或其他故障均安全。',
 '受控面板不攔截 Blender／CAD Sketcher 原生欄位、Save 或 Export；關閉 Blender 再開後面板持久性未驗。',
 '尺寸範圍不是製造或配合合格範圍；未做全面碰撞、實體列印、量測及試配，0.4 mm總間隙仍為試驗值。'], 'artifacts':[ref]}
 old={s['id'] for c in d['chapters'] for s in c['steps']}
 if len(old)!=252 or step['id'] in old:raise ValueError('unexpected baseline')
 ch=next(c for c in d['chapters'] if c['id']=='ch05');ch['steps'].append(step);ch['limitations'].append('v025 假專案故障注入顯示更新工具缺失時「回復未確認、請勿存檔」；此例沒有證明完整回滾或其他故障均安全。')
 d['version']='v025 · 2026-10-27';d['description']='12章詳細操作參照；v025追加手工盒受控更新工具缺失的故障示範。'
 d['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v024.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}]);d['manualBoxGuardFaultTrial']={'summary':ref,'fakeFaultOnly':True,'rollbackConfirmed':False,'warningManuallyObserved':True,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
 if OUTPUT.exists():raise FileExistsError('refusing to overwrite v025')
 OUTPUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(sha(OUTPUT))
if __name__=='__main__':main()
