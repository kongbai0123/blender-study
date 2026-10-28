"""Check evidence, source coverage and presentation contract of the new path."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class CurriculumV002Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_json('learning/web/engineering-curriculum-v002.json')
        cls.catalog = read_json('learning/catalog.json')
        cls.original = {s['id']: s for lesson in cls.catalog['lessons'] for s in lesson['steps']}

    def test_chapters_and_unique_microsteps(self):
        chapters = self.data['chapters']
        self.assertEqual([c['id'] for c in chapters], [f'ch{x:02d}' for x in range(1, 13)])
        seen = set()
        for chapter in chapters:
            self.assertTrue(chapter['goal'])
            self.assertTrue(chapter['limitations'])
            self.assertTrue(chapter['steps'])
            for step in chapter['steps']:
                self.assertNotIn(step['id'], seen)
                seen.add(step['id'])
                self.assertTrue(step['context'])
                self.assertTrue(step['success'])
                self.assertGreaterEqual(len(step['actions']), 1)
                self.assertLessEqual(len(step['actions']), 3)
                self.assertIn(step['evidenceStatus'], self.data['evidenceStatusDefinitions'])
                self.assertTrue(step['limitations'] or step['evidenceStatus'] == 'concept_only')

    def test_covered_original_steps_and_no_fake_pending_demo(self):
        refs = set()
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for ref in step['sourceSteps']:
                    sid = ref['stepId']
                    self.assertEqual(ref['lessonId'], sid[:2])
                    self.assertIn(sid, self.original)
                    refs.add(sid)
                    if sid in ('08-02', '08-03', '08-04', '08-05', '09-01', '09-02', '09-03'):
                        self.assertEqual(step['evidenceStatus'], 'draft_pending_demo')
        self.assertEqual(refs, set(self.original))

    def test_all_original_images_and_shortcut_sources_match_hash(self):
        checked = set()
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for figure in step['figures']:
                    self.assertEqual(figure['type'], 'screenshot')
                    self.assertTrue(figure['caption'])
                    checked.add((figure['path'], figure['sha256']))
                for shortcut in step['shortcuts']:
                    self.assertTrue(shortcut['keys'])
                    self.assertIsInstance(shortcut['requirements'], list)
                    self.assertIsInstance(shortcut['cautions'], list)
                    for evidence in shortcut['evidence']:
                        if evidence.get('path') and evidence.get('sha256'):
                            checked.add((evidence['path'], evidence['sha256']))
        self.assertGreater(len(checked), 20)
        for rel, expected in checked:
            self.assertTrue(rel.startswith('learning/evidence/'), rel)
            resolved = (ROOT / rel).resolve()
            self.assertTrue(resolved.is_relative_to(ROOT.resolve()))
            self.assertEqual(hashlib.sha256(resolved.read_bytes()).hexdigest(), expected, rel)

    def test_practical_boundaries_are_preserved(self):
        limits = {c['id']: ' '.join(c['limitations']) for c in self.data['chapters']}
        self.assertIn('試驗', limits['ch02'])
        self.assertIn('0.399994', limits['ch06'])
        self.assertIn('448', limits['ch08'])
        self.assertIn('待定', limits['ch09'])
        self.assertIn('08-02', limits['ch10'])
        self.assertEqual(self.data['contentReview']['learnerProgressChanged'], False)


if __name__ == '__main__':
    unittest.main()
