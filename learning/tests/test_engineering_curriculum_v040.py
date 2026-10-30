"""Current lesson completion, evidence scope, and shared-state protection."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'learning'
PATCH = L / 'patches/2026-10-30-chapter-completion-v040'
FORMAL = L / 'web/engineering-curriculum-v040.json'
CURRENT = FORMAL if FORMAL.exists() else PATCH / 'candidate/engineering-curriculum-v040.json'
sys.path.insert(0, str(L))
from build_engineering_curriculum_v040 import build, SOURCE, SOURCE_SHA, PHOTOS, FAST
from chapter_page_frontend_v002 import make_assets


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompletedLessonPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read(CURRENT)
        cls.old = read(SOURCE)
        cls.cards = [c for s in cls.data['chapterPages']['sections'].values()
                     for c in [s.get('prep'), *s['steps']] if c]

    def test_history_ids_tracks_and_mainline_are_preserved(self):
        self.assertEqual(sha(SOURCE), SOURCE_SHA)
        self.assertEqual(self.data['id'], self.old['id'])
        before = [(ch['id'], s['id'], s.get('track')) for ch in self.old['chapters'] for s in ch['steps']]
        after = [(ch['id'], s['id'], s.get('track')) for ch in self.data['chapters'] for s in ch['steps']]
        self.assertEqual(before, after)
        self.assertEqual(sum(not track for _, _, track in after), 243)

    def test_all_85_sections_are_real_pages(self):
        pages = self.data['chapterPages']['sections']
        self.assertEqual(len(pages), 85)
        self.assertEqual(len(self.cards), 447)
        self.assertEqual(len({c['stepId'] for c in self.cards}), 447)
        for section in pages.values():
            self.assertTrue(section.get('prep') or section['steps'], section['id'])
        for card in self.cards:
            self.assertTrue(1 <= len(card['actions']) <= 3, card['stepId'])
            self.assertTrue(2 <= len(card['checks']) <= 3, card['stepId'])
            self.assertTrue(card.get('figure') or card.get('figures'), card['stepId'])

    def test_30_new_photos_have_individual_saved_versions_and_honest_scope(self):
        records = read(PHOTOS / 'run.json')['records']
        self.assertEqual(len(records), 30)
        self.assertEqual(len({r['sha256'] for r in records}), 30)
        for r in records:
            self.assertEqual(sha(PHOTOS / r['file']), r['sha256'])
            observed = r['observed']
            self.assertEqual(sha(ROOT / observed['preparedScene']['path']), observed['preparedScene']['sha256'])
            for key in ['physicalPrint', 'physicalMeasurement', 'physicalFit']:
                self.assertIsNone(observed[key])
            self.assertIn(observed['role'], ['digital_preparation', 'version_reference', 'physical_preparation'])
        for folder in [PHOTOS, FAST]:
            status = read(folder / 'runner-status.json')
            self.assertEqual(status['status'], 'completed')
            self.assertTrue(status['workspacesUnchanged'])

    def test_all_referenced_photos_preserve_native_bytes(self):
        for card in self.cards:
            for f in ([card['figure']] if card.get('figure') else card.get('figures', [])):
                self.assertEqual(sha(L / f['path']), f['sha256'])
                self.assertLessEqual(len(f['marks']), 3)
                width, height = f['size']
                for m in f['marks']:
                    x, y, w, h = m['box']
                    self.assertTrue(x >= 0 and y >= 0 and x+w <= width and y+h <= height)

    def test_shortcut_trial_is_six_independent_meshes_with_different_widths(self):
        checks = read(FAST / 'verification.json')['checks']
        self.assertTrue(all(c['passed'] for c in checks))
        actual = next(c['readback'] for c in checks if c['case'] == 'six-varied-cutters')['objects']
        self.assertEqual(len(actual), 6)
        self.assertEqual(len({o['mesh'] for o in actual}), 6)
        for i, obj in enumerate(actual):
            self.assertAlmostEqual(obj['location'][0], 14*i, places=4)
            for axis in [0,1]:
                self.assertAlmostEqual(obj['dimensions'][axis], 10.1+.1*i, places=4)
            self.assertAlmostEqual(obj['dimensions'][2], 8, places=4)

    def test_candidate_is_reproducible_and_csp_safe(self):
        self.assertEqual(build(), self.data)
        html, css, js = make_assets((L / 'drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
        for name, expected in [('index.html',html), ('chapter-pages-v001.css',css), ('chapter-pages-v001.js',js)]:
            self.assertEqual((CURRENT.parent / name).read_text('utf8'), expected)
        self.assertNotIn('<script>', html)
        self.assertNotIn('<style>', html)
        self.assertNotIn('method:', js)
        self.assertIn('mainlineKeys.has', js)
        self.assertIn('script-src \'self\'', (L / 'server.py').read_text('utf8'))

    def test_chapter_renderer_does_not_render_cross_course_resume(self):
        text = (CURRENT.parent / 'engineering-path.js').read_text('utf8')
        self.assertNotIn('${nextButton}</header>', text)
        self.assertNotIn('${resume}</section>${pilot}', text)

    def test_docs_are_current_and_shared_progress_is_untouched(self):
        for name in ['README.md','AGENTS.md']:
            path = ROOT / name if FORMAL.exists() else PATCH / (name+'.candidate')
            self.assertIn('v040', path.read_text('utf8'))
        self.assertEqual(sha(L / 'progress.json'), read(PATCH / 'before.json')['learning/progress.json'])
        if FORMAL.exists():
            self.assertIn('engineering-curriculum-v040.json', (L / 'manage.py').read_text('utf8'))


if __name__ == '__main__':
    unittest.main()
