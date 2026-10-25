"""07-05: native UI independent duplicates and a single geometric length change.

The standalone anchor/beam/hook specimens are not full-box improvements or
qualified printed parts. No direct mesh, selection, object-transform or view
matrix writes are used: Python reads native UI results and protects versions.
"""
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
from overhang_checks import read_analysis_mesh_data
from coupon_checks import validate_source_snap_tool, validate_coupon, validate_coupon_layout

PLAN=PROJECT/'learning/plans/07-05-coupon-length-draft-v001.json'
PLAN_SHA='35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33'
PRIOR=PROJECT/'learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/verification.json'
PRIOR_SHA='ab84fcc47ee59d2303a1174a8b67c27c898255c5c556e3b0deaee616741b9dc7'
ORIGINALS=('Body','Lid','SnapTool','FlangeTool')
FILENAME='u07_cantilever_length_coupons_v001.blend'


def build(g):
    return _build(g,False)


def build_probe(g):
    return _build(g,True)


def _build(g,probe):
    k=Kit(g)
    do,click,key,move,record=k.do,k.click,k.key,k.move,k.record
    out=Path(g['OUT']);sources=Path(k.demo_dir)/'sources';sources.mkdir()
    if g['sha256'](str(PLAN))!=PLAN_SHA:raise RuntimeError('Fixed coupon draft changed')
    plan=json.loads(PLAN.read_text('utf-8'));variants=plan['coupon_objects']
    source=PROJECT/plan['source_scene']['path'];source_sha=plan['source_scene']['sha256']
    copy=sources/source.name
    bindings_input=[(PLAN,'coupon-plan-v001.json'),(PRIOR,'source-orientation-verification.json')]
    fixed=[(PLAN,PLAN_SHA),(PRIOR,PRIOR_SHA),(source,source_sha)]
    for field,name in (('source_tool_mesh','source-snap-tool-reference.json'),('source_geometry_record','source-geometry-record-v001.json'),
                       ('continuity_reference','source-export-record-v001.json')):
        original=PROJECT/plan[field]['path'];fixed.append((original,plan[field]['sha256']));bindings_input.append((original,name))
    for p,h in fixed:
        if g['sha256'](str(p))!=h:raise RuntimeError('Protected coupon input changed: '+str(p))
    copy.write_bytes(source.read_bytes())
    prior=json.loads(PRIOR.read_text('utf-8'))
    snaps=out/'source-snapshot';snaps.mkdir();files=[]
    dependencies=['learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
        'learning/tutor/scenarios/lesson07_coupons.py','learning/tutor/scenarios/coupon_checks.py',
        'learning/tutor/scenarios/overhang_checks.py','learning/tutor/scenarios/snapfit_checks.py',
        'learning/tutor/scenarios/snapfit_stl_checks.py','learning/tutor/scenarios/stl_checks.py',
        'learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py']
    if probe:dependencies.append('learning/tutor/scenarios/lesson07_coupons_probe.py')
    for relative in dependencies:
        target=snaps/Path(relative).name;target.write_bytes((PROJECT/relative).read_bytes())
        files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    bindings=[]
    for original,name in bindings_input:
        target=snaps/name;target.write_bytes(original.read_bytes())
        bindings.append(dict(source=original.relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+name,sha256=g['sha256'](str(target))))
    manifest=dict(recordedAt=datetime.now(timezone.utc).isoformat(),files=files,dataBindings=bindings,
                  sourceScene=str(source),sourceCopy=str(copy),sourceSha256=source_sha)
    (snaps/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state=dict(source_frame={},candidates={},selection_proofs={},motion_proofs={},duplicates={})
    names=[v['name'] for v in variants]
    geometry_keys=('type','scale','modifier_count','matrix_world','local_mesh_sha256','mesh_data_name')

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        for p,h in fixed+[(copy,source_sha)]:
            if g['sha256'](str(p))!=h:raise RuntimeError('Original, copy, plan or previous record changed: '+str(p))

    def obj(name):return bpy.data.objects[name]

    def inventory(which=None):
        result={}
        for name in which or list(bpy.data.objects.keys()):
            o=obj(name)
            shape=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons])
            result[name]=dict(type=o.type,hidden=o.hide_get(),scale=list(o.scale),modifier_count=len(o.modifiers),
                matrix_world=[list(row) for row in o.matrix_world],location_mm=list(o.location),
                rotation_euler_radians=list(o.rotation_euler),object_axis_dimensions_mm=list(o.dimensions),mesh_data_name=o.data.name,
                local_mesh_sha256=hashlib.sha256(json.dumps(shape,separators=(',',':')).encode()).hexdigest())
        return result

    def sources_unchanged(final=False):
        unchanged();current=inventory(ORIGINALS)
        for name in ORIGINALS:
            if any(current[name][field]!=state['source_objects'][name][field] for field in geometry_keys):
                raise RuntimeError('Original source object geometry/matrix/datablock changed: '+name)
            if final and not current[name]['hidden']:raise RuntimeError('All four source objects must finish hidden')
        return current

    def raw(name,filename):
        o=obj(name);d=read_analysis_mesh_data(o)
        d['cad_metadata'].update(matrix_world=[list(row) for row in o.matrix_world],
            object_rotation_euler_degrees=[math.degrees(a) for a in o.rotation_euler],
            object_axis_dimensions_mm=list(o.dimensions),mesh_data_name=o.data.name)
        write(filename,d);return d

    def frame(notches=1):
        def x():return 236 if bpy.context.mode=='EDIT_MESH' else 184
        def item():return 288 if bpy.context.mode=='EDIT_MESH' else 236
        do(lambda:click(x(),38),.3);do(lambda:move(item(),168),.3);do(lambda:click(item(),168),.5);k.wheel_out(notches)

    def front():do(lambda:key('NUMPAD_1',x=700,y=600),.3)

    def oblique():
        do(lambda:key('NUMPAD_7',x=700,y=600),.3);do(lambda:key('NUMPAD_2',x=700,y=600),.2)
        do(lambda:key('NUMPAD_2',x=700,y=600),.2);do(lambda:key('NUMPAD_6',x=700,y=600),.3)

    def hide(name):
        k.click_outliner(name)
        def press():
            if bpy.context.view_layer.objects.active!=obj(name):raise RuntimeError('Wrong source/coupon before Hide '+name)
            if not obj(name).hide_get():key('H',x=700,y=600)
        do(press,.3)

    def solo(name):
        do(lambda:key('H',alt=True,x=700,y=600),.4)
        def queue_hides():
            actions=[]
            for target in bpy.data.objects.keys():
                if target!=name:
                    actions.extend([(lambda n=target:click(1340,k.outliner_y(n)),.3),
                        (lambda n=target:key('H',x=700,y=600) if not obj(n).hide_get() else None,.3)])
            actions.extend([(lambda:click(1340,k.outliner_y(name)),.4)])
            g['queue'][0:0]=actions
        do(queue_hides,.1)
        def check():
            if any(o.hide_get()!=(o.name!=name) for o in bpy.data.objects):raise RuntimeError('Solo visibility differs')
            if bpy.context.view_layer.objects.active!=obj(name):raise RuntimeError('Wrong solo active object')
        do(check,.1)

    def projected(point):
        a=k.area('VIEW_3D');r=next(r for r in a.regions if r.type=='WINDOW')
        p=location_3d_to_region_2d(r,a.spaces.active.region_3d,Vector(point))
        if p is None:raise RuntimeError('Coupon selection point outside projection')
        return r.x+p.x,k.window().height-r.y-p.y

    def signature(points):return sorted(tuple(round(v,4) for v in p) for p in points)

    def upper_selection(v):
        o=obj(v['name']);bm=bmesh.from_edit_mesh(o.data)
        if not k.view3d().shading.show_xray or k.view3d().overlay.show_statvis or bpy.context.scene.transform_orientation_slots[0].type!='GLOBAL':
            raise RuntimeError('Vertex box selection needs Xray, no inherited analysis, and Global orientation')
        selected=[list(o.matrix_world@vertex.co) for vertex in bm.verts if vertex.select]
        expected=[p for p in state['source_raw']['vertices'] if p[2]>=10.9999]
        info=dict(variant=v['name'],expected_count=14,selected_count=len(selected),selected_world_vertices_mm=selected,
                  original_upper_vertices_mm=expected,selection_method='Front orthographic / Vertex / Xray / native B box select',
                  box_source_world_mm=dict(x=[-5,5],z=[10,14]))
        state['selection_proofs'][v['name']]=info;write('upper-vertex-selection-proofs.json',state['selection_proofs'])
        if len(selected)!=14 or signature(selected)!=signature(expected):raise RuntimeError('Native box selection did not select exactly the original 14 upper vertices')
        return '%s：原生B框選實際14頂點，world Z11／12.2／13，沒有選入根部、miter或anchor；讀回全點座標已保存。'%v['name']

    def box_upper():
        a=projected((-5,-22.2,14));b=projected((5,-22.2,10))
        if not (0<a[0]<b[0]<950 and 55<a[1]<b[1]<920):raise RuntimeError('Native selection rectangle does not fit viewport')
        k.drag_slow([a,b],button='LEFTMOUSE')

    def motion(v):
        mesh=raw(v['name'],v['name']+'_source_frame_mesh.json');source_raw=state['source_raw'];delta=v['upper_vertex_translation_z_mm']
        if mesh['polygons']!=source_raw['polygons'] or len(mesh['vertices'])!=42:raise RuntimeError('Coupon mesh topology changed')
        upper=[];unchanged_points=[];maximum=0
        for index,(old,new) in enumerate(zip(source_raw['vertices'],mesh['vertices'])):
            expected=list(old)
            if old[2]>=10.9999:expected[2]+=delta;upper.append(index)
            else:unchanged_points.append(index)
            residual=max(abs(a-b) for a,b in zip(expected,new));maximum=max(maximum,residual)
            if residual>1e-4:raise RuntimeError('Coupon edit moved a protected vertex or incorrect axis/amount')
        proof=dict(variant=v['name'],upper_vertex_count=len(upper),unchanged_vertex_count=len(unchanged_points),
            upper_source_vertex_indices=upper,unchanged_source_vertex_indices=unchanged_points,translation_z_mm=delta,
            maximum_coordinate_residual_mm=maximum,polygon_topology_unchanged=True,
            coupon_geometry_modified=delta!=0,source_frame_origin_unchanged=True)
        if len(upper)!=14 or len(unchanged_points)!=28:raise RuntimeError('Unexpected source vertex partition')
        state['motion_proofs'][v['name']]=proof;write('vertex-motion-proofs.json',state['motion_proofs'])
        result=validate_coupon(source_raw,mesh,v['name'],pose='source_frame',plan=plan)
        state['source_frame'][v['name']]=result;sources_unchanged()
        return '%s：只將原14個上端頂點沿Z移%g mm；其他28點與polygons拓撲不變。根平面至承接面幾何L=%g、全試片高%g mm，並非力學有效L。'%(v['name'],delta,v['L_geometry_mm'],v['whole_coupon_height_mm'])

    def independent():
        objs=[obj(n) for n in names if n in bpy.data.objects]
        data=[o.data for o in objs]
        source_data={obj(n).data.as_pointer() for n in ORIGINALS}
        if len({d.as_pointer() for d in data})!=len(data) or any(o.data.as_pointer() in source_data for o in objs):
            raise RuntimeError('Coupon duplicates must use independent meshes, not linked source data')
        return {o.name:o.data.name for o in objs}

    def candidate(v):
        sources_unchanged();independent()
        mesh=raw(v['name'],v['name']+'_candidate_mesh.json')
        state['candidates'][v['name']]=validate_coupon(state['source_raw'],mesh,v['name'],pose='print_candidate',plan=plan)
        dims=[max(p[i] for p in mesh['vertices'])-min(p[i] for p in mesh['vertices']) for i in range(3)]
        minimum=min(p[2] for p in mesh['vertices'])
        bed=state['candidates'][v['name']]['bed_and_raised_features'];raised=bed['raised_features']
        return ('%s：Ry90保留、Scale1，物件Location%s；world外框%s mm、最低Z %.9g mm。'
            '接床僅anchor側面約%.6g mm²；直臂最低Z %.6g、根部／miter最低Z %.6g mm。'
            '只是獨立anchor試片的幾何擺向，支撐／材料／有效L仍待定。')%(v['name'],list(obj(v['name']).location),[round(d,6) for d in dims],minimum,
                bed['bed_contact_area_mm2'],raised['straight_beam']['world_z_range_mm'][0],raised['root_fillet_and_miters']['world_z_range_mm'][0])

    def non_manifold(v):
        do(lambda:key('TAB',x=700,y=600),.3);do(lambda:key('TWO',x=700,y=600),.2);do(lambda:key('A',alt=True,x=700,y=600),.2)
        do(lambda:key('F3',x=700,y=600),.3);do(lambda:k.type_text('Select Non Manifold'),.3);do(lambda:key('RET'),.7)
        def check():
            bm=bmesh.from_edit_mesh(obj(v['name']).data)
            if not bm.faces or any(not e.is_manifold or e.select for e in bm.edges):raise RuntimeError('Native coupon Non Manifold check failed')
            return v['name']+'：原生Select Non Manifold選到0邊，非空閉合網格。這不是強度或可列印合格判定。'
        record('07-05',v['name']+'-non-manifold','Tab > Edge Select > Select None > Select Non Manifold，核對單一試片',check,park=PARK)
        do(lambda:key('TAB',x=700,y=600),.3)

    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(sources)+'\\',copy.name)
    record('07-05','source-dialog','File > Open，開啟07-03同hash副本；不動既有盒體與上蓋',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def source_read():
        unchanged()
        if set(bpy.data.objects.keys())!=set(ORIGINALS) or Path(bpy.data.filepath).resolve()!=copy.resolve():raise RuntimeError('Wrong four-object source copy')
        state['source_objects']=inventory(ORIGINALS)
        if state['source_objects']['SnapTool']['local_mesh_sha256']!=prior['final_tools']['SnapTool']['local_mesh_sha256']:
            raise RuntimeError('Original SnapTool shape differs from protected 07-03 tool')
        state['source_raw']=raw('SnapTool','source_snap_tool_mesh.json')
        state['source_tool']=validate_source_snap_tool(state['source_raw'])
        write('source-object-inventory.json',state['source_objects'])
        return '原SnapTool為42頂點／80三角面，R0／Scale1；原點(0,−22.2000007629,−9.5)。保存四件來源局部mesh指紋與matrix，之後只改可見性。'
    record('07-05','source-reference','先讀取原SnapTool與四個來源物件，固定比較基準',source_read,park=PARK)
    do(lambda:k.drag_slow([(1305,207),(1305,330)],button='LEFTMOUSE'),.1)
    def outliner_check():
        a=k.area('OUTLINER')
        if a.height<270:raise RuntimeError('Outliner divider resize did not make seven object rows visible')
        return '原生拖曳Outliner／Properties分隔線；Outliner高度%d，可顯示保留來源與三件試片。'%a.height
    record('07-05','outliner-room','加高Outliner，避免新增三試片後名稱被裁切',outliner_check,park=PARK)

    for v in variants:
        solo('SnapTool');front();frame(1)
        do(lambda:key('D',shift=True,x=700,y=600),.3);do(lambda:key('ESC',x=700,y=600),.4)
        k.rename_active(v['name'])
        def duplicated(variant=v):
            if bpy.context.view_layer.objects.active!=obj(variant['name']):raise RuntimeError('Wrong duplicate active')
            independent();sources_unchanged()
            if list(obj(variant['name']).location)!=plan['source_object_origin_mm'] or any(abs(a)>1e-7 for a in obj(variant['name']).rotation_euler):
                raise RuntimeError('Shift+D cancellation changed source-frame transform')
            state['duplicates'][variant['name']]=dict(source_object='SnapTool',operation='native Shift+D then Esc',mesh_data_name=obj(variant['name']).data.name,
                independent_from_source=True,location_mm=list(obj(variant['name']).location),rotation_euler_radians=list(obj(variant['name']).rotation_euler))
            write('duplicate-proofs.json',state['duplicates'])
            return variant['name']+'：Shift+D後Esc只取消移動，副本仍在；已讀回獨立mesh，原點／R0保持。'
        record('07-05',v['name']+'-duplicate','從原SnapTool另建獨立 '+v['name']+'；不複製前一個已修改試片',duplicated,park=PARK)
        hide('SnapTool');k.click_outliner(v['name'])
        do(lambda:key('TAB',x=700,y=600),.3);do(lambda:key('ONE',x=700,y=600),.2);do(lambda:key('A',x=700,y=600),.2)
        if v['name']==names[0]:
            do(lambda:click(1076,38),.4)
            def native_analysis_off():
                if k.view3d().overlay.show_statvis:click(940,253)
            do(native_analysis_off,.4)
            def display_read():
                view=k.view3d()
                state['display_settings']=dict(show_statvis=view.overlay.show_statvis,shading=view.shading.type,
                    deactivated_with='native Edit Mesh Overlays / Mesh Analysis checkbox',new_overhang_analysis_performed=False)
                write('native-display-settings.json',state['display_settings'])
                if state['display_settings']['show_statvis']:raise RuntimeError('Inherited Mesh Analysis must be disabled using the native checkbox')
                return '實際Mesh Analysis checkbox已關，show_statvis=false；07-05只做幾何對照，沒有重做Overhang或支撐分析。'
            record('07-05','inherited-analysis-off','Edit Mesh Overlays，關閉07-03留下的Mesh Analysis顯示，避免誤認本步做了分析',display_read)
            do(lambda:key('ESC'),.3)
        front();frame(1);do(lambda:key('A',alt=True,x=700,y=600),.2)
        def xray_on():
            if not k.view3d().shading.show_xray:key('Z',alt=True,x=700,y=600)
        do(xray_on,.3);do(lambda:key('B',x=700,y=600),.3);do(box_upper,.1)
        record('07-05',v['name']+'-upper-selection','Front Orthographic＋Vertex Select＋Xray，只B框選source Z≥11的完整上端',lambda variant=v:upper_selection(variant),park=PARK,
            note='畫面N面板的Local Median是選取平均座標，並非幾何L或world Z；本步逐點座標由原物件matrix讀回，保留原點(0,−22.2000007629,−9.5)。')
        if v['upper_vertex_translation_z_mm']:
            do(lambda:key('G',x=700,y=600),.2);do(lambda:key('Z'),.2)
            do(lambda variant=v:k.type_text(str(variant['upper_vertex_translation_z_mm'])+'mm'),.2);do(lambda:key('RET'),.4)
        do(lambda:key('TAB',x=700,y=600),.3)
        def xray_off():
            if k.view3d().shading.show_xray:key('Z',alt=True,x=700,y=600)
        do(xray_off,.3)
        record('07-05',v['name']+'-source-frame','讀回source-frame實際頂點移動、28個未動點與L幾何定義',lambda variant=v:motion(variant),park=PARK)
        do(lambda:key('R',x=700,y=600),.2);do(lambda:key('Y'),.2);do(lambda:k.type_text('90'),.2);do(lambda:key('RET'),.4)
        for y,value in zip((141,161,181),v['candidate_object_location_mm']):k.type_into(1075,y,str(value)+'mm')
        oblique();frame(1)
        record('07-05',v['name']+'-candidate','Object Mode Ry90後，以N面板Location作獨立候選擺位；不Apply Rotation',lambda variant=v:candidate(variant),park=PARK,
            note='來源物件軸尺寸與旋轉後world外框分開。臂長只為幾何對照，未驗證完整盒體邊界、夾持、材料、撓度或改善。')
        non_manifold(v)

    do(lambda:key('H',alt=True,x=700,y=600),.4)
    for name in ORIGINALS:hide(name)
    k.click_outliner('A_L19');k.click_outliner('B_L17',ctrl=True);k.click_outliner('C_L21',ctrl=True)
    oblique();frame(1)
    def layout_read():
        sources_unchanged(final=True);independent()
        if set(bpy.data.objects.keys())!=set(ORIGINALS+tuple(names)) or any(obj(n).hide_get() for n in names):raise RuntimeError('Final coupon/source inventory differs')
        for variant in variants:candidate(variant)
        state['layout']=validate_coupon_layout(state['candidates'],plan)
        return 'A_L19／B_L17／C_L21三件獨立mesh均Ry90候選、各自world Z≈0，沿Y分列−12／0／12。原Body／Lid／SnapTool／FlangeTool全hidden且原形與matrix不變；無STL、無力學改善結論。'
    record('07-05','coupon-layout','顯示三件單參數幾何對照；來源四件隱藏，核對三者分離與world落床',layout_read,park=PARK)
    if probe:return
    k.file_dialog(163,k.demo_dir,FILENAME)
    record('07-05','save-dialog','File > Save As，另存獨立長度對照草案新版本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    def safe_save():
        folder,name=k.browser();target=(Path(folder)/name).resolve()
        if target.parent!=Path(k.demo_dir).resolve() or name!=FILENAME or target.exists():raise RuntimeError('Unsafe or existing coupon scene version')
        sources_unchanged(final=True)
    do(safe_save,.1);k.confirm_dialog(1.8)
    def saved():
        p=Path(bpy.data.filepath).resolve()
        if p!=(Path(k.demo_dir)/FILENAME).resolve() or not p.is_file():raise RuntimeError('New coupon scene not saved')
        state.update(scene_path=str(p),scene_sha256=g['sha256'](str(p)),scene_bytes=p.stat().st_size)
        return '新coupon場景%d bytes，SHA-256 %s；07-03原scene／副本及先前匯出不覆寫。'%(state['scene_bytes'],state['scene_sha256'])
    record('07-05','saved','讀回新場景路徑／bytes／SHA-256，與所有舊版本分開保存',saved,park=PARK)
    k.file_dialog(56,k.demo_dir,FILENAME)
    record('07-05','open-saved','File > Open，重開同一coupon新版本',lambda:'資料夾 %s；檔名 %s。'%k.browser(),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    def reopened():
        p=Path(bpy.data.filepath).resolve()
        if str(p)!=state['scene_path'] or g['sha256'](str(p))!=state['scene_sha256']:raise RuntimeError('Reopened coupon checkpoint differs')
        layout_read();final_sources=sources_unchanged(final=True);final=inventory();independent()
        if k.view3d().overlay.show_statvis:raise RuntimeError('Reopened coupon scene must not display inherited Mesh Analysis')
        record_path=out/'coupon-record-v001.json'
        write(record_path.name,dict(plan,recordedAt=datetime.now(timezone.utc).isoformat(),
            reference_scene=dict(path=str(p),sha256=state['scene_sha256'],bytes=state['scene_bytes'],scene_role='standalone_length_geometry_comparison_draft'),
            geometry_readback=dict(source_tool=state['source_tool'],source_frame=state['source_frame'],candidates=state['candidates'],layout=state['layout']),
            source_geometry_modified=False,coupon_geometry_modified=True,per_variant_geometry_modified={v['name']:v['upper_vertex_translation_z_mm']!=0 for v in variants}))
        result=dict(passed=True,kind='snapfit_length_coupons_geometry_demo',source_scene_path=str(source),source_scene_sha256=source_sha,
            opened_scene_path=str(copy),opened_scene_sha256=source_sha,source_unchanged=True,opened_copy_unchanged=True,
            draft_plan_path=str(PLAN),draft_plan_sha256=PLAN_SHA,source_tool_mesh_path=str(PROJECT/plan['source_tool_mesh']['path']),source_tool_mesh_sha256=plan['source_tool_mesh']['sha256'],
            source_geometry_record_path=str(PROJECT/plan['source_geometry_record']['path']),source_geometry_record_sha256=plan['source_geometry_record']['sha256'],
            continuity_reference_path=str(PROJECT/plan['continuity_reference']['path']),continuity_reference_sha256=plan['continuity_reference']['sha256'],
            scene_path=str(p),scene_sha256=state['scene_sha256'],scene_bytes=state['scene_bytes'],reopened=True,
            coupon_record_path=str(record_path),coupon_record_sha256=g['sha256'](str(record_path)),source_tool=state['source_tool'],source_objects=state['source_objects'],
            final_source_objects=final_sources,source_frame=state['source_frame'],candidates=state['candidates'],selection_proofs=state['selection_proofs'],
            motion_proofs=state['motion_proofs'],duplicate_proofs=state['duplicates'],layout=state['layout'],final_objects=final,independent_coupon_meshes=True,
            display_settings=state['display_settings'],
            source_geometry_modified=False,coupon_geometry_modified=True,per_variant_geometry_modified={v['name']:v['upper_vertex_translation_z_mm']!=0 for v in variants},
            full_box_modified=False,full_box_boundary_equivalence=None,anchor_clamping_or_fixture=None,effective_mechanical_length_mm=None,
            rotation_applied_to_mesh=False,exported_stl=False,mesh_analysis_overhang_checked=False,support_required=None,final_print_orientation_approved=None,
            slicer_support_settings=None,bridge_or_support_qualified=None,improvement_validated=None,material_grade=None,epsilon_allow=None,Q=None,
            required_deflection_mm=None,delta_allow_mm=None,forces=None,physical_measurements=None,fit_results=None,physical_interference=None,
            qualified_strength_N=None,qualified_clearance_mm=None,**plan['performed_flags'],
            numericComparison=dict(positionEpsilonMm=1e-4,volumeRelativeEpsilon=1e-5,purpose='Floating point geometry reconstruction only; not manufacturing, support, strength, printability or fit acceptance'))
        write('verification.json',result)
        return '重開新檔後三試片形狀／候選擺位及獨立mesh皆核對；source四件原形與matrix未動。只變B/C上端幾何L，A為原草案參照；有效力學L、改善、材料、支撐、列印與試配仍待定。'
    record('07-05','reopened-verified','Open後重驗三試片、七份raw、來源保護及新版本，保存coupon對照紀錄',reopened,park=PARK)
