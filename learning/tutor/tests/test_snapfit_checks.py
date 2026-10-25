"""Analytic closed trial fixtures exercise actual surface and gap validation."""
import copy
import importlib.util
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scenarios"))
import snapfit_checks as checks
from lid_checks import validate_body_mesh as original_body


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = _load("snapfit_original_fixtures", "test_lid_checks.py")
profiles = _load("snapfit_profile_fixtures", "test_dovetail_checks.py")


def source_fixture():
    return old.body_fixture()


def _native_fixture(filename):
    record=json.loads((HERE/"fixtures"/filename).read_text(encoding="utf-8"))
    raw=record["raw_mesh"]
    return copy.deepcopy(raw["vertices"]),copy.deepcopy(raw["triangles"])


def _polygon(no_fillet=False, wrong_ramp=False):
    # Independently state the geometry: six 30-degree root chords and one ramp.
    outer = [(-23.6+.6*math.sin(i*math.pi/6), -7.4-.6*math.cos(i*math.pi/6)) for i in range(4)]
    inner = [(-20.8-.6*math.sin(i*math.pi/6), -7.4-.6*math.cos(i*math.pi/6)) for i in range(4)]
    if no_fillet:
        outer,inner=[(-23,-8)],[(-21.4,-8)]
    return ([(-24.5,-11),(-19.9,-11),(-19.9,-8)]+inner+
            [(-21.4,13),(-23.2 if wrong_ramp else -23.4,13),(-24.2,12.2),(-24.2,11),(-23,11)]+
            list(reversed(outer))+[(-24.5,-8)])


