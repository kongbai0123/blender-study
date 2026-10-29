"""數位尺寸預檢與可選的 Blender 受控輸入面板（v004 試作專用）。

在 Blender 的 Scripting 工作區以 Text Editor 開啟本檔並 Run Script，然後
3D Viewport 側欄的「盒尺寸預檢」面板可一次修改一個參數。
此工具不會攔截 CAD Sketcher 或 Scene 原生欄位的直接修改，也不會存檔。
檢查為數位模型的必要條件，不是完整干涉、切片、強度或實體配合驗證。
"""
import json
import math
import os
import stat
import struct
from pathlib import Path

SCRIPT_NAME = 'guarded_box_parameters_v007.py'
# Bound only at registration, never inferred from cwd or a Blender virtual __file__.
_GUARD_ROOT = None
_GUARD_SCRIPT = None
ROOT = WORKSPACE = PROGRESS = None

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

# 工具可處理的保守數值範圍，不代表製程或產品允許尺寸。
MAX_MM = 1000.0


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
        elif value > MAX_MM:
            errors.append(f'{label} 超出本工具上限 {MAX_MM:g} mm；此上限不是製造能力。')
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
        error = float32_geometry_error(values)
        if error:
            errors.append(error)
    if not errors:
        if H - D == B:
            warnings.append('H−D=B：唇邊與盒內底在名義位置接觸；未留軸向間隙。')
        if C == 0:
            warnings.append('C=0：名義水平間隙為零；尚無實體配合結論。')
        warnings.append('僅通過必要的數位尺寸條件；未驗證完整碰撞、切片、列印或配合。')
    return errors, warnings


def _link_in_path(root, target):
    """Reject every symlink or Windows reparse point under the project root."""
    base = Path(os.path.abspath(root))
    path = Path(os.path.abspath(target))
    parts = path.relative_to(base).parts
    current = base
    for part in parts:
        current = current / part
        st = current.lstat()
        if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
            return True
    return False


def _has_reparse_ancestor(path):
    """Inspect the entire absolute chain, including the root directory itself."""
    path = Path(path)
    for component in reversed((path, *path.parents)):
        st = component.lstat()
        if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
            return True
    return False


def resolve_script_root(raw_file, *, text_mode=False, text_filepath=None, text_abspath=None,
                        text_content=None, text_dirty=None, blend_filepath=None):
    """Find the one project anchored by the saved external script; fail closed.

    Blender Text Editor supplies a virtual __file__. In that context only the
    saved Text.filepath resolved by Blender is accepted. Outside it, only an
    existing absolute __file__ can be used. No cwd-relative resolution.
    """
    if text_mode:
        if not isinstance(text_filepath, str) or not text_filepath.strip() or not callable(text_abspath):
            raise GuardError('文字編輯器必須開啟外部已存腳本；無法確認來源。')
        try:
            source = text_abspath(text_filepath)
        except Exception as exc:
            raise GuardError('無法解析文字檔路徑。') from exc
    else:
        source = raw_file
    if not isinstance(source, str) or not source or not Path(source).is_absolute():
        raise GuardError('腳本來源必須是已存在的絕對路徑；不使用目前工作目錄。')
    # Blender's absolute Text path may still contain '..'. Check every original
    # component for reparse points before collapsing lexical traversal.
    original_path = Path(source)
    try:
        if _has_reparse_ancestor(original_path):
            raise GuardError('腳本不存在或路徑含連結／重新剖析點。')
        path = Path(os.path.normpath(source))
        if path.name != SCRIPT_NAME or path.parent.name != 'tutor' or path.parent.parent.name != 'learning':
            raise GuardError('腳本必須位於專案 learning/tutor 的 v007 原始檔。')
        if not path.is_file() or _has_reparse_ancestor(path):
            raise GuardError('腳本不存在或路徑含連結／重新剖析點。')
        canonical = path.resolve(strict=True)
        if text_mode:
            if text_dirty is not False or not isinstance(text_content, str):
                raise GuardError('文字檔尚未儲存或無法確認內容。')
            if canonical.read_text(encoding='utf-8') != text_content:
                raise GuardError('文字編輯器內容與磁碟腳本不同；拒絕執行。')
            if not isinstance(raw_file, str) or not Path(raw_file).is_absolute():
                raise GuardError('無法確認執行來源。')
            raw = Path(raw_file)
            if raw.is_file():
                if raw.resolve(strict=True) != canonical:
                    raise GuardError('執行來源與目前文字檔不同；拒絕執行。')
            else:
                if not isinstance(blend_filepath, str) or not Path(blend_filepath).is_absolute():
                    raise GuardError('無法確認 Text Editor 的虛擬執行路徑。')
                expected_virtual = Path(blend_filepath) / SCRIPT_NAME
                if os.path.normcase(os.path.normpath(str(raw))) != os.path.normcase(os.path.normpath(str(expected_virtual))):
                    raise GuardError('執行來源與目前文字檔不一致；拒絕執行。')
        project = canonical.parents[2]
        if canonical != project / 'learning' / 'tutor' / SCRIPT_NAME:
            raise GuardError('腳本位置不符合專案結構。')
        parts = [part.casefold() for part in project.parts]
        if any(a == 'learning' and b == 'evidence' for a, b in zip(parts, parts[1:])):
            raise GuardError('專案根位於 evidence 證據區內；拒絕修改。')
        workspace = project / 'learning' / 'workspaces' / 'engineering-parametric'
        progress = project / 'learning' / 'progress.json'
        if not workspace.is_dir() or not progress.is_file():
            raise GuardError('專案缺少預期工作區或進度檔。')
        if _has_reparse_ancestor(workspace) or _has_reparse_ancestor(progress):
            raise GuardError('工作區或進度路徑包含連結／重新剖析點。')
    except (OSError, RuntimeError, ValueError) as exc:
        raise GuardError('無法確認已存腳本及專案路徑。') from exc
    return project, canonical


