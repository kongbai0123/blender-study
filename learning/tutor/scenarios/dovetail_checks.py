"""Read-only 06-02 constant-section dovetail slide measurements.

Coordinates are world-space millimetres. Trial horizontal and normal gaps are
reported separately. Numeric epsilons do not qualify a manufactured fit. The
original upper side walls are locally modified; the original source *file* is
preserved separately by the runner. No Blender modelling operator is used here.
"""
from collections import defaultdict
import hashlib
import json
import math

from lid_checks import _bounds, _check_planes, _components
from tenon_checks import (_mesh, _public, _rays, _rectangular_planes,
                         read_mesh_data)


EPS_MM = 1e-4
REL_EPS = 1e-5
SLOPE = 0.2
CENTRES_Y = (-17.0, 17.0)


def _require(condition, message):
    if not condition:
        raise ValueError("06-02 dovetail validation: " + message)


def _close(a, b):
    return math.isclose(a, b, rel_tol=0, abs_tol=EPS_MM)


def _near(actual, expected, message):
    _require(math.isclose(actual, expected, rel_tol=REL_EPS, abs_tol=EPS_MM), message)


def _signature(mesh):
    faces = []
    for triangle in mesh["triangles"]:
        points = [tuple(round(c / EPS_MM) for c in mesh["vertices"][i]) for i in triangle]
        faces.append(min(tuple(points[i:] + points[:i]) for i in range(3)))
    encoded = json.dumps(sorted(faces), separators=(",", ":")).encode("ascii")
    return {"algorithm": "SHA-256 of sorted oriented triangle coordinates on numeric comparison grid",
            "coordinate_grid_mm": EPS_MM, "sha256": hashlib.sha256(encoded).hexdigest()}


def _result(mesh, kind):
    result = _public(mesh)
    result.update(kind=kind, geometry_signature=_signature(mesh), exported_stl=False,
                  slicer_checked=False, overhang_analysis_performed=False)
    return result


def _pair_mesh(vertices, triangles):
    """Measure two independent construction tools, not one disconnected part."""
    triangles = [tuple(t) for t in triangles]
    _require(triangles, "empty paired tool")
    adjacency, edges = [set() for _ in triangles], defaultdict(list)
    for i, triangle in enumerate(triangles):
        _require(len(triangle) == 3 and all(isinstance(v, int) and 0 <= v < len(vertices) for v in triangle), "invalid tool triangle")
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[min(a, b), max(a, b)].append(i)
    for linked in edges.values():
        for i in linked:
            adjacency[i].update(j for j in linked if i != j)
    components = _components(range(len(triangles)), adjacency)
    _require(len(components) == 2, "construction tool must contain exactly two separate closed shells")
    parts = []
    for component in components:
        used = sorted({v for i in component for v in triangles[i]})
        mapping = {old: new for new, old in enumerate(used)}
        parts.append(_mesh([vertices[i] for i in used],
                           [tuple(mapping[v] for v in triangles[i]) for i in component], 0))
    _require(len({v for t in triangles for v in t}) == len(vertices), "unused tool vertices")
    # Reuse original indices for the actual-face plane evidence and signature.
    points = [tuple(tuple(float(c) for c in vertices[i]) for i in t) for t in triangles]
    normals, areas = [], []
    for pts in points:
        a = [pts[1][i] - pts[0][i] for i in range(3)]
        b = [pts[2][i] - pts[0][i] for i in range(3)]
        cross = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        length = math.sqrt(sum(c*c for c in cross))
        normals.append(tuple(c / length for c in cross))
        areas.append(length / 2)
    bounds = _bounds(vertices)
    return {"vertices": [tuple(v) for v in vertices], "triangles": triangles, "points": points,
            "normals": normals, "areas": areas, "bounds_mm": bounds,
            "dimensions_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)],
            "volume_mm3": sum(part["volume_mm3"] for part in parts),
            "non_manifold_edges": 0, "non_manifold_vertex_links": 0, "inconsistent_winding_edges": 0,
            "connected_shells": 2, "euler_characteristic": 4, "genus": 0,
            "mesh_counts": {"vertices": len(vertices), "edges": len(edges), "faces": len(triangles),
                            "triangles": len(triangles), "representation": "paired world-space triangulated tools"}}


