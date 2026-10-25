"""Independent 07-04 native STL/source/reimport audit; no export checker calls.

The established strict binary reader is reused only for file decoding/welding.
Topology, source correspondence, raw stored normals, world bounds and placement
are audited separately. One new exclusive audit JSON is written per run.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import struct
import sys

from audit_overhang import topology, need, digest, cycle, sub, dot, cross, length
sys.path.insert(0,str(Path(__file__).resolve().parent/"scenarios"))
from stl_checks import read_stl


EPS=.0001
SOURCE_SHA="360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d"
ORIENTATION_SHA="b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986"


def _point_in_triangle(p,a,b,c,normal):
    if abs(dot(normal,sub(p,a)))>EPS:
        return False
    for first,second in ((a,b),(b,c),(c,a)):
        edge=sub(second,first)
        if dot(cross(edge,sub(p,first)),normal)<-EPS*length(edge):
            return False
    return True


def _surface_samples(actual,source):
    source_top,normals,areas=topology(source)
    actual_top,anormals,aareas=topology(actual)
    # Independent grouping/point checks supplement a signature mismatch after
    # a legal retessellation. The actual native run normally matches exactly.
    source_triangles=[[source["vertices"][v] for v in f] for f in source["triangles"]]
    checks=0
    for face,normal in zip(actual["triangles"],anormals):
        pts=[actual["vertices"][v] for v in face]
        samples=pts+[[sum(p[i] for p in pts)/3 for i in range(3)]]
        samples += [[(a[i]+b[i])/2 for i in range(3)] for a,b in zip(pts,pts[1:]+pts[:1])]
        for point in samples:
            need(any(dot(normal,n)>1-1e-6 and _point_in_triangle(point,*triangle,n)
                     for triangle,n in zip(source_triangles,normals)),"surface sample is off actual oriented source")
            checks+=1
    return checks


def compare_meshes(actual,source):
    at,_,_=topology(actual);st,_,_=topology(source)
    for side in ("min","max"):
        need(all(abs(a-b)<=EPS for a,b in zip(at["bounds_mm"][side],st["bounds_mm"][side])),"world bounds differ from source")
    need(math.isclose(at["volume_mm3"],st["volume_mm3"],rel_tol=1e-5,abs_tol=EPS),"world signed volume changed")
    mapping={};residual=[];exact=True
    for ai,point in enumerate(actual["vertices"]):
        si=min(range(len(source["vertices"])),key=lambda i:length(sub(point,source["vertices"][i])))
        distance=length(sub(point,source["vertices"][si]));residual.append(distance)
        if distance>EPS:
            exact=False
        mapping[ai]=si
    if exact:
        a=Counter(cycle([mapping[i] for i in f]) for f in actual["triangles"])
        b=Counter(cycle(f) for f in source["triangles"])
        exact=a==b
    sampled=None
    if not exact:
        sampled={"actual_on_source":_surface_samples(actual,source),"source_on_actual":_surface_samples(source,actual),
                 "scope":"Independent bidirectional finite samples, bounds, topology and volume; exact full planar clipping is separately performed by the production checker."}
    return {"passed":True,"actual_topology":at,"source_topology":st,
            "exact_oriented_triangles_match_within_numeric_epsilon":exact,
            "max_nearest_source_vertex_distance_mm":max(residual),"fallback_surface_samples":sampled,
            "method":"Independent oriented triangle correspondence for native output, with bidirectional surface samples for retessellation"}


def stored_normals(path):
    data=Path(path).read_bytes();need(len(data)>=84,"truncated STL")
    count=struct.unpack_from("<I",data,80)[0];need(len(data)==84+50*count and count>0,"bad binary STL length")
    lengths=[];angles=[];zero=0
    for i in range(count):
        values=struct.unpack_from("<12fH",data,84+50*i)
        need(all(math.isfinite(v) for v in values[:12]),"nonfinite stored normal/vertex")
        n=values[:3];size=length(n);lengths.append(size)
        if size==0:
            zero+=1;continue
        a,b,c=values[3:6],values[6:9],values[9:12]
        winding=cross(sub(b,a),sub(c,a));need(length(winding)>0,"degenerate stored triangle")
        angle=math.degrees(math.atan2(length(cross(n,winding)),dot(n,winding)))
        angles.append(angle)
    return {"all_normal_fields_finite":True,"zero_length_normal_count":zero,
            "normal_length_min_max":[min(lengths),max(lengths)],
            "max_unit_length_deviation":max(abs(v-1) for v in lengths),
            "max_stored_normal_vs_vertex_winding_angle_deg":max(angles,default=None),
            "opposite_hemisphere_count":sum(a>90 for a in angles),
            "scope":"Stored-normal diagnostics only; small float32 miter angular differences are preserved, not converted to a geometric tolerance or print qualification. Vertex winding controls the independent closed-shell test."}


def audit(run_dir):
    run_dir=Path(run_dir).resolve();verification_path=run_dir/"verification.json"
    report=json.loads(verification_path.read_text(encoding="utf-8"))
    need(report.get("passed") is True and report.get("source_scene_sha256")==SOURCE_SHA,"wrong source checkpoint or failed run")
    for key in ("source_scene_path","opened_scene_path"):
        need(digest(Path(report[key]))==SOURCE_SHA,"source/original-copy hash changed")
    need(digest(Path(report["source_orientation_record_path"]))==ORIENTATION_SHA,"orientation record changed")
    for key in ("printed","fit_tested","slicer_checked","support_generation_performed","strength_analysis_performed","saved_new_scene","geometry_modified","rotation_applied_to_mesh"):
        need(report.get(key) is False,"unexpected completed or modified stage: "+key)
    for key in ("material_grade","epsilon_allow","Q","required_deflection_mm","delta_allow_mm","forces","physical_measurements","fit_results","physical_interference","qualified_strength_N","qualified_clearance_mm","support_required","final_print_orientation_approved","slicer_support_settings","bridge_or_support_qualified"):
        need(report.get(key) is None,"unexpected physical/material/support qualification: "+key)
    result={"schema_version":1,"passed":True,"kind":"independent_snapfit_stl_audit",
            "audited_at":datetime.now(timezone.utc).isoformat(),"run_dir":str(run_dir),
            "audit_script_sha256":digest(Path(__file__)),"verification_sha256":digest(verification_path),
            "method":"Strict low-level binary reader plus independent directed-edge topology/volume, source/STL/reimport oriented coordinate triangles and stored-normal decoding; no snapfit_stl_checks or semantic checker called.",
            "source_scene_sha256":SOURCE_SHA,"source_orientation_record_sha256":ORIENTATION_SHA,
            "input_sha256":{},"parts":{},"numeric_position_epsilon_mm":EPS,
            "epsilon_role":"Floating point reconstruction only; not manufacturing, bridge, support or printed-fit acceptance",
            "support_required":None,"support_generation_performed":False,"material_grade":None,"epsilon_allow":None,
            "forces":None,"printed":False,"fit_tested":False,"physical_measurements":None,
            "qualified_strength_N":None,"qualified_clearance_mm":None}
    candidates={}
    for entry in report["exports"]:
        kind=entry["kind"];need(kind in ("body","lid") and kind not in candidates,"duplicate or extra export")
        paths={label:run_dir/(label+"_"+kind+"_mesh.json") for label in ("source","reimport")}
        raws={label:json.loads(p.read_text(encoding="utf-8")) for label,p in paths.items()}
        for label,path in paths.items():result["input_sha256"][path.name]=digest(path)
        stl_path=Path(entry["stl_path"]);need(digest(stl_path)==entry["stl_sha256"],"STL hash changed")
        mesh=read_stl(stl_path);result["input_sha256"][stl_path.name]=mesh["stl_sha256"]
        need(mesh["byte_size"]==entry["stl_bytes"] and mesh["triangle_count"]==entry["stl_triangles"],"STL entry size/count mismatch")
        opts=entry["export_options"]
        need(opts["only_selected"] and opts["global_scale"]==1 and not opts["use_scene_unit"] and
             not opts["ascii_format"] and not opts["use_batch"] and opts["forward_axis"]=="Y" and opts["up_axis"]=="Z","wrong native export options")
        need(entry["selected_names"]==["Body" if kind=="body" else "Lid"],"wrong selected object")
        stl_compare=compare_meshes(mesh,raws["source"])
        reimport_compare=compare_meshes(raws["reimport"],mesh)
        meta=raws["reimport"]["cad_metadata"]
        need(meta["modifier_count"]==0 and all(abs(s-1)<=1e-7 for s in meta["scale"]) and
             all(abs(v)<=1e-7 for v in meta["object_location_mm"]+meta["object_rotation_euler_radians"]),"fresh reimport did not retain baked world vertices at origin0/rotation0/Scale1")
        need(abs(stl_compare["actual_topology"]["bounds_mm"]["min"][2])<=EPS,"STL no longer lands on numerical Z0")
        candidates[kind]=mesh
        result["parts"][kind]={"stl_sha256":mesh["stl_sha256"],"byte_size":mesh["byte_size"],
            "triangle_count":mesh["triangle_count"],"stl_vs_source":stl_compare,
            "reimport_vs_stl":reimport_compare,"stored_normal_diagnostics":stored_normals(stl_path)}
    need(set(candidates)=={"body","lid"},"need exactly two final part STLs")
    gap=candidates["lid"]["bounds_mm"]["min"][0]-candidates["body"]["bounds_mm"]["max"][0]
    need(abs(gap-35)<=EPS,"candidate world separation changed")
    result["x_projection_gap_mm"]=gap
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    parser.add_argument("--output",default="independent-stl-audit-v001.json");args=parser.parse_args()
    need(Path(args.output).name==args.output and args.output.endswith(".json"),"output must be a JSON basename in run_dir")
    result=audit(args.run_dir);target=args.run_dir.resolve()/args.output
    with target.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
    print(json.dumps({"passed":True,"output":str(target),"sha256":digest(target)},ensure_ascii=False))


if __name__=="__main__":main()
