"""Ensure restart lesson is bounded to explicit GUI script execution."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'learning/web/engineering-curriculum-v025.json';NEW=ROOT/'learning/web/engineering-curriculum-v026.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class GuardRestartCurriculumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=read(OLD);cls.data=read(NEW)
 def test_append_only(self):
  self.assertEqual(self.old['id'],self.data['id']);a={s['id']:s for c in self.old['chapters'] for s in c['steps']};b={s['id']:s for c in self.data['chapters'] for s in c['steps']};self.assertEqual((len(a),len(b)),(253,255));self.assertEqual(set(b)-set(a),{'ch05-manual-guard-restart-01','ch05-manual-guard-restart-02'});self.assertTrue(all(b[k]==v for k,v in a.items()))
  for c,d in zip(self.old['chapters'],self.data['chapters']):self.assertEqual([s['id'] for s in c['steps']],[s['id'] for s in d['steps'][:len(c['steps'])]])
 def test_manual_reload_and_scope(self):
  t=self.data['manualBoxGuardRestartTrial'];self.assertTrue(t['manualScriptExecution']);self.assertFalse(t['automaticPersistenceConfirmed']);self.assertEqual((t['testedBeforeMm'],t['testedAfterMm']),([70,40],[80,40]));self.assertEqual([t[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None])
  e=read(ROOT/t['summary']['path']);self.assertEqual(e['after']['bounds']['Body.001'][:2],[[2,78],[2,38]])
  ss=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-guard-restart-')];text=json.dumps(ss,ensure_ascii=False)
  for p in ('learning/workspaces/engineering-parametric/','資料夾不存在先建立','learning/progress.json','guarded_manual_box_v001.py','Alt+P','未核驗 Alt+P 前面板狀態','尚未證實面板自動常駐','v001／v003','sketcher.slvs_select','假專案','不是製造或配合合格'):self.assertIn(p,text)
  self.assertEqual(sum(len(s['figures']) for s in ss),8)
 def test_refs_and_write_once(self):
  refs=[]
  for ch in self.data['chapters']:
   for s in ch['steps']:
    refs+=s.get('figures',[])+s.get('artifacts',[])
    for k in s.get('shortcuts',[]):refs+=k.get('evidence',[])
  refs+=self.data['sourceVersions']
  for r in refs:
   p=(ROOT/r['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),r['path']);self.assertEqual(sha(p),r['sha256'])
  before=NEW.read_bytes();p=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v026.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(p.returncode,0);self.assertIn('refusing to overwrite v026',p.stderr);self.assertEqual(before,NEW.read_bytes())
if __name__=='__main__':unittest.main()
