"""Independent stdlib audit of native three-coupon STL export/reimport.

No STL semantic or coupon checker is imported. Binary floats, stored normals,
directed edges, full bidirectional oriented triangle coverage and all native
source corners are read again. Only a new exclusive audit JSON is written.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import struct

from audit_overhang import topology, need, digest, sub, dot, cross, length


EPS = 1e-4
SOURCE_SHA = "22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8"
PLAN_SHA = "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33"
COUPON_RECORD_SHA = "1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d"
PRIOR_VERIFICATION_SHA = "ecea0a82400931113ad34f9c1fe054d6711835558d268973680a029ea656950b"
SOURCE_TOOL_SHA = "cb01f749d093467ec90742d38f90243067cdec00eee545c6c81f3f7b20a6aee7"
CANDIDATE_SHAS = {"A_L19":"5646200083769661833503b5177306fa0d80e0117597dad691b83f97b7b7530c",
                  "B_L17":"dc7cb34b232c1853fad6ae67f5de3149a63f0da2bbf7eac595fa062ef4acbcc7",
                  "C_L21":"0a40675dd41b0c8d6eb96376295ca0aaa090696b3349360187b3f0e23bcfc8c2"}
NAMES = ("A_L19", "B_L17", "C_L21")
ORIGIN = [0., -22.200000762939453, -9.5]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def binary_stl(path):
    """Independent strict <12fH decoder, with exact repeated-float welding."""
    data = path.read_bytes()
    need(len(data)>=84, "truncated binary header")
    count = struct.unpack_from("<I",data,80)[0]
    need(count>0 and len(data)==84+50*count, "binary STL count/length mismatch")
    vertices=[];triangles=[];lookup={};normal_sizes=[];angles=[];zero=0
    for index in range(count):
        values=struct.unpack_from("<12fH",data,84+50*index)
        need(all(math.isfinite(c) for c in values[:12]), "nonfinite stored normal or vertex")
        normal=values[:3];size=length(normal);normal_sizes.append(size)
        pts=[tuple(values[start:start+3]) for start in (3,6,9)]
        winding=cross(sub(pts[1],pts[0]),sub(pts[2],pts[0]))
        need(length(winding)>1e-12, "degenerate binary facet")
        if size:
            angles.append(math.degrees(math.atan2(length(cross(normal,winding)),dot(normal,winding))))
        else:
            zero+=1
        face=[]
        for point in pts:
            if point not in lookup:
                lookup[point]=len(vertices);vertices.append(point)
            face.append(lookup[point])
        triangles.append(face)
    raw={"vertices":vertices,"triangles":triangles}
    topo,_,_=topology(raw)
    return raw,{"sha256":digest(path),"byte_size":len(data),"triangle_count":count,"topology":topo,
                "coordinate_welding":"Exact repeated binary float triples; no manufacturing epsilon applied",
                "stored_normal_diagnostics":{"all_fields_finite":True,"zero_length_count":zero,
                    "length_min_max":[min(normal_sizes),max(normal_sizes)],
                    "maximum_unit_length_deviation":max(abs(s-1) for s in normal_sizes),
                    "maximum_winding_angle_deg":max(angles,default=None),
                    "opposite_hemisphere_count":sum(angle>90 for angle in angles),
                    "scope":"Stored-normal diagnostics only; does not qualify printing, supports or strength"}}


def signed_area(poly):
    return math.fsum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2


def intersection_area(subject,clipper):
    """Independent convex planar intersection (Sutherland-Hodgman)."""
    direction=1. if signed_area(clipper)>0 else -1.
    output=list(subject)
    for edge in range(3):
        if not output:
            return 0.
        a,b=clipper[edge],clipper[(edge+1)%3]
        def side(point): return direction*((b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]))
        polygon=output;output=[]
        for previous,current in zip(polygon[-1:]+polygon[:-1],polygon):
            sp,sc=side(previous),side(current)
            if (sp>=0)!=(sc>=0):
                ratio=sp/(sp-sc)
                output.append((previous[0]+ratio*(current[0]-previous[0]),previous[1]+ratio*(current[1]-previous[1])))
            if sc>=0:
                output.append(current)
    return abs(signed_area(output)) if len(output)>2 else 0.


def directed_coverage(actual,source):
    _,anormals,aareas=topology(actual);_,snormals,_=topology(source)
    source_points=[[source["vertices"][v] for v in f] for f in source["triangles"]]
    maximum_deficit=0.;maximum_distance=0.;tests=0
    for face,normal,area in zip(actual["triangles"],anormals,aareas):
        points=[actual["vertices"][v] for v in face]
        drop=max(range(3),key=lambda i:abs(normal[i]));keep=[i for i in range(3) if i!=drop]
        projected=[tuple(p[i] for i in keep) for p in points]
        coverage=0.;matches=0
        for source_points_one,snormal in zip(source_points,snormals):
            if dot(normal,snormal)<=1-1e-6:
                continue
            distances=[abs(dot(snormal,sub(p,source_points_one[0]))) for p in points]
            if max(distances)>EPS:
                continue
            coverage+=intersection_area(projected,[tuple(p[i] for i in keep) for p in source_points_one])
            maximum_distance=max(maximum_distance,max(distances));matches+=1;tests+=1
        need(matches>0,"actual oriented facet is not on an original finite plane")
        deficit=abs(coverage-abs(signed_area(projected)))
        perimeter=sum(length(sub(a,b)) for a,b in zip(points,points[1:]+points[:1]))
        need(deficit<=EPS*(perimeter+1),"oriented triangle extends beyond or crosses a source surface gap")
        maximum_deficit=max(maximum_deficit,deficit)
    return {"tested_facets":len(actual["triangles"]),"coplanar_triangle_pairs":tests,
            "max_projected_area_difference_mm2":maximum_deficit,"max_plane_distance_mm":maximum_distance}


def compare(actual,source):
    at,_,_=topology(actual);st,_,_=topology(source)
    for side in ("min","max"):
        need(all(abs(a-b)<=EPS for a,b in zip(at["bounds_mm"][side],st["bounds_mm"][side])),"world bounds changed")
    need(math.isclose(at["volume_mm3"],st["volume_mm3"],rel_tol=1e-5,abs_tol=EPS),"closed signed volume changed")
    return {"passed":True,"actual_topology":at,"source_topology":st,
            "actual_on_source":directed_coverage(actual,source),"source_on_actual":directed_coverage(source,actual),
            "method":"Independent bidirectional full oriented facet intersection-area coverage; indexing and legal subdivision may differ"}


def pose_and_bed(raw,original_tool,spec):
    """Inverse fixed Ry90 using known source origin, then recover actual L."""
    row=spec["candidate_object_location_mm"]
    frame=[[row[2]-p[2],p[1]-row[1]+ORIGIN[1],p[0]+ORIGIN[2]-row[0]] for p in raw["vertices"]]
    deltas=spec["upper_vertex_translation_z_mm"]
    expected=[[x,y,z+deltas if z>=11-EPS else z] for x,y,z in original_tool["vertices"]]
    match=[];distances=[]
    for point in expected:
        index=min(range(len(frame)),key=lambda i:length(sub(point,frame[i])))
        match.append(index);distances.append(length(sub(point,frame[index])))
    need(max(distances)<=EPS and len(set(match))==len(expected),"an original source corner is absent/changed after inverse pose and length edit")
    upper=[match[i] for i,p in enumerate(original_tool["vertices"]) if p[2]>=11-EPS]
    root=[match[i] for i in range(4,8)]
    bearing=min(frame[i][2] for i in upper);root_z=math.fsum(frame[i][2] for i in root)/len(root)
    geometric_L=bearing-root_z
    need(abs(geometric_L-spec["L_geometry_mm"])<=EPS,"measured inverse geometric L differs")
    topo,normals,areas=topology(raw)
    frame_raw={"vertices":frame,"triangles":raw["triangles"]};_,frame_normals,_=topology(frame_raw)
    bed=[i for i,t in enumerate(raw["triangles"]) if all(abs(raw["vertices"][v][2])<=EPS for v in t)]
    need(bed and all(normals[i][2]<-1+1e-6 for i in bed),"bad numeric bed contact orientation")
    need(abs(topo["bounds_mm"]["min"][2])<=EPS,"candidate is not on numerical Z0")
    raised={}
    for name in ("straight_beam","root_transition","upper_hook"):
        vertices=set()
        for i,t in enumerate(raw["triangles"]):
            zs=[frame[v][2] for v in t];lo,hi=min(zs),max(zs)
            include=((name=="straight_beam" and lo>=-7.4-EPS and hi<=bearing+EPS and hi-lo>EPS and abs(frame_normals[i][2])<1e-6) or
                     (name=="root_transition" and lo>=-8-EPS and hi<=-7.4+EPS and hi-lo>EPS) or
                     (name=="upper_hook" and lo>=bearing-EPS))
            if include: vertices.update(t)
        need(vertices,"missing raised feature")
        z=[raw["vertices"][i][2] for i in vertices]
        raised[name]={"world_z_range_mm":[min(z),max(z)],"all_samples_above_bed":min(z)>EPS}
    return {"passed":True,"geometric_L_mm":geometric_L,"actual_source_frame_bearing_z_mm":bearing,
            "actual_source_frame_root_z_mm":root_z,"maximum_inverse_native_corner_residual_mm":max(distances),
            "native_source_corner_count":len(match),"minimum_world_z_mm":topo["bounds_mm"]["min"][2],
            "bed_contact_triangle_count":len(bed),"bed_contact_area_mm2":math.fsum(areas[i] for i in bed),
            "raised_feature_heights":raised,"support_required":None,"effective_mechanical_length_mm":None}


def operator_evidence(entry,export,path):
    key="export_operator" if export else "import_operator"
    info=entry[key];options=entry["export_options" if export else "import_options"]
    need(info["idname"]==("WM_OT_stl_export" if export else "WM_OT_stl_import"),"wrong native STL operator")
    need(info["captured_at"]=="live_file_browser_before_native_confirm" and info["options"]==options,
         "missing actual preconfirm File Browser operator evidence")
    need(Path(info["filepath"]).resolve()==path.resolve(),"native operator filepath differs")
    need(options["global_scale"]==1 and options["use_scene_unit"] is False and options["forward_axis"]=="Y" and options["up_axis"]=="Z","native unit/axis options differ")
    if export:
        need(options["only_selected"] is True and options["ascii_format"] is False and options["use_batch"] is False,"export is not selected-only binary single object")
    history=info["operator_history_available"]
    need(type(history) is bool,"operator history flag is not actual boolean")
    if history:
        need(info.get("operator_history_entry")=={k:info[k] for k in ("idname","options","filepath")},"claimed operator history differs")
    else:
        need("operator_history_entry" not in info,"unavailable history cannot be claimed")
    return {"operator_history_available":history,"capture":"live File Browser before native confirmation"}


def audit(run_dir):
    run_dir=Path(run_dir).resolve();v=read(run_dir/"verification.json")
    need(v.get("passed") is True and v.get("reimport_verified") is True and v.get("kind")=="cantilever_coupon_stl_exports","not a completed three-coupon STL run")
    need(v["source_scene_sha256"]==SOURCE_SHA,"wrong geometry checkpoint")
    for key in ("source_scene_path","opened_scene_path"):
        need(digest(Path(v[key]))==SOURCE_SHA,"source/copy checkpoint changed")
    need(digest(Path(v["draft_plan_path"]))==PLAN_SHA==v["draft_plan_sha256"],"frozen plan changed")
    need(digest(Path(v["source_coupon_record_path"]))==v["source_coupon_record_sha256"]==COUPON_RECORD_SHA,"source geometry record changed")
    need(digest(Path(v["export_record_path"]))==v["export_record_sha256"],"new export record changed")
    for key in ("saved_new_scene","geometry_modified","source_geometry_modified","new_geometry_created","full_box_modified",
                "rotation_applied_to_mesh","mesh_analysis_overhang_checked","improvement_assessed","strength_analysis_performed",
                "deformation_analysis_performed","fit_qualification","slicer_checked","printed","fit_tested","support_generation_performed"):
        need(v.get(key) is False,"unexpected completed/modified stage: "+key)
    for key in ("material_grade","epsilon_allow","Q","effective_mechanical_length_mm","full_box_boundary_equivalence",
                "anchor_clamping_or_fixture","required_deflection_mm","delta_allow_mm","forces","physical_measurements","fit_results",
                "physical_interference","qualified_strength_N","qualified_clearance_mm","improvement_validated","support_required",
                "final_print_orientation_approved","slicer_support_settings","bridge_or_support_qualified"):
        need(v.get(key) is None,"unexpected physical/strength/support result: "+key)
    need(v["exported_stl"] is True,"STL export stage not recorded")
    plan=read(Path(v["draft_plan_path"]));specs={item["name"]:item for item in plan["coupon_objects"]}
    snapshot=run_dir/"source-snapshot";prior=read(snapshot/"source-coupon-verification.json")
    tool=read(snapshot/"source-snap-tool-reference.json")
    for filename,sha in (("source-coupon-verification.json",PRIOR_VERIFICATION_SHA),
                         ("source-coupon-record-v001.json",COUPON_RECORD_SHA),
                         ("source-snap-tool-reference.json",SOURCE_TOOL_SHA),("coupon-plan-v001.json",PLAN_SHA)):
        need(digest(snapshot/filename)==sha,"fixed historical data snapshot changed: "+filename)
    result={"schema_version":1,"passed":True,"kind":"independent_coupon_stl_export_audit",
            "audited_at":datetime.now(timezone.utc).isoformat(),"run_dir":str(run_dir),"audit_script_sha256":digest(Path(__file__)),
            "audit_primitive_dependency_sha256":{"audit_overhang.py":digest(Path(__file__).with_name("audit_overhang.py"))},
            "verification_sha256":digest(run_dir/"verification.json"),"source_scene_sha256":SOURCE_SHA,
            "method":"Independent stdlib binary decoder, exact repeated-float welding, directed-edge topology, bidirectional complete oriented facet coverage and inverse Ry90/native-corner/length readback. No semantic geometry checker called.",
            "parts":{},"input_sha256":{},"snapshot_sha256":{},"numeric_position_epsilon_mm":EPS,
            "epsilon_role":"Numerical reconstruction only; not manufacturing, support, strength, improvement or fit acceptance",
            "material_grade":None,"epsilon_allow":None,"forces":None,"printed":False,"fit_tested":False,"slicer_checked":False,
            "effective_mechanical_length_mm":None,"anchor_clamping_or_fixture":None,"full_box_boundary_equivalence":None,
            "improvement_assessed":False,"improvement_validated":None,"physical_measurements":None,"qualified_strength_N":None,
            "qualified_clearance_mm":None,"support_required":None}
    entries=v["exports"].values() if isinstance(v["exports"],dict) else v["exports"]
    candidates={}
    for entry in entries:
        name=entry["kind"];need(name in NAMES and name not in candidates,"extra or duplicate coupon")
        source_path=run_dir/("source_"+name+"_mesh.json");reimport_path=run_dir/("reimport_"+name+"_mesh.json")
        source,reimport=read(source_path),read(reimport_path)
        expected=read(snapshot/("source-"+name+"-candidate-mesh.json"))
        need(digest(snapshot/("source-"+name+"-candidate-mesh.json"))==CANDIDATE_SHAS[name],"fixed candidate raw snapshot changed")
        need(source["vertices"]==expected["vertices"] and source["triangles"]==expected["triangles"],"source candidate world mesh differs from immutable original")
        for key in ("scale","modifier_count","object_location_mm","object_rotation_euler_radians","matrix_world"):
            need(source["cad_metadata"][key]==expected["cad_metadata"][key],"source candidate transform changed")
        stl_path=Path(entry["stl_path"])
        need(stl_path.resolve().parent==(run_dir/"demo-files/exports").resolve() and stl_path.name=="u07_"+name+"_v001.stl", "wrong STL output location or version")
        mesh,binary=binary_stl(stl_path)
        need(binary["sha256"]==entry["stl_sha256"] and binary["byte_size"]==entry["stl_bytes"] and binary["triangle_count"]==entry["stl_triangles"],"STL metadata changed")
        need(entry["selected_names"]==[name] and entry["source_object"]==name,"export was not the single intended coupon")
        export_op=operator_evidence(entry,True,stl_path);import_op=operator_evidence(entry,False,stl_path)
        meta=reimport["cad_metadata"]
        need(meta["object_name"]==name+"_STL" and meta["modifier_count"]==0 and all(abs(s-1)<=1e-7 for s in meta["scale"]) and
             all(abs(c)<=1e-7 for c in meta["object_location_mm"]+meta["object_rotation_euler_radians"]),"fresh reimport must preserve world-baked vertices at Location0/Rotation0/Scale1")
        stl_compare=compare(mesh,source);reimport_compare=compare(reimport,mesh)
        bounds=binary["topology"]["bounds_mm"]
        dims=[bounds["max"][i]-bounds["min"][i] for i in range(3)]
        need(all(abs(a-b)<=EPS for a,b in zip(meta["object_axis_dimensions_mm"],dims)),"reimport Item dimensions do not show world dimensions")
        candidate_pose=pose_and_bed(mesh,tool,specs[name])
        result["parts"][name]={"binary":binary,"world_dimensions_mm":dims,"stl_vs_source":stl_compare,
            "reimport_vs_stl":reimport_compare,"candidate_pose_and_bed":candidate_pose,
            "source_object_axis_dimensions_mm":source["cad_metadata"]["object_axis_dimensions_mm"],
            "reimport_object_axis_dimensions_mm":meta["object_axis_dimensions_mm"],
            "export_operator_provenance":export_op,"import_operator_provenance":import_op}
        for path in (source_path,reimport_path,stl_path): result["input_sha256"][path.name]=digest(path)
        candidates[name]=binary["topology"]
    need(set(candidates)==set(NAMES),"three coupon exports required")
    result["adjacent_y_projection_gaps_mm"]=[candidates[b]["bounds_mm"]["min"][1]-candidates[a]["bounds_mm"]["max"][1] for a,b in zip(NAMES,NAMES[1:])]
    need(all(abs(g-7.4)<=EPS for g in result["adjacent_y_projection_gaps_mm"]),"world candidate rows changed")
    final=v["final_objects"];need(set(final)=={name+"_STL" for name in NAMES} and all(obj["hidden"] is False for obj in final.values()),"fresh final scene must contain only the three visible actual imported coupons")
    need(set(v["source_objects"])==set(prior["final_objects"]),"source seven-object inventory differs")
    for name,item in v["source_objects"].items():
        for key in ("type","scale","modifier_count","matrix_world","local_mesh_sha256","mesh_data_name"):
            need(item[key]==prior["final_objects"][name][key],"a source shape/matrix/datablock changed")
    need(not list((run_dir/"demo-files").glob("*.blend")),"STL export must not save a new blend")
    manifest=read(snapshot/"manifest.json")
    need(len(manifest["files"])==12 and len(manifest["dataBindings"])==7,"wrong formal frozen dependency count")
    for entry in manifest["files"]+manifest["dataBindings"]:
        path=run_dir/entry["snapshot"];need(digest(path)==entry["sha256"],"frozen dependency hash changed")
        result["snapshot_sha256"][entry["snapshot"]]=digest(path)
    records=read(run_dir/"run.json")["records"]
    for record in records:
        path=run_dir/record["file"];data=path.read_bytes()
        need(data[:8]==b"\x89PNG\r\n\x1a\n" and list(struct.unpack_from(">II",data,16))==[record["width"],record["height"]] and digest(path)==record["sha256"],"actual screenshot bytes/header/hash changed")
    need(len(list(run_dir.glob("*.png")))==len(records),"unrecorded or missing PNG")
    result["original_png_count"]=len(records)
    runner=read(run_dir/"runner-status.json")
    need(runner["status"]=="completed" and runner["blenderExitCode"]==0 and runner["workspacesUnchanged"] is True and not runner["runErrors"],"isolated runner did not finish cleanly")
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    parser.add_argument("--output",default="independent-coupon-export-audit-v001.json");args=parser.parse_args()
    need(Path(args.output).name==args.output and args.output.endswith(".json"),"output must be a JSON basename")
    result=audit(args.run_dir);target=args.run_dir.resolve()/args.output
    with target.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
    print(json.dumps({"passed":True,"output":str(target),"sha256":digest(target)},ensure_ascii=False))


if __name__=="__main__": main()
