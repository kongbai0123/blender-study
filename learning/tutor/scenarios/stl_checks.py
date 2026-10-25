"""Strict, read-only binary STL checks using the Python standard library.

STL contains no unit declaration.  These exports are interpreted numerically as
millimetres.  All epsilons address floating point reconstruction; they are NOT
manufacturing tolerances or proof that a printed part fits.
"""
from collections import defaultdict
import hashlib
import math
from pathlib import Path
import struct


DIMENSION_EPS_MM = 1e-4
WELD_EPS_MM = 1e-5
AREA_EPS_MM2 = 1e-12
VOLUME_REL_EPS = 1e-5
HOLE_X_MM = (-35.0, -21.0, -7.0, 7.0, 21.0, 35.0)
TRIAL_CLEARANCES_MM = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
FACET = struct.Struct("<12fH")


def _require(condition, message):
    if not condition:
        raise ValueError("STL validation: " + message)


def _close(a, b, eps=DIMENSION_EPS_MM):
    return math.isclose(a, b, rel_tol=0.0, abs_tol=eps)


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _length(a):
    return math.sqrt(_dot(a, a))


def _round(value):
    return round(float(value), 7)


def _bounds(points):
    return {"min": [min(p[a] for p in points) for a in range(3)],
            "max": [max(p[a] for p in points) for a in range(3)]}


def _components(indices, adjacency):
    pending, result = set(indices), []
    while pending:
        seed = pending.pop()
        component, stack = {seed}, [seed]
        while stack:
            current = stack.pop()
            neighbours = pending.intersection(adjacency[current])
            pending.difference_update(neighbours)
            component.update(neighbours)
            stack.extend(neighbours)
        result.append(component)
    return result


def read_stl(path):
    """Parse binary STL strictly and return geometry plus measured topology.

    Open/unoriented geometry is reported here and rejected by validate_export.
    Invalid lengths, nonfinite fields and degenerate triangles always raise.
    Header text, including an optional leading ``solid``, does not select ASCII.
    """
    path = Path(path).resolve()
    data = path.read_bytes()
    _require(len(data) >= 84, "binary STL header/count is truncated")
    count = struct.unpack_from("<I", data, 80)[0]
    _require(count > 0, "empty STL")
    _require(len(data) == 84 + count * FACET.size,
             "binary STL length/count mismatch (truncation or trailing bytes)")
    vertices, triangles, buckets = [], [], defaultdict(list)
    nonzero_attributes = 0

    def weld(point):
        cell = tuple(math.floor(c / WELD_EPS_MM) for c in point)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for index in buckets.get((cell[0] + dx, cell[1] + dy, cell[2] + dz), ()):
                        if _length(_sub(point, vertices[index])) <= WELD_EPS_MM:
                            return index
        index = len(vertices)
        vertices.append(point)
        buckets[cell].append(index)
        return index

    for number in range(count):
        values = FACET.unpack_from(data, 84 + number * FACET.size)
        _require(all(math.isfinite(v) for v in values[:12]),
                 "nonfinite normal or vertex in triangle %d" % number)
        raw = (values[3:6], values[6:9], values[9:12])
        _require(_length(_cross(_sub(raw[1], raw[0]), _sub(raw[2], raw[0]))) / 2.0 > AREA_EPS_MM2,
                 "degenerate triangle %d" % number)
        triangle = tuple(weld(point) for point in raw)
        _require(len(set(triangle)) == 3, "triangle %d collapses after numeric coordinate welding" % number)
        a, b, c = (vertices[i] for i in triangle)
        _require(_length(_cross(_sub(b, a), _sub(c, a))) / 2.0 > AREA_EPS_MM2,
                 "triangle %d is degenerate after coordinate welding" % number)
        triangles.append(triangle)
        nonzero_attributes += bool(values[12])

    edges = defaultdict(list)
    adjacency = [set() for _ in triangles]
    incident = [set() for _ in vertices]
    for face, triangle in enumerate(triangles):
        for vertex in triangle:
            incident[vertex].add(face)
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[min(a, b), max(a, b)].append((face, a, b))
    non_manifold = sum(len(faces) != 2 for faces in edges.values())
    inconsistent = 0
    for faces in edges.values():
        indices = [face[0] for face in faces]
        for face in indices:
            adjacency[face].update(other for other in indices if other != face)
        if len(faces) == 2 and faces[0][1:] != tuple(reversed(faces[1][1:])):
            inconsistent += 1
    shells = _components(range(len(triangles)), adjacency)
    vertex_link_failures = sum(len(_components(faces, adjacency)) != 1 for faces in incident)
    chi = len(vertices) - len(edges) + len(triangles)
    genus_numerator = 2 * len(shells) - chi
    genus = (genus_numerator // 2 if non_manifold == 0 and vertex_link_failures == 0 and
             inconsistent == 0 and genus_numerator >= 0 and genus_numerator % 2 == 0 else None)
    volume = math.fsum(_dot(vertices[a], _cross(vertices[b], vertices[c])) / 6.0
                       for a, b, c in triangles)
    bounds = _bounds(vertices)
    return {
        "format": "binary_stl", "stl_path": str(path), "stl_sha256": hashlib.sha256(data).hexdigest(),
        "byte_size": len(data), "triangle_count": count, "vertex_count": len(vertices),
        "edge_count": len(edges), "bounds_mm": bounds,
        "dimensions_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)],
        "non_manifold_edges": non_manifold, "inconsistent_winding_edges": inconsistent,
        "non_manifold_vertex_links": vertex_link_failures, "connected_shells": len(shells),
        "euler_characteristic": chi, "genus": genus, "signed_volume_mm3": volume, "volume_mm3": volume,
        "nonzero_attribute_fields": nonzero_attributes,
        "unit_interpretation": "STL has no units; numeric coordinates are interpreted as millimetres for this export",
        "vertices": vertices, "triangles": triangles,
    }


