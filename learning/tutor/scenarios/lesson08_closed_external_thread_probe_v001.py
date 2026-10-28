"""Isolated closed helical radial mesh probe; setup is scripted, verification uses Blender UI.

It is a nonstandard educational draft, not an ISO thread, printing or fit validation.
The generated mesh is not presented as a hand-drawn GUI modeling workflow.
"""
import hashlib
import json
import math
from pathlib import Path
import bpy
import bmesh
from common import Kit, PROJECT

SOURCE = PROJECT / 'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
SOURCE_SHA = '9bda36c10fd916ef9cbe688f5ca56dcf8cfa0adb83d684300e60196225589d8f'
NAME = 'External_Thread_Draft'
SCENE = 'u08_closed_external_thread_probe_v001.blend'
N_ANGLE = 32
N_Z = 80


def radius(z, theta):
    # Single-start repeating triangular crest with flat root; clipped by z=0 and z=4.
    phase = (z - theta / (2 * math.pi)) % 1.0
    return 5.0 + (phase / .3 if phase <= .3 else (1.0 - (phase - .3) / .3 if phase <= .6 else 0.0))


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    snap = out / 'source-snapshot'
    snap.mkdir()
    files = []
    for rel in ('learning/tutor/run_demo.py', 'learning/tutor/blender_demo.py',
                'learning/tutor/scenarios/common.py', 'learning/tutor/scenarios/lesson08_closed_external_thread_probe_v001.py'):
        src = PROJECT / rel
        dst = snap / src.name
        dst.write_bytes(src.read_bytes())
        files.append({'source': rel, 'snapshot': dst.name, 'sha256': g['sha256'](dst)})
    (snap / 'manifest.json').write_text(json.dumps(files, indent=2), encoding='utf-8')
    if g['sha256'](SOURCE) != SOURCE_SHA:
        raise RuntimeError('source reference SHA mismatch')
    copy = Path(k.demo_dir) / SOURCE.name
    copy.write_bytes(SOURCE.read_bytes())
    if g['sha256'](copy) != SOURCE_SHA:
        raise RuntimeError('reference copy SHA mismatch')

    def send(key, **kw):
        k.do(lambda: k.key(key, x=700, y=500, **kw), .5)

    def prepare():
        scene = bpy.context.scene
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = .001
        scene.unit_settings.length_unit = 'MILLIMETERS'
        bpy.data.objects['Body_Reference'].hide_set(True)
        vertices = []
        for zi in range(N_Z + 1):
            z = zi * .05
            for j in range(N_ANGLE):
                t = j * 2 * math.pi / N_ANGLE
                r = radius(z, t)
                vertices.append((r * math.cos(t), r * math.sin(t), z))
        faces = []
        for zi in range(N_Z):
            for j in range(N_ANGLE):
                n = (j + 1) % N_ANGLE
                a, b = zi * N_ANGLE + j, zi * N_ANGLE + n
                faces.append((a, b, b + N_ANGLE, a + N_ANGLE))
        faces.append(tuple(reversed(range(N_ANGLE))))
        faces.append(tuple(N_Z * N_ANGLE + j for j in range(N_ANGLE)))
        mesh = bpy.data.meshes.new('Radial_Helix_Closed_Draft')
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(NAME, mesh)
        scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()

    def measure(label):
        obj = bpy.data.objects.get(NAME)
        if obj is None or obj.type != 'MESH':
            raise RuntimeError('draft object missing')
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        boundary = sum(e.is_boundary for e in bm.edges)
        nonmanifold = sum(not e.is_manifold for e in bm.edges)
        volume = bm.calc_volume(signed=True)
        bm.free()
        verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        zmin, zmax = min(v.z for v in verts), max(v.z for v in verts)
        radii = [math.hypot(v.x, v.y) for v in verts]
        # Read sample radii at the same angle for phase shift across four turns.
        phase = [math.hypot(verts[zi * N_ANGLE].x, verts[zi * N_ANGLE].y)
                 for zi in (6, 26, 46, 66)]
        result = {'stage': label, 'sourceSceneSha256': SOURCE_SHA, 'object': NAME,
                  'construction': 'scripted radial graph with planar z-end caps; GUI is used for selection, inspection and save/reopen',
                  'modelParameters': {'rootRadiusMm': 5, 'crestRadiusMm': 6,
                      'profileZMm': [0, .3, .6], 'pitchMm': 1, 'starts': 1,
                      'clipPlaneZMm': [0, 4], 'angularSegments': N_ANGLE, 'axialIntervals': N_Z},
                  'readback': {'vertices': len(verts), 'edges': len(obj.data.edges),
                      'polygons': len(obj.data.polygons), 'zMinMaxMm': [zmin, zmax],
                      'radiusMinMaxMm': [min(radii), max(radii)], 'phaseSampleRadiusMm': phase,
                      'boundaryEdges': boundary, 'nonManifoldEdges': nonmanifold,
                      'signedVolumeMm3': volume},
                  'limitations': ['programmatically generated, not hand-built GUI steps',
                      'clipped ends have incomplete thread; no counterpart, entry lead-in or fastener standard',
                      'non-manifold edge count is not a complete self-intersection or printability test',
                      'no material, clearance, slicing, print, fit or strength validation'],
                  'physical': {'printed': False, 'fitTested': False, 'qualifiedClearanceMm': None,
                      'material': None, 'qualifiedStrength': None}}
        checks = {'vertexCount': len(verts) == (N_Z + 1) * N_ANGLE,
                  'boundsZ': abs(zmin) < 1e-5 and abs(zmax - 4) < 1e-5,
                  'rootRadius': abs(min(radii)-5) < 1e-4,
                  'crestRadius': abs(max(radii)-6) < 1e-4,
                  'fourCrestsAtSamePhase': all(abs(r-6)<1e-4 for r in phase),
                  'zeroBoundaryAndNonmanifoldEdges': boundary == 0 and nonmanifold == 0,
                  'positiveVolume': volume > 0}
        result['checks'] = checks
        (out / (label + '-verification.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        if not all(checks.values()):
            raise RuntimeError('closed mesh verification failed: ' + json.dumps(checks))
        return result

    k.setup()
    send('O', ctrl=True)
    k.fill_dialog(k.demo_dir, copy.name)
    k.confirm_dialog(wait=3)
    k.do(prepare, 1)
    k.record('08-CLOSED', 'programmatic-geometry', '程式產生閉合徑向螺旋草案及端面，原盒暫時隱藏；非 GUI 手工建模', lambda: measure('before'))
    send('F3')
    k.do(lambda: k.type_text('Frame Selected'), .4)
    send('RET')
    send('NUMPAD_2')
    send('NUMPAD_2')
    k.record('08-CLOSED', 'framed', 'GUI 透過 Frame Selected 與視角鍵觀察；數值與閉合性另以網格讀回', lambda: measure('framed'))
    send('TAB')
    send('TWO')
    send('A', alt=True)
    send('F3')
    k.do(lambda: k.type_text('Select Non Manifold'), .4)
    send('RET')
    def gui_selected():
        obj = bpy.data.objects[NAME]
        bm = bmesh.from_edit_mesh(obj.data)
        selected = sum(edge.select for edge in bm.edges)
        actual = sum(not edge.is_manifold for edge in bm.edges)
        if selected != 0 or actual != 0:
            raise RuntimeError('GUI edge selection or topology check failed')
        return {'selectedNonManifoldEdges': selected, 'actualNonManifoldEdges': actual,
                'note': 'not a complete self-intersection, printing or fit test'}
    k.record('08-CLOSED', 'non-manifold', 'GUI 邊選取、清除選取、F3 > Select Non Manifold；讀回選取與實際邊數', gui_selected)
    send('TAB')
    k.file_dialog(163, k.demo_dir, SCENE)
    k.confirm_dialog(wait=3)
    k.record('08-CLOSED', 'saved', 'GUI Save As 另存草案；檔案視窗路徑由程式填入', lambda: measure('saved'))
    send('O', ctrl=True)
    k.fill_dialog(k.demo_dir, SCENE)
    k.confirm_dialog(wait=4)
    k.record('08-CLOSED', 'reopened', 'GUI Open 重開並讀回幾何；仍未做切片、列印或試配', lambda: measure('reopened'))
