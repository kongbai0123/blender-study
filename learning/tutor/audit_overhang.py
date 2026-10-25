"""Independent stdlib audit of a completed 07-03 run (no geometry helpers).

Reads six immutable raw meshes, native polygon-normal readbacks, analysis RNA
and the four-pose report. Writes one new, exclusive independent-audit-v001.json.
It does not launch Blender, alter geometry, infer supports, or qualify a print.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


EPS = .0001
ANGLE_BAND = .0001
REL = .00001
POSES = ("body_baseline", "body_candidate", "lid_baseline", "lid_candidate")


def need(condition,message):
    if not condition:
        raise ValueError(message)


def sub(a,b):
    return [x-y for x,y in zip(a,b)]


def dot(a,b):
    return math.fsum(x*y for x,y in zip(a,b))


def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def length(v):
    return math.sqrt(dot(v,v))


def close(a,b):
    return abs(a-b)<=EPS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cycle(indices):
    values=tuple(indices)
    return min(values[i:]+values[:i] for i in range(len(values)))


def topology(raw):
    points,faces=raw["vertices"],raw["triangles"]
    need(points and faces,"empty raw mesh")
    need(all(len(p)==3 and all(math.isfinite(c) for c in p) for p in points),"invalid vertex")
    edges=defaultdict(list);normals=[];areas=[];volumes=[];adjacency=[set() for _ in faces]
    for index,face in enumerate(faces):
        need(len(face)==3 and len(set(face))==3 and all(type(v) is int and 0<=v<len(points) for v in face),"invalid triangle")
        a,b,c=[points[i] for i in face]
        vector=cross(sub(b,a),sub(c,a));size=length(vector)
        need(size>1e-12,"degenerate triangle")
        normals.append([v/size for v in vector]);areas.append(size/2)
        volumes.append(dot(a,cross(b,c))/6)
        for va,vb in zip(face,face[1:]+face[:1]):
            edges[min(va,vb),max(va,vb)].append((index,va,vb))
    need(len({v for f in faces for v in f})==len(points),"unused vertex")
    for linked in edges.values():
        need(len(linked)==2,"triangle edge is not exactly two-sided")
        a,b=linked
        need(a[1:]==b[:0:-1],"triangle winding is inconsistent")
        adjacency[a[0]].add(b[0]);adjacency[b[0]].add(a[0])
    seen=set();stack=[0]
    while stack:
        face=stack.pop()
        if face not in seen:
            seen.add(face);stack.extend(adjacency[face]-seen)
    need(len(seen)==len(faces),"multiple connected shells")
    euler=len(points)-len(edges)+len(faces)
    need(euler==2,"unexpected genus/Euler characteristic")
    volume=math.fsum(volumes);need(volume>0,"non-positive signed volume")
    bounds={"min":[min(p[i] for p in points) for i in range(3)],
            "max":[max(p[i] for p in points) for i in range(3)]}
    return {"vertices":len(points),"triangles":len(faces),"edges":len(edges),
            "non_manifold_edges":0,"connected_shells":1,"euler_characteristic":euler,
            "genus":0,"volume_mm3":volume,"bounds_mm":bounds},normals,areas


def native_polygons(raw,triangle_normals,triangle_areas):
    polygons=raw["polygons"];mapping=raw["triangle_polygon_indices"]
    normals=raw["polygon_normals_world"]
    need(len(mapping)==len(raw["triangles"]) and len(normals)==len(polygons),"native polygon table size mismatch")
    groups=defaultdict(list)
    for i,face in enumerate(mapping):
        need(type(face) is int and 0<=face<len(polygons),"invalid native polygon index")
        groups[face].append(i)
    items=[]
    for index,ring in enumerate(polygons):
        need(len(ring)>=3 and len(set(ring))==len(ring) and groups[index],"invalid native polygon ring")
        normal=normals[index]
        need(len(normal)==3 and all(math.isfinite(v) for v in normal) and abs(length(normal)-1)<1e-5,"invalid raw native normal")
        directed=Counter();vector=[0.,0.,0.]
        for ti in groups[index]:
            tri=raw["triangles"][ti]
            need(set(tri)<=set(ring),"native triangle mapping crosses polygon")
            directed.update(zip(tri,tri[1:]+tri[:1]))
            need(dot(normal,triangle_normals[ti])>1-1e-6,"raw native normal and triangle disagree")
            for i in range(3):
                vector[i]+=triangle_normals[ti][i]*triangle_areas[ti]
        boundary=Counter(zip(ring,ring[1:]+ring[:1]))
        need(all(directed[e]-directed[e[::-1]]==boundary[e]-boundary[e[::-1]] for e in directed) and
             all(directed[e]-directed[e[::-1]]==1 for e in boundary),"polygon/triangulation boundary mismatch")
        points=[raw["vertices"][v] for v in ring]
        geometric=[v/length(vector) for v in vector]
        need(all(abs(dot(geometric,sub(p,points[0])))<=EPS for p in points),"nonplanar polygon")
        items.append((index,points,normal,math.fsum(triangle_areas[t] for t in groups[index])))
    return items


def classify(items,settings):
    need(settings["type"]=="OVERHANG" and settings["axis"]=="NEG_Z" and
         settings["show_statvis"] and settings["show_overlays"] and settings["shading"]=="SOLID" and not settings["xray"],"wrong native analysis context")
    low=math.degrees(settings["minimum_radians"]);high=math.degrees(settings["maximum_radians"])
    need(abs(low)<=ANGLE_BAND and abs(high-45)<=ANGLE_BAND and high>low,"wrong native display range")
    need(abs(low-settings["minimum_deg"])<=ANGLE_BAND and abs(high-settings["maximum_deg"])<=ANGLE_BAND,"native rad/deg mismatch")
    names=("all","bed_contact","downward_not_bed_contact","fully_elevated_downward","downward_touching_bed_edge",
           "derived_native_visible","derived_native_visible_not_bed_contact","above_maximum_gray","angle_boundary_band")
    summary={n:{"count":0,"area_mm2":0.,"indices":[]} for n in names};records=[]
    for index,points,normal,area in items:
        # atan2 of raw RNA normal components differs independently from the
        # production helper's acos of the Newell world-position reconstruction.
        angle=math.degrees(math.atan2(math.hypot(normal[0],normal[1]),-normal[2]))
        weight=1. if angle<low else -1. if angle>high else 1-(angle-low)/(high-low)
        downward=normal[2]<-1e-7
        contact=downward and max(abs(p[2]) for p in points)<=EPS
        nonbed=downward and not contact
        elevated=nonbed and min(p[2] for p in points)>EPS
        visible=weight>=0;band=min(abs(angle-low),abs(angle-high))<=ANGLE_BAND
        membership=(True,contact,nonbed,elevated,nonbed and not elevated,visible,visible and not contact,not visible,band)
        for name,member in zip(names,membership):
            if member:
                s=summary[name];s["count"]+=1;s["area_mm2"]+=area;s["indices"].append(index)
        records.append({"index":index,"area_mm2":area,"angle_from_negative_z_deg":angle,
                        "derived_native_weight":weight,"native_world_normal":normal,
                        "bed_contact":contact,"downward_not_bed_contact":nonbed,
                        "fully_elevated_downward":elevated,"angle_boundary_band":band})
    return {"summary":summary,"records":records}


def compare_statistics(actual,reported):
    for name,group in actual["summary"].items():
        prior=reported["summary"][name]
        need(group["count"]==prior["count"] and group["indices"]==prior["indices"],"classification mask differs: "+name)
        need(close(group["area_mm2"],prior["area_mm2"]),"classification area differs: "+name)
    need(len(actual["records"])==len(reported["records"]),"record count differs")
    angles=[];weights=[]
    for a,b in zip(actual["records"],reported["records"]):
        need(a["index"]==b["index"] and close(a["area_mm2"],b["area_mm2"]),"record index/area differs")
        angles.append(abs(a["angle_from_negative_z_deg"]-b["angle_from_negative_z_deg"]))
        weights.append(abs(a["derived_native_weight"]-b["derived_native_weight"]))
    return {"all_classification_masks_equal":True,"all_classification_areas_equal":True,
            "max_raw_normal_vs_reported_geometry_angle_difference_deg":max(angles,default=0),
            "max_scalar_weight_difference":max(weights,default=0),
            "angle_difference_note":"Raw native normals and world-position reconstruction can differ on small float32 miter faces; no band expansion or exact-angle identity is claimed."}


def rigid_pose(source,raw,name):
    kind,pose=name.split("_")
    rotation=([[1,0,0],[0,1,0],[0,0,1]] if pose=="baseline" else
              [[0,0,1],[0,1,0],[-1,0,0]] if kind=="body" else [[1,0,0],[0,-1,0],[0,0,-1]])
    translation=([-40,0,15] if name=="body_baseline" else [-40,0,30] if kind=="body" else
                 [40,0,-10.2] if pose=="baseline" else [40,-6,max(p[2] for p in source["vertices"])])
    need(len(source["vertices"])==len(raw["vertices"]),"rigid vertex count changed")
    pending=set(range(len(raw["vertices"])));mapping={};residual=[]
    for si,p in enumerate(source["vertices"]):
        target=[dot(row,p)+translation[i] for i,row in enumerate(rotation)]
        ti=min(pending,key=lambda i:length(sub(raw["vertices"][i],target)))
        distance=length(sub(raw["vertices"][ti],target));need(distance<=EPS,"rigid point residual exceeds 0.0001 mm")
        mapping[ti]=si;pending.remove(ti);residual.append(distance)
    for table in ("triangles","polygons"):
        original=Counter(cycle(f) for f in source[table])
        placed=Counter(cycle([mapping[v] for v in f]) for f in raw[table])
        need(original==placed,"rigid transform changed oriented "+table)
    meta=raw["cad_metadata"]
    need(meta["modifier_count"]==0 and len(meta["scale"])==3 and all(abs(v-1)<=1e-6 for v in meta["scale"]),"wrong modifier/scale")
    need(meta["length_unit"]=="MILLIMETERS" and abs(meta["unit_scale"]-.001)<=1e-9,"wrong scene units")
    euler=[0,0,0] if pose=="baseline" else [0,math.pi/2,0] if kind=="body" else [math.pi,0,0]
    need(all(abs(a-b)<=math.radians(ANGLE_BAND) for a,b in zip(meta["object_rotation_euler_radians"],euler)),"wrong retained object Euler pose")
    matrix=meta["matrix_world"]
    need(len(matrix)==4 and all(len(row)==4 for row in matrix),"missing object matrix readback")
    need(all(abs(matrix[i][j]-rotation[i][j])<1e-6 for i in range(3) for j in range(3)),"object matrix rotation mismatch")
    source_origin=source["cad_metadata"]["object_location_mm"]
    expected_location=[dot(row,source_origin)+translation[i] for i,row in enumerate(rotation)]
    need(all(close(matrix[i][3],expected_location[i]) and close(meta["object_location_mm"][i],expected_location[i]) for i in range(3)),"object origin confused with world rigid translation")
    return {"world_rotation_rows":rotation,"world_translation_mm_expected":translation,
            "max_source_to_pose_vertex_residual_mm":max(residual),"all_vertices_matched":len(residual),
            "oriented_triangles_preserved":True,"oriented_native_polygon_rings_preserved":True,
            "scale_one":True,"object_rotation_retained":True}


def audit(run_dir):
    run_dir=Path(run_dir).resolve()
    names=["source_body_mesh.json","source_lid_mesh.json"]+[n+"_mesh.json" for n in POSES]
    names += ["analysis-settings-by-pose.json","pose-verification.json"]
    data={name:json.loads((run_dir/name).read_text(encoding="utf-8")) for name in names}
    report={"schema_version":1,"passed":True,"kind":"independent_overhang_raw_audit",
            "audited_at":datetime.now(timezone.utc).isoformat(),"run_dir":str(run_dir),
            "audit_script_sha256":digest(Path(__file__)),"input_sha256":{n:digest(run_dir/n) for n in names},
            "method":"Independent stdlib directed-edge topology/volume, fixed rigid transform, raw native polygon normal atan2 and mapped triangle area; no overhang_checks or other project helper imported.",
            "numeric_comparison":{"rigid_and_bed_abs_mm":EPS,"angle_boundary_band_deg":ANGLE_BAND,
                                  "volume_relative":REL,"scope":"numeric reconstruction only; not manufacturing/print acceptance"},
            "poses":{},"printed":False,"fit_tested":False,"support_required":None,
            "support_generation_performed":False,"physical_measurements":None,"fit_results":None,
            "material_grade":None,"epsilon_allow":None,"forces":None,
            "qualified_strength_N":None,"qualified_clearance_mm":None}
    sources={kind:data["source_"+kind+"_mesh.json"] for kind in ("body","lid")}
    source_topology={k:topology(v)[0] for k,v in sources.items()}
    report["source_topology"]=source_topology
    for name in POSES:
        raw=data[name+"_mesh.json"];kind=name.split("_")[0]
        topo,normals,areas=topology(raw)
        need(abs(topo["bounds_mm"]["min"][2])<=EPS,"not landed on bed")
        need(math.isclose(topo["volume_mm3"],source_topology[kind]["volume_mm3"],rel_tol=REL,abs_tol=EPS),"pose volume changed")
        rigid=rigid_pose(sources[kind],raw,name)
        polygons=native_polygons(raw,normals,areas)
        tri_items=[(i,[raw["vertices"][v] for v in f],normals[i],areas[i]) for i,f in enumerate(raw["triangles"])]
        settings=data["analysis-settings-by-pose.json"][name]
        poly=classify(polygons,settings);tri=classify(tri_items,settings)
        prior=data["pose-verification.json"][name]
        need(prior["passed"] is True,"pose report did not pass")
        for key in ("material_grade","epsilon_allow","root_flexibility_Q","required_deflection_mm","delta_allow_mm",
                    "insertion_force_N","retention_force_N","physical_measurements","fit_results","qualified_strength_N","qualified_clearance_mm","support_required"):
            need(prior.get(key) is None,"unexpected physical/material/support claim: "+key)
        for key in ("strength_analysis_performed","slicer_checked","printed","fit_tested","support_generation_performed"):
            need(prior.get(key) is False,"unexpected completed physical stage: "+key)
        report["poses"][name]={"passed":True,"topology":topo,"rigid_pose":rigid,
            "derived_native_polygon_statistics":poly,"derived_loop_triangle_statistics":tri,
            "native_normal_vs_report_comparison":compare_statistics(poly,prior["derived_polygon_statistics"]),
            "loop_triangle_vs_report_comparison":compare_statistics(tri,prior["derived_loop_triangle_statistics"])}
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir",type=Path)
    parser.add_argument("--output",default="independent-audit-v001.json")
    args=parser.parse_args()
    need(Path(args.output).name==args.output and args.output.endswith(".json"),"output must be a JSON basename inside run_dir")
    result=audit(args.run_dir)
    output=args.run_dir.resolve()/args.output
    with output.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
    print(json.dumps({"passed":result["passed"],"output":str(output),"sha256":digest(output)},ensure_ascii=False))


if __name__=="__main__":
    main()