def _triangle_geometry(mesh):
    points, normals, areas = [], [], []
    for triangle in mesh["triangles"]:
        pts = tuple(mesh["vertices"][i] for i in triangle)
        normal = _cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0]))
        magnitude = _length(normal)
        points.append(pts)
        normals.append(tuple(v / magnitude for v in normal))
        areas.append(magnitude / 2.0)
    return points, normals, areas


def _vertical_intersections(points, x, y):
    """Z intersections of an infinite vertical ray, deduplicated at seams."""
    values = []
    for a, b, c in points:
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) <= AREA_EPS_MM2:
            continue
        u = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / denominator
        v = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / denominator
        w = 1.0 - u - v
        if min(u, v, w) >= -1e-9:
            z = u * a[2] + v * b[2] + w * c[2]
            if not any(_close(z, old) for old in values):
                values.append(z)
    return sorted(values)


def _plane_groups(indices, points, axis):
    groups = []
    for index in indices:
        value = math.fsum(point[axis] for point in points[index]) / 3.0
        _require(all(_close(point[axis], value) for point in points[index]), "inner wall is not planar")
        for group in groups:
            if _close(value, group["plane_mm"]):
                group["indices"].append(index)
                break
        else:
            groups.append({"plane_mm": value, "indices": [index]})
    return sorted(groups, key=lambda group: group["plane_mm"])


