"""Keep old steps and warning evidence faithful to observed intermediate states."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
V016=ROOT/'learning/web/engineering-curriculum-v016.json'
V017=ROOT/'learning/web/engineering-curriculum-v017.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV017Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V016)
        cls.data=read(V017)

    def test_previous_steps_and_order(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(226,228))
        self.assertEqual(set(new)-set(old),{'ch04-xy-safety-01','ch04-xy-safety-02'})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_intermediate_geometry_and_scope(self):
        info=self.data['manualXYIntermediateReview']
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        review=read(ROOT/info['summary']['path'])
        self.assertEqual((review['paste']['outerY'],review['paste']['cutterY']),([0,40],[2,42]))
        self.assertEqual(review['formula']['cutterY'],[2,38])
        self.assertEqual((review['beforeUpdate']['cutterX'],review['beforeUpdate']['cutterY']),([2,68],[2,38]))
        self.assertEqual((review['beforeUpdate']['solver'],review['beforeUpdate']['dof']),('OKAY',0))
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-xy-safety-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('暫時無效幾何','Fully defined','必須手動更新後再核對','尺寸標籤有重疊','上蓋連動未驗'):
            self.assertIn(phrase,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),3)

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
        before=V017.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v017.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v017',proc.stderr)
        self.assertEqual(V017.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
