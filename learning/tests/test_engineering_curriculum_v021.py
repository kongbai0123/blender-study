"""Protect prior steps and the observed shape-key clamp counterexample."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
V020=ROOT/'learning/web/engineering-curriculum-v020.json'
V021=ROOT/'learning/web/engineering-curriculum-v021.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV021Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V020)
        cls.data=read(V021)

    def test_previous_steps_and_order(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(241,243))
        self.assertEqual(set(new)-set(old),{'ch05-manual-lid-clamp-01','ch05-manual-lid-clamp-02'})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_counterexample_and_scope(self):
        info=self.data['manualBoxLidClampingCounterexample']
        self.assertEqual((info['shapeKeyComputedValue'],info['observedClampedValue']),(3,2))
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        result=read(ROOT/info['summary']['path'])
        p=result['phases']['reopened']
        self.assertEqual(p['shapeKeys'][1]['value'],2)
        self.assertEqual(p['meshReadback']['Body.001']['levels']['30.0']['x'],[2,108])
        self.assertEqual(p['meshReadback']['Cube']['levels']['26.0']['x'][-1],97.7995)
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-lid-clamp-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('實際只改 X80→110，Y 維持50','理論值3','實際鍵值被夾為2','右側界限差約10.2005 mm','不是已驗證全區、安全或製造範圍','舊 v007 尺寸防護不適用','非完成品'):
            self.assertIn(phrase,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),9)

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
        before=V021.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v021.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v021',proc.stderr)
        self.assertEqual(V021.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
