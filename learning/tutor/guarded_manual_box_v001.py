"""手工盒尺寸預檢：僅限具名 CAD Sketcher 示範模型副本。

此工具不攔截 Blender 或 CAD Sketcher 原生欄位；不自動存檔。
範圍只避免本形狀鍵公式觸及夾限，並不證明設計或實體製造合格。
"""
import importlib
import importlib.util
import hashlib
import json
import math
import os
import stat
from pathlib import Path

SCRIPT_NAME = 'guarded_manual_box_v001.py'
_GUARD_ROOT = None
_GUARD_SCRIPT = None
ROOT = WORKSPACE = PROGRESS = None
FIELDS = {
    'L': ('長度 L', 'slvs:c:b596b36138076155'),
    'W': ('寬度 W', 'slvs:c:854e8777cfe2608d'),
}
INNER_UID = {'L': 'slvs:c:d111c9dc741ee189', 'W': 'slvs:c:1876d52c9b6423cb'}
LIMITS = {'L': (60.0, 100.0), 'W': (30.0, 70.0)}
# Pinned reference for the exact hand-built lid: original Basis/relative keys,
# transform and face topology. A mismatch disables the controlled operation.
REFERENCE_SHA256 = '78f39a6ec422bb02b64fff64f70896c927a6ab449bcd84be9a03b6657bedae5c'
UPDATER_SHA256 = 'cc39a2376c8abc41f61cb5beb796a83e22b63dc33b6b6aed5df9f135e83fc457'

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
            raise GuardError('腳本必須位於專案 learning/tutor 的 本預檢原始檔。')
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
    operator.value_text = ''
    operator.acknowledged = False


def value_text_changed(operator, _context=None):
    operator.acknowledged = False


def validate(values):
    """Reject known shape-key clipping; no claim of design or fit validity."""
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        return ['必須完整提供長度 L 與寬度 W。']
    errors = []
    for field, (label, _) in FIELDS.items():
        number = values[field]
        try:
            valid = isinstance(number, (int, float)) and not isinstance(number, bool) and math.isfinite(number)
        except OverflowError:
            valid = False
        if not valid:
            errors.append(f'{label} 必須是有限數值（mm）。')
            continue
        low, high = LIMITS[field]
        if not low <= number <= high:
            errors.append(f'{label} 超出本範本形狀鍵未夾取的計算界限 {low:g}～{high:g} mm。')
    return errors


def parse_edit_input(field, text):
    if field not in FIELDS:
        raise GuardError('請先明確選擇要修改的參數。')
    if not isinstance(text, str) or not text.strip():
        raise GuardError('請輸入新數值（mm）；不可空白。')
    try:
        value = float(text.strip())
    except ValueError as exc:
        raise GuardError('新數值不是有效數字。') from exc
    proposed = {key: 80.0 if key == 'L' else 50.0 for key in FIELDS}
    proposed[field] = value
    errors = validate(proposed)
    if errors:
        raise GuardError('；'.join(errors))
    return value


def unit_error(system, scale):
    if system != 'METRIC' or not isinstance(scale, (float, int)) or isinstance(scale, bool) or not math.isfinite(scale) or not math.isclose(scale, .001, abs_tol=1e-9):
        return '場景必須為 Metric、Unit Scale 0.001。'
    return None


def geometry_error(values, levels, counts, nonmanifold):
    """Check the captured template's evaluated vertex levels, not complete collision.

    Levels contain per-z x/y coordinate sets in world space. The fixed lip has
    measured ~0.0005 mm scale deviation; tolerance is deliberately smaller
    than nominal 0.2 mm per-side trial clearance.
    """
    errors = validate(values)
    if errors:
        return '；'.join(errors)
    L, W = values['L'], values['W']
    if counts != {'Body': (16, 12), 'Body.001': (8, 6), 'Cube': (24, 22)}:
        return '評估網格的點／面數與指定示範不符。'
    if nonmanifold != {'Body': 0, 'Body.001': 0, 'Cube': 0}:
        return '評估網格的非流形邊數不符本示範。'
    desired = {
        'Body': {0.0: ([0,L],[0,W]), 2.0: ([2,L-2],[2,W-2]), 30.0: ([0,2,L-2,L],[0,2,W-2,W])},
        'Body.001': {2.0: ([2,L-2],[2,W-2]), 30.0: ([2,L-2],[2,W-2])},
        'Cube': {26.0: ([2.2,4.2,L-4.2,L-2.2],[2.2,4.2,W-4.2,W-2.2]),
                 30.0: ([0,2.2,4.2,L-4.2,L-2.2,L],[0,2.2,4.2,W-4.2,W-2.2,W]),
                 32.0: ([0,L],[0,W])},
    }
    tolerance = .002
    for name, by_z in desired.items():
        actual = levels.get(name)
        if not isinstance(actual, dict) or set(actual) != set(by_z):
            return f'{name} 頂點高度層與指定範本不符。'
        for z, axes in by_z.items():
            observed = actual[z]
            for axis in range(2):
                if len(observed[axis]) != len(axes[axis]) or any(not math.isclose(a, b, rel_tol=0, abs_tol=tolerance) for a, b in zip(observed[axis], axes[axis])):
                    return f'{name} 在 Z={z:g} 的評估頂點不符預期；可能未更新或已被修改。'
    return None


