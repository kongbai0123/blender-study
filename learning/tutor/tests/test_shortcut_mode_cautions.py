"""Reviewed mode-error cautions stay narrowly bound to frozen native evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
OLD = "learning/annotations/guide-shortcuts-v001.json"
CURRENT = "learning/annotations/guide-shortcuts-v002.json"
OLD_SHA256 = "c48c1da9ad65b196f66057199d578fa63e2fbf9a93d564d575bc98f8ffeb18ee"
EDITED = {("04-06", 1), ("05-05", 1), ("07-02", 0), ("07-02", 1)}
MODE_WARNINGS = EDITED - {("04-06", 1)}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def entries(data):
    return {(item["step"], item["guideIndex"]): item for item in data["entries"]}


class ShortcutModeCautionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = load(OLD)
        cls.current = load(CURRENT)
        cls.before = entries(cls.old)
        cls.after = entries(cls.current)

    def native_verifications(self):
        old_paths = {proof["path"] for proof in self.old["sourceDocuments"]}
        found = []
        for proof in self.current["sourceDocuments"]:
            if (proof["path"] not in old_paths and proof["path"].startswith("learning/evidence/")
                    and "mode-errors" in proof["path"]):
                document = load(proof["path"])
                if document.get("kind") == "native_shortcut_mode_error_verification":
                    found.append((proof, document))
        self.assertTrue(found, "Native mode-error observations must remain available")
        return found

    def test_previous_annotation_bytes_and_reviewed_coverage_stay_frozen(self):
        self.assertEqual(hashlib.sha256((ROOT / OLD).read_bytes()).hexdigest(), OLD_SHA256)
        self.assertEqual(self.current["id"], "guide-shortcuts-v002")
        self.assertEqual(self.current["coverage"], self.old["coverage"])
        self.assertEqual(len(self.after), 75)
        self.assertEqual(len(self.current["coverage"]), 142)
        self.assertEqual(set(self.after), set(self.before))
        old_sources = {proof["path"]: proof["sha256"] for proof in self.old["sourceDocuments"]}
        new_sources = {proof["path"]: proof["sha256"] for proof in self.current["sourceDocuments"]}
        self.assertGreater(len(new_sources), len(old_sources))
        for path, sha256 in old_sources.items():
            self.assertEqual(new_sources[path], sha256, path)

    def test_review_delta_changes_only_the_four_authorized_shortcuts(self):
        changed = {key for key in self.before if self.before[key] != self.after[key]}
        self.assertEqual(changed, EDITED)
        for key in EDITED:
            before, after = self.before[key], self.after[key]
            self.assertEqual({k: v for k, v in before.items() if k != "shortcut"},
                             {k: v for k, v in after.items() if k != "shortcut"})
            changed_fields = {field for field in before["shortcut"]
                              if before["shortcut"][field] != after["shortcut"][field]}
            allowed = {"effect", "requirements"} if key == ("04-06", 1) else {"cautions", "evidence"}
            self.assertTrue(changed_fields)
            self.assertLessEqual(changed_fields, allowed, key)
            self.assertEqual(set(before["shortcut"]), set(after["shortcut"]))

    def test_04_06_deselect_prepares_edge_check_instead_of_top_face_selection(self):
        shortcut = self.after[("04-06", 1)]["shortcut"]
        text = " ".join([shortcut["effect"], *shortcut["requirements"]])
        self.assertNotIn("頂面", text)
        self.assertIn("Edit Mode", text)
        self.assertIn("邊選取", text)
        self.assertIn("Non Manifold", text)
        self.assertIn("取消", shortcut["effect"])
        self.assertNotEqual(shortcut["effect"], self.after[("04-04", 1)]["shortcut"]["effect"])

    def test_mode_cautions_bind_new_native_images_and_readback_documents(self):
        old_sources = {proof["path"] for proof in self.old["sourceDocuments"]}
        added_sources = [proof for proof in self.current["sourceDocuments"] if proof["path"] not in old_sources]
        native_sources = {proof["path"] for proof in added_sources
                          if proof["path"].startswith("learning/evidence/") and "mode-errors" in proof["path"]}
        self.assertTrue(native_sources, "Mode-error readback needs its own hashed source document")
        for proof in added_sources:
            self.assertEqual(hashlib.sha256((ROOT / proof["path"]).read_bytes()).hexdigest(), proof["sha256"])
        for key in MODE_WARNINGS:
            with self.subTest(key=key):
                old_evidence = self.before[key]["shortcut"]["evidence"]
                new_evidence = self.after[key]["shortcut"]["evidence"]
                for proof in old_evidence:
                    self.assertIn(proof, new_evidence)
                added = [proof for proof in new_evidence if proof not in old_evidence]
                self.assertTrue(any(proof["path"] in native_sources for proof in added))
                self.assertTrue(any(Path(proof["path"]).suffix == ".png" and "mode-errors" in proof["path"]
                                    for proof in added))
                for proof in added:
                    self.assertEqual(proof["method"], "native_events_and_readback")
                    self.assertEqual(hashlib.sha256((ROOT / proof["path"]).read_bytes()).hexdigest(), proof["sha256"])

    def test_i_and_e_cautions_distinguish_object_mode_mistakes_and_recovery(self):
        for key in (("05-05", 1), ("07-02", 0)):
            with self.subTest(key=key):
                cautions = self.after[key]["shortcut"]["cautions"]
                i_warning = " ".join(text for text in cautions
                                     if "Object Mode" in text and re.search(r"(?<![A-Za-z])I(?![A-Za-z])", text))
                e_warning = " ".join(text for text in cautions
                                     if "Object Mode" in text and re.search(r"(?<![A-Za-z])E(?![A-Za-z])", text))
                self.assertTrue(i_warning, "I must warn about pressing it in Object Mode")
                self.assertTrue(any(word in i_warning for word in ("關鍵影格", "關鍵幀", "keyframe")))
                self.assertIn("Ctrl+Z", i_warning)
                self.assertTrue(e_warning, "E needs its own Object Mode observation")
                self.assertTrue(any(word in e_warning for word in ("無", "未", "沒有", "不會")))
                self.assertIn("擠出", e_warning)

    def test_ctrl_b_warns_about_render_region_with_a_cancel_path(self):
        cautions = self.after[("07-02", 1)]["shortcut"]["cautions"]
        warning = " ".join(text for text in cautions if "Object Mode" in text and "Ctrl+B" in text)
        self.assertTrue(warning, "Ctrl+B must explain its Object Mode context")
        self.assertTrue(any(word in warning for word in ("Render Region", "渲染範圍", "渲染區域")))
        self.assertTrue(any(word in warning for word in ("Esc", "右鍵")))
        self.assertIn("取消", warning)

    def test_i_native_readback_records_keyframes_then_actual_undo(self):
        for proof, document in self.native_verifications():
            with self.subTest(source=proof["path"]):
                self.assertEqual(document["blender"], "5.2.1 LTS")
                self.assertEqual(document["buildHash"], "9e2066aef7ef")
                self.assertTrue(document["factoryStartup"])
                cases = {case["case"]: case for case in document["cases"]}
                before = cases["baseline"]["actual"]["animation"]
                inserted = cases["object-i-keyframe"]["actual"]["animation"]
                undo = cases["object-i-undo"]["actual"]["animation"]
                self.assertFalse(before["animationData"])
                self.assertIsNone(before["action"])
                self.assertTrue(inserted["animationData"])
                self.assertIsNotNone(inserted["action"])
                self.assertEqual(inserted["pointCount"], 9)
                self.assertEqual(len(inserted["channels"]), 9)
                self.assertEqual(inserted["keyedFrames"], [1.0])
                self.assertFalse(undo["animationData"])
                self.assertIsNone(undo["action"])

    def test_e_native_readback_preserves_object_transform_mesh_and_animation(self):
        for proof, document in self.native_verifications():
            with self.subTest(source=proof["path"]):
                cases = {case["case"]: case for case in document["cases"]}
                before, after = cases["baseline"]["actual"], cases["object-e"]["actual"]
                self.assertEqual(after["mode"], "OBJECT")
                for field in ("mesh", "animation", "location", "rotation", "scale"):
                    self.assertEqual(after[field], before[field], field)

    def test_border_native_readback_distinguishes_undo_and_explicit_clear(self):
        candidates = []
        for proof, document in self.native_verifications():
            cases = {case["case"]: case for case in document["cases"]}
            if "perspective-border-before-clear" in cases and "camera-border-before-clear" in cases:
                candidates.append((proof, cases))
        self.assertTrue(candidates, "Clear needs a fresh true-border precondition, not an already cleared state")
        for proof, cases in candidates:
            with self.subTest(source=proof["path"]):
                for view, field in (("perspective", "viewRenderBorder"), ("camera", "sceneRenderBorder")):
                    complete = cases[view + "-border-complete"]["actual"][field]
                    undo = cases[view + "-border-undo"]["actual"][field]
                    pre_clear = cases[view + "-border-before-clear"]["actual"][field]
                    clear = cases[view + "-border-clear"]["actual"][field]
                    self.assertTrue(complete["enabled"])
                    self.assertTrue(pre_clear["enabled"])
                    self.assertFalse(clear["enabled"])
                    self.assertEqual((clear["xmin"], clear["xmax"], clear["ymin"], clear["ymax"]),
                                     (0.0, 1.0, 0.0, 1.0))
                    self.assertNotEqual(pre_clear, clear)
                    if view == "perspective":
                        self.assertEqual(undo, complete, "Perspective Undo was observed not to clear the border")
                    else:
                        self.assertFalse(undo["enabled"])

    def test_native_cases_bind_their_own_original_screenshot_bytes(self):
        for proof, document in self.native_verifications():
            for case in document["cases"]:
                with self.subTest(source=proof["path"], case=case["case"]):
                    shot = case["screenshot"]
                    image = ROOT / Path(proof["path"]).parent / shot["path"]
                    self.assertEqual(image.suffix, ".png")
                    self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), shot["sha256"])
                    self.assertEqual((shot["width"], shot["height"]), (1494, 1019))


if __name__ == "__main__":
    unittest.main()