def workspace_error(filepath, root=ROOT, workspace=WORKSPACE, progress=PROGRESS, link_check=_link_in_path):
    """Fail closed outside workspace or if path is a registered checkpoint."""
    if not filepath:
        return '請先將個人副本另存至 engineering-parametric 工作區。'
    try:
        project_root = Path(root).resolve()
        raw_workspace = Path(os.path.abspath(workspace))
        raw_progress = Path(os.path.abspath(progress))
        raw_path = Path(os.path.abspath(filepath))
        if raw_workspace != project_root / 'learning' / 'workspaces' / 'engineering-parametric' or raw_progress != project_root / 'learning' / 'progress.json':
            return '工作區或進度檔路徑不符合預期。'
        for target in (raw_workspace, raw_progress, raw_path):
            if link_check(project_root, target):
                return '工作區、檔案或進度路徑包含連結／重新剖析點；拒絕修改。'
        path = raw_path.resolve()
        workspaces_root = (project_root / 'learning' / 'workspaces').resolve()
        workspaces_root.relative_to(project_root)
        Path(workspace).resolve().relative_to(workspaces_root)
        evidence = (project_root / 'learning' / 'evidence').resolve()
        for candidate in (workspaces_root, Path(workspace).resolve(), path, raw_progress.resolve()):
            if candidate == evidence or evidence in candidate.parents:
                return '路徑指向 evidence 證據區；拒絕修改。'
    except (OSError, RuntimeError, ValueError):
        return '無法核對共用版本清單或工作區路徑；拒絕修改。'
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


def clear_edit_input(operator, _context=None):
    """Whenever a different parameter is selected, discard input and consent."""
    operator.value_text = ''
    operator.acknowledged = False


def value_text_changed(operator, _context=None):
    """Any change to the proposed value invalidates prior confirmation."""
    operator.acknowledged = False


def parse_edit_input(field, text):
    if field not in FIELDS:
        raise GuardError('請先明確選擇要修改的參數。')
    if not isinstance(text, str) or not text.strip():
        raise GuardError('請輸入新數值（mm）；不可空白。')
    try:
        value = float(text.strip())
    except ValueError as exc:
        raise GuardError('新數值不是有效數字。') from exc
    if not math.isfinite(value):
        raise GuardError('新數值必須是有限數字。')
    return value


