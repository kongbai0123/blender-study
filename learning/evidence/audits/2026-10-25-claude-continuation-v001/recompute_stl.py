"""Independent standard-library binary STL and selected geometry audit."""
import hashlib
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
READ=json.loads((OUT/'blender-readback-v001.json').read_text(encoding='utf-8'))
CAT=json.loads((ROOT/'learning/catalog.json').read_text(encoding='utf-8'))

def find(value):
    if isinstance(value,dict):
        for x in value.values():yield from find(x)
    elif isinstance(value,list):
        for x in value:yield from find(x)
    elif isinstance(value,str) and value.startswith('learning/evidence/') and value.endswith('.stl'):yield value

def sub(a,b):return [a[i]-b[i] for i in range(3)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def length(a):return math.sqrt(dot(a,a))

def source(name):
    mapping={
      'u05_fit_coupon_v001.stl':('u05_fit_coupon_v001.blend','FitCoupon'),
      'u05_hole_plate_v001.stl':('u05_hole_plate_v001.blend','Plate'),
      'u05_lid_v001.stl':('u05_lid_v001.blend','Lid'),
      'u06_dovetail_body_v001.stl':('u06_dovetail_slide_v001.blend','Body'),
      'u06_dovetail_lid_v001.stl':('u06_dovetail_slide_v001.blend','SlidingLid'),
      'u07_snap_body_v001.stl':('u07_print_orientation_v001.blend','Body'),
      'u07_snap_lid_v001.stl':('u07_print_orientation_v001.blend','Lid'),
      'u07_A_L19_v001.stl':('u07_cantilever_length_coupons_v001.blend','A_L19'),
      'u07_B_L17_v001.stl':('u07_cantilever_length_coupons_v001.blend','B_L17'),
      'u07_C_L21_v001.stl':('u07_cantilever_length_coupons_v001.blend','C_L21')}
    scene_name,object_name=mapping[name]
    s=next(s for s in READ['scenes'] if s['path'].endswith('/'+scene_name))
    # The pin's original name is recovered explicitly below if necessary.
    candidates=[o for o in s['objects'] if o['name']==object_name]
    if not candidates and name=='u05_fit_coupon_v001.stl':
        assert len(s['objects'])==1
        candidates=s['objects']
    return s,candidates[0]

records=[]
for rel in sorted(set(find([l for l in CAT['lessons'] if l['id'] in ['05','06','07','08']]))):
    path=ROOT/rel; raw=path.read_bytes(); n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*n
    triangles=[]; stored=[]
    for i in range(n):
        t=struct.unpack_from('<12fH',raw,84+50*i)
        stored.append(t[:3]);triangles.append([t[3:6],t[6:9],t[9:12]])
    allv=[v for t in triangles for v in t]
    lo=[min(v[k] for v in allv) for k in range(3)]
    hi=[max(v[k] for v in allv) for k in range(3)]
    def key(v):return tuple(round(x/1e-5) for x in v)
    edges=Counter();directions=Counter();adj=defaultdict(set);volume=0.;normal_bad=0;degenerate=0;ledge=[]
    for index,(t,normal) in enumerate(zip(triangles,stored)):
        a,b,c=t;cr=cross(sub(b,a),sub(c,a));area=length(cr)/2
        volume+=dot(a,cross(b,c))/6
        if area<1e-10:degenerate+=1
        elif dot(cr,normal)<=0:normal_bad+=1
        keys=[key(v) for v in t]
        for va,vb in zip(keys,keys[1:]+keys[:1]):
            edges[tuple(sorted([va,vb]))]+=1;directions[(va,vb)]+=1;adj[va].add(vb);adj[vb].add(va)
        if path.name=='u06_dovetail_body_v001.stl' and cr[2]<0 and abs(cr[0])+abs(cr[1])<1e-5 and all(abs(v[2]-10)<1e-4 for v in t):
            ledge.append({'index':index,'area_mm2':area,'vertices_mm':t})
    unseen=set(adj);components=0
    while unseen:
        components+=1;stack=[unseen.pop()]
        while stack:
            for v in adj[stack.pop()]:
                if v in unseen:unseen.remove(v);stack.append(v)
    nonmanifold=sum(c!=2 for c in edges.values())
    inconsistent=sum(directions[(b,a)]!=c for (a,b),c in directions.items())
    scene,obj=source(path.name)
    bounds={'min':lo,'max':hi,'dimensions':[hi[i]-lo[i] for i in range(3)]}
    max_bounds_error=max(abs(bounds[k][i]-obj['world_bounds_mm'][k][i]) for k in ['min','max'] for i in range(3))
    volume_error=abs(volume-obj['signed_volume_mm3'])
    assert max_bounds_error<1e-4
    assert volume_error<max(1e-3,abs(volume)*1e-6)
    assert nonmanifold==inconsistent==degenerate==normal_bad==0 and components==1
    result={'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'triangles':n,'unit_policy':'STL has no unit field; numeric coordinates interpreted as mm in this project',
         'bounds_mm':bounds,'volume_mm3':volume,'weld_epsilon_mm':1e-5,'nonmanifold_edges':nonmanifold,'orientation_inconsistencies':inconsistent,'components':components,
         'degenerate_triangles':degenerate,'bad_stored_normals':normal_bad,'source_scene':scene['path'],'source_scene_sha256':scene['sha256_before'],'source_object':obj['name'],
         'max_bounds_error_mm':max_bounds_error,'volume_difference_mm3':volume_error,'dimensions_and_topology_consistent':True}
    if ledge:result['dovetail_ledge']={'triangles':ledge,'area_total_mm2':sum(t['area_mm2'] for t in ledge)}
    records.append(result)

hole_scene=next(s for s in READ['scenes'] if s['path'].endswith('/u05_hole_plate_v001.blend'))
plate=next(o for o in hole_scene['objects'] if o['name']=='Plate')
verts=plate['raw_world_vertices_mm']; floors=[]
for poly in plate['polygons_vertex_indices']:
    points=[verts[i] for i in poly]
    if all(abs(v[2]-1.2)<1e-4 for v in points):
        lo=[min(v[k] for v in points) for k in range(3)];hi=[max(v[k] for v in points) for k in range(3)]
        center=[(lo[k]+hi[k])/2 for k in range(3)]
        floors.append({'center_mm':center,'x_diameter_mm':hi[0]-lo[0],'y_diameter_mm':hi[1]-lo[1]})
assert len(floors)==21
gaps=[]
for i,a in enumerate(floors):
    for b in floors[i+1:]:
        ca,cb=a['center_mm'],b['center_mm'];d=math.dist(ca[:2],cb[:2])
        gaps.append({'centers_mm':[ca,cb],'center_distance_mm':d,'gap_from_x_radii_mm':d-(a['x_diameter_mm']+b['x_diameter_mm'])/2})
nearest=min(gaps,key=lambda x:x['gap_from_x_radii_mm'])
cutters=next(o for o in hole_scene['objects'] if o['name']=='Cutters')
tenon_scene=next(s for s in READ['scenes'] if s['path'].endswith('/u06_locating_tenon_v001.blend'))
tenon=next(o for o in tenon_scene['objects'] if o['name']=='TenonTool')
out={'schemaVersion':1,'method':'independent stdlib struct/triangle cross products/edge adjacency, compared with new Blender readback; existing audit/checker modules not imported',
     'stls':records,'count':len(records),'holeplate':{'recesses':floors,'nearest_recess_pair':nearest,'cutters_item_dimensions_mm':cutters['item_dimensions_mm'],
     'display_rounding_explanation':'X80.3500099 mm rounds to 80.4 mm at one decimal; nominal combined extent 80.35 mm, not a geometry mismatch',
     'nozzle_mm':0.4,'line_width_mm':None,'single_line_printability_or_merged_recesses_assessed':False},
     'tenon':{'construction_height_mm':tenon['world_bounds_mm']['dimensions'][2],
               'free_height_above_inner_floor_mm':tenon['world_bounds_mm']['max'][2]-(-13),'nominal_diameter_mm':4,
               'free_slenderness_nominal':29.5/4,'overconstraint_is_potential_not_measured_failure':True},
     'physicalPrintResult':None,'physicalFitResult':None,'qualifiedFit':None,'qualifiedStrength':None}
with (OUT/'stl-and-geometric-checks-v001.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print('STL_AUDIT_COMPLETED',len(records),'nearest_recess_gap_mm',nearest['gap_from_x_radii_mm'])
