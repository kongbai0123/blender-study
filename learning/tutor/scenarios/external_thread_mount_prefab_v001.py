"""Prepare mount teaching scene by appending an existing mesh; GUI reopen and audit.

No model is generated, repositioned, rotated, or joined. Program prepares and
saves a separate file; the independent GUI then opens it with simulated events.
"""
import bpy, json, hashlib
from pathlib import Path
from common import Kit, PROJECT

BOX=PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
THREAD=PROJECT/'learning/evidence/08/2026-10-28-external-thread-gui-trial-v010/demo-files/u08_external_gui_draft_v003.blend'
BOX_SHA='ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
THREAD_SHA='5a0aea1af13f46e9bff1b14327aa199b6b34f421936fd5a516226fc13072ec04'
OLD=PROJECT/'learning/evidence/08/2026-10-28-external-thread-mount-gui-v002/run.json'
NAME='u11_mount_prefab_v001.blend'

def build(g):
    k=Kit(g); out=Path(g['OUT']); target=Path(k.demo_dir)/NAME
    if g['sha256'](BOX)!=BOX_SHA or g['sha256'](THREAD)!=THREAD_SHA:raise RuntimeError('source SHA changed')
    prior=json.loads(json.loads(OLD.read_text(encoding='utf8'))['records'][0]['observed'])
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.6)
    def signature(o):
        mesh=o.data; return {'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'matrix':[[float(x) for x in row] for row in o.matrix_world], 'worldBounds':[[min((o.matrix_world@v.co)[i] for v in mesh.vertices),max((o.matrix_world@v.co)[i] for v in mesh.vertices)] for i in range(3)],'modifierCount':len(o.modifiers)}
    def prep():
        before={n:signature(bpy.data.objects[n]) for n in ('Body','Lid')}
        with bpy.data.libraries.load(str(THREAD),link=False) as (src,dst):
            if 'Thread_Core' not in src.objects:raise RuntimeError('missing Thread_Core')
            dst.objects=['Thread_Core']
        obj=dst.objects[0];bpy.data.objects['Body'].users_collection[0].objects.link(obj)
        obj.hide_set(False); bpy.data.objects['Body'].hide_set(False);bpy.data.objects['Lid'].hide_set(False)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.context.view_layer.update()
        now={n:signature(bpy.data.objects[n]) for n in ('Body','Lid','Thread_Core')}
        if any(before[n]!=now[n] for n in before):raise RuntimeError('box or lid changed')
        if target.exists():raise RuntimeError('refuse overwriting prefab')
        bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=True)
        (out/'prepared-readback-v001.json').write_text(json.dumps(now,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    def verify():
        objs={n:signature(bpy.data.objects[n]) for n in ('Body','Lid','Thread_Core')}
        before=json.loads((out/'prepared-readback-v001.json').read_text(encoding='utf8'))
        if objs!=before:raise RuntimeError('prepared vs GUI-opened changed')
        expected={'Thread_Core':'threadBounds','Body':'bodyBounds','Lid':'lidBounds'}
        for name,key in expected.items():
            if any(abs(x-y)>0.00001 for row,want in zip(objs[name]['worldBounds'],prior[key]) for x,y in zip(row,want)):raise RuntimeError('old start mismatch '+name)
        if any(abs(a-b)>1e-6 for a,b in zip(objs['Thread_Core']['location'],prior['location'])):raise RuntimeError('old start location mismatch')
        if objs['Body']['modifierCount'] or objs['Thread_Core']['modifierCount']:raise RuntimeError('unexpected modifiers')
        result={'file':NAME,'sha256':g['sha256'](target),'objects':objs,'oldMountStep1BoundsAndLocationMatch':True,'sourceBoxSha256':BOX_SHA,'sourceThreadSha256':THREAD_SHA,'preparation':'程式 Append 與另存；未程式重建幾何、移動、旋轉或布林。','physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
        (out/'gui-reopen-readback-v001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        return json.dumps(result,ensure_ascii=False)
    k.setup();send('O',ctrl=True);k.fill_dialog(str(BOX.parent),BOX.name);k.confirm_dialog(wait=4)
    k.do(prep,1);send('O',ctrl=True);k.fill_dialog(k.demo_dir,NAME);k.confirm_dialog(wait=4)
    k.record('PREFAB','gui-open','獨立 Blender GUI 重開程式預備場景；Outliner 查看三物件，程式讀回狀態。',verify)
