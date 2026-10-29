import hashlib
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
LEARNING=Path(__file__).resolve().parents[1];ROOT=LEARNING.parent
sys.path.insert(0,str(LEARNING))
import server
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ChallengesV008Test(unittest.TestCase):
 def setUp(self):
  self.path=LEARNING/'web/challenges/challenges-v008.json';self.data=json.loads(self.path.read_text(encoding='utf8'))
 def test_history_progress_identity_and_source(self):
  oldpath=LEARNING/'web/challenges/challenges-v007.json';old=json.loads(oldpath.read_text(encoding='utf8'))
  self.assertEqual(self.data['previousVersion']['sha256'],sha(oldpath));self.assertEqual(self.data['source']['sha256'],sha(ROOT/self.data['source']['path']))
  self.assertEqual([c['challengeId'] for c in old['chapters']],[c['challengeId'] for c in self.data['chapters']])
  for before,after in zip(old['chapters'],self.data['chapters']):
   if before['chapterId']!='ch11':self.assertEqual(before,after)
 def test_evidence_and_unverified_physical_results(self):
  c=next(x for x in self.data['chapters'] if x['chapterId']=='ch11')
  self.assertEqual([d['section'] for d in c['demonstrations'][:4]],['11-13','11-14','11-15','11-16'])
  self.assertEqual([len(d['steps']) for d in c['demonstrations'][:4]],[13,14,17,15])
  for demo in c['demonstrations'][:4]:
   for step in demo['steps']:
    p=LEARNING/'web/challenges'/step['screenshot']['path'].split('/')[-1];self.assertEqual(sha(p),step['screenshot']['sha256'])
   for source in demo.get('sourceVersions',[]):
    self.assertRegex(source['sha256'],r'^[0-9a-f]{64}$')
    if (ROOT/source['path']).exists():self.assertEqual(sha(ROOT/source['path']),source['sha256'])
  for image in [c['drawing'],*c['supplementalDrawings']]:
   if image.get('sha256'):self.assertEqual(sha(LEARNING/'web/challenges'/image['path'].split('/')[-1]),image['sha256'])
  self.assertTrue(all(v is None for v in c['physicalResults'].values()))
  self.assertEqual(sha(ROOT/c['hardwareInformation']['recordPath']),c['hardwareInformation']['recordSha256'])
  self.assertNotIn('runner-status.json',json.dumps(self.data))
 def test_live_http_asset_whitelist(self):
  with patch.object(server.manage,'CHALLENGES',self.path):
   httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
   try:
    for route,expected in [('/challenges/manifest.json',200),('/challenges/side-thread-cap-drawing-v002.svg',200),('/challenges/manual-thread-profile-drawing-v001.svg',200),('/challenges/m3-four-boss-layout-drawing-v001.svg',200),('/challenges/metal-box-v001-15.png',200),('/challenges/side-cap-v002-17.png',200),('/challenges/not-listed.svg',404)]:
     conn=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=3);conn.request('GET',route,headers={'Host':f'127.0.0.1:{httpd.server_port}'});res=conn.getresponse();res.read();self.assertEqual(res.status,expected,route);conn.close()
   finally:httpd.shutdown();httpd.server_close();worker.join(3)
if __name__=='__main__':unittest.main()
