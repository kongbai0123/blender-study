"""Read-only 05-05 source-body, trial lid and nominal assembly measurements.

The pure mesh functions accept world-space millimetre vertices/triangles and
can be tested without Blender. Blender wrappers only copy evaluated loop
triangles; they do not run modelling operators or modify source geometry.
Numeric epsilons are reconstruction thresholds, never manufacturing tolerances.
"""
from collections import defaultdict
import math


DIMENSION_EPS_MM = 1e-4
VOLUME_REL_EPS = 1e-5


def _require(condition, message):
    if not condition:
        raise ValueError("05-05 geometry validation: " + message)


def _close(a, b, eps=DIMENSION_EPS_MM):
    return math.isclose(a, b, rel_tol=0, abs_tol=eps)


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _round(value):
    return round(float(value), 7)


def _bounds(points):
    return {"min": [min(p[a] for p in points) for a in range(3)],
            "max": [max(p[a] for p in points) for a in range(3)]}


def _components(indices, adjacency):
    pending, result = set(indices), []
    while pending:
        seed = pending.pop()
        stack, component = [seed], {seed}
        while stack:
            neighbours = pending.intersection(adjacency[stack.pop()])
            pending.difference_update(neighbours)
            component.update(neighbours)
            stack.extend(neighbours)
        result.append(component)
    return result


def _read_mesh(vertices, triangles):
    vertices = [tuple(map(float, vertex)) for vertex in vertices]
    triangles = [tuple(triangle) for triangle in triangles]
    _require(vertices and triangles, "empty mesh")
    _require(all(len(vertex) == 3 and all(math.isfinite(c) for c in vertex) for vertex in vertices),
             "nonfinite or invalid vertex")
    edges, incident = defaultdict(list), [set() for _ in vertices]
    points, normals, areas, contributions = [], [], [], []
    for number, triangle in enumerate(triangles):
        _require(len(triangle) == 3 and len(set(triangle)) == 3 and
                 all(isinstance(i, int) and 0 <= i < len(vertices) for i in triangle), "invalid triangle")
        pts = tuple(vertices[i] for i in triangle)
        cross = _cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0]))
        magnitude = math.sqrt(_dot(cross, cross))
        _require(magnitude > 1e-12, "degenerate triangle")
        points.append(pts)
        normals.append(tuple(c / magnitude for c in cross))
        areas.append(magnitude / 2)
        contributions.append(_dot(pts[0], _cross(pts[1], pts[2])) / 6)
        for vertex in triangle:
            incident[vertex].add(number)
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[min(a, b), max(a, b)].append((number, a, b))
    _require(all(incident), "unused/isolated vertex")
    adjacency = [set() for _ in triangles]
    for linked in edges.values():
        for face, a, b in linked:
            adjacency[face].update(other[0] for other in linked if other[0] != face)
    non_manifold = sum(len(linked) != 2 for linked in edges.values())
    inconsistent = sum(len(linked) == 2 and linked[0][1:] != tuple(reversed(linked[1][1:]))
                       for linked in edges.values())
    shells = _components(range(len(triangles)), adjacency)
    vertex_links = sum(len(_components(faces, adjacency)) != 1 for faces in incident)
    _require(non_manifold == 0 and vertex_links == 0, "mesh is not a closed manifold")
    _require(inconsistent == 0, "inconsistent triangle winding")
    _require(len(shells) == 1, "mesh is not one connected shell")
    chi = len(vertices) - len(edges) + len(triangles)
    _require(chi == 2, "expected a single closed genus-0 material shell")
    volume = math.fsum(contributions)
    _require(volume > 0 and math.isfinite(volume), "signed volume is not positive")
    bounds = _bounds(vertices)
    return {"points": points, "normals": normals, "areas": areas,
            "bounds_mm": bounds,
            "dimensions_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)],
            "volume_mm3": volume, "non_manifold_edges": non_manifold,
            "non_manifold_vertex_links": vertex_links, "inconsistent_winding_edges": inconsistent,
            "connected_shells": 1, "euler_characteristic": chi, "genus": 0,
            "mesh_counts": {"vertices": len(vertices), "edges": len(edges), "faces": len(triangles),
                            "triangles": len(triangles), "representation": "evaluated loop-triangulated mesh"}}


