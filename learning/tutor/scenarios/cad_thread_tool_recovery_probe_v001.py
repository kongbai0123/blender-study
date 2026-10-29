"""Reopen-warning recovery GUI probe; no claims beyond explicitly tested operations."""
import bpy,addon_utils,importlib,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from common import Kit,PROJECT
SOURCE=PROJECT/'learning/evidence/parametric/2026-10-28-cad-thread-triangle-restore-v001/demo-files/cad_thread_triangle_060_restored_v003.blend';SHA='f45cb87cb9084bb9ca92612d6dc8726c28f7abfd099954e14ea4964975dd8508';NAME='cad_thread_triangle_recovery_v001.blend'
def build(g):
 k=Kit(g);out=Path(g['OUT']);memo={}
 if g['sha256'](SOURCE)!=SHA:raise RuntimeError('source mismatch')
 cp=Path(k.demo_dir)/SOURCE.name;cp.write_bytes(SOURCE.read_bytes())
 def setup():
  name='bl_ext.user_default.CAD_Sketcher';addon_utils.enable(name,default_set=True,persistent=True);memo['ref']=importlib.import_module(name+'.model.sketch_ref');memo['sel']=importlib.import_module(name+'.drawing.selection')
 def state():
  s=memo['ref'].get_active_sketch(bpy.context);selected=list(memo['sel'].selected);area=k.area('VIEW_3D');tool=bpy.context.workspace.tools.from_space_view3d_mode('OBJECT',create=False)
  r={'activeSketch':s.name if s else None,'dof':s.dof if s else None,'solver':s.solver_state if s else None,'tool':tool.idname if tool else None,'selectedSketchCurveIds':[str(v) for v in selected]}
  if s:
   r['constraints']=[{'type':c.type,'value':getattr(c,'value',None)} for c in s.constraints.all];r['positions']=[list(v.vector) for v in s.target_object.data.attributes['position'].data]
  return json.dumps(r)
 def check(label,target,require_selected=False):
  d=json.loads(state());vals=sorted(x['value'] for x in d.get('constraints',[]) if x['type']=='DISTANCE');assert d['activeSketch'] and d['solver']=='OKAY' and d['dof']==0 and len(vals)==2 and abs(vals[0]-target)<1e-5
  if require_selected and not d['selectedSketchCurveIds']:raise RuntimeError('select failed '+json.dumps(d))
  (out/(label+'-verification.json')).write_text(json.dumps(d,indent=2),encoding='utf8')
 def send(key,**kw):k.do(lambda:k.key(key,x=600,y=450,**kw),.6)
 def at(x,y):
  a=k.area('VIEW_3D');r=next(r for r in a.regions if r.type=='WINDOW');p=location_3d_to_region_2d(r,a.spaces.active.region_3d,Vector((x,y,0)));xx=int(r.x+p.x);yy=int(k.window().height-r.y-p.y);k.move(xx,yy);k.click(xx,yy)
 k.setup();k.do(setup,2);send('O',ctrl=True);k.fill_dialog(k.demo_dir,cp.name);k.confirm_dialog(wait=4);k.record('CADREC','reopened-warning','GUI 重開隔離副本，保留可能的工具警告畫面',state);k.do(lambda:check('reopened',.6),.3)
 k.do(lambda:k.click(1145,38),1.0);k.record('CADREC','leave','GUI 暫離草圖，檢查目前活動狀態',state)
 k.do(lambda:k.click(1149,169),1.0);k.record('CADREC','reenter','GUI 由 Sketcher 清單重新進入草圖',state);k.do(lambda:check('reentered',.6),.3)
 send('L');send('ESC');k.record('CADREC','select-tool','GUI 按 L 啟動 Line 後 Esc 回 Select',state)
 k.do(lambda:at(5.4,.15),1.0);k.record('CADREC','selected-line','GUI 點選現有斜邊並讀取選取集合',state);k.do(lambda:check('selected-line',.6,True),.3)
 k.do(lambda:k.click(1124,641,ctrl=True),.5);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text('0.8mm'),.4);k.do(lambda:k.key('RET'),1.2);k.record('CADREC','changed-080','GUI 尺寸改成 0.8 mm',state);k.do(lambda:check('changed',.8),.3)
 k.do(lambda:k.click(1124,641,ctrl=True),.5);k.do(lambda:k.key('A',ctrl=True),.2);k.do(lambda:k.type_text('0.6mm'),.4);k.do(lambda:k.key('RET'),1.2);k.record('CADREC','restored-060','GUI 還原 0.6 mm',state);k.do(lambda:check('restored',.6),.3)
 k.file_dialog(163,k.demo_dir,NAME);k.confirm_dialog(wait=3);k.record('CADREC','saved','GUI 另存恢復測試新版本',state)
 send('O',ctrl=True);k.fill_dialog(k.demo_dir,NAME);k.confirm_dialog(wait=4);k.record('CADREC','reopened-result','GUI 再重開並讀回，記錄任何警告',state);k.do(lambda:check('reopened-result',.6),.3)