def float32_geometry_error(values):
    """Require nonzero modeled boundaries to remain distinct in float32.

    No arbitrary epsilon: this is a representation check, not tolerance advice.
    """
    L, W, H, T, B, P, D, C, S = (values[k] for k in FIELDS)
    def f(x):
        return struct.unpack('f', struct.pack('f', x))[0]
    try:
        for size in (L, W):
            outer = (0, T, size-T, size)
            lip = (T+C/2, T+C/2+S, size-T-C/2-S, size-T-C/2)
            for limits in (outer, lip):
                converted = [f(x) for x in limits]
                if not all(math.isfinite(x) for x in converted) or not all(a < b for a, b in zip(converted, converted[1:])):
                    return '必要壁或內腔邊界在 float32 中無法區分；拒絕修改。'
            # Nonzero specified clearance must not round to contact.
            if C > 0 and not (f(T) < f(T+C/2) and f(size-T-C/2) < f(size-T)):
                return '非零名義間隙在 float32 中無法區分；拒絕修改。'
        z0, bottom, lip_bottom, top, cover = (f(v) for v in (0, B, H-D, H, H+P))
        if not all(math.isfinite(x) for x in (z0, bottom, lip_bottom, top, cover)) or not (z0 < bottom <= lip_bottom < top < cover):
            return '必要高度邊界在 float32 中無法區分；拒絕修改。'
        if H-D > B and lip_bottom <= bottom:
            return '非零軸向間距在 float32 中無法區分；拒絕修改。'
    except (OverflowError, struct.error):
        return '參數超過 float32 可表示範圍；拒絕修改。'
    return None


def unit_error(system, scale):
    """This particular file uses one Blender unit = one millimetre."""
    try:
        valid = system == 'METRIC' and math.isfinite(scale) and math.isclose(scale, 0.001, rel_tol=1e-6, abs_tol=1e-9)
    except (TypeError, ValueError):
        valid = False
    return None if valid else '需要 Metric 且 Unit Scale = 0.001；拒絕修改。'


def expected_vertices(values):
    """World-space vertex positions for the original v004 topology only."""
    L, W, H, T, B, P, D, C, S = (values[k] for k in FIELDS)
    def ring(x0, x1, y0, y1, z):
        return [(x0,y0,z), (x1,y0,z), (x1,y1,z), (x0,y1,z)]
    x0, x1, y0, y1 = T+C/2, L-T-C/2, T+C/2, W-T-C/2
    xi0, xi1, yi0, yi1 = x0+S, x1-S, y0+S, y1-S
    body = (ring(0,L,0,W,0) + ring(0,L,0,W,H) +
            ring(T,L-T,T,W-T,H) + ring(T,L-T,T,W-T,B))
    lid = (ring(0,L,0,W,H+P) + ring(0,L,0,W,H) +
           ring(x0,x1,y0,y1,H) + ring(x0,x1,y0,y1,H-D) +
           ring(xi0,xi1,yi0,yi1,H-D) + ring(xi0,xi1,yi0,yi1,H))
    return body, lid


def expected_faces():
    """Face connectivity and winding for the original v004 object topology."""
    def join(a, b, flip=False):
        faces = [(a+i, a+(i+1)%4, b+(i+1)%4, b+i) for i in range(4)]
        return [tuple(reversed(f)) for f in faces] if flip else faces
    body = [(3, 2, 1, 0)] + join(0, 4) + join(4, 8) + join(8, 12) + [(12, 13, 14, 15)]
    lid = ([(0, 1, 2, 3)] + join(4, 0) + join(4, 8, True) + join(12, 8) +
           join(12, 16, True) + join(20, 16) + [(23, 22, 21, 20)])
    return body, lid


def _face_key(face):
    """Cyclic rotation is equivalent; reversing a face is not."""
    face = tuple(face)
    if len(face) < 3:
        raise ValueError('degenerate face')
    return min(face[i:] + face[:i] for i in range(len(face)))


def _signed_volume(vertices, faces):
    volume6 = 0.0
    for face in faces:
        a = vertices[face[0]]
        for i in range(1, len(face)-1):
            b, c = vertices[face[i]], vertices[face[i+1]]
            volume6 += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
    return volume6 / 6.0


def geometry_error(values, body, lid, nonmanifold, faces):
    """Exact float32 coordinate, source connectivity, winding and volume checks.

    This checks specified geometry only; not general collision or physical fit.
    """
    expected = expected_vertices(values)
    if nonmanifold != (0, 0):
        return '盒體或上蓋有非流形邊，拒絕修改。'
    if len(faces) != 2:
        return '無法讀取盒體與上蓋的面。'
    for name, actual, target, actual_faces, target_faces in zip(('盒體', '上蓋'), (body, lid), expected, faces, expected_faces()):
        if len(actual) != len(target):
            return f'{name}求值網格頂點數不符 v004。'
        try:
            if sorted(map(_face_key, actual_faces)) != sorted(map(_face_key, target_faces)):
                return f'{name}的面連接或方向不符 v004。'
            for xyz, wanted in zip(actual, target):
                if len(xyz) != 3 or any(not math.isfinite(x) for x in xyz):
                    return f'{name}求值頂點不是有限座標。'
                def f32(x):
                    return struct.unpack('f', struct.pack('f', x))[0]
                if any(f32(a) != f32(b) for a, b in zip(xyz, wanted)):
                    return f'{name}求值頂點與參數的 float32 表示不符；拒絕修改。'
            volume = _signed_volume(actual, actual_faces)
            if not math.isfinite(volume) or volume <= 0:
                return f'{name}有向體積不是有限正值。'
        except (ValueError, TypeError, OverflowError, struct.error, IndexError):
            return f'{name}求值網格無法核對。'
    return None