def guarded_change(current, field, value, write, read, update, postcheck):
    """Precheck, single write, update, postcheck; best-effort rollback on error."""
    if field not in FIELDS:
        raise GuardError('未知參數。')
    old = dict(current)
    if validate(old):
        raise GuardError('目前尺寸超出本工具界限；先回復可核對的版本。')
    candidate = dict(old)
    candidate[field] = value
    problems = validate(candidate)
    if problems:
        raise GuardError('；'.join(problems))
    try:
        write(field, value)
        update()
        actual = read(field)
        if not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isclose(actual, value, rel_tol=0, abs_tol=1e-6):
            raise RuntimeError('修改後讀回值不一致。')
        if not postcheck(candidate):
            raise RuntimeError('更新後草圖或網格核對失敗。')
    except Exception as exc:
        try:
            write(field, old[field])
            update()
            restored = read(field)
            if not math.isclose(restored, old[field], rel_tol=0, abs_tol=1e-6) or not postcheck(old):
                raise RuntimeError('回復後網格核對失敗')
        except Exception as rollback_exc:
            raise GuardError(f'修改失敗（{exc}）；回復未確認（{rollback_exc}）。請勿存檔，重開原副本。') from exc
        raise GuardError(f'修改失敗（{exc}）；已回復原數值及可核對的頂點。') from exc
    return candidate


def _expect_driver(fcurves, path, expression, variable, target_path, scene):
    found = [curve for curve in fcurves if curve.data_path == path and curve.array_index == 0]
    if len(found) != 1:
        raise GuardError('缺少唯一且符合預期的 Driver。')
    driver = found[0].driver
    if driver.type != 'SCRIPTED' or not driver.is_valid or driver.expression.replace(' ', '') != expression:
        raise GuardError('Driver 公式或有效性與示範不符。')
    if len(driver.variables) != 1:
        raise GuardError('Driver 變數數量與示範不符。')
    var = driver.variables[0]
    if var.type != 'SINGLE_PROP' or var.name != variable or len(var.targets) != 1:
        raise GuardError('Driver 變數類型或名稱與示範不符。')
    target = var.targets[0]
    if target.id != scene or target.data_path != target_path:
        raise GuardError('Driver 來源不是預期的場景尺寸。')


def _reference_error(snapshot, reference):
    """Compare the specific lid mesh, basis and relative keys, without Blender.

    This is deliberately order-sensitive. A reordered or edited personal mesh
    is refused rather than guessed equivalent. It does not certify collisions.
    """
    try:
        if snapshot['name'] != 'Cube' or snapshot['type'] != 'MESH':
            return '上蓋物件名稱或類型不符。'
        ref_object, ref_mesh = reference['object'], reference['mesh']
        def close_tree(actual, expected):
            if isinstance(expected, list):
                return isinstance(actual, list) and len(actual) == len(expected) and all(
                    close_tree(a, b) for a, b in zip(actual, expected))
            return (isinstance(actual, (int, float)) and not isinstance(actual, bool)
                    and math.isfinite(actual)
                    and math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-5))
        if not close_tree(snapshot['matrixWorld'], ref_object['matrixWorld']):
            return '上蓋的物件矩陣與範本不符。'
        if not close_tree(snapshot['vertices'], ref_mesh['vertices']):
            return '上蓋的原始頂點與範本不符。'
        if snapshot['edges'] != ref_mesh['edges'] or snapshot['faces'] != ref_mesh['faces']:
            return '上蓋的邊或面拓撲與範本不符。'
        if len(snapshot['keys']) != len(reference['keys']):
            return '上蓋形狀鍵數量與範本不符。'
        for actual, expected in zip(snapshot['keys'], reference['keys']):
            if actual['name'] != expected['name'] or actual['relative'] != expected['relative']:
                return '上蓋形狀鍵名稱或相對基礎不符。'
            if not close_tree(actual['min'], expected['min']) or not close_tree(actual['max'], expected['max']):
                return '上蓋形狀鍵範圍與範本不符。'
            if not close_tree(actual['values'], expected['values']):
                return '上蓋形狀鍵頂點與範本不符。'
    except (KeyError, TypeError, ValueError, OverflowError):
        return '無法核對上蓋原始網格與形狀鍵。'
    return None


