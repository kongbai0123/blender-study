"""07-05 read-only single-parameter cantilever coupon geometry checks.

World coordinates are millimetres. L is the root-plane-to-bearing geometric
distance, never an effective mechanical length. The continuous inverse map
preserves valid subdivision of the stretched straight arm. It performs no
modelling, strength, contact, support or print qualification.
"""
import math

from lid_checks import _dot, _sub
from tenon_checks import _mesh, _public
from snapfit_checks import validate_tool_mesh
from snapfit_stl_checks import _surface_match


EPS_MM = 1e-4
REL_EPS = 1e-5
SOURCE_ORIGIN = [0., -22.200000762939453, -9.5]
ROTATION = [[0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]]
SPECS = {
    "A_L19": {"name": "A_L19", "L_geometry_mm": 19., "upper_vertex_translation_z_mm": 0.,
              "bearing_plane_z_mm": 11., "total_arm_height_mm": 21., "whole_coupon_height_mm": 24.,
              "candidate_rotation_degrees": [0, 90, 0], "candidate_object_location_mm": [0, -12, 4.5],
              "candidate_world_dimensions_nominal_mm": [24, 4.6, 9]},
    "B_L17": {"name": "B_L17", "L_geometry_mm": 17., "upper_vertex_translation_z_mm": -2.,
              "bearing_plane_z_mm": 9., "total_arm_height_mm": 19., "whole_coupon_height_mm": 22.,
              "candidate_rotation_degrees": [0, 90, 0], "candidate_object_location_mm": [0, 0, 4.5],
              "candidate_world_dimensions_nominal_mm": [22, 4.6, 9]},
    "C_L21": {"name": "C_L21", "L_geometry_mm": 21., "upper_vertex_translation_z_mm": 2.,
              "bearing_plane_z_mm": 13., "total_arm_height_mm": 23., "whole_coupon_height_mm": 26.,
              "candidate_rotation_degrees": [0, 90, 0], "candidate_object_location_mm": [0, 12, 4.5],
              "candidate_world_dimensions_nominal_mm": [26, 4.6, 9]},
}


def _require(condition, message):
    if not condition:
        raise ValueError("07-05 coupon geometry: " + message)


def _near(a, b, label, relative=False):
    _require(math.isfinite(float(a)) and math.isfinite(float(b)) and
             math.isclose(a, b, rel_tol=REL_EPS if relative else 0., abs_tol=EPS_MM),
             label + " differs from the frozen geometric draft")


def _vector(actual, expected, label):
    _require(isinstance(actual, (list, tuple)) and len(actual) == len(expected), label + " missing")
    for a, b in zip(actual, expected):
        _near(a, b, label)


def _spec(variant, plan):
    name = variant if isinstance(variant, str) else variant.get("name")
    _require(name in SPECS, "unknown coupon variant")
    spec = SPECS[name]
    supplied = variant if isinstance(variant, dict) else None
    if plan is not None:
        _vector(plan.get("source_object_origin_mm"), SOURCE_ORIGIN, "source object origin")
        _require(plan.get("lesson_step") == "07-05", "wrong lesson plan")
        entries = [item for item in plan.get("coupon_objects", []) if item.get("name") == name]
        _require(len(entries) == 1, "plan variant missing/duplicated")
        supplied = entries[0]
    if supplied is not None:
        for key, value in spec.items():
            if key == "name":
                _require(supplied.get(key) == value, "variant name mismatch")
            elif isinstance(value, list):
                _vector(supplied.get(key), value, "plan " + key)
            else:
                _near(supplied.get(key, float("nan")), value, "plan " + key)
    return spec


def _flags():
    return {"specimen_scope": "standalone anchor + arm + hook; full-box boundary is not reproduced",
            "parameter_scope": "geometric root-plane-to-bearing length only",
            "effective_mechanical_length_mm": None, "full_box_boundary_equivalence": None,
            "anchor_clamping_or_fixture": None, "material_grade": None, "epsilon_allow": None,
            "root_flexibility_Q": None, "required_deflection_mm": None, "delta_allow_mm": None,
            "forces": None, "physical_measurements": None, "fit_results": None,
            "physical_interference": None, "qualified_strength_N": None, "qualified_clearance_mm": None,
            "improvement_validated": None, "improvement_assessed": False,
            "strength_analysis_performed": False, "deformation_analysis_performed": False,
            "fit_qualification": False, "support_generation_performed": False,
            "support_strategy_status": "pending_slicer_review", "final_print_orientation_approved": None,
            "support_required": None, "slicer_support_settings": None, "bridge_or_support_qualified": None,
            "slicer_checked": False, "printed": False, "fit_tested": False, "exported_stl": False,
            "candidate_orientation_only": True, "printer_bed_dimensions_mm": None}


