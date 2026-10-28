"""Engineering workspace: copy of the guarded demo box, registration, and the guard's refusal.

Every test runs on a temporary project; the real progress.json and workspaces are only read.
"""
import contextlib
import hashlib
import http.client
import importlib.util
import io
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
spec = importlib.util.spec_from_file_location('isolated_workspace_manage', LEARNING / 'manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)
guard_spec = importlib.util.spec_from_file_location('isolated_workspace_guard', LEARNING / 'tutor' / 'guarded_manual_box_v001.py')
guard = importlib.util.module_from_spec(guard_spec)
guard_spec.loader.exec_module(guard)

WORKSPACE = 'engineering-parametric'
LEGACY_NOTES = [
    {'at': '2026-10-22T11:10:29+08:00', 'text': '一般助教筆記', 'noteKind': 'note', 'step': '01-01'},
    {'at': '2026-10-27T13:06:47+08:00', 'text': '是下方的環形唇邊', 'noteKind': 'note', 'author': 'learner', 'step': '01-01'},
    {'at': '2026-10-27T13:06:47+08:00', 'text': 'engineering:path-01-observe-lip:answered\n學員已正確辨認環形唇邊。',
     'noteKind': 'note', 'author': 'tutor', 'step': '01-01'},
]


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class EngineeringWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.actual = {name: hashlib.sha256((LEARNING / name).read_bytes()).hexdigest() for name in ('progress.json', 'catalog.json')}
        self.tmp = tempfile.TemporaryDirectory(prefix='blender-engineering-workspace-')
        self.root = Path(self.tmp.name).resolve()
        self.learning = self.root / 'learning'
        self.progress = {'schemaVersion': 1, 'revision': 1, 'updatedAt': 'test', 'activeLesson': '01',
            'lessons': {'01': {'status': 'in_progress', 'currentStep': '01-01', 'completedSteps': [],
                               'notes': [dict(note) for note in LEGACY_NOTES], 'workspace': 'learning/workspaces/01'}},
            'fileVersions': [], 'events': []}
        save_json(self.learning / 'catalog.json', {'schemaVersion': 1, 'lessons': [
            {'id': '01', 'title': '基本操作', 'steps': [{'id': '01-01', 'title': '開啟', 'action': '開啟', 'success': '看到畫面'}]}]})
        save_json(self.learning / 'progress.json', self.progress)
        (self.learning / 'workspaces/01').mkdir(parents=True)
        self.base = self.root / manage.MANUAL_BOX_BASE[0]
        self.base.parent.mkdir(parents=True)
        shutil.copy2(LEARNING.parent / manage.MANUAL_BOX_BASE[0], self.base)
        self.patchers = [mock.patch.object(manage, 'LEARNING', self.learning),
                         mock.patch.object(manage, 'PROJECT', self.root),
                         mock.patch.object(manage, 'PROGRESS', self.learning / 'progress.json'),
                         mock.patch.object(manage, 'CATALOG', self.learning / 'catalog.json')]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.tmp.cleanup()
        for name, digest in self.actual.items():
            self.assertEqual(digest, hashlib.sha256((LEARNING / name).read_bytes()).hexdigest(), name)

    def workspace(self):
        return self.root / manage.ENGINEERING_WORKSPACES[WORKSPACE]

    def copy_box(self, name='my_manual_box_v001.blend'):
        with contextlib.redirect_stdout(io.StringIO()):
            return manage.engineering_workspace(name)

    def register(self, path, revision=1, role='source_scene', source=None, lesson=None, workspace=WORKSPACE):
        return manage.mutate('register_file', lesson, revision, path=path, role=role, source=source, workspace=workspace)

    def test_workspace_command_creates_folder_and_verified_copy_without_touching_progress(self):
        before = (self.learning / 'progress.json').read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(manage.engineering_workspace())
        self.assertTrue(self.workspace().is_dir())
        target = self.copy_box()
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), manage.MANUAL_BOX_BASE[1])
        self.assertEqual(target.parent, self.workspace())
        with self.assertRaisesRegex(ValueError, '已存在'):
            self.copy_box()
        for name in ('../escape.blend', 'nested/box.blend', 'box.txt', '.hidden.blend', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.copy_box(name)
        self.assertEqual((self.learning / 'progress.json').read_bytes(), before)

    def test_changed_demo_base_is_never_copied(self):
        self.base.write_bytes(self.base.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, '不符'):
            self.copy_box()
        self.assertFalse((self.workspace() / 'my_manual_box_v001.blend').exists())

    def test_workspace_registration_records_owner_and_links_sources(self):
        self.copy_box()
        relative = 'learning/workspaces/engineering-parametric/my_manual_box_v001.blend'
        result = self.register(relative)
        record = result['fileVersions'][-1]
        self.assertEqual((record['workspace'], record['path'], record['role']), (WORKSPACE, relative, 'source_scene'))
        self.assertNotIn('lesson', record)
        self.assertEqual(result['events'][-1]['type'], 'file_registered')
        self.assertEqual(result['events'][-1]['workspace'], WORKSPACE)
        export = self.workspace() / 'box_v001.stl'
        export.write_bytes(b'solid test\nendsolid test\n')
        result = self.register('learning/workspaces/engineering-parametric/box_v001.stl', revision=2, role='export', source=relative)
        self.assertEqual(result['fileVersions'][-1]['source']['path'], relative)
        # A lesson source cannot be used for a workspace export, and owners cannot be mixed.
        lesson_file = self.learning / 'workspaces/01/u01_basics_v001.blend'
        lesson_file.write_bytes(b'BLENDER-test')
        self.register('learning/workspaces/01/u01_basics_v001.blend', revision=3, lesson='01', workspace=None)
        with self.assertRaisesRegex(ValueError, '同一工作區'):
            self.register('learning/workspaces/engineering-parametric/box_v001.stl', revision=4, role='export',
                          source='learning/workspaces/01/u01_basics_v001.blend')
        with self.assertRaisesRegex(ValueError, '擇一'):
            self.register(relative, revision=4, lesson='01')
        with self.assertRaisesRegex(ValueError, '指定的工作區'):
            self.register('learning/workspaces/01/u01_basics_v001.blend', revision=4)
        with self.assertRaisesRegex(ValueError, '不支援'):
            self.register(relative, revision=4, workspace='other')

    def test_registered_copy_is_refused_by_the_guarded_panel(self):
        self.copy_box()
        working = self.copy_box('my_manual_box_v002.blend')
        registered = self.workspace() / 'my_manual_box_v001.blend'
        progress_path = self.learning / 'progress.json'
        self.assertIsNone(guard.workspace_error(str(registered), self.root, self.workspace(), progress_path))
        self.register('learning/workspaces/engineering-parametric/my_manual_box_v001.blend')
        self.assertEqual(guard.workspace_error(str(registered), self.root, self.workspace(), progress_path),
                         '此檔案已登記為版本；請先以新檔名另存。')
        self.assertIsNone(guard.workspace_error(str(working), self.root, self.workspace(), progress_path))

    def test_cli_register_file_accepts_workspace_and_rejects_two_owners(self):
        parser = manage.build_parser()
        args = parser.parse_args(['register-file', '--workspace', WORKSPACE, '--revision', '1',
                                  '--path', 'learning/workspaces/engineering-parametric/a.blend', '--role', 'source_scene'])
        self.assertEqual((args.workspace, args.lesson), (WORKSPACE, None))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(['register-file', '--workspace', WORKSPACE, '--lesson', '01', '--revision', '1',
                               '--path', 'x.blend', '--role', 'source_scene'])

    def test_legacy_engineering_answer_is_separated_from_lesson_notes(self):
        legacy = manage.legacy_engineering_notes(self.progress)
        self.assertEqual(legacy, {('01', 1): {'activity': 'path-01-observe-lip', 'role': 'answer'},
                                  ('01', 2): {'activity': 'path-01-observe-lip', 'role': 'marker'}})
        catalog, progress = manage.load_state()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            manage.status(catalog, progress, type('Args', (), {'lesson': '01'})())
        text = output.getvalue()
        self.assertIn('最近筆記（未標示作者）：一般助教筆記', text)
        self.assertNotIn('engineering:path-01-observe-lip', text)
        self.assertIn('engineering-status', text)

    def test_default_status_leads_with_the_next_main_step(self):
        curriculum = {'schemaVersion': 1, 'id': 'engineering-curriculum-v002', 'chapters': [
            {'id': 'ch01', 'number': '01', 'title': '基本操作', 'sections': [{'id': '01-01', 'title': '開啟'}, {'id': '01-02', 'title': '觀察'}],
             'steps': [{'id': 'ch01-a', 'section': '01-01', 'title': '辨認畫面', 'actions': ['看畫面'], 'success': '能回報'},
                       {'id': 'ch01-lip', 'section': '01-02', 'title': '辨認唇邊', 'actions': ['看圖'], 'legacyActivity': 'path-01-observe-lip'},
                       {'id': 'ch01-extra', 'section': '01-02', 'title': '選修', 'actions': ['x'], 'track': 'optional'}]}]}
        save_json(self.learning / 'web/curriculum.json', curriculum)
        self.progress['events'].append({'type': 'engineering_step_confirmed', 'curriculumId': 'engineering-curriculum-v002',
                                        'chapterId': 'ch01', 'stepId': 'ch01-a', 'author': 'learner'})
        with mock.patch.object(manage, 'ENGINEERING_CURRICULUM', self.learning / 'web/curriculum.json'):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                manage.status({}, self.progress, type('Args', (), {'lesson': None})())
        text = output.getvalue()
        self.assertIn('新版主線：1 / 2 小步已確認', text)
        self.assertIn('下一小步 ch01-lip：第 01 章 基本操作 › 01-02 觀察 › 辨認唇邊', text)
        self.assertIn('學員先前在聊天的回答（尚未確認本步）：是下方的環形唇邊', text)
        self.assertIn('原教材只供查閱', text)

    def test_legacy_rule_needs_marker_on_first_line_and_matching_answer(self):
        cases = [
            ('marker later in the text', [LEGACY_NOTES[1], dict(LEGACY_NOTES[2], text='說明\nengineering:path-01-observe-lip:answered')], {}),
            ('answer at another time', [dict(LEGACY_NOTES[1], at='2026-10-27T13:00:00+08:00'), LEGACY_NOTES[2]],
             {('01', 1): {'activity': 'path-01-observe-lip', 'role': 'marker'}}),
            ('marker by the learner', [LEGACY_NOTES[1], dict(LEGACY_NOTES[2], author='learner')], {}),
        ]
        for label, notes, expected in cases:
            with self.subTest(label):
                progress = {'lessons': {'01': {'notes': notes}}}
                self.assertEqual(manage.legacy_engineering_notes(progress), expected)

    def test_http_registration_and_bootstrap_expose_workspace_and_legacy_notes(self):
        for name in ('manage.py', 'server.py'):
            shutil.copy2(LEARNING / name, self.learning / name)
        (self.learning / 'web').mkdir()
        (self.learning / 'journal').mkdir()
        shutil.copytree(LEARNING / 'tutor', self.learning / 'tutor', ignore=shutil.ignore_patterns('__pycache__', 'scenarios', 'tests'))
        self.copy_box()
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen([sys.executable, str(self.learning / 'server.py'), '--port', str(port)],
                                   cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def request(method, route, payload=None):
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
            try:
                headers = {'Host': f'127.0.0.1:{port}'}
                body = None
                if payload is not None:
                    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                    headers.update({'Origin': f'http://127.0.0.1:{port}', 'Content-Type': 'application/json'})
                conn.request(method, route, body=body, headers=headers)
                response = conn.getresponse()
                return response.status, json.loads(response.read())
            finally:
                conn.close()
        try:
            deadline = time.monotonic() + 8
            while True:
                try:
                    if request('GET', '/api/health')[0] == 200:
                        break
                except OSError:
                    pass
                if time.monotonic() > deadline:
                    self.fail('isolated HTTP server did not start')
                time.sleep(0.03)
            status, data = request('GET', '/api/bootstrap')
            self.assertEqual(status, 200)
            self.assertEqual(data['engineeringWorkspaces'], manage.ENGINEERING_WORKSPACES)
            self.assertEqual([(item['noteIndex'], item['role']) for item in data['legacyEngineeringNotes']], [(1, 'answer'), (2, 'marker')])
            self.assertIn('learning/workspaces/engineering-parametric/my_manual_box_v001.blend', [item['path'] for item in data['files']])
            payload = {'workspaceId': WORKSPACE, 'expectedRevision': 1, 'role': 'source_scene',
                       'path': 'learning/workspaces/engineering-parametric/my_manual_box_v001.blend'}
            status, data = request('POST', '/api/register-file', payload)
            self.assertEqual(status, 200)
            self.assertEqual(data['progress']['fileVersions'][-1]['workspace'], WORKSPACE)
            status, _ = request('POST', '/api/register-file', dict(payload, expectedRevision=2, lessonId='01'))
            self.assertEqual(status, 400)
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
