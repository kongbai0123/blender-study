"""07-04 strict binary STL/world-pose readback for the 07-03 candidates.

STL has no units; numbers are interpreted as millimetres. Full oriented surface
coverage and inverse snapfit profiles are checked, independently of indexing or
valid subdivision. Bed epsilon is numeric reconstruction, never a print limit.
"""
import math

from lid_checks import _cross, _dot, _sub
from tenon_checks import _mesh
from stl_checks import read_stl, WELD_EPS_MM
from overhang_checks import analyze_mesh, ROTATIONS
from snapfit_checks import validate_body_mesh, validate_lid_mesh


EPS_MM = 1e-4
REL_EPS = 1e-5
SOURCE_SHA256 = "360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d"


def _require(condition,message):
    if not condition:
        raise ValueError("07-04 snapfit STL: "+message)


def _near(a,b,label,relative=False):
    _require(math.isfinite(float(b)) and math.isclose(a,b,rel_tol=REL_EPS if relative else 0,abs_tol=EPS_MM),label+" differs from the actual source")


def _semantic(actual,source,path="geometry"):
    """Compare measured features; counts of valid triangulation may differ."""
    if isinstance(actual,dict):
        _require(isinstance(source,dict),path+" missing")
        for key,value in actual.items():
            if key not in ("mesh_counts","triangle_count","source_body_metadata_compared"):
                _require(key in source,path+"."+key+" missing")
                _semantic(value,source[key],path+"."+key)
    elif isinstance(actual,(list,tuple)):
        _require(isinstance(source,(list,tuple)) and len(actual)==len(source),path+" shape mismatch")
        for i,(a,b) in enumerate(zip(actual,source)):
            _semantic(a,b,path+"[%d]"%i)
    elif isinstance(actual,(float,int)) and not isinstance(actual,bool):
        _near(actual,source,path,"area_mm2" in path or "volume_mm3" in path)
    else:
        _require(actual==source,path+" mismatch")


def _inverse(vertices,rotation,translation):
    transpose=list(zip(*rotation))
    return [tuple(_dot(row,_sub(p,translation)) for row in transpose) for p in vertices]


def _area2(points):
    return math.fsum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))/2


def _clip(subject,triangle):
    """Exact planar convex clipping; positional allowance is checked outside."""
    sign=1 if _area2(triangle)>=0 else -1
    polygon=list(subject)
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        if not polygon:
            break
        result=[]
        def distance(p):
            return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
        previous=polygon[-1];dp=distance(previous)
        for current in polygon:
            dc=distance(current)
            if (dp>=0)!=(dc>=0):
                fraction=dp/(dp-dc)
                result.append(tuple(previous[i]+fraction*(current[i]-previous[i]) for i in range(2)))
            if dc>=0:
                result.append(current)
            previous,dp=current,dc
        polygon=result
    return abs(_area2(polygon)) if len(polygon)>=3 else 0.


