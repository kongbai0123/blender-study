"""GUI triangulate a copy, save separately, and report changed tessellation."""
import json
from pathlib import Path
import bpy,bmesh
from common import Kit,PROJECT
def build(g,cfg):
 k=Kit(g);out=Path(g['OUT']);source=PROJECT/cfg['source'];h=cfg['sha256']
 if g['sha256'](source)!=h:raise RuntimeError('source mismatch')
 cp=Path(k.demo_dir)/source.name;cp.write_bytes(source.read_bytes())
 def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.5)
 def stats(stage):
  o=bpy.data.objects[cfg['object']]
  if o.mode=='EDIT':bm=bmesh.from_edit_mesh(o.data);owned=False
  else:bm=bmesh.new();bm.from_mesh(o.data);owned=True
  bm.verts.index_update();points=[o.matrix_world@v.co for v in bm.verts];tris=[tuple(l.vert.index for l in tri) for tri in bm.calc_loop_triangles()]
  seen=set();duplicates=0
  for tri in tris:
   key=tuple(sorted(tri));duplicates+=int(key in seen);seen.add(key)
  remain=set(bm.verts);components=0
  while remain:
   components+=1;stack=[remain.pop()]
   while stack:
    for edge in stack.pop().link_edges:
     for v in edge.verts:
      if v in remain:remain.remove(v);stack.append(v)
  result={'stage':stage,'object':o.name,'mode':o.mode,'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(tris),
          'exactDuplicateIndexTriangles':duplicates,'boundaryEdges':sum(e.is_boundary for e in bm.edges),
          'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,
          'signedVolumeMm3':bm.calc_volume(signed=True),
          'boundsMm':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
          'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None,'qualifiedStrength':None}
  if owned:bm.free()
  (out/(stage+'-verification.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
  if stage!='source' and (duplicates or result['boundaryEdges'] or result['nonManifoldEdges'] or components!=1):raise RuntimeError('triangulation did not remove issue '+json.dumps(result))
  return json.dumps(result)
 def ensure_outliner():
  area=k.area('OUTLINER')
  if area.height<270:
   divider=k.window().height-area.y;k.drag_slow([(1305,divider),(1305,divider+120)],button='LEFTMOUSE')
 k.setup();send('O',ctrl=True);k.fill_dialog(k.demo_dir,cp.name);k.confirm_dialog(wait=3);k.do(ensure_outliner,.3)
 k.click_outliner(cfg['object']);send('F3');k.do(lambda:k.type_text('Frame Selected'),.35);send('RET')
 k.record('FIX','source','GUI 選擇來源副本目標，讀出來源三角化重複數；原模型不覆寫。',lambda:stats('source'))
 send('TAB');send('A');send('T',ctrl=True)
 k.record('FIX','triangulated','GUI Edit Mode 全選 Ctrl+T，明確將面重新三角化；可能改變非平面 n-gon 的表面。',lambda:stats('triangulated'))
 send('TAB');k.file_dialog(163,k.demo_dir,cfg['filename']);k.confirm_dialog(wait=3)
 k.record('FIX','saved','GUI 另存修訂副本；路徑和檔名由程式填入。',lambda:stats('saved'))
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,cfg['filename']);k.confirm_dialog(wait=4)
 k.record('FIX','reopened','GUI 重開修訂副本，重新核對網格；未做實體驗證。',lambda:stats('reopened'))
