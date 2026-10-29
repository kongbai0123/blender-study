"""公開衍生摘要跨版本保真；只用臨時假資料，不讀私人 Recent 清單。"""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("publication_under_test", ROOT / "scripts/prepare_publication.py")
PUBLICATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PUBLICATION)


class PublicationSemanticsTests(unittest.TestCase):
    def test_prior_derivative_bytes_survive_new_date_and_changed_input_gets_new_version(self):
        with tempfile.TemporaryDirectory(prefix="publication-semantics-") as directory:
            root = Path(directory).resolve()
            relative = "learning/evidence/05/sample/runner-status.json"
            raw = root / relative
            raw.parent.mkdir(parents=True)
            value = {"workspacesUnchanged": True, "recentCleanup": {"beforeLinks": ["fixture-only.lnk"]}}
            raw.write_text(json.dumps(value), encoding="utf-8")
            first = PUBLICATION.Publication(root).derivative(relative)
            path = root / first
            previous = json.loads(path.read_text(encoding="utf-8"))
            previous["preparedOn"] = "2026-10-26"
            path.write_text(json.dumps(previous, indent=4) + "\n", encoding="utf-8")
            before, mtime = path.read_bytes(), path.stat().st_mtime_ns
            self.assertEqual(PUBLICATION.Publication(root).derivative(relative), first)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (before, mtime))
            value["workspacesUnchanged"] = False
            raw.write_text(json.dumps(value), encoding="utf-8")
            second = PUBLICATION.Publication(root).derivative(relative)
            self.assertNotEqual(second, first)
            self.assertTrue(second.endswith("v002.json"))
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), (before, mtime))
            current = json.loads((root / second).read_text(encoding="utf-8"))
            self.assertNotIn("recentCleanup", current["content"])
            self.assertIs(current["content"]["workspacesUnchanged"], False)
            self.assertEqual(PUBLICATION.Publication(root).derivative(relative), second)

    def test_private_publication_baseline_is_excluded_even_if_referenced(self):
        with tempfile.TemporaryDirectory(prefix="publication-private-") as directory:
            root = Path(directory).resolve()
            publication = PUBLICATION.Publication(root)
            relative = "learning/.publication-private/local-check.json"
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_text('{"private":"fixture"}', encoding="utf-8")
            publication.add(relative, "accidental document reference")
            self.assertNotIn(relative, publication.selected)
            self.assertIn(relative, publication.omissions)

    def test_archived_omission_inventory_is_not_a_dependency_root_and_scratch_is_not_probed(self):
        with tempfile.TemporaryDirectory(prefix="publication-inventory-") as directory:
            root = Path(directory).resolve()
            (root / "learning/evidence/ui").mkdir(parents=True)
            (root / "docs").mkdir()
            (root / "learning/catalog.json").write_text('{"lessons":[]}', encoding="utf-8")
            omitted = "learning/evidence/ui/unpublished.txt"
            (root / omitted).write_text("local fixture", encoding="utf-8")
            (root / "docs/publication-manifest-2026-10-26.json").write_text(json.dumps({"omitted": [omitted]}), encoding="utf-8")
            inaccessible = "learning/tests/.scratch/no-access/private.json"
            (root / "README.md").write_text(inaccessible, encoding="utf-8")
            real_is_dir = Path.is_dir
            def guarded_is_dir(path):
                if path == root / inaccessible:
                    raise PermissionError("excluded fixture must not be statted")
                return real_is_dir(path)
            publication = PUBLICATION.Publication(root)
            with patch.object(Path, "is_dir", guarded_is_dir), contextlib.redirect_stdout(io.StringIO()):
                publication.build()
            self.assertNotIn(omitted, publication.selected)
            self.assertNotIn(inaccessible, publication.selected)
            self.assertIn(inaccessible, publication.omissions)



    def test_runner_workspace_snapshots_are_not_public_derivatives(self):
        with tempfile.TemporaryDirectory(prefix="publication-snapshots-") as directory:
            root = Path(directory).resolve()
            relative = "learning/evidence/05/sample/runner-status.json"
            raw = root / relative
            raw.parent.mkdir(parents=True)
            raw.write_text(json.dumps({"workspacesBefore": {"private-fixture.blend": {"sha256": "fixture"}},
                                       "recentCleanup": {"beforeLinks": []}}), encoding="utf-8")
            before = raw.read_bytes()
            publication = PUBLICATION.Publication(root)
            publication.add(relative, "fixture")
            self.assertIsNone(publication.derivative(relative))
            self.assertNotIn(relative, publication.selected)
            self.assertEqual(raw.read_bytes(), before)

    def test_current_engineering_references_do_not_bulk_publish_new_runs(self):
        with tempfile.TemporaryDirectory(prefix="publication-current-") as directory:
            root = Path(directory).resolve()
            (root / "learning/web").mkdir(parents=True)
            (root / "learning/evidence/parametric/demo").mkdir(parents=True)
            (root / "learning/catalog.json").write_text('{"lessons":[]}', encoding="utf-8")
            (root / "learning/manage.py").write_text(
                'ENGINEERING_CURRICULUM = LEARNING / "web" / "c.json"\n'
                'ENGINEERING_PATH = LEARNING / "web" / "p.json"\n'
                'CHALLENGES = LEARNING / "web" / "q.json"\n', encoding="utf-8")
            used = "learning/evidence/parametric/demo/used.png"
            unused = "learning/evidence/parametric/demo/unpublished.png"
            (root / used).write_bytes(b"policy-fixture")
            (root / unused).write_bytes(b"unpublished-fixture")
            for name, value in [("c", {"path": used}), ("p", {}), ("q", {})]:
                (root / ("learning/web/" + name + ".json")).write_text(json.dumps(value), encoding="utf-8")
            publication = PUBLICATION.Publication(root)
            with contextlib.redirect_stdout(io.StringIO()):
                publication.build()
            self.assertIn(used, publication.selected)
            self.assertNotIn(unused, publication.selected)

    def test_summary_paths_can_be_relative_to_evidence_parent(self):
        with tempfile.TemporaryDirectory(prefix="publication-relative-") as directory:
            root = Path(directory).resolve()
            base = root / "learning/evidence/parametric"
            (base / "run-a").mkdir(parents=True)
            (base / "run-b").mkdir()
            (base / "run-b/image.png").write_bytes(b"policy-fixture")
            summary = base / "run-a/summary.json"
            summary.write_text('{"images":[{"file":"run-b/image.png"}]}', encoding="utf-8")
            publication = PUBLICATION.Publication(root)
            self.assertIn("learning/evidence/parametric/run-b/image.png",
                          publication.references(summary.relative_to(root).as_posix()))

    def test_only_empty_generated_course_directories_are_public_scaffolding(self):
        self.assertFalse(PUBLICATION.has_workspace_snapshot({"workspacesBefore": {
            ".": {"kind": "directory"}, "01": {"kind": "directory"}}}))
        self.assertTrue(PUBLICATION.has_workspace_snapshot({"workspacesBefore": {
            "01/own.blend": {"kind": "file", "sha256": "fixture"}}}))
        self.assertTrue(PUBLICATION.has_workspace_snapshot({"workspacesBefore": {
            "private-custom-directory": {"kind": "directory"}}}))


if __name__ == "__main__":
    unittest.main()
