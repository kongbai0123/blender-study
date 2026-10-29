"""獨立 Blender：以既有程式建外牙草案作工具，GUI 建立試塊並 Boolean Difference。

這是局部幾何探測，不等同配合對件：無預設間隙、無標準牙型、端部牙形截斷。
"""
import json
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import Kit, PROJECT, PARK

SOURCE = PROJECT/'learning/evidence/08/2026-10-28-closed-external-thread-probe-v001/demo-files/u08_closed_external_thread_probe_v001.blend'
SOURCE_HASH = 'dadb268dce5836f46d877d90a7ca0113de5280790f6d9611ce9a551422c4c700'
CUTTER = 'External_Thread_Draft'
BLOCK = 'Cube'
FILENAME = 'u08_inner_boolean_trial_v002.blend'

def build(g):
    k=Kit(g); out=Path(g['OUT']); dest=Path(k.demo_dir)/'sources';dest.mkdir()
    if g['sha256'](str(SOURCE))!=SOURCE_HASH:raise RuntimeError('來源外牙 hash 不符')
    src=dest/SOURCE.name;src.write_bytes(SOURCE.read_bytes())
    if g['sha256'](str(src))!=SOURCE_HASH:raise RuntimeError('來源副本 hash 不符')
    snap=out/'source-snapshot';snap.mkdir();files=[]
    for name in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                 'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_inner_boolean_trial_v002.py'):
        target=snap/Path(name).name;target.write_bytes((PROJECT/name).read_bytes())
        files.append({'source':name,'snapshot':target.name,'sha256':g['sha256'](str(target))})
    (snap/'manifest.json').write_text(json.dumps({'files':files,'sourceSha256':SOURCE_HASH},indent=2)+'\n',encoding='utf8')
    state={}
    def do(fn,wait=.4):k.do(fn,wait)
    def key(name,**kwargs):k.key(name,x=700,y=600,**kwargs)
    def search(text):
        do(lambda:key('F3'),.3);do(lambda:k.type_text(text),.3);do(lambda:key('RET'),.8)
    def scale(axis,amount):
        do(lambda:key('S'),.2);do(lambda:key(axis),.2);do(lambda:k.type_text(amount),.2);do(lambda:key('RET'),.5)
    def move(axis,amount):
        do(lambda:key('G'),.2);do(lambda:key(axis),.2);do(lambda:k.type_text(amount),.2);do(lambda:key('RET'),.5)
    def select(name):
        do(lambda:k.click(1340,k.outliner_y(name)),.6)
        def check():
            active=bpy.context.view_layer.objects.active
            if not active or active.name!=name: raise RuntimeError('選取不符：'+str(active.name if active else None))
        do(check,.1)
    def unchanged():
        if g['sha256'](str(SOURCE))!=SOURCE_HASH or g['sha256'](str(src))!=SOURCE_HASH:raise RuntimeError('外牙原檔或來源副本改變')
    def bounds(o):
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    def before():
        unchanged();o=bpy.data.objects[CUTTER]; b=bounds(o)
        if len(o.data.vertices)!=2592 or abs(b[2][0])>1e-4 or abs(b[2][1]-4)>1e-4: raise RuntimeError('來源外牙幾何不符')
        return {'sourceObject':CUTTER,'boundsMm':b,'construction':'既有程式生成的封閉外牙徑向網格，非本輪 GUI 手工建牙',
                'limitations':['截斷端牙形不完整','沒有設置配合間隙','非 ISO 規格','未列印或試配']}
    def check_blank():
        unchanged();o=bpy.data.objects[BLOCK];b=bounds(o)
        expected=[[-8,8],[-8,8],[.5,3.5]]
        if any(abs(x-y)>1e-4 for a,e in zip(b,expected) for x,y in zip(a,e)):raise RuntimeError('試塊外框不符 '+str(b))
        if any(abs(v-1)>1e-4 for v in o.scale):raise RuntimeError('試塊縮放尚未套用')
        return {'block':BLOCK,'boundsMm':b,'dimensionsMm':[16,16,3], 'scale':list(o.scale),'note':'試塊由 GUI 新增、縮放與移位；僅數位探測，非盒蓋'}
    def assignment():
        mods=[m for m in bpy.data.objects[BLOCK].modifiers if m.type=='BOOLEAN'];m=mods[0] if len(mods)==1 else None
        return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
    def try_assign(attempt=0):
        actual=assignment();state.setdefault('operandAttempts',[]).append({'attempt':attempt,**actual})
        if actual=={'operation':'DIFFERENCE','operand':CUTTER,'solver':'EXACT'}:return
        if attempt>=2:raise RuntimeError('Boolean 未正確指定：'+str(state['operandAttempts']))
        g['queue'][0:0]=[(lambda:k.move(1380,400),.3),(lambda:k.click(1380,400),.4),(lambda:key('A',ctrl=True),.2),
            (lambda:k.type_text(CUTTER),.4),(lambda:k.move(1310,432),.3),(lambda:k.click(1310,432),.6),(lambda:try_assign(attempt+1),.1)]
    def selected():
        actual=assignment()
        if actual!={'operation':'DIFFERENCE','operand':CUTTER,'solver':'EXACT'}:raise RuntimeError('Boolean 未正確指定 '+str(actual))
        return {'modifier':actual,'note':'GUI 指定 Difference；此時仍為修改器預覽，未套用'}
    def validate(stage):
        unchanged();o=bpy.data.objects.get(BLOCK)
        if not o or o.modifiers or o.type!='MESH':raise RuntimeError('試塊不存在或修改器未套用')
        bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);bm.verts.ensure_lookup_table();bm.verts.index_update()
        # Connected components via graph built from actual edges.
        adj={v.index:set() for v in bm.verts}
        for e in bm.edges:
            a,b=(v.index for v in e.verts);adj[a].add(b);adj[b].add(a)
        unseen=set(adj);components=0
        while unseen:
            components+=1;todo=[unseen.pop()]
            while todo:
                v=todo.pop()
                for n in adj[v]&unseen:unseen.remove(n);todo.append(n)
        nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
        pts=[v.co.copy() for v in bm.verts];bb=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
        tree=BVHTree.FromBMesh(bm);rays=[]
        for axis,z,want in [('x',1.0,5.0),('x',1.3,6.0),('y',1.3,5+1/6),('x',2.3,6.0)]:
            vector=Vector((1,0,0)) if axis=='x' else Vector((0,1,0))
            hit,normal,idx,distance=tree.ray_cast(Vector((0,0,z)),vector,20)
            actual=(hit.x if axis=='x' else hit.y) if hit else None
            rays.append({'direction':axis,'zMm':z,'expectedRadiusMm':want,'actualMm':actual})
        expected=[[-8,8],[-8,8],[.5,3.5]]
        checks={'nonEmpty':bool(pts),'bounds':all(abs(x-y)<1e-4 for a,e in zip(bb,expected) for x,y in zip(a,e)),
                'closed':nonmanifold==0,'singleShell':components==1,'positiveVolume':volume>0,
                'materialRemoved':volume<768,'helicalSampleRays':all(x['actualMm'] is not None and abs(x['actualMm']-x['expectedRadiusMm'])<.03 for x in rays)}
        result={'stage':stage,'boundsMm':bb,'vertices':len(pts),'faces':len(bm.faces),'nonManifoldEdges':nonmanifold,
                'connectedComponents':components,'signedVolumeMm3':volume,'radialSamples':rays,'checks':checks,
                'limitations':['工具牙由程式預建且端部不完整','無配合間隙與對件試配','射線是局部抽樣，不證明完整牙型或無自交','未切片、列印、量測或試配'],
                'material':None,'physicalPrint':None,'physicalFit':None,'qualifiedClearanceMm':None,'qualifiedStrength':None}
        bm.free();(out/(stage+'-verification.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        if not all(checks.values()):raise RuntimeError('差集幾何檢查未通過：'+json.dumps(checks,ensure_ascii=False))
        return result
    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    do(lambda:key('O',ctrl=True),1.2);k.fill_dialog(str(dest)+'\\',src.name);k.confirm_dialog(wait=3)
    k.record('08-inner','source','開啟外牙程式草案副本，外牙非本次 GUI 手工建牙',before,park=PARK)
    # In this Blender scene Add Cube produces 2000 mm; scale factors are dimensionless.
    search('Add Cube');scale('X','.008');scale('Y','.008');scale('Z','.0015');move('Z','2');search('Apply Scale')
    k.record('08-inner','blank','GUI 新增方塊，依序縮放 X/Y/Z、移位 Z 並套用縮放',check_blank,park=PARK)
    do(lambda:k.click(1245,503),.5);search('Add Boolean Modifier')
    do(lambda:k.click(1380,400),.4);do(lambda:k.type_text(CUTTER),.4);do(lambda:key('RET'),.8)
    k.record('08-inner','operand-probe','GUI 嘗試指定 Boolean 物件並讀回欄位',lambda:assignment(),park=PARK)
    do(try_assign,.1)
    k.record('08-inner','preview','確認 GUI Boolean Difference/Exact 與工具',selected,park=PARK)
    do(lambda:k.click(1452,k.outliner_y(CUTTER)),.7);select(BLOCK)
    do(lambda:k.click(1424,320),.4);k.menu_item(1331,343,1.5)
    k.record('08-inner','applied','GUI 套用 Difference，檢查實際切削結果',lambda:validate('applied'),park=PARK)
    k.file_dialog(163,k.demo_dir,FILENAME);k.confirm_dialog(wait=2)
    k.record('08-inner','saved','GUI 另存新檔並讀回；檔案欄位由程式填入',lambda:validate('saved'),park=PARK)
    do(lambda:key('O',ctrl=True),1.2);k.fill_dialog(k.demo_dir,FILENAME);k.confirm_dialog(wait=3)
    k.record('08-inner','reopened','重開新場景並讀回，列印與試配未執行',lambda:validate('reopened'),park=PARK)
    def summary():
        unchanged();state['outputScene']={'path':FILENAME,'sha256':g['sha256'](str(Path(k.demo_dir)/FILENAME))}
        state.update(sourceSha256=SOURCE_HASH,material=None,clearance=None,physicalPrint=None,physicalFit=None,qualifiedStrength=None)
        (out/'trial-summary.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    do(summary,.1)
