import bpy,hashlib,math,json,os
from pathlib import Path
p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()=='b97a021c1422ced95b17a80893195df1907a725eb2e53789e0992a23793320ce'
o=bpy.data.objects['Body'];m=o.data;m.calc_loop_triangles();pts=[o.matrix_world@v.co for v in m.vertices];tri=min(m.loop_triangles,key=lambda t:t.area);poly=m.polygons[tri.polygon_index]; normal=poly.normal.copy();o_matrix=o.matrix_world
origin=m.vertices[poly.vertices[0]].co;dist=[abs((m.vertices[i].co-origin).dot(normal)) for i in poly.vertices];edgekeys={tuple(sorted(e.vertices)) for e in m.edges}; tri_edges=[(int(tri.vertices[i]),int(tri.vertices[(i+1)%3])) for i in range(3)];v=[pts[i] for i in tri.vertices];area=(v[1]-v[0]).cross(v[2]-v[0]).length/2
report={'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'minimumTriangleAreaMm2':area,'triangleVertices':list(tri.vertices),'triangleEdgeIsActualMeshEdge':[tuple(sorted(e)) in edgekeys for e in tri_edges],'polygonIndex':tri.polygon_index,'polygonVertexCount':len(poly.vertices),'polygonAreaMm2':poly.area,'polygonNormal':list(normal),'polygonVertices':[list(pts[i]) for i in poly.vertices],'maxPolygonPlaneDeviationMm':max(dist),'shortestRealEdgeVertices':[621,675],'explanation':'Triangle is an internal triangulation of its polygon; its area and altitude describe the tessellation, not wall thickness. Real mesh edge and polygon geometry still require independent validity checks.'}
out=Path(os.environ['MOUNT_POLYGON_AUDIT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report))
