"""Verify v006 only corrects boss evidence semantics; prior step IDs stay valid."""
import hashlib
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v005.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v006.json'
ALLOWED = {
    'ch10-boss-draft-observe': {'limitations'},
    'ch10-boss-draft-diameter': {'limitations', 'context', 'actions', 'success', 'figures'},
    'ch10-boss-draft-depth': {'limitations', 'goal', 'context', 'actions', 'success', 'figures'},
    'ch10-boss-draft-save': {'limitations', 'success'},
}


class CurriculumV006Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_bytes = OLD.read_bytes()
        cls.old = json.loads(cls.old_bytes)
        cls.new = json.loads(NEW.read_text(encoding='utf-8'))

    def test_only_documented_fields_changed_and_order_preserved(self):
        self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(), '9cc2e9e54ac587669cd90cc19f5fe08cce8952af11cde412cb4674e648aaedff')
        self.assertEqual(self.old['id'], self.new['id'])
        self.assertEqual(self.new['id'], 'engineering-curriculum-v002')
        self.assertIn('v006', self.new['version'])
        changes = {}
        for old, new in zip(self.old['chapters'], self.new['chapters']):
            self.assertEqual(old['id'], new['id'])
            self.assertEqual([s['id'] for s in old['steps']], [s['id'] for s in new['steps']])
            self.assertEqual({k:v for k,v in old.items() if k != 'steps'}, {k:v for k,v in new.items() if k != 'steps'})
            for a,b in zip(old['steps'],new['steps']):
                self.assertEqual(set(a), set(b))
                diffs = {k for k in a if a[k] != b[k]}
                if a['id'] in ALLOWED:
                    self.assertEqual(diffs, ALLOWED[a['id']])
                else:
                    self.assertEqual(diffs, set(), a['id'])
                for field in diffs:
                    changes[(a['id'], field)] = (a[field], b[field])
        records = self.new['contentReview']['correctionsV006']
        self.assertEqual(len(records), len(changes))
        for record in records:
            self.assertEqual(changes[(record['stepId'],record['field'])], (record['before'],record['after']))
        self.assertEqual(sum(len(c['steps']) for c in self.new['chapters']), 172)

    def test_polygon_and_blind_bottom_claims_are_explicitly_classified(self):
        chapter = next(c for c in self.new['chapters'] if c['id'] == 'ch10')
        boss = {s['id']:s for s in chapter['steps'] if s['id'].startswith('ch10-boss-draft-')}
        for step in boss.values():
            limits = ' '.join(step['limitations'])
            self.assertIn('理想正32邊形公式推算', limits)
            self.assertIn('尚非實際投影量測', limits)
            self.assertIn('孔深與底厚由網格 Z 邊界讀值推得', limits)
            self.assertIn('未驗證彼此無干涉', limits)
        diameter = boss['ch10-boss-draft-diameter']
        self.assertIn('對頂網格讀值', diameter['success'])
        self.assertIn('非實際投影量測', diameter['success'])
        self.assertAlmostEqual(8*math.cos(math.pi/32),7.961477813377575)
        self.assertAlmostEqual(4*math.cos(math.pi/32),3.9807389066887877)
        self.assertIn('由網格 Z 邊界讀值推得', boss['ch10-boss-draft-depth']['success'])
        self.assertIn('未核對彼此是否干涉', boss['ch10-boss-draft-save']['success'])

    def test_images_artifacts_and_sources_have_original_hashes(self):
        checked = set()
        for chapter in self.new['chapters']:
            for step in chapter['steps']:
                for fig in step['figures']:
                    self.assertEqual(fig['type'], 'screenshot')
                    checked.add((fig['path'],fig['sha256']))
                for artifact in step.get('artifacts',[]):
                    checked.add((artifact['path'],artifact['sha256']))
                for shortcut in step['shortcuts']:
                    for item in shortcut['evidence']:
                        if item.get('path') and item.get('sha256'):
                            checked.add((item['path'],item['sha256']))
        for source in self.new['sourceVersions']:
            checked.add((source['path'],source['sha256']))
        for rel, expected in checked:
            path = (ROOT / rel).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, rel)


if __name__ == '__main__':
    unittest.main()
