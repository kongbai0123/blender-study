"""Protect prior steps and the explicit manual X/Y sketch update."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V015 = ROOT / 'learning/web/engineering-curriculum-v015.json'
V016 = ROOT / 'learning/web/engineering-curriculum-v016.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV016Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V015)
        cls.data=read(V016)

    def test_previous_steps_and_order(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(221,226))
        self.assertEqual(set(new)-set(old),{f'ch04-xy-driver-0{i}' for i in range(1,6)})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_manual_update_and_scope(self):
        info=self.data['manualXYUpdateVerification']
        self.assertFalse(info['automaticSync'])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        result=read(ROOT/info['summary']['path'])
        pre=result['beforeManualUpdate']; post=result['afterManualUpdateAndReopen']
        self.assertEqual((pre['cutterX'],pre['cutterY']),([2,68],[2,38]))
        self.assertEqual((post['cutterX'],post['cutterY']),([2,78],[2,48]))
        self.assertEqual((post['boundaryDifferencesX'],post['boundaryDifferencesY'],post['driversValid']),([2,2],[2,2],2))
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-xy-driver-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('並非自動同步','手動按更新','尚未驗證布林後實際壁厚與閉合性','上蓋、盒蓋連動與實體列印'):
            self.assertIn(phrase,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),24)

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
        before=V016.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v016.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v016',proc.stderr)
        self.assertEqual(V016.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
