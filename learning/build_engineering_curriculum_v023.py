"""Append GUI X/Y controlled updates and bounded same-session reopen evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'learning/web/engineering-curriculum-v022.json'
OUTPUT=ROOT/'learning/web/engineering-curriculum-v023.json'
SOURCE_SHA='2f4e1f787bd4c30506ff99d33f51a2561fd93d1210f3dc2b7e26f9650d5c18e4'
BASE='learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v003/'
SUMMARY_SHA='eb174f82c29737ab47959c4a105fc20e2aa823ec39dec21a12c0cdd5f4a5f18c'
SCENE_SHA='4d5c383a67f855f81707604d6b1f871ae74054611ce878b63b01a73451d9e201'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path,expected,label,kind):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected:raise ValueError('missing or changed: '+path)
 return {'path':path,'sha256':expected,'label':label,'type':kind}
def main():
 before=SOURCE.read_bytes()
 if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:raise ValueError('v022 changed')
 data=json.loads(before.decode('utf-8-sig'))
 if data['id']!='engineering-curriculum-v002':raise ValueError('unexpected curriculum id')
 ref=checked(BASE+'guard-gui-xy-reopen-verification-v001.json',SUMMARY_SHA,'手工盒受控面板雙軸及重開驗證摘要','verification-json')
 d=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
 if d['kind']!='controlled-manual-box-xy-and-reopen-gui-trial':raise ValueError('unexpected kind')
 for name,L,W in [('invalid-assertion',80,50),('valid-assertion',90,50),('width-assertion-alt',90,60),('shrink-x-assertion',70,60),('shrink-y-assertion',70,40),('reopened-assertion',70,40),('registered-assertion',70,40)]:
  p=d['phases'][name]
  if p['outerMm']!=[L,W] or p['cutterX']!=[2,L-2] or p['cutterY']!=[2,W-2]:raise ValueError('unexpected phase '+name)
  if abs((p['lidBoundsMm'][0][1]-p['lidBoundsMm'][0][0])-L)>.003 or abs((p['lidBoundsMm'][1][1]-p['lidBoundsMm'][1][0])-W)>.003:raise ValueError('unexpected lid')
 for p in d['programs']:checked(p['path'],p['sha256'],'本機檔','local-source')
 scene=d['scene']
 if scene['sha256']!=SCENE_SHA:raise ValueError('unexpected scene')
 scene_ref=checked(BASE+scene['file'],SCENE_SHA,'70×40 假專案測試版（非學員作品）','scene-blend')
 lookup={}
 for item in d['images']:
  checked(BASE+item['file'],item['sha256'],item['file'],'screenshot');lookup[item['file']]=item
 if len(lookup)!=27:raise ValueError('unexpected image count')
 def fig(name,caption):return {'type':'screenshot','path':BASE+name,'sha256':lookup[name]['sha256'],'caption':caption}
 common=[
  '此為獨立 Blender、CAD Sketcher 的假專案與假 progress；插件由程式啟用、對話框路徑由程式填入，欄位、提交與另存重開由 GUI 事件操作。',
  '僅受控面板提交會觸發此更新；直接修改 Blender／CAD Sketcher 原生欄位可繞過防護與自動求解，工具不攔截原生存檔或匯出。',
  '本例依序 X110被拒、80×50→90×50→90×60→70×60→70×40；切割體與蓋外框為 Python 讀值，圖中尺寸標籤可能重疊，不能由圖片直接量取。',
  '70×40 是同一 Blender 執行期間另存並重開；Blender 程式結束再重啟後面板是否保留尚未驗證。',
  'GUARD-27 點側欄後面板消失，沒有實際看到已登記版本被拒絕；程式只核對假 progress 有登記、幾何仍為70×40。已登記版本的 GUI 拒絕與失敗回滾尚未在此實證。',
  'v002 寬度輸入曾因焦點而失敗，不能當作模型失效；本版 v003 另行操作成功。X60～100／Y30～70只是形狀鍵未夾限理論候選，並非全區安全或製造配合合格。',
  '未做全面碰撞、列印、量測及實體試配；0.4 mm總間隙為試驗值。',
 ]
 parts=[
  ('ch05-manual-guard-xy-01','由90×50改為90×60','觀察受控面板的寬度提交','假專案 Body Sketch，外框90×50。',['開啟預檢，選寬度 W、輸入60並核對。','提交後查看外框，對照摘要的切割體與上蓋讀值。'],'原圖可見60／90；程式讀回切割體 X2～88／Y2～58、上蓋外框約90×60。',[('GUARD-13-width-dialog-open.png','原圖：開啟預檢。'),('GUARD-14-width-menu-open.png','原圖：選擇參數。'),('GUARD-15-width-selected.png','原圖：選中寬度。'),('GUARD-16-width-typing-alt.png','原圖：輸入60。'),('GUARD-17-width-entered-alt.png','原圖：輸入值已確定。'),('GUARD-18-width-checked-alt.png','原圖：勾選核對。'),('GUARD-19-width-result-alt.png','原圖：提交後外框顯示90／60。')],[ref]),
  ('ch05-manual-guard-xy-02','逐次縮小長與寬','觀察每次受控提交後的數位更新','假專案起始90×60，兩次獨立提交。',['先選 L=70並核對提交；再選 W=40並核對提交。','對照摘要中每次外框、內腔切割體與蓋的程式讀值。'],'兩次讀回依次為70×60、70×40；第二次切割體 X2～68／Y2～38，上蓋外框約70×40。',[('GUARD-20-shrink-x-proposal.png','原圖：準備長度70。'),('GUARD-21-shrink-x-result.png','原圖：提交後70／60。'),('GUARD-22-shrink-y-proposal.png','原圖：準備寬度40。'),('GUARD-23-shrink-y-result.png','原圖：提交後畫面，尺寸標籤重疊；詳細讀值見摘要。')],[ref]),
  ('ch05-manual-guard-xy-03','保存並重開70×40測試版','確認本次數位結果可在同一次 Blender 執行期重開','70×40 假專案；另存新檔。',['於假專案另存並重開測試版。','對照程式讀回的外框、切割體和蓋外框。'],'重開後讀回外框70×40、切割體 X2～68／Y2～38，蓋外框約70×40；非程式重啟測試。',[('GUARD-24-saved.png','原圖：假專案另存成功提示。'),('GUARD-25-reopened.png','原圖：假專案同一執行期重開。')],[scene_ref,ref]),
  ('ch05-manual-guard-xy-04','辨認未完成的版本拒絕測試','區分登記與實際拒絕證據','同一執行期重開假70×40版。',['對照假 progress 登記與下方兩張畫面。','辨認畫面並未顯示拒絕訊息，不將其視為拒絕測試成功。'],'程式確認假 progress 登記且幾何不變；第二張圖面板已消失，沒有確認拒絕操作。',[('GUARD-26-registered-fixture.png','原圖：假 progress 登記後；登記由程式讀回。'),('GUARD-27-registered-attempt.png','原圖：側欄切換後面板不見，未看到拒絕訊息。')],[ref]),
 ]
 steps=[{'id':i,'title':t,'goal':g,'context':c,'actions':acts,'success':ok,'shortcuts':[],'figures':[fig(n,cap) for n,cap in figs],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts} for i,t,g,c,acts,ok,figs,artifacts in parts]
 old={s['id'] for c in data['chapters'] for s in c['steps']}
 if len(old)!=247 or any(s['id'] in old for s in steps):raise ValueError('unexpected prior steps')
 ch=next(c for c in data['chapters'] if c['id']=='ch05');ch['steps'].extend(steps)
 ch['limitations'].append('v023 假專案受控面板經90×60、70×60、70×40且同一次Blender執行期重開；原生欄位可繞過，程式重啟與已登記版本拒絕尚未驗。')
 data['version']='v023 · 2026-10-27';data['description']='12章詳細操作參照；v023追加手工盒受控面板雙軸及同一執行期重開試驗。'
 data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v022.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}])
 data['manualBoxGuardXYReopenTrial']={'summary':ref,'scene':scene_ref,'rejectedL':110,'testedDimensions':[[90,50],[90,60],[70,60],[70,40]],'sameBlenderSessionReopen':True,'applicationRestartTested':False,'registeredRefusalTested':False,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
 if OUTPUT.exists():raise FileExistsError('refusing to overwrite v023')
 OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(sha(OUTPUT))
if __name__=='__main__':main()
