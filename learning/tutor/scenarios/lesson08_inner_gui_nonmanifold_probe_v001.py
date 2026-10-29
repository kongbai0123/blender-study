"""對已保存的內牙試塊示範 GUI Non Manifold 選取；不改原檔或工作區。"""
import json
from pathlib import Path
import bmesh
import bpy
from common import Kit, PROJECT, PARK

SOURCE=PROJECT/'learning/evidence/08/2026-10-28-inner-boolean-trial-v003/demo-files/u08_inner_boolean_trial_v003.blend'
EXPECTED='a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80'

def build(g):
    k=Kit(g);out=Path(g['OUT']);copy=Path(k.demo_dir)/SOURCE.name
    if g['sha256'](str(SOURCE))!=EXPECTED:raise RuntimeError('來源 SHA 不符')
    copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](str(copy))!=EXPECTED:raise RuntimeError('副本 SHA 不符')
    def do(fn,wait=.4):k.do(fn,wait)
    def key(name,**kw):k.key(name,x=700,y=600,**kw)
    def source():
        o=bpy.context.view_layer.objects.active
        if not o or o.name!='Cube' or o.mode!='OBJECT':raise RuntimeError('來源選取或模式不符')
        return {'active':o.name,'mode':o.mode,'sourceSha256':EXPECTED}
    def selected():
        o=bpy.context.view_layer.objects.active
        if not o or o.name!='Cube' or o.mode!='EDIT':raise RuntimeError('編輯模式或對象不符')
        bm=bmesh.from_edit_mesh(o.data);count=sum(e.select for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
        if count!=0 or nonmanifold!=0:raise RuntimeError('選取或非流形邊結果不符')
        return {'selectedEdges':count,'actualNonManifoldEdges':nonmanifold,
                'limitation':'僅邊選取及拓樸檢查，非完整自交、牙型、製造或配合驗證'}
    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    do(lambda:key('O',ctrl=True),1.2);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3)
    k.record('08-inner-check','source','開啟同雜湊示範副本，確認作用中物件與模式',source,park=PARK)
    do(lambda:key('TAB'),.5);do(lambda:key('TWO'),.3);do(lambda:key('A',alt=True),.3)
    do(lambda:key('F3'),.3);do(lambda:k.type_text('Select Non Manifold'),.3);do(lambda:key('RET'),.8)
    k.record('08-inner-check','nonmanifold','GUI 切邊選取、清除選取、F3 搜尋 Select Non Manifold',selected,park=PARK)
    def finish():
        if g['sha256'](str(SOURCE))!=EXPECTED or g['sha256'](str(copy))!=EXPECTED:raise RuntimeError('原場景或副本內容改變')
        result={'sourceSha256':EXPECTED,'checks':selected(),'physicalPrint':None,'physicalFit':None,'qualifiedStrength':None}
        (out/'check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    do(finish,.1)
