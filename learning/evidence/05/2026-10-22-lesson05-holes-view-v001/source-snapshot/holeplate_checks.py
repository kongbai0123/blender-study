"""Read-only checks of the final 05-03 mesh, in world-space millimetres.

No model is generated and no Blender operator is called.  Only the evaluated
object is copied into a temporary bmesh for measurement.  Numeric comparison
thresholds below address floating point reconstruction, not manufacturing
tolerances or an acceptance criterion for a printed fit.
"""
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


DIMENSION_EPS_MM = 1e-4
NORMAL_EPS = 1e-6
VOLUME_REL_EPS = 1e-5
CENTRES_X_MM = (-35.0, -21.0, -7.0, 7.0, 21.0, 35.0)
TRIAL_CLEARANCES_MM = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
PIN_WIDTH_MM = 10.0
MARKER_RADIUS_MM = 0.6
MARKER_FLOOR_Z_MM = 1.2


def _require(condition, message):
    if not condition:
        raise RuntimeError("05-03 final-mesh validation: " + message)


def _close(actual, expected, eps=DIMENSION_EPS_MM):
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=eps)


def _rounded(value):
    return round(float(value), 7)


def _vector(value):
    return [_rounded(v) for v in value]


def _bounds(vertices):
    coordinates = [v.co for v in vertices]
    _require(bool(coordinates), "empty vertex set")
    return ([min(v[a] for v in coordinates) for a in range(3)],
            [max(v[a] for v in coordinates) for a in range(3)])


def _components(faces):
    """Connected face patches through shared edges, without changing topology."""
    pending = set(faces)
    components = []
    while pending:
        seed = pending.pop()
        found, stack = {seed}, [seed]
        while stack:
            face = stack.pop()
            for edge in face.edges:
                for neighbour in edge.link_faces:
                    if neighbour in pending:
                        pending.remove(neighbour)
                        found.add(neighbour)
                        stack.append(neighbour)
        components.append(found)
    return components


def _plane_groups(faces, axis):
    groups = []
    for face in faces:
        coordinate = sum(v.co[axis] for v in face.verts) / len(face.verts)
        _require(all(_close(v.co[axis], coordinate) for v in face.verts),
                 "inner wall is not planar")
        for group in groups:
            if _close(group["coordinate"], coordinate):
                group["faces"].append(face)
                break
        else:
            groups.append({"coordinate": coordinate, "faces": [face]})
    return sorted(groups, key=lambda group: group["coordinate"])


def _ray(bvh, origin, direction, distance=10.0):
    location, normal, face_index, travelled = bvh.ray_cast(
        Vector(origin), Vector(direction), distance)
    if location is None:
        return None
    return {"location_mm": _vector(location), "normal": _vector(normal),
            "face_index": int(face_index), "distance_mm": _rounded(travelled)}


