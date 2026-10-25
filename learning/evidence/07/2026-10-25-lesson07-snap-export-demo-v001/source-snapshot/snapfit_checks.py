"""Read-only 07-02 trial cantilever/catch geometry, in world millimetres.

No modelling operators or material/strength calculations are performed. A fitted
fillet radius describes the circle through the real three-segment chord ends;
the mesh itself remains faceted. Numeric epsilons are not print tolerances.
"""
import math

from lid_checks import _bounds, _check_planes, _cross, _dot, _sub
from tenon_checks import _mesh, _public, _rays, _rectangular_planes, read_mesh_data


EPS_MM = 1e-4
REL_EPS = 1e-5
# Integral of (z + 8) * outward_normal_z over the six analytical chord
# trapezoids and twelve end-cap triangles; the root's base is at z = -8.
# Inset shoulder miters add material beyond a constant-width extrusion.
NATIVE_ROOT_VOLUME_MM3 = 1.2047076581449612
SNAP_VOLUME_MM3 = 124.2 + 201.6 + 12.48 + NATIVE_ROOT_VOLUME_MM3


def _require(condition, message):
    if not condition:
        raise ValueError("07-02 snapfit geometry: " + message)


def _close(a, b):
    return math.isclose(a, b, rel_tol=0, abs_tol=EPS_MM)


def _near(a, b, message):
    _require(math.isclose(a, b, rel_tol=REL_EPS, abs_tol=EPS_MM), message)


def _result(mesh, kind):
    result = _public(mesh)
    result.update(kind=kind, material_grade=None, epsilon_allow=None,
                  root_flexibility_Q=None, required_deflection_mm=None,
                  delta_allow_mm=None, insertion_force_N=None, retention_force_N=None,
                  qualified_strength_N=None, strength_assessment=None, fit_assessment=None,
                  strength_analysis_performed=False, deformation_analysis_performed=False,
                  exported_stl=False, slicer_checked=False)
    return result


def _arc(side):
    centre = (-23.6, -7.4) if side == "outer" else (-20.8, -7.4)
    sign = 1 if side == "outer" else -1
    return [(centre[0] + sign * .6 * math.sin(i * math.pi / 6),
             centre[1] - .6 * math.cos(i * math.pi / 6)) for i in range(4)]


def _circle(points):
    a, b, c = points[0], points[1], points[-1]
    d = 2 * (a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1]))
    _require(abs(d) > 1e-10, "fillet chord endpoints are collinear")
    sq = lambda p: p[0]*p[0] + p[1]*p[1]
    cy = (sq(a)*(b[1]-c[1]) + sq(b)*(c[1]-a[1]) + sq(c)*(a[1]-b[1])) / d
    cz = (sq(a)*(c[0]-b[0]) + sq(b)*(a[0]-c[0]) + sq(c)*(b[0]-a[0])) / d
    radius = math.hypot(a[0]-cy, a[1]-cz)
    _require(all(_close(math.hypot(y-cy, z-cz), radius) for y, z in points),
             "actual fillet chord endpoints do not share one circle")
    return [cy, cz], radius


def _facet_reference():
    """Analytical boundary planes for Native Bevel's precise end miters.

    The inset shoulder diagonal extends a root chord's half-width by its
    horizontal distance from the straight arm. This is a validation reference,
    never a model exported to Blender. Twelve triangular cap planes close the
    four ends; they are not arbitrary sloped faces or a convex hull allowance.
    """
    facets = []
    for side in ("outer", "inner"):
        arc = _arc(side)
        beam = -23 if side == "outer" else -21.4
        for i, (a, b) in enumerate(zip(arc, arc[1:])):
            sa, sb = abs(a[0]-beam), abs(b[0]-beam)
            corners = [(-3-sa, *a), (3+sa, *a), (3+sb, *b), (-3-sb, *b)]
            facets.append((side, i, corners))
            for end in (-1, 1):
                apex = (end*3, beam + (.6 if side == "outer" else -.6), -8)
                cap = [(end*(3+sa), *a), (end*(3+sb), *b), apex]
                facets.append((side+"_miter_"+str(end), i, cap))
    facets.append(("entry_ramp", 0, [(-3,-23.4,13),(3,-23.4,13),
                                     (3,-24.2,12.2),(-3,-24.2,12.2)]))
    result = []
    for feature, ordinal, corners in facets:
        normal = _cross(_sub(corners[1],corners[0]),_sub(corners[2],corners[0]))
        if normal[2] < 0:
            corners.reverse()
            normal = tuple(-n for n in normal)
        magnitude = math.sqrt(_dot(normal,normal))
        normal = tuple(n/magnitude for n in normal)
        area = sum(math.sqrt(_dot(cross,cross))/2 for cross in
                   [_cross(_sub(corners[i],corners[0]),_sub(corners[i+1],corners[0]))
                    for i in range(1,len(corners)-1)])
        result.append((feature,ordinal,corners,normal,area))
    return result


