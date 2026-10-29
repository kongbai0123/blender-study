"""題目 v002 源自凍結 v001，只增補第 02／09／10 章題圖。"""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'learning/web/challenges/challenges-v001.json'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v002.json'
SPEC = importlib.util.spec_from_file_location('challenge_builder_v002', ROOT / 'learning/build_challenges_v002.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ChallengesV002Tests(unittest.TestCase):
    def setUp(self):
        self.old_bytes = SOURCE.read_bytes()
        self.old = json.loads(self.old_bytes)
        self.new = json.loads(OUTPUT.read_bytes())

    def test_source_and_builder_output_match(self):
        self.assertEqual(sha256(self.old_bytes).hexdigest(), builder.EXPECTED)
        self.assertEqual(self.new, builder.build())
        self.assertEqual(self.new['version'], 'v002')
        self.assertEqual(self.new['previousVersion']['sha256'], builder.EXPECTED)

    def test_only_requested_chapter_drawings_changed(self):
        old, new = deepcopy(self.old), deepcopy(self.new)
        new['version'] = old['version']
        del new['previousVersion']
        for row in new['chapters']:
            if row['chapterId'] in builder.DRAWINGS:
                original = next(x for x in old['chapters'] if x['chapterId'] == row['chapterId'])
                self.assertEqual(row['drawing'], builder.DRAWINGS[row['chapterId']])
                self.assertEqual(row['drawingStatus'], builder.STATUS[row['chapterId']])
                row['drawing'], row['drawingStatus'] = original['drawing'], original['drawingStatus']
        self.assertEqual(new, old)

    def test_drawing_files_match_frozen_hash_and_safety_labels(self):
        for chapter, definition in builder.DRAWINGS.items():
            drawing = ROOT / 'learning/web' / definition['path'].lstrip('/')
            self.assertEqual(sha256(drawing.read_bytes()).hexdigest(), definition['sha256'])
        self.assertIn('試驗值', builder.STATUS['ch02'])
        self.assertIn('定位柱', builder.STATUS['ch09'])
        self.assertIn('未證調整改善', builder.STATUS['ch10'])

    def test_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory(prefix='challenge-v002-test-') as folder:
            existing = Path(folder) / 'challenges-v002.json'
            existing.write_bytes(b'keep')
            with mock.patch.object(builder, 'OUTPUT', existing), self.assertRaises(FileExistsError):
                builder.main()
            self.assertEqual(existing.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
