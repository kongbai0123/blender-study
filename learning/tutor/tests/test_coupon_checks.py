"""Meaningful single-L invariants, native miters, reindexing and subdivisions."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scenarios"))
import coupon_checks as checks


def source_fixture():
    """Pinned real Native Bevel fixture; no published model is generated here."""
    fixture = json.loads((HERE / "fixtures/snapfit-native-bevel-tool-v001.json").read_text(encoding="utf-8"))
    raw = copy.deepcopy(fixture["raw_mesh"])
    raw["cad_metadata"]["object_rotation_euler_radians"] = [0., 0., 0.]
    return raw


def coupon_fixture(variant="A_L19", pose="source_frame", source=None):
    source = source or source_fixture()
    raw = copy.deepcopy(source)
    spec = checks.SPECS[variant]
    for p in raw["vertices"]:
        if p[2] >= 11.:
            p[2] += spec["upper_vertex_translation_z_mm"]
    raw["cad_metadata"]["object_name"] = variant
    if pose == "print_candidate":
        translation = checks._translation(spec)
        raw["vertices"] = [[sum(a*b for a,b in zip(row,p))+t for row,t in zip(checks.ROTATION,translation)]
                           for p in raw["vertices"]]
        raw["cad_metadata"].update(object_location_mm=spec["candidate_object_location_mm"],
                                   object_rotation_euler_radians=[0.,math.pi/2,0.])
    return raw


def subdivide_raw(raw):
    raw = copy.deepcopy(raw)
    triangles = []
    for a,b,c in raw["triangles"]:
        index = len(raw["vertices"])
        raw["vertices"].append([sum(raw["vertices"][v][i] for v in (a,b,c))/3 for i in range(3)])
        triangles.extend(((a,b,index),(b,c,index),(c,a,index)))
    raw["triangles"] = triangles
    return raw


class CouponChecksTests(unittest.TestCase):
    def test_native_source_selection_is_fourteen_upper_and_twenty_eight_unchanged(self):
        result = checks.validate_source_snap_tool(source_fixture())
        selection = result["native_ui_selection_reference"]
        self.assertEqual(selection["upper_vertex_count"],14)
        self.assertEqual(selection["unchanged_vertex_count"],28)
        self.assertTrue(selection["original_42_vertex_14_upper_reference"])
        self.assertEqual(result["geometry_readback"]["profiles"]["native_miter_count"],12)

    def test_all_three_source_frame_and_candidate_lengths_preserve_roots_and_hooks(self):
        source = source_fixture();results = {}
        for name,spec in checks.SPECS.items():
            frame = checks.validate_coupon(source,coupon_fixture(name),name)
            world = checks.validate_coupon(source,coupon_fixture(name,"print_candidate"),name,"print_candidate")
            results[name] = world
            self.assertAlmostEqual(frame["L_geometry_mm"],spec["L_geometry_mm"],places=5)
            self.assertAlmostEqual(frame["total_arm_height_mm"],spec["total_arm_height_mm"],places=5)
            self.assertTrue(world["source_surface_match"]["passed"])
            self.assertTrue(world["canonical_vertex_mapping"]["native_vertex_identity_proof_available"])
            self.assertEqual(world["non_manifold_edges"],0);self.assertEqual(world["connected_shells"],1)
            self.assertIsNone(world["effective_mechanical_length_mm"])
            self.assertFalse(world["improvement_assessed"]);self.assertIsNone(world["improvement_validated"])
            bed = world["bed_and_raised_features"]
            self.assertAlmostEqual(bed["bed_contact_area_mm2"],13.8,places=4)
            self.assertAlmostEqual(bed["raised_features"]["straight_beam"]["world_z_range_mm"][0],1.5,places=4)
            self.assertAlmostEqual(bed["raised_features"]["root_fillet_and_miters"]["world_z_range_mm"][0],.9,places=4)
            self.assertIsNone(bed["support_required"])
        layout = checks.validate_coupon_layout(results)
        self.assertAlmostEqual(layout["minimum_y_projection_gap_mm"],7.4,places=4)
        self.assertIsNone(layout["anchor_clamping_or_fixture"])

    def test_continuous_inverse_accepts_reindexed_subdivisions_of_lengthened_arm(self):
        source=source_fixture()
        for name in ("B_L17","C_L21"):
            for pose in ("source_frame","print_candidate"):
                raw=subdivide_raw(subdivide_raw(coupon_fixture(name,pose)))
                size=len(raw["vertices"]);raw["vertices"].reverse()
                raw["triangles"]=[tuple(size-1-i for i in tri) for tri in reversed(raw["triangles"])]
                result=checks.validate_coupon(source,raw,name,pose)
                self.assertEqual(result["mesh_counts"]["triangles"],720)
                self.assertTrue(result["source_surface_match"]["passed"])
                self.assertFalse(result["canonical_vertex_mapping"]["native_vertex_identity_proof_available"])

    def test_changing_root_miter_or_hook_projection_is_rejected(self):
        source=source_fixture()
        for index,axis in ((22,0),(16,1)):
            raw=coupon_fixture("B_L17");raw["vertices"][index][axis]+=.02
            with self.assertRaises(ValueError):
                checks.validate_coupon(source,raw,"B_L17")

    def test_moving_whole_arm_or_scaling_is_not_single_parameter_change(self):
        source=source_fixture();raw=coupon_fixture("B_L17")
        for p in raw["vertices"]:
            if -8.01<p[2]<8.:
                p[2]-=2
        with self.assertRaises(ValueError): checks.validate_coupon(source,raw,"B_L17")
        raw=coupon_fixture("B_L17");raw["vertices"]=[[x*1.01,y,z] for x,y,z in raw["vertices"]]
        with self.assertRaises(ValueError): checks.validate_coupon(source,raw,"B_L17")

    def test_wrong_bearing_length_or_thickness_is_rejected(self):
        source=source_fixture()
        with self.assertRaises(ValueError): checks.validate_coupon(source,coupon_fixture("B_L17"),"C_L21")
        raw=coupon_fixture("C_L21")
        raw["vertices"]=[[x,y+.02 if abs(y+21.400001525878906)<1e-6 else y,z] for x,y,z in raw["vertices"]]
        with self.assertRaises(ValueError): checks.validate_coupon(source,raw,"C_L21")

    def test_wrong_candidate_pose_apply_rotation_and_bed_translation_are_rejected(self):
        source=source_fixture()
        for alteration in ("rotate","bed","scale"):
            raw=coupon_fixture("A_L19","print_candidate")
            if alteration=="rotate": raw["cad_metadata"]["object_rotation_euler_radians"]=[0,0,0]
            if alteration=="bed": raw["vertices"]=[[x,y,z+.01] for x,y,z in raw["vertices"]]
            if alteration=="scale": raw["cad_metadata"]["scale"]=[1,1,1.01]
            with self.assertRaises(ValueError): checks.validate_coupon(source,raw,"A_L19","print_candidate")

    def test_extra_hidden_component_missing_triangle_and_reversed_winding_are_rejected(self):
        source=source_fixture()
        variants=[]
        raw=coupon_fixture();raw["triangles"]=raw["triangles"][:-1];variants.append(raw)
        raw=coupon_fixture();raw["triangles"]=[list(reversed(t)) for t in raw["triangles"]];variants.append(raw)
        raw=coupon_fixture();size=len(raw["vertices"])
        raw["vertices"] += [[x+20,y,z] for x,y,z in raw["vertices"]]
        raw["triangles"] += [[i+size for i in t] for t in raw["triangles"]];variants.append(raw)
        for raw in variants:
            with self.assertRaises(ValueError): checks.validate_coupon(source,raw,"A_L19")

    def test_mutated_plan_and_layout_wrong_row_are_rejected(self):
        source=source_fixture();spec=copy.deepcopy(checks.SPECS["A_L19"]);spec["L_geometry_mm"]=20
        with self.assertRaises(ValueError): checks.validate_coupon(source,coupon_fixture(),spec)
        results={name:checks.validate_coupon(source,coupon_fixture(name,"print_candidate"),name,"print_candidate") for name in checks.SPECS}
        results["B_L17"]["bounds_mm"]["min"][1]-=.1
        with self.assertRaises(ValueError): checks.validate_coupon_layout(results)


if __name__=="__main__": unittest.main()