def _in_facet(point,corners,normal):
    # Every point must be on the given finite convex reference facet, including
    # Boolean-created collinear split points; no tolerance change or hull fill.
    for a,b in zip(corners,corners[1:]+corners[:1]):
        edge=_sub(b,a)
        cross=_cross(edge,_sub(point,a))
        if _dot(cross,normal)<-EPS_MM*math.sqrt(_dot(edge,edge)):
            return False
    return True


def _sloped_profile(mesh):
    """Read six varying-width chords, twelve exact miter caps, and one ramp."""
    specifications = _facet_reference()
    groups = [[] for _ in specifications]
    excluded = set()
    for i, normal in enumerate(mesh["normals"]):
        if max(abs(n) for n in normal) >= 1 - 1e-6:
            continue
        matches = []
        for j, (_, _, corners, expected_normal, _) in enumerate(specifications):
            if _dot(normal,expected_normal) < 1-1e-6:
                continue
            if all(abs(_dot(expected_normal,_sub(p,corners[0]))) <= EPS_MM and
                   _in_facet(p,corners,expected_normal) for p in mesh["points"][i]):
                matches.append(j)
        _require(len(matches) == 1, "unexpected sloped face or wrong fillet/ramp orientation")
        groups[matches[0]].append(i)
        excluded.add(i)
    measured, miters = [], []
    corner_map = {}
    for (side, ordinal, corners, normal, expected_area), faces in zip(specifications, groups):
        _require(faces, "missing actual %s profile facet" % side)
        samples = [p for i in faces for p in mesh["points"][i]]
        bounds = _bounds(samples)
        actual_corners=[]
        for endpoint in corners:
            p = min(samples,key=lambda q:math.sqrt(_dot(_sub(q,endpoint),_sub(q,endpoint))))
            _require(math.sqrt(_dot(_sub(p,endpoint),_sub(p,endpoint)))<=EPS_MM,
                     "native facet corner missing or incorrectly positioned")
            actual_corners.append(list(p))
        area = math.fsum(mesh["areas"][i] for i in faces)
        _near(area,expected_area,"native fillet/miter/ramp actual area mismatch")
        entry={"feature":side,"segment":ordinal,"corners_mm":actual_corners,
               "bounds_mm":bounds,"area_mm2":area,"triangle_count":len(faces),
               "normal":list(mesh["normals"][faces[0]])}
        if "_miter_" in side:
            miters.append(entry)
        else:
            actual_ends=[]
            refs=_arc(side)[ordinal:ordinal+2] if side in ("outer","inner") else [(-23.4,13),(-24.2,12.2)]
            for endpoint in refs:
                p=min(samples,key=lambda q:math.hypot(q[1]-endpoint[0],q[2]-endpoint[1]))
                value=[p[1],p[2]]
                actual_ends.append(value)
                corner_map[side,endpoint]=value
            entry["endpoints_yz_mm"]=actual_ends
            measured.append(entry)
    fillets = []
    for side in ("outer", "inner"):
        points = [corner_map[side, p] for p in _arc(side)]
        centre, radius = _circle(points)
        _near(radius, .6, "measured root fillet circle radius differs from draft")
        fillets.append({"side": side, "segments": 3, "chord_endpoints_yz_mm": points,
                        "fitted_circle_centre_yz_mm": centre,
                        "fitted_circle_radius_mm": radius,
                        "radius_definition": "circle through actual chord endpoints; the mesh is faceted",
                        "input_bevel_offset_mm": .6})
    ramp = measured[-1]["endpoints_yz_mm"]
    angle = math.degrees(math.atan2(abs(ramp[1][0]-ramp[0][0]), abs(ramp[1][1]-ramp[0][1])))
    _near(angle, 45, "entry angle differs from 45 degrees to the Z insertion axis")
    return {"fillets": fillets, "entry_angle_deg": angle, "entry_ramp_endpoints_yz_mm": ramp,
            "facets": measured, "native_end_miters":miters,
            "native_miter_count":len(miters),
            "native_root_volume_mm3":NATIVE_ROOT_VOLUME_MM3}, excluded


def _axes(mesh, expected, excluded=()):
    axes = _rectangular_planes(mesh, set(excluded))
    _check_planes(axes, expected)
    return {a: values for a, values in zip("XYZ", axes)}


def _coordinate(axes, axis, target):
    return next(p["coordinate_mm"] for p in axes[axis] if _close(p["coordinate_mm"], target))