def _planes(mesh):
    axes = [[], [], []]
    for points, normal, area in zip(mesh["points"], mesh["normals"], mesh["areas"]):
        axis = max(range(3), key=lambda a: abs(normal[a]))
        _require(abs(normal[axis]) >= 1 - 1e-6, "non-axis-aligned final face")
        coordinate = math.fsum(point[axis] for point in points) / 3
        _require(all(_close(point[axis], coordinate) for point in points), "nonplanar face")
        for group in axes[axis]:
            if _close(group["coordinate_mm"], coordinate):
                group["points"].extend(points)
                group["area_mm2"] += area
                break
        else:
            axes[axis].append({"coordinate_mm": coordinate, "area_mm2": area, "points": list(points)})
    for axis in axes:
        axis.sort(key=lambda group: group["coordinate_mm"])
        for group in axis:
            group["bounds_mm"] = _bounds(group.pop("points"))
    return axes


def _check_planes(axes, expected):
    for axis, design in enumerate(expected):
        _require(len(axes[axis]) == len(design), "unexpected %s face-plane count" % "XYZ"[axis])
        for measured, (coordinate, area) in zip(axes[axis], design):
            _require(_close(measured["coordinate_mm"], coordinate), "actual face-plane position differs from design")
            _require(math.isclose(measured["area_mm2"], area, rel_tol=VOLUME_REL_EPS,
                                 abs_tol=DIMENSION_EPS_MM), "actual face-plane area differs from design")


def _vertical_hits(points, x, y):
    values = []
    for a, b, c in points:
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) <= 1e-12:
            continue
        u = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / denominator
        v = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / denominator
        w = 1 - u - v
        if min(u, v, w) >= -1e-9:
            z = u * a[2] + v * b[2] + w * c[2]
            if not any(_close(z, old) for old in values):
                values.append(z)
    return sorted(values)


def _ray_evidence(mesh, probes):
    result = []
    for label, x, y, expected in probes:
        hits = _vertical_hits(mesh["points"], x, y)
        _require(len(hits) == len(expected) and all(_close(a, b) for a, b in zip(hits, expected)),
                 "vertical ray '%s' differs from expected material intervals: %r" % (label, hits))
        result.append({"label": label, "xy_mm": [x, y], "z_hits_mm": hits})
    return result


