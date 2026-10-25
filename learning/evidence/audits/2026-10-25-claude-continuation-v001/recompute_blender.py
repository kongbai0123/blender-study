"""Read-only independent Blender audit. No existing checker or geometry edits."""
import bpy
import bmesh
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
OUT = Path(__file__).resolve().parent
CAT = json.loads((ROOT / 'learning/catalog.json').read_text(encoding='utf-8'))


def paths(value, suffix):
    if isinstance(value, dict):
        for item in value.values():
            yield from paths(item, suffix)
    elif isinstance(value, list):
        for item in value:
            yield from paths(item, suffix)
    elif isinstance(value, str) and value.startswith('learning/evidence/') and value.endswith(suffix):
        yield value


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_object(obj, factor):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    mesh.calc_loop_triangles()
    world = [obj.matrix_world @ v.co for v in mesh.vertices]
    xyz = [[float(x) * factor for x in p] for p in world]
    lo = [min(v[i] for v in xyz) for i in range(3)]
    hi = [max(v[i] for v in xyz) for i in range(3)]
    areas = []
    signed_volume = 0.0
    for t in mesh.loop_triangles:
        a, b, c = [world[i] for i in t.vertices]
        cross = (b-a).cross(c-a)
        area = cross.length * factor**2 / 2
        signed_volume += a.dot(b.cross(c)) * factor**3 / 6
        if area > 1e-10:
            normal = cross.normalized()
            if normal.z < -0.999999:
                areas.append({'triangle': t.index, 'area_mm2': area,
                              'vertices_mm': [xyz[i] for i in t.vertices],
                              'normal': list(normal)})
    # Topology is calculated separately from Blender's nonmanifold selection.
    adjacency = {v.index: set() for v in mesh.vertices}
    for e in mesh.edges:
        a,b=e.vertices; adjacency[a].add(b);adjacency[b].add(a)
    unseen=set(adjacency); components=0
    while unseen:
        components+=1; stack=[unseen.pop()]
        while stack:
            for other in adjacency[stack.pop()]:
                if other in unseen: unseen.remove(other);stack.append(other)
    return {'name':obj.name,'hidden':obj.hide_get(),'hide_render':obj.hide_render,
            'item_dimensions_mm':[float(x)*factor for x in obj.dimensions],
            'rotation_rad':list(obj.rotation_euler),'location_mm':[float(x)*factor for x in obj.location],
            'scale':list(obj.scale),'matrix_world':[list(row) for row in obj.matrix_world],
            'world_bounds_mm':{'min':lo,'max':hi,'dimensions':[hi[i]-lo[i] for i in range(3)]},
            'vertices':len(mesh.vertices),'edges':len(mesh.edges),'polygons':len(mesh.polygons),
            'loop_triangles':len(mesh.loop_triangles),'nonmanifold_edges':nonmanifold,
            'connected_components':components,'signed_volume_mm3':signed_volume,
            'horizontal_downward_faces':areas,
            'raw_world_vertices_mm':xyz,
            'polygons_vertex_indices':[list(p.vertices) for p in mesh.polygons]}


scenes=[]
lessons=[l for l in CAT['lessons'] if l['id'] in ['05','06','07','08']]
for rel in sorted(set(paths(lessons,'.blend'))):
    src=ROOT/rel
    before=digest(src)
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
    factor=bpy.context.scene.unit_settings.scale_length*1000
    objects=[inspect_object(obj,factor) for obj in bpy.context.scene.objects if obj.type=='MESH']
    after=digest(src)
    assert before==after, 'source changed'
    scenes.append({'path':rel,'sha256_before':before,'sha256_after':after,
                   'unit_factor_to_mm':factor,'objects':objects})

result={'schemaVersion':1,'method':'separate Blender --background --factory-startup --disable-autoexec; open_mainfile load_ui=False; independent bpy/bmesh readback; no save or geometry edits; no existing project checkers imported',
        'blenderVersion':bpy.app.version_string,'buildHash':bpy.app.build_hash.decode(),
        'scenes':scenes,'numeric_epsilon_mm':1e-4,
        'epsilonMeaning':'floating point reconstruction only, not manufacturing tolerance',
        'physicalPrintResult':None,'physicalFitResult':None,'qualifiedStrength':None,'qualifiedFit':None}

def scene(fragment): return next(s for s in scenes if fragment in s['path'])
hole_scene=scene('u05_hole_plate_v001.blend')
hole_objects=hole_scene['objects']
result['holeplate_object_names']=[o['name'] for o in hole_objects]
plate=next(o for o in hole_objects if o['name']=='Plate')
# Infer circular recess groups from their actual vertical mesh faces, not draft inputs.
recess_vertices=[v for v in plate['raw_world_vertices_mm'] if abs(v[2]-1.2)<1e-4]
result['holeplate_recess_floor_vertices_mm']=recess_vertices
dovetail=scene('u06_dovetail_slide_v001.blend')
body=next(o for o in dovetail['objects'] if o['name']=='Body')
ledges=[t for t in body['horizontal_downward_faces'] if all(abs(v[2]-10)<1e-4 for v in t['vertices_mm'])]
result['dovetail_inward_ledge']={'worldZ_mm':10,'triangles':ledges,'area_total_mm2':sum(t['area_mm2'] for t in ledges),
    'method':'actual Body world triangles with normal -Z at Z10, excluding bed and other faces; two inward exposed ledges, not entire construction tool length',
    'supports_required_or_final_orientation_determined':False}
result['source_files_unchanged']=True
with (OUT/'blender-readback-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print('AUDIT_COMPLETED scenes='+str(len(scenes))+' ledge_area_mm2='+str(result['dovetail_inward_ledge']['area_total_mm2']),flush=True)
