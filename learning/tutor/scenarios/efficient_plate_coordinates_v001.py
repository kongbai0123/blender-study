"""Replay the actual 05-02 cutter coordinates, with real UI events and saved stages."""
import hashlib
import json
import shutil
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g['OUT'])
    checks = []
    saved = {}
    snapshot = out / 'source-snapshot'
    snapshot.mkdir()
    for source in [Path(__file__), PROJECT/'learning/tutor/scenarios/common.py',
                   PROJECT/'learning/tutor/blender_demo.py', PROJECT/'learning/tutor/run_demo.py']:
        shutil.copyfile(source, snapshot/source.name)

    def key(name, **kw):
        k.do(lambda: k.key(name, x=650, y=450, **kw), .28)

    def text(value):
        k.do(lambda: k.type_text(value), .2)

    def search(value):
        key('F3'); text(value); key('RET')

    def rename(value):
        key('F2'); text(value); key('RET')

    def move(axis, value):
        key('G'); key(axis); text(value); key('RET')

    def state():
        w = k.window()
        cutters = sorted([o for o in w.scene.objects if o.type == 'MESH' and o.name.startswith('Cut_')],
                         key=lambda o: o.location.x)
        plate = w.scene.objects.get('Plate')
        return {'cutters': [{'name':o.name, 'mesh':o.data.name, 'location':list(o.location),
                             'dimensions':list(o.dimensions), 'scale':list(o.scale)} for o in cutters],
                'plate': None if plate is None else {'dimensions':list(plate.dimensions), 'hidden':plate.hide_get()},
                'active': w.view_layer.objects.active.name if w.view_layer.objects.active else None,
                'blender': bpy.app.version_string, 'unitScale':w.scene.unit_settings.scale_length,
                'savedScene': saved.copy(), 'physicalPrint':None, 'physicalMeasurement':None, 'physicalFit':None}

    def checkpoint(slug):
        path = out/'demo-files'/(slug+'-v001.blend')
        assert not path.exists()
        with bpy.context.temp_override(window=k.window(), area=k.area('VIEW_3D')):
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
        saved.update(path=path.relative_to(PROJECT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    def shot(step, slug, action, validator):
        k.do(lambda: checkpoint(slug), .4)
        def observe():
            actual = state()
            passed = bool(validator(actual))
            checks.append({'stepId':step, 'case':slug, 'passed':passed, 'readback':actual})
            assert passed, (slug, actual)
            return actual
        k.record(step, slug, action, observe,
                 highlights=lambda:[k.box(953, 382, 244, 84, 'Dimensions'),
                                    k.box(953, 119, 244, 82, 'Location')],
                 note='Unit display is prepared with Python; modelling, duplication, transforms and object selection use simulated UI events. Saving uses the file operator into this run only. Plate is a hidden blank, not a completed Boolean plate.')

    def near(a, b):
        return abs(a-b) < 1e-4

    def canonical(d):
        return len(d['cutters']) == 6 and all(near(o['location'][0], -35+14*i) and
               near(o['location'][1], 2) and near(o['location'][2], 0)
               for i, o in enumerate(d['cutters']))

    k.setup()
    def units():
        u=k.window().scene.unit_settings
        u.system='METRIC';u.scale_length=.001;u.length_unit='MILLIMETERS'
    k.do(units, .4)
    key('N')
    rename('Plate')
    for y, value in [(411,'96mm'), (430,'26mm'), (450,'4mm')]:
        k.type_into(1075,y,value)
    search('Apply Scale'); key('H')
    search('Add Cube'); rename('Cut_01')
    for y, value in [(411,'10.1mm'), (430,'10.1mm'), (450,'8mm')]:
        k.type_into(1075,y,value)
    search('Apply Scale'); move('X','-35mm'); move('Y','2mm')
    key('NUMPAD_7'); search('Frame Selected'); k.wheel_out(2)
    shot('ch05-05-03-03', 'first-cutter',
         'F3 Add Cube；N輸入10.1×10.1×8mm，Apply Scale，再G X -35mm、G Y 2mm。Plate已H隱藏。',
         lambda d:len(d['cutters'])==1 and near(d['cutters'][0]['location'][0],-35) and
         near(d['cutters'][0]['location'][1],2) and all(near(a,b) for a,b in zip(d['cutters'][0]['dimensions'],[10.1,10.1,8])) and
         all(near(v,1) for v in d['cutters'][0]['scale']) and d['plate']['hidden'])
    key('D',shift=True);key('X');text('14mm');key('RET')
    for _ in range(4):
        key('R',shift=True)
    key('HOME'); k.wheel_out(3)
    shot('ch05-05-03-04', 'six-equal',
         'Shift+D X 14mm，立刻Shift+R四次；六件先同尺寸，中心X=-35,-21,-7,7,21,35mm，Y=2mm。',
         lambda d:canonical(d) and len({o['mesh'] for o in d['cutters']})==6 and
         all(near(o['dimensions'][0],10.1) for o in d['cutters']))

    def click_index(i):
        w=k.window()
        cutters=sorted([o for o in w.scene.objects if o.type=='MESH' and o.name.startswith('Cut_')],key=lambda o:o.location.x)
        a=k.area('VIEW_3D');region=next(r for r in a.regions if r.type=='WINDOW')
        p=location_3d_to_region_2d(region,a.spaces.active.region_3d,cutters[i].matrix_world@Vector((0,0,0)))
        assert p is not None
        k.click(region.x+p.x,w.height-(region.y+p.y))

    for i in range(1,6):
        k.do(lambda index=i:click_index(index),.35)
        k.type_into(1075,411,str(round(10.1+.1*i,1))+'mm')
        k.type_into(1075,430,str(round(10.1+.1*i,1))+'mm')
        search('Apply Scale')
        if i==2:
            shot('ch05-05-03-04','first-three-widths',
                 '複製完成後，逐一選第2、第3件，N的X/Y改10.2、10.3mm，Z保持8mm並Apply Scale。',
                 lambda d:canonical(d) and all(near(o['dimensions'][0],width)
                 for o,width in zip(d['cutters'],[10.1,10.2,10.3,10.1,10.1,10.1])))
    shot('ch05-05-03-05','six-varied',
         '第4～6件X/Y為10.4、10.5、10.6mm；六件位置及Y=2mm與正文相同，Z=8mm、Scale1。尚未進行Boolean。',
         lambda d:canonical(d) and len({o['mesh'] for o in d['cutters']})==6 and
         all(near(o['dimensions'][0],10.1+.1*i) and near(o['dimensions'][1],10.1+.1*i) and
             near(o['dimensions'][2],8) and all(near(v,1) for v in o['scale']) for i,o in enumerate(d['cutters'])))

    def finish():
        assert len(checks)==4 and all(c['passed'] for c in checks)
        (out/'verification.json').write_text(json.dumps({'checks':checks,'physicalPrint':None,'physicalMeasurement':None,
                                                        'physicalFit':None},ensure_ascii=False,indent=2)+'\n','utf8')
    k.do(finish,.2)