def _public(mesh):
    result = {key: value for key, value in mesh.items() if key not in ("points", "normals", "areas")}
    result.update(passed=True, printed=False, fit_tested=False, physical_interference=None,
                  qualified_clearance_mm=None,
                  numericComparison={"purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                     "dimensionsAbsMm": DIMENSION_EPS_MM, "volumeRelative": VOLUME_REL_EPS})
    return result


def validate_body_mesh(vertices, triangles):
    """Measure the actual source box, not a presumed 60x40x30 bounding box."""
    mesh = _read_mesh(vertices, triangles)
    axes = _planes(mesh)
    _check_planes(axes, [
        [(-30, 1200), (-28, 1008), (28, 1008), (30, 1200)],
        [(-20, 1800), (-18, 1568), (18, 1568), (20, 1800)],
        [(-15, 2400), (-13, 2016), (15, 384)],
    ])
    _require(math.isclose(mesh["volume_mm3"], 15552.0, rel_tol=VOLUME_REL_EPS,
                         abs_tol=DIMENSION_EPS_MM), "source body volume mismatch")
    rays = _ray_evidence(mesh, [("cavity centre", 0, 0, [-15, -13]),
                                ("negative X rim", -29, 0, [-15, 15]),
                                ("positive X rim", 29, 0, [-15, 15]),
                                ("negative Y rim", 0, -19, [-15, 15]),
                                ("positive Y rim", 0, 19, [-15, 15]),
                                ("near cavity corner", 27, 17, [-15, -13])])
    cavity = {"min": [axes[0][1]["coordinate_mm"], axes[1][1]["coordinate_mm"], axes[2][1]["coordinate_mm"]],
              "max": [axes[0][2]["coordinate_mm"], axes[1][2]["coordinate_mm"], axes[2][2]["coordinate_mm"]]}
    dimensions = [cavity["max"][a] - cavity["min"][a] for a in range(3)]
    result = _public(mesh)
    result.update(kind="box_body", outer_dimensions_mm=mesh["dimensions_mm"],
                  cavity_bounds_mm=cavity, cavity_dimensions_mm=dimensions,
                  wall_thicknesses_mm=[cavity["min"][0] - mesh["bounds_mm"]["min"][0],
                                       mesh["bounds_mm"]["max"][0] - cavity["max"][0],
                                       cavity["min"][1] - mesh["bounds_mm"]["min"][1],
                                       mesh["bounds_mm"]["max"][1] - cavity["max"][1]],
                  floor_thickness_mm=cavity["min"][2] - mesh["bounds_mm"]["min"][2],
                  rim_z_mm=cavity["max"][2], actual_face_planes={axis: groups for axis, groups in zip("XYZ", axes)},
                  vertical_rays=rays, measurement_scope="actual source body mesh; no physical fit conclusion")
    return result


def _assembly(lid, body):
    _require(isinstance(body, dict) and body.get("passed") is True and body.get("kind") == "box_body",
             "body metadata must be an actual successful source-body measurement")
    cavity = body["cavity_bounds_mm"]
    ring = lid["ring_outer_bounds_mm"]
    plate_bottom, ring_bottom = lid["plate_z_mm"][0], lid["ring_z_mm"][0]
    gaps = [ring["min"][0] - cavity["min"][0], cavity["max"][0] - ring["max"][0],
            ring["min"][1] - cavity["min"][1], cavity["max"][1] - ring["max"][1]]
    _require(all(_close(gap, 0.2) for gap in gaps), "nominal per-side clearance differs from 0.2 mm trial")
    _require(_close(plate_bottom, body["rim_z_mm"]), "lid underside does not meet the body rim")
    engagement = body["rim_z_mm"] - ring_bottom
    _require(_close(engagement, 4.0) and engagement < body["cavity_dimensions_mm"][2] and
             ring_bottom > cavity["min"][2], "lip engagement exceeds the measured cavity depth")
    return {"scope": "nominal mesh placement only; physical fit remains untested",
            "geometric_nonintersection": True, "interior_volume_overlap_mm3": 0.0,
            "per_side_order": ["negative_x", "positive_x", "negative_y", "positive_y"],
            "per_side_clearances_mm": gaps, "total_clearances_mm": [gaps[0] + gaps[1], gaps[2] + gaps[3]],
            "trial_total_clearance_mm": 0.4, "engagement_mm": engagement,
            "cavity_depth_mm": body["cavity_dimensions_mm"][2],
            "floor_reserve_mm": ring_bottom - cavity["min"][2],
            "rim_contact_z_mm": body["rim_z_mm"], "physical_interference": None,
            "printed": False, "fit_tested": False, "qualified_clearance_mm": None}


def validate_lid_mesh(vertices, triangles, body_metadata=None):
    """Measure the final integrated cap and annular lip, rejecting solid plugs."""
    mesh = _read_mesh(vertices, triangles)
    axes = _planes(mesh)
    ring_area = 55.6 * 35.6 - 51.6 * 31.6
    _check_planes(axes, [
        [(-30, 80), (-27.8, 142.4), (-25.8, 126.4), (25.8, 126.4), (27.8, 142.4), (30, 80)],
        [(-20, 120), (-17.8, 222.4), (-15.8, 206.4), (15.8, 206.4), (17.8, 222.4), (20, 120)],
        [(11, ring_area), (15, 2400 - ring_area), (17, 2400)],
    ])
    expected_volume = 60 * 40 * 2 + ring_area * 4
    _require(math.isclose(mesh["volume_mm3"], expected_volume, rel_tol=VOLUME_REL_EPS,
                         abs_tol=DIMENSION_EPS_MM), "lid volume mismatch")
    rays = _ray_evidence(mesh, [("covered hollow centre", 0, 0, [15, 17]),
                                ("negative X lip", -26.8, 0, [11, 17]),
                                ("positive X lip", 26.8, 0, [11, 17]),
                                ("negative Y lip", 0, -16.8, [11, 17]),
                                ("positive Y lip", 0, 16.8, [11, 17]),
                                ("negative X outer ledge", -29, 0, [15, 17]),
                                ("positive X outer ledge", 29, 0, [15, 17]),
                                ("negative Y outer ledge", 0, -19, [15, 17]),
                                ("positive Y outer ledge", 0, 19, [15, 17]),
                                ("hollow interior corner", 24, 14, [15, 17])])
    x, y, z = axes
    outer = {"min": [x[1]["coordinate_mm"], y[1]["coordinate_mm"], z[0]["coordinate_mm"]],
             "max": [x[4]["coordinate_mm"], y[4]["coordinate_mm"], z[1]["coordinate_mm"]]}
    inner = {"min": [x[2]["coordinate_mm"], y[2]["coordinate_mm"], z[0]["coordinate_mm"]],
             "max": [x[3]["coordinate_mm"], y[3]["coordinate_mm"], z[1]["coordinate_mm"]]}
    result = _public(mesh)
    result.update(kind="lid", plate_dimensions_mm=[mesh["dimensions_mm"][0], mesh["dimensions_mm"][1],
                                                   z[2]["coordinate_mm"] - z[1]["coordinate_mm"]],
                  plate_z_mm=[z[1]["coordinate_mm"], z[2]["coordinate_mm"]],
                  plate_thickness_mm=z[2]["coordinate_mm"] - z[1]["coordinate_mm"],
                  ring_outer_bounds_mm=outer, ring_inner_bounds_mm=inner,
                  ring_outer_mm=[outer["max"][a] - outer["min"][a] for a in (0, 1)],
                  ring_inner_mm=[inner["max"][a] - inner["min"][a] for a in (0, 1)],
                  ring_wall_thicknesses_mm=[inner["min"][0] - outer["min"][0], outer["max"][0] - inner["max"][0],
                                            inner["min"][1] - outer["min"][1], outer["max"][1] - inner["max"][1]],
                  ring_z_mm=[z[0]["coordinate_mm"], z[1]["coordinate_mm"]],
                  ring_depth_mm=z[1]["coordinate_mm"] - z[0]["coordinate_mm"],
                  engagement_mm=z[1]["coordinate_mm"] - z[0]["coordinate_mm"],
                  ring_wall_mm=(inner["min"][0] - outer["min"][0] + outer["max"][0] - inner["max"][0] +
                                inner["min"][1] - outer["min"][1] + outer["max"][1] - inner["max"][1]) / 4,
                  expected_volume_mm3=expected_volume,
                  actual_face_planes={axis: groups for axis, groups in zip("XYZ", axes)},
                  vertical_rays=rays, trial_total_clearance_mm=0.4, trial_per_side_clearance_mm=0.2,
                  trial_status="experimental_geometry_only",
                  measurement_scope="nominal lid and ring geometry only; no qualified printed clearance")
    result["assembly"] = _assembly(result, body_metadata) if body_metadata is not None else None
    return result


def _object_mesh(obj):
    import bpy
    _require(obj is not None and obj.type == "MESH", "object is not a mesh")
    _require(all(_close(value, 1.0) for value in obj.scale), "object Scale is not 1 / 1 / 1")
    units = bpy.context.scene.unit_settings
    _require(units.system == "METRIC" and units.length_unit == "MILLIMETERS" and
             math.isclose(units.scale_length, 0.001, rel_tol=0, abs_tol=1e-9),
             "scene units are not Metric / Millimeters / 0.001")
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        factor = units.scale_length * 1000
        vertices = [tuple((evaluated.matrix_world @ vertex.co) * factor) for vertex in mesh.vertices]
        triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
        return vertices, triangles, {"object_name": obj.name, "scale": list(obj.scale),
                                     "unit_scale": units.scale_length, "length_unit": units.length_unit,
                                     "measurement_source": "evaluated final mesh loop triangles in world-space millimetres"}
    finally:
        evaluated.to_mesh_clear()


def read_body_and_validate(obj):
    vertices, triangles, metadata = _object_mesh(obj)
    result = validate_body_mesh(vertices, triangles)
    result.update(metadata)
    return result


def read_lid_and_validate(obj, body_obj_or_metadata=None):
    body = body_obj_or_metadata
    if body is not None and not isinstance(body, dict):
        body = read_body_and_validate(body)
    vertices, triangles, metadata = _object_mesh(obj)
    result = validate_lid_mesh(vertices, triangles, body)
    result.update(metadata)
    return result
