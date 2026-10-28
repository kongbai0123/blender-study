"""Guard the bounded dual-axis GUI evidence and preserve all prior steps."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];V022=ROOT/'learning/web/engineering-curriculum-v022.json';V023=ROOT/'learning/web/engineering-curriculum-v023.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ManualGuardXYCurriculumTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=read(V022);cls.data=read(V023)
 def test_append_only(self):
  self.assertEqual(self.old['id'],self.data['id']);old={s['id']:s for c in self.old['chapters'] for s in c['steps']};new={s['id']:s for c in self.data['chapters'] for s in c['steps']};self.assertEqual((len(old),len(new)),(247,251));self.assertEqual(set(new)-set(old),{f'ch05-manual-guard-xy-0{i}' for i in range(1,5)});self.assertTrue(all(new[k]==v for k,v in old.items()))
  for a,b in zip(self.old['chapters'],self.data['chapters']):self.assertEqual([s['id'] for s in a['steps']],[s['id'] for s in b['steps'][:len(a['steps'])]])
 def test_results_limitations_and_privacy(self):
  d=self.data['manualBoxGuardXYReopenTrial'];self.assertEqual(d['testedDimensions'],[[90,50],[90,60],[70,60],[70,40]]);self.assertTrue(d['sameBlenderSessionReopen']);self.assertFalse(d['registeredRefusalTested']);self.assertFalse(d['applicationRestartTested']);self.assertEqual([d[k] for k in ('physicalMeasurements','fitResults','qualifiedClearanceMm')],[None,None,None])
  summary=read(ROOT/d['summary']['path']);self.assertEqual(summary['phases']['reopened-assertion']['outerMm'],[70,40]);self.assertEqual(summary['phases']['reopened-assertion']['cutterX'],[2,68]);self.assertEqual(summary['phases']['reopened-assertion']['cutterY'],[2,38])
  steps=[s for c in self.data['chapters'] for s in c['steps'] if s['id'].startswith('ch05-manual-guard-xy-')];text=json.dumps(steps,ensure_ascii=False)
  for p in ('假專案','原生欄位','沒有實際看到已登記版本被拒絕','Blender 程式結束再重啟後面板是否保留尚未驗證','面板消失','焦點','未做全面碰撞'):self.assertIn(p,text)
  self.assertEqual(sum(len(s['figures']) for s in steps),15)
  for s in steps:
   for ref in s['artifacts']:self.assertNotIn('state.json',ref['path']);self.assertNotIn('runner-status',ref['path'])
 def test_refs_and_write_once(self):
  refs=[]
  for ch in self.data['chapters']:
   for s in ch['steps']:
    refs+=s.get('figures',[])+s.get('artifacts',[])
    for shortcut in s.get('shortcuts',[]):refs+=shortcut.get('evidence',[])
  refs+=self.data['sourceVersions']
  for r in refs:
   p=(ROOT/r['path']).resolve();self.assertTrue(p.is_relative_to(ROOT.resolve()));self.assertTrue(p.is_file(),r['path']);self.assertEqual(sha(p),r['sha256'])
  before=V023.read_bytes();p=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v023.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(p.returncode,0);self.assertIn('refusing to overwrite v023',p.stderr);self.assertEqual(before,V023.read_bytes())
if __name__=='__main__':unittest.main()
