import hashlib,http.client,json,struct,threading,unittest,sys
from pathlib import Path
from unittest.mock import patch
LEARNING=Path(__file__).resolve().parents[1];ROOT=LEARNING.parent
sys.path.insert(0,str(LEARNING))
import server
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ChallengeV009Test(unittest.TestCase):
 def setUp(self):
  self.path=LEARNING/'web/challenges/challenges-v009.json';self.data=json.loads(self.path.read_text(encoding='utf8'))
 def test_previous_source_and_identity(self):
  previous=LEARNING/'web/challenges/challenges-v008.json';old=json.loads(previous.read_text(encoding='utf8'))
  self.assertEqual(self.data['previousVersion']['sha256'],sha(previous));self.assertEqual(self.data['source']['sha256'],sha(ROOT/self.data['source']['path']))
  self.assertEqual([c['challengeId'] for c in old['chapters']],[c['challengeId'] for c in self.data['chapters']])
  for a,b in zip(old['chapters'],self.data['chapters']):
   if a['chapterId'] not in ('ch01','ch04','ch11'):self.assertEqual(a,b)
 def test_photos_from_real_frozen_records_and_status(self):
  c=next(x for x in self.data['chapters'] if x['chapterId']=='ch11')
  self.assertEqual([d['section'] for d in c['demonstrations'][:4]],['11-18','11-19','11-17','11-20'])
  self.assertEqual([len(d['steps']) for d in c['demonstrations'][:4]],[16,12,44,7])
  for d in c['demonstrations'][:4]:
   for s in d['steps']:
    image=s['screenshot'];self.assertTrue(image['path'].startswith('/challenges/'))
    file=LEARNING/'web/challenges'/image['path'].split('/')[-1];self.assertEqual(sha(file),image['sha256'])
    self.assertTrue(s['readings'] and s['limits'])
  self.assertTrue(all(value is None for value in c['physicalResults'].values()))
  self.assertIn('截字',' '.join(c['demonstrations'][0]['steps'][0]['limits']))
  self.assertIn('原 CAD Body',' '.join(c['demonstrations'][1]['steps'][5]['limits']))
  self.assertIn('不是警告成因修復',' '.join(c['demonstrations'][3]['steps'][0]['limits']))
  self.assertNotRegex(json.dumps(self.data),r'"path":\s*"[^"]*runner-status\.json"')
 def test_no_private_png_text_metadata_in_new_images(self):
  c=next(x for x in self.data['chapters'] if x['chapterId']=='ch11')
  for d in c['demonstrations'][:4]:
   for s in d['steps']:
    p=LEARNING/'web/challenges'/s['screenshot']['path'].split('/')[-1];raw=p.read_bytes();self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n');pos=8
    while pos+12<=len(raw):
     length=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8];self.assertNotIn(kind,(b'tEXt',b'zTXt',b'iTXt'));pos+=length+12
 def test_live_http_whitelist(self):
  with patch.object(server.manage,'CHALLENGES',self.path):
   httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
   try:
    for route,expected in [('/challenges/manifest.json',200),('/challenges/box-lid-identification-drawing-v001.svg',200),('/challenges/station-render-drawing-v001.svg',200),('/challenges/cad-thread-constraint-drawing-v001.svg',200),('/challenges/chapter11-stl-v002-03.png',200),('/challenges/cad-screw-v001-12.png',200),('/challenges/cad-recovery-v001-01.png',200),('/challenges/unlisted.png',404)]:
     conn=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=3);conn.request('GET',route,headers={'Host':f'127.0.0.1:{httpd.server_port}'});res=conn.getresponse();res.read();self.assertEqual(res.status,expected,route);conn.close()
   finally:httpd.shutdown();httpd.server_close();worker.join(3)
if __name__=='__main__':unittest.main()