def _profiles(mesh, intercept_half_width, z_min, z_max, x_min, x_max, cavity):
    """Measure four actual sloped planes y + slope_z*z = offset_mm."""
    expected = []
    for centre in CENTRES_Y:
        expected.extend(((centre, "negative_y", -SLOPE, centre - intercept_half_width),
                         (centre, "positive_y", SLOPE, centre + intercept_half_width)))
    groups = [[] for _ in expected]
    excluded = set()
    for i, normal in enumerate(mesh["normals"]):
        if max(abs(v) for v in normal) >= 1 - 1e-6:
            continue
        _require(abs(normal[0]) <= 1e-6 and abs(normal[1]) > 0.9, "unexpected non-axis face")
        slope = normal[2] / normal[1]
        offset = sum(p[1] + slope * p[2] for p in mesh["points"][i]) / 3
        matches = [j for j, (_, _, s, c) in enumerate(expected) if abs(slope - s) <= 1e-5 and _close(offset, c)]
        _require(len(matches) == 1, "actual sloped wall differs from dovetail profile")
        _require(all(_close(p[1] + slope * p[2], offset) for p in mesh["points"][i]), "nonplanar dovetail wall")
        side = expected[matches[0]][1]
        positive_normal = (side == "negative_y") if cavity else (side == "positive_y")
        _require((normal[1] > 0) == positive_normal, "dovetail wall has incorrect orientation")
        groups[matches[0]].append(i)
        excluded.add(i)
    profiles = []
    for n, centre in enumerate(CENTRES_Y):
        planes = []
        for j in (2*n, 2*n+1):
            faces = groups[j]
            _require(faces, "missing sloped wall")
            bounds = _bounds([p for i in faces for p in mesh["points"][i]])
            _require(_close(bounds["min"][0], x_min) and _close(bounds["max"][0], x_max) and
                     _close(bounds["min"][2], z_min) and _close(bounds["max"][2], z_max),
                     "sloped wall does not span the full longitudinal/profile range")
            area = sum(mesh["areas"][i] for i in faces)
            _near(area, (x_max-x_min)*(z_max-z_min)*math.sqrt(1+SLOPE*SLOPE), "sloped wall area mismatch")
            slopes = [mesh["normals"][i][2] / mesh["normals"][i][1] for i in faces]
            slope = sum(slopes) / len(slopes)
            coordinates = [p[1] + slope*p[2] for i in faces for p in mesh["points"][i]]
            offset = sum(coordinates) / len(coordinates)
            planes.append({"side": expected[j][1], "slope_z": slope, "offset_mm": offset,
                           "equation": "y + slope_z*z = offset_mm", "bounds_mm": bounds,
                           "area_mm2": area, "triangle_count": len(faces)})
        actual_z = [min(p["bounds_mm"]["min"][2] for p in planes), max(p["bounds_mm"]["max"][2] for p in planes)]
        widths = [(planes[1]["offset_mm"] - planes[1]["slope_z"]*z) -
                  (planes[0]["offset_mm"] - planes[0]["slope_z"]*z) for z in actual_z]
        profiles.append({"centre_y_mm": centre, "x_mm": [x_min, x_max],
                         "profile": {"z_mm": actual_z, "widths_mm": widths,
                                     "side_slope_abs": sum(abs(p["slope_z"]) for p in planes)/2,
                                     "side_planes": planes}})
    return profiles, excluded


def validate_tool_mesh(vertices, triangles, kind):
    aliases = {"guide": "guide", "guides": "guide", "groove": "groove", "grooves": "groove", "male": "male", "males": "male"}
    _require(kind in aliases, "unknown tool kind")
    kind = aliases[kind]
    mesh = _pair_mesh(vertices, triangles)
    if kind == "guide":
        profiles, excluded = [], set()
        expected = [[(-30, 60), (30, 60)], [(-20, 300), (-14, 300), (14, 300), (20, 300)], [(10, 720), (15, 720)]]
        volume = 3600
    elif kind == "groove":
        profiles, excluded = _profiles(mesh, 4.16, 11.8, 15.8, -31, 31, False)
        expected = [[(-31, 22.4), (31, 22.4)], [], [(11.8, 446.4), (15.8, 248)]]
        volume = 1388.8
    else:
        profiles, excluded = _profiles(mesh, 3.96, 12, 15.4, -30, 30, False)
        expected = [[(-30, 16.592), (30, 16.592)], [], [(12, 374.4), (15.4, 211.2)]]
        volume = 995.52
    axes = _rectangular_planes(mesh, excluded)
    _check_planes(axes, expected)
    _near(mesh["volume_mm3"], volume, "paired tool volume mismatch")
    result = _result(mesh, "paired_dovetail_tool")
    result.update(tool_kind=kind, profiles=profiles,
                  actual_axis_planes={axis: values for axis, values in zip("XYZ", axes)},
                  measurement_scope="full paired construction tools; clipped final geometry is measured separately")
    return result


