"""Unpublished native Mesh Analysis UI/RNA discovery; no geometry writes."""
import json
import math
from pathlib import Path

import bpy

from common import Kit, PARK, PROJECT
from tenon_checks import read_mesh_data

SOURCE = PROJECT/'learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/demo-files/u07_cantilever_snap_v001.blend'
SOURCE_SHA = '5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305'


def build(g):
    k = Kit(g)
    do,click,key,record = k.do,k.click,k.key,k.record
    out = Path(g['OUT'])
    copies = Path(k.demo_dir)/'sources'
    copies.mkdir()
    copy = copies/SOURCE.name
    if g['sha256'](str(SOURCE))!=SOURCE_SHA:
        raise RuntimeError('Verified snap source changed')
    copy.write_bytes(SOURCE.read_bytes())
    snaps=out/'source-snapshot'
    snaps.mkdir()
    items=[]
    for p in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
              'learning/tutor/scenarios/lesson07_overhang_probe.py','learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py'):
        target=snaps/Path(p).name
        target.write_bytes((PROJECT/p).read_bytes())
        items.append(dict(source=p,snapshot='source-snapshot/'+target.name,sha256=g['sha256'](str(target))))
    (snaps/'manifest.json').write_text(json.dumps(dict(files=items,sourceScene=str(SOURCE),sourceCopy=str(copy),sourceSha256=SOURCE_SHA),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def write(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def unchanged():
        k.guard()
        if any(g['sha256'](str(p))!=SOURCE_SHA for p in (SOURCE,copy)):
            raise RuntimeError('Source or opened copy changed')

    def rna():
        unchanged()
        sv=bpy.context.scene.tool_settings.statvis
        properties={}
        for n in ('type','overhang_axis','overhang_min','overhang_max'):
            p=sv.bl_rna.properties[n]
            value=dict(identifier=p.identifier,name=p.name,description=p.description,type=p.type,value=getattr(sv,n))
            if p.type=='ENUM':
                value['items']=[dict(identifier=e.identifier,name=e.name,description=e.description,value=e.value) for e in p.enum_items]
            else:
                value.update(subtype=p.subtype,default=p.default,hard_min=p.hard_min,hard_max=p.hard_max,soft_min=p.soft_min,soft_max=p.soft_max)
            properties[n]=value
        view=k.view3d()
        result=dict(properties=properties,overlay_show_statvis=view.overlay.show_statvis,show_overlays=view.overlay.show_overlays,
                    shading_type=view.shading.type,xray=view.shading.show_xray,mode=bpy.context.mode,
                    active=bpy.context.view_layer.objects.active.name,selected=[o.name for o in bpy.context.selected_objects],
                    min_degrees=math.degrees(sv.overhang_min),max_degrees=math.degrees(sv.overhang_max))
        write('native-statvis-rna.json',result)
        return '原生狀態 '+json.dumps(result,ensure_ascii=False)

    k.setup()
    do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    k.file_dialog(56,str(copies)+'\\',copy.name)
    record('07-03','source-dialog','開啟07-02同hash副本，僅探測原生Mesh Analysis介面',lambda:str(k.browser()),win='FILE_BROWSER',park=(300,400))
    k.confirm_dialog(2)
    k.click_outliner('Lid')
    do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Body')
    do(lambda:click(184,38),.3)
    k.menu_item(236,168,.5)
    k.wheel_out(1)
    def source_read():
        unchanged()
        for name in ('Body','Lid'):
            write('source_'+name.lower()+'_mesh.json',read_mesh_data(bpy.data.objects[name]))
        if any(not bpy.data.objects[n].hide_get() for n in ('Lid','SnapTool','FlangeTool')):
            raise RuntimeError('Only Body should be visible')
        return rna()
    record('07-03','source-state','只顯示Body，保存未旋轉幾何與原生預設值',source_read,park=PARK)
    do(lambda:key('TAB',x=700,y=600),.3)
    do(lambda:key('THREE',x=700,y=600),.2)
    do(lambda:key('A',alt=True,x=700,y=600),.2)
    record('07-03','edit-state','Edit Mode，取消選取以免選面色遮住分析色',rna,park=PARK)
    do(lambda:click(1076,38),.5)
    record('07-03','mesh-overlays-popover','點Edit Mesh專用Overlays圖示，探測Shading／Mesh Analysis控制項',rna)
    do(lambda:click(940,253),.5)
    record('07-03','native-overhang-controls','UI勾選Mesh Analysis，讀回Overhang類型／角度／軸與原生著色',rna)