def _evaluated_geometry(context, values):
    import bmesh
    import bpy
    dg = context.evaluated_depsgraph_get()
    points, counts, faces = [], [], []
    for name in ('Parametric Box', 'Parametric Lid'):
        obj = bpy.data.objects[name].evaluated_get(dg)
        mesh = obj.to_mesh()
        if mesh is None:
            raise GuardError(f'{name} 無法取得求值網格。')
        try:
            expected_counts = (16, 28, 14) if name == 'Parametric Box' else (24, 44, 22)
            if (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) != expected_counts:
                raise GuardError(f'{name} 求值網格拓樸數量不符 v004。')
            points.append([tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices])
            faces.append([tuple(poly.vertices) for poly in mesh.polygons])
            bm = bmesh.new()
            try:
                bm.from_mesh(mesh)
                counts.append(sum(not edge.is_manifold for edge in bm.edges))
            finally:
                bm.free()
        finally:
            obj.to_mesh_clear()
    return geometry_error(values, points[0], points[1], tuple(counts), faces), points


def driver_change_error(old_values, new_values, before, after):
    """Every coordinate expected to change in float32 must actually change."""
    expected_before, expected_after = expected_vertices(old_values), expected_vertices(new_values)
    def f(x):
        return struct.unpack('f', struct.pack('f', x))[0]
    for first, second, actual_before, actual_after in zip(expected_before, expected_after, before, after):
        for a, b, c, d in zip(first, second, actual_before, actual_after):
            for x, y, observed_x, observed_y in zip(a, b, c, d):
                if f(x) != f(y) and f(observed_x) == f(observed_y):
                    return '應變動的頂點未更新；可能存在失效驅動。'
    return None


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
        if not postcheck(candidate):
            raise RuntimeError('草圖或求值網格核對失敗。')
    except Exception as exc:
        try:
            write(field, old[field])
            restored = read(field)
            if not math.isclose(restored, old[field], rel_tol=1e-8, abs_tol=1e-6) or not postcheck(old):
                raise RuntimeError('回復後核對失敗')
        except Exception as rollback_exc:
            raise GuardError(f'修改失敗（{exc}）；自動回復未確認（{rollback_exc}）。請勿存檔，重新開啟原副本。') from exc
        raise GuardError(f'修改失敗（{exc}）；已回復原數值。') from exc
    return candidate, warnings


def _blender_state(context):
    """Get the active v004-compatible sketch and parameters without writes."""
    import importlib
    import bpy

    if _GUARD_ROOT is None or _GUARD_SCRIPT is None:
        raise GuardError('無法確認載入的 v007 腳本與專案；拒絕修改。')
    root, script = resolve_script_root(str(_GUARD_SCRIPT))
    if root != _GUARD_ROOT or script != _GUARD_SCRIPT:
        raise GuardError('腳本或專案路徑已變動；拒絕修改。')
    problem = workspace_error(bpy.data.filepath, root, root / 'learning' / 'workspaces' / 'engineering-parametric', root / 'learning' / 'progress.json')
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
        if context.scene.objects.get(name) != obj:
            raise GuardError('盒體或上蓋不屬於目前場景；拒絕修改。')
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
    problem = unit_error(scene.unit_settings.system, scene.unit_settings.scale_length)
    if problem:
        raise GuardError(problem)
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
    from bpy.props import BoolProperty, EnumProperty, StringProperty
    from bpy.types import Operator, Panel
except ModuleNotFoundError:
    bpy = None

