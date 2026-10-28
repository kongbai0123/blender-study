"""New parametric evidence may extend, but never change, the v002 step contract."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v002.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v003.json'


class CurriculumV003Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_bytes = OLD.read_bytes()
        cls.old = json.loads(cls.old_bytes)
        cls.new = json.loads(NEW.read_text(encoding='utf-8'))

    def test_original_v002_and_existing_steps_are_unchanged(self):
        self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(), 'bb02ba7511162d1de1ae08ce710274b8839568af485da7a8ed8a621b2a64d495')
        self.assertEqual(self.old['id'], self.new['id'])
        self.assertEqual(self.new['id'], 'engineering-curriculum-v002')
        self.assertIn('v003', self.new['version'])
        self.assertEqual([c['id'] for c in self.old['chapters']], [c['id'] for c in self.new['chapters']])
        for old, new in zip(self.old['chapters'], self.new['chapters']):
            self.assertEqual({k: v for k, v in old.items() if k != 'steps'}, {k: v for k, v in new.items() if k != 'steps'})
            self.assertEqual(old['steps'], new['steps'][:len(old['steps'])])
            if old['id'] != 'ch05':
                self.assertEqual(old['steps'], new['steps'])
        old_count = sum(len(c['steps']) for c in self.old['chapters'])
        self.assertEqual(sum(len(c['steps']) for c in self.new['chapters']), old_count + 4)

    def test_new_steps_have_unique_ids_and_valid_references(self):
        seen = set()
        for chapter in self.new['chapters']:
            for step in chapter['steps']:
                self.assertNotIn(step['id'], seen)
                seen.add(step['id'])
                self.assertTrue(step['context'])
                self.assertTrue(1 <= len(step['actions']) <= 3)
                self.assertIn(step['evidenceStatus'], self.new['evidenceStatusDefinitions'])
                for fig in step['figures']:
                    self.assertEqual(fig['type'], 'screenshot')
                    self.assert_hash(fig)
                for artifact in step.get('artifacts', []):
                    self.assertTrue(artifact['label'])
                    self.assert_hash(artifact)
                for shortcut in step['shortcuts']:
                    for item in shortcut['evidence']:
                        if item.get('path') and item.get('sha256'):
                            self.assert_hash(item)
        for source in self.new['sourceVersions']:
            self.assert_hash(source)

    def assert_hash(self, item):
        p = (ROOT / item['path']).resolve()
        self.assertTrue(p.is_relative_to(ROOT.resolve()))
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), item['sha256'], item['path'])

    def test_launch_and_evidence_scope_stays_explicit(self):
        chapter = next(c for c in self.new['chapters'] if c['id'] == 'ch05')
        steps = {s['id']: s for s in chapter['steps']}
        launch = steps['ch05-linked-01']
        self.assertEqual(launch['evidenceStatus'], 'draft_pending_demo')
        self.assertIn('open_parametric_box.py --copy-to', launch['actions'][0])
        self.assertIn('尚未驗證使用者互動啟動', ' '.join(launch['limitations']))
        self.assertEqual(len(launch['artifacts']), 4)
        self.assertIn('非 GUI', ' '.join(launch['limitations']))
        verified = self.new['parametricBoxVerification']
        self.assertIsNone(verified['physicalMeasurements'])
        self.assertIsNone(verified['fitResults'])
        self.assertIsNone(verified['qualifiedClearanceMm'])
        self.assertIn('非GUI', verified['scope'])
        self.assertIn('內腔76×36×28', steps['ch05-linked-03']['success'])


if __name__ == '__main__':
    unittest.main()
