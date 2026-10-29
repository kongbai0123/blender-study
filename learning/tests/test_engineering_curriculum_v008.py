"""Evidence and version checks for the Y-dimension teaching supplement."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V007 = ROOT / 'learning/web/engineering-curriculum-v007.json'
V008 = ROOT / 'learning/web/engineering-curriculum-v008.json'
EVIDENCE = ROOT / 'learning/evidence/parametric/2026-10-27-cad-sketcher-y-dimension-v001'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V007)
        cls.data = read(V008)

    def test_previous_steps_and_stable_id_are_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.data['id'], self.previous['id'])
        self.assertEqual(len(self.data['chapters']), 12)
        old = {step['id']: step for chapter in self.previous['chapters'] for step in chapter['steps']}
        new = {step['id']: step for chapter in self.data['chapters'] for step in chapter['steps']}
        self.assertEqual(len(old), 176)
        self.assertEqual(len(new), 179)
        self.assertTrue(all(new[key] == step for key, step in old.items()))
        self.assertEqual(set(new) - set(old), {'ch05-linked-y-01', 'ch05-linked-y-02', 'ch05-linked-y-03'})
        self.assertEqual(sha(V007), '479e9a60679a091079f0a6011019338bbd4e8ff0ba4ccd89f6c616ee1571ec86')

    def test_y_results_warning_and_no_physical_qualification(self):
        info = self.data['yDimensionVerification']
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        warning = read(ROOT / info['warning']['path'])
        self.assertEqual(len(summary['cases']), 6)
        for case in summary['cases']:
            checks = read(ROOT / case['verificationPath'])['checks']
            self.assertEqual(len(checks), 12)
            self.assertTrue(all(value is True for value in checks.values()))
            self.assertEqual(case['solver'], 'OKAY')
            self.assertEqual(case['dof'], 0)
        self.assertEqual(warning['warning']['cause'], 'unknown; no diagnosis inferred')
        chapter = next(c for c in self.data['chapters'] if c['id'] == 'ch05')
        steps = {step['id']: step for step in chapter['steps']}
        joined = json.dumps([steps[f'ch05-linked-y-0{i}'] for i in range(1, 4)], ensure_ascii=False)
        self.assertIn('工具未找到', joined)
        self.assertIn('先停下並回報畫面', joined)
        self.assertIn('並非手工完成盒蓋建模', joined)
        self.assertIn('不將它說成已重開', joined)
        self.assertIn('不證明其他草圖工具正常', joined)

    def test_all_references_are_unchanged_and_generator_refuses_overwrite(self):
        refs = []
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for figure in step.get('figures', []):
                    self.assertEqual(figure['type'], 'screenshot')
                    self.assertTrue(figure['path'].startswith('learning/evidence/'))
                    refs.append(figure)
                refs.extend(step.get('artifacts', []))
                for shortcut in step.get('shortcuts', []):
                    refs.extend(shortcut.get('evidence', []))
        refs.extend(self.data['sourceVersions'])
        self.assertTrue(refs)
        for ref in refs:
            path = (ROOT / ref['path']).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()), ref['path'])
            self.assertTrue(path.is_file(), ref['path'])
            self.assertEqual(sha(path), ref['sha256'], ref['path'])
        before = V008.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v008.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v008', proc.stderr)
        self.assertEqual(V008.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
