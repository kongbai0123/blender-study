"""Read-only, standard-library verification of the 05-06 lid STL export.

STL has no units; numeric coordinates are interpreted as millimetres in this
workflow. The parser measures binary triangle data, then the lid checker tests
the actual cap/lip planes, areas and material rays. Source metadata is compared
separately. None of these checks qualifies a printed clearance.
"""
import math

from lid_checks import DIMENSION_EPS_MM, VOLUME_REL_EPS, validate_lid_mesh
from stl_checks import WELD_EPS_MM, read_stl


def _require(condition, message):
    if not condition:
        raise ValueError("Lid STL verification: " + message)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _compare(actual, expected, key, volume=False):
    _require(_number(expected) and math.isclose(actual, expected,
             rel_tol=VOLUME_REL_EPS if volume else 0.0, abs_tol=DIMENSION_EPS_MM),
             "STL/source %s mismatch" % key)


def _compare_vector(actual, expected, key):
    _require(isinstance(expected, (list, tuple)) and len(expected) == len(actual),
             "STL/source %s shape mismatch" % key)
    for index, (a, b) in enumerate(zip(actual, expected)):
        _compare(a, b, "%s[%d]" % (key, index))


def validate_lid_stl(path, source_metadata=None):
    """Return measured STL evidence or raise ValueError on a mismatch.

    ``source_metadata`` is the full successful 05-05 ``verification.json`` with
    ``body`` and ``lid`` records. With it, nominal assembly gaps are recomputed
    from STL lip planes and the measured source cavity; no Blender is launched.
    Without it, lid geometry is still measured, while assembly remains ``None``.
    """
    source_body = source_lid = None
    if source_metadata is not None:
        _require(isinstance(source_metadata, dict) and source_metadata.get("passed") is True,
                 "source metadata must be a successful verification dict")
        source_body, source_lid = source_metadata.get("body"), source_metadata.get("lid")
        _require(isinstance(source_body, dict) and source_body.get("passed") is True and
                 source_body.get("kind") == "box_body", "successful source body measurement is required")
        _require(isinstance(source_lid, dict) and source_lid.get("passed") is True and
                 source_lid.get("kind") == "lid", "successful source lid measurement is required")
    mesh = read_stl(path)
    # Both independent readers must agree on closed, consistently oriented,
    # single-shell topology. Geometry is tested from actual binary vertices.
    _require(mesh["non_manifold_edges"] == 0 and mesh["non_manifold_vertex_links"] == 0,
             "export is not a closed manifold")
    _require(mesh["inconsistent_winding_edges"] == 0, "inconsistent triangle winding")
    _require(mesh["connected_shells"] == 1 and mesh["genus"] == 0,
             "export is not one connected genus-0 shell")
    _require(mesh["signed_volume_mm3"] > 0, "signed volume is not positive")
    geometry = validate_lid_mesh(mesh["vertices"], mesh["triangles"], source_body)
    _compare_vector(mesh["dimensions_mm"], geometry["dimensions_mm"], "independent mesh dimensions")
    _compare(mesh["volume_mm3"], geometry["volume_mm3"], "independent mesh volume", volume=True)

    compared = []
    if source_lid is not None:
        for key in ("dimensions_mm", "plate_dimensions_mm", "plate_z_mm", "ring_outer_mm", "ring_inner_mm",
                    "ring_z_mm", "ring_wall_thicknesses_mm"):
            _require(key in source_lid, "source lid is missing %s" % key)
            _compare_vector(geometry[key], source_lid[key], key)
            compared.append("lid." + key)
        for key in ("plate_thickness_mm", "ring_depth_mm", "ring_wall_mm", "engagement_mm", "volume_mm3"):
            _require(key in source_lid, "source lid is missing %s" % key)
            _compare(geometry[key], source_lid[key], key, volume=key == "volume_mm3")
            compared.append("lid." + key)
        for key in ("bounds_mm", "ring_outer_bounds_mm", "ring_inner_bounds_mm"):
            expected = source_lid.get(key)
            _require(isinstance(expected, dict), "source lid is missing %s" % key)
            for side in ("min", "max"):
                _compare_vector(geometry[key][side], expected.get(side), "%s.%s" % (key, side))
            compared.append("lid." + key)
        for key, expected in (("non_manifold_edges", 0), ("connected_shells", 1), ("genus", 0)):
            _require(source_lid.get(key) == expected, "source lid topology failed: " + key)
        source_assembly = source_lid.get("assembly")
        _require(isinstance(source_assembly, dict), "source lid assembly measurement is required")
        for key in ("per_side_clearances_mm", "total_clearances_mm"):
            _compare_vector(geometry["assembly"][key], source_assembly.get(key), "assembly." + key)
            compared.append("lid.assembly." + key)
        for key in ("engagement_mm", "cavity_depth_mm", "floor_reserve_mm", "rim_contact_z_mm"):
            _compare(geometry["assembly"][key], source_assembly.get(key), "assembly." + key)
            compared.append("lid.assembly." + key)
        compared.append("body.cavity_bounds_mm")

    result = {key: value for key, value in mesh.items() if key not in ("vertices", "triangles")}
    result.update(passed=True, kind="lid_stl", lid_geometry=geometry,
                  source_metadata_compared=compared,
                  printed=False, fit_tested=False, physical_measurements=None,
                  fit_results=None, physical_interference=None, qualified_clearance_mm=None,
                  trial_status="experimental_geometry_only", trial_total_clearance_mm=0.4,
                  trial_per_side_clearance_mm=0.2,
                  numericComparison={
                      "purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                      "dimensionsAbsMm": DIMENSION_EPS_MM, "coordinateWeldMm": WELD_EPS_MM,
                      "volumeRelative": VOLUME_REL_EPS,
                  })
    if source_metadata is not None:
        result.update(source_scene_path=source_metadata.get("scene_path"),
                      source_scene_sha256=source_metadata.get("scene_sha256"))
    return result
