"""Append-only fake registered-file GUI refusal, distinct from prior unsuccessful run."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];V023=ROOT/'learning/web/engineering-curriculum-v023.json';V024=ROOT/'learning/web/engineering-curriculum-v024.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class GuardRegisteredCurriculumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=read(V023);cls.data=read(V024)
 def test_append_and_prior_history(self):
  self.assertEqual(self.old['id'],self.data['id']);old={s['id']:s for c in self.old['chapters'] for s in c['steps']};new={s['id']:s for c in self.data['chapters'] for s in c['steps']};self.assertEqual((len(old),len(new)),(251,252));self.assertEqual(set(new)-set(old),{'ch05-manual-guard-registered-01'});self.assertTrue(all(new[k]==v for k,v in old.items()))
  for a,b in zip(self.old['chapters'],self.data['chapters']):self.assertEqual([s['id'] for s in a['steps']],[s['id'] for s in b['steps'][:len(a['steps'])]])
 def test_evidence_and_scope(self):
  trial=self.data['manualBoxGuardRegisteredTrial'];self.assertTrue(trial['rejectionMessageManuallyObserved']);self.assertTrue(trial['registeredFakeFixture']);self.assertFalse(trial['applicationRestartTested']);self.assertEqual([trial[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None]);d=read(ROOT/trial['summary']['path']);self.assertEqual(d['phases']['reopened-assertion'],d['phases']['registered-assertion']);self.assertEqual(d['phases']['registered-assertion']['outerMm'],[70,40]);self.assertEqual(d['phases']['registered-assertion']['cutterX'],[2,68]);self.assertEqual(d['phases']['registered-assertion']['cutterY'],[2,38])
  s=next(s for c in self.data['chapters'] for s in c['steps'] if s['id']=='ch05-manual-guard-registered-01');text=json.dumps(s,ensure_ascii=False)
  for p in ('假專案','人工查看原圖','v003 相同嘗試','不能攔截 Blender 原生欄位','Save 或 Export','關閉 Blender 再啟動後面板是否保留尚未測試','非學員作品'):self.assertIn(p,text)
  self.assertEqual(len(s['figures']),3)
  for ref in s['artifacts']:self.assertNotIn('state.json',ref['path']);self.assertNotIn('runner-status',ref['path'])
 def test_refs_and_frozen_builder(self):
  refs=[]
  for ch in self.data['chapters']:
   for s in ch['steps']:
    refs+=s.get('figures',[])+s.get('artifacts',[])
    for shortcut in s.get('shortcuts',[]):refs+=shortcut.get('evidence',[])
  refs+=self.data['sourceVersions']
  for r in refs:
   p=(ROOT/r['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),r['path']);self.assertEqual(sha(p),r['sha256'])
  before=V024.read_bytes();p=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v024.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(p.returncode,0);self.assertIn('refusing to overwrite v024',p.stderr);self.assertEqual(before,V024.read_bytes())
if __name__=='__main__':unittest.main()
