"""Analytic watertight fixtures exercise actual radial and assembly geometry."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scenarios"))
import tenon_checks as checks
from lid_checks import validate_body_mesh, validate_lid_mesh

SPEC = importlib.util.spec_from_file_location("tenon_source_fixtures", HERE / "test_lid_checks.py")
old = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(old)


def source_fixture():
    body = validate_body_mesh(*old.body_fixture())
    lid = validate_lid_mesh(*old.lid_fixture(), body_metadata=body)
    return {"passed": True, "body": body, "lid": lid}


class Surface:
    def __init__(self):
        self.vertices, self.triangles, self.mapping = [], [], {}

    def vertex(self, point):
        key = tuple(round(value, 10) for value in point)
        if key not in self.mapping:
            self.mapping[key] = len(self.vertices)
            self.vertices.append(key)
        return self.mapping[key]

    def triangle(self, a, b, c, positive=True):
        ids = tuple(self.vertex(point) for point in (a, b, c))
        self.triangles.append(ids if positive else tuple(reversed(ids)))

    def wall(self, loop, bottom, top, outward=True):
        for a, b in zip(loop, loop[1:] + loop[:1]):
            p, q = (*a, bottom), (*b, bottom)
            r, s = (*b, top), (*a, top)
            self.triangle(p, q, r, outward)
            self.triangle(p, r, s, outward)

    def cap(self, loop, z, positive=True):
        centre = (23.0, 13.0, z)
        for a, b in zip(loop, loop[1:] + loop[:1]):
            self.triangle(centre, (*a, z), (*b, z), positive)

    def annulus(self, outer, inner, z, positive=True):
        """Angular zipper between dense convex loops, both starting on +X."""
        def angles(loop):
            return [math.atan2(p[1] - 13, p[0] - 23) % (2 * math.pi) for p in loop]
        ao, ai = angles(outer), angles(inner)
        i = j = 0
        while i < len(outer) or j < len(inner):
            next_o = ao[(i + 1) % len(outer)] if i + 1 < len(outer) else 2 * math.pi
            next_i = ai[(j + 1) % len(inner)] if j + 1 < len(inner) else 2 * math.pi
            if i >= len(outer):
                next_o = math.inf
            if j >= len(inner):
                next_i = math.inf
            op, ip = outer[i % len(outer)], inner[j % len(inner)]
            if abs(next_o - next_i) < 1e-9:
                on, inn = outer[(i + 1) % len(outer)], inner[(j + 1) % len(inner)]
                self.triangle((*ip, z), (*op, z), (*on, z), positive)
                self.triangle((*ip, z), (*on, z), (*inn, z), positive)
                i, j = i + 1, j + 1
            elif next_o < next_i:
                on = outer[(i + 1) % len(outer)]
                self.triangle((*ip, z), (*op, z), (*on, z), positive)
                i += 1
            else:
                inn = inner[(j + 1) % len(inner)]
                self.triangle((*ip, z), (*op, z), (*inn, z), positive)
                j += 1

    def result(self):
        return self.vertices, self.triangles


def _angles():
    angles = [i * 2 * math.pi / 32 for i in range(32)]
    for hx, hy in ((30, 20), (28, 18), (27.8, 17.8), (25.8, 15.8)):
        angles.extend(math.atan2(y - 13, x - 23) % (2 * math.pi)
                      for x in (-hx, hx) for y in (-hy, hy))
    unique = []
    for value in sorted(angles):
        if not unique or value - unique[-1] > 1e-9:
            unique.append(value)
    return unique


def _rectangle(hx, hy):
    points = []
    for angle in _angles():
        dx, dy = math.cos(angle), math.sin(angle)
        tx = ((hx if dx >= 0 else -hx) - 23) / dx if abs(dx) > 1e-12 else math.inf
        ty = ((hy if dy >= 0 else -hy) - 13) / dy if abs(dy) > 1e-12 else math.inf
        t = min(tx, ty)
        points.append((23 + t * dx, 13 + t * dy))
    return points


def _circle(radius, segments=32, phase=0):
    return [(23 + radius * math.cos(phase + i * 2 * math.pi / segments),
             13 + radius * math.sin(phase + i * 2 * math.pi / segments)) for i in range(segments)]


def tool_fixture(kind="pin", segments=32, radius=None):
    r, bottom, top = (2, -13.5, 16.5) if kind == "pin" else (2.2, 11, 21)
    loop = _circle(r if radius is None else radius, segments)
    surface = Surface()
    surface.wall(loop, bottom, top)
    surface.cap(loop, bottom, False)
    surface.cap(loop, top)
    return surface.result()


def body_pin_fixture():
    outer, cavity, pin = _rectangle(30, 20), _rectangle(28, 18), _circle(2)
    surface = Surface()
    surface.wall(outer, -15, 15)
    surface.cap(outer, -15, False)
    surface.annulus(outer, cavity, 15)
    surface.wall(cavity, -13, 15, False)
    surface.annulus(cavity, pin, -13)
    surface.wall(pin, -13, 16.5)
    surface.cap(pin, 16.5)
    return surface.result()


def lid_hole_fixture():
    outer, lip_outer, lip_inner = _rectangle(30, 20), _rectangle(27.8, 17.8), _rectangle(25.8, 15.8)
    hole = _circle(2.2)
    surface = Surface()
    surface.wall(outer, 15, 17)
    surface.annulus(outer, hole, 17)
    surface.annulus(outer, lip_outer, 15, False)
    surface.wall(lip_outer, 11, 15)
    surface.wall(lip_inner, 11, 15, False)
    surface.annulus(lip_outer, lip_inner, 11, False)
    surface.annulus(lip_inner, hole, 15, False)
    surface.wall(hole, 15, 17, False)
    return surface.result()


class TenonChecksTests(unittest.TestCase):
    def setUp(self):
        self.source = source_fixture()

    def tool(self):
        return checks.validate_tool_mesh(*tool_fixture(), "pin")

    def body(self, construction=True):
        return checks.validate_body_pin_mesh(*body_pin_fixture(), self.source["body"], self.tool() if construction else None)

    def lid(self):
        return checks.validate_lid_hole_mesh(*lid_hole_fixture(), self.source["lid"])

    def test_actual_tools_have_32_sides_full_bounds_and_correct_polygons(self):
        pin = self.tool()
        cutter = checks.validate_tool_mesh(*tool_fixture("hole_cutter"), "hole_cutter")
        self.assertEqual(pin["z_mm"], [-13.5, 16.5])
        self.assertEqual(pin["location_mm"], [23, 13, 1.5])
        self.assertEqual(cutter["z_mm"], [11, 21])
        self.assertEqual(cutter["location_mm"], [23, 13, 16])
        for tool, radius in ((pin, 2), (cutter, 2.2)):
            polygon = tool["polygon"]
            self.assertEqual(polygon["segments"], 32)
            self.assertEqual(len(tool["radial_walls"]), 32)
            self.assertAlmostEqual(polygon["radius_mm"], radius)
            self.assertAlmostEqual(polygon["across_flats_diameter_mm"], 2 * radius * math.cos(math.pi / 32))
            self.assertAlmostEqual(tool["volume_mm3"], polygon["area_mm2"] * tool["height_mm"])

    def test_union_retains_original_shell_but_only_exposes_pin_above_floor(self):
        body = self.body()
        self.assertEqual(body["dimensions_mm"], [60, 40, 31.5])
        self.assertEqual(body["source_shell_dimensions_mm"], [60, 40, 30])
        self.assertEqual(body["source_cavity_dimensions_mm"], [56, 36, 28])
        self.assertEqual(body["pin"]["exposed_z_mm"], [-13, 16.5])
        self.assertAlmostEqual(body["construction_floor_overlap_mm"], 0.5)
        self.assertAlmostEqual(body["volume_mm3"], 15920.330527966, places=5)
        self.assertEqual(body["genus"], 0)
        self.assertEqual(body["connected_shells"], 1)
        self.assertEqual(body["vertical_rays"][0]["z_hits_mm"], [-15, 16.5])

    def test_union_does_not_invent_deleted_construction_bottom(self):
        body = self.body(construction=False)
        self.assertIsNone(body["construction_pin"])
        self.assertIsNone(body["construction_floor_overlap_mm"])
        self.assertEqual(body["pin"]["exposed_z_mm"], [-13, 16.5])

    def test_actual_through_hole_changes_genus_preserves_ring_and_has_no_centre_hit(self):
        lid = self.lid()
        self.assertEqual(lid["genus"], 1)
        self.assertEqual(lid["euler_characteristic"], 0)
        self.assertEqual(lid["non_manifold_edges"], 0)
        self.assertEqual(lid["hole"]["z_mm"], [15, 17])
        self.assertTrue(lid["hole"]["through"])
        self.assertEqual(lid["vertical_rays"][0]["z_hits_mm"], [])
        self.assertAlmostEqual(lid["volume_mm3"], 6164.984410926, places=5)
        for a, b in zip(lid["ring_outer_mm"], [55.6, 35.6]):
            self.assertAlmostEqual(a, b)

    def test_actual_normal_gaps_differ_from_nominal_radial_clearance(self):
        assembly = checks.validate_tenon_assembly(self.body(), self.lid())
        expected = 0.2 * math.cos(math.pi / 32)
        self.assertEqual(assembly["nominal_diameter_total_clearance_mm"], 0.4)
        self.assertEqual(assembly["nominal_radial_clearance_mm"], 0.2)
        self.assertEqual(len(assembly["actual_normal_gaps_mm"]), 32)
        for gap in assembly["actual_normal_gaps_mm"]:
            self.assertAlmostEqual(gap, expected, places=8)
        self.assertLess(assembly["min_normal_gap_mm"], 0.2)
        self.assertAlmostEqual(assembly["across_flats_total_clearance_mm"], 2 * expected)
        self.assertEqual(assembly["engagement_mm"], 1.5)
        self.assertEqual(assembly["tip_to_lid_top_mm"], 0.5)
        self.assertFalse(assembly["single_pin_limits_rotation"])
        self.assertFalse(assembly["printed"])
        self.assertFalse(assembly["fit_tested"])
        self.assertIsNone(assembly["qualified_clearance_mm"])

    def test_wrong_segment_count_radius_or_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "32 vertices"):
            checks.validate_tool_mesh(*tool_fixture(segments=16), "pin")
        with self.assertRaisesRegex(ValueError, "circumradius"):
            checks.validate_tool_mesh(*tool_fixture(radius=1.9), "pin")
        failed = copy.deepcopy(self.source["body"])
        failed["passed"] = False
        with self.assertRaisesRegex(ValueError, "original"):
            checks.validate_body_pin_mesh(*body_pin_fixture(), failed)

    def test_original_unmodified_lid_is_not_a_through_hole_result(self):
        with self.assertRaisesRegex(ValueError, "Euler"):
            checks.validate_lid_hole_mesh(*old.lid_fixture(), self.source["lid"])

    def test_missing_face_and_wrong_position_are_rejected(self):
        vertices, triangles = body_pin_fixture()
        with self.assertRaisesRegex(ValueError, "closed manifold"):
            checks.validate_body_pin_mesh(vertices, triangles[:-1], self.source["body"])
        vertices, triangles = tool_fixture()
        with self.assertRaises(ValueError):
            checks.validate_tool_mesh([(x + 0.2, y, z) for x, y, z in vertices], triangles, "pin")

    def test_phase_or_axial_mismatch_cannot_pass_assembly(self):
        body, lid = self.body(), self.lid()
        wrong = copy.deepcopy(lid)
        wrong["hole"]["polygon"]["phase_angle_rad"] += math.pi / 32
        with self.assertRaisesRegex(ValueError, "same phase"):
            checks.validate_tenon_assembly(body, wrong)
        wrong = copy.deepcopy(body)
        wrong["pin"]["tip_z_mm"] = 16
        with self.assertRaisesRegex(ValueError, "engagement"):
            checks.validate_tenon_assembly(wrong, lid)

    def test_actual_exact_boolean_collinear_split_preserves_32_facets(self):
        # Original, unedited world-mesh dump from the isolated Blender probe:
        # evidence/06/2026-10-25-tenon-operand-probe-v002/lid_mesh.json.
        # Exact Boolean added one z=15 sample 60% along an existing facet edge;
        # its distance from that line is 7.48e-8 mm, not a new polygon corner.
        data = (HERE / "fixtures/tenon-exact-boolean-lid-v001.json").read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "4ae28e1981fa44e9be4d504a2d62b5fcecda16ec9634c84127aaa8191e797d9a")
        actual = json.loads(data)
        lid = checks.validate_lid_hole_mesh(actual["vertices"], actual["triangles"], self.source["lid"])
        polygon = lid["hole"]["polygon"]
        self.assertEqual(polygon["segments"], 32)
        self.assertEqual(len(polygon["edge_planes"]), 32)
        self.assertEqual(len(lid["hole"]["radial_walls"]), 32)
        self.assertEqual([level["boundary_sample_count"] for level in polygon["boundary_levels"]], [33, 32])
        self.assertEqual([level["collinear_split_count"] for level in polygon["boundary_levels"]], [1, 0])
        self.assertEqual(lid["vertical_rays"][0]["z_hits_mm"], [])
        self.assertAlmostEqual(lid["volume_mm3"], 6164.984350685121, places=7)
        self.assertEqual(checks.EPS_MM, 1e-4)
        checks.validate_tenon_assembly(self.body(), lid)

    def test_true_31_or_33_corner_polygons_are_not_accepted_as_32(self):
        for number in (31, 33):
            with self.subTest(segments=number):
                with self.assertRaisesRegex(ValueError, "32 vertices/corners"):
                    checks.validate_tool_mesh(*tool_fixture(segments=number), "pin")

    def test_convex_boundary_does_not_hide_noncollinear_inward_or_outward_defects(self):
        data = json.loads((HERE / "fixtures/tenon-exact-boolean-lid-v001.json").read_text())
        for sign in (-1, 1):
            changed = copy.deepcopy(data)
            point = changed["vertices"][71]
            dx, dy = point[0] - 23, point[1] - 13
            r = math.hypot(dx, dy)
            point[0] += sign * 0.001 * dx / r
            point[1] += sign * 0.001 * dy / r
            with self.subTest(direction=sign):
                with self.assertRaises(ValueError):
                    checks.validate_lid_hole_mesh(changed["vertices"], changed["triangles"], self.source["lid"])
        # Exercise the actual boundary rejection directly as well, independent
        # of the complete mesh's wall-normal and wall-area checks.
        corners = _circle(2.2)
        a, b = corners[0], corners[1]
        middle = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        dx, dy = middle[0] - 23, middle[1] - 13
        r = math.hypot(dx, dy)
        middle[0] -= 0.001 * dx / r
        middle[1] -= 0.001 * dy / r
        with self.assertRaisesRegex(ValueError, "non-collinear boundary sample"):
            checks._polygon(corners + [middle], 2.2)


if __name__ == "__main__":
    unittest.main()