def _check_reference(obj):
    path = _GUARD_ROOT / 'learning' / 'tutor' / 'manual_box_reference_v001.json'
    if not path.is_file() or _has_reparse_ancestor(path):
        raise GuardError('找不到安全的上蓋範本簽章。')
    try:
        contents = path.read_bytes()
        if hashlib.sha256(contents).hexdigest() != REFERENCE_SHA256:
            raise GuardError('上蓋範本簽章內容已變動。')
        reference = json.loads(contents.decode('utf-8-sig'))
        keys = obj.data.shape_keys
        if keys is None:
            raise GuardError('找不到上蓋形狀鍵。')
        snapshot = {
            'name': obj.name, 'type': obj.type,
            'matrixWorld': [[float(x) for x in row] for row in obj.matrix_world],
            'vertices': [[float(x) for x in v.co] for v in obj.data.vertices],
            'edges': [[int(x) for x in edge.vertices] for edge in obj.data.edges],
            'faces': [[int(x) for x in face.vertices] for face in obj.data.polygons],
            'keys': [{'name': key.name, 'relative': key.relative_key.name,
                      'min': float(key.slider_min), 'max': float(key.slider_max),
                      'values': [[float(x) for x in point.co] for point in key.data]}
                     for key in keys.key_blocks],
        }
        problem = _reference_error(snapshot, reference)
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        raise GuardError('無法讀取上蓋範本簽章或網格。') from exc
    if problem:
        raise GuardError(problem)


def _check_keys(obj, scene, values):
    keys = obj.data.shape_keys
    if keys is None or not keys.use_relative or len(keys.key_blocks) != 3:
        raise GuardError('上蓋須具有示範用 Basis、Key 1 與 Key 2。')
    basis = keys.key_blocks.get('Basis')
    if basis is None or len(basis.data) != 24 or not keys.animation_data:
        raise GuardError('無法辨認上蓋的形狀鍵資料。')
    if len(keys.animation_data.drivers) != 2:
        raise GuardError('上蓋 Driver 數量與指定範本不符。')
    matrix = obj.matrix_world
    for index, field in enumerate(('L', 'W'), start=1):
        key = keys.key_blocks.get(f'Key {index}')
        if key is None or key.relative_key != basis or len(key.data) != len(basis.data):
            raise GuardError('上蓋形狀鍵的相對基礎不符。')
        if not math.isclose(key.slider_min, -2.0, abs_tol=1e-7) or not math.isclose(key.slider_max, 2.0, abs_tol=1e-7):
            raise GuardError('上蓋形狀鍵夾限已變動。')
        desired = (values[field] - (80.0 if field == 'L' else 50.0)) / 10.0
        if not math.isclose(float(key.value), desired, rel_tol=0, abs_tol=1e-5):
            raise GuardError('上蓋形狀鍵值未隨尺寸更新或被夾限。')
        source = FIELDS[field][1]
        varname = source.replace(':', '_')
        expr = varname + ('/10-8' if field == 'L' else '/10-5')
        _expect_driver(keys.animation_data.drivers, f'key_blocks["Key {index}"].value', expr, varname, f'["{source}"]', scene)
        # Relative key must move exactly the 12 positive-side vertices by 10 mm,
        # with the other 12 untouched; this guards against altered shape data.
        moved = 0
        for first, second in zip(basis.data, key.data):
            origin = matrix @ first.co
            delta = matrix.to_3x3() @ (second.co - first.co)
            target = 10.0 if origin[index-1] > (40.0 if field == 'L' else 25.0) else 0.0
            expected = (target, 0.0, 0.0) if field == 'L' else (0.0, target, 0.0)
            if any(not math.isclose(float(delta[i]), expected[i], rel_tol=0, abs_tol=.002) for i in range(3)):
                raise GuardError('上蓋形狀鍵的頂點位移與示範不符。')
            moved += bool(target)
        if moved != 12:
            raise GuardError('上蓋形狀鍵的移動頂點數不符。')


