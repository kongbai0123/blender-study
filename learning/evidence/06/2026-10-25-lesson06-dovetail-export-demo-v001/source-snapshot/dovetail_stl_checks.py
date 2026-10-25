"""Strict binary STL readback for the verified 06-02 Body/SlidingLid.

STL declares no units. Numeric coordinates are interpreted as millimetres and
world Z is preserved. Source matching uses measured planes, profiles, areas,
rays and volume, not vertex indices or a particular triangulation/signature.
These are geometry/file checks, never qualification of a printed clearance.
"""
import math

from dovetail_checks import (EPS_MM, REL_EPS, validate_assembly,
                            validate_body_mesh, validate_lid_mesh)
from stl_checks import WELD_EPS_MM, read_stl


def _require(condition, message):
    if not condition:
        raise ValueError("Dovetail STL verification: " + message)


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _number(actual, expected, label, relative=False, eps=EPS_MM):
    _require(_numeric(expected) and math.isclose(actual, expected,
             rel_tol=REL_EPS if relative else 0.0, abs_tol=eps), "STL/source %s mismatch" % label)


def _vector(actual, expected, label, relative=False):
    _require(isinstance(expected, (list, tuple)) and len(actual) == len(expected), "STL/source %s shape mismatch" % label)
    for i, (a, b) in enumerate(zip(actual, expected)):
        _number(a, b, "%s[%d]" % (label, i), relative)


def _bounds(actual, expected, label):
    _require(isinstance(expected, dict), "source %s is missing" % label)
    for side in ("min", "max"):
        _vector(actual[side], expected.get(side), label + "." + side)


def _profiles(actual, expected, label):
    _require(isinstance(expected, list) and len(actual) == len(expected) == 2, "source %s needs two profiles" % label)
    for i, (a, b) in enumerate(zip(actual, expected)):
        prefix = "%s[%d]" % (label, i)
        _require(isinstance(b, dict), "invalid source profile")
        _number(a["centre_y_mm"], b.get("centre_y_mm"), prefix + ".centre_y_mm")
        _vector(a["x_mm"], b.get("x_mm"), prefix + ".x_mm")
        ap, bp = a["profile"], b.get("profile")
        _require(isinstance(bp, dict), "missing source profile geometry")
        for key in ("z_mm", "widths_mm"):
            _vector(ap[key], bp.get(key), prefix + "." + key)
        _number(ap["side_slope_abs"], bp.get("side_slope_abs"), prefix + ".side_slope_abs", eps=1e-5)
        planes = bp.get("side_planes")
        _require(isinstance(planes, list) and len(planes) == 2, "source profile requires two side planes")
        for j, (left, right) in enumerate(zip(ap["side_planes"], planes)):
            plane_label = prefix + ".side_planes[%d]" % j
            _require(isinstance(right, dict) and left["side"] == right.get("side"), "source profile sides mismatch")
            _number(left["slope_z"], right.get("slope_z"), plane_label + ".slope_z", eps=1e-5)
            _number(left["offset_mm"], right.get("offset_mm"), plane_label + ".offset_mm")
            _number(left["area_mm2"], right.get("area_mm2"), plane_label + ".area_mm2", relative=True)
            _bounds(left["bounds_mm"], right.get("bounds_mm"), plane_label + ".bounds_mm")
        if "open_ends" in a:
            _require(b.get("open_ends") is True, "source channel is not open at both ends")


def _compare_geometry(actual, source, kind):
    expected_kind = "dovetail_body" if kind == "body" else "dovetail_lid"
    _require(isinstance(source, dict) and source.get("passed") is True and source.get("kind") == expected_kind,
             "successful source %s measurement is required" % kind)
    compared = ["dimensions_mm", "bounds_mm", "volume_mm3", "topology"]
    _vector(actual["dimensions_mm"], source.get("dimensions_mm"), "dimensions_mm")
    _bounds(actual["bounds_mm"], source.get("bounds_mm"), "bounds_mm")
    _number(actual["volume_mm3"], source.get("volume_mm3"), "volume_mm3", relative=True)
    for key, expected in (("non_manifold_edges", 0), ("non_manifold_vertex_links", 0),
                          ("inconsistent_winding_edges", 0), ("connected_shells", 1),
                          ("euler_characteristic", 2), ("genus", 0)):
        _require(source.get(key) == expected, "source topology failed: " + key)

    profile_key = "channels" if kind == "body" else "male_ribs"
    _profiles(actual[profile_key], source.get(profile_key), profile_key)
    compared.append(profile_key)
    expected_axes = source.get("actual_axis_planes")
    _require(isinstance(expected_axes, dict), "missing source axis planes")
    for axis in "XYZ":
        a, b = actual["actual_axis_planes"][axis], expected_axes.get(axis)
        _require(isinstance(b, list) and len(a) == len(b), "source axis-plane count mismatch")
        for i, (left, right) in enumerate(zip(a, b)):
            label = "actual_axis_planes.%s[%d]" % (axis, i)
            _number(left["coordinate_mm"], right.get("coordinate_mm"), label + ".coordinate_mm")
            _number(left["area_mm2"], right.get("area_mm2"), label + ".area_mm2", relative=True)
            _bounds(left["bounds_mm"], right.get("bounds_mm"), label + ".bounds_mm")
    compared.append("actual_axis_planes")
    rays = source.get("vertical_rays")
    _require(isinstance(rays, list) and len(rays) == len(actual["vertical_rays"]), "source ray count mismatch")
    for i, (a, b) in enumerate(zip(actual["vertical_rays"], rays)):
        _require(a["label"] == b.get("label"), "source ray label mismatch")
        _vector(a["xy_mm"], b.get("xy_mm"), "vertical_rays[%d].xy_mm" % i)
        _vector(a["z_hits_mm"], b.get("z_hits_mm"), "vertical_rays[%d].z_hits_mm" % i)
    compared.append("vertical_rays")

    if kind == "body":
        for key in ("min_guide_ligament_mm", "channel_floor_web_mm", "local_cavity_width_mm", "rim_z_mm"):
            _number(actual[key], source.get(key), key)
            compared.append(key)
        for key in ("original_shell_dimensions_mm", "original_lower_cavity_dimensions_mm"):
            _vector(actual[key], source.get(key), key)
            compared.append(key)
        proof = source.get("full_length_entry_proof")
        _require(isinstance(proof, dict) and proof.get("both_end_faces_have_channel_cutouts") is True,
                 "source full-length entry proof is missing")
        for key in ("end_face_area_mm2", "sloped_walls_and_floors_span_x_mm"):
            _vector(actual["full_length_entry_proof"][key], proof.get(key), "full_length_entry_proof." + key,
                    relative=key == "end_face_area_mm2")
        compared.append("full_length_entry_proof")
    else:
        for key in ("plate_dimensions_mm", "plate_z_mm"):
            _vector(actual[key], source.get(key), key)
            compared.append(key)
        _number(actual["exposed_male_depth_mm"], source.get("exposed_male_depth_mm"), "exposed_male_depth_mm")
        compared.append("exposed_male_depth_mm")
    return compared


