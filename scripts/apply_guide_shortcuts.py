"""Validate reviewed shortcut sidecars; optionally update guide.shortcut only.

Default is read-only. --write never imports runs, launches Blender, or touches
learner progress. Coverage binds every guide, including deliberately omitted ones.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = "learning/annotations/guide-shortcuts-v002.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".json"}
HASH_RE = re.compile(r"[0-9a-fA-F]{64}\Z")


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def guide_digest(guide):
    """Bind the unchanged conventional guide, excluding its optional shortcut."""
    original = {key: value for key, value in guide.items() if key != "shortcut"}
    return _digest(json.dumps(original, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")).encode("utf-8"))


def _link_or_reparse(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _project_root(project):
    root = Path(project).absolute()
    if not root.is_dir() or _link_or_reparse(root):
        raise ValueError("專案根目錄不存在或為符號連結／reparse point")
    return root.resolve()


def _contained_file(project, relative, prefixes=None, extensions=None):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("證據路徑必須是專案內的正規相對路徑")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
        raise ValueError("拒絕路徑逃逸或非正規路徑")
    if prefixes is not None and not any(relative.startswith(prefix) for prefix in prefixes):
        raise ValueError("來源／證據路徑不在允許目錄")
    if extensions is not None and pure.suffix.lower() not in extensions:
        raise ValueError("來源／證據副檔名不在允許範圍")
    path = project
    for part in pure.parts:
        path = path / part
        if not path.exists() or _link_or_reparse(path):
            raise ValueError("來源／證據不存在或含符號連結／reparse point")
    if not path.is_file() or not path.resolve().is_relative_to(project):
        raise ValueError("來源／證據不是專案內的普通檔案")
    return path


def _nonempty_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + "必須是非空文字")


def _check_proof(project, proof, source=False):
    if not isinstance(proof, dict):
        raise ValueError("證據格式必須是物件")
    expected = proof.get("sha256")
    if not isinstance(expected, str) or not HASH_RE.fullmatch(expected):
        raise ValueError("證據 SHA-256 必須是 64 位十六進位")
    prefixes = ("learning/evidence/", "learning/annotations/") if source else ("learning/evidence/",)
    path = _contained_file(project, proof.get("path"), prefixes, EXTENSIONS)
    if _digest(path.read_bytes()) != expected.lower():
        raise ValueError("來源／證據雜湊不符：" + proof["path"])
    if not source:
        _nonempty_text(proof.get("method"), "驗證方法")
        _nonempty_text(proof.get("label"), "證據標籤")


def _guide_key(item):
    if not isinstance(item, dict):
        raise ValueError("guide 註記必須是物件")
    _nonempty_text(item.get("step"), "步驟 ID")
    index = item.get("guideIndex")
    if type(index) is not int or index < 0:
        raise ValueError("guideIndex 必須是從 0 起算的整數")
    return item["step"], index


def annotate(catalog, project=ROOT):
    """Return a deep copy with only reviewed guide.shortcut additions/updates."""
    project = _project_root(project)
    annotation_path = _contained_file(project, ANNOTATIONS, ("learning/annotations/",), {".json"})
    data = json.loads(annotation_path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or type(data.get("schemaVersion")) is not int
            or data["schemaVersion"] != 1
            or not all(isinstance(data.get(key), list) for key in ("sourceDocuments", "entries", "coverage"))):
        raise ValueError("快捷鍵註記格式不符")
    if not data["sourceDocuments"]:
        raise ValueError("必須提供已雜湊的來源文件")
    source_paths = set()
    for proof in data["sourceDocuments"]:
        _check_proof(project, proof, source=True)
        if proof["path"] in source_paths:
            raise ValueError("重複來源文件")
        source_paths.add(proof["path"])

    result = copy.deepcopy(catalog)
    guides, steps = {}, set()
    try:
        for lesson in result["lessons"]:
            for step in lesson["steps"]:
                step_id = step["id"]
                _nonempty_text(step_id, "catalog 步驟 ID")
                if step_id in steps:
                    raise ValueError("catalog 步驟 ID 重複")
                steps.add(step_id)
                guide_list = step.get("guide", [])
                if not isinstance(guide_list, list):
                    raise ValueError("catalog guide 必須是陣列")
                for index, guide in enumerate(guide_list):
                    if not isinstance(guide, dict):
                        raise ValueError("catalog guide 必須是物件")
                    guides[(step_id, index)] = guide
    except (KeyError, TypeError) as exc:
        raise ValueError("catalog 結構不符") from exc

    entries, coverage = {}, {}
    for item in data["entries"]:
        key = _guide_key(item)
        if key in entries:
            raise ValueError("重複快捷鍵 entry")
        if key not in guides or item.get("guideSha256") != guide_digest(guides[key]):
            raise ValueError("entry 的 guide 綁定失效或不存在")
        shortcut = item.get("shortcut")
        if not isinstance(shortcut, dict):
            raise ValueError("shortcut 格式必須是物件")
        for field in ("keys", "effect"):
            _nonempty_text(shortcut.get(field), "shortcut " + field)
        for field in ("requirements", "cautions"):
            if not isinstance(shortcut.get(field), list):
                raise ValueError("shortcut " + field + " 必須是文字陣列")
            for text in shortcut[field]:
                _nonempty_text(text, "shortcut " + field)
        if not isinstance(shortcut.get("evidence"), list) or not shortcut["evidence"]:
            raise ValueError("每個快捷鍵必須有驗證證據")
        for proof in shortcut["evidence"]:
            _check_proof(project, proof)
        entries[key] = shortcut

    for item in data["coverage"]:
        key = _guide_key(item)
        if key in coverage:
            raise ValueError("重複 coverage")
        if key not in guides or item.get("guideSha256") != guide_digest(guides[key]):
            raise ValueError("coverage 的 guide 綁定失效或不存在")
        status = item.get("status")
        if status not in ("added", "omitted"):
            raise ValueError("coverage status 只能是 added 或 omitted")
        _nonempty_text(item.get("reason"), "coverage 原因")
        if (status == "added") != (key in entries):
            raise ValueError("coverage added 必須與 entries 精確一致")
        if status == "omitted" and "shortcut" in guides[key]:
            raise ValueError("omitted guide 不能保留 shortcut；不可隱性刪除")
        coverage[key] = status
    if set(coverage) != set(guides):
        raise ValueError("coverage 必須完整涵蓋每個 guide，恰好一筆")
    for key, shortcut in entries.items():
        guides[key]["shortcut"] = copy.deepcopy(shortcut)
    return result, {
        "guides": len(guides), "added": len(entries), "omitted": len(guides) - len(entries),
        "sourceDocuments": len(source_paths), "annotationSha256": _digest(annotation_path.read_bytes()),
        "originalEvidenceWritten": False, "learnerProgressWritten": False,
        "operationRunsWritten": False,
    }


def _atomic_json(path, value, expected, project):
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # Revalidate path and compare bytes immediately before replacement.
        current = _contained_file(project, "learning/catalog.json")
        if current.read_bytes() != expected:
            raise ValueError("catalog 已變更，停止；先重新交接與核對")
        os.replace(temporary, current)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update(project=ROOT, write=False):
    project = _project_root(project)
    path = _contained_file(project, "learning/catalog.json")
    before = path.read_bytes()
    catalog = json.loads(before.decode("utf-8"))
    result, report = annotate(catalog, project)
    if write:
        if path.read_bytes() != before:
            raise ValueError("catalog 已變更，停止；先重新交接與核對")
        if result != catalog:
            _atomic_json(path, result, before, project)
    elif result != catalog:
        raise ValueError("catalog 尚未套用已審快捷鍵註記（只有 --write 會更新）")
    report["catalogSha256"] = _digest(path.read_bytes())
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(update(args.root, args.write), ensure_ascii=False, indent=2))
