"""Read-only verifier plus new supplemental index for shortcut-run evidence.

Run this normal-Python script after the Blender processes have exited. Existing
evidence is read only. The index is created with exclusive mode; subsequent
invocations only verify the same bytes' inputs, without rewriting the index.
"""
import hashlib
import json
from pathlib import Path


PROJECT=Path(__file__).resolve().parents[3]
TARGET=PROJECT/"learning/annotations/shortcut-runtime-review-v001.json"
RUNS=(
    ("2026-10-27-shortcuts-demo-v001","shortcut-verification-v001.json",36),
    ("2026-10-27-shortcuts-keyboard-demo-v002","keyboard-verification-v001.json",9),
    ("2026-10-27-shortcuts-mesh-demo-v001","mesh-shortcut-verification-v001.json",8),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return dict(path=path.relative_to(PROJECT).as_posix(),sha256=digest(path))


def create_index():
    entries=[]
    for name,manifest_name,count in RUNS:
        out=PROJECT/"learning/evidence/01"/name
        run=json.loads((out/"run.json").read_text("utf-8"))
        manifest=json.loads((out/manifest_name).read_text("utf-8"))
        status=json.loads((out/"runner-status.json").read_text("utf-8"))
        records=run["records"]
        assert len(records)==count and len(list(out.glob("*.png")))==count
        assert not any("error" in r for r in records)
        assert run["blender"]=="5.2.1 LTS" and run["buildHash"]=="9e2066aef7ef"
        assert status["status"]=="completed" and status["blenderExitCode"]==0
        assert status["workspacesUnchanged"] is True and status["workspaceChanges"]==[]
        assert status["workspacesBefore"]==status["workspacesAfter"]
        images=[]
        for r in records:
            picture=out/r["file"]
            assert digest(picture)==r["sha256"]
            images.append(dict(case=r["slug"],screenshot=ref(picture),
                visualReview="view_image_original_png",reviewPassed=True,
                observedKind="structured_readback_with_native_screenshot"))
        source_index=out/"source-snapshot/manifest.json"
        source_manifest=json.loads(source_index.read_text("utf-8"))
        for src in source_manifest["files"]:
            assert digest(out/src["snapshot"])==src["sha256"]
        for case in manifest["cases"]:
            assert case["passed"] is not False
            assert digest(out/case["screenshot"]["path"])==case["screenshot"]["sha256"]
        entries.append(dict(runId=name,run=ref(out/"run.json"),verification=ref(out/manifest_name),
            sourceSnapshot=ref(source_index),screenshots=images,
            screenshotCount=count,nativeAssertionPassCount=sum(c["passed"] is True for c in manifest["cases"]),
            observationOnlyCases=[c["case"] for c in manifest["cases"] if c["passed"] is None],
            workspaceContentsUnchanged=True,learnerWorkspaceWrites=None,
            workspaceEvidenceNote="Runner遞迴前後路徑與雜湊一致；不證明期間未寫入，也不辨認寫入者。"))
    failed=PROJECT/"learning/evidence/01/2026-10-27-shortcuts-keyboard-demo-v001"
    failed_run=json.loads((failed/"run.json").read_text("utf-8"))
    failed_status=json.loads((failed/"runner-status.json").read_text("utf-8"))
    assert failed_status["status"]=="failed" and any("error" in r for r in failed_run["records"])
    return dict(schemaVersion=1,kind="supplemental_shortcut_evidence_review",date="2026-10-27",
        reviewer="Codex/shortcut_runtime",scope="53 original successful-run PNGs individually viewed; native state/mesh readbacks and hashes checked",
        blender="5.2.1 LTS",buildHash="9e2066aef7ef",runs=entries,
        nativeAssertionPassCount=sum(e["nativeAssertionPassCount"] for e in entries),
        successfulRunCount=3,successfulScreenshotCount=53,
        failedRuns=[dict(runId=failed.name,run=ref(failed/"run.json"),
            reason="Emulate Numpad已勾選，但模擬主ONE沒有匹配NUMPAD_1；嚴格斷言中止。未刪圖、未回填或改寫；v002加plain/unicode對照並保留未證實狀態。",
            learnerWorkspaceWrites=None,workspaceContentsUnchanged=failed_status["workspacesUnchanged"],publishedAsShortcutSuccess=False)],
        preciseConclusions=[
            "Object Mode/Global/factory perspective: G X .5 from X0→.5 and X1→1.5; G X -.5 from1.5→1; field Location X=.5 sets absolute .5.",
            "G .5 with no X from[1,0,0] returned[1.5,0,0] in this tested context; advise explicit X/Y/Z rather than generalizing to other modes or orientations.",
            "G X3 followed by Esc or right mouse returned to exactly the previous location within1e-5 numerical readback comparison; not manufacturing tolerance.",
            "R X/Y/Z30 changed the matching degree component; S X/Y/Z1.5 changed the matching scale component. Scale is multiplicative, not Dimensions absolute length.",
            "N opened Sidebar; Tab toggled Edit/Object; A selected all3 objects and AltA deselected; NumpadDecimal framed selected object without changing its location.",
            "ShiftA opened Add, X opened Delete confirmation (canceled), F2 renamed Cube→ShortcutCube, M opened Move to Collection, CtrlA opened Apply (no apply option executed).",
            "Main row1 with emulation off preserved User Perspective; NUMPAD1=Front Orthographic and NUMPAD3=Right Orthographic.",
            "Preferences/Input/Keyboard/Emulate Numpad checkbox and tooltip read from original UI; the tooltip describes main1–0 as numpad equivalents, but plain and unicode simulatedONE did not change Right view after checkbox click. Physical keyboard remapping remains unverified by this runner.",
            "Main PERIOD opened Pivot Point even with Emulate Numpad checked; NUMPAD_PERIOD framed selection. Main row digits/period must not be conflated with numeric keypad keys.",
            "Numpad0 switched viewPerspective to CAMERA; main3 in Edit Mode enabled face selection; AltA deselected edit components; I .2 inset6→10 faces; E .4 normal extrusion10→14 with selected faceY=-1.4; main2 edge selection; CtrlB .1 bevel14→18 faces. These disposable factory-unit values are not engineering dimensions or qualifications."
        ],
        limitations=["Only native simulated events and original UI screenshots, no physical-keyboard experiment.",
            "For Emulate Numpad, actual checkbox/tooltip is verified; effective main-keyboard remapping is not. A completed v002 runner is not evidence this behavior passed.",
            "Mesh front view does not expose extrusion depth visually; selected-face coordinate readback supplies that separate evidence.",
            "No source scene or STL saved, no learner completion/fit/strength assessment, no progress or catalog write by this probe agent.",
            "Raw runner-status contains private Recent inventory and is not part of this public review; only content-comparison outcome is quoted."])


if __name__=="__main__":
    result=create_index()
    if TARGET.exists():
        assert json.loads(TARGET.read_text("utf-8"))==result,"Existing review differs; preserve it and create a new version"
        print("verified",TARGET.relative_to(PROJECT),"53 PNGs / 43 native assertions / 1 preserved failed run")
    else:
        with TARGET.open("x",encoding="utf-8",newline="\n") as handle:
            json.dump(result,handle,ensure_ascii=False,indent=2);handle.write("\n")
        print("created",TARGET.relative_to(PROJECT))
