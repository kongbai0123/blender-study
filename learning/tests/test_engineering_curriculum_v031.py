"""Ensure v031 adds traceable draft detail without changing existing learning state or evidence."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v030.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v031.json'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

class CurriculumV031Tests(unittest.TestCase):
    def test_coverage_and_preservation(self):
        old, new = read(OLD), read(NEW)
        self.assertEqual(old['id'], new['id'])
        count = 0
        for before, after in zip(old['chapters'], new['chapters'], strict=True):
            self.assertEqual({k:v for k,v in before.items() if k!='steps'}, {k:v for k,v in after.items() if k!='steps'})
            for a,b in zip(before['steps'], after['steps'], strict=True):
                if before['id'] in ('ch07','ch08','ch09','ch10','ch11','ch12') and not a.get('track'):
                    pending = {'ch11-08-02-02', 'ch11-08-03-01', 'ch11-08-03-02', 'ch11-08-04-02'}
                    omit = {'detail', 'actions', 'success'} if a['id'] in pending else {'detail'}
                    self.assertEqual({k:v for k,v in a.items() if k not in omit}, {k:v for k,v in b.items() if k not in omit})
                    if a['id'] in pending:
                        self.assertIn('尚不能',b['actions'][0]);self.assertIn('待後續實作及驗證',b['success'])
                    d=b['detail'];self.assertEqual(set(d),{'steps','why','verification'})
                    self.assertTrue(1<=len(d['steps'])<=3 and all(isinstance(s,str) and s.strip() for s in d['steps']))
                    self.assertIn('尚未逐步重新實拍',d['verification']);self.assertTrue(d['why'].strip())
                    count+=1
                else: self.assertEqual(a,b)
        self.assertEqual(count,110)
        self.assertFalse(new['contentReview']['reviewV031']['learnerProgressChanged'])
        for entry in new['sourceVersions'][-3:]:
            self.assertEqual(hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest(),entry['sha256'])

    def test_builder_refuses_to_overwrite(self):
        before=NEW.read_bytes()
        result=subprocess.run([sys.executable,'-X','utf8','learning/build_engineering_curriculum_v031.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('refusing to overwrite',result.stderr)
        self.assertEqual(before,NEW.read_bytes())

if __name__ == '__main__':
    unittest.main()
