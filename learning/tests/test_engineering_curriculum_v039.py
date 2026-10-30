"""Formal promotion contracts; never reads or writes learner progress."""
import hashlib,json,sys,unittest,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
L=ROOT/'learning';sys.path.insert(0,str(L))
from chapter_page_frontend_v001 import make_assets

def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class FormalChapterPages(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=read(L/'web/engineering-curriculum-v038.json');cls.new=read(L/'web/engineering-curriculum-v039.json')
 def test_stable_history_and_ids(self):
  self.assertEqual(sha(L/'web/engineering-curriculum-v038.json'),'7f0150607d736a6bbd2b43767fba09ffb4f3bbc8aaf6228a4c08aec54dddf4df')
  self.assertEqual(self.old['id'],self.new['id']);self.assertEqual(self.old['chapters'],self.new['chapters'])
 def test_full_mainline_coverage(self):
  pages=self.new['chapterPages']['sections'];self.assertEqual(len(pages),85)
  cards=[c for s in pages.values() for c in ([s['prep']] if s.get('prep') else [])+s['steps']]
  expected={s['id'] for c in self.old['chapters'] for s in c['steps'] if s.get('track') not in ['reference','appendix','optional','pending']}
  self.assertEqual(len(cards),243);self.assertEqual({c['stepId'] for c in cards},expected)
  self.assertEqual(sum(bool(s.get('prep') or s['steps']) for s in pages.values()),70)
 def test_reviewed_source_content_is_preserved(self):
  for source in self.new['chapterPages']['sources']:
   p=ROOT/source['path'];self.assertEqual(sha(p),source['sha256'])
   text=p.read_text('utf8');expected=json.loads(text[text.index(' = {')+3:].strip().rstrip(';'))
   actual=dict(self.new['chapterPages']['sections'][expected['id']])
   if not expected.get('prep') and not expected['steps']:
    for key in ['keyPoint','scope']:expected.pop(key,None);actual.pop(key,None)
   self.assertEqual(actual,expected,source['path'])
 def test_original_photos(self):
  photos=set()
  def walk(x):
   if isinstance(x,list):
    for v in x:walk(v)
   elif isinstance(x,dict):
    if x.get('path','').startswith('evidence/') and 'size' in x:
     self.assertEqual(sha(L/x['path']),x['sha256']);photos.add(x['sha256'])
    for v in x.values():walk(v)
  walk(self.new['chapterPages']['sections']);self.assertEqual(len(photos),332)
 def test_exact_legacy_and_other_protected_files(self):
  snapshot=read(L/'drafts/ux-chapter-01-v001/checks/protected-before.json')
  self.assertEqual(sha(L/'web/legacy.html'),snapshot['learning/web/index.html'])
  allowed={'learning/manage.py','learning/server.py','learning/web/index.html','learning/Start-Learning.ps1'}
  for name,value in snapshot.items():
   if name not in allowed:self.assertEqual(sha(ROOT/name),value,name)
 def test_reproducible_csp_safe_assets(self):
  html,css,js=make_assets((L/'drafts/ux-chapter-01-v001/index.html').read_text('utf8'))
  for filename,text in [('index.html',html),('chapter-pages-v001.css',css),('chapter-pages-v001.js',js)]:
   self.assertEqual((L/'web'/filename).read_text('utf8'),text,filename)
  self.assertNotIn('<style>',html);self.assertNotIn('<script>',html)
  server=(L/'server.py').read_text('utf8');self.assertIn("script-src 'self'",server);self.assertNotIn("'unsafe-inline'",server)
 def test_pointer_and_readonly_frontend(self):
  self.assertIn('engineering-curriculum-v039.json',(L/'manage.py').read_text('utf8'))
  js=(L/'web/chapter-pages-v001.js').read_text('utf8')
  self.assertNotIn('method:',js);self.assertIn('/api/bootstrap',js)
  for dest in ['/legacy.html#journal','/legacy.html#versions']:
   self.assertIn(dest,(L/'web/index.html').read_text('utf8'))
 def test_refuses_overwrite(self):
  result=subprocess.run([sys.executable,str(L/'build_engineering_curriculum_v039.py')],capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('refusing to overwrite',result.stderr)
if __name__=='__main__':unittest.main()
