"""The new recorded exercises are optional and do not unlock unfinished work."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v032.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v033.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurriculumV033Tests(unittest.TestCase):
    def test_optional_screenshots_match_and_old_steps_unchanged(self):
        old, new = read(OLD), read(NEW)
        old_ch = next(c for c in old['chapters'] if c['id'] == 'ch11')
        ch = next(c for c in new['chapters'] if c['id'] == 'ch11')
        self.assertEqual(ch['steps'][:len(old_ch['steps'])], old_ch['steps'])
        steps = ch['steps'][len(old_ch['steps']):]
        self.assertEqual(len(steps), 28)
        self.assertEqual({s['section'] for s in steps}, {'11-08', '11-09', '11-10'})
        self.assertTrue(all(s['track'] == 'optional' for s in steps))
        self.assertEqual(len({s['id'] for s in ch['steps']}), len(ch['steps']))
        for step in steps:
            image = step['figures'][0]
            self.assertEqual(digest(ROOT / image['path']), image['sha256'], step['id'])
            self.assertTrue(step['actions'] and step['success'] and step['limitations'])
        for chapter in new['chapters']:
            self.assertEqual(sum(not s.get('track') for s in chapter['steps']),
                             sum(not s.get('track') for s in next(c for c in old['chapters'] if c['id'] == chapter['id'])['steps']))
        self.assertEqual(sum(s.get('track') == 'pending' for c in new['chapters'] for s in c['steps']), 6)
        self.assertFalse(new['contentReview']['reviewV033']['learnerProgressChanged'])
        self.assertIsNone(new['contentReview']['reviewV033']['physicalFit'])

    def test_pointer_and_non_overwrite(self):
        spec = importlib.util.spec_from_file_location('manage_v033', ROOT / 'learning/manage.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Retain this version as immutable history as the active pointer advances.
        self.assertEqual(digest(NEW), 'a5688b2abaad001a60c193a187784c8a67ec88c9862fd5fade7bfa8ce1d3bfa6')
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v033.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(NEW.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
