"""Preserve steps and qualify fixed-lid geometry and historical limits."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
V017=ROOT/'learning/web/engineering-curriculum-v017.json'
V018=ROOT/'learning/web/engineering-curriculum-v018.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EngineeringCurriculumV018Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=read(V017)
        cls.data=read(V018)

    def test_previous_steps_preserved_and_historical_labels(self):
        self.assertEqual(self.data['id'],self.old['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(228,232))
        self.assertEqual(set(new)-set(old),{f'ch05-manual-lid-fixed-0{i}' for i in range(1,5)})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for prev,curr in zip(self.old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in prev['steps']],[s['id'] for s in curr['steps'][:len(prev['steps'])]])
        limitations=next(c for c in self.data['chapters'] if c['id']=='ch04')['limitations']
        for prefix in ('v009 當時：','v012 當時：','v014 當時：','v015 當時：'):
            self.assertTrue(any(s.startswith(prefix) for s in limitations))

    def test_fixed_lid_evidence_is_not_fit_or_linkage(self):
        info=self.data['manualFixedLidVerification']
        self.assertFalse(info['lidParametricLinkageVerified'])
        for key in ('physicalMeasurements','fitResults','qualifiedClearanceMm'):
            self.assertIsNone(info[key])
        review=read(ROOT/info['summary']['path'])
        for obj in ('Body','Cube'):
            self.assertEqual(review['bodyAndLidEvaluation'][obj]['nonManifoldEdges'],0)
        levels=review['bodyAndLidEvaluation']['Cube']['levels']
        self.assertEqual(levels['26.0']['x'],[2.2005,4.2005,75.7995,77.7995])
        self.assertEqual(levels['26.0']['y'],[2.2003,4.2003,45.7997,47.7997])
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-lid-fixed-')]
        text=json.dumps(steps,ensure_ascii=False)
        for phrase in ('尚未建立盒蓋參數連動','沒有實際截面、單殼或盒蓋交集檢查','不是截面檢查','不是實體試配','sketcher.slvs_select','頂點座標推算'):
            self.assertIn(phrase,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),12)

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
        before=V018.read_bytes()
        proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v018.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('refusing to overwrite v018',proc.stderr)
        self.assertEqual(V018.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
