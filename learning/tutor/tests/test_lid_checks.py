"""Analytic source-body and cap fixtures test measured topology and material."""
import copy
import importlib.util
from pathlib import Path
import unittest


MODULE = Path(__file__).resolve().parents[1] / "scenarios" / "lid_checks.py"
SPEC = importlib.util.spec_from_file_location("lid_checks", MODULE)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


def cell_surface(xs, ys, zs, occupied):
    """Conformal analytic cell-boundary fixture with no Blender dependency."""
    cells = {(i, j, k) for i in range(len(xs) - 1) for j in range(len(ys) - 1)
             for k in range(len(zs) - 1)
             if occupied((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2,
                         (zs[k] + zs[k + 1]) / 2)}
    vertices, mapping, triangles = [], {}, []

    def vertex(point):
        if point not in mapping:
            mapping[point] = len(vertices)
            vertices.append(point)
        return mapping[point]

    def quad(a, b, c, d):
        ids = tuple(vertex(p) for p in (a, b, c, d))
        triangles.extend(((ids[0], ids[1], ids[2]), (ids[0], ids[2], ids[3])))

    for i, j, k in sorted(cells):
        x0, x1, y0, y1, z0, z1 = xs[i], xs[i + 1], ys[j], ys[j + 1], zs[k], zs[k + 1]
        a, b, c, d = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
        e, f, g, h = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
        if (i, j, k - 1) not in cells:
            quad(a, d, c, b)
        if (i, j, k + 1) not in cells:
            quad(e, f, g, h)
        if (i, j - 1, k) not in cells:
            quad(a, b, f, e)
        if (i + 1, j, k) not in cells:
            quad(b, c, g, f)
        if (i, j + 1, k) not in cells:
            quad(c, d, h, g)
        if (i - 1, j, k) not in cells:
            quad(d, a, e, h)
    return vertices, triangles


def body_fixture(floor_z=-13):
    return cell_surface([-30, -28, 28, 30], [-20, -18, 18, 20], [-15, floor_z, 15],
                        lambda x, y, z: not (abs(x) < 28 and abs(y) < 18 and z > floor_z))


def lid_fixture(solid_plug=False, inner_half_x=25.8, inner_half_y=15.8):
    xs = [-30, -27.8, -inner_half_x, inner_half_x, 27.8, 30]
    ys = [-20, -17.8, -inner_half_y, inner_half_y, 17.8, 20]
    return cell_surface(xs, ys, [11, 15, 17],
                        lambda x, y, z: z > 15 or
                        (abs(x) < 27.8 and abs(y) < 17.8 and
                         (solid_plug or not (abs(x) < inner_half_x and abs(y) < inner_half_y))))


class LidChecksTests(unittest.TestCase):
    def test_source_body_is_measured_including_open_cavity_and_floor(self):
        result = checks.validate_body_mesh(*body_fixture())
        self.assertEqual(result["outer_dimensions_mm"], [60, 40, 30])
        self.assertEqual(result["cavity_dimensions_mm"], [56, 36, 28])
        self.assertEqual(result["wall_thicknesses_mm"], [2, 2, 2, 2])
        self.assertEqual(result["floor_thickness_mm"], 2)
        self.assertEqual(result["rim_z_mm"], 15)
        self.assertAlmostEqual(result["volume_mm3"], 15552)
        self.assertEqual(result["vertical_rays"][0]["z_hits_mm"], [-15, -13])
        self.assertEqual(result["genus"], 0)

    def test_lid_is_integrated_ring_and_covered_centre_not_solid_plug(self):
        result = checks.validate_lid_mesh(*lid_fixture())
        self.assertEqual(result["dimensions_mm"], [60, 40, 6])
        self.assertEqual(result["plate_dimensions_mm"], [60, 40, 2])
        self.assertEqual(result["plate_z_mm"], [15, 17])
        for actual, expected in zip(result["ring_outer_mm"], [55.6, 35.6]):
            self.assertAlmostEqual(actual, expected)
        for actual, expected in zip(result["ring_inner_mm"], [51.6, 31.6]):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(result["ring_z_mm"], [11, 15])
        self.assertAlmostEqual(result["ring_wall_mm"], 2)
        self.assertAlmostEqual(result["volume_mm3"], 6195.2)
        rays = {ray["label"]: ray["z_hits_mm"] for ray in result["vertical_rays"]}
        self.assertEqual(rays["covered hollow centre"], [15, 17])
        self.assertEqual(rays["positive X lip"], [11, 17])
        self.assertEqual(rays["positive X outer ledge"], [15, 17])
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertEqual(result["connected_shells"], 1)
        self.assertEqual(result["genus"], 0)

    def test_assembly_trial_clearances_are_geometric_only(self):
        body = checks.validate_body_mesh(*body_fixture())
        lid = checks.validate_lid_mesh(*lid_fixture(), body_metadata=body)
        assembly = lid["assembly"]
        for side in assembly["per_side_clearances_mm"]:
            self.assertAlmostEqual(side, 0.2)
        for total in assembly["total_clearances_mm"]:
            self.assertAlmostEqual(total, 0.4)
        self.assertAlmostEqual(assembly["engagement_mm"], 4)
        self.assertAlmostEqual(assembly["cavity_depth_mm"], 28)
        self.assertAlmostEqual(assembly["floor_reserve_mm"], 24)
        self.assertTrue(assembly["geometric_nonintersection"])
        self.assertEqual(lid["trial_status"], "experimental_geometry_only")
        for result in (lid, assembly):
            self.assertFalse(result["printed"])
            self.assertFalse(result["fit_tested"])
            self.assertIsNone(result["physical_interference"])
            self.assertIsNone(result["qualified_clearance_mm"])

    def test_same_outer_bounds_solid_body_is_rejected(self):
        solid = cell_surface([-30, 30], [-20, 20], [-15, 15], lambda x, y, z: True)
        with self.assertRaisesRegex(ValueError, "face-plane count"):
            checks.validate_body_mesh(*solid)

    def test_same_lid_bounds_solid_plug_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "face-plane count"):
            checks.validate_lid_mesh(*lid_fixture(solid_plug=True))

    def test_wrong_floor_and_ring_wall_do_not_pass_dimension_only_checks(self):
        with self.assertRaisesRegex(ValueError, "face-plane"):
            checks.validate_body_mesh(*body_fixture(-14.5))
        with self.assertRaisesRegex(ValueError, "face-plane"):
            checks.validate_lid_mesh(*lid_fixture(inner_half_x=25.7))

    def test_missing_face_and_inverted_normals_are_rejected(self):
        vertices, triangles = lid_fixture()
        with self.assertRaisesRegex(ValueError, "closed manifold"):
            checks.validate_lid_mesh(vertices, triangles[:-1])
        with self.assertRaisesRegex(ValueError, "positive"):
            checks.validate_lid_mesh(vertices, [tuple(reversed(face)) for face in triangles])

    def test_wrong_source_measurement_or_insufficient_cavity_is_rejected(self):
        body = checks.validate_body_mesh(*body_fixture())
        failed = copy.deepcopy(body)
        failed["passed"] = False
        with self.assertRaisesRegex(ValueError, "successful source-body"):
            checks.validate_lid_mesh(*lid_fixture(), body_metadata=failed)
        shallow = copy.deepcopy(body)
        shallow["cavity_bounds_mm"]["min"][2] = 12
        shallow["cavity_dimensions_mm"][2] = 3
        with self.assertRaisesRegex(ValueError, "engagement"):
            checks.validate_lid_mesh(*lid_fixture(), body_metadata=shallow)
        wrong_width = copy.deepcopy(body)
        wrong_width["cavity_bounds_mm"]["min"][0] = -27.9
        with self.assertRaisesRegex(ValueError, "per-side clearance"):
            checks.validate_lid_mesh(*lid_fixture(), body_metadata=wrong_width)

    def test_nonfinite_or_isolated_vertices_are_rejected(self):
        vertices, triangles = lid_fixture()
        with self.assertRaisesRegex(ValueError, "isolated"):
            checks.validate_lid_mesh(vertices + [(0, 0, 16)], triangles)
        bad = list(vertices)
        bad[0] = (float("nan"), 0, 0)
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            checks.validate_lid_mesh(bad, triangles)


if __name__ == "__main__":
    unittest.main()
