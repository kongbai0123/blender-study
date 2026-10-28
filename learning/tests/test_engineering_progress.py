"""Engineering events use the existing progress transaction and preserve legacy state."""
import copy
import hashlib
import http.client
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


LEARNING = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('isolated_engineering_manage', LEARNING / 'manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class EngineeringProgressTests(unittest.TestCase):
    def setUp(self):
        self.actual_hash = hashlib.sha256((LEARNING / 'progress.json').read_bytes()).hexdigest()
        self.tmp = tempfile.TemporaryDirectory(prefix='blender-engineering-test-')
        self.root = Path(self.tmp.name).resolve()
        self.learning = self.root / 'learning'
        self.learning.mkdir()
        self.progress = {'schemaVersion': 1, 'revision': 1, 'updatedAt': 'test', 'activeLesson': '01',
            'lessons': {'01': {'status': 'in_progress', 'currentStep': '01-01', 'completedSteps': [],
                               'notes': [], 'workspace': 'learning/workspaces/01'}},
            'fileVersions': [], 'events': []}
        self.curriculum = {'schemaVersion': 1, 'id': 'engineering-curriculum-v002', 'chapters': [
            {'id': 'ch01', 'steps': [{'id': 'ch01-fit-surfaces'}, {'id': 'ch01-other'}]},
            {'id': 'ch02', 'steps': [{'id': 'ch02-gap-terms'}]}]}
        save_json(self.learning / 'catalog.json', {'schemaVersion': 1, 'lessons': []})
        save_json(self.learning / 'progress.json', self.progress)
        # Subprocess tests run a copied manage.py, so the fixture uses the pointer's file name.
        curriculum_path = self.learning / 'web' / manage.ENGINEERING_CURRICULUM.name
        save_json(curriculum_path, self.curriculum)
        self.patchers = [mock.patch.object(manage, 'LEARNING', self.learning),
                         mock.patch.object(manage, 'PROJECT', self.root),
                         mock.patch.object(manage, 'PROGRESS', self.learning / 'progress.json'),
                         mock.patch.object(manage, 'CATALOG', self.learning / 'catalog.json'),
                         mock.patch.object(manage, 'ENGINEERING_CURRICULUM', curriculum_path)]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.tmp.cleanup()
        self.assertEqual(self.actual_hash, hashlib.sha256((LEARNING / 'progress.json').read_bytes()).hexdigest())

    def confirm(self, revision=1, chapter='ch01', step='ch01-fit-surfaces'):
        return manage.mutate('engineering_confirm', None, revision, chapter=chapter, step=step, evidence='我確認')

    def test_confirmation_is_atomic_deduplicated_and_preserves_legacy(self):
        before = copy.deepcopy(self.progress)
        result = self.confirm()
        self.assertEqual(result['revision'], 2)
        self.assertEqual(result['lessons'], before['lessons'])
        self.assertEqual(result['fileVersions'], before['fileVersions'])
        self.assertEqual(result['activeLesson'], before['activeLesson'])
        self.assertEqual(result['events'][-1]['type'], 'engineering_step_confirmed')
        self.assertEqual(result['events'][-1]['curriculumId'], 'engineering-curriculum-v002')
        self.assertEqual(result['events'][-1]['author'], 'learner')
        self.assertEqual(json.loads((self.learning / '.history/progress-r000001.json').read_text(encoding='utf-8')), before)
        snapshot = (self.learning / 'progress.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '已確認'):
            self.confirm(revision=2)
        self.assertEqual((self.learning / 'progress.json').read_bytes(), snapshot)
        with self.assertRaises(manage.RevisionConflict):
            self.confirm(revision=1, step='ch01-other')
        self.assertEqual((self.learning / 'progress.json').read_bytes(), snapshot)

    def test_invalid_ids_text_and_kinds_never_mutate(self):
        before = (self.learning / 'progress.json').read_bytes()
        for chapter, step in [('ch99', 'ch01-fit-surfaces'), ('ch02', 'ch01-fit-surfaces'), ('ch01', None)]:
            with self.subTest(chapter=chapter, step=step), self.assertRaises(ValueError):
                self.confirm(chapter=chapter, step=step)
            self.assertEqual((self.learning / 'progress.json').read_bytes(), before)
        for values in [dict(note='  ', note_kind='note', author='learner'),
                       dict(note='x', note_kind='invalid', author='learner'),
                       dict(note='x', note_kind='stuck', author='robot')]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                manage.mutate('engineering_note', None, 1, chapter='ch01', step='ch01-fit-surfaces', **values)
        self.assertEqual((self.learning / 'progress.json').read_bytes(), before)

    def test_appendix_steps_accept_notes_but_never_confirmations(self):
        self.curriculum['chapters'][0]['steps'].append({'id': 'ch01-trial-log', 'track': 'appendix'})
        save_json(manage.ENGINEERING_CURRICULUM, self.curriculum)
        before = (self.learning / 'progress.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '附錄'):
            self.confirm(step='ch01-trial-log')
        self.assertEqual((self.learning / 'progress.json').read_bytes(), before)
        result = manage.mutate('engineering_note', None, 1, chapter='ch01', step='ch01-trial-log',
                               note='這個測試想問一下', note_kind='note', author='learner')
        self.assertEqual(result['events'][-1]['type'], 'engineering_step_note')

    def test_stuck_note_keeps_user_text_verbatim(self):
        raw = '  <script>不要執行</script>\n  卡在這裡\n'
        result = manage.mutate('engineering_note', None, 1, chapter='ch01', step='ch01-fit-surfaces',
                               note=raw, note_kind='stuck', author='learner')
        event = result['events'][-1]
        self.assertEqual(event['text'], raw)
        self.assertEqual(event['noteKind'], 'stuck')
        self.assertEqual(event['author'], 'learner')
        self.assertEqual(result['lessons'], self.progress['lessons'])

    def test_existing_progress_without_engineering_events_and_cli(self):
        parser = manage.build_parser()
        args = parser.parse_args(['engineering-confirm', '--revision', '1', '--chapter', 'ch01',
                                  '--step', 'ch01-fit-surfaces', '--evidence', '完成'])
        result = manage.mutate('engineering_confirm', None, args.revision,
                               chapter=args.chapter, step=args.step, evidence=args.evidence)
        self.assertEqual(result['events'][-1]['stepId'], args.step)

    def test_cli_note_preserves_crlf_and_spaces(self):
        shutil.copy2(LEARNING / 'manage.py', self.learning / 'manage.py')
        note_file = self.root / 'note.txt'
        raw = ' 第一行\r\n第二行 \r\n'
        note_file.write_bytes(raw.encode('utf-8'))
        result = subprocess.run([sys.executable, str(self.learning / 'manage.py'), 'engineering-note',
            '--revision', '1', '--chapter', 'ch01', '--step', 'ch01-fit-surfaces', '--note-kind', 'stuck',
            '--author', 'learner', '--note-file', str(note_file)], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        event = json.loads((self.learning / 'progress.json').read_text(encoding='utf-8'))['events'][-1]
        self.assertEqual(event['text'], raw)
        self.assertEqual(event['author'], 'learner')

    def test_http_actions_same_transaction_and_conflict(self):
        shutil.copy2(LEARNING / 'manage.py', self.learning / 'manage.py')
        shutil.copy2(LEARNING / 'server.py', self.learning / 'server.py')
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen([sys.executable, str(self.learning / 'server.py'), '--port', str(port)],
                                   cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def request(payload=None):
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
            try:
                if payload is None:
                    conn.request('GET', '/api/health', headers={'Host': f'127.0.0.1:{port}'})
                else:
                    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                    conn.request('POST', '/api/progress', body=body, headers={'Host': f'127.0.0.1:{port}',
                        'Origin': f'http://127.0.0.1:{port}', 'Content-Type': 'application/json'})
                response = conn.getresponse()
                return response.status, json.loads(response.read())
            finally:
                conn.close()
        try:
            deadline = time.monotonic() + 8
            while True:
                try:
                    if request()[0] == 200:
                        break
                except OSError:
                    pass
                if time.monotonic() > deadline:
                    self.fail('isolated HTTP server did not start')
                time.sleep(0.03)
            payload = {'action': 'engineering_note', 'chapterId': 'ch01', 'stepId': 'ch01-fit-surfaces',
                       'expectedRevision': 1, 'noteKind': 'stuck', 'note': '  <b>卡住</b>\n', 'author': 'tutor'}
            status, data = request(payload)
            self.assertEqual(status, 200)
            event = data['progress']['events'][-1]
            self.assertEqual((event['author'], event['text']), ('learner', payload['note']))
            payload = {'action': 'engineering_confirm', 'chapterId': 'ch01', 'stepId': 'ch01-fit-surfaces',
                       'expectedRevision': 1, 'evidence': '完成'}
            self.assertEqual(request(payload)[0], 409)
            payload['expectedRevision'] = 2
            self.assertEqual(request(payload)[0], 200)
            payload['expectedRevision'] = 3
            self.assertEqual(request(payload)[0], 400)
            payload.update(expectedRevision=3, chapterId='ch02')
            self.assertEqual(request(payload)[0], 400)
            final = json.loads((self.learning / 'progress.json').read_text(encoding='utf-8'))
            self.assertEqual(final['revision'], 3)
            self.assertEqual(final['lessons'], self.progress['lessons'])
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
