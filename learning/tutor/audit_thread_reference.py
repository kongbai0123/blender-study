"""Independent stdlib audit of 08-01's unchanged box and pending thread plan.

This audits document semantics and measured reference geometry only. It does
not calculate thread dimensions, choose a route/standard, configure Screw or
infer manufactured fit. No modelling/semantic geometry checker is imported.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import struct

from audit_overhang import topology, need, digest, sub, dot, cross, length


EPS=1e-4
SOURCE_SHA="b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530"
PLAN_SHA="92c0bf94ede81a48a5c16179ae1558bb8c61c521f960c79cd4ad05830f0d79bb"
FACTS_SHA="78a0b7b1092287e7956b9a11da17f4b1ef838c7da50473e989d05cc759b67834"
INPUT_KEYS=("angle_degrees","axis","axis_object","object_screw","screw_offset_mm","iterations",
            "steps_viewport","steps_render","merge_distance_mm","evaluated_export_mode")
FALSE_KEYS=("thread_modeled","boss_modeled","geometry_modified","modifier_created","calculations_performed",
            "strength_analysis_performed","fit_qualification","slicer_checked","exported_stl","printed","fit_tested")
NULL_KEYS=("physical_measurements","fit_results","qualified_strength_N","qualified_clearance_mm","qualified_torque_Nm")
AXIS_PLANES=[{ -30:(1200,-1),-28:(1008,1),28:(1008,-1),30:(1200,1)},
             { -20:(1800,-1),-18:(1568,1),18:(1568,-1),20:(1800,1)},
             { -15:(2400,-1),-13:(2016,1),15:(384,1)}]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def near(actual,expected,label,relative=False):
    need(math.isfinite(float(actual)) and math.isclose(actual,expected,rel_tol=1e-5 if relative else 0,abs_tol=EPS),
         label+" differs from actual reference geometry")


def pending_plan(plan,facts):
    """Reject an invented numeric/route/configuration result in this record."""
    need(plan["lesson_step"]=="08-01" and plan["stage"]=="specification_planning_only","wrong planning document")
    parameters=plan["draft_parameters"]
    need(len(parameters)==24 and len({p["id"] for p in parameters})==24 and
         all(p.get("value") is None and p.get("status")=="draft_pending" for p in parameters),"all 24 thread parameters must remain pending")
    route=plan["route"]
    need(route["selected"] is None and route["selection_status"]=="pending_user_choice" and
         route["candidate_is_not_a_user_decision"] is True,"tutor route suggestion must not become a learner decision")
    mapping=plan["blender_mapping"]
    need(mapping["status"]=="documented_mapping_only_not_configured" and mapping["modifier_created"] is False and
         all(mapping[key] is None for key in INPUT_KEYS),"documented Screw mappings are not configured RNA inputs")
    need(len(mapping["relationships"])==4 and all(isinstance(x,str) and x for x in mapping["relationships"]),"conditional mapping relationships missing")
    need("Angle=360°" in mapping["relationships"][0] and "Object Screw" in mapping["relationships"][0] and
         "n=1" in mapping["relationships"][0] and "Iterations" in mapping["relationships"][1],"single-turn/single-start mapping conditions missing")
    for key in FALSE_KEYS: need(plan.get(key) is False,"unexpected thread stage: "+key)
    for key in NULL_KEYS: need(key in plan and plan[key] is None,"unexpected thread qualification: "+key)
    conditions=plan["print_conditions"]
    need(conditions["nozzle_diameter_mm"]==.4 and all(conditions[k] is None for k in
         ("process","printer_model","material_grade","line_width_mm","layer_height_mm","slicer_and_version","print_orientation","support_settings")),
         "known nozzle cannot supply unknown manufacturing parameters")
    need(all(v is None for v in plan["service_conditions"].values()),"service conditions must remain pending")
    need(facts["thread_standard_selected"] is None and facts["manufacturing_parameters_selected"] is False and
         facts["strength_or_fit_qualification"] is False and facts["full_standards_obtained"] is False and facts["source_images_used"] is False,
         "source facts cannot select a standard or claim full standards/qualification")
    by_id={f["id"]:f for f in facts["facts"]}
    need(by_id["general_sweep_mapping"]["numeric_values_applied"] is False and
         "Object Screw" in by_id["single_turn_condition"]["statement"],"source inference must remain conditional and unapplied")
    return {"passed":True,"pending_parameter_count":24,"thread_route_selected":None,
            "screw_configuration_present":False,"thread_parameter_calculations_performed":False,
            "standard_selected":None,"numeric_thread_inputs_applied":False}


def vertical_hits(raw,x,y):
    values=[]
    for face in raw["triangles"]:
        a,b,c=[raw["vertices"][i] for i in face]
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-12: continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denominator
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denominator
        if min(u,v,1-u-v)<-1e-9: continue
        z=u*a[2]+v*b[2]+(1-u-v)*c[2]
        if not any(abs(z-old)<=EPS for old in values):values.append(z)
    return sorted(values)


def inspect_box(raw):
    measured,normals,areas=topology(raw)
    expected_corners=[(x,y,z) for z in (-15,15) for x in (-30,30) for y in (-20,20)]
    expected_corners += [(x,y,z) for z in (-13,15) for x in (-28,28) for y in (-18,18)]
    need(len(raw["vertices"])==16 and len(raw["triangles"])==28,"expected original native box topology")
    need(all(min(length(sub(p,e)) for e in expected_corners)<=EPS for p in raw["vertices"]) and
         all(min(length(sub(e,p)) for p in raw["vertices"])<=EPS for e in expected_corners),"source box corner geometry differs")
    groups=[{} for _ in range(3)]
    for face,normal,area in zip(raw["triangles"],normals,areas):
        axis=max(range(3),key=lambda i:abs(normal[i]))
        need(abs(abs(normal[axis])-1)<=1e-8,"unexpected non-axis reference face")
        coordinates=[raw["vertices"][v][axis] for v in face]
        level=sum(coordinates)/3
        need(max(coordinates)-min(coordinates)<=EPS,"nonplanar reference face")
        target=min(AXIS_PLANES[axis],key=lambda coordinate:abs(coordinate-level))
        near(level,target,"reference face plane")
        expected_area,direction=AXIS_PLANES[axis][target]
        need(normal[axis]*direction>1-1e-8,"reference plane has reversed winding")
        groups[axis][target]=groups[axis].get(target,0)+area
    evidence={}
    for axis,groups_one in enumerate(groups):
        need(set(groups_one)==set(AXIS_PLANES[axis]),"missing reference plane")
        for coordinate,area in groups_one.items():near(area,AXIS_PLANES[axis][coordinate][0],"reference plane area",True)
        evidence["XYZ"[axis]]=[{"coordinate_mm":c,"area_mm2":a} for c,a in sorted(groups_one.items())]
    near(measured["volume_mm3"],15552,"reference signed volume",True)
    rays=[]
    for x,y,expected in ((0,0,[-15,-13]),(-29,0,[-15,15]),(29,0,[-15,15]),(0,-19,[-15,15]),(0,19,[-15,15]),(27,17,[-15,-13])):
        actual=vertical_hits(raw,x,y)
        need(len(actual)==len(expected),"source cavity ray does not match material intervals")
        for a,b in zip(actual,expected):near(a,b,"reference ray hit")
        rays.append({"xy_mm":[x,y],"z_hits_mm":actual})
    cad=raw["cad_metadata"]
    need(cad["scale"]==[1,1,1] and cad["modifier_count"]==0 and cad["length_unit"]=="MILLIMETERS" and
         abs(cad["unit_scale"]-.001)<=1e-9,"reference CAD units/Scale/modifiers differ")
    need(all(abs(v)<=1e-7 for v in cad["object_location_mm"]+cad["object_rotation_euler_radians"]),"reference pose is not original")
    result=dict(measured,actual_plane_areas=evidence,vertical_rays=rays,outer_dimensions_mm=[60,40,30],
                cavity_dimensions_mm=[56,36,28],wall_and_floor_thickness_mm=2)
    return result


def selected_faces(measurements,raw):
    expected={"rim":([-30,-20,15],[30,-18,15],116,1),
              "inner_floor":([-28,-18,-13],[28,18,-13],2016,1),
              "outer_floor":([-30,-20,-15],[30,20,-15],2400,-1)}
    need(set(measurements)==set(expected),"need the three real selected reference faces")
    result={}
    for role,item in measurements.items():
        lo,hi,area,direction=expected[role]
        need(item["object_name"]=="Body_Reference" and item["selected_face_count"]==1 and item["selected_vertex_count"]==4,"wrong native face selection")
        points=item["vertices_mm"];need(len(points)==4 and len(set(map(tuple,points)))==4,"selected face must have four distinct real vertices")
        for point in points:need(min(length(sub(point,p)) for p in raw["vertices"])<=EPS,"selected face coordinate absent from actual box")
        bounds={"min":[min(p[i] for p in points) for i in range(3)],"max":[max(p[i] for p in points) for i in range(3)]}
        for actual,target in ((bounds["min"],lo),(bounds["max"],hi)):
            for a,b in zip(actual,target):near(a,b,"selected "+role+" bound")
        need(item["bounds_mm"]==bounds,"reported selected face bounds do not match its actual points")
        vector=[0.,0.,0.]
        for a,b in zip(points,points[1:]+points[:1]):
            one=cross(a,b)
            vector=[x+y/2 for x,y in zip(vector,one)]
        near(length(vector),area,"selected "+role+" actual polygon area",True)
        need(vector[2]*direction>0,"selected face winding mismatch")
        result[role]={"bounds_mm":bounds,"actual_area_mm2":length(vector),
                      "spans_mm":[bounds["max"][i]-bounds["min"][i] for i in range(3)]}
    return result


def audit(run_dir):
    run_dir=Path(run_dir).resolve();project=run_dir.parents[3]
    v=read(run_dir/"verification.json")
    need(v.get("passed") is True and v.get("kind")=="thread_parameter_reference" and v.get("reopened") is True,"not a completed 08-01 reference")
    for key in ("source_unchanged","opened_copy_unchanged","source_body_geometry_unchanged"):need(v.get(key) is True,"reference changed: "+key)
    for key in FALSE_KEYS+("pilot_hole_modeled","counterpart_modeled","screw_modifier_created","exported"):
        need(v.get(key) is False,"unexpected model/calculation/physical stage: "+key)
    for key in NULL_KEYS+("physical_interference","material_grade","thread_route_selected","thread_standard_selected"):
        need(key in v and v[key] is None,"unselected/unqualified result must remain null: "+key)
    for key in ("source_scene_path","opened_scene_path"):
        need(digest(Path(v[key]))==SOURCE_SHA,"original source/copy hash changed")
    need(v["source_scene_sha256"]==v["opened_scene_sha256"]==SOURCE_SHA,"source provenance differs")
    plan_path=Path(v["parameter_template_path"]);facts_path=Path(v["source_facts_path"])
    need(digest(plan_path)==v["parameter_template_sha256"]==PLAN_SHA and digest(facts_path)==v["source_facts_sha256"]==FACTS_SHA,"frozen plan/facts changed")
    plan,facts=read(plan_path),read(facts_path);pending=pending_plan(plan,facts)
    need(v["route"]==plan["route"] and v["blender_mapping"]==plan["blender_mapping"],"unconfigured document mapping differs from template")
    source_path=run_dir/"source_body_mesh.json";reference_path=run_dir/"reference_body_mesh.json"
    source,reference=read(source_path),read(reference_path)
    source_geometry,reference_geometry=inspect_box(source),inspect_box(reference)
    need(source["vertices"]==reference["vertices"] and source["triangles"]==reference["triangles"],"reference point/oriented triangle geometry changed")
    for key in ("matrix_world","scale","modifier_count","local_mesh_sha256","mesh_data_name"):
        need(source["cad_metadata"][key]==reference["cad_metadata"][key],"source mesh/matrix/datablock changed")
    need(source["cad_metadata"]["object_name"]=="Cube" and reference["cad_metadata"]["object_name"]=="Body_Reference","wrong original/reference object")
    faces=selected_faces(v["face_measurements"],reference)
    need(read(run_dir/"face-measurements.json")==v["face_measurements"],"native selected-face record changed")
    need(type(v["non_manifold_selected_edges"]) is int and v["non_manifold_selected_edges"]==0,"native NM selection did not return zero")
    scene=Path(v["scene_path"])
    need(scene.resolve()==(run_dir/"demo-files/u08_thread_reference_v001.blend").resolve() and scene.stat().st_size==v["scene_bytes"] and
         digest(scene)==v["scene_sha256"] and v["scene_sha256"]!=SOURCE_SHA and v["scene_role"]=="unmodified_box_thread_reference","new reopened reference scene provenance differs")
    record_path=Path(v["parameter_record_path"]);record=read(record_path)
    need(record_path.resolve()==(run_dir/"parameter-record-v001.json").resolve() and digest(record_path)==v["parameter_record_sha256"],"parameter record provenance differs")
    extras={"recordedAt","source_scene_readback","reference_scene","measured_box","face_measurements"}
    need(set(record)==set(plan)|extras and all(record[k]==value for k,value in plan.items()),"parameter record changed the frozen all-pending document")
    need(record["source_scene_readback"]=={"path":v["source_scene_path"],"sha256":SOURCE_SHA,"bytes":Path(v["source_scene_path"]).stat().st_size},"source readback must supplement, not overwrite template source_scene")
    need(record["reference_scene"]=={"path":str(scene),"sha256":v["scene_sha256"],"bytes":v["scene_bytes"],"scene_role":v["scene_role"]} and
         record["measured_box"]==v["reference_body"] and record["face_measurements"]==v["face_measurements"],"reference record did not bind actual scene/box/faces")
    final=v["final_objects"]
    need(set(final)=={"Body_Reference","Camera","Light"} and final["Body_Reference"]["type"]=="MESH" and
         final["Body_Reference"]["hidden"] is False and final["Body_Reference"]["modifier_count"]==0,"only the original plain box mesh is allowed")
    for name in ("Camera","Light"):need(final[name]["hidden"] is True,"reference camera/light must stay hidden")
    need(final["Body_Reference"]["matrix_world"]==reference["cad_metadata"]["matrix_world"],"final reference matrix differs")
    need(not list((run_dir/"demo-files").rglob("*.stl")),"08-01 must not export STL")
    manifest=read(run_dir/"source-snapshot/manifest.json")
    need(len(manifest["files"])==6 and len(manifest["dataBindings"])==2,"wrong formal 6-code/2-data dependency count")
    snapshots={}
    for entry in manifest["files"]+manifest["dataBindings"]:
        path=run_dir/entry["snapshot"];need(digest(path)==entry["sha256"],"frozen source snapshot changed")
        snapshots[entry["snapshot"]]=digest(path)
    need(digest(run_dir/"source-snapshot/parameter-template-v001.json")==PLAN_SHA and
         digest(run_dir/"source-snapshot/thread-source-facts-v001.json")==FACTS_SHA,"snapshot plan/facts do not match pinned versions")
    records=read(run_dir/"run.json")["records"]
    for item in records:
        image=run_dir/item["file"];data=image.read_bytes()
        need(data[:8]==b"\x89PNG\r\n\x1a\n" and list(struct.unpack_from(">II",data,16))==[item["width"],item["height"]] and digest(image)==item["sha256"],"native screenshot bytes/header/hash changed")
    need(len(records)==len(list(run_dir.glob("*.png")))==12,"expected 12 actual UI reference records")
    runner=read(run_dir/"runner-status.json")
    need(runner["status"]=="completed" and runner["blenderExitCode"]==0 and runner["workspacesUnchanged"] is True and not runner["runErrors"],"independent UI runner did not complete cleanly")
    progress_hash=digest(project/"learning/progress.json")
    baseline=run_dir/"publication-baseline-v001.json"
    if baseline.exists():need(progress_hash==read(baseline)["progress_sha256"],"learner progress changed during preparation")
    return {"schema_version":1,"passed":True,"kind":"independent_thread_parameter_reference_audit",
            "audited_at":datetime.now(timezone.utc).isoformat(),"run_dir":str(run_dir),"audit_script_sha256":digest(Path(__file__)),
            "audit_primitive_dependency_sha256":{"audit_overhang.py":digest(Path(__file__).with_name("audit_overhang.py"))},
            "verification_sha256":digest(run_dir/"verification.json"),"source_scene_sha256":SOURCE_SHA,
            "parameter_template_sha256":PLAN_SHA,"source_facts_sha256":FACTS_SHA,"source_and_reference_geometry_equal":True,
            "method":"Independent directed-edge topology/volume, all 16 native corners, all oriented face-plane areas and six material-interval rays; real three-face selection coordinates; full pending document semantics and provenance. No thread/formula/model checker called.",
            "source_geometry":source_geometry,"reference_geometry":reference_geometry,"selected_faces":faces,"pending_document":pending,
            "saved_scene":{"path":str(scene),"bytes":scene.stat().st_size,"sha256":digest(scene)},"original_png_count":12,
            "raw_sha256":{source_path.name:digest(source_path),reference_path.name:digest(reference_path)},"snapshot_sha256":snapshots,
            "learner_progress_sha256":progress_hash,"learner_completion_confirmed":False,
            "geometry_measurement_recomputed":True,"thread_parameter_calculations_performed":False,
            "thread_geometry_created":False,"thread_route_selected":None,"thread_standard_selected":None,
            "screw_modifier_configured":False,"printed":False,"fit_tested":False,"slicer_checked":False,
            "physical_measurements":None,"fit_results":None,"qualified_torque_Nm":None,"qualified_strength_N":None,"qualified_clearance_mm":None,
            "numeric_position_epsilon_mm":EPS,"epsilon_role":"Floating point geometry reconstruction only; not thread manufacturing tolerance or fit qualification"}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    parser.add_argument("--output",default="independent-thread-reference-audit-v001.json");args=parser.parse_args()
    need(Path(args.output).name==args.output and args.output.endswith(".json"),"output must be a JSON basename")
    result=audit(args.run_dir);target=args.run_dir.resolve()/args.output
    with target.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
    print(json.dumps({"passed":True,"output":str(target),"sha256":digest(target)},ensure_ascii=False))


if __name__=="__main__":main()
