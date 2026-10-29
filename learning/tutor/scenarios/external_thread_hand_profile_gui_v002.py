"""Construct the three-edge screw profile using GUI events only.

Python only hides the box reference, reads checks, and fills file dialogs. All
profile geometry is created/edited by Blender GUI events.
"""
import json
from pathlib import Path
import bpy,bmesh
from common import Kit,PROJECT

SOURCE=PROJECT/'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_HASH='9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'

def build(g):
    k=Kit(g);out=Path(g['OUT'])
    if g['sha256'](SOURCE)!=SOURCE_HASH:raise RuntimeError('source differs')
    source_copy=Path(k.demo_dir)/SOURCE.name;source_copy.write_bytes(SOURCE.read_bytes())
    def send(key,**kw): k.do(lambda:k.key(key,x=700,y=500,**kw),.55)
    def typed(keys,value):
        for key in keys:send(key)
        k.do(lambda:k.type_text(value),.35);send('RET')
    def search(value):send('F3');k.do(lambda:k.type_text(value),.5);send('RET')
    def prepare():
        bpy.data.objects['Body_Reference'].hide_set(True)
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
    def stats(stage,expected_points,edges,faces):
        obj=bpy.data.objects['Thread_Hand_Profile']
        if obj.mode=='EDIT':
            bm=bmesh.from_edit_mesh(obj.data); verts=list(bm.verts); nedge=len(bm.edges); nface=len(bm.faces); selected=[list(v.co) for v in verts if v.select]
        else:
            verts=list(obj.data.vertices); nedge=len(obj.data.edges); nface=len(obj.data.polygons);selected=[]
        points=sorted([list(map(float,v.co)) for v in verts])
        result={'stage':stage,'mode':obj.mode,'vertices':points,'selected':selected,'edges':nedge,'faces':nface,'sourceSha256':SOURCE_HASH,'physicalPrint':None,'physicalFit':None}
        (out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
        want=sorted(expected_points)
        if len(points)!=len(want) or nedge!=edges or nface!=faces or any(abs(a-b)>0.0001 for p,q in zip(points,want) for a,b in zip(p,q)):
            raise RuntimeError('wrong '+json.dumps(result))
        return json.dumps(result)
    p1=[4.8,0,0];p2=[6,0,.3];p3=[4.8,0,.6]
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,source_copy.name);k.confirm_dialog(wait=3);k.do(prepare,.6)
    search('Add Plane');send('F2');k.do(lambda:k.type_text('Thread_Hand_Profile'),.5);send('RET');send('TAB');send('ONE');send('A')
    search('Merge at Center');send('A');send('NUMPAD_1')
    k.record('HP','merged','GUI 新增平面並在編輯模式合併到中心，成為單點。',lambda:stats('merged',[[0,0,0]],0,0))
    typed(['G','X'],'4.8mm');search('Frame Selected');k.wheel_out(7)
    k.record('HP','point-1','GUI 移動第一點到 X=4.8 mm，Y=0、Z=0。',lambda:stats('point-1',[p1],0,0))
    typed(['E','X'],'1.2mm');typed(['G','Z'],'0.3mm')
    k.record('HP','point-2','GUI 從第一點擠出第二點，X 增加 1.2 mm、Z 增加 0.3 mm。',lambda:stats('point-2',[p1,p2],1,0))
    typed(['E','X'],'-1.2mm');typed(['G','Z'],'0.3mm');send('A');search('Frame Selected');k.wheel_out(2)
    k.record('HP','point-3','GUI 從第二點擠出第三點，X 減少 1.2 mm、Z 增加 0.3 mm，選取三點。',lambda:stats('point-3',[p1,p2,p3],2,0))
    send('F');k.record('HP','filled','GUI 對三點按 F 臨時建立三角面和閉合邊。',lambda:stats('filled',[p1,p2,p3],3,1))
    search('Only Faces');k.record('HP','closed-profile','GUI 僅刪除面，保留三條閉合邊；此輪廓不由 Python 建立。',lambda:stats('closed-profile',[p1,p2,p3],3,0))
    send('TAB');k.file_dialog(163,k.demo_dir,'u11_hand_profile_v001.blend');k.confirm_dialog(wait=3)
    k.record('HP','saved','GUI 另存手工輪廓版本；檔案視窗路徑及名稱由程式填寫。',lambda:stats('saved',[p1,p2,p3],3,0))
    send('O',ctrl=True);k.fill_dialog(k.demo_dir,'u11_hand_profile_v001.blend');k.confirm_dialog(wait=4)
    k.record('HP','reopened','GUI 重開並核對三頂點與三條邊。',lambda:stats('reopened',[p1,p2,p3],3,0))
