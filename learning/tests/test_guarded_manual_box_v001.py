"""Pure unit tests for one specific hand-built box; no Blender launched."""
import importlib.util
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

GUARD = Path(__file__).resolve().parents[1] / 'tutor' / 'guarded_manual_box_v001.py'
spec = importlib.util.spec_from_file_location('guarded_manual_box_test', GUARD)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def shape(L=80., W=50.):
    levels = {
      'Body': {0.:([0,L],[0,W]), 2.:([2,L-2],[2,W-2]), 30.:([0,2,L-2,L],[0,2,W-2,W])},
      'Body.001': {2.:([2,L-2],[2,W-2]),30.:([2,L-2],[2,W-2])},
      'Cube': {26.:([2.2005,4.2005,L-4.2005,L-2.2005],[2.2003,4.2003,W-4.2003,W-2.2003]),
               30.:([.0005,2.2005,4.2005,L-4.2005,L-2.2005,L-.0005],[.0003,2.2003,4.2003,W-4.2003,W-2.2003,W-.0003]),
               32.:([.0005,L-.0005],[.0003,W-.0003])}}
    return levels, {'Body':(16,12),'Body.001':(8,6),'Cube':(24,22)}, {'Body':0,'Body.001':0,'Cube':0}


class NumericGuardTest(unittest.TestCase):
    def test_reference_checks_full_vertices_face_topology_and_relative_keys(self):
        reference_path = GUARD.parent / 'manual_box_reference_v001.json'
        reference = json.loads(reference_path.read_text(encoding='utf8'))
        snap = {'name':'Cube', 'type':'MESH', 'matrixWorld':copy.deepcopy(reference['object']['matrixWorld']),
                'vertices':copy.deepcopy(reference['mesh']['vertices']),
                'edges':copy.deepcopy(reference['mesh']['edges']),
                'faces':copy.deepcopy(reference['mesh']['faces']),
                'keys':copy.deepcopy(reference['keys'])}
        self.assertIsNone(g._reference_error(snap, reference))
        # Rewire one polygon without changing coordinate sets or face count.
        altered=copy.deepcopy(snap)
        altered['faces'][0][0],altered['faces'][0][1]=altered['faces'][0][1],altered['faces'][0][0]
        self.assertIsNotNone(g._reference_error(altered, reference))
        altered=copy.deepcopy(snap);altered['keys'][1]['values'][0][0] += .01
        self.assertIsNotNone(g._reference_error(altered, reference))
        altered=copy.deepcopy(snap);altered['matrixWorld'][0][3] += .01
        self.assertIsNotNone(g._reference_error(altered, reference))
        altered=copy.deepcopy(snap);altered['vertices'][0][0] = float('nan')
        self.assertIsNotNone(g._reference_error(altered, reference))

    def test_sample_and_boundary_values(self):
        for values in ({'L':60.,'W':30.}, {'L':100.,'W':70.}, {'L':70.,'W':40.}, {'L':90.,'W':60.}):
            self.assertEqual(g.validate(values), [])
        for values in ({'L':110.,'W':50.}, {'L':59.999,'W':50.}, {'L':80.,'W':70.001},
                       {'L':80.,'W':float('nan')}, {'L':float('inf'),'W':50.},
                       {'L':True,'W':50.}, {'L':10**1000,'W':50.}, {'L':80.}):
            self.assertTrue(g.validate(values), values)

    def test_parse_and_ack_reset(self):
        for field, text in [('NONE','70'), ('L',''), ('L','NaN'), ('L','110'), ('W','inf')]:
            with self.subTest(field=field,text=text), self.assertRaises(g.GuardError):
                g.parse_edit_input(field,text)
        self.assertEqual(g.parse_edit_input('L',' 90 '),90)
        obj = type('Input', (), {'field':'L', 'value_text':'70', 'acknowledged':True})()
        g.clear_edit_input(obj)
        self.assertEqual((obj.value_text,obj.acknowledged),('',False))
        obj.acknowledged=True
        g.value_text_changed(obj)
        self.assertFalse(obj.acknowledged)

    def test_invalid_proposal_does_not_write_or_refresh(self):
        trace=[]
        with self.assertRaises(g.GuardError):
            g.guarded_change({'L':80.,'W':50.},'L',110.,lambda *x:trace.append(('write',x)),lambda _:80.,lambda:trace.append(('update',)),lambda _:True)
        self.assertEqual(trace,[])

    def test_postcheck_failure_restores_and_checks_old_geometry(self):
        state={'L':80.,'W':50.}; trace=[]
        def write(k,v): trace.append(('write',v));state[k]=v
        def update(): trace.append(('update',))
        def check(v): trace.append(('check',dict(v)));return v['L']==80.
        with self.assertRaisesRegex(g.GuardError,'已回復'):
            g.guarded_change(state,'L',90.,write,state.__getitem__,update,check)
        self.assertEqual(state,{'L':80.,'W':50.})
        self.assertEqual([x[0] for x in trace],['write','update','check','write','update','check'])

    def test_rollback_failure_tells_user_not_to_save(self):
        state={'L':80.,'W':50.}
        def write(k,v):
            if v==80.: raise RuntimeError('rollback blocked')
            state[k]=v
        with self.assertRaisesRegex(g.GuardError,'請勿存檔'):
            g.guarded_change(state,'L',90.,write,state.__getitem__,lambda:None,lambda _:False)

    def test_evaluated_levels_detect_stale_cavity_or_lid(self):
        levels,counts,nm=shape(90,60)
        self.assertIsNone(g.geometry_error({'L':90.,'W':60.},levels,counts,nm))
        stale,_,_=shape(80,50)
        for target in ('Body','Body.001','Cube'):
            with self.subTest(target=target):
                altered=dict(levels); altered[target]=stale[target]
                self.assertIsNotNone(g.geometry_error({'L':90.,'W':60.},altered,counts,nm))
        changed=dict(nm);changed['Cube']=1
        self.assertIsNotNone(g.geometry_error({'L':90.,'W':60.},levels,counts,changed))

    def test_registered_files_and_evidence_blocked(self):
        with tempfile.TemporaryDirectory(prefix='guard-manual-') as tmp:
            root=Path(tmp).resolve(); work=root/'learning/workspaces/engineering-parametric';work.mkdir(parents=True)
            progress=root/'learning/progress.json';progress.write_text('{"fileVersions": []}',encoding='utf8')
            file=work/'personal.blend';file.write_bytes(b'fixture')
            self.assertIsNone(g.workspace_error(file,root,work,progress))
            progress.write_text('{"fileVersions":[{"path":"learning/workspaces/engineering-parametric/personal.blend"}]}',encoding='utf8')
            self.assertIn('已登記',g.workspace_error(file,root,work,progress))
            evidence=root/'learning/evidence';evidence.mkdir();record=evidence/'record.blend';record.write_bytes(b'x')
            self.assertIsNotNone(g.workspace_error(record,root,work,progress))

    def test_source_scene_target_and_formula_checked(self):
        from types import SimpleNamespace as S
        scene=object()
        target=S(id=scene,data_path='["slvs:c:b596b36138076155"]')
        var=S(type='SINGLE_PROP', name='slvs_c_b596b36138076155',targets=[target])
        driver=S(type='SCRIPTED',is_valid=True,expression='slvs_c_b596b36138076155/10-8',variables=[var])
        curve=S(data_path='key_blocks["Key 1"].value',array_index=0,driver=driver)
        args=([curve],curve.data_path,driver.expression,var.name,target.data_path,scene)
        self.assertIsNone(g._expect_driver(*args))
        target.id=object()
        with self.assertRaises(g.GuardError):g._expect_driver(*args)
        target.id=scene;driver.expression='2'
        with self.assertRaises(g.GuardError):g._expect_driver(*args)


    def test_changed_shape_key_geometry_or_slider_is_rejected(self):
        from types import SimpleNamespace as S
        class Vec:
            def __init__(self,*x): self.x=list(x)
            def __getitem__(self,index): return self.x[index]
            def __sub__(self,other): return Vec(*(a-b for a,b in zip(self.x,other.x)))
        class Matrix:
            def __matmul__(self,vector): return vector
            def to_3x3(self): return self
        class Blocks(list):
            def get(self,name): return next((x for x in self if x.name==name),None)
        scene=object()
        points=[Vec(x,y,30.) for x in (0.,20.,60.,80.) for y in (0.,10.,20.,30.,40.,50.)]
        basis=S(name='Basis',data=[S(co=p) for p in points])
        x=S(name='Key 1',relative_key=basis,slider_min=-2.,slider_max=2.,value=0.,data=[S(co=Vec(p[0]+(10. if p[0]>40. else 0),p[1],p[2])) for p in points])
        y=S(name='Key 2',relative_key=basis,slider_min=-2.,slider_max=2.,value=0.,data=[S(co=Vec(p[0],p[1]+(10. if p[1]>25. else 0),p[2])) for p in points])
        def curve(number,field):
            source=g.FIELDS[field][1];varname=source.replace(':','_')
            v=S(type='SINGLE_PROP',name=varname,targets=[S(id=scene,data_path=f'["{source}"]')])
            d=S(type='SCRIPTED',is_valid=True,expression=varname+('/10-8' if field=='L' else '/10-5'),variables=[v])
            return S(data_path=f'key_blocks["Key {number}"].value',array_index=0,driver=d)
        keys=S(use_relative=True,key_blocks=Blocks([basis,x,y]),animation_data=S(drivers=[curve(1,'L'),curve(2,'W')]))
        obj=S(data=S(shape_keys=keys),matrix_world=Matrix())
        self.assertIsNone(g._check_keys(obj,scene,{'L':80.,'W':50.}))
        x.slider_max=1.
        with self.assertRaises(g.GuardError):g._check_keys(obj,scene,{'L':80.,'W':50.})
        x.slider_max=2.;x.data[0].co=Vec(1.,0.,30.)
        with self.assertRaises(g.GuardError):g._check_keys(obj,scene,{'L':80.,'W':50.})



if __name__=='__main__':unittest.main()
