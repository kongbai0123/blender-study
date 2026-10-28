"""Append-only fault warning; sampled geometry cannot certify rollback."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];V024=ROOT/'learning/web/engineering-curriculum-v024.json';V025=ROOT/'learning/web/engineering-curriculum-v025.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class GuardFaultCurriculumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=read(V024);cls.data=read(V025)
 def test_append_and_prior_history(self):
  self.assertEqual(self.old['id'],self.data['id']);old={s['id']:s for c in self.old['chapters'] for s in c['steps']};new={s['id']:s for c in self.data['chapters'] for s in c['steps']};self.assertEqual((len(old),len(new)),(252,253));self.assertEqual(set(new)-set(old),{'ch05-manual-guard-fault-01'});self.assertTrue(all(new[k]==v for k,v in old.items()))
  for a,b in zip(self.old['chapters'],self.data['chapters']):self.assertEqual([s['id'] for s in a['steps']],[s['id'] for s in b['steps'][:len(a['steps'])]])
 def test_result_and_scope(self):
  trial=self.data['manualBoxGuardFaultTrial'];self.assertTrue(trial['fakeFaultOnly']);self.assertFalse(trial['rollbackConfirmed']);self.assertTrue(trial['warningManuallyObserved']);self.assertEqual([trial[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None]);d=read(ROOT/trial['summary']['path']);self.assertEqual(d['phases']['helper-unavailable'],d['phases']['fault-result']);self.assertEqual(d['phases']['fault-result']['outerMm'],[90,50]);self.assertEqual(d['proposedL'],70)
  s=next(s for c in self.data['chapters'] for s in c['steps'] if s['id']=='ch05-manual-guard-fault-01');text=json.dumps(s,ensure_ascii=False)
  for p in ('假專案','人工目視','回復沒有確認','不能證明完整','勿存檔','v024 的回滾未實證屬當時狀態','Save 或 Export','未做全面碰撞'):self.assertIn(p,text)
  self.assertEqual(len(s['figures']),3)
  for r in s['artifacts']:self.assertNotIn('state.json',r['path']);self.assertNotIn('runner-status',r['path'])
 def test_refs_and_frozen_builder(self):
  refs=[]
  for ch in self.data['chapters']:
   for s in ch['steps']:
    refs+=s.get('figures',[])+s.get('artifacts',[])
    for shortcut in s.get('shortcuts',[]):refs+=shortcut.get('evidence',[])
  refs+=self.data['sourceVersions']
  for r in refs:
   p=(ROOT/r['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),r['path']);self.assertEqual(sha(p),r['sha256'])
  before=V025.read_bytes();p=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v025.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(p.returncode,0);self.assertIn('refusing to overwrite v025',p.stderr);self.assertEqual(before,V025.read_bytes())
if __name__=='__main__':unittest.main()