def _read_hole(bm, bvh, number, centre_x, expected_width):
    centre_y = 2.0
    # A 12.4 mm ROI isolates each actual inner wall. Adjacent hole centres are
    # 14 mm apart, and the marker row lies outside this ROI.
    candidates = [face for face in bm.faces if all(
        abs(v.co.x - centre_x) <= 6.2 and abs(v.co.y - centre_y) <= 6.2
        for v in face.verts)]
    groups_by_axis = []
    wall_evidence = []
    for axis in (0, 1):
        axial = [face for face in candidates
                 if abs(face.normal[axis]) >= 1.0 - NORMAL_EPS]
        groups = _plane_groups(axial, axis)
        _require(len(groups) == 2,
                 "hole %d has %d inner-wall planes on axis %d" %
                 (number, len(groups), axis))
        groups_by_axis.append(groups)
        for group in groups:
            vertices = {v for face in group["faces"] for v in face.verts}
            lower, upper = _bounds(vertices)
            area = sum(face.calc_area() for face in group["faces"])
            _require(_close(lower[2], -2.0) and _close(upper[2], 2.0),
                     "hole %d wall does not span the plate thickness" % number)
            _require(math.isclose(area, expected_width * 4.0,
                                 rel_tol=VOLUME_REL_EPS, abs_tol=DIMENSION_EPS_MM),
                     "hole %d wall area is inconsistent with a full square wall" % number)
            wall_evidence.append({"axis": "XY"[axis],
                                  "coordinate_mm": _rounded(group["coordinate"]),
                                  "bounds_min_mm": _vector(lower),
                                  "bounds_max_mm": _vector(upper),
                                  "area_mm2": _rounded(area),
                                  "face_count": len(group["faces"])})

    x_planes = [group["coordinate"] for group in groups_by_axis[0]]
    y_planes = [group["coordinate"] for group in groups_by_axis[1]]
    width, height = x_planes[1] - x_planes[0], y_planes[1] - y_planes[0]
    _require(_close(width, expected_width) and _close(height, expected_width),
             "hole %d measured width/height %r differ from nominal %r" %
             (number, (width, height), expected_width))
    _require(_close(sum(x_planes) / 2.0, centre_x) and
             _close(sum(y_planes) / 2.0, centre_y),
             "hole %d measured centre differs from design" % number)

    vertical = _ray(bvh, (centre_x, centre_y, 3.0), (0, 0, -1), 6.0)
    reverse_vertical = _ray(bvh, (centre_x, centre_y, -3.0), (0, 0, 1), 6.0)
    _require(vertical is None and reverse_vertical is None,
             "hole %d centre is obstructed along Z" % number)
    side_rays = []
    for z in (-1.0, 0.0, 1.0):
        for axis, sign in ((0, -1), (0, 1), (1, -1), (1, 1)):
            direction = [0, 0, 0]
            direction[axis] = sign
            hit = _ray(bvh, (centre_x, centre_y, z), direction, 7.0)
            expected = (width if axis == 0 else height) / 2.0
            _require(hit is not None and _close(hit["distance_mm"], expected),
                     "hole %d side ray is inconsistent at z=%g" % (number, z))
            side_rays.append({"origin_mm": [centre_x, centre_y, z],
                              "direction": direction, "hit": hit})
    return {"number": number, "centre_mm": [centre_x, centre_y],
            "nominal_width_mm": expected_width, "width_mm": _rounded(width),
            "height_mm": _rounded(height),
            "measured_total_clearance_x_mm": _rounded(width - PIN_WIDTH_MM),
            "measured_total_clearance_y_mm": _rounded(height - PIN_WIDTH_MM),
            "through_at_centre": True, "vertical_ray_from_above": vertical,
            "vertical_ray_from_below": reverse_vertical,
            "inner_walls": wall_evidence, "side_rays": side_rays}


