import hashlib
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

LEARNING=Path(__file__).resolve().parents[1]
ROOT=LEARNING.parent
sys.path.insert(0,str(LEARNING))
import server

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
class ChallengesV007Test(unittest.TestCase):
    def setUp(self):
        self.path=LEARNING/'web/challenges/challenges-v007.json'
        self.data=json.loads(self.path.read_text(encoding='utf-8'))
    def test_versions_and_preserved_progress_identity(self):
        oldfile=LEARNING/'web/challenges/challenges-v006.json';old=json.loads(oldfile.read_text(encoding='utf-8'))
        self.assertEqual(self.data['previousVersion']['sha256'],sha(oldfile))
        self.assertEqual(self.data['source']['sha256'],sha(ROOT/self.data['source']['path']))
        self.assertEqual([x['challengeId'] for x in old['chapters']],[x['challengeId'] for x in self.data['chapters']])
        for a,b in zip(old['chapters'],self.data['chapters']):
            if a['chapterId']!='ch11':self.assertEqual(a,b)
    def test_screenshots_and_sources(self):
        c=next(x for x in self.data['chapters'] if x['chapterId']=='ch11')
        self.assertTrue(all(v is None for v in c['physicalResults'].values()))
        a,b,_,_,historical,oldmount=c['demonstrations']
        self.assertEqual([a['section'],b['section']],['11-11','11-12'])
        self.assertTrue(historical['historical'])
        self.assertTrue(oldmount['historical'])
        self.assertEqual([len(a['steps']),len(b['steps']),len(oldmount['steps'])],[14,11,10])
        self.assertEqual(sha(LEARNING/'web/challenges'/c['drawing']['path'].split('/')[-1]),c['drawing']['sha256'])
        for d in (a,b,oldmount):
            for v in d['sourceVersions']:
                self.assertRegex(v['sha256'],r'^[0-9a-f]{64}$')
                if (ROOT/v['path']).is_file():self.assertEqual(sha(ROOT/v['path']),v['sha256'])
            for s in d['steps']:
                im=s['screenshot']; self.assertEqual(sha(LEARNING/'web/challenges'/im['path'].split('/')[-1]),im['sha256'])
                self.assertTrue(s['context'] and s['success'] and s['limits'] and s['readings'])
        self.assertIn('5.625°',a['description']);self.assertIn('4.8',a['description'])
        self.assertTrue({'11-11','11-12'}.issubset({x['sectionId'] for x in c['sourceSteps']}))
        self.assertNotIn('runner-status.json',json.dumps(self.data))
    def test_live_http_allowlist(self):
        with patch.object(server.manage,'CHALLENGES',self.path):
            httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
            try:
                for route,expected in [('/challenges/manifest.json',200),('/challenges/box-external-thread-drawing-v003.svg',200),('/challenges/external-gui-v010-14.png',200),('/challenges/mount-gui-v002-11.png',200),('/challenges/mount-gui-v001-10.png',200),('/challenges/external-gui-v005-14.png',200),('/challenges/unlisted.png',404)]:
                    connection=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=3);connection.request('GET',route,headers={'Host':f'127.0.0.1:{httpd.server_port}'})
                    response=connection.getresponse();response.read();self.assertEqual(response.status,expected,route);connection.close()
            finally:httpd.shutdown();httpd.server_close();worker.join(3)
if __name__=='__main__':unittest.main()
