"""Binary export fixtures test geometry/source matching beyond bounding boxes."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scenarios"))
from dovetail_checks import validate_body_mesh, validate_lid_mesh, validate_assembly
from dovetail_stl_checks import validate_dovetail_stl
from stl_checks import read_stl
SPEC = importlib.util.spec_from_file_location("dovetail_export_fixtures", HERE / "test_dovetail_checks.py")
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


def binary_stl(vertices, triangles, header=b"binary dovetail test export"):
    data = bytearray(header[:80].ljust(80, b"\0") + struct.pack("<I", len(triangles)))
    for face in triangles:
        coordinates = tuple(c for index in face for c in vertices[index])
        data.extend(struct.pack("<12fH", 0, 0, 0, *coordinates, 0))
    return bytes(data)


def source_fixture():
    body = validate_body_mesh(*fixture.body_fixture())
    lid = validate_lid_mesh(*fixture.lid_fixture())
    return {"passed": True, "body": body, "lid": lid, "assembly": validate_assembly(body, lid),
            "scene_path": "verified/u06_dovetail_slide_v001.blend",
            "scene_sha256": "b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e",
            "source_scene_path": "ancestor/u04_box_v001.blend", "source_scene_sha256": "b"*64}


def subdivide(vertices, triangles):
    points, faces = list(vertices), []
    for a, b, c in triangles:
        centre = tuple((vertices[a][axis]+vertices[b][axis]+vertices[c][axis])/3 for axis in range(3))
        index = len(points)
        points.append(centre)
        faces.extend(((a,b,index),(b,c,index),(c,a,index)))
    # Reverse vertex numbering and face order, while preserving orientation.
    n = len(points)
    return list(reversed(points)), [tuple(n-1-v for v in face) for face in reversed(faces)]


class DovetailSTLChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dovetail-stl-checks-")
        self.path = Path(self.temp.name)/"export.stl"
        self.source = source_fixture()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, vertices, triangles, header=b"binary dovetail test export"):
        self.path.write_bytes(binary_stl(vertices,triangles,header))
        return self.path

    def test_actual_body_and_lid_profiles_are_source_bound(self):
        for kind, make, dimensions, volume in (("body",fixture.body_fixture,[60,40,30],16655.36),
                                               ("lid",fixture.lid_fixture,[60,40,5.2],5752.32)):
            with self.subTest(kind=kind):
                result = validate_dovetail_stl(self.write(*make()),kind,self.source)
                self.assertTrue(result["passed"])
                self.assertEqual(result["kind"],"dovetail_stl")
                self.assertEqual(result["part_kind"],kind)
                for actual, expected in zip(result["dimensions_mm"],dimensions):
                    self.assertAlmostEqual(actual,expected,places=4)
                self.assertAlmostEqual(result["volume_mm3"],volume,places=2)
                self.assertEqual(result["non_manifold_edges"],0)
                self.assertEqual(result["connected_shells"],1)
                self.assertEqual(result["genus"],0)
                self.assertIn("actual_axis_planes",result["source_measurement_compared"])
                self.assertIn("vertical_rays",result["source_measurement_compared"])
                self.assertEqual(result["source_scene_path"],self.source["scene_path"])
                self.assertEqual(result["source_scene_sha256"],self.source["scene_sha256"])
                self.assertNotEqual(result["source_scene_sha256"],self.source["source_scene_sha256"])
                self.assertIn("no units",result["unit_interpretation"])
                self.assertAlmostEqual(result["assembly_readback"]["normal_side_gap_mm"],.2/math.sqrt(1.04),places=4)
                json.dumps(result)

    def test_reindexing_and_new_triangulation_do_not_require_a_source_signature(self):
        for kind, make in (("body",fixture.body_fixture),("lid",fixture.lid_fixture)):
            vertices, triangles = make()
            divided = subdivide(vertices,triangles)
            result = validate_dovetail_stl(self.write(*divided),kind,self.source)
            self.assertEqual(result["triangle_count"],3*len(triangles))
            self.assertNotEqual(result["geometry_readback"]["geometry_signature"],self.source[kind]["geometry_signature"])
            self.assertTrue(result["passed"])

    def test_per_part_source_is_supported_without_inventing_an_assembly(self):
        result = validate_dovetail_stl(self.write(*fixture.lid_fixture()),"SlidingLid",self.source["lid"])
        self.assertEqual(result["part_kind"],"lid")
        self.assertNotIn("assembly_readback",result)

    def test_same_bounds_blind_channels_are_rejected(self):
        path = self.write(*fixture.body_fixture(block_entries=True))
        self.assertEqual(read_stl(path)["dimensions_mm"],[60,40,30])
        with self.assertRaises(ValueError):
            validate_dovetail_stl(path,"body",self.source)

    def test_same_bounds_changed_male_profile_is_rejected(self):
        vertices,triangles = fixture.lid_fixture()
        altered = [(x,y+(.02 if z==12 and y>0 else 0),z) for x,y,z in vertices]
        path = self.write(altered,triangles)
        for a,b in zip(read_stl(path)["dimensions_mm"],[60,40,5.2]):
            self.assertAlmostEqual(a,b,places=4)
        with self.assertRaises(ValueError):
            validate_dovetail_stl(path,"lid",self.source)

    def test_second_hidden_tool_cannot_be_exported_alongside_body(self):
        vertices,triangles = fixture.body_fixture()
        tool_v,tool_t = fixture.tool_fixture("groove")
        combined = vertices+tool_v, triangles+[tuple(v+len(vertices) for v in t) for t in tool_t]
        with self.assertRaisesRegex(ValueError,"one connected"):
            validate_dovetail_stl(self.write(*combined),"body",self.source)

    def test_swapped_parts_scale_axis_and_world_z_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_dovetail_stl(self.write(*fixture.lid_fixture()),"body",self.source)
        vertices,triangles = fixture.lid_fixture()
        for transform in (lambda x,y,z:(x*.001,y*.001,z*.001),
                          lambda x,y,z:(x,z,-y),lambda x,y,z:(x,y,z-12)):
            with self.assertRaises(ValueError):
                validate_dovetail_stl(self.write([transform(*p) for p in vertices],triangles),"lid",self.source)

    def test_source_volume_profile_and_entry_measurements_must_match(self):
        self.write(*fixture.body_fixture())
        for mutate in (lambda d:d["body"].update(volume_mm3=16600),
                       lambda d:d["body"]["channels"][0]["profile"].update(widths_mm=[3.5,2.32]),
                       lambda d:d["body"]["full_length_entry_proof"].update(both_end_faces_have_channel_cutouts=False)):
            source=copy.deepcopy(self.source)
            mutate(source)
            with self.assertRaises(ValueError):
                validate_dovetail_stl(self.path,"body",source)

    def test_failed_or_missing_source_does_not_pass(self):
        self.write(*fixture.body_fixture())
        for source in (None,{"passed":False}, {"passed":True,"body":None}):
            with self.assertRaises(ValueError):
                validate_dovetail_stl(self.path,"body",source)

    def test_ascii_truncation_nonfinite_and_empty_binary_are_rejected(self):
        valid = binary_stl(*fixture.lid_fixture())
        nonfinite = bytearray(valid)
        struct.pack_into("<f",nonfinite,84,float("nan"))
        for data in (b"solid empty\nendsolid empty\n",valid[:-1],nonfinite,b"\0"*84):
            self.path.write_bytes(data)
            with self.assertRaises(ValueError):
                validate_dovetail_stl(self.path,"lid",self.source)

    def test_file_and_source_are_read_only_and_physical_fit_stays_unknown(self):
        self.write(*fixture.lid_fixture(),header=b"solid binary STL with valid facets")
        before=self.path.read_bytes()
        metadata=copy.deepcopy(self.source)
        result=validate_dovetail_stl(self.path,"lid",self.source)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(self.source,metadata)
        self.assertTrue(result["exported_stl"])
        self.assertFalse(result["slicer_checked"])
        self.assertFalse(result["printed"])
        self.assertFalse(result["fit_tested"])
        for key in ("physical_measurements","fit_results","physical_interference","qualified_clearance_mm"):
            self.assertIsNone(result[key])
        self.assertEqual(result["nominal_horizontal_total_trial_mm"],.4)


if __name__=="__main__":
    unittest.main()
