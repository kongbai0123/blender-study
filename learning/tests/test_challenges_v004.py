"""保留既有題目，僅釐清新舊盲孔柱草案的版本關係。"""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'learning/web/challenges/challenges-v003.json'
OUTPUT=ROOT/'learning/web/challenges/challenges-v004.json'

class ChallengeV004Tests(unittest.TestCase):
    def test_only_intended_limitation_changed(self):
        old=json.loads(SOURCE.read_bytes());new=json.loads(OUTPUT.read_bytes())
        self.assertEqual(new['previousVersion']['sha256'],hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        for a,b in zip(old['chapters'],new['chapters'],strict=True):
            if a['chapterId']=='ch11':
                self.assertEqual({k:v for k,v in a.items() if k!='limitations'},{k:v for k,v in b.items() if k!='limitations'})
                self.assertEqual(a['limitations'][1:],b['limitations'][1:]);self.assertIn('不同版本',b['limitations'][0])
            else:self.assertEqual(a,b)

    def test_builder_refuses_overwrite(self):
        before=OUTPUT.read_bytes(); result=subprocess.run([sys.executable,'-X','utf8','learning/build_challenges_v004.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
        self.assertNotEqual(result.returncode,0);self.assertIn('refusing to overwrite',result.stderr);self.assertEqual(before,OUTPUT.read_bytes())

if __name__=='__main__':unittest.main()
