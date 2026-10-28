"""驗證題目 v003 只補已核對圖與證據，不改舊題目、進度或檔案。"""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'learning/web/challenges/challenges-v002.json'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v003.json'
SPEC = importlib.util.spec_from_file_location('challenge_builder_v003', ROOT / 'learning/build_challenges_v003.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ChallengesV003Tests(unittest.TestCase):
    def setUp(self):
        self.old_bytes = SOURCE.read_bytes()
        self.old = json.loads(self.old_bytes)
        self.new = json.loads(OUTPUT.read_bytes())

    def test_source_hash_and_builder_match(self):
        self.assertEqual(sha256(self.old_bytes).hexdigest(), builder.EXPECTED)
        self.assertEqual(self.new, builder.build())
        self.assertEqual(self.new['previousVersion']['sha256'], builder.EXPECTED)

    def test_only_requested_chapters_are_changed(self):
        old, new = deepcopy(self.old), deepcopy(self.new)
        new['version'] = old['version']
        new['previousVersion'] = old['previousVersion']
        for row in new['chapters']:
            chapter = row['chapterId']
            if chapter in builder.DRAWINGS:
                original = next(x for x in old['chapters'] if x['chapterId'] == chapter)
                self.assertEqual(row['drawing'], builder.DRAWINGS[chapter])
                self.assertEqual(row['drawingStatus'], builder.DRAWING_STATUS[chapter])
                row['drawing'], row['drawingStatus'] = original['drawing'], original['drawingStatus']
            if chapter == 'ch11':
                self.assertEqual(row.pop('extraDemos'), builder.EXTRA_DEMOS)
        self.assertEqual(new, old)

    def test_images_and_summaries_are_hash_bound_and_qualified(self):
        for chapter, drawing in builder.DRAWINGS.items():
            self.assertEqual(sha256((ROOT / 'learning/web' / drawing['path'].lstrip('/')).read_bytes()).hexdigest(), drawing['sha256'])
        self.assertIn('不同保存階段', builder.DRAWING_STATUS['ch07'])
        self.assertIn('固定基準', builder.DRAWING_STATUS['ch08'])
        self.assertIn('試驗總間隙', builder.DRAWING_STATUS['ch08'])
        for demo in builder.EXTRA_DEMOS:
            self.assertEqual(sha256((ROOT / demo['screenshot']['path']).read_bytes()).hexdigest(), demo['screenshot']['sha256'])
            self.assertEqual(sha256((ROOT / demo['summaryPath']).read_bytes()).hexdigest(), demo['summarySha256'])
            self.assertIn('程式建立', demo['description'])
        self.assertIn('不完整', builder.EXTRA_DEMOS[0]['description'])
        self.assertIn('尚無蓋孔', builder.EXTRA_DEMOS[1]['description'])

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='challenge-v003-test-') as folder:
            output = Path(folder) / 'challenges-v003.json'
            output.write_bytes(b'keep')
            with mock.patch.object(builder, 'OUTPUT', output), self.assertRaises(FileExistsError):
                builder.main()
            self.assertEqual(output.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
