"""Challenges v005 folds the chapter 03 pilot page into the shared challenge page without changing other chapters."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/challenges/challenges-v004.json'
NEW = ROOT / 'learning/web/challenges/challenges-v005.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ChallengesV005Tests(unittest.TestCase):
    def test_pointer_history_and_scope(self):
        spec = importlib.util.spec_from_file_location('manage_challenges_v005', ROOT / 'learning/manage.py')
        manage = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manage)
        self.assertEqual(manage.CHALLENGES, NEW)
        self.assertEqual(sha(OLD), 'c17a274a4e70ccd82463bd83f76a58f7a9821bafaa09fad402cc5766aa8a1af0')
        old, new = read(OLD), read(NEW)
        self.assertEqual(new['previousVersion'], {'path': 'learning/web/challenges/challenges-v004.json', 'sha256': sha(OLD)})
        self.assertEqual(new['source']['path'], 'learning/web/engineering-curriculum-v032.json')
        for a, b in zip(old['chapters'], new['chapters'], strict=True):
            if a['chapterId'] != 'ch03':
                self.assertEqual(a, b)
        ch03 = next(item for item in new['chapters'] if item['chapterId'] == 'ch03')
        self.assertNotIn('pilotPath', ch03)
        self.assertEqual((ch03['progressKind'], ch03['challengeId']), ('pilot', 'box-opening-v001'))
        self.assertEqual(sha(ROOT / 'learning/web/pilot/box-demo.gif'), ch03['animation']['sha256'])
        for record in ch03['animation']['records']:
            self.assertTrue((ROOT / record['path']).is_file())
            self.assertNotIn('run.json', record['path'])

    def test_pilot_page_only_redirects(self):
        html = (ROOT / "learning/web/pilot/box-lesson.html").read_text(encoding="utf-8")
        self.assertIn("url=/challenges/index.html?chapter=ch03", html)
        self.assertNotIn("<script", html)
        self.assertFalse((ROOT / "learning/web/pilot/box-lesson.js").exists())

    def test_builder_refuses_to_overwrite(self):
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, "-X", "utf8", "learning/build_challenges_v005.py"],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(before, NEW.read_bytes())


if __name__ == "__main__":
    unittest.main()
