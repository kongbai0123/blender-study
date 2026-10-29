import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class PatchTest(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/'learning/patches/ch07-ch08-ch12-teaching-v001.json').read_text(encoding='utf8'))
 def test_every_target_and_hash(self):
  self.assertEqual(sha(ROOT/self.data['base']['path']),self.data['base']['sha256'])
  c=json.loads((ROOT/self.data['base']['path']).read_text(encoding='utf8'));steps={s['id']:s for ch in c['chapters'] for s in ch['steps']}
  expected={s['id'] for ch in c['chapters'] if ch['id'] in ('ch07','ch08','ch12') for s in ch['steps'] if s.get('track')!='appendix' and s.get('evidenceStatus') in ('draft_pending_demo','concept_only')}
  self.assertEqual(set(self.data['patches']),expected)
  for sid,p in self.data['patches'].items():
   self.assertNotEqual(steps[sid].get('track'),'appendix');self.assertTrue(p['detail']['steps']);self.assertIn(p['evidenceStatus'],{'documented_lesson','field_protocol_ready','existing_demo'})
   for f in p.get('figures',[]):self.assertEqual(sha(ROOT/f['path']),f['sha256'])
   for a in p.get('artifacts',[]):self.assertEqual(sha(ROOT/a['path']),a['sha256'])
 def test_templates_are_empty_and_not_real_results(self):
  for name in ('engineering-measurement-fit-v001.json','engineering-compensation-v001.json','engineering-assembly-trace-v001.json'):
   d=json.loads((ROOT/'learning/journal/templates'/name).read_text(encoding='utf8'))
   self.assertIn('template_',d['status'])
   if 'records' in d:self.assertTrue(all(value is None or value==[] for value in d['records'][0].values()))
   if 'assembly' in d:self.assertTrue(all(value is None for value in d['assembly'].values()))
 def test_fake_workspace_and_render_are_not_learner_evidence(self):
  f=json.loads((ROOT/'learning/evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json').read_text(encoding='utf8'))
  self.assertEqual(f['kind'],'isolated-synthetic-project');self.assertTrue(f['checks']['duplicateNameRefused']);self.assertTrue(f['checks']['guardRefusedRegistered']);self.assertEqual(f['checks']['syntheticRevisionAfter'],3)
  self.assertIn('synthetic_fixture_not_printable',f['checks']['syntheticExportPath'])
  r=json.loads((ROOT/'learning/evidence/12/2026-10-28-render-safe-copy-gui-v003/safe-summary-v001.json').read_text(encoding='utf8'))
  self.assertEqual(len(r['records']),4);self.assertTrue(r['records'][2]['observed']['outputInFakeWorkspace']);self.assertEqual(r['records'][2]['observed']['propertiesContext'],'OUTPUT')
if __name__=='__main__':unittest.main()
