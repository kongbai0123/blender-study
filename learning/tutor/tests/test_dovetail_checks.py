"""Conformal analytic-cell fixtures test full entries and sloped clearances."""
import copy
import importlib.util
import math
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scenarios"))
import dovetail_checks as checks
SPEC = importlib.util.spec_from_file_location("dovetail_source_fixtures", HERE / "test_lid_checks.py")
old = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(old)


def source_fixture():
    return old.body_fixture()


def profile_surface(xs, zs, lines, occupied):
    """Boundary of cells with linear Y(Z) sides; no Blender or mesh operators."""
    lower, upper = min(zs), max(zs)
    values = list(zs)
    for i, (ma, ba) in enumerate(lines):
        for mb, bb in lines[i+1:]:
            if abs(ma-mb) > 1e-12:
                z = (bb-ba)/(ma-mb)
                if lower < z < upper:
                    values.append(z)
    levels = []
    for value in sorted(values):
        if not levels or value-levels[-1] > 1e-8:
            levels.append(value)
    vertices, mapping, triangles = [], {}, []

    def vertex(point):
        key = tuple(round(c, 9) for c in point)
        if key not in mapping:
            mapping[key] = len(vertices)
            vertices.append(key)
        return mapping[key]

    def face(points):
        ids = []
        for point in points:
            index = vertex(point)
            if not ids or index != ids[-1]:
                ids.append(index)
        if len(ids) > 1 and ids[0] == ids[-1]:
            ids.pop()
        if len(ids) < 3:
            return
        for j in range(1, len(ids)-1):
            triangles.append((ids[0], ids[j], ids[j+1]))

    for x0, x1 in zip(xs, xs[1:]):
        xm = (x0+x1)/2
        for z0, z1 in zip(levels, levels[1:]):
            zm = (z0+z1)/2
            ordered = sorted(lines, key=lambda line: line[0]*zm+line[1])
            for left, right in zip(ordered, ordered[1:]):
                l0, l1 = left[0]*z0+left[1], left[0]*z1+left[1]
                r0, r1 = right[0]*z0+right[1], right[0]*z1+right[1]
                lm, rm = left[0]*zm+left[1], right[0]*zm+right[1]
                if rm-lm <= 1e-8 or not occupied(xm, (lm+rm)/2, zm):
                    continue
                a,b,c,d = (x0,l0,z0),(x1,l0,z0),(x1,r0,z0),(x0,r0,z0)
                e,f,g,h = (x0,l1,z1),(x1,l1,z1),(x1,r1,z1),(x0,r1,z1)
                delta = 1e-7
                if not occupied(xm, (l0+r0)/2, z0-delta):
                    face([a,d,c,b])
                if not occupied(xm, (l1+r1)/2, z1+delta):
                    face([e,f,g,h])
                if not occupied(xm, lm-delta, zm):
                    face([a,b,f,e])
                if not occupied(xm, rm+delta, zm):
                    face([d,h,g,c])
                if not occupied(x0-delta, (lm+rm)/2, zm):
                    face([a,e,h,d])
                if not occupied(x1+delta, (lm+rm)/2, zm):
                    face([b,c,g,f])
    # Degenerate cell tips can create unused cached vertices; the fixture itself
    # removes them, while production validators still reject unused vertices.
    used = sorted({v for triangle in triangles for v in triangle})
    remap = {v:i for i,v in enumerate(used)}
    return [vertices[v] for v in used], [tuple(remap[v] for v in triangle) for triangle in triangles]


def _slopes(half_intercept):
    return [(slope, centre + sign*half_intercept)
            for centre in (-17,17) for sign,slope in ((-1,.2),(1,-.2))]


def body_fixture(block_entries=False):
    def material(x,y,z):
        if not (-30 < x < 30 and -20 < y < 20 and -15 < z < 15):
            return False
        cavity_half = 18 if z < 10 else 14
        solid = abs(x) > 28 or z < -13 or abs(y) > cavity_half
        if solid and z > 11.8 and (not block_entries or abs(x) < 28):
            if any(abs(y-centre) < 4.16-.2*z for centre in (-17,17)):
                return False
        return solid
    return profile_surface([-30,-28,28,30], [-15,-13,10,11.8,15],
                           [(0,y) for y in (-20,-18,-14,14,18,20)]+_slopes(4.16), material)


def lid_fixture():
    def material(x,y,z):
        return (-30 < x < 30 and 12 < z < 17.2 and
                ((z > 15.2 and abs(y) < 20) or
                 (z < 15.2 and any(abs(y-centre) < 3.96-.2*z for centre in (-17,17)))))
    return profile_surface([-30,30], [12,15.2,17.2], [(0,-20),(0,20)]+_slopes(3.96), material)


def tool_fixture(kind):
    if kind == "guide":
        material = lambda x,y,z: -30<x<30 and 10<z<15 and 14<abs(y)<20
        return profile_surface([-30,30], [10,15], [(0,y) for y in (-20,-14,14,20)], material)
    half, lo, hi, length = (4.16,11.8,15.8,31) if kind == "groove" else (3.96,12,15.4,30)
    material = lambda x,y,z: -length<x<length and lo<z<hi and any(abs(y-c)<half-.2*z for c in (-17,17))
    return profile_surface([-length,length], [lo,hi], _slopes(half), material)


def travel_fixture():
    vertices, triangles = lid_fixture()
    return {str(distance): {"vertices": [(x+distance,y,z) for x,y,z in vertices], "triangles": triangles,
                            "cad_metadata": {"object_name":"SlidingLid","scale":[1,1,1],"modifier_count":0,
                                             "unit_scale":.001,"length_unit":"MILLIMETERS",
                                             "object_location_mm":[distance,0,16.2]}}
            for distance in (30,62)}