def _snap_readback(mesh, axes, profiles):
    y = lambda target: _coordinate(axes, "Y", target)
    z = lambda target: _coordinate(axes, "Z", target)
    return {"beam_x_mm": [-3, 3], "beam_outer_y_mm": y(-23), "beam_inner_y_mm": y(-21.4),
            "beam_thickness_mm": y(-21.4)-y(-23), "beam_width_mm": 6,
            "root_plane_z_mm": z(-8), "bearing_z_mm": z(11), "arm_top_z_mm": z(13),
            "root_to_bearing_geometric_length_mm": z(11)-z(-8),
            "full_arm_geometric_height_mm": z(13)-z(-8),
            "hook_outer_y_mm": y(-24.2), "hook_projection_mm": y(-23)-y(-24.2),
            "return_angle_deg": 90, "root_fillets": profiles["fillets"],
            "entry_angle_deg": profiles["entry_angle_deg"],
            "entry_ramp_endpoints_yz_mm": profiles["entry_ramp_endpoints_yz_mm"],
            "effective_mechanical_length_confirmed": False}


def validate_tool_mesh(vertices, triangles, kind):
    aliases = {"snap": "snap", "snaptool": "snap", "SnapTool": "snap",
               "flange": "flange", "lid_flange": "flange", "LidFlangeTool": "flange"}
    _require(kind in aliases, "unknown construction tool kind")
    kind = aliases[kind]
    mesh = _mesh(vertices, triangles, 0)
    profiles, excluded = _sloped_profile(mesh) if kind == "snap" else ({}, set())
    if kind == "snap":
        expected = [[(-4.5, 13.8), (-3, 35.32), (3, 35.32), (4.5, 13.8)],
                    [(-24.5, 27), (-24.2, 7.2), (-23, 110.4), (-21.4, 122.4), (-19.9, 27)],
                    [(-11, 41.4), (-8, 23.16), (11, 7.2), (13, 12)]]
        volume = SNAP_VOLUME_MM3
        probes = [("anchor outer shoulder", 0, -24.4, [-11, -8]),
                  ("straight beam", 0, -22, [-11, 13]),
                  ("hook ledge", 0, -24, [-11, -8, 11, 12.4])]
    else:
        expected = [[(-5, 8.52), (5, 8.52)],
                    [(-26, 52), (-24.5, 46), (-23.3, 6)],
                    [(10.2, 27), (10.8, 12), (15.4, 15)]]
        volume = 85.2
        probes = [("skirt", 0, -25, [10.2, 15.4]), ("ledge", 0, -24, [10.2, 10.8])]
    axes = _axes(mesh, expected, excluded)
    _near(mesh["volume_mm3"], volume, "construction tool volume mismatch")
    result = _result(mesh, "snapfit_construction_tool")
    result.update(tool_kind=kind, actual_axis_planes=axes, profiles=profiles,
                  vertical_rays=_rays(mesh, probes))
    if kind == "snap":
        result["snap_profile"] = _snap_readback(mesh, axes, profiles)
    return result


def validate_body_mesh(vertices, triangles, source_body=None):
    mesh = _mesh(vertices, triangles, 0)
    profiles, excluded = _sloped_profile(mesh)
    axes = _axes(mesh, [
        [(-30, 1200), (-28, 1008), (-4.5, 13.5), (-3, 35.32), (3, 35.32), (4.5, 13.5), (28, 1008), (30, 1200)],
        [(-24.5, 27), (-24.2, 7.2), (-23, 110.4), (-21.4, 122.4), (-20, 1773), (-18, 1568), (18, 1568), (20, 1800)],
        [(-15, 2400), (-13, 2016), (-11, 40.5), (-8, 22.26), (11, 7.2), (13, 12), (15, 384)]
    ], excluded)
    _near(mesh["volume_mm3"],15552+SNAP_VOLUME_MM3-2.7,"body plus integrated snap volume mismatch")
    if source_body is not None:
        _require(isinstance(source_body, dict) and source_body.get("passed") is True and
                 source_body.get("kind") == "box_body", "source body must be an actual validated original box")
        _near(source_body["volume_mm3"], 15552, "source body volume mismatch")
        _require(all(_close(a,b) for a,b in zip(source_body["outer_dimensions_mm"], [60,40,30])) and
                 all(_close(a,b) for a,b in zip(source_body["cavity_dimensions_mm"], [56,36,28])),
                 "source box reference dimensions mismatch")
    probes = [("original cavity centre", 0, 0, [-15,-13]),
              ("original front rim away from snap", 10,-19,[-15,15]),
              ("original back rim", 0,19,[-15,15]),
              ("anchor outside original box", 0,-24.4,[-11,-8]),
              ("straight beam", 0,-22,[-11,13]),
              ("hook and anchor", 0,-24,[-11,-8,11,12.4]),
              ("air behind arm", 0,-20.5,[-11,-8])]
    result = _result(mesh, "snapfit_body")
    result.update(actual_axis_planes=axes, profiles=profiles, vertical_rays=_rays(mesh, probes),
                  snap_profile=_snap_readback(mesh, axes, profiles),
                  original_core_outer_mm=[60,40,30], cavity_dimensions_mm=[56,36,28],
                  wall_and_floor_mm=2, original_rim_z_mm=_coordinate(axes,"Z",15),
                  original_front_wall_y_mm=_coordinate(axes,"Y",-20),
                  source_body_metadata_compared=source_body is not None,
                  source_core_preserved=True, whole_body_geometry_unchanged=False,
                  measurement_scope="original box surfaces and integrated exterior snap; static geometry only")
    return result


