"""Verify v004 compatibility and explicitly scoped v005 teaching corrections."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v004.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v005.json'
BOOLEAN_WARNING = '本次未封端的開放曲面不可直接當成已驗證的 Boolean 切割體；須先建立並驗證可用的封閉工具。'


class CurriculumV005Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_bytes = OLD.read_bytes()
        cls.old = json.loads(cls.old_bytes)
        cls.new = json.loads(NEW.read_text(encoding='utf-8'))

    def test_old_steps_only_have_explicitly_recorded_corrections(self):
        self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(), 'fb8ce0cbbf4606ad9d83498756ad891a0b2bbaaf747c65ca307da5d5f93825ec')
        self.assertEqual(self.old['id'], self.new['id'])
        self.assertEqual(self.new['id'], 'engineering-curriculum-v002')
        self.assertIn('v005', self.new['version'])
        self.assertEqual([c['id'] for c in self.old['chapters']], [c['id'] for c in self.new['chapters']])
        for old, new in zip(self.old['chapters'], self.new['chapters']):
            by_id = {s['id']: s for s in new['steps']}
            for step in old['steps']:
                expected = copy.deepcopy(step)
                if step['id'] == 'ch10-screw-surface-inspect':
                    expected['context'] = '已新增 Screw 修改器並顯示評估結果；修改器未套用（Apply）。'
                if any(ref.get('stepId') == '08-03' for ref in step['sourceSteps']):
                    expected['limitations'].append(BOOLEAN_WARNING)
                self.assertEqual(expected, by_id[step['id']], step['id'])
            if old['id'] != 'ch10':
                self.assertEqual(old, new)
        self.assertEqual(sum(len(c['steps']) for c in self.old['chapters']), 168)
        self.assertEqual(sum(len(c['steps']) for c in self.new['chapters']), 172)

    def test_chapter_10_order_and_boolean_guard(self):
        chapter = next(c for c in self.new['chapters'] if c['id'] == 'ch10')
        ids = [s['id'] for s in chapter['steps']]
        self.assertLess(ids.index('ch10-08-01-03'), ids.index('ch10-screw-surface-profile'))
        self.assertLess(ids.index('ch10-screw-surface-reopen'), ids.index('ch10-boss-draft-observe'))
        self.assertLess(ids.index('ch10-boss-draft-save'), ids.index('ch10-08-02-01'))
        boolean_steps = [s for s in chapter['steps'] if any(r.get('stepId') == '08-03' for r in s['sourceSteps'])]
        self.assertEqual(len(boolean_steps), 2)
        for step in boolean_steps:
            self.assertIn(BOOLEAN_WARNING, step['limitations'])

    def test_sources_images_artifacts_and_educational_limits(self):
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
        for rel, expected in checked:
            path = (ROOT / rel).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, rel)
        boss = self.new['bossDraftVerification']
        self.assertIsNone(boss['physicalMeasurements'])
        self.assertIsNone(boss['fitResults'])
        self.assertIsNone(boss['qualifiedHoleDiameterMm'])
        self.assertIsNone(boss['strengthQualified'])
        c10 = next(c for c in self.new['chapters'] if c['id'] == 'ch10')
        steps = [s for s in c10['steps'] if s['id'].startswith('ch10-boss-draft-')]
        self.assertEqual(len(steps), 4)
        for step in steps:
            limits = ' '.join(step['limitations'])
            self.assertIn('程式建模', limits)
            self.assertIn('沒有與原盒結合', limits)
            self.assertIn('盲孔底部不可見', limits)
        self.assertIn('7.9615／3.9807', steps[1]['success'])
        self.assertIn('孔深7 mm、底厚1 mm', steps[2]['success'])


if __name__ == '__main__':
    unittest.main()
