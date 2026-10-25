"""07-03 read-only rigid poses and derived native-Overhang angle statistics.

World coordinates are millimetres. Native Blender uses polygon normals, not
loop-triangle counts. These independent calculations reproduce its angle/remap
definition, not framebuffer pixels or a slicer's support decisions. No Blender
operator, material model, printer limit, or strength qualification is used.
"""
from collections import Counter, defaultdict
import math

from lid_checks import _bounds, _cross, _dot, _sub
from tenon_checks import _mesh
from snapfit_checks import validate_body_mesh, validate_lid_mesh


EPS_MM = 1e-4
ANGLE_EPS_DEG = 1e-4
REL_EPS = 1e-5
SOURCE_COMMIT = "9e2066aef7ef"
SOURCE_URL = "https://raw.githubusercontent.com/blender/blender/" + SOURCE_COMMIT + "/source/blender/draw/intern/mesh_extractors/extract_mesh_vbo_mesh_analysis.cc"
ROTATIONS = {
    ("body", "baseline"): ((1,0,0),(0,1,0),(0,0,1)),
    ("lid", "baseline"): ((1,0,0),(0,1,0),(0,0,1)),
    ("body", "candidate"): ((0,0,1),(0,1,0),(-1,0,0)),
    ("lid", "candidate"): ((1,0,0),(0,-1,0),(0,0,-1)),
}


def _require(condition, message):
    if not condition:
        raise ValueError("07-03 orientation/Overhang: " + message)


def _close(a,b,eps=EPS_MM):
    return math.isclose(a,b,rel_tol=0,abs_tol=eps)


def _multiply(matrix,point):
    return tuple(math.fsum(row[i]*point[i] for i in range(3)) for row in matrix)


def _normal(points):
    vector=[math.fsum(_cross(a,b)[i] for a,b in zip(points,points[1:]+points[:1])) for i in range(3)]
    magnitude=math.sqrt(_dot(vector,vector))
    _require(magnitude>1e-12,"degenerate native polygon")
    return tuple(v/magnitude for v in vector)


def _settings(settings):
    _require(isinstance(settings,dict),"missing native analysis settings readback")
    _require(settings.get("type")=="OVERHANG" and settings.get("axis")=="NEG_Z",
             "this lesson requires native OVERHANG / negative world Z")
    _require(settings.get("show_statvis") is True and settings.get("shading")=="SOLID" and
             settings.get("xray") is False,"native overlay must be enabled in Solid mode with X-Ray off")
    values=[]
    for prefix,target in (("minimum",0),("maximum",45)):
        radians=float(settings[prefix+"_radians"])
        degrees=float(settings[prefix+"_deg"])
        _require(math.isfinite(radians) and math.isfinite(degrees) and 0<=radians<=math.pi,
                 "invalid native angular range")
        _require(_close(math.degrees(radians),degrees,ANGLE_EPS_DEG) and
                 _close(degrees,target,ANGLE_EPS_DEG),"native angle/radian readback differs from lesson display range")
        values.append(math.degrees(radians))
    _require(values[1]>values[0],"native angular range must be nonzero")
    return values


def native_weight(angle_deg,minimum_deg,maximum_deg):
    """Scalar analogue of the pinned C++ remap; not a sampled GPU colour."""
    _require(all(math.isfinite(v) for v in (angle_deg,minimum_deg,maximum_deg)) and
             maximum_deg>minimum_deg,"invalid remap range")
    if angle_deg<minimum_deg:
        return 1.0
    if angle_deg>maximum_deg:
        return -1.0
    return max(0.0,min(1.0,1-(angle_deg-minimum_deg)/(maximum_deg-minimum_deg)))