def _blender_state(context):
    import bpy
    if _GUARD_ROOT is None or _GUARD_SCRIPT is None:
        raise GuardError('無法確認預檢腳本來源。')
    root, script = resolve_script_root(str(_GUARD_SCRIPT))
    if root != _GUARD_ROOT or script != _GUARD_SCRIPT:
        raise GuardError('預檢腳本或專案路徑已變動。')
    problem = workspace_error(bpy.data.filepath, root, root / 'learning' / 'workspaces' / 'engineering-parametric', root / 'learning' / 'progress.json')
    if problem:
        raise GuardError(problem)
    if 'bl_ext.user_default.CAD_Sketcher' not in context.preferences.addons:
        raise GuardError('CAD Sketcher 未啟用。')
    scene = context.scene
    problem = unit_error(scene.unit_settings.system, scene.unit_settings.scale_length)
    if problem:
        raise GuardError(problem)
    if scene.library or scene.override_library:
        raise GuardError('場景必須是本機副本。')
    for name in ('Body', 'Body.001', 'Cube'):
        obj = scene.objects.get(name)
        if obj is None or obj.type != 'MESH' or obj.library or obj.override_library or obj.data.library or obj.data.override_library:
            raise GuardError(f'找不到本機示範網格 {name}。')
    ref = importlib.import_module('bl_ext.user_default.CAD_Sketcher.model.sketch_ref')
    sketch = ref.get_active_sketch(context)
    if not sketch or sketch.name != 'Body Sketch' or sketch.solver_state != 'OKAY' or sketch.dof != 0:
        raise GuardError('請進入指定的 Body Sketch 並先完成求解。')
    constraints = {}
    for field, (_, source) in FIELDS.items():
        uid = source.removeprefix('slvs:c:')
        found = [c for c in sketch.constraints.all if c.type == 'DISTANCE' and c.constraint_uid == uid and not c.is_reference]
        if len(found) != 1 or source not in scene:
            raise GuardError('原始長寬約束不存在或重複。')
        constraints[field] = found[0]
    values = {field: float(constraint.value) for field, constraint in constraints.items()}
    if validate(values):
        raise GuardError('目前尺寸超出本工具界限。')
    for field, (_, source) in FIELDS.items():
        if not math.isclose(float(scene[source]), values[field], rel_tol=0, abs_tol=1e-6):
            raise GuardError('外框約束與場景來源不一致。')
    if not scene.animation_data:
        raise GuardError('找不到內腔 Driver。')
    if len(scene.animation_data.drivers) != 2:
        raise GuardError('場景 Driver 數量與指定範本不符。')
    for field, (_, source) in FIELDS.items():
        name = source.replace(':', '_')
        _expect_driver(scene.animation_data.drivers, f'["{INNER_UID[field]}"]', name + '-4', name, f'["{source}"]', scene)
    lid = scene.objects['Cube']
    _check_reference(lid)
    _check_keys(lid, scene, values)
    return sketch, constraints, scene, values


def _evaluated_geometry(context, values):
    import bmesh
    depsgraph = context.evaluated_depsgraph_get()
    levels, counts, nonmanifold = {}, {}, {}
    for name in ('Body', 'Body.001', 'Cube'):
        obj = context.scene.objects[name].evaluated_get(depsgraph)
        mesh = obj.to_mesh()
        if mesh is None:
            raise GuardError(f'無法讀取 {name} 評估網格。')
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            nonmanifold[name] = sum(not e.is_manifold for e in bm.edges)
            counts[name] = (len(mesh.vertices), len(mesh.polygons))
            by_z = {}
            for vertex in mesh.vertices:
                p = obj.matrix_world @ vertex.co
                if not all(math.isfinite(float(p[i])) for i in range(3)):
                    raise GuardError('評估網格包含非有限座標。')
                z = round(float(p.z), 3)
                axes = by_z.setdefault(z, (set(), set()))
                axes[0].add(round(float(p.x), 4))
                axes[1].add(round(float(p.y), 4))
            levels[name] = {z: (sorted(x), sorted(y)) for z, (x, y) in by_z.items()}
        finally:
            bm.free()
            obj.to_mesh_clear()
    return geometry_error(values, levels, counts, nonmanifold)


