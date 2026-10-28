"""Append-only GUI width rejection, not a manufacturing limit."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'learning/web/engineering-curriculum-v026.json';NEW=ROOT/'learning/web/engineering-curriculum-v027.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class GuardWidthRejectCurriculumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=read(OLD);cls.data=read(NEW)
 def test_append_only(self):
  self.assertEqual(self.old['id'],self.data['id']);a={s['id']:s for c in self.old['chapters'] for s in c['steps']};b={s['id']:s for c in self.data['chapters'] for s in c['steps']};self.assertEqual((len(a),len(b)),(255,256));self.assertEqual(set(b)-set(a),{'ch05-manual-guard-y-reject-01'});self.assertTrue(all(b[k]==v for k,v in a.items()))
  for c,d in zip(self.old['chapters'],self.data['chapters']):self.assertEqual([s['id'] for s in c['steps']],[s['id'] for s in d['steps'][:len(c['steps'])]])
 def test_result_and_scope(self):
  t=self.data['manualBoxGuardWidthRejectTrial'];self.assertEqual(t['proposedWidthMm'],80);self.assertEqual(t['prePostOuterMm'],[80,50]);self.assertTrue(t['messageManuallyObserved']);self.assertEqual([t[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None]);e=read(ROOT/t['summary']['path']);self.assertEqual(e['prePostBoundsMm']['Body.001'][:2],[[2,78],[2,48]])
  s=next(s for c in self.data['chapters'] for s in c['steps'] if s['id']=='ch05-manual-guard-y-reject-01');text=json.dumps(s,ensure_ascii=False)
  for p in ('假專案','人工查看原圖','程式未自動解析 UI 文字','原生欄位可繞過','理論候選範圍','不是全區安全','實體列印'):self.assertIn(p,text)
  self.assertEqual(len(s['figures']),3)
 def test_refs_and_frozen_builder(self):
  refs=[]
  for c in self.data['chapters']:
   for s in c['steps']:
    refs+=s.get('figures',[])+s.get('artifacts',[])
    for k in s.get('shortcuts',[]):refs+=k.get('evidence',[])
  refs+=self.data['sourceVersions']
  for r in refs:
   p=(ROOT/r['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),r['path']);self.assertEqual(sha(p),r['sha256'])
  before=NEW.read_bytes();p=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v027.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(p.returncode,0);self.assertIn('refusing to overwrite v027',p.stderr);self.assertEqual(before,NEW.read_bytes())
if __name__=='__main__':unittest.main()