def validate_dovetail_stl(path, kind, source_measurement):
    """Strictly read and source-check a Body or SlidingLid binary STL.

    Source may be the complete 06-02 verification or the appropriate successful
    per-part measurement. Complete metadata additionally supports an independent
    nominal assembly readback using this STL and the other source part.
    Reindexing and alternative valid triangulations do not require matching a
    source triangle signature or a fixed number of triangles.
    """
    aliases = {"body": "body", "Body": "body", "lid": "lid", "SlidingLid": "lid", "sliding_lid": "lid"}
    _require(kind in aliases, "unknown part kind")
    kind = aliases[kind]
    full_source = None
    if isinstance(source_measurement, dict) and ("body" in source_measurement or "lid" in source_measurement):
        full_source = source_measurement
        _require(full_source.get("passed") is True, "full source verification did not pass")
        source = full_source.get(kind)
    else:
        source = source_measurement
    _require(isinstance(source, dict) and source.get("passed") is True,
             "successful source measurement is required")

    mesh = read_stl(path)
    _require(mesh["non_manifold_edges"] == 0 and mesh["non_manifold_vertex_links"] == 0, "STL is not a closed manifold")
    _require(mesh["inconsistent_winding_edges"] == 0, "STL has inconsistent triangle winding")
    _require(mesh["connected_shells"] == 1 and mesh["genus"] == 0, "STL is not one connected genus-0 shell")
    _require(mesh["signed_volume_mm3"] > 0, "STL signed volume is not positive")
    geometry = (validate_body_mesh if kind == "body" else validate_lid_mesh)(mesh["vertices"], mesh["triangles"])
    _vector(mesh["dimensions_mm"], geometry["dimensions_mm"], "independent reader dimensions")
    _number(mesh["volume_mm3"], geometry["volume_mm3"], "independent reader volume", relative=True)
    compared = _compare_geometry(geometry, source, kind)
    result = {key: value for key, value in mesh.items() if key not in ("vertices", "triangles")}
    result.update(passed=True, kind="dovetail_stl", part_kind=kind,
                  geometry_readback=geometry, source_measurement_compared=compared,
                  source_match_method="actual profile/plane positions, areas, bounds, material rays and volume; independent of triangle indexing/triangulation",
                  exported_stl=True, slicer_checked=False, overhang_analysis_performed=False,
                  printed=False, fit_tested=False, physical_measurements=None, fit_results=None,
                  physical_interference=None, qualified_clearance_mm=None,
                  trial_status="experimental_geometry_only", nominal_horizontal_total_trial_mm=0.4,
                  numericComparison={"purpose": "Floating point reconstruction only; not manufacturing tolerance or printed fit acceptance",
                                     "dimensionsAbsMm": EPS_MM, "coordinateWeldMm": WELD_EPS_MM,
                                     "volumeRelative": REL_EPS})
    if full_source is not None:
        counterpart = full_source.get("lid" if kind == "body" else "body")
        _require(isinstance(counterpart, dict) and counterpart.get("passed") is True, "successful counterpart source measurement required")
        result["assembly_readback"] = (validate_assembly(geometry, counterpart) if kind == "body"
                                       else validate_assembly(counterpart, geometry))
        prior_assembly = full_source.get("assembly")
        if prior_assembly is not None:
            _require(isinstance(prior_assembly, dict) and prior_assembly.get("passed") is True, "source assembly measurement did not pass")
            for key in ("horizontal_side_gap_mm", "normal_side_gap_mm", "bottom_gap_mm", "plate_rim_gap_mm"):
                _number(result["assembly_readback"][key], prior_assembly.get(key), "assembly." + key)
            compared.append("assembly_actual_clearances")
        # scene_* points to the actual dovetail source checkpoint; its own
        # source_scene_* fields identify the earlier plain-box ancestor.
        result.update(source_scene_path=full_source.get("scene_path"),
                      source_scene_sha256=full_source.get("scene_sha256"))
    return result
