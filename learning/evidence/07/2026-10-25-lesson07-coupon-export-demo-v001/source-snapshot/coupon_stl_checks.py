"""07-05 strict binary STL/readback of three source-bound coupon candidates.

STL stores no units or object transform. Numbers are interpreted as millimetres;
the original Ry90 reference is used solely to invert world points for geometry
validation. It is never reported as STL or fresh reimport transform metadata.
"""
import copy

from tenon_checks import _mesh, _public
from stl_checks import read_stl, WELD_EPS_MM
from snapfit_stl_checks import _surface_match, _semantic, _near
from coupon_checks import (validate_coupon, validate_coupon_layout, _flags,
                           SPECS, EPS_MM, REL_EPS)


SOURCE_SHA256 = "22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8"


def _require(condition, message):
    if not condition:
        raise ValueError("07-05 coupon STL: " + message)


def _source_context(variant, source_verification, source_candidate_raw, source_snap_tool_raw):
    _require(variant in SPECS, "unknown coupon variant")
    _require(source_verification.get("passed") is True and source_verification.get("reopened") is True and
             source_verification.get("kind") == "snapfit_length_coupons_geometry_demo" and
             source_verification.get("scene_sha256") == SOURCE_SHA256,
             "fixed successful 07-05 candidate checkpoint is required")
    record = source_verification.get("candidates", {}).get(variant)
    _require(isinstance(record, dict) and record.get("passed") is True and
             record.get("variant") == variant and record.get("pose") == "print_candidate",
             "actual source candidate readback is missing")
    source_readback = validate_coupon(source_snap_tool_raw, source_candidate_raw, variant, "print_candidate")
    _semantic(source_readback, record, "fixed_source.candidate")
    return source_readback


def validate_coupon_export_mesh(vertices, triangles, variant, source_verification,
                                source_candidate_raw, source_snap_tool_raw):
    """Validate baked world geometry; actual reimport CAD metadata is separate."""
    source_readback = _source_context(variant, source_verification, source_candidate_raw, source_snap_tool_raw)
    actual = _mesh(vertices, triangles, 0)
    source = _mesh(source_candidate_raw["vertices"], source_candidate_raw["triangles"], 0)
    for side in ("min", "max"):
        for a, b in zip(actual["bounds_mm"][side], source["bounds_mm"][side]):
            _near(a, b, "candidate world " + side + " bound")
    _near(actual["volume_mm3"], source["volume_mm3"], "source-bound coupon volume", True)
    _require(abs(actual["bounds_mm"]["min"][2]) <= EPS_MM, "candidate is not on the numeric Z0 reference")
    reference_raw = {"vertices": actual["vertices"], "triangles": actual["triangles"],
                     "cad_metadata": copy.deepcopy(source_candidate_raw["cad_metadata"])}
    geometry = validate_coupon(source_snap_tool_raw, reference_raw, variant, "print_candidate")
    coverage = _surface_match(actual, source)
    # Shape validation is independent of face count/indexing. Bed area and
    # raised feature heights are separately source-bound measured quantities.
    _near(geometry["L_geometry_mm"], source_readback["L_geometry_mm"], "geometric arm length")
    for key in ("total_arm_height_mm", "whole_coupon_height_mm", "measured_bearing_area_mm2"):
        _near(geometry[key], source_readback[key], key, key.endswith("area_mm2"))
    bed = geometry["bed_and_raised_features"]
    source_bed = source_readback["bed_and_raised_features"]
    _near(bed["bed_contact_area_mm2"], source_bed["bed_contact_area_mm2"], "anchor-only numeric bed area", True)
    for name, feature in bed["raised_features"].items():
        for a, b in zip(feature["world_z_range_mm"], source_bed["raised_features"][name]["world_z_range_mm"]):
            _near(a, b, name + " raised world height")
    result = _public(actual)
    result.update(_flags())
    result.update(kind="cantilever_coupon_export_mesh", variant=variant,
                  source_pose="print_candidate", world_pose_retained=True,
                  source_scene_path=source_verification["scene_path"], source_scene_sha256=SOURCE_SHA256,
                  geometry_readback=geometry, source_surface_match=coverage,
                  L_geometry_mm=geometry["L_geometry_mm"], total_arm_height_mm=geometry["total_arm_height_mm"],
                  whole_coupon_height_mm=geometry["whole_coupon_height_mm"],
                  bed_and_raised_features=bed, minimum_world_z_mm=actual["bounds_mm"]["min"][2],
                  reference_source_object_axis_dimensions_mm=source_candidate_raw["cad_metadata"].get("object_axis_dimensions_mm"),
                  reference_pose_metadata=copy.deepcopy(source_candidate_raw["cad_metadata"]),
                  pose_metadata_role="Source candidate Ry90/origin is an inverse-geometry reference only. STL has no transform; fresh reimport CAD metadata must be recorded independently.",
                  geometry_readback_scope="Frozen coupon validator given the source pose reference and actual exported world vertices; its CAD readback describes that reference, never STL or reimport transforms.",
                  rotation_applied_for_export=False, geometry_modified_for_export=False,
                  mesh_analysis_overhang_checked=False, physical_interpretation="digital geometry only",
                  statistics_scope="Actual STL/reimport loop-triangle areas and world-height samples; not native polygon or GPU counts and not a new Overhang analysis.",
                  units="STL has no unit marker; coordinates are interpreted as millimetres for this export.",
                  numericComparison={"purpose":"Floating point reconstruction only; not manufacturing tolerance, support, strength or fit acceptance",
                                     "dimensionsAbsMm":EPS_MM,"coordinateWeldMm":WELD_EPS_MM,"volumeRelative":REL_EPS})
    return result


def validate_coupon_stl(path, variant, source_verification, source_candidate_raw, source_snap_tool_raw):
    """Strict binary decoding/welding plus oriented surface and inverse checks."""
    mesh = read_stl(path)
    result = validate_coupon_export_mesh(mesh["vertices"], mesh["triangles"], variant,
                                         source_verification, source_candidate_raw, source_snap_tool_raw)
    result.update({key:value for key,value in mesh.items() if key not in ("vertices", "triangles")})
    result.update(kind="cantilever_coupon_stl", exported_stl=True)
    return result


def validate_export_layout(results_by_variant, source_verification=None):
    _require(set(results_by_variant) == set(SPECS), "layout needs exactly A/B/C exports")
    geometries = {}
    for name, part in results_by_variant.items():
        _require(part.get("passed") is True and part.get("variant") == name and
                 part.get("world_pose_retained") is True and part.get("source_pose") == "print_candidate" and
                 part.get("source_scene_sha256") == SOURCE_SHA256, "layout has a wrong candidate/export")
        geometries[name] = part["geometry_readback"]
    layout = validate_coupon_layout(geometries)
    if source_verification is not None:
        _require(source_verification.get("passed") is True and source_verification.get("scene_sha256") == SOURCE_SHA256,
                 "layout source checkpoint mismatch")
        _semantic(layout, source_verification["layout"], "source.layout")
    layout.update(kind="cantilever_coupon_export_layout", source_pose="print_candidate",
                  source_scene_sha256=SOURCE_SHA256, geometry_modified_for_export=False,
                  rotation_applied_for_export=False, printer_bed_dimensions_mm=None, bed_capacity_checked=False,
                  scope="Three separate standalone candidate coupons with preserved world layout; no full-box assembly, fixture or printer-bed capacity checked.")
    return layout
