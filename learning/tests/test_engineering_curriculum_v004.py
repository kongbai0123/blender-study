"""Open Screw evidence extends v003 without changing its learner event IDs."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v003.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v004.json'


class CurriculumV004Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_bytes = OLD.read_bytes()
        cls.old = json.loads(cls.old_bytes)
        cls.new = json.loads(NEW.read_text(encoding='utf-8'))

    def test_original_v003_and_all_prior_steps_unchanged(self):
        self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(), '0a708e4c1cb06f524db4acb3d09412ce3adb6ba66e1a99fe3bb7f30897faf9cf')
        self.assertEqual(self.old['id'], self.new['id'])
        self.assertEqual(self.new['id'], 'engineering-curriculum-v002')
        self.assertIn('v004', self.new['version'])
        self.assertEqual([c['id'] for c in self.old['chapters']], [c['id'] for c in self.new['chapters']])
        for old, new in zip(self.old['chapters'], self.new['chapters']):
            self.assertEqual(old['steps'], new['steps'][:len(old['steps'])])
            if old['id'] != 'ch10':
                self.assertEqual(old, new)
            else:
                self.assertIn('開放曲面', ' '.join(new['limitations']))
        self.assertEqual(sum(len(c['steps']) for c in self.new['chapters']), 168)

    def test_all_sources_figures_artifacts_and_ids(self):
        checked = set()
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
                    checked.add((fig['path'], fig['sha256']))
                for artifact in step.get('artifacts', []):
                    self.assertTrue(artifact['label'])
                    checked.add((artifact['path'], artifact['sha256']))
                for shortcut in step['shortcuts']:
                    for item in shortcut['evidence']:
                        if item.get('path') and item.get('sha256'):
                            checked.add((item['path'], item['sha256']))
        for source in self.new['sourceVersions']:
            checked.add((source['path'], source['sha256']))
        self.assertGreater(len(checked), 30)
        for rel, expected in checked:
            path = (ROOT / rel).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, rel)

    def test_open_surface_is_not_misrepresented_as_printable(self):
        chapter = next(c for c in self.new['chapters'] if c['id'] == 'ch10')
        steps = [s for s in chapter['steps'] if s['id'].startswith('ch10-screw-surface-')]
        self.assertEqual(len(steps), 8)
        for step in steps:
            limits = ' '.join(step['limitations'])
            self.assertIn('程式準備', limits)
            self.assertIn('260條開放邊', limits)
            self.assertIn('不是閉合可列印實體', limits)
            self.assertIn('不代表學員已完成', limits)
        data = self.new['screwSurfaceVerification']
        self.assertIsNone(data['physicalMeasurements'])
        self.assertIsNone(data['fitResults'])
        self.assertIsNone(data['qualifiedClearanceMm'])
        self.assertIsNone(data['strengthQualified'])
        self.assertIn('未提供獨立起始輪廓檔', ' '.join(steps[1]['limitations']))
        self.assertIn('4.6 mm', steps[5]['success'])


if __name__ == '__main__':
    unittest.main()