if bpy is not None:
    class BOX_OT_guarded_change(Operator):
        bl_idname = 'learning_box.guarded_change_v007'
        bl_label = '預檢後修改一項尺寸'
        bl_description = '先檢查所有數位尺寸，再修改一項；不保證實體配合'
        bl_options = {'REGISTER', 'UNDO'}
        field: EnumProperty(name='參數', items=[('NONE', '請選參數', '每次操作都須重新選擇')] + [(k, v[0], '') for k, v in FIELDS.items()], default='NONE', update=clear_edit_input)
        value_text: StringProperty(name='新數值 (mm)', default='', description='請自行輸入數值；修改數值後須重新確認', update=value_text_changed)
        acknowledged: BoolProperty(name='我已核對參數與新數值', default=False)

        def invoke(self, context, event):
            try:
                _blender_state(context)
                self.field = 'NONE'
                clear_edit_input(self)
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            return context.window_manager.invoke_props_dialog(self, width=420)

        def draw(self, context):
            self.layout.prop(self, 'field')
            self.layout.prop(self, 'value_text')
            try:
                _, _, _, values = _blender_state(context)
                if self.field in FIELDS:
                    self.layout.label(text=f'目前 {FIELDS[self.field][0]}：{values[self.field]:g} mm')
                else:
                    self.layout.label(text='請先選參數，再輸入新數值。', icon='INFO')
            except Exception:
                self.layout.label(text='目前值無法讀取；操作將被拒絕。', icon='ERROR')
            self.layout.prop(self, 'acknowledged')
            self.layout.label(text='一次一項；不攔截原生欄位直接輸入。', icon='INFO')
            self.layout.label(text='預檢非完整干涉或實體配合判定。', icon='ERROR')

        def execute(self, context):
            try:
                if not self.acknowledged:
                    raise GuardError('請先核對參數與新數值並勾選確認。')
                value = parse_edit_input(self.field, self.value_text)
                sketch, constraints, scene, current = _blender_state(context)
                before_errors, _ = validate(current)
                if before_errors:
                    raise GuardError('目前尺寸不符預檢；先回復有效版本。')
                problem, before = _evaluated_geometry(context, current)
                if problem:
                    raise GuardError('套用前：' + problem)

                def write(field, value):
                    if field in constraints:
                        constraints[field].value = value
                    else:
                        scene[FIELDS[field][1]] = value
                    scene.update_tag()
                    context.view_layer.update()

                def read(field):
                    return float(constraints[field].value) if field in constraints else float(scene[FIELDS[field][1]])

                def postcheck(values):
                    # The add-on defers solving through depsgraph callbacks;
                    # do not report success while a solve is still pending.
                    import importlib
                    state = importlib.import_module('bl_ext.user_default.CAD_Sketcher.global_data')
                    if state.needs_solve or sketch.solver_state != 'OKAY' or sketch.dof != 0:
                        return False
                    for name, (_, key) in FIELDS.items():
                        if not math.isclose(float(scene[key]), values[name], rel_tol=1e-8, abs_tol=1e-6):
                            return False
                    problem, after = _evaluated_geometry(context, values)
                    if problem:
                        return False
                    return driver_change_error(current, values, before, after) is None

                _, warnings = guarded_change(current, self.field, value, write, read, postcheck)
                self.report({'INFO'}, '已修改；' + ' '.join(warnings))
                return {'FINISHED'}
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}

    class BOX_PT_guarded_parameters(Panel):
        bl_label = '盒尺寸預檢 v007'
        bl_idname = 'BOX_PT_guarded_parameters_v007'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = '盒尺寸預檢'

        def draw(self, context):
            self.layout.label(text='v004 盒蓋個人副本專用', icon='INFO')
            self.layout.label(text='先進入 Body Sketch；原生欄位不受攔截。')
            self.layout.operator('learning_box.guarded_change_v007', icon='CHECKMARK')

    CLASSES = (BOX_OT_guarded_change, BOX_PT_guarded_parameters)

    def register():
        global _GUARD_ROOT, _GUARD_SCRIPT
        space = getattr(bpy.context, 'space_data', None)
        text_mode = getattr(space, 'type', None) == 'TEXT_EDITOR'
        text = getattr(space, 'text', None) if text_mode else None
        text_path = getattr(text, 'filepath', None) if text is not None else None
        try:
            content = text.as_string() if text is not None else None
            dirty = getattr(text, 'is_dirty', None) if text is not None else None
        except Exception as exc:
            raise GuardError('無法讀取文字編輯器內容。') from exc
        _GUARD_ROOT, _GUARD_SCRIPT = resolve_script_root(
            globals().get('__file__'), text_mode=text_mode,
            text_filepath=text_path, text_abspath=bpy.path.abspath if text_mode else None,
            text_content=content, text_dirty=dirty,
            blend_filepath=bpy.data.filepath if text_mode else None)
        for cls in CLASSES:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in reversed(CLASSES):
            bpy.utils.unregister_class(cls)

    if __name__ == '__main__':
        register()
