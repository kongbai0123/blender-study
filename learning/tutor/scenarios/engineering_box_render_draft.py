"""Isolated EEVEE render draft of the existing box/lid.

Materials, lights, camera, ground and exploded lid location are PROGRAMMATIC
preparation, not GUI instruction. Rendering is requested via the Render menu.
"""
import json, math
from pathlib import Path
import bpy
from mathutils import Vector
from common import Kit, PROJECT

SOURCE=PROJECT/'learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/demo-files/u05_lid_v001.blend'
SOURCE_HASH='ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'

def build(g):
    k=Kit(g);out=Path(g['OUT']);snapshot=out/'source-snapshot';snapshot.mkdir()
    records=[]
    for rel in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py','learning/tutor/scenarios/engineering_box_render_draft.py'):
        dst=snapshot/Path(rel).name;dst.write_bytes((PROJECT/rel).read_bytes())
        records.append({'source':rel,'snapshot':dst.name,'sha256':g['sha256'](dst)})
    (snapshot/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    if g['sha256'](SOURCE)!=SOURCE_HASH:raise RuntimeError('box/lid source SHA mismatch')
    copy=Path(k.demo_dir)/SOURCE.name;copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](copy)!=SOURCE_HASH:raise RuntimeError('source copy differs')
    flags={'renders':0}
    @bpy.app.handlers.persistent
    def done(*_):flags['renders']+=1
    bpy.app.handlers.render_complete.append(done)
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.5)
    def setup():
        scene=bpy.context.scene
        # Keep the mesh coordinates; raise lid only for an exploded-view render.
        body=bpy.data.objects['Body'];lid=bpy.data.objects['Lid']
        body.hide_set(False);lid.hide_set(False);body.hide_render=False;lid.hide_render=False
        lid.location.z+=18
        for obj in scene.objects:
            if obj.type in {'CAMERA','LIGHT'}:obj.hide_render=True
        def material(name,color):
            m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
            bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1)
            bsdf.inputs['Roughness'].default_value=.43
            return m
        color=material('Render_Draft_Blue',(.10,.24,.45));ground=material('Render_Draft_Ground',(.30,.32,.36))
        body.data.materials.clear();body.data.materials.append(color)
        lid.data.materials.clear();lid.data.materials.append(color)
        mesh=bpy.data.meshes.new('RenderGroundMesh');mesh.from_pydata([(-150,-150,-15.1),(150,-150,-15.1),(150,150,-15.1),(-150,150,-15.1)],[],[(0,1,2,3)])
        floor=bpy.data.objects.new('RenderGround',mesh);scene.collection.objects.link(floor);floor.data.materials.append(ground)
        camera_data=bpy.data.cameras.new('RenderDemoCamera');camera=bpy.data.objects.new('RenderDemoCamera',camera_data);scene.collection.objects.link(camera)
        camera.location=(100,-145,115);camera.rotation_euler=(Vector((0,0,5))-camera.location).to_track_quat('-Z','Y').to_euler()
        camera_data.type='ORTHO';camera_data.ortho_scale=140;camera_data.clip_end=1000;scene.camera=camera
        for name,position,energy in [('RenderDemoSunA',(80,-60,120),2.2),('RenderDemoSunB',(-80,35,90),.8)]:
            data=bpy.data.lights.new(name,'SUN');data.energy=energy;data.angle=math.radians(12)
            light=bpy.data.objects.new(name,data);scene.collection.objects.link(light)
            light.rotation_euler=(-Vector(position)).to_track_quat('-Z','Y').to_euler()
        if scene.world is None:scene.world=bpy.data.worlds.new('RenderDemoWorld')
        scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.12,.14,.18,1);bg.inputs['Strength'].default_value=.7
        scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
        # Relative output avoids hard-coding the author’s demo evidence folder
        # into a scene copied and later used by a learner for animation output.
        scene.render.filepath='//render_output/box_lid'
        bpy.context.view_layer.update()
    def read():
        scene=bpy.context.scene;body=bpy.data.objects['Body'];lid=bpy.data.objects['Lid']
        return {'sourceHash':SOURCE_HASH,'engine':scene.render.engine,'resolution':[scene.render.resolution_x,scene.render.resolution_y],
                'camera':scene.camera.name,'bodyDimensionsMm':list(body.dimensions),'lidDimensionsMm':list(lid.dimensions),
                'lidLocationZMm':lid.location.z,'lidRaisedForDisplayMm':18,
                'setupMethod':'programmatic materials, lighting, camera, ground and display placement',
                'notPhysicalFit':True}
    k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,copy.name);k.confirm_dialog(wait=3)
    k.do(setup,1)
    send('NUMPAD_0')
    k.record('12-01','prepared','程式設定相機、光源、顏色及暫抬高上蓋；切換到相機視圖',read)
    k.file_dialog(163,k.demo_dir,'engineering_box_render_v001.blend');k.confirm_dialog(wait=2)
    k.record('12-01','saved','先另存渲染場景 v001；原盒與上蓋檔未覆寫',read)
    k.do(lambda:k.click(119,13),.6);k.menu_item(163,36,1)
    k.wait_until(lambda:flags['renders']>=1,timeout=300)
    k.do(lambda:None,1)
    k.record('12-01','render-result','Render > Render Image 實際完成；呈現 Blender Render Result',read,win='IMAGE_EDITOR')
    def save_image():
        image=bpy.data.images.get('Render Result')
        if not image:raise RuntimeError('Render Result not found')
        image.save_render(filepath=str(Path(k.demo_dir)/'box_lid_render_v001.png'),scene=bpy.context.scene)
        p=Path(k.demo_dir)/'box_lid_render_v001.png'
        if not p.is_file() or p.stat().st_size==0:raise RuntimeError('Render PNG missing')
        (out/'render-readback.json').write_text(json.dumps({**read(),'renderCompleteEvents':flags['renders'],
              'png':str(p),'pngSha256':g['sha256'](p),'pngBytes':p.stat().st_size,
              'saveMethod':'programmatic bpy.data.images[Render Result].save_render, not GUI Save As'},indent=2),encoding='utf-8')
    k.do(save_image,1)
    k.record('12-01','png-saved','程式將 Render Result 保存為PNG；不是 GUI 的 Save As 操作',read,win='IMAGE_EDITOR')