def _polygons(raw,mesh):
    polygons=raw.get("polygons")
    triangle_polygons=raw.get("triangle_polygon_indices")
    reported_normals=raw.get("polygon_normals_world")
    _require(isinstance(polygons,list) and polygons and isinstance(triangle_polygons,list) and
             len(triangle_polygons)==len(mesh["triangles"]) and isinstance(reported_normals,list) and
             len(reported_normals)==len(polygons),"raw must retain polygons, triangle mapping and native world normals")
    grouped=defaultdict(list)
    for i,p in enumerate(triangle_polygons):
        _require(isinstance(p,int) and not isinstance(p,bool) and 0<=p<len(polygons),"invalid triangle polygon index")
        grouped[p].append(i)
    result=[]
    for index,polygon in enumerate(polygons):
        _require(isinstance(polygon,list) and len(polygon)>=3 and len(set(polygon))==len(polygon) and
                 all(isinstance(v,int) and not isinstance(v,bool) and 0<=v<len(mesh["vertices"]) for v in polygon),
                 "invalid polygon ring")
        points=[mesh["vertices"][v] for v in polygon]
        normal=_normal(points)
        _require(all(abs(_dot(normal,_sub(p,points[0])))<=EPS_MM for p in points),
                 "nonplanar native polygon: facet angle cannot stand in for native face angle")
        given=reported_normals[index]
        _require(len(given)==3 and all(math.isfinite(c) for c in given) and
                 _close(math.sqrt(_dot(given,given)),1,1e-5) and _dot(given,normal)>1-1e-6,
                 "native polygon normal readback disagrees with actual world polygon")
        faces=grouped[index]
        _require(faces,"polygon has no mapped loop triangles")
        directed=Counter()
        for face in faces:
            triangle=mesh["triangles"][face]
            _require(set(triangle)<=set(polygon) and _dot(mesh["normals"][face],normal)>1-1e-6,
                     "triangle mapping crosses a polygon or has opposite winding")
            directed.update(zip(triangle,triangle[1:]+triangle[:1]))
        boundary=Counter(zip(polygon,polygon[1:]+polygon[:1]))
        for edge,count in list(directed.items()):
            residual=count-directed[edge[::-1]]
            _require(residual==boundary[edge]-boundary[edge[::-1]],
                     "triangulation boundary does not equal native polygon ring")
        _require(all(directed[e]-directed[e[::-1]]==1 for e in boundary),"polygon boundary is missing")
        area=math.fsum(mesh["areas"][i] for i in faces)
        result.append({"index":index,"points":points,"normal":normal,"area_mm2":area,
                       "loop_triangle_indices":faces})
    return result


def _angle_records(items,minimum,maximum):
    records=[]
    summaries={name:{"count":0,"area_mm2":0.0,"indices":[]} for name in
               ("all","bed_contact","downward_not_bed_contact","fully_elevated_downward",
                "downward_touching_bed_edge","derived_native_visible","derived_native_visible_not_bed_contact",
                "above_maximum_gray","angle_boundary_band")}
    for item in items:
        points,normal=item["points"],item["normal"]
        angle=math.degrees(math.acos(max(-1.0,min(1.0,-normal[2]))))
        weight=native_weight(angle,minimum,maximum)
        lowest=min(p[2] for p in points)
        highest=max(p[2] for p in points)
        downward=normal[2]<-1e-7
        contact=downward and all(abs(p[2])<=EPS_MM for p in points)
        nonbed=downward and not contact
        elevated=nonbed and lowest>EPS_MM
        visible=weight>=0
        boundary=min(abs(angle-minimum),abs(angle-maximum))<=ANGLE_EPS_DEG
        record={"index":item["index"],"area_mm2":item["area_mm2"],"normal_world":list(normal),
                "angle_from_negative_z_deg":angle,"derived_native_weight":weight,
                "z_range_mm":[lowest,highest],"bed_contact":contact,
                "downward_not_bed_contact":nonbed,"fully_elevated_downward":elevated,
                "angle_boundary_band":boundary}
        if "loop_triangle_indices" in item:
            record["loop_triangle_indices"]=item["loop_triangle_indices"]
        records.append(record)
        membership={"all":True,"bed_contact":contact,"downward_not_bed_contact":nonbed,
                    "fully_elevated_downward":elevated,"downward_touching_bed_edge":nonbed and not elevated,
                    "derived_native_visible":visible,"derived_native_visible_not_bed_contact":visible and not contact,
                    "above_maximum_gray":weight<0,"angle_boundary_band":boundary}
        for name,belongs in membership.items():
            if belongs:
                group=summaries[name]
                group["count"]+=1;group["area_mm2"]+=item["area_mm2"];group["indices"].append(item["index"])
    return {"summary":summaries,"records":records}