def validate_body_mesh(vertices, triangles):
    mesh = _mesh(vertices, triangles, 0)
    channels, excluded = _profiles(mesh, 4.16, 11.8, 15, -30, 30, True)
    axes = _rectangular_planes(mesh, excluded)
    _check_planes(axes, [[(-30, 1181.056), (-28, 968), (28, 968), (30, 1181.056)],
                         [(-20, 1800), (-18, 1288), (-14, 280), (14, 280), (18, 1288), (20, 1800)],
                         [(-15, 2400), (-13, 2016), (10, 448), (11.8, 432), (15, 553.6)]])
    _near(mesh["volume_mm3"], 16655.36, "guide/channel body volume mismatch")
    probes = [("original cavity floor", 0, 0, [-15, -13]),
              ("guide underside and top", 0, 14.5, [-15, -13, 10, 15])]
    for x in (-29, 0, 29):
        for y in CENTRES_Y:
            expected = [-15, 11.8] if abs(x) > 28 else [-15, -13, 10, 11.8]
            probes.append(("open channel floor x%g y%g" % (x, y), x, y, expected))
    rays = _rays(mesh, probes)
    for channel in channels:
        channel["open_ends"] = True
    result = _result(mesh, "dovetail_body")
    result.update(channels=channels, original_shell_dimensions_mm=[60, 40, 30],
                  original_lower_cavity_dimensions_mm=[56, 36, 28], local_cavity_width_mm=28.0,
                  min_guide_ligament_mm=(6.0-max(c["profile"]["widths_mm"][0] for c in channels))/2,
                  channel_floor_web_mm=min(c["profile"]["z_mm"][0] for c in channels)-axes[2][2]["coordinate_mm"],
                  rim_z_mm=axes[2][-1]["coordinate_mm"],
                  actual_axis_planes={axis: values for axis, values in zip("XYZ", axes)}, vertical_rays=rays,
                  full_length_entry_proof={"both_end_faces_have_channel_cutouts": True,
                                           "end_face_area_mm2": [g["area_mm2"] for g in axes[0]
                                                                 if abs(g["coordinate_mm"]) > 29],
                                           "sloped_walls_and_floors_span_x_mm": [-30, 30]},
                  source_shell_preservation="outer envelope, floor and lower walls retained; upper side walls locally modified")
    return result


def validate_lid_mesh(vertices, triangles):
    mesh = _mesh(vertices, triangles, 0)
    males, excluded = _profiles(mesh, 3.96, 12, 15.2, -30, 30, False)
    axes = _rectangular_planes(mesh, excluded)
    _check_planes(axes, [[(-30, 95.872), (30, 95.872)], [(-20, 120), (20, 120)],
                         [(12, 374.4), (15.2, 2179.2), (17.2, 2400)]])
    _near(mesh["volume_mm3"], 5752.32, "plate/male union volume mismatch")
    rays = _rays(mesh, [("plate centre", 0, 0, [15.2, 17.2]),
                        ("negative male centre", 0, -17, [12, 17.2]),
                        ("positive male centre", 0, 17, [12, 17.2]),
                        ("outside male", 0, 19, [15.2, 17.2])])
    result = _result(mesh, "dovetail_lid")
    result.update(male_ribs=males, plate_dimensions_mm=[60, 40, axes[2][2]["coordinate_mm"]-axes[2][1]["coordinate_mm"]],
                  plate_z_mm=[axes[2][1]["coordinate_mm"], axes[2][2]["coordinate_mm"]],
                  exposed_male_depth_mm=axes[2][1]["coordinate_mm"]-axes[2][0]["coordinate_mm"],
                  actual_axis_planes={axis: values for axis, values in zip("XYZ", axes)}, vertical_rays=rays,
                  measurement_scope="final integrated plate and exposed male profiles; buried tool top is not inferred")
    return result


