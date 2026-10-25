"""07-01: inspect an unchanged box through UI; record pending cantilever parameters."""
import json
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import Kit, PARK, PROJECT
from tenon_checks import read_mesh_data
from lid_checks import validate_body_mesh

SOURCE = PROJECT/'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend'
SOURCE_SHA = 'b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530'
TEMPLATE = 'learning/plans/07-01-cantilever-parameters-v001.json'
FACTS = 'sources/engineering/snapfit-source-facts-v001.json'
FILENAME = 'u07_snap_reference_v001.blend'


def build(g):
    k = Kit(g)
    do, click, key, record = k.do, k.click, k.key, k.record
    out = Path(g['OUT'])
    sources = Path(k.demo_dir)/'sources'
    sources.mkdir()
    if g['sha256'](str(SOURCE)) != SOURCE_SHA:
        raise RuntimeError('Original box checkpoint changed')
    source_copy = sources/SOURCE.name
    source_copy.write_bytes(SOURCE.read_bytes())
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    files, data = [], []
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson07_parameters.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/tenon_checks.py'):
        target = snapshots/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    for relative, name in ((TEMPLATE,'parameter-template-v001.json'),(FACTS,'snapfit-source-facts-v001.json')):
        target = snapshots/name
        target.write_bytes((PROJECT/relative).read_bytes())
        data.append(dict(source=relative,snapshot='source-snapshot/'+name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=files,dataBindings=data,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    template = json.loads((snapshots/'parameter-template-v001.json').read_text('utf-8'))
    state = dict(face_measurements={})

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        if any(g['sha256'](str(p)) != SOURCE_SHA for p in (SOURCE,source_copy)):
            raise RuntimeError('Original scene or opened copy changed')

    def read_body(name, filename):
        unchanged()
        raw = read_mesh_data(bpy.data.objects[name])
        write(filename,raw)
        cad = raw['cad_metadata']
        if cad['scale'] != [1,1,1] or cad['modifier_count'] or cad['length_unit'] != 'MILLIMETERS' or abs(cad['unit_scale']-.001)>1e-9:
            raise RuntimeError('Expected applied millimetre reference mesh')
        return validate_body_mesh(raw['vertices'],raw['triangles'])

    def frame():
        do(lambda:click(184,38),.35)
        k.menu_item(236,168,.6)
        k.wheel_out(1)

    def project(point):
        a=k.area('VIEW_3D')
        region=next(r for r in a.regions if r.type=='WINDOW')
        p=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(point))
        if p is None:
            raise RuntimeError('Reference face is outside viewport')
        return region.x+p.x,k.window().height-(region.y+p.y)

    def select_face(point):
        do(lambda:key('A',alt=True,x=700,y=600),.3)
        do(lambda:click(*project(point)),.5)

    def face_read(role, expected_min, expected_max):
        obj=bpy.data.objects['Body_Reference']
        bm=bmesh.from_edit_mesh(obj.data)
        selected=[f for f in bm.faces if f.select]
        if len(selected)!=1 or len(selected[0].verts)!=4:
            raise RuntimeError('Expected exactly one reference quadrilateral')
        factor=bpy.context.scene.unit_settings.scale_length*1000
        vertices=[[c*factor for c in (obj.matrix_world@v.co)] for v in selected[0].verts]
        bounds=dict(min=[min(p[a] for p in vertices) for a in range(3)],max=[max(p[a] for p in vertices) for a in range(3)])
        item=dict(object_name=obj.name,selected_face_count=1,selected_vertex_count=4,vertices_mm=vertices,
                  bounds_mm=bounds,spans_mm=[bounds['max'][a]-bounds['min'][a] for a in range(3)])
        state['face_measurements'][role]=item
        write('face-measurements.json',state['face_measurements'])
        if any(abs(a-b)>1e-4 for a,b in zip(bounds['min']+bounds['max'],expected_min+expected_max)):
            raise RuntimeError('Actual selected face bounds differ: '+str(item))
        return '%s：實選 1 面／4 頂點，world min %s、max %s mm；跨度 %s mm。'%(role,bounds['min'],bounds['max'],item['spans_mm'])

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',source_copy.name)
    record('07-01','source-open-dialog','File > Open…：開啟原 04 盒體的同雜湊副本',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','原盒 v001 副本'),k.fb_box('confirm','Open')],park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Cube')

    def source_read():
        if Path(bpy.data.filepath).resolve()!=source_copy.resolve():
            raise RuntimeError('Source copy was not opened')
        state['source_body']=read_body('Cube','source_body_mesh.json')
        return '原盒外形 %s、內腔 %s mm；壁／底 2 mm、體積 %g mm³、Non Manifold %d。'%(state['source_body']['outer_dimensions_mm'],state['source_body']['cavity_dimensions_mm'],state['source_body']['volume_mm3'],state['source_body']['non_manifold_edges'])

    record('07-01','source-checked','Object Mode：選 Cube，從實際網格重驗原盒基準',source_read,
           highlights=[k.box(963,383,228,77,'原盒外形 60 × 40 × 30 mm')],park=PARK,
           note='本步只整理參數。沒有卡扣臂，也沒有材料或強度結果。')
    for name in ('Camera','Light'):
        k.click_outliner(name)
        do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Cube')
    k.rename_active('Body_Reference')
    do(lambda:key('NUMPAD_7',x=700,y=600),.4)
    frame()
    record('07-01','reference-top','隱藏 Camera／Light；UI 改名 Body_Reference，數字鍵盤 7 頂視並 Frame Selected',
           lambda:k.size('Body_Reference',' mm',bpy.context.scene.unit_settings.scale_length*1000),park=PARK,
           note='這是原盒的獨立卡扣參考分支；不承接燕尾導軌、定位柱或 0.4 mm 燕尾間隙。')
    do(lambda:key('TAB',x=700,y=600),.3)
    do(lambda:key('THREE',x=700,y=600),.3)
    select_face((0,-19,15))
    record('07-01','rim-face','Edit Mode 面選取：點前側盒口環面，讀回 world Y 邊界',
           lambda:face_read('rim',[-30,-20,15],[30,-18,15]),park=PARK,
           note='Y −20 至 −18 的平面跨度是原盒壁厚參考 2 mm；角落斜邊不是 2 mm。這不是卡扣臂 h。')
    select_face((0,0,-13))
    record('07-01','inner-floor','頂視面選取：取消前一面，點內腔底面，記錄其 world Z',
           lambda:face_read('inner_floor',[-28,-18,-13],[28,18,-13]),park=PARK,
           note='內底 world Z −13 mm；面跨度 56 × 36。先保留卡扣位置、彎曲方向及讓位空間待定。')
    do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.4)
    select_face((0,0,-15))
    record('07-01','outer-floor','Ctrl + 數字鍵盤 7 底視：點外底面，與內底 Z 分開記錄',
           lambda:face_read('outer_floor',[-30,-20,-15],[30,20,-15]),park=PARK,
           note='外底 Z −15 與內底 Z −13 相差 2 mm；只驗盒體基準，不推定臂厚或允許應變。')
    do(lambda:key('TWO',x=700,y=600),.3)
    do(lambda:key('A',alt=True,x=700,y=600),.3)
    do(lambda:key('F3',x=700,y=600),.3)
    do(lambda:k.type_text('Select Non Manifold'),.3)
    do(lambda:key('RET'),.6)

    def non_manifold():
        bm=bmesh.from_edit_mesh(bpy.data.objects['Body_Reference'].data)
        selected=sum(e.select for e in bm.edges)
        actual=sum(not e.is_manifold for e in bm.edges)
        if not bm.faces or selected or actual:
            raise RuntimeError('Reference Non Manifold check failed')
        state['non_manifold_selected_edges']=selected
        return '實際 Select Non Manifold：選到 0 邊；實網格 Non Manifold 0。這不是強度或製程判定。'

    record('07-01','non-manifold','邊選取、Alt+A，再 F3 > Select Non Manifold',non_manifold,park=PARK)
    do(lambda:key('TAB',x=700,y=600),.4)
    do(lambda:key('NUMPAD_7',x=700,y=600),.3)
    do(lambda:key('NUMPAD_2',x=700,y=600),.3)
    do(lambda:key('NUMPAD_2',x=700,y=600),.3)
    do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def reference_read():
        result=read_body('Body_Reference','reference_body_mesh.json')
        if result!=state['source_body']:
            raise RuntimeError('Box geometry changed during parameter inspection')
        state['reference_body']=result
        return '參考盒仍為 60 × 40 × 30／內腔 56 × 36 × 28、壁底 2 mm；臂長 L、臂厚 h、寬 b、u、δ_req、材料及 ε_allow 均待定；尚未計算。'

    record('07-01','reference-overview','回 Object Mode，改斜視；讀回完整原盒網格未變',reference_read,park=PARK,
           note='07-01 只建立參數與估算條件紀錄；07-02 才進行卡扣建模。')
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('07-01','save-dialog','File > Save As…：另存原盒卡扣參考場景 u07_snap_reference_v001.blend',
           lambda:'目標 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','只有原盒的參考版本 v001'),k.fb_box('confirm','Save As')],park=(300,400))

    def safe_target():
        folder,name=k.browser()
        target=(Path(folder)/name).resolve()
        if target.parent!=Path(k.demo_dir).resolve() or name!=FILENAME or target.exists():
            raise RuntimeError('Unsafe or existing reference scene version')
        unchanged()
    do(safe_target,.1)
    k.confirm_dialog(1.8)

    def saved():
        path=Path(bpy.data.filepath).resolve()
        if path!=(Path(k.demo_dir)/FILENAME).resolve() or not path.is_file():
            raise RuntimeError('Reference scene was not saved')
        reference_read()
        state.update(scene_path=str(path),scene_sha256=g['sha256'](str(path)),scene_bytes=path.stat().st_size)
        return '已另存原盒參考場景，%d bytes，SHA-256 %s；原檔／讀取副本未變。'%(state['scene_bytes'],state['scene_sha256'])
    record('07-01','saved','按 Save As，核對新檔路徑、bytes 與 SHA-256',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('07-01','open-saved','File > Open…：重開剛才的原盒參考版本',
           lambda:'目標 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','同一參考版本 v001'),k.fb_box('confirm','Open')],park=(300,400))
    k.confirm_dialog(2)

    def reopened():
        path=Path(bpy.data.filepath).resolve()
        if str(path)!=state['scene_path'] or g['sha256'](str(path))!=state['scene_sha256']:
            raise RuntimeError('Reference reopen path/hash differs')
        reference_read()
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        if [o.name for o in meshes]!=['Body_Reference'] or any(not bpy.data.objects[n].hide_get() for n in ('Camera','Light')):
            raise RuntimeError('Expected only one unchanged reference box mesh')
        plan=dict(template,recordedAt=datetime.now(timezone.utc).isoformat(),
                  source_scene=dict(path=str(SOURCE),sha256=SOURCE_SHA),
                  reference_scene=dict(path=str(path),sha256=state['scene_sha256'],bytes=state['scene_bytes'],scene_role='unmodified_box_reference'),
                  measured_box=state['reference_body'],face_measurements=state['face_measurements'])
        write('parameter-record-v001.json',plan)
        result=dict(passed=True,kind='snapfit_parameter_reference',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
                    opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
                    source_body_geometry_unchanged=True,source_body=state['source_body'],reference_body=state['reference_body'],
                    scene_path=str(path),scene_sha256=state['scene_sha256'],scene_bytes=state['scene_bytes'],scene_role='unmodified_box_reference',
                    reopened=True,snap_arm_modeled=False,face_measurements=state['face_measurements'],
                    non_manifold_selected_edges=state['non_manifold_selected_edges'],
                    parameter_record_path=str(out/'parameter-record-v001.json'),parameter_record_sha256=g['sha256'](str(out/'parameter-record-v001.json')),
                    calculations_performed=False,strength_analysis_performed=False,fit_qualification=False,
                    printed=False,fit_tested=False,slicer_checked=False,exported=False,
                    physical_measurements=None,fit_results=None,qualified_strength_N=None,qualified_clearance_mm=None,
                    numericComparison=dict(dimensionsAbsMm=1e-4,purpose='Floating point reconstruction only; not manufacturing tolerance or strength/fit qualification'))
        write('verification.json',result)
        return '重開實測與來源一致：60 × 40 × 30、壁底 2 mm／NM 0；只有原盒。參數表 v001 已綁定場景 hash；材料／ε_allow／估算／列印／試配結果留空。'
    record('07-01','reopened-verified','按 Open：重驗未修改原盒，保存參數表、三個實選面座標及 verification.json',reopened,park=PARK,
           note='助教準備完成不等於學員已完成；不更新 progress、不做強度或配合合格判定。')
