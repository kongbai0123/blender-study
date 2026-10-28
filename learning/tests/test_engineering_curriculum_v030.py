"""v030 adds a detailed walkthrough to every chapter 01-06 main step and leaves v029 untouched."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'learning/web'
OLD, NEW = WEB / 'engineering-curriculum-v029.json', WEB / 'engineering-curriculum-v030.json'
PATH = WEB / 'engineering-path-v003.json'
REWRITTEN = {'ch01', 'ch02', 'ch03', 'ch04', 'ch05', 'ch06'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurriculumV030Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.data = read(OLD), read(NEW)

    def test_pointer_and_history(self):
        spec = importlib.util.spec_from_file_location('pointer_manage_v030', ROOT / 'learning/manage.py')
        manage = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manage)
        # v030 is a frozen historical source after the current curriculum advances.
        self.assertEqual(sha(NEW), '55d0cc4c731a550fbe2c17635426dd14efca2894cf99455b322d0ed9f8d8515b')
        self.assertEqual(manage.ENGINEERING_PATH, PATH)
        self.assertEqual(sha(OLD), 'c042a30f169541b3087e1a9919320b689745cb170813a4f8ab0bf569b9a6edc1')
        self.assertEqual(self.data['id'], self.old['id'])
        self.assertEqual(self.data['sourceVersions'][-2], {'path': 'learning/web/engineering-curriculum-v029.json', 'sha256': sha(OLD)})
        self.assertFalse(self.data['contentReview']['reviewV030']['learnerProgressChanged'])

    def test_only_detail_is_added(self):
        for old, new in zip(self.old['chapters'], self.data['chapters'], strict=True):
            self.assertEqual({k: v for k, v in old.items() if k != 'steps'}, {k: v for k, v in new.items() if k != 'steps'})
            for a, b in zip(old['steps'], new['steps'], strict=True):
                expected = new['id'] in REWRITTEN and not a.get('track')
                self.assertEqual('detail' in b, expected, b['id'])
                self.assertEqual(a, {k: v for k, v in b.items() if k != 'detail'})

    def test_details_are_complete_walkthroughs(self):
        details = [step['detail'] for chapter in self.data['chapters'] for step in chapter['steps'] if 'detail' in step]
        self.assertEqual(len(details), 135)
        for detail in details:
            self.assertEqual(set(detail), {'steps', 'why'})
            self.assertTrue(detail['steps'] and all(isinstance(line, str) and line.strip() for line in detail['steps']))
            self.assertTrue(detail['why'].strip())

    def test_builder_refuses_to_overwrite(self):
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v030.py'],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(before, NEW.read_bytes())


if __name__ == '__main__':
    unittest.main()
