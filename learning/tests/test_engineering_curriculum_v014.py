"""Protect prior lessons and distinguish partial native driver evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
V013 = ROOT / 'learning/web/engineering-curriculum-v013.json'
V014 = ROOT / 'learning/web/engineering-curriculum-v014.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = read(V013)
        cls.data = read(V014)

    def test_prior_steps_and_order_preserved(self):
        self.assertEqual(self.data['id'], 'engineering-curriculum-v002')
        self.assertEqual(self.previous['id'], self.data['id'])
        old = {s['id']:s for c in self.previous['chapters'] for s in c['steps']}
        new = {s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)), (211,217))
        self.assertEqual(set(new)-set(old), {f'ch04-driver-partial-0{i}' for i in range(1,7)})
        self.assertTrue(all(new[k] == value for k,value in old.items()))
        for prev,curr in zip(self.previous['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])

    def test_partial_driver_and_failed_xy_are_honest(self):
        info = self.data['nativeDriverPartialVerification']
        self.assertEqual(sha(ROOT/info['summary']['path']), 'bcf1fda35c8305f7de44fe7931c7986522e257bc40e4018d346f6dc0cb16bda2')
        self.assertEqual([sha(ROOT/s['path']) for s in info['scenes']],
                         ['0d697fdf4d20bd6ff6999be64296949e8bcb0f90e7245079c9c0ce4e76bca0ec','fe77918de7c1eb80bc9e2bfa17371b879e0ba1b33eef8451ad398ba61c8bd04e'])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        summary = read(ROOT/info['summary']['path'])
        self.assertEqual(len(summary['images']),29)
        self.assertTrue(summary['overallXYValidation'].startswith('failed'))
        self.assertEqual(summary['xDriver']['expression'],'slvs_c_b596b36138076155-4')
        self.assertTrue(summary['xDriver']['valid'])
        self.assertFalse(summary['xDriver']['testedOuterDimensionChange'])
        self.assertEqual(summary['reopened']['driverCount'],1)
        self.assertEqual(summary['reopened']['outerBoundsMm'],[[0,60],[0,40],[0,30]])
        self.assertEqual([s['actualOuterMm'] for s in summary['scenes']],[[60,40,30],[60,40,30]])
        steps = [s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch04-driver-partial-')]
        text = json.dumps(steps,ensure_ascii=False)
        for phrase in ['未成功改變外框尺寸', 'Y Driver 未建立', 'X70／Y50 未生效', 'activeSketch null', '仍60×40×30', '不能硬套其他場景', '原 run 後續預期標籤不能當成成功紀錄']:
            self.assertIn(phrase,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),22)
        self.assertEqual(sha(ROOT/info['retrySummary']['path']),'43556bc29e0a039d45538ecf677b20f113ac43e9cf7f7b9676e1c91ae6b1046c')
        self.assertIn('Edit Sketch 灰色停用，原因未確認', text)

    def test_all_references_and_immutable_generator(self):
        refs=[]
        for chapter in self.data['chapters']:
            for step in chapter['steps']:
                for fig in step.get('figures',[]):
                    self.assertEqual(fig['type'],'screenshot')
                    self.assertTrue(fig['path'].startswith('learning/evidence/'))
                    refs.append(fig)
                refs.extend(step.get('artifacts',[]))
                for shortcut in step.get('shortcuts',[]):
                    refs.extend(shortcut.get('evidence',[]))
        refs.extend(self.data['sourceVersions'])
        for ref in refs:
            path=(ROOT/ref['path']).resolve()
            self.assertTrue(path.is_relative_to(ROOT.resolve()),ref['path'])
            self.assertTrue(path.is_file(),ref['path'])
            self.assertEqual(sha(path),ref['sha256'],ref['path'])
        before=V014.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v014.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v014',proc.stderr)
        self.assertEqual(V014.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
