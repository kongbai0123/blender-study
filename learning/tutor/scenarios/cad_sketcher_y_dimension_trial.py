"""Native-event Y-dimension edits of the existing program-built parametric box.

Source box meshes and drivers are NOT manually built in this run. The CAD
Sketcher constraint field is edited using simulated native Blender events.
Python bootstraps the isolated extension and only reads/evaluates geometry.
"""
import importlib
import json
import shutil
from pathlib import Path

import addon_utils
import bmesh
import bpy
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    source = PROJECT / 'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/demo-files/parametric_box_80x40_v003.blend'
    expected = 'a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2'
    if g['sha256'](source) != expected:
        raise RuntimeError('Source hash mismatch')
    copied = Path(k.demo_dir) / 'source_parametric_80x40.blend'
    shutil.copyfile(source, copied)
    if g['sha256'](copied) != expected:
        raise RuntimeError('Source copy hash mismatch')
    snapshot = out / 'source-snapshot'
    snapshot.mkdir()
    snapshots = []
    for rel in ('learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py', 'learning/tutor/scenarios/cad_sketcher_y_dimension_trial.py'):
        target = snapshot / Path(rel).name
        target.write_bytes((PROJECT / rel).read_bytes())
        snapshots.append({'source': rel, 'snapshot': target.name, 'sha256': g['sha256'](target)})
    (snapshot / 'manifest.json').write_text(json.dumps(snapshots, indent=2), encoding='utf-8')

    def enable():
        addon_utils.enable('bl_ext.user_default.CAD_Sketcher', default_set=True, persistent=True)
        if 'bl_ext.user_default.CAD_Sketcher' not in bpy.context.preferences.addons:
            raise RuntimeError('CAD Sketcher could not enable')

    def send(key, **kw):
        k.do(lambda: k.key(key, x=600, y=450, **kw), .5)

    def read(label, expected_y):
        ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
        sketch = ref.get_active_sketch(bpy.context)
        if not sketch:
            raise RuntimeError('No active sketch; do not infer constraint or solver state')
        vals = {c.constraint_uid: float(c.value) for c in sketch.constraints.all if c.type == 'DISTANCE'}
        dg = bpy.context.evaluated_depsgraph_get()
        def inspect(name):
            obj = bpy.data.objects[name].evaluated_get(dg)
            mesh = obj.to_mesh()
            points = [obj.matrix_world @ v.co for v in mesh.vertices]
            bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
            bm = bmesh.new(); bm.from_mesh(mesh)
            nonmanifold = sum(not e.is_manifold for e in bm.edges)
            volume = bm.calc_volume(signed=True)
            bm.free(); obj.to_mesh_clear()
            return {'bounds': bounds, 'points': [list(p) for p in points],
                    'nonManifoldEdges': nonmanifold, 'signedVolumeMm3': volume}
        body, lid = inspect('Parametric Box'), inspect('Parametric Lid')
        def xy(points):
            return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]
        cavity = xy(body['points'][8:12]); lip = xy(lid['points'][8:12])
        gaps = [[lip[i][0]-cavity[i][0], cavity[i][1]-lip[i][1]] for i in range(2)]
        def equal(a, b): return abs(a-b) < 1e-4
        def same_bounds(got, wanted): return all(equal(v,w) for row,ex in zip(got,wanted) for v,w in zip(row,ex))
        checks = {
            'solverOkay': sketch.solver_state == 'OKAY', 'fullyDefined': sketch.dof == 0,
            'constraints80AndY': len(vals) == 2 and any(equal(v,80) for v in vals.values()) and any(equal(v,expected_y) for v in vals.values()),
            'bodyBounds': same_bounds(body['bounds'], [[0,80],[0,expected_y],[0,30]]),
            'lidBounds': same_bounds(lid['bounds'], [[0,80],[0,expected_y],[26,32]]),
            'cavityXY': same_bounds(cavity, [[2,78],[2,expected_y-2]]),
            'lipOuterXY': same_bounds(lip, [[2.2,77.8],[2.2,expected_y-2.2]]),
            'fourNominalGaps': all(equal(v,.2) for row in gaps for v in row),
            'bodyManifold': body['nonManifoldEdges'] == 0, 'lidManifold': lid['nonManifoldEdges'] == 0,
            'bodyPositiveVolume': body['signedVolumeMm3'] > 0, 'lidPositiveVolume': lid['signedVolumeMm3'] > 0,
        }
        data = {'label':label,'mode':bpy.context.mode,'sketch':{'name':sketch.name,'solver':sketch.solver_state,
                  'dof':sketch.dof,'constraints':vals},'box':body,'lid':lid,'cavityBoundsXY':cavity,
                'lipOuterBoundsXY':lip,'sideGapsXY':gaps,'checks':checks,'allPassed':all(checks.values()),
                'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None,
                'geometryConstruction':'source meshes and drivers were programmatically created in prior v004; not GUI construction',
                'dimensionOperation':'native Blender GUI event', 'comparisonMm':1e-4}
        (out / (label+'-verification.json')).write_text(json.dumps(data, indent=2), encoding='utf-8')
        if not data['allPassed']:
            raise RuntimeError('Y trial verification failed: '+json.dumps(checks))
        return data

    def set_y(value):
        k.do(lambda:k.click(1124,657,ctrl=True),.5)
        k.do(lambda:k.key('A',ctrl=True),.2)
        k.do(lambda:k.type_text(str(value)+'mm'),.3)
        k.do(lambda:k.key('RET'),1.5)

    k.setup()
    k.do(enable,2)
    send('O',ctrl=True)
    k.fill_dialog(k.demo_dir, copied.name)
    k.confirm_dialog(wait=4)
    k.record('CAD-Y','opened-80x40','開啟先前程式建置的 80×40 參數盒副本，核對草圖與兩件原始讀值',lambda:read('opened-80x40',40))
    set_y(50)
    k.record('CAD-Y','changed-80x50','在 Sketcher 側欄以原生事件將第二個尺寸由 40 改成 50 mm',lambda:read('changed-80x50',50))
    k.file_dialog(163,k.demo_dir,'parametric_box_80x50_y_v001.blend')
    k.confirm_dialog(wait=2)
    k.record('CAD-Y','saved-80x50','另存新的 80×50 mm 示範場景 v001',lambda:read('saved-80x50',50))
    send('O',ctrl=True)
    k.fill_dialog(k.demo_dir,'parametric_box_80x50_y_v001.blend')
    k.confirm_dialog(wait=4)
    k.record('CAD-Y','reopened-80x50','重開 80×50 場景並核對尺寸、兩件與自由度',lambda:read('reopened-80x50',50))
    set_y(45)
    k.record('CAD-Y','reopened-changed-80x45','重開後改第二個尺寸至 45 mm，核對兩件與四側數位間隙',lambda:read('reopened-changed-80x45',45))
    k.file_dialog(163,k.demo_dir,'parametric_box_80x45_y_v002.blend')
    k.confirm_dialog(wait=2)
    k.record('CAD-Y','saved-80x45','另存 80×45 mm 示範場景 v002',lambda:read('saved-80x45',45))
