"""Three source-bound STL candidates; malformed files and semantic negatives."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"scenarios"))
import coupon_stl_checks as checks
import coupon_checks
spec=importlib.util.spec_from_file_location("coupon_export_fixtures",HERE/"test_coupon_checks.py")
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)


def source_fixture():
    tool=fixtures.source_fixture()
    raws={name:fixtures.coupon_fixture(name,"print_candidate",tool) for name in checks.SPECS}
    readings={name:coupon_checks.validate_coupon(tool,raw,name,"print_candidate") for name,raw in raws.items()}
    prior={"passed":True,"reopened":True,"kind":"snapfit_length_coupons_geometry_demo",
           "scene_path":"unit-test-coupon-source.blend","scene_sha256":checks.SOURCE_SHA256,
           "candidates":readings,"layout":coupon_checks.validate_coupon_layout(readings)}
    return prior,raws,tool


def binary_stl(vertices,triangles):
    data=bytearray(b"coupon test fixture".ljust(80,b" ")+struct.pack("<I",len(triangles)))
    for triangle in triangles:
        pts=[vertices[i] for i in triangle];a=[pts[1][i]-pts[0][i] for i in range(3)];b=[pts[2][i]-pts[0][i] for i in range(3)]
        normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
        magnitude=math.sqrt(sum(c*c for c in normal));normal=[c/magnitude for c in normal]
        data.extend(struct.pack("<12fH",*normal,*(c for p in pts for c in p),0))
    return bytes(data)


def subdivide(vertices,triangles):
    raw=fixtures.subdivide_raw({"vertices":vertices,"triangles":triangles})
    return raw["vertices"],raw["triangles"]


class CouponStlChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.source,cls.raws,cls.tool=source_fixture()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"coupon.stl"

    def validate(self,data,name="A_L19",source=None,raw=None,tool=None):
        self.path.write_bytes(data)
        return checks.validate_coupon_stl(self.path,name,source or self.source,raw or self.raws[name],tool or self.tool)

    def test_all_three_binary_candidates_world_layout_and_inverse_single_length(self):
        results={}
        for name,L in (("A_L19",19),("B_L17",17),("C_L21",21)):
            raw=self.raws[name];result=self.validate(binary_stl(raw["vertices"],raw["triangles"]),name)
            results[name]=result
            self.assertEqual(result["triangle_count"],80)
            self.assertAlmostEqual(result["L_geometry_mm"],L,places=4)
            self.assertTrue(result["world_pose_retained"]);self.assertEqual(result["connected_shells"],1)
            self.assertEqual(result["non_manifold_edges"],0);self.assertEqual(result["genus"],0)
            self.assertTrue(result["source_surface_match"]["passed"])
            self.assertAlmostEqual(result["bed_and_raised_features"]["bed_contact_area_mm2"],13.8,places=4)
            self.assertIsNone(result["support_required"]);self.assertIsNone(result["effective_mechanical_length_mm"])
            self.assertIsNone(result["improvement_validated"]);self.assertFalse(result["improvement_assessed"])
            self.assertIn("STL has no transform",result["pose_metadata_role"])
        layout=checks.validate_export_layout(results,self.source)
        self.assertAlmostEqual(layout["minimum_y_projection_gap_mm"],7.4,places=4)
        self.assertFalse(layout["bed_capacity_checked"])

    def test_reindexed_subdivided_binary_and_pure_reimport_are_accepted(self):
        for name in checks.SPECS:
            raw=self.raws[name];v,t=subdivide(raw["vertices"],raw["triangles"])
            count=len(v);v.reverse();t=[tuple(count-1-i for i in face) for face in reversed(t)]
            result=self.validate(binary_stl(v,t),name)
            self.assertEqual(result["triangle_count"],240)
            pure=checks.validate_coupon_export_mesh(v,t,name,self.source,raw,self.tool)
            self.assertTrue(pure["source_surface_match"]["passed"])
            self.assertFalse(pure["source_surface_match"]["indexing_or_triangulation_identity_required"])

    def test_fresh_reimport_world_mesh_does_not_need_original_object_origin_or_rotation(self):
        raw=copy.deepcopy(self.raws["C_L21"])
        raw["cad_metadata"].update(object_location_mm=[0,0,0],object_rotation_euler_radians=[0,0,0])
        result=checks.validate_coupon_export_mesh(raw["vertices"],raw["triangles"],"C_L21",self.source,self.raws["C_L21"],self.tool)
        self.assertAlmostEqual(result["dimensions_mm"][0],26,places=4)
        self.assertIn("reference",result["geometry_readback_scope"])
        self.assertEqual(raw["cad_metadata"]["object_rotation_euler_radians"],[0,0,0])

    def test_wrong_unit_scale_recenter_or_old_sourceframe_is_rejected(self):
        raw=self.raws["A_L19"]
        bad=[[[x*.001,y*.001,z*.001] for x,y,z in raw["vertices"]],
             [[x,y+12,z] for x,y,z in raw["vertices"]],
             fixtures.coupon_fixture("A_L19")["vertices"]]
        for vertices in bad:
            with self.assertRaises(ValueError): self.validate(binary_stl(vertices,raw["triangles"]))

    def test_exporting_wrong_variant_or_extra_hidden_tool_is_rejected(self):
        raw=self.raws["B_L17"]
        with self.assertRaises(ValueError): self.validate(binary_stl(raw["vertices"],raw["triangles"]))
        raw=copy.deepcopy(self.raws["A_L19"]);n=len(raw["vertices"])
        raw["vertices"] += [[x+30,y,z] for x,y,z in raw["vertices"]]
        raw["triangles"] += [[v+n for v in face] for face in raw["triangles"]]
        with self.assertRaises(ValueError): self.validate(binary_stl(raw["vertices"],raw["triangles"]))

    def test_root_miter_damage_same_bbox_and_changed_hook_or_arm_are_rejected(self):
        for index,axis in ((22,2),(16,1),(9,1)):
            raw=copy.deepcopy(self.raws["A_L19"]);raw["vertices"][index][axis]+=.02
            with self.assertRaises(ValueError): self.validate(binary_stl(raw["vertices"],raw["triangles"]))

    def test_ascii_truncation_nonfinite_degenerate_and_unoriented_are_rejected(self):
        raw=self.raws["A_L19"];valid=binary_stl(raw["vertices"],raw["triangles"])
        nan=bytearray(valid);struct.pack_into("<f",nan,84,float("nan"))
        degenerate=bytearray(valid);degenerate[84+24:84+36]=degenerate[84+12:84+24]
        reverse=binary_stl(raw["vertices"],[tuple(reversed(face)) for face in raw["triangles"]])
        for data in (b"solid ascii\nendsolid\n",valid[:-1],valid+b"x",nan,degenerate,reverse):
            with self.assertRaises(ValueError): self.validate(data)

    def test_wrong_source_hash_pose_or_reported_actual_length_is_rejected(self):
        raw=self.raws["A_L19"];valid=binary_stl(raw["vertices"],raw["triangles"])
        for alteration in ("hash","length","pose"):
            source=copy.deepcopy(self.source);candidate=copy.deepcopy(raw)
            if alteration=="hash": source["scene_sha256"]="0"*64
            if alteration=="length": source["candidates"]["A_L19"]["L_geometry_mm"]+=.1
            if alteration=="pose": candidate["cad_metadata"]["object_rotation_euler_radians"]=[0,0,0]
            with self.assertRaises(ValueError): self.validate(valid,source=source,raw=candidate)


if __name__=="__main__": unittest.main()
