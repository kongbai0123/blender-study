"""Read-only bounds of actual open box/lid scene; does not write the scene."""
import bpy, json, hashlib
objects={}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    coords=[obj.matrix_world@v.co for v in obj.data.vertices]
    faces=sorted(tuple(sorted(tuple(round(float(coords[v][i]),6) for i in range(3)) for v in f.vertices)) for f in obj.data.polygons)
    fingerprint=hashlib.sha256(json.dumps(faces,separators=(',',':')).encode()).hexdigest()
    objects[obj.name]={'worldBoundsMm':[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)],'vertices':len(coords),'location':list(obj.location),'scale':list(obj.scale),'worldFaceVertexSetSha256':fingerprint}
print('MOUNT_REFERENCE_JSON',json.dumps({'blender':bpy.app.version_string,'unitScale':bpy.context.scene.unit_settings.scale_length,'objects':objects},ensure_ascii=False))