def analyze_mesh(raw,settings):
    """Independent polygon and facet angle/area calculations for one bed pose."""
    minimum,maximum=_settings(settings)
    mesh=_mesh(raw["vertices"],raw["triangles"],0)
    _require(mesh["bounds_mm"]["min"][2]>=-EPS_MM and _close(mesh["bounds_mm"]["min"][2],0),
             "part is below the bed or not landed at world Z=0")
    polygons=_polygons(raw,mesh)
    triangles=[{"index":i,"points":p,"normal":n,"area_mm2":a}
               for i,(p,n,a) in enumerate(zip(mesh["points"],mesh["normals"],mesh["areas"]))]
    poly_stats=_angle_records(polygons,minimum,maximum)
    tri_stats=_angle_records(triangles,minimum,maximum)
    _require(poly_stats["summary"]["bed_contact"]["area_mm2"]>0,"no actual horizontal bed-contact face")
    return {"derived_polygon_statistics":poly_stats,"derived_loop_triangle_statistics":tri_stats,
            "analysis_settings_readback":dict(settings),
            "native_definition_source":SOURCE_URL,"native_definition_commit":SOURCE_COMMIT,
            "angle_definition":"angle between outward world polygon normal and world negative Z; 0 down, 90 vertical, 180 up",
            "statistics_scope":"independently derived angles/areas and scalar remap; not GPU face-count or framebuffer readback",
            "angle_boundary_band_deg":ANGLE_EPS_DEG,"numeric_height_epsilon_mm":EPS_MM,
            "support_required":None,"support_generation_performed":False,"printability_qualified":None}


def validate_orientation(source_raw,pose_raw,kind,settings,pose="candidate"):
    _require((kind,pose) in ROTATIONS,"unsupported part/pose")
    rotation=ROTATIONS[kind,pose]
    source_geometry=(validate_body_mesh if kind=="body" else validate_lid_mesh)(source_raw["vertices"],source_raw["triangles"])
    source=_mesh(source_raw["vertices"],source_raw["triangles"],0)
    placed=_mesh(pose_raw["vertices"],pose_raw["triangles"],0)
    _polygons(source_raw,source)
    _require(len(source["vertices"])==len(placed["vertices"]),"rigid pose changed the vertex count")
    rotated=[_multiply(rotation,p) for p in source["vertices"]]
    rb=_bounds(rotated)
    translation=[(placed["bounds_mm"]["min"][a]+placed["bounds_mm"]["max"][a]-rb["min"][a]-rb["max"][a])/2 for a in range(3)]
    expected=([-40,0,15] if pose=="baseline" and kind=="body" else
              [40,0,-10.2] if pose=="baseline" else
              [-40,0,30] if kind=="body" else [40,-6,source["bounds_mm"]["max"][2]])
    _require(all(_close(a,b) for a,b in zip(translation,expected)),"world rigid translation differs from lesson pose")
    pending=set(range(len(placed["vertices"])))
    residuals=[]
    for point in rotated:
        target=[point[a]+translation[a] for a in range(3)]
        index=min(pending,key=lambda i:math.sqrt(_dot(_sub(placed["vertices"][i],target),_sub(placed["vertices"][i],target))))
        delta=math.sqrt(_dot(_sub(placed["vertices"][index],target),_sub(placed["vertices"][index],target)))
        _require(delta<=EPS_MM,"world mesh is not the prescribed rigid transform of the source")
        pending.remove(index);residuals.append(delta)
    transpose=tuple(zip(*rotation))
    inverse=[_multiply(transpose,_sub(p,translation)) for p in placed["vertices"]]
    inverse_geometry=(validate_body_mesh if kind=="body" else validate_lid_mesh)(inverse,placed["triangles"])
    _require(math.isclose(source["volume_mm3"],placed["volume_mm3"],rel_tol=REL_EPS,abs_tol=EPS_MM),
             "rigid pose changed signed volume")
    stats=analyze_mesh(pose_raw,settings)
    metadata=pose_raw.get("cad_metadata",{})
    _require(metadata.get("modifier_count")==0 and len(metadata.get("scale",[]))==3 and
             all(_close(s,1,1e-6) for s in metadata["scale"]),"pose needs Scale1 and no modifiers")
    expected_euler=[0,0,0] if pose=="baseline" else [0,math.pi/2,0] if kind=="body" else [math.pi,0,0]
    actual_euler=metadata.get("object_rotation_euler_radians")
    _require(isinstance(actual_euler,list) and len(actual_euler)==3 and
             all(_close(a,b,math.radians(ANGLE_EPS_DEG)) for a,b in zip(actual_euler,expected_euler)),
             "native object rotation was applied/changed instead of retaining the specified UI pose")
    result={"passed":True,"kind":"snapfit_print_orientation","part_kind":kind,"pose":pose,
            "rotation_matrix_world":[list(row) for row in rotation],"world_translation_mm":translation,
            "max_rigid_vertex_residual_mm":max(residuals),"rigid_shape_preserved":True,
            "rotation_applied_to_mesh":False,"source_geometry_readback":source_geometry,
            "inverse_geometry_readback":inverse_geometry,"source_bounds_mm":source["bounds_mm"],
            "bounds_mm":placed["bounds_mm"],"dimensions_mm":placed["dimensions_mm"],
            "volume_mm3":placed["volume_mm3"],"mesh_counts":placed["mesh_counts"],
            "non_manifold_edges":placed["non_manifold_edges"],"connected_shells":1,"genus":0,
            "minimum_world_z_mm":placed["bounds_mm"]["min"][2],
            "bed_contact_area_mm2":stats["derived_polygon_statistics"]["summary"]["bed_contact"]["area_mm2"],
            **stats,"material_grade":None,"epsilon_allow":None,"root_flexibility_Q":None,
            "required_deflection_mm":None,"delta_allow_mm":None,"insertion_force_N":None,"retention_force_N":None,
            "strength_analysis_performed":False,"slicer_checked":False,"printed":False,"fit_tested":False,
            "physical_measurements":None,"fit_results":None,"physical_interference":None,
            "qualified_strength_N":None,"qualified_clearance_mm":None,"trial_status":"orientation_geometry_only"}
    if kind=="body":
        length=_multiply(rotation,(0,0,1));bending=_multiply(rotation,(0,1,0))
        result["layer_direction_readback"]={"layer_plane_normal_world":[0,0,1],
              "arm_length_direction_world":list(length),"nominal_bending_direction_world":list(bending),
              "arm_length_parallel_bed":abs(length[2])<1e-7,"bending_direction_parallel_bed":abs(bending[2])<1e-7,
              "scope":"geometric direction only; no layer adhesion, strain, fatigue or strength qualification"}
    return result


