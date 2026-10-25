"""Independent binary fixtures exercise malformed, wrong and open STL exports."""
import hashlib
import importlib.util
import math
from pathlib import Path
import struct
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / "scenarios" / "stl_checks.py"
SPEC = importlib.util.spec_from_file_location("stl_checks", MODULE)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


def box_triangles(dimensions=(10.0, 10.0, 8.0), centre=(0, 0, 0)):
    x, y, z = (value / 2 for value in dimensions)
    vertices = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
                (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    vertices = [tuple(v[a] + centre[a] for a in range(3)) for v in vertices]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
             (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return [tuple(vertices[i] for i in face) for face in faces]


def grid_slab_with_holes(xs, ys, holes, z_min=-2.0, z_max=2.0):
    """Analytic rectangular-cell boundary fixture; no Blender dependency.

    Global grid lines make every shared edge conformal. The resulting slab has
    through holes but intentionally has no blind marker recesses.
    """
    occupied = set()
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x, y = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if not any(abs(x - cx) < width / 2 and abs(y - cy) < width / 2
                       for cx, cy, width in holes):
                occupied.add((i, j))
    triangles = []

    def quad(a, b, c, d):
        triangles.extend(((a, b, c), (a, c, d)))

    for i, j in sorted(occupied):
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
        a, b, c, d = (x0, y0, z_min), (x1, y0, z_min), (x1, y1, z_min), (x0, y1, z_min)
        e, f, g, h = (x0, y0, z_max), (x1, y0, z_max), (x1, y1, z_max), (x0, y1, z_max)
        quad(a, d, c, b)
        quad(e, f, g, h)
        if (i, j - 1) not in occupied:
            quad(a, b, f, e)
        if (i + 1, j) not in occupied:
            quad(b, c, g, f)
        if (i, j + 1) not in occupied:
            quad(c, d, h, g)
        if (i - 1, j) not in occupied:
            quad(d, a, e, h)
    return triangles


def binary_stl(triangles, header=b"standard library test fixture", normal=(0.0, 0.0, 0.0)):
    result = bytearray(header[:80].ljust(80, b"\0") + struct.pack("<I", len(triangles)))
    for triangle in triangles:
        values = normal + tuple(value for point in triangle for value in point)
        result.extend(struct.pack("<12fH", *values, 0))
    return bytes(result)


class STLChecksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="stl-checks-")
        self.path = Path(self.temporary.name) / "export.stl"

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, data):
        self.path.write_bytes(data)
        return self.path

    def test_valid_pin_is_measured_not_named(self):
        data = binary_stl(box_triangles())
        result = checks.validate_export(self.write(data), "pin", {"passed": True, "volume_mm3": 800,
                                                                  "dimensions_mm": [10, 10, 8]})
        self.assertEqual(result["dimensions_mm"], [10, 10, 8])
        self.assertEqual(result["triangle_count"], 12)
        self.assertEqual(result["vertex_count"], 8)
        self.assertEqual(result["stl_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["genus"], 0)
        self.assertEqual(result["euler_characteristic"], 2)
        self.assertEqual(result["connected_shells"], 1)
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertAlmostEqual(result["signed_volume_mm3"], 800)
        self.assertFalse(result["printed"])
        self.assertFalse(result["fit_tested"])
        self.assertIsNone(result["qualified_clearance_mm"])

    def test_binary_header_starting_solid_is_not_misclassified(self):
        result = checks.read_stl(self.write(binary_stl(box_triangles(), header=b"solid real binary STL")))
        self.assertEqual(result["format"], "binary_stl")
        self.assertEqual(len(result["triangles"]), 12)

    def test_truncated_and_trailing_bytes_are_rejected(self):
        data = binary_stl(box_triangles())
        for damaged in (data[:80], data[:-1], data + b"unexpected", data[:80] + struct.pack("<I", 1) + data[84:]):
            with self.subTest(length=len(damaged)):
                with self.assertRaises(ValueError):
                    checks.read_stl(self.write(damaged))

    def test_empty_and_ascii_stl_are_rejected(self):
        for data in (binary_stl([]), b"solid empty\nendsolid empty\n"):
            with self.assertRaises(ValueError):
                checks.read_stl(self.write(data))

    def test_nonfinite_vertices_and_normals_are_rejected(self):
        for coordinate in (float("nan"), float("inf"), float("-inf")):
            bad = [((coordinate, 0, 0), (1, 0, 0), (0, 1, 0))]
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                checks.read_stl(self.write(binary_stl(bad)))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            checks.read_stl(self.write(binary_stl(box_triangles(), normal=(math.nan, 0, 1))))

    def test_degenerate_and_numeric_weld_collapse_are_rejected(self):
        for triangle in (((0, 0, 0), (1, 1, 1), (2, 2, 2)),
                         ((0, 0, 0), (0, 0, 0), (1, 0, 0)),
                         ((0, 0, 0), (1e-6, 0, 0), (0, 1, 0))):
            with self.assertRaises(ValueError):
                checks.read_stl(self.write(binary_stl([triangle])))

    def test_missing_triangle_is_open_even_with_same_bounds(self):
        path = self.write(binary_stl(box_triangles()[:-1]))
        result = checks.read_stl(path)
        self.assertEqual(result["dimensions_mm"], [10, 10, 8])
        self.assertGreater(result["non_manifold_edges"], 0)
        with self.assertRaisesRegex(ValueError, "not closed"):
            checks.validate_export(path, "pin")

    def test_inconsistent_or_inward_winding_is_rejected(self):
        triangles = box_triangles()
        triangles[0] = tuple(reversed(triangles[0]))
        path = self.write(binary_stl(triangles))
        self.assertGreater(checks.read_stl(path)["inconsistent_winding_edges"], 0)
        with self.assertRaisesRegex(ValueError, "winding"):
            checks.validate_export(path, "pin")
        path = self.write(binary_stl([tuple(reversed(t)) for t in box_triangles()]))
        with self.assertRaisesRegex(ValueError, "positive"):
            checks.validate_export(path, "pin")

    def test_extra_internal_shell_is_rejected_despite_same_bounds(self):
        path = self.write(binary_stl(box_triangles() + box_triangles((1, 1, 1))))
        self.assertEqual(checks.read_stl(path)["dimensions_mm"], [10, 10, 8])
        self.assertEqual(checks.read_stl(path)["connected_shells"], 2)
        with self.assertRaisesRegex(ValueError, "connected shell"):
            checks.validate_export(path, "pin")

    def test_through_hole_changes_genus_despite_same_pin_bounds(self):
        triangles = grid_slab_with_holes([-5, -2, 2, 5], [-5, -2, 2, 5], [(0, 0, 4)], -4, 4)
        path = self.write(binary_stl(triangles))
        result = checks.read_stl(path)
        self.assertEqual(result["dimensions_mm"], [10, 10, 8])
        self.assertEqual(result["connected_shells"], 1)
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertEqual(result["genus"], 1)
        self.assertAlmostEqual(result["volume_mm3"], 672)
        with self.assertRaisesRegex(ValueError, "genus"):
            checks.validate_export(path, "pin")

    def test_six_holes_without_required_blind_markers_are_rejected(self):
        holes = [(x, 2, 10 + c) for x, c in zip(checks.HOLE_X_MM, checks.TRIAL_CLEARANCES_MM)]
        xs = sorted({-48, 48, *(x + sign * w / 2 for x, y, w in holes for sign in (-1, 1))})
        ys = sorted({-13, 13, *(y + sign * w / 2 for x, y, w in holes for sign in (-1, 1))})
        path = self.write(binary_stl(grid_slab_with_holes(xs, ys, holes)))
        read = checks.read_stl(path)
        self.assertEqual(read["genus"], 6)
        self.assertEqual(read["non_manifold_edges"], 0)
        self.assertAlmostEqual(read["volume_mm3"], 7412.36, places=3)
        with self.assertRaisesRegex(ValueError, "21 separate blind-marker"):
            checks.validate_export(path, "plate")

    def test_wrong_axis_scale_and_source_metadata_do_not_pass(self):
        for dimensions in ((10, 8, 10), (0.01, 0.01, 0.008), (10.1, 10, 8)):
            with self.assertRaisesRegex(ValueError, "dimensions"):
                checks.validate_export(self.write(binary_stl(box_triangles(dimensions))), "pin")
        path = self.write(binary_stl(box_triangles()))
        with self.assertRaisesRegex(ValueError, "source volume"):
            checks.validate_export(path, "pin", {"volume_mm3": 790})
        with self.assertRaisesRegex(ValueError, "source dimensions"):
            checks.validate_export(path, "pin", {"dimensions_mm": [10, 8, 10]})
        with self.assertRaisesRegex(ValueError, "source verification"):
            checks.validate_export(path, "pin", {"passed": False})


if __name__ == "__main__":
    unittest.main()
