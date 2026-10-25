"""Independent 07-05 native coupon audit, using only stdlib audit primitives.

Checks the actual 42-point native UI edits, oriented polygon boundaries and
all-point rigid transformations. This complements the subdivision-capable
production checker; it does not call coupon_checks or semantic validators.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from audit_overhang import topology, native_polygons, need, digest, sub, length


EPS = 1e-4
PLAN_SHA = "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33"
SOURCE_SHA = "360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d"
ORIGIN = [0., -22.200000762939453, -9.5]
NAMES = ("A_L19", "B_L17", "C_L21")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def near(actual, expected, label):
    need(abs(actual-expected) <= EPS, label + " differs by more than numeric 0.0001 mm")


def point_match(actual, expected):
    need(len(actual) == len(expected) == 42, "native UI point correspondence requires original 42 vertices")
    residual = max(length(sub(a,b)) for a,b in zip(actual,expected))
    need(residual <= EPS, "native UI changed a protected point or incorrect translation")
    return residual


def inspect(raw):
    topo, normals, areas = topology(raw)
    polygons = native_polygons(raw,normals,areas)
    dims = [topo["bounds_mm"]["max"][i]-topo["bounds_mm"]["min"][i] for i in range(3)]
    return dict(topo,dimensions_mm=dims,native_polygon_count=len(polygons)),normals,areas


def audit(run_dir):
    run_dir = Path(run_dir).resolve()
    report = read(run_dir/"verification.json")
    plan_path = Path(report["draft_plan_path"])
    need(digest(plan_path) == PLAN_SHA == report["draft_plan_sha256"], "frozen plan changed")
    plan = read(plan_path)
    need(report.get("passed") is True and report.get("reopened") is True, "native run is not successfully reopened")
    for key in ("source_scene_path","opened_scene_path"):
        need(digest(Path(report[key])) == SOURCE_SHA, "source or read-only scene copy changed")
    for prefix in ("source_tool_mesh","source_geometry_record","continuity_reference"):
        need(digest(Path(report[prefix+"_path"])) == report[prefix+"_sha256"] ==
             plan[prefix]["sha256"], "fixed history input changed: " + prefix)
    scene_path = Path(report["scene_path"])
    need(digest(scene_path) == report["scene_sha256"] and scene_path.stat().st_size == report["scene_bytes"], "saved scene changed")
    need(scene_path.name == plan["save_policy"]["filename"], "wrong new scene version")
    need(digest(Path(report["coupon_record_path"])) == report["coupon_record_sha256"], "coupon record changed")
    need(report.get("per_variant_geometry_modified") == {"A_L19":False,"B_L17":True,"C_L21":True}, "wrong single-parameter modification claims")
    for key in ("printed","fit_tested","slicer_checked","support_generation_performed","strength_analysis_performed",
                "deformation_analysis_performed","improvement_assessed","fit_qualification","exported_stl",
                "mesh_analysis_overhang_checked","rotation_applied_to_mesh","source_geometry_modified","full_box_modified"):
        need(report.get(key) is False, "unexpected performed or modified stage: " + key)
    for key in ("material_grade","epsilon_allow","Q","required_deflection_mm","delta_allow_mm","forces",
                "physical_measurements","fit_results","physical_interference","qualified_strength_N","qualified_clearance_mm",
                "improvement_validated","effective_mechanical_length_mm","full_box_boundary_equivalence","anchor_clamping_or_fixture",
                "support_required","final_print_orientation_approved","slicer_support_settings","bridge_or_support_qualified"):
        need(report.get(key) is None, "unexpected physical/strength/support qualification: " + key)
    source_path = run_dir/"source_snap_tool_mesh.json"
    source = read(source_path)
    prior_source = read(Path(report["source_tool_mesh_path"]))
    point_match(source["vertices"],prior_source["vertices"])
    source_top,_,_ = inspect(source)
    need(source_top["vertices"] == 42 and source_top["triangles"] == 80, "wrong native source point/triangle count")
    upper = [i for i,p in enumerate(source["vertices"]) if p[2] >= 11-EPS]
    need(len(upper) == 14 and len(source["vertices"])-len(upper) == 28, "wrong native upper selection partition")
    source_inventory = report["source_objects"]
    final_inventory = report["final_source_objects"]
    need(set(source_inventory) == set(final_inventory) == {"Body","Lid","SnapTool","FlangeTool"}, "source inventory differs")
    for name in source_inventory:
        for key in ("type","scale","modifier_count","matrix_world","local_mesh_sha256","mesh_data_name"):
            need(source_inventory[name][key] == final_inventory[name][key], "source object shape/matrix changed")
        need(final_inventory[name]["hidden"] is True, "source objects must finish hidden")
    objects = report["final_objects"]
    need(set(objects)==set(source_inventory)|set(NAMES), "final inventory is not the four sources plus three coupons")
    source_data = {item["mesh_data_name"] for item in final_inventory.values()}
    coupon_data = [objects[name]["mesh_data_name"] for name in NAMES]
    need(len(set(coupon_data))==3 and not (set(coupon_data)&source_data), "coupons have linked source or shared meshes")
    need(all(objects[name]["hidden"] is False for name in NAMES), "coupon comparison must show all three independent specimens")
    result = {"schema_version":1,"passed":True,"kind":"independent_coupon_length_audit",
              "audited_at":datetime.now(timezone.utc).isoformat(),"run_dir":str(run_dir),
              "audit_script_sha256":digest(Path(__file__)),"verification_sha256":digest(run_dir/"verification.json"),
              "source_scene_sha256":SOURCE_SHA,"plan_sha256":PLAN_SHA,"saved_scene_sha256":digest(scene_path),
              "method":"Independent all-42-point piecewise native UI edit, unchanged oriented polygon indices, all-point rigid pose, directed-edge topology/volume and actual loop-triangle bed areas; no coupon or semantic checker called.",
              "source_topology":source_top,"source_upper_vertex_count":14,"source_unchanged_vertex_count":28,
              "input_sha256":{source_path.name:digest(source_path)},"variants":{},"snapshot_sha256":{},
              "numeric_position_epsilon_mm":EPS,"epsilon_role":"Floating point reconstruction only; not manufacturing, support, strength or fit acceptance",
              "material_grade":None,"epsilon_allow":None,"forces":None,"printed":False,"fit_tested":False,
              "physical_measurements":None,"qualified_strength_N":None,"qualified_clearance_mm":None,
              "improvement_validated":None,"improvement_assessed":False,"effective_mechanical_length_mm":None,
              "anchor_clamping_or_fixture":None,"full_box_boundary_equivalence":None,"support_required":None}
    meshes = {}
    for spec in plan["coupon_objects"]:
        name = spec["name"];need(name in NAMES and name not in meshes, "extra or duplicate variant")
        paths = {pose:run_dir/(name+"_"+pose+"_mesh.json") for pose in ("source_frame","candidate")}
        raws = {pose:read(path) for pose,path in paths.items()}
        for path in paths.values(): result["input_sha256"][path.name] = digest(path)
        expected_frame = [[x,y,z+spec["upper_vertex_translation_z_mm"] if i in upper else z]
                          for i,(x,y,z) in enumerate(source["vertices"])]
        frame,candidate = raws["source_frame"],raws["candidate"]
        frame_residual = point_match(frame["vertices"],expected_frame)
        for raw in (frame,candidate):
            need(raw["polygons"] == source["polygons"], "native coupon oriented polygon topology changed")
            meta = raw["cad_metadata"]
            need(meta["modifier_count"] == 0 and all(abs(s-1) <= 1e-7 for s in meta["scale"]), "non-unit scale or modifier")
        location = spec["candidate_object_location_mm"]
        # Ry90 transforms sourceframe (x,y,z) to (z+9.5,y+rowY+22.2,4.5-x).
        expected_candidate = [[z-ORIGIN[2]+location[0],y-ORIGIN[1]+location[1],-x+location[2]] for x,y,z in expected_frame]
        candidate_residual = point_match(candidate["vertices"],expected_candidate)
        frame_meta,candidate_meta = frame["cad_metadata"],candidate["cad_metadata"]
        need(all(abs(a-b) <= EPS for a,b in zip(frame_meta["object_location_mm"],ORIGIN)), "sourceframe origin changed")
        need(all(abs(v) <= 1e-7 for v in frame_meta["object_rotation_euler_radians"]), "sourceframe rotation changed")
        need(all(abs(a-b) <= EPS for a,b in zip(candidate_meta["object_location_mm"],location)), "candidate location changed")
        need(all(abs(a-b) <= 1e-7 for a,b in zip(candidate_meta["object_rotation_euler_radians"],[0,math.pi/2,0])), "candidate rotation applied or changed")
        frame_top,frame_normals,_ = inspect(frame)
        top,normals,areas = inspect(candidate)
        near(top["bounds_mm"]["min"][2],0,"candidate numerical bed")
        need(top["vertices"] == 42 and top["triangles"] == 80, "actual native coupon topology differs")
        # Actual source beam thickness is read from its two longest side planes.
        thickness = abs(source["vertices"][9][1]-source["vertices"][8][1])
        expected_volume = source_top["volume_mm3"] + 6*thickness*spec["upper_vertex_translation_z_mm"]
        need(math.isclose(top["volume_mm3"],expected_volume,rel_tol=1e-5,abs_tol=EPS), "not a length-only actual volume change")
        bed = [i for i,t in enumerate(candidate["triangles"]) if all(abs(candidate["vertices"][v][2]) <= EPS for v in t)]
        need(bed and all(normals[i][2] < -1+1e-6 for i in bed), "invalid bed contact winding")
        heights = {}
        bearing = spec["bearing_plane_z_mm"]
        for label in ("straight_beam","root_fillet_and_miters","upper_hook"):
            indices=[]
            for i,t in enumerate(frame["triangles"]):
                zs=[frame["vertices"][v][2] for v in t];lo,hi=min(zs),max(zs)
                include = ((label=="straight_beam" and lo>=-7.4-EPS and hi<=bearing+EPS and hi-lo>EPS and abs(frame_normals[i][2])<1e-6) or
                           (label=="root_fillet_and_miters" and lo>=-8-EPS and hi<=-7.4+EPS and hi-lo>EPS) or
                           (label=="upper_hook" and lo>=bearing-EPS))
                if include: indices.append(i)
            need(indices,"missing raised feature")
            # Polygon identities stay fixed, but loop triangulation is allowed
            # to choose its diagonal anew. Geometric point sets determine Z.
            source_indices={v for i in indices for v in frame["triangles"][i]}
            zs=[candidate["vertices"][v][2] for v in source_indices]
            heights[label] = {"world_z_range_mm":[min(zs),max(zs)],"all_samples_above_bed":min(zs)>EPS}
        proof = report["motion_proofs"][name]
        need(proof["upper_vertex_count"]==14 and proof["unchanged_vertex_count"]==28 and proof["polygon_topology_unchanged"], "wrong native edit proof")
        selection = report["selection_proofs"][name]
        need(selection["selected_count"] == 14,"native selection evidence does not contain 14 vertices")
        selected = selection["selected_world_vertices_mm"]
        selected_indices = [min(upper,key=lambda i:length(sub(p,source["vertices"][i]))) for p in selected]
        need(set(selected_indices)==set(upper) and all(length(sub(p,source["vertices"][i]))<=EPS for p,i in zip(selected,selected_indices)),
             "native selected a protected root/anchor point or omitted an upper point")
        actual_bearing = min(frame["vertices"][i][2] for i in upper)
        actual_root = min(source["vertices"][i][2] for i in range(4,8))
        result["variants"][name] = {"source_frame_topology":frame_top,"candidate_topology":top,
            "geometric_L_mm":actual_bearing-actual_root,"actual_bearing_z_mm":actual_bearing,
            "actual_root_plane_z_mm":actual_root,"whole_coupon_height_mm":frame_top["dimensions_mm"][2],
            "max_source_frame_point_residual_mm":frame_residual,"max_candidate_point_residual_mm":candidate_residual,
            "native_upper14_and_unchanged28_verified":True,"source_polygon_topology_preserved":True,
            "bed_contact_triangle_count":len(bed),"bed_contact_area_mm2":math.fsum(areas[i] for i in bed),
            "raised_feature_heights":heights,"support_required":None}
        meshes[name] = top
    need(set(meshes)==set(NAMES),"need all three actual coupons")
    result["adjacent_y_projection_gaps_mm"] = [meshes[b]["bounds_mm"]["min"][1]-meshes[a]["bounds_mm"]["max"][1]
                                                for a,b in zip(NAMES,NAMES[1:])]
    for gap in result["adjacent_y_projection_gaps_mm"]: near(gap,7.4,"row separation")
    manifest = read(run_dir/"source-snapshot/manifest.json")
    need(len(manifest["files"])==11 and len(manifest["dataBindings"])==5, "wrong main-run snapshot/data-binding count")
    for entry in manifest["files"]+manifest["dataBindings"]:
        path = run_dir/entry["snapshot"]
        need(digest(path)==entry["sha256"],"frozen snapshot hash changed")
        result["snapshot_sha256"][entry["snapshot"]] = digest(path)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    parser.add_argument("--output",default="independent-coupon-audit-v001.json");args=parser.parse_args()
    need(Path(args.output).name==args.output and args.output.endswith(".json"),"output must be a JSON basename")
    result=audit(args.run_dir);target=args.run_dir.resolve()/args.output
    with target.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
    print(json.dumps({"passed":True,"output":str(target),"sha256":digest(target)},ensure_ascii=False))


if __name__=="__main__": main()
