"""證據匯入的完整性與失敗不污染 catalog；全部資料都在 TemporaryDirectory。"""
import copy
import hashlib
import importlib.util
import json
import math
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "import_run.py"
SPEC = importlib.util.spec_from_file_location("blender_import_run", MODULE_PATH)
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)
RUN_ID = "2026-10-22-lesson05-demo-v001"
HOLES_RUN_ID = "2026-10-22-lesson05-holes-demo-v001"
EXPORT_RUN_ID = "2026-10-22-lesson05-export-demo-v001"
LID_RUN_ID = "2026-10-22-lesson05-lid-demo-v001"
LID_EXPORT_RUN_ID = "2026-10-25-lesson05-lid-export-demo-v001"
TENON_RUN_ID = "2026-10-25-lesson06-tenon-demo-v001"
DOVETAIL_RUN_ID = "2026-10-25-lesson06-dovetail-demo-v001"
DOVETAIL_EXPORT_RUN_ID = "2026-10-25-lesson06-dovetail-export-demo-v001"
PARAMETERS_RUN_ID = "2026-10-25-lesson07-parameters-demo-v001"
SNAP_RUN_ID = "2026-10-25-lesson07-snap-demo-v001"
OVERHANG_RUN_ID = "2026-10-25-lesson07-overhang-demo-v001"
SNAP_EXPORT_RUN_ID = "2026-10-25-lesson07-snap-export-demo-v001"
COUPONS_RUN_ID = "2026-10-25-lesson07-coupons-demo-v001"
COUPON_EXPORT_RUN_ID = "2026-10-25-lesson07-coupon-export-demo-v001"
THREAD_PARAMETERS_RUN_ID = "2026-10-25-lesson08-parameters-demo-v001"