def _plate_features(mesh):
    points, normals, areas = _triangle_geometry(mesh)
    holes = []
    for number, (centre_x, clearance) in enumerate(zip(HOLE_X_MM, TRIAL_CLEARANCES_MM), 1):
        expected = 10.0 + clearance
        roi = [i for i, pts in enumerate(points)
               if all(abs(p[0] - centre_x) <= 6.2 and abs(p[1] - 2.0) <= 6.2 for p in pts)]
        wall_evidence, axes = [], []
        for axis in (0, 1):
            axial = [i for i in roi if abs(normals[i][axis]) >= 1.0 - 1e-6]
            groups = _plane_groups(axial, points, axis)
            _require(len(groups) == 2, "hole %d does not have two actual inner-wall planes on axis %d" % (number, axis))
            axes.append([group["plane_mm"] for group in groups])
            for group in groups:
                bounds = _bounds([p for i in group["indices"] for p in points[i]])
                area = math.fsum(areas[i] for i in group["indices"])
                _require(_close(bounds["min"][2], -2.0) and _close(bounds["max"][2], 2.0),
                         "hole %d wall does not span the full plate thickness" % number)
                _require(math.isclose(area, expected * 4.0, rel_tol=VOLUME_REL_EPS, abs_tol=DIMENSION_EPS_MM),
                         "hole %d wall area differs from a full square wall" % number)
                wall_evidence.append({"axis": "XY"[axis], "plane_mm": group["plane_mm"],
                                      "bounds_mm": bounds, "area_mm2": area,
                                      "triangle_count": len(group["indices"])})
        width, height = axes[0][1] - axes[0][0], axes[1][1] - axes[1][0]
        _require(_close(width, expected) and _close(height, expected), "hole %d width/height mismatch" % number)
        _require(_close(sum(axes[0]) / 2.0, centre_x) and _close(sum(axes[1]) / 2.0, 2.0),
                 "hole %d centre mismatch" % number)
        intersections = _vertical_intersections(points, centre_x, 2.0)
        _require(not intersections, "hole %d centre ray is obstructed" % number)
        holes.append({"number": number, "centre_mm": [centre_x, 2.0],
                      "width_mm": width, "height_mm": height,
                      "total_clearance_x_mm": width - 10.0, "total_clearance_y_mm": height - 10.0,
                      "wall_planes": wall_evidence, "vertical_ray_z_hits_mm": intersections})

    adjacency = [set() for _ in points]
    edges = defaultdict(list)
    floor_indices = [i for i, pts in enumerate(points) if normals[i][2] >= 1.0 - 1e-6 and
                     all(_close(point[2], 1.2) for point in pts)]
    for i in floor_indices:
        triangle = mesh["triangles"][i]
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[min(a, b), max(a, b)].append(i)
    for linked in edges.values():
        for i in linked:
            adjacency[i].update(j for j in linked if j != i)
    floors = _components(floor_indices, adjacency)
    _require(len(floors) == 21, "expected 21 separate blind-marker floor patches")
    patches = []
    for component in floors:
        bounds = _bounds([p for i in component for p in points[i]])
        _require(all(_close(bounds["max"][a] - bounds["min"][a], 1.2) for a in (0, 1)),
                 "blind marker diameter differs from 1.2 mm")
        centre = [(bounds["min"][a] + bounds["max"][a]) / 2.0 for a in (0, 1)]
        boundary_vertices = {v for edge, linked in edges.items()
                             if len(linked) == 1 and linked[0] in component for v in edge}
        _require(len(boundary_vertices) >= 8 and all(
            _close(math.hypot(mesh["vertices"][v][0] - centre[0],
                              mesh["vertices"][v][1] - centre[1]), 0.6)
            for v in boundary_vertices), "blind marker floor boundary is not a radius 0.6 mm circle polygon")
        patches.append({"centre_mm": centre,
                        "bounds_mm": bounds, "area_mm2": math.fsum(areas[i] for i in component),
                        "triangle_count": len(component), "boundary_vertex_count": len(boundary_vertices)})
    markers, assigned = [], set()
    for number, centre_x in enumerate(HOLE_X_MM, 1):
        row = []
        for j in range(number):
            x, y = centre_x + (j - (number - 1) / 2.0) * 1.6, -8.5
            matches = [i for i, patch in enumerate(patches)
                       if _close(patch["centre_mm"][0], x) and _close(patch["centre_mm"][1], y)]
            _require(len(matches) == 1 and matches[0] not in assigned, "blind marker centre/count mismatch")
            assigned.add(matches[0])
            intersections = _vertical_intersections(points, x, y)
            _require(len(intersections) == 2 and _close(intersections[0], -2.0) and _close(intersections[1], 1.2),
                     "blind marker floor/bottom ray mismatch")
            controls = [_vertical_intersections(points, x, control_y) for control_y in (y - 0.9, y + 0.9)]
            _require(all(len(hits) == 2 and _close(hits[0], -2.0) and _close(hits[1], 2.0) for hits in controls),
                     "solid top surface beside marker is missing")
            row.append({"centre_mm": [x, y], "z_ray_hits_mm": intersections,
                        "solid_control_z_hits_mm": controls, "floor_patch": patches[matches[0]]})
        markers.append({"hole_number": number, "count": len(row), "points": row})
    _require(len(assigned) == 21, "unassigned marker floor")
    expected_volume = (96.0 * 26.0 * 4.0 - sum(h["width_mm"] * h["height_mm"] * 4.0 for h in holes) -
                       sum(patch["area_mm2"] for patch in patches) * 0.8)
    _require(math.isclose(mesh["volume_mm3"], expected_volume, rel_tol=VOLUME_REL_EPS,
                         abs_tol=DIMENSION_EPS_MM), "plate volume does not match measured holes/recesses")
    return {"measured_hole_widths_mm": [[_round(h["width_mm"]), _round(h["height_mm"])] for h in holes],
            "through_holes": len(holes), "holes": holes,
            "trial_total_clearances_mm": list(TRIAL_CLEARANCES_MM),
            "marker_counts": [row["count"] for row in markers], "marker_total": 21,
            "markers": markers, "expected_volume_from_measured_stl_mm3": expected_volume}


