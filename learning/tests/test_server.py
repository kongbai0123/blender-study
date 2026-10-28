"""真實 progress.json 僅讀取；每個 API/CLI 測試在受控 scratch 副本執行。"""
from __future__ import annotations

import hashlib
import http.client
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest


LEARNING = Path(__file__).resolve().parents[1]
SCRATCH = (LEARNING / "tests" / ".scratch").resolve()


def current_pointer():
    """目前工程教材版本只在 manage.py 指定；測試讀同一個指標，不另寫版本號。"""
    spec = importlib.util.spec_from_file_location("isolated_manage_pointer", LEARNING / "manage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.original_hash = hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest()
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="blender-api-", dir=SCRATCH)).resolve()
        self.root.relative_to(SCRATCH)
        self.learning = self.root / "learning"
        self.learning.mkdir()
        for name in ("server.py", "manage.py", "catalog.json", "progress.json"):
            shutil.copy2(LEARNING / name, self.learning / name)
        lesson_ids = json.loads((LEARNING / "progress.json").read_text(encoding="utf-8"))["lessons"]
        for name in ("assets", "evidence", "journal", "web", *("workspaces/" + lesson for lesson in lesson_ids)):
            (self.learning / name).mkdir(parents=True, exist_ok=True)
        (self.learning / "web/index.html").write_text("<!doctype html><title>Test</title>", encoding="utf-8")
        (self.learning / "evidence/help.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (self.learning / "assets/old-diagram.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (self.learning / "journal/test.md").write_text("# Test journal\n<script>alert(1)</script>", encoding="utf-8")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            self.port = listener.getsockname()[1]
        self.server_log = (self.root / "server-error.log").open("wb")
        self.process = subprocess.Popen([sys.executable, str(self.learning / "server.py"), "--port", str(self.port)],
                                        cwd=self.root, stdout=subprocess.DEVNULL, stderr=self.server_log)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            try:
                status, _, _ = self.request("GET", "/api/health")
                if status == 200:
                    break
            except OSError:
                time.sleep(0.03)
        else:
            self.fail("isolated server did not start")

    def tearDown(self):
        self.process.terminate()
        self.process.wait(timeout=5)
        self.server_log.close()
        # 遞迴刪除前重新核對絕對路徑，只刪除本測試建立的 scratch 子目錄。
        target = self.root.resolve()
        target.relative_to(SCRATCH)
        self.assertNotEqual(target, SCRATCH)
        self.assertTrue(target.name.startswith("blender-api-"))
        shutil.rmtree(target)
        self.assertEqual(self.original_hash, hashlib.sha256((LEARNING / "progress.json").read_bytes()).hexdigest())

    def request(self, method, route, payload=None, headers=None, raw=None, timeout=3):
        body = raw if raw is not None else (json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None)
        request_headers = {"Host": f"127.0.0.1:{self.port}"}
        if body is not None:
            request_headers.update({"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{self.port}"})
        request_headers.update(headers or {})
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        try:
            connection.request(method, route, body=body, headers=request_headers)
            response = connection.getresponse()
            data, response_headers = response.read(), dict(response.getheaders())
            if response_headers.get("Content-Type", "").startswith("application/json"):
                data = json.loads(data)
            return response.status, data, response_headers
        finally:
            connection.close()

    def bootstrap(self):
        status, data, _ = self.request("GET", "/api/bootstrap")
        self.assertEqual(status, 200)
        return data

    def test_pilot_static_assets_are_narrowly_allowlisted(self):
        pilot = self.learning / "web" / "pilot"
        pilot.mkdir()
        challenges = self.learning / "web" / "challenges"
        challenges.mkdir()
        # 試教頁已併入練習題頁：只留轉址頁與共用樣式，圖與動畫要由目前題目資料引用才提供。
        (challenges / "challenges-v005.json").write_text(json.dumps({"schemaVersion": 1, "chapters": [
            {"chapterId": "ch03", "drawing": {"path": "/pilot/box-drawing-v002.svg"}, "animation": {"path": "/pilot/box-demo.gif"}}]}), encoding="utf-8")
        for name, content, status in (("box-lesson.html", "<title>pilot</title>", 200),
                                      ("box-lesson.css", "body {}", 200),
                                      ("box-lesson.js", "'use strict';", 404),
                                      ("box-demo.gif", "GIF89a", 200),
                                      ("box-drawing.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>', 404),
                                      ("box-drawing-v002.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>', 200)):
            (pilot / name).write_text(content, encoding="utf-8")
            self.assertEqual(self.request("GET", "/pilot/" + name)[0], status, name)
        (pilot / "hidden.txt").write_text("not public", encoding="utf-8")
        self.assertEqual(self.request("GET", "/pilot/hidden.txt")[0], 404)
        self.assertEqual(self.request("GET", "/pilot/%2e%2e/server.py")[0], 404)
        # /files/ 不因試教頁而允許讀取網頁或擴大執行範圍。
        self.assertEqual(self.request("GET", "/files/learning/web/pilot/box-lesson.html")[0], 403)

    def post(self, payload, route="/api/progress"):
        return self.request("POST", route, payload)

    def confirm_payload(self):
        progress = self.bootstrap()["progress"]
        lesson = progress["activeLesson"]
        return {"action": "confirm_step", "lessonId": lesson,
                "stepId": progress["lessons"][lesson]["currentStep"],
                "expectedRevision": progress["revision"], "evidence": "隔離測試學員確認"}

    def test_bootstrap_and_export_are_read_only(self):
        original = (self.learning / "progress.json").read_bytes()
        data = self.bootstrap()
        self.assertEqual(set(data), {"projectRoot", "catalog", "progress", "files", "journal",
                                     "engineeringWorkspaces", "legacyEngineeringNotes"})
        self.assertEqual(data["engineeringWorkspaces"], {"engineering-parametric": "learning/workspaces/engineering-parametric"})
        for record in data["legacyEngineeringNotes"]:
            note = data["progress"]["lessons"][record["lessonId"]]["notes"][record["noteIndex"]]
            self.assertEqual(note["author"], "learner" if record["role"] == "answer" else "tutor")
        self.assertEqual(data["projectRoot"], str(self.root))
        self.assertEqual(data["journal"], [{"path": "learning/journal/test.md", "title": "Test journal"}])
        status, health, _ = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(health, {"application": "blender-guided-learning", "project": str(self.root), "ready": True})
        status, exported, headers = self.request("GET", "/api/export")
        self.assertEqual(status, 200)
        self.assertEqual(exported, data["progress"])
        self.assertIn("attachment", headers["Content-Disposition"])
        self.assertEqual(original, (self.learning / "progress.json").read_bytes())

    def test_real_catalog_uses_only_existing_screenshots(self):
        # 專案內容不使用示意圖；圖片必須是 evidence 中真實存在的截圖。
        catalog = json.loads((LEARNING / "catalog.json").read_text(encoding="utf-8"))
        for lesson in catalog["lessons"]:
            for step in lesson["steps"]:
                for figure in step.get("figures", []):
                    self.assertEqual(figure.get("type"), "screenshot", step["id"])
                    self.assertTrue(figure["path"].startswith("learning/evidence/"), step["id"])
                    self.assertTrue((LEARNING.parent / figure["path"]).is_file(), figure["path"])
                    self.assertIn(Path(figure["path"]).suffix.lower(), {".png", ".jpg", ".jpeg", ".webp"})

    def test_engineering_path_assets_are_named_and_read_only(self):
        original = (self.learning / "progress.json").read_bytes()
        pointer = current_pointer()
        # 目前版本只由 manage.py 指定；網頁只用固定網址，歷史版本與其他 JSON 都不經網頁提供。
        for route, name, body in (("/engineering-path.js", "engineering-path.js", "'use strict';"),
                                  ("/engineering-path.json", pointer.ENGINEERING_PATH.name, '{"schemaVersion":1,"kind":"path"}'),
                                  ("/engineering-curriculum.json", pointer.ENGINEERING_CURRICULUM.name, '{"schemaVersion":1,"kind":"curriculum"}')):
            (self.learning / "web" / name).write_text(body, encoding="utf-8")
            status, content, headers = self.request("GET", route)
            self.assertEqual(status, 200)
            self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
            self.assertEqual(content, json.loads(body) if name.endswith(".json") else body.encode())
        (self.learning / "web/private.json").write_text('{"private":true}', encoding="utf-8")
        (self.learning / "web/engineering-curriculum-v027.json").write_text('{"schemaVersion":1}', encoding="utf-8")
        for route in ("/private.json", "/engineering-path-v001.json", "/engineering-curriculum-v027.json",
                      "/" + pointer.ENGINEERING_CURRICULUM.name, "/web/private.json"):
            self.assertEqual(self.request("GET", route)[0], 404, route)
        self.assertEqual(self.request("GET", "/files/learning/web/engineering-path.js")[0], 403)
        self.assertEqual(original, (self.learning / "progress.json").read_bytes())

    def test_engineering_path_references_and_original_pixels(self):
        pointer = current_pointer()
        document = json.loads(pointer.ENGINEERING_PATH.read_text(encoding="utf-8"))
        curriculum = json.loads(pointer.ENGINEERING_CURRICULUM.read_text(encoding="utf-8"))
        catalog = json.loads((LEARNING / "catalog.json").read_text(encoding="utf-8"))
        references = {(lesson["id"], step["id"]) for lesson in catalog["lessons"] for step in lesson["steps"]}
        chapter_ids = [chapter["id"] for chapter in document["chapters"]]
        self.assertEqual(len(chapter_ids), len(set(chapter_ids)))
        for chapter in document["chapters"]:
            for reference in chapter["references"]:
                self.assertIn((reference["lessonId"], reference["stepId"]), references)
        original_figures = {event["figure"]["path"]: event["figure"] for lesson in catalog["lessons"]
                            for step in lesson["steps"] for event in step.get("operationRun", {}).get("events", [])}
        # 第 01 章章末的兩題觀察沿用 05-05 示範原圖，必須與原 run 的像素指紋一致。
        observation = [step for step in curriculum["chapters"][0]["steps"] if step["id"] in ("ch01-observe-lip", "ch01-fit-surfaces")]
        self.assertEqual(len(observation), 2)
        for figure in [figure for step in observation for figure in step["figures"]]:
            original = original_figures[figure["path"]]
            self.assertEqual(figure["type"], "screenshot")
            self.assertEqual(figure["sha256"], original["sha256"])
            self.assertEqual(hashlib.sha256((LEARNING.parent / figure["path"]).read_bytes()).hexdigest(), figure["sha256"])
        source = document["baseline"]["sourceScene"]
        self.assertEqual(hashlib.sha256((LEARNING.parent / source["path"]).read_bytes()).hexdigest(), source["sha256"])

    def test_engineering_curriculum_steps_and_evidence(self):
        pointer = current_pointer()
        document = json.loads(pointer.ENGINEERING_CURRICULUM.read_text(encoding="utf-8"))
        outline = json.loads(pointer.ENGINEERING_PATH.read_text(encoding="utf-8"))
        catalog = json.loads((LEARNING / "catalog.json").read_text(encoding="utf-8"))
        references = {(lesson["id"], step["id"]) for lesson in catalog["lessons"] for step in lesson["steps"]}
        self.assertEqual([x["id"] for x in document["chapters"]], [x["id"] for x in outline["chapters"]])
        step_ids = set()
        for chapter in document["chapters"]:
            self.assertTrue(chapter["steps"], chapter["id"])
            for step in chapter["steps"]:
                self.assertNotIn(step["id"], step_ids)
                step_ids.add(step["id"])
                self.assertTrue(step["title"] and step["goal"] and step["success"], step["id"])
                self.assertTrue(step["actions"], step["id"])
                for ref in step.get("sourceSteps", []):
                    self.assertIn((ref["lessonId"], ref["stepId"]), references)
                for figure in step.get("figures", []):
                    self.assertEqual(figure["type"], "screenshot")
                    self.assertTrue(figure["path"].startswith("learning/evidence/"))
                    path = LEARNING.parent / figure["path"]
                    self.assertTrue(path.is_file(), figure["path"])
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), figure["sha256"], figure["path"])

    def test_operation_run_screenshots_match_files_and_highlights_fit(self):
        # 助教示範實拍：檔案存在、雜湊與尺寸和紀錄一致，標示框落在圖內（標示由網頁疊上，不改原圖）。
        catalog = json.loads((LEARNING / "catalog.json").read_text(encoding="utf-8"))
        for lesson in catalog["lessons"]:
            for step in lesson["steps"]:
                for event in (step.get("operationRun") or {}).get("events", []):
                    figure = event.get("figure") or {}
                    path = LEARNING.parent / figure["path"]
                    self.assertTrue(figure["path"].startswith("learning/evidence/") and path.is_file(), figure["path"])
                    if "sha256" in figure:
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), figure["sha256"], figure["path"])
                    if path.suffix.lower() == ".png" and "width" in figure:
                        width, height = struct.unpack(">II", path.read_bytes()[16:24])
                        self.assertEqual((width, height), (figure["width"], figure["height"]), figure["path"])
                    for mark in figure.get("highlights", []):
                        self.assertTrue(0 <= mark["x"] and 0 <= mark["y"] and mark["w"] > 0 and mark["h"] > 0, mark)
                        self.assertLessEqual(mark["x"] + mark["w"], figure["width"], (figure["path"], mark))
                        self.assertLessEqual(mark["y"] + mark["h"], figure["height"], (figure["path"], mark))

    def test_confirm_rejects_stale_duplicate_and_skipping(self):
        payload = self.confirm_payload()
        skipped = dict(payload, stepId="01-03")
        self.assertEqual(self.post(skipped)[0], 400)
        status, result, _ = self.post(payload)
        self.assertEqual(status, 200)
        progress = result["progress"]
        self.assertEqual(progress["revision"], payload["expectedRevision"] + 1)
        self.assertIn(payload["stepId"], progress["lessons"][payload["lessonId"]]["completedSteps"])
        self.assertEqual(self.post(payload)[0], 409)
        payload["expectedRevision"] = progress["revision"]
        self.assertEqual(self.post(payload)[0], 400)
        backup = self.learning / ".history" / ("progress-r%06d.json" % (progress["revision"] - 1))
        self.assertTrue(backup.is_file())

    def reset_lesson_01(self, catalog_step_patch=None):
        """scratch 副本回到 01-01，讓測試不受真實進度推進影響。"""
        progress = json.loads((self.learning / "progress.json").read_text(encoding="utf-8"))
        progress["activeLesson"] = "01"
        progress["lessons"]["01"].update(status="in_progress", currentStep="01-01", completedSteps=[])
        progress["learner"]["interfaceLanguage"] = None
        (self.learning / "progress.json").write_text(json.dumps(progress, ensure_ascii=False), encoding="utf-8")
        if catalog_step_patch:
            catalog = json.loads((self.learning / "catalog.json").read_text(encoding="utf-8"))
            catalog["lessons"][0]["steps"][1].update(catalog_step_patch)
            (self.learning / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    def test_language_step_records_interface_language_on_confirm(self):
        self.reset_lesson_01()
        step = self.bootstrap()["catalog"]["lessons"][0]["steps"][1]
        self.assertEqual((step["id"], step["setsLearner"]), ("01-02", {"interfaceLanguage": "en"}))
        status, result, _ = self.post(self.confirm_payload())
        self.assertEqual(status, 200)
        self.assertIsNone(result["progress"]["learner"]["interfaceLanguage"])
        status, result, _ = self.post(dict(self.confirm_payload(), evidence="選單已顯示 File、Edit；左上是 Object Mode"))
        self.assertEqual(status, 200)
        progress = result["progress"]
        self.assertEqual(progress["learner"]["interfaceLanguage"], "en")
        self.assertEqual(progress["lessons"]["01"]["currentStep"], "01-03")
        self.assertEqual(progress["events"][-1]["learner"], {"interfaceLanguage": "en"})

    def test_catalog_cannot_set_unlisted_learner_values(self):
        self.reset_lesson_01({"setsLearner": {"interfaceLanguage": "fr"}})
        self.assertEqual(self.post(self.confirm_payload())[0], 200)
        payload = self.confirm_payload()
        self.assertEqual(self.post(payload)[0], 400)
        self.assertEqual(self.bootstrap()["progress"]["revision"], payload["expectedRevision"])

    def test_cli_corrects_interface_language_without_confirming(self):
        self.reset_lesson_01()
        initial = self.bootstrap()["progress"]
        command = [sys.executable, str(self.learning / "manage.py"), "set-interface-language",
                   "--revision", str(initial["revision"]), "--language", "zh-Hant", "--evidence", "學員改回繁體中文"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        progress = self.bootstrap()["progress"]
        self.assertEqual(progress["revision"], initial["revision"] + 1)
        self.assertEqual(progress["learner"]["interfaceLanguage"], "zh-Hant")
        self.assertEqual(progress["lessons"]["01"]["completedSteps"], [])
        self.assertEqual(progress["events"][-1]["type"], "learner_updated")
        command[4] = str(progress["revision"])
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.bootstrap()["progress"]["revision"], progress["revision"])
        result = subprocess.run(command[:6] + ["fr", "--evidence", "x"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)

    def test_missing_workspace_folder_does_not_break_bootstrap(self):
        shutil.rmtree(self.learning / "workspaces/02")
        data = self.bootstrap()
        self.assertIn("02", data["progress"]["lessons"])

    def test_cli_adds_new_catalog_lessons_without_touching_existing(self):
        catalog = json.loads((self.learning / "catalog.json").read_text(encoding="utf-8"))
        catalog["lessons"].append({"id": "99", "title": "測試單元", "steps": [{"id": "99-01", "title": "第一步"}]})
        (self.learning / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        before = self.bootstrap()["progress"]
        command = [sys.executable, str(self.learning / "manage.py"), "add-lessons",
                   "--revision", str(before["revision"]), "--reason", "測試：學員核准的新單元"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.bootstrap()["progress"]
        self.assertEqual(after["revision"], before["revision"] + 1)
        self.assertEqual(after["lessons"]["99"], {"status": "not_started", "currentStep": "99-01", "completedSteps": [],
                                                  "notes": [], "workspace": "learning/workspaces/99"})
        for lesson_id, state in before["lessons"].items():
            self.assertEqual(after["lessons"][lesson_id], state)
        self.assertEqual(after["activeLesson"], before["activeLesson"])
        self.assertTrue((self.learning / "workspaces/99").is_dir())
        self.assertEqual(after["events"][-1]["lessons"], ["99"])
        command[4] = str(after["revision"])
        self.assertEqual(subprocess.run(command, capture_output=True, text=True, encoding="utf-8").returncode, 0)
        self.assertEqual(self.bootstrap()["progress"]["revision"], after["revision"])
        catalog["lessons"].append({"id": "../x", "title": "壞 ID", "steps": [{"id": "x-01"}]})
        (self.learning / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(subprocess.run(command, capture_output=True, text=True, encoding="utf-8").returncode, 2)
        self.assertFalse((self.learning / "x").exists())

    def test_api_and_cli_share_notes_and_revision(self):
        initial = self.bootstrap()["progress"]
        note = {"action": "add_note", "lessonId": "01", "stepId": initial["lessons"]["01"]["currentStep"],
                "expectedRevision": initial["revision"], "noteKind": "stuck", "note": "找不到目前模式 <img onerror=alert(1)>",
                "author": "tutor"}
        status, result, _ = self.post(note)
        self.assertEqual(status, 200)
        progress = result["progress"]
        self.assertEqual(progress["lessons"]["01"]["notes"][:-1], initial["lessons"]["01"]["notes"])
        self.assertEqual(progress["lessons"]["01"]["notes"][-1]["noteKind"], "stuck")
        # 網頁送來的 author 不被採用：網頁筆記一律是學員寫的。
        self.assertEqual(progress["lessons"]["01"]["notes"][-1]["author"], "learner")
        self.assertEqual(progress["events"][-1]["author"], "learner")
        note_file = self.root / "cli-note.txt"
        note_file.write_text("CLI 已讀到網頁筆記", encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.learning / "manage.py"), "note", "--lesson", "01",
                                 "--revision", str(progress["revision"]), "--note-file", str(note_file)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        fresh = self.bootstrap()["progress"]
        self.assertEqual(fresh["revision"], initial["revision"] + 2)
        self.assertEqual(fresh["lessons"]["01"]["notes"][-1]["text"], "CLI 已讀到網頁筆記")
        self.assertEqual(fresh["lessons"]["01"]["notes"][-1]["author"], "tutor")
        self.assertEqual(fresh["lessons"]["01"]["completedSteps"], initial["lessons"]["01"]["completedSteps"])
        self.assertEqual(self.post(note)[0], 409)
        command = [sys.executable, str(self.learning / "manage.py"), "note", "--lesson", "01",
                   "--revision", str(fresh["revision"]), "--note-file", str(note_file)]
        result = subprocess.run(command + ["--author", "learner"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.bootstrap()["progress"]["lessons"]["01"]["notes"][-1]["author"], "learner")
        result = subprocess.run(command + ["--author", "someone"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)

    def test_server_log_keeps_failed_requests_only(self):
        for _ in range(3):
            self.bootstrap()
        self.assertEqual(self.request("GET", "/missing-page")[0], 404)
        log = (self.root / "server-error.log").read_text(encoding="utf-8", errors="replace")
        self.assertIn("GET /missing-page", log)
        self.assertIn('" 404 ', log)
        self.assertNotIn('" 200 ', log)

    def test_write_lock_waits_briefly_then_reports_busy(self):
        spec = importlib.util.spec_from_file_location("scratch_manage", self.learning / "manage.py")
        scratch_manage = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scratch_manage)
        held = threading.Event()

        def hold(seconds):
            with scratch_manage.progress_lock():
                held.set()
                time.sleep(seconds)

        def note(revision):
            return {"action": "add_note", "lessonId": "01", "expectedRevision": revision, "note": "鎖定測試"}

        revision = self.bootstrap()["progress"]["revision"]
        worker = threading.Thread(target=hold, args=(0.5,))
        worker.start()
        self.assertTrue(held.wait(2))
        started = time.monotonic()
        status, result, _ = self.post(note(revision))
        waited = time.monotonic() - started
        worker.join()
        self.assertEqual(status, 200, result)
        self.assertGreater(waited, 0.3)
        revision = result["progress"]["revision"]
        held.clear()
        worker = threading.Thread(target=hold, args=(4.5,))
        worker.start()
        self.assertTrue(held.wait(2))
        status, result, _ = self.request("POST", "/api/progress", note(revision), timeout=10)
        worker.join()
        self.assertEqual(status, 503)
        self.assertIn("本次未寫入", result["error"])
        self.assertEqual(self.bootstrap()["progress"]["revision"], revision)

    def test_register_file_links_hash_and_rejects_overwritten_checkpoint(self):
        path = "learning/workspaces/01/u01_test_v001.blend"
        scene = self.root / path
        scene.write_bytes(b"test scene; deliberately not claimed as valid Blender")
        revision = self.bootstrap()["progress"]["revision"]
        payload = {"lessonId": "01", "path": path, "role": "source_scene", "expectedRevision": revision}
        status, result, _ = self.post(payload, "/api/register-file")
        self.assertEqual(status, 200)
        registered = result["progress"]["fileVersions"][-1]
        self.assertEqual(registered["sha256"], hashlib.sha256(scene.read_bytes()).hexdigest())
        self.assertTrue(self.bootstrap()["files"][0]["registered"])
        render_path = "learning/workspaces/01/test.png"
        (self.root / render_path).write_bytes(b"test render bytes")
        render = {"lessonId": "01", "path": render_path, "role": "render", "source": path,
                  "expectedRevision": result["progress"]["revision"]}
        status, result, _ = self.post(render, "/api/register-file")
        self.assertEqual(status, 200)
        self.assertEqual(result["progress"]["fileVersions"][-1]["source"], {"path": path, "sha256": registered["sha256"]})
        payload["expectedRevision"] = result["progress"]["revision"]
        self.assertEqual(self.post(payload, "/api/register-file")[1]["progress"]["revision"], payload["expectedRevision"])
        scene.write_bytes(b"overwritten scene")
        self.assertEqual(self.post(payload, "/api/register-file")[0], 400)
        render["expectedRevision"] = payload["expectedRevision"]
        self.assertEqual(self.post(render, "/api/register-file")[0], 400)

    def test_file_registration_cannot_leave_lesson_workspace(self):
        revision = self.bootstrap()["progress"]["revision"]
        (self.learning / "workspaces/02/wrong.blend").write_bytes(b"wrong lesson")
        for path in ("../progress.json", "learning/progress.json", "learning/workspaces/02/wrong.blend", "C:/Windows/win.ini"):
            payload = {"lessonId": "01", "path": path, "role": "source_scene", "expectedRevision": revision}
            self.assertEqual(self.post(payload, "/api/register-file")[0], 400, path)

    def test_registration_rejects_unknown_role_and_changed_duplicate_association(self):
        first_path = "learning/workspaces/01/source_v001.blend"
        second_path = "learning/workspaces/01/source_v002.blend"
        for path in (first_path, second_path):
            (self.root / path).write_bytes(b"same source content, separate version path")
        initial = self.bootstrap()["progress"]["revision"]
        invalid = {"lessonId": "01", "path": first_path, "role": "arbitrary", "source": second_path,
                   "expectedRevision": initial}
        self.assertEqual(self.post(invalid, "/api/register-file")[0], 400)
        self.assertEqual(self.bootstrap()["progress"]["revision"], initial)
        revision = initial
        for path in (first_path, second_path):
            status, result, _ = self.post({"lessonId": "01", "path": path, "role": "source_scene",
                                          "expectedRevision": revision}, "/api/register-file")
            self.assertEqual(status, 200)
            revision = result["progress"]["revision"]
        render_path = "learning/workspaces/01/result.png"
        (self.root / render_path).write_bytes(b"render bytes")
        original = {"lessonId": "01", "path": render_path, "role": "render", "source": first_path,
                    "expectedRevision": revision}
        status, result, _ = self.post(original, "/api/register-file")
        self.assertEqual(status, 200)
        revision = result["progress"]["revision"]
        original["expectedRevision"] = revision
        for altered in (dict(original, role="export"), dict(original, source=second_path)):
            self.assertEqual(self.post(altered, "/api/register-file")[0], 400)
            self.assertEqual(self.bootstrap()["progress"]["revision"], revision)
        status, result, _ = self.post(original, "/api/register-file")
        self.assertEqual(status, 200)
        self.assertEqual(result["progress"]["revision"], revision)
        self.assertEqual(result["progress"]["fileVersions"][-1]["source"]["path"], first_path)

    def test_security_blocks_traversal_host_origin_and_content_type(self):
        for route in ("/files/learning/progress.json", "/files/learning/evidence/../progress.json",
                      "/files/learning/evidence/%2e%2e/progress.json", "/files/C:/Windows/win.ini",
                      "/files/learning/assets/old-diagram.svg",
                      "/read/learning/workspaces/01/test.md"):
            self.assertEqual(self.request("GET", route)[0], 403, route)
        self.assertEqual(self.request("GET", "/api/bootstrap", headers={"Host": "attacker.example"})[0], 403)
        payload = self.confirm_payload()
        self.assertEqual(self.request("POST", "/api/progress", payload, {"Origin": "https://attacker.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/progress", payload, {"Sec-Fetch-Site": "cross-site"})[0], 403)
        self.assertEqual(self.request("POST", "/api/progress", payload, {"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.request("POST", "/api/progress", raw=b"{")[0], 400)
        self.assertEqual(self.request("POST", "/api/progress", raw=b"x" * 65537)[0], 413)

    def test_authored_report_pages_use_separate_static_route(self):
        reports = self.learning / "web/reports"
        reports.mkdir()
        (reports / "audit-v001.html").write_text("<!doctype html><h1>Reviewed report</h1>", encoding="utf-8")
        (reports / "audit-v001.css").write_text("h1{color:navy}", encoding="utf-8")
        status, body, headers = self.request("GET", "/reports/audit-v001.html")
        self.assertEqual(status, 200)
        self.assertIn(b"Reviewed report", body)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        status, _, headers = self.request("GET", "/reports/audit-v001.css")
        self.assertEqual(status, 200)
        self.assertIn("text/css", headers["Content-Type"])
        (self.learning / "evidence/arbitrary.html").write_text("<script>alert(1)</script>", encoding="utf-8")
        self.assertEqual(self.request("GET", "/files/learning/evidence/arbitrary.html")[0], 403)

    def test_report_route_rejects_other_files_and_traversal(self):
        for route in ("/reports/../index.html", "/reports/%2e%2e/index.html", "/reports/nested/audit.html",
                      "/reports/audit.js", "/reports/audit.json", "/reports/C:/Windows/test.html"):
            self.assertEqual(self.request("GET", route)[0], 403, route)
        self.assertEqual(self.request("GET", "/reports/missing-v001.html")[0], 404)

    def test_read_and_files_are_safe_and_open_cannot_run_arbitrary_command(self):
        status, content, headers = self.request("GET", "/read/learning/journal/test.md")
        self.assertEqual(status, 200)
        self.assertIn("text/plain", headers["Content-Type"])
        self.assertIn(b"<script>", content)
        status, _, headers = self.request("GET", "/files/learning/evidence/help.svg")
        self.assertEqual(status, 200)
        self.assertIn("image/svg+xml", headers["Content-Type"])
        for payload in ({"lessonId": "01", "target": "cmd.exe"}, {"lessonId": "99", "target": "workspace"}):
            self.assertEqual(self.post(payload, "/api/open")[0], 400)


if __name__ == "__main__":
    unittest.main()
