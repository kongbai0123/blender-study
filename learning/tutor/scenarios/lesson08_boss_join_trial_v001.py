"""獨立 Blender GUI：既有盲孔柱沿 Z 移動，再試行與原盒 Boolean Union。

材質、螺絲／嵌件規格、實際孔徑、力學與配合待定；不修改學員進度或原檔。
"""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import Kit, PARK, PROJECT

SOURCE = PROJECT/'learning/evidence/08/2026-10-27-lesson08-boss-draft-v002/demo-files/u08_blind_boss_draft_v001.blend'
SOURCE_HASH = '4df306ac6b7e3f57108cb0221fad62480ca47c80f77d5ccd3e91632a6d5c7320'
BODY = 'Body_Reference'
BOSS = 'Boss_Blind_Polygon32'
FILENAME = 'u08_box_boss_trial_v001.blend'

def build(g):
    k=Kit(g); out=Path(g['OUT']); copied=Path(k.demo_dir)/'sources';copied.mkdir()
    if g['sha256'](str(SOURCE))!=SOURCE_HASH:raise RuntimeError('來源盲孔柱場景 hash 不符')
    source_copy=copied/SOURCE.name;source_copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](str(source_copy))!=SOURCE_HASH:raise RuntimeError('來源副本 hash 不符')
    snap=out/'source-snapshot';snap.mkdir()
    files=[]
    for name in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                 'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_boss_join_trial_v001.py'):
        target=snap/Path(name).name;target.write_bytes((PROJECT/name).read_bytes())
        files.append({'source':name,'snapshot':target.name,'sha256':g['sha256'](str(target))})
    (snap/'manifest.json').write_text(json.dumps({'files':files,'sourceSha256':SOURCE_HASH},indent=2)+'\n',encoding='utf-8')
    state={}
    def obj(name):return bpy.data.objects[name]
    def do(fn,wait=.4):k.do(fn,wait)
    def key(name,**kwargs):k.key(name,x=700,y=600,**kwargs)
    def search(text):
        do(lambda:key('F3'),.3);do(lambda:k.type_text(text),.3);do(lambda:key('RET'),.8)
    def move_z(text):
        do(lambda:key('G'),.2);do(lambda:key('Z'),.2);do(lambda:k.type_text(text),.2);do(lambda:key('RET'),.7)
    def select_row(name,y):
        do(lambda:k.click(1340,y),.6)
        def check():
            active=bpy.context.view_layer.objects.active
            if not active or active.name!=name:raise RuntimeError('Outliner 選取不符：'+str(active.name if active else None))
        do(check,.1)
    def assert_sources():
        if g['sha256'](str(SOURCE))!=SOURCE_HASH or g['sha256'](str(source_copy))!=SOURCE_HASH:
            raise RuntimeError('原始場景或來源副本內容改變')
    def values(name):
        o=obj(name); pts=[o.matrix_world@v.co for v in o.data.vertices]
        bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
        return {'name':name,'location':list(o.location),'boundsMm':bounds,'vertices':len(pts),'visible':not o.hide_get()}
    def before():
        assert_sources(); b,p=values(BODY),values(BOSS)
        if b['vertices']<8 or p['vertices']!=128:raise RuntimeError('來源幾何不符')
        state['before']={'body':b,'boss':p,'sourceSha256':SOURCE_HASH,'method':'既有獨立柱與盒，未進行 Union'}
        return '來源為既有獨立盲孔柱與原盒，原始場景未修改。柱頂點對頂點外徑 8 mm、孔 4 mm；僅為草案。'
    def positioned():
        assert_sources(); b,p=values(BODY),values(BOSS)
        for i,(a,c) in enumerate(zip(p['boundsMm'],[[-4,4],[-4,4],[-13.5,-5.5]])):
            if any(abs(x-y)>1e-4 for x,y in zip(a,c)):raise RuntimeError('柱位置超出預期：'+str(p))
        if any(abs(x-y)>1e-4 for x,y in zip(b['boundsMm'][2],[-15,15])):
            raise RuntimeError('盒體高度不符')
        state['positioned']={'body':b,'boss':p,'intendedOverlapMm':0.5,'placement':'置中、與盒內底重疊；僅作幾何示範'}
        return '柱由 Z 0～8 移到 Z −13.5～−5.5 mm；內底 Z −13 mm，名義重疊 0.5 mm。位置與尺寸僅為草案。'
    def validate(label):
        assert_sources();o=obj(BODY)
        if o.modifiers or not o.data.polygons:raise RuntimeError('尚未套用 Boolean 或結果為空')
        dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);mesh=ev.to_mesh()
        bm=bmesh.new();bm.from_mesh(mesh);bm.transform(o.matrix_world);bm.verts.ensure_lookup_table();bm.verts.index_update()
        vertices=list(bm.verts);seen=set();components=0
        for v in vertices:
            if v.index in seen:continue
            components+=1;stack=[v];seen.add(v.index)
            while stack:
                node=stack.pop()
                for edge in node.link_edges:
                    nxt=edge.other_vert(node)
                    if nxt.index not in seen:seen.add(nxt.index);stack.append(nxt)
        nonmanifold=sum(not e.is_manifold for e in bm.edges)
        volume=bm.calc_volume(signed=True);pts=[v.co.copy() for v in vertices]
        bbox=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
        tree=BVHTree.FromBMesh(bm); rays={}
        for name,x,z in [('holeFloor',0.,-12.5),('bossTop',3.,-5.5),('boxFloor',5.,-13.)]:
            hit,normal,idx,distance=tree.ray_cast(Vector((x,0,20)),Vector((0,0,-1)),100)
            rays[name]={'x':x,'z':float(hit.z) if hit else None,'expectedZ':z}
        outer_area=16*16*math.sin(math.pi/16)
        boss_volume=16*math.sin(math.pi/16)*(16*8-4*7)
        expected_volume=15552+boss_volume-.5*outer_area
        checks={'nonempty':len(vertices)>0,'closed':nonmanifold==0,'singleShell':components==1,
                'bounds':all(abs(a-b)<1e-4 for actual,expected in zip(bbox,[[-30,30],[-20,20],[-15,15]]) for a,b in zip(actual,expected)),
                'positiveVolume':volume>0,'volume':abs(volume-expected_volume)<0.05,
                'rays':all(v['z'] is not None and abs(v['z']-v['expectedZ'])<1e-4 for v in rays.values())}
        result={'label':label,'boundsMm':bbox,'vertices':len(vertices),'faces':len(bm.faces),
                'connectedComponents':components,'nonManifoldEdges':nonmanifold,'signedVolumeMm3':volume,
                'expectedVolumeMm3':expected_volume,'verticalRays':rays,'checks':checks,
                'sourceSha256':SOURCE_HASH,'dimensionsStatus':'demonstration draft',
                'hardware':None,'material':None,'physicalFit':None,'qualifiedHoleDiameter':None,'qualifiedStrength':None}
        bm.free();ev.to_mesh_clear();(out/(label+'-verification.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if not all(checks.values()):raise RuntimeError('幾何驗證失敗：'+json.dumps(checks))
        return '盒體與柱 Union：單一連通殼、非流形邊 0，孔底／柱頂／盒底射線與體積核對通過；非實體合格判定。'

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    do(lambda:key('O',ctrl=True),1.2);k.fill_dialog(str(copied)+'\\',source_copy.name);k.confirm_dialog(wait=3)
    k.record('08-boss','before','開啟盲孔柱與原盒場景的同雜湊副本，保留原本的兩個物件',before,park=PARK)
    # Alt+H restores the previously hidden reference box. Click row addresses are checked against the active object.
    do(lambda:key('H',alt=True),1)
    select_row(BOSS,162);move_z('-13.5mm')
    k.record('08-boss','positioned','顯示原盒，選柱並以 G Z −13.5 mm 與盒底重疊',positioned,park=PARK)
    select_row(BODY,102)
    search('Frame Selected');k.wheel_out(2)
    do(lambda:key('NUMPAD_7'),.3);do(lambda:key('NUMPAD_2'),.3);do(lambda:key('NUMPAD_2'),.3);do(lambda:key('NUMPAD_6'),.5)
    do(lambda:k.click(1245,503),.5)
    search('Add Boolean Modifier')
    do(lambda:k.click(1369,350),.4)
    do(lambda:k.click(1380,400),.4);do(lambda:k.type_text(BOSS),.4);do(lambda:key('RET'),.8)
    def assigned():
        mods=[m for m in obj(BODY).modifiers if m.type=='BOOLEAN']
        m=mods[0] if len(mods)==1 else None
        actual={'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
        state['booleanAssignment']=actual
        if actual!={'operation':'UNION','operand':BOSS,'solver':'EXACT'}:raise RuntimeError('Boolean UI 指定錯誤：'+str(actual))
        return 'Boolean UNION / EXACT，對象為既有盲孔柱；此時為預覽，尚未套用。'
    k.record('08-boss','boolean-preview','使用 Modifier UI 指定 Boolean Union 與既有盲孔柱',assigned,park=PARK)
    # Hide the operand via the eye icon in the Outliner, keeping it available to the modifier.
    do(lambda:k.click(1452,162),.7)
    select_row(BODY,102)
    do(lambda:k.click(1424,320),.4);k.menu_item(1331,343,.9)
    k.record('08-boss','union','套用 Boolean Union，讀回接合網格',lambda:validate('union'),park=PARK)
    k.file_dialog(163,k.demo_dir,FILENAME);k.confirm_dialog(wait=2)
    k.record('08-boss','saved','以新檔名另存示範場景，驗證幾何',lambda:validate('saved'),park=PARK)
    do(lambda:key('O',ctrl=True),1.2);k.fill_dialog(k.demo_dir,FILENAME);k.confirm_dialog(wait=3)
    k.record('08-boss','reopened','重新開啟新示範檔並再次核對接合網格',lambda:validate('reopened'),park=PARK)
    def summary():
        assert_sources(); state['outputScene']={'path':FILENAME,'sha256':g['sha256'](str(Path(k.demo_dir)/FILENAME))}
        state.update(hardware=None,material=None,physicalPrint=None,physicalFit=None,qualifiedHoleDiameter=None,qualifiedStrength=None)
        (out/'trial-summary.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    do(summary,.1)
