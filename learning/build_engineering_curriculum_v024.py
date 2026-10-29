"""Append independently observed registered-version refusal in a fake project."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v023.json';OUTPUT=ROOT/'learning/web/engineering-curriculum-v024.json'
SOURCE_SHA='36561b7585efdc470fa8ae5fc7f7c4c368eaa134d7faf3af751bb3d7b0a4fa1a'
BASE='learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v004/'
SUMMARY_SHA='3438328a764c5ff3ec5e7e9d5f673bd671b95f5c552ca41aebe9f25b7f723b40'
SCENE_SHA='9942f712fe5f7bf88daa9b144de0b29fbae5a9dd8217acdb96a3df0f3aacad3f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path,expected,label,kind):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected:raise ValueError('missing or changed: '+path)
 return {'path':path,'sha256':expected,'label':label,'type':kind}
def main():
 before=SOURCE.read_bytes()
 if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:raise ValueError('v023 changed')
 d=json.loads(before.decode('utf-8-sig'))
 if d['id']!='engineering-curriculum-v002':raise ValueError('unexpected curriculum id')
 ref=checked(BASE+'guard-gui-registered-rejection-verification-v001.json',SUMMARY_SHA,'假已登記版本拒絕的 GUI 驗證摘要','verification-json')
 trial=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
 if trial['kind']!='controlled-manual-box-registered-rejection-gui-trial':raise ValueError('unexpected kind')
 refusal=trial['registeredRefusal']
 if refusal!={'fakeRegistration':True,'screenMessageReviewedByHuman':True,'message':'此檔案已登記為版本；請先以新檔名另存','geometryUnchangedAfterAttempt':True}:raise ValueError('unexpected refusal')
 for n in ('reopened-assertion','registered-assertion'):
  p=trial['phases'][n]
  if p['outerMm']!=[70,40] or p['cutterX']!=[2,68] or p['cutterY']!=[2,38]:raise ValueError('unexpected bounds')
 if trial['phases']['reopened-assertion']!=trial['phases']['registered-assertion']:raise ValueError('geometry changed')
 for p in trial['programs']:checked(p['path'],p['sha256'],'本機檔','local-source')
 lookup={}
 for i in trial['images']:
  checked(BASE+i['file'],i['sha256'],i['file'],'screenshot');lookup[i['file']]=i
 if len(lookup)!=27:raise ValueError('unexpected image count')
 scene=checked(BASE+trial['scene']['file'],SCENE_SHA,'v004 假專案 70×40 示範副本（非學員作品）','scene-blend')
 def fig(name,caption):return {'type':'screenshot','path':BASE+name,'sha256':lookup[name]['sha256'],'caption':caption}
 step={'id':'ch05-manual-guard-registered-01','title':'觀察已登記版本拒絕','goal':'分清假登記、畫面拒絕與幾何讀值','context':'v004 假專案；70×40 測試版在同一 Blender 執行期重開。','actions':['對照程式寫入假 progress 的版本登記。','按預檢面板按鈕，觀察要求以新檔名另存的錯誤。','對照重開與嘗試之後的程式讀值。'],'success':'GUARD-27 原圖可見已登記版本拒絕訊息；程式核對假 progress 及前後外框70×40、切割體 X2～68／Y2～38、蓋外框不變。錯誤文字由人目視，不是程式自動辨識。','shortcuts':[],'figures':[fig('GUARD-25-reopened.png','原圖：假專案同一執行期重開。'),fig('GUARD-26-registered-fixture.png','原圖：程式登記假 progress 後；登記以讀值核對。'),fig('GUARD-27-registered-attempt.png','原圖：按面板按鈕後顯示已登記版本拒絕。')],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':[
 '這是獨立 Blender 假專案及假 progress，插件由程式啟用，檔案路徑及假登記由程式寫入；面板按鈕、保存與同一執行期重開由 GUI 事件操作，不是學員作品或確認。',
 'v003 相同嘗試時點到側欄導致面板消失，並未看見拒絕，保留在前一步；此 v004 修正操作後，原圖顯示拒絕。',
 '錯誤訊息由人工查看原圖確認；程式僅核對假版本登記與前後評估外框，不自動解析 UI 文字。截圖無法直接量出切割體與上蓋尺寸。',
 '登記拒絕只適用此受控面板，不能攔截 Blender 原生欄位、Save 或 Export；已登記版仍須依正常版本流程另存新名。',
 'v004 另存與重開在同一 Blender 執行期完成；關閉 Blender 再啟動後面板是否保留尚未測試。',
 '更新工具只適用指定手工盒副本；0.4 mm 是試驗總間隙，沒有全面碰撞或實體列印、量測及試配合格結論。',
 '此 v004 假場景檔名沿用 v003；以執行資料夾和 SHA-256 識別，不等於先前 v003 檔。'], 'artifacts':[scene,ref]}
 old={s['id'] for c in d['chapters'] for s in c['steps']}
 if len(old)!=251 or step['id'] in old:raise ValueError('unexpected baseline')
 ch=next(c for c in d['chapters'] if c['id']=='ch05');ch['steps'].append(step);ch['limitations'].append('v024 假專案重新操作已登記版本，畫面顯示拒絕；僅限面板，不攔截原生存檔／匯出，程式重啟持久性未測。')
 d['version']='v024 · 2026-10-27';d['description']='12章詳細操作參照；v024追加假已登記版本面板拒絕的實際畫面。'
 d['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v023.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}]);d['manualBoxGuardRegisteredTrial']={'summary':ref,'scene':scene,'rejectionMessageManuallyObserved':True,'registeredFakeFixture':True,'applicationRestartTested':False,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
 if OUTPUT.exists():raise FileExistsError('refusing to overwrite v024')
 OUTPUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(sha(OUTPUT))
if __name__=='__main__':main()
