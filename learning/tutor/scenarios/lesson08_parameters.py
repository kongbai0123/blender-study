"""08-01: inspect an unchanged box through UI; record pending thread specifications."""
import hashlib
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
TEMPLATE = 'learning/plans/08-01-thread-parameters-v001.json'
TEMPLATE_SHA = '92c0bf94ede81a48a5c16179ae1558bb8c61c521f960c79cd4ad05830f0d79bb'
FACTS = 'sources/engineering/thread-source-facts-v001.json'
FACTS_SHA = '78a0b7b1092287e7956b9a11da17f4b1ef838c7da50473e989d05cc759b67834'
FILENAME = 'u08_thread_reference_v001.blend'


def build(g):
    return _build(g,False)


def build_probe(g):
    return _build(g,True)


def _build(g,probe):
    k = Kit(g)
    do, click, key, record = k.do, k.click, k.key, k.record
    out = Path(g['OUT'])
    sources = Path(k.demo_dir)/'sources'
    sources.mkdir()
    fixed=((SOURCE,SOURCE_SHA),(PROJECT/TEMPLATE,TEMPLATE_SHA),(PROJECT/FACTS,FACTS_SHA))
    for path,digest in fixed:
        if g['sha256'](str(path))!=digest:raise RuntimeError('Protected source/template/facts changed: '+str(path))
    source_copy = sources/SOURCE.name
    source_copy.write_bytes(SOURCE.read_bytes())
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    files, data = [], []
    dependencies=['learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson08_parameters.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/tenon_checks.py']
    if probe:dependencies.append('learning/tutor/scenarios/lesson08_parameters_probe.py')
    for relative in dependencies:
        target = snapshots/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    for relative, name in ((TEMPLATE,'parameter-template-v001.json'),(FACTS,'thread-source-facts-v001.json')):
        target = snapshots/name
        target.write_bytes((PROJECT/relative).read_bytes())
        data.append(dict(source=relative,snapshot='source-snapshot/'+name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=files,dataBindings=data,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    template = json.loads((snapshots/'parameter-template-v001.json').read_text('utf-8'))
    if len(template.get('draft_parameters',[]))!=24 or any(p.get('value') is not None or p.get('status')!='draft_pending' for p in template['draft_parameters']):
        raise RuntimeError('Thread draft must have 24 pending/unmodelled parameters')
    if template['route']['selected'] is not None or template['route']['selection_status']!='pending_user_choice':
        raise RuntimeError('Thread route has not been selected by the learner')
    if template['blender_mapping']['modifier_created'] is not False or any(template['blender_mapping'][key] is not None for key in ('angle_degrees','axis','axis_object','object_screw','screw_offset_mm','iterations','steps_viewport','steps_render','merge_distance_mm','evaluated_export_mode')):
        raise RuntimeError('Modifier mapping must remain documented only and unconfigured')
    state = dict(face_measurements={})

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        for path,digest in fixed+((source_copy,SOURCE_SHA),):
            if g['sha256'](str(path))!=digest:raise RuntimeError('Source, copy, parameter template or source facts changed: '+str(path))

    def read_body(name, filename):
        unchanged()
        obj=bpy.data.objects[name]
        raw = read_mesh_data(obj)
        shape=dict(vertices=[list(v.co) for v in obj.data.vertices],polygons=[list(p.vertices) for p in obj.data.polygons])
        raw['cad_metadata'].update(matrix_world=[list(row) for row in obj.matrix_world],object_rotation_euler_radians=list(obj.rotation_euler),
            mesh_data_name=obj.data.name,local_mesh_sha256=hashlib.sha256(json.dumps(shape,separators=(',',':')).encode()).hexdigest())
        if name=='Cube':state['source_raw']=raw
        elif 'source_raw' in state:
            old=state['source_raw']
            if any(raw[key]!=old[key] for key in ('vertices','triangles')) or any(raw['cad_metadata'][key]!=old['cad_metadata'][key] for key in ('matrix_world','scale','modifier_count','local_mesh_sha256')):
                raise RuntimeError('Reference box raw geometry or object transform changed')
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
    record('08-01','source-open-dialog','File > Open…：開啟原 04 盒體的同雜湊副本',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',
           highlights=lambda:[k.fb_box('name','原盒 v001 副本'),k.fb_box('confirm','Open')],park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Cube')

    def source_read():
        if Path(bpy.data.filepath).resolve()!=source_copy.resolve():
            raise RuntimeError('Source copy was not opened')
        state['source_body']=read_body('Cube','source_body_mesh.json')
        return '原盒外形 %s、內腔 %s mm；壁／底 2 mm、體積 %g mm³、Non Manifold %d。'%(state['source_body']['outer_dimensions_mm'],state['source_body']['cavity_dimensions_mm'],state['source_body']['volume_mm3'],state['source_body']['non_manifold_edges'])

    record('08-01','source-checked','Object Mode：選 Cube，從實際網格重驗原盒基準',source_read,
           highlights=[k.box(963,383,228,77,'原盒外形 60 × 40 × 30 mm')],park=PARK,
           note='本步只整理螺紋規格與建模參數；沒有牙、柱、導孔或配對件，也沒有材料或強度結果。')
    for name in ('Camera','Light'):
        k.click_outliner(name)
        do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Cube')
    k.rename_active('Body_Reference')
    do(lambda:key('NUMPAD_7',x=700,y=600),.4)
    frame()
    record('08-01','reference-top','隱藏 Camera／Light；UI 改名 Body_Reference，數字鍵盤 7 頂視並 Frame Selected',
           lambda:k.size('Body_Reference',' mm',bpy.context.scene.unit_settings.scale_length*1000),park=PARK,
           note='這是從原04盒另建的螺紋參照分支；完整盒形不變，沒有承接卡扣、燕尾或已核准螺紋間隙。')
    do(lambda:key('TAB',x=700,y=600),.3)
    do(lambda:key('THREE',x=700,y=600),.3)
    select_face((0,-19,15))
    record('08-01','rim-face','Edit Mode 面選取：點前側盒口環面，讀回 world Y 邊界',
           lambda:face_read('rim',[-30,-20,15],[30,-18,15]),park=PARK,
           note='Y −20 至 −18 的平面跨度是原盒壁厚參考 2 mm；角落斜邊不是 2 mm。這不是螺紋柱肉厚或合格條件。')
    select_face((0,0,-13))
    record('08-01','inner-floor','頂視面選取：取消前一面，點內腔底面，記錄其 world Z',
           lambda:face_read('inner_floor',[-28,-18,-13],[28,18,-13]),park=PARK,
           note='內底 world Z −13 mm；面跨度 56 × 36。螺紋路線、位置、對件及尺寸均待定，原盒內底保持。')
    do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.4)
    select_face((0,0,-15))
    record('08-01','outer-floor','Ctrl + 數字鍵盤 7 底視：點外底面，與內底 Z 分開記錄',
           lambda:face_read('outer_floor',[-30,-20,-15],[30,20,-15]),park=PARK,
           note='外底 Z −15 與內底 Z −13 相差 2 mm；只驗盒體基準，不推定螺紋尺寸、柱肉厚或允許扭矩。')
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

    record('08-01','non-manifold','邊選取、Alt+A，再 F3 > Select Non Manifold',non_manifold,park=PARK)
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
        return '參考盒仍為60×40×30／內腔56×36×28、壁底2mm；24個螺紋草案參數待補、沒有實作。路線selected=null，自訂列印僅助教候選，沒有建立Screw修改器或進行計算。'

    record('08-01','reference-overview','回 Object Mode，改斜視；讀回完整原盒網格未變',reference_read,park=PARK,
           note='08-01只建立規格與建模參數紀錄；Blender映射只有文件關係，各數值未設定，沒有螺紋、柱、配對件或STL。')
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('08-01','save-dialog','File > Save As…：另存原盒螺紋參照場景 u08_thread_reference_v001.blend',
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
    record('08-01','saved','按 Save As，核對新檔路徑、bytes 與 SHA-256',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('08-01','open-saved','File > Open…：重開剛才的原盒參考版本',
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
                  source_scene_readback=dict(path=str(SOURCE),sha256=SOURCE_SHA,bytes=SOURCE.stat().st_size),
                  reference_scene=dict(path=str(path),sha256=state['scene_sha256'],bytes=state['scene_bytes'],scene_role='unmodified_box_thread_reference'),
                  measured_box=state['reference_body'],face_measurements=state['face_measurements'])
        write('parameter-record-v001.json',plan)
        result=dict(passed=True,kind='thread_parameter_reference',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
                    opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
                    source_body_geometry_unchanged=True,source_body=state['source_body'],reference_body=state['reference_body'],
                    scene_path=str(path),scene_sha256=state['scene_sha256'],scene_bytes=state['scene_bytes'],scene_role='unmodified_box_thread_reference',
                    reopened=True,thread_modeled=False,boss_modeled=False,pilot_hole_modeled=False,counterpart_modeled=False,
                    modifier_created=False,screw_modifier_created=False,geometry_modified=False,face_measurements=state['face_measurements'],
                    parameter_template_path=str(PROJECT/TEMPLATE),parameter_template_sha256=TEMPLATE_SHA,source_facts_path=str(PROJECT/FACTS),source_facts_sha256=FACTS_SHA,
                    route=template['route'],thread_route_selected=None,thread_standard_selected=None,blender_mapping=template['blender_mapping'],
                    final_objects={o.name:dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),modifier_count=len(o.modifiers) if o.type=='MESH' else 0,matrix_world=[list(row) for row in o.matrix_world]) for o in bpy.data.objects},
                    non_manifold_selected_edges=state['non_manifold_selected_edges'],
                    parameter_record_path=str(out/'parameter-record-v001.json'),parameter_record_sha256=g['sha256'](str(out/'parameter-record-v001.json')),
                    calculations_performed=False,strength_analysis_performed=False,fit_qualification=False,
                    printed=False,fit_tested=False,slicer_checked=False,exported=False,exported_stl=False,
                    physical_measurements=None,fit_results=None,physical_interference=None,material_grade=None,qualified_strength_N=None,qualified_clearance_mm=None,qualified_torque_Nm=None,
                    numericComparison=dict(dimensionsAbsMm=1e-4,purpose='Floating point reconstruction only; not manufacturing tolerance or strength/fit qualification'))
        write('verification.json',result)
        return '重開實測與來源一致：60 × 40 × 30、壁底 2 mm／NM 0；只有原盒。參數表 v001 已綁定場景 hash；24個參數／路線／修改器設定仍待定；沒有建牙或柱、計算、STL、列印或試配。'
    record('08-01','reopened-verified','按 Open：重驗未修改原盒，保存參數表、三個實選面座標及 verification.json',reopened,park=PARK,
           note='助教準備完成不等於學員已完成；不更新 progress、不做強度或配合合格判定。')
