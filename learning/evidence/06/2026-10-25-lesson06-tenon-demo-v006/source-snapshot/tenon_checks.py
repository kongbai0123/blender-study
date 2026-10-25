"""Read-only 06-01 polygonal locating-pin/hole and nominal assembly checks.

Pure mesh functions use world-space millimetres and the standard library only.
Blender access is confined to read_mesh_data and its wrappers. A union result
cannot reveal its deleted buried tool bottom; that claim needs the separately
measured construction pin. Numeric epsilons are not manufacturing tolerances.
"""
from collections import defaultdict
import math

from lid_checks import (_assembly, _bounds, _check_planes, _components, _cross,
                        _dot, _object_mesh, _planes, _sub, _vertical_hits)


EPS_MM = 1e-4
VOLUME_REL_EPS = 1e-5
SEGMENTS = 32
CENTRE = (23.0, 13.0)
STEP = 2 * math.pi / SEGMENTS


def _require(condition, message):
    if not condition:
        raise ValueError("06-01 geometry validation: " + message)


def _close(a, b):
    return math.isclose(a, b, rel_tol=0.0, abs_tol=EPS_MM)


def _mesh(vertices, triangles, genus):
    vertices = [tuple(map(float, point)) for point in vertices]
    triangles = [tuple(face) for face in triangles]
    _require(vertices and triangles, "empty mesh")
    _require(all(len(p) == 3 and all(math.isfinite(c) for c in p) for p in vertices), "invalid/nonfinite vertex")
    points, normals, areas, volumes = [], [], [], []
    edges, incident = defaultdict(list), [set() for _ in vertices]
    for number, triangle in enumerate(triangles):
        _require(len(triangle) == 3 and len(set(triangle)) == 3 and
                 all(isinstance(i, int) and 0 <= i < len(vertices) for i in triangle), "invalid triangle")
        pts = tuple(vertices[i] for i in triangle)
        cross = _cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0]))
        length = math.sqrt(_dot(cross, cross))
        _require(length > 1e-12, "degenerate triangle")
        points.append(pts)
        normals.append(tuple(c / length for c in cross))
        areas.append(length / 2)
        volumes.append(_dot(pts[0], _cross(pts[1], pts[2])) / 6)
        for vertex in triangle:
            incident[vertex].add(number)
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[min(a, b), max(a, b)].append((number, a, b))
    _require(all(incident), "isolated/unused vertex")
    adjacency = [set() for _ in triangles]
    for linked in edges.values():
        for face, a, b in linked:
            adjacency[face].update(other[0] for other in linked if other[0] != face)
    non_manifold = sum(len(linked) != 2 for linked in edges.values())
    inconsistent = sum(len(linked) == 2 and linked[0][1:] != tuple(reversed(linked[1][1:])) for linked in edges.values())
    vertex_links = sum(len(_components(faces, adjacency)) != 1 for faces in incident)
    shells = len(_components(range(len(triangles)), adjacency))
    chi = len(vertices) - len(edges) + len(triangles)
    _require(non_manifold == 0 and vertex_links == 0, "mesh is not a closed manifold")
    _require(inconsistent == 0, "inconsistent triangle winding")
    _require(shells == 1, "mesh is not one connected shell")
    _require(chi == 2 - 2 * genus, "incorrect Euler characteristic/genus")
    volume = math.fsum(volumes)
    _require(math.isfinite(volume) and volume > 0, "nonpositive signed volume")
    bounds = _bounds(vertices)
    return {"vertices": vertices, "triangles": triangles, "points": points, "normals": normals, "areas": areas,
            "bounds_mm": bounds, "dimensions_mm": [bounds["max"][a] - bounds["min"][a] for a in range(3)],
            "volume_mm3": volume, "non_manifold_edges": non_manifold,
            "non_manifold_vertex_links": vertex_links, "inconsistent_winding_edges": inconsistent,
            "connected_shells": shells, "euler_characteristic": chi, "genus": genus,
            "mesh_counts": {"vertices": len(vertices), "edges": len(edges), "faces": len(triangles),
                            "triangles": len(triangles), "representation": "world-space triangulated mesh"}}


