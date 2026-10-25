"""Test rigid world poses and independently derived native polygon statistics."""
import copy
import importlib.util
import math
from pathlib import Path
import struct
import sys
import unittest


HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"scenarios"))
import overhang_checks as checks
from tenon_checks import _mesh
spec=importlib.util.spec_from_file_location("overhang_snap_fixtures",HERE/"test_snapfit_checks.py")
snap=importlib.util.module_from_spec(spec);spec.loader.exec_module(snap)


def settings_fixture():
    maximum=struct.unpack("<f",struct.pack("<f",math.pi/4))[0]
    return {"type":"OVERHANG","axis":"NEG_Z","minimum_radians":0.,"maximum_radians":maximum,
            "minimum_deg":0.,"maximum_deg":math.degrees(maximum),"show_statvis":True,
            "shading":"SOLID","xray":False}


def _raw(vertices,triangles,polygons=None,mapping=None):
    vertices=[list(v) for v in vertices];triangles=[list(t) for t in triangles]
    polygons=copy.deepcopy(polygons) if polygons is not None else copy.deepcopy(triangles)
    mapping=list(mapping) if mapping is not None else list(range(len(triangles)))
    return {"vertices":vertices,"triangles":triangles,"polygons":polygons,
            "triangle_polygon_indices":mapping,
            "polygon_normals_world":[list(checks._normal([vertices[i] for i in p])) for p in polygons],
            "cad_metadata":{"scale":[1,1,1],"modifier_count":0,
                            "object_rotation_euler_radians":[0,0,0],"unit_scale":.001,
                            "length_unit":"MILLIMETERS"}}


def source_fixture(kind):
    return _raw(*(snap.body_fixture() if kind=="body" else snap.lid_fixture()))


def pose_fixture(kind,pose="candidate",source=None):
    source=source or source_fixture(kind)
    rotation=checks.ROTATIONS[kind,pose]
    top=max(p[2] for p in source["vertices"])
    translation=([-40,0,15] if pose=="baseline" and kind=="body" else
                 [40,0,-10.2] if pose=="baseline" else
                 [-40,0,30] if kind=="body" else [40,-6,top])
    vertices=[[value+translation[i] for i,value in enumerate(checks._multiply(rotation,p))]
              for p in source["vertices"]]
    raw=_raw(vertices,source["triangles"],source["polygons"],source["triangle_polygon_indices"])
    raw["cad_metadata"]["object_rotation_euler_radians"]=(
        [0,0,0] if pose=="baseline" else [0,math.pi/2,0] if kind=="body" else [math.pi,0,0])
    return raw


def cube_fixture():
    vertices=[[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0],[-1,-1,2],[1,-1,2],[1,1,2],[-1,1,2]]
    polygons=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
    triangles=[];mapping=[]
    for index,(a,b,c,d) in enumerate(polygons):
        triangles.extend(((a,b,c),(a,c,d)));mapping.extend((index,index))
    return _raw(vertices,triangles,polygons,mapping)


class OverhangChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings=settings_fixture()
        cls.sources={k:source_fixture(k) for k in ("body","lid")}
        cls.parts={(k,p):checks.validate_orientation(cls.sources[k],pose_fixture(k,p,cls.sources[k]),k,cls.settings,p)
                   for k in ("body","lid") for p in ("baseline","candidate")}

    def test_four_poses_preserve_source_shape_and_land_actual_geometry_on_bed(self):
        for (kind,pose),part in self.parts.items():
            self.assertTrue(part["rigid_shape_preserved"])
            self.assertLess(part["max_rigid_vertex_residual_mm"],1e-10)
            self.assertAlmostEqual(part["minimum_world_z_mm"],0)
            self.assertTrue(part["inverse_geometry_readback"]["passed"])
            self.assertFalse(part["rotation_applied_to_mesh"])
        body=self.parts["body","candidate"]
        self.assertEqual(body["bounds_mm"]["min"],[-55,-24.5,0])
        self.assertEqual(body["bounds_mm"]["max"],[-25,20,60])
        self.assertTrue(body["layer_direction_readback"]["arm_length_parallel_bed"])
        self.assertTrue(body["layer_direction_readback"]["bending_direction_parallel_bed"])
        self.assertFalse(self.parts["body","baseline"]["layer_direction_readback"]["arm_length_parallel_bed"])

    def test_contact_area_and_elevated_downward_area_are_distinct(self):
        self.assertAlmostEqual(self.parts["body","baseline"]["bed_contact_area_mm2"],2400)
        self.assertAlmostEqual(self.parts["body","candidate"]["bed_contact_area_mm2"],1200)
        self.assertAlmostEqual(self.parts["lid","baseline"]["bed_contact_area_mm2"],27)
        lid=self.parts["lid","candidate"]
        self.assertAlmostEqual(lid["bed_contact_area_mm2"],2760)
        self.assertAlmostEqual(lid["derived_polygon_statistics"]["summary"]["fully_elevated_downward"]["area_mm2"],12)
        self.assertGreater(lid["derived_polygon_statistics"]["summary"]["derived_native_visible"]["area_mm2"],2760)
        self.assertIsNone(lid["support_required"])

    def test_polygon_counts_are_not_presented_as_loop_triangle_or_gpu_counts(self):
        result=checks.analyze_mesh(cube_fixture(),self.settings)
        poly=result["derived_polygon_statistics"]["summary"]
        tri=result["derived_loop_triangle_statistics"]["summary"]
        self.assertEqual(poly["all"]["count"],6)
        self.assertEqual(tri["all"]["count"],12)
        self.assertEqual(poly["bed_contact"]["count"],1)
        self.assertEqual(tri["bed_contact"]["count"],2)
        self.assertEqual(poly["bed_contact"]["area_mm2"],tri["bed_contact"]["area_mm2"])
        angles={round(r["angle_from_negative_z_deg"]) for r in result["derived_polygon_statistics"]["records"]}
        self.assertEqual(angles,{0,90,180})
        self.assertIn("not GPU",result["statistics_scope"])

    def test_native_remap_saturates_below_min_and_keeps_exact_max_boundary(self):
        self.assertEqual(checks.native_weight(5,10,45),1)
        self.assertEqual(checks.native_weight(10,10,45),1)
        self.assertEqual(checks.native_weight(45,10,45),0)
        self.assertEqual(checks.native_weight(45.00001,10,45),-1)
        self.assertAlmostEqual(checks.native_weight(27.5,10,45),.5)
        minimum,maximum=checks._settings(self.settings)
        self.assertGreater(maximum,45)  # Actual RNA float radians are retained.
        self.assertEqual(checks.native_weight(maximum,minimum,maximum),0)

    def test_subtle_shape_change_and_wrong_rotation_are_rejected_even_with_same_bbox(self):
        raw=pose_fixture("body")
        i=next(i for i,p in enumerate(raw["vertices"]) if abs(p[0]+47.7)<.01 and abs(p[2]-26.919615)<.01)
        raw["vertices"][i][1]+=.01
        with self.assertRaisesRegex(ValueError,"rigid transform"):
            checks.validate_orientation(self.sources["body"],raw,"body",self.settings)
        with self.assertRaises(ValueError):
            checks.validate_orientation(self.sources["body"],pose_fixture("body","baseline"),"body",self.settings)

    def test_applied_rotation_wrong_axis_or_hidden_xray_is_rejected(self):
        raw=pose_fixture("body");raw["cad_metadata"]["object_rotation_euler_radians"]=[0,0,0]
        with self.assertRaisesRegex(ValueError,"rotation was applied"):
            checks.validate_orientation(self.sources["body"],raw,"body",self.settings)
        for key,value in (("axis","POS_Z"),("xray",True),("show_statvis",False)):
            settings=dict(self.settings);settings[key]=value
            with self.assertRaises(ValueError):
                checks.analyze_mesh(cube_fixture(),settings)

    def test_bad_native_polygon_mapping_or_normal_cannot_fabricate_face_counts(self):
        raw=cube_fixture();raw["triangle_polygon_indices"][0]=1
        with self.assertRaisesRegex(ValueError,"mapping|boundary"):
            checks.analyze_mesh(raw,self.settings)
        raw=cube_fixture();raw["polygon_normals_world"][0]=[0,0,1]
        with self.assertRaisesRegex(ValueError,"normal"):
            checks.analyze_mesh(raw,self.settings)

    def test_below_bed_or_floating_part_is_not_excused_by_angle_colours(self):
        for delta in (-.01,.01):
            raw=cube_fixture();raw["vertices"]=[[x,y,z+delta] for x,y,z in raw["vertices"]]
            with self.assertRaisesRegex(ValueError,"bed"):
                checks.analyze_mesh(raw,self.settings)

    def test_layout_reports_only_separation_without_machine_bed_or_support_qualification(self):
        result=checks.validate_layout(self.parts["body","candidate"],self.parts["lid","candidate"])
        self.assertAlmostEqual(result["x_projection_gap_mm"],35)
        self.assertTrue(result["parts_geometrically_separate"])
        self.assertFalse(result["bed_capacity_checked"])
        self.assertIsNone(result["printer_bed_dimensions_mm"])
        self.assertIsNone(result["support_required"])
        self.assertIsNone(result["qualified_strength_N"])
        self.assertFalse(result["printed"])


if __name__=="__main__":
    unittest.main()
