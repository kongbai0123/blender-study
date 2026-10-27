"""Catalog-only editorial updates preserve frozen evidence and reject stale bindings."""
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
SPEC = importlib.util.spec_from_file_location("catalog_semantics_updater", ROOT / "scripts/apply_evidence_semantics.py")
UPDATER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATER)
RUN_ID = "isolated-reviewed-run-v001"
OLD_SUMMARY = "助教已在獨立 Blender 逐一實際操作並截圖，結果數值由 Blender 讀回；這是示範，不代表你已完成。"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def snapshot(project):
    return {p.relative_to(project).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in project.rglob("*") if p.is_file()}


class CatalogSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blender-catalog-semantics-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def fixture(self, name="project"):
        project = self.base / name
        image_path = "learning/evidence/05/reviewed/after.png"
        source_path = "learning/tutor/scenarios/isolated.py"
        for relative, data in {
            image_path: b"isolated image binding, no Blender replay",
            "learning/evidence/05/reviewed/manual.png": b"legacy manual capture",
            source_path: b'observed = "Menu opened; count=1"\n',
            "learning/evidence/05/reviewed/run.json": b'{"historical":"run bytes stay frozen"}',
            "learning/evidence/05/reviewed/metadata.json": b'{"learnerWorkspaceWrites":false,"original":"metadata"}',
            "learning/evidence/05/reviewed/runner-status.json": b'{"workspacesUnchanged":true,"private":"keep local"}',
            "learning/evidence/05/reviewed/demo-files/part.blend": b"isolated frozen scene",
            "learning/evidence/05/reviewed/demo-files/part.stl": b"isolated frozen STL",
            "learning/progress.json": b'{"revision":6,"completedSteps":[]}',
        }.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        entry = {
            "runId": RUN_ID, "step": "05-02", "imagePath": image_path,
            "sha256": digest((project / image_path).read_bytes()),
            "observedSha256": digest(b"Menu opened; count=1"),
            "observedKind": "mixed", "reason": "Explicit source expression contains description and value",
            "source": {"path": source_path, "line": 1, "sha256": digest((project / source_path).read_bytes())},
        }
        write_json(project / UPDATER.IMPORTER.OBSERVED_ANNOTATIONS, {"schemaVersion": 1, "entries": [entry]})
        original_path = "learning/evidence/05/reviewed/runner-status.json"
        public_path = "learning/evidence/public-metadata/runner-public-v001.json"
        original_hash = digest((project / original_path).read_bytes())
        write_json(project / public_path, {
            "kind": "redacted_public_derivative", "originalPath": original_path,
            "originalSha256": original_hash, "content": {"workspacesUnchanged": True},
        })
        write_json(project / UPDATER.WORKSPACES, {"schemaVersion": 1, "runs": [{
            "runId": RUN_ID, "workspaceContentsUnchanged": True, "learnerWorkspaceWrites": None,
            "workspaceEvidenceNote": UPDATER.IMPORTER.WORKSPACE_NOTE,
            "runnerEvidence": {"path": public_path, "sha256": digest((project / public_path).read_bytes()),
                               "originalPath": original_path, "originalSha256": original_hash},
        }]})
        catalog = {"title": "Isolated catalog", "contentPolicy": {"preserve": "existing policy"}, "lessons": [{
            "id": "05", "steps": [{"id": "05-02", "title": "Existing lesson", "guide": [{"action": "Keep guide"}],
                "contentReview": {"summary": OLD_SUMMARY, "references": ["unchanged-reference"]},
                "operationRun": {"id": RUN_ID, "performedBy": "tutor", "learnerWorkspaceWrites": False,
                    "outputFiles": [{"path": "learning/evidence/05/reviewed/demo-files/part.stl", "sha256": "old-source-bound-hash", "dimensionsMm": [10, 10, 8]}],
                    "events": [
                        {"seq": 1, "action": "Open menu", "observed": "Menu opened; count=1", "note": "Keep original note",
                         "figure": {"path": image_path, "sha256": entry["sha256"], "type": "screenshot", "caption": "Original caption"}},
                        {"seq": 2, "action": "Manual capture", "observed": "Do not infer a reading",
                         "figure": {"path": "learning/evidence/05/reviewed/manual.png", "type": "screenshot", "caption": "Legacy no hash"}},
                    ]}}]}]}
        write_json(project / "learning/catalog.json", catalog)
        return project, catalog

    def test_annotation_is_a_narrow_nonmutating_editorial_layer(self):
        project, catalog = self.fixture()
        original = copy.deepcopy(catalog)
        before = snapshot(project)
        result, report = UPDATER.annotate(catalog, project)
        self.assertEqual(catalog, original)
        self.assertEqual(snapshot(project), before)
        old_step = original["lessons"][0]["steps"][0]
        new_step = result["lessons"][0]["steps"][0]
        self.assertEqual(new_step["guide"], old_step["guide"])
        self.assertEqual(new_step["contentReview"]["references"], old_step["contentReview"]["references"])
        self.assertNotEqual(new_step["contentReview"]["summary"], OLD_SUMMARY)
        old_run, new_run = old_step["operationRun"], new_step["operationRun"]
        self.assertEqual(new_run["outputFiles"], old_run["outputFiles"])
        for old, new in zip(old_run["events"], new_run["events"]):
            for key, value in old.items():
                self.assertEqual(new[key], value, key)
        self.assertEqual(new_run["events"][0]["observedKind"], "mixed")
        self.assertIsNone(new_run["learnerWorkspaceWrites"])
        self.assertIs(new_run["workspaceContentsUnchanged"], True)
        self.assertEqual(result["contentPolicy"]["preserve"], "existing policy")
        self.assertEqual(report["matchedAnnotations"], 1)
        self.assertFalse(report["originalEvidenceWritten"])
        self.assertFalse(report["learnerProgressWritten"])

    def test_update_requires_explicit_write_then_verifies_idempotently_without_touching_evidence(self):
        project, _ = self.fixture()
        before = snapshot(project)
        with self.assertRaisesRegex(ValueError, "只有 --write"):
            UPDATER.update(project)
        self.assertEqual(snapshot(project), before)
        UPDATER.update(project, write=True)
        after = snapshot(project)
        for path, original in before.items():
            if path != "learning/catalog.json":
                self.assertEqual(after[path], original, path)
        with patch.object(UPDATER.IMPORTER, "_atomic_json", side_effect=AssertionError("idempotence must not write")):
            verified = UPDATER.update(project)
            UPDATER.update(project, write=True)
        self.assertEqual(snapshot(project), after)
        self.assertEqual(verified["catalogSha256"], digest(after["learning/catalog.json"][0]))

    def test_tampered_image_source_observed_and_workspace_proof_fail_before_write(self):
        for case in ("image", "source", "observed", "workspace"):
            with self.subTest(case=case):
                project, catalog = self.fixture(case)
                if case == "image":
                    (project / "learning/evidence/05/reviewed/after.png").write_bytes(b"tampered image")
                elif case == "source":
                    (project / "learning/tutor/scenarios/isolated.py").write_text("changed source\n", encoding="utf-8")
                elif case == "observed":
                    catalog["lessons"][0]["steps"][0]["operationRun"]["events"][0]["observed"] = "Altered after review"
                    write_json(project / "learning/catalog.json", catalog)
                else:
                    write_json(project / "learning/evidence/public-metadata/runner-public-v001.json", {"content": {"workspacesUnchanged": False}})
                before = snapshot(project)
                with self.assertRaises(ValueError):
                    UPDATER.update(project, write=True)
                self.assertEqual(snapshot(project), before)

    def test_extra_observation_or_workspace_annotations_are_rejected_without_writes(self):
        for case in ("extra-observation", "extra-workspace"):
            with self.subTest(case=case):
                project, _ = self.fixture(case)
                relative = UPDATER.IMPORTER.OBSERVED_ANNOTATIONS if case == "extra-observation" else UPDATER.WORKSPACES
                path = project / relative
                data = json.loads(path.read_text(encoding="utf-8"))
                key = "entries" if case == "extra-observation" else "runs"
                extra = copy.deepcopy(data[key][0])
                extra["runId"] = "run-not-in-catalog"
                data[key].append(extra)
                write_json(path, data)
                before = snapshot(project)
                with self.assertRaisesRegex(ValueError, "不在 catalog|未匹配到 catalog"):
                    UPDATER.update(project, write=True)
                self.assertEqual(snapshot(project), before)

    def test_legacy_manual_figure_remains_unclassified_without_hash_or_metadata_backfill(self):
        project, original = self.fixture()
        metadata_path = project / "learning/evidence/05/reviewed/metadata.json"
        frozen_metadata = metadata_path.read_bytes()
        UPDATER.update(project, write=True)
        catalog = json.loads((project / "learning/catalog.json").read_text(encoding="utf-8"))
        event = catalog["lessons"][0]["steps"][0]["operationRun"]["events"][1]
        old = original["lessons"][0]["steps"][0]["operationRun"]["events"][1]
        self.assertEqual(event, {**old, "observedKind": "unclassified"})
        self.assertNotIn("sha256", event["figure"])
        self.assertNotIn("observedSource", event)
        self.assertEqual(metadata_path.read_bytes(), frozen_metadata)
        _, report = UPDATER.annotate(catalog, project)
        self.assertEqual(report["historicalFiguresWithoutDeclaredHash"], 1)
        # A later review may withdraw a classification; its old source must not
        # remain attached to an event that is now explicitly unclassified.
        annotations = project / UPDATER.IMPORTER.OBSERVED_ANNOTATIONS
        write_json(annotations, {"schemaVersion": 1, "entries": []})
        before = snapshot(project)
        UPDATER.update(project, write=True)
        revised = json.loads((project / "learning/catalog.json").read_text(encoding="utf-8"))
        formerly_classified = revised["lessons"][0]["steps"][0]["operationRun"]["events"][0]
        self.assertEqual(formerly_classified["observedKind"], "unclassified")
        self.assertNotIn("observedSource", formerly_classified)
        self.assertNotIn("observedReason", formerly_classified)
        self.assertNotIn("observedAnnotation", formerly_classified)
        for key, value in original["lessons"][0]["steps"][0]["operationRun"]["events"][0].items():
            self.assertEqual(formerly_classified[key], value, key)
        after = snapshot(project)
        for path in before:
            if path != "learning/catalog.json":
                self.assertEqual(after[path], before[path], path)


if __name__ == "__main__":
    unittest.main()
