"""v028 keeps each original lesson whole and in order, has no duplicate steps, and separates trial logs."""
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'learning/web'
OLD, NEW = WEB / 'engineering-curriculum-v027.json', WEB / 'engineering-curriculum-v028.json'
PATH_OLD, PATH_NEW = WEB / 'engineering-path-v001.json', WEB / 'engineering-path-v002.json'
STATUSES = {'existing_demo', 'source_step_demo', 'concept_only', 'draft_pending_demo'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(step):
    return {key: value for key, value in step.items() if key != 'id'}


class CurriculumV028Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.data = read(OLD), read(NEW)
        cls.path_old, cls.path = read(PATH_OLD), read(PATH_NEW)
        cls.catalog = read(ROOT / 'learning/catalog.json')
        cls.steps = [(chapter['id'], step) for chapter in cls.data['chapters'] for step in chapter['steps']]
        cls.learner = [(cid, step) for cid, step in cls.steps if step.get('track') != 'appendix']

    def test_history_is_untouched(self):
        self.assertEqual(sha(OLD), '615b1ef2f3482b1f585548a82ab0cf86528c546e42a792cccaeaa0dbb935be2b')
        self.assertEqual(sha(PATH_OLD), '6dcc77a613a905f35cd793e96c6d20ad0c39bb4cf915a30de5f0fddd1e1dca5f')
        self.assertEqual(sha(NEW), 'f7ff40301a86d9eea544f02f6a7f006f31345f84f1781ad81052de220294a188')
        self.assertEqual(sha(PATH_NEW), '28cfa6959794d6e6423459cd7ab5e7b376e4c487adc23432078c8be4bfdadf95')
        self.assertEqual(self.data['id'], self.old['id'])
        self.assertIn({'path': 'learning/web/engineering-curriculum-v027.json', 'sha256': sha(OLD)}, self.data['sourceVersions'])

    def test_each_original_lesson_is_whole_ordered_and_in_one_chapter(self):
        catalog_order = [step['id'] for lesson in self.catalog['lessons'] for step in lesson['steps']]
        chapter_of = {}
        for cid, step in self.learner:
            for ref in step.get('sourceSteps', []):
                chapter_of.setdefault(ref['lessonId'], set()).add(cid)
        self.assertEqual(chapter_of['01'], {'ch01'})
        self.assertEqual(chapter_of['02'], {'ch03'})
        self.assertEqual(chapter_of['03'], {'ch12'})
        for chapter in self.data['chapters']:
            sources = [step['sourceSteps'][0]['stepId'] for step in chapter['steps']
                       if step.get('track') != 'appendix' and len(step.get('sourceSteps', [])) == 1]
            for lesson in self.catalog['lessons']:
                positions = [catalog_order.index(s) for s in sources if s.startswith(lesson['id'] + '-')]
                with self.subTest(chapter=chapter['id'], lesson=lesson['id']):
                    self.assertEqual(positions, sorted(positions))
        mapped = {ref['stepId'] for _, step in self.learner for ref in step.get('sourceSteps', [])}
        self.assertEqual(mapped, set(catalog_order))

    def test_saving_comes_before_the_steps_that_depend_on_it(self):
        ids = [step['id'] for _, step in self.learner]
        self.assertLess(ids.index('ch01-01-04-01'), ids.index('ch01-01-07-01'))
        self.assertLess(ids.index('ch01-01-09-03'), ids.index('ch03-02-01-01'))
        self.assertLess(ids.index('ch03-02-04-03'), ids.index('ch03-02-07-03'))
        self.assertLess(ids.index('ch04-setup-02'), ids.index('ch04-sketch-01'))
        self.assertLess(ids.index('ch05-guard-prepare-01'), ids.index('ch05-manual-guard-01'))
        order = {chapter['id']: index for index, chapter in enumerate(self.data['chapters'])}
        home = {ref['stepId']: cid for cid, step in self.learner for ref in step.get('sourceSteps', [])}
        for cid, step in self.learner:
            text = ' '.join([step.get('context', ''), step.get('success', '')] + step['actions'])
            own = {ref['stepId'] for ref in step.get('sourceSteps', [])}
            # A step may point at its own source (e.g. observing 05-05 screenshots in ch01); other refs must come earlier.
            for ref in re.findall(r'(?<![\d.-])(0\d-0\d)(?!\d)', text):
                if ref in home and ref not in own:
                    self.assertLessEqual(order[home[ref]], order[cid], (step['id'], ref))

    def test_no_duplicates_and_id_changes_are_recorded(self):
        ids = [step['id'] for _, step in self.steps]
        self.assertEqual(len(ids), len(set(ids)))
        bodies = [json.dumps(body(step), ensure_ascii=False, sort_keys=True) for _, step in self.steps]
        self.assertEqual(len(bodies), len(set(bodies)))
        old_ids = {step['id'] for chapter in self.old['chapters'] for step in chapter['steps']}
        review = self.data['contentReview']['reviewV028']
        self.assertEqual(old_ids - set(ids), set(self.data['stepIdChanges']) | set(review['removedDuplicates']))
        self.assertEqual(set(ids) - old_ids, set(self.data['stepIdChanges'].values()) | set(review['newSteps']))
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                self.assertTrue(step['id'].startswith(chapter['id'] + '-'), step['id'])
        self.assertEqual((len(self.learner), len(self.steps) - len(self.learner)), (225, 30))

    def test_appendix_holds_only_trial_logs(self):
        appendix = {step['id'] for _, step in self.steps if step.get('track') == 'appendix'}
        self.assertEqual(appendix, set(self.data['contentReview']['reviewV028']['appendixSteps']))
        for cid, step in self.learner:
            text = json.dumps({k: step.get(k) for k in ('title', 'goal', 'actions')}, ensure_ascii=False)
            for marker in ('假 progress', '故障', '失敗探測', '未完成的版本拒絕測試'):
                self.assertNotIn(marker, text, step['id'])
        for chapter in self.data['chapters']:
            if any(step.get('track') == 'appendix' for step in chapter['steps']):
                self.assertTrue(chapter['appendix']['title'])
                tracks = [step.get('track') == 'appendix' for step in chapter['steps']]
                self.assertEqual(tracks, sorted(tracks), chapter['id'])

    def test_statuses_match_their_evidence_and_refs_are_intact(self):
        for _, step in self.steps:
            self.assertIn(step['evidenceStatus'], STATUSES, step['id'])
            own = bool(step.get('figures') or step.get('artifacts'))
            if step['evidenceStatus'] == 'source_step_demo':
                self.assertFalse(own, step['id'])
                self.assertTrue(step['sourceSteps'], step['id'])
            if step['evidenceStatus'] == 'existing_demo':
                self.assertTrue(own, step['id'])
            refs = list(step.get('figures', [])) + list(step.get('artifacts', []))
            for shortcut in step.get('shortcuts', []):
                refs += shortcut.get('evidence', [])
            for ref in refs:
                path = (ROOT / ref['path']).resolve()
                self.assertTrue(path.is_relative_to(ROOT.resolve()) and path.is_file(), ref['path'])
                self.assertEqual(sha(path), ref['sha256'], ref['path'])
        for ref in self.data['sourceVersions']:
            self.assertEqual(sha(ROOT / ref['path']), ref['sha256'], ref['path'])

    def test_new_steps_are_drafts_with_verifiable_facts(self):
        steps = dict((step['id'], step) for _, step in self.steps)
        for step_id in self.data['contentReview']['reviewV028']['newSteps']:
            self.assertEqual(steps[step_id]['evidenceStatus'], 'draft_pending_demo', step_id)
            self.assertTrue(steps[step_id]['limitations'], step_id)
        self.assertIn('b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59', steps['ch04-setup-01']['success'])
        self.assertIn('Install from Disk', ' '.join(steps['ch04-setup-02']['actions']))
        self.assertIn('engineering-workspace --copy-manual-box', ' '.join(steps['ch05-guard-prepare-01']['actions']))
        self.assertIn('--workspace engineering-parametric', ' '.join(steps['ch05-guard-checkpoint-01']['actions']))

    def test_path_v002_carries_the_display_text_the_page_used_to_patch(self):
        self.assertEqual([c['id'] for c in self.path['chapters']], [c['id'] for c in self.data['chapters']])
        for chapter in self.path['chapters']:
            self.assertTrue(chapter['availabilityLabel'], chapter['id'])
        follow = self.path['followUpActivity']
        self.assertEqual(follow['curriculumStep'], 'ch01-fit-surfaces')
        for figure in follow['figures'] + self.path['firstActivity']['figures']:
            self.assertEqual(sha(ROOT / figure['path']), figure['sha256'])
        refs = {chapter['id']: {ref['stepId'] for ref in chapter['references']} for chapter in self.path['chapters']}
        self.assertIn('01-04', refs['ch01'])
        self.assertNotIn('01-04', refs['ch11'])
        self.assertNotIn('01-07', refs['ch03'])

    def test_builder_refuses_to_overwrite(self):
        before = (NEW.read_bytes(), PATH_NEW.read_bytes())
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v028.py'],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(before, (NEW.read_bytes(), PATH_NEW.read_bytes()))


if __name__ == '__main__':
    unittest.main()
