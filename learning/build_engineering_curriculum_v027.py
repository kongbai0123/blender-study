"""Append a bounded GUI width-limit refusal for the manual box."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;SOURCE=ROOT/'learning/web/engineering-curriculum-v026.json';OUTPUT=ROOT/'learning/web/engineering-curriculum-v027.json'
SOURCE_SHA='3f63711c49cf0d4630381c42ae422c1b9b9be3a21c5ea864194a9f749b7a6146';BASE='learning/evidence/parametric/2026-10-27-manual-box-guard-y-reject-v001/';SUMMARY_SHA='6644842b1e15b63346b8dddeb123ceeca983e35b2fef38ffa2f1a152083e747c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path,expected,label,kind):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected:raise ValueError('missing or changed: '+path)
 return {'path':path,'sha256':expected,'label':label,'type':kind}
def main():
 before=SOURCE.read_bytes()
 if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:raise ValueError('v026 changed')
 d=json.loads(before.decode('utf-8-sig'))
 if d['id']!='engineering-curriculum-v002':raise ValueError('unexpected curriculum id')
 ref=checked(BASE+'guard-gui-y-out-of-range-verification-v001.json',SUMMARY_SHA,'假專案寬度超界拒絕驗證摘要','verification-json');e=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
 if e['kind']!='controlled-manual-box-width-out-of-range-rejected' or e['proposedWidth']!=80 or e['prePostOuterMm']!=[80,50] or e['prePostBoundsMm']['Body.001'][:2]!=[[2,78],[2,48]] or not e['screenMessageReviewedByHuman']:raise ValueError('unexpected width refusal')
 for p in e['programs']:checked(p['path'],p['sha256'],'本機檔','local-source')
 imgs={}
 for x in e['images']:checked(BASE+x['file'],x['sha256'],x['file'],'screenshot');imgs[x['file']]=x
 if len(imgs)!=10:raise ValueError('unexpected screenshots')
 def fig(n,c):return {'type':'screenshot','path':BASE+n,'sha256':imgs[n]['sha256'],'caption':c}
 step={'id':'ch05-manual-guard-y-reject-01','title':'觀察寬度超界被拒','goal':'核對 Y 超界前後的數位狀態','context':'獨立 Blender 假專案、指定手工盒受控面板，外框80×50。','actions':['選擇寬度 W，輸入80 mm 並核對後提交。','觀察拒絕訊息，對照提交前後三件的程式讀值。'],'success':'原圖顯示寬度超出候選計算界限的拒絕訊息；程式讀回外框仍80×50、切割體 X2～78／Y2～48、蓋外框約80×50。訊息由人工目視，圖片不能直接量出幾何。','shortcuts':[],'figures':[fig('GUARD-08-parameter-menu.png','原圖：參數選單中的寬度 W。'),fig('GUARD-09-y-invalid-proposal.png','原圖：選 W、輸入80並勾選核對。'),fig('GUARD-10-y-invalid-result.png','原圖：面板顯示寬度超界拒絕。')],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':[
 '此為獨立 Blender 5.2.1 / CAD Sketcher 0.32.1 假專案與假 progress；插件啟用及檔案路徑由程式處理，面板輸入與提交為 GUI 事件。',
 '寬度拒絕的文字由人工查看原圖，程式未自動解析 UI 文字；前後參數與三件評估外框由 Python 讀回，不等於全部資料或完整拓撲未變。',
 '只限指定手工範本及受控面板；直接修改 Blender／CAD Sketcher 原生欄位可繞過防護及自動更新，面板也不攔截原生 Save／Export。',
 '30～70 mm 是該範本形狀鍵未夾限的理論候選範圍，不是全區安全、製造能力或配合合格的證據。',
 '沒有全面碰撞、實體列印、量測或試配，0.4 mm 總間隙仍為試驗值。'], 'artifacts':[ref]}
 old={s['id'] for c in d['chapters'] for s in c['steps']}
 if len(old)!=255 or step['id'] in old:raise ValueError('unexpected baseline')
 ch=next(c for c in d['chapters'] if c['id']=='ch05');ch['steps'].append(step);ch['limitations'].append('v027 假專案受控面板的寬度80 mm 超界拒絕已由原圖目視；原生欄位仍可繞過。')
 d['version']='v027 · 2026-10-27';d['description']='12章詳細操作參照；v027追加手工盒寬度超界拒絕的實際面板操作。'
 d['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v026.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}]);d['manualBoxGuardWidthRejectTrial']={'summary':ref,'proposedWidthMm':80,'prePostOuterMm':[80,50],'messageManuallyObserved':True,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
 if OUTPUT.exists():raise FileExistsError('refusing to overwrite v027')
 OUTPUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(sha(OUTPUT))
if __name__=='__main__':main()
