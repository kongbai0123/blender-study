"""07-02: native UI extrusions, exact root-edge bevels and a trial snap lid.

All modelling is performed by simulated UI events in the isolated runner.
Python copies sources and reads actual mesh/operator state only.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import Kit, PARK, PROJECT
from lid_checks import validate_body_mesh as validate_source_body
from tenon_checks import read_mesh_data

SOURCE = PROJECT/'learning/evidence/07/2026-10-25-lesson07-parameters-demo-v001/demo-files/u07_snap_reference_v001.blend'
SOURCE_SHA = '6a6b6c03295c8b6047b97c3efdea9884954b714da87b45b7aa36b4d2b612d3a9'
PARAMETER = PROJECT/'learning/evidence/07/2026-10-25-lesson07-parameters-demo-v001/parameter-record-v001.json'
PARAMETER_SHA = '57d411f24486aad351056854b8eb427aae853b99f290372c9d0294d367ac6ead'
PLAN = PROJECT/'learning/plans/07-02-cantilever-geometry-draft-v001.json'
PLAN_SHA = 'f4f0fab02a47eaade189c3b1c6cb8094753b435fe1a3ab570843af65fb2044be'
FILENAME = 'u07_cantilever_snap_v001.blend'


def build(g):
    return _build(g, False)


def build_probe(g):
    return _build(g, True)


def build_full_probe(g):
    return _build(g, 'full')


def _build(g, probe):
    if not probe:
        from snapfit_checks import validate_tool_mesh, validate_body_mesh, validate_lid_mesh, validate_assembly
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    out = Path(g['OUT'])
    sources = Path(k.demo_dir)/'sources'
    sources.mkdir()
    source_copy = sources/SOURCE.name
    for p, expected in ((SOURCE,SOURCE_SHA),(PARAMETER,PARAMETER_SHA),(PLAN,PLAN_SHA)):
        if g['sha256'](str(p)) != expected:
            raise RuntimeError('Fixed source/parameter/draft changed: '+str(p))
    source_copy.write_bytes(SOURCE.read_bytes())
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    relatives = ['learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
        'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson07_snap.py',
        'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/tenon_checks.py']
    relatives += [('learning/tutor/scenarios/lesson07_snap_probe_full.py' if probe=='full' else 'learning/tutor/scenarios/lesson07_snap_probe.py') if probe else 'learning/tutor/scenarios/snapfit_checks.py']
    files, bindings = [], []
    for relative in relatives:
        target = snapshots/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    for original, name in ((PLAN,'geometry-plan-v001.json'),(PARAMETER,'parameter-source-v001.json'),
                           (PROJECT/'sources/engineering/snapfit-source-facts-v001.json','snapfit-source-facts-v001.json')):
        target = snapshots/name
        target.write_bytes(original.read_bytes())
        bindings.append(dict(source=original.relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=files,dataBindings=bindings,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    plan = json.loads((snapshots/'geometry-plan-v001.json').read_text('utf-8'))
    state = dict(bevel_operations={},selected_edges={},operand_attempts=[])
    hidden_expected = {}

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def obj(name):
        return bpy.data.objects[name]

    def unchanged():
        k.guard()
        for p, expected in ((SOURCE,SOURCE_SHA),(source_copy,SOURCE_SHA),(PARAMETER,PARAMETER_SHA),(PLAN,PLAN_SHA)):
            if g['sha256'](str(p)) != expected:
                raise RuntimeError('Protected input changed: '+str(p))

    def dump(name,filename):
        raw = read_mesh_data(obj(name))
        write(filename,raw)
        return raw

    def search(text):
        do(lambda:key('F3',x=700,y=600),.3)
        do(lambda:k.type_text(text),.3)
        do(lambda:key('RET'),.7)

    def transform(axis,text):
        do(lambda:key('G',x=700,y=600),.15)
        do(lambda:key(axis),.15)
        do(lambda:k.type_text(text),.2)
        do(lambda:key('RET'),.4)

    def extrude(axis,text):
        # Region extrusion is already constrained to the selected face normal.
        # Repeating its axis key releases that constraint in Blender 5.2.
        do(lambda:key('E',x=700,y=600),.2)
        do(lambda:k.type_text(text.lstrip('-')),.2)
        do(lambda:key('RET'),.5)

    def frame(notches=1):
        # Edit Mode inserts selection icons before View; the menu moves right.
        do(lambda:click(236 if bpy.context.mode=='EDIT_MESH' else 184,38),.3)
        do(lambda:move(288 if bpy.context.mode=='EDIT_MESH' else 236,168),.3)
        do(lambda:click(288 if bpy.context.mode=='EDIT_MESH' else 236,168),.5)
        k.wheel_out(notches)

    def oblique(front=False):
        do(lambda:key('NUMPAD_1' if front else 'NUMPAD_7',x=700,y=600),.3)
        do(lambda:key('NUMPAD_8' if front else 'NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_8' if front else 'NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_6',x=700,y=600),.3)

    def back_oblique(bottom=False):
        do(lambda:key('NUMPAD_1',ctrl=True,x=700,y=600),.3)
        do(lambda:key('NUMPAD_2' if bottom else 'NUMPAD_8',x=700,y=600),.2)
        do(lambda:key('NUMPAD_2' if bottom else 'NUMPAD_8',x=700,y=600),.2)
        do(lambda:key('NUMPAD_6',x=700,y=600),.3)

    def visibility(name,hidden):
        hidden_expected[name] = hidden
        expected = dict(hidden_expected)
        def hide_target(target):
            do(lambda:click(1340,k.outliner_y(target)) if not obj(target).hide_get() else None,.3)
            def hide():
                if not obj(target).hide_get():
                    if bpy.context.view_layer.objects.active != obj(target):
                        raise RuntimeError('Wrong object before hiding '+target)
                    key('H',x=700,y=600)
            do(hide,.4)
        if hidden:
            hide_target(name)
        else:
            do(lambda:key('H',alt=True,x=700,y=600),.4)
            for target, flag in expected.items():
                if flag:
                    hide_target(target)
        def checked():
            if {n:obj(n).hide_get() for n in expected} != expected:
                raise RuntimeError('Visibility differs from intended isolated objects')
        do(checked,.1)

    def cube(name,dimensions,location):
        search('Add Cube')
        for y,value in zip((411,430,450),dimensions):
            k.type_into(1075,y,str(value)+'mm')
        do(lambda:click(313,38),.3)
        do(lambda:move(336,141),.3)
        k.menu_item(533,180,.5)
        for axis,value in zip(('X','Y','Z'),location):
            if value:
                transform(axis,str(value)+'mm')
        k.rename_active(name)

    def projected(point):
        a = k.area('VIEW_3D')
        region = next(r for r in a.regions if r.type=='WINDOW')
        p = location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(point))
        if p is None:
            raise RuntimeError('Target point not visible')
        return region.x+p.x,k.window().height-region.y-p.y

    def select_face(point):
        do(lambda:key('THREE',x=700,y=600),.2)
        do(lambda:key('A',alt=True,x=700,y=600),.2)
        do(lambda:click(*projected(point)),.4)

    def face_info(name,expected_min,expected_max):
        bm = bmesh.from_edit_mesh(obj(name).data)
        faces = [f for f in bm.faces if f.select]
        points = [list(obj(name).matrix_world@v.co) for f in faces for v in f.verts]
        detail = dict(face_count=len(faces),vertices=points)
        write('last-selected-face.json',detail)
        if len(faces)!=1:
            raise RuntimeError('Expected one face: '+str(detail))
        bounds = [min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]
        if any(abs(a-b)>1e-4 for a,b in zip(bounds,expected_min+expected_max)):
            raise RuntimeError('Selected face bounds differ: '+str(bounds))
        return '實選1面，world min %s、max %s mm。'%(bounds[:3],bounds[3:])

    def selected_edges(name,kind,expected):
        bm = bmesh.from_edit_mesh(obj(name).data)
        actual = [[list(obj(name).matrix_world@v.co) for v in e.verts] for e in bm.edges if e.select]
        state['selected_edges'][kind] = actual
        write('selected-root-hook-edges.json',state['selected_edges'])
        def signature(edge):
            return sorted(tuple(round(c,4) for c in p) for p in edge)
        if sorted(signature(e) for e in actual)!=sorted(signature(e) for e in expected):
            raise RuntimeError('Wrong selected '+kind+' edges: '+str(actual))
        return '精確選中%d條%s邊，端點world座標 %s mm；不是整盒外緣。'%(len(actual),kind,actual)

    def choose_edges(points):
        do(lambda:key('TWO',x=700,y=600),.2)
        do(lambda:key('A',alt=True,x=700,y=600),.2)
        do(lambda:key('Z',alt=True,x=700,y=600),.3)
        for i,point in enumerate(points):
            do(lambda p=point,add=bool(i):click(*projected(p),shift=add),.4)

    def bevel(kind,amount,segments):
        do(lambda:key('B',ctrl=True,x=700,y=600),.3)
        # This modal operator treats M as a width-method shortcut, including
        # M key events inside "mm". Scene units already make one unit 1 mm.
        do(lambda:k.type_text(str(amount)),.3)
        if segments>1:
            def wheels():
                move(700,600)
                for _ in range(segments-1):
                    g['_event'](k.window(),'WHEELUPMOUSE','PRESS',700,600)
            do(wheels,.4)
        do(lambda:key('RET'),.5)
        def actual_operator():
            candidates = [o for o in bpy.context.window_manager.operators if o.bl_idname=='MESH_OT_bevel']
            if not candidates:
                write('bevel-operator-diagnostic.json',[o.bl_idname for o in bpy.context.window_manager.operators])
                raise RuntimeError('Actual native Bevel operator missing')
            p = candidates[-1].properties
            detail = {n:getattr(p,n,None) for n in ('offset','offset_type','segments','profile','affect','clamp_overlap')}
            detail.update(operator_id='MESH_OT_bevel',offset_mm=float(p.offset)*bpy.context.scene.unit_settings.scale_length*1000)
            state['bevel_operations'][kind] = detail
            write('bevel-operations.json',state['bevel_operations'])
            if abs(detail['offset_mm']-amount)>1e-4 or detail['segments']!=segments or detail['offset_type']!='OFFSET' or abs(detail['profile']-.5)>1e-5:
                raise RuntimeError('Actual Bevel settings differ: '+str(detail))
            return '實際 Bevel operator：'+str(detail)+'。輸入offset與實際圓角輪廓分開記錄。'
        record('07-02',kind+'-bevel','Ctrl+B：%s offset %g mm、%d段；立即讀回原生operator'%(kind,amount,segments),actual_operator,park=PARK)
        do(lambda:key('Z',alt=True,x=700,y=600),.3)

    def boolean(target,tool,slug):
        k.click_outliner(target)
        do(lambda:click(1245,k.props_y(296)),.4)
        search('Add Boolean Modifier')
        do(lambda:click(1369,k.props_y(143)),.4)
        do(lambda:move(1380,k.props_y(193)),.3)
        do(lambda:click(1380,k.props_y(193)),.4)
        do(lambda:k.type_text(tool),.4)
        do(lambda:key('RET'),.6)
        def assigned(attempt=0):
            mods = [m for m in obj(target).modifiers if m.type=='BOOLEAN']
            m = mods[0] if len(mods)==1 else None
            item = dict(target=target,tool=tool,attempt=attempt,operation=m.operation if m else None,operand=m.object.name if m and m.object else None,solver=m.solver if m else None)
            state['operand_attempts'].append(item)
            write('operand-attempts.json',state['operand_attempts'])
            if m and m.operation=='UNION' and m.solver=='EXACT' and m.object==obj(tool):
                return
            if attempt>=2:
                raise RuntimeError('Boolean assignment failed: '+str(item))
            g['queue'][0:0] = [(lambda:move(1380,k.props_y(193)),.3),(lambda:click(1380,k.props_y(193)),.4),
                (lambda:key('A',ctrl=True),.2),(lambda:k.type_text(tool),.4),
                (lambda:move(1310,k.props_y(225)),.3),(lambda:click(1310,k.props_y(225)),.5),(lambda:assigned(attempt+1),.1)]
        do(assigned,.1)
        visibility(tool,True)
        k.click_outliner(target)
        frame(1)
        record('07-02',slug,'選'+target+'，Boolean Union／Exact 指定'+tool+'，隱藏工具後看真正預覽',
               lambda:'實際修改器 '+str([(m.operation,m.solver,m.object.name if m.object else None) for m in obj(target).modifiers]),park=PARK)
        do(lambda:click(1424,k.props_y(113)),.3)
        k.menu_item(1331,343,.7)
        def applied():
            if obj(target).modifiers or not obj(target).data.polygons:
                raise RuntimeError('Union not applied or empty result')
        do(applied,.1)

    def read_part(name,kind,filename):
        raw = dump(name,filename)
        if probe:
            return dict(probe_only=True,vertices=len(raw['vertices']),triangles=len(raw['triangles']))
        if kind in ('snap','flange'):
            result = validate_tool_mesh(raw['vertices'],raw['triangles'],kind)
        elif kind=='body':
            result = validate_body_mesh(raw['vertices'],raw['triangles'],state['source_body'])
        else:
            result = validate_lid_mesh(raw['vertices'],raw['triangles'])
        state[{'snap':'construction_snap','flange':'construction_flange','body':'body','lid':'lid'}[kind]] = result
        return result

    def part_summary(name,kind,filename):
        r = read_part(name,kind,filename)
        if probe:
            return '%s UI探測：保存實際mesh，%d頂點／%d三角面；尚未由正式幾何helper認證。'%(name,r['vertices'],r['triangles'])
        text = '%s 實際外框 %s mm、體積 %.6g mm³，單殼／Non Manifold %d。'%(name,[round(v,6) for v in r['dimensions_mm']],r['volume_mm3'],r['non_manifold_edges'])
        if kind in ('snap','body'):
            s = r['snap_profile']
            radii = [round(f['fitted_circle_radius_mm'],6) for f in s['root_fillets']]
            text += ' 直臂h %.6g／b %.6g、根平面至承接面 %.6g、鉤突出 %.6g mm；兩根部3段弦端擬合R %s mm。'%(s['beam_thickness_mm'],s['beam_width_mm'],s['root_to_bearing_geometric_length_mm'],s['hook_projection_mm'],radii)
        elif kind=='lid':
            s = r['mating_profile']
            text += ' 蓋板 %s mm；凸緣寬 %.6g、厚 %.6g、突出 %.6g mm。'%([round(v,6) for v in r['plate_dimensions_mm']],s['flange_width_mm'],s['ledge_thickness_mm'],s['ledge_projection_mm'])
        return text

    def non_manifold(name,slug):
        do(lambda:key('TAB',x=700,y=600),.3)
        do(lambda:key('TWO',x=700,y=600),.2)
        do(lambda:key('A',alt=True,x=700,y=600),.2)
        search('Select Non Manifold')
        def read():
            bm = bmesh.from_edit_mesh(obj(name).data)
            if not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):
                raise RuntimeError('Non Manifold check failed '+name)
            return name+'：Select Non Manifold選中0條邊，實際非流形邊0；不作強度或製程判定。'
        record('07-02',slug,'Tab／邊模式／Alt+A／Select Non Manifold',read,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.3)

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',source_copy.name)
    record('07-02','source-open-dialog','File > Open，開啟07-01原盒參考版同hash副本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Body_Reference')
    def source_read():
        unchanged()
        raw = dump('Body_Reference','source_body_mesh.json')
        state['source_body'] = validate_source_body(raw['vertices'],raw['triangles'])
        return '原盒60×40×30、內腔56×36×28、壁底2mm；來源與07-01參數紀錄hash固定。新增尺寸為草案，不填材料或允許應變。'
    record('07-02','source-geometry','改前重驗原盒；這次另建卡扣分支',source_read,park=PARK)
    do(lambda:key('H',alt=True,x=700,y=600),.4)
    for n in ('Camera','Light'):
        k.click_outliner(n)
        do(lambda:key('X',x=700,y=600),.3)
        do(lambda:key('RET'),.5)
    k.click_outliner('Body_Reference')
    k.rename_active('Body')
    visibility('Body',True)

    cube('SnapTool',(9,4.6,3),(0,-22.2,-9.5))
    do(lambda:key('NUMPAD_7',x=700,y=600),.3)
    frame(1)
    do(lambda:key('TAB',x=700,y=600),.3)
    select_face((0,-22.2,-8))
    record('07-02','anchor-top','選anchor頂面，檢查9×4.6×3基塊真實位置',lambda:face_info('SnapTool',[-4.5,-24.5,-8],[4.5,-19.9,-8]),park=PARK)
    do(lambda:key('I',x=700,y=600),.2)
    do(lambda:k.type_text('1.5mm'),.2)
    do(lambda:key('RET'),.5)
    record('07-02','beam-inset','頂面Inset1.5mm，形成6×1.6mm直臂截面',lambda:face_info('SnapTool',[-3,-23,-8],[3,-21.4,-8]),park=PARK)
    extrude('Z','19mm')
    extrude('Z','2mm')
    oblique(front=True)
    frame(1)
    record('07-02','beam-extruded','Edit Mode E19mm、再E2mm（頂面法向+Z），讀回臂頂Z13；扣鉤根層Z11',lambda:face_info('SnapTool',[-3,-23,13],[3,-21.4,13]),park=PARK)
    do(lambda:key('NUMPAD_1',x=700,y=600),.3)
    select_face((0,-23,12))
    do(lambda:face_info('SnapTool',[-3,-23,11],[3,-23,13]),.1)
    extrude('Y','-1.2mm')
    record('07-02','hook-extruded','選最高2mm的−Y外側面，E1.2mm沿面法向−Y形成外鉤',lambda:face_info('SnapTool',[-3,-24.2,11],[3,-24.2,13]),park=PARK)
    oblique(front=True)
    do(lambda:key('A',x=700,y=600),.2)
    frame(1)
    choose_edges(((0,-24.2,13),))
    record('07-02','hook-edge','Xray精確點選鉤外頂的一條X向邊',lambda:selected_edges('SnapTool','hook',[[[-3,-24.2,13],[3,-24.2,13]]]),park=PARK)
    bevel('hook',.8,1)
    choose_edges(((0,-23,-8),(0,-21.4,-8)))
    record('07-02','root-edges','Xray只選兩條臂腳與anchor頂面的凹根部邊',lambda:selected_edges('SnapTool','root',[[[-3,-23,-8],[3,-23,-8]],[[-3,-21.4,-8],[3,-21.4,-8]]]),park=PARK)
    bevel('root',.6,3)
    do(lambda:key('TAB',x=700,y=600),.4)
    oblique(front=True)
    frame(1)
    record('07-02','snap-tool','回Object Mode，讀回一體anchor／臂／鉤與實際根部圓角網格',
           lambda:part_summary('SnapTool','snap','snap_tool_mesh.json'),park=PARK,
           note='這些是幾何草案；未計算允許撓度或裝配行程，不代表已可扣入。')
    if probe and probe!='full':
        return

    visibility('Body',False)
    boolean('Body','SnapTool','body-union')
    oblique(front=True)
    frame(1)
    record('07-02','body-applied','Apply Union，從成品Body讀回原盒核心與外掛卡扣',
           lambda:part_summary('Body','body','body_mesh.json'),park=PARK,
           note='原盒核心60×40×30保留；含anchor的Body外框Y44.5mm，不宣稱整件仍寬40。')
    non_manifold('Body','body-non-manifold')
    visibility('Body',True)
    cube('Lid',(60,46,2),(0,-3,16.2))
    oblique()
    frame(1)
    record('07-02','lid-plate','新增草案蓋板60×46×2，前緣Y−26、板底Z15.2',lambda:k.size('Lid',' mm'),park=PARK,
           note='此為新卡扣蓋板，不是舊環唇或燕尾上蓋。')
    visibility('Lid',True)
    cube('FlangeTool',(10,1.5,.6),(0,-25.25,10.5))
    do(lambda:key('NUMPAD_7',x=700,y=600),.3)
    frame(1)
    do(lambda:key('TAB',x=700,y=600),.3)
    select_face((0,-25.25,10.8))
    do(lambda:face_info('FlangeTool',[-5,-26,10.8],[5,-24.5,10.8]),.1)
    extrude('Z','4.6mm')
    do(lambda:key('NUMPAD_1',ctrl=True,x=700,y=600),.3)
    select_face((0,-24.5,10.5))
    do(lambda:face_info('FlangeTool',[-5,-24.5,10.2],[5,-24.5,10.8]),.1)
    extrude('Y','1.2mm')
    record('07-02','flange-extruded','基塊頂面E4.6mm沿+Z成裙，內側低面E1.2mm沿+Y成承接凸緣',lambda:face_info('FlangeTool',[-5,-23.3,10.2],[5,-23.3,10.8]),park=PARK)
    do(lambda:key('TAB',x=700,y=600),.4)
    back_oblique()
    frame(1)
    record('07-02','flange-tool','讀回一體蓋裙／承接凸緣的實際網格',lambda:part_summary('FlangeTool','flange','flange_tool_mesh.json'),park=PARK)
    visibility('Lid',False)
    boolean('Lid','FlangeTool','lid-union')
    back_oblique(bottom=True)
    frame(1)
    record('07-02','lid-applied','Apply Union，讀回一體蓋板／裙／承接凸緣',lambda:part_summary('Lid','lid','lid_mesh.json'),park=PARK)
    non_manifold('Lid','lid-non-manifold')
    if probe:
        return
    visibility('Body',False)
    k.click_outliner('Lid')
    transform('Z','12mm')
    k.click_outliner('Body',ctrl=True)
    oblique(front=True)
    frame(1)
    record('07-02','lid-raised','僅將Lid抬高12mm展示hook與ledge；沒有模擬接觸或彎曲',lambda:'Lid實際Location '+str(list(obj('Lid').location))+'；展示位置，不作裝配路徑證明。',park=PARK)
    k.click_outliner('Lid')
    transform('Z','-12mm')
    k.click_outliner('Body',ctrl=True)
    oblique(front=True)
    frame(1)

    def assembly_read():
        unchanged()
        read_part('Body','body','body_mesh.json')
        read_part('Lid','lid','lid_mesh.json')
        state['assembly'] = validate_assembly(state['body'],state['lid'])
        a = state['assembly']
        return ('實際靜態讀值：板底／盒頂 %.6g、臂／凸緣 %.6g、鉤／裙 %.6g、鉤底／凸緣頂 %.6g mm；'
                'Y投影重疊 %.6g、直臂內側淨空 %.6g、內根部局部淨空 %.6g mm。δ_req、材料及允許應變仍待定。')%(a['plate_rim_gap_mm'],a['beam_ledge_gap_mm'],a['hook_skirt_gap_mm'],a['hook_ledge_vertical_gap_mm'],a['hook_ledge_projection_overlap_mm'],a['straight_beam_inward_static_space_mm'],a['inner_root_fillet_local_static_gap_mm'])
    record('07-02','assembly-geometry','Lid回原位置，讀取靜態間距、投影重疊與根部局部淨空',assembly_read,park=PARK,
           note='未變形靜態幾何；不等於裝配可行、保持力、強度或試配合格。')
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('07-02','save-dialog','File > Save As，另存卡扣幾何草案u07_cantilever_snap_v001.blend',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    def safe_target():
        folder,name = k.browser()
        target = (Path(folder)/name).resolve()
        if target.parent!=Path(k.demo_dir).resolve() or name!=FILENAME or target.exists():
            raise RuntimeError('Unsafe save target')
        unchanged()
    do(safe_target,.1)
    k.confirm_dialog(1.8)
    def saved():
        p = Path(bpy.data.filepath).resolve()
        if p!=(Path(k.demo_dir)/FILENAME).resolve() or not p.is_file():
            raise RuntimeError('New snap scene not saved')
        state.update(scene_path=str(p),scene_sha256=g['sha256'](str(p)),scene_bytes=p.stat().st_size)
        return '另存%d bytes，SHA-256 %s。'%(state['scene_bytes'],state['scene_sha256'])
    record('07-02','saved','Save As後讀回新版本hash與bytes',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('07-02','open-saved','File > Open，重開剛才卡扣幾何草案版本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def reopened():
        unchanged()
        p = Path(bpy.data.filepath).resolve()
        if str(p)!=state['scene_path'] or g['sha256'](str(p))!=state['scene_sha256']:
            raise RuntimeError('Reopened version differs')
        assembly_read()
        read_part('SnapTool','snap','snap_tool_mesh.json')
        read_part('FlangeTool','flange','flange_tool_mesh.json')
        final = {n:dict(object_name=n,type=obj(n).type,hidden=obj(n).hide_get(),modifier_count=len(obj(n).modifiers),scale=list(obj(n).scale)) for n in ('Body','Lid','SnapTool','FlangeTool')}
        if set(bpy.data.objects.keys())!=set(final) or any(v['modifier_count'] or v['scale']!=[1,1,1] or v['hidden']!=(n.endswith('Tool')) for n,v in final.items()):
            raise RuntimeError('Final finished/tool object inventory differs')
        draft = dict(plan,recordedAt=datetime.now(timezone.utc).isoformat(),source_scene=dict(path=str(SOURCE),sha256=SOURCE_SHA),
            reference_scene=dict(path=str(p),sha256=state['scene_sha256'],bytes=state['scene_bytes'],scene_role='experimental_cantilever_geometry'),
            geometry_readback={n:state[n] for n in ('body','lid','assembly')})
        draft_path = out/'geometry-draft-record-v001.json'
        write(draft_path.name,draft)
        result = dict(passed=True,kind='cantilever_snap_geometry_demo',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_body=state['source_body'],body=state['body'],lid=state['lid'],construction_snap=state['construction_snap'],construction_flange=state['construction_flange'],assembly=state['assembly'],
            bevel_operations=state['bevel_operations'],source_snap_parameter_path=str(PARAMETER),source_snap_parameter_sha256=PARAMETER_SHA,
            scene_path=str(p),scene_sha256=state['scene_sha256'],scene_bytes=state['scene_bytes'],reopened=True,final_objects=final,
            draft_plan_path=str(PLAN),draft_plan_sha256=PLAN_SHA,draft_record_path=str(draft_path),draft_record_sha256=g['sha256'](str(draft_path)),
            geometry_modified=True,strength_analysis_performed=False,fit_qualification=False,exported_stl=False,slicer_checked=False,printed=False,fit_tested=False,
            material_grade=None,epsilon_allow=None,Q=None,delta_allow_mm=None,required_deflection_mm=None,forces=None,
            physical_measurements=None,fit_results=None,physical_interference=None,qualified_strength_N=None,qualified_clearance_mm=None,
            numericComparison=dict(dimensionsAbsMm=1e-4,purpose='Floating point reconstruction only; not manufacturing tolerance or strength/fit qualification'))
        write('verification.json',result)
        return '重開版本、實際Body／Lid／工具／根部Bevel與靜態間距已重驗；材料、允許撓度、裝配行程、力、列印與試配結果仍空白。'
    record('07-02','reopened-verified','Open後重驗幾何與版本，保存草案及verification',reopened,park=PARK)
