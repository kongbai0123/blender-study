"""Readback correspondence and honest visible evidence roles."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
L=ROOT/'learning'
sys.path.insert(0,str(L))
from build_engineering_curriculum_v041 import build,SOURCE,SOURCE_SHA,PATCH,RUN
from chapter_page_frontend_v003 import make_assets


def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class CorrespondenceV041(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=L/'web/engineering-curriculum-v041.json'
        if not cls.path.exists():cls.path=PATCH/'candidate/engineering-curriculum-v041.json'
        cls.data=read(cls.path)

    def test_v040_is_unchanged_and_all_ids_tracks_are_preserved(self):
        self.assertEqual(sha(SOURCE),SOURCE_SHA)
        before=[(ch['id'],s['id'],s.get('track')) for ch in read(SOURCE)['chapters'] for s in ch['steps']]
        after=[(ch['id'],s['id'],s.get('track')) for ch in self.data['chapters'] for s in ch['steps']]
        self.assertEqual(before,after)
        self.assertEqual(len(after),506)

    def test_85_pages_and_15_conversions_have_real_cards(self):
        pages=self.data['chapterPages']['sections']
        self.assertEqual(len(pages),85)
        cards=[c for s in pages.values() for c in [s.get('prep'),*s['steps']] if c]
        self.assertEqual(len(cards),447)
        self.assertEqual(len({c['stepId'] for c in cards}),447)
        for sid in self.data['contentReview']['completionV040']['convertedSections']:
            self.assertTrue(pages[sid]['steps'],sid)

    def test_native_stages_use_the_actual_lesson_coordinates(self):
        stages=read(RUN/'verification.json')['checks']
        self.assertTrue(all(s['passed'] for s in stages))
        final=next(s['readback'] for s in stages if s['case']=='six-varied')
        self.assertEqual(len(final['cutters']),6)
        self.assertEqual(len({o['mesh'] for o in final['cutters']}),6)
        for i,o in enumerate(final['cutters']):
            for a,b in zip(o['location'],[-35+14*i,2,0]):self.assertAlmostEqual(a,b,places=4)
            for a,b in zip(o['dimensions'],[10.1+.1*i,10.1+.1*i,8]):self.assertAlmostEqual(a,b,places=4)
            self.assertTrue(all(abs(v-1)<1e-6 for v in o['scale']))
        self.assertTrue(final['plate']['hidden'])
        for stage in stages:
            saved=stage['readback']['savedScene']
            self.assertEqual(sha(ROOT/saved['path']),saved['sha256'])
            for key in ['physicalPrint','physicalMeasurement','physicalFit']:self.assertIsNone(stage['readback'][key])

    def test_three_changed_cards_use_matching_same_run_photos(self):
        ids={'ch05-05-03-03','ch05-05-03-04','ch05-05-03-05'}
        cards=[c for c in self.data['chapterPages']['sections']['05-02']['steps'] if c['stepId'] in ids]
        self.assertEqual(sum(len(c['figures']) for c in cards),4)
        for card in cards:
            for f in card['figures']:
                self.assertEqual(f['evidenceRole'],'direct_operation')
                self.assertIn('efficient-plate-coordinates-v002',f['path'])
                self.assertEqual(sha(L/f['path']),f['sha256'])
                self.assertNotIn('X=0',f['caption'])

    def test_30_reference_photos_are_not_labelled_as_action_completion(self):
        cards=[c for s in self.data['chapterPages']['sections'].values() for c in [s.get('prep'),*s['steps']] if c]
        refs=[c for c in cards if c.get('figure',{}).get('path','').startswith('evidence/chapters/2026-10-30-independent-step-reference-v005/')]
        self.assertEqual(len(refs),30)
        for c in refs:
            role=c['figure']['evidenceRole']
            self.assertIn(role,['digital_preparation','version_reference','physical_preparation'])
            self.assertIn('參考',self.data['chapterPages']['evidenceRoles'][role]['label'])

    def test_generator_and_candidate_are_reproducible_without_inline_code(self):
        self.assertEqual(build(),self.data)
        html,css,js=make_assets((L/'drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
        for name,text in [('index.html',html),('chapter-pages-v001.css',css),('chapter-pages-v001.js',js)]:
            self.assertEqual((self.path.parent/name).read_text('utf8'),text)
        self.assertNotIn('<script>',html)
        self.assertNotIn('<style>',html)
        self.assertIn('curriculum.chapterPages.evidenceRoles',js)
        self.assertIn('note.dataset.role',js)

    def test_progress_is_preserved(self):
        self.assertEqual(sha(L/'progress.json'),read(PATCH/'before.json')['learning/progress.json'])
        if self.path.parent==L/'web':
            self.assertIn('engineering-curriculum-v041.json',(L/'manage.py').read_text('utf8'))


if __name__=='__main__':unittest.main()
