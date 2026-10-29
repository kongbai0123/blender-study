"""v029 follows the learner-approved order B, splits every chapter into sections and keeps all v028 content traceable."""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'learning/web'
OLD, NEW = WEB / 'engineering-curriculum-v028.json', WEB / 'engineering-curriculum-v029.json'
PATH_OLD, PATH_NEW = WEB / 'engineering-path-v002.json', WEB / 'engineering-path-v003.json'
ORDER = ['基本操作與小盒用途', '公差、間隙與量測觀念', '毫米建模與必要編輯', '訊號站材質、燈光與渲染', '配合試片與試驗設計',
         '匯出、列印、量測與試配', '草圖、標尺寸與約束', '盒體與上蓋參數連動', '定位榫與燕尾滑蓋', '懸臂卡扣與對照試片',
         '螺紋與螺絲固定', '尺寸鏈、交付與成品渲染']


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_of(step):
    return ' '.join([step.get('context', ''), step.get('success', '')] + step['actions'])


class CurriculumV029Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.data, cls.path = read(OLD), read(NEW), read(PATH_NEW)
        cls.catalog = read(ROOT / 'learning/catalog.json')
        cls.steps = [(chapter['id'], step) for chapter in cls.data['chapters'] for step in chapter['steps']]
        cls.main = [(cid, step) for cid, step in cls.steps if not step.get('track')]
        cls.by_id = {step['id']: (cid, step) for cid, step in cls.steps}

    def test_pointer_and_history(self):
        spec = importlib.util.spec_from_file_location('pointer_manage_v029', ROOT / 'learning/manage.py')
        manage = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manage)
        # v030 起指標改指向新版；這裡只確認 v029 與 path v003 不再變動。
        self.assertEqual(sha(PATH_NEW), '9cb08486d3de4c3225aebb9de1ff8471b5902026c84320f4b97a42a5d64962b0')
        self.assertEqual(sha(NEW), 'c042a30f169541b3087e1a9919320b689745cb170813a4f8ab0bf569b9a6edc1')
        self.assertEqual(sha(OLD), 'f7ff40301a86d9eea544f02f6a7f006f31345f84f1781ad81052de220294a188')
        self.assertEqual(sha(PATH_OLD), '28cfa6959794d6e6423459cd7ab5e7b376e4c487adc23432078c8be4bfdadf95')
        self.assertEqual(self.data['id'], self.old['id'])

    def test_order_b_and_counts(self):
        self.assertEqual([chapter['title'] for chapter in self.data['chapters']], ORDER)
        self.assertEqual([chapter['title'] for chapter in self.path['chapters']], ORDER)
        tracks = [step.get('track', 'main') for _, step in self.steps]
        self.assertEqual((tracks.count('main'), tracks.count('optional'), tracks.count('appendix')), (245, 11, 30))
        homes = {}
        for cid, step in self.main:
            for ref in step.get('sourceSteps', []):
                homes.setdefault(ref['lessonId'], set()).add(cid)
        self.assertEqual((homes['01'], homes['02'], homes['03']), ({'ch01'}, {'ch03'}, {'ch04'}))
        index = {chapter['id']: n for n, chapter in enumerate(self.data['chapters'])}
        # Coupons are printed and measured before CAD Sketcher and the parametric lid.
        self.assertLess(index[self.by_id['ch06-fit-04'][0]], index[self.by_id['ch07-sketch-01'][0]])
        self.assertLess(index[self.by_id['ch04-03-05-02'][0]], index[self.by_id['ch05-05-02-01'][0]])

    def test_every_main_step_sits_in_a_section_in_order(self):
        for chapter in self.data['chapters']:
            ids = [section['id'] for section in chapter['sections']]
            self.assertEqual(ids, ['%s-%02d' % (chapter['number'], n) for n in range(1, len(ids) + 1)], chapter['id'])
            seen = [step['section'] for step in chapter['steps'] if step.get('track') != 'appendix']
            self.assertEqual(seen, sorted(seen, key=ids.index), chapter['id'])
            self.assertTrue(set(ids) <= set(seen), chapter['id'])
            for step in chapter['steps']:
                self.assertTrue(step['id'].startswith(chapter['id'] + '-'), step['id'])
                self.assertNotIn(' · ', step['title'], step['id'])
        optional = {step['id'] for _, step in self.steps if step.get('track') == 'optional'}
        self.assertEqual({self.by_id[s][1]['section'] for s in optional}, {'08-08'})

    def test_basics_come_before_their_use(self):
        ids = [step['id'] for _, step in self.main]
        first = lambda pattern: next(i for i, (_, step) in enumerate(self.main) if re.search(pattern, text_of(step)))
        self.assertEqual(ids[0], 'ch01-01-01-01')
        self.assertEqual(ids[ids.index('ch01-observe-lip') + 1], 'ch01-fit-surfaces')
        self.assertLess(ids.index('ch01-01-04-01'), ids.index('ch01-01-07-01'))
        self.assertLess(ids.index('ch03-edit-05'), ids.index('ch03-05-05-05'))
        self.assertGreaterEqual(first(r'按 I，'), ids.index('ch03-edit-05'))
        self.assertGreaterEqual(first(r'按 H'), ids.index('ch03-edit-06'))
        self.assertGreaterEqual(first(r'Viewpoint > Bottom'), ids.index('ch03-edit-07'))
        self.assertLess(ids.index('ch03-04-06-04'), ids.index('ch03-05-05-01'))

    def test_v028_content_is_kept_replaced_or_appendixed(self):
        old_ids = {step['id'] for chapter in self.old['chapters'] for step in chapter['steps']}
        new_ids = set(self.by_id)
        changes, replaced = self.data['stepIdChanges'], self.data['replacedSteps']
        for old_id in old_ids:
            with self.subTest(old_id):
                if old_id in replaced:
                    self.assertTrue(set(replaced[old_id]) <= new_ids)
                else:
                    self.assertIn(changes.get(old_id, old_id), new_ids)
        self.assertEqual(sorted(new_ids - {changes.get(i, i) for i in old_ids} - {n for ids in replaced.values() for n in ids}),
                         sorted(set(self.data['contentReview']['reviewV029']['newSteps']) - {n for ids in replaced.values() for n in ids}))

    def test_rewritten_chapters_give_learner_instructions(self):
        for cid, step in self.main:
            if int(cid[2:]) > 6:
                continue
            with self.subTest(step['id']):
                self.assertTrue(1 <= len(step['actions']) <= 3)
                joined = text_of(step)
                for marker in ('程式讀回', '摘要', '助教畫面', '觀察示範'):
                    self.assertNotIn(marker, ' '.join(step['actions']))
                self.assertNotIn('第三單元', joined)
        plate = self.by_id['ch05-05-03-08'][1]
        self.assertIn('39', plate['actions'][0])
        self.assertIn('2.2mm', ' '.join(self.by_id['ch03-05-05-05'][1]['actions']))

    def test_status_matches_evidence_and_refs_are_intact(self):
        for _, step in self.steps:
            own = bool(step.get('figures') or step.get('artifacts'))
            if step['evidenceStatus'] == 'existing_demo':
                self.assertTrue(own, step['id'])
            if step['evidenceStatus'] == 'source_step_demo':
                self.assertFalse(own, step['id'])
                self.assertTrue(step['sourceSteps'], step['id'])
            refs = list(step.get('figures', [])) + list(step.get('artifacts', []))
            for shortcut in step.get('shortcuts', []):
                refs += shortcut.get('evidence', [])
            for ref in refs:
                self.assertEqual(sha(ROOT / ref['path']), ref['sha256'], ref['path'])
        lip = self.by_id['ch01-observe-lip'][1]
        self.assertEqual(lip['legacyActivity'], 'path-01-observe-lip')
        self.assertNotIn('firstActivity', self.path)
        self.assertNotIn('followUpActivity', self.path)

    def test_builder_refuses_to_overwrite(self):
        before = (NEW.read_bytes(), PATH_NEW.read_bytes())
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v029.py'],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(before, (NEW.read_bytes(), PATH_NEW.read_bytes()))


if __name__ == '__main__':
    unittest.main()
