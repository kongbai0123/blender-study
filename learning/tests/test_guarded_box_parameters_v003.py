"""Dimensions and fail-closed guard tests; does not launch Blender."""
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

GUARD = Path(__file__).resolve().parents[1] / 'tutor' / 'guarded_box_parameters_v003.py'
spec = importlib.util.spec_from_file_location('guarded_box_parameters_v003', GUARD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class DimensionsTest(unittest.TestCase):
    def setUp(self):
        self.valid = {'L': 80., 'W': 40., 'H': 30., 'T': 2., 'B': 2., 'P': 2., 'D': 4., 'C': .4, 'S': 2.}

    def rejected(self, **changes):
        proposed = {**self.valid, **changes}
        self.assertTrue(guard.validate(proposed)[0], proposed)

    def test_valid_baseline_and_resized_y(self):
        self.assertFalse(guard.validate(self.valid)[0])
        self.assertFalse(guard.validate({**self.valid, 'W': 50.})[0])

    def test_reject_bad_values_and_degenerate_openings(self):
        for update in ({'L': math.nan}, {'W': math.inf}, {'P': True}, {'P': 0}, {'T': -1},
                       {'B': 0}, {'D': 0}, {'S': 0}, {'C': -.1}, {'H': 2},
                       {'W': 8.4}, {'L': 4}, {'L': '80'}, {'H': 10**1000}):
            with self.subTest(update=update):
                self.rejected(**update)

    def test_overlapping_lip_is_rejected_and_contact_warned(self):
        self.rejected(D=29.)  # H 30, B 2: lip bottom 1 is below floor 2.
        errors, warnings = guard.validate({**self.valid, 'D': 28.})
        self.assertFalse(errors)
        self.assertTrue(any('接觸' in item for item in warnings))
        errors, warnings = guard.validate({**self.valid, 'C': 0.})
        self.assertFalse(errors)
        self.assertTrue(any('間隙為零' in item for item in warnings))

    def test_invalid_candidate_does_not_call_writer(self):
        writes = []
        with self.assertRaises(guard.GuardError):
            guard.guarded_change(self.valid, 'D', 29., lambda *x: writes.append(x), lambda _: 4., lambda _: True)
        self.assertEqual(writes, [])

    def test_valid_candidate_applies_only_one_field(self):
        state = dict(self.valid)
        writes = []
        def write(k, v):
            writes.append((k, v)); state[k] = v
        result, _ = guard.guarded_change(state, 'W', 50., write, state.__getitem__, lambda _: True)
        self.assertEqual(writes, [('W', 50.)])
        self.assertEqual(result['W'], 50.)
        self.assertEqual(state['L'], 80.)

    def test_solver_failure_rolls_back_or_fails_loudly(self):
        state = dict(self.valid)
        def write(k, v): state[k] = v
        with self.assertRaisesRegex(guard.GuardError, '已回復原數值'):
            guard.guarded_change(state, 'W', 50., write, state.__getitem__, lambda _: state['W'] != 50.)
        self.assertEqual(state['W'], 40.)
        def bad_write(k, v):
            if v == 40.: raise RuntimeError('rollback failure')
            state[k] = v
        with self.assertRaisesRegex(guard.GuardError, '自動回復未確認'):
            guard.guarded_change(state, 'W', 50., bad_write, state.__getitem__, lambda _: False)

    def test_finite_max_and_float32_boundary_separation(self):
        self.rejected(H=1e39)
        self.rejected(L=1000.01)
        self.rejected(T=1e-8)
        self.rejected(L=1000, T=1e-6)
        self.rejected(C=1e-9)
        self.rejected(H=1000, P=1e-6)
        self.assertFalse(guard.validate({**self.valid, 'L': 1000})[0])

    def test_units_fail_closed(self):
        self.assertIsNone(guard.unit_error('METRIC', .001))
        self.assertIsNone(guard.unit_error('METRIC', .00100000005))
        for system, scale in [('NONE', .001), ('METRIC', 1), ('IMPERIAL', .001), ('METRIC', float('nan')), ('METRIC', None)]:
            self.assertIsNotNone(guard.unit_error(system, scale))

    def test_mesh_checks_and_failed_change_rollback(self):
        base = self.valid
        body, lid = guard.expected_vertices(base)
        faces = guard.expected_faces()
        self.assertIsNone(guard.geometry_error(base, body, lid, (0, 0), faces))
        self.assertIsNotNone(guard.geometry_error(base, body, lid, (1, 0), faces))
        self.assertIsNotNone(guard.geometry_error({**base, 'W': 50.}, body, lid, (0, 0), faces))
        new = {**base, 'W': 50.}
        newbody, newlid = guard.expected_vertices(new)
        self.assertIsNone(guard.driver_change_error(base, new, [body, lid], [newbody, newlid]))
        self.assertIsNotNone(guard.driver_change_error(base, new, [body, lid], [body, newlid]))
        state = dict(base)
        def write(k, v): state[k] = v
        def check(v):
            return guard.geometry_error(v, body, lid, (0, 0), faces) is None
        with self.assertRaisesRegex(guard.GuardError, '已回復原數值'):
            guard.guarded_change(state, 'W', 50., write, state.__getitem__, check)
        self.assertEqual(state, base)

    def test_thin_wall_collapsed_inside_float32_is_rejected(self):
        value = {**self.valid, 'T': .0001}
        self.assertFalse(guard.validate(value)[0])
        body, lid = guard.expected_vertices(value)
        body = list(body)
        for index in (9, 10, 13, 14):
            _, y, z = body[index]
            body[index] = (80., y, z)
        self.assertIsNotNone(guard.geometry_error(value, body, lid, (0, 0), guard.expected_faces()))

    def test_face_winding_and_connectivity_checked(self):
        body, lid = guard.expected_vertices(self.valid)
        box_faces, lid_faces = guard.expected_faces()
        self.assertGreater(guard._signed_volume(body, box_faces), 0)
        self.assertGreater(guard._signed_volume(lid, lid_faces), 0)
        reverse = [tuple(reversed(face)) for face in box_faces]
        self.assertIsNotNone(guard.geometry_error(self.valid, body, lid, (0, 0), (reverse, lid_faces)))
        changed = list(box_faces)
        changed[1] = (0, 1, 2, 4)
        self.assertIsNotNone(guard.geometry_error(self.valid, body, lid, (0, 0), (changed, lid_faces)))
        rotated = [face[1:] + face[:1] for face in box_faces]
        self.assertIsNone(guard.geometry_error(self.valid, body, lid, (0, 0), (rotated, lid_faces)))


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='guard-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.work = self.root / 'learning' / 'workspaces' / 'engineering-parametric'
        self.work.mkdir(parents=True)
        self.progress = self.root / 'learning' / 'progress.json'
        self.progress.write_text('{"fileVersions": []}', encoding='utf-8')
        self.copy = self.work / 'box_v001.blend'
        self.copy.write_bytes(b'personal test copy')

    def check(self, file):
        return guard.workspace_error(file, self.root, self.work, self.progress)

    def test_only_existing_unregistered_workspace_copy_allowed(self):
        self.assertIsNone(self.check(self.copy))
        self.assertIsNotNone(self.check(''))
        self.assertIsNotNone(self.check(self.work / 'missing.blend'))
        evidence = self.root / 'learning' / 'evidence' / 'source.blend'
        evidence.parent.mkdir(); evidence.write_bytes(b'source')
        self.assertIsNotNone(self.check(evidence))
        self.progress.write_text(json.dumps({'fileVersions': [{'path': 'learning/workspaces/engineering-parametric/box_v001.blend'}]}), encoding='utf-8')
        self.assertIn('已登記', self.check(self.copy))

    def test_progress_missing_or_malformed_fails_closed(self):
        self.progress.unlink()
        self.assertIn('無法核對', self.check(self.copy))

    def test_in_project_junction_to_evidence_is_rejected_in_memory(self):
        evidence = self.root / 'learning' / 'evidence'
        evidence.mkdir()
        workspaces = self.root / 'learning' / 'workspaces'
        original_resolve = Path.resolve
        def simulated_resolve(path, *args, **kwargs):
            path = Path(path)
            if path == workspaces:
                return evidence
            if path == self.work:
                return evidence / 'engineering-parametric'
            if path == self.copy:
                return evidence / 'engineering-parametric' / self.copy.name
            return original_resolve(path, *args, **kwargs)
        # Even if a hypothetical platform's link detector misses the junction,
        # resolved evidence remains an independently rejected destination.
        with mock.patch.object(Path, 'resolve', simulated_resolve):
            self.assertIn('evidence', guard.workspace_error(self.copy, self.root, self.work, self.progress, link_check=lambda *_: False))

    def test_progress_or_workspace_reparse_point_rejected(self):
        for bad_path in (self.work, self.progress, self.copy):
            self.assertIsNotNone(guard.workspace_error(self.copy, self.root, self.work, self.progress,
                                                      link_check=lambda _, p: p == bad_path))
        self.progress.write_text('{bad', encoding='utf-8')
        self.assertIn('無法核對', self.check(self.copy))

    def test_workspace_link_escaping_project_is_rejected(self):
        outside_dir = self.root.parent / (self.root.name + '-outside')
        outside_dir.mkdir()
        self.addCleanup(lambda: outside_dir.rmdir())
        link = self.root / 'learning' / 'workspaces' / 'escape'
        try:
            link.symlink_to(outside_dir, target_is_directory=True)
        except OSError:
            self.skipTest('directory symlink creation not permitted')
        self.addCleanup(lambda: link.unlink())
        foreign_file = outside_dir / 'other.blend'
        foreign_file.write_bytes(b'outside')
        self.addCleanup(lambda: foreign_file.unlink())
        self.assertIsNotNone(guard.workspace_error(link / 'other.blend', self.root, link, self.progress))


class BlenderDefinitionTest(unittest.TestCase):
    def test_property_declarations_are_evaluated_for_blender_registration(self):
        # Test only class definitions against stand-ins; this does not launch Blender.
        fake_bpy = types.ModuleType('bpy')
        fake_props = types.ModuleType('bpy.props')
        fake_types = types.ModuleType('bpy.types')
        fake_types.Operator = type('Operator', (), {})
        fake_types.Panel = type('Panel', (), {})
        sentinel = object()
        for name in ('BoolProperty', 'EnumProperty', 'FloatProperty'):
            setattr(fake_props, name, lambda **kwargs: sentinel)
        fake_bpy.props, fake_bpy.types = fake_props, fake_types
        namespace = {'__name__': 'guard_definition_test', '__file__': str(GUARD)}
        with mock.patch.dict('sys.modules', {'bpy': fake_bpy, 'bpy.props': fake_props, 'bpy.types': fake_types}):
            exec(compile(GUARD.read_bytes(), str(GUARD), 'exec'), namespace)
        operator = namespace['BOX_OT_guarded_change']
        self.assertIs(operator.__annotations__['field'], sentinel)
        self.assertIs(operator.__annotations__['value'], sentinel)
        self.assertIs(operator.__annotations__['acknowledged'], sentinel)


if __name__ == '__main__':
    unittest.main()