class DovetailChecksTests(unittest.TestCase):
    def test_each_paired_tool_is_closed_and_measures_the_full_construction_profile(self):
        for kind, volume in (("guide",3600),("groove",1388.8),("male",995.52)):
            result = checks.validate_tool_mesh(*tool_fixture(kind),kind)
            self.assertEqual(result["connected_shells"],2)
            self.assertEqual(result["euler_characteristic"],4)
            self.assertAlmostEqual(result["volume_mm3"],volume,places=5)
        groove = checks.validate_tool_mesh(*tool_fixture("groove"),"groove")
        self.assertEqual(groove["profiles"][0]["profile"]["z_mm"],[11.8,15.8])

    def test_final_body_has_real_full_length_entries_and_records_the_thinner_webs(self):
        body = checks.validate_body_mesh(*body_fixture())
        self.assertAlmostEqual(body["volume_mm3"],16655.36,places=4)
        self.assertEqual(body["dimensions_mm"],[60,40,30])
        self.assertEqual(body["local_cavity_width_mm"],28)
        self.assertAlmostEqual(body["min_guide_ligament_mm"],1.2)
        self.assertAlmostEqual(body["channel_floor_web_mm"],1.8)
        self.assertEqual([plane["coordinate_mm"] for plane in body["actual_axis_planes"]["X"]],[-30,-28,28,30])
        self.assertEqual(len(body["full_length_entry_proof"]["end_face_area_mm2"]),2)
        self.assertTrue(all(channel["open_ends"] for channel in body["channels"]))
        for channel in body["channels"]:
            for actual, expected in zip(channel["profile"]["widths_mm"],[3.6,2.32]):
                self.assertAlmostEqual(actual,expected)

    def test_final_lid_exposes_only_the_male_below_the_plate(self):
        lid = checks.validate_lid_mesh(*lid_fixture())
        self.assertAlmostEqual(lid["volume_mm3"],5752.32,places=4)
        self.assertAlmostEqual(lid["dimensions_mm"][2],5.2)
        for actual,expected in zip(lid["plate_z_mm"],[15.2,17.2]):
            self.assertAlmostEqual(actual,expected)
        self.assertAlmostEqual(lid["exposed_male_depth_mm"],3.2)
        for actual,expected in zip(lid["male_ribs"][0]["profile"]["z_mm"],[12,15.2]):
            self.assertAlmostEqual(actual,expected)

    def test_horizontal_trial_and_actual_normal_gaps_are_different(self):
        assembly = checks.validate_assembly(checks.validate_body_mesh(*body_fixture()),checks.validate_lid_mesh(*lid_fixture()))
        self.assertEqual(len(assembly["side_clearances"]),4)
        self.assertAlmostEqual(assembly["horizontal_side_gap_mm"],.2)
        self.assertAlmostEqual(assembly["normal_side_gap_mm"],.2/math.sqrt(1.04))
        self.assertLess(assembly["normal_side_gap_mm"],.2)
        self.assertAlmostEqual(assembly["bottom_gap_mm"],.2)
        self.assertAlmostEqual(assembly["plate_rim_gap_mm"],.2)
        self.assertFalse(assembly["overhang_analysis_performed"])
        self.assertFalse(assembly["printed"])
        self.assertIsNone(assembly["qualified_clearance_mm"])

    def test_actual_partial_and_full_disengagement_are_recomputed_from_translated_meshes(self):
        body,lid=checks.validate_body_mesh(*body_fixture()),checks.validate_lid_mesh(*lid_fixture())
        travel=checks.validate_travel(body,lid,travel_fixture())
        self.assertEqual([s["overlap_length_mm"] for s in travel["states"]],[60,30,0])
        self.assertFalse(travel["states"][1]["fully_disengaged"])
        self.assertTrue(travel["states"][2]["fully_disengaged"])
        self.assertEqual(travel["states"][2]["end_gap_mm"],2)
        self.assertTrue(travel["continuous_sweep_geometric_nonintersection"])

    def test_same_bounds_blind_channels_cannot_claim_open_entry(self):
        with self.assertRaises(ValueError):
            checks.validate_body_mesh(*body_fixture(block_entries=True))

    def test_wrong_profile_slope_or_missing_face_is_rejected(self):
        vertices,triangles=lid_fixture()
        with self.assertRaises(ValueError):
            checks.validate_lid_mesh(vertices,triangles[:-1])
        altered=[(x,y+(0.02 if z==12 and y>0 else 0),z) for x,y,z in vertices]
        with self.assertRaises(ValueError):
            checks.validate_lid_mesh(altered,triangles)

    def test_changed_y_position_or_wrong_travel_distance_is_rejected(self):
        body,lid=checks.validate_body_mesh(*body_fixture()),checks.validate_lid_mesh(*lid_fixture())
        raw=travel_fixture()
        raw["30"]["vertices"]=[(x,y+.1,z) for x,y,z in raw["30"]["vertices"]]
        with self.assertRaises(ValueError):
            checks.validate_travel(body,lid,raw)
        raw=travel_fixture()
        raw["62"]["vertices"]=[(x-1,y,z) for x,y,z in raw["62"]["vertices"]]
        with self.assertRaisesRegex(ValueError,"translation"):
            checks.validate_travel(body,lid,raw)


if __name__=="__main__":
    unittest.main()