def _inside(polygon,y,z):
    inside=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>z)!=(b[1]>z):
            cross=a[0]+(z-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if y<cross:
                inside=not inside
    return inside


def _snap_surface(body=False,no_fillet=False,wrong_ramp=False):
    polygon=_polygon(no_fillet,wrong_ramp)
    lines=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if abs(a[1]-b[1])>1e-10:
            slope=(b[0]-a[0])/(b[1]-a[1])
            line=(slope,a[0]-slope*a[1])
            if not any(abs(line[0]-l[0])<1e-9 and abs(line[1]-l[1])<1e-9 for l in lines):
                lines.append(line)
    if body:
        lines.extend((0,y) for y in (-20,-18,18,20))
    def material(x,y,z):
        anchor=abs(x)<4.5 and -24.5<y<-19.9 and -11<z<-8
        snap=anchor or (abs(x)<3 and _inside(polygon,y,z))
        source=(body and abs(x)<30 and abs(y)<20 and -15<z<15 and
                (abs(x)>28 or abs(y)>18 or z<-13))
        return snap or source
    levels=sorted(set(p[1] for p in polygon)|({-15,-13,15} if body else set()))
    xs=[-30,-28,-4.5,-3,3,4.5,28,30] if body else [-4.5,-3,3,4.5]
    return profiles.profile_surface(xs,levels,lines,material)


def tool_fixture(kind="snap",**kwargs):
    if kind=="snap":
        return _snap_surface(**kwargs) if kwargs else _native_fixture("snapfit-native-bevel-tool-v001.json")
    if kind!="flange":
        raise ValueError(kind)
    return old.cell_surface([-5,5],[-26,-24.5,-23.3],[10.2,10.8,15.4],
                            lambda x,y,z:y<-24.5 or z<10.8)


def body_fixture(**kwargs):
    return _snap_surface(body=True,**kwargs) if kwargs else _native_fixture("snapfit-native-union-body-v001.json")


def lid_fixture(ledge_top=10.8,solid_skirt=False):
    return old.cell_surface([-30,-5,5,30],[-26,-24.5,-23.3,20],[10.2,ledge_top,15.2,17.2],
             lambda x,y,z:z>15.2 or (abs(x)<5 and y<-23.3 and
                          (solid_skirt or y<-24.5 or z<ledge_top)))


class SnapfitChecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=original_body(*source_fixture())
        cls.snap_raw=tool_fixture("snap")
        cls.body_raw=body_fixture()
        cls.lid_raw=lid_fixture()
        cls.body=checks.validate_body_mesh(*cls.body_raw,cls.source)
        cls.lid=checks.validate_lid_mesh(*cls.lid_raw)

    def test_actual_tool_profiles_have_two_three_segment_roots_and_45_degree_ramp(self):
        snap=checks.validate_tool_mesh(*self.snap_raw,"snap")
        self.assertAlmostEqual(snap["volume_mm3"],339.4844908728352,places=7)
        self.assertEqual(snap["profiles"]["native_miter_count"],12)
        self.assertEqual(len(snap["profiles"]["native_end_miters"]),12)
        for cap in snap["profiles"]["native_end_miters"]:
            self.assertEqual(len(cap["corners_mm"]),3)
            self.assertGreater(abs(cap["normal"][0]),.4)
            self.assertGreater(cap["area_mm2"],.1)
        self.assertEqual(snap["connected_shells"],1)
        self.assertEqual([f["segments"] for f in snap["snap_profile"]["root_fillets"]],[3,3])
        for fillet in snap["snap_profile"]["root_fillets"]:
            self.assertEqual(len(fillet["chord_endpoints_yz_mm"]),4)
            self.assertAlmostEqual(fillet["fitted_circle_radius_mm"],.6,places=5)
        self.assertAlmostEqual(snap["snap_profile"]["entry_angle_deg"],45,places=5)
        flange=checks.validate_tool_mesh(*tool_fixture("flange"),"flange")
        self.assertAlmostEqual(flange["volume_mm3"],85.2)
        self.assertAlmostEqual(flange["bounds_mm"]["max"][2],15.4)

    def test_final_body_reads_original_cavity_and_changed_external_bounds(self):
        b=self.body
        self.assertEqual(b["dimensions_mm"],[60,44.5,30])
        self.assertAlmostEqual(b["volume_mm3"],15888.784532071566,places=7)
        self.assertEqual(b["cavity_dimensions_mm"],[56,36,28])
        self.assertTrue(b["source_core_preserved"])
        self.assertFalse(b["whole_body_geometry_unchanged"])
        self.assertAlmostEqual(b["snap_profile"]["beam_thickness_mm"],1.6,places=5)
        self.assertAlmostEqual(b["snap_profile"]["root_to_bearing_geometric_length_mm"],19)
        self.assertFalse(b["snap_profile"]["effective_mechanical_length_confirmed"])
        self.assertEqual(b["non_manifold_edges"],0)
        self.assertEqual(b["genus"],0)

    def test_final_lid_is_integrated_plate_skirt_and_ledge_with_air_above_ledge(self):
        lid=self.lid
        self.assertAlmostEqual(lid["volume_mm3"],5602.2,places=5)
        for a,b in zip(lid["dimensions_mm"],[60,46,7]):
            self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(lid["mating_profile"]["ledge_projection_mm"],1.2)
        self.assertEqual(lid["vertical_rays"][2]["z_hits_mm"],[10.2,10.8,15.2,17.2])

    def test_static_gaps_distinguish_straight_beam_and_local_root_fillet_space(self):
        result=checks.validate_assembly(self.body,self.lid)
        for k,v in (("plate_rim_gap_mm",.2),("beam_ledge_gap_mm",.3),("hook_skirt_gap_mm",.3),
                    ("hook_ledge_projection_overlap_mm",.9),("hook_ledge_vertical_gap_mm",.2),
                    ("straight_beam_inward_static_space_mm",1.4),("inner_root_fillet_local_static_gap_mm",.8)):
            self.assertAlmostEqual(result[k],v,places=5)
        self.assertTrue(result["geometric_nonintersection"])
        for key in ("required_deflection_mm","delta_allow_mm","epsilon_allow","material_grade",
                    "root_flexibility_Q","insertion_force_N","qualified_strength_N","qualified_clearance_mm"):
            self.assertIsNone(result[key])
        self.assertFalse(result["strength_analysis_performed"])
        self.assertFalse(result["fit_tested"])

    def test_same_outer_bounds_missing_roots_and_wrong_hook_ramp_are_rejected(self):
        for kwargs in ({"no_fillet":True},{"wrong_ramp":True}):
            with self.assertRaises(ValueError):
                checks.validate_tool_mesh(*tool_fixture("snap",**kwargs),"snap")

    def test_native_probe_fixtures_are_pinned_to_actual_readback_hashes(self):
        expected={"snapfit-native-bevel-tool-v001.json":"364cb250792aafa2b7b6b9fadcbf668a987393d642e3933ca4e55d6c063529f1",
                  "snapfit-native-union-body-v001.json":"f40578c09793b6418afaf6b3f5508016a7186022f46bf37695f0c9d25e6df86f"}
        for filename,digest in expected.items():
            record=json.loads((HERE/"fixtures"/filename).read_text(encoding="utf-8"))
            self.assertEqual(record["evidence_kind"],"actual_blender_native_ui_probe")
            if digest is not None:
                self.assertEqual(record["source_sha256"],digest)
            source=HERE.parents[2]/record["source_path"]
            if source.is_file():
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),record["source_sha256"])

    def test_miter_endpoint_displacement_with_unchanged_bbox_is_rejected(self):
        vertices,triangles=tool_fixture("snap")
        index=next(i for i,p in enumerate(vertices) if abs(p[0]-3.3)<1e-4 and abs(p[1]+23.3)<1e-4)
        vertices[index][0]+=.01
        with self.assertRaisesRegex(ValueError,"sloped|facet"):
            checks.validate_tool_mesh(vertices,triangles,"snap")

    def test_subdividing_native_triangles_preserves_finite_facet_checks(self):
        vertices,triangles=tool_fixture("snap")
        split=[]
        for a,b,c in triangles:
            midpoint=[(vertices[a][i]+vertices[b][i]+vertices[c][i])/3 for i in range(3)]
            index=len(vertices);vertices.append(midpoint)
            split.extend(((a,b,index),(b,c,index),(c,a,index)))
        result=checks.validate_tool_mesh(vertices,split,"snap")
        self.assertEqual(result["mesh_counts"]["triangles"],240)
        self.assertEqual(result["profiles"]["native_miter_count"],12)

    def test_same_lid_bbox_wrong_ledge_or_solid_skirt_is_rejected(self):
        for raw in (lid_fixture(ledge_top=10.9),lid_fixture(solid_skirt=True)):
            with self.assertRaises(ValueError):
                checks.validate_lid_mesh(*raw)

    def test_missing_face_reverse_winding_or_hidden_extra_shell_cannot_pass(self):
        vertices,triangles=self.lid_raw
        for altered in (triangles[:-1],[tuple(reversed(t)) for t in triangles]):
            with self.assertRaises(ValueError):
                checks.validate_lid_mesh(vertices,altered)
        offset=len(vertices)
        extra=[(x+100,y,z) for x,y,z in vertices]
        with self.assertRaisesRegex(ValueError,"one connected shell"):
            checks.validate_lid_mesh(vertices+extra,triangles+[tuple(i+offset for i in t) for t in triangles])

    def test_source_report_and_tampered_assembly_reference_are_rejected(self):
        wrong=copy.deepcopy(self.source)
        wrong["cavity_dimensions_mm"][1]=35
        with self.assertRaisesRegex(ValueError,"reference dimensions"):
            checks.validate_body_mesh(*self.body_raw,wrong)
        lid=copy.deepcopy(self.lid)
        lid["mating_profile"]["ledge_top_z_mm"]+=.1
        with self.assertRaisesRegex(ValueError,"vertical_gap"):
            checks.validate_assembly(self.body,lid)


if __name__=="__main__":
    unittest.main()
