"""Protect prior steps and bound claims to the observed GUI linkage case."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
V018=ROOT/'learning/web/engineering-curriculum-v018.json'
V019=ROOT/'learning/web/engineering-curriculum-v019.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV019Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V018)
        cls.data=read(V019)

    def test_previous_steps_preserved_and_historical_lid_limit(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(232,238))
        self.assertEqual(set(new)-set(old),{f'ch05-manual-lid-link-0{i}' for i in range(1,7)})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])
        limits=next(c for c in self.data['chapters'] if c['id']=='ch05')['limitations']
        self.assertTrue(any(s.startswith('v018 當時：') for s in limits))
        self.assertTrue(any(s.startswith('v019 單組') for s in limits))

    def test_linkage_and_safety_limits(self):
        info=self.data['manualBoxLidLinkageVerification']
        self.assertTrue(info['cavityRequiresManualUpdate'])
        self.assertEqual(info['testedChangeMm'],[[80,50],[90,60]])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        result=read(ROOT/info['summary']['path'])
        pre=result['phases']['inner-before-solve']['meshReadback']['Body.001']['levels']['30.0']
        post=result['phases']['reopened']['meshReadback']['Body.001']['levels']['30.0']
        self.assertEqual(pre,{'x':[2,78],'y':[2,48]})
        self.assertEqual(post,{'x':[2,88],'y':[2,58]})
        self.assertEqual(len(result['phases']['reopened']['shapeDrivers']),2)
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-lid-link-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('須進內腔草圖手動點更新','鍵值暫被夾為2','約 −9.8 mm','不是已驗證的安全或製造範圍','舊 v007 防護面板不適用','未做完整交集或實體列印','本輪未直接列出 Scene Driver 各來源目標','原 run 的部分 X 動作標籤有誤'):
            self.assertIn(phrase,text)

    def test_references_and_frozen_generator(self):
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
        before=V019.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v019.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v019',proc.stderr)
        self.assertEqual(V019.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