def _metadata(raw, pose, spec=None):
    meta = raw.get("cad_metadata", {})
    _vector(meta.get("scale"), [1., 1., 1.], "object Scale")
    _require(meta.get("modifier_count") == 0, "unapplied modifier")
    _near(meta.get("unit_scale", float("nan")), .001, "scene unit scale")
    _require(meta.get("length_unit") == "MILLIMETERS", "scene length unit must be millimetres")
    location = SOURCE_ORIGIN if pose == "source_frame" else spec["candidate_object_location_mm"]
    _vector(meta.get("object_location_mm"), location, "object location")
    rotation = [0., 0., 0.] if pose == "source_frame" else [0., math.pi / 2, 0.]
    # The historic source dump predates Euler readback. New pose dumps must
    # provide it; source's original geometry itself is still fully checked.
    if "object_rotation_euler_radians" in meta:
        _vector(meta["object_rotation_euler_radians"], rotation, "object Euler rotation")
    return {"scale": list(meta["scale"]), "object_location_mm": list(meta["object_location_mm"]),
            "object_rotation_euler_radians": meta.get("object_rotation_euler_radians"),
            "rotation_readback_available": "object_rotation_euler_radians" in meta,
            "modifier_count": meta["modifier_count"], "unit_scale": meta["unit_scale"],
            "length_unit": meta["length_unit"]}


def validate_source_snap_tool(source_raw):
    """Validate the actual original L19 native-bevel construction tool."""
    geometry = validate_tool_mesh(source_raw["vertices"], source_raw["triangles"], "snap")
    metadata = _metadata(source_raw, "source_frame")
    upper = [i for i, p in enumerate(source_raw["vertices"]) if p[2] >= 11. - EPS_MM]
    lower = [i for i in range(len(source_raw["vertices"])) if i not in upper]
    result = {"passed": True, "kind": "coupon_source_snap_tool", "geometry_readback": geometry,
              "cad_metadata_readback": metadata, "L_geometry_mm": geometry["snap_profile"]["root_to_bearing_geometric_length_mm"],
              "native_ui_selection_reference": {"source_vertex_count": len(source_raw["vertices"]),
                  "source_triangle_count": len(source_raw["triangles"]), "z_threshold_mm": 11.,
                  "upper_vertex_indices": upper, "upper_vertex_count": len(upper),
                  "unchanged_vertex_count": len(lower),
                  "original_42_vertex_14_upper_reference": len(upper) == 14 and len(lower) == 28}}
    result.update(_flags())
    return result


def _translation(spec):
    return [q - _dot(row, SOURCE_ORIGIN) for q, row in zip(spec["candidate_object_location_mm"], ROTATION)]


def _frame_vertices(raw, pose, spec):
    if pose == "source_frame":
        return [list(p) for p in raw["vertices"]]
    translation = _translation(spec)
    return [[_dot(column, _sub(p, translation)) for column in zip(*ROTATION)] for p in raw["vertices"]]


def _inverse_length(vertices, spec):
    baseline = []
    bearing = spec["bearing_plane_z_mm"]
    delta = spec["upper_vertex_translation_z_mm"]
    for x, y, z in vertices:
        if z <= -7.4:
            restored = z
        elif z < bearing:
            restored = -7.4 + (z + 7.4) * 18.4 / (bearing + 7.4)
        else:
            restored = z - delta
        baseline.append([x, y, restored])
    return baseline


def _canonical_vertices(source, frame, spec):
    """Separate native-vertex correspondence proof from surface equivalence."""
    distances = []
    for x, y, z in source["vertices"]:
        expected = (x, y, z + spec["upper_vertex_translation_z_mm"] if z >= 11. - EPS_MM else z)
        distances.append(min(math.dist(expected, p) for p in frame))
    available = all(d <= EPS_MM for d in distances)
    return {"reference_point_count": len(distances), "reference_upper_count": sum(p[2] >= 11. - EPS_MM for p in source["vertices"]),
            "all_reference_vertices_present": available, "maximum_nearest_vertex_residual_mm": max(distances),
            "native_vertex_identity_proof_available": available and len(frame) == len(source["vertices"]),
            "surface_equivalence_does_not_require_native_vertex_count": True,
            "ui_selected_indices_are_separate_execution_evidence": True}


