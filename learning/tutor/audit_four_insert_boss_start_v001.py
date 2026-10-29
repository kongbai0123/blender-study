"""Read-only audit of prepared-tools start scene and untouched source box/lid."""
import bpy,bmesh,json,hashlib,sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1])
NAMES=['Body','Lid','zz_Boss_Pillars','zz_Boss_Ribs_X','zz_Boss_Ribs_Y','zz_Boss_Pilot_Tools','zz_Boss_Lid_Tools']
def audit(name):
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);pts=[o.matrix_world@v.co for v in o.data.vertices]
 faces=sorted(tuple(sorted(tuple(round(float(pts[i][j]),6) for j in range(3)) for i in f.vertices)) for f in o.data.polygons)
 rem=set(bm.verts);components=0
 while rem:
    components+=1;stack=[rem.pop()]
    while stack:
        for edge in stack.pop().link_edges:
            for v in edge.verts:
                if v in rem:rem.remove(v);stack.append(v)
 result={'worldFaceVertexSetSha256':hashlib.sha256(json.dumps(faces,separators=(',',':')).encode()).hexdigest(),
   'worldBoundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
   'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,
   'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),
   'hidden':o.hide_get(),'modifiers':[m.type for m in o.modifiers]}
 bm.free();return result
result={'sceneSha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'blenderVersion':bpy.app.version_string,'objects':{n:audit(n) for n in NAMES},
 'limitations':['Tools were program-prepared; source body and lid are geometrically unmodified.',
                'Disconnected tools are intentional before Boolean; actual print and fit are not tested.']}
out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
assert result['objects']['Body']['worldFaceVertexSetSha256']=='14aadcea96872f701a71b38280cf1a6788a13a3b45574e083930e46e3541e58b'
assert result['objects']['Lid']['worldFaceVertexSetSha256']=='95fe03fdbe5e99141156cbb018cca4407c275b06359930d43776ccec69241c00'
assert all(result['objects'][n]['components']==4 and not result['objects'][n]['nonManifoldEdges'] for n in NAMES[2:])