def _surface_match(actual,source):
    groups=[]
    for pts,normal,area in zip(source["points"],source["normals"],source["areas"]):
        for group in groups:
            if _dot(normal,group["normal"])>1-1e-6 and all(abs(_dot(group["normal"],_sub(p,group["origin"])))<=EPS_MM for p in pts):
                break
        else:
            group={"normal":normal,"origin":pts[0],"triangles":[],"area_mm2":0.,"actual_area_mm2":0.}
            groups.append(group)
        group["triangles"].append(pts);group["area_mm2"]+=area
    maximum_deficit=0.;maximum_plane_distance=0.
    for pts,normal,area in zip(actual["points"],actual["normals"],actual["areas"]):
        candidates=[g for g in groups if _dot(normal,g["normal"])>1-1e-6 and
                    all(abs(_dot(g["normal"],_sub(p,g["origin"])))<=EPS_MM for p in pts)]
        _require(len(candidates)==1,"export triangle is not on one actual oriented source plane")
        group=candidates[0];drop=max(range(3),key=lambda i:abs(group["normal"][i]));keep=[i for i in range(3) if i!=drop]
        projected=[tuple(p[i] for i in keep) for p in pts]
        covered=math.fsum(_clip(projected,[tuple(p[i] for i in keep) for p in tri]) for tri in group["triangles"])
        projected_area=abs(_area2(projected))
        perimeter=sum(math.sqrt(_dot(_sub(a,b),_sub(a,b))) for a,b in zip(pts,pts[1:]+pts[:1]))
        # A positional epsilon sweeps at most epsilon*perimeter of area. This
        # dimensional conversion preserves the same numeric position threshold.
        area_band=EPS_MM*(perimeter+1)
        _require(abs(covered-projected_area)<=area_band,"export facet crosses a source hole/gap or extends beyond its source surface")
        maximum_deficit=max(maximum_deficit,abs(covered-projected_area))
        maximum_plane_distance=max(maximum_plane_distance,max(abs(_dot(group["normal"],_sub(p,group["origin"]))) for p in pts))
        group["actual_area_mm2"]+=area
    planes=[]
    for group in groups:
        _near(group["actual_area_mm2"],group["area_mm2"],"whole oriented source-plane area",True)
        planes.append({"source_normal":list(group["normal"]),"source_origin_mm":list(group["origin"]),
                       "source_area_mm2":group["area_mm2"],"actual_area_mm2":group["actual_area_mm2"]})
    return {"passed":True,"method":"Every oriented export facet is covered by the actual coplanar source-triangle union; all whole-plane areas also agree",
            "source_triangle_count":len(source["triangles"]),"actual_triangle_count":len(actual["triangles"]),
            "oriented_plane_count":len(groups),"planes":planes,
            "max_plane_position_residual_mm":maximum_plane_distance,
            "max_projected_coverage_area_difference_mm2":maximum_deficit,
            "indexing_or_triangulation_identity_required":False,
            "coverage_numeric_band":"1e-4 mm times (triangle perimeter in mm + 1 mm); positional reconstruction only"}


def _facet_raw(mesh):
    return {"vertices":mesh["vertices"],"triangles":mesh["triangles"],
            "polygons":[list(t) for t in mesh["triangles"]],
            "triangle_polygon_indices":list(range(len(mesh["triangles"]))),
            "polygon_normals_world":[list(n) for n in mesh["normals"]]}


