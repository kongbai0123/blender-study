"""Candidate controlled update for the CAD Sketcher manual box.

This is a called helper, not a background handler: native edits bypass it.  A
caller must reject invalid sizes before changing them and validate the resulting
mesh after return.  The scene identifies the exact manual tutorial sketch.
"""
import importlib

class UpdateError(RuntimeError):
    pass


def update_cavity(context):
    if context is None or context.scene is None or context.view_layer is None:
        raise UpdateError('缺少場景或視圖層')
    prefix = 'bl_ext.user_default.CAD_Sketcher'
    try:
        refs = importlib.import_module(prefix + '.model.sketch_ref')
        solver = importlib.import_module(prefix + '.curve_solver')
        curves = importlib.import_module(prefix + '.utilities.curve_data')
        glob = importlib.import_module(prefix + '.global_data')
    except ImportError as exc:
        raise UpdateError('找不到 CAD Sketcher 0.32.1') from exc
    if glob.stateful_op_running:
        raise UpdateError('CAD Sketcher 正在執行互動工具，請先完成或取消')
    found = list(refs.get_sketches(context.scene))
    sketches = []
    for name in ('Body Sketch', 'Body.001 Sketch'):
        matches = [s for s in found if s.name == name]
        if len(matches) != 1:
            raise UpdateError('找不到唯一的手工盒草圖：' + name)
        sketch = matches[0]
        if not sketch.target_object or not sketch.target_object.data or len(sketch.target_object.data.curves) == 0:
            raise UpdateError('草圖缺少曲線資料：' + name)
        sketches.append(sketch)
    context.view_layer.update()
    for sketch in sketches:
        if not solver.solve_system(context, sketch=sketch):
            raise UpdateError('草圖求解失敗：' + sketch.name)
        curves.refresh_curve_geometry(sketch)
        context.view_layer.update()
    return {'sketches': [{'name': s.name, 'solver_state': s.solver_state, 'dof': s.dof} for s in sketches]}