def validate_assembly(body, lid):
    _require(body.get("passed") is True and body.get("kind") == "dovetail_body" and
             lid.get("passed") is True and lid.get("kind") == "dovetail_lid", "successful body/lid measurements required")
    clearances, floor_gaps = [], []
    for channel, male in zip(body["channels"], lid["male_ribs"]):
        _require(_close(channel["centre_y_mm"], male["centre_y_mm"]), "guide and male centres differ")
        cp, mp = channel["profile"], male["profile"]
        overlap = [max(cp["z_mm"][0], mp["z_mm"][0]), min(cp["z_mm"][1], mp["z_mm"][1])]
        _require(overlap[1] > overlap[0], "no vertical dovetail engagement")
        for side, (c, m) in enumerate(zip(cp["side_planes"], mp["side_planes"])):
            _require(abs(c["slope_z"]-m["slope_z"]) <= 1e-5, "profile slopes are not parallel")
            distances = []
            for z in overlap:
                yc, ym = c["offset_mm"]-c["slope_z"]*z, m["offset_mm"]-m["slope_z"]*z
                horizontal = ym-yc if side == 0 else yc-ym
                normal = horizontal/math.sqrt(1+c["slope_z"]**2)
                _require(_close(horizontal, .2) and _close(normal, .2/math.sqrt(1.04)), "actual side clearance differs from trial")
                distances.append({"z_mm": z, "horizontal_gap_mm": horizontal, "normal_gap_mm": normal})
            clearances.append({"centre_y_mm": channel["centre_y_mm"], "side": c["side"],
                               "z_overlap_mm": overlap, "endpoints": distances,
                               "horizontal_gap_mm": min(d["horizontal_gap_mm"] for d in distances),
                               "normal_gap_mm": min(d["normal_gap_mm"] for d in distances)})
        floor_gaps.append(mp["z_mm"][0]-cp["z_mm"][0])
    plate_gap = lid["plate_z_mm"][0]-body["rim_z_mm"]
    _require(all(_close(gap, .2) for gap in floor_gaps) and _close(plate_gap, .2), "vertical floor or plate clearance mismatch")
    horizontal = [c["horizontal_gap_mm"] for c in clearances]
    normal = [c["normal_gap_mm"] for c in clearances]
    result = {"passed": True, "kind": "dovetail_assembly", "side_clearances": clearances,
              "horizontal_side_gap_mm": min(horizontal), "normal_side_gap_mm": min(normal),
              "horizontal_side_gaps_mm": horizontal, "normal_side_gaps_mm": normal,
              "nominal_horizontal_side_trial_mm": .2, "nominal_horizontal_total_trial_mm": .4,
              "bottom_gaps_mm": floor_gaps, "bottom_gap_mm": min(floor_gaps),
              "plate_rim_gap_mm": plate_gap, "retained_vertical_overlap_mm": 3.0,
              "geometric_nonintersection": True, "entry_open_both_ends": True,
              "profile_invariant_along_x": True, "printed": False, "fit_tested": False,
              "physical_measurements": None, "fit_results": None, "physical_interference": None,
              "qualified_clearance_mm": None, "trial_status": "experimental_geometry_only",
              "overhang_analysis_performed": False,
              "numericComparison": {"purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                    "dimensionsAbsMm": EPS_MM, "volumeRelative": REL_EPS}}
    return result


def validate_travel(body, lid, travel_raw):
    assembly = validate_assembly(body, lid)
    _require(isinstance(travel_raw, dict) and set(travel_raw) == {"30", "62"}, "expected actual +30 and +62 mm travel dumps")
    states = [{"translation_x_mm": 0.0, "x_bounds_mm": lid["bounds_mm"]["min"][:1]+lid["bounds_mm"]["max"][:1],
               "overlap_length_mm": 60.0, "fully_disengaged": False, "end_gap_mm": 0.0,
               "geometric_nonintersection": True, "same_mesh_after_normalising_translation": True}]
    for name in ("30", "62"):
        raw, translation = travel_raw[name], float(name)
        _require(isinstance(raw, dict) and "vertices" in raw and "triangles" in raw, "missing travel mesh")
        bounds = _bounds(raw["vertices"])
        actual = (bounds["min"][0]+bounds["max"][0])/2
        _require(_close(actual, translation), "actual longitudinal translation differs from requested travel")
        normalised = [(p[0]-actual, p[1], p[2]) for p in raw["vertices"]]
        measured = validate_lid_mesh(normalised, raw["triangles"])
        _require(measured["geometry_signature"] == lid["geometry_signature"], "travel dump is not the same translated lid mesh")
        overlap = max(0.0, min(bounds["max"][0], body["bounds_mm"]["max"][0])-
                      max(bounds["min"][0], body["bounds_mm"]["min"][0]))
        gap = max(0.0, bounds["min"][0]-body["bounds_mm"]["max"][0])
        states.append({"translation_x_mm": actual, "x_bounds_mm": [bounds["min"][0], bounds["max"][0]],
                       "overlap_length_mm": overlap, "fully_disengaged": overlap == 0,
                       "end_gap_mm": gap, "geometric_nonintersection": True,
                       "same_mesh_after_normalising_translation": True})
    _require(_close(states[1]["overlap_length_mm"], 30) and states[2]["fully_disengaged"] and
             _close(states[2]["end_gap_mm"], 2), "unexpected partial/full disengagement state")
    return {"passed": True, "kind": "dovetail_travel", "states": states,
            "sweep_interval_x_mm": [0, 62], "continuous_sweep_geometric_nonintersection": True,
            "proof": "full-length constant profiles, cut end openings, positive transverse gaps, and identical rigidly translated lid meshes",
            "reference_cross_section_clearances": assembly,
            "printed": False, "fit_tested": False, "physical_measurements": None,
            "fit_results": None, "physical_interference": None, "qualified_clearance_mm": None,
            "trial_status": "experimental_geometry_only", "overhang_analysis_performed": False}
