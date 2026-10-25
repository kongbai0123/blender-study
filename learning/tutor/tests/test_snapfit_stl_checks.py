"""Source-bound world-pose STL checks, including valid retessellation."""
import copy
import importlib.util
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest


HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"scenarios"))
import snapfit_stl_checks as checks
import overhang_checks
spec=importlib.util.spec_from_file_location("snapfit_export_pose_fixtures",HERE/"test_overhang_checks.py")
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)


def binary_stl(vertices,triangles):
    data=bytearray(b"unit-test-only native-coordinate fixture".ljust(80,b"\0"))
    data.extend(struct.pack("<I",len(triangles)))
    for triangle in triangles:
        pts=[vertices[i] for i in triangle]
        a=[pts[1][i]-pts[0][i] for i in range(3)];b=[pts[2][i]-pts[0][i] for i in range(3)]
        n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
        size=math.sqrt(sum(v*v for v in n));n=[v/size for v in n]
        data.extend(struct.pack("<12fH",*n,*(c for p in pts for c in p),0))
    return bytes(data)


def source_fixture():
    settings=fixtures.settings_fixture();raws={};poses={}
    for kind in ("body","lid"):
        source=fixtures.source_fixture(kind);candidate=fixtures.pose_fixture(kind,"candidate",source)
        raws[kind]=candidate
        poses[kind+"_candidate"]=overhang_checks.validate_orientation(source,candidate,kind,settings)
    metadata={"passed":True,"scene_path":"unit-test-fixture-source.blend","scene_sha256":checks.SOURCE_SHA256,
              "poses":poses,"analysis_settings_by_pose":{k:settings for k in poses}}
    return metadata,raws


def subdivide(vertices,triangles):
    vertices=copy.deepcopy(vertices);output=[]
    for a,b,c in triangles:
        centre=[(vertices[a][i]+vertices[b][i]+vertices[c][i])/3 for i in range(3)]
        index=len(vertices);vertices.append(centre)
        output.extend(((a,b,index),(b,c,index),(c,a,index)))
    return vertices,output


class SnapfitStlChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.raw=source_fixture()

    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/"part.stl"

    def check_bytes(self,data,kind="body",source=None,raw=None):
        self.path.write_bytes(data)
        return checks.validate_snapfit_stl(self.path,kind,source or self.source,raw or self.raw[kind])

    def test_both_native_candidate_world_parts_roundtrip_with_inverse_profiles(self):
        results={}
        for kind in ("body","lid"):
            raw=self.raw[kind]
            result=self.check_bytes(binary_stl(raw["vertices"],raw["triangles"]),kind)
            results[kind]=result
            self.assertTrue(result["world_pose_retained"])
            self.assertTrue(result["inverse_geometry_readback"]["passed"])
            self.assertEqual(result["source_scene_sha256"],checks.SOURCE_SHA256)
            self.assertEqual(result["connected_shells"],1);self.assertEqual(result["non_manifold_edges"],0)
            self.assertAlmostEqual(result["minimum_world_z_mm"],0,places=5)
            self.assertIsNone(result["support_required"])
            self.assertFalse(result["slicer_checked"])
            self.assertIsNone(result["qualified_strength_N"])
        self.assertTrue(results["body"]["bounds_mm"]["min"][0]<0)
        self.assertAlmostEqual(results["body"]["dimensions_mm"][2],60,places=4)
        self.assertEqual(checks.validate_export_layout(results["body"],results["lid"])["x_projection_gap_mm"],35)

    def test_legal_subdivision_reindexing_does_not_require_fixed_triangle_counts(self):
        raw=self.raw["body"];vertices,triangles=subdivide(raw["vertices"],raw["triangles"])
        size=len(vertices);vertices.reverse();triangles=[tuple(size-1-i for i in t) for t in reversed(triangles)]
        result=self.check_bytes(binary_stl(vertices,triangles))
        self.assertEqual(result["triangle_count"],3*len(raw["triangles"]))
        self.assertTrue(result["source_surface_match"]["passed"])
        self.assertFalse(result["source_surface_match"]["indexing_or_triangulation_identity_required"])

    def test_reimport_origin_and_rotation_zero_are_allowed_when_world_mesh_is_preserved(self):
        raw=self.raw["lid"]
        result=checks.validate_snapfit_export_mesh(raw["vertices"],raw["triangles"],"lid",self.source,raw)
        self.assertTrue(result["world_pose_retained"])
        self.assertAlmostEqual(result["inverse_geometry_readback"]["mating_profile"]["ledge_projection_mm"],1.2)

    def test_recentering_original_assembly_or_wrong_scale_is_rejected(self):
        raw=self.raw["body"]
        variants=[[[x+55,y,z] for x,y,z in raw["vertices"]],
                  [[x*.001,y*.001,z*.001] for x,y,z in raw["vertices"]]]
        for vertices in variants:
            with self.assertRaises(ValueError):
                self.check_bytes(binary_stl(vertices,raw["triangles"]))
        original=fixtures.source_fixture("body")
        with self.assertRaises(ValueError):
            self.check_bytes(binary_stl(original["vertices"],original["triangles"]))

    def test_same_bbox_miter_deformation_and_a_second_hidden_tool_are_rejected(self):
        raw=self.raw["body"];vertices=copy.deepcopy(raw["vertices"])
        index=next(i for i,p in enumerate(vertices) if abs(p[0]+47.7)<.01 and abs(p[2]-26.919615)<.01)
        vertices[index][1]+=.02
        with self.assertRaises(ValueError):
            self.check_bytes(binary_stl(vertices,raw["triangles"]))
        offset=len(raw["vertices"])
        vertices=raw["vertices"]+[[x+100,y,z] for x,y,z in raw["vertices"]]
        triangles=raw["triangles"]+[[i+offset for i in t] for t in raw["triangles"]]
        with self.assertRaises(ValueError):
            self.check_bytes(binary_stl(vertices,triangles))

    def test_source_context_or_profile_tampering_is_rejected(self):
        raw=self.raw["body"];data=binary_stl(raw["vertices"],raw["triangles"])
        changed=copy.deepcopy(self.source);changed["scene_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"fixed successful"):
            self.check_bytes(data,source=changed)
        changed=copy.deepcopy(self.source)
        changed["poses"]["body_candidate"]["inverse_geometry_readback"]["snap_profile"]["hook_projection_mm"]+=.1
        with self.assertRaises(ValueError):
            self.check_bytes(data,source=changed)

    def test_binary_parser_rejects_ascii_truncated_nonfinite_empty_and_degenerate(self):
        raw=self.raw["lid"];data=binary_stl(raw["vertices"],raw["triangles"])
        nan=bytearray(data);struct.pack_into("<f",nan,84+12,float("nan"))
        degenerate=bytearray(data);degenerate[84+24:84+36]=degenerate[84+12:84+24]
        variants=[b"solid part\nendsolid part\n",data[:-1],bytes(nan),b"x"*80+struct.pack("<I",0),bytes(degenerate)]
        for value in variants:
            with self.assertRaises(ValueError):
                self.check_bytes(value,"lid")


if __name__=="__main__":
    unittest.main()
