"""Preserve prior steps and verify fixed-size cutter probe references."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V011 = ROOT / 'learning/web/engineering-curriculum-v011.json'
V012 = ROOT / 'learning/web/engineering-curriculum-v012.json'
BASE = ROOT / 'learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV012Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V011)
        cls.data = read(V012)

    def test_prior_steps_and_order_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        self.assertEqual(len(self.data['chapters']), 12)
        old = {s['id']: s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']: s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old), len(new)), (200, 206))
        self.assertEqual(set(new) - set(old), {f'ch04-cavity-0{i}' for i in range(1, 7)})
        self.assertTrue(all(new[k] == value for k, value in old.items()))
        for prev, curr in zip(self.previous['chapters'], self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']], [s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_probe_scope_and_readbacks(self):
        info = self.data['fixedCavityCutterVerification']
        self.assertEqual(sha(ROOT / info['summary']['path']), '2b980d31d86dcd82fa7c4f2f290ff70b1446ba92ceee0142da8098fd193c0c9d')
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        self.assertEqual(summary['kind'], 'fixed-geometry-probe-not-parametric-box')
        self.assertEqual(summary['cutterBoundsMm'], [[2,58], [2,38], [2,30]])
        self.assertEqual(summary['sketch']['distanceConstraintsMm'], [56,36,28,18])
        for name, dof in [('height-state.json',2), ('center-horizontal-state.json',1), ('center-vertical-state.json',0)]:
            sketch = read(BASE / name)['sketch']
            self.assertEqual((sketch['solver'], sketch['dof']), ('OKAY',dof))
        steps = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-cavity-')]
        text = json.dumps(steps, ensure_ascii=False)
        for phrase in ['固定尺寸', '未充分驗證布林', '沒有驗證更改外草圖', '未建立上蓋或另存', '由程式讀回', 'DoF 由2降為1', 'DoF 由1降為0']:
            self.assertIn(phrase, text)
        self.assertEqual(sum(len(s['figures']) for s in steps), 11)

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
        before = V012.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v012.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v012', proc.stderr)
        self.assertEqual(V012.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
