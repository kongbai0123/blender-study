"""Save render scene to isolated fake workspace and verify relative output in Blender GUI."""
from pathlib import Path
import json
import bpy
from common import Kit, PROJECT, PARK

SOURCE=PROJECT/'learning/evidence/12/2026-10-27-engineering-box-render-v004/demo-files/engineering_box_render_v001.blend'
HASH='db03247077da659ff4c4a0a5ac411e7662ab326fb6302e58496e1636f69246de'
NAME='render_safe_copy_v001.blend'
def build(g):
 k=Kit(g);out=Path(g['OUT']);demo=Path(k.demo_dir);workspace=demo/'fake-workspace';workspace.mkdir()
 if g['sha256'](SOURCE)!=HASH:raise RuntimeError('source hash mismatch')
 local=demo/SOURCE.name;local.write_bytes(SOURCE.read_bytes())
 def send(name,wait=.5,**flags):k.do(lambda:k.key(name,x=700,y=500,**flags),wait)
 def state():
  scene=bpy.context.scene;file=Path(bpy.data.filepath).resolve()
  output=Path(bpy.path.abspath(scene.render.filepath)).resolve()
  inside=output.is_relative_to(workspace.resolve())
  return {'blendInFakeWorkspace':file.is_relative_to(workspace.resolve()),'relativeOutputSetting':scene.render.filepath,
          'outputInFakeWorkspace':inside,'outputRelativeToWorkspace':output.relative_to(workspace.resolve()).as_posix() if inside else None,
          'propertiesContext':k.area('PROPERTIES').spaces.active.context,
          'interpretation':'demonstration only; no learner file or physical test'}
 def verify():
  s=state()
  if not s['blendInFakeWorkspace'] or not s['outputInFakeWorkspace'] or s['relativeOutputSetting'].replace('\\','/')!='//render_output/box_lid':raise RuntimeError('unsafe destination '+str(s))
  (out/'safe-copy-readback.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  return s
 k.setup();send('O',1.2,ctrl=True);k.fill_dialog(str(demo),local.name);k.confirm_dialog(wait=3)
 k.record('12-COPY','source','開啟隔離複本；相對輸出依場景位置解析',state,park=PARK)
 k.file_dialog(163,str(workspace),NAME);k.confirm_dialog(wait=3)
 k.record('12-COPY','saved','GUI 另存到隔離假工作區的新檔名',verify,park=PARK)
 k.do(lambda:k.click(1245,345),1)
 def check_context():
  s=verify()
  if s['propertiesContext']!='OUTPUT':raise RuntimeError('Output properties not selected: '+str(s))
  return s
 k.record('12-COPY','output','GUI 選擇 Output Properties 並核對相對目的地',check_context,park=PARK)
 send('O',1.2,ctrl=True);k.fill_dialog(str(workspace),NAME);k.confirm_dialog(wait=3)
 k.record('12-COPY','reopened','重開副本並重新解析輸出',verify,park=PARK)
