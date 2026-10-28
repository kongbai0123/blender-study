"""Keep historical lessons and manual X-refresh evidence distinct."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V014 = ROOT / 'learning/web/engineering-curriculum-v014.json'
V015 = ROOT / 'learning/web/engineering-curriculum-v015.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV015Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = read(V014)
        cls.data = read(V015)

    def test_prior_steps_preserved(self):
        self.assertEqual(self.data['id'], self.old['id'])
        old = {s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new = {s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(217,221))
        self.assertEqual(set(new)-set(old),{f'ch04-x-refresh-0{i}' for i in range(1,5)})
        self.assertTrue(all(new[k] == v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']], [s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_manual_update_is_not_automatic_or_saved(self):
        info = self.data['manualXRefreshVerification']
        self.assertFalse(info['automaticSync'])
        self.assertFalse(info['savedAfterRefresh'])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        result = read(ROOT/info['summary']['path'])
        self.assertEqual(result['saved_x70_before_solve']['cutterX'],[2,58])
        self.assertEqual(result['saved_x70_before_solve']['wallBoundaryDifferences'],[2,12])
        self.assertEqual(result['after_manual_sketch_update']['cutterX'],[2,68])
        self.assertEqual(result['after_manual_sketch_update']['wallBoundaryDifferences'],[2,2])
        steps = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-x-refresh-')]
        text = json.dumps(steps,ensure_ascii=False)
        for phrase in ('不能當成全自動同步','更新後狀態此次沒有另存','未驗證布林後實際壁厚或閉合性','Y Driver、上蓋及盒蓋連動未完成'):
            self.assertIn(phrase,text)

    def test_sources_and_immutable_generator(self):
        refs = []
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for figure in step.get('figures',[]):
                    self.assertEqual(figure['type'],'screenshot')
                    self.assertTrue(figure['path'].startswith('learning/evidence/'))
                    refs.append(figure)
                refs.extend(step.get('artifacts',[]))
                for shortcut in step.get('shortcuts',[]):
                    refs.extend(shortcut.get('evidence',[]))
        refs.extend(self.data['sourceVersions'])
        for ref in refs:
            path = (ROOT/ref['path']).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()),ref['path'])
            self.assertTrue(path.is_file(),ref['path'])
            self.assertEqual(sha(path),ref['sha256'],ref['path'])
        before = V015.read_bytes()
        proc = subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v015.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v015',proc.stderr)
        self.assertEqual(V015.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
