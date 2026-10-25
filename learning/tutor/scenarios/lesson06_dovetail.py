"""06-02: independent Blender UI events, paired dovetail grooves and slide lid."""
import json
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

from common import Kit, PARK, PROJECT
from lid_checks import read_body_and_validate
from tenon_checks import read_mesh_data
from dovetail_checks import validate_tool_mesh, validate_body_mesh, validate_lid_mesh, validate_assembly, validate_travel

SOURCE = PROJECT/'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend'
SOURCE_SHA = 'b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530'
FILENAME = 'u06_dovetail_slide_v001.blend'


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    out = Path(g['OUT'])
    sources = Path(k.demo_dir)/'sources'
    sources.mkdir()
    source_copy = sources/SOURCE.name
    if g['sha256'](str(SOURCE)) != SOURCE_SHA:
        raise RuntimeError('Original 04 box checkpoint changed')
    source_copy.write_bytes(SOURCE.read_bytes())
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    manifest = []
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson06_dovetail.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
                     'learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/dovetail_checks.py'):
        target = snapshots/Path(relative).name
        target.write_bytes((PROJECT/relative).read_bytes())
        manifest.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=manifest,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state, hidden_expected = {}, {}

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def guard():
        k.guard()
        if any(g['sha256'](str(p)) != SOURCE_SHA for p in (SOURCE,source_copy)):
            raise RuntimeError('Original scene or source copy overwritten')

    def obj(name):
        return bpy.data.objects[name]

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
        do(lambda:k.type_text(text),.15)
        do(lambda:key('RET'),.4)

    def apply_scale():
        do(lambda:click(313,38),.3)
        do(lambda:move(336,141),.3)
        k.menu_item(533,180,.5)

    def visibility(name,hidden):
        hidden_expected[name] = hidden
        expected = dict(hidden_expected)
        def hide_target(target):
            do(lambda:click(1340,k.outliner_y(target)) if not obj(target).hide_get() else None,.3)
            def hide():
                if not obj(target).hide_get():
                    if bpy.context.view_layer.objects.active != obj(target):
                        raise RuntimeError('Wrong selection before hiding '+target)
                    key('H',x=700,y=600)
            do(hide,.4)
        if hidden:
            hide_target(name)
        else:
            do(lambda:key('H',alt=True,x=700,y=600),.4)
            for target,hide in expected.items():
                if hide:
                    hide_target(target)
        def checked():
            actual = {n:obj(n).hide_get() for n in expected}
            if actual != expected:
                raise RuntimeError('Unexpected hidden states '+str(actual))
        do(checked,.1)

    def frame(notches=1):
        do(lambda:click(184,38),.3)
        k.menu_item(236,168,.5)
        k.wheel_out(notches)

    def oblique(bottom=False):
        do(lambda:key('NUMPAD_7',ctrl=bottom,x=700,y=600),.3)
        do(lambda:key('NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_6',x=700,y=600),.3)

    def size(name):
        o = obj(name)
        return '%s Dimensions %s、Location %s、Scale %s。'%(name,k.triple(o.dimensions,' mm'),k.triple(o.location,' mm'),k.triple(o.scale,''))

    def cube(name,dimensions,location):
        search('Add Cube')
        for y,value in zip((411,430,450),dimensions):
            k.type_into(1075,y,str(value)+'mm')
        apply_scale()
        for axis,value in zip(('X','Y','Z'),location):
            if value:
                transform(axis,str(value)+'mm')
        k.rename_active(name)

    def paired_tool(name,dimensions,location,top_ratio=None):
        cube(name,dimensions,location)
        do(lambda:key('NUMPAD_7',x=700,y=600),.3)
        frame(1)
        do(lambda:key('TAB',x=700,y=600),.3)
        if top_ratio is not None:
            do(lambda:key('THREE',x=700,y=600),.2)
            do(lambda:key('A',alt=True,x=700,y=600),.3)
            def select_top():
                o = obj(name)
                a = k.area('VIEW_3D')
                region = next(r for r in a.regions if r.type == 'WINDOW')
                # Read the real top-face centre; use UI click, never select vertices through RNA.
                face = max(o.data.polygons,key=lambda f:f.center.z)
                p = location_3d_to_region_2d(region,a.spaces.active.region_3d,o.matrix_world@face.center)
                if p is None:
                    raise RuntimeError('Top face not visible')
                click(region.x+p.x,k.window().height-region.y-p.y)
            do(select_top,.4)
            def check_top():
                bm = bmesh.from_edit_mesh(obj(name).data)
                selected = [f for f in bm.faces if f.select]
                if len(selected) != 1 or selected[0].normal.z < .99:
                    raise RuntimeError('Top-face click selected wrong face')
            do(check_top,.1)
            do(lambda:key('S',x=700,y=600),.15)
            do(lambda:key('Y'),.15)
            do(lambda:k.type_text(str(top_ratio)),.2)
            do(lambda:key('RET'),.4)
        do(lambda:key('A',x=700,y=600),.2)
        do(lambda:key('D',shift=True,x=700,y=600),.2)
        do(lambda:key('Y'),.15)
        do(lambda:k.type_text('-34mm'),.2)
        do(lambda:key('RET'),.4)
        do(lambda:key('TAB',x=700,y=600),.4)
        oblique()
        frame(1)

    def boolean(target,tool,operation,slug):
        k.click_outliner(target)
        do(lambda:click(1245,503),.4)
        search('Add Boolean Modifier')
        if operation == 'UNION':
            do(lambda:click(1369,350),.4)
        do(lambda:move(1380,400),.3)
        do(lambda:click(1380,400),.4)
        do(lambda:k.type_text(tool),.4)
        do(lambda:key('RET'),.6)
        def assigned(attempt=0):
            mods = [m for m in obj(target).modifiers if m.type == 'BOOLEAN']
            m = mods[0] if len(mods) == 1 else None
            state.setdefault('operand_attempts',[]).append(dict(target=target,tool=tool,attempt=attempt,
                operation=m.operation if m else None,operand=m.object.name if m and m.object else None))
            write('operand-attempts.json',state['operand_attempts'])
            if m and m.operation == operation and m.object == obj(tool):
                return
            if attempt >= 2:
                raise RuntimeError('Boolean assignment failed '+str(state['operand_attempts']))
            g['queue'][0:0] = [(lambda:move(1380,400),.3),(lambda:click(1380,400),.4),
                (lambda:key('A',ctrl=True),.2),(lambda:k.type_text(tool),.4),
                (lambda:move(1310,432),.3),(lambda:click(1310,432),.5),(lambda:assigned(attempt+1),.1)]
        do(assigned,.1)
        visibility(tool,True)
        k.click_outliner(target)
        def read():
            m = next(m for m in obj(target).modifiers if m.type == 'BOOLEAN')
            if m.operation != operation or m.object != obj(tool) or m.solver != 'EXACT':
                raise RuntimeError('Boolean operand changed')
            return '%s：%s／%s，Object %s；這是 Apply 前的真實預覽。'%(target,m.operation,m.solver,m.object.name)
        record('06-02',slug,'選 '+target+'，新增 Boolean '+operation+'，Object 搜尋指定 '+tool,read,park=PARK)
        do(lambda:click(1424,320),.3)
        k.menu_item(1331,343,.7)
        def applied():
            if obj(target).modifiers or not obj(target).data.polygons:
                raise RuntimeError('Boolean was not applied or empty output')
        do(applied,.1)

    def tool_read(name,kind):
        raw = dump(name,kind+'_tool_mesh.json')
        result = validate_tool_mesh(raw['vertices'],raw['triangles'],kind)
        state['construction_'+{'guide':'guides','groove':'grooves','male':'males'}[kind]] = result
        detail = {'guide':'單條名義60 × 6 × 5 mm；成對Y外框40 mm。',
                  'groove':'單條名義長62／底寬3.6／頂寬2／高4 mm；成對Y外框37.6 mm。',
                  'male':'單條名義長60／底寬3.12／頂寬1.76／高3.4 mm；成對Y外框37.12 mm。'}[kind]
        return size(name)+'Item Dimensions 是成對工具總外框，Location 為第一條建構時的物件原點。'+detail+'兩條實際中心Y±17、截面、端面與封閉工具網格均已由world mesh核對。'

    def body_read():
        raw = dump('Body','body_mesh.json')
        state['body'] = validate_body_mesh(raw['vertices'],raw['triangles'])
        return 'Body 外形仍 60 × 40 × 30 mm；兩側加厚導軌 Z10～15，盒口中央局部縮至 56 × 28。燕尾槽在 X 兩端貫通，槽底 Z11.8、寬3.6，rim Z15 的槽口寬2.32 mm；單殼、Non Manifold 0。'

    def lid_read():
        raw = dump('SlidingLid','lid_mesh.json')
        state['lid'] = validate_lid_mesh(raw['vertices'],raw['triangles'])
        return 'SlidingLid 外形 60 × 40 × 5.2 mm；蓋板厚2、Z15.2～17.2。兩條燕尾榫底 Z12、寬3.12，與板底相交處 Z15.2、寬1.84；已 Union 一體閉合，Non Manifold 0。'

    def all_read():
        guard()
        body_read()
        lid_read()
        state['assembly'] = validate_assembly(state['body'],state['lid'])
        return '水平截面總差0.4／每側0.2 mm為助教試驗；斜面法向間距約0.196116 mm，槽底與榫底、盒頂與板底各0.2 mm。槽和榫斜面同斜率0.2（距垂直約11.3099°）；未列印試配。'

    def non_manifold(name,slug):
        do(lambda:key('TAB',x=700,y=600),.3)
        do(lambda:key('TWO',x=700,y=600),.2)
        do(lambda:key('A',alt=True,x=700,y=600),.2)
        search('Select Non Manifold')
        def read():
            bm = bmesh.from_edit_mesh(obj(name).data)
            if not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):
                raise RuntimeError('Non Manifold selection failed '+name)
            return name+'：Select Non Manifold 選到0條邊；實際網格非流形邊0。'
        record('06-02',slug,'選 '+name+'，Tab > 邊選取 > Select None > Select Non Manifold',read,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.3)

    def final_objects():
        result = {n:dict(object_name=n,type=obj(n).type,modifier_count=len(obj(n).modifiers),scale=list(obj(n).scale),hidden=obj(n).hide_get())
                  for n in ('Body','SlidingLid','GuideTool','GrooveTool','MaleTool')}
        for n,r in result.items():
            if r['modifier_count'] or r['hidden'] != (n.endswith('Tool')) or r['scale'] != [1,1,1]:
                raise RuntimeError('Unexpected final object state '+n)
        return result

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',source_copy.name)
    record('06-02','source-open-dialog','File > Open，開啟原04通用小盒同 hash 副本，建立獨立滑蓋分支',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Cube')
    oblique()
    frame(1)
    def original_read():
        guard()
        if Path(bpy.data.filepath).resolve() != source_copy.resolve():
            raise RuntimeError('Wrong source opened')
        dump('Cube','source_body_mesh.json')
        state['source_body'] = read_body_and_validate(obj('Cube'))
        write('source-geometry-verification.json',dict(passed=True,body=state['source_body']))
        return '原盒60 × 40 × 30、內腔56 × 36 × 28、壁底2 mm，改前重驗。06-01 的定位柱與環唇會阻擋滑動，因此本次另建滑蓋分支，不覆寫前版。'
    record('06-02','source-geometry','修改前核對原盒，確認這次沒有定位柱或環唇',original_read,park=PARK)
    # Remove only factory camera/light in this disposable branch, keeping short Outliner visible.
    for n in ('Camera','Light'):
        k.click_outliner(n)
        do(lambda:key('X',x=700,y=600),.3)
        do(lambda:key('RET'),.5)
    k.click_outliner('Cube')
    k.rename_active('Body')
    visibility('Body',True)

    paired_tool('GuideTool',(60,6,5),(0,17,12.5))
    record('06-02','guide-blocks','新增60 × 6 × 5方塊，中心Y17／Z12.5；Edit Mode Shift+D Y−34mm，做對稱導軌加厚工具',
           lambda:tool_read('GuideTool','guide'),park=PARK,note='導軌向盒內增加4 mm；局部盒口會縮小，不宣稱原內腔全高仍36 mm寬。')
    visibility('Body',False)
    boolean('Body','GuideTool','UNION','guide-union')
    record('06-02','guides-applied','Apply Union，核對實際加厚導軌與原盒連成一體',
           lambda:size('Body')+'加厚區位於Y±14～20、Z10～15，原外形未增加。',park=PARK)
    visibility('Body',True)

    paired_tool('GrooveTool',(62,3.6,4),(0,17,13.8),2/3.6)
    record('06-02','groove-tools','建62 × 3.6 × 4切割體；頂面 S Y 0.555555556 使頂寬2，再複製Y−34mm',
           lambda:tool_read('GrooveTool','groove'),park=PARK,
           note='切割體Z11.8～15.8；X±31超出原盒兩端，避免封閉入口。斜率由上下實際輪廓讀回。')
    visibility('Body',False)
    boolean('Body','GrooveTool','DIFFERENCE','groove-difference')
    oblique()
    frame(1)
    record('06-02','body-grooves','Apply Difference，核對兩端開口、斜槽、剩餘壁厚與原盒外形',body_read,park=PARK)
    do(lambda:key('NUMPAD_3',x=700,y=600),.3)
    frame(1)
    record('06-02','body-end-profile','沿X看盒體實際端面，查看兩個貫通燕尾槽入口',body_read,park=PARK,
           note='這是Right Orthographic的真實端面視圖，未切片或重畫剖面；槽口到槽底的深度3.2 mm。')
    non_manifold('Body','body-non-manifold')
    visibility('Body',True)

    cube('SlidingLid',(60,40,2),(0,0,16.2))
    oblique(bottom=True)
    frame(1)
    record('06-02','lid-plate','新增滑蓋板60 × 40 × 2 mm，中心Z16.2，板底留在盒頂上方0.2 mm',
           lambda:size('SlidingLid'),park=PARK)
    visibility('SlidingLid',True)
    paired_tool('MaleTool',(60,3.12,3.4),(0,17,13.7),1.76/3.12)
    record('06-02','male-ribs','燕尾榫工具底寬3.12／頂寬1.76、高3.4；中心Z13.7、Y±17，讀回兩條同斜率榫',
           lambda:tool_read('MaleTool','male'),park=PARK,
           note='工具頂Z15.4與板交入0.2；Union後埋入板內的頂面消失，成品可見榫到板底Z15.2。0.4是同高度水平總差試驗值。')
    visibility('SlidingLid',False)
    boolean('SlidingLid','MaleTool','UNION','lid-union')
    oblique(bottom=True)
    frame(1)
    record('06-02','lid-underside','Apply Union，從底部斜視核對一體燕尾榫與滑蓋板',lid_read,park=PARK)
    do(lambda:key('NUMPAD_3',x=700,y=600),.3)
    frame(1)
    record('06-02','lid-end-profile','沿X看滑蓋實際端面，核對下寬上窄的兩條燕尾榫',lid_read,park=PARK,
           note='真實Right Orthographic視圖；榫外露深3.2 mm，建構工具交入板內的0.2 mm已在Union後消失。')
    non_manifold('SlidingLid','lid-non-manifold')
    visibility('Body',False)
    k.click_outliner('SlidingLid')
    k.click_outliner('Body',ctrl=True)
    oblique()
    frame(1)
    record('06-02','assembly-geometry','回名義組裝位置，從實際截面量水平差、斜面法向gap與垂直餘量',all_read,park=PARK,
           note='兩端貫通，這版沒有端擋、止退或鎖定設計；不能當成已驗證列印結構。')
    state['travel_raw'] = {}
    for delta,total in ((30,30),(32,62)):
        k.click_outliner('SlidingLid')
        transform('X',str(delta)+'mm')
        k.click_outliner('Body',ctrl=True)
        frame(1)
        def travel_read(x=total):
            raw = dump('SlidingLid','travel_%d_lid_mesh.json'%x)
            state['travel_raw'][str(x)] = raw
            return 'SlidingLid 實際Location X=%g mm；已保存此位置world mesh。這是數位滑動檢視，非實體試配。'%obj('SlidingLid').location.x
        record('06-02','slide-x%d'%total,'沿X移動滑蓋至 +%d mm，拍攝入口與導軌相對位置'%total,travel_read,park=PARK)
    k.click_outliner('SlidingLid')
    transform('X','-62mm')
    k.click_outliner('Body',ctrl=True)
    oblique()
    frame(1)
    def travel_return():
        all_read()
        state['travel'] = validate_travel(state['body'],state['lid'],state['travel_raw'])
        return '滑蓋已回X0；+30／+62的實際網格是純X平移。兩端入口與沿X均勻截面共同驗證無碰撞平移路徑；不是實體滑動合格證明。'
    record('06-02','slide-return','回X0，結合實際截面、兩端入口與移動網格核對滑動路徑',travel_return,park=PARK)
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('06-02','save-dialog','File > Save As，另存燕尾滑蓋分支 u06_dovetail_slide_v001.blend',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    def safe_target():
        folder,name = k.browser()
        target = (Path(folder)/name).resolve()
        if target.parent != Path(k.demo_dir).resolve() or name != FILENAME or target.exists():
            raise RuntimeError('Unsafe save target')
        guard()
        final_objects()
    do(safe_target,.1)
    k.confirm_dialog(1.8)
    def saved():
        p = Path(bpy.data.filepath).resolve()
        if p != (Path(k.demo_dir)/FILENAME).resolve() or not p.is_file():
            raise RuntimeError('Scene save failed')
        state['scene_path'],state['scene_sha256'] = str(p),g['sha256'](str(p))
        return '已另存新場景v001，%d bytes；SHA-256 %s。'%(p.stat().st_size,state['scene_sha256'])
    record('06-02','saved','按 Save As，讀回新檔案版本與hash',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('06-02','open-saved','File > Open，重新開啟本次燕尾滑蓋 v001',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def reopened():
        guard()
        p = Path(bpy.data.filepath).resolve()
        if str(p) != state['scene_path'] or g['sha256'](str(p)) != state['scene_sha256']:
            raise RuntimeError('Reopened scene differs')
        all_read()
        for name,kind in (('GuideTool','guide'),('GrooveTool','groove'),('MaleTool','male')):
            tool_read(name,kind)
        state['travel'] = validate_travel(state['body'],state['lid'],state['travel_raw'])
        result = dict(passed=True,kind='dovetail_slide_geometry_demo',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_body=state['source_body'],scene_path=str(p),scene_sha256=state['scene_sha256'],scene_bytes=p.stat().st_size,reopened=True,
            construction_guides=state['construction_guides'],construction_grooves=state['construction_grooves'],construction_males=state['construction_males'],
            body=state['body'],lid=state['lid'],assembly=state['assembly'],travel=state['travel'],final_objects=final_objects(),
            trial=dict(status='experimental_geometry_only',selected_by='tutor',horizontal_total_clearance_mm=.4,horizontal_side_clearance_mm=.2,qualified_clearance_mm=None),
            mesh_analysis_overhang_checked=False,exported_stl=False,slicer_checked=False,printed=False,fit_tested=False,
            physical_measurements=None,fit_results=None,physical_interference=None,qualified_clearance_mm=None,
            numericComparison=dict(dimensionsAbsMm=1e-4,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing tolerance or printed fit acceptance'))
        write('verification.json',result)
        return '重新開啟後hash、Body／SlidingLid及三工具、X0組裝與行程證據一致。未匯出STL、切片、列印或實體試配；Overhang介面分析待後續，合格值留空。'
    record('06-02','reopened-verified','按 Open，重讀最終網格、版本及行程證據，保存 verification',reopened,park=PARK)
