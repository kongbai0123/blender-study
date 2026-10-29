"""Native GUI Edit Mode practice. Geometry changes use simulated UI events only."""
import json
import bpy
import bmesh
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from common import Kit


def build(g):
    k = Kit(g)
    def key(name, **kw):
        k.do(lambda: k.key(name, x=700, y=500, **kw), .55)
    def search(text):
        key('F3'); k.do(lambda: k.type_text(text), .35); key('RET')
    def typed(keys, value):
        for name in keys: key(name)
        k.do(lambda: k.type_text(value), .3); key('RET')
    def stats():
        o=bpy.data.objects['Cube']; o.update_from_editmode()
        bm=bmesh.from_edit_mesh(o.data) if o.mode=='EDIT' else None
        points=[o.matrix_world@v.co for v in o.data.vertices]
        selected=[v.co for v in bm.verts if v.select] if bm else []
        return {'mode':o.mode,'dimensions':list(o.dimensions),'scale':list(o.scale),
                'vertices':len(o.data.vertices),'faces':len(o.data.polygons),
                'selectionMode':list(bpy.context.tool_settings.mesh_select_mode),
                'selectedVertices':sum(v.select for v in bm.verts) if bm else None,
                'selectedEdges':sum(e.select for e in bm.edges) if bm else None,
                'selectedFaces':sum(f.select for f in bm.faces) if bm else None,
                'selectedMedian':[sum(v[i] for v in selected)/len(selected) for i in range(3)] if selected else None,
                'worldBounds':[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)],
                'hidden':o.hide_get(),'units':bpy.context.scene.unit_settings.length_unit,
                'unitScale':float(bpy.context.scene.unit_settings.scale_length)}
    def record(slug, action, validator=None):
        def checked():
            d=stats()
            if validator and not validator(d): raise RuntimeError(action+': '+json.dumps(d))
            return json.dumps(d)
        k.record('EDIT',slug,action,checked)
    def click_world(coords):
        def click():
            a=k.area('VIEW_3D'); region=next(r for r in a.regions if r.type=='WINDOW')
            p=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(coords))
            if p is None: raise RuntimeError('target not visible')
            k.click(region.x+p.x,k.window().height-(region.y+p.y))
        k.do(click,.7)
    def select(mode, coords):
        key(mode); key('A',alt=True); click_world(coords)

    k.setup()
    record('default','觀察隔離 Blender General 預設畫面；此圖不代表學員畫面。')
    k.do(lambda:k.click(1245,374),.8); k.do(lambda:k.click(1302,433),.8)
    k.do(lambda:k.click(1418,557),.7); k.menu_item(1397,668)
    k.type_into(1417,488,'0.001'); k.open_sidebar()
    record('units','GUI 設定毫米顯示與 Unit Scale 0.001。',lambda d:d['units']=='MILLIMETERS' and abs(d['unitScale']-.001)<1e-8)
    k.file_dialog(163,k.demo_dir,'u03_edit_practice_v001.blend'); k.confirm_dialog(wait=2)
    record('saved-start','GUI 另存編輯練習副本；檔案欄位由程式填入。')
    for y in (411,430,450): k.type_into(1075,y,'20mm')
    search('Apply Scale')
    search('Frame Selected'); k.wheel_out(3)
    record('cube20','GUI 尺寸欄輸入 20 mm 並套用 Scale。',lambda d:all(abs(v-20)<1e-3 for v in d['dimensions']) and all(abs(v-1)<1e-6 for v in d['scale']))
    key('TAB'); select('ONE',(10,-10,10))
    record('vertex','GUI 進 Edit Mode、頂點模式，點一個可見頂點。',lambda d:d['selectedVertices']==1)
    select('TWO',(0,-10,10))
    record('edge','GUI 切邊模式並點上方邊線。',lambda d:d['selectedEdges']==1)
    select('THREE',(0,0,10))
    record('face','GUI 切面模式並選中頂面。',lambda d:d['selectedFaces']==1 and abs(d['selectedMedian'][2]-10)<1e-4)
    typed(['G','Z'],'5mm')
    record('move-top','GUI G Z 5mm；所選頂面的 Median Z 由10到15。',lambda d:abs(d['selectedMedian'][2]-15)<1e-4)
    key('Z',ctrl=True)
    record('undo-move','GUI Ctrl+Z 撤回頂面移動。',lambda d:abs(d['selectedMedian'][2]-10)<1e-4)
    typed(['I'],'3mm')
    record('inset','GUI I 3mm，頂面內插；選中內面 XY 跨距應各14mm。',lambda d:d['selectedFaces']==1 and d['vertices']==12)
    typed(['E'],'5mm')
    record('extrude','GUI E 5mm，內面沿法向擠出。',lambda d:abs(d['selectedMedian'][2]-15)<1e-4)
    key('Z',ctrl=True); key('Z',ctrl=True)
    record('undo-twice','GUI 兩次 Ctrl+Z，恢復原本方塊。',lambda d:d['vertices']==8 and d['faces']==6)
    key('TAB'); key('H')
    record('hidden','GUI H 隱藏物件。',lambda d:d['hidden'])
    key('H',alt=True)
    record('shown','GUI Alt+H 顯示物件。',lambda d:not d['hidden'])
    key('NUMPAD_7',ctrl=True); search('Frame Selected')
    record('bottom','GUI Ctrl+Numpad7 切底視；只改視角。')
    key('NUMPAD_2'); key('NUMPAD_2')
    record('orbit','GUI 數字鍵盤轉回傾斜視角。')
    k.file_dialog(163,k.demo_dir,'u03_edit_practice_v002.blend'); k.confirm_dialog(wait=2)
    record('saved-end','GUI 另存第二版，不覆蓋第一版。')
    key('O',ctrl=True); k.fill_dialog(k.demo_dir,'u03_edit_practice_v002.blend'); k.confirm_dialog(wait=3)
    record('reopened','GUI 重開第二版並核對尺寸、縮放與幾何。',lambda d:d['vertices']==8 and d['faces']==6 and all(abs(v-20)<1e-3 for v in d['dimensions']))
