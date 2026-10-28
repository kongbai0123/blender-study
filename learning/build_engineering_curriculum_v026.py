"""Append a fresh Blender session with explicit manual script execution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;SOURCE=ROOT/'learning/web/engineering-curriculum-v025.json';OUTPUT=ROOT/'learning/web/engineering-curriculum-v026.json'
SOURCE_SHA='8466f7c733fe2a01f4f3c9cac50eae247897b8d7840f000344b47cca935d53c7';BASE='learning/evidence/parametric/2026-10-27-manual-box-guard-restart-trial-v004/';SUMMARY_SHA='eecd80b6cd6b5753af40fce3dd9ad50029ab81be8418be67cb7914b54258fe64'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path,expected,label,kind):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected:raise ValueError('missing or changed: '+path)
 return {'path':path,'sha256':expected,'label':label,'type':kind}
def main():
 before=SOURCE.read_bytes()
 if hashlib.sha256(before).hexdigest()!=SOURCE_SHA:raise ValueError('v025 changed')
 d=json.loads(before.decode('utf-8-sig'))
 if d['id']!='engineering-curriculum-v002':raise ValueError('unexpected curriculum id')
 ref=checked(BASE+'guard-gui-restart-manual-script-verification-v002.json',SUMMARY_SHA,'新 Blender 程序手動執行腳本的驗證摘要','verification-json')
 e=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
 if e['kind']!='controlled-manual-box-restart-rerun-script-gui-trial' or e['before']['outerMm']!=[70,40] or e['after']['outerMm']!=[80,40]:raise ValueError('unexpected restart trial')
 b=e['after']['bounds']
 if b['Body.001'][0]!=[2,78] or b['Body.001'][1]!=[2,38] or abs(b['Cube'][0][1]-b['Cube'][0][0]-80)>.003 or abs(b['Cube'][1][1]-b['Cube'][1][0]-40)>.003:raise ValueError('unexpected mesh bounds')
 source=checked(e['sourceScene']['path'],e['sourceScene']['sha256'],'70×40已驗證助教來源場景（非學員作品）','scene-blend')
 for p in e['programs']:checked(p['path'],p['sha256'],'本機腳本與資料','local-source')
 images={}
 for x in e['images']:checked(BASE+x['file'],x['sha256'],x['file'],'screenshot');images[x['file']]=x
 if len(images)!=8:raise ValueError('unexpected screenshot count')
 def fig(n,c):return {'type':'screenshot','path':BASE+n,'sha256':images[n]['sha256'],'caption':c}
 common=[
 '試驗在新開的獨立 Blender 5.2.1／CAD Sketcher 0.32.1 假專案與假 progress；程式啟用插件、複製假副本、填檔案對話框路徑與讀值，GUI 事件操作 Text Editor、Alt+P 及面板；未修改學員工作區。',
 '個人使用需先將已驗證的手工盒來源另存至此專案 learning/workspaces/engineering-parametric/（資料夾不存在先建立），並與此專案原有 learning/progress.json 共存；使用新且未登記的檔名，不覆寫既有版本。此為使用前提，本次只在假專案重現。',
 '使用同專案 learning/tutor/guarded_manual_box_v001.py 及相同資料夾內 manual_box_auto_update_v002.py、manual_box_reference_v001.json；本次程式先準備這三項副本，在文字編輯器內已有相對連結的腳本時主動按 Alt+P。不同個人環境首次載入步驟以畫面為準。',
 '本次未核驗 Alt+P 前面板狀態，不可推定每次啟動是否自動載入；尚未證實面板自動常駐。原生欄位可繞過面板及受控自動更新，Save／Export 也不受攔截。',
 'v001／v003 重啟探測的文字編輯器點按與側欄切換有誤、保留失敗證據；本次 v004 改成對已連結檔執行 Alt+P 才觀察後續成功，不把先前操作失誤當模型失效。',
 '原圖開啟及返回視圖有 sketcher.slvs_select 工具未找到提示，原因未知；本次操作成功不證明全部工具正常。原圖標籤重疊，內腔和蓋外框數值為程式讀值。',
 '未做全面碰撞、實體列印、量測及試配，0.4 mm總間隙仍是試驗值；理論形狀鍵界限不是製造或配合合格範圍。']
 parts=[
  ('ch05-manual-guard-restart-01','準備個人副本並辨認重啟前提','保留來源與已登記版本','需已有本教材指定手工盒與 CAD Sketcher 環境。',['個人練習先將已驗證手工盒另存至專案 learning/workspaces/engineering-parametric/；若資料夾不存在先建立。','保留專案原有 progress.json 與 learning/tutor 三項檔案，不覆寫既有已登記版本。'],'原圖是新 Blender 程序開啟假專案70×40測試副本；個人工作區操作本次未實際執行。',[('GUARD-01-opened.png','原圖：新 Blender 程序讀入假專案的70×40副本；底部有工具提示。'),('GUARD-02-outer-sketch.png','原圖：Body Sketch，尺寸標籤重疊。')],[source,ref]),
  ('ch05-manual-guard-restart-02','重新執行腳本並測一次尺寸','辨認新程序的面板載入與受控更新','個人副本已另存、Body Sketch及插件可用。',['在 Blender Text Editor 開啟專案 learning/tutor/guarded_manual_box_v001.py；若已連結則核對來源，按 Alt+P 執行。','回到 3D Viewport 的手工盒預檢面板，選 L=80、勾選核對並提交。'],'本次新 Blender 程序從70×40副本經 Alt+P 後受控改為80×40；程式讀回切割體 X2～78／Y2～38、蓋外框約80×40，並非照片直接量出。',[('GUARD-03-text-after-restart.png','原圖：新程序 Text Editor 已連結腳本；依劇本確認執行 Alt+P。'),('GUARD-04-script-open.png','原圖：同一文字檔；不可由圖片差異推按鍵。'),('GUARD-05-script-run.png','原圖：Alt+P 後；執行依事件與後續面板判讀。'),('GUARD-06-viewport.png','原圖：返回視圖，面板顯示；底部有工具提示。'),('GUARD-07-restart-proposal.png','原圖：L由70提案改為80並核對。'),('GUARD-08-restart-result.png','原圖：提交後畫面，尺寸標籤重疊；內腔依程式讀值。')],[ref]),
 ]
 steps=[{'id':i,'title':t,'goal':g,'context':c,'actions':acts,'success':ok,'shortcuts':[],'figures':[fig(n,cap) for n,cap in figs],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':artifacts} for i,t,g,c,acts,ok,figs,artifacts in parts]
 old={s['id'] for c in d['chapters'] for s in c['steps']}
 if len(old)!=253 or any(s['id'] in old for s in steps):raise ValueError('unexpected baseline')
 ch=next(c for c in d['chapters'] if c['id']=='ch05');ch['steps'].extend(steps);ch['limitations'].append('v026 新 Blender 程序重新按 Alt+P 後以受控面板成功70×40→80×40；未核驗執行前面板狀態或自動常駐。')
 d['version']='v026 · 2026-10-27';d['description']='12章詳細操作參照；v026追加新 Blender 程序中手動執行面板腳本並測尺寸。'
 d['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v025.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}]);d['manualBoxGuardRestartTrial']={'summary':ref,'sourceScene':source,'manualScriptExecution':True,'testedBeforeMm':[70,40],'testedAfterMm':[80,40],'automaticPersistenceConfirmed':False,'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
 if OUTPUT.exists():raise FileExistsError('refusing to overwrite v026')
 OUTPUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(sha(OUTPUT))
if __name__=='__main__':main()