def _bed_features(world, frame, triangles, spec):
    bed = [i for i, pts in enumerate(world["points"]) if all(abs(p[2]) <= EPS_MM for p in pts)]
    _require(bed and all(world["normals"][i][2] < -1 + 1e-6 for i in bed), "bed contact face has wrong orientation")
    _near(world["bounds_mm"]["min"][2], 0., "candidate bed minimum")
    sourceframe = _mesh(frame, triangles, 0)
    groups = {"straight_beam": [], "root_fillet_and_miters": [], "upper_hook": []}
    bearing = spec["bearing_plane_z_mm"]
    for i, (pts, n) in enumerate(zip(sourceframe["points"], sourceframe["normals"])):
        lo, hi = min(p[2] for p in pts), max(p[2] for p in pts)
        if lo >= -7.4-EPS_MM and hi <= bearing+EPS_MM and hi-lo > EPS_MM and abs(n[2]) < 1e-6:
            groups["straight_beam"].append(i)
        if lo >= -8-EPS_MM and hi <= -7.4+EPS_MM and hi-lo > EPS_MM:
            groups["root_fillet_and_miters"].append(i)
        if lo >= bearing-EPS_MM:
            groups["upper_hook"].append(i)
    features = {}
    for name, indices in groups.items():
        _require(indices, "missing world feature " + name)
        heights = [p[2] for i in indices for p in world["points"][i]]
        features[name] = {"world_z_range_mm": [min(heights), max(heights)],
                          "triangle_count": len(indices), "triangle_indices": indices,
                          "surface_area_mm2": math.fsum(world["areas"][i] for i in indices),
                          "all_feature_samples_above_bed": min(heights) > EPS_MM}
    return {"bed_reference_z_mm": 0., "minimum_world_z_mm": world["bounds_mm"]["min"][2],
            "bed_contact_triangle_count": len(bed), "bed_contact_triangle_indices": bed,
            "bed_contact_area_mm2": math.fsum(world["areas"][i] for i in bed),
            "bed_contact_scope": "actual downward loop triangles wholly on Z=0 numeric plane; anchor side only",
            "raised_features": features, "support_required": None,
            "scope": "geometric heights/contact area only; no support, bridge, adhesion or strength decision"}