def _update_cavity(context):
    """Load the companion updater from this same anchored project on demand."""
    path = _GUARD_ROOT / 'learning' / 'tutor' / 'manual_box_auto_update_v002.py'
    if not path.is_file() or _has_reparse_ancestor(path):
        raise GuardError('找不到同專案的內腔更新工具，或路徑含連結；拒絕修改。')
    try:
        if hashlib.sha256(path.read_bytes()).hexdigest() != UPDATER_SHA256:
            raise GuardError('內腔更新工具內容已變動，拒絕修改。')
    except OSError as exc:
        raise GuardError('無法確認內腔更新工具。') from exc
    spec = importlib.util.spec_from_file_location('learning_manual_box_auto_update_v002', str(path))
    if spec is None or spec.loader is None:
        raise GuardError('無法載入內腔更新工具。')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'update_cavity', None)):
        raise GuardError('內腔更新工具缺少必要函式。')
    module.update_cavity(context)


try:
    import bpy
    from bpy.props import BoolProperty, EnumProperty, StringProperty
    from bpy.types import Operator, Panel
except ModuleNotFoundError:
    bpy = None

if bpy is not None:
    class MANUAL_BOX_OT_guarded_change(Operator):
        bl_idname = 'learning_box.manual_guarded_change_v001'
        bl_label = '預檢並更新一項尺寸'
        bl_description = '只處理指定手工盒範本；原生欄位可繞過'
        bl_options = {'REGISTER', 'UNDO'}
        field: EnumProperty(name='參數', items=[('NONE', '請選參數', '每次操作都須重新選擇')] + [(k, v[0], '') for k, v in FIELDS.items()], default='NONE', update=clear_edit_input)
        value_text: StringProperty(name='新數值 (mm)', default='', update=value_text_changed)
        acknowledged: BoolProperty(name='我已核對參數與新數值', default=False)

        def invoke(self, context, event):
            try:
                _blender_state(context)
                self.field = 'NONE'
                clear_edit_input(self)
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            return context.window_manager.invoke_props_dialog(self, width=430)

        def draw(self, context):
            self.layout.prop(self, 'field')
            self.layout.prop(self, 'value_text')
            try:
                _, _, _, values = _blender_state(context)
                self.layout.label(text=(f'目前 {FIELDS[self.field][0]}：{values[self.field]:g} mm' if self.field in FIELDS else '先選參數，再輸入數值。'))
            except Exception:
                self.layout.label(text='目前狀態無法讀取；操作將被拒絕。', icon='ERROR')
            self.layout.prop(self, 'acknowledged')
            self.layout.label(text='此範本鍵值範圍不是製造或配合合格範圍。', icon='ERROR')
            self.layout.label(text='原生欄位可繞過預檢；此工具不會存檔。', icon='INFO')

        def execute(self, context):
            try:
                if not self.acknowledged:
                    raise GuardError('請先核對參數與新數值並勾選確認。')
                value = parse_edit_input(self.field, self.value_text)
                sketch, constraints, scene, current = _blender_state(context)
                problem = _evaluated_geometry(context, current)
                if problem:
                    raise GuardError('套用前：' + problem)
                def write(field, number):
                    constraints[field].value = number
                    scene.update_tag()
                    context.view_layer.update()
                def read(field):
                    return float(constraints[field].value)
                def update():
                    _update_cavity(context)
                def check(expected):
                    _, _, _, actual = _blender_state(context)
                    if any(not math.isclose(actual[k], expected[k], rel_tol=0, abs_tol=1e-6) for k in FIELDS):
                        return False
                    return _evaluated_geometry(context, expected) is None
                guarded_change(current, self.field, value, write, read, update, check)
                self.report({'INFO'}, '已更新並核對指定模板頂點；並非實體配合判定。')
                return {'FINISHED'}
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}

    class MANUAL_BOX_PT_guard(Panel):
        bl_label = '手工盒尺寸預檢 v001'
        bl_idname = 'MANUAL_BOX_PT_guard_v001'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = '手工盒預檢'
        def draw(self, context):
            self.layout.label(text='指定手工盒個人副本，先進 Body Sketch。')
            self.layout.label(text='原生欄位可繞過；工具不自動存檔。')
            self.layout.operator('learning_box.manual_guarded_change_v001', icon='CHECKMARK')

    CLASSES = (MANUAL_BOX_OT_guarded_change, MANUAL_BOX_PT_guard)

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
