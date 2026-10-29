"""Check fixed and non-linked saved samples and preserve prior course steps."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V012 = ROOT / 'learning/web/engineering-curriculum-v012.json'
V013 = ROOT / 'learning/web/engineering-curriculum-v013.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV013Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V012)
        cls.data = read(V013)

    def test_prior_steps_and_order_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        old = {s['id']: s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']: s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old), len(new)), (206, 211))
        self.assertEqual(set(new) - set(old), {f'ch04-link-counterexample-0{i}' for i in range(1, 6)})
        self.assertTrue(all(new[k] == value for k, value in old.items()))
        for prev, curr in zip(self.previous['chapters'], self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']], [s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_linkage_counterexample_and_scene_versions(self):
        info = self.data['outerLinkageNegativeVerification']
        self.assertEqual(sha(ROOT / info['summary']['path']), '37a505f8394fc1e96cda6f1a6120f4e18bccc8072ec2df0204709b34ecefa329')
        self.assertEqual(sha(ROOT / info['fixedScene']['path']), '087589e91d1f2cffc52e8b2fa6893be1b4a9b4332d165f97a9510b4729ca8918')
        self.assertEqual(sha(ROOT / info['trialScene']['path']), '479a7e29e3dc65c0da8e3e51608e7f86cd15b4954eda9f1f3e35523b56326cc7')
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        self.assertEqual(len(summary['images']), 8)
        for phase, x, y, walls in [('opened',60,40,[[2,2],[2,2]]),('x70',70,40,[[2,12],[2,2]]),('x70y50',70,50,[[2,12],[2,12]]),('reopened',70,50,[[2,12],[2,12]])]:
            r = next(p for p in summary['phases'] if p['phase'] == phase)
            self.assertEqual(r['boxBounds'], [[0,x],[0,y],[0,30]])
            self.assertEqual(r['cutterBounds'], [[2,58],[2,38],[2,30]])
            self.assertEqual(r['wallWidthsXY'], walls)
        steps = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-link-counterexample-')]
        text = json.dumps(steps, ensure_ascii=False)
        for phrase in ['不跟隨', '不推論此技術無法實現連動', '界限的差值', '布林後實際內腔壁厚', '上蓋未建立', '反例並非完成品']:
            self.assertIn(phrase, text)
        self.assertEqual(sum(len(s['figures']) for s in steps), 10)

    def test_all_references_and_immutable_generator(self):
        refs = []
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for fig in step.get('figures', []):
                    self.assertEqual(fig['type'], 'screenshot')
                    self.assertTrue(fig['path'].startswith('learning/evidence/'))
                    refs.append(fig)
                refs.extend(step.get('artifacts', []))
                for shortcut in step.get('shortcuts', []):
                    refs.extend(shortcut.get('evidence', []))
        refs.extend(self.data['sourceVersions'])
        for ref in refs:
            path = (ROOT / ref['path']).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()), ref['path'])
            self.assertTrue(path.is_file(), ref['path'])
            self.assertEqual(sha(path), ref['sha256'], ref['path'])
        before = V013.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v013.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v013', proc.stderr)
        self.assertEqual(V013.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
