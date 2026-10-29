"""Cross-check the frozen v037 candidate without mutating learner progress."""
from functools import lru_cache
from hashlib import sha256
import http.client
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / 'learning'
sys.path.insert(0, str(LEARNING))
import server

CURRICULUM = LEARNING/'web/engineering-curriculum-v037.json'
PREVIOUS = LEARNING/'web/engineering-curriculum-v036.json'
PATH_DATA = LEARNING/'web/engineering-path-v006.json'
CHALLENGES = LEARNING/'web/challenges/challenges-v010.json'
STL_SOURCE = LEARNING/'lesson11_stl_export_optional_steps_v002.json'
TOOL = LEARNING/'tutor/inspect_stl_v001.py'
PROGRESS = LEARNING/'progress.json'
HASHES = {
    CURRICULUM: '79522345aef709d92f5eb28b47176c54e3a45dbc728beacf9c1420dd21d1248a',
    PATH_DATA: 'c5deb3aa4ecede22bfd8b283f632000114202d2b32b198a3ea2887a102c33c99',
    CHALLENGES: '45bc3007a61efdbab5327e1b21dec4901ed1c92f36d6058d1389e13d2d3e90fa',
}

@lru_cache(maxsize=None)
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

@lru_cache(maxsize=None)
def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def step_map(data):
    return {s['id']:s for c in data['chapters'] for s in c['steps']}

class FrozenCorrespondenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.progress_before=sha256(PROGRESS.read_bytes()).hexdigest()
        cls.data=read(CURRICULUM)
        cls.steps=step_map(cls.data)
        cls.stl=read(STL_SOURCE)

    @classmethod
    def tearDownClass(cls):
        assert sha256(PROGRESS.read_bytes()).hexdigest()==cls.progress_before, 'learner progress changed during audit'

    def test_frozen_sources_ids_tracks_and_447_details(self):
        for path,expected in HASHES.items():self.assertEqual(digest(path),expected,path)
        old=read(PREVIOUS)
        self.assertEqual([c['id'] for c in self.data['chapters']],[c['id'] for c in old['chapters']])
        for before,after in zip(old['chapters'],self.data['chapters']):
            self.assertEqual([s['id'] for s in before['steps']],[s['id'] for s in after['steps']])
            self.assertEqual([s.get('track') for s in before['steps']],[s.get('track') for s in after['steps']])
        all_steps=[s for c in self.data['chapters'] for s in c['steps']]
        self.assertEqual(len(self.steps),len(all_steps),'duplicate step IDs')
        active=[s for s in all_steps if s.get('track')!='appendix']
        self.assertEqual(len(active),447)
        for s in active:
            with self.subTest(step=s['id']):
                self.assertTrue(s.get('detail') and isinstance(s['detail'].get('steps'),list) and s['detail']['steps'])
                self.assertTrue(all(isinstance(x,str) and x.strip() for x in s['detail']['steps']))

    def test_191_ch11_demonstrations_match_source_record_photo_and_readback(self):
        demonstrations=[s for s in self.steps.values() if s.get('demonstration') and s.get('track')!='appendix']
        self.assertEqual(len(demonstrations),192)
        own=[s for s in demonstrations if s['id'].startswith('ch11-')]
        self.assertEqual(len(own),191)
        seen=set()
        for step in own:
            demo=step['demonstration'];src=demo['source'];source=ROOT/src['path']
            with self.subTest(step=step['id']):
                self.assertEqual(digest(source),src['sha256'])
                doc=read(source)
                records=[x for x in doc['steps'] if x['id']==demo['recordId']]
                self.assertEqual(len(records),1)
                record=records[0]; key=(src['path'],record['id'])
                self.assertNotIn(key,seen);seen.add(key)
                expected_values=([record['programReadback']] if 'programReadback' in record else [r['value'] for r in record.get('readings',[])])
                self.assertEqual([r['value'] for r in demo['readings'] if r['kind']=='readback'],expected_values)
                if 'programReadback' not in record:
                    self.assertEqual([r['label'] for r in demo['readings']],[r['location'] for r in record['readings']])
                shot=record['screenshot'];path=shot.get('path',shot.get('relativePath'))
                self.assertEqual([(f['path'],f['sha256']) for f in demo['figures']],[(path,shot['sha256'])])
                self.assertEqual(digest(ROOT/path),shot['sha256'])
                self.assertTrue(demo.get('scope'))
        other=[s for s in demonstrations if not s['id'].startswith('ch11-')]
        self.assertEqual([s['id'] for s in other],['ch08-manual-guard-y-reject-01'])
        demo=other[0]['demonstration'];source=ROOT/demo['source']['path'];self.assertEqual(digest(source),demo['source']['sha256'])
        records={r['slug']:r for r in read(source)['records']}
        self.assertEqual(demo['recordId'],'y80-refused')
        self.assertEqual([r['value'] for r in demo['readings']], [records['y80-proposal']['observed'],records['y80-refused']['observed']])
        self.assertEqual([(f['path'],f['sha256']) for f in demo['figures']],[(records[name]['screenshot']['path'],records[name]['screenshot']['sha256']) for name in ('y80-proposal','y80-refused')])
        for fig in demo['figures']:self.assertEqual(digest(ROOT/fig['path']),fig['sha256'])

    def test_six_stl_sources_exports_and_cli_readback(self):
        stl_steps=[s for s in self.steps.values() if s.get('section')=='11-17']
        artifacts=[a for s in stl_steps for a in s.get('artifacts',[])]
        artifact_by_path={a['path']:a for a in artifacts}
        self.assertEqual(len(self.stl['items']),6)
        for item in self.stl['items']:
            with self.subTest(item=item['id']):
                for field,key in [('sourceScene','sourceSha256'),('stl','stlSha256')]:
                    relative=item[field];self.assertIn(relative,artifact_by_path)
                    self.assertEqual(artifact_by_path[relative]['sha256'],item[key])
                    self.assertEqual(digest(ROOT/relative),item[key])
                command=[sys.executable,str(TOOL),'--file',str(ROOT/item['stl']),'--units','mm','--expected-dimensions',*[str(v) for v in item['dimensionsMm']]]
                result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',check=True)
                parsed=json.loads(result.stdout)
                self.assertEqual(parsed['sha256'],item['stlSha256'])
                self.assertEqual(parsed['binaryTriangles'],item['binaryTriangles'])
                self.assertTrue(parsed['numericalComparison']['withinNumericEpsilon'])
                self.assertIsNone(parsed['physicalFit']);self.assertIsNone(parsed['qualifiedClearance'])
        tool_artifacts=[a for a in artifacts if a.get('path')=='learning/tutor/inspect_stl_v001.py']
        self.assertEqual(len(tool_artifacts),6)
        for a in tool_artifacts:self.assertEqual(a['sha256'],digest(TOOL))

    def test_drawings_sources_ch07_checks_and_physical_status(self):
        data=read(CHALLENGES);chapters={c['chapterId']:c for c in data['chapters']}
        for cid,name in [('ch09','tenon-box-lid-drawing-v001.svg'),('ch10','snapfit-box-lid-drawing-v001.svg')]:
            refs=[d for d in chapters[cid]['supplementalDrawings'] if d['path']=='/challenges/'+name]
            self.assertEqual(len(refs),1);self.assertEqual(digest(LEARNING/'web/challenges'/name),refs[0]['sha256'])
            self.assertTrue(refs[0]['description'])
        self.assertTrue(all(x is None for x in read(PATH_DATA)['physicalResults'].values()))
        self.assertTrue(all(x is None for x in chapters['ch11']['physicalResults'].values()))
        for key in ('checks','limitations'):
            text=' '.join(chapters['ch07'].get(key,[]))
            self.assertNotIn('本章詳細文字與操作仍須逐步改寫及實測',text)
        self.assertIn('內腔', ' '.join(chapters['ch07']['checks']))

    def test_http_challenge_whitelist_and_local_stl_links(self):
        with patch.object(server.manage,'CHALLENGES',CHALLENGES):
            httpd=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
            try:
                challenge={c['chapterId']:c for c in read(CHALLENGES)['chapters']}
                targets=[]
                for cid,name in [('ch09','tenon-box-lid-drawing-v001.svg'),('ch10','snapfit-box-lid-drawing-v001.svg')]:
                    ref=next(x for x in challenge[cid]['supplementalDrawings'] if x['path'].endswith('/'+name))
                    targets.append((ref['path'],200,ref['sha256']))
                targets.append(('/challenges/unlisted-correspondence.png',404,None))
                for i in self.stl['items']:
                    targets += [('/files/'+i['sourceScene'],200,i['sourceSha256']),('/files/'+i['stl'],200,i['stlSha256'])]
                for route,expected,expected_hash in targets:
                    conn=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=5)
                    conn.request('GET',route,headers={'Host':f'127.0.0.1:{httpd.server_port}'})
                    response=conn.getresponse();body=response.read()
                    self.assertEqual(response.status,expected,route)
                    if expected_hash:self.assertEqual(sha256(body).hexdigest(),expected_hash,route)
                    conn.close()
            finally:
                httpd.shutdown();httpd.server_close();worker.join(3)

    def test_frozen_builders_refuse_overwrite(self):
        for builder in ['build_engineering_curriculum_v037.py','build_engineering_path_v006.py','build_challenges_v010.py']:
            result=subprocess.run([sys.executable,str(LEARNING/builder)],capture_output=True,text=True,encoding='utf8')
            self.assertNotEqual(result.returncode,0,builder)
            self.assertIn('refus',result.stderr.lower(),builder)
        for path,expected in HASHES.items():self.assertEqual(sha256(path.read_bytes()).hexdigest(),expected)

if __name__=='__main__':unittest.main()
