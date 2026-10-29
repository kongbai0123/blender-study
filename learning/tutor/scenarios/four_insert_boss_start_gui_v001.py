"""Save/reopen original Body/Lid with program-prepared tools, no Booleans."""
import bpy,json,hashlib
from pathlib import Path
from common import Kit,PROJECT
from four_insert_boss_tools import prepare,CENTRES
SOURCE=PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
SOURCE_HASH='ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
BODY_FACE='14aadcea96872f701a71b38280cf1a6788a13a3b45574e083930e46e3541e58b'
LID_FACE='95fe03fdbe5e99141156cbb018cca4407c275b06359930d43776ccec69241c00'
TOOLS=['zz_Boss_Pillars','zz_Boss_Ribs_X','zz_Boss_Ribs_Y','zz_Boss_Pilot_Tools','zz_Boss_Lid_Tools']
def build(g):
    k=Kit(g);out=Path(g['OUT'])
    if g['sha256'](SOURCE)!=SOURCE_HASH:raise RuntimeError('source sha mismatch')
    cp=Path(k.demo_dir)/SOURCE.name;cp.write_bytes(SOURCE.read_bytes())
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
    def facehash(o):
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        faces=sorted(tuple(sorted(tuple(round(float(pts[i][j]),6) for j in range(3)) for i in f.vertices)) for f in o.data.polygons)
        return hashlib.sha256(json.dumps(faces,separators=(',',':')).encode()).hexdigest()
    def stats(stage):
        body=bpy.data.objects['Body'];lid=bpy.data.objects['Lid']
        checks={'stage':stage,'boxSourceSha256':SOURCE_HASH,'bodyFaceFingerprint':facehash(body),'lidFaceFingerprint':facehash(lid),
                'bodyModifiers':[m.type for m in body.modifiers],'lidModifiers':[m.type for m in lid.modifiers],
                'bodyHidden':body.hide_get(),'lidHidden':lid.hide_get(),'centresMm':CENTRES,
                'tools':{n:{'vertices':len(bpy.data.objects[n].data.vertices),'faces':len(bpy.data.objects[n].data.polygons),'hidden':bpy.data.objects[n].hide_get()} for n in TOOLS},
                'toolPreparation':'Python prebuilt; no Boolean has been applied',
                'material':None,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
        if checks['bodyFaceFingerprint']!=BODY_FACE or checks['lidFaceFingerprint']!=LID_FACE or checks['bodyModifiers'] or checks['lidModifiers'] or any(not x['hidden'] for x in checks['tools'].values()):raise RuntimeError('start geometry mismatch '+json.dumps(checks))
        (out/(stage+'-verification.json')).write_text(json.dumps(checks,indent=2),encoding='utf8')
        return json.dumps(checks)
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,cp.name);k.confirm_dialog(wait=3);k.do(prepare,1)
    k.click_outliner('Body');send('F3');k.do(lambda:k.type_text('Frame Selected'),.5);send('RET')
    k.record('START','prepared','程式預建四柱、八肋與孔刀具並隱藏，原盒蓋尚未作布林。',lambda:stats('prepared'))
    k.file_dialog(163,k.demo_dir,'u11_four_insert_boss_start_v001.blend');k.confirm_dialog(wait=3)
    k.record('START','saved','GUI 另存可跟做起始副本；檔案視窗欄位由程式填寫。',lambda:stats('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u11_four_insert_boss_start_v001.blend');k.confirm_dialog(wait=4)
    k.record('START','reopened','GUI 重開起始副本，核對原盒、原蓋和隱藏工具。',lambda:stats('reopened'))
