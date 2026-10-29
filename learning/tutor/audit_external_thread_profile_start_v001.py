import bpy,hashlib,json,os
from pathlib import Path
p=Path(bpy.data.filepath); obj=bpy.data.objects['Thread_Triangle_Profile'];m=obj.data
verts=[list(v.co) for v in m.vertices];edges=[list(e.vertices) for e in m.edges]
expected=[[4.8,0,0],[6,0,.3],[4.8,0,.6]]
assert len(verts)==3 and len(edges)==3 and len(m.polygons)==0
assert all(abs(a-b)<1e-5 for row,ex in zip(verts,expected) for a,b in zip(row,ex))
assert {tuple(sorted(e)) for e in edges}=={(0,1),(1,2),(0,2)}
assert bpy.data.objects['Body_Reference'].hide_get()
assert bpy.context.view_layer.objects.active==obj and obj.select_get()
assert abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-8
report={'sourceScene':'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend','sourceSha256':'9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f','scene':'learning/evidence/08/2026-10-28-external-thread-profile-start-v001/u08_external_thread_profile_start_v001.blend','sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blenderVersion':bpy.app.version_string,'construction':'程式由來源場景建立三頂點、三邊、無面輪廓；未由使用者 GUI 手繪','object':obj.name,'verticesLocalMm':verts,'edges':edges,'polygons':len(m.polygons),'sourceBodyHidden':True,'profileSelected':True,'unitScaleLength':bpy.context.scene.unit_settings.scale_length,'limitations':['這是輪廓起始副本，不是完成的螺紋或盒體','後續 Boolean 示範仍有候選交疊及極薄面待修','列印、量測、試配與合格判定未執行']}
out=Path(os.environ['THREAD_PROFILE_AUDIT'])
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