def validate_export(path, kind, expected_source_metadata=None):
    """Validate the pin/plate STL independently of the export UI or file name.

    ``expected_source_metadata`` can be the source Blender verification dict.
    This compares measured volume, dimensions and (for plate) six XY hole pairs.
    """
    aliases = {"pin": "pin", "fit_pin": "pin", "plate": "plate", "hole_plate": "plate"}
    _require(kind in aliases, "unknown expected export kind: %r" % kind)
    kind = aliases[kind]
    mesh = read_stl(path)
    _require(mesh["non_manifold_edges"] == 0, "mesh is not closed: every edge must belong to exactly two triangles")
    _require(mesh["non_manifold_vertex_links"] == 0, "non-manifold vertex link")
    _require(mesh["inconsistent_winding_edges"] == 0, "inconsistent adjacent triangle winding")
    _require(mesh["connected_shells"] == 1, "expected one connected shell")
    _require(mesh["signed_volume_mm3"] > 0, "signed volume must be positive")
    expected_dimensions = (10.0, 10.0, 8.0) if kind == "pin" else (96.0, 26.0, 4.0)
    expected_genus = 0 if kind == "pin" else 6
    _require(all(_close(value, expected) for value, expected in zip(mesh["dimensions_mm"], expected_dimensions)),
             "dimensions/axis order do not match the expected %s" % kind)
    _require(mesh["genus"] == expected_genus, "genus does not match the expected %s" % kind)
    result = {key: value for key, value in mesh.items() if key not in ("vertices", "triangles")}
    if kind == "pin":
        _require(math.isclose(mesh["volume_mm3"], 800.0, rel_tol=VOLUME_REL_EPS,
                             abs_tol=DIMENSION_EPS_MM), "pin volume is not 800 mm3")
    else:
        _require(all(_close(value, target) for value, target in zip(mesh["bounds_mm"]["min"], (-48, -13, -2))) and
                 all(_close(value, target) for value, target in zip(mesh["bounds_mm"]["max"], (48, 13, 2))),
                 "plate world-space bounds differ from source")
        result.update(_plate_features(mesh))
    compared = []
    if expected_source_metadata is not None:
        _require(isinstance(expected_source_metadata, dict), "expected_source_metadata must be a dict")
        _require(expected_source_metadata.get("passed") is not False, "source verification did not pass")
        source_volume = expected_source_metadata.get("volume_mm3", expected_source_metadata.get("signed_volume_mm3"))
        if source_volume is not None:
            _require(math.isfinite(source_volume) and math.isclose(mesh["volume_mm3"], source_volume,
                     rel_tol=VOLUME_REL_EPS, abs_tol=DIMENSION_EPS_MM), "STL/source volume mismatch")
            compared.append("volume_mm3")
        source_dimensions = expected_source_metadata.get("board_dimensions_mm" if kind == "plate" else "dimensions_mm")
        if source_dimensions is not None:
            _require(len(source_dimensions) == 3 and all(_close(a, b) for a, b in zip(mesh["dimensions_mm"], source_dimensions)),
                     "STL/source dimensions mismatch")
            compared.append("dimensions_mm")
        if kind == "plate":
            source_widths = expected_source_metadata.get("measured_hole_widths_mm")
            if source_widths is not None:
                _require(len(source_widths) == 6 and all(len(pair) == 2 for pair in source_widths) and
                         all(_close(a, b) for actual, expected in zip(result["measured_hole_widths_mm"], source_widths)
                             for a, b in zip(actual, expected)), "STL/source actual hole widths mismatch")
                compared.append("measured_hole_widths_mm")
            if "marker_counts" in expected_source_metadata:
                _require(expected_source_metadata["marker_counts"] == result["marker_counts"], "STL/source marker counts mismatch")
                compared.append("marker_counts")
    result.update(passed=True, kind=kind, source_metadata_compared=compared,
                  printed=False, fit_tested=False, qualified_clearance_mm=None,
                  numericComparison={"purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                     "dimensionsAbsMm": DIMENSION_EPS_MM, "coordinateWeldMm": WELD_EPS_MM,
                                     "volumeRelative": VOLUME_REL_EPS})
    return result
