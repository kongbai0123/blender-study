"""通用挑戰題的交易測試；只使用暫存工作區及測試用假 .blend。"""
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
spec = importlib.util.spec_from_file_location("isolated_challenge_manage", LEARNING / "manage.py")
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class ChallengeProgressTests(unittest.TestCase):
    def setUp(self):
        self.real_hash = hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest()
        self.temp = tempfile.TemporaryDirectory(prefix="challenge-progress-test-")
        self.root = Path(self.temp.name).resolve()
        self.learning = self.root / "learning"
        self.learning.mkdir()
        self.progress = self.learning / "progress.json"
        self.catalog = self.learning / "catalog.json"
        self.manifest = self.learning / "web/challenges/challenges-v005.json"
        self.manifest.parent.mkdir(parents=True)
        self.progress.write_text(json.dumps({"schemaVersion": 1, "revision": 1, "updatedAt": "test",
            "activeLesson": "04", "lessons": {
                "04": {"workspace": "learning/workspaces/04", "completedSteps": [], "notes": []},
                "05": {"workspace": "learning/workspaces/05", "completedSteps": [], "notes": []}},
            "fileVersions": [], "events": []}), encoding="utf-8")
        self.catalog.write_text(json.dumps({"schemaVersion": 1, "lessons": [{"id": "04"}, {"id": "05"}]}), encoding="utf-8")
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "chapters": [
            {"chapterId": "ch03", "challengeId": "box-opening-v001", "workspaceLesson": "04"},
            {"chapterId": "ch05", "challengeId": "fit-coupon-v001", "workspaceLesson": "05", "drawing": {"path": "/challenges/fit-trial-drawing-v003.svg"}},
            {"chapterId": "ch08", "challengeId": "linked-box-v001", "workspaceLesson": None, "workspaceId": "engineering-parametric"},
            {"chapterId": "ch02", "challengeId": "tolerance-v001", "workspaceLesson": None, "drawing": {"path": "/challenges/lip-clearance-drawing-v001.svg"}}]}), encoding="utf-8")
        self.patches = [mock.patch.object(manage, "LEARNING", self.learning),
                        mock.patch.object(manage, "PROJECT", self.root),
                        mock.patch.object(manage, "PROGRESS", self.progress),
                        mock.patch.object(manage, "CATALOG", self.catalog),
                        mock.patch.object(manage, "CHALLENGES", self.manifest)]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.temp.cleanup()
        self.assertEqual(self.real_hash, hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest())

    def confirm(self, challenge="fit-coupon-v001", revision=1, **values):
        return manage.mutate("challenge_confirm", None, revision, challenge=challenge, **values)

    def register(self, lesson="05"):
        target = self.learning / ("workspaces/" + lesson + "/test-v001.blend")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"isolated fixture, not a Blender model")
        result = manage.mutate("register_file", lesson, 1, path=f"learning/workspaces/{lesson}/test-v001.blend",
                               role="source_scene", source=None, workspace=None)
        return target, result

    def test_unknown_pilot_and_duplicate_ids_rejected(self):
        before = self.progress.read_bytes()
        for identifier in ("unknown", "box-opening-v001", "../x", None):
            with self.assertRaises(ValueError):
                self.confirm(identifier, evidence="完成")
        data = json.loads(self.manifest.read_text())
        data["chapters"].append(data["chapters"][1])
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "唯一"):
            self.confirm(evidence="完成")
        self.assertEqual(before, self.progress.read_bytes())

    def test_confirmation_notes_separate_and_revision_conflict(self):
        note = "  卡在選取\n請看畫面  "
        result = manage.mutate("challenge_note", None, 1, challenge="fit-coupon-v001", note=note, author="learner")
        self.assertEqual(result["events"][-1]["text"], note)
        self.assertEqual(result["events"][-1]["type"], "challenge_note")
        with self.assertRaises(manage.RevisionConflict):
            self.confirm(revision=1, evidence="完成")
        result = self.confirm(revision=2, evidence="已完成")
        self.assertEqual(result["events"][-1]["type"], "challenge_confirmed")
        self.assertEqual(result["events"][-1]["chapterId"], "ch05")
        self.assertEqual(result["lessons"]["05"]["completedSteps"], [])
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "已確認"):
            self.confirm(revision=3, evidence="再確認")
        self.assertEqual(before, self.progress.read_bytes())

    def test_version_association_checks_lesson_and_current_hash(self):
        target, _ = self.register()
        path = "learning/workspaces/05/test-v001.blend"
        event = self.confirm(revision=2, evidence="完成", source_path=path)["events"][-1]
        self.assertEqual(event["sourcePath"], path)
        self.assertEqual(event["sourceSha256"], hashlib.sha256(target.read_bytes()).hexdigest())

    def test_changed_wrong_owner_and_no_workspace_rejected(self):
        target, _ = self.register()
        path = "learning/workspaces/05/test-v001.blend"
        target.write_bytes(b"overwritten")
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "內容已改變"):
            self.confirm(revision=2, evidence="完成", source_path=path)
        with self.assertRaisesRegex(ValueError, "沒有指定檔案工作區"):
            self.confirm("tolerance-v001", revision=2, evidence="完成", source_path=path)
        self.assertEqual(before, self.progress.read_bytes())

    def test_wrong_owner_rejected(self):
        self.register("04")
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "此題的工作區"):
            self.confirm(revision=2, evidence="完成", source_path="learning/workspaces/04/test-v001.blend")
        self.assertEqual(before, self.progress.read_bytes())

    def test_engineering_workspace_registered_source_and_overwrite(self):
        target = self.learning / "workspaces/engineering-parametric/box-v001.blend"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"isolated engineering fixture")
        path = "learning/workspaces/engineering-parametric/box-v001.blend"
        manage.mutate("register_file", None, 1, path=path, role="source_scene", source=None,
                      workspace="engineering-parametric")
        target.write_bytes(b"changed after registration")
        before = self.progress.read_bytes()
        with self.assertRaisesRegex(ValueError, "內容已改變"):
            self.confirm("linked-box-v001", revision=2, evidence="完成", source_path=path)
        self.assertEqual(before, self.progress.read_bytes())
        target.write_bytes(b"isolated engineering fixture")
        event = self.confirm("linked-box-v001", revision=2, evidence="完成", source_path=path)["events"][-1]
        self.assertEqual(event["sourcePath"], path)
        self.assertEqual(event["sourceSha256"], hashlib.sha256(target.read_bytes()).hexdigest())

    def test_conflicting_or_unknown_workspace_rejected(self):
        data = json.loads(self.manifest.read_text())
        data["chapters"][1]["workspaceId"] = "engineering-parametric"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "不能同時"):
            self.confirm(evidence="完成")
        data["chapters"][1]["workspaceId"] = "unknown"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "工作區設定"):
            self.confirm(evidence="完成")

    def test_cli_parser(self):
        parser = manage.build_parser()
        self.assertEqual(parser.parse_args(["challenge-status", "--challenge", "fit-coupon-v001"]).challenge, "fit-coupon-v001")
        self.assertEqual(parser.parse_args(["challenge-confirm", "--challenge", "fit-coupon-v001", "--revision", "1", "--evidence", "完成"]).evidence, "完成")
        self.assertEqual(parser.parse_args(["challenge-note", "--challenge", "fit-coupon-v001", "--revision", "1", "--note-file", "note.txt"]).author, "tutor")

    def test_http_actions_and_static_allowlist(self):
        shutil.copy2(LEARNING / "manage.py", self.learning / "manage.py")
        shutil.copy2(LEARNING / "server.py", self.learning / "server.py")
        for name in ("index.html", "app.js", "app.css", "challenges-v001.json", "fit-trial-drawing-v001.svg", "fit-trial-drawing-v002.svg", "fit-trial-drawing-v003.svg", "lip-clearance-drawing-v001.svg", "dovetail-trial-drawing-v002.svg", "snapfit-coupons-drawing-v003.svg", "private.txt"):
            (self.manifest.parent / name).write_text("test", encoding="utf-8")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen([sys.executable, str(self.learning / "server.py"), "--port", str(port)],
                                   cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def request(route, payload=None):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            try:
                headers = {"Host": f"127.0.0.1:{port}"}
                if payload is None:
                    conn.request("GET", route, headers=headers)
                else:
                    headers.update({"Origin": f"http://127.0.0.1:{port}", "Content-Type": "application/json"})
                    conn.request("POST", route, body=json.dumps(payload).encode("utf-8"), headers=headers)
                response = conn.getresponse()
                return response.status, response.read()
            finally:
                conn.close()
        try:
            deadline = time.monotonic() + 8
            while True:
                try:
                    if request("/api/health")[0] == 200:
                        break
                except OSError:
                    pass
                if time.monotonic() > deadline:
                    self.fail("隔離伺服器未啟動")
                time.sleep(0.03)
            # 只提供頁面檔與目前題目資料引用的工程圖；歷史版本與未引用的圖不經網頁提供。
            for name in ("index.html", "app.js", "app.css", "manifest.json", "fit-trial-drawing-v003.svg", "lip-clearance-drawing-v001.svg"):
                self.assertEqual(request("/challenges/" + name)[0], 200)
            for name in ("challenges-v001.json", "fit-trial-drawing-v001.svg", "fit-trial-drawing-v002.svg", "dovetail-trial-drawing-v002.svg"):
                self.assertEqual(request("/challenges/" + name)[0], 404)
            self.assertEqual(request("/challenges/private.txt")[0], 404)
            self.assertEqual(request("/challenges/%2e%2e/server.py")[0], 404)
            status, body = request("/api/progress", {"action": "challenge_note", "challengeId": "fit-coupon-v001", "expectedRevision": 1, "note": "卡住", "author": "tutor"})
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)["progress"]["events"][-1]["author"], "learner")
            payload = {"action": "challenge_confirm", "challengeId": "fit-coupon-v001", "expectedRevision": 1, "evidence": "完成"}
            self.assertEqual(request("/api/progress", payload)[0], 409)
            payload["expectedRevision"] = 2
            status, body = request("/api/progress", payload)
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)["progress"]["events"][-1]["type"], "challenge_confirmed")
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
