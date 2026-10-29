"""GUI Boolean demonstration on the original box; tools are program-prepared.

The source box is copied. Cylinders, ribs and cutters are prebuilt by the helper
script, not GUI from scratch. Modifier configuration and applying are GUI events.
"""
import json
from pathlib import Path
import bpy,bmesh
from common import Kit,PROJECT
from four_insert_boss_tools import prepare,CENTRES

SOURCE=PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
SOURCE_HASH='ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'

def build(g):
    k=Kit(g);out=Path(g['OUT'])
    if g['sha256'](SOURCE)!=SOURCE_HASH:raise RuntimeError('source hash differs')
    source_copy=Path(k.demo_dir)/SOURCE.name;source_copy.write_bytes(SOURCE.read_bytes())
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
    def search(s):send('F3');k.do(lambda:k.type_text(s),.5);send('RET')
    def prepare_tools():prepare()
    def bounds(o):
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    def mesh_stats(name,stage):
        obj=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(obj.data)
        remain=set(bm.verts);comp=0
        while remain:
            comp+=1;stack=[remain.pop()]
            while stack:
                for e in stack.pop().link_edges:
                    for v in e.verts:
                        if v in remain:remain.remove(v);stack.append(v)
        result={'stage':stage,'object':name,'vertices':len(bm.verts),'faces':len(bm.faces),'components':comp,
                'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),
                'boundsMm':bounds(obj),'pendingModifiers':[m.type for m in obj.modifiers],
                'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedStrength':None,'qualifiedClearance':None}
        bm.free();(out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
        if comp!=1 or result['nonManifoldEdges'] or result['boundaryEdges'] or result['pendingModifiers']:raise RuntimeError('failed '+json.dumps(result))
        return json.dumps(result)
    def tools_stats():
        result={'toolPreparation':'Python prebuilt, not GUI hand modeling','centresMm':CENTRES,
                'toolNames':['zz_Boss_Pillars','zz_Boss_Ribs_X','zz_Boss_Ribs_Y','zz_Boss_Pilot_Tools','zz_Boss_Lid_Tools'],
                'boundsMm':{n:bounds(bpy.data.objects[n]) for n in ['zz_Boss_Pillars','zz_Boss_Ribs_X','zz_Boss_Ribs_Y','zz_Boss_Pilot_Tools','zz_Boss_Lid_Tools']},
                'physicalPrint':None,'physicalFit':None}
        return json.dumps(result)
    def assignment(target):
        obj=bpy.data.objects[target];ms=[m for m in obj.modifiers if m.type=='BOOLEAN'];m=ms[0] if len(ms)==1 else None
        return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
    def set_assignment(target,tool,operation,attempt=0):
        actual=assignment(target)
        if actual=={'operation':operation,'operand':tool,'solver':'EXACT'}:return
        if attempt>=2:raise RuntimeError('GUI assignment failed '+str(actual))
        y=k.props_y(193)
        g['queue'][0:0]=[(lambda:k.move(1380,y),.3),(lambda:k.click(1380,y),.4),
          (lambda:k.key('A',ctrl=True,x=700,y=500),.2),(lambda:k.type_text(tool),.4),
          (lambda:k.move(1310,y+32),.3),(lambda:k.click(1310,y+32),.6),
          (lambda:set_assignment(target,tool,operation,attempt+1),.1)]
    def do_boolean(target,tool,operation,slug,description):
        k.click_outliner(target);search('Add Boolean Modifier')
        k.do(lambda:k.click(1369 if operation=='UNION' else 1438,k.props_y(143)),.5)
        k.do(lambda:k.click(1380,k.props_y(193)),.4);k.do(lambda:k.type_text(tool),.4);send('RET')
        k.do(lambda:set_assignment(target,tool,operation),.1)
        k.record('BOS',slug+'-preview',description+'；GUI 先選擇對應布林模式、Exact 與工具。',lambda:json.dumps(assignment(target)))
        k.do(lambda:k.click(1424,k.props_y(113)),.4);k.menu_item(1331,k.props_y(136),1)
        k.record('BOS',slug+'-applied',description+'；GUI 套用 Boolean 並讀回網格。',lambda:mesh_stats(target,slug+'-applied'))
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3);k.do(prepare_tools,1)
    k.do(lambda:k.click(1246,k.props_y(300)),.5)
    k.click_outliner('Body');search('Frame Selected')
    k.record('BOS','source','開啟原盒蓋保護副本；柱、肋與孔工具由 Python 預建並隱藏。',tools_stats)
    do_boolean('Body','zz_Boss_Pillars','UNION','pillars','將四個名義直徑 8 mm 的柱體聯集到盒底')
    do_boolean('Body','zz_Boss_Ribs_X','UNION','ribs-x','將四條 X 向連壁肋聯集到盒體')
    do_boolean('Body','zz_Boss_Ribs_Y','UNION','ribs-y','將四條 Y 向連壁肋聯集到盒體')
    do_boolean('Body','zz_Boss_Pilot_Tools','DIFFERENCE','pilots','使用四個工具切出名義直徑 4.0 mm、深 9 mm 的盲孔')
    k.do(lambda:k.click(1452,k.outliner_y('Lid')),.7)
    def lid_shown():
        if bpy.data.objects['Lid'].hide_get():raise RuntimeError('Lid still hidden')
        return 'GUI 已顯示原上蓋，位置未變。'
    k.record('BOS','lid-visible','GUI 在 Outliner 顯示既有上蓋。',lid_shown)
    do_boolean('Lid','zz_Boss_Lid_Tools','DIFFERENCE','lid-holes','在上蓋切出四個名義 3.4 mm 的試驗穿孔')
    k.click_outliner('Body');search('Frame Selected');send('NUMPAD_2');send('NUMPAD_2')
    k.record('BOS','framed','GUI 聚焦整盒，檢視四柱與既有蓋的幾何草案。',lambda:mesh_stats('Body','framed'))
    k.file_dialog(163,k.demo_dir,'u11_four_insert_boss_box_v001.blend');k.confirm_dialog(wait=3)
    k.record('BOS','saved','GUI 另存新版本；檔案對話框路徑與檔名由程式填寫。',lambda:mesh_stats('Body','saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u11_four_insert_boss_box_v001.blend');k.confirm_dialog(wait=4)
    k.record('BOS','reopened','GUI 重開新版本；數位讀值不代表實體列印或試配。',lambda:mesh_stats('Body','reopened'))