def validate_snapfit_export_mesh(vertices,triangles,kind,source_verification,source_pose_raw):
    """Verify a parsed/reimported mesh without requiring the original origin/RNA."""
    aliases={"body":"body","Body":"body","lid":"lid","Lid":"lid"}
    _require(kind in aliases,"unknown part kind");kind=aliases[kind]
    _require(source_verification.get("passed") is True and source_verification.get("scene_sha256")==SOURCE_SHA256,
             "fixed successful 07-03 source checkpoint is required")
    source_record=source_verification["poses"][kind+"_candidate"]
    _require(source_record.get("passed") is True and source_record.get("pose")=="candidate" and
             source_record.get("part_kind")==kind,"successful source candidate measurement is missing")
    rotation=ROTATIONS[kind,"candidate"];translation=source_record["world_translation_mm"]
    _require(all(abs(a-b)<1e-6 for ar,br in zip(rotation,source_record["rotation_matrix_world"]) for a,b in zip(ar,br)),
             "source candidate rotation differs from fixed 07-03 pose")
    actual=_mesh(vertices,triangles,0);source=_mesh(source_pose_raw["vertices"],source_pose_raw["triangles"],0)
    for side in ("min","max"):
        for a,b,c in zip(actual["bounds_mm"][side],source["bounds_mm"][side],source_record["bounds_mm"][side]):
            _near(a,b,"world "+side+" bound");_near(b,c,"source world "+side+" bound")
    _require(abs(actual["bounds_mm"]["min"][2])<=EPS_MM,"candidate world bed placement was changed")
    _near(actual["volume_mm3"],source["volume_mm3"],"oriented part volume",True)
    inverse=_inverse(actual["vertices"],rotation,translation)
    inverse_source=_inverse(source["vertices"],rotation,translation)
    validator=validate_body_mesh if kind=="body" else validate_lid_mesh
    geometry=validator(inverse,actual["triangles"])
    source_geometry=validator(inverse_source,source["triangles"])
    _semantic(source_geometry,source_record["inverse_geometry_readback"],"source.inverse_geometry")
    _semantic(geometry,source_geometry,"export.inverse_geometry")
    surface=_surface_match(actual,source)
    settings=source_verification.get("analysis_settings_by_pose",{}).get(kind+"_candidate",source_record["analysis_settings_readback"])
    derived=analyze_mesh(_facet_raw(actual),settings)
    _near(derived["derived_loop_triangle_statistics"]["summary"]["bed_contact"]["area_mm2"],source_record["bed_contact_area_mm2"],"actual bed-contact area",True)
    return {"passed":True,"kind":"snapfit_candidate_export_mesh","part_kind":kind,
            "bounds_mm":actual["bounds_mm"],"dimensions_mm":actual["dimensions_mm"],
            "volume_mm3":actual["volume_mm3"],"mesh_counts":actual["mesh_counts"],
            "non_manifold_edges":actual["non_manifold_edges"],"non_manifold_vertex_links":actual["non_manifold_vertex_links"],
            "inconsistent_winding_edges":actual["inconsistent_winding_edges"],"connected_shells":1,
            "euler_characteristic":2,"genus":0,"minimum_world_z_mm":actual["bounds_mm"]["min"][2],
            "inverse_geometry_readback":geometry,"source_surface_match":surface,
            "source_scene_path":source_verification["scene_path"],"source_scene_sha256":SOURCE_SHA256,
            "source_pose":"candidate","world_pose_retained":True,"rotation_applied_for_export":False,
            "derived_loop_triangle_statistics":derived["derived_loop_triangle_statistics"],
            "statistics_scope":"STL/reimport facet normals and areas independently calculated; not native polygon counts or GPU pixels",
            "analysis_settings_reference":settings,"numericComparison":{"purpose":"Numeric reconstruction only; not manufacturing tolerance or print/fit acceptance",
                 "dimensionsAbsMm":EPS_MM,"coordinateWeldMm":WELD_EPS_MM,"volumeRelative":REL_EPS},
            "support_strategy_status":"pending_slicer_review","support_required":None,"support_generation_performed":False,
            "final_print_orientation_approved":None,"slicer_support_settings":None,"bridge_or_support_qualified":None,
            "material_grade":None,"epsilon_allow":None,"root_flexibility_Q":None,"required_deflection_mm":None,
            "delta_allow_mm":None,"forces":None,"strength_analysis_performed":False,
            "slicer_checked":False,"printed":False,"fit_tested":False,"physical_measurements":None,
            "fit_results":None,"physical_interference":None,"qualified_strength_N":None,"qualified_clearance_mm":None}


def validate_snapfit_stl(path,kind,source_verification,source_pose_raw):
    mesh=read_stl(path)
    result=validate_snapfit_export_mesh(mesh["vertices"],mesh["triangles"],kind,source_verification,source_pose_raw)
    result.update({key:value for key,value in mesh.items() if key not in ("vertices","triangles")})
    result.update(kind="snapfit_candidate_stl",exported_stl=True)
    return result


def validate_export_layout(body,lid):
    _require(body.get("passed") is True and body.get("part_kind")=="body" and
             lid.get("passed") is True and lid.get("part_kind")=="lid","layout needs both measured candidate exports")
    _require(all(part.get("source_pose",part.get("pose"))=="candidate" for part in (body,lid)),
             "layout cannot use the 07-02 assembly or baseline poses")
    gap=lid["bounds_mm"]["min"][0]-body["bounds_mm"]["max"][0]
    _near(gap,35,"candidate layout X projection gap")
    _require(all(abs(p["bounds_mm"]["min"][2])<=EPS_MM for p in (body,lid)),"export layout is not on world Z=0")
    return {"passed":True,"kind":"snapfit_candidate_export_layout","source_pose":"candidate",
            "x_projection_gap_mm":gap,"bed_reference_z_mm":0,"parts_geometrically_separate":True,
            "printer_bed_dimensions_mm":None,"bed_capacity_checked":False,
            "support_strategy_status":"pending_slicer_review","support_required":None,"support_generation_performed":False,
            "final_print_orientation_approved":None,"bridge_or_support_qualified":None,"slicer_checked":False,
            "printed":False,"fit_tested":False,"physical_measurements":None,"fit_results":None,
            "qualified_strength_N":None,"qualified_clearance_mm":None}
