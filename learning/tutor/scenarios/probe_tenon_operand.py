"""Short isolated UI probe for Boolean operand selection; no scene saves."""
from pathlib import Path
import bpy
from common import Kit, PARK, PROJECT
import json
from tenon_checks import read_mesh_data
from lid_checks import read_body_and_validate, read_lid_and_validate


def build(g):
    k=Kit(g)
    do,key,click,record=k.do,k.key,k.click,k.record
    source=PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
    directory=Path(k.demo_dir)/'sources'
    directory.mkdir()
    copy=directory/source.name
    copy.write_bytes(source.read_bytes())
    def search(text):
        do(lambda:key('F3',x=700,y=600),.3)
        do(lambda:k.type_text(text),.3)
        do(lambda:key('RET'),.8)
    def info():
        m=next(m for m in bpy.data.objects['Lid'].modifiers if m.type=='BOOLEAN')
        return 'Actual modifier: %s / %s; objects %s'%(m.operation,m.object.name if m.object else None,[(o.name,o.hide_get()) for o in bpy.context.scene.objects])
    k.setup()
    k.file_dialog(56,str(directory)+'\\',copy.name)
    k.confirm_dialog(1.8)
    def source_read():
        body=read_body_and_validate(bpy.data.objects['Body'])
        lid=read_lid_and_validate(bpy.data.objects['Lid'],body)
        (Path(g['OUT'])/'source-geometry-verification.json').write_text(json.dumps(dict(passed=True,body=body,lid=lid),indent=2)+'\n',encoding='utf-8')
    do(source_read,.1)
    search('Add Cube')
    k.rename_active('TenonTool')
    do(lambda:key('H',x=700,y=600),.4)
    search('Add Cylinder')
    for y,value in ((411,'4.4mm'),(430,'4.4mm'),(450,'10mm')):
        k.type_into(1075,y,value)
    do(lambda:click(313,38),.4)
    do(lambda:k.move(336,141),.4)
    k.menu_item(533,180,.6)
    for axis,value in (('X','23mm'),('Y','13mm'),('Z','16mm')):
        do(lambda:key('G',x=700,y=600),.2)
        do(lambda a=axis:key(a),.2)
        do(lambda text=value:k.type_text(text),.2)
        do(lambda:key('RET'),.4)
    k.rename_active('HoleTool')
    do(lambda:key('H',x=700,y=600),.4)
    k.click_outliner('Lid')
    do(lambda:click(1245,503),.5)
    search('Add Boolean Modifier')
    record('06-01','before','Probe: actual empty Boolean',info,park=PARK)
    do(lambda:click(1380,400),.5)
    record('06-01','object-list','Probe: click Object field to open object search list',info)
    do(lambda:k.type_text('HoleTool'),.5)
    record('06-01','object-filter','Probe: type exact HoleTool in object search',info)
    do(lambda:key('RET'),.8)
    record('06-01','assigned','Probe: Return picks actual HoleTool operand',info,park=PARK)
    do(lambda:click(1424,320),.4)
    k.menu_item(1331,343,.8)
    def dump():
        data=read_mesh_data(bpy.data.objects['Lid'])
        (Path(g['OUT'])/'lid_mesh.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        return 'Diagnostic final mesh: %d vertices / %d triangles; no qualification or print result.'%(len(data['vertices']),len(data['triangles']))
    record('06-01','actual-mesh','Probe: apply actual 32-sided 4.4 mm hole and preserve raw final mesh',dump,park=PARK)
    k.file_dialog(163,k.demo_dir,'u06_hole_diagnostic_v001.blend')
    k.confirm_dialog(1.8)
