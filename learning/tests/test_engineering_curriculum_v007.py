"""Verify render output and genuine UI screenshots are classified separately."""
import hashlib
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v006.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v007.json'


class CurriculumV007Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_bytes = OLD.read_bytes()
        cls.old = json.loads(cls.old_bytes)
        cls.new = json.loads(NEW.read_text(encoding='utf-8'))

    def test_v006_is_preserved_with_stable_step_ids(self):
        self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(), 'ae76637b949603e9e213c1f1f8237e0c2a8127e8ae77ab1717474bd76bb76a9e')
        self.assertEqual(self.old['id'], self.new['id'])
        self.assertEqual(self.new['id'], 'engineering-curriculum-v002')
        self.assertIn('v007', self.new['version'])
        self.assertEqual([c['id'] for c in self.old['chapters']], [c['id'] for c in self.new['chapters']])
        for old, new in zip(self.old['chapters'], self.new['chapters']):
            self.assertEqual(old['steps'], new['steps'][:len(old['steps'])])
            if old['id'] != 'ch12':
                self.assertEqual(old, new)
        self.assertEqual(sum(len(c['steps']) for c in self.old['chapters']), 172)
        self.assertEqual(sum(len(c['steps']) for c in self.new['chapters']), 176)

    def test_source_image_and_artifact_hashes_and_unique_ids(self):
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
                    checked.add((fig['path'],fig['sha256']))
                for artifact in step.get('artifacts',[]):
                    self.assertTrue(artifact['label'])
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

    def test_render_result_png_is_not_a_screenshot_or_fit_evidence(self):
        chapter = next(c for c in self.new['chapters'] if c['id'] == 'ch12')
        steps = [s for s in chapter['steps'] if s['id'].startswith('ch12-box-render-')]
        self.assertEqual(len(steps),4)
        self.assertEqual(steps[0]['id'], 'ch12-box-render-safe-copy')
        self.assertEqual(steps[0]['evidenceStatus'], 'draft_pending_demo')
        self.assertIn('個人工作區', steps[0]['actions'][0])
        self.assertIn('Output Properties', steps[0]['actions'][0])
        for step in steps:
            limits=' '.join(step['limitations'])
            self.assertIn('上移18 mm由程式設定',limits)
            self.assertIn('原生 GUI 事件',limits)
            self.assertIn('程式 save_render',limits)
            self.assertIn('不能證明尺寸配合',limits)
            self.assertIn('直接開證據原檔仍可能寫入 evidence',limits)
        artifact = self.new['boxRenderVerification']['renderOutput']
        self.assertEqual(artifact['type'], 'render-output-png')
        self.assertFalse(any(fig['path'] == artifact['path'] for s in steps for fig in s['figures']))
        body = (ROOT / artifact['path']).read_bytes()
        self.assertEqual(body[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II', body[16:24]), (640,480))
        verified = self.new['boxRenderVerification']
        self.assertIsNone(verified['physicalMeasurements'])
        self.assertIsNone(verified['fitResults'])
        self.assertIsNone(verified['qualifiedClearanceMm'])


if __name__ == '__main__':
    unittest.main()
