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


if __name__ == "__main__":
    unittest.main()
