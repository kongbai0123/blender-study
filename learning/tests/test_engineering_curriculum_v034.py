"""New demonstration evidence must not silently complete the learner or hardware tasks."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v033.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v034.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurriculumV034Tests(unittest.TestCase):
    def test_evidence_scope_and_progress_stability(self):
        old, new = read(OLD), read(NEW)
        self.assertEqual(new['id'], old['id'])
        a = {s['id']: s for c in old['chapters'] for s in c['steps']}
        b = {s['id']: s for c in new['chapters'] for s in c['steps']}
        self.assertEqual({k for k, s in a.items() if s.get('track') == 'pending'},
                         {k for k, s in b.items() if s.get('track') == 'pending'})
        self.assertEqual({k for k, s in a.items() if not s.get('track')},
                         {k for k, s in b.items() if not s.get('track')})
        additions = [s for k, s in b.items() if k not in a]
        self.assertEqual(len(additions), 25)
        self.assertEqual({s['section'] for s in additions}, {'11-11', '11-12'})
        for step in additions:
            self.assertEqual(step['track'], 'optional')
            image = step['figures'][0]
            self.assertEqual(digest(ROOT / image['path']), image['sha256'])
            self.assertTrue(step['limitations'])
        audit = new['contentReview']['reviewV034']
        self.assertFalse(audit['learnerProgressChanged'])
        for key in ('physicalPrint', 'physicalMeasurement', 'physicalFit', 'qualifiedClearance', 'qualifiedStrength'):
            self.assertIsNone(audit[key])
        text = json.dumps(additions, ensure_ascii=False)
        self.assertIn('5.625', text)
        self.assertIn('4.8', text)
        self.assertIn('診斷', text)

    def test_active_pointer_and_no_overwrite(self):
        spec = importlib.util.spec_from_file_location('manage_v034', ROOT / 'learning/manage.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(digest(NEW), '119432ade0437a1c1d8063ad4d4d8cb368faa4351a21da6975164b2f69dbafd5')
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v034.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(NEW.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
