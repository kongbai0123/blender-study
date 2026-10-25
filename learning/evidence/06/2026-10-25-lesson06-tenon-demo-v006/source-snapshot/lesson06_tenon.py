"""06-01: UI event demo of an integral locating pin and matching trial hole."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from lid_checks import read_body_and_validate, read_lid_and_validate
from tenon_checks import (read_tool_and_validate, read_body_pin_and_validate,
                          read_lid_hole_and_validate, validate_tenon_assembly, read_mesh_data)

SOURCE_RUN = PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001'
SOURCE = SOURCE_RUN/'demo-files/u05_lid_v001.blend'
SOURCE_SHA = 'ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
FILENAME = 'u06_locating_tenon_v001.blend'


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    out = Path(g['OUT'])
    sources = Path(k.demo_dir)/'sources'
    sources.mkdir()
    source_copy = sources/SOURCE.name
    prior = json.loads((SOURCE_RUN/'verification.json').read_text('utf-8'))
    if g['sha256'](str(SOURCE)) != SOURCE_SHA or prior.get('scene_sha256') != SOURCE_SHA or not prior.get('passed'):
        raise RuntimeError('Original 05-05 source checkpoint changed')
    source_copy.write_bytes(SOURCE.read_bytes())
    state = {}
    hidden_expected = {}
    snapshots = out/'source-snapshot'
    snapshots.mkdir()
    manifest = []
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                     'learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson06_tenon.py',
                     'learning/tutor/scenarios/lid_checks.py','learning/tutor/scenarios/stl_checks.py',
                     'learning/tutor/scenarios/tenon_checks.py'):
        original = PROJECT/relative
        target = snapshots/original.name
        target.write_bytes(original.read_bytes())
        manifest.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snapshots/'manifest.json').write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),
        files=manifest,sourceScene=str(SOURCE),sourceCopy=str(source_copy),sourceSha256=SOURCE_SHA),
        ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def write(name, value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def guard():
        k.guard()
        if any(g['sha256'](str(p)) != SOURCE_SHA for p in (SOURCE,source_copy)):
            raise RuntimeError('Original scene or source copy was overwritten')

    def obj(name):
        return bpy.data.objects[name]

    def active():
        value = bpy.context.view_layer.objects.active
        if not value or value.type != 'MESH':
            raise RuntimeError('Expected an active mesh')
        return value

    def size(name):
        o = obj(name)
        f = bpy.context.scene.unit_settings.scale_length*1000
        return '%s Dimensions %s、Location %s、Scale %s。'%(name,k.triple(o.dimensions,' mm',f),
                k.triple(o.location,' mm',f),k.triple(o.scale,''))

    def search(text):
        do(lambda:key('F3',x=700,y=600),.3)
        do(lambda:k.type_text(text),.3)
        do(lambda:key('RET'),.8)

    def transform(axis,text):
        do(lambda:key('G',x=700,y=600),.2)
        do(lambda:key(axis),.2)
        do(lambda:k.type_text(text),.2)
        do(lambda:key('RET'),.5)

    def apply_scale():
        do(lambda:click(313,38),.4)
        do(lambda:move(336,141),.4)
        k.menu_item(533,180,.6)

    def visibility(name,hidden):
        hidden_expected[name] = hidden
        expected = dict(hidden_expected)
        def hide_target(target):
            def select():
                if not obj(target).hide_get():
                    click(1340,min(k.outliner_y(target),198))
            def hide():
                if not obj(target).hide_get():
                    selected = bpy.context.view_layer.objects.active
                    if not selected or selected.name != target:
                        raise RuntimeError('Wrong active object before Hide: '+target)
                    key('H',x=700,y=600)
            do(select,.4)
            do(hide,.5)
        if hidden:
            hide_target(name)
        else:
            do(lambda:key('H',alt=True,x=700,y=600),.6)
            for target, hide in expected.items():
                if hide:
                    hide_target(target)
        def checked():
            actual = {target:obj(target).hide_get() for target in expected}
            if actual != expected:
                raise RuntimeError('Visibility did not match: '+str(actual)+' expected '+str(expected))
        do(checked,.1)

    def frame(notches=1):
        do(lambda:click(184,38),.4)
        k.menu_item(236,168,.6)
        k.wheel_out(notches)

    def top_oblique():
        do(lambda:key('NUMPAD_7',x=700,y=600),.4)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def bottom_oblique():
        do(lambda:key('NUMPAD_7',ctrl=True,x=700,y=600),.4)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_2',x=700,y=600),.3)
        do(lambda:key('NUMPAD_6',x=700,y=600),.4)

    def boolean(target):
        mods = [m for m in obj(target).modifiers if m.type == 'BOOLEAN']
        if len(mods) != 1:
            raise RuntimeError('Expected exactly one Boolean modifier')
        return mods[0]

    def bool_info(target, operation=None, tool=None):
        m = boolean(target)
        if (operation and m.operation != operation) or (tool and (not m.object or m.object.name != tool)):
            raise RuntimeError('Boolean operation/operand differ: '+str((target,m.operation,m.object.name if m.object else None)))
        return '%s：Operation %s、Solver %s、Operand %s。'%(target,m.operation,m.solver,m.object.name if m.object else '尚未指定')

    def apply_boolean(target):
        do(lambda:click(1424,320),.4)
        k.menu_item(1331,343,.8)
        def check():
            if obj(target).modifiers or not obj(target).data.polygons:
                raise RuntimeError('Boolean was not applied, or mesh is empty')
        do(check,.1)

    def non_manifold(name,slug):
        do(lambda:key('TAB',x=700,y=600),.4)
        do(lambda:key('TWO',x=700,y=600),.3)
        do(lambda:click(280,38),.3)
        k.menu_item(303,81,.4)
        search('Select Non Manifold')
        def read():
            bm = bmesh.from_edit_mesh(active().data)
            if not bm.verts or not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):
                raise RuntimeError('Non Manifold UI readback failed')
            return name+' 非空網格；Select Non Manifold 選到邊 0，實際非流形邊 0。'
        record('06-01',slug,'選 '+name+'，Tab > 邊選取 > Select None > Select Non Manifold',read,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.4)

    def body_read():
        guard()
        write('body_mesh.json',read_mesh_data(obj('Body')))
        bd = read_body_pin_and_validate(obj('Body'),state['source_body'],state['construction_pin'])
        state['body'] = bd
        return '原盒殼 60 × 40 × 30、內腔基準 56 × 36 × 28、壁／底 2 mm；含定位柱的 Body 整體高 31.5 mm。柱與底板已 Union 成單一封閉殼，非流形邊 0；突出段 Z -13～16.5 mm。'

    def lid_read():
        guard()
        write('lid_mesh.json',read_mesh_data(obj('Lid')))
        ld = read_lid_hole_and_validate(obj('Lid'),state['source_lid'])
        state['lid'] = ld
        return 'Lid 外形 60 × 40 × 6、板厚 2、環唇深 4／壁 2 mm；(23,13) 的實際 32 邊孔外接直徑 4.4 mm，Z 15～17 貫穿；單殼、非流形邊 0，新增穿孔後 genus 1。'

    def all_read():
        body_read()
        lid_read()
        a = validate_tenon_assembly(state['body'],state['lid'])
        state['assembly'] = a
        return '柱孔名義外接直徑總差 0.4 mm、名義單邊 0.2 mm；實際最小法向間隙 %.9f mm、對邊總差 %.9f mm。柱伸入孔 1.5 mm，柱頂到蓋頂餘 0.5 mm；僅數位幾何試驗。'%(a['min_normal_gap_mm'],a['across_flats_total_clearance_mm'])

    def mesh_dump(name):
        return read_mesh_data(obj(name))

    def final_objects():
        result = {}
        for name in ('Body','Lid','TenonTool','HoleTool'):
            o = obj(name)
            result[name] = dict(object_name=o.name,type=o.type,modifier_count=len(o.modifiers),scale=list(o.scale),hidden=o.hide_get())
        if any(not result[name]['hidden'] for name in ('TenonTool','HoleTool')):
            raise RuntimeError('Construction tools must be hidden before saving')
        if any(result[name]['modifier_count'] or result[name]['hidden'] for name in ('Body','Lid')):
            raise RuntimeError('Body and Lid must be visible applied final meshes')
        return result

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',source_copy.name)
    record('06-01','source-open-dialog','File > Open，開啟已驗證的 05-05 Body＋Lid 場景同雜湊副本',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','05-05 來源 v001'),k.fb_box('confirm','Open')])
    k.confirm_dialog(2)
    k.click_outliner('Body')
    top_oblique()
    frame(1)

    def original_read():
        guard()
        if Path(bpy.data.filepath).resolve() != source_copy.resolve():
            raise RuntimeError('Wrong source copy opened')
        state['source_body'] = read_body_and_validate(obj('Body'))
        state['source_lid'] = read_lid_and_validate(obj('Lid'),state['source_body'])
        write('source-geometry-verification.json',dict(passed=True,body=state['source_body'],lid=state['source_lid']))
        return '修改前重驗：盒殼 60 × 40 × 30、內腔 56 × 36 × 28、壁／底 2；蓋板厚 2、環唇深 4、Lid 整高 6 mm；來源與副本 hash 一致。'
    record('06-01','source-geometry','修改前重驗既有盒體與上蓋，這張作用中物件是 Body',original_read,park=PARK,
           highlights=[B(963,383,228,77,'原盒 Body 60 × 40 × 30 mm')])
    for name in ('Camera','Light','Lid'):
        visibility(name,True)

    search('Add Cylinder')
    for y,value in ((411,'4mm'),(430,'4mm'),(450,'30mm')):
        k.type_into(1075,y,value)
    apply_scale()
    transform('X','23mm')
    transform('Y','13mm')
    transform('Z','1.5mm')
    k.rename_active('TenonTool')
    frame(2)
    def pin_read():
        state['construction_pin'] = read_tool_and_validate(obj('TenonTool'),'pin')
        write('construction-pin-verification.json',state['construction_pin'])
        return size('TenonTool')+'實際 32 段；建構底 -13.5、頂 16.5 mm，與底板體積交入 0.5 mm，合併後內部底面會消失。'
    record('06-01','pin-tool','F3 Add Cylinder，輸入 4 × 4 × 30 mm，Apply Scale，移到 (23,13,1.5) 並命名 TenonTool',
           pin_read,park=PARK,highlights=[B(963,133,228,59,'Location 23 / 13 / 1.5 mm'),B(963,383,228,77,'定位柱 4 × 4 × 30 mm')],
           note='這些是本次助教幾何示範尺寸。單一圓柱用於對位，配合既有矩形唇邊；不宣稱圓柱本身完全限制旋轉。')
    k.click_outliner('Body')
    do(lambda:click(1245,503),.5)
    search('Add Boolean Modifier')
    do(lambda:click(1369,350),.5)
    record('06-01','union-operation','選 Body，F3 Add Boolean Modifier，將 Operation 切為 Union',
           lambda:bool_info('Body','UNION'),park=PARK,highlights=[B(1343,341,62,20,'Union')])
    do(lambda:click(1445,400),.3)
    do(lambda:click(1340,k.outliner_y('TenonTool')),.6)
    visibility('TenonTool',True)
    k.click_outliner('Body')
    top_oblique()
    frame(1)
    record('06-01','union-assigned','Object 滴管指定 TenonTool，隱藏建構柱，預覽 Body 的 Union',
           lambda:bool_info('Body','UNION','TenonTool'),park=PARK,highlights=[B(1351,389,104,22,'TenonTool')])
    apply_boolean('Body')
    record('06-01','union-applied','修改器下拉 > Apply，從最終 Body 網格量底板、柱頂、連通性與體積',body_read,park=PARK,
           highlights=[B(963,383,228,77,'含柱整高 31.5；原盒殼高 30 mm')])
    non_manifold('Body','body-non-manifold')
    visibility('Body',True)

    search('Add Cylinder')
    for y,value in ((411,'4.4mm'),(430,'4.4mm'),(450,'10mm')):
        k.type_into(1075,y,value)
    apply_scale()
    transform('X','23mm')
    transform('Y','13mm')
    transform('Z','16mm')
    k.rename_active('HoleTool')
    frame(2)
    def cutter_read():
        state['construction_cutter'] = read_tool_and_validate(obj('HoleTool'),'hole_cutter')
        write('construction-cutter-verification.json',state['construction_cutter'])
        return size('HoleTool')+'實際 32 段，Z 11～21，跨過蓋板 15～17；最終穿孔另從差集後網格驗證。'
    record('06-01','hole-tool','Add Cylinder，設 4.4 × 4.4 × 10 mm、Apply Scale，中心 (23,13,16)，命名 HoleTool',
           cutter_read,park=PARK,highlights=[B(963,383,228,77,'孔切割體 4.4 × 4.4 × 10 mm')],
           note='4.4 − 4 = 0.4 mm 是外接直徑總差試驗值；不是已列印或已試配的合格值。')
    visibility('Lid',False)
    k.click_outliner('Lid')
    search('Add Boolean Modifier')
    record('06-01','hole-boolean-empty','選 Lid 新增 Boolean，先查看實際選項與 Object 欄位位置',
           lambda:bool_info('Lid'),park=PARK)
    # The default Difference was read from the real panel above. Separate pointer
    # movement from clicking so Blender has processed the new Properties region.
    do(lambda:move(1380,400),.4)
    do(lambda:click(1380,400),.5)
    do(lambda:k.type_text('HoleTool'),.5)
    record('06-01','hole-object-search','點 Object 欄位，輸入 HoleTool，從實際搜尋清單選建構切割體',
           lambda:bool_info('Lid'),note='用物件名稱搜尋，避免滴管沒有指定到預期物件。')
    do(lambda:key('RET'),.8)
    def ensure_operand(attempt=0):
        m = boolean('Lid')
        state.setdefault('operand_attempts',[]).append(dict(attempt=attempt,operation=m.operation,operand=m.object.name if m.object else None))
        write('operand-attempts.json',state['operand_attempts'])
        if m.operation == 'DIFFERENCE' and m.object and m.object.name == 'HoleTool':
            return
        if attempt >= 2:
            raise RuntimeError('Object search did not assign HoleTool: '+str(state['operand_attempts']))
        # The filtered result row was measured from the isolated operand probe.
        # Retry locally, using the actual dropdown result rather than replaying
        # the entire modelling procedure or setting the operand through Python.
        g['queue'][0:0] = [
            (lambda:move(1380,400),.4),(lambda:click(1380,400),.5),
            (lambda:key('A',ctrl=True),.2),(lambda:k.type_text('HoleTool'),.5),
            (lambda:move(1310,432),.4),(lambda:click(1310,432),.6),
            (lambda:ensure_operand(attempt+1),.2)]
    do(ensure_operand,.1)
    visibility('HoleTool',True)
    k.click_outliner('Lid')
    do(lambda:key('NUMPAD_7',x=700,y=600),.4)
    frame(1)
    record('06-01','hole-difference','確認 Lid 的 Boolean Difference 已指定 HoleTool，隱藏切割體查看孔',
           lambda:bool_info('Lid','DIFFERENCE','HoleTool'),park=PARK,highlights=[B(1408,341,67,20,'Difference')])
    apply_boolean('Lid')
    record('06-01','hole-applied','Apply Difference，從最終孔壁量 32 邊孔，射線確認貫穿蓋板',lid_read,park=PARK,
           note='孔與既有環唇最近淨距約 0.6 mm，環壁未被切穿。閉合網格可以有真正穿孔，這裡 genus 由 0 變 1。')
    non_manifold('Lid','lid-non-manifold')
    bottom_oblique()
    frame(1)
    record('06-01','lid-underside','底部斜視，核對實際穿孔、環形唇邊與 Item Dimensions',lid_read,park=PARK,
           highlights=[B(963,383,228,77,'Lid 外形仍 60 × 40 × 6 mm')])
    visibility('Body',False)
    k.click_outliner('Lid')
    transform('Z','12mm')
    k.click_outliner('Body',ctrl=True)
    top_oblique()
    frame(1)
    record('06-01','separated-view','暫把 Lid 上抬 12 mm，查看新定位柱與對應孔，再於存檔前移回',
           lambda:size('Lid')+'這是獨立 Blender 的暫時分離檢視，不是實體試配。',park=PARK,
           note='本圖作用中為 Body，Dimensions 60 × 40 × 31.5 屬含柱盒體；蓋子尺寸請看前一張。')
    k.click_outliner('Lid')
    transform('Z','-12mm')
    k.click_outliner('Body',ctrl=True)
    frame(1)
    record('06-01','assembly-geometry','將 Lid 移回名義位置，從實際 32 邊輪廓重算相位、孔柱間隙與嵌入量',
           all_read,park=PARK,note='柱孔同相位仍需實際網格核對。數位間隙不是製造公差；列印／實測／試配結果及正式合格間隙維持空白。')
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('06-01','save-dialog','File > Save As，另存新單元場景 u06_locating_tenon_v001.blend',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','新場景 v001'),k.fb_box('confirm','Save As')])
    def safe_target():
        folder,name = k.browser()
        target = (Path(folder)/name).resolve()
        if target.parent != Path(k.demo_dir).resolve() or name != FILENAME or target.exists():
            raise RuntimeError('Unsafe or existing output version')
        guard()
        final_objects()
    do(safe_target,.1)
    k.confirm_dialog(1.8)
    def saved():
        path = Path(bpy.data.filepath).resolve()
        if path != (Path(k.demo_dir)/FILENAME).resolve() or not path.is_file():
            raise RuntimeError('New scene did not save at the intended version')
        all_read()
        state['scene_path'] = str(path)
        state['scene_sha256'] = g['sha256'](str(path))
        return '已另存 '+path.name+'，%d bytes，SHA-256 '%path.stat().st_size+state['scene_sha256']+'。原來源與副本未改。'
    record('06-01','saved','按 Save As，讀回新場景檔大小與 SHA-256',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('06-01','open-saved','File > Open，重新開啟本次已保存的定位榫場景 v001',
           lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400),
           highlights=lambda:[k.fb_box('name','同一定位榫 v001'),k.fb_box('confirm','Open')])
    k.confirm_dialog(2)
    def reopened():
        guard()
        path = Path(bpy.data.filepath).resolve()
        if str(path) != state['scene_path'] or g['sha256'](str(path)) != state['scene_sha256']:
            raise RuntimeError('Reopened scene path/hash differ')
        observation = all_read()
        tools = final_objects()
        write('body_mesh.json',mesh_dump('Body'))
        write('lid_mesh.json',mesh_dump('Lid'))
        write('pin_tool_mesh.json',mesh_dump('TenonTool'))
        write('hole_tool_mesh.json',mesh_dump('HoleTool'))
        result = dict(passed=True,kind='locating_tenon_geometry_demo',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(source_copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            source_body=state['source_body'],source_lid=state['source_lid'],scene_path=str(path),scene_sha256=state['scene_sha256'],
            scene_bytes=path.stat().st_size,reopened=True,construction_pin=state['construction_pin'],construction_cutter=state['construction_cutter'],
            body=state['body'],lid=state['lid'],assembly=state['assembly'],final_objects=tools,
            trial=dict(status='experimental_geometry_only',selected_by='tutor',diameter_total_clearance_mm=.4,nominal_radial_clearance_mm=.2,qualified_clearance_mm=None),
            exported_stl=False,slicer_checked=False,printed=False,fit_tested=False,physical_measurements=None,fit_results=None,
            physical_interference=None,qualified_clearance_mm=None,
            numericComparison=dict(dimensionsAbsMm=1e-4,volumeRelative=1e-5,purpose='Floating point reconstruction only; not manufacturing tolerance or printed fit acceptance'))
        write('verification.json',result)
        return '重新開啟後場景 hash 與幾何一致。'+observation+'未匯出 STL、未列印或試配；合格值留空。'
    record('06-01','reopened-verified','按 Open，重讀最終 Body／Lid 網格與隱藏工具，核對版本並保存驗證',
           reopened,park=PARK,note='本次是 06-01 定位榫幾何示範，不代學員確認完成；不推定第五單元已有實體合格間隙。')
