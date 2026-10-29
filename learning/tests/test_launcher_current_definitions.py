"""A running service for this project can still serve an older curriculum."""
import json
import http.server
import shutil
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[2]
SHELL=shutil.which('powershell.exe')


@unittest.skipUnless(SHELL,'Windows PowerShell launcher checks')
class LauncherDefinitionsTests(unittest.TestCase):
    def test_actual_windows_http_decoder_preserves_utf8_version_and_project_text(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body=json.dumps({'version':'v001 · 2026','source':{'sha256':'right'},'project':'教材'},ensure_ascii=False).encode('utf8')
                self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def log_message(self,*args):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix='definition-utf8-') as tmp:
                folder=Path(tmp);(folder/'web').mkdir()
                (folder/'manage.py').write_text('ENGINEERING_CURRICULUM = LEARNING / "web" / "one.json"\nENGINEERING_PATH = LEARNING / "web" / "one.json"\nCHALLENGES = LEARNING / "web" / "one.json"\n',encoding='utf8')
                (folder/'web/one.json').write_text(json.dumps({'version':'v001 · 2026','source':{'sha256':'right'}},ensure_ascii=False),encoding='utf8')
                helper=(ROOT/'learning/Test-LearningDefinitions.ps1').as_posix().replace("'","''")
                task_dir=folder.as_posix().replace("'","''")
                code=f"$ErrorActionPreference='Stop'; . '{helper}'; if(Test-LearningDefinitions -TaskLearningRoot '{task_dir}' -TaskPort {server.server_port}){{'current'}}else{{'stale'}}"
                result=subprocess.run([SHELL,'-NoProfile','-ExecutionPolicy','Bypass','-Command',code],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'current')
        finally:server.shutdown();server.server_close();thread.join(3)

    def check_case(self,mode):
        with tempfile.TemporaryDirectory(prefix='learning-definition-test-') as tmp:
            folder=Path(tmp);(folder/'web/challenges').mkdir(parents=True)
            (folder/'manage.py').write_text('ENGINEERING_CURRICULUM = LEARNING / "web" / "course-new.json"\nENGINEERING_PATH = LEARNING / "web" / "path-new.json"\nCHALLENGES = LEARNING / "web" / "challenges" / "tasks-new.json"\n',encoding='utf8')
            for name in ('web/course-new.json','web/path-new.json','web/challenges/tasks-new.json'):
                (folder/name).write_text(json.dumps({'version':'current','source':{'sha256':'right'}}),encoding='utf8')
            helper=(ROOT/'learning/Test-LearningDefinitions.ps1').as_posix().replace("'","''")
            task_dir=folder.as_posix().replace("'","''")
            response = "throw 'unavailable'" if mode=='unavailable' else "@{version='"+('old' if mode=='stale' else 'current')+"'; source=@{sha256='"+('wrong' if mode=='source_mismatch' else 'right')+"'}}"
            code=f"$ErrorActionPreference='Stop'; . '{helper}'; $result = Test-LearningDefinitions -TaskLearningRoot '{task_dir}' -TaskPort 12345 -FetchJson {{ param($u) {response} }}; if ($result) {{'current'}} else {{'stale'}}"
            # Match Start-Learning.cmd's existing process-only invocation;
            # do not change any machine/user execution-policy setting.
            result=subprocess.run([SHELL,'-NoProfile','-ExecutionPolicy','Bypass','-Command',code],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            return result.stdout.strip()

    def test_stale_or_unavailable_same_project_server_is_not_reused(self):
        for mode in ('stale','unavailable','source_mismatch'):
            self.assertEqual(self.check_case(mode),'stale',mode)

    def test_matching_versions_and_sources_are_reused(self):
        self.assertEqual(self.check_case('current'),'current')
