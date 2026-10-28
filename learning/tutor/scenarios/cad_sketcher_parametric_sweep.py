"""Programmatically vary each independent property in memory; never save source.

Run in isolated Blender background with -- <scene.blend> <output.json>.
This is a numeric validation, not a GUI operation or a physical fit test.
"""
import json
import sys
from pathlib import Path
import addon_utils
import bpy
import bmesh

source,out=(Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:])
addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
depth_key=next(k for k in scene.keys() if k.startswith('slvs:c:') and abs(scene[k]-40)<1e-5)
def geometry(name):
    obj=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=obj.to_mesh()
    points=[obj.matrix_world@p.co for p in mesh.vertices]
    bm=bmesh.new();bm.from_mesh(mesh); nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    obj.to_mesh_clear()
    return points,nonmanifold
def close(a,b): return abs(a-b)<1e-4
def run(label,key,value):
    previous=scene[key]
    scene[key]=value; scene.update_tag(); bpy.context.view_layer.update()
    body,nb=geometry('Parametric Box'); lid,nl=geometry('Parametric Lid')
    L=80.; W=scene[depth_key]; H=scene['box_height_mm']; T=scene['box_wall_mm']; B=scene['box_bottom_mm']
    P=scene['lid_plate_mm']; D=scene['lid_depth_mm']; C=scene['gap_total_mm']; S=scene['lid_lip_wall_mm']
    bounds=lambda pts,i: [min(p[i] for p in pts),max(p[i] for p in pts)]
    cavity=[bounds(body[8:12],i) for i in range(2)]
    lip=[bounds(lid[8:12],i) for i in range(2)]
    inner=[bounds(lid[16:20],i) for i in range(2)]
    actual={'box': [bounds(body,i) for i in range(3)],'lid':[bounds(lid,i) for i in range(3)],
            'cavityXY':cavity,'lipOuterXY':lip,'lipInnerXY':inner,'floorZ':body[12].z,
            'nonManifoldEdges':[nb,nl]}
    def rows_equal(actual,expected): return all(close(a,b) for row1,row2 in zip(actual,expected) for a,b in zip(row1,row2))
    checks={'box':rows_equal(actual['box'],[[0,L],[0,W],[0,H]]),
            'lid':rows_equal(actual['lid'],[[0,L],[0,W],[H-D,H+P]]),
            'cavity':rows_equal(cavity,[[T,L-T],[T,W-T]]),
            'lipOuter':rows_equal(lip,[[T+C/2,L-T-C/2],[T+C/2,W-T-C/2]]),
            'lipInner':rows_equal(inner,[[T+C/2+S,L-T-C/2-S],[T+C/2+S,W-T-C/2-S]]),
            'floor':close(actual['floorZ'],B),'closed':nb==0 and nl==0}
    scene[key]=previous;scene.update_tag();bpy.context.view_layer.update()
    return {'label':label,'property':key,'testValue':value,'checks':checks,'actual':actual}
items=[('sketch-Y',depth_key,50.),('height','box_height_mm',35.),('wall','box_wall_mm',3.),
       ('bottom','box_bottom_mm',3.),('plate','lid_plate_mm',3.),('lip-depth','lid_depth_mm',5.),
       ('clearance','gap_total_mm',.6),('lip-wall','lid_lip_wall_mm',3.)]
cases=[run(*item) for item in items]
result={'method':'independent in-memory Python changes on one saved scene; not GUI and no save',
        'sourceSaved':False,'cases':cases,'allPassed':all(all(c['checks'].values()) for c in cases),
        'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
if not result['allPassed']: raise RuntimeError('Parameter sweep failed')
