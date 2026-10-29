"""獨立背景 Blender 複核 GUI Difference 之內牙試塊，輸出至指定 evidence 目錄。"""
import hashlib
import json
import math
import os
from pathlib import Path
import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

EXPECTED='a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80'
file=Path(bpy.data.filepath)
if hashlib.sha256(file.read_bytes()).hexdigest()!=EXPECTED:raise RuntimeError('場景 hash 不符')
obj=bpy.data.objects['Cube'];bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
nonmanifold=sum(not e.is_manifold for e in bm.edges); tree=BVHTree.FromBMesh(bm)
def target(z,theta):
    phase=(z-theta/(2*math.pi))%1
    return 5+(phase/.3 if phase<=.3 else (1-(phase-.3)/.3 if phase<=.6 else 0))
samples=[]
for z in (1.3,2.3):
    for angle in (0,math.pi/2,math.pi,3*math.pi/2):
        direction=Vector((math.cos(angle),math.sin(angle),0))
        hit,normal,face,distance=tree.ray_cast(Vector((0,0,z)),direction,20)
        value=(hit.xy.length if hit else None);expected=target(z,angle)
        samples.append({'zMm':z,'angleDeg':angle*180/math.pi,'actualRadiusMm':value,'expectedRadiusMm':expected})
checks={'closedEdges':nonmanifold==0,'eightRadialSamples':all(s['actualRadiusMm'] is not None and abs(s['actualRadiusMm']-s['expectedRadiusMm'])<.04 for s in samples)}
res={'sceneSha256':EXPECTED,'method':'獨立重開場景，從孔中心沿四角度和兩個軸向位置作徑向射線抽樣','samples':samples,'nonManifoldEdges':nonmanifold,'checks':checks,
     'limitations':['僅抽樣，不證明完整表面、無自交、製造或配合合格','工具牙由程式預建，無間隙補償','實體列印、量測與試配未執行']}
bm.free();Path(os.environ['INNER_AUDIT_OUT']).write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if not all(checks.values()):raise RuntimeError('獨立複核未通過 '+str(checks))
print('checks',checks)
