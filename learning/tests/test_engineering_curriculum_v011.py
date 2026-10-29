"""Preservation and evidence checks for v007 Text Editor GUI trial."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V010 = ROOT / 'learning/web/engineering-curriculum-v010.json'
V011 = ROOT / 'learning/web/engineering-curriculum-v011.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV011Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V010)
        cls.data = read(V011)

    def test_prior_steps_and_stable_id_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        self.assertEqual(len(self.data['chapters']), 12)
        old = {s['id']: s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']: s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old), len(new)), (191, 200))
        self.assertEqual(set(new) - set(old), {f'ch05-guard-v007-0{i}' for i in range(1, 10)})
        self.assertTrue(all(new[k] == value for k, value in old.items()))
        for prev, curr in zip(self.previous['chapters'], self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']], [s['id'] for s in curr['steps'][:len(prev['steps'])]])
        limits = next(c for c in self.data['chapters'] if c['id'] == 'ch05')['limitations']
        self.assertTrue(any('v005' in x and '歷史' in x and '未驗 Text Editor' in x for x in limits))

    def test_gui_results_and_scope(self):
        info = self.data['textGuardVerification']
        self.assertEqual(sha(ROOT / info['summary']['path']), 'f940df8fabb5262c474c88ab464630185969ab60b22ac6168238ff6e83ebdc16')
        self.assertEqual(sha(ROOT / info['script']['path']), 'd04a945e1fc8d60d0c6d3323774819c817860d91b1aaf8f0a06d7223eb4e7bf4')
        self.assertEqual(sha(ROOT / info['scene']['path']), 'cab6d3d950fa87b94a0e40aa42c6a244e6f5270174a0e28803d47950f286543f')
        self.assertEqual(info['script']['path'], 'learning/tutor/guarded_box_parameters_v007.py')
        for key in ('physicalMeasurements', 'fitResults', 'qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT / info['summary']['path'])
        self.assertEqual(len(summary['images']), 22)
        self.assertEqual(summary['images'][1]['sha256'], summary['images'][2]['sha256'])
        self.assertEqual(summary['images'][8]['sha256'], summary['images'][11]['sha256'])
        self.assertTrue(summary['checks']['registeredErrorNotMachineParsed'])
        self.assertTrue(summary['checks']['registeredFixtureUnchanged'])
        self.assertEqual(summary['checks']['registeredErrorVisuallyConfirmedImage'], 'GUARD-22-registered-attempt.png')
        for stage, l, w in [('width-assertion', 80, 50), ('invalid-assertion', 80, 50), ('length-assertion', 70, 50), ('reopened-assertion', 70, 50), ('registered-assertion', 70, 50)]:
            r = summary['readings'][stage]
            self.assertEqual((r['L'], r['W'], r['D']), (l, w, 4))
        guard = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-guard-v007-')]
        text = json.dumps(guard, ensure_ascii=False)
        for phrase in ['程式填入', '退出 Blender 後是否保留', '原生欄位可以繞過', '不自動存檔', '不是製程能力', '人工目視', '未自動解析', '起始及重開圖有工具']:
            self.assertIn(phrase, text)
        self.assertEqual(sum(len(s['figures']) for s in guard), 22)

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
        before = V011.read_bytes()
        proc = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v011.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('refusing to overwrite v011', proc.stderr)
        self.assertEqual(V011.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
