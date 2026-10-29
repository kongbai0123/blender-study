"""Append a bounded independent GUI probe of the manual-box guard."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT/'learning/web/engineering-curriculum-v021.json'
OUTPUT = ROOT/'learning/web/engineering-curriculum-v022.json'
SOURCE_SHA = '98ec27409a2799e7e9b20f09edd60cef28b92ec7020cf6d22fb522dca9ff7142'
BASE = 'learning/evidence/parametric/2026-10-27-manual-box-guard-gui-trial-v001/'
SUMMARY_SHA = '5e43dc1c82f48d9d8c3a554e46214392c48dff3f4ffde4d11775ac07914b3c53'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(path, expected, label, kind):
    p=(ROOT/path).resolve()
    if not p.is_relative_to(ROOT.resolve()) or not p.is_file() or sha(p)!=expected: raise ValueError('missing or changed: '+path)
    return {'path':path,'sha256':expected,'label':label,'type':kind}

def main():
    before=SOURCE.read_bytes()
    if hashlib.sha256(before).hexdigest()!=SOURCE_SHA: raise ValueError('v021 baseline changed')
    data=json.loads(before.decode('utf-8-sig'))
    if data['id']!='engineering-curriculum-v002': raise ValueError('unexpected curriculum ID')
    ref=checked(BASE+'guard-gui-one-x-verification-v001.json',SUMMARY_SHA,'手工盒面板單組 GUI 驗證摘要','verification-json')
    summary=json.loads((ROOT/ref['path']).read_text(encoding='utf-8-sig'))
    if summary['kind']!='controlled-manual-box-one-x-gui-trial': raise ValueError('unexpected kind')
    a,b=summary['rejected'],summary['accepted']
    if a['proposedL']!=110 or a['outerMm']!=[80,50] or a['cutterX']!=[2,78] or a['cutterY']!=[2,48]: raise ValueError('unexpected rejected state')
    if b['proposedL']!=90 or b['outerMm']!=[90,50] or b['cutterX']!=[2,88] or b['cutterY']!=[2,48]: raise ValueError('unexpected accepted state')
    if not(89.99 < b['lidBoundsMm'][0][1]-b['lidBoundsMm'][0][0] < 90.01): raise ValueError('unexpected lid bounds')
    for p in summary['programs']:
        checked(p['path'],p['sha256'],'本機程式及資料','local-source')
    lookup={}
    for item in summary['images']:
        checked(BASE+item['file'],item['sha256'],item['file'],'screenshot');lookup[item['file']]=item
    if len(lookup)!=12: raise ValueError('unexpected image count')
    def fig(name,caption):
        item=lookup[name];return {'type':'screenshot','path':BASE+name,'sha256':item['sha256'],'caption':caption}
    common=[
        '此為獨立 Blender 與 CAD Sketcher 的假專案、假 progress 試驗；本次插件由程式啟用，檔案對話框路徑由程式填入；文字編輯器 Alt+P、面板欄位及確認由 GUI 事件操作。',
        '此面板只適用經核對的特定手工盒副本；本機腳本 learning/tutor/guarded_manual_box_v001.py，需同專案的 manual_box_auto_update_v002.py 和 manual_box_reference_v001.json。三者 SHA-256 請見驗證摘要，且此輪未驗證每種不同工作區操作。',
        '直接修改 Blender 或 CAD Sketcher 原生欄位仍可繞過預檢及受控自動更新；工具不會自動保存，也不攔截原生存檔或匯出。',
        '本次僅測 X=110 被拒、X80→90 接受；拒絕訊息由原圖目視，外框、內腔切割體及蓋外框由程式讀值；沒有驗 Y、其他尺寸、失敗回滾或重開。',
        'X60～100／Y30～70 為形狀鍵的理論未夾限候選範圍，不是全區安全或製造、配合合格範圍；未完成全面碰撞、列印、量測及實體試配。',
    ]
    parts=[
      ('ch05-manual-guard-01','開啟外框草圖與面板','確認本次面板操作前提','指定手工盒隔離副本；需啟用 CAD Sketcher。',['選 Body 並進入 Body Sketch。','於 Blender 文字編輯器開啟本機腳本並按 Alt+P；返回 3D Viewport。'],'原圖顯示 Body Sketch 與文字編輯器；腳本執行事件須結合後續面板出現判讀。', [('GUARD-01-opened.png','原圖：假專案的手工盒。'),('GUARD-02-outer-sketch.png','原圖：Body Sketch 與80／50。'),('GUARD-03-script-open.png','原圖：文字編輯器載入腳本。'),('GUARD-04-script-run.png','原圖：Alt+P 後文字編輯器；執行事件依劇本及後續面板判讀。'),('GUARD-05-viewport.png','原圖：返回3D視圖。')]),
      ('ch05-manual-guard-02','開啟預檢並選擇參數','辨識受控輸入的位置','Body Sketch 中，側欄顯示手工盒尺寸預檢。',['開啟側欄的預檢面板並按預檢按鈕。','查看參數選單；選擇長度或寬度後輸入並核對。'],'原圖顯示面板、空白對話框及長度／寬度選項；本次測試使用長度。',[('GUARD-06-panel.png','原圖：手工盒尺寸預檢面板。'),('GUARD-07-dialog.png','原圖：選擇參數與確認的對話框。'),('GUARD-08-parameter-menu.png','原圖：參數選單。')]),
      ('ch05-manual-guard-03','觀察超界輸入被拒','辨認超界不得送入模型','隔離試驗目前外框80×50 mm。',['在受控面板選長度 L，輸入110並核對後提交。','查看錯誤訊息，對照摘要中的前後讀值。'],'原圖顯示110提案與超出界限的錯誤；程式讀回外框仍80×50、切割體 X2～78／Y2～48 mm。',[('GUARD-09-invalid-proposal.png','原圖：輸入110 mm並勾選核對。'),('GUARD-10-invalid-result.png','原圖：畫面拒絕超界輸入。')]),
      ('ch05-manual-guard-04','觀察一次受控自動更新','比較原生尺寸與內腔更新結果','隔離試驗從80×50出發；由受控面板提交。',['選長度 L，輸入90並核對後提交。','查看確認訊息，對照程式讀回的外框、切割體和上蓋外框。'],'原圖顯示外框90／50；程式讀回切割體 X2～88／Y2～48，上蓋外框約90×50 mm。本次未切入內腔草圖，也未另存重開。',[('GUARD-11-valid-proposal.png','原圖：輸入90 mm並勾選核對。'),('GUARD-12-valid-result.png','原圖：受控更新後的90／50；內腔及上蓋外框依程式讀值。')]),
    ]
    steps=[{'id':i,'title':t,'goal':g,'context':c,'actions':acts,'success':ok,'shortcuts':[], 'figures':[fig(n,capt) for n,capt in figs], 'sourceSteps':[], 'evidenceStatus':'existing_demo','limitations':list(common),'artifacts':[ref]} for i,t,g,c,acts,ok,figs in parts]
    ids={s['id'] for c in data['chapters'] for s in c['steps']}
    if len(ids)!=243 or any(s['id'] in ids for s in steps): raise ValueError('unexpected step baseline')
    ch=next(c for c in data['chapters'] if c['id']=='ch05');ch['steps'].extend(steps)
    ch['limitations'].append('v022 假專案中受控面板已試 X110 拒絕及 X80→90 自動更新；只限本次試驗，直接改原生欄位不受防護，Y及重開等待驗。')
    data['version']='v022 · 2026-10-27';data['description']='12章詳細操作參照；v022追加手工盒受控尺寸面板的單組 GUI 試驗。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v021.json','sha256':SOURCE_SHA},{'path':ref['path'],'sha256':ref['sha256']}])
    data['manualBoxGuardOneXTrial']={'summary':ref,'rejectedL':110,'acceptedL':90,'automaticUpdateScope':'受控面板一次長度提交','physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    if OUTPUT.exists(): raise FileExistsError('refusing to overwrite v022')
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(sha(OUTPUT))

if __name__=='__main__': main()