def png_bytes(width=3, height=2):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = b"".join(b"\x00" + b"\x10\x20\x30" * width for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


def cuboid_plate_stl(width, height, depth, holes=()):
    """小型封閉測試模型：整齊網格板，holes 為 (centre_x, centre_y, width)。"""
    xs = sorted({-width / 2, width / 2} | {x + side * size / 2 for x, y, size in holes for side in (-1, 1)})
    ys = sorted({-height / 2, height / 2} | {y + side * size / 2 for x, y, size in holes for side in (-1, 1)})
    solid = {(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1)
             if not any(abs((xs[i] + xs[i + 1]) / 2 - x) < size / 2 and
                        abs((ys[j] + ys[j + 1]) / 2 - y) < size / 2 for x, y, size in holes)}
    triangles = []
    for i, j in solid:
        x0, x1, y0, y1, z0, z1 = xs[i], xs[i + 1], ys[j], ys[j + 1], -depth / 2, depth / 2
        a, b, c, d = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
        e, f, g, h = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
        triangles.extend(((e, f, g), (e, g, h), (a, c, b), (a, d, c)))
        if (i - 1, j) not in solid:
            triangles.extend(((a, h, d), (a, e, h)))
        if (i + 1, j) not in solid:
            triangles.extend(((b, c, g), (b, g, f)))
        if (i, j - 1) not in solid:
            triangles.extend(((a, b, f), (a, f, e)))
        if (i, j + 1) not in solid:
            triangles.extend(((d, g, c), (d, h, g)))
    data = b"test real binary STL".ljust(80, b"\0") + struct.pack("<I", len(triangles))
    for triangle in triangles:
        data += struct.pack("<12fH", 0, 0, 0, *(coordinate for point in triangle for coordinate in point), 0)
    return data, len(triangles), width * height * depth - sum(size * size * depth for x, y, size in holes)


class ImportRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "05" / RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "05", "steps": [
            {"id": "05-02", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.metadata_path = self.run_dir.parent / (RUN_ID + ".json")
        image = png_bytes()
        self.image_path = self.run_dir / "05-02-01-dimensions.png"
        self.image_path.write_bytes(image)
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson05.py",
            "records": [{
                "seq": 1, "step": "05-02", "file": self.image_path.name,
                "action": "輸入插銷尺寸", "observed": "10 × 10 × 8 mm", "recordedAt": "2026-10-22T07:00:00Z",
                "width": 3, "height": 2, "sha256": hashlib.sha256(image).hexdigest(),
                "highlights": [{"x": 1, "y": 0, "w": 2, "h": 1, "label": "Dimensions"}],
                "note": "示範，不代表學員完成"}]}
        self.scene = self.run_dir / "demo-files" / "u05_fit_coupon_v001.blend"
        self.scene.parent.mkdir()
        self.scene.write_bytes(b"BLENDER-test-scene")
        self.verification = {
            "passed": True, "dimensions_mm": [10, 10, 8], "scale": [1, 1, 1], "unit_scale": 0.001,
            "length_unit": "MILLIMETERS", "non_manifold_edges": 0, "closed_volume": True,
            "scene_path": str(self.scene), "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
            "reopened": True}
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson05", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-22T06:59:00Z", "endedAt": "2026-10-22T07:01:00Z"}
        self.write_evidence()

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse(self.metadata_path.exists())

    def test_valid_import_preserves_highlights_uses_actual_version_and_separates_learner(self):
        progress = self.project / "learning" / "progress.json"
        progress.write_bytes(b'{"revision":5}')
        result = IMPORTER.import_run(RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        operation = catalog["lessons"][0]["steps"][0]["operationRun"]
        self.assertEqual(operation["performedBy"], "tutor")
        figure = operation["events"][0]["figure"]
        self.assertEqual(figure["highlights"], self.run["records"][0]["highlights"])
        self.assertIn("5.9.9 TEST", figure["caption"])
        metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["application"], "Blender 5.9.9 TEST")
        self.assertEqual(metadata["verification"], self.verification)
        self.assertTrue(metadata["runnerStatus"]["workspacesUnchanged"])
        self.assertEqual(progress.read_bytes(), b'{"revision":5}')

    def test_v002_has_fixed_route_and_same_required_verification(self):
        run_id = "2026-10-22-lesson05-demo-v002"
        new_run_dir = self.run_dir.with_name(run_id)
        self.run_dir.rename(new_run_dir)
        self.run_dir = new_run_dir
        self.scene = new_run_dir / "demo-files" / "u05_fit_coupon_v001.blend"
        self.verification["scene_path"] = str(self.scene)
        self.runner["outputDir"] = str(new_run_dir)
        self.verification["passed"] = False
        self.write_evidence()
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(run_id, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((new_run_dir.parent / (run_id + ".json")).exists())

        self.verification["passed"] = True
        self.write_evidence()
        result = IMPORTER.import_run(run_id, self.project)
        self.assertEqual(result["steps"], 1)
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        operation = catalog["lessons"][0]["steps"][0]["operationRun"]
        self.assertEqual(operation["id"], run_id)
        self.assertEqual(operation["journal"], "learning/journal/2026-10-22-lesson05-demo-v002.md")

    def test_modified_screenshot_rejected_without_catalog_or_metadata(self):
        self.image_path.write_bytes(self.image_path.read_bytes() + b"changed")
        self.assert_rejected_cleanly()

    def test_missing_screenshot_rejected_without_catalog_or_metadata(self):
        self.image_path.unlink()
        self.assert_rejected_cleanly()

    def test_screenshot_dimensions_mismatch_rejected(self):
        self.run["records"][0]["width"] = 4
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_non_png_with_matching_digest_rejected(self):
        invalid = b"not-a-real-PNG" * 8
        self.image_path.write_bytes(invalid)
        self.run["records"][0]["sha256"] = hashlib.sha256(invalid).hexdigest()
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_path_escaping_run_directory_rejected(self):
        outside = self.run_dir.parent / "outside.png"
        outside.write_bytes(self.image_path.read_bytes())
        self.run["records"][0]["file"] = "../outside.png"
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_empty_records_or_wrong_step_rejected(self):
        original = copy.deepcopy(self.run)
        for records in ([], [dict(original["records"][0], step="04-07")], [dict(original["records"][0], error="bad action")]):
            with self.subTest(records=records):
                self.run["records"] = records
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_bad_verification_rejected_without_catalog_or_metadata(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("passed", False), ("reopened", False), ("dimensions_mm", [10, 10, 9]),
                             ("scale", [1, 1, 2]), ("unit_scale", 1), ("length_unit", "METERS"),
                             ("non_manifold_edges", 1), ("closed_volume", False), ("scene_sha256", "wrong")):
            with self.subTest(field=field):
                self.verification = dict(original, **{field: value})
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_changed_scene_rejected(self):
        self.scene.write_bytes(b"changed-after-verification")
        self.assert_rejected_cleanly()

    def test_runner_failure_or_changed_workspaces_rejected(self):
        original = copy.deepcopy(self.runner)
        for field, value in (("status", "failed"), ("blenderExitCode", 1), ("workspacesUnchanged", False),
                             ("runErrors", ["readback failed"]), ("scenario", "lesson04"),
                             ("outputDir", str(self.project)), ("endedAt", "")):
            with self.subTest(field=field):
                self.runner = dict(original, **{field: value})
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_metadata_write_failure_does_not_touch_catalog(self):
        with patch.object(IMPORTER, "_atomic_json", side_effect=OSError("metadata unavailable")):
            with self.assertRaises(OSError):
                IMPORTER.import_run(RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse(self.metadata_path.exists())

    def test_atomic_metadata_precedes_catalog(self):
        actual = IMPORTER._atomic_json
        written = []

        def record_write(path, value):
            written.append(path)
            actual(path, value)

        with patch.object(IMPORTER, "_atomic_json", side_effect=record_write):
            IMPORTER.import_run(RUN_ID, self.project)
        self.assertEqual(written, [self.metadata_path, self.catalog_path])
        self.assertEqual(list(self.catalog_path.parent.glob(".catalog.json.*.tmp")), [])


class HolePlateImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-holes-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "05" / HOLES_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.previous_pin = {"id": "05-02", "operationRun": {"id": "existing-pin-run"}}
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "05", "steps": [
            self.previous_pin, {"id": "05-03", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":9,"lessons":{"05":{"currentStep":"05-02"}}}')
        self.original_progress = self.progress.read_bytes()
        image = png_bytes()
        self.image_path = self.run_dir / "05-03-01-hole-widths.png"
        self.image_path.write_bytes(image)
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson05_holes.py",
            "records": [{
                "seq": 1, "step": "05-03", "file": self.image_path.name,
                "action": "讀回六孔尺寸", "observed": "0.1～0.6 mm 總間隙僅為草案試驗點",
                "recordedAt": "2026-10-22T08:00:00Z", "width": 3, "height": 2,
                "sha256": hashlib.sha256(image).hexdigest(), "highlights": []}]}
        self.scene = self.run_dir / "demo-files" / "u05_hole_plate_v001.blend"
        self.scene.parent.mkdir()
        self.scene.write_bytes(b"BLENDER-test-hole-plate")
        self.verification = {
            "passed": True, "kind": "hole_plate", "board_dimensions_mm": [96, 26, 4],
            "pin_nominal_mm": 10, "trial_total_clearances_mm": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            "measured_hole_widths_mm": [[10 + n / 10, 10 + n / 10] for n in range(1, 7)],
            "non_manifold_edges": 0, "through_holes": 6, "marker_counts": [1, 2, 3, 4, 5, 6],
            "scene_path": str(self.scene), "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
            "reopened": True, "printed": False, "fit_tested": False, "qualified_clearance_mm": None}
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson05_holes", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-22T07:59:00Z", "endedAt": "2026-10-22T08:01:00Z"}
        self.write_evidence()

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self, run_id=HOLES_RUN_ID):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(run_id, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (run_id + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), self.original_progress)

    def test_geometry_import_keeps_pin_and_progress_and_marks_clearances_as_unqualified(self):
        # 孔板不具有插銷專用 dimensions_mm/scale/closed_volume，必須走自己的分支。
        result = IMPORTER.import_run(HOLES_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        pin, holes = catalog["lessons"][0]["steps"]
        self.assertEqual(pin, self.previous_pin)
        operation = holes["operationRun"]
        self.assertEqual(operation["id"], HOLES_RUN_ID)
        self.assertEqual(operation["performedBy"], "tutor")
        self.assertIn("草案試驗值", operation["summary"])
        self.assertIn("尚未列印、試配", operation["summary"])
        self.assertIn("尚無合格值", holes["contentReview"]["summary"])
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(metadata["verification"], self.verification)
        self.assertEqual(metadata["runnerStatus"], self.runner)
        self.assertIn("總間隙作為試驗點", metadata["authorization"])
        self.assertEqual(metadata["numericComparison"]["meshReadbackAbsToleranceMm"], 1e-4)
        self.assertIn("不是製造公差", metadata["numericComparison"]["purpose"])
        self.assertEqual(self.progress.read_bytes(), self.original_progress)

    def test_mesh_float_readback_threshold_is_separate_from_declared_parameters(self):
        self.verification["board_dimensions_mm"] = [96.00005, 25.99995, 4.00005]
        self.verification["measured_hole_widths_mm"] = [
            [10 + n / 10 + 0.00005, 10 + n / 10 - 0.00005] for n in range(1, 7)]
        self.write_evidence()
        result = IMPORTER.import_run(HOLES_RUN_ID, self.project)
        self.assertEqual(result["steps"], 1)

    def test_mesh_readback_over_float_threshold_and_changed_design_are_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("board_dimensions_mm", [96.0002, 26, 4]),
                             ("measured_hole_widths_mm", [[10.1002, 10.1]] + original["measured_hole_widths_mm"][1:]),
                             ("trial_total_clearances_mm", [0.10005, 0.2, 0.3, 0.4, 0.5, 0.6]),
                             ("pin_nominal_mm", 10.00005)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_holes_v002_fixed_alias_has_its_own_journal(self):
        run_id = "2026-10-22-lesson05-holes-demo-v002"
        new_run_dir = self.run_dir.with_name(run_id)
        self.run_dir.rename(new_run_dir)
        self.run_dir = new_run_dir
        self.verification["scene_path"] = str(new_run_dir / "demo-files" / self.scene.name)
        self.runner["outputDir"] = str(new_run_dir)
        self.write_evidence()
        result = IMPORTER.import_run(run_id, self.project)
        self.assertEqual(result["steps"], 1)
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(catalog["lessons"][0]["steps"][1]["operationRun"]["journal"],
                         "learning/journal/2026-10-22-lesson05-holes-demo-v002.md")

    def test_bad_geometry_or_unverified_qualification_is_rejected_cleanly(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("kind", "pin"), ("passed", False), ("reopened", False),
                             ("board_dimensions_mm", [96, 26, 5]), ("pin_nominal_mm", 9),
                             ("trial_total_clearances_mm", [0.2, 0.4, 0.6]),
                             ("measured_hole_widths_mm", [[10.2, 10.2]] * 6),
                             ("measured_hole_widths_mm", [[float("nan"), 10.1]] + original["measured_hole_widths_mm"][1:]),
                             ("non_manifold_edges", 1), ("non_manifold_edges", False),
                             ("through_holes", 5), ("marker_counts", [1, 2, 3, 4, 5, True]),
                             ("printed", True), ("fit_tested", True), ("qualified_clearance_mm", 0.3),
                             ("scene_sha256", "wrong"), ("errors", ["mesh readback failed"])):
            with self.subTest(field=field, value=value):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_qualification_fields_must_be_explicit(self):
        original = copy.deepcopy(self.verification)
        for field in ("printed", "fit_tested", "qualified_clearance_mm"):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                del self.verification[field]
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_wrong_scenario_and_pin_records_do_not_enter_hole_plate_run(self):
        original_run = copy.deepcopy(self.run)
        for scope, key, value in (("runner", "scenario", "lesson05"),
                                  ("run", "scenario", "scenarios/lesson05.py"),
                                  ("record", "step", "05-02")):
            with self.subTest(scope=scope):
                self.run = copy.deepcopy(original_run)
                self.runner["scenario"] = "lesson05_holes"
                target = self.runner if scope == "runner" else self.run["records"][0] if scope == "record" else self.run
                target[key] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_changed_hole_plate_scene_is_rejected(self):
        self.scene.write_bytes(b"scene changed after readback")
        self.assert_rejected_cleanly()


class StlExportImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-stl-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "05" / EXPORT_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "05", "steps": [
            {"id": "05-04", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":9}')
        self.image = self.run_dir / "05-04-01-export.png"
        self.image.write_bytes(png_bytes())
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson05_export.py",
            "records": [{"seq": 1, "step": "05-04", "file": self.image.name, "action": "匯出 STL",
                         "observed": "只完成 STL 匯出部分", "recordedAt": "2026-10-22T09:00:00Z",
                         "width": 3, "height": 2, "sha256": hashlib.sha256(self.image.read_bytes()).hexdigest()}]}
        self.verification = {
            "passed": True, "kind": "fit_coupon_stl_exports", "exports": [],
            "printed": False, "fit_tested": False, "qualified_clearance_mm": None,
            "physical_measurements": None, "fit_results": None,
            "trial_total_clearances_mm": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            "numericComparison": {"purpose": "float reconstruction only; not manufacturing tolerance"}}
        source_specs = (
            ("pin", "2026-10-22-lesson05-demo-v002", "u05_fit_coupon_v001", "FitPin", [10, 10, 8], 0),
            ("hole_plate", "2026-10-22-lesson05-holes-demo-v002", "u05_hole_plate_v001", "Plate", [96, 26, 4], 6))
        for kind, source_run, filename, obj, dims, genus in source_specs:
            source_dir = self.run_dir.parent / source_run
            source = source_dir / "demo-files" / (filename + ".blend")
            source.parent.mkdir(parents=True)
            source.write_bytes(("BLENDER-test-" + kind).encode("ascii"))
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            (source_dir / "verification.json").write_text(json.dumps({"passed": True, "scene_sha256": sha}), encoding="utf-8")
            opened = self.run_dir / "demo-files" / "sources" / source.name
            opened.parent.mkdir(parents=True, exist_ok=True)
            opened.write_bytes(source.read_bytes())
            stl = self.run_dir / "demo-files" / "exports" / (filename + ".stl")
            stl.parent.mkdir(parents=True, exist_ok=True)
            holes = [(x, 2, 10 + n / 10) for n, x in enumerate((-35, -21, -7, 7, 21, 35), 1)] if kind == "hole_plate" else []
            data, triangles, volume = cuboid_plate_stl(*dims, holes)
            stl.write_bytes(data)
            self.verification["exports"].append({
                "kind": kind, "source_scene_path": str(source), "source_scene_sha256": sha,
                "opened_scene_path": str(opened), "opened_scene_sha256": sha,
                "source_object": obj, "source_dimensions_mm": dims, "stl_path": str(stl),
                "stl_sha256": hashlib.sha256(data).hexdigest(), "stl_bytes": len(data),
                "stl_dimensions_mm": dims, "stl_triangles": triangles, "stl_non_manifold_edges": 0,
                "stl_connected_shells": 1, "stl_genus": genus, "stl_volume_mm3": volume,
                "source_unchanged": True, "opened_copy_unchanged": True, "only_selected": True,
                "global_scale": 1.0, "use_scene_unit": False, "apply_modifiers": True,
                "forward_axis": "Y", "up_axis": "Z"})
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson05_export", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-22T08:59:00Z", "endedAt": "2026-10-22T09:01:00Z"}
        self.write_evidence()

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(EXPORT_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (EXPORT_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":9}')

    def test_valid_exports_keep_only_export_completion_scope_and_learner_progress(self):
        result = IMPORTER.import_run(EXPORT_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        operation = catalog["lessons"][0]["steps"][0]["operationRun"]
        self.assertIn("STL 匯出部分", operation["completionScope"])
        self.assertIn("尚未切片、列印或試配", operation["summary"])
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(metadata["verification"], self.verification)
        self.assertEqual(metadata["completionScope"], operation["completionScope"])
        self.assertIn("不是製造公差", metadata["numericComparison"]["purpose"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":9}')

    def test_export_v002_fixed_alias_keeps_validation_and_uses_its_own_journal(self):
        self.assert_export_alias("2026-10-22-lesson05-export-demo-v002")

    def test_export_v003_fixed_alias_keeps_validation_and_uses_its_own_journal(self):
        self.assert_export_alias("2026-10-22-lesson05-export-demo-v003")

    def assert_export_alias(self, run_id):
        old_run_dir = self.run_dir
        self.run_dir = self.run_dir.with_name(run_id)
        old_run_dir.rename(self.run_dir)
        for entry in self.verification["exports"]:
            for field in ("opened_scene_path", "stl_path"):
                entry[field] = str(self.run_dir / Path(entry[field]).relative_to(old_run_dir))
        self.runner["outputDir"] = str(self.run_dir)
        self.verification["passed"] = False
        self.write_evidence()
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(run_id, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (run_id + ".json")).exists())
        self.verification["passed"] = True
        self.write_evidence()
        result = IMPORTER.import_run(run_id, self.project)
        self.assertEqual(result["steps"], 1)
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(catalog["lessons"][0]["steps"][0]["operationRun"]["journal"],
                         "learning/journal/%s.md" % run_id)

    def test_missing_physical_status_or_claimed_fit_is_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("printed", True), ("fit_tested", True), ("qualified_clearance_mm", 0.3),
                             ("physical_measurements", []), ("fit_results", "pass"),
                             ("trial_total_clearances_mm", [0.1, 0.2]), ("numericComparison", {})):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        for field in ("printed", "fit_tested", "qualified_clearance_mm", "physical_measurements", "fit_results"):
            with self.subTest(missing=field):
                self.verification = copy.deepcopy(original)
                del self.verification[field]
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_wrong_export_options_or_false_geometry_report_is_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("source_object", "Cutters"), ("only_selected", False),
                             ("source_unchanged", False), ("opened_copy_unchanged", False),
                             ("apply_modifiers", False), ("global_scale", 1000), ("use_scene_unit", True),
                             ("forward_axis", "X"), ("up_axis", "Y"), ("stl_dimensions_mm", [10, 10, 9]),
                             ("stl_triangles", 1), ("stl_bytes", 1), ("stl_non_manifold_edges", 1),
                             ("stl_connected_shells", 2), ("stl_genus", 6), ("stl_volume_mm3", 1),
                             ("source_scene_sha256", "wrong"), ("opened_scene_sha256", "wrong")):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification["exports"][0][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_changed_source_snapshot_or_stl_is_rejected(self):
        for field in ("source_scene_path", "opened_scene_path", "stl_path"):
            with self.subTest(field=field):
                path = Path(self.verification["exports"][0][field])
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_plate_without_holes_cannot_claim_genus_six_even_with_matching_digest(self):
        plate = self.verification["exports"][1]
        data, triangles, volume = cuboid_plate_stl(96, 26, 4)
        Path(plate["stl_path"]).write_bytes(data)
        plate.update(stl_sha256=hashlib.sha256(data).hexdigest(), stl_bytes=len(data),
                     stl_triangles=triangles, stl_volume_mm3=volume)
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_stl_outside_current_exports_directory_is_rejected(self):
        entry = self.verification["exports"][0]
        outside = self.run_dir.parent / Path(entry["stl_path"]).name
        outside.write_bytes(Path(entry["stl_path"]).read_bytes())
        entry["stl_path"] = str(outside)
        self.write_evidence()
        self.assert_rejected_cleanly()


class LidGeometryImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-lid-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "05" / LID_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "05", "steps": [
            {"id": "05-05", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":12}')
        self.image = self.run_dir / "05-05-01-lid.png"
        self.image.write_bytes(png_bytes())
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson05_lid.py",
            "records": [{"seq": 1, "step": "05-05", "file": self.image.name, "action": "製作蓋子試驗幾何",
                         "observed": "蓋板 2 mm，含定位環整體高度 6 mm；未列印、未試配",
                         "recordedAt": "2026-10-22T10:00:00Z", "width": 3, "height": 2,
                         "sha256": hashlib.sha256(self.image.read_bytes()).hexdigest()}]}
        self.source = self.project / "learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-original-box")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[LID_RUN_ID]["source_scene_sha256"]
        patched_hash = patch.dict(IMPORTER.RUNS[LID_RUN_ID], {"source_scene_sha256": source_hash})
        patched_hash.start()
        self.addCleanup(patched_hash.stop)
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u05_lid_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-body-and-one-piece-lid")
        common = {
            "passed": True, "scale": [1, 1, 1], "unit_scale": 0.001, "length_unit": "MILLIMETERS",
            "mesh_counts": {"vertices": 16, "edges": 42, "faces": 28, "triangles": 28},
            "non_manifold_edges": 0, "non_manifold_vertex_links": 0, "inconsistent_winding_edges": 0,
            "connected_shells": 1, "euler_characteristic": 2, "genus": 0,
            "printed": False, "fit_tested": False, "physical_interference": None, "qualified_clearance_mm": None}
        body = dict(copy.deepcopy(common), kind="box_body", object_name="Body", dimensions_mm=[60, 40, 30],
                    outer_dimensions_mm=[60, 40, 30], cavity_dimensions_mm=[56, 36, 28],
                    wall_thicknesses_mm=[2, 2, 2, 2], floor_thickness_mm=2, rim_z_mm=15, volume_mm3=15552)
        lid = dict(copy.deepcopy(common), kind="lid", object_name="Lid", dimensions_mm=[60, 40, 6],
                   plate_dimensions_mm=[60, 40, 2], plate_thickness_mm=2, plate_z_mm=[15, 17],
                   ring_outer_mm=[55.6, 35.6], ring_inner_mm=[51.6, 31.6], ring_z_mm=[11, 15],
                   ring_wall_mm=2, ring_wall_thicknesses_mm=[2, 2, 2, 2], ring_depth_mm=4, engagement_mm=4,
                   volume_mm3=6195.2, trial_status="experimental_geometry_only", trial_total_clearance_mm=0.4,
                   trial_per_side_clearance_mm=0.2,
                   assembly={"geometric_nonintersection": True, "interior_volume_overlap_mm3": 0,
                             "per_side_clearances_mm": [0.2, 0.2, 0.2, 0.2], "total_clearances_mm": [0.4, 0.4],
                             "engagement_mm": 4, "cavity_depth_mm": 28, "floor_reserve_mm": 24,
                             "rim_contact_z_mm": 15, "printed": False, "fit_tested": False,
                             "physical_interference": None, "qualified_clearance_mm": None})
        self.verification = {
            "passed": True, "kind": "lid_geometry_demo", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True, "scene_path": str(self.scene),
            "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(), "reopened": True,
            "body": body, "lid": lid, "trial": {"status": "experimental_geometry_only", "total_clearance_mm": 0.4,
                                               "per_side_clearance_mm": 0.2, "qualified_clearance_mm": None},
            "printed": False, "fit_tested": False, "physical_measurements": None, "fit_results": None,
            "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "purpose": "Floating point only; not manufacturing tolerance"}}
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson05_lid", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-22T09:59:00Z", "endedAt": "2026-10-22T10:01:00Z"}
        self.write_evidence()

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(LID_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (LID_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":12}')

    def test_valid_lid_records_geometry_only_plate_thickness_and_unchanged_progress(self):
        self.assertEqual(self.production_source_hash,
                         "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530")
        result = IMPORTER.import_run(LID_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        operation = catalog["lessons"][0]["steps"][0]["operationRun"]
        self.assertIn("蓋板本身厚 2 mm", operation["summary"])
        self.assertIn("整個蓋子高 6 mm", operation["summary"])
        self.assertIn("助教選用", operation["summary"])
        self.assertIn("尚未列印或試配", operation["summary"])
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(metadata["verification"], self.verification)
        self.assertIn("不是製造公差", metadata["numericComparison"]["purpose"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":12}')

    def test_changed_source_snapshot_or_output_is_rejected(self):
        for path in (self.source, self.opened, self.scene):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_wrong_body_lid_empty_or_disconnected_mesh_is_rejected(self):
        original = copy.deepcopy(self.verification)
        cases = [("body", "outer_dimensions_mm", [60, 40, 31]),
                 ("body", "cavity_dimensions_mm", [56, 36, 26]),
                 ("body", "wall_thicknesses_mm", [2, 2, 2, 1]),
                 ("body", "floor_thickness_mm", 1), ("body", "volume_mm3", 1),
                 ("lid", "plate_dimensions_mm", [60, 40, 6]), ("lid", "dimensions_mm", [60, 40, 2]),
                 ("lid", "ring_outer_mm", [56, 36]), ("lid", "ring_inner_mm", [0, 0]),
                 ("lid", "ring_z_mm", [10, 15]), ("lid", "engagement_mm", 5),
                 ("lid", "ring_wall_thicknesses_mm", [2, 2, 2, 1]),
                 ("lid", "mesh_counts", {"vertices": 0, "edges": 0, "faces": 0, "triangles": 0}),
                 ("lid", "connected_shells", 2), ("lid", "non_manifold_edges", 1),
                 ("lid", "inconsistent_winding_edges", 1), ("lid", "object_name", "Body"),
                 ("lid", "passed", False), ("lid", "unit_scale", 1), ("lid", "scale", [1, 1, 3])]
        for label, field, value in cases:
            with self.subTest(label=label, field=field):
                self.verification = copy.deepcopy(original)
                self.verification[label][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_false_trial_or_physical_result_is_rejected_at_each_scope(self):
        original = copy.deepcopy(self.verification)
        cases = [((), "printed", True), ((), "fit_tested", True), ((), "physical_measurements", []),
                 ((), "fit_results", "pass"), ((), "qualified_clearance_mm", 0.4),
                 (("trial",), "status", "qualified"), (("trial",), "total_clearance_mm", 0.2),
                 (("trial",), "per_side_clearance_mm", 0.4), (("trial",), "qualified_clearance_mm", 0.4),
                 (("lid",), "printed", True), (("lid",), "qualified_clearance_mm", 0.4),
                 (("lid",), "trial_status", "qualified"),
                 (("lid", "assembly"), "geometric_nonintersection", False),
                 (("lid", "assembly"), "interior_volume_overlap_mm3", 1),
                 (("lid", "assembly"), "per_side_clearances_mm", [0.2, 0.2, 0.4, 0]),
                 (("lid", "assembly"), "fit_tested", True)]
        for path, field, value in cases:
            with self.subTest(path=path, field=field):
                self.verification = copy.deepcopy(original)
                target = self.verification
                for component in path:
                    target = target[component]
                target[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_missing_explicit_physical_status_or_reopen_is_rejected(self):
        original = copy.deepcopy(self.verification)
        for field in ("printed", "fit_tested", "qualified_clearance_mm", "physical_measurements", "fit_results",
                      "reopened", "source_unchanged", "opened_copy_unchanged"):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                del self.verification[field]
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_wrong_scenario_or_non_png_visual_evidence_is_rejected(self):
        self.runner["scenario"] = "lesson05_holes"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.runner["scenario"] = "lesson05_lid"
        self.write_evidence()
        self.image.write_bytes(b"not an actual PNG")
        self.assert_rejected_cleanly()


class LidStlExportImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-lid-stl-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "05" / LID_EXPORT_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "05", "steps": [
            {"id": "05-06", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":15}')
        image = self.run_dir / "05-06-01-lid-export.png"
        image.write_bytes(png_bytes())
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson05_lid_export.py",
            "records": [{"seq": 1, "step": "05-06", "file": image.name, "action": "只選蓋子匯出並重新匯入",
                         "observed": "World Z 11～17 mm，蓋板厚 2 mm；尚未切片、列印、試配",
                         "recordedAt": "2026-10-25T10:00:00Z", "width": 3, "height": 2,
                         "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_path = Path(__file__).with_name("test_lid_checks.py")
        fixture_spec = importlib.util.spec_from_file_location("lid_export_import_fixtures", fixture_path)
        self.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.fixture)
        self.vertices, self.triangles = self.fixture.lid_fixture()
        body = self.fixture.checks.validate_body_mesh(*self.fixture.body_fixture())
        lid = self.fixture.checks.validate_lid_mesh(self.vertices, self.triangles, body)
        for record, name in ((body, "Body"), (lid, "Lid")):
            record.update(object_name=name, scale=[1, 1, 1], unit_scale=0.001, length_unit="MILLIMETERS")
        self.source = self.run_dir.parent / LID_RUN_ID / "demo-files" / "u05_lid_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-saved-lid-source")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[LID_EXPORT_RUN_ID]["source_scene_sha256"]
        patched_hash = patch.dict(IMPORTER.RUNS[LID_EXPORT_RUN_ID], {"source_scene_sha256": source_hash})
        patched_hash.start()
        self.addCleanup(patched_hash.stop)
        self.source_metadata = {"passed": True, "kind": "lid_geometry_demo", "scene_path": str(self.source),
                                "scene_sha256": source_hash, "body": body, "lid": lid}
        self.source_verification = self.source.parent.parent / "verification.json"
        self.source_verification.write_text(json.dumps(self.source_metadata), encoding="utf-8")
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.stl = self.run_dir / "demo-files" / "exports" / "u05_lid_v001.stl"
        self.stl.parent.mkdir()
        self.stl.write_bytes(self.binary_stl(self.vertices, self.triangles))
        scenarios = str(MODULE_PATH.parent / "scenarios")
        sys.path.insert(0, scenarios)
        try:
            from lid_stl_checks import validate_lid_stl
            detailed = validate_lid_stl(self.stl, {"passed": True, "body": body, "lid": lid})
        finally:
            sys.path.pop(0)
        self.verification = {
            "passed": True, "kind": "lid_stl_export", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened),
            "opened_scene_sha256": source_hash, "source_unchanged": True, "opened_copy_unchanged": True,
            "source_object": "Lid", "source_lid": copy.deepcopy(lid), "source_body": copy.deepcopy(body),
            "stl_path": str(self.stl), "stl_sha256": hashlib.sha256(self.stl.read_bytes()).hexdigest(),
            "stl_bytes": self.stl.stat().st_size, "stl_dimensions_mm": [60, 40, 6],
            "stl_triangles": len(self.triangles), "stl_non_manifold_edges": 0,
            "stl_connected_shells": 1, "stl_genus": 0, "stl_volume_mm3": detailed["volume_mm3"],
            "stl_verification": detailed, "only_selected": True, "global_scale": 1,
            "use_scene_unit": False, "apply_modifiers": True, "forward_axis": "Y", "up_axis": "Z",
            "ascii_format": False, "use_batch": False, "reimport_verified": True,
            "reimport_lid": dict(copy.deepcopy(lid), object_name="ImportedLid"),
            "trial_total_clearance_mm": 0.4, "trial_per_side_clearance_mm": 0.2,
            "trial_status": "experimental_geometry_only", "printed": False, "fit_tested": False,
            "physical_measurements": None, "fit_results": None, "qualified_clearance_mm": None,
            "slicer_checked": False, "numericComparison": {"dimensionsAbsMm": 1e-4, "purpose": "Floating point only"}}
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson05_lid_export", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-25T09:59:00Z", "endedAt": "2026-10-25T10:01:00Z"}
        self.write_evidence()

    @staticmethod
    def binary_stl(vertices, triangles):
        data = bytearray(b"lid STL importer test".ljust(80, b"\0") + struct.pack("<I", len(triangles)))
        for triangle in triangles:
            data.extend(struct.pack("<12fH", 0, 0, 0,
                                    *(value for index in triangle for value in vertices[index]), 0))
        return bytes(data)

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(LID_EXPORT_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (LID_EXPORT_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":15}')

    def test_valid_lid_export_and_named_reimport_keep_cad_only_scope_and_progress(self):
        self.assertEqual(self.production_source_hash,
                         "ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff")
        result = IMPORTER.import_run(LID_EXPORT_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        operation = json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]
        self.assertIn("STL 匯出與 CAD 讀回", operation["completionScope"])
        self.assertIn("尚未切片、列印或試配", operation["summary"])
        self.assertIn("蓋板厚 2 mm", operation["summary"])
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(metadata["verification"], self.verification)
        self.assertEqual(self.progress.read_bytes(), b'{"revision":15}')

    def test_wrong_selection_options_or_unverified_stage_claims_are_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("source_object", "Body"), ("only_selected", False), ("ascii_format", True),
                             ("use_batch", True), ("use_scene_unit", True), ("global_scale", 1000),
                             ("reimport_verified", False), ("printed", True), ("fit_tested", True),
                             ("slicer_checked", True), ("qualified_clearance_mm", 0.4),
                             ("physical_measurements", []), ("fit_results", "pass"),
                             ("trial_status", "qualified"), ("trial_per_side_clearance_mm", 0.4)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_null_nested_stl_provenance_does_not_relax_the_pinned_top_level_source(self):
        self.assertIsNone(self.verification["stl_verification"]["source_scene_path"])
        self.assertIsNone(self.verification["stl_verification"]["source_scene_sha256"])
        self.verification["source_scene_sha256"] = "0" * 64
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_changed_original_source_copy_stl_or_original_checkpoint_digest_is_rejected(self):
        for path in (self.source, self.opened, self.stl):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)
        self.source_metadata["scene_sha256"] = "wrong"
        self.source_verification.write_text(json.dumps(self.source_metadata), encoding="utf-8")
        self.assert_rejected_cleanly()

    def test_wrong_mesh_readback_or_details_cannot_claim_valid_lid(self):
        original = copy.deepcopy(self.verification)
        for path, field, value in ((("source_lid",), "plate_dimensions_mm", [60, 40, 6]),
                                  (("source_body",), "cavity_dimensions_mm", [60, 40, 30]),
                                  (("reimport_lid",), "ring_inner_mm", [0, 0]),
                                  (("reimport_lid",), "connected_shells", 2),
                                  (("reimport_lid",), "object_name", ""),
                                  (("stl_verification", "lid_geometry"), "ring_z_mm", [0, 4]),
                                  (("stl_verification",), "printed", True)):
            with self.subTest(path=path, field=field):
                self.verification = copy.deepcopy(original)
                target = self.verification
                for key in path:
                    target = target[key]
                target[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_stl_with_shifted_world_z_does_not_pass_by_dimensions_and_hash(self):
        shifted = [(x, y, z - 11) for x, y, z in self.vertices]
        self.stl.write_bytes(self.binary_stl(shifted, self.triangles))
        self.verification["stl_sha256"] = hashlib.sha256(self.stl.read_bytes()).hexdigest()
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_wrong_scenario_or_wrong_step_is_rejected(self):
        self.runner["scenario"] = "lesson05_lid"
        self.write_evidence()
        self.assert_rejected_cleanly()


class TenonGeometryImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-tenon-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "06" / TENON_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "06", "steps": [
            {"id": "06-01", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "06-01-01-tenon.png"
        image.write_bytes(png_bytes())
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson06_tenon.py",
            "records": [{"seq": 1, "step": "06-01", "file": image.name, "action": "建立一體定位柱及對應穿孔",
                         "observed": "盒殼高 30 mm；含柱整高 31.5 mm；尚無實體配合結果",
                         "recordedAt": "2026-10-25T11:00:00Z", "width": 3, "height": 2,
                         "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_path = Path(__file__).with_name("test_tenon_checks.py")
        fixture_spec = importlib.util.spec_from_file_location("tenon_import_fixtures", fixture_path)
        self.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.fixture)
        self.checks = self.fixture.checks
        prior = self.fixture.source_fixture()
        for record, name, location in ((prior["body"], "Body", [0, 0, 0]), (prior["lid"], "Lid", [0, 0, 16])):
            record.update(self.cad(name, location))
        self.source = self.project / "learning" / "evidence" / "05" / LID_RUN_ID / "demo-files" / "u05_lid_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-fixed-body-and-lid-source")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[TENON_RUN_ID]["source_scene_sha256"]
        patched_hash = patch.dict(IMPORTER.RUNS[TENON_RUN_ID], {"source_scene_sha256": source_hash})
        patched_hash.start()
        self.addCleanup(patched_hash.stop)
        prior.update(kind="lid_geometry_demo", scene_path=str(self.source), scene_sha256=source_hash)
        self.source_metadata = prior
        self.source_verification = self.source.parent.parent / "verification.json"
        self.source_verification.write_text(json.dumps(prior), encoding="utf-8")
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u06_locating_tenon_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-new-integral-pin-and-hole-scene")

        self.meshes = {}
        for role, name, location, values in (
                ("construction_pin", "TenonTool", [23, 13, 1.5], self.fixture.tool_fixture("pin")),
                ("construction_cutter", "HoleTool", [23, 13, 16], self.fixture.tool_fixture("hole_cutter")),
                ("body", "Body", [0, 0, 0], self.fixture.body_pin_fixture()),
                ("lid", "Lid", [0, 0, 16], self.fixture.lid_hole_fixture())):
            self.meshes[role] = {"vertices": values[0], "triangles": values[1], "cad_metadata": self.cad(name, location)}
        pin = self.with_cad(self.checks.validate_tool_mesh(*self.geometry("construction_pin"), "pin"), "construction_pin")
        cutter = self.with_cad(self.checks.validate_tool_mesh(*self.geometry("construction_cutter"), "hole_cutter"), "construction_cutter")
        body = self.with_cad(self.checks.validate_body_pin_mesh(*self.geometry("body"), prior["body"], pin), "body")
        lid = self.with_cad(self.checks.validate_lid_hole_mesh(*self.geometry("lid"), prior["lid"]), "lid")
        assembly = self.checks.validate_tenon_assembly(body, lid)
        objects = {name: {"object_name": name, "type": "MESH", "modifier_count": 0, "scale": [1, 1, 1],
                          "hidden": name in ("TenonTool", "HoleTool")} for name in ("Body", "Lid", "TenonTool", "HoleTool")}
        self.verification = {
            "passed": True, "kind": "locating_tenon_geometry_demo", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True, "source_body": prior["body"], "source_lid": prior["lid"],
            "scene_path": str(self.scene), "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
            "scene_bytes": self.scene.stat().st_size, "reopened": True, "construction_pin": pin, "construction_cutter": cutter,
            "body": body, "lid": lid, "assembly": assembly, "final_objects": objects,
            "trial": {"status": "experimental_geometry_only", "selected_by": "tutor", "diameter_total_clearance_mm": 0.4,
                      "nominal_radial_clearance_mm": 0.2, "qualified_clearance_mm": None},
            "exported_stl": False, "slicer_checked": False, "printed": False, "fit_tested": False,
            "physical_measurements": None, "fit_results": None, "physical_interference": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "volumeRelative": 1e-5, "purpose": "Floating point only"}}
        self.runner = {
            "status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson06_tenon", "outputDir": str(self.run_dir),
            "startedAt": "2026-10-25T10:59:00Z", "endedAt": "2026-10-25T11:01:00Z"}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson06_tenon.py", "learning/tutor/scenarios/tenon_checks.py",
                   "learning/tutor/scenarios/lid_checks.py", "learning/tutor/scenarios/stl_checks.py")
        records = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            records.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        self.snapshot_manifest = {"recordedAt": "2026-10-25T10:59:00Z", "files": records,
                                  "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": source_hash}
        self.write_evidence()

    @staticmethod
    def cad(name, location):
        return {"object_name": name, "scale": [1, 1, 1], "unit_scale": 0.001, "length_unit": "MILLIMETERS",
                "modifier_count": 0, "object_location_mm": location}

    def geometry(self, role):
        return self.meshes[role]["vertices"], self.meshes[role]["triangles"]

    def with_cad(self, result, role):
        return dict(result, **self.meshes[role]["cad_metadata"])

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner), ("source-snapshot/manifest.json", self.snapshot_manifest)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        names = {"body": "body_mesh.json", "lid": "lid_mesh.json", "construction_pin": "pin_tool_mesh.json",
                 "construction_cutter": "hole_tool_mesh.json"}
        for role, name in names.items():
            (self.run_dir / name).write_text(json.dumps(self.meshes[role]), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(TENON_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (TENON_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_geometry_pins_four_mesh_dumps_snapshots_and_does_not_confirm(self):
        self.assertEqual(self.production_source_hash,
                         "ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff")
        result = IMPORTER.import_run(TENON_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 4)
        for item in metadata["geometryEvidence"]:
            self.assertEqual(item["sha256"], hashlib.sha256((self.project / item["path"]).read_bytes()).hexdigest())
        self.assertIn("source-snapshot/manifest.json", metadata["sourceSnapshotEvidence"]["path"])
        operation = json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]
        self.assertIn("盒殼仍高 30 mm", operation["summary"])
        self.assertIn("Body 整高 31.5 mm", operation["summary"])
        self.assertIn("尚未匯出 STL、切片、列印或試配", operation["summary"])
        self.assertEqual(self.verification["body"]["genus"], 0)
        self.assertEqual(self.verification["lid"]["genus"], 1)
        self.assertLess(self.verification["assembly"]["min_normal_gap_mm"], 0.2)
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_tenon_v002_fixed_alias_requires_complete_proof_and_uses_its_own_journal(self):
        self.assert_tenon_alias("2026-10-25-lesson06-tenon-demo-v002")

    def test_tenon_v003_fixed_alias_requires_complete_proof_and_uses_its_own_journal(self):
        self.assert_tenon_alias("2026-10-25-lesson06-tenon-demo-v003")

    def test_tenon_v004_fixed_alias_requires_complete_proof_and_uses_its_own_journal(self):
        self.assert_tenon_alias("2026-10-25-lesson06-tenon-demo-v004")

    def test_tenon_v005_fixed_alias_requires_complete_proof_and_uses_its_own_journal(self):
        self.assert_tenon_alias("2026-10-25-lesson06-tenon-demo-v005")

    def test_tenon_v006_fixed_alias_requires_complete_proof_and_uses_its_own_journal(self):
        self.assert_tenon_alias("2026-10-25-lesson06-tenon-demo-v006")

    def assert_tenon_alias(self, run_id):
        previous_dir = self.run_dir
        self.run_dir = self.run_dir.with_name(run_id)
        previous_dir.rename(self.run_dir)
        self.opened = self.run_dir / "demo-files" / "sources" / "u05_lid_v001.blend"
        self.scene = self.run_dir / "demo-files" / "u06_locating_tenon_v001.blend"
        self.verification["opened_scene_path"] = str(self.opened)
        self.verification["scene_path"] = str(self.scene)
        self.snapshot_manifest["sourceCopy"] = str(self.opened)
        self.runner["outputDir"] = str(self.run_dir)
        patched_hash = patch.dict(IMPORTER.RUNS[run_id], {"source_scene_sha256": self.verification["source_scene_sha256"]})
        with patched_hash:
            self.verification["passed"] = False
            self.write_evidence()
            with self.assertRaises(IMPORTER.ImportValidationError):
                IMPORTER.import_run(run_id, self.project)
            self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
            self.assertFalse((self.run_dir.parent / (run_id + ".json")).exists())
            self.verification["passed"] = True
            self.write_evidence()
            result = IMPORTER.import_run(run_id, self.project)
        self.assertEqual(result["steps"], 1)
        operation = json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]
        self.assertEqual(operation["journal"], "learning/journal/%s.md" % run_id)
        self.assertEqual(operation["id"], run_id)
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_wrong_nominal_physical_scope_or_reopen_is_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("exported_stl", True), ("slicer_checked", True), ("printed", True),
                             ("fit_tested", True), ("physical_measurements", []), ("fit_results", "pass"),
                             ("physical_interference", False), ("qualified_clearance_mm", 0.4),
                             ("source_body_geometry_unchanged", True), ("scene_bytes", 1), ("reopened", False)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["trial"]["selected_by"] = "learner"
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_modified_original_copy_or_new_scene_is_rejected(self):
        for path in (self.source, self.opened, self.scene):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_old_shell_height_or_nominal_gap_cannot_replace_measured_values(self):
        original = copy.deepcopy(self.verification)
        for path, field, value in ((("body",), "dimensions_mm", [60.0, 40.0, 30.0]),
                                  (("body", "pin"), "exposed_z_mm", [-13.5, 16.5]),
                                  (("lid",), "genus", 0), (("lid",), "euler_characteristic", 2),
                                  (("assembly",), "min_normal_gap_mm", 0.2),
                                  (("assembly",), "across_flats_total_clearance_mm", 0.4),
                                  (("construction_pin",), "height_mm", 29.5)):
            with self.subTest(path=path, field=field):
                self.verification = copy.deepcopy(original)
                target = self.verification
                for part in path:
                    target = target[part]
                target[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_actual_mesh_without_hole_is_rejected_even_when_report_claims_genus_one(self):
        self.meshes["lid"]["vertices"], self.meshes["lid"]["triangles"] = self.fixture.old.lid_fixture()
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_unfused_pin_and_changed_tool_dump_cannot_pass_by_unchanged_bounds(self):
        original = copy.deepcopy(self.meshes)
        body_vertices, body_triangles = self.fixture.old.body_fixture()
        pin_vertices, pin_triangles = self.fixture.tool_fixture("pin")
        self.meshes["body"]["vertices"] = body_vertices + pin_vertices
        self.meshes["body"]["triangles"] = body_triangles + [tuple(i + len(body_vertices) for i in tri) for tri in pin_triangles]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["construction_cutter"]["vertices"] = [(x, y, z + 1) for x, y, z in self.meshes["construction_cutter"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_hidden_tools_and_applied_final_meshes_are_required(self):
        original = copy.deepcopy(self.verification)
        for name, field, value in (("TenonTool", "hidden", False), ("HoleTool", "hidden", False),
                                  ("Body", "hidden", True), ("Body", "modifier_count", 1),
                                  ("Lid", "scale", [1, 1, 2])):
            with self.subTest(name=name, field=field):
                self.verification = copy.deepcopy(original)
                self.verification["final_objects"][name][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_snapshot_dependencies_and_snapshot_integrity_are_required(self):
        original = copy.deepcopy(self.snapshot_manifest)
        for script in ("lid_checks.py", "stl_checks.py"):
            with self.subTest(missing=script):
                self.snapshot_manifest = copy.deepcopy(original)
                self.snapshot_manifest["files"] = [item for item in self.snapshot_manifest["files"] if not item["source"].endswith(script)]
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.snapshot_manifest = copy.deepcopy(original)
        self.write_evidence()
        (self.run_dir / "source-snapshot" / "tenon_checks.py").write_bytes(b"changed snapshot")
        self.assert_rejected_cleanly()

    def test_dimension_comparison_has_no_implicit_relative_tolerance(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER._readback_subset_matches({"dimensions_mm": [60.0005]}, {"dimensions_mm": [60.0]}, "尺寸")
        IMPORTER._readback_subset_matches({"volume_mm3": 15552.01}, {"volume_mm3": 15552.0}, "浮點體積")
        self.runner["scenario"] = "lesson05_lid_export"
        self.run["records"][0]["step"] = "05-05"
        self.write_evidence()
        self.assert_rejected_cleanly()


class DovetailGeometryImportTests(unittest.TestCase):
    """Independent closed-mesh fixtures exercise the complete import boundary."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-dovetail-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "06" / DOVETAIL_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "06", "steps": [
            {"id": "06-02", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "06-02-01-dovetail.png"
        image.write_bytes(png_bytes())
        self.run = {
            "blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson06_dovetail.py",
            "records": [{"seq": 1, "step": "06-02", "file": image.name, "action": "建立燕尾滑蓋並讀回數位行程",
                         "observed": "水平間距與斜面法向間距分開；尚未做 Overhang 介面分析或實體試配",
                         "recordedAt": "2026-10-25T12:00:00Z", "width": 3, "height": 2,
                         "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_path = Path(__file__).with_name("test_dovetail_checks.py")
        fixture_spec = importlib.util.spec_from_file_location("dovetail_import_fixtures", fixture_path)
        self.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.fixture)
        self.checks = self.fixture.checks
        from lid_checks import validate_body_mesh as validate_source_body

        self.source = (self.project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001"
                       / "demo-files" / "u04_box_v001.blend")
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-fixed-original04-box-source")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[DOVETAIL_RUN_ID]["source_scene_sha256"]
        patched_hash = patch.dict(IMPORTER.RUNS[DOVETAIL_RUN_ID], {"source_scene_sha256": source_hash})
        patched_hash.start()
        self.addCleanup(patched_hash.stop)
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u06_dovetail_slide_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-new-dovetail-body-and-sliding-lid-scene")
        self.meshes = {}
        for role, name, location, values in (
                ("source_body", "Cube", [0, 0, 0], self.fixture.source_fixture()),
                ("construction_guides", "GuideTool", [0, 17, 12.5], self.fixture.tool_fixture("guide")),
                ("construction_grooves", "GrooveTool", [0, 17, 13.8], self.fixture.tool_fixture("groove")),
                ("construction_males", "MaleTool", [0, 17, 13.7], self.fixture.tool_fixture("male")),
                ("body", "Body", [0, 0, 0], self.fixture.body_fixture()),
                ("lid", "SlidingLid", [0, 0, 16.2], self.fixture.lid_fixture())):
            self.meshes[role] = {"vertices": values[0], "triangles": values[1],
                                 "cad_metadata": TenonGeometryImportTests.cad(name, location)}
        for distance in (30, 62):
            moved = copy.deepcopy(self.meshes["lid"])
            moved["vertices"] = [(x + distance, y, z) for x, y, z in moved["vertices"]]
            moved["cad_metadata"]["object_location_mm"][0] += distance
            self.meshes["travel_%d" % distance] = moved
        source_body = validate_source_body(*self.geometry("source_body"))
        source_body.update({key: self.meshes["source_body"]["cad_metadata"][key]
                            for key in ("object_name", "scale", "unit_scale", "length_unit")})
        guides = self.checks.validate_tool_mesh(*self.geometry("construction_guides"), "guide")
        grooves = self.checks.validate_tool_mesh(*self.geometry("construction_grooves"), "groove")
        males = self.checks.validate_tool_mesh(*self.geometry("construction_males"), "male")
        body = self.checks.validate_body_mesh(*self.geometry("body"))
        lid = self.checks.validate_lid_mesh(*self.geometry("lid"))
        assembly = self.checks.validate_assembly(body, lid)
        travel = self.checks.validate_travel(body, lid, {str(d): self.meshes["travel_%d" % d] for d in (30, 62)})
        objects = {name: {"object_name": name, "type": "MESH", "modifier_count": 0, "scale": [1, 1, 1],
                          "hidden": name.endswith("Tool")}
                   for name in ("Body", "SlidingLid", "GuideTool", "GrooveTool", "MaleTool")}
        self.verification = {
            "passed": True, "kind": "dovetail_slide_geometry_demo", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True, "source_body": source_body,
            "scene_path": str(self.scene), "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
            "scene_bytes": self.scene.stat().st_size, "reopened": True, "construction_guides": guides,
            "construction_grooves": grooves, "construction_males": males, "body": body, "lid": lid,
            "assembly": assembly, "travel": travel, "final_objects": objects,
            "trial": {"status": "experimental_geometry_only", "selected_by": "tutor", "horizontal_total_clearance_mm": 0.4,
                      "horizontal_side_clearance_mm": 0.2, "qualified_clearance_mm": None},
            "mesh_analysis_overhang_checked": False, "exported_stl": False, "slicer_checked": False,
            "printed": False, "fit_tested": False, "physical_measurements": None, "fit_results": None,
            "physical_interference": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "volumeRelative": 1e-5,
                                  "purpose": "Floating point only; not manufacturing tolerance"}}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
                       "scenario": "lesson06_dovetail", "outputDir": str(self.run_dir),
                       "startedAt": "2026-10-25T11:59:00Z", "endedAt": "2026-10-25T12:01:00Z"}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson06_dovetail.py", "learning/tutor/scenarios/lid_checks.py",
                   "learning/tutor/scenarios/stl_checks.py", "learning/tutor/scenarios/tenon_checks.py",
                   "learning/tutor/scenarios/dovetail_checks.py")
        records = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            records.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        self.snapshot_manifest = {"recordedAt": "2026-10-25T11:59:00Z", "files": records,
                                  "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": source_hash}
        self.write_evidence()

    def geometry(self, role):
        return self.meshes[role]["vertices"], self.meshes[role]["triangles"]

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner), ("source-snapshot/manifest.json", self.snapshot_manifest)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        files = {"source_body": "source_body_mesh.json", "construction_guides": "guide_tool_mesh.json",
                 "construction_grooves": "groove_tool_mesh.json", "construction_males": "male_tool_mesh.json",
                 "body": "body_mesh.json", "lid": "lid_mesh.json", "travel_30": "travel_30_lid_mesh.json",
                 "travel_62": "travel_62_lid_mesh.json"}
        for role, name in files.items():
            (self.run_dir / name).write_text(json.dumps(self.meshes[role]), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(DOVETAIL_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (DOVETAIL_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_source04_branch_recomputes_eight_meshes_without_confirm_or_old_verification(self):
        self.assertEqual(self.production_source_hash,
                         "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530")
        self.assertFalse((self.source.parent.parent / "verification.json").exists())
        result = IMPORTER.import_run(DOVETAIL_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 8)
        for item in metadata["geometryEvidence"]:
            self.assertEqual(item["sha256"], hashlib.sha256((self.project / item["path"]).read_bytes()).hexdigest())
        self.assertIn("source-snapshot/manifest.json", metadata["sourceSnapshotEvidence"]["path"])
        operation = json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]
        self.assertIn("Overhang", operation["summary"])
        self.assertIn("斜面法向實際間距分開", operation["summary"])
        self.assertIn("尚未完成", metadata["completionScope"])
        self.assertEqual(self.verification["construction_grooves"]["connected_shells"], 2)
        self.assertEqual(self.verification["body"]["connected_shells"], 1)
        self.assertLess(self.verification["assembly"]["normal_side_gap_mm"], 0.2)
        self.assertTrue(self.verification["travel"]["states"][2]["fully_disengaged"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_unperformed_stages_physical_results_and_changed_body_claim_are_rejected(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("mesh_analysis_overhang_checked", True), ("exported_stl", True), ("slicer_checked", True),
                             ("printed", True), ("fit_tested", True), ("physical_measurements", []), ("fit_results", "pass"),
                             ("physical_interference", False), ("qualified_clearance_mm", 0.4),
                             ("source_body_geometry_unchanged", True), ("reopened", False), ("scene_bytes", 1)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_v002_alias_requires_complete_proof_and_uses_its_own_journal(self):
        run_id = "2026-10-25-lesson06-dovetail-demo-v002"
        previous_dir = self.run_dir
        self.run_dir = self.run_dir.with_name(run_id)
        previous_dir.rename(self.run_dir)
        self.opened = self.run_dir / "demo-files" / "sources" / "u04_box_v001.blend"
        self.scene = self.run_dir / "demo-files" / "u06_dovetail_slide_v001.blend"
        self.verification["opened_scene_path"] = str(self.opened)
        self.verification["scene_path"] = str(self.scene)
        self.snapshot_manifest["sourceCopy"] = str(self.opened)
        self.runner["outputDir"] = str(self.run_dir)
        with patch.dict(IMPORTER.RUNS[run_id], {"source_scene_sha256": self.verification["source_scene_sha256"]}):
            self.verification["passed"] = False
            self.write_evidence()
            with self.assertRaises(IMPORTER.ImportValidationError):
                IMPORTER.import_run(run_id, self.project)
            self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
            self.assertFalse((self.run_dir.parent / (run_id + ".json")).exists())
            self.verification["passed"] = True
            self.write_evidence()
            result = IMPORTER.import_run(run_id, self.project)
        self.assertEqual(result["steps"], 1)
        operation = json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]
        self.assertEqual(operation["journal"], "learning/journal/%s.md" % run_id)
        self.assertEqual(operation["id"], run_id)
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_trial_must_be_tutor_selected_horizontal_experiment(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("status", "qualified"), ("selected_by", "learner"),
                             ("horizontal_side_clearance_mm", 0.196116), ("horizontal_total_clearance_mm", 0.2),
                             ("qualified_clearance_mm", 0.4)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification["trial"][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_modified_source_copy_or_saved_scene_cannot_pass_the_recorded_hashes(self):
        for path in (self.source, self.opened, self.scene):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b" changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_renamed_source_copy_cannot_be_claimed_as_a_new_geometry_scene(self):
        self.scene.write_bytes(self.source.read_bytes())
        self.verification.update(scene_sha256=hashlib.sha256(self.scene.read_bytes()).hexdigest(),
                                 scene_bytes=self.scene.stat().st_size)
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_fixed_source_path_and_reported_hash_remain_required(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("source_scene_path", str(self.opened)), ("source_scene_sha256", "0" * 64),
                             ("opened_scene_path", str(self.source)), ("opened_scene_sha256", "0" * 64)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_measured_clipped_profiles_cannot_be_replaced_with_tool_depths_or_nominal_gaps(self):
        original = copy.deepcopy(self.verification)
        changes = (("body", "local_cavity_width_mm", 36), ("lid", "dimensions_mm", [60, 40, 5.4]),
                   ("lid", "exposed_male_depth_mm", 3.4), ("assembly", "normal_side_gap_mm", 0.2),
                   ("assembly", "horizontal_side_gap_mm", 0.196116), ("body", "channel_floor_web_mm", 2),
                   ("construction_grooves", "connected_shells", 1))
        for role, field, value in changes:
            with self.subTest(role=role, field=field):
                self.verification = copy.deepcopy(original)
                self.verification[role][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["body"]["channels"][0]["profile"]["z_mm"] = [11.8, 15.8]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_unmodified_box_or_deformed_tool_raw_mesh_cannot_pass_with_successful_reports(self):
        original = copy.deepcopy(self.meshes)
        self.meshes["body"]["vertices"], self.meshes["body"]["triangles"] = self.fixture.source_fixture()
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["construction_grooves"]["vertices"] = [(x, y + 0.01, z) for x, y, z in self.meshes["construction_grooves"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_static_or_deformed_travel_meshes_do_not_prove_the_sliding_path(self):
        original = copy.deepcopy(self.meshes)
        self.meshes["travel_30"]["vertices"] = copy.deepcopy(self.meshes["lid"]["vertices"])
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["travel_62"]["vertices"] = [(x, y, z + 0.01) for x, y, z in self.meshes["travel_62"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["travel_62"]["cad_metadata"]["object_location_mm"][1] += 0.01
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_source_actual_geometry_and_cad_metadata_are_checked_separately(self):
        original = copy.deepcopy(self.meshes)
        for role, field, value in (("source_body", "object_name", "Body"), ("body", "unit_scale", 1),
                                  ("lid", "modifier_count", 1), ("construction_guides", "scale", [1, 1, 2])):
            with self.subTest(role=role, field=field):
                self.meshes = copy.deepcopy(original)
                self.meshes[role]["cad_metadata"][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["source_body"]["vertices"] = [(x, y, z + 1) for x, y, z in self.meshes["source_body"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_hidden_tools_applied_final_meshes_and_complete_snapshot_dependencies_are_required(self):
        original = copy.deepcopy(self.verification)
        for name, field, value in (("GuideTool", "hidden", False), ("SlidingLid", "hidden", True),
                                  ("Body", "modifier_count", 1), ("MaleTool", "scale", [1, 2, 1])):
            with self.subTest(name=name, field=field):
                self.verification = copy.deepcopy(original)
                self.verification["final_objects"][name][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        original_manifest = copy.deepcopy(self.snapshot_manifest)
        for item in original_manifest["files"]:
            with self.subTest(missing=item["source"]):
                self.snapshot_manifest = copy.deepcopy(original_manifest)
                self.snapshot_manifest["files"].remove(item)
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.snapshot_manifest = copy.deepcopy(original_manifest)
        self.write_evidence()
        (self.run_dir / "source-snapshot" / "dovetail_checks.py").write_bytes(b"changed snapshot")
        self.assert_rejected_cleanly()

    def test_wrong_record_step_scenario_or_photo_digest_rejects_without_progress_change(self):
        original_run, original_runner = copy.deepcopy(self.run), copy.deepcopy(self.runner)
        self.run["records"][0]["step"] = "06-01"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.run = copy.deepcopy(original_run)
        self.runner["scenario"] = "lesson06_tenon"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.runner = copy.deepcopy(original_runner)
        self.run["records"][0]["sha256"] = "0" * 64
        self.write_evidence()
        self.assert_rejected_cleanly()


class DovetailStlExportImportTests(unittest.TestCase):
    """STL bytes, old checkpoint and actual UI-readback meshes are separate inputs."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-dovetail-stl-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "06" / DOVETAIL_EXPORT_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "06", "steps": [
            {"id": "06-03", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "06-03-01-export.png"
        image.write_bytes(png_bytes())
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson06_dovetail_export.py",
                    "records": [{"seq": 1, "step": "06-03", "file": image.name,
                                 "action": "只選單件匯出燕尾 STL 並實際重新匯入",
                                 "observed": "世界座標與剖面數位核對；實體結果仍空白",
                                 "recordedAt": "2026-10-25T13:00:00Z", "width": 3, "height": 2,
                                 "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_spec = importlib.util.spec_from_file_location("dovetail_stl_import_fixtures", Path(__file__).with_name("test_dovetail_stl_checks.py"))
        self.stl_fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.stl_fixture)
        self.fixture = self.stl_fixture.fixture
        self.checks = self.fixture.checks
        self.source = (self.project / "learning" / "evidence" / "06" / "2026-10-25-lesson06-dovetail-demo-v002"
                       / "demo-files" / "u06_dovetail_slide_v001.blend")
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-fixed-verified-dovetail-checkpoint")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[DOVETAIL_EXPORT_RUN_ID]["source_scene_sha256"]
        patcher = patch.dict(IMPORTER.RUNS[DOVETAIL_EXPORT_RUN_ID], {"source_scene_sha256": source_hash})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.source_metadata = self.stl_fixture.source_fixture()
        self.source_metadata.update(kind="dovetail_slide_geometry_demo", scene_path=str(self.source),
                                    scene_sha256=source_hash, reopened=True)
        self.source_verification = self.source.parent.parent / "verification.json"
        self.source_verification.write_text(json.dumps(self.source_metadata), encoding="utf-8")
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.meshes, self.stls, self.exports = {}, {}, []
        for part, name, origin in (("body", "Body", [0, 0, 0]), ("lid", "SlidingLid", [0, 0, 16.2])):
            vertices, triangles = (self.fixture.body_fixture if part == "body" else self.fixture.lid_fixture)()
            self.meshes["source_" + part] = {"vertices": vertices, "triangles": triangles,
                                             "cad_metadata": TenonGeometryImportTests.cad(name, origin)}
            path = self.run_dir / "demo-files" / "exports" / ("u06_dovetail_%s_v001.stl" % part)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.stl_fixture.binary_stl(vertices, triangles))
            self.stls[part] = path
            entry = {"kind": part, "source_object": name, "selected_names": [name], "stl_path": str(path),
                     "reimport_object": name + "_STL",
                     "export_options": {"only_selected": True, "global_scale": 1.0, "use_scene_unit": False,
                                        "apply_modifiers": True, "forward_axis": "Y", "up_axis": "Z",
                                        "ascii_format": False, "use_batch": False},
                     "import_options": {"global_scale": 1.0, "use_scene_unit": False, "forward_axis": "Y", "up_axis": "Z"}}
            self.exports.append(entry)
            self.refresh_export(entry)
            self.refresh_reimport(part)
        self.verification = {
            "passed": True, "kind": "dovetail_stl_exports", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True,
            "source_body": copy.deepcopy(self.source_metadata["body"]), "source_lid": copy.deepcopy(self.source_metadata["lid"]),
            "source_assembly": copy.deepcopy(self.source_metadata["assembly"]), "exports": self.exports,
            "reimport_verified": True, "exported_stl": True, "saved_new_scene": False,
            "trial": {"status": "experimental_geometry_only", "selected_by": "tutor", "horizontal_total_clearance_mm": .4,
                      "horizontal_side_clearance_mm": .2, "qualified_clearance_mm": None},
            "mesh_analysis_overhang_checked": False, "slicer_checked": False, "printed": False, "fit_tested": False,
            "physical_measurements": None, "fit_results": None, "physical_interference": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "volumeRelative": 1e-5, "purpose": "Floating point reconstruction only"}}
        self.refresh_assemblies()
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
                       "scenario": "lesson06_dovetail_export", "outputDir": str(self.run_dir),
                       "startedAt": "2026-10-25T12:59:00Z", "endedAt": "2026-10-25T13:01:00Z"}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson06_dovetail_export.py", "learning/tutor/scenarios/lid_checks.py",
                   "learning/tutor/scenarios/stl_checks.py", "learning/tutor/scenarios/tenon_checks.py",
                   "learning/tutor/scenarios/dovetail_checks.py", "learning/tutor/scenarios/dovetail_stl_checks.py")
        records = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            records.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        self.snapshot_manifest = {"recordedAt": "2026-10-25T12:59:00Z", "files": records,
                                  "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": source_hash}
        self.write_evidence()

    def refresh_export(self, entry, detailed=True):
        path = self.stls[entry["kind"]]
        actual = IMPORTER._read_binary_stl(path)
        entry.update(stl_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), stl_bytes=actual["bytes"],
                     stl_dimensions_mm=actual["dimensions_mm"], stl_triangles=actual["triangles"],
                     stl_non_manifold_edges=actual["non_manifold_edges"], stl_connected_shells=actual["connected_shells"],
                     stl_genus=int(actual["genus"]), stl_volume_mm3=actual["volume_mm3"])
        if detailed:
            entry["stl_verification"] = self.stl_fixture.validate_dovetail_stl(path, entry["kind"], self.source_metadata)

    def refresh_reimport(self, part):
        raw = self.stl_fixture.read_stl(self.stls[part])
        name = "Body_STL" if part == "body" else "SlidingLid_STL"
        self.meshes["reimport_" + part] = {"vertices": raw["vertices"], "triangles": raw["triangles"],
                                           "cad_metadata": TenonGeometryImportTests.cad(name, [0, 0, 0])}

    def refresh_assemblies(self):
        parts = {entry["kind"]: entry["stl_verification"]["geometry_readback"] for entry in self.exports}
        self.verification["stl_assembly"] = self.checks.validate_assembly(parts["body"], parts["lid"])
        for part, function in (("body", self.checks.validate_body_mesh), ("lid", self.checks.validate_lid_mesh)):
            raw = self.meshes["reimport_" + part]
            self.verification["reimport_" + part] = function(raw["vertices"], raw["triangles"])
        self.verification["reimport_assembly"] = self.checks.validate_assembly(self.verification["reimport_body"], self.verification["reimport_lid"])

    def write_evidence(self):
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner), ("source-snapshot/manifest.json", self.snapshot_manifest)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        for role, raw in self.meshes.items():
            (self.run_dir / (role + "_mesh.json")).write_text(json.dumps(raw), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(DOVETAIL_EXPORT_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (DOVETAIL_EXPORT_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_source_bound_binary_exports_and_actual_reimports_preserve_physical_blank_and_progress(self):
        self.assertEqual(self.production_source_hash,
                         "b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e")
        result = IMPORTER.import_run(DOVETAIL_EXPORT_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 4)
        self.assertIn("定位榫 STL", metadata["completionScope"])
        self.assertIn("尚未完成", metadata["completionScope"])
        for entry in metadata["verification"]["exports"]:
            self.assertEqual(entry["stl_verification"]["source_scene_path"], str(self.source))
            self.assertEqual(entry["stl_verification"]["source_scene_sha256"], self.verification["source_scene_sha256"])
        self.assertLess(self.verification["reimport_assembly"]["normal_side_gap_mm"], .2)
        self.assertEqual(self.meshes["reimport_lid"]["cad_metadata"]["object_location_mm"], [0, 0, 0])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_legal_retriangulation_does_not_need_source_triangle_signature_or_count(self):
        for entry in self.exports:
            part = entry["kind"]
            raw = self.meshes["source_" + part]
            vertices, triangles = self.stl_fixture.subdivide(raw["vertices"], raw["triangles"])
            old_count = entry["stl_triangles"]
            self.stls[part].write_bytes(self.stl_fixture.binary_stl(vertices, triangles))
            self.refresh_export(entry)
            self.refresh_reimport(part)
            self.assertEqual(entry["stl_triangles"], old_count * 3)
        self.refresh_assemblies()
        self.write_evidence()
        self.assertEqual(IMPORTER.import_run(DOVETAIL_EXPORT_RUN_ID, self.project)["steps"], 1)
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_selected_names_export_and_import_options_exclude_tools_and_scaling(self):
        original = copy.deepcopy(self.exports)
        for section, field, value in ((None, "selected_names", ["Body", "GuideTool"]), (None, "source_object", "TenonTool"),
                                     (None, "reimport_object", "Body"), ("export_options", "only_selected", False),
                                     ("export_options", "global_scale", 1.00005), ("export_options", "use_scene_unit", True),
                                     ("export_options", "apply_modifiers", False), ("export_options", "ascii_format", True),
                                     ("export_options", "use_batch", True), ("import_options", "global_scale", 1000),
                                     ("import_options", "use_scene_unit", True), ("import_options", "up_axis", "Y")):
            with self.subTest(section=section, field=field):
                self.exports[:] = copy.deepcopy(original)
                target = self.exports[0] if section is None else self.exports[0][section]
                target[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_stl_byte_hash_version_and_strict_binary_length_are_required(self):
        original = self.stls["body"].read_bytes()
        self.stls["body"].write_bytes(original + b"trailing")
        self.exports[0]["stl_sha256"] = hashlib.sha256(self.stls["body"].read_bytes()).hexdigest()
        self.exports[0]["stl_bytes"] = len(original) + len(b"trailing")
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.stls["body"].write_bytes(original)
        self.refresh_export(self.exports[0])
        self.exports[0]["stl_triangles"] += 1
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_wrong_dovetail_profile_cannot_pass_by_same_bounds_and_updated_binary_summary(self):
        raw = copy.deepcopy(self.meshes["source_body"])
        points = [list(v) for v in raw["vertices"]]
        index = next(i for i, v in enumerate(points) if abs(v[1]) < 19 and v[2] > 11)
        points[index][1] += .01
        self.stls["body"].write_bytes(self.stl_fixture.binary_stl(points, raw["triangles"]))
        self.refresh_export(self.exports[0], detailed=False)
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_source_checkpoint_copy_metadata_and_source_raw_cannot_be_substituted(self):
        for path in (self.source, self.opened):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)
        original = copy.deepcopy(self.source_metadata)
        self.source_metadata["scene_sha256"] = "0" * 64
        self.source_verification.write_text(json.dumps(self.source_metadata), encoding="utf-8")
        self.assert_rejected_cleanly()
        self.source_verification.write_text(json.dumps(original), encoding="utf-8")
        self.meshes["source_body"]["vertices"], self.meshes["source_body"]["triangles"] = self.fixture.source_fixture()
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_actual_reimport_geometry_and_baked_world_coordinate_origin_are_verified(self):
        original = copy.deepcopy(self.meshes)
        self.meshes["reimport_lid"]["cad_metadata"]["object_location_mm"][2] = 16.2
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["reimport_lid"]["vertices"] = [(x, y, z + .2) for x, y, z in self.meshes["reimport_lid"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_reimport_and_stl_assembly_must_report_actual_normal_gap(self):
        original = copy.deepcopy(self.verification)
        for role in ("source_assembly", "stl_assembly", "reimport_assembly"):
            with self.subTest(role=role):
                self.verification = copy.deepcopy(original)
                self.verification[role]["normal_side_gap_mm"] = .2
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_no_new_scene_overhang_print_or_qualified_fit_claims_are_accepted(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("saved_new_scene", True), ("mesh_analysis_overhang_checked", True), ("slicer_checked", True),
                             ("exported_stl", False), ("reimport_verified", False), ("printed", True), ("fit_tested", True),
                             ("physical_measurements", []), ("fit_results", "pass"), ("physical_interference", False),
                             ("qualified_clearance_mm", .4)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["trial"]["selected_by"] = "learner"
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_four_raw_mesh_cad_metadata_and_nine_snapshots_are_required(self):
        original_meshes = copy.deepcopy(self.meshes)
        for role, field, value in (("source_lid", "object_name", "Lid"), ("source_body", "unit_scale", 1),
                                  ("reimport_body", "modifier_count", 1), ("reimport_lid", "scale", [1, 1, 2])):
            with self.subTest(role=role, field=field):
                self.meshes = copy.deepcopy(original_meshes)
                self.meshes[role]["cad_metadata"][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original_meshes)
        original_manifest = copy.deepcopy(self.snapshot_manifest)
        for name in ("lid_checks.py", "tenon_checks.py", "dovetail_checks.py", "stl_checks.py", "dovetail_stl_checks.py"):
            with self.subTest(missing=name):
                self.snapshot_manifest = copy.deepcopy(original_manifest)
                self.snapshot_manifest["files"] = [x for x in self.snapshot_manifest["files"] if not x["source"].endswith("/" + name)]
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_scenario_step_and_image_hash_are_validated_before_publication(self):
        original_run, original_runner = copy.deepcopy(self.run), copy.deepcopy(self.runner)
        self.run["records"][0]["step"] = "06-02"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.run = copy.deepcopy(original_run)
        self.runner["scenario"] = "lesson06_dovetail"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.runner = copy.deepcopy(original_runner)
        self.run["records"][0]["sha256"] = "0" * 64
        self.write_evidence()
        self.assert_rejected_cleanly()


class ThreadParameterImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-parameter-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "08" / THREAD_PARAMETERS_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "08", "steps": [
            {"id": "08-01", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "08-01-01-reference.png"
        image.write_bytes(png_bytes())
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson08_parameters.py",
                    "records": [{"seq": 1, "step": "08-01", "file": image.name,
                                 "action": "實選原盒基準面並建立空白參數紀錄",
                                 "observed": "未建卡扣臂；所有未提供參數及計算結果留空",
                                 "recordedAt": "2026-10-25T14:00:00Z", "width": 3, "height": 2,
                                 "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_spec = importlib.util.spec_from_file_location("parameter_box_fixtures", Path(__file__).with_name("test_lid_checks.py"))
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        vertices, triangles = fixture.body_fixture()
        box = fixture.checks.validate_body_mesh(vertices, triangles)
        self.meshes = {role: {"vertices": vertices, "triangles": triangles,
                              "cad_metadata": TenonGeometryImportTests.cad(name, [0, 0, 0])}
                       for role, name in (("source_body", "Cube"), ("reference_body", "Body_Reference"))}
        self.source = self.project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files" / "u04_box_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes((IMPORTER.PROJECT / self.source.relative_to(self.project)).read_bytes())
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[THREAD_PARAMETERS_RUN_ID]["source_scene_sha256"]
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u08_thread_reference_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-renamed-box-reference-no-snap-arm")
        self.parameter_path = self.run_dir / "parameter-record-v001.json"
        self.faces = {}
        corners = {"rim": [[-30, -20, 15], [30, -20, 15], [28, -18, 15], [-28, -18, 15]],
                   "inner_floor": [[-28, -18, -13], [28, -18, -13], [28, 18, -13], [-28, 18, -13]],
                   "outer_floor": [[-30, -20, -15], [30, -20, -15], [30, 20, -15], [-30, 20, -15]]}
        # Blender's Python-side unit factor retains small double-precision offsets.
        for role, points in corners.items():
            points = [[c * 1.0000000474974513 for c in point] for point in points]
            bounds = {"min": [min(point[a] for point in points) for a in range(3)],
                      "max": [max(point[a] for point in points) for a in range(3)]}
            self.faces[role] = {"object_name": "Body_Reference", "selected_face_count": 1, "selected_vertex_count": 4,
                                "vertices_mm": points, "bounds_mm": bounds,
                                "spans_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)]}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson08_parameters.py", "learning/tutor/scenarios/lid_checks.py",
                   "learning/tutor/scenarios/tenon_checks.py")
        records = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            records.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        bindings = []
        for name, expected in IMPORTER.RUNS[THREAD_PARAMETERS_RUN_ID]["data_bindings"].items():
            original, snapshot = self.project / name, self.run_dir / expected["snapshot"]
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes((IMPORTER.PROJECT / name).read_bytes())
            snapshot.write_bytes(original.read_bytes())
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), expected["sha256"])
            bindings.append({"source": name, **expected})
        template = json.loads((snapshot_dir / "parameter-template-v001.json").read_text(encoding="utf-8"))
        self.parameter = copy.deepcopy(template)
        self.parameter.update(recordedAt="2026-10-25T14:00:00Z", source_scene_readback={"path": str(self.source), "sha256": source_hash, "bytes": self.source.stat().st_size},
                              reference_scene={"path": str(self.scene), "sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
                                               "bytes": self.scene.stat().st_size, "scene_role": "unmodified_box_thread_reference"},
                              measured_box=box, face_measurements=copy.deepcopy(self.faces))
        self.verification = {
            "passed": True, "kind": "thread_parameter_reference", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True, "source_body_geometry_unchanged": True,
            "source_body": box, "reference_body": copy.deepcopy(box), "scene_path": str(self.scene),
            "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(), "scene_bytes": self.scene.stat().st_size,
            "scene_role": "unmodified_box_thread_reference", "reopened": True, "thread_modeled": False, "boss_modeled": False, "pilot_hole_modeled": False, "counterpart_modeled": False,
            "modifier_created": False, "screw_modifier_created": False, "geometry_modified": False,
            "face_measurements": copy.deepcopy(self.faces), "non_manifold_selected_edges": 0,
            "parameter_record_path": str(self.parameter_path), "calculations_performed": False,
            "strength_analysis_performed": False, "fit_qualification": False, "printed": False, "fit_tested": False,
            "slicer_checked": False, "exported": False, "exported_stl": False, "physical_measurements": None, "fit_results": None,
            "material_grade": None, "physical_interference": None, "qualified_torque_Nm": None, "thread_route_selected": None, "thread_standard_selected": None,
            "qualified_strength_N": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "purpose": "Floating point only; not strength qualification"}}
        self.snapshot_manifest = {"recordedAt": "2026-10-25T13:59:00Z", "files": records, "dataBindings": bindings,
                                  "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": source_hash}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
                       "scenario": "lesson08_parameters", "outputDir": str(self.run_dir),
                       "startedAt": "2026-10-25T13:59:00Z", "endedAt": "2026-10-25T14:01:00Z"}
        identity = [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        for raw in self.meshes.values():
            raw["cad_metadata"].update(matrix_world=copy.deepcopy(identity),object_rotation_euler_radians=[0.,0.,0.],mesh_data_name="OriginalBoxData",
                local_mesh_sha256=hashlib.sha256(json.dumps({"vertices":vertices,"triangles":triangles},separators=(',',':')).encode()).hexdigest())
        self.verification.update(route=copy.deepcopy(template['route']),blender_mapping=copy.deepcopy(template['blender_mapping']),
            parameter_template_path=str(self.project/'learning/plans/08-01-thread-parameters-v001.json'),
            parameter_template_sha256=IMPORTER.RUNS[THREAD_PARAMETERS_RUN_ID]['data_bindings']['learning/plans/08-01-thread-parameters-v001.json']['sha256'],
            source_facts_path=str(self.project/'sources/engineering/thread-source-facts-v001.json'),
            source_facts_sha256=IMPORTER.RUNS[THREAD_PARAMETERS_RUN_ID]['data_bindings']['sources/engineering/thread-source-facts-v001.json']['sha256'],
            final_objects={name:dict(type=kind,hidden=name!='Body_Reference',scale=[1.,1.,1.],modifier_count=0,matrix_world=copy.deepcopy(identity))
                for name,kind in (('Body_Reference','MESH'),('Camera','CAMERA'),('Light','LIGHT'))})
        self.run['records']=[]
        for index,slug in enumerate(('rim-face','inner-floor','outer-floor','non-manifold','saved','reopened-verified'),1):
            image=self.run_dir/('08-01-%02d-%s.png'%(index,slug));image.write_bytes(png_bytes())
            self.run['records'].append(dict(seq=index,step='08-01',slug=slug,file=image.name,action='實選原盒／另存重開',observed='24項草案仍待定',
                recordedAt='2026-10-25T14:00:00Z',width=3,height=2,sha256=hashlib.sha256(image.read_bytes()).hexdigest()))
        self.write_evidence()

    def write_evidence(self):
        self.parameter_path.write_text(json.dumps(self.parameter), encoding="utf-8")
        self.verification["parameter_record_sha256"] = hashlib.sha256(self.parameter_path.read_bytes()).hexdigest()
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner), ("source-snapshot/manifest.json", self.snapshot_manifest),
                            ("face-measurements.json", self.faces)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        for role, raw in self.meshes.items():
            (self.run_dir / (role + "_mesh.json")).write_text(json.dumps(raw), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(THREAD_PARAMETERS_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (THREAD_PARAMETERS_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_reference_only_measured_box_pending_spec_and_no_progress_change(self):
        result=IMPORTER.import_run(THREAD_PARAMETERS_RUN_ID,self.project)
        self.assertEqual((result['steps'],result['records']),(1,6))
        metadata=json.loads(Path(result['metadata']).read_text('utf8'))
        self.assertEqual(len(metadata['geometryEvidence']),2);self.assertEqual(len(metadata['dataEvidence']),2)
        self.assertEqual(len(self.parameter['draft_parameters']),24)
        self.assertTrue(all(p['value'] is None and p['status']=='draft_pending' for p in self.parameter['draft_parameters']))
        self.assertIsNone(self.parameter['route']['selected']);self.assertFalse(self.parameter['blender_mapping']['modifier_created'])
        self.assertFalse(Path(self.parameter['source_scene']['path']).is_absolute())
        self.assertTrue(Path(self.parameter['source_scene_readback']['path']).is_absolute())
        self.assertEqual(self.progress.read_bytes(),b'{"revision":18}')

    def test_all_twenty_four_draft_values_and_status_cannot_be_promoted_to_measured_or_selected(self):
        before=copy.deepcopy(self.parameter)
        for index in range(24):
            for field,value in [('value',2),('status','measured_in_blender')]:
                with self.subTest(parameter=before['draft_parameters'][index]['id'],field=field):
                    self.parameter=copy.deepcopy(before);self.parameter['draft_parameters'][index][field]=value
                    self.write_evidence();self.assert_rejected_cleanly()

    def test_route_tutor_candidate_mapping_inputs_and_documented_relationships_are_not_configured(self):
        before=copy.deepcopy(self.parameter)
        for field,value in [('selected','custom_printed_thread'),('candidate_is_not_a_user_decision',False),('selection_status','selected')]:
            self.parameter=copy.deepcopy(before);self.parameter['route'][field]=value;self.write_evidence();self.assert_rejected_cleanly()
        for field,value in [('angle_degrees',360),('screw_offset_mm',2),('iterations',3),('axis','Z'),('steps_viewport',32),('modifier_created',True)]:
            self.parameter=copy.deepcopy(before);self.parameter['blender_mapping'][field]=value;self.write_evidence();self.assert_rejected_cleanly()
        self.parameter=copy.deepcopy(before);self.verification['blender_mapping']['angle_degrees']=360
        self.write_evidence();self.assert_rejected_cleanly()

    def test_template_source_scene_must_remain_intact_and_readback_has_distinct_provenance(self):
        before=copy.deepcopy(self.parameter)
        for change in (lambda:self.parameter.__setitem__('source_scene',self.parameter['source_scene_readback']),
                       lambda:self.parameter['source_scene_readback'].__setitem__('sha256','0'*64),
                       lambda:self.parameter['reference_scene'].__setitem__('scene_role','modeled_thread')):
            self.parameter=copy.deepcopy(before);change();self.write_evidence();self.assert_rejected_cleanly()

    def test_source_reference_local_mesh_matrix_and_final_single_box_inventory_cannot_change(self):
        before=copy.deepcopy(self.meshes)
        for change in (lambda:self.meshes['reference_body']['cad_metadata'].__setitem__('local_mesh_sha256','0'*64),
                       lambda:self.meshes['reference_body']['cad_metadata'].__setitem__('matrix_world',[[1.]*4]*4),
                       lambda:self.meshes['source_body']['cad_metadata'].__setitem__('modifier_count',1),
                       lambda:self.meshes['reference_body'].__setitem__('vertices',[(x,y,z+.1) for x,y,z in self.meshes['reference_body']['vertices']])):
            self.meshes=copy.deepcopy(before);change();self.write_evidence();self.assert_rejected_cleanly()
        self.meshes=copy.deepcopy(before);self.verification['final_objects']['Thread']={'type':'MESH','hidden':False}
        self.write_evidence();self.assert_rejected_cleanly()

    def test_three_actual_face_points_counts_spans_and_separate_face_record_are_required(self):
        before=copy.deepcopy(self.verification)
        for role,field,value in [('rim','selected_face_count',True),('rim','spans_mm',[60,2.01,0]),('inner_floor','object_name','Cube')]:
            self.verification=copy.deepcopy(before);self.verification['face_measurements'][role][field]=value
            self.write_evidence();self.assert_rejected_cleanly()
        self.verification=copy.deepcopy(before);self.faces['outer_floor']['vertices_mm'][0][2]+=.01
        self.write_evidence();self.assert_rejected_cleanly()

    def test_source_template_facts_and_snapshots_are_fixed_even_if_manifest_is_rehashed(self):
        for relative,info in IMPORTER.RUNS[THREAD_PARAMETERS_RUN_ID]['data_bindings'].items():
            for path in (self.project/relative,self.run_dir/info['snapshot']):
                with self.subTest(path=path):
                    previous=path.read_bytes();path.write_bytes(previous+b' ');self.assert_rejected_cleanly();path.write_bytes(previous)
        self.verification['source_facts_sha256']='0'*64;self.write_evidence();self.assert_rejected_cleanly()

    def test_modeling_exports_strength_hardware_material_and_physical_results_cannot_be_invented(self):
        before=copy.deepcopy(self.verification)
        for field,value in [('thread_modeled',True),('boss_modeled',True),('pilot_hole_modeled',True),('counterpart_modeled',True),('modifier_created',True),
            ('screw_modifier_created',True),('geometry_modified',True),('calculations_performed',True),('exported_stl',True),('printed',True),('fit_tested',True),
            ('thread_route_selected','custom_printed_thread'),('thread_standard_selected','M6'),('material_grade','PLA'),('qualified_torque_Nm',0),('physical_measurements',[])]:
            with self.subTest(field=field):
                self.verification=copy.deepcopy(before);self.verification[field]=value;self.write_evidence();self.assert_rejected_cleanly()

    def test_source_copy_reference_scene_and_parameter_hash_remain_bound_to_actual_files(self):
        for path in (self.source,self.opened,self.scene,self.parameter_path):
            with self.subTest(path=path):
                previous=path.read_bytes();path.write_bytes(previous+b'changed');self.assert_rejected_cleanly();path.write_bytes(previous)
        (self.run_dir/'demo-files/forbidden.stl').write_bytes(b'not authorized')
        self.assert_rejected_cleanly()

    def test_required_script_data_bindings_current_scenario_and_screenshot_provenance_are_complete(self):
        before=copy.deepcopy(self.snapshot_manifest)
        self.snapshot_manifest['files']=[x for x in self.snapshot_manifest['files'] if not x['source'].endswith('tenon_checks.py')]
        self.write_evidence();self.assert_rejected_cleanly();self.snapshot_manifest=copy.deepcopy(before)
        self.snapshot_manifest['dataBindings'].pop();self.write_evidence();self.assert_rejected_cleanly();self.snapshot_manifest=copy.deepcopy(before)
        self.run['records'][0]['slug']='synthetic-rim';self.write_evidence();self.assert_rejected_cleanly()


class CantileverParameterImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-parameter-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "07" / PARAMETERS_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "07", "steps": [
            {"id": "07-01", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "07-01-01-reference.png"
        image.write_bytes(png_bytes())
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson07_parameters.py",
                    "records": [{"seq": 1, "step": "07-01", "file": image.name,
                                 "action": "實選原盒基準面並建立空白參數紀錄",
                                 "observed": "未建卡扣臂；所有未提供參數及計算結果留空",
                                 "recordedAt": "2026-10-25T14:00:00Z", "width": 3, "height": 2,
                                 "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_spec = importlib.util.spec_from_file_location("parameter_box_fixtures", Path(__file__).with_name("test_lid_checks.py"))
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        vertices, triangles = fixture.body_fixture()
        box = fixture.checks.validate_body_mesh(vertices, triangles)
        self.meshes = {role: {"vertices": vertices, "triangles": triangles,
                              "cad_metadata": TenonGeometryImportTests.cad(name, [0, 0, 0])}
                       for role, name in (("source_body", "Cube"), ("reference_body", "Body_Reference"))}
        self.source = self.project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files" / "u04_box_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"BLENDER-test-unchanged-original-box")
        source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.production_source_hash = IMPORTER.RUNS[PARAMETERS_RUN_ID]["source_scene_sha256"]
        patcher = patch.dict(IMPORTER.RUNS[PARAMETERS_RUN_ID], {"source_scene_sha256": source_hash})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u07_snap_reference_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-renamed-box-reference-no-snap-arm")
        self.parameter_path = self.run_dir / "parameter-record-v001.json"
        self.faces = {}
        corners = {"rim": [[-30, -20, 15], [30, -20, 15], [28, -18, 15], [-28, -18, 15]],
                   "inner_floor": [[-28, -18, -13], [28, -18, -13], [28, 18, -13], [-28, 18, -13]],
                   "outer_floor": [[-30, -20, -15], [30, -20, -15], [30, 20, -15], [-30, 20, -15]]}
        # Blender's Python-side unit factor retains small double-precision offsets.
        for role, points in corners.items():
            points = [[c * 1.0000000474974513 for c in point] for point in points]
            bounds = {"min": [min(point[a] for point in points) for a in range(3)],
                      "max": [max(point[a] for point in points) for a in range(3)]}
            self.faces[role] = {"object_name": "Body_Reference", "selected_face_count": 1, "selected_vertex_count": 4,
                                "vertices_mm": points, "bounds_mm": bounds,
                                "spans_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)]}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson07_parameters.py", "learning/tutor/scenarios/lid_checks.py",
                   "learning/tutor/scenarios/tenon_checks.py")
        records = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            records.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        bindings = []
        for name, expected in IMPORTER.RUNS[PARAMETERS_RUN_ID]["data_bindings"].items():
            original, snapshot = self.project / name, self.run_dir / expected["snapshot"]
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes((IMPORTER.PROJECT / name).read_bytes())
            snapshot.write_bytes(original.read_bytes())
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), expected["sha256"])
            bindings.append({"source": name, **expected})
        template = json.loads((snapshot_dir / "parameter-template-v001.json").read_text(encoding="utf-8"))
        self.parameter = copy.deepcopy(template)
        self.parameter.update(recordedAt="2026-10-25T14:00:00Z", source_scene={"path": str(self.source), "sha256": source_hash},
                              reference_scene={"path": str(self.scene), "sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
                                               "bytes": self.scene.stat().st_size, "scene_role": "unmodified_box_reference"},
                              measured_box=box, face_measurements=copy.deepcopy(self.faces))
        self.verification = {
            "passed": True, "kind": "snapfit_parameter_reference", "source_scene_path": str(self.source),
            "source_scene_sha256": source_hash, "opened_scene_path": str(self.opened), "opened_scene_sha256": source_hash,
            "source_unchanged": True, "opened_copy_unchanged": True, "source_body_geometry_unchanged": True,
            "source_body": box, "reference_body": copy.deepcopy(box), "scene_path": str(self.scene),
            "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(), "scene_bytes": self.scene.stat().st_size,
            "scene_role": "unmodified_box_reference", "reopened": True, "snap_arm_modeled": False,
            "face_measurements": copy.deepcopy(self.faces), "non_manifold_selected_edges": 0,
            "parameter_record_path": str(self.parameter_path), "calculations_performed": False,
            "strength_analysis_performed": False, "fit_qualification": False, "printed": False, "fit_tested": False,
            "slicer_checked": False, "exported": False, "physical_measurements": None, "fit_results": None,
            "qualified_strength_N": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "purpose": "Floating point only; not strength qualification"}}
        self.snapshot_manifest = {"recordedAt": "2026-10-25T13:59:00Z", "files": records, "dataBindings": bindings,
                                  "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": source_hash}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
                       "scenario": "lesson07_parameters", "outputDir": str(self.run_dir),
                       "startedAt": "2026-10-25T13:59:00Z", "endedAt": "2026-10-25T14:01:00Z"}
        self.write_evidence()

    def write_evidence(self):
        self.parameter_path.write_text(json.dumps(self.parameter), encoding="utf-8")
        self.verification["parameter_record_sha256"] = hashlib.sha256(self.parameter_path.read_bytes()).hexdigest()
        for name, value in (("run.json", self.run), ("verification.json", self.verification),
                            ("runner-status.json", self.runner), ("source-snapshot/manifest.json", self.snapshot_manifest),
                            ("face-measurements.json", self.faces)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        for role, raw in self.meshes.items():
            (self.run_dir / (role + "_mesh.json")).write_text(json.dumps(raw), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(PARAMETERS_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (PARAMETERS_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_reference_preserves_pending_parameters_and_binds_both_data_versions(self):
        self.assertEqual(self.production_source_hash, "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530")
        result = IMPORTER.import_run(PARAMETERS_RUN_ID, self.project)
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        self.assertEqual(len(metadata["geometryEvidence"]), 2)
        self.assertEqual(len(metadata["dataEvidence"]), 2)
        self.assertTrue(all(x["value"] is None for x in self.parameter["parameters"] + self.parameter["material_parameters"]))
        self.assertIn("不建卡扣臂", json.loads(self.catalog_path.read_text(encoding="utf-8"))["lessons"][0]["steps"][0]["operationRun"]["summary"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_arm_material_and_strain_values_cannot_be_filled_from_reference_wall_or_generic_tables(self):
        original = copy.deepcopy(self.parameter)
        for group in ("parameters", "material_parameters"):
            for index in range(len(original[group])):
                with self.subTest(group=group, field=original[group][index]["id"]):
                    self.parameter = copy.deepcopy(original)
                    self.parameter[group][index]["value"] = 2 if group == "parameters" else .015
                    self.write_evidence()
                    self.assert_rejected_cleanly()

    def test_formula_estimates_Q_and_qualification_remain_pending_and_template_exact(self):
        original = copy.deepcopy(self.parameter)
        for group, field, value in (("formula", "coefficient", 2/3), ("formula", "root_flexibility_Q", 1),
                                    ("formula", "applicability_confirmed", True), ("estimates", "delta_allow_mm", 0),
                                    ("estimates", "insertion_force_N", 1), ("results", "qualified_strength_N", 5),
                                    ("service_conditions", "assembly_cycles", 1)):
            with self.subTest(group=group, field=field):
                self.parameter = copy.deepcopy(original)
                self.parameter[group][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_face_points_counts_and_recomputed_spans_reject_wrong_or_synthetic_selection(self):
        original = copy.deepcopy(self.verification)
        for role, field, value in (("rim", "selected_face_count", True), ("rim", "selected_vertex_count", 3),
                                  ("rim", "spans_mm", [60, 2.01, 0]), ("inner_floor", "object_name", "Cube")):
            with self.subTest(role=role, field=field):
                self.verification = copy.deepcopy(original)
                self.verification["face_measurements"][role][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["face_measurements"]["rim"]["vertices_mm"][0][0] += .0005
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_face_file_parameter_record_hash_and_scene_association_are_checked(self):
        self.parameter["reference_scene"]["sha256"] = "0" * 64
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.parameter["reference_scene"]["sha256"] = self.verification["scene_sha256"]
        self.parameter["face_measurements"]["inner_floor"]["spans_mm"] = [60, 40, 0]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_source_copy_and_reference_checkpoint_must_match_unchanged_hashes(self):
        for path in (self.source, self.opened, self.scene):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous + b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_reference_mesh_or_applied_cad_state_cannot_change_under_same_report(self):
        original = copy.deepcopy(self.meshes)
        self.meshes["reference_body"]["vertices"] = [(x, y, z + 1) for x, y, z in self.meshes["reference_body"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["reference_body"]["cad_metadata"]["modifier_count"] = 1
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_provided_template_and_fact_data_cannot_be_replaced_with_rehashed_copies(self):
        for binding in self.snapshot_manifest["dataBindings"]:
            path = self.run_dir / binding["snapshot"]
            previous = path.read_bytes()
            with self.subTest(source=binding["source"]):
                path.write_bytes(previous + b" ")
                old_hash = binding["sha256"]
                binding["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.write_evidence()
                self.assert_rejected_cleanly()
                binding["sha256"] = old_hash
                path.write_bytes(previous)

    def test_no_model_calculation_strength_fit_or_physical_claim_can_be_published(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("snap_arm_modeled", True), ("calculations_performed", True), ("strength_analysis_performed", True),
                             ("fit_qualification", True), ("printed", True), ("fit_tested", True), ("exported", True),
                             ("qualified_strength_N", 0), ("qualified_clearance_mm", .4), ("physical_measurements", []),
                             ("source_body_geometry_unchanged", False), ("non_manifold_selected_edges", True)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_required_script_data_bindings_and_current_scenario_are_complete(self):
        original = copy.deepcopy(self.snapshot_manifest)
        self.snapshot_manifest["files"] = [x for x in self.snapshot_manifest["files"] if not x["source"].endswith("tenon_checks.py")]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.snapshot_manifest = copy.deepcopy(original)
        self.snapshot_manifest["dataBindings"].pop()
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.snapshot_manifest = copy.deepcopy(original)
        self.runner["scenario"] = "lesson06_dovetail_export"
        self.write_evidence()
        self.assert_rejected_cleanly()


class CantileverSnapImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-snap-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning" / "evidence" / "07" / SNAP_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning" / "catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "07", "steps": [
            {"id": "07-02", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning" / "progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        image = self.run_dir / "07-02-01-snap.png"
        image.write_bytes(png_bytes())
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson07_snap.py",
                    "records": [{"seq": 1, "step": "07-02", "file": image.name,
                                 "action": "精確選邊Bevel與靜態幾何核對", "observed": "幾何草案，材料與力學結果未定",
                                 "recordedAt": "2026-10-25T15:00:00Z", "width": 3, "height": 2,
                                 "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]}
        fixture_spec = importlib.util.spec_from_file_location("snap_import_fixtures", Path(__file__).with_name("test_snapfit_checks.py"))
        self.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.fixture)
        self.checks = self.fixture.checks
        # The source is a pinned, immutable native checkpoint. Copy it only into
        # TemporaryDirectory; final trial parts are independent analytic meshes.
        relative_source = Path("learning/evidence/07") / PARAMETERS_RUN_ID
        actual_source = IMPORTER.PROJECT / relative_source
        self.source_dir = self.project / relative_source
        self.source = self.source_dir / "demo-files" / "u07_snap_reference_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes((actual_source / "demo-files" / self.source.name).read_bytes())
        self.parameter_source = self.source_dir / "parameter-record-v001.json"
        self.parameter_source.write_bytes((actual_source / self.parameter_source.name).read_bytes())
        old = json.loads((actual_source / "verification.json").read_text(encoding="utf-8"))
        old.update(scene_path=str(self.source), parameter_record_path=str(self.parameter_source))
        self.old_verification = self.source_dir / "verification.json"
        self.old_verification.write_text(json.dumps(old), encoding="utf-8")
        self.source_body = old["reference_body"]
        self.opened = self.run_dir / "demo-files" / "sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files" / "u07_cantilever_snap_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-analytic-snap-and-lid-scene")
        self.meshes = {"source_body": json.loads((actual_source / "reference_body_mesh.json").read_text(encoding="utf-8"))}
        for role, name, location, geometry in (
                ("construction_snap", "SnapTool", [0, -22.2, -9.5], self.fixture.tool_fixture("snap")),
                ("construction_flange", "FlangeTool", [0, -25.25, 10.5], self.fixture.tool_fixture("flange")),
                ("body", "Body", [0, 0, 0], self.fixture.body_fixture()),
                ("lid", "Lid", [0, -3, 16.2], self.fixture.lid_fixture())):
            self.meshes[role] = {"vertices": geometry[0], "triangles": geometry[1],
                                 "cad_metadata": TenonGeometryImportTests.cad(name, location)}
        body = self.checks.validate_body_mesh(*self.geometry("body"), self.source_body)
        lid = self.checks.validate_lid_mesh(*self.geometry("lid"))
        assembly = self.checks.validate_assembly(body, lid)
        snap = self.checks.validate_tool_mesh(*self.geometry("construction_snap"), "snap")
        flange = self.checks.validate_tool_mesh(*self.geometry("construction_flange"), "flange")
        self.plan_path = self.project / "learning/plans/07-02-cantilever-geometry-draft-v001.json"
        self.plan_path.parent.mkdir(parents=True)
        self.plan_path.write_bytes((IMPORTER.PROJECT / self.plan_path.relative_to(self.project)).read_bytes())
        plan = json.loads(self.plan_path.read_text(encoding="utf-8"))
        self.draft_path = self.run_dir / "geometry-draft-record-v001.json"
        self.draft = copy.deepcopy(plan)
        self.draft.update(recordedAt="2026-10-25T15:00:00Z",
                          source_scene={"path": str(self.source), "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest()},
                          reference_scene={"path": str(self.scene), "sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
                                           "bytes": self.scene.stat().st_size, "scene_role": "experimental_cantilever_geometry"},
                          geometry_readback={"body": body, "lid": lid, "assembly": assembly})
        self.bevels = {role: {"operator_id": "MESH_OT_bevel", "offset": amount, "offset_mm": amount,
                             "offset_type": "OFFSET", "segments": segments, "profile": .5,
                             "affect": "EDGES", "clamp_overlap": False}
                       for role, amount, segments in (("hook", .8, 1), ("root", .6, 3))}
        self.edges = {"hook": [[[-3.0, -24.2, 13.0], [3.0, -24.2, 13.0]]],
                      "root": [[[-3.0, -23.0, -8.0], [3.0, -23.0, -8.0]], [[-3.0, -21.4, -8.0], [3.0, -21.4, -8.0]]]}
        self.attempts = [{"target": target, "tool": tool, "attempt": 0, "operation": "UNION", "operand": tool, "solver": "EXACT"}
                         for target, tool in (("Body", "SnapTool"), ("Lid", "FlangeTool"))]
        self.verification = {
            "passed": True, "kind": "cantilever_snap_geometry_demo", "source_scene_path": str(self.source),
            "source_scene_sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(), "opened_scene_path": str(self.opened),
            "opened_scene_sha256": hashlib.sha256(self.opened.read_bytes()).hexdigest(), "source_unchanged": True,
            "opened_copy_unchanged": True, "source_body": self.source_body, "body": body, "lid": lid,
            "construction_snap": snap, "construction_flange": flange, "assembly": assembly, "bevel_operations": self.bevels,
            "source_snap_parameter_path": str(self.parameter_source),
            "source_snap_parameter_sha256": hashlib.sha256(self.parameter_source.read_bytes()).hexdigest(),
            "scene_path": str(self.scene), "scene_sha256": hashlib.sha256(self.scene.read_bytes()).hexdigest(),
            "scene_bytes": self.scene.stat().st_size, "reopened": True,
            "final_objects": {name: {"object_name": name, "type": "MESH", "hidden": name.endswith("Tool"),
                                      "modifier_count": 0, "scale": [1, 1, 1]}
                              for name in ("Body", "Lid", "SnapTool", "FlangeTool")},
            "draft_plan_path": str(self.plan_path), "draft_plan_sha256": hashlib.sha256(self.plan_path.read_bytes()).hexdigest(),
            "draft_record_path": str(self.draft_path), "geometry_modified": True, "strength_analysis_performed": False,
            "fit_qualification": False, "exported_stl": False, "slicer_checked": False, "printed": False, "fit_tested": False,
            "material_grade": None, "epsilon_allow": None, "Q": None, "delta_allow_mm": None, "required_deflection_mm": None,
            "forces": None, "physical_measurements": None, "fit_results": None, "physical_interference": None,
            "qualified_strength_N": None, "qualified_clearance_mm": None,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "purpose": "Floating point only; not strength/fit qualification"}}
        snapshot_dir = self.run_dir / "source-snapshot"
        snapshot_dir.mkdir()
        scripts = ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                   "learning/tutor/scenarios/lesson07_snap.py", "learning/tutor/scenarios/lid_checks.py",
                   "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/snapfit_checks.py")
        files = []
        for script in scripts:
            target = snapshot_dir / Path(script).name
            target.write_bytes(("# isolated snapshot fixture: " + script).encode("utf-8"))
            files.append({"source": script, "snapshot": "source-snapshot/" + target.name,
                          "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        bindings = []
        for name, expected in IMPORTER.RUNS[SNAP_RUN_ID]["data_bindings"].items():
            source, target = self.project / name, self.run_dir / expected["snapshot"]
            source.parent.mkdir(parents=True, exist_ok=True)
            if not source.exists():
                source.write_bytes((IMPORTER.PROJECT / name).read_bytes())
            target.write_bytes(source.read_bytes())
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected["sha256"])
            bindings.append({"source": name, **expected})
        self.manifest = {"recordedAt": "2026-10-25T14:59:00Z", "files": files, "dataBindings": bindings,
                         "sourceScene": str(self.source), "sourceCopy": str(self.opened),
                         "sourceSha256": self.verification["source_scene_sha256"]}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
                       "scenario": "lesson07_snap", "outputDir": str(self.run_dir),
                       "startedAt": "2026-10-25T14:59:00Z", "endedAt": "2026-10-25T15:01:00Z"}
        self.write_evidence()

    def geometry(self, role):
        return self.meshes[role]["vertices"], self.meshes[role]["triangles"]

    def write_evidence(self):
        self.draft_path.write_text(json.dumps(self.draft), encoding="utf-8")
        self.verification["draft_record_sha256"] = hashlib.sha256(self.draft_path.read_bytes()).hexdigest()
        for name, value in (("run.json", self.run), ("verification.json", self.verification), ("runner-status.json", self.runner),
                            ("source-snapshot/manifest.json", self.manifest), ("bevel-operations.json", self.bevels),
                            ("selected-root-hook-edges.json", self.edges), ("operand-attempts.json", self.attempts)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        names = {"source_body": "source_body_mesh.json", "construction_snap": "snap_tool_mesh.json", "body": "body_mesh.json",
                 "construction_flange": "flange_tool_mesh.json", "lid": "lid_mesh.json"}
        for role, name in names.items():
            (self.run_dir / name).write_text(json.dumps(self.meshes[role]), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(SNAP_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (SNAP_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_draft_recomputes_tools_parts_and_static_gaps_without_material_or_progress_claims(self):
        result = IMPORTER.import_run(SNAP_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 5)
        self.assertEqual(len(metadata["dataEvidence"]), 4)
        self.assertEqual(self.verification["body"]["dimensions_mm"], [60, 44.5, 30])
        self.assertAlmostEqual(self.verification["assembly"]["straight_beam_inward_static_space_mm"], 1.4, delta=1e-4)
        self.assertAlmostEqual(self.verification["assembly"]["inner_root_fillet_local_static_gap_mm"], .8, delta=1e-4)
        self.assertIsNone(self.draft["parameters"][-1]["value"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_local_boolean_retry_records_are_preserved_but_last_assignment_must_be_correct(self):
        self.attempts[0]["operand"] = None
        self.attempts.insert(1, dict(self.attempts[0], attempt=1, operand="SnapTool"))
        self.write_evidence()
        self.assertEqual(IMPORTER.import_run(SNAP_RUN_ID, self.project)["steps"], 1)

    def test_unknown_strain_force_required_deflection_and_qualified_values_remain_null(self):
        original = copy.deepcopy(self.verification)
        for field in ("epsilon_allow", "Q", "delta_allow_mm", "required_deflection_mm", "forces",
                      "physical_measurements", "physical_interference", "qualified_strength_N", "qualified_clearance_mm"):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = 1.2
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_draft_dimensions_do_not_authorize_material_values_or_replacement_of_fixed_source_plan(self):
        original = copy.deepcopy(self.draft)
        for field, value in (("epsilon_allow", .015), ("root_flexibility_Q", 1), ("delta_allow_mm", 1.4),
                             ("insertion_force_N", 10), ("chosen_by", "learner")):
            with self.subTest(field=field):
                self.draft = copy.deepcopy(original)
                self.draft[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()

    def test_real_operator_settings_and_precisely_selected_root_edges_are_required(self):
        original = copy.deepcopy(self.bevels)
        for role, field, value in (("root", "segments", 1), ("root", "offset_type", "WIDTH"),
                                  ("root", "offset_mm", .8), ("root", "offset_mm", .60005),
                                  ("hook", "profile", .6), ("hook", "affect", "VERTICES")):
            with self.subTest(role=role, field=field):
                self.bevels.clear(); self.bevels.update(copy.deepcopy(original))
                self.bevels[role][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.bevels.clear(); self.bevels.update(copy.deepcopy(original))
        self.edges["root"][0][0] = [-30.0, -20.0, 15.0]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_false_body_size_effective_length_or_straight_space_in_place_of_root_gap_is_rejected(self):
        original = copy.deepcopy(self.verification)
        changes = (("body", "dimensions_mm", [60, 40, 30]),
                   ("assembly", "inner_root_fillet_local_static_gap_mm", 1.4),
                   ("assembly", "required_deflection_mm", .9))
        for role, field, value in changes:
            with self.subTest(role=role, field=field):
                self.verification = copy.deepcopy(original)
                self.verification[role][field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["body"]["snap_profile"]["root_to_bearing_geometric_length_mm"] = 21
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_unfused_body_or_changed_fillet_tool_mesh_cannot_pass_by_unchanged_report(self):
        original = copy.deepcopy(self.meshes)
        source, tool = self.meshes["source_body"], self.meshes["construction_snap"]
        self.meshes["body"]["vertices"] = source["vertices"] + tool["vertices"]
        self.meshes["body"]["triangles"] = source["triangles"] + [[i+len(source["vertices"]) for i in tri] for tri in tool["triangles"]]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(original)
        self.meshes["construction_snap"]["vertices"] = [(x, y+.01, z) for x,y,z in self.meshes["construction_snap"]["vertices"]]
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_source_parameter_source_copy_scene_and_data_snapshots_are_immutable(self):
        for path in (self.source, self.parameter_source, self.opened, self.scene,
                     self.run_dir / "source-snapshot/geometry-plan-v001.json"):
            with self.subTest(path=path):
                previous = path.read_bytes()
                path.write_bytes(previous+b"changed")
                self.assert_rejected_cleanly()
                path.write_bytes(previous)

    def test_finished_visibility_applied_modifiers_and_no_strength_or_print_flags_are_required(self):
        original = copy.deepcopy(self.verification)
        for field, value in (("geometry_modified", False), ("source_body_geometry_unchanged", True),
                             ("strength_analysis_performed", True), ("fit_qualification", True), ("printed", True),
                             ("fit_tested", True), ("exported_stl", True)):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(original)
                self.verification[field] = value
                self.write_evidence()
                self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(original)
        self.verification["final_objects"]["SnapTool"]["hidden"] = False
        self.write_evidence()
        self.assert_rejected_cleanly()

    def test_last_boolean_assignment_and_full_script_data_evidence_cannot_be_omitted(self):
        self.attempts[-1]["operand"] = "SnapTool"
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.attempts[-1]["operand"] = "FlangeTool"
        original = copy.deepcopy(self.manifest)
        self.manifest["files"] = [x for x in self.manifest["files"] if not x["source"].endswith("snapfit_checks.py")]
        self.write_evidence()
        self.assert_rejected_cleanly()
        self.manifest = copy.deepcopy(original)
        self.manifest["dataBindings"].pop()
        self.write_evidence()
        self.assert_rejected_cleanly()


class PrintOrientationImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-orientation-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning/evidence/07" / OVERHANG_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning/catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "07", "steps": [
            {"id": "07-03", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning/progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        fixture_spec = importlib.util.spec_from_file_location("overhang_import_fixtures", Path(__file__).with_name("test_overhang_checks.py"))
        self.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(self.fixture)
        self.checks = self.fixture.checks
        self.source_dir = self.project / "learning/evidence/07" / SNAP_RUN_ID
        real_source = IMPORTER.PROJECT / "learning/evidence/07" / SNAP_RUN_ID
        self.source = self.source_dir / "demo-files/u07_cantilever_snap_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes((real_source / "demo-files" / self.source.name).read_bytes())
        self.geometry_record = self.source_dir / "geometry-draft-record-v001.json"
        self.geometry_record.write_bytes((real_source / self.geometry_record.name).read_bytes())
        old = json.loads((real_source / "verification.json").read_text(encoding="utf-8"))
        old["scene_path"] = str(self.source)
        (self.source_dir / "verification.json").write_text(json.dumps(old), encoding="utf-8")
        self.opened = self.run_dir / "demo-files/sources" / self.source.name
        self.opened.parent.mkdir(parents=True)
        self.opened.write_bytes(self.source.read_bytes())
        self.scene = self.run_dir / "demo-files/u07_print_orientation_v001.blend"
        self.scene.write_bytes(b"BLENDER-test-rigid-orientation-comparison")
        self.plan_path = self.project / "learning/plans/07-03-print-orientation-draft-v001.json"
        self.plan_path.parent.mkdir(parents=True)
        self.plan_path.write_bytes((IMPORTER.PROJECT / self.plan_path.relative_to(self.project)).read_bytes())
        self.plan = json.loads(self.plan_path.read_text(encoding="utf-8"))
        self.meshes = {}
        for kind in ("body", "lid"):
            original = json.loads((real_source / (kind + "_mesh.json")).read_text(encoding="utf-8"))
            raw = self.fixture._raw(original["vertices"], original["triangles"])
            raw["cad_metadata"] = self.cad(kind.title(), [0, 0, 0] if kind == "body" else [0, -3, 16.2], [0, 0, 0])
            self.meshes["source_" + kind] = raw
            for pose in ("baseline", "candidate"):
                label = kind + "_" + pose
                placed = self.fixture.pose_fixture(kind, pose, raw)
                item = self.plan["poses"][label]
                placed["cad_metadata"] = self.cad(kind.title(), item["object_location_mm_nominal"], item["rotation_degrees"])
                self.meshes[label] = placed
        self.settings = dict(self.fixture.settings_fixture(), show_overlays=True)
        self.poses = {label: self.checks.validate_orientation(self.meshes["source_" + label.split("_")[0]], raw,
                      label.split("_")[0], self.settings, label.split("_")[1])
                      for label, raw in self.meshes.items() if not label.startswith("source_")}
        self.layout = self.checks.validate_layout(self.poses["body_candidate"], self.poses["lid_candidate"])
        self.by_pose = {label: copy.deepcopy(self.settings) for label in self.poses}
        contexts = {label: {"mode": "EDIT_MESH", "active_object": label.split("_")[0].title(),
                    "only_finished_part_visible": label.split("_")[0].title(), "source_tools_hidden": True,
                    "native_popover_checked": True} for label in self.poses}
        self.tools = {}
        for name, location in (("SnapTool", [0, -22.2, -9.5]), ("FlangeTool", [0, -25.25, 10.5])):
            cad = self.cad(name, location, [0, 0, 0])
            self.tools[name] = {"type": "MESH", "hidden": True, "scale": [1, 1, 1], "location": location,
                "rotation": [0, 0, 0], "modifier_count": 0, "matrix_world": cad["matrix_world"],
                "local_mesh_sha256": hashlib.sha256((name + "-unchanged-native-source").encode()).hexdigest()}
        final = {}
        for name in ("Body", "Lid", "SnapTool", "FlangeTool"):
            if name.endswith("Tool"):
                tool = self.tools[name]
                location, rotation, matrix = tool["location"], tool["rotation"], tool["matrix_world"]
            else:
                cad = self.meshes[name.lower() + "_candidate"]["cad_metadata"]
                location, rotation, matrix = cad["object_location_mm"], cad["object_rotation_euler_radians"], cad["matrix_world"]
            final[name] = {"object_name": name, "type": "MESH", "hidden": name.endswith("Tool"),
                           "scale": [1, 1, 1], "modifier_count": 0, "location_mm": location,
                           "rotation_euler_radians": rotation, "matrix_world": matrix}
        self.record_path = self.run_dir / "print-orientation-record-v001.json"
        self.record = dict(copy.deepcopy(self.plan), recordedAt="2026-10-25T16:00:00Z",
            source_scene={"path": str(self.source), "sha256": self.digest(self.source)},
            reference_scene={"path": str(self.scene), "sha256": self.digest(self.scene), "bytes": self.scene.stat().st_size,
                             "scene_role": "print_orientation_comparison_draft"},
            analysis_settings=self.settings, poses=self.poses, layout=self.layout)
        self.verification = {"passed": True, "kind": "snapfit_print_orientation_demo", "source_scene_path": str(self.source),
            "source_scene_sha256": self.digest(self.source), "opened_scene_path": str(self.opened),
            "opened_scene_sha256": self.digest(self.opened), "source_unchanged": True, "opened_copy_unchanged": True,
            "source_geometry_draft_path": str(self.geometry_record), "source_geometry_draft_sha256": self.digest(self.geometry_record),
            "source_geometry_draft_unchanged": True, "scene_path": str(self.scene), "scene_sha256": self.digest(self.scene),
            "scene_bytes": self.scene.stat().st_size, "reopened": True, "draft_plan_path": str(self.plan_path),
            "draft_plan_sha256": self.digest(self.plan_path), "orientation_record_path": str(self.record_path),
            "analysis_settings": self.settings, "analysis_settings_by_pose": self.by_pose, "analysis_contexts": contexts,
            "poses": self.poses, "layout": self.layout, "source_tools": self.tools, "final_tools": copy.deepcopy(self.tools),
            "final_objects": final, "rigid_geometry_only": True, "geometry_modified": False, "rotation_applied_to_mesh": False,
            "mesh_analysis_overhang_checked": True,
            "numericComparison": {"dimensionsAbsMm": 1e-4, "angleBoundaryBandDeg": 1e-4, "purpose": "Floating point only; no support qualification"}}
        for field in ("strength_analysis_performed", "fit_qualification", "exported_stl", "slicer_checked", "printed", "fit_tested", "support_generation_performed"):
            self.verification[field] = False
        for field in ("material_grade", "epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces", "physical_measurements",
                      "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm", "support_required",
                      "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified"):
            self.verification[field] = None
        records = []
        for label in self.poses:
            for suffix in ("-controls", "-analysis"):
                image = self.run_dir / (label + suffix + ".png")
                image.write_bytes(png_bytes())
                records.append({"seq": len(records) + 1, "step": "07-03", "slug": label + suffix, "file": image.name,
                    "action": "實際原生設定與著色檢查", "observed": "派生統計不等於GPU或支撐合格", "recordedAt": "2026-10-25T16:00:00Z",
                    "width": 3, "height": 2, "sha256": self.digest(image)})
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson07_overhang.py", "records": records}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [],
            "scenario": "lesson07_overhang", "outputDir": str(self.run_dir), "startedAt": "2026-10-25T15:59:00Z", "endedAt": "2026-10-25T16:01:00Z"}
        snapshots = self.run_dir / "source-snapshot"
        snapshots.mkdir()
        files = []
        for relative in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                         "learning/tutor/scenarios/lesson07_overhang.py", "learning/tutor/scenarios/overhang_checks.py",
                         "learning/tutor/scenarios/snapfit_checks.py", "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py"):
            target = snapshots / Path(relative).name
            target.write_text("# isolated snapshot fixture: " + relative, encoding="utf-8")
            files.append({"source": relative, "snapshot": "source-snapshot/" + target.name, "sha256": self.digest(target)})
        bindings = []
        for relative, expected in IMPORTER.RUNS[OVERHANG_RUN_ID]["data_bindings"].items():
            original = self.project / relative
            original.parent.mkdir(parents=True, exist_ok=True)
            if not original.exists():
                original.write_bytes((IMPORTER.PROJECT / relative).read_bytes())
            target = self.run_dir / expected["snapshot"]
            target.write_bytes(original.read_bytes())
            self.assertEqual(self.digest(original), expected["sha256"])
            bindings.append({"source": relative, **expected})
        self.manifest = {"recordedAt": "2026-10-25T15:59:00Z", "files": files, "dataBindings": bindings,
            "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": self.digest(self.source)}
        self.write_evidence()

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def cad(name, location, degrees):
        x, y, z = [math.radians(a) for a in degrees]
        if abs(y) > .1:
            rotation = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
        elif abs(x) > .1:
            rotation = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
        else:
            rotation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        return {"object_name": name, "scale": [1, 1, 1], "modifier_count": 0, "unit_scale": .001,
                "length_unit": "MILLIMETERS", "object_location_mm": list(location),
                "object_rotation_euler_radians": [x, y, z], "object_rotation_euler_degrees": list(degrees),
                "matrix_world": [rotation[i] + [location[i]] for i in range(3)] + [[0, 0, 0, 1]]}

    def write_evidence(self):
        self.record_path.write_text(json.dumps(self.record), encoding="utf-8")
        self.verification["orientation_record_sha256"] = self.digest(self.record_path)
        for name, value in (("run.json", self.run), ("runner-status.json", self.runner), ("verification.json", self.verification),
                            ("source-snapshot/manifest.json", self.manifest), ("analysis-settings-by-pose.json", self.by_pose),
                            ("pose-verification.json", self.poses), ("source-tool-inventory.json", self.tools)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        for label, value in self.meshes.items():
            (self.run_dir / (label + "_mesh.json")).write_text(json.dumps(value), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):
            IMPORTER.import_run(OVERHANG_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (OVERHANG_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_four_pose_comparison_preserves_geometry_and_pending_support_without_progress(self):
        result = IMPORTER.import_run(OVERHANG_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 8))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 6)
        self.assertEqual(len(metadata["dataEvidence"]), 4)
        self.assertTrue(self.poses["body_candidate"]["layer_direction_readback"]["arm_length_parallel_bed"])
        self.assertFalse(self.poses["body_baseline"]["layer_direction_readback"]["arm_length_parallel_bed"])
        self.assertIsNone(metadata["verification"]["support_required"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_source_draft_plan_copy_and_new_scene_hashes_are_immutable(self):
        for path in (self.source, self.geometry_record, self.plan_path, self.opened, self.scene,
                     self.run_dir / "source-snapshot/overhang-source-facts-v001.json"):
            with self.subTest(path=path):
                original = path.read_bytes(); path.write_bytes(original + b"changed")
                self.assert_rejected_cleanly(); path.write_bytes(original)

    def test_material_mechanics_support_and_final_orientation_claims_remain_null(self):
        previous = copy.deepcopy(self.verification)
        for field in ("epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces", "support_required",
                      "final_print_orientation_approved", "bridge_or_support_qualified", "qualified_strength_N", "physical_measurements"):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(previous); self.verification[field] = 1
                self.write_evidence(); self.assert_rejected_cleanly()

    def test_record_cannot_promote_angle_range_or_static_space_to_print_qualification(self):
        previous = copy.deepcopy(self.record)
        for field, value in (("epsilon_allow", .015), ("support_strategy_status", "qualified"),
                             ("final_print_orientation_approved", True), ("required_deflection_mm", 1.4)):
            with self.subTest(field=field):
                self.record = copy.deepcopy(previous); self.record[field] = value
                self.write_evidence(); self.assert_rejected_cleanly()

    def test_shape_change_floating_pose_and_applied_rotation_are_rejected(self):
        previous = copy.deepcopy(self.meshes)
        self.meshes["body_candidate"]["vertices"][3][1] += .01
        self.write_evidence(); self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(previous)
        self.meshes["lid_candidate"]["vertices"] = [[x, y, z + .01] for x, y, z in self.meshes["lid_candidate"]["vertices"]]
        self.write_evidence(); self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(previous)
        self.meshes["body_candidate"]["cad_metadata"]["object_rotation_euler_radians"] = [0, 0, 0]
        self.write_evidence(); self.assert_rejected_cleanly()

    def test_native_axis_overlay_context_and_four_actual_view_records_are_required(self):
        previous = copy.deepcopy(self.verification)
        self.verification["analysis_contexts"]["body_baseline"]["mode"] = "OBJECT"
        self.write_evidence(); self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(previous)
        self.by_pose["lid_candidate"]["axis"] = "POS_Z"
        self.write_evidence(); self.assert_rejected_cleanly()
        self.by_pose["lid_candidate"]["axis"] = "NEG_Z"
        self.run["records"][-1]["slug"] = "unrelated-view"
        self.write_evidence(); self.assert_rejected_cleanly()

    def test_contact_area_raised_downward_area_boundary_band_and_gpu_claims_are_not_interchangeable(self):
        previous = copy.deepcopy(self.poses)
        for change in ("bed", "raised", "boundary", "gpu"):
            with self.subTest(change=change):
                self.poses.clear(); self.poses.update(copy.deepcopy(previous))
                candidate = self.poses["lid_candidate"]
                stats = candidate["derived_polygon_statistics"]["summary"]
                if change == "bed":
                    stats["bed_contact"]["area_mm2"] = stats["all"]["area_mm2"]
                elif change == "raised":
                    stats["downward_not_bed_contact"]["area_mm2"] = 0
                elif change == "boundary":
                    stats["angle_boundary_band"]["count"] += 1
                else:
                    candidate["gpu_visible_face_count"] = 99
                self.write_evidence(); self.assert_rejected_cleanly()

    def test_polygon_mapping_and_reported_world_normal_cannot_fabricate_native_face_statistics(self):
        previous = copy.deepcopy(self.meshes)
        self.meshes["lid_baseline"]["polygon_normals_world"][0] = [0, 0, 1]
        self.write_evidence(); self.assert_rejected_cleanly()
        self.meshes = copy.deepcopy(previous)
        self.meshes["body_candidate"]["triangle_polygon_indices"][0] = 1
        self.write_evidence(); self.assert_rejected_cleanly()

    def test_tools_stay_hidden_unchanged_and_two_finished_candidate_objects_are_reopened(self):
        previous = copy.deepcopy(self.verification)
        for field in ("geometry_modified", "rotation_applied_to_mesh", "slicer_checked", "printed", "support_generation_performed"):
            with self.subTest(field=field):
                self.verification = copy.deepcopy(previous); self.verification[field] = True
                self.write_evidence(); self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(previous)
        self.verification["final_tools"]["SnapTool"]["local_mesh_sha256"] = "0" * 64
        self.write_evidence(); self.assert_rejected_cleanly()
        self.verification = copy.deepcopy(previous)
        self.verification["final_objects"]["FlangeTool"]["hidden"] = False
        self.write_evidence(); self.assert_rejected_cleanly()

    def test_script_and_primary_fact_bindings_cannot_be_omitted(self):
        previous = copy.deepcopy(self.manifest)
        self.manifest["files"] = [r for r in self.manifest["files"] if not r["source"].endswith("overhang_checks.py")]
        self.write_evidence(); self.assert_rejected_cleanly()
        self.manifest = copy.deepcopy(previous); self.manifest["dataBindings"].pop()
        self.write_evidence(); self.assert_rejected_cleanly()


class SnapfitCandidateStlImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-snap-stl-import-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning/evidence/07" / SNAP_EXPORT_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning/catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons": [{"id": "07", "steps": [
            {"id": "07-04", "figures": [], "guide": []}]}]}), encoding="utf-8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning/progress.json"
        self.progress.write_bytes(b'{"revision":18}')
        fs = importlib.util.spec_from_file_location("snap_stl_import_fixtures", Path(__file__).with_name("test_snapfit_stl_checks.py"))
        self.fixture = importlib.util.module_from_spec(fs); fs.loader.exec_module(self.fixture)
        self.checks = self.fixture.checks
        self.source_dir = self.project / "learning/evidence/07" / OVERHANG_RUN_ID
        original_dir = IMPORTER.PROJECT / "learning/evidence/07" / OVERHANG_RUN_ID
        self.source = self.source_dir / "demo-files/u07_print_orientation_v001.blend"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes((original_dir / "demo-files" / self.source.name).read_bytes())
        # These source evidence files retain their original provenance bytes;
        # their fixed hashes are not rewritten to invent a fixture checkpoint.
        for name in ("print-orientation-record-v001.json", "verification.json", "body_candidate_mesh.json", "lid_candidate_mesh.json"):
            (self.source_dir / name).write_bytes((original_dir / name).read_bytes())
        self.prior = json.loads((self.source_dir / "verification.json").read_text(encoding="utf-8"))
        self.orientation = self.source_dir / "print-orientation-record-v001.json"
        self.opened = self.run_dir / "demo-files/sources" / self.source.name
        self.opened.parent.mkdir(parents=True); self.opened.write_bytes(self.source.read_bytes())
        (self.run_dir / "demo-files/exports").mkdir()
        self.meshes = {}
        self.exports = []
        self.export_options = {"only_selected": True, "global_scale": 1.0, "use_scene_unit": False, "apply_modifiers": True,
            "forward_axis": "Y", "up_axis": "Z", "ascii_format": False, "use_batch": False, "evaluation_mode": "DAG_EVAL_RENDER"}
        self.import_options = {"global_scale": 1.0, "use_scene_unit": False, "forward_axis": "Y", "up_axis": "Z"}
        for part in ("body", "lid"):
            raw = json.loads((self.source_dir / (part + "_candidate_mesh.json")).read_text(encoding="utf-8"))
            raw["cad_metadata"]["object_axis_dimensions_mm"] = [60, 44.5, 30] if part == "body" else [60, 46, 7.000000953674316]
            self.meshes["source_" + part] = raw
            path = self.run_dir / ("demo-files/exports/u07_snap_" + part + "_v001.stl")
            path.write_bytes(self.fixture.binary_stl(raw["vertices"], raw["triangles"]))
            mesh = self.checks.read_stl(path)
            imported = {"vertices": mesh["vertices"], "triangles": mesh["triangles"],
                "cad_metadata": PrintOrientationImportTests.cad(part.title() + "_STL", [0, 0, 0], [0, 0, 0])}
            imported["cad_metadata"]["object_axis_dimensions_mm"] = mesh["dimensions_mm"]
            # Native mathutils matrices contain floats, including exact 0/1.
            # Keep the valid fixture faithful so int-only comparison cannot
            # accidentally reject a real identity matrix after STL import.
            imported["cad_metadata"]["matrix_world"] = [[float(value) for value in row]
                                                        for row in imported["cad_metadata"]["matrix_world"]]
            self.meshes["reimport_" + part] = imported
            self.exports.append({"kind": part, "source_object": part.title(), "selected_names": [part.title()], "stl_path": str(path),
                "source_item_dimensions_mm": raw["cad_metadata"]["object_axis_dimensions_mm"],
                "export_options": copy.deepcopy(self.export_options), "import_options": copy.deepcopy(self.import_options),
                "reimport_object": part.title() + "_STL",
                "export_operator": {"idname": "WM_OT_stl_export", "options": copy.deepcopy(self.export_options), "filepath": str(path),
                    "captured_at": "live_file_browser_before_native_confirm", "operator_history_available": False,
                    "execution_verified_by": "native UI confirmation and new binary STL readback"},
                "import_operator": {"idname": "WM_OT_stl_import", "options": copy.deepcopy(self.import_options), "filepath": str(path),
                    "captured_at": "live_file_browser_before_native_confirm", "operator_history_available": False,
                    "execution_verified_by": "native UI confirmation and newly created mesh readback"}})
        self.source_objects = {}
        for name, value in self.prior["final_objects"].items():
            item = {key: copy.deepcopy(value[key]) for key in ("type", "scale", "location_mm", "rotation_euler_radians", "modifier_count", "matrix_world")}
            item["hidden"] = name != "Lid"
            self.source_objects[name] = item
        self.verification = {"passed": True, "kind": "snapfit_stl_exports", "source_scene_path": str(self.source),
            "source_scene_sha256": self.digest(self.source), "opened_scene_path": str(self.opened), "opened_scene_sha256": self.digest(self.opened),
            "source_unchanged": True, "opened_copy_unchanged": True, "source_orientation_record_path": str(self.orientation),
            "source_orientation_record_sha256": self.digest(self.orientation), "source_orientation_record_unchanged": True,
            "source_body": self.prior["poses"]["body_candidate"], "source_lid": self.prior["poses"]["lid_candidate"],
            "source_layout": self.prior["layout"], "source_tools": self.prior["final_tools"], "source_objects": self.source_objects,
            "exports": self.exports, "reimport_verified": True, "exported_stl": True, "saved_new_scene": False, "geometry_modified": False,
            "rotation_applied_to_mesh": False, "source_overhang_comparison_completed": True, "mesh_analysis_overhang_checked": False,
            "stl_unit_interpretation": "STL unitless; mm coordinates, retaining candidate world placement",
            "numericComparison": {"dimensionsAbsMm": 1e-4, "coordinateWeldMm": 1e-5, "volumeRelative": 1e-5, "purpose": "Numeric only; not print/fit qualification"}}
        for field in ("strength_analysis_performed", "fit_qualification", "slicer_checked", "printed", "fit_tested", "support_generation_performed"):
            self.verification[field] = False
        for field in ("material_grade", "epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces", "physical_measurements",
                      "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm", "support_required",
                      "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified"):
            self.verification[field] = None
        self.refresh_geometry()
        self.export_record = {"schema_version": 1, "lesson_step": "07-04", "stage": "digital_stl_export_only", "recordedAt": "2026-10-25T17:00:00Z",
            "source_scene": {"path": str(self.source), "sha256": self.digest(self.source)},
            "source_orientation_record": {"path": str(self.orientation), "sha256": self.digest(self.orientation)}, "exports": self.exports,
            **{key: self.verification[key] for key in ("reimport_body", "reimport_lid", "reimport_layout")},
            "saved_new_scene": False, "printed": False, "fit_tested": False, "slicer_checked": False, "physical_measurements": None,
            "fit_results": None, "qualified_clearance_mm": None, "qualified_strength_N": None, "support_required": None, "final_print_orientation_approved": None}
        self.record_path = self.run_dir / "stl-export-record-v001.json"
        self.verification["export_record_path"] = str(self.record_path)
        image = self.run_dir / "07-04-01-stl.png"; image.write_bytes(png_bytes())
        self.run = {"blender": "5.9.9 TEST", "buildHash": "test-build", "scenario": "scenarios/lesson07_snap_export.py", "records": [
            {"seq": 1, "step": "07-04", "slug": "exports-verified", "file": image.name, "recordedAt": "2026-10-25T17:00:00Z",
             "action": "原生分件STL與實際重匯入核對", "observed": "數位準備，支撐與實體結果未定", "width": 3, "height": 2, "sha256": self.digest(image)}]}
        self.runner = {"status": "completed", "blenderExitCode": 0, "workspacesUnchanged": True, "runErrors": [], "scenario": "lesson07_snap_export",
            "outputDir": str(self.run_dir), "startedAt": "2026-10-25T16:59:00Z", "endedAt": "2026-10-25T17:01:00Z"}
        folder = self.run_dir / "source-snapshot"; folder.mkdir()
        files = []
        for relative in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
            "learning/tutor/scenarios/lesson07_snap_export.py", "learning/tutor/scenarios/snapfit_stl_checks.py", "learning/tutor/scenarios/stl_checks.py",
            "learning/tutor/scenarios/overhang_checks.py", "learning/tutor/scenarios/snapfit_checks.py", "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py"):
            target = folder / Path(relative).name; target.write_text("# isolated snapshot fixture: " + relative, encoding="utf-8")
            files.append({"source": relative, "snapshot": "source-snapshot/" + target.name, "sha256": self.digest(target)})
        bindings = []
        for relative, expected in IMPORTER.RUNS[SNAP_EXPORT_RUN_ID]["data_bindings"].items():
            original, target = self.project / relative, self.run_dir / expected["snapshot"]
            target.write_bytes(original.read_bytes()); self.assertEqual(self.digest(original), expected["sha256"])
            bindings.append({"source": relative, **expected})
        self.manifest = {"recordedAt": "2026-10-25T16:59:00Z", "files": files, "dataBindings": bindings,
            "sourceScene": str(self.source), "sourceCopy": str(self.opened), "sourceSha256": self.digest(self.source)}
        self.write_evidence()

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def measured_layout(self, meshes):
        parts = []
        for part in ("body", "lid"):
            raw = meshes[part]
            bounds = {key: [fn(v[a] for v in raw["vertices"]) for a in range(3)] for key, fn in (("min", min), ("max", max))}
            parts.append({"passed": True, "pose": "candidate", "part_kind": part, "bounds_mm": bounds, "minimum_world_z_mm": bounds["min"][2]})
        return self.checks.validate_export_layout(*parts)

    def refresh_geometry(self):
        parsed = {}
        final = {}
        for entry in self.exports:
            part = entry["kind"]; path = Path(entry["stl_path"])
            mesh = self.checks.read_stl(path); parsed[part] = mesh
            for field, key in (("stl_bytes", "byte_size"), ("stl_dimensions_mm", "dimensions_mm"), ("stl_bounds_mm", "bounds_mm"),
                ("stl_triangles", "triangle_count"), ("stl_non_manifold_edges", "non_manifold_edges"), ("stl_connected_shells", "connected_shells"),
                ("stl_genus", "genus"), ("stl_volume_mm3", "volume_mm3"), ("stl_sha256", "stl_sha256")):
                entry[field] = mesh[key]
            entry["stl_verification"] = self.checks.validate_snapfit_stl(path, part, self.prior, self.meshes["source_" + part])
            imported = self.meshes["reimport_" + part]
            self.verification["reimport_" + part] = self.checks.validate_snapfit_export_mesh(imported["vertices"], imported["triangles"], part, self.prior, self.meshes["source_" + part])
            cad = imported["cad_metadata"]
            final[part.title() + "_STL"] = {"type": "MESH", "hidden": False, "scale": [1, 1, 1], "modifier_count": 0,
                "location_mm": cad["object_location_mm"], "rotation_euler_radians": cad["object_rotation_euler_radians"],
                "object_axis_dimensions_mm": cad["object_axis_dimensions_mm"], "matrix_world": cad["matrix_world"]}
        # The native scenario uses overhang_checks' historical layout schema.
        scenarios = str(MODULE_PATH.parent / "scenarios")
        if scenarios not in sys.path: sys.path.insert(0, scenarios)
        from overhang_checks import validate_layout
        def old_layout(meshes):
            args=[]
            for kind in ("body", "lid"):
                mesh=meshes[kind]; bounds={key:[fn(v[a] for v in mesh["vertices"]) for a in range(3)] for key,fn in (("min",min),("max",max))}
                args.append({"passed":True,"pose":"candidate","part_kind":kind,"bounds_mm":bounds,"minimum_world_z_mm":bounds['min'][2]})
            return validate_layout(*args)
        self.verification["stl_layout"] = old_layout(parsed)
        self.verification["reimport_layout"] = old_layout({kind:self.meshes['reimport_'+kind] for kind in ('body','lid')})
        self.verification["final_objects"] = final

    def write_evidence(self):
        self.record_path.write_text(json.dumps(self.export_record), encoding="utf-8")
        self.verification["export_record_sha256"] = self.digest(self.record_path)
        for name, value in (("run.json", self.run), ("runner-status.json", self.runner), ("verification.json", self.verification), ("source-snapshot/manifest.json", self.manifest)):
            (self.run_dir / name).write_text(json.dumps(value), encoding="utf-8")
        for entry in self.exports:
            (self.run_dir / (entry["kind"] + "-stl-verification.json")).write_text(json.dumps(entry["stl_verification"]), encoding="utf-8")
        for role, raw in self.meshes.items():
            (self.run_dir / (role + "_mesh.json")).write_text(json.dumps(raw), encoding="utf-8")

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError): IMPORTER.import_run(SNAP_EXPORT_RUN_ID, self.project)
        self.assertEqual(self.original_catalog, self.catalog_path.read_bytes())
        self.assertFalse((self.run_dir.parent / (SNAP_EXPORT_RUN_ID + ".json")).exists())
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_exports_preserve_candidate_world_pose_and_only_complete_digital_stage(self):
        result = IMPORTER.import_run(SNAP_EXPORT_RUN_ID, self.project)
        self.assertEqual((result["steps"], result["records"]), (1, 1))
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        self.assertEqual(len(metadata["geometryEvidence"]), 4)
        self.assertEqual(len(metadata["dataEvidence"]), 3)
        self.assertIsNone(metadata["verification"]["support_required"])
        self.assertEqual(self.progress.read_bytes(), b'{"revision":18}')

    def test_valid_subdivision_is_accepted_without_requiring_source_triangle_identity(self):
        entry=self.exports[0];raw=self.meshes['source_body'];vertices,triangles=self.fixture.subdivide(raw['vertices'],raw['triangles'])
        Path(entry['stl_path']).write_bytes(self.fixture.binary_stl(vertices,triangles))
        mesh=self.checks.read_stl(entry['stl_path']);self.meshes['reimport_body']['vertices']=mesh['vertices'];self.meshes['reimport_body']['triangles']=mesh['triangles']
        self.refresh_geometry()
        self.export_record.update({key:self.verification[key] for key in ('reimport_body','reimport_lid','reimport_layout')})
        self.write_evidence()
        self.assertEqual(IMPORTER.import_run(SNAP_EXPORT_RUN_ID,self.project)['steps'],1)

    def test_fixed_source_orientation_raw_snapshots_and_export_files_cannot_change(self):
        for path in (self.source,self.orientation,self.opened,self.source_dir/'verification.json',self.source_dir/'body_candidate_mesh.json',
                     self.run_dir/'source-snapshot/source-orientation-record-v001.json',Path(self.exports[0]['stl_path'])):
            with self.subTest(path=path):
                previous=path.read_bytes();path.write_bytes(previous+b'changed');self.assert_rejected_cleanly();path.write_bytes(previous)

    def test_world_dimensions_cannot_be_replaced_with_source_object_axis_dimensions(self):
        self.exports[0]['stl_dimensions_mm']=self.exports[0]['source_item_dimensions_mm']
        self.write_evidence();self.assert_rejected_cleanly()

    def test_only_selected_binary_mm_and_actual_native_operator_options_are_required(self):
        previous=copy.deepcopy(self.exports[0])
        for field,value in (('only_selected',False),('use_scene_unit',True),('global_scale',1000),('ascii_format',True),('forward_axis','X')):
            with self.subTest(field=field):
                self.exports[0].clear();self.exports[0].update(copy.deepcopy(previous));self.exports[0]['export_options'][field]=value
                self.write_evidence();self.assert_rejected_cleanly()
        self.exports[0].clear();self.exports[0].update(copy.deepcopy(previous));self.exports[0]['selected_names']=['Body','SnapTool']
        self.write_evidence();self.assert_rejected_cleanly()

    def test_native_operator_history_is_optional_but_cannot_be_fabricated_or_contradict_live_dialog(self):
        operator = self.exports[0]['export_operator']
        operator['operator_history_available'] = True
        self.write_evidence(); self.assert_rejected_cleanly()
        operator['operator_history_entry'] = {key:copy.deepcopy(operator[key]) for key in ('idname','options','filepath')}
        self.write_evidence()
        self.assertEqual(IMPORTER.import_run(SNAP_EXPORT_RUN_ID,self.project)['steps'],1)

    def test_actual_reimport_must_keep_world_position_origin_zero_and_complete_source_surface(self):
        previous=copy.deepcopy(self.meshes)
        self.meshes['reimport_body']['vertices']=[[x+.01,y,z] for x,y,z in self.meshes['reimport_body']['vertices']]
        self.write_evidence();self.assert_rejected_cleanly();self.meshes=copy.deepcopy(previous)
        self.meshes['reimport_body']['cad_metadata']['object_rotation_euler_radians']=[0,math.pi/2,0]
        self.write_evidence();self.assert_rejected_cleanly();self.meshes=copy.deepcopy(previous)
        self.meshes['source_body']['vertices'][0][1]+=.01
        self.write_evidence();self.assert_rejected_cleanly()

    def test_support_material_strain_force_and_physical_qualifications_stay_null(self):
        previous=copy.deepcopy(self.verification)
        for field in ('epsilon_allow','Q','required_deflection_mm','delta_allow_mm','forces','physical_measurements','fit_results',
                      'qualified_strength_N','qualified_clearance_mm','support_required','final_print_orientation_approved'):
            with self.subTest(field=field):
                self.verification=copy.deepcopy(previous);self.verification[field]=1;self.write_evidence();self.assert_rejected_cleanly()

    def test_no_new_scene_no_new_analysis_and_no_printed_fit_flags_are_allowed(self):
        previous=copy.deepcopy(self.verification)
        for field in ('saved_new_scene','geometry_modified','rotation_applied_to_mesh','mesh_analysis_overhang_checked','slicer_checked','printed','fit_tested'):
            with self.subTest(field=field):
                self.verification=copy.deepcopy(previous);self.verification[field]=True;self.write_evidence();self.assert_rejected_cleanly()
        self.verification=copy.deepcopy(previous);self.write_evidence();(self.run_dir/'demo-files/unrequested.blend').write_bytes(b'BLENDER-extra')
        self.assert_rejected_cleanly()

    def test_export_record_cannot_fill_physical_results_or_rename_the_stage_as_printed(self):
        previous=copy.deepcopy(self.export_record)
        for field,value in (('physical_measurements',{'width_mm':30}),('fit_results',{'passes':True}),('stage','printed'),('qualified_clearance_mm',.3)):
            with self.subTest(field=field):
                self.export_record=copy.deepcopy(previous);self.export_record[field]=value;self.write_evidence();self.assert_rejected_cleanly()

    def test_hidden_source_tools_final_inventory_and_complete_snapshot_chain_are_required(self):
        self.verification['source_objects']['SnapTool']['hidden']=False;self.write_evidence();self.assert_rejected_cleanly()
        self.verification['source_objects']['SnapTool']['hidden']=True
        self.verification['final_objects']['SnapTool']={'type':'MESH','hidden':False};self.write_evidence();self.assert_rejected_cleanly()
        del self.verification['final_objects']['SnapTool']
        self.manifest['files']=[x for x in self.manifest['files'] if not x['source'].endswith('snapfit_stl_checks.py')]
        self.write_evidence();self.assert_rejected_cleanly()


class CouponStlImportTests(unittest.TestCase):
    """Native-like source references plus real binary STL in temporary storage."""
    names = ("A_L19", "B_L17", "C_L21")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="coupon-stl-import-"); self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.run_dir = self.project / "learning/evidence/07" / COUPON_EXPORT_RUN_ID
        self.run_dir.mkdir(parents=True)
        self.catalog_path = self.project / "learning/catalog.json"
        self.catalog_path.write_text(json.dumps({"lessons":[{"id":"07","steps":[{"id":"07-05","figures":[],"guide":[]}]}]}), encoding="utf8")
        self.original_catalog = self.catalog_path.read_bytes()
        self.progress = self.project / "learning/progress.json"; self.progress.write_bytes(b'{"revision":5}')
        fs = importlib.util.spec_from_file_location("coupon_stl_import_fixtures",Path(__file__).with_name("test_coupon_stl_checks.py"))
        self.fixture = importlib.util.module_from_spec(fs); fs.loader.exec_module(self.fixture); self.checks = self.fixture.checks
        self.source_dir = self.project / "learning/evidence/07" / COUPONS_RUN_ID
        self.source = self.source_dir / "demo-files/u07_cantilever_length_coupons_v001.blend"
        self.source.parent.mkdir(parents=True)
        original_dir = IMPORTER.PROJECT / "learning/evidence/07" / COUPONS_RUN_ID
        self.source.write_bytes((original_dir / "demo-files" / self.source.name).read_bytes())
        spec = IMPORTER.RUNS[COUPON_EXPORT_RUN_ID]
        for relative in spec["data_bindings"]:
            path = self.project / relative; path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((IMPORTER.PROJECT / relative).read_bytes())
        self.prior = json.loads((self.source_dir/"verification.json").read_text("utf8"))
        self.tool = json.loads((self.source_dir/"source_snap_tool_mesh.json").read_text("utf8"))
        self.source_record = self.source_dir/"coupon-record-v001.json"
        self.plan = self.project/"learning/plans/07-05-coupon-length-draft-v001.json"
        self.opened = self.run_dir/"demo-files/sources"/self.source.name
        self.opened.parent.mkdir(parents=True); self.opened.write_bytes(self.source.read_bytes())
        (self.run_dir/"demo-files/exports").mkdir()
        self.export_options = dict(only_selected=True,global_scale=1.,use_scene_unit=False,apply_modifiers=True,
            forward_axis="Y",up_axis="Z",ascii_format=False,use_batch=False,evaluation_mode="DAG_EVAL_RENDER")
        self.import_options = dict(global_scale=1.,use_scene_unit=False,forward_axis="Y",up_axis="Z")
        self.meshes,self.exports = {},[]
        for name in self.names:
            raw=json.loads((self.source_dir/(name+"_candidate_mesh.json")).read_text("utf8"))
            self.meshes['source_'+name]=raw
            path=self.run_dir/("demo-files/exports/u07_"+name+"_v001.stl")
            path.write_bytes(self.fixture.binary_stl(raw['vertices'],raw['triangles']))
            mesh=self.checks.read_stl(path)
            cad=PrintOrientationImportTests.cad(name+'_STL',[0,0,0],[0,0,0])
            cad['matrix_world']=[[float(x) for x in row] for row in cad['matrix_world']]
            cad['object_axis_dimensions_mm']=mesh['dimensions_mm']
            self.meshes['reimport_'+name]={'vertices':mesh['vertices'],'triangles':mesh['triangles'],'cad_metadata':cad}
            entry=dict(kind=name,variant=name,source_object=name,selected_names=[name],stl_path=str(path),reimport_object=name+'_STL',
                source_item_dimensions_mm=raw['cad_metadata']['object_axis_dimensions_mm'],
                export_options=copy.deepcopy(self.export_options),import_options=copy.deepcopy(self.import_options))
            for prefix,idname,execution in [('export','WM_OT_stl_export','native UI confirmation and new binary STL readback'),
                ('import','WM_OT_stl_import','native UI confirmation and newly created mesh readback')]:
                entry[prefix+'_operator']=dict(idname=idname,options=copy.deepcopy(entry[prefix+'_options']),filepath=str(path),
                    captured_at='live_file_browser_before_native_confirm',operator_history_available=False,execution_verified_by=execution)
            self.exports.append(entry)
        source_objects=copy.deepcopy(self.prior['final_objects'])
        for name,item in source_objects.items():
            item['data_name']=item['mesh_data_name'];item['hidden']=name!='C_L21'
        self.v=dict(passed=True,kind='cantilever_coupon_stl_exports',source_scene_path=str(self.source),source_scene_sha256=self.digest(self.source),
            opened_scene_path=str(self.opened),opened_scene_sha256=self.digest(self.opened),source_unchanged=True,opened_copy_unchanged=True,
            source_coupon_record_path=str(self.source_record),source_coupon_record_sha256=self.digest(self.source_record),source_coupon_record_unchanged=True,
            draft_plan_path=str(self.plan),draft_plan_sha256=self.digest(self.plan),source_candidates=self.prior['candidates'],source_layout=self.prior['layout'],
            source_objects=source_objects,exports=self.exports,reimport_verified=True,exported_stl=True,
            reimport_mesh_datablocks_created=True,new_specimen_design_created=False,geometry_scope='Native reimport creates new mesh data but no new specimen design',
            stl_unit_interpretation='STL unitless; numeric coordinates interpreted as millimetres; original candidate world positions retained',
            numericComparison=dict(dimensionsAbsMm=1e-4,coordinateWeldMm=1e-5,volumeRelative=1e-5,purpose='Numerical reconstruction only; not manufacturing or fit qualification'))
        for field in ('saved_new_scene','geometry_modified','source_geometry_modified','new_geometry_created','full_box_modified','rotation_applied_to_mesh',
            'mesh_analysis_overhang_checked','improvement_assessed','strength_analysis_performed','deformation_analysis_performed','fit_qualification',
            'slicer_checked','printed','fit_tested','support_generation_performed'):self.v[field]=False
        for field in ('material_grade','epsilon_allow','Q','effective_mechanical_length_mm','full_box_boundary_equivalence','anchor_clamping_or_fixture',
            'required_deflection_mm','delta_allow_mm','forces','physical_measurements','fit_results','physical_interference','qualified_strength_N',
            'qualified_clearance_mm','improvement_validated','support_required','final_print_orientation_approved','slicer_support_settings','bridge_or_support_qualified'):self.v[field]=None
        self.refresh_geometry()
        self.record=dict(schema_version=1,lesson_step='07-05',stage='standalone_coupon_digital_stl_export_only',recordedAt='2026-10-25T17:00:00Z',
            source_scene=dict(path=str(self.source),sha256=self.digest(self.source)),
            source_coupon_record=dict(path=str(self.source_record),sha256=self.digest(self.source_record)),draft_plan=dict(path=str(self.plan),sha256=self.digest(self.plan)),
            exports=self.exports,reimport=self.v['reimport'],reimport_layout=self.v['reimport_layout'],saved_new_scene=False,geometry_modified=False,
            full_box_modified=False,exported_stl=True,printed=False,fit_tested=False,slicer_checked=False,
            geometry_scope='No new specimen design or source shape edit; actual STL reimport creates three new mesh datablocks from the retained world vertices.',
            reimport_mesh_datablocks_created=True,new_specimen_design_created=False,material_grade=None,epsilon_allow=None,
            effective_mechanical_length_mm=None,improvement_validated=None,physical_measurements=None,fit_results=None,qualified_clearance_mm=None,
            qualified_strength_N=None,support_required=None,final_print_orientation_approved=None)
        self.record_path=self.run_dir/'coupon-stl-export-record-v001.json';self.v['export_record_path']=str(self.record_path)
        self.run=dict(blender='5.9.9 TEST',buildHash='test-build',scenario='scenarios/lesson07_coupon_export.py',records=[])
        for name in self.names:
            for suffix in ('-source-selected','-source-profile','-export-options','-stl-checked','-import-dialog','-reimport-dimensions','-reimport-profile','-reimport-non-manifold'):
                seq=len(self.run['records'])+1;path=self.run_dir/('%02d.png'%seq);path.write_bytes(png_bytes())
                self.run['records'].append(dict(seq=seq,step='07-05',slug=name+suffix,file=path.name,recordedAt='2026-10-25T17:00:00Z',
                    action='原生STL核對',observed='未填實體結果',width=3,height=2,sha256=self.digest(path)))
        self.runner=dict(status='completed',blenderExitCode=0,workspacesUnchanged=True,runErrors=[],scenario='lesson07_coupon_export',outputDir=str(self.run_dir),
            startedAt='2026-10-25T16:59:00Z',endedAt='2026-10-25T17:01:00Z')
        folder=self.run_dir/'source-snapshot';folder.mkdir();files=[]
        for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py',
            'learning/tutor/scenarios/lesson07_coupon_export.py','learning/tutor/scenarios/coupon_stl_checks.py','learning/tutor/scenarios/coupon_checks.py',
            'learning/tutor/scenarios/snapfit_stl_checks.py','learning/tutor/scenarios/overhang_checks.py','learning/tutor/scenarios/snapfit_checks.py',
            'learning/tutor/scenarios/stl_checks.py','learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py'):
            target=folder/Path(relative).name;target.write_text('# isolated snapshot fixture: '+relative,encoding='utf8')
            files.append(dict(source=relative,snapshot='source-snapshot/'+target.name,sha256=self.digest(target)))
        bindings=[]
        for relative,expected in spec['data_bindings'].items():
            original,target=self.project/relative,self.run_dir/expected['snapshot'];target.write_bytes(original.read_bytes())
            self.assertEqual(self.digest(original),expected['sha256']);bindings.append(dict(source=relative,**expected))
        self.manifest=dict(recordedAt='2026-10-25T16:59:00Z',files=files,dataBindings=bindings,sourceScene=str(self.source),sourceCopy=str(self.opened),sourceSha256=self.digest(self.source))
        self.write_evidence()

    @staticmethod
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

    def refresh_geometry(self):
        stls,imported_results,final={},{},{}
        for entry in self.exports:
            name=entry['kind'];path=Path(entry['stl_path']);mesh=self.checks.read_stl(path)
            for field,key in (('stl_bytes','byte_size'),('stl_dimensions_mm','dimensions_mm'),('stl_bounds_mm','bounds_mm'),('stl_triangles','triangle_count'),
                ('stl_non_manifold_edges','non_manifold_edges'),('stl_connected_shells','connected_shells'),('stl_genus','genus'),('stl_volume_mm3','volume_mm3'),('stl_sha256','stl_sha256')):entry[field]=mesh[key]
            source=self.meshes['source_'+name];raw=self.meshes['reimport_'+name]
            entry['stl_verification']=self.checks.validate_coupon_stl(path,name,self.prior,source,self.tool);stls[name]=entry['stl_verification']
            imported_results[name]=self.checks.validate_coupon_export_mesh(raw['vertices'],raw['triangles'],name,self.prior,source,self.tool)
            cad=raw['cad_metadata'];data_name=name+'_ImportedData'
            final[name+'_STL']=dict(type='MESH',hidden=False,scale=[1.,1.,1.],modifier_count=0,location_mm=cad['object_location_mm'],
                rotation_euler_radians=cad['object_rotation_euler_radians'],matrix_world=cad['matrix_world'],object_axis_dimensions_mm=cad['object_axis_dimensions_mm'],
                mesh_data_name=data_name,data_name=data_name)
        self.v['reimport']=imported_results;self.v['stl_layout']=self.checks.validate_export_layout(stls,self.prior)
        self.v['reimport_layout']=self.checks.validate_export_layout(imported_results,self.prior);self.v['final_objects']=final
        if hasattr(self,'record'):self.record.update(reimport=self.v['reimport'],reimport_layout=self.v['reimport_layout'])

    def write_evidence(self):
        self.record_path.write_text(json.dumps(self.record),encoding='utf8');self.v['export_record_sha256']=self.digest(self.record_path)
        for name,value in [('run.json',self.run),('runner-status.json',self.runner),('verification.json',self.v),('source-snapshot/manifest.json',self.manifest)]:
            (self.run_dir/name).write_text(json.dumps(value),encoding='utf8')
        for role,raw in self.meshes.items():(self.run_dir/(role+'_mesh.json')).write_text(json.dumps(raw),encoding='utf8')
        for entry in self.exports:(self.run_dir/(entry['kind']+'-stl-verification.json')).write_text(json.dumps(entry['stl_verification']),encoding='utf8')

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):IMPORTER.import_run(COUPON_EXPORT_RUN_ID,self.project)
        self.assertEqual(self.original_catalog,self.catalog_path.read_bytes());self.assertEqual(self.progress.read_bytes(),b'{"revision":5}')
        self.assertFalse((self.run_dir.parent/(COUPON_EXPORT_RUN_ID+'.json')).exists())

    def test_three_exports_are_only_digital_stage_with_unchanged_progress_and_actual_variant_lengths(self):
        result=IMPORTER.import_run(COUPON_EXPORT_RUN_ID,self.project)
        self.assertEqual((result['steps'],result['records']),(1,24))
        metadata=json.loads(Path(result['metadata']).read_text('utf8'));self.assertEqual(len(metadata['geometryEvidence']),6);self.assertEqual(len(metadata['dataEvidence']),4)
        for name,expected in zip(self.names,[19.,17.,21.]):self.assertAlmostEqual(self.v['reimport'][name]['L_geometry_mm'],expected,places=4)
        self.assertEqual(self.progress.read_bytes(),b'{"revision":5}')
        self.assertTrue(all(self.v['reimport'][n]['reference_pose_metadata']['object_rotation_euler_radians'][1]>1.5 for n in self.names))
        self.assertEqual(self.meshes['reimport_A_L19']['cad_metadata']['object_rotation_euler_radians'],[0,0,0])

    def test_legal_retriangulation_and_native_float_identity_are_accepted(self):
        entry=self.exports[1];raw=self.meshes['source_B_L17'];v,t=self.fixture.subdivide(raw['vertices'],raw['triangles'])
        v.reverse();t=[tuple(len(v)-1-i for i in face) for face in reversed(t)]
        Path(entry['stl_path']).write_bytes(self.fixture.binary_stl(v,t));mesh=self.checks.read_stl(entry['stl_path'])
        self.meshes['reimport_B_L17'].update(vertices=mesh['vertices'],triangles=mesh['triangles'])
        self.refresh_geometry();self.write_evidence()
        self.assertEqual(IMPORTER.import_run(COUPON_EXPORT_RUN_ID,self.project)['steps'],1)

    def test_fixed_scene_record_plan_candidate_tool_snapshot_and_stl_cannot_be_tampered(self):
        for path in (self.source,self.opened,self.source_record,self.plan,self.source_dir/'verification.json',self.source_dir/'source_snap_tool_mesh.json',
            self.source_dir/'B_L17_candidate_mesh.json',self.run_dir/'source-snapshot/source-C_L21-candidate-mesh.json',Path(self.exports[2]['stl_path'])):
            with self.subTest(path=path):
                before=path.read_bytes();path.write_bytes(before+b'changed');self.assert_rejected_cleanly();path.write_bytes(before)

    def test_world_dimensions_and_kind_variant_cannot_be_swapped(self):
        previous=copy.deepcopy(self.exports[0])
        for field,value in [('stl_dimensions_mm',self.exports[0]['source_item_dimensions_mm']),('source_item_dimensions_mm',self.exports[0]['stl_dimensions_mm']),('variant','B_L17')]:
            with self.subTest(field=field):
                self.exports[0].clear();self.exports[0].update(copy.deepcopy(previous));self.exports[0][field]=value;self.write_evidence();self.assert_rejected_cleanly()

    def test_only_selected_binary_scale_scene_unit_and_live_operator_must_match(self):
        previous=copy.deepcopy(self.exports[0])
        for field,value in [('only_selected',False),('global_scale',1000),('use_scene_unit',True),('ascii_format',True)]:
            with self.subTest(field=field):
                self.exports[0].clear();self.exports[0].update(copy.deepcopy(previous));self.exports[0]['export_options'][field]=value
                self.write_evidence();self.assert_rejected_cleanly()
        self.exports[0].clear();self.exports[0].update(copy.deepcopy(previous));self.exports[0]['selected_names']=['A_L19','Body'];self.write_evidence();self.assert_rejected_cleanly()

    def test_live_filebrowser_capture_cannot_be_replaced_with_fabricated_history(self):
        op=self.exports[0]['export_operator'];op['operator_history_entry']={};self.write_evidence();self.assert_rejected_cleanly()
        op['operator_history_available']=True;op['operator_history_entry']={k:copy.deepcopy(op[k]) for k in ('idname','options','filepath')}
        self.write_evidence();self.assertEqual(IMPORTER.import_run(COUPON_EXPORT_RUN_ID,self.project)['steps'],1)

    def test_reimport_R0_origin_scale_and_complete_world_surface_are_independent_of_reference_Ry90(self):
        before=copy.deepcopy(self.meshes)
        for field,value in [('object_location_mm',[1.,0.,0.]),('object_rotation_euler_radians',[0.,math.pi/2,0.]),('scale',[2.,2.,2.])]:
            with self.subTest(field=field):
                self.meshes=copy.deepcopy(before);self.meshes['reimport_C_L21']['cad_metadata'][field]=value;self.write_evidence();self.assert_rejected_cleanly()
        self.meshes=copy.deepcopy(before);point=list(self.meshes['reimport_A_L19']['vertices'][0]);point[0]+=.01;self.meshes['reimport_A_L19']['vertices'][0]=point;self.write_evidence();self.assert_rejected_cleanly()

    def test_hidden_originals_and_independent_reimport_inventory_are_protected(self):
        before=copy.deepcopy(self.v)
        for mutate in (lambda:self.v['source_objects']['Body'].__setitem__('hidden',False),
            lambda:self.v['source_objects']['SnapTool'].__setitem__('local_mesh_sha256','0'*64),
            lambda:self.v['source_objects']['A_L19'].__setitem__('matrix_world',[[1.]*4]*4),
            lambda:self.v['final_objects']['B_L17_STL'].update(mesh_data_name=self.v['final_objects']['A_L19_STL']['mesh_data_name'],data_name=self.v['final_objects']['A_L19_STL']['data_name'])):
            self.v=copy.deepcopy(before);mutate();self.write_evidence();self.assert_rejected_cleanly()

    def test_mechanical_fixture_counterpart_improvement_support_and_physical_results_remain_null(self):
        before=copy.deepcopy(self.v)
        for field in ('material_grade','epsilon_allow','Q','effective_mechanical_length_mm','full_box_boundary_equivalence','anchor_clamping_or_fixture',
            'required_deflection_mm','delta_allow_mm','forces','physical_measurements','fit_results','qualified_strength_N','qualified_clearance_mm','improvement_validated','support_required'):
            with self.subTest(field=field):
                self.v=copy.deepcopy(before);self.v[field]=1;self.write_evidence();self.assert_rejected_cleanly()

    def test_no_new_geometry_scene_or_analysis_physical_flags_and_strict_record_stage(self):
        before=copy.deepcopy(self.v)
        for field in ('saved_new_scene','geometry_modified','source_geometry_modified','new_geometry_created','full_box_modified','rotation_applied_to_mesh',
            'mesh_analysis_overhang_checked','improvement_assessed','strength_analysis_performed','printed','fit_tested','slicer_checked','new_specimen_design_created'):
            with self.subTest(field=field):
                self.v=copy.deepcopy(before);self.v[field]=True;self.write_evidence();self.assert_rejected_cleanly()
        self.v=copy.deepcopy(before);self.record['physical_measurements']={'length_mm':19};self.write_evidence();self.assert_rejected_cleanly()


class LengthCouponImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='blender-coupons-import-test-');self.addCleanup(self.temp.cleanup)
        self.project=Path(self.temp.name);self.run_dir=self.project/'learning/evidence/07'/COUPONS_RUN_ID;self.run_dir.mkdir(parents=True)
        self.catalog_path=self.project/'learning/catalog.json';self.catalog_path.write_text(json.dumps({'lessons':[{'id':'07','steps':[{'id':'07-05','guide':[],'figures':[]}]}]}),encoding='utf-8')
        self.original_catalog=self.catalog_path.read_bytes();self.progress=self.project/'learning/progress.json';self.progress.write_bytes(b'{"revision":18}')
        fs=importlib.util.spec_from_file_location('coupon_import_fixtures',Path(__file__).with_name('test_coupon_checks.py'));self.fixture=importlib.util.module_from_spec(fs);fs.loader.exec_module(self.fixture);self.checks=self.fixture.checks
        self.source=self.project/'learning/evidence/07'/OVERHANG_RUN_ID/'demo-files/u07_print_orientation_v001.blend';self.source.parent.mkdir(parents=True)
        self.source.write_bytes((IMPORTER.PROJECT/self.source.relative_to(self.project)).read_bytes())
        self.opened=self.run_dir/'demo-files/sources'/self.source.name;self.opened.parent.mkdir(parents=True);self.opened.write_bytes(self.source.read_bytes())
        folder=self.run_dir/'source-snapshot';folder.mkdir();bindings=[]
        for relative,expected in IMPORTER.RUNS[COUPONS_RUN_ID]['data_bindings'].items():
            original=self.project/relative;original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes((IMPORTER.PROJECT/relative).read_bytes());(self.run_dir/expected['snapshot']).write_bytes(original.read_bytes());bindings.append(dict(source=relative,**expected))
        self.plan_path=self.project/'learning/plans/07-05-coupon-length-draft-v001.json';self.plan=json.loads(self.plan_path.read_text(encoding='utf-8'))
        self.prior=json.loads((folder/'source-orientation-verification.json').read_text(encoding='utf-8'))
        self.source_objects={}
        for name,old in self.prior['final_objects'].items():
            item={k:copy.deepcopy(old[k]) for k in ('type','hidden','scale','modifier_count','matrix_world','location_mm','rotation_euler_radians')}
            item.update(object_axis_dimensions_mm=[9,4.6,24],mesh_data_name='source_'+name,local_mesh_sha256=self.prior['final_tools'][name]['local_mesh_sha256'] if name in self.prior['final_tools'] else hashlib.sha256(name.encode()).hexdigest())
            self.source_objects[name]=item
        self.final_sources=copy.deepcopy(self.source_objects)
        for item in self.final_sources.values():item['hidden']=True
        self.meshes={'source':self.fixture.source_fixture()};self.meshes['source']['polygons']=copy.deepcopy(self.meshes['source']['triangles'])
        self.meshes['source']['cad_metadata']=self.cad('SnapTool',self.plan['source_object_origin_mm'],[0,0,0],'source_SnapTool')
        self.source_frame={};self.candidates={};self.selection={};self.motion={};self.duplicates={};self.final=copy.deepcopy(self.final_sources)
        source=self.meshes['source'];upper=[i for i,p in enumerate(source['vertices']) if p[2]>=10.9999];lower=[i for i in range(42) if i not in upper]
        for variant in self.plan['coupon_objects']:
            name=variant['name'];data_name='coupon_'+name
            for pose in ('source_frame','print_candidate'):
                raw=self.fixture.coupon_fixture(name,pose,source)
                raw['cad_metadata']=self.cad(name,self.plan['source_object_origin_mm'] if pose=='source_frame' else variant['candidate_object_location_mm'],[0,0,0] if pose=='source_frame' else [0,90,0],data_name)
                dims=[max(p[a] for p in self.fixture.coupon_fixture(name,source=source)['vertices'])-min(p[a] for p in self.fixture.coupon_fixture(name,source=source)['vertices']) for a in range(3)]
                raw['cad_metadata']['object_axis_dimensions_mm']=dims
                self.meshes[name+'_'+('candidate' if pose=='print_candidate' else pose)]=raw
                result=self.checks.validate_coupon(source,raw,name,pose,self.plan)
                (self.source_frame if pose=='source_frame' else self.candidates)[name]=result
            self.selection[name]={'variant':name,'expected_count':14,'selected_count':14,'selected_world_vertices_mm':[source['vertices'][i] for i in upper],
                'original_upper_vertices_mm':[source['vertices'][i] for i in upper],'selection_method':'Front orthographic / Vertex / Xray / native B box select','box_source_world_mm':{'x':[-5,5],'z':[10,14]}}
            self.motion[name]={'variant':name,'upper_vertex_count':14,'unchanged_vertex_count':28,'upper_source_vertex_indices':upper,'unchanged_source_vertex_indices':lower,
                'translation_z_mm':variant['upper_vertex_translation_z_mm'],'maximum_coordinate_residual_mm':0.,'polygon_topology_unchanged':True,'coupon_geometry_modified':name!='A_L19','source_frame_origin_unchanged':True}
            self.duplicates[name]={'source_object':'SnapTool','operation':'native Shift+D then Esc','mesh_data_name':data_name,'independent_from_source':True,'location_mm':[float(x) for x in self.plan['source_object_origin_mm']],'rotation_euler_radians':[0.,0.,0.]}
            cad=self.meshes[name+'_candidate']['cad_metadata'];self.final[name]={'type':'MESH','hidden':False,'scale':[1.,1.,1.],'modifier_count':0,'matrix_world':cad['matrix_world'],'location_mm':cad['object_location_mm'],'rotation_euler_radians':cad['object_rotation_euler_radians'],'object_axis_dimensions_mm':cad['object_axis_dimensions_mm'],'mesh_data_name':data_name,'local_mesh_sha256':hashlib.sha256(name.encode()).hexdigest()}
        self.layout=self.checks.validate_coupon_layout(self.candidates,self.plan);self.scene=self.run_dir/'demo-files/u07_cantilever_length_coupons_v001.blend';self.scene.write_bytes(b'BLENDER-independent-three-length-coupons')
        self.display={'show_statvis':False,'shading':'SOLID','deactivated_with':'native Edit Mesh Overlays / Mesh Analysis checkbox','new_overhang_analysis_performed':False}
        self.verification={'passed':True,'kind':'snapfit_length_coupons_geometry_demo','source_scene_path':str(self.source),'source_scene_sha256':self.digest(self.source),'opened_scene_path':str(self.opened),'opened_scene_sha256':self.digest(self.opened),
            'source_unchanged':True,'opened_copy_unchanged':True,'draft_plan_path':str(self.plan_path),'draft_plan_sha256':self.digest(self.plan_path),'scene_path':str(self.scene),'scene_sha256':self.digest(self.scene),'scene_bytes':self.scene.stat().st_size,'reopened':True,
            'source_tool':self.checks.validate_source_snap_tool(source),'source_objects':self.source_objects,'final_source_objects':self.final_sources,'source_frame':self.source_frame,'candidates':self.candidates,'selection_proofs':self.selection,'motion_proofs':self.motion,'duplicate_proofs':self.duplicates,
            'layout':self.layout,'final_objects':self.final,'independent_coupon_meshes':True,'display_settings':self.display,'source_geometry_modified':False,'coupon_geometry_modified':True,'per_variant_geometry_modified':{'A_L19':False,'B_L17':True,'C_L21':True},'full_box_modified':False,'rotation_applied_to_mesh':False,'exported_stl':False,'mesh_analysis_overhang_checked':False,
            'numericComparison':{'positionEpsilonMm':1e-4,'volumeRelativeEpsilon':1e-5,'purpose':'Numeric geometry only, no material or improvement qualification'},**self.plan['performed_flags']}
        for field in ('full_box_boundary_equivalence','anchor_clamping_or_fixture','effective_mechanical_length_mm','support_required','final_print_orientation_approved','slicer_support_settings','bridge_or_support_qualified','improvement_validated','material_grade','epsilon_allow','Q','required_deflection_mm','delta_allow_mm','forces','physical_measurements','fit_results','physical_interference','qualified_strength_N','qualified_clearance_mm'):self.verification[field]=None
        for field in ('source_tool_mesh','source_geometry_record','continuity_reference'):
            self.verification[field+'_path']=str(self.project/self.plan[field]['path']);self.verification[field+'_sha256']=self.plan[field]['sha256']
        self.record_path=self.run_dir/'coupon-record-v001.json';self.verification['coupon_record_path']=str(self.record_path)
        self.record=dict(copy.deepcopy(self.plan),recordedAt='2026-10-25T19:00:00Z',reference_scene={'path':str(self.scene),'sha256':self.digest(self.scene),'bytes':self.scene.stat().st_size,'scene_role':'standalone_length_geometry_comparison_draft'},geometry_readback={k:self.verification[k] for k in ('source_tool','source_frame','candidates','layout')},source_geometry_modified=False,coupon_geometry_modified=True,per_variant_geometry_modified=self.verification['per_variant_geometry_modified'])
        records=[]
        for slug in ['inherited-analysis-off']+[name+suffix for name in self.candidates for suffix in ('-duplicate','-upper-selection','-source-frame','-candidate','-non-manifold')]:
            image=self.run_dir/(slug+'.png');image.write_bytes(png_bytes());records.append({'seq':len(records)+1,'step':'07-05','slug':slug,'file':image.name,'recordedAt':'2026-10-25T19:00:00Z','action':'原生獨立duplicate與14點單參數長度','observed':'獨立試片幾何，不是已驗證改善','width':3,'height':2,'sha256':self.digest(image)})
        self.run={'scenario':'scenarios/lesson07_coupons.py','blender':'5.9.9 TEST','buildHash':'test-build','records':records};self.runner={'status':'completed','blenderExitCode':0,'workspacesUnchanged':True,'runErrors':[],'scenario':'lesson07_coupons','outputDir':str(self.run_dir),'startedAt':'2026-10-25T18:59:00Z','endedAt':'2026-10-25T19:01:00Z'}
        files=[]
        for relative in ('learning/tutor/run_demo.py','learning/tutor/blender_demo.py','learning/tutor/scenarios/common.py','learning/tutor/scenarios/lesson07_coupons.py','learning/tutor/scenarios/coupon_checks.py','learning/tutor/scenarios/overhang_checks.py','learning/tutor/scenarios/snapfit_checks.py','learning/tutor/scenarios/snapfit_stl_checks.py','learning/tutor/scenarios/stl_checks.py','learning/tutor/scenarios/tenon_checks.py','learning/tutor/scenarios/lid_checks.py'):
            target=folder/Path(relative).name;target.write_text('# isolated snapshot fixture: '+relative,encoding='utf-8');files.append({'source':relative,'snapshot':'source-snapshot/'+target.name,'sha256':self.digest(target)})
        self.manifest={'recordedAt':'2026-10-25T18:59:00Z','files':files,'dataBindings':bindings,'sourceScene':str(self.source),'sourceCopy':str(self.opened),'sourceSha256':self.digest(self.source)};self.write_evidence()

    @staticmethod
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def cad(name,location,degrees,data_name):
        cad=PrintOrientationImportTests.cad(name,[float(x) for x in location],degrees);cad['matrix_world']=[[float(x) for x in row] for row in cad['matrix_world']];cad['mesh_data_name']=data_name;cad['object_axis_dimensions_mm']=[9.,4.6,24.];return cad

    def write_evidence(self):
        self.record_path.write_text(json.dumps(self.record),encoding='utf-8');self.verification['coupon_record_sha256']=self.digest(self.record_path)
        for name,value in (('run.json',self.run),('verification.json',self.verification),('runner-status.json',self.runner),('source-snapshot/manifest.json',self.manifest),('source-object-inventory.json',self.source_objects),('native-display-settings.json',self.display),('upper-vertex-selection-proofs.json',self.selection),('vertex-motion-proofs.json',self.motion),('duplicate-proofs.json',self.duplicates)):(self.run_dir/name).write_text(json.dumps(value),encoding='utf-8')
        for label,raw in self.meshes.items():(self.run_dir/('source_snap_tool_mesh.json' if label=='source' else label+'_mesh.json')).write_text(json.dumps(raw),encoding='utf-8')

    def assert_rejected_cleanly(self):
        with self.assertRaises(IMPORTER.ImportValidationError):IMPORTER.import_run(COUPONS_RUN_ID,self.project)
        self.assertEqual(self.catalog_path.read_bytes(),self.original_catalog);self.assertFalse((self.run_dir.parent/(COUPONS_RUN_ID+'.json')).exists());self.assertEqual(self.progress.read_bytes(),b'{"revision":18}')

    def test_valid_three_coupons_preserve_old_geometry_and_separate_all_height_definitions(self):
        result=IMPORTER.import_run(COUPONS_RUN_ID,self.project);self.assertEqual((result['steps'],result['records']),(1,16))
        self.assertEqual([self.source_frame[n]['L_geometry_mm'] for n in self.candidates],[19,17,21]);self.assertEqual([self.source_frame[n]['whole_coupon_height_mm'] for n in self.candidates],[24,22,26])
        metadata=json.loads(Path(result['metadata']).read_text(encoding='utf-8'));self.assertEqual(len(metadata['geometryEvidence']),7);self.assertIsNone(metadata['verification']['effective_mechanical_length_mm']);self.assertEqual(self.progress.read_bytes(),b'{"revision":18}')

    def test_fixed_plan_scene_copy_reference_mesh_and_continuity_record_are_immutable(self):
        for path in (self.source,self.opened,self.scene,self.plan_path,Path(self.verification['source_tool_mesh_path']),Path(self.verification['continuity_reference_path']),self.run_dir/'source-snapshot/source-geometry-record-v001.json'):
            with self.subTest(path=path):
                original=path.read_bytes();path.write_bytes(original+b'changed');self.assert_rejected_cleanly();path.write_bytes(original)

    def test_fourteen_actual_upper_coordinates_not_just_count_and_motion_proofs_are_required(self):
        points=self.selection['B_L17']['selected_world_vertices_mm'];old=copy.deepcopy(points);points[0]=self.meshes['source']['vertices'][0];self.write_evidence();self.assert_rejected_cleanly();self.selection['B_L17']['selected_world_vertices_mm']=old
        self.motion['C_L21']['unchanged_source_vertex_indices'][0]=30;self.write_evidence();self.assert_rejected_cleanly()

    def test_moving_root_width_or_wrong_upper_amount_cannot_be_hidden_by_successful_reports(self):
        previous=copy.deepcopy(self.meshes)
        for label,index,axis,change in (('B_L17_source_frame',0,2,-2),('C_L21_source_frame',22,0,.01),('B_L17_source_frame',16,1,.02)):
            with self.subTest(label=label,index=index):
                self.meshes=copy.deepcopy(previous);self.meshes[label]['vertices'][index][axis]+=change;self.write_evidence();self.assert_rejected_cleanly()

    def test_source_and_new_coupon_geometry_modified_flags_must_describe_different_scopes(self):
        previous=copy.deepcopy(self.verification)
        for field,value in (('source_geometry_modified',True),('coupon_geometry_modified',False),('full_box_modified',True)):
            with self.subTest(field=field):
                self.verification=copy.deepcopy(previous);self.verification[field]=value;self.write_evidence();self.assert_rejected_cleanly()
        self.verification=copy.deepcopy(previous);self.verification['per_variant_geometry_modified']['A_L19']=True;self.write_evidence();self.assert_rejected_cleanly()

    def test_linked_mesh_data_or_changed_hidden_source_matrices_are_rejected(self):
        self.final['B_L17']['mesh_data_name']=self.final['A_L19']['mesh_data_name'];self.write_evidence();self.assert_rejected_cleanly();self.final['B_L17']['mesh_data_name']='coupon_B_L17'
        self.final_sources['Body']['matrix_world'][0][3]+=.01;self.write_evidence();self.assert_rejected_cleanly()

    def test_side_pose_anchor_contact_does_not_authorize_all_features_on_bed_or_support(self):
        bed=self.candidates['A_L19']['bed_and_raised_features'];bed['raised_features']['straight_beam']['world_z_range_mm'][0]=0
        self.write_evidence();self.assert_rejected_cleanly()

    def test_material_effective_length_boundary_improvement_and_physical_results_stay_null(self):
        previous=copy.deepcopy(self.verification)
        for field in ('full_box_boundary_equivalence','anchor_clamping_or_fixture','effective_mechanical_length_mm','epsilon_allow','Q','required_deflection_mm','delta_allow_mm','forces','physical_measurements','fit_results','qualified_strength_N','qualified_clearance_mm','improvement_validated','support_required'):
            with self.subTest(field=field):
                self.verification=copy.deepcopy(previous);self.verification[field]=1;self.write_evidence();self.assert_rejected_cleanly()

    def test_record_no_stl_or_overhang_repeat_and_full_original_ui_evidence_are_required(self):
        self.record['boundary_and_orientation']['anchor_clamping_or_fixture']='old box';self.write_evidence();self.assert_rejected_cleanly();self.record['boundary_and_orientation']['anchor_clamping_or_fixture']=None
        self.display['show_statvis']=True;self.write_evidence();self.assert_rejected_cleanly();self.display['show_statvis']=False
        self.run['records'][2]['slug']='unrelated';self.write_evidence();self.assert_rejected_cleanly()

    def test_wrong_candidate_rotation_and_missing_snapshot_dependency_are_rejected(self):
        self.meshes['C_L21_candidate']['cad_metadata']['object_rotation_euler_radians']=[0.,0.,0.];self.write_evidence();self.assert_rejected_cleanly()
        self.meshes['C_L21_candidate']['cad_metadata']['object_rotation_euler_radians']=[0.,math.pi/2,0.]
        self.manifest['files']=[item for item in self.manifest['files'] if not item['source'].endswith('coupon_checks.py')];self.write_evidence();self.assert_rejected_cleanly()


if __name__ == "__main__":
    unittest.main()
