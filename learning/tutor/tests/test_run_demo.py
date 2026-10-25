"""Runner 防護測試；Blender 使用替身，PowerShell 僅實測陣列枚舉，不修改最近項目。"""
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("run_demo", Path(__file__).resolve().parents[1] / "run_demo.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-runner-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.here = self.root / "tutor"
        (self.here / "scenarios").mkdir(parents=True)
        (self.here / "scenarios" / "lesson05.py").write_text("# test", encoding="utf-8")
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.workspaces = self.root / "workspaces"
        (self.workspaces / "05" / "exports").mkdir(parents=True)
        self.learner_file = self.workspaces / "05" / "exports" / "original.stl"
        self.learner_file.write_bytes(b"before")
        self.out = self.evidence / "05" / "new-run"
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in (("HERE", self.here), ("EVIDENCE", self.evidence), ("WORKSPACES", self.workspaces)):
            self.stack.enter_context(patch.object(runner, name, value))

    def test_scenario_name_must_exist_and_cannot_escape(self):
        self.assertEqual(runner.resolve_scenario("lesson05"), self.here / "scenarios" / "lesson05.py")
        for name in ("missing", "../lesson05", "lesson05.py", "a/b", "a\\b"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                runner.resolve_scenario(name)

    def test_output_boundary_and_nonempty_version(self):
        for path in (self.evidence, self.workspaces / "05", self.evidence / ".." / "elsewhere",
                     self.root / "evidence-other" / "run"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                runner.prepare_output(path)
        self.assertEqual(runner.prepare_output(self.out), self.out)
        self.assertEqual(runner.prepare_output(self.out), self.out)  # 空資料夾可用
        (self.out / "original.png").write_bytes(b"preserve")
        with self.assertRaises(ValueError):
            runner.prepare_output(self.out)
        self.assertEqual((self.out / "original.png").read_bytes(), b"preserve")

    def test_resolved_output_symlink_cannot_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.evidence / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("此 Windows 帳戶無建立 symlink 權限")
        with self.assertRaises(ValueError):
            runner.prepare_output(link / "run")

    def test_recursive_snapshot_detects_same_name_and_size_change(self):
        before = runner.workspace_snapshot(self.workspaces)
        self.learner_file.write_bytes(b"after!")  # 同大小、同路徑
        after = runner.workspace_snapshot(self.workspaces)
        self.assertEqual(before["05/exports/original.stl"]["size"], after["05/exports/original.stl"]["size"])
        self.assertNotEqual(before["05/exports/original.stl"]["sha256"], after["05/exports/original.stl"]["sha256"])
        self.assertEqual(before["05/exports"]["kind"], "directory")

    def test_run_requires_nonempty_records_without_errors(self):
        path = self.root / "run.json"
        with self.assertRaises(ValueError):
            runner.validate_run(path)
        for payload in ({}, {"records": []}, {"records": [{"error": "failed"}]},
                        {"records": ["bad"]}, [], {"records": "bad"}):
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                runner.validate_run(path)
        path.write_text('{"records":[{"step":"05-02"}]}', encoding="utf-8")
        self.assertEqual(len(runner.validate_run(path)["records"]), 1)

    def run_main(self, fake_process, cleanup_error=None):
        old_links = {"old.lnk"}
        with patch.object(runner.subprocess, "run", side_effect=fake_process) as process, \
             patch.object(runner, "recent_links", return_value=old_links), \
             patch.object(runner, "clean_windows_recent", side_effect=cleanup_error, return_value=[]) as cleanup, \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = runner.main(["lesson05", str(self.out)])
        status = json.loads((self.out / "runner-status.json").read_text(encoding="utf-8"))
        cleanup.assert_called_once()
        self.assertEqual(cleanup.call_args.args, (self.out, old_links))
        self.assertIn("beforeLinks", cleanup.call_args.kwargs["audit"])
        self.assertEqual(process.call_args.kwargs["timeout"], 600)
        return code, status

    def write_run(self, records):
        (self.out / "run.json").write_text(json.dumps({"records": records}), encoding="utf-8")

    def test_success_status_requires_run_and_workspace_evidence(self):
        def process(command, **kwargs):
            self.assertIn("--enable-event-simulate", command)
            self.assertNotEqual(kwargs["env"]["BLENDER_USER_CONFIG"], str(self.root))
            self.write_run([{"step": "05-02"}])
            return subprocess.CompletedProcess(command, 0)
        code, status = self.run_main(process)
        self.assertEqual(code, 0)
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["blenderExitCode"], 0)
        self.assertTrue(status["workspacesUnchanged"])
        self.assertEqual(status["workspacesBefore"], status["workspacesAfter"])
        self.assertEqual(status["runErrors"], [])
        self.assertEqual(status["recentCleanup"]["beforeLinks"][0]["path"], "old.lnk")
        self.assertIsNotNone(status["recentCleanup"]["beforeAt"])

    def test_zero_process_exit_with_script_error_still_fails(self):
        def process(command, **kwargs):
            self.write_run([{"error": "test error"}])
            return subprocess.CompletedProcess(command, 0)
        code, status = self.run_main(process)
        self.assertNotEqual(code, 0)
        self.assertEqual(status["status"], "failed")
        self.assertIn("test error", status["runErrors"][0])

    def test_zero_process_exit_with_missing_run_still_fails(self):
        code, status = self.run_main(lambda command, **kwargs: subprocess.CompletedProcess(command, 0))
        self.assertNotEqual(code, 0)
        self.assertEqual(status["status"], "failed")
        self.assertTrue(status["runErrors"])

    def test_workspace_change_fails_even_when_blender_succeeds(self):
        def process(command, **kwargs):
            self.write_run([{"step": "05-02"}])
            self.learner_file.write_bytes(b"after!")
            return subprocess.CompletedProcess(command, 0)
        code, status = self.run_main(process)
        self.assertNotEqual(code, 0)
        self.assertFalse(status["workspacesUnchanged"])
        self.assertEqual(status["workspaceChanges"], ["05/exports/original.stl"])

    def test_timeout_keeps_status_and_cleanup_failure_does_not_mask_it(self):
        def process(command, **kwargs):
            raise subprocess.TimeoutExpired(command, 600)
        code, status = self.run_main(process, cleanup_error=RuntimeError("cleanup unavailable"))
        self.assertEqual(code, 124)
        self.assertEqual(status["status"], "failed")
        self.assertTrue(status["workspacesUnchanged"])
        self.assertIn("600", status["runErrors"][0])
        self.assertEqual(status["recentCleanup"]["warnings"], ["cleanup unavailable"])

    @unittest.skipUnless(runner.os.name == "nt", "Windows 捷徑清理")
    def test_recent_cleanup_excludes_existing_links_and_scopes_target(self):
        with patch.object(runner, "recent_links", return_value={"old.lnk", "new.lnk"}), \
             patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as process:
            audit = {}
            runner.clean_windows_recent(self.out, {"old.lnk"}, audit=audit)
        call = process.call_args
        self.assertEqual(json.loads(call.kwargs["env"]["DEMO_RECENT_CANDIDATES"]), ["new.lnk"])
        self.assertEqual(call.kwargs["env"]["DEMO_OUT_ROOT"], str(self.out))
        script = call.args[0][-1]
        self.assertIn("$target.StartsWith($demoRoot", script)
        self.assertIn("Remove-Item -LiteralPath $link", script)
        self.assertIn("foreach ($candidate in (ConvertFrom-Json -InputObject", script)
        self.assertNotIn("GetFullPath([string]$_)", script)
        self.assertNotIn(str(self.evidence), script)
        self.assertEqual([item["path"] for item in audit["candidates"]], ["new.lnk"])

    @unittest.skipUnless(runner.os.name == "nt", "Windows PowerShell 5 陣列枚舉")
    def test_real_powershell_enumerates_two_candidates_without_touching_files(self):
        paths = [str(self.root / "first file.lnk"), str(self.root / "second.lnk")]
        # 僅執行與清理器相同的陣列迴圈及 GetFullPath；沒有 COM、Test-Path 或 Remove-Item。
        script = "$ErrorActionPreference='Stop'; " + runner.recent_candidates_loop("Write-Output $link;")
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script],
                                capture_output=True, text=True,
                                env=dict(os.environ, DEMO_RECENT_CANDIDATES=json.dumps(paths)),
                                timeout=15, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), paths)
        self.assertFalse(any(Path(path).exists() for path in paths))


if __name__ == "__main__":
    unittest.main()
