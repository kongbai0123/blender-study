"""數位尺寸預檢與可選的 Blender 受控輸入面板（v004 試作專用）。

在 Blender 的 Scripting 工作區以 Text Editor 開啟本檔並 Run Script，然後
3D Viewport 側欄的「盒尺寸預檢」面板可一次修改一個參數。
此工具不會攔截 CAD Sketcher 或 Scene 原生欄位的直接修改，也不會存檔。
檢查為數位模型的必要條件，不是完整干涉、切片、強度或實體配合驗證。
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / 'learning' / 'workspaces' / 'engineering-parametric'
PROGRESS = ROOT / 'learning' / 'progress.json'

# 唯一適用對象是 2026-10-27 parametric-box-v004 所衍生且保留這兩個約束 ID 的個人副本。
FIELDS = {
    'L': ('長度 L', 'slvs:c:b596b36138076155'),
    'W': ('寬度 W', 'slvs:c:854e8777cfe2608d'),
    'H': ('盒高 H', 'box_height_mm'),
    'T': ('側壁 T', 'box_wall_mm'),
    'B': ('底厚 B', 'box_bottom_mm'),
    'P': ('蓋板厚 P', 'lid_plate_mm'),
    'D': ('唇深 D', 'lid_depth_mm'),
    'C': ('水平總間隙 C', 'gap_total_mm'),
    'S': ('唇壁厚 S', 'lid_lip_wall_mm'),
}


def validate(values):
    """Return (errors, observations). Units are mm; no manufacturing criteria.

    All checks are necessary for this specific rectangular model's nominal
    algebra. They are not sufficient to prove a correct model or printable fit.
    """
    errors, warnings = [], []
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        return ['必須提供 L、W、H、T、B、P、D、C、S 九個數值。'], warnings
    for key, (label, _) in FIELDS.items():
        value = values[key]
        try:
            finite = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            errors.append(f'{label} 必須為有限數值（mm）。')
        elif key == 'C' and value < 0:
            errors.append('水平總間隙 C 不能為負數。')
        elif key != 'C' and value <= 0:
            errors.append(f'{label} 必須大於 0 mm。')
    if errors:
        return errors, warnings
    L, W, H, T, B, P, D, C, S = (values[k] for k in FIELDS)
    # Rectangle inner opening and lip's inner opening both need positive size.
    if L <= 2 * T or W <= 2 * T:
        errors.append('盒口內長及內寬必須大於 0：L、W 均須大於 2×T。')
    if L <= 2 * T + C + 2 * S or W <= 2 * T + C + 2 * S:
        errors.append('唇邊內長及內寬必須大於 0：L、W 均須大於 2×T+C+2×S。')
    if H <= B:
        errors.append('盒高 H 必須大於底厚 B，才有正的內腔高度。')
    if H - D < B:
        errors.append('唇邊底面低於盒內底：須 H−D ≥ B，避免 Z 方向重疊。')
    if not errors:
        if H - D == B:
            warnings.append('H−D=B：唇邊與盒內底在名義位置接觸；未留軸向間隙。')
        if C == 0:
            warnings.append('C=0：名義水平間隙為零；尚無實體配合結論。')
        warnings.append('僅通過必要的數位尺寸條件；未驗證完整碰撞、切片、列印或配合。')
    return errors, warnings


def workspace_error(filepath, root=ROOT, workspace=WORKSPACE, progress=PROGRESS):
    """Fail closed outside workspace or if path is a registered checkpoint."""
    if not filepath:
        return '請先將個人副本另存至 engineering-parametric 工作區。'
    path = Path(filepath).resolve()
    try:
        # Resolve links/junctions first; neither the workspaces root nor its
        # engineering subfolder may resolve outside the actual project.
        project_root = Path(root).resolve()
        workspaces_root = (project_root / 'learning' / 'workspaces').resolve()
        workspaces_root.relative_to(project_root)
        Path(workspace).resolve().relative_to(workspaces_root)
    except (OSError, ValueError):
        return '工作區連結超出專案；拒絕修改。'
    if path.suffix.lower() != '.blend' or not path.is_file():
        return '請先另存為工作區中已存在的 .blend 個人副本。'
    try:
        path.relative_to(Path(workspace).resolve())
    except ValueError:
        return '只允許 engineering-parametric 工作區中的個人副本。'
    try:
        data = json.loads(Path(progress).read_text(encoding='utf-8-sig'))
        registered = data['fileVersions']
        if not isinstance(registered, list):
            raise ValueError('fileVersions')
        for entry in registered:
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
                raise ValueError('invalid fileVersions record')
            if (Path(root) / entry['path']).resolve() == path:
                return '此檔案已登記為版本；請先以新檔名另存。'
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return '無法核對共用版本清單，拒絕修改；請先修復進度檔。'
    return None


class GuardError(ValueError):
    pass


def guarded_change(current, field, value, write, read, postcheck):
    """Validate a one-field proposal before invoking writer; roll back on failure.

    Callbacks permit independent tests without importing Blender. `postcheck`
    must check the solver after a constraint change. No file is written here.
    """
    if field not in FIELDS:
        raise GuardError('未知參數。')
    old = dict(current)
    before_errors, _ = validate(old)
    if before_errors:
        raise GuardError('目前尺寸已不符合預檢條件；先回復有效版本。')
    candidate = dict(old)
    candidate[field] = value
    errors, warnings = validate(candidate)
    if errors:
        raise GuardError('；'.join(errors))
    try:
        write(field, value)
        actual = read(field)
        if not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isclose(actual, value, rel_tol=1e-8, abs_tol=1e-6):
            raise RuntimeError('修改後讀回值不一致。')
        if not postcheck():
            raise RuntimeError('草圖求解失敗或非完全約束。')
    except Exception as exc:
        try:
            write(field, old[field])
            restored = read(field)
            if not math.isclose(restored, old[field], rel_tol=1e-8, abs_tol=1e-6) or not postcheck():
                raise RuntimeError('回復後核對失敗')
        except Exception as rollback_exc:
            raise GuardError(f'修改失敗（{exc}）；自動回復未確認（{rollback_exc}）。請勿存檔，重新開啟原副本。') from exc
        raise GuardError(f'修改失敗（{exc}）；已回復原數值。') from exc
    return candidate, warnings


def _blender_state(context):
    """Get the active v004-compatible sketch and parameters without writes."""
    import importlib
    import bpy

    problem = workspace_error(bpy.data.filepath)
    if problem:
        raise GuardError(problem)
    if 'bl_ext.user_default.CAD_Sketcher' not in context.preferences.addons:
        raise GuardError('CAD Sketcher 未啟用；請勿修改。')
    globals_module = importlib.import_module('bl_ext.user_default.CAD_Sketcher.global_data')
    if globals_module.needs_solve:
        raise GuardError('草圖求解尚待執行；請等待畫面更新後再操作。')
    for name in ('Parametric Box', 'Parametric Lid'):
        if name not in bpy.data.objects or bpy.data.objects[name].type != 'MESH':
            raise GuardError('找不到 v004 的盒體或上蓋；此工具不適用目前場景。')
        obj = bpy.data.objects[name]
        if obj.library or obj.override_library or obj.data.library or obj.data.override_library:
            raise GuardError('物件或網格是外部連結／覆寫；請先建立本地個人副本。')
    sketch_ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
    sketch = sketch_ref.get_active_sketch(context)
    if not sketch or sketch.solver_state != 'OKAY' or sketch.dof != 0:
        raise GuardError('請進入 v004 的 Body Sketch，確認求解正常且 Fully defined。')
    constraints = {}
    for field in ('L', 'W'):
        uid = FIELDS[field][1].removeprefix('slvs:c:')
        found = [c for c in sketch.constraints.all if c.type == 'DISTANCE' and c.constraint_uid == uid and not c.is_reference]
        if len(found) != 1:
            raise GuardError('找不到原始長寬驅動約束；請勿使用此工具。')
        constraints[field] = found[0]
    scene = context.scene
    if scene.library or scene.override_library:
        raise GuardError('場景是外部連結／覆寫；請先建立本地個人副本。')
    target = getattr(sketch, 'target_object', None)
    if target and (target.library or target.override_library or target.data.library or target.data.override_library):
        raise GuardError('草圖目標是外部連結／覆寫；拒絕修改。')
    for _, key in FIELDS.values():
        if key not in scene:
            raise GuardError('缺少 v004 尺寸主控；請勿使用此工具。')
    values = {name: (float(constraints[name].value) if name in constraints else float(scene[key]))
              for name, (_, key) in FIELDS.items()}
    # A direct Scene-ID-property change can desynchronise displayed constraints.
    for name in ('L', 'W'):
        if not math.isclose(values[name], float(scene[FIELDS[name][1]]), rel_tol=1e-8, abs_tol=1e-6):
            raise GuardError('約束與尺寸主控不一致；請重新開啟已核對的副本。')
    return sketch, constraints, scene, values


try:
    import bpy
    from bpy.props import BoolProperty, EnumProperty, FloatProperty
    from bpy.types import Operator, Panel
except ModuleNotFoundError:
    bpy = None

if bpy is not None:
    class BOX_OT_guarded_change(Operator):
        bl_idname = 'learning_box.guarded_change'
        bl_label = '預檢後修改一項尺寸'
        bl_description = '先檢查所有數位尺寸，再修改一項；不保證實體配合'
        bl_options = {'REGISTER', 'UNDO'}
        field: EnumProperty(name='參數', items=[(k, v[0], '') for k, v in FIELDS.items()])
        value: FloatProperty(name='新數值 (mm)', default=0, precision=4)
        acknowledged: BoolProperty(name='我已核對參數與新數值', default=False)

        def invoke(self, context, event):
            try:
                _, _, _, values = _blender_state(context)
                self.value = values.get(self.field, values['L'])
                self.acknowledged = False
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            return context.window_manager.invoke_props_dialog(self, width=420)

        def draw(self, context):
            self.layout.prop(self, 'field')
            self.layout.prop(self, 'value')
            try:
                _, _, _, values = _blender_state(context)
                self.layout.label(text=f'目前 {FIELDS[self.field][0]}：{values[self.field]:g} mm')
            except Exception:
                self.layout.label(text='目前值無法讀取；操作將被拒絕。', icon='ERROR')
            self.layout.prop(self, 'acknowledged')
            self.layout.label(text='一次一項；不攔截原生欄位直接輸入。', icon='INFO')
            self.layout.label(text='預檢非完整干涉或實體配合判定。', icon='ERROR')

        def execute(self, context):
            try:
                if not self.acknowledged:
                    raise GuardError('請先核對參數與新數值並勾選確認。')
                sketch, constraints, scene, current = _blender_state(context)

                def write(field, value):
                    if field in constraints:
                        constraints[field].value = value
                    else:
                        scene[FIELDS[field][1]] = value
                    scene.update_tag()
                    context.view_layer.update()

                def read(field):
                    return float(constraints[field].value) if field in constraints else float(scene[FIELDS[field][1]])

                def postcheck():
                    # The add-on defers solving through depsgraph callbacks;
                    # do not report success while a solve is still pending.
                    import importlib
                    state = importlib.import_module('bl_ext.user_default.CAD_Sketcher.global_data')
                    return not state.needs_solve and sketch.solver_state == 'OKAY' and sketch.dof == 0

                _, warnings = guarded_change(current, self.field, self.value, write, read, postcheck)
                self.report({'INFO'}, '已修改；' + ' '.join(warnings))
                return {'FINISHED'}
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}

    class BOX_PT_guarded_parameters(Panel):
        bl_label = '盒尺寸預檢 v001'
        bl_idname = 'BOX_PT_guarded_parameters'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = '盒尺寸預檢'

        def draw(self, context):
            self.layout.label(text='v004 盒蓋個人副本專用', icon='INFO')
            self.layout.label(text='先進入 Body Sketch；原生欄位不受攔截。')
            self.layout.operator('learning_box.guarded_change', icon='CHECKMARK')

    CLASSES = (BOX_OT_guarded_change, BOX_PT_guarded_parameters)

    def register():
        for cls in CLASSES:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in reversed(CLASSES):
            bpy.utils.unregister_class(cls)

    if __name__ == '__main__':
        register()
