"""分類綁定與工作區語義；以隔離 run 驗證，不執行 Blender 或更動作者進度。"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("semantics_fixtures", Path(__file__).with_name("test_import_run.py"))
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)
IMPORTER = FIXTURES.IMPORTER


class EvidenceSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.fixture = FIXTURES.ImportRunTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.project = self.fixture.project
        self.path = self.project / IMPORTER.OBSERVED_ANNOTATIONS
        self.source = self.project / "learning/tutor/scenarios/source.py"
        self.source.parent.mkdir(parents=True)
        self.source.write_text('observed = "static description"\n', encoding="utf-8")
        record = self.fixture.run["records"][0]
        self.entry = {"runId": FIXTURES.RUN_ID, "step": record["step"],
            "imagePath": self.fixture.image_path.relative_to(self.project).as_posix(),
            "sha256": record["sha256"],
            "observedSha256": hashlib.sha256(record["observed"].encode("utf-8")).hexdigest(),
            "observedKind": "scripted_description", "reason": "fixture explicit source classification",
            "source": {"path": self.source.relative_to(self.project).as_posix(), "line": 1,
                       "sha256": IMPORTER._digest(self.source)}}

    def write_annotations(self, entries=None):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"schemaVersion": 1, "entries": entries or [self.entry]}), encoding="utf-8")

    def test_missing_annotations_do_not_guess_and_snapshot_equality_never_proves_no_writes(self):
        IMPORTER.import_run(FIXTURES.RUN_ID, self.project)
        metadata = json.loads(self.fixture.metadata_path.read_text(encoding="utf-8"))
        self.assertIs(metadata["workspaceContentsUnchanged"], True)
        self.assertIsNone(metadata["learnerWorkspaceWrites"])
        self.assertEqual(metadata["records"][0]["observedKind"], "unclassified")
        self.assertIn("不能判定寫入者", metadata["workspaceEvidenceNote"])

    def test_bound_annotation_reaches_both_catalog_event_and_new_metadata(self):
        self.write_annotations()
        IMPORTER.import_run(FIXTURES.RUN_ID, self.project)
        catalog = json.loads(self.fixture.catalog_path.read_text(encoding="utf-8"))
        run = catalog["lessons"][0]["steps"][0]["operationRun"]
        event = run["events"][0]
        self.assertEqual(event["observedKind"], "scripted_description")
        self.assertEqual(event["observedSource"], self.entry["source"])
        self.assertEqual(event["observedAnnotation"]["sha256"], IMPORTER._digest(self.path))
        self.assertIsNone(run["learnerWorkspaceWrites"])
        self.assertIs(run["workspaceContentsUnchanged"], True)
        metadata = json.loads(self.fixture.metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["records"][0]["observedAnnotation"], event["observedAnnotation"])

    def test_tampered_bindings_and_unknown_classifications_fail_before_any_write(self):
        original = copy.deepcopy(self.entry)
        variants = []
        for key, value in (("sha256", "0"*64), ("observedSha256", "0"*64), ("observedKind", "guess")):
            item = copy.deepcopy(original); item[key] = value; variants.append([item])
        for key, value in (("sha256", "0"*64), ("line", 100), ("path", "../../outside.py")):
            item = copy.deepcopy(original); item["source"][key] = value; variants.append([item])
        variants.append([original, copy.deepcopy(original)])
        for entries in variants:
            with self.subTest(entries=entries):
                self.write_annotations(entries)
                self.fixture.assert_rejected_cleanly()

    def test_legacy_and_missing_evidence_stay_null_even_when_given_a_true_flag(self):
        for run_id in IMPORTER.LEGACY_RUNS:
            value = IMPORTER.workspace_semantics(run_id, {"workspacesUnchanged": True})
            self.assertIsNone(value["workspaceContentsUnchanged"])
            self.assertIsNone(value["learnerWorkspaceWrites"])
            self.assertIn("第一層檔名", value["workspaceEvidenceNote"])
            self.assertIn("未保存前後雜湊", value["workspaceEvidenceNote"])
        for value in (None, {}, {"workspacesUnchanged": 1}):
            self.assertIsNone(IMPORTER.workspace_semantics("new", value)["workspaceContentsUnchanged"])
        self.assertIs(IMPORTER.workspace_semantics("new", {"workspacesUnchanged": False})["workspaceContentsUnchanged"], False)

    def test_frozen_legacy_metadata_is_never_overwritten_by_a_semantics_reimport(self):
        original = b'{"learnerWorkspaceWrites":false,"historical":"preserve bytes"}'
        self.fixture.metadata_path.write_bytes(original)
        with self.assertRaisesRegex(IMPORTER.ImportValidationError, "版本化語義註記"):
            IMPORTER.import_run(FIXTURES.RUN_ID, self.project)
        self.assertEqual(self.fixture.metadata_path.read_bytes(), original)
        self.assertEqual(self.fixture.catalog_path.read_bytes(), self.fixture.original_catalog)


if __name__ == "__main__":
    unittest.main()
