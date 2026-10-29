import hashlib
import json
import http.client
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

LEARNING = Path(__file__).resolve().parents[1]
ROOT = LEARNING.parent
sys.path.insert(0, str(LEARNING))
import server

class ChallengesV006Test(unittest.TestCase):
    def setUp(self):
        self.path=LEARNING/'web/challenges/challenges-v006.json'
        self.data=json.loads(self.path.read_text(encoding='utf-8'))

    def test_source_history_and_unchanged_ids(self):
        previous=LEARNING/'web/challenges/challenges-v005.json'
        old=json.loads(previous.read_text(encoding='utf-8'))
        self.assertEqual(self.data['previousVersion']['sha256'],hashlib.sha256(previous.read_bytes()).hexdigest())
        curriculum=ROOT/self.data['source']['path']
        self.assertEqual(hashlib.sha256(curriculum.read_bytes()).hexdigest(),self.data['source']['sha256'])
        self.assertEqual([c['challengeId'] for c in old['chapters']],[c['challengeId'] for c in self.data['chapters']])
        for before,after in zip(old['chapters'],self.data['chapters']):
            if before['chapterId'] not in ('ch11','ch12'):
                self.assertEqual(before,after)

    def test_new_assets_are_in_repository_and_hash_verified(self):
        c=next(c for c in self.data['chapters'] if c['chapterId']=='ch11')
        self.assertEqual([len(d['steps']) for d in c['demonstrations']],[8,14,6])
        self.assertEqual([d['section'] for d in c['demonstrations']],['11-10','11-08','11-09'])
        self.assertTrue({'11-08','11-09','11-10'}.issubset({s['sectionId'] for s in c['sourceSteps']}))
        resources=[c['drawing'],*c['supplementalDrawings']]
        resources += [s['screenshot'] for d in c['demonstrations'] for s in d['steps']]
        for resource in resources:
            relative=resource['path'].removeprefix('/challenges/')
            asset=LEARNING/'web/challenges'/relative
            self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),resource['sha256'])
        start=c['demonstrations'][1]['startingScene']
        self.assertRegex(start['sha256'],r'^[0-9a-f]{64}$')
        if (ROOT/start['path']).is_file():
            self.assertEqual(hashlib.sha256((ROOT/start['path']).read_bytes()).hexdigest(),start['sha256'])
        self.assertTrue(all('limits' in s and 'readings' in s for d in c['demonstrations'] for s in d['steps']))

    def test_server_allows_only_declared_asset_names(self):
        with patch.object(server.manage,'CHALLENGES',self.path):
            paths=server.challenge_assets()
        self.assertIn('/challenges/manual-boss-drawing-v002.svg',paths)
        self.assertIn('/challenges/inner-thread-block-drawing-v002.svg',paths)
        self.assertIn('/challenges/boss-gui-v003-01.png',paths)
        self.assertIn('/challenges/external-gui-v005-14.png',paths)
        self.assertNotIn('/challenges/manual-boss-drawing-v001.svg',paths)
        corrupted={'chapters':[{'drawing':{'path':'/challenges/../../secret.svg'},'demonstrations':[{'steps':[{'screenshot':{'path':'//evil.test/private.png'}}]}]}]}
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'manifest.json'; p.write_text(json.dumps(corrupted),encoding='utf-8')
            with patch.object(server.manage,'CHALLENGES',p):
                self.assertEqual(server.challenge_assets(),set())

    def test_live_http_serves_v006_images_and_rejects_unlisted(self):
        with patch.object(server.manage,'CHALLENGES',self.path):
            httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
            try:
                for route,expected in [('/challenges/manifest.json',200),('/challenges/manual-boss-drawing-v002.svg',200),('/challenges/inner-thread-block-drawing-v002.svg',200),('/challenges/boss-gui-v003-01.png',200),('/challenges/external-gui-v005-14.png',200),('/challenges/inner-gui-v003-06.png',200),('/challenges/manual-boss-drawing-v001.svg',404)]:
                    connection=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=3)
                    connection.request('GET',route,headers={'Host':f'127.0.0.1:{httpd.server_port}'})
                    response=connection.getresponse();response.read();self.assertEqual(response.status,expected,route);connection.close()
            finally:
                httpd.shutdown();httpd.server_close();worker.join(3)

if __name__=='__main__':unittest.main()
