"""Independent parametric box proof from the verified CAD Sketcher rectangle.

The constrained sketch was created by native events in a preceding recorded run.
This experiment PROGRAMMATICALLY builds meshes and vertex drivers; it does not
present that part as GUI instruction. The recorded change is a native UI event.
"""
import importlib
import json
import shutil
from pathlib import Path

import addon_utils
import bpy
import bmesh
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    source = PROJECT / 'learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/demo-files/cad_rectangle_60x40_v001.blend'
    copied = Path(k.demo_dir) / 'source_rectangle_60x40.blend'
    shutil.copyfile(source, copied)
    if g['sha256'](source) != g['sha256'](copied):
        raise RuntimeError('Source copy differs')
    snapshot = out / 'source-snapshot'
    snapshot.mkdir()
    source_files = ['learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                    'learning/tutor/scenarios/common.py',
                    'learning/tutor/scenarios/cad_sketcher_parametric_box_trial.py']
    manifest = []
    for rel in source_files:
        target = snapshot / Path(rel).name
        target.write_bytes((PROJECT / rel).read_bytes())
        manifest.append({'source': rel, 'snapshot': target.name, 'sha256': g['sha256'](target)})
    (snapshot / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    def send(key, **kw):
        k.do(lambda: k.key(key, x=600, y=450, **kw), .5)

    def bootstrap():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher', default_set=True, persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons:
            raise RuntimeError('CAD Sketcher could not enable')

    k.setup()
    k.do(bootstrap, 2)
    send('O', ctrl=True)
    k.fill_dialog(k.demo_dir, copied.name)
    k.confirm_dialog(wait=4)

    def sketch_state():
        ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sketch = ref.get_active_sketch(bpy.context)
        if not sketch:
            raise RuntimeError('No active CAD Sketcher sketch')
        vals = {c.constraint_uid: c.value for c in sketch.constraints.all if c.type == 'DISTANCE'}
        return sketch, vals

    def read_sketch():
        sketch, vals = sketch_state()
        return {'solver': sketch.solver_state, 'dof': sketch.dof,
                'constraints': vals, 'generatedMesh': sketch.target_object.name}

    k.record('CAD-BOX', 'sketch-source', '開啟先前實際建立的受約束草圖副本，讀回尺寸與自由度', read_sketch)

    def construct():
        sketch, vals = sketch_state()
        if sketch.solver_state != 'OKAY' or sketch.dof != 0:
            raise RuntimeError('Input sketch is not fully defined')
        width_uid = next(uid for uid, v in vals.items() if abs(v-60) < .00001)
        depth_uid = next(uid for uid, v in vals.items() if abs(v-40) < .00001)
        scene = bpy.context.scene
        sources = {'L':'slvs:c:'+width_uid, 'W':'slvs:c:'+depth_uid,
                   'H':'box_height_mm', 'T':'box_wall_mm', 'B':'box_bottom_mm',
                   'P':'lid_plate_mm', 'D':'lid_depth_mm', 'C':'gap_total_mm',
                   'S':'lid_lip_wall_mm'}
        for key, value in {'box_height_mm':30., 'box_wall_mm':2., 'box_bottom_mm':2.,
                           'lid_plate_mm':2., 'lid_depth_mm':4., 'gap_total_mm':.4,
                           'lid_lip_wall_mm':2.}.items(): scene[key] = value
        def ring(x0,x1,y0,y1,z):
            return [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]
        def sides(a,b,flip=False):
            return [tuple(reversed(f)) if flip else f for f in
                    [(a+i, a+(i+1)%4, b+(i+1)%4, b+i) for i in range(4)]]
        def rings(a,b,flip=False):
            return [tuple(reversed(f)) if flip else f for f in
                    [(a+i, a+(i+1)%4, b+(i+1)%4, b+i) for i in range(4)]]
        body_verts = (ring('0','L','0','W','0') + ring('0','L','0','W','H') +
                      ring('T','L-T','T','W-T','H') + ring('T','L-T','T','W-T','B'))
        body_faces = [tuple(reversed((0,1,2,3)))] + sides(0,4) + rings(4,8) + sides(8,12) + [(12,13,14,15)]
        x0,x1,y0,y1='T+C/2','L-T-C/2','T+C/2','W-T-C/2'
        xi0,xi1,yi0,yi1='T+C/2+S','L-T-C/2-S','T+C/2+S','W-T-C/2-S'
        lid_verts = (ring('0','L','0','W','H+P') + ring('0','L','0','W','H') +
                     ring(x0,x1,y0,y1,'H') + ring(x0,x1,y0,y1,'H-D') +
                     ring(xi0,xi1,yi0,yi1,'H-D') + ring(xi0,xi1,yi0,yi1,'H'))
        lid_faces = [(0,1,2,3)] + sides(4,0) + rings(4,8,True) + sides(12,8) + rings(12,16,True) + sides(20,16) + [tuple(reversed((20,21,22,23)))]
        def make(name, vertices, faces):
            mesh = bpy.data.meshes.new(name+' Mesh')
            mesh.from_pydata([(0,0,0)]*len(vertices), [], faces)
            obj = bpy.data.objects.new(name, mesh)
            scene.collection.objects.link(obj)
            for index, coords in enumerate(vertices):
                for axis, expression in enumerate(coords):
                    if expression == '0':
                        continue
                    drv = mesh.driver_add('vertices[%d].co' % index, axis).driver
                    drv.expression = expression
                    for symbol,key in sources.items():
                        if symbol not in expression: continue
                        var = drv.variables.new(); var.name=symbol; var.type='SINGLE_PROP'
                        var.targets[0].id_type='SCENE'; var.targets[0].id=scene
                        var.targets[0].data_path='["'+key+'"]'
            return obj
        body = make('Parametric Box', body_verts, body_faces)
        lid = make('Parametric Lid', lid_verts, lid_faces)
        body.hide_set(True); lid.hide_set(True)
        bpy.context.view_layer.update()
        info = {'method':'programmatic mesh and vertex driver setup, not GUI teaching',
                'widthConstraintUid':width_uid, 'depthConstraintUid':depth_uid,
                'sources':sources, 'sourceSha256':g['sha256'](source),
                'designLimits':'valid only where L,W > 2*(T+C/2+S), H>B>=0, H>=D>0; no automatic guards',
                'physicalFitTested':False, 'qualifiedClearanceMm':None}
        (out/'driver-setup.json').write_text(json.dumps(info,indent=2),encoding='utf-8')

    k.do(construct, 2)

    def verify(label, length):
        sketch, vals = sketch_state()
        scene=bpy.context.scene
        dg=bpy.context.evaluated_depsgraph_get()
        def inspect(name):
            o=bpy.data.objects[name].evaluated_get(dg)
            mesh=o.to_mesh(); points=[o.matrix_world@v.co for v in mesh.vertices]
            bounds=[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)]
            bm=bmesh.new(); bm.from_mesh(mesh)
            nonmanifold=sum(not e.is_manifold for e in bm.edges)
            volume=bm.calc_volume(signed=True)
            bm.free(); o.to_mesh_clear()
            return {'bounds':bounds,'vertices':len(points),'nonManifoldEdges':nonmanifold,'signedVolume':volume,
                    'points':[list(p) for p in points]}
        box=inspect('Parametric Box'); lid=inspect('Parametric Lid')
        def approx(a,b): return abs(a-b)<1e-4
        # Volumes accumulate float32 vertex roundoff; same relative 1e-5
        # comparison used by the baseline 05-05 audit, not a fit tolerance.
        def volume_approx(a,b): return abs(a-b) <= abs(b)*1e-5
        def xy_extents(pts):
            return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
        cavity=xy_extents(box['points'][8:12]); lip=xy_extents(lid['points'][8:12])
        gaps=[[lip[i][0]-cavity[i][0],cavity[i][1]-lip[i][1]] for i in range(2)]
        checks={'solverOkay':sketch.solver_state=='OKAY','dofZero':sketch.dof==0,
                'sketchLength':any(approx(x,length) for x in vals.values()),
                'boxBounds':all(approx(v,w) for row,expected in zip(box['bounds'],[[0,length],[0,40],[0,30]]) for v,w in zip(row,expected)),
                'lidBounds':all(approx(v,w) for row,expected in zip(lid['bounds'],[[0,length],[0,40],[26,32]]) for v,w in zip(row,expected)),
                'boxManifold':box['nonManifoldEdges']==0,'lidManifold':lid['nonManifoldEdges']==0,
                'boxPositiveVolume':box['signedVolume']>0,'lidPositiveVolume':lid['signedVolume']>0,
                'cavityXY':all(approx(v,w) for row,expected in zip(cavity,[[2,length-2],[2,38]]) for v,w in zip(row,expected)),
                'lipOuterXY':all(approx(v,w) for row,expected in zip(lip,[[2.2,length-2.2],[2.2,37.8]]) for v,w in zip(row,expected)),
                'fourNominalGaps':all(approx(v,.2) for row in gaps for v in row),
                'boxVolume':volume_approx(box['signedVolume'],length*40*30-(length-4)*36*28),
                'lidVolume':volume_approx(lid['signedVolume'],length*40*2+((length-4.4)*35.6-(length-8.4)*31.6)*4)}
        record={'label':label,'checks':checks,'sketch':read_sketch(),'box':box,'lid':lid,
                'cavityBoundsXY':cavity,'lipOuterBoundsXY':lip,'sideGapsXY':gaps,
                'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
        (out/(label+'-verification.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
        if not all(checks.values()): raise RuntimeError('Verification failed: '+json.dumps(checks))
        return record

    k.do(lambda:verify('parametric-60',60),1)
    k.record('CAD-BOX','drivers-created','程式建立參數盒與上蓋網格及驅動器；尺寸主控為受約束草圖（非GUI建模）',read_sketch)
    k.do(lambda:[bpy.data.objects[name].hide_set(False) for name in ('Parametric Box','Parametric Lid')],1)
    k.file_dialog(163,k.demo_dir,'parametric_box_60x40_v001.blend')
    k.confirm_dialog(wait=2)
    k.record('CAD-BOX','saved-60','Save As 保存 60×40 參數盒基線 v001',read_sketch)
    k.do(lambda:k.click(1124,641,ctrl=True),.5)
    k.do(lambda:k.key('A',ctrl=True),.2)
    k.do(lambda:k.type_text('80mm'),.3)
    k.do(lambda:k.key('RET'),1)
    k.record('CAD-BOX','changed-80','在 Sketcher 側欄把草圖第一個尺寸由 60 改為 80 mm',read_sketch)
    k.do(lambda:verify('parametric-80',80),1)
    k.file_dialog(163,k.demo_dir,'parametric_box_80x40_v002.blend')
    k.confirm_dialog(wait=2)
    k.record('CAD-BOX','saved-80','另存 80×40 參數盒 v002',read_sketch)
    send('O',ctrl=True)
    k.fill_dialog(k.demo_dir,'parametric_box_80x40_v002.blend')
    k.confirm_dialog(wait=4)
    k.record('CAD-BOX','reopened-80','重開 v002，確認尺寸及約束仍保留',read_sketch)
    k.do(lambda:verify('reopened-80',80),1)
    k.do(lambda:k.click(1124,641,ctrl=True),.5)
    k.do(lambda:k.key('A',ctrl=True),.2)
    k.do(lambda:k.type_text('70mm'),.3)
    k.do(lambda:k.key('RET'),1)
    k.record('CAD-BOX','reopened-edit-70','重開後再次在側欄修改草圖尺寸為 70 mm，驗證依賴關係可持續編輯',read_sketch)
    k.do(lambda:verify('reopened-edit-70',70),1)
    k.do(lambda:k.click(1124,641,ctrl=True),.5)
    k.do(lambda:k.key('A',ctrl=True),.2)
    k.do(lambda:k.type_text('80mm'),.3)
    k.do(lambda:k.key('RET'),1)
    k.do(lambda:verify('reopened-restored-80',80),1)
    k.file_dialog(163,k.demo_dir,'parametric_box_80x40_v003.blend')
    k.confirm_dialog(wait=2)
    k.record('CAD-BOX','saved-80-after-reopen','重開後實際修改再恢復 80 mm，另存 v003',read_sketch)
    def show_model():
        for name in ('Parametric Box','Parametric Lid'): bpy.data.objects[name].hide_set(False)
        bpy.data.objects['Body'].hide_set(True)
        ref=importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        # Active-sketch overlay is left in place; viewport orientation is native user action below.
    k.do(show_model,1)
    k.do(lambda:k.click(1076,130),2)
    send('HOME')
    send('NUMPAD_3',ctrl=True)
    send('NUMPAD_6')
    send('NUMPAD_8')
    k.record('CAD-BOX','model-80','離開草圖後顯示程式建置的參數盒與上蓋（實際 Blender 畫面）',
             lambda: {'visibleObjects':[o.name for o in bpy.context.visible_objects],
                      'activeSketch':False,'note':'此前已在草圖內完成幾何與尺寸驗證'})
