"""Shortcut sidecars bind unchanged guides and verified contained evidence only."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("guide_shortcuts_updater", ROOT / "scripts/apply_guide_shortcuts.py")
UPDATER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATER)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


class GuideShortcutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="blender-guide-shortcuts-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()

    def fixture(self, suffix="project"):
        root = self.base / suffix
        source = "learning/annotations/shortcut-source-v001.json"
        image = "learning/evidence/01/reviewed/file-menu.png"
        files = {
            source: b'{"method":"visual reading"}', image: b"isolated original image bytes",
            "learning/evidence/01/reviewed/run.json": b'{"frozen":"run"}',
            "learning/evidence/01/reviewed/metadata.json": b'{"frozen":"metadata"}',
            "learning/evidence/01/reviewed/demo-files/part.blend": b"frozen scene",
            "learning/evidence/01/reviewed/demo-files/part.stl": b"frozen STL",
            "learning/progress.json": b'{"revision":6,"completedSteps":[]}',
        }
        for relative, payload in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        guides = [{"mark": "1", "where": "File > Save", "do": "Save current working version", "see": "Saved"},
                  {"mark": "2", "where": "Journal", "do": "Record real evidence", "see": "Recorded"}]
        catalog = {"title": "Isolated catalog", "contentPolicy": {"keep": "policy"}, "lessons": [
            {"id": "01", "steps": [{"id": "01-09", "guide": guides,
                "operationRun": {"id": "frozen-run", "events": [{"observed": "Original text"}]},
                "previousOperationRuns": [{"id": "older-frozen-run"}]}]}]}
        shortcut = {"keys": "Ctrl+S", "effect": "Save", "requirements": ["Correct working version"],
                    "cautions": ["Do not overwrite a registered checkpoint"], "evidence": [
                        {"path": image, "sha256": digest(files[image]),
                         "method": "menu_label_visual", "label": "File > Save: Ctrl S"}]}
        annotation = {"schemaVersion": 1, "sourceDocuments": [{"path": source, "sha256": digest(files[source])}],
            "entries": [{"step": "01-09", "guideIndex": 0,
                         "guideSha256": UPDATER.guide_digest(guides[0]), "shortcut": shortcut}],
            "coverage": [{"step": "01-09", "guideIndex": index,
                          "guideSha256": UPDATER.guide_digest(guide),
                          "status": "added" if index == 0 else "omitted",
                          "reason": "Verified menu label" if index == 0 else "No equivalent Blender action"}
                         for index, guide in enumerate(guides)]}
        write_json(root / "learning/catalog.json", catalog)
        write_json(root / UPDATER.ANNOTATIONS, annotation)
        return root, catalog, annotation

    def assert_rejected_without_writes(self, root):
        before = snapshot(root)
        with self.assertRaises(ValueError):
            UPDATER.update(root, write=True)
        self.assertEqual(snapshot(root), before)

    def test_annotate_only_changes_shortcut_without_mutating_input_or_files(self):
        root, catalog, annotation = self.fixture()
        original, before = copy.deepcopy(catalog), snapshot(root)
        result, report = UPDATER.annotate(catalog, root)
        self.assertEqual(catalog, original)
        self.assertEqual(snapshot(root), before)
        self.assertEqual(result["lessons"][0]["steps"][0]["guide"][0]["shortcut"], annotation["entries"][0]["shortcut"])
        result["lessons"][0]["steps"][0]["guide"][0].pop("shortcut")
        self.assertEqual(result, original)
        self.assertEqual((report["guides"], report["added"], report["omitted"]), (2, 1, 1))
        self.assertFalse(report["originalEvidenceWritten"])
        self.assertFalse(report["learnerProgressWritten"])
        self.assertFalse(report["operationRunsWritten"])

    def test_write_is_explicit_then_verification_and_reapply_are_read_only(self):
        root, _, _ = self.fixture()
        before = snapshot(root)
        with self.assertRaisesRegex(ValueError, "只有 --write"):
            UPDATER.update(root)
        self.assertEqual(snapshot(root), before)
        UPDATER.update(root, write=True)
        after = snapshot(root)
        for relative, original in before.items():
            if relative != "learning/catalog.json":
                self.assertEqual(after[relative], original)
        with patch.object(UPDATER, "_atomic_json", side_effect=AssertionError("must not write")):
            report = UPDATER.update(root)
            UPDATER.update(root, write=True)
        self.assertEqual(snapshot(root), after)
        self.assertEqual(report["catalogSha256"], digest(after["learning/catalog.json"][0]))

    def test_shortcut_can_update_without_changing_conventional_guide(self):
        root, catalog, annotation = self.fixture()
        UPDATER.update(root, write=True)
        annotation["entries"][0]["shortcut"]["cautions"].append("Additional reviewed caution")
        write_json(root / UPDATER.ANNOTATIONS, annotation)
        UPDATER.update(root, write=True)
        actual = json.loads((root / "learning/catalog.json").read_text(encoding="utf-8"))
        guide = actual["lessons"][0]["steps"][0]["guide"][0]
        self.assertEqual(guide.pop("shortcut"), annotation["entries"][0]["shortcut"])
        self.assertEqual(actual, catalog)

    def test_current_sidecar_is_v002_and_never_falls_back_to_historical_v001(self):
        root, _, annotation = self.fixture()
        self.assertEqual(UPDATER.ANNOTATIONS, "learning/annotations/guide-shortcuts-v002.json")
        historical = root / "learning/annotations/guide-shortcuts-v001.json"
        write_json(historical, annotation)
        historical_bytes = historical.read_bytes()
        annotation["entries"][0]["shortcut"]["evidence"][0]["sha256"] = "0" * 64
        write_json(root / UPDATER.ANNOTATIONS, annotation)
        self.assert_rejected_without_writes(root)
        self.assertEqual(historical.read_bytes(), historical_bytes)

    def test_tampered_guide_source_or_image_fails_before_write(self):
        for target in ("guide", "source", "image"):
            with self.subTest(target=target):
                root, catalog, _ = self.fixture(target)
                if target == "guide":
                    catalog["lessons"][0]["steps"][0]["guide"][0]["do"] = "Changed after review"
                    write_json(root / "learning/catalog.json", catalog)
                else:
                    relative = ("learning/annotations/shortcut-source-v001.json" if target == "source"
                                else "learning/evidence/01/reviewed/file-menu.png")
                    (root / relative).write_bytes(b"changed after review")
                self.assert_rejected_without_writes(root)

    def test_coverage_missing_duplicate_extra_or_inconsistent_is_rejected(self):
        for kind in ("missing", "duplicate", "extra", "status", "reason", "stale", "entry-missing", "entry-extra"):
            with self.subTest(kind=kind):
                root, _, annotation = self.fixture(kind)
                if kind == "missing":
                    annotation["coverage"].pop()
                elif kind == "duplicate":
                    annotation["coverage"].append(copy.deepcopy(annotation["coverage"][0]))
                elif kind == "extra":
                    extra = copy.deepcopy(annotation["coverage"][0]); extra["step"] = "99-99"
                    annotation["coverage"].append(extra)
                elif kind == "status":
                    annotation["coverage"][0]["status"] = "unknown"
                elif kind == "reason":
                    annotation["coverage"][1]["reason"] = " "
                elif kind == "stale":
                    annotation["coverage"][1]["guideSha256"] = "0" * 64
                elif kind == "entry-missing":
                    annotation["entries"] = []
                else:
                    extra = copy.deepcopy(annotation["entries"][0]); extra["guideIndex"] = 1
                    extra["guideSha256"] = annotation["coverage"][1]["guideSha256"]
                    annotation["entries"].append(extra)
                write_json(root / UPDATER.ANNOTATIONS, annotation)
                self.assert_rejected_without_writes(root)

    def test_omitted_existing_shortcut_is_not_silently_removed(self):
        root, catalog, _ = self.fixture()
        catalog["lessons"][0]["steps"][0]["guide"][1]["shortcut"] = {"keys": "unreviewed"}
        write_json(root / "learning/catalog.json", catalog)
        self.assert_rejected_without_writes(root)

    def test_evidence_paths_extensions_and_hashes_are_strict(self):
        bad_paths = ["../outside.png", "learning/evidence/../annotations/shortcut-source-v001.json",
                     "C:/outside.png", "/outside.png", "learning\\evidence\\file.png",
                     "learning/evidence//file.png", "learning/evidence/./file.png",
                     "learning/annotations/shortcut-source-v001.json", "learning/evidence/model.blend"]
        for index, relative in enumerate(bad_paths):
            with self.subTest(relative=relative):
                root, _, annotation = self.fixture("path-" + str(index))
                annotation["entries"][0]["shortcut"]["evidence"][0]["path"] = relative
                write_json(root / UPDATER.ANNOTATIONS, annotation)
                self.assert_rejected_without_writes(root)
        for index, value in enumerate((None, "", "0" * 63, "g" * 64, "0" * 64)):
            with self.subTest(hash=value):
                root, _, annotation = self.fixture("hash-" + str(index))
                annotation["entries"][0]["shortcut"]["evidence"][0]["sha256"] = value
                write_json(root / UPDATER.ANNOTATIONS, annotation)
                self.assert_rejected_without_writes(root)

    def test_json_evidence_is_accepted_but_source_documents_cannot_escape(self):
        root, _, annotation = self.fixture()
        proof = annotation["entries"][0]["shortcut"]["evidence"][0]
        proof["path"] = "learning/evidence/01/reviewed/verification.json"
        (root / proof["path"]).write_bytes(b'{"readback":true}')
        proof["sha256"] = digest((root / proof["path"]).read_bytes())
        write_json(root / UPDATER.ANNOTATIONS, annotation)
        UPDATER.update(root, write=True)
        annotation["sourceDocuments"][0]["path"] = "learning/progress.json"
        write_json(root / UPDATER.ANNOTATIONS, annotation)
        self.assert_rejected_without_writes(root)

    def test_symlink_or_reparse_component_is_rejected_even_if_target_is_contained(self):
        root, _, _ = self.fixture()
        actual = UPDATER._link_or_reparse
        def simulated_reparse(path):
            return path.name == "reviewed" or actual(path)
        with patch.object(UPDATER, "_link_or_reparse", side_effect=simulated_reparse):
            self.assert_rejected_without_writes(root)

    def test_catalog_and_annotation_paths_also_reject_links(self):
        for filename in ("catalog.json", Path(UPDATER.ANNOTATIONS).name):
            with self.subTest(filename=filename):
                root, _, _ = self.fixture(filename)
                actual = UPDATER._link_or_reparse
                def simulated_reparse(path):
                    return path.name == filename or actual(path)
                with patch.object(UPDATER, "_link_or_reparse", side_effect=simulated_reparse):
                    self.assert_rejected_without_writes(root)

    def test_shortcut_schema_and_duplicate_entries_are_rejected(self):
        for kind in ("empty-keys", "empty-effect", "requirements", "cautions", "evidence", "method", "label", "duplicate", "bool-index"):
            with self.subTest(kind=kind):
                root, _, annotation = self.fixture(kind)
                shortcut = annotation["entries"][0]["shortcut"]
                if kind.startswith("empty-"):
                    shortcut[kind.removeprefix("empty-")] = ""
                elif kind in ("requirements", "cautions"):
                    shortcut[kind] = "not an array"
                elif kind == "evidence":
                    shortcut["evidence"] = []
                elif kind in ("method", "label"):
                    shortcut["evidence"][0][kind] = ""
                elif kind == "duplicate":
                    annotation["entries"].append(copy.deepcopy(annotation["entries"][0]))
                else:
                    annotation["entries"][0]["guideIndex"] = False
                write_json(root / UPDATER.ANNOTATIONS, annotation)
                self.assert_rejected_without_writes(root)

    def test_concurrent_catalog_change_is_preserved(self):
        root, catalog, _ = self.fixture()
        actual = UPDATER.annotate
        def change_after_validation(*args, **kwargs):
            result = actual(*args, **kwargs)
            changed = copy.deepcopy(catalog); changed["title"] = "Other editor's change"
            write_json(root / "learning/catalog.json", changed)
            return result
        with patch.object(UPDATER, "annotate", side_effect=change_after_validation):
            with self.assertRaisesRegex(ValueError, "catalog 已變更"):
                UPDATER.update(root, write=True)
        self.assertEqual(json.loads((root / "learning/catalog.json").read_text(encoding="utf-8"))["title"], "Other editor's change")

    def test_last_moment_byte_check_preserves_other_editor_and_removes_temporary_file(self):
        root, _, _ = self.fixture()
        path = root / "learning/catalog.json"
        before = path.read_bytes()
        path.write_bytes(b'{"other":"editor"}')
        with self.assertRaisesRegex(ValueError, "catalog 已變更"):
            UPDATER._atomic_json(path, {"must": "not replace"}, before, root)
        self.assertEqual(path.read_bytes(), b'{"other":"editor"}')
        self.assertEqual(list(path.parent.glob("catalog.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