def _read_markers(bm, bvh):
    floor_faces = [face for face in bm.faces
                   if face.normal.z >= 1.0 - NORMAL_EPS and
                   all(_close(v.co.z, MARKER_FLOOR_Z_MM) for v in face.verts)]
    patches = _components(floor_faces)
    _require(len(patches) == 21,
             "expected 21 separate blind-marker floors, found %d" % len(patches))
    observed = []
    for patch in patches:
        lower, upper = _bounds({v for face in patch for v in face.verts})
        _require(_close(upper[0] - lower[0], 2 * MARKER_RADIUS_MM) and
                 _close(upper[1] - lower[1], 2 * MARKER_RADIUS_MM),
                 "a marker-floor diameter differs from 1.2 mm")
        observed.append({"centre": ((lower[0] + upper[0]) / 2.0,
                                     (lower[1] + upper[1]) / 2.0),
                         "bounds_min_mm": _vector(lower),
                         "bounds_max_mm": _vector(upper),
                         "area_mm2": sum(face.calc_area() for face in patch),
                         "face_count": len(patch)})

    markers = []
    counts = []
    assigned = set()
    for number, hole_x in enumerate(CENTRES_X_MM, 1):
        row = []
        for j in range(number):
            x = hole_x + (j - (number - 1) / 2.0) * 1.6
            y = -8.5
            matches = [(index, patch) for index, patch in enumerate(observed)
                       if _close(patch["centre"][0], x) and
                       _close(patch["centre"][1], y)]
            _require(len(matches) == 1 and matches[0][0] not in assigned,
                     "marker %d/%d has no unique measured floor patch" % (number, j + 1))
            index, patch = matches[0]
            assigned.add(index)
            floor = _ray(bvh, (x, y, 3.0), (0, 0, -1), 6.0)
            bottom = _ray(bvh, (x, y, -3.0), (0, 0, 1), 6.0)
            _require(floor is not None and
                     _close(floor["location_mm"][2], MARKER_FLOOR_Z_MM),
                     "marker %d/%d is not a blind recess with floor z=1.2" % (number, j + 1))
            _require(bottom is not None and _close(bottom["location_mm"][2], -2.0),
                     "marker %d/%d has no intact plate bottom" % (number, j + 1))
            top_controls = []
            for control_y in (y - 0.9, y + 0.9):
                hit = _ray(bvh, (x, control_y, 3.0), (0, 0, -1), 6.0)
                _require(hit is not None and _close(hit["location_mm"][2], 2.0),
                         "solid control beside marker %d/%d is not at z=2" % (number, j + 1))
                top_controls.append({"origin_mm": [x, control_y, 3.0], "hit": hit})
            row.append({"number_in_row": j + 1, "centre_mm": [x, y],
                        "floor_z_mm": floor["location_mm"][2],
                        "depth_mm": _rounded(2.0 - floor["location_mm"][2]),
                        "remaining_bottom_thickness_mm": _rounded(
                            floor["location_mm"][2] - bottom["location_mm"][2]),
                        "floor_ray": floor, "bottom_ray": bottom,
                        "solid_top_controls": top_controls,
                        "floor_patch": {key: (_rounded(value) if key == "area_mm2" else value)
                                        for key, value in patch.items() if key != "centre"}})
        counts.append(len(row))
        markers.append({"hole_number": number, "count": len(row), "points": row})
    _require(len(assigned) == len(patches), "unassigned extra marker floor")
    return markers, counts, sum(patch["area_mm2"] for patch in observed)


