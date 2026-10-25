"""新下載專案的隔離初始化測試；不讀取或改動作者的個人進度。"""
from __future__ import annotations

import copy
import http.client
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest


LEARNING = Path(__file__).resolve().parents[1]
SCRATCH = (LEARNING / "tests" / ".scratch").resolve()


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="blender-bootstrap-中文 空格-", dir=SCRATCH)).resolve()
        self.root.relative_to(SCRATCH)
        self.addCleanup(self.remove_scratch)
        self.learning = self.root / "learning"
        self.learning.mkdir()
        for name in ("bootstrap.py", "manage.py", "server.py", "catalog.json"):
            shutil.copy2(LEARNING / name, self.learning / name)
        self.catalog = json.loads((self.learning / "catalog.json").read_text(encoding="utf-8"))
        self.progress = self.learning / "progress.json"
        self.environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")

    def remove_scratch(self):
        # 使用同一 Python 程序核對後清理，只移除本測試建立的 scratch 子目錄。
        target = self.root.resolve()
        target.relative_to(SCRATCH)
        self.assertNotEqual(target, SCRATCH)
        self.assertTrue(target.name.startswith("blender-bootstrap-"))
        shutil.rmtree(target)

    def cli(self, script="bootstrap.py", *args, timeout=12):
        return subprocess.run([sys.executable, "-X", "utf8", str(self.learning / script), *args],
                              cwd=self.root, env=self.environment, capture_output=True,
                              text=True, encoding="utf-8", timeout=timeout)

    def initialize(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(self.progress.read_text(encoding="utf-8")), result

    def write_catalog(self, catalog):
        (self.learning / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    def test_fresh_state_and_status_in_relocated_path_with_spaces_and_chinese(self):
        self.assertFalse(self.progress.exists())
        self.assertFalse((self.learning / "workspaces").exists())
        progress, result = self.initialize()
        self.assertIn("created:", result.stdout)
        self.assertEqual(progress["schemaVersion"], 1)
        self.assertEqual(progress["revision"], 1)
        self.assertTrue(progress["updatedAt"].endswith("+08:00"))
        self.assertEqual(progress["activeLesson"], self.catalog["lessons"][0]["id"])
        self.assertEqual(progress["learner"], {"language": "zh-Hant", "timezone": "Asia/Taipei",
                                             "interfaceLanguage": None, "blenderVersion": None})
        self.assertEqual(progress["decisions"], {})
        self.assertEqual(progress["events"], [])
        self.assertEqual(progress["fileVersions"], [])
        self.assertEqual(set(progress["lessons"]), {lesson["id"] for lesson in self.catalog["lessons"]})
        self.assertEqual(len(progress["lessons"]), 9)
        for index, lesson in enumerate(self.catalog["lessons"]):
            state = progress["lessons"][lesson["id"]]
            self.assertEqual(state, {"status": "in_progress" if index == 0 else "not_started",
                                     "currentStep": lesson["steps"][0]["id"], "completedSteps": [],
                                     "notes": [], "workspace": "learning/workspaces/" + lesson["id"]})
            self.assertTrue((self.root / state["workspace"]).is_dir())
        self.assertFalse((self.learning / ".history").exists())
        status = self.cli("manage.py", "status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("revision 1", status.stdout)
        self.assertIn("01-01", status.stdout)
        self.assertIn("尚未記錄", status.stdout)

    def test_initialize_python_contract_returns_created_flag_and_state(self):
        code = ("import bootstrap,json; created,state=bootstrap.initialize(); "
                "print(json.dumps({'created':created,'revision':state['revision']}))")
        for expected in (True, False):
            result = subprocess.run([sys.executable, "-X", "utf8", "-c", code],
                                    cwd=self.learning, env=self.environment, capture_output=True,
                                    text=True, encoding="utf-8", timeout=12)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"created": expected, "revision": 1})

    def test_existing_personal_state_is_kept_byte_for_byte_including_mtime(self):
        progress, _ = self.initialize()
        progress["revision"] = 7
        progress["learner"]["interfaceLanguage"] = "en"
        progress["decisions"]["personalChoice"] = "preserve"
        progress["events"].append({"type": "test_learner_event", "revision": 7})
        progress["lessons"]["01"]["notes"].append({"author": "learner", "text": "保留我的筆記"})
        progress["lessons"]["01"]["completedSteps"] = ["01-01"]
        progress["lessons"]["01"]["currentStep"] = "01-02"
        original = (json.dumps(progress, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        self.progress.write_bytes(original)
        before = self.progress.stat().st_mtime_ns
        (self.learning / "workspaces/09").rmdir()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("kept:", result.stdout)
        self.assertIn("revision 7", result.stdout)
        self.assertEqual(self.progress.read_bytes(), original)
        self.assertEqual(self.progress.stat().st_mtime_ns, before)
        self.assertTrue((self.learning / "workspaces/09").is_dir())
        self.assertFalse((self.learning / ".history").exists())

    def test_corrupt_existing_state_is_rejected_without_replacement(self):
        for original in (b"", b"{bad json", b"[]", b'"not an object"',
                         b'{"schemaVersion":1,"revision":true}',
                         b'{"schemaVersion":1,"revision":1,"lessons":{},"fileVersions":[],"events":[]}'):
            with self.subTest(original=original):
                self.progress.write_bytes(original)
                before = self.progress.stat().st_mtime_ns
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.progress.read_bytes(), original)
                self.assertEqual(self.progress.stat().st_mtime_ns, before)
                self.assertFalse((self.learning / "workspaces").exists())
                self.assertFalse((self.learning / ".history").exists())

    def test_malformed_catalog_ids_steps_and_empty_lists_are_rejected_before_workspace_creation(self):
        mutations = []
        for bad_id in ("../escape", "01/../../escape", "０１", "1", "C:/escape"):
            candidate = copy.deepcopy(self.catalog)
            candidate["lessons"][0]["id"] = bad_id
            mutations.append(candidate)
        duplicate_lesson = copy.deepcopy(self.catalog)
        duplicate_lesson["lessons"][1]["id"] = "01"
        mutations.append(duplicate_lesson)
        for bad_steps in ([], [{"id": "02-01"}], [{"id": "01-01"}, {"id": "01-01"}],
                          [{"id": "01-../escape"}], ["not a step"]):
            candidate = copy.deepcopy(self.catalog)
            candidate["lessons"][0]["steps"] = bad_steps
            mutations.append(candidate)
        mutations.extend(({"schemaVersion": 1, "lessons": []}, {"schemaVersion": 1, "lessons": "wrong"}, []))
        for index, candidate in enumerate(mutations):
            with self.subTest(case=index):
                self.write_catalog(candidate)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.progress.exists())
                self.assertFalse((self.learning / "workspaces").exists())
                self.assertFalse((self.root / "escape").exists())

    def test_workspace_link_is_rejected_without_writing_to_its_target(self):
        outside = self.root / "outside-workspace"
        outside.mkdir()
        root = self.learning / "workspaces"
        root.mkdir()
        try:
            (root / "01").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("此環境沒有建立目錄 symlink 的權限")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.progress.exists())
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((root / "02").exists())

    def test_workspace_file_obstruction_is_rejected_before_creating_other_workspaces(self):
        root = self.learning / "workspaces"
        root.mkdir()
        obstruction = root / "09"
        obstruction.write_bytes(b"preserve")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.progress.exists())
        self.assertFalse((root / "01").exists())
        self.assertEqual(obstruction.read_bytes(), b"preserve")

    @unittest.skipUnless(os.name == "nt", "Windows junction 邊界")
    def test_windows_workspace_junction_is_rejected_without_writing_to_target(self):
        outside = self.root / "outside-workspace"
        outside.mkdir()
        root = self.learning / "workspaces"
        root.mkdir()
        link = root / "01"
        # PowerShell 只建立此隔離測試的 junction；不執行移動或刪除。
        script = ("$ErrorActionPreference='Stop'; "
                  "New-Item -ItemType Junction -Path $env:BOOTSTRAP_TEST_LINK "
                  "-Target $env:BOOTSTRAP_TEST_TARGET | Out-Null")
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script],
                                env=dict(self.environment, BOOTSTRAP_TEST_LINK=str(link),
                                         BOOTSTRAP_TEST_TARGET=str(outside)),
                                capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.progress.exists())
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((root / "02").exists())

    def test_dangling_progress_link_is_never_replaced(self):
        target = self.root / "missing-progress.json"
        try:
            self.progress.symlink_to(target)
        except OSError:
            self.skipTest("此環境沒有建立檔案 symlink 的權限")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.progress.is_symlink())
        self.assertFalse(target.exists())
        self.assertFalse((self.learning / "workspaces").exists())

    def test_held_os_lock_refuses_initialization_without_partial_progress(self):
        ready = self.root / "lock-held"
        code = ("import manage,sys; from pathlib import Path; "
                "lock=manage.progress_lock(); lock.__enter__(); "
                "Path(sys.argv[1]).write_text('ready'); sys.stdin.buffer.read(1); lock.__exit__(None,None,None)")
        holder = subprocess.Popen([sys.executable, "-X", "utf8", "-c", code, str(ready)],
                                  cwd=self.learning, env=self.environment, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 8
            while not ready.exists() and time.monotonic() < deadline:
                if holder.poll() is not None:
                    self.fail("lock holder failed: " + holder.stderr.read().decode("utf-8", errors="replace"))
                time.sleep(.02)
            self.assertTrue(ready.exists(), "isolated lock holder did not become ready")
            result = self.cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("另一個視窗或聊天正在寫入進度", result.stderr)
            self.assertFalse(self.progress.exists())
            self.assertFalse((self.learning / "workspaces").exists())
            self.assertFalse((self.learning / ".history").exists())
        finally:
            if holder.poll() is None:
                holder.communicate(b"x", timeout=5)
            else:
                holder.communicate(timeout=5)
        progress, _ = self.initialize()
        self.assertEqual(progress["revision"], 1)

    def test_fresh_bootstrap_can_start_server_and_serve_api(self):
        progress, _ = self.initialize()
        original = self.progress.read_bytes()
        web = self.learning / "web"
        web.mkdir()
        (web / "index.html").write_text("<!doctype html><title>Bootstrap smoke test</title>", encoding="utf-8")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen([sys.executable, "-X", "utf8", str(self.learning / "server.py"), "--port", str(port)],
                                   cwd=self.root, env=self.environment, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    self.fail("isolated server failed: " + process.stderr.read().decode("utf-8", errors="replace"))
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                try:
                    connection.request("GET", "/api/bootstrap")
                    response = connection.getresponse()
                    body = response.read()
                    self.assertEqual(response.status, 200, body)
                    data = json.loads(body)
                    self.assertEqual(data["progress"], progress)
                    self.assertEqual(Path(data["projectRoot"]).resolve(), self.root)
                    self.assertEqual(data["files"], [])
                    self.assertEqual(data["journal"], [])
                    break
                except OSError:
                    time.sleep(.03)
                finally:
                    connection.close()
            else:
                self.fail("isolated server did not become ready")
        finally:
            if process.poll() is None:
                process.terminate()
            process.communicate(timeout=5)
        self.assertEqual(self.progress.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
