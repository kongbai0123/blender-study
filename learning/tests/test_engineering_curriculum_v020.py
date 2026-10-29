"""Protect old steps and the scope of GUI multicase linkage observations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
V019=ROOT/'learning/web/engineering-curriculum-v019.json'
V020=ROOT/'learning/web/engineering-curriculum-v020.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV020Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V019)
        cls.data=read(V020)

    def test_previous_steps_and_order(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(238,241))
        self.assertEqual(set(new)-set(old),{f'ch05-manual-lid-cases-0{i}' for i in range(1,4)})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_multicase_and_stale_geometry_limits(self):
        info=self.data['manualBoxLidMulticaseVerification']
        self.assertTrue(info['cavityRequiresManualUpdate'])
        self.assertEqual(info['testedSequenceMm'],[[80,50],[90,50],[80,60],[70,40]])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        result=read(ROOT/info['summary']['path'])
        self.assertEqual(result['phases']['x80y60-before']['meshReadback']['Body.001']['levels']['30.0']['x'],[2,88])
        self.assertEqual(result['phases']['x70y40-before']['meshReadback']['Body.001']['levels']['30.0'],{'x':[2,78],'y':[2,58]})
        self.assertEqual(result['phases']['reopened']['meshReadback']['Body.001']['levels']['30.0'],{'x':[2,68],'y':[2,38]})
        self.assertEqual([k['value'] for k in result['phases']['reopened']['shapeKeys'][1:]],[-1,-1])
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-lid-cases-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('實際該步由90×50同時改 X 和 Y','Body non-manifold 邊數仍為0','不可作完成品匯出或列印','並非完整截面、碰撞或實體配合檢驗','僅未夾限理論區間','舊 v007 防護不適用'):
            self.assertIn(phrase,text)
        limits=next(c for c in self.data['chapters'] if c['id']=='ch05')['limitations']
        self.assertTrue(any('重開僅驗70×40' in s for s in limits))

    def test_references_and_frozen_generator(self):
        refs=[]
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for fig in step.get('figures',[]):
                    self.assertEqual(fig['type'],'screenshot')
                    self.assertTrue(fig['path'].startswith('learning/evidence/'))
                    refs.append(fig)
                refs.extend(step.get('artifacts',[]))
                for shortcut in step.get('shortcuts',[]):
                    refs.extend(shortcut.get('evidence',[]))
        refs.extend(self.data['sourceVersions'])
        for ref in refs:
            path=(ROOT/ref['path']).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()),ref['path'])
            self.assertTrue(path.is_file(),ref['path'])
            self.assertEqual(sha(path),ref['sha256'],ref['path'])
        before=V020.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v020.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v020',proc.stderr)
        self.assertEqual(V020.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