def read_and_validate(obj):
    """Return final-mesh measurements, or raise RuntimeError on mismatch.

    The returned experiment values do not assert a qualified printed clearance.
    The caller remains responsible for the separate file/reopen/SHA checks.
    """
    _require(obj is not None and obj.type == "MESH", "object is not a mesh")
    units = bpy.context.scene.unit_settings
    _require(units.system == "METRIC" and units.length_unit == "MILLIMETERS" and
             math.isclose(units.scale_length, 0.001, rel_tol=0, abs_tol=1e-9),
             "scene units are not Metric / Millimeters / 0.001")
    _require(all(_close(v, 1.0) for v in obj.scale), "object Scale is not 1 / 1 / 1")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        factor = units.scale_length * 1000.0
        for vertex in bm.verts:
            vertex.co = (evaluated.matrix_world @ vertex.co) * factor
        bm.normal_update()
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()
        lower, upper = _bounds(bm.verts)
        dimensions = [upper[a] - lower[a] for a in range(3)]
        _require(all(_close(v, target) for v, target in zip(dimensions, (96.0, 26.0, 4.0))),
                 "plate bounds are not 96 x 26 x 4 mm: %r" % dimensions)
        _require(all(_close(v, target) for v, target in zip(lower, (-48.0, -13.0, -2.0))) and
                 all(_close(v, target) for v, target in zip(upper, (48.0, 13.0, 2.0))),
                 "plate world-space bounds are not centred at (0, 0, 0)")
        non_manifold = sum(not edge.is_manifold for edge in bm.edges)
        isolated_vertices = sum(not vertex.link_edges for vertex in bm.verts)
        _require(non_manifold == 0 and isolated_vertices == 0,
                 "plate has non-manifold edges or isolated vertices")
        components = _components(bm.faces)
        _require(len(components) == 1, "plate is not a single connected shell")
        euler = len(bm.verts) - len(bm.edges) + len(bm.faces)
        _require(euler == -10, "Euler characteristic does not describe six through holes: %d" % euler)
        volume = bm.calc_volume(signed=True)
        _require(math.isfinite(volume) and volume > 0, "plate signed volume is not positive")
        bvh = BVHTree.FromBMesh(bm)
        holes = [_read_hole(bm, bvh, i, x, PIN_WIDTH_MM + clearance)
                 for i, (x, clearance) in enumerate(zip(CENTRES_X_MM, TRIAL_CLEARANCES_MM), 1)]
        markers, marker_counts, floor_area = _read_markers(bm, bvh)
        # Uses actual final-mesh floor areas, including the cylinder polygon
        # approximation, rather than pretending those floors are exact circles.
        expected_volume = (96.0 * 26.0 * 4.0 -
                           sum(h["width_mm"] * h["height_mm"] * 4.0 for h in holes) -
                           floor_area * 0.8)
        _require(math.isclose(volume, expected_volume, rel_tol=VOLUME_REL_EPS,
                             abs_tol=DIMENSION_EPS_MM),
                 "signed volume differs from outer plate minus measured holes and blind recesses")
        solid_top = _ray(bvh, (-46.0, 0.0, 3.0), (0, 0, -1), 6.0)
        solid_bottom = _ray(bvh, (-46.0, 0.0, -3.0), (0, 0, 1), 6.0)
        _require(solid_top is not None and _close(solid_top["location_mm"][2], 2.0) and
                 solid_bottom is not None and _close(solid_bottom["location_mm"][2], -2.0),
                 "solid plate control rays failed")
        return {
            "passed": True, "measurement_source": "evaluated final plate mesh in world-space millimetres",
            "object_name": obj.name, "board_dimensions_mm": _vector(dimensions),
            "board_bounds_mm": {"min": _vector(lower), "max": _vector(upper)},
            "pin_nominal_mm": PIN_WIDTH_MM, "pin_dimensions_mm": [10.0, 10.0, 8.0],
            "trial_total_clearances_mm": list(TRIAL_CLEARANCES_MM),
            "measured_hole_widths_mm": [[hole["width_mm"], hole["height_mm"]] for hole in holes],
            "measured_hole_x_mm": [hole["width_mm"] for hole in holes],
            "measured_hole_y_mm": [hole["height_mm"] for hole in holes],
            "measured_hole_heights_mm": [hole["height_mm"] for hole in holes],
            "through_holes": len(holes), "holes": holes,
            "marker_counts": marker_counts, "marker_total": sum(marker_counts),
            "markers": markers, "non_manifold_edges": non_manifold,
            "isolated_vertices": isolated_vertices, "connected_shells": len(components),
            "euler_characteristic": euler, "genus": (2 - euler) // 2,
            "closed_volume": True, "volume_mm3": _rounded(volume),
            "expected_volume_from_measured_mesh_mm3": _rounded(expected_volume),
            "mesh_counts": {"vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces)},
            "scale": _vector(obj.scale), "unit_scale": round(units.scale_length, 9),
            "length_unit": units.length_unit,
            "solid_plate_control_rays": {"top": solid_top, "bottom": solid_bottom},
            "printed": False, "fit_tested": False, "qualified_clearance_mm": None,
            "clearance_status": "experimental trial points; no qualified printed fit",
            "numericComparison": {
                "purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                "dimensionsAbsMm": DIMENSION_EPS_MM, "normalAbs": NORMAL_EPS,
                "volumeRelative": VOLUME_REL_EPS,
            },
        }
    finally:
        bm.free()
        evaluated.to_mesh_clear()