def _public(mesh):
    result = {key: value for key, value in mesh.items()
              if key not in ("vertices", "triangles", "points", "normals", "areas")}
    result.update(passed=True, printed=False, fit_tested=False, physical_measurements=None,
                  fit_results=None, physical_interference=None, qualified_clearance_mm=None,
                  trial_status="experimental_geometry_only",
                  numericComparison={"purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                     "dimensionsAbsMm": EPS_MM, "volumeRelative": VOLUME_REL_EPS})
    return result


def _volume(actual, expected):
    _require(math.isclose(actual, expected, rel_tol=VOLUME_REL_EPS, abs_tol=EPS_MM), "signed volume differs from measured polygon/material geometry")


def _rays(mesh, probes):
    evidence = []
    for label, x, y, expected in probes:
        hits = _vertical_hits(mesh["points"], x, y)
        _require(len(hits) == len(expected) and all(_close(a, b) for a, b in zip(hits, expected)),
                 "vertical ray '%s' has wrong material intervals: %r" % (label, hits))
        evidence.append({"label": label, "xy_mm": [x, y], "z_hits_mm": hits})
    return evidence


def _boundary_corners(points):
    """Recover facet corners while retaining proof for every boundary sample.

    Exact Boolean may split an existing straight edge at a triangulation seam.
    This does not add a polygon direction. A monotone convex boundary removes
    only redundant samples, then *every* original point must still lie on a
    resulting boundary segment within the unchanged reconstruction threshold.
    An inward dent is therefore rejected instead of hidden by the convex hull.
    """
    unique = sorted(set(tuple(point) for point in points))
    _require(len(unique) >= SEGMENTS, "radial boundary must retain exactly 32 vertices/corners")

    def half(sequence):
        result = []
        for point in sequence:
            while len(result) >= 2:
                a, b = result[-2:]
                cross = ((b[0] - a[0]) * (point[1] - a[1]) -
                         (b[1] - a[1]) * (point[0] - a[0]))
                chord = math.hypot(point[0] - a[0], point[1] - a[1])
                if cross > EPS_MM * chord:
                    break
                result.pop()
            result.append(point)
        return result

    corners = half(unique)[:-1] + half(reversed(unique))[:-1]
    _require(len(corners) == SEGMENTS, "radial boundary must retain exactly 32 vertices/corners")
    for point in points:
        closest = math.inf
        for a, b in zip(corners, corners[1:] + corners[:1]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            fraction = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / (dx * dx + dy * dy)
            fraction = min(1.0, max(0.0, fraction))
            closest = min(closest, math.hypot(point[0] - a[0] - fraction * dx,
                                              point[1] - a[1] - fraction * dy))
        _require(closest <= EPS_MM, "non-collinear boundary sample is not on a recovered facet segment")
    return corners


def _polygon(points, radius):
    raw_points = list(points)
    points = _boundary_corners(raw_points)
    cx = math.fsum(p[0] for p in points) / SEGMENTS
    cy = math.fsum(p[1] for p in points) / SEGMENTS
    _require(_close(cx, CENTRE[0]) and _close(cy, CENTRE[1]), "radial boundary centre differs from (23,13)")
    ordered = sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx) % (2 * math.pi))
    angles = [math.atan2(p[1] - cy, p[0] - cx) % (2 * math.pi) for p in ordered]
    radii = [math.hypot(p[0] - cx, p[1] - cy) for p in ordered]
    _require(all(_close(r, radius) for r in radii), "actual circumradius differs from specification")
    _require(all(abs(((angles[(i + 1) % SEGMENTS] - angles[i]) % (2 * math.pi)) - STEP) <= 1e-4
                 for i in range(SEGMENTS)), "radial polygon is not regular/equiangular")
    planes, area_terms = [], []
    for a, b in zip(ordered, ordered[1:] + ordered[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        normal = [dy / length, -dx / length]
        offset = normal[0] * (a[0] - cx) + normal[1] * (a[1] - cy)
        _require(_close(offset, radius * math.cos(math.pi / SEGMENTS)), "incorrect radial facet plane")
        planes.append({"normal_xy": normal, "offset_mm": offset, "edge_length_mm": length,
                       "offset_origin_mm": [cx, cy]})
        area_terms.append((a[0] - cx) * (b[1] - cy) - (b[0] - cx) * (a[1] - cy))
    phase = angles[0] % STEP
    if min(phase, STEP - phase) < 1e-5:
        phase = 0.0
    widths = [planes[i]["offset_mm"] + planes[(i + SEGMENTS // 2) % SEGMENTS]["offset_mm"]
              for i in range(SEGMENTS // 2)]
    return {"segments": SEGMENTS, "centre_mm": [cx, cy],
            "boundary_sample_count": len(raw_points), "collinear_split_count": len(raw_points) - SEGMENTS,
            "raw_boundary_xy_mm": [list(p) for p in raw_points],
            "radius_mm": math.fsum(radii) / SEGMENTS, "nominal_diameter_mm": 2 * radius,
            "measured_circumdiameter_mm": 2 * math.fsum(radii) / SEGMENTS,
            "across_flats_diameter_mm": min(widths), "across_flats_diameters_mm": widths,
            "phase_angle_rad": phase, "area_mm2": math.fsum(area_terms) / 2,
            "vertices_xy_mm": [list(p) for p in ordered], "edge_planes": planes}


def _radial(mesh, radius, z_min, z_max, solid):
    indices = [i for i, pts in enumerate(mesh["points"])
               if abs(mesh["normals"][i][2]) <= 1e-6 and
               all(math.hypot(p[0] - CENTRE[0], p[1] - CENTRE[1]) <= radius + 0.25 and
                   z_min - EPS_MM <= p[2] <= z_max + EPS_MM for p in pts)]
    _require(indices, "no actual radial wall triangles")
    levels = []
    for z in (z_min, z_max):
        ids = {v for i in indices for v in mesh["triangles"][i] if _close(mesh["vertices"][v][2], z)}
        levels.append(_polygon([(mesh["vertices"][v][0], mesh["vertices"][v][1]) for v in ids], radius))
    lower, upper = levels
    _require(all(math.hypot(a[0] - b[0], a[1] - b[1]) <= EPS_MM
                 for a, b in zip(lower["vertices_xy_mm"], upper["vertices_xy_mm"])), "upper/lower polygon boundaries do not correspond")
    upper["boundary_levels"] = [
        {"z_mm": z, "boundary_sample_count": polygon["boundary_sample_count"],
         "corner_count": polygon["segments"], "collinear_split_count": polygon["collinear_split_count"],
         "raw_boundary_xy_mm": polygon["raw_boundary_xy_mm"]}
        for z, polygon in zip((z_min, z_max), levels)]
    groups = [[] for _ in upper["edge_planes"]]
    for i in indices:
        matches = []
        for number, plane in enumerate(upper["edge_planes"]):
            nx, ny = plane["normal_xy"]
            cx, cy = upper["centre_mm"]
            if all(_close(nx * (p[0] - cx) + ny * (p[1] - cy), plane["offset_mm"]) for p in mesh["points"][i]):
                matches.append(number)
        _require(len(matches) == 1, "radial side triangle does not lie on one polygon plane")
        plane = upper["edge_planes"][matches[0]]
        expected_sign = 1 if solid else -1
        orientation = mesh["normals"][i][0] * plane["normal_xy"][0] + mesh["normals"][i][1] * plane["normal_xy"][1]
        _require(expected_sign * orientation >= 1 - 1e-6, "radial wall orientation is incorrect")
        groups[matches[0]].append(i)
    walls = []
    for number, (plane, faces) in enumerate(zip(upper["edge_planes"], groups)):
        _require(faces, "missing polygon side wall")
        bounds = _bounds([p for i in faces for p in mesh["points"][i]])
        area = math.fsum(mesh["areas"][i] for i in faces)
        _require(_close(bounds["min"][2], z_min) and _close(bounds["max"][2], z_max), "radial wall does not span full height")
        _volume(area, plane["edge_length_mm"] * (z_max - z_min))
        walls.append({"number": number + 1, "normal_xy": plane["normal_xy"], "offset_mm": plane["offset_mm"],
                      "bounds_mm": bounds, "area_mm2": area, "triangle_count": len(faces)})
    return upper, walls, set(indices)


def _rectangular_planes(mesh, excluded):
    kept = [i for i in range(len(mesh["points"])) if i not in excluded]
    return _planes({key: [mesh[key][i] for i in kept] for key in ("points", "normals", "areas")})


def _source(source, kind):
    _require(isinstance(source, dict) and source.get("passed") is True and source.get("kind") == kind,
             "successful original %s measurement is required" % kind)
    expected_dims = [60, 40, 30] if kind == "box_body" else [60, 40, 6]
    dims = source.get("dimensions_mm", [])
    _require(len(dims) == 3 and all(_close(a, b) for a, b in zip(dims, expected_dims)), "incorrect original source dimensions")
    _volume(source.get("volume_mm3", math.nan), 15552 if kind == "box_body" else 6195.2)


def validate_tool_mesh(vertices, triangles, kind):
    _require(kind in ("pin", "hole_cutter"), "unknown construction tool kind")
    radius, z_min, z_max = (2.0, -13.5, 16.5) if kind == "pin" else (2.2, 11.0, 21.0)
    mesh = _mesh(vertices, triangles, 0)
    polygon, walls, excluded = _radial(mesh, radius, z_min, z_max, True)
    planes = _rectangular_planes(mesh, excluded)
    _check_planes(planes, [[], [], [(z_min, polygon["area_mm2"]), (z_max, polygon["area_mm2"])]])
    _volume(mesh["volume_mm3"], polygon["area_mm2"] * (z_max - z_min))
    rays = _rays(mesh, [("tool centre", *CENTRE, [z_min, z_max]),
                        ("inside tool", CENTRE[0] + radius * 0.5, CENTRE[1], [z_min, z_max]),
                        ("outside tool", CENTRE[0] + radius + 0.2, CENTRE[1], [])])
    result = _public(mesh)
    result.update(kind="cylinder_tool", tool_kind=kind, polygon=polygon, z_mm=[z_min, z_max],
                  height_mm=z_max - z_min,
                  location_mm=[polygon["centre_mm"][0], polygon["centre_mm"][1], (z_min + z_max) / 2],
                  radial_walls=walls, vertical_rays=rays,
                  measurement_scope="construction tool before Boolean; not inferred from the final union")
    return result


def validate_body_pin_mesh(vertices, triangles, source_body_metadata, construction_pin_metadata=None):
    _source(source_body_metadata, "box_body")
    mesh = _mesh(vertices, triangles, 0)
    polygon, walls, excluded = _radial(mesh, 2.0, -13.0, 16.5, True)
    axes = _rectangular_planes(mesh, excluded)
    area = polygon["area_mm2"]
    _check_planes(axes, [[(-30, 1200), (-28, 1008), (28, 1008), (30, 1200)],
                         [(-20, 1800), (-18, 1568), (18, 1568), (20, 1800)],
                         [(-15, 2400), (-13, 2016 - area), (15, 384), (16.5, area)]])
    _volume(mesh["volume_mm3"], 15552 + area * 29.5)
    rays = _rays(mesh, [("continuous body and pin centre", 23, 13, [-15, 16.5]),
                        ("continuous body and pin interior", 24, 13, [-15, 16.5]),
                        ("cavity floor beside pin", 26, 13, [-15, -13]),
                        ("cavity centre", 0, 0, [-15, -13]),
                        ("outer body rim", 29, 0, [-15, 15])])
    floor_overlap = None
    if construction_pin_metadata is not None:
        tool = construction_pin_metadata
        _require(isinstance(tool, dict) and tool.get("passed") is True and tool.get("tool_kind") == "pin",
                 "construction pin evidence must be a successful pin-tool measurement")
        _require(all(_close(a, b) for a, b in zip(tool.get("z_mm", []), [-13.5, 16.5])) and len(tool.get("z_mm", [])) == 2,
                 "incorrect construction pin Z range")
        old = tool.get("polygon", {})
        _require(old.get("segments") == 32 and _close(old.get("radius_mm", math.nan), 2.0), "incorrect construction pin polygon")
        old_points = old.get("vertices_xy_mm", [])
        _require(len(old_points) == 32 and all(math.hypot(a[0] - b[0], a[1] - b[1]) <= EPS_MM
                 for a, b in zip(old_points, polygon["vertices_xy_mm"])), "final pin boundary differs from measured construction pin")
        floor_overlap = -13.0 - tool["z_mm"][0]
    x, y, z = axes
    cavity = {"min": [x[1]["coordinate_mm"], y[1]["coordinate_mm"], z[1]["coordinate_mm"]],
              "max": [x[2]["coordinate_mm"], y[2]["coordinate_mm"], z[2]["coordinate_mm"]]}
    shell = dict(source_body_metadata)
    shell.update(cavity_bounds_mm=cavity,
                 cavity_dimensions_mm=[cavity["max"][a] - cavity["min"][a] for a in range(3)],
                 rim_z_mm=z[2]["coordinate_mm"], volume_mm3=mesh["volume_mm3"] - area * 29.5,
                 measurement_scope="original rectangular shell reconstructed from final union wall/floor/rim planes")
    result = _public(mesh)
    result.update(kind="body_with_locating_pin", source_shell_dimensions_mm=[60.0, 40.0, 30.0],
                  source_cavity_dimensions_mm=shell["cavity_dimensions_mm"], body_shell=shell,
                  source_body=source_body_metadata, construction_pin=construction_pin_metadata,
                  construction_floor_overlap_mm=floor_overlap,
                  pin={"polygon": polygon, "exposed_z_mm": [-13.0, 16.5], "exposed_height_mm": 29.5,
                       "tip_z_mm": 16.5, "radial_walls": walls},
                  actual_rectangular_planes={axis: groups for axis, groups in zip("XYZ", axes)}, vertical_rays=rays,
                  measurement_scope="final union mesh; buried tool bottom is absent and is not inferred")
    return result


def validate_lid_hole_mesh(vertices, triangles, source_lid_metadata):
    _source(source_lid_metadata, "lid")
    mesh = _mesh(vertices, triangles, 1)
    polygon, walls, excluded = _radial(mesh, 2.2, 15.0, 17.0, False)
    axes = _rectangular_planes(mesh, excluded)
    hole_area = polygon["area_mm2"]
    ring_area = 55.6 * 35.6 - 51.6 * 31.6
    _check_planes(axes, [
        [(-30, 80), (-27.8, 142.4), (-25.8, 126.4), (25.8, 126.4), (27.8, 142.4), (30, 80)],
        [(-20, 120), (-17.8, 222.4), (-15.8, 206.4), (15.8, 206.4), (17.8, 222.4), (20, 120)],
        [(11, ring_area), (15, 2400 - ring_area - hole_area), (17, 2400 - hole_area)]])
    _volume(mesh["volume_mm3"], 6195.2 - hole_area * 2)
    rays = _rays(mesh, [("through locating hole centre", 23, 13, []),
                        ("inside locating hole", 24, 13, []),
                        ("cap beside locating hole", 20, 13, [15, 17]),
                        ("covered hollow centre", 0, 0, [15, 17]),
                        ("negative X lip", -26.8, 0, [11, 17]), ("positive X lip", 26.8, 0, [11, 17]),
                        ("negative Y lip", 0, -16.8, [11, 17]), ("positive Y lip", 0, 16.8, [11, 17]),
                        ("negative X outer ledge", -29, 0, [15, 17]), ("positive X outer ledge", 29, 0, [15, 17]),
                        ("negative Y outer ledge", 0, -19, [15, 17]), ("positive Y outer ledge", 0, 19, [15, 17])])
    x, y, z = axes
    outer = {"min": [x[1]["coordinate_mm"], y[1]["coordinate_mm"], z[0]["coordinate_mm"]],
             "max": [x[4]["coordinate_mm"], y[4]["coordinate_mm"], z[1]["coordinate_mm"]]}
    inner = {"min": [x[2]["coordinate_mm"], y[2]["coordinate_mm"], z[0]["coordinate_mm"]],
             "max": [x[3]["coordinate_mm"], y[3]["coordinate_mm"], z[1]["coordinate_mm"]]}
    result = _public(mesh)
    result.update(kind="lid_with_locating_hole", source_lid=source_lid_metadata,
                  plate_dimensions_mm=[60.0, 40.0, z[2]["coordinate_mm"] - z[1]["coordinate_mm"]],
                  plate_z_mm=[z[1]["coordinate_mm"], z[2]["coordinate_mm"]],
                  plate_thickness_mm=z[2]["coordinate_mm"] - z[1]["coordinate_mm"],
                  ring_outer_bounds_mm=outer, ring_inner_bounds_mm=inner,
                  ring_outer_mm=[outer["max"][a] - outer["min"][a] for a in (0, 1)],
                  ring_inner_mm=[inner["max"][a] - inner["min"][a] for a in (0, 1)],
                  ring_z_mm=[z[0]["coordinate_mm"], z[1]["coordinate_mm"]],
                  ring_depth_mm=z[1]["coordinate_mm"] - z[0]["coordinate_mm"],
                  ring_wall_thicknesses_mm=[inner["min"][0] - outer["min"][0], outer["max"][0] - inner["max"][0],
                                            inner["min"][1] - outer["min"][1], outer["max"][1] - inner["max"][1]],
                  hole={"polygon": polygon, "z_mm": [15.0, 17.0], "through": True, "radial_walls": walls},
                  actual_rectangular_planes={axis: groups for axis, groups in zip("XYZ", axes)}, vertical_rays=rays)
    return result


def validate_tenon_assembly(body, lid):
    _require(body.get("passed") is True and body.get("kind") == "body_with_locating_pin" and
             lid.get("passed") is True and lid.get("kind") == "lid_with_locating_hole", "successful body and lid measurements required")
    pin, hole = body["pin"]["polygon"], lid["hole"]["polygon"]
    _require(all(_close(a, b) for a, b in zip(pin["centre_mm"], hole["centre_mm"])), "pin and hole centres are not aligned")
    phase = (hole["phase_angle_rad"] - pin["phase_angle_rad"] + STEP / 2) % STEP - STEP / 2
    _require(abs(phase) <= 1e-4, "pin and hole polygons do not have the same phase")
    gaps, evidence = [], []
    cx, cy = hole["centre_mm"]
    for number, plane in enumerate(hole["edge_planes"], 1):
        nx, ny = plane["normal_xy"]
        support = max(nx * (p[0] - cx) + ny * (p[1] - cy) for p in pin["vertices_xy_mm"])
        gap = plane["offset_mm"] - support
        _require(gap > 0 and _close(gap, 0.2 * math.cos(math.pi / 32)), "actual polygon normal clearance differs from trial")
        gaps.append(gap)
        evidence.append({"number": number, "normal_xy": [nx, ny], "hole_plane_offset_mm": plane["offset_mm"],
                         "pin_support_mm": support, "normal_gap_mm": gap})
    across = hole["across_flats_diameter_mm"] - pin["across_flats_diameter_mm"]
    _require(_close(across, 0.4 * math.cos(math.pi / 32)), "across-flats total clearance differs from trial")
    engagement = body["pin"]["tip_z_mm"] - lid["plate_z_mm"][0]
    reserve = lid["plate_z_mm"][1] - body["pin"]["tip_z_mm"]
    _require(_close(engagement, 1.5) and _close(reserve, 0.5), "incorrect axial engagement or tip headroom")
    ringfit = _assembly(lid, body["body_shell"])
    result = {"passed": True, "kind": "locating_tenon_assembly",
              "nominal_diameter_total_clearance_mm": 0.4, "nominal_radial_clearance_mm": 0.2,
              "actual_normal_gaps_mm": gaps, "min_normal_gap_mm": min(gaps),
              "normal_gap_evidence": evidence, "across_flats_total_clearance_mm": across,
              "phase_alignment_rad": phase, "engagement_mm": engagement, "tip_to_lid_top_mm": reserve,
              "ringfit": ringfit, "geometric_nonintersection": True,
              "single_pin_limits_rotation": False,
              "scope": "nominal polygon and axial mesh clearances only; one round pin does not fully constrain rotation",
              "printed": False, "fit_tested": False, "physical_measurements": None,
              "fit_results": None, "physical_interference": None, "qualified_clearance_mm": None,
              "trial_status": "experimental_geometry_only",
              "numericComparison": {"purpose": "Floating point reconstruction only; not manufacturing tolerance or fit acceptance",
                                    "dimensionsAbsMm": EPS_MM, "volumeRelative": VOLUME_REL_EPS}}
    return result


def read_mesh_data(obj):
    vertices, triangles, metadata = _object_mesh(obj)
    metadata.update(modifier_count=len(obj.modifiers), object_location_mm=[float(v) for v in obj.matrix_world.translation])
    return {"vertices": vertices, "triangles": triangles, "cad_metadata": metadata}


def read_tool_and_validate(obj, kind="pin"):
    data = read_mesh_data(obj)
    result = validate_tool_mesh(data["vertices"], data["triangles"], kind)
    result.update(data["cad_metadata"])
    _require(all(_close(a, b) for a, b in zip(result["object_location_mm"], result["location_mm"])),
             "construction tool object origin is not at its measured centre")
    return result


def read_body_pin_and_validate(obj, source_body, construction_pin=None):
    data = read_mesh_data(obj)
    result = validate_body_pin_mesh(data["vertices"], data["triangles"], source_body, construction_pin)
    result.update(data["cad_metadata"])
    return result


def read_lid_hole_and_validate(obj, source_lid):
    data = read_mesh_data(obj)
    result = validate_lid_hole_mesh(data["vertices"], data["triangles"], source_lid)
    result.update(data["cad_metadata"])
    return result
