"""GUI mount of a separately audited thread; program append is disclosed.

Never run until the v010 independent audit confirms no BVH candidates and no
very thin triangles under the recorded diagnostic threshold.
"""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import Kit, PROJECT

BOX = PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
BOX_SHA = 'ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
THREAD = PROJECT/'learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/demo-files/u08_external_gui_draft_v003.blend'
AUDIT = PROJECT/'learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/independent-audit-v001.json'

def build(g):
    k=Kit(g); out=Path(g['OUT'])
    if g['sha256'](BOX)!=BOX_SHA: raise RuntimeError('Box scene hash mismatch')
    audit=json.loads(AUDIT.read_text(encoding='utf8'))
    if audit['nonAdjacentTriangleOverlapPairs'] or audit['triangleAreasBelow1eMinus5Mm2'] or audit['nonManifoldEdges'] or audit['connectedComponents']!=1 or audit['sceneSha256']!=g['sha256'](THREAD):
        raise RuntimeError('Thread has not passed prerequisite diagnostics; do not mount')
    source_sha=g['sha256'](THREAD)
    copy=Path(k.demo_dir)/BOX.name; copy.write_bytes(BOX.read_bytes())
    def send(key,**kw): k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
    def typed(keys,value):
        for key in keys: send(key)
        k.do(lambda:k.type_text(value),.35);send('RET')
    def prepare():
        # Append a verified object, not generated geometry; subsequent placement
        # and union are performed by GUI events. Do not modify either source.
        with bpy.data.libraries.load(str(THREAD),link=False) as (src,dst):
            if 'Thread_Core' not in src.objects:raise RuntimeError('Thread_Core missing')
            dst.objects=['Thread_Core']
        obj=dst.objects[0];bpy.data.objects['Body'].users_collection[0].objects.link(obj)
        obj.hide_set(False); bpy.data.objects['Body'].hide_set(False); bpy.data.objects['Lid'].hide_set(False)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.context.view_layer.update()
    def bounds(obj):
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
    def tree(obj):
        m=obj.data; vertices=[obj.matrix_world@v.co for v in m.vertices]
        return BVHTree.FromPolygons(vertices,[tuple(poly.vertices) for poly in m.polygons])
    def body_check(stage):
        body=bpy.data.objects['Body']; lid=bpy.data.objects['Lid'];bm=bmesh.new();bm.from_mesh(body.data)
        remaining=set(bm.verts); comps=0
        while remaining:
            comps+=1;stack=[remaining.pop()]
            while stack:
                for e in stack.pop().link_edges:
                    for v in e.verts:
                        if v in remaining:remaining.remove(v);stack.append(v)
        bvh=tree(body); ray=[]
        for y,z in [(0,0),(2,2),(-2,-2),(8,4),(-8,-4)]:
            point,_,_,_=bvh.ray_cast(Vector((0,y,z)),Vector((1,0,0)),100)
            ray.append({'origin':[0,y,z],'hit':list(point) if point else None})
        result={'stage':stage,'bodyBounds':bounds(body),'lidBounds':bounds(lid),'bodyVertices':len(bm.verts),'bodyFaces':len(bm.faces),
                'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),
                'components':comps,'innerCavityRayHits':ray,'threadSourceSha256':source_sha,'boxSourceSha256':BOX_SHA,
                'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedStrength':None,'qualifiedClearance':None}
        bm.free();(out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
        if result['boundaryEdges'] or result['nonManifoldEdges'] or result['components']!=1: raise RuntimeError('Body topology failed '+json.dumps(result))
        if any(r['hit'] is None or abs(r['hit'][0]-28)>1e-3 for r in ray):raise RuntimeError('Interior wall rays differ '+json.dumps(result))
        return json.dumps(result)
    def thread_check(stage):
        obj=bpy.data.objects['Thread_Core']; actual=bounds(obj)
        result={'stage':stage,'threadBounds':actual,'location':list(obj.location),'lidBounds':bounds(bpy.data.objects['Lid']),'bodyBounds':bounds(bpy.data.objects['Body'])}
        if stage=='placed':
            expected=[[29.5,34.3],[-6,6],[-6,6]]
            if any(abs(a-b)>0.002 for row,want in zip(actual,expected) for a,b in zip(row,want)): raise RuntimeError('Mount placement failed '+json.dumps(result))
        return json.dumps(result)
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3);k.do(prepare,1)
    k.record('MNT','appended','程式將已稽核外牙物件載入既有盒蓋複本；未用程式生成此幾何。',lambda:thread_check('appended'))
    typed(['R','Y'],'90');k.record('MNT','rotated','GUI 將牙軸由 Z 轉向 X。',lambda:thread_check('rotated'))
    typed(['R','X'],'11.25');k.record('MNT','phase','GUI 繞牙軸 X 再旋轉 11.25 度，改變牙條端部與盒壁的接合相位。',lambda:thread_check('phase'))
    typed(['G','X'],'31.9mm');typed(['G','Z'],'-2.3mm')
    k.record('MNT','placed','GUI 將牙根嵌入盒右外壁 0.5 mm；不代表內牙或配合合格。',lambda:thread_check('placed'))
    k.click_outliner('Body');send('F3');k.do(lambda:k.type_text('Add Boolean Modifier'),.5);send('RET')
    k.do(lambda:k.click(1369,k.props_y(143)),.5)
    k.do(lambda:k.click(1380,k.props_y(193)),.4);k.do(lambda:k.type_text('Thread_Core'),.4);send('RET')
    def assignment():
        o=bpy.data.objects['Body']; m=next((m for m in o.modifiers if m.type=='BOOLEAN'),None)
        return {'operation':m.operation if m else None,'operand':m.object.name if m and m.object else None,'solver':m.solver if m else None}
    k.record('MNT','assignment-probe','GUI 指定布林對象，先讀回是否生效。',lambda:json.dumps(assignment()))
    def try_assigned(attempt=0):
        actual=assignment()
        if actual=={'operation':'UNION','operand':'Thread_Core','solver':'EXACT'}:return
        if attempt>=2:raise RuntimeError('Boolean assignment failed '+str(actual))
        y=k.props_y(193)
        g['queue'][0:0]=[(lambda:k.move(1380,y),.3),(lambda:k.click(1380,y),.4),
          (lambda:k.key('A',ctrl=True,x=700,y=500),.2),(lambda:k.type_text('Thread_Core'),.4),
          (lambda:k.move(1310,y+32),.3),(lambda:k.click(1310,y+32),.6),(lambda:try_assigned(attempt+1),.1)]
    k.do(try_assigned,.1)
    k.record('MNT','preview','GUI 選擇 Union/Exact 和 Thread_Core，讀回設定。',lambda:json.dumps(assignment()))
    # Hide separate operand using a visual Outliner click; coordinate checked by screenshot when needed.
    k.do(lambda:k.click(1452,k.outliner_y('Thread_Core')),.7)
    def hidden():
        if not bpy.data.objects['Thread_Core'].hide_get():raise RuntimeError('Operand not hidden')
        return 'GUI 已隱藏工具物件，仍保留其資料。'
    k.record('MNT','operand-hidden','GUI 隱藏牙條工具。',hidden)
    k.do(lambda:k.click(1424,k.props_y(113)),.4);k.menu_item(1331,k.props_y(136),.9)
    k.record('MNT','union','GUI 套用 Union；後續必須獨立檢查整體網格。',lambda:body_check('union'))
    send('F3');k.do(lambda:k.type_text('Frame Selected'),.4);send('RET')
    k.record('MNT','framed','GUI 聚焦盒體，保留可見的上蓋與外側接口。',lambda:body_check('framed'))
    k.file_dialog(163,k.demo_dir,'u11_box_external_thread_draft_v002.blend');k.confirm_dialog(wait=3)
    k.record('MNT','saved','GUI 另存新版本；檔案欄位由程式填入。',lambda:body_check('saved'))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u11_box_external_thread_draft_v002.blend');k.confirm_dialog(wait=4)
    k.record('MNT','reopened','GUI 重開並再次讀值；實際列印與試配留空。',lambda:body_check('reopened'))
