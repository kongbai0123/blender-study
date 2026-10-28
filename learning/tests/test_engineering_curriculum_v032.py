"""v032 moves chapter 11 steps that cannot be done yet out of the main line and tidies the ch07-12 walkthroughs."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'learning/web'
OLD, NEW = WEB / 'engineering-curriculum-v031.json', WEB / 'engineering-curriculum-v032.json'
PENDING = {'ch11-08-02-02', 'ch11-08-03-01', 'ch11-08-03-02', 'ch11-08-04-02', 'ch11-08-05-01', 'ch11-08-05-02'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manage():
    spec = importlib.util.spec_from_file_location('manage_v032', ROOT / 'learning/manage.py')
    manage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manage)
    return manage


class CurriculumV032Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.data = read(OLD), read(NEW)
        cls.steps = {step['id']: (chapter, step) for chapter in cls.data['chapters'] for step in chapter['steps']}

    def test_pointer_and_history(self):
        manage = load_manage()
        self.assertEqual(manage.ENGINEERING_CURRICULUM, NEW)
        self.assertEqual(sha(OLD), '96a3304fee401b61cc59b6764eaa31b6a22e31e9865b873534299f8eb42c5b92')
        self.assertEqual(self.data['id'], self.old['id'])
        self.assertEqual(self.data['sourceVersions'][-1], {'path': 'learning/web/engineering-curriculum-v031.json', 'sha256': sha(OLD)})
        self.assertFalse(self.data['contentReview']['reviewV032']['learnerProgressChanged'])

    def test_pending_steps_leave_the_main_line(self):
        pending = {step_id for step_id, (_, step) in self.steps.items() if step.get('track') == 'pending'}
        self.assertEqual(pending, PENDING)
        main = [step for _, step in self.steps.values() if not step.get('track')]
        self.assertEqual(len(main), 239)
        for _, step in self.steps.values():
            self.assertNotIn('尚不能依現有教學完成', json.dumps(step, ensure_ascii=False) if not step.get('track') else '')
        ch11 = next(chapter for chapter in self.data['chapters'] if chapter['id'] == 'ch11')
        self.assertEqual({section['id'] for section in ch11['sections'] if section.get('track') == 'pending'}, {'11-05', '11-07'})
        self.assertIn('pending', self.data['trackDefinitions'])

    def test_walkthrough_note_is_per_chapter_and_tools_are_named(self):
        for chapter in self.data['chapters']:
            details = [step['detail'] for step in chapter['steps'] if 'detail' in step]
            self.assertTrue(all(set(detail) == {'steps', 'why'} for detail in details), chapter['id'])
            self.assertEqual('detailNote' in chapter, chapter['id'] >= 'ch07', chapter['id'])
            text = json.dumps(details, ensure_ascii=False)
            self.assertNotIn('可用工具', text)
            self.assertNotIn('可用世界座標', text)

    def test_only_listed_changes(self):
        for old, new in zip(self.old['chapters'], self.data['chapters'], strict=True):
            for a, b in zip(old['steps'], new['steps'], strict=True):
                a, b = dict(a), dict(b)
                if b['id'] in PENDING:
                    self.assertEqual(b.pop('track'), 'pending')
                ad, bd = a.pop('detail', None), b.pop('detail', None)
                self.assertEqual(a, b)
                if ad:
                    ad = {k: v for k, v in ad.items() if k != 'verification'}
                    self.assertEqual(ad['why'], bd['why'])
                    self.assertEqual(len(ad['steps']), len(bd['steps']))

    def test_manage_refuses_to_confirm_a_pending_step(self):
        manage = load_manage()
        with tempfile.TemporaryDirectory() as folder:
            progress = {'events': []}
            args = SimpleNamespace(chapter='ch11', step='ch11-08-03-01', evidence='完成')
            with self.assertRaisesRegex(ValueError, '待製作'):
                manage.engineering_event(progress, args, confirmed=True)
            overview = manage.engineering_overview({'events': []})
            self.assertEqual(overview['total'], 239)

    def test_builder_refuses_to_overwrite(self):
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v032.py'],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(before, NEW.read_bytes())


if __name__ == '__main__':
    unittest.main()
