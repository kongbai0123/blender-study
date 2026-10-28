"""試教題事件走共用交易；測試只使用隔離的暫存工作區。"""
import hashlib
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil
import socket
import subprocess
import sys
import time
import unittest
from unittest import mock

LEARNING = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("isolated_pilot_manage", LEARNING / "manage.py")
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class PilotProgressTests(unittest.TestCase):
    def setUp(self):
        self.real_hash = hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest()
        self.temp = tempfile.TemporaryDirectory(prefix="pilot-progress-test-")
        self.root = Path(self.temp.name).resolve()
        self.learning = self.root / "learning"
        self.learning.mkdir()
        self.progress = self.learning / "progress.json"
        self.catalog = self.learning / "catalog.json"
        self.progress.write_text(json.dumps({"schemaVersion": 1, "revision": 1, "updatedAt": "test",
            "activeLesson": "04", "lessons": {"04": {"workspace": "learning/workspaces/04",
            "completedSteps": [], "notes": []}}, "fileVersions": [], "events": []}), encoding="utf-8")
        self.catalog.write_text(json.dumps({"schemaVersion": 1, "lessons": [{"id": "04"}]}), encoding="utf-8")
        self.patches = [mock.patch.object(manage, "LEARNING", self.learning),
                        mock.patch.object(manage, "PROJECT", self.root),
                        mock.patch.object(manage, "PROGRESS", self.progress),
                        mock.patch.object(manage, "CATALOG", self.catalog)]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.temp.cleanup()
        self.assertEqual(self.real_hash, hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest())

    def confirm(self, revision=1, **values):
        return manage.mutate("pilot_confirm", None, revision, challenge="box-opening-v001", **values)

    def register_box(self):
        target = self.learning / "workspaces/04/box_v001.blend"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"fixture blend")
        result = manage.mutate("register_file", "04", 1, path="learning/workspaces/04/box_v001.blend",
                               role="source_scene", source=None, workspace=None)
        return target, result

    def test_confirmation_is_separate_and_deduplicated(self):
        result = self.confirm(evidence="我已完成小盒")
        self.assertEqual(result["revision"], 2)
        self.assertEqual(result["lessons"]["04"]["completedSteps"], [])
        self.assertEqual(result["events"][-1]["type"], "pilot_challenge_confirmed")
        self.assertEqual(result["events"][-1]["author"], "learner")
        self.assertNotIn("sourcePath", result["events"][-1])
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "已確認"):
            self.confirm(2, evidence="重複")
        with self.assertRaises(manage.RevisionConflict):
            self.confirm(1, evidence="舊版")
        self.assertEqual(before, self.progress.read_bytes())

    def test_registered_version_records_current_hash(self):
        target, result = self.register_box()
        event = self.confirm(2, evidence="完成", source_path="learning/workspaces/04/box_v001.blend")["events"][-1]
        self.assertEqual(event["sourcePath"], "learning/workspaces/04/box_v001.blend")
        self.assertEqual(event["sourceSha256"], hashlib.sha256(target.read_bytes()).hexdigest())
        self.assertEqual(event["sourceSha256"], result["fileVersions"][0]["sha256"])

    def test_changed_and_unregistered_files_rejected_without_write(self):
        target, _ = self.register_box()
        target.write_bytes(b"overwritten")
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "內容已改變"):
            self.confirm(2, evidence="完成", source_path="learning/workspaces/04/box_v001.blend")
        unrelated = target.with_name("other.blend")
        unrelated.write_bytes(b"not registered")
        with self.assertRaisesRegex(ValueError, "已在原盒工作區登記"):
            self.confirm(2, evidence="完成", source_path="learning/workspaces/04/other.blend")
        self.assertEqual(before, self.progress.read_bytes())

    def test_notes_preserve_text_and_invalid_data_do_not_mutate(self):
        raw = "  卡在這裡\n<標記>\n"
        result = manage.mutate("pilot_note", None, 1, challenge="box-opening-v001", note=raw, author="learner")
        self.assertEqual(result["events"][-1]["text"], raw)
        self.assertEqual(result["events"][-1]["noteKind"], "stuck")
        before = self.progress.read_bytes()
        with self.assertRaises(ValueError):
            manage.mutate("pilot_note", None, 2, challenge="other", note="內容", author="learner")
        with self.assertRaises(ValueError):
            self.confirm(2, evidence="  ")
        with self.assertRaises(ValueError):
            manage.mutate("pilot_note", None, 2, challenge="box-opening-v001", note="x", author="robot")
        self.assertEqual(before, self.progress.read_bytes())

    def test_cli_parses_chat_commands(self):
        parser = manage.build_parser()
        self.assertEqual(parser.parse_args(["pilot-status"]).command, "pilot-status")
        args = parser.parse_args(["pilot-confirm", "--revision", "1", "--evidence", "完成"])
        self.assertEqual(args.evidence, "完成")
        args = parser.parse_args(["pilot-note", "--revision", "1", "--note-file", "note.txt"])
        self.assertEqual(args.author, "tutor")

    def test_http_note_confirm_and_revision_conflict_use_same_transaction(self):
        shutil.copy2(LEARNING / "manage.py", self.learning / "manage.py")
        shutil.copy2(LEARNING / "server.py", self.learning / "server.py")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen([sys.executable, str(self.learning / "server.py"), "--port", str(port)],
                                   cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def request(payload=None):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            try:
                headers = {"Host": f"127.0.0.1:{port}"}
                if payload is None:
                    conn.request("GET", "/api/health", headers=headers)
                else:
                    headers.update({"Origin": f"http://127.0.0.1:{port}", "Content-Type": "application/json"})
                    conn.request("POST", "/api/progress", body=json.dumps(payload).encode("utf-8"), headers=headers)
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
                    self.fail("隔離伺服器未啟動")
                time.sleep(0.03)
            note = {"action": "pilot_note", "challengeId": "box-opening-v001", "expectedRevision": 1,
                    "note": "卡在選面", "author": "tutor"}
            status, body = request(note)
            self.assertEqual(status, 200)
            self.assertEqual(body["progress"]["events"][-1]["author"], "learner")
            confirm = {"action": "pilot_confirm", "challengeId": "box-opening-v001", "expectedRevision": 1,
                       "evidence": "完成"}
            self.assertEqual(request(confirm)[0], 409)
            confirm["expectedRevision"] = 2
            status, body = request(confirm)
            self.assertEqual(status, 200)
            self.assertEqual(body["progress"]["events"][-1]["type"], "pilot_challenge_confirmed")
            self.assertEqual(body["progress"]["lessons"]["04"]["completedSteps"], [])
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