def validate_coupon(source_raw, coupon_raw, variant, pose="source_frame", plan=None):
    """Validate one unchanged-root/hook, single-L coupon, in either saved pose."""
    _require(pose in ("source_frame", "print_candidate"), "unknown coupon pose")
    spec = _spec(variant, plan)
    source_result = validate_source_snap_tool(source_raw)
    cad = _metadata(coupon_raw, pose, spec)
    if pose == "print_candidate":
        _require(cad["rotation_readback_available"], "candidate Euler readback required; Apply Rotation is not permitted")
    actual = _mesh(coupon_raw["vertices"], coupon_raw["triangles"], 0)
    frame = _frame_vertices(coupon_raw, pose, spec)
    frame_mesh = _mesh(frame, coupon_raw["triangles"], 0)
    inverse = _inverse_length(frame, spec)
    inverse_mesh = _mesh(inverse, coupon_raw["triangles"], 0)
    baseline = validate_tool_mesh(inverse, coupon_raw["triangles"], "snap")
    source_mesh = _mesh(source_raw["vertices"], source_raw["triangles"], 0)
    coverage = _surface_match(inverse_mesh, source_mesh)
    # This formula is geometric prism volume only; it is not a stiffness model.
    source_profile = source_result["geometry_readback"]["snap_profile"]
    expected_volume = source_mesh["volume_mm3"] + source_profile["beam_width_mm"] * source_profile["beam_thickness_mm"] * spec["upper_vertex_translation_z_mm"]
    _near(actual["volume_mm3"], expected_volume, "actual length-only volume", True)
    for a, b in zip(frame_mesh["dimensions_mm"], [9., 4.6, spec["whole_coupon_height_mm"]]):
        _near(a, b, "source-frame whole-coupon dimensions")
    # The horizontal underside of the protruding hook is the bearing plane;
    # measure its actual finite triangles, rather than echoing a tool location.
    bearing_faces = [i for i, (pts, n) in enumerate(zip(frame_mesh["points"], frame_mesh["normals"]))
                     if n[2] < -1+1e-6 and all(abs(p[2]-spec["bearing_plane_z_mm"]) <= EPS_MM for p in pts)]
    _require(bearing_faces, "no actual hook bearing underside")
    bearing_area = math.fsum(frame_mesh["areas"][i] for i in bearing_faces)
    _near(bearing_area, 7.2, "hook bearing area", True)
    bearing = math.fsum(frame_mesh["areas"][i] * frame_mesh["points"][i][0][2] for i in bearing_faces) / bearing_area
    root = baseline["snap_profile"]["root_plane_z_mm"]
    length = bearing - root
    _near(length, spec["L_geometry_mm"], "actual L geometry")
    result = _public(actual)
    result.update(kind="cantilever_length_coupon", variant=spec["name"], pose=pose,
                  L_geometry_mm=length, root_plane_z_mm=root, bearing_plane_z_mm=bearing,
                  arm_top_z_mm=frame_mesh["bounds_mm"]["max"][2],
                  total_arm_height_mm=frame_mesh["bounds_mm"]["max"][2]-root,
                  whole_coupon_height_mm=frame_mesh["dimensions_mm"][2],
                  source_frame_bounds_mm=frame_mesh["bounds_mm"], source_frame_dimensions_mm=frame_mesh["dimensions_mm"],
                  upper_translation_z_mm=spec["upper_vertex_translation_z_mm"],
                  measured_bearing_area_mm2=bearing_area, source_volume_mm3=source_mesh["volume_mm3"],
                  expected_length_only_volume_mm3=expected_volume,
                  inverse_geometry_readback=baseline, source_surface_match=coverage,
                  canonical_vertex_mapping=_canonical_vertices(source_raw, frame, spec),
                  held_geometry_readback=baseline["snap_profile"], cad_metadata_readback=cad,
                  inverse_mapping={"root_unchanged_at_or_below_z_mm": -7.4,
                      "source_bearing_z_mm": 11., "variant_bearing_z_mm": bearing,
                      "middle_segment_scale": 18.4/(spec["bearing_plane_z_mm"]+7.4),
                      "description": "continuous inverse: fixed root, affine straight-arm interval, rigid translated upper hook"},
                  source_reference_native_selection=source_result["native_ui_selection_reference"],
                  rigid_rotation_matrix_world=ROTATION if pose == "print_candidate" else [[1,0,0],[0,1,0],[0,0,1]],
                  rigid_world_translation_mm=_translation(spec) if pose == "print_candidate" else [0,0,0],
                  bed_and_raised_features=None)
    if pose == "print_candidate":
        for a, b in zip(actual["dimensions_mm"], spec["candidate_world_dimensions_nominal_mm"]):
            _near(a, b, "candidate world dimensions")
        result["bed_and_raised_features"] = _bed_features(actual, frame, coupon_raw["triangles"], spec)
    result.update(_flags())
    return result


def validate_coupon_layout(results_by_variant, plan=None):
    """Numerical bed/row layout, not assembled fit or printer-bed acceptance."""
    _require(set(results_by_variant) == set(SPECS), "layout must contain exactly three variants")
    names = ["A_L19", "B_L17", "C_L21"]
    for name in names:
        result = results_by_variant[name]
        spec = _spec(name, plan)
        _require(result.get("passed") is True and result.get("variant") == name and
                 result.get("pose") == "print_candidate", "layout needs actual candidate readbacks")
        _near(result["bounds_mm"]["min"][2], 0., "layout minimum Z")
        _vector(result["cad_metadata_readback"]["object_location_mm"], spec["candidate_object_location_mm"], "layout location")
    gaps = []
    for first, second in zip(names, names[1:]):
        a, b = results_by_variant[first], results_by_variant[second]
        gap = b["bounds_mm"]["min"][1] - a["bounds_mm"]["max"][1]
        _near(gap, 7.4, "adjacent row Y projection separation")
        _require(gap > 0, "coupon row bounding boxes overlap")
        gaps.append({"between": [first, second], "y_projection_gap_mm": gap, "nominal_row_pitch_mm": 12.})
    result = {"passed": True, "kind": "standalone_coupon_candidate_layout", "variant_count": 3,
              "adjacent_y_gaps": gaps, "minimum_y_projection_gap_mm": min(g["y_projection_gap_mm"] for g in gaps),
              "all_minimum_z_on_numerical_bed": True,
              "scope": "separate standalone coupons; no full box, clamp or printer-bed capacity is represented"}
    result.update(_flags())
    return result
