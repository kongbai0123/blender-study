"""Verify append-only one-case manual-box guard lesson and frozen inputs."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V021=ROOT/'learning/web/engineering-curriculum-v021.json'
V022=ROOT/'learning/web/engineering-curriculum-v022.json'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
class GuardCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.old=read(V021);cls.data=read(V022)
    def test_prior_steps_preserved_and_append(self):
        self.assertEqual(self.old['id'],self.data['id'])
        old={s['id']:s for c in self.old['chapters'] for s in c['steps']}
        new={s['id']:s for c in self.data['chapters'] for s in c['steps']}
        self.assertEqual((len(old),len(new)),(243,247))
        self.assertEqual(set(new)-set(old),{f'ch05-manual-guard-0{i}' for i in range(1,5)})
        self.assertTrue(all(new[k]==v for k,v in old.items()))
        for a,b in zip(self.old['chapters'],self.data['chapters']): self.assertEqual([s['id'] for s in a['steps']],[s['id'] for s in b['steps'][:len(a['steps'])]])
    def test_result_and_limitations(self):
        trial=self.data['manualBoxGuardOneXTrial'];self.assertEqual((trial['rejectedL'],trial['acceptedL']),(110,90))
        self.assertEqual([trial[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None])
        evidence=read(ROOT/trial['summary']['path']);self.assertEqual(evidence['rejected']['outerMm'],[80,50]);self.assertEqual(evidence['accepted']['cutterX'],[2,88]);self.assertEqual(evidence['accepted']['cutterY'],[2,48])
        steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-guard-')]
        text=json.dumps(steps,ensure_ascii=False)
        for expected in ('假專案','直接修改 Blender','本次僅測 X=110','沒有驗 Y','不攔截原生存檔','未完成全面碰撞'):
            self.assertIn(expected,text)
        self.assertEqual(sum(len(s['figures']) for s in steps),12)
    def test_pinned_assets_and_builder_refuses_overwrite(self):
        refs=[]
        for ch in self.data['chapters']:
            for step in ch['steps']:
                refs += step.get('figures',[])+step.get('artifacts',[])
                for shortcut in step.get('shortcuts',[]): refs += shortcut.get('evidence',[])
        refs+=self.data['sourceVersions']
        for ref in refs:
            p=(ROOT/ref['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),ref['path']);self.assertEqual(sha(p),ref['sha256'])
        raw=V022.read_bytes();proc=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v022.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');self.assertNotEqual(proc.returncode,0);self.assertIn('refusing to overwrite v022',proc.stderr);self.assertEqual(raw,V022.read_bytes())
if __name__=='__main__':unittest.main()