def validate_layout(body,lid):
    _require(all(p.get("passed") is True and p.get("pose")=="candidate" for p in (body,lid)) and
             body.get("part_kind")=="body" and lid.get("part_kind")=="lid","layout requires measured candidate parts")
    gap=lid["bounds_mm"]["min"][0]-body["bounds_mm"]["max"][0]
    _require(_close(gap,35),"candidate X projection gap differs from 35 mm")
    _require(all(abs(p["minimum_world_z_mm"])<=EPS_MM for p in (body,lid)),"both parts must be on world Z=0")
    return {"passed":True,"kind":"snapfit_print_layout","x_projection_gap_mm":gap,
            "parts_geometrically_separate":True,"bed_reference_z_mm":0,
            "printer_bed_dimensions_mm":None,"bed_capacity_checked":False,
            "support_required":None,"support_generation_performed":False,"slicer_checked":False,
            "printed":False,"fit_tested":False,"physical_measurements":None,
            "fit_results":None,"qualified_strength_N":None,"qualified_clearance_mm":None}


def read_analysis_mesh_data(obj):
    """Copy evaluated source/pose polygons and triangulation; never modify Blender."""
    import bpy
    _require(obj is not None and obj.type=="MESH","object is not a mesh")
    units=bpy.context.scene.unit_settings
    _require(units.system=="METRIC" and units.length_unit=="MILLIMETERS" and
             _close(units.scale_length,.001,1e-9),"scene must use Metric / Millimeters / .001")
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        factor=units.scale_length*1000
        normals=evaluated.matrix_world.to_3x3().inverted().transposed()
        return {"vertices":[list((evaluated.matrix_world@v.co)*factor) for v in mesh.vertices],
                "triangles":[list(t.vertices) for t in mesh.loop_triangles],
                "polygons":[list(p.vertices) for p in mesh.polygons],
                "triangle_polygon_indices":[t.polygon_index for t in mesh.loop_triangles],
                "polygon_normals_world":[list((normals@p.normal).normalized()) for p in mesh.polygons],
                "cad_metadata":{"object_name":obj.name,"scale":list(obj.scale),"modifier_count":len(obj.modifiers),
                   "object_location_mm":list(obj.matrix_world.translation*factor),
                   "object_rotation_euler_radians":list(obj.rotation_euler),
                   "unit_scale":units.scale_length,"length_unit":units.length_unit,
                   "measurement_source":"evaluated world-mm polygons and loop triangles; read only"}}
    finally:
        evaluated.to_mesh_clear()
