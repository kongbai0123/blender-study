"""05-05: UI-modelled one-piece lid with a recessed locating ring; trial gaps only."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import Kit, PARK, PROJECT
from lid_checks import read_body_and_validate, read_lid_and_validate

SOURCE = PROJECT / 'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend'
SOURCE_SHA = 'b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530'
FILENAME = 'u05_lid_v001.blend'


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    out = Path(g['OUT'])
    sources = Path(k.demo_dir) / 'sources'
    sources.mkdir()
    if g['sha256'](str(SOURCE)) != SOURCE_SHA:
        raise RuntimeError('Original box checkpoint hash differs')
    copy = sources / SOURCE.name
    copy.write_bytes(SOURCE.read_bytes())
    state = {}
    snapshot_dir = out / 'source-snapshot'
    snapshot_dir.mkdir()
    snapshots = []
    for relative in ('learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py', 'learning/tutor/scenarios/lesson05_lid.py',
                     'learning/tutor/scenarios/lid_checks.py'):
        source = PROJECT / relative
        target = snapshot_dir / source.name
        target.write_bytes(source.read_bytes())
        snapshots.append(dict(source=relative,snapshot='source-snapshot/'+source.name,sha256=g['sha256'](str(target))))
    (snapshot_dir/'manifest.json').write_text(json.dumps(dict(
        recordedAt=datetime.now(timezone.utc).isoformat(),files=snapshots,
        sourceScene=str(SOURCE),openedCopy=str(copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'trial-plan.json').write_text(json.dumps(dict(
        purpose='Geometry demonstration only, not qualified printed fit',
        selectedBy='tutor for this geometry demonstration, from the existing experimental range',
        body_outer_mm=[60,40,30],body_cavity_xy_mm=[56,36],body_demo_wall_mm=2,
        plate_mm=[60,40,2],lip_outer_mm=[55.6,35.6],lip_inner_mm=[51.6,31.6],lip_wall_mm=2,lip_depth_mm=4,
        total_clearance_mm=.4,per_side_clearance_mm=.2,status='experimental_geometry_only',
        printed=False,fit_tested=False,qualified_clearance_mm=None),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def guard():
        if g['sha256'](str(SOURCE)) != SOURCE_SHA or g['sha256'](str(copy)) != SOURCE_SHA:
            raise RuntimeError('Source checkpoint or source copy changed')
        k.guard()

    def body():
        return bpy.data.objects['Body']

    def lid():
        return bpy.data.objects['Lid']

    def body_fingerprint():
        obj=body()
        payload=dict(vertices=[list(v.co) for v in obj.data.vertices],
                     polygons=[list(p.vertices) for p in obj.data.polygons],
                     world=[list(row) for row in obj.matrix_world])
        return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

    def read_all():
        guard()
        bd=read_body_and_validate(body())
        ld=read_lid_and_validate(lid(),bd)
        if body_fingerprint()!=state['body_geometry_sha256']:
            raise RuntimeError('Source body geometry was edited')
        return bd,ld

    def size(obj):
        f=bpy.context.scene.unit_settings.scale_length*1000
        return '%s Dimensions %s、Location %s、Scale %s' % (
            obj.name,k.triple(obj.dimensions,' mm',f),k.triple(obj.location,' mm',f),k.triple(obj.scale,''))

    def transform(axis,amount):
        do(lambda:key('G',x=700,y=600),.2)
        do(lambda:key(axis),.2)
        do(lambda:k.type_text(amount),.2)
        do(lambda:key('RET'),.6)

    def modal(shortcut,amount):
        do(lambda:key(shortcut,x=700,y=600),.3)
        do(lambda:k.type_text(amount),.3)
        do(lambda:key('RET'),.7)

    def frame(notches=2):
        do(lambda:click(184,38),.4)
        k.menu_item(236,168,.7)
        k.wheel_out(notches)

    def project(point):
        a=k.area('VIEW_3D')
        region=next(r for r in a.regions if r.type=='WINDOW')
        p=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(point))
        if p is None:
            raise RuntimeError('Expected face is outside the viewport')
        return region.x+p.x,k.window().height-(region.y+p.y)

    def selected_face(width,height,z,normal_z=-1):
        bm=bmesh.from_edit_mesh(lid().data)
        selected=[face for face in bm.faces if face.select]
        if len(selected)!=1:
            raise RuntimeError('Expected one selected centre face, got %d'%len(selected))
        face=selected[0]
        factor=bpy.context.scene.unit_settings.scale_length*1000
        points=[lid().matrix_world@v.co for v in face.verts]
        xs=[p.x*factor for p in points];ys=[p.y*factor for p in points];zs=[p.z*factor for p in points]
        dims=[max(xs)-min(xs),max(ys)-min(ys)]
        if (any(not math.isclose(a,b,abs_tol=1e-4) for a,b in zip(dims,[width,height]))
                or any(not math.isclose(v,z,abs_tol=1e-4) for v in zs)
                or not math.isclose(face.normal.z,normal_z,abs_tol=1e-6)):
            raise RuntimeError('Selected face differs: XY%s Z%s normal%s'%(dims,zs,list(face.normal)))
        return '單一中心面：XY %s mm、Z %g mm、法線 Z %g。'%(k.triple(dims,''),sum(zs)/len(zs),face.normal.z)

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',copy.name)
    record('05-05','source-open-dialog','File > Open…，開啟既有盒體 v001 的同雜湊副本',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','既有盒體 v001'),k.fb_box('confirm','Open')],park=(300,400))
    k.confirm_dialog(2.0)
    k.click_outliner('Cube')
    k.rename_active('Body')

    def source_body():
        guard()
        if Path(bpy.data.filepath).resolve()!=copy.resolve():
            raise RuntimeError('Opened source path mismatch')
        bd=read_body_and_validate(body())
        state['body_geometry_sha256']=body_fingerprint()
        state['body_source']=bd
        (out/'source-body-verification.json').write_text(json.dumps(bd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return 'Body 實際外形 %s mm、內腔 %s mm、底厚 %g mm；體積 %g mm³；Non Manifold %d。'%(
            bd['outer_dimensions_mm'],bd['cavity_dimensions_mm'],bd['floor_thickness_mm'],bd['volume_mm3'],bd['non_manifold_edges'])

    record('05-05','source-body-checked','將工作副本的 Cube 命名 Body，從實際網格重驗原盒外形、內腔、底厚',
           source_body,highlights=k.boxes(k.outliner_box('Body','原盒 Body')),park=PARK,
           note='2 mm 是沿用既有盒體的示範壁厚，沒有把它或 0.4 mm 噴嘴當成已驗證製造條件。')
    do(lambda:key('H',x=700,y=600),.5)
    k.add_mesh(80,.6)
    for y,value in ((411,'60mm'),(430,'40mm'),(450,'2mm')):
        k.type_into(1075,y,value)
    transform('Z','16mm')
    do(lambda:click(313,38),.4)
    do(lambda:move(336,141),.5)
    k.menu_item(533,180,.6)
    k.rename_active('Lid')
    frame(2)

    def blank():
        f=bpy.context.scene.unit_settings.scale_length*1000
        if any(not math.isclose(a*f,b,abs_tol=1e-4) for a,b in zip(lid().dimensions,[60,40,2])):
            raise RuntimeError('Lid plate dimensions were not entered')
        if not math.isclose(lid().location.z*f,16,abs_tol=1e-4) or not body().hide_get():
            raise RuntimeError('Plate position or body visibility differs')
        return size(lid())+'；板底 Z 15、板頂 Z 17 mm，Body 暫時隱藏。'

    record('05-05','plate','隱藏 Body，Add > Mesh > Cube；Dimensions 設 60 × 40 × 2 mm，G Z 16mm，Apply Scale，命名 Lid',
           blank,highlights=[B(963,318,228,142,'蓋板 60 × 40 × 2 mm / Scale 1')],park=PARK)
    do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.5)
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('THREE',x=700,y=600),.3)
    do(lambda:click(280,38),.4)
    k.menu_item(303,81,.4)
    do(lambda:click(*project((0,0,15))),.5)
    record('05-05','bottom-face','Ctrl + 數字鍵盤 7 底視；Tab 進 Edit Mode，面選取、Select None，再點蓋板底面',
           lambda:selected_face(60,40,15),highlights=[B(49,28,96,20,'Edit Mode')],park=PARK)
    modal('I','2.2mm')
    record('05-05','lip-footprint','I 內插 2.2mm：由 60 × 40 mm 板底留下 55.6 × 35.6 mm 唇邊外形',
           lambda:selected_face(55.6,35.6,15),park=PARK,
           note='56 − 2 × 0.2 = 55.6；36 − 2 × 0.2 = 35.6 mm。總間隙 0.4、每側 0.2 是助教選用的幾何試驗值。')
    modal('E','4mm')
    record('05-05','lip-depth','E 4mm 沿底面向下延伸：唇邊深 4 mm，選面到 Z 11 mm',
           lambda:selected_face(55.6,35.6,11),park=PARK)
    modal('I','2mm')
    record('05-05','lip-wall','I 2mm：保留 2 mm 環壁，內側中心面為 51.6 × 31.6 mm',
           lambda:selected_face(51.6,31.6,11),park=PARK)
    modal('E','-4mm')
    record('05-05','lip-recess','E -4mm 把中心面推回 Z 15 mm，形成盲內凹與環形唇邊',
           lambda:selected_face(51.6,31.6,15),park=PARK,
           note='這是與蓋板一體的定位環，不是整塊實心塞。最終整個 Lid 高 6 mm，分別是板厚 2 與唇深 4 mm。')
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('NUMPAD_2',x=700,y=600),.4)
    do(lambda:key('NUMPAD_2',x=700,y=600),.4)
    do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def lid_read():
        bd,ld=read_all()
        return 'Lid 整體 %s mm；板厚 %g、唇外 %s、唇內 %s、環壁 %g、唇深 %g mm；體積 %g mm³、Non Manifold %d。'%(
            ld['dimensions_mm'],ld['plate_thickness_mm'],ld['ring_outer_mm'],ld['ring_inner_mm'],ld['ring_wall_mm'],ld['ring_depth_mm'],ld['volume_mm3'],ld['non_manifold_edges'])

    record('05-05','underside-checked','回 Object Mode，改底部斜視，從最終網格核對板厚、唇內外尺寸、環壁與深度',
           lid_read,highlights=[B(963,383,228,77,'Lid 整體高 6 mm，板厚另讀 2 mm')],park=PARK)
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('TWO',x=700,y=600),.3)
    do(lambda:click(280,38),.3)
    k.menu_item(303,81,.4)
    do(lambda:key('F3',x=700,y=600),.3)
    do(lambda:k.type_text('Select Non Manifold'),.3)
    do(lambda:key('RET'),.6)

    def selected_edges():
        bm=bmesh.from_edit_mesh(lid().data)
        if not bm.faces or not bm.verts:
            raise RuntimeError('Empty model cannot pass')
        n=sum(not e.is_manifold for e in bm.edges); selected=sum(e.select for e in bm.edges)
        if n or selected:
            raise RuntimeError('Non Manifold selection failed')
        return 'Lid Edit Mode，Non Manifold 0、選到邊 0；網格非空。'

    record('05-05','non-manifold','邊選取、Select None，再 F3 搜尋 Select Non Manifold',selected_edges,park=PARK)
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('H',alt=True,x=700,y=600),.5)
    k.click_outliner('Lid')
    transform('Z','12mm')
    k.click_outliner('Body',ctrl=True)
    do(lambda:key('NUMPAD_1',x=700,y=600),.4)
    do(lambda:key('NUMPAD_6',x=700,y=600),.3)
    do(lambda:key('NUMPAD_8',x=700,y=600),.4)
    frame(1)
    record('05-05','separated-view','暫將 Lid 上移 12 mm，與 Body 一起對焦，查看蓋板、定位環及盒口的關係',
           lambda:size(lid())+'；這張暫時分離檢視，尚未存檔；下一步會移回名義位置。',park=PARK,
           note='這是實際 Blender 視角與暫時位置，不是合成圖，也不是實體試配結果。')
    k.click_outliner('Lid')
    transform('Z','-12mm')
    k.click_outliner('Body',ctrl=True)
    frame(1)

    def assembled():
        bd,ld=read_all()
        a=ld['assembly']
        state['body']=bd;state['lid']=ld
        return '已回名義位置；實際四側間隙 %s mm、XY 總間隙 %s mm、嵌入深度 %g mm；僅 CAD 幾何預覽。'%(
            a['per_side_clearances_mm'],a['total_clearances_mm'],a['engagement_mm'])

    record('05-05','assembly-geometry','Lid 下移 12 mm 回到板底 Z 15、唇底 Z 11；讀回四側試驗間隙與嵌入深度',
           assembled,park=PARK,note='幾何位置符合本次試驗設計；尚未列印或實際試配，正式合格間隙仍為 null。')
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('05-05','save-dialog','File > Save As…，另存 u05_lid_v001.blend；不覆寫原盒',
           lambda:'目標 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','上蓋場景 v001'),k.fb_box('confirm','Save As')],park=(300,400))

    def safe_target():
        folder,name=k.browser();target=(Path(folder)/name).resolve()
        if target.parent!=Path(k.demo_dir).resolve() or name!=FILENAME or target.exists():
            raise RuntimeError('Unsafe or existing scene version')
        guard()
    do(safe_target,.1)
    k.confirm_dialog(1.8)

    def saved():
        path=Path(bpy.data.filepath).resolve()
        if path!=(Path(k.demo_dir)/FILENAME).resolve() or not path.is_file():
            raise RuntimeError('Lid scene not saved to expected new path')
        read_all()
        state['scene_path']=str(path);state['scene_sha256']=g['sha256'](str(path))
        return '已存 '+path.name+'，%d bytes，SHA-256 '%path.stat().st_size+state['scene_sha256']+'；原盒與來源副本雜湊未變。'

    record('05-05','saved','按 Save As，核對新場景檔案與雜湊',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('05-05','open-saved','File > Open…，重新開啟同一上蓋場景 v001',
           lambda:'目標 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','同一上蓋 v001'),k.fb_box('confirm','Open')],park=(300,400))
    k.confirm_dialog(2.0)

    def reopened():
        path=Path(bpy.data.filepath).resolve()
        if str(path)!=state['scene_path'] or g['sha256'](str(path))!=state['scene_sha256']:
            raise RuntimeError('Reopened scene/hash differs')
        bd,ld=read_all()
        result=dict(passed=True,kind='lid_geometry_demo',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
                    opened_scene_path=str(copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
                    source_body_geometry_unchanged=True,scene_path=str(path),scene_sha256=state['scene_sha256'],reopened=True,
                    body=bd,lid=ld,trial=dict(status='experimental_geometry_only',selected_by='tutor',
                    total_clearance_mm=.4,per_side_clearance_mm=.2,qualified_clearance_mm=None),
                    printed=False,fit_tested=False,physical_measurements=None,fit_results=None,qualified_clearance_mm=None,
                    numericComparison=dict(dimensionsAbsMm=1e-4,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing tolerance or qualification of printed fit'))
        (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return '重開後原盒 60 × 40 × 30、板厚 2、唇深 4、唇外 55.6 × 35.6 mm；四側試驗間隙各約 0.2 mm、拓樸與雜湊一致。未列印、未試配、無合格值。'

    record('05-05','reopened-verified','按 Open，從實際最終網格重新驗上蓋、定位環與原盒，保存 verification.json',
           reopened,park=PARK,note='本次是幾何示範；學員完成狀態維持共用 progress.json，不自動確認。')
