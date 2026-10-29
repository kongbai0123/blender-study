"""檢查題目對應既有章節、畫面、來源與明示的證據範圍。"""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / 'learning/web/challenges/challenges-v001.json'
COURSE = ROOT / 'learning/web/engineering-curriculum-v030.json'


class ChallengesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding='utf-8'))
        cls.course = json.loads(COURSE.read_text(encoding='utf-8'))

    def test_each_chapter_and_section_has_valid_references(self):
        rows = self.data['chapters']
        self.assertEqual([row['chapterId'] for row in rows], [c['id'] for c in self.course['chapters']])
        self.assertEqual(len({row['challengeId'] for row in rows}), 12)
        by_chapter = {c['id']: {s['id'] for s in c['sections']} for c in self.course['chapters']}
        for row in rows:
            sections = by_chapter[row['chapterId']]
            self.assertTrue(row['requirements'] and row['checks'] and row['limitations'])
            self.assertEqual(len(row['hints']), 3)
            self.assertTrue(all(h['section'] in sections and h['text'] for h in row['hints']))
            self.assertTrue(all(s['chapterId'] == row['chapterId'] and s['sectionId'] in sections for s in row['sourceSteps']))

    def test_original_blender_screenshots_exist_with_hash_and_scope(self):
        for row in self.data['chapters']:
            shot = row['screenshot']
            path = ROOT / shot['path']
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), shot['sha256'])
            self.assertIn('並非本題完整示範', shot['caption'])
            self.assertIn('並非此題逐步驗證或學員完成', row['evidenceStatus'])

    def test_special_workspaces_and_drawing_status_are_explicit(self):
        rows = {row['chapterId']: row for row in self.data['chapters']}
        self.assertEqual(rows['ch03']['challengeId'], 'box-opening-v001')
        self.assertEqual(rows['ch03']['pilotPath'], '/pilot/box-lesson.html')
        self.assertEqual(rows['ch07']['workspaceId'], 'engineering-parametric')
        self.assertEqual(rows['ch08']['workspaceId'], 'engineering-parametric')
        for chapter in ('ch05', 'ch06'):
            self.assertEqual(rows[chapter]['drawing']['path'], '/challenges/fit-trial-drawing-v003.svg')
        self.assertIsNone(rows['ch09']['drawing'])
        self.assertIn('尚待製作', rows['ch09']['drawingStatus'])


if __name__ == '__main__':
    unittest.main()
