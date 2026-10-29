"""Compare saved meshes by world-space bounds and bidirectional samples.

Sampled vertex and triangle-centroid distances are not full Hausdorff bounds.
This does not assume equal vertex or face indices and does not assert ISO fit.
"""
import bpy,bmesh,sys,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:]
reference,out=map(Path,args[:2]);obj=bpy.data.objects['Thread_Core']
with bpy.data.libraries.load(str(reference),link=False) as (src,dst):dst.objects=['Thread_Core']
ref=dst.objects[0];bpy.context.scene.collection.objects.link(ref);bpy.context.view_layer.update()
def describe(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.index_update()
    p=[o.matrix_world@v.co for v in bm.verts]
    tris=[tuple(l.vert.index for l in t) for t in bm.calc_loop_triangles()]
    tree=BVHTree.FromPolygons(p,tris,all_triangles=True,epsilon=0)
    samples=p+[(p[a]+p[b]+p[c])/3 for a,b,c in tris]
    bounds=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
    volume=bm.calc_volume(signed=True);nv=len(bm.verts);nf=len(bm.faces);bm.free()
    return tree,samples,bounds,volume,nv,nf
at,asamples,ab,av,an,af=describe(obj);bt,bsamples,bb,bv,bn,bf=describe(ref)
def distances(samples,tree):
    d=[tree.find_nearest(p)[3] for p in samples]
    return {'samples':len(d),'maxMm':max(d),'meanMm':sum(d)/len(d)}
result={'newSceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'referenceSceneSha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
 'new':{'boundsMm':ab,'signedVolumeMm3':av,'vertices':an,'faces':af},
 'reference':{'boundsMm':bb,'signedVolumeMm3':bv,'vertices':bn,'faces':bf},
 'newToReferenceSamples':distances(asamples,bt),'referenceToNewSamples':distances(bsamples,at),
 'limitations':'Only mesh vertices and triangle centroids are sampled; no complete surface-distance proof, no physical or ISO claim.'}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
