"""Binary lid export fixtures test source comparison and wrong selections."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SCENARIOS = HERE.parent / "scenarios"
sys.path.insert(0, str(SCENARIOS))
from lid_checks import validate_body_mesh, validate_lid_mesh
from lid_stl_checks import validate_lid_stl

FIXTURE_SPEC = importlib.util.spec_from_file_location("lid_fixture_helpers", HERE / "test_lid_checks.py")
fixture = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(fixture)


def binary_stl(vertices, triangles):
    data = bytearray(b"lid export fixture".ljust(80, b"\0") + struct.pack("<I", len(triangles)))
    for triangle in triangles:
        coordinates = tuple(value for index in triangle for value in vertices[index])
        data.extend(struct.pack("<12fH", 0, 0, 0, *coordinates, 0))
    return bytes(data)


class LidSTLChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lid-stl-checks-")
        self.path = Path(self.temp.name) / "lid.stl"
        self.vertices, self.triangles = fixture.lid_fixture()
        body = validate_body_mesh(*fixture.body_fixture())
        lid = validate_lid_mesh(self.vertices, self.triangles, body)
        self.source = {"passed": True, "body": body, "lid": lid,
                       "scene_path": "source/u05_lid_v001.blend", "scene_sha256": "a" * 64}

    def tearDown(self):
        self.temp.cleanup()

    def write(self, vertices=None, triangles=None):
        self.path.write_bytes(binary_stl(self.vertices if vertices is None else vertices,
                                         self.triangles if triangles is None else triangles))
        return self.path

    def test_actual_binary_geometry_and_source_assembly_are_checked(self):
        result = validate_lid_stl(self.write(), self.source)
        self.assertTrue(result["passed"])
        self.assertEqual(result["kind"], "lid_stl")
        self.assertEqual(result["dimensions_mm"], [60, 40, 6])
        self.assertEqual(result["bounds_mm"], {"min": [-30, -20, 11], "max": [30, 20, 17]})
        self.assertAlmostEqual(result["volume_mm3"], 6195.2, places=3)
        self.assertEqual(result["triangle_count"], len(self.triangles))
        self.assertNotEqual(result["triangle_count"], 44)  # no triangulation-count shortcut
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertEqual(result["connected_shells"], 1)
        self.assertEqual(result["genus"], 0)
        geometry = result["lid_geometry"]
        self.assertAlmostEqual(geometry["plate_thickness_mm"], 2)
        self.assertAlmostEqual(geometry["ring_depth_mm"], 4)
        self.assertEqual(len(geometry["vertical_rays"]), 10)
        for gap in geometry["assembly"]["per_side_clearances_mm"]:
            self.assertAlmostEqual(gap, 0.2, places=4)
        self.assertIn("lid.ring_inner_mm", result["source_metadata_compared"])
        self.assertIn("body.cavity_bounds_mm", result["source_metadata_compared"])
        self.assertIn("no units", result["unit_interpretation"])
        self.assertEqual(result["source_scene_sha256"], "a" * 64)
        json.dumps(result)  # all evidence is serializable

    def test_omitting_source_does_not_invent_assembly_or_physical_results(self):
        result = validate_lid_stl(self.write())
        self.assertIsNone(result["lid_geometry"]["assembly"])
        self.assertEqual(result["source_metadata_compared"], [])
        self.assertFalse(result["printed"])
        self.assertFalse(result["fit_tested"])
        for key in ("physical_measurements", "fit_results", "physical_interference", "qualified_clearance_mm"):
            self.assertIsNone(result[key])

    def test_closed_solid_plug_with_same_bounds_is_rejected(self):
        vertices, triangles = fixture.lid_fixture(solid_plug=True)
        with self.assertRaisesRegex(ValueError, "face-plane"):
            validate_lid_stl(self.write(vertices, triangles), self.source)

    def test_exporting_body_instead_of_lid_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_lid_stl(self.write(*fixture.body_fixture()), self.source)

    def test_exporting_both_objects_instead_of_selected_lid_is_rejected(self):
        body_vertices, body_triangles = fixture.body_fixture()
        vertices = self.vertices + body_vertices
        triangles = self.triangles + [tuple(index + len(self.vertices) for index in tri) for tri in body_triangles]
        with self.assertRaises(ValueError):
            validate_lid_stl(self.write(vertices, triangles), self.source)

    def test_wrong_world_z_axis_and_unit_scale_are_rejected(self):
        transforms = (lambda x, y, z: (x, y, z - 11), lambda x, y, z: (x, z, y),
                      lambda x, y, z: (x * 0.001, y * 0.001, z * 0.001))
        for transform in transforms:
            with self.subTest(transform=transform):
                with self.assertRaises(ValueError):
                    validate_lid_stl(self.write([transform(*v) for v in self.vertices]), self.source)

    def test_source_dimensions_volume_and_features_must_match(self):
        self.write()
        for key, wrong in (("ring_inner_mm", [51.7, 31.6]), ("plate_thickness_mm", 2.1),
                           ("volume_mm3", 6100), ("dimensions_mm", [60, 40, 5])):
            source = copy.deepcopy(self.source)
            source["lid"][key] = wrong
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "STL/source"):
                    validate_lid_stl(self.path, source)

    def test_source_body_and_prior_assembly_cannot_disagree(self):
        self.write()
        source = copy.deepcopy(self.source)
        source["body"]["cavity_bounds_mm"]["min"][0] = -27.9
        with self.assertRaisesRegex(ValueError, "per-side clearance"):
            validate_lid_stl(self.path, source)
        source = copy.deepcopy(self.source)
        source["lid"]["assembly"]["per_side_clearances_mm"][0] = 0.3
        with self.assertRaisesRegex(ValueError, "STL/source assembly"):
            validate_lid_stl(self.path, source)

    def test_failed_or_missing_source_records_are_rejected(self):
        self.write()
        for source in ({"passed": False}, {"passed": True},
                       {"passed": True, "body": self.source["body"], "lid": {"passed": False}}):
            with self.assertRaises(ValueError):
                validate_lid_stl(self.path, source)

    def test_missing_triangle_and_malformed_binary_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "closed manifold"):
            validate_lid_stl(self.write(triangles=self.triangles[:-1]), self.source)
        self.write()
        self.path.write_bytes(self.path.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError, "length/count mismatch"):
            validate_lid_stl(self.path, self.source)

    def test_checker_does_not_modify_export_or_source_metadata(self):
        self.write()
        before_bytes = self.path.read_bytes()
        before_metadata = copy.deepcopy(self.source)
        validate_lid_stl(self.path, self.source)
        self.assertEqual(self.path.read_bytes(), before_bytes)
        self.assertEqual(self.source, before_metadata)


if __name__ == "__main__":
    unittest.main()
