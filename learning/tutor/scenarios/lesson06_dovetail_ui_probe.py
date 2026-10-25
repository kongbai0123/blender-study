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
def validate_tool_mesh(vertices, triangles, kind):
    return dict(kind=kind, vertex_count=len(vertices), triangle_count=len(triangles), probe_only=True)

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
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson06_dovetail_ui_probe.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
                     'learning/tutor/scenarios/tenon_checks.py'):
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
            if m.operation != operation or m.object != obj(tool):
                raise RuntimeError('Boolean operand changed')
            return '%s：%s／Exact，Object %s；這是 Apply 前的真實預覽。'%(target,m.operation,m.object.name)
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
        return size(name)+'UI探測：僅保存原始網格供後續核對，本探測不發布。'

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
