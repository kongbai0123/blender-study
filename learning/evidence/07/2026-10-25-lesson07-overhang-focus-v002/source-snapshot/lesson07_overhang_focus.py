"""Read-only native view evidence of the elevated inverted-lid ledge."""
import hashlib
import json
import math
from pathlib import Path

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import Kit, PARK, PROJECT
from overhang_checks import read_analysis_mesh_data, validate_orientation

MAIN=PROJECT/'learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001'
SOURCE=MAIN/'demo-files/u07_print_orientation_v001.blend'
SOURCE_SHA='360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d'


def build(g):
    k=Kit(g)
    do,click,key,move,record=k.do,k.click,k.key,k.move,k.record
    out=Path(g['OUT']);copies=Path(k.demo_dir)/'sources';copies.mkdir()
    copy=copies/SOURCE.name
    if g['sha256'](str(SOURCE))!=SOURCE_SHA:
        raise RuntimeError('Candidate source version changed')
    copy.write_bytes(SOURCE.read_bytes())
    snaps=out/'source-snapshot';snaps.mkdir();items=[]
    for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
        'learning/tutor/scenarios/lesson07_overhang_focus.py','learning/tutor/scenarios/overhang_checks.py',
        'learning/tutor/scenarios/snapfit_checks.py','learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py'):
        target=snaps/Path(relative).name;target.write_bytes((PROJECT/relative).read_bytes())
        items.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    bindings=[]
    for name in ('verification.json','source_lid_mesh.json','lid_candidate_mesh.json'):
        target=snaps/('main-'+name);target.write_bytes((MAIN/name).read_bytes())
        bindings.append(dict(source=(MAIN/name).relative_to(PROJECT).as_posix(),snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snaps/'manifest.json').write_text(json.dumps(dict(files=items,dataBindings=bindings,sourceScene=str(SOURCE),sourceCopy=str(copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    source_raw=json.loads((snaps/'main-source_lid_mesh.json').read_text('utf-8'))
    baseline_raw=json.loads((snaps/'main-lid_candidate_mesh.json').read_text('utf-8'))
    state={'orbit':[]}

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        if any(g['sha256'](str(p))!=SOURCE_SHA for p in (SOURCE,copy)):
            raise RuntimeError('Original or focus copy changed')

    def settings():
        unchanged();v=k.view3d();s=bpy.context.scene.tool_settings.statvis
        result=dict(type=s.type,axis=s.overhang_axis,minimum_radians=float(s.overhang_min),maximum_radians=float(s.overhang_max),
            minimum_deg=math.degrees(s.overhang_min),maximum_deg=math.degrees(s.overhang_max),show_statvis=v.overlay.show_statvis,
            show_overlays=v.overlay.show_overlays,shading=v.shading.type,xray=v.shading.show_xray)
        if not result['show_statvis'] or result['xray']:
            raise RuntimeError('Original native analysis setting must stay enabled without Xray')
        return result

    def camera():
        region=k.view3d().region_3d;direction=region.view_rotation@Vector((0,0,1))
        return dict(camera_direction_world=list(direction),elevation_degrees=math.degrees(math.asin(max(-1,min(1,direction.z)))),
            view_location=list(region.view_location),view_distance=region.view_distance,view_perspective=region.view_perspective)

    def projected(point):
        a=k.area('VIEW_3D');r=next(r for r in a.regions if r.type=='WINDOW')
        p=location_3d_to_region_2d(r,a.spaces.active.region_3d,Vector(point))
        if p is None:raise RuntimeError('Target outside view')
        return r.x+p.x,k.window().height-r.y-p.y

    def wheel_up(count):
        p=projected(state['target'])
        move(*p)
        for _ in range(count):g['_event'](k.window(),'WHEELUPMOUSE','PRESS',*p)

    def mesh_check():
        raw=read_analysis_mesh_data(bpy.data.objects['Lid'])
        if raw['vertices']!=baseline_raw['vertices'] or raw['triangles']!=baseline_raw['triangles'] or raw['polygons']!=baseline_raw['polygons']:
            raise RuntimeError('Read-only focus changed candidate geometry or pose')
        result=validate_orientation(source_raw,raw,'lid',settings(),pose='candidate')
        write('focus_lid_candidate_mesh.json',raw)
        return result

    def target_face():
        raw=read_analysis_mesh_data(bpy.data.objects['Lid']);matches=[]
        for i,(poly,n) in enumerate(zip(raw['polygons'],raw['polygon_normals_world'])):
            pts=[raw['vertices'][v] for v in poly]
            if n[2]<-.999 and min(p[2] for p in pts)>1e-4:
                matches.append((i,pts,n))
        if len(matches)!=1:raise RuntimeError('Expected one elevated downward ledge polygon')
        i,points,normal=matches[0]
        state['target']=[sum(p[a] for p in points)/len(points) for a in range(3)]
        state['target_face']=dict(polygon_index=i,vertices_mm=points,normal_world=normal,centre_mm=state['target'])
        write('target-face.json',state['target_face'])
        return '實際高處朝下polygon %d，中心 %s mm，normal %s；僅調整視角／縮放，不變更模型。'%(i,state['target'],normal)

    def adjust_camera(attempt=0):
        c=camera();state['orbit'].append(c);write('view-orbit.json',state['orbit'])
        angle=c['elevation_degrees']
        if -5<angle<-1:return
        if attempt>=2 or abs(angle)<1e-5:return
        dy=max(-40,min(40,12*(-3-angle)/angle))
        # Pure native MMB motion calibrated from the first real orbit readback.
        g['drag_slow']([(600,500),(600,500+dy)],button='MIDDLEMOUSE')
        g['queue'].insert(4,(lambda:adjust_camera(attempt+1),.2))

    def orbit_preference():
        # Only this runner's isolated factory-startup preferences are changed.
        # The actual view navigation remains native NUMPAD_2, not an RNA view write.
        view=bpy.context.preferences.view
        prop=view.bl_rna.properties['rotation_angle']
        before=float(view.rotation_angle)
        desired=math.radians(3) if prop.subtype=='ANGLE' else 3.0
        view.rotation_angle=desired
        state['orbit_preference']=dict(property='preferences.view.rotation_angle',
            subtype=prop.subtype,unit=prop.unit,before=before,after=float(view.rotation_angle),
            requested_degrees=3.0,isolated_runner_only=True,saved_preferences=False,
            geometry_or_view_matrix_written=False)
        write('isolated-orbit-preference.json',state['orbit_preference'])

    def selected():
        o=bpy.data.objects['Lid'];bm=bmesh.from_edit_mesh(o.data);faces=[f for f in bm.faces if f.select]
        info=[]
        for f in faces:
            points=[list(o.matrix_world@v.co) for v in f.verts]
            normal=list((o.matrix_world.to_3x3().inverted().transposed()@f.normal).normalized())
            info.append(dict(vertices_mm=points,normal_world=normal))
        state['selected_faces']=info;write('selected-focus-faces.json',info)
        state['correct_selected_face']=len(info)==1 and info[0]['normal_world'][2]<-.999 and all(abs(p[2]-state['target'][2])<1e-4 for p in info[0]['vertices_mm'])
        return 'UI實選%d面；是否為高處朝下凸緣面：%s。'%(len(info),state['correct_selected_face'])

    def overview():
        result=mesh_check();c=camera();write('focus-view-state.json',c)
        return 'Native Overhang −Z／0～45°；實際視線仰角 %.6g°，高處polygon最低Z %.6g mm；原候選姿態、形狀及來源hash未變。'%(c['elevation_degrees'],min(p[2] for p in state['target_face']['vertices_mm']))

    k.setup();do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(copies)+'\\',copy.name)
    record('07-03','focus-source-dialog','唯讀開啟已驗方向候選同hash副本',lambda:str(k.browser()),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Body');do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Lid')
    do(lambda:click(184,38),.3);k.menu_item(236,168,.5);k.wheel_out(1)
    record('07-03','target-polygon','讀回高處朝下凸緣的實際polygon位置，不改模型',target_face,park=PARK)
    do(lambda:key('TAB',x=700,y=600),.3);do(lambda:key('THREE',x=700,y=600),.2);do(lambda:key('A',alt=True,x=700,y=600),.2)
    do(lambda:click(1076,38),.4)
    record('07-03','focus-native-controls','核對沿用正式比較的原生Overhang設定',lambda:json.dumps(settings(),ensure_ascii=False))
    do(lambda:key('ESC'),.3);do(orbit_preference,.2);do(lambda:key('NUMPAD_1',x=700,y=600),.3)
    do(lambda:key('NUMPAD_2',x=700,y=600),.6)
    def check_shallow():
        c=camera();state['orbit'].append(c);write('view-orbit.json',state['orbit'])
        if not -5<c['elevation_degrees']<-1:
            raise RuntimeError('Native NUMPAD_2 did not yield the intended shallow negative elevation')
    do(check_shallow,.3)
    do(lambda:wheel_up(6),.7)
    record('07-03','shallow-native-view','僅將獨立偏好Rotation Angle設3°，原生Numpad2淺角繞視；不改形狀／姿態',overview,park=PARK)
    do(lambda:click(*projected(state['target'])),.5)
    record('07-03','selected-ledge','UI點選實際高處朝下凸緣，讀回所選面法線及高度',selected,park=PARK)
    def frame_selected():
        if state.get('correct_selected_face'):
            g['queue'][0:0]=[(lambda:click(236,38),.3),(lambda:move(288,168),.3),(lambda:click(288,168),.5)]
    do(frame_selected,.1)
    do(lambda:key('A',alt=True,x=700,y=600),.3)
    do(lambda:wheel_up(2),.7)
    record('07-03','elevated-ledge-closeup','取消選取色後，以真實Native Overhang視圖近看高處凸緣',overview,park=PARK,
           note='獨立附證視角，沒有修改形狀／姿態／正式scene或補畫著色。是否需支撐仍待切片。')
    def final():
        result=mesh_check()
        write('focus-verification.json',dict(passed=True,kind='native_overhang_view_evidence',source_scene_path=str(SOURCE),source_scene_sha256=SOURCE_SHA,
            opened_scene_path=str(copy),opened_scene_sha256=SOURCE_SHA,source_unchanged=True,opened_copy_unchanged=True,
            read_only_view=True,geometry_unchanged=True,pose_unchanged=True,saved_new_scene=False,
            analysis_settings=settings(),camera=camera(),isolated_orbit_preference=state.get('orbit_preference'),target_face=state['target_face'],correct_ui_selected_face=state.get('correct_selected_face',False),
            candidate_geometry_readback=result,source_main_run=str(MAIN),visual_clarity_requires_image_review=True,
            support_required=None,slicer_checked=False,printed=False,fit_tested=False,qualified_strength_N=None,qualified_clearance_mm=None))
    do(final,.2)
