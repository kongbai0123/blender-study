"""Native GUI STL export and actual GUI reimport in isolated Blender.

Source scenes are copied. The file-browser path and filename are filled by
Python; object selection, export/import menus, confirm and hide use GUI events.
STL has no embedded units; here exported coordinates are interpreted as mm.
"""
import hashlib,json,math,struct,os,tempfile,shutil
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from common import Kit,PROJECT

def build(g,cfg):
    k=Kit(g);out=Path(g['OUT']);source=PROJECT/cfg['source'];source_hash=cfg['sha256']
    if g['sha256'](source)!=source_hash:raise RuntimeError('Source SHA mismatch')
    copies=Path(k.demo_dir)/'sources';repository_exports=Path(k.demo_dir)/'exports';copies.mkdir();repository_exports.mkdir()
    public_parent=Path(os.environ.get('PUBLIC',r'C:\Users\Public'))/'Documents'
    if not public_parent.is_dir():raise RuntimeError('Public Documents unavailable')
    exports=Path(tempfile.mkdtemp(prefix='BlenderStudy_',dir=str(public_parent)))
    copied=copies/source.name;copied.write_bytes(source.read_bytes());state={}
    def send(key,**kw):k.do(lambda:k.key(key,x=700,y=500,**kw),.45)
    def search(s):send('F3');k.do(lambda:k.type_text(s),.35);send('RET')
    def unchanged():
        k.guard()
        if g['sha256'](source)!=source_hash or g['sha256'](copied)!=source_hash:raise RuntimeError('source copy changed')
    def op():return k.window('FILE_BROWSER').screen.areas[0].spaces.active.active_operator
    def hide_file_browser_sidebar():
        # Hide real OS shortcuts in the live Blender file browser; pixels are
        # never cropped, blurred, overwritten, or otherwise edited.
        w=k.window('FILE_BROWSER');space=w.screen.areas[0].spaces.active;space.show_region_toolbar=False
    def options(export):
        operator=op();p=operator.properties
        data={'operator':operator.bl_idname,'globalScale':float(p.global_scale),'sceneUnit':bool(p.use_scene_unit),'forwardAxis':p.forward_axis,'upAxis':p.up_axis}
        if export:data.update(selectionOnly=bool(p.export_selected_objects),applyModifiers=bool(p.apply_modifiers),binary=not bool(p.ascii_format),batch=bool(p.use_batch))
        return data
    def scene_mesh(obj):
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world)
        pts=[v.co.copy() for v in bm.verts]; tris=bm.calc_loop_triangles();areas=[((t[1].vert.co-t[0].vert.co).cross(t[2].vert.co-t[0].vert.co)).length/2 for t in tris]
        data={'object':obj.name,'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':len(tris),
              'boundsMm':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
              'signedVolumeMm3':bm.calc_volume(signed=True),'minimumTriangleAreaMm2':min(areas),
              'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges)}
        bm.free();return data
    def binary_read(p):
        raw=p.read_bytes()
        if len(raw)<84:raise RuntimeError('truncated binary STL')
        n=struct.unpack_from('<I',raw,80)[0]
        if n==0 or len(raw)!=84+50*n:raise RuntimeError('bad binary STL length')
        bounds=[[float('inf'),-float('inf')] for _ in range(3)];minimum=float('inf');zeros=0;seen={};duplicates=[]
        for i in range(n):
            vals=struct.unpack_from('<12fH',raw,84+i*50)
            if not all(math.isfinite(v) for v in vals[:12]):raise RuntimeError('nonfinite STL')
            a,b,c=(Vector(vals[j:j+3]) for j in (3,6,9))
            area=(b-a).cross(c-a).length/2;minimum=min(minimum,area);zeros+=int(area==0)
            signature=tuple(sorted((tuple(a),tuple(b),tuple(c))))
            if signature in seen:duplicates.append({'firstTriangle':seen[signature],'duplicateTriangle':i,'verticesMm':[list(v) for v in signature],'areaMm2':area})
            else:seen[signature]=i
            for v in (a,b,c):
                for axis in range(3):bounds[axis][0]=min(bounds[axis][0],v[axis]);bounds[axis][1]=max(bounds[axis][1],v[axis])
        return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'triangles':n,'boundsMm':bounds,'minimumTriangleAreaMm2':minimum,'exactZeroAreaTriangles':zeros,'exactDuplicateTriangleCount':len(duplicates),'exactDuplicateTriangles':duplicates,'interpretation':'binary STL has no unit declaration; coordinates interpreted as mm; duplicates use exact unordered vertex coordinates'}
    def selected(p):
        unchanged();o=bpy.context.view_layer.objects.active
        if o is None or o.name!=p['object'] or [v.name for v in bpy.context.selected_objects]!=[p['object']]:raise RuntimeError('not exactly target selected')
        if bpy.context.scene.unit_settings.system!='METRIC' or abs(bpy.context.scene.unit_settings.scale_length-.001)>1e-7:raise RuntimeError('source units differ')
        state[p['id']]={'source':scene_mesh(o),'unitScale':float(bpy.context.scene.unit_settings.scale_length)}
        return json.dumps(state[p['id']]['source'])
    def check_export(p):
        unchanged();actual=options(True)
        expected={'operator':'WM_OT_stl_export','globalScale':1.0,'sceneUnit':False,'forwardAxis':'Y','upAxis':'Z','selectionOnly':True,'applyModifiers':True,'binary':True,'batch':False}
        if actual!=expected or [v.name for v in bpy.context.selected_objects]!=[p['object']]:raise RuntimeError('export settings/selection differ '+json.dumps(actual))
        folder,name=k.browser();dest=Path(folder)/name
        if dest.parent.resolve()!=exports.resolve() or name!=p['filename'] or dest.exists():raise RuntimeError('unsafe target')
        state[p['id']]['exportOptions']=actual;return json.dumps(actual)
    def exported(p):
        unchanged();r=binary_read(exports/p['filename']);source_mesh=state[p['id']]['source']
        if r['triangles']!=source_mesh['triangles'] or any(abs(a-b)>1e-4 for row,orig in zip(r['boundsMm'],source_mesh['boundsMm']) for a,b in zip(row,orig)):raise RuntimeError('binary STL/source differ')
        state[p['id']]['stl']=r;return json.dumps(r)
    def check_import(p):
        o=options(False);expected={'operator':'WM_OT_stl_import','globalScale':1.0,'sceneUnit':False,'forwardAxis':'Y','upAxis':'Z'}
        if o!=expected:raise RuntimeError('import options differ '+json.dumps(o))
        folder,name=k.browser()
        if (Path(folder)/name).resolve()!=(exports/p['filename']).resolve():raise RuntimeError('wrong import file')
        state[p['id']]['importOptions']=o;state[p['id']]['beforeImportNames']=list(bpy.data.objects.keys());return json.dumps(o)
    def imported(p):
        unchanged();s=state[p['id']];new=set(bpy.data.objects.keys())-set(s['beforeImportNames']);o=bpy.context.view_layer.objects.active
        if o is None or o.name not in new or o.type!='MESH':raise RuntimeError('native import did not produce selected new mesh')
        m=scene_mesh(o);binary=s['stl'];source_mesh=s['source']
        bounds_match=not any(abs(a-b)>1e-4 for row,orig in zip(m['boundsMm'],binary['boundsMm']) for a,b in zip(row,orig))
        volumes_match=math.isclose(m['signedVolumeMm3'],source_mesh['signedVolumeMm3'],rel_tol=1e-5,abs_tol=1e-4)
        lost=binary['triangles']-m['triangles']
        s['comparison']={'boundsMatchAt1eMinus4Mm':bounds_match,'signedVolumeMatches':volumes_match,
            'stlTriangleCount':binary['triangles'],'reimportTriangleCount':m['triangles'],'trianglesRemoved':lost,
            'binaryExactDuplicateTriangleCount':binary['exactDuplicateTriangleCount'],
            'status':'exact-count-match' if bounds_match and volumes_match and not lost else 'warning-geometry-difference-investigate',
            'interpretation':('Binary file contains exact duplicates and the importer may remove them.' if binary['exactDuplicateTriangleCount'] else 'No exact duplicate triangles found in binary STL.')+' Counts alone do not prove full surface equivalence or print readiness.'}
        s['reimport']=m;s['sourceSceneSha256']=source_hash;s['numericComparison']='1e-4 mm coordinate / 1e-5 relative volume for numerical reconstruction, not engineering tolerance'
        s.update(physicalPrint=None,physicalMeasurement=None,physicalFit=None,qualifiedClearance=None,qualifiedStrength=None)
        # Copy the real GUI-exported bytes into the evidence directory, then
        # delete just this temporary file; verify byte-for-byte identity first.
        temporary=exports/p['filename'];destination=repository_exports/p['filename']
        if destination.exists():raise RuntimeError('evidence target exists')
        shutil.copyfile(temporary,destination)
        if hashlib.sha256(destination.read_bytes()).hexdigest()!=binary['sha256']:raise RuntimeError('copied STL differs')
        s['evidenceCopyVerifiedSha256']=binary['sha256'];s['pathHandling']='GUI exported and reimported from Public Documents temporary folder; byte-identical STL copied into evidence; live file browser sidebar hidden for privacy.'
        temporary.unlink()
        (out/(p['id']+'-verification.json')).write_text(json.dumps(s,indent=2),encoding='utf8')
        return json.dumps(m)
    def ensure_outliner():
        area=k.area('OUTLINER')
        if area.height<270:
            divider=k.window().height-area.y;k.drag_slow([(1305,divider),(1305,divider+120)],button='LEFTMOUSE')
    k.setup();k.do(lambda:setattr(bpy.context.preferences.view,'use_save_prompt',False),.1)
    for part in cfg['parts']:
        send('O',ctrl=True);k.fill_dialog(str(copies)+'\\',copied.name);k.confirm_dialog(wait=3);k.do(ensure_outliner,.3)
        k.click_outliner(part['object']);search('Frame Selected')
        k.record('STL',part['id']+'-selected','GUI 選取單一目標物件並讀回來源世界尺寸。',lambda p=part:selected(p))
        k.do(lambda:k.click(40,13),.5);k.do(lambda:k.move(73,317),.6);k.do(lambda:k.move(288,436),.4)
        k.record('STL',part['id']+'-menu','GUI File > Export > STL；僅目標物件已選中。',lambda:k.selection())
        k.menu_item(288,436,1.2);k.fill_dialog(str(exports)+'\\',part['filename']);k.do(hide_file_browser_sidebar,.5)
        def selection_only():
            if not op().properties.export_selected_objects:k.click(929,159,win='FILE_BROWSER')
        k.do(selection_only,.6)
        k.record('STL',part['id']+'-options','GUI 核對 Selection Only、Scale 1、Scene Unit 關閉，並另存 STL。',lambda p=part:check_export(p),win='FILE_BROWSER',park=(300,400))
        k.confirm_dialog(1.6)
        k.record('STL',part['id']+'-binary','讀取剛輸出的 STL 原始二進位檔，對照來源世界外框。',lambda p=part:exported(p))
        send('H');search('Import STL');k.fill_dialog(str(exports)+'\\',part['filename']);k.do(hide_file_browser_sidebar,.5)
        k.record('STL',part['id']+'-import-options','GUI 匯入剛才 STL，核對 Scale 1 與 Scene Unit 關。',lambda p=part:check_import(p),win='FILE_BROWSER',park=(300,400))
        k.confirm_dialog(2);search('Frame Selected')
        k.record('STL',part['id']+'-reimported','GUI 實際匯入 STL，讀回新網格的尺寸與拓樸。',lambda p=part:imported(p))
    def cleanup():
        if exports.parent.resolve()!=public_parent.resolve() or not exports.name.startswith('BlenderStudy_'):raise RuntimeError('unexpected temp path')
        exports.rmdir()
    k.do(cleanup,.2)
