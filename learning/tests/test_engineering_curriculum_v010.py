"""Preservation and evidence checks for the controlled dimension guard GUI."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V009 = ROOT / 'learning/web/engineering-curriculum-v009.json'
V010 = ROOT / 'learning/web/engineering-curriculum-v010.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV010Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V009)
        cls.data = read(V010)

    def test_old_steps_and_stable_id_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        self.assertEqual(len(self.data['chapters']), 12)
        old = {s['id']: s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']: s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old), len(new)), (183, 191))
        self.assertEqual(set(new) - set(old), {f'ch05-guard-0{i}' for i in range(1, 9)})
        self.assertTrue(all(new[k] == value for k, value in old.items()))
        for prev, curr in zip(self.previous['chapters'], self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']], [s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_gui_results_limits_and_duplicate_images(self):
        info = self.data['dimensionGuardVerification']
        self.assertEqual(sha(ROOT / info['summary']['path']), 'c0ddca8eae92eec6bdfb8725d091035f76e6857e7bb27b3c5bc6461691498a5f')
        self.assertEqual(sha(ROOT / info['script']['path']), 'e084d0e5a041528863c1b82e5674ebc5a2b218e105632709f0cd442572d25b24')
        self.assertEqual(sha(ROOT / info['scene']['path']), 'cb0652ae0a45183345039d291ffc8f1c3ef303819104413c34d5489ea2dac415')
        self.assertEqual(info['script']['path'], 'learning/tutor/guarded_box_parameters_v005.py')
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        self.assertEqual(len(summary['screenshots']), 20)
        self.assertEqual(summary['screenshots'][6]['sha256'], summary['screenshots'][9]['sha256'])
        cases = {c['stage']: c for c in summary['cases']}
        for stage, l, w in [('width-assertion', 80, 50), ('invalid-assertion', 80, 50), ('length-assertion', 70, 50), ('reopened-assertion', 70, 50)]:
            c = cases[stage]
            self.assertEqual((c['values']['L'], c['values']['W'], c['values']['D']), (l, w, 4))
            self.assertEqual(c['bodyBounds'], [[0, l], [0, w], [0, 30]])
            self.assertEqual(c['lidBounds'], [[0, l], [0, w], [26, 32]])
        self.assertIn('已登記', cases['registered-assertion']['guardError'])
        guard = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-guard-')]
        text = json.dumps(guard, ensure_ascii=False)
        for phrase in ['未示範手動', '可繞過此面板', '不自動存檔', '不是製造公差', '實體', '原因未知', 'GUARD-07 與 GUARD-10']:
            self.assertIn(phrase, text)
        self.assertEqual(sum(len(s['figures']) for s in guard), 20)

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
        before = V010.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v010.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v010', proc.stderr)
        self.assertEqual(V010.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
