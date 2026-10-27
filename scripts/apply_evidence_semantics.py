"""Apply reviewed sidecar annotations to the catalog only; never replay/import a run.

Default is read-only verification. --write replaces catalog after an optimistic
byte check; original run/metadata files and learner progress are never written.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = "learning/annotations/workspace-semantics-v001.json"
SPEC = importlib.util.spec_from_file_location("semantics_importer", ROOT / "learning/tutor/import_run.py")
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def operation_runs(catalog):
    for lesson in catalog["lessons"]:
        for step in lesson["steps"]:
            for run in [step.get("operationRun"), *step.get("previousOperationRuns", [])]:
                if run:
                    yield step, run


def annotate(catalog, project=ROOT):
    project = Path(project).resolve()
    workspace_path = IMPORTER._contained_file(project / WORKSPACES, project, "工作區語義更正")
    data = IMPORTER._read_json(workspace_path)
    if data.get("schemaVersion") != 1 or not isinstance(data.get("runs"), list):
        raise ValueError("工作區語義更正格式不符")
    records = {}
    for item in data["runs"]:
        if item["runId"] in records:
            raise ValueError("重複工作區 runId")
        runner = None
        if item.get("runnerEvidence"):
            proof = item["runnerEvidence"]
            path = IMPORTER._contained_file(project / proof["path"], project, "公開 runner 衍生摘要")
            if IMPORTER._digest(path) != proof["sha256"]:
                raise ValueError("公開 runner 衍生摘要雜湊不符")
            public = IMPORTER._read_json(path)
            if public.get("kind") != "redacted_public_derivative" or public.get("originalPath") != proof["originalPath"] or public.get("originalSha256") != proof["originalSha256"]:
                raise ValueError("runner 原件／衍生摘要關聯不符")
            runner = public["content"]
        expected = IMPORTER.workspace_semantics(item["runId"], runner)
        if any(item.get(k) != v for k, v in expected.items()):
            raise ValueError("更正註記不能超出 runner 證據或回填未知值")
        records[item["runId"]] = item
    result = copy.deepcopy(catalog)
    # This is a new editorial layer, not a rewrite of frozen run/metadata evidence.
    result.setdefault("contentPolicy", {})["evidenceSemantics"] = {
        "reviewedOn": "2026-10-27",
        "annotations": IMPORTER.OBSERVED_ANNOTATIONS,
        "workspaceCorrection": WORKSPACES,
        "scope": "原圖是畫面證據；observed 的文字生成方式依逐事件註記，未分類只稱觀察紀錄。幾何檢查另查 verification；學員理解需本人確認，實體合格需列印、量測與試配等證據。"
    }
    indexes = {}
    seen, matched = set(), set()
    workspace_binding = {"path": WORKSPACES, "sha256": IMPORTER._digest(workspace_path)}
    counts = {}
    unhashed_figures = 0
    for step, run in operation_runs(result):
        review = step.get("contentReview", {})
        if review.get("summary") == "助教已在獨立 Blender 逐一實際操作並截圖，結果數值由 Blender 讀回；這是示範，不代表你已完成。":
            review["summary"] = "助教已在獨立 Blender 操作並保留原圖；事件依註記分為文字描述或混合紀錄，未分類稱觀察紀錄。數位幾何核對另查 verification，不代表學員理解或實體合格。"
        run_id = run["id"]
        if run_id not in records:
            raise ValueError("缺少已發布 run 的工作區更正註記：" + run_id)
        seen.add(run_id)
        item = records[run_id]
        for field in ("workspaceContentsUnchanged", "learnerWorkspaceWrites", "workspaceEvidenceNote"):
            run[field] = item[field]
        run["workspaceAnnotation"] = workspace_binding.copy()
        if run_id not in indexes:
            indexes[run_id] = IMPORTER.observation_annotations(project, run_id)
        index, binding = indexes[run_id]
        for event in run["events"]:
            figure = event["figure"]
            path = IMPORTER._contained_file(project / figure["path"], project, "已發布原圖")
            if figure.get("sha256") and IMPORTER._digest(path) != figure["sha256"]:
                raise ValueError("catalog 原圖雜湊不符")
            if not figure.get("sha256"):
                unhashed_figures += 1  # Historical manual captures stay unclassified; do not backfill original fields.
            semantics = IMPORTER.event_observation_semantics(step["id"], figure, event["observed"], index, binding)
            for field in ("observedKind", "observedReason", "observedSource", "observedAnnotation"):
                event.pop(field, None)
            event.update(semantics)
            kind = semantics["observedKind"]
            counts[kind] = counts.get(kind, 0) + 1
            if kind != "unclassified":
                matched.add((run_id, step["id"], figure["path"]))
    if seen != set(records):
        raise ValueError("工作區更正含有不在 catalog 的 run")
    annotation = IMPORTER._read_json(project / IMPORTER.OBSERVED_ANNOTATIONS)
    expected_matches = {(x["runId"], x["step"], x["imagePath"]) for x in annotation["entries"]}
    if matched != expected_matches:
        raise ValueError("有分類註記未匹配到 catalog；不可靜默省略")
    return result, {"runs": len(seen), "events": sum(counts.values()), "observedKinds": counts,
                    "matchedAnnotations": len(matched), "originalEvidenceWritten": False,
                    "learnerProgressWritten": False, "historicalFiguresWithoutDeclaredHash": unhashed_figures}


def update(project=ROOT, write=False):
    project = Path(project).resolve()
    path = project / "learning/catalog.json"
    before = path.read_bytes()
    catalog = json.loads(before.decode("utf-8"))
    result, report = annotate(catalog, project)
    if write:
        if path.read_bytes() != before:
            raise ValueError("catalog 已變更，停止；先重新交接與核對")
        if result != catalog:
            IMPORTER._atomic_json(path, result)
    elif result != catalog:
        raise ValueError("catalog 尚未套用最新已審註記（只有 --write 會更新）")
    report["catalogSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(update(args.root, args.write), ensure_ascii=False, indent=2))