def validate_lid_mesh(vertices, triangles):
    mesh = _mesh(vertices, triangles, 0)
    axes = _axes(mesh, [[(-30,92),(-5,8.22),(5,8.22),(30,92)],
                        [(-26,170),(-24.5,44),(-23.3,6),(20,120)],
                        [(10.2,27),(10.8,12),(15.2,2745),(17.2,2760)]])
    _near(mesh["volume_mm3"],5602.2,"integrated lid/ledge volume mismatch")
    y = lambda target: _coordinate(axes,"Y",target)
    z = lambda target: _coordinate(axes,"Z",target)
    profile = {"skirt_inner_y_mm":y(-24.5),"ledge_inner_y_mm":y(-23.3),
               "skirt_outer_y_mm":y(-26),"ledge_bottom_z_mm":z(10.2),
               "ledge_top_z_mm":z(10.8),"ledge_thickness_mm":z(10.8)-z(10.2),
               "ledge_projection_mm":y(-23.3)-y(-24.5),"flange_width_mm":10}
    result = _result(mesh,"snapfit_lid")
    result.update(actual_axis_planes=axes,mating_profile=profile,
                  plate_z_mm=[z(15.2),z(17.2)],plate_thickness_mm=z(17.2)-z(15.2),
                  plate_dimensions_mm=[60,46,z(17.2)-z(15.2)],profiles={"mating":profile},
                  vertical_rays=_rays(mesh,[("plate centre",0,0,[15.2,17.2]),
                     ("integrated skirt",0,-25,[10.2,17.2]),
                     ("ledge under plate",0,-24,[10.2,10.8,15.2,17.2]),
                     ("plate beside narrow flange",10,-25,[15.2,17.2])]))
    return result


def validate_assembly(body,lid):
    _require(body.get("passed") is True and body.get("kind")=="snapfit_body" and
             lid.get("passed") is True and lid.get("kind")=="snapfit_lid",
             "assembly requires measured 07-02 body and lid")
    s,p=body["snap_profile"],lid["mating_profile"]
    straight=body["original_front_wall_y_mm"]-s["beam_inner_y_mm"]
    root_inner=max(point[0] for f in s["root_fillets"] if f["side"]=="inner"
                   for point in f["chord_endpoints_yz_mm"])
    values={"plate_rim_gap_mm":lid["plate_z_mm"][0]-body["original_rim_z_mm"],
            "beam_ledge_gap_mm":s["beam_outer_y_mm"]-p["ledge_inner_y_mm"],
            "hook_skirt_gap_mm":s["hook_outer_y_mm"]-p["skirt_inner_y_mm"],
            "hook_ledge_projection_overlap_mm":p["ledge_inner_y_mm"]-s["hook_outer_y_mm"],
            "hook_ledge_vertical_gap_mm":s["bearing_z_mm"]-p["ledge_top_z_mm"],
            "straight_beam_inward_static_space_mm":straight,
            "inner_root_fillet_local_static_gap_mm":body["original_front_wall_y_mm"]-root_inner}
    for key,expected in zip(values,(.2,.3,.3,.9,.2,1.4,.8)):
        _near(values[key],expected,"actual assembly %s mismatch"%key)
    values.update(passed=True,kind="snapfit_static_assembly",geometric_nonintersection=True,
                  scope="undeformed nominal placement only; no contact/deformation/insertion path solved",
                  required_deflection_mm=None,delta_allow_mm=None,root_flexibility_Q=None,
                  material_grade=None,epsilon_allow=None,insertion_force_N=None,retention_force_N=None,
                  strength_analysis_performed=False,deformation_analysis_performed=False,
                  printed=False,fit_tested=False,physical_measurements=None,fit_results=None,
                  physical_interference=None,qualified_strength_N=None,qualified_clearance_mm=None,
                  trial_status="experimental_geometry_only",
                  numericComparison={"purpose":"Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                     "dimensionsAbsMm":EPS_MM,"volumeRelative":REL_EPS})
    return values
