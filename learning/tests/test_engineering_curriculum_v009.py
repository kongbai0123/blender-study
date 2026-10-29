"""Ensure manual extrusion evidence, limits, and prior learner IDs are retained."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V008 = ROOT / 'learning/web/engineering-curriculum-v008.json'
V009 = ROOT / 'learning/web/engineering-curriculum-v009.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV009Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V008)
        cls.data = read(V009)

    def test_179_prior_steps_and_stable_curriculum_id(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        self.assertEqual(len(self.data['chapters']), 12)
        old = {s['id']: s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']: s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old), len(new)), (179, 183))
        self.assertEqual({s['id'] for c in self.data['chapters'] for s in c['steps']} - old.keys(),
                         {f'ch04-solid-0{i}' for i in range(1, 5)})
        self.assertTrue(all(new[k] == value for k, value in old.items()))
        self.assertEqual(sha(V008), '2c6944b7a00da650286628298942cd4fe69a7ee5af87f14cba89f68088626443')
        for previous_ch, current_ch in zip(self.previous['chapters'], self.data['chapters']):
            self.assertEqual([s['id'] for s in current_ch['steps'][:len(previous_ch['steps'])]],
                             [s['id'] for s in previous_ch['steps']])

    def test_trial_limits_and_states(self):
        info = self.data['manualExtrudeVerification']
        self.assertEqual(sha(ROOT / info['summary']['path']), '520daefc24ad6b46c502cca242684c55529fd0ff6c8c27f8eb331c325d1064ba')
        self.assertEqual(sha(ROOT / info['scene']['path']), '688a06f588bbe0728a7d0c866acbc307c44fa7cc1c71e467b0aa807af2084c2d')
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        self.assertEqual(summary['unitScale'], 0.001)
        self.assertEqual({c['stage'] for c in summary['cases']}, {'confirmed-state.json', 'reopened-state.json'})
        for case in summary['cases']:
            self.assertEqual(case['bounds'], [[0, 60], [0, 40], [0, 30]])
            self.assertEqual((case['vertices'], case['faces']), (8, 6))
            self.assertEqual([m['name'] for m in case['modifiers']], ['CAD Sketcher Convert', 'CAD_Sketcher Extrude'])
        new = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-solid-')]
        text = json.dumps(new, ensure_ascii=False)
        for phrase in ['30mm讀回0.03 mm', '不能推廣', '工具未找到', '先停止並回報畫面', '不是有內腔', '程式讀回']:
            self.assertIn(phrase, text)
        self.assertEqual(sum(len(s['figures']) for s in new), 7)

    def test_evidence_hashes_and_immutable_generator(self):
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
        before = V009.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v009.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v009', proc.stderr)
        self.assertEqual(V009.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
