"""Prepare an explicit, privacy-conscious public file list without staging Git.

Original execution records are never rewritten. Private runner metadata gets a
separately labelled derivative; the public package is deliberately not a mirror.
Run this again after editing public documentation to refresh the manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# Each revision prepares a new manifest; reviewed prior manifests stay historical.
DATE = "2026-10-29"
RELEASE = "2026-10-29-engineering-v038"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = f"docs/publication-manifest-{RELEASE}.json"
PATHSPEC = f"docs/publication-paths-{RELEASE}.txt"
DERIVATIVES = "learning/evidence/public-metadata"
AUDIT = "learning/evidence/audits/2026-10-25-claude-continuation-v001"
RECENT_KEYS = {"recentCleanup", "beforeLinks", "afterLinks"}
TEXT_EXTENSIONS = {".json", ".md", ".txt", ".html", ".css", ".js", ".cjs", ".py", ".cmd", ".ps1", ".yml", ".yaml"}
PUBLIC_EXTENSIONS = TEXT_EXTENSIONS | {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".blend", ".stl", ".csv"}
REFERENCE_PATTERN = re.compile(r"(?:learning|sources|docs|scripts|\.github)/[^\s\"'<>`\[\]{}(),;]+")
SECRET_PATTERN = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def stable_json(path: Path, value) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def nodes(value, pointer=""):
    yield pointer, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from nodes(item, pointer + "/" + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from nodes(item, pointer + "/" + str(index))


def has_recent(value) -> bool:
    return any(isinstance(item, dict) and RECENT_KEYS.intersection(item) for _, item in nodes(value))


def has_progress_state(value) -> bool:
    for pointer, item in nodes(value):
        if not isinstance(item, dict):
            continue
        if pointer.rsplit("/", 1)[-1].lower() in {"progress", "progresssnapshot", "learnerprogress"}:
            return True
        if {"revision", "activeLesson", "lessons", "events"}.issubset(item):
            return True
    return False


def has_workspace_snapshot(value) -> bool:
    # Old immutable public summaries contain only empty, bootstrap-created
    # course directories. Those reveal no learner files or custom names.
    # File records, arbitrary names and other snapshot shapes remain private.
    scaffold = {".", "engineering-parametric"} | {f"{n:02d}" for n in range(1, 10)} | {
        f"{n:02d}/exports" for n in range(1, 10)}
    for _, item in nodes(value):
        if not isinstance(item, dict):
            continue
        for key in ("workspacesBefore", "workspacesAfter"):
            if key not in item or item[key] is None:
                continue
            state = item[key]
            if isinstance(state, dict) and all(name in scaffold and entry == {"kind": "directory"}
                                               for name, entry in state.items()):
                continue
            return True
    return False


def strip_recent(value, pointer="", removed=None):
    if removed is None:
        removed = []
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            child = pointer + "/" + str(key)
            if key in RECENT_KEYS:
                removed.append(child)
            else:
                cleaned[key] = strip_recent(item, child, removed)
        return cleaned
    if isinstance(value, list):
        return [strip_recent(item, pointer + "/" + str(index), removed) for index, item in enumerate(value)]
    return value


class Publication:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.selected: set[str] = set()
        self.reasons: dict[str, set[str]] = {}
        self.omissions: dict[str, str] = {}
        self.replacements: dict[str, str] = {}
        self.unavailable: dict[tuple[str, str], str] = {}
        self.missing: set[tuple[str, str]] = set()
        self.json_cache = {}
        self.published_dirs: set[str] = set()

    def json(self, rel):
        if rel not in self.json_cache:
            try:
                self.json_cache[rel] = read_json(self.root / rel)
            except (ValueError, UnicodeError):
                self.json_cache[rel] = None
        return self.json_cache[rel]

    def local_only(self, rel: str, inspect_json=True) -> str | None:
        p = Path(rel)
        parts = p.parts
        # These belong to the next integration batch, not the reviewed v038
        # release. Keep the original worktree and all partial evidence intact.
        pending_tokens = ("four_boss_manual", "four_insert_boss_manual", "side_cap_manual", "radial_cutter",
                          "cad_tool_load", "cad-sketcher-load-tools-isolated", "encode_blender_sampled_motion",
                          "encode_sampled_motion_gif", "build_visual_review_inventory", "replay_operations_batch",
                          "audit_side_cap_sources", "side_cap_cylinder_f9_probe")
        if any(token in p.name for token in pending_tokens) or "/_candidates/" in rel:
            return "next-batch integration or private intermediate candidate; excluded from v038 release"
        if rel.startswith("learning/patches/2026-10-29-") and any(token in p.name for token in ("image-review", "image-caption", "visual-", "replay-plan")):
            return "in-progress next-batch review; excluded from v038 release"
        if rel == "learning/evidence/parametric/2026-10-29-manual-guard-70x40-reject-v004/02-text-prepared.png":
            return "local screenshot contains a personal temporary path; not used by published lessons"
        if any(part in {".git", "__pycache__", "node_modules", ".scratch"} for part in parts):
            return "local tooling/cache"
        if rel in {MANIFEST, PATHSPEC}:
            return None
        if rel.startswith(("learning/.history/", "learning/workspaces/", "learning/archive/", "learning/.publication-private/")):
            return "private learner history/workspace or retired local archive"
        if rel in {"learning/progress.json", "learning/.progress.lock", "learning/runtime.json"}:
            return "private learner state or runtime"
        if "/source-cache/" in "/" + rel:
            return "third-party audit cache: redistribution permission not established"
        if p.suffix.lower() in {".log", ".pyc", ".lnk", ".blend1", ".pdf"}:
            return "local log/cache/backup or unlicensed original publication"
        if p.name.startswith(".env") or p.suffix.lower() in {".pem", ".key"}:
            return "environment or credential material"
        name = p.name.lower()
        if (name.startswith("baseline-v") or "publication-baseline" in name
                or name.startswith("progress-baseline-v") or name.startswith("recent-cleanup")):
            return "private publication/state baseline or Recent recovery inventory"
        if inspect_json and p.suffix.lower() == ".json" and not rel.startswith(DERIVATIVES + "/"):
            value = self.json(rel)
            if value is not None:
                if has_progress_state(value):
                    return "embedded private learner progress snapshot"
                if has_workspace_snapshot(value):
                    return "embedded private learner workspace inventory"
                if has_recent(value):
                    return "Windows Recent inventory embedded in raw metadata"
        if name == "runner-status.json":
            return "raw runner-status kept local by publication policy"
        # 2026-10-28 的動畫採樣與 Blender 探測：原始影格、讀值與執行紀錄含本機路徑；公開 GIF、前後原圖與去識別摘要即可。
        if "/2026-10-28-pilot-box-move-record-v001/" in rel:
            return "failed animation sampling run kept local"
        if re.search(r"/2026-10-28-(?:pilot-box-move-record|boss-box-join-trial|closed-external-thread-probe)-v\d{3}/", rel) and (
                name.startswith(("frame-", "gif-")) or name in {"frames.json", "run.json"}):
            return "raw sampling frames or run record with local paths; the GIF, before/after screenshots and public summaries are published instead"
        return None

    def derivative(self, rel: str) -> str | None:
        if rel in self.replacements:
            return self.replacements[rel]
        value = self.json(rel)
        if value is None or has_progress_state(value):
            return None
        if has_workspace_snapshot(value):
            # Current runner metadata also contains learner workspace snapshots;
            # stripping Recent alone does not make those records public.
            return None
        if not has_recent(value) and Path(rel).name != "runner-status.json":
            return None
        removed = []
        sanitized = strip_recent(value, removed=removed)
        # The path is stable across refreshes; original hashes prove which raw
        # input produced this clearly distinguished public derivative.
        identifier = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:12]
        prefix = f"{DERIVATIVES}/{Path(rel).stem}-{identifier}-public-v"
        candidate = {
            "schemaVersion": 1,
            "kind": "redacted_public_derivative",
            "redacted_public_derivative": True,
            "preparedOn": DATE,
            "originalPath": rel,
            "originalSha256": sha256(self.root / rel),
            "originalBytes": (self.root / rel).stat().st_size,
            "originalAvailableInPublicPackage": False,
            "redactedKeys": sorted(removed),
            "redactionPolicy": "Recursively omit Windows Recent inventory keys recentCleanup, beforeLinks and afterLinks. Original stays unchanged locally. This derivative is not the original execution record.",
            "content": sanitized,
        }
        # Preserve the prior release's metadata bytes. A changed raw input or
        # redaction policy needs a new version, not a replacement of public-v001.
        version = 1
        while True:
            target = prefix + f"{version:03d}.json"
            path = self.root / target
            if not path.exists():
                stable_json(path, candidate)
                break
            previous = read_json(path)
            if ({k: v for k, v in previous.items() if k != "preparedOn"}
                    == {k: v for k, v in candidate.items() if k != "preparedOn"}):
                break
            version += 1
        self.replacements[rel] = target
        return target

    def add(self, rel: str, reason: str, allow_derivative=True):
        rel = rel.replace("\\", "/").removeprefix("./")
        p = self.root / rel
        if not p.is_file():
            return
        resolved = p.resolve()
        if not resolved.is_relative_to(self.root) or p.is_symlink():
            self.omissions[rel] = "symlink or file outside project root"
            return
        why = self.local_only(rel)
        if why:
            self.omissions[rel] = why
            if allow_derivative:
                target = self.derivative(rel) if p.suffix.lower() == ".json" else None
                if target:
                    self.add(target, "explicitly redacted public derivative of " + rel, False)
            return
        if p.suffix.lower() not in PUBLIC_EXTENSIONS and p.name not in {".gitignore", ".gitattributes", "LICENSE", "NOTICE", "AUTHORS"}:
            self.omissions[rel] = "file type outside curated public format allowlist"
            return
        if p.suffix.lower() in TEXT_EXTENSIONS:
            text = p.read_text(encoding="utf-8-sig")
            if SECRET_PATTERN.search(text):
                raise RuntimeError(f"Credential marker in candidate {rel}; no content printed")
        self.selected.add(rel)
        self.reasons.setdefault(rel, set()).add(reason)

    def published_record(self, rel: str) -> bool:
        if any(rel.startswith(directory + "/") for directory in self.published_dirs):
            return True
        # Import metadata is next to, rather than inside, its published run.
        return any(rel == directory + ".json" for directory in self.published_dirs)

    def references(self, rel: str):
        path = self.root / rel
        # Historical manifests contain explicit omitted/private inventories. They
        # are archived records, never dependency roots for the next candidate.
        historical_inventory = rel.startswith(("docs/publication-manifest-", "docs/publication-paths-"))
        if path.suffix.lower() not in TEXT_EXTENSIONS or rel in {MANIFEST, PATHSPEC} or historical_inventory:
            return set()
        text = path.read_text(encoding="utf-8-sig")
        results = set()
        if path.suffix.lower() == ".json":
            value = self.json(rel)
            for _, item in nodes(value):
                if isinstance(item, str):
                    normalized = item.replace("\\", "/")
                    # Whole-string paths include original Windows capture paths.
                    prefix = "D:/others/study/Blender-Learning/"
                    if normalized.startswith(prefix):
                        normalized = normalized[len(prefix):]
                    if normalized.startswith(("learning/", "sources/", "docs/", "scripts/", ".github/")) and len(normalized) < 500 and "\n" not in normalized:
                        results.add(normalized.rstrip("/"))
                    elif len(normalized) < 200 and not re.search(r"\s|://", normalized):
                        # Some frozen geometry summaries store files relative to
                        # evidence/parametric rather than the summary's run dir.
                        # Resolve only actual in-root files, never invent a path.
                        for parent in path.parents:
                            if not parent.is_relative_to(self.root):
                                break
                            candidate = parent / normalized
                            if candidate.is_file() and candidate.resolve().is_relative_to(self.root):
                                results.add(candidate.relative_to(self.root).as_posix())
                                break
        for match in REFERENCE_PATTERN.finditer(text):
            candidate = match.group(0).rstrip(".。：；／。")
            # Ignore parameterized paths and prose tails, but retain exact
            # absent file paths for the incomplete-reference report.
            if "<" not in candidate and len(candidate) < 500:
                results.add(candidate.rstrip("/"))
        return results

    def build(self):
        read_json(self.root / "learning/catalog.json")  # Validate, never migrate or rewrite teaching content.
        # Code, launchers, plans, tests and editorial documentation are the
        # portable core. Runtime state and evidence require their own policy.
        for path in self.root.iterdir():
            if path.is_file():
                self.add(path.name, "project root application/documentation")
        for directory in ("scripts", "docs", "sources", ".github", "learning/tutor", "learning/tests", "learning/plans", "learning/drafts", "learning/web", "learning/annotations"):
            folder = self.root / directory
            if folder.exists():
                for path in sorted(folder.rglob("*")):
                    if path.is_file():
                        self.add(path.relative_to(self.root).as_posix(), "portable code/documentation/source facts")
        for path in sorted((self.root / "learning").iterdir()):
            if path.is_file() and path.suffix.lower() in {".py", ".ps1", ".cmd", ".cjs"}:
                self.add(path.relative_to(self.root).as_posix(), "application code/launcher")
        self.add("learning/catalog.json", "current teaching catalog")
        # Only catalog-rooted evidence directories get a bulk per-file review.
        # This includes published focus/view supplements, not unreferenced probes.
        catalog_refs = self.references("learning/catalog.json")
        for ref in catalog_refs:
            parts = Path(ref).parts
            if len(parts) > 4 and parts[:2] == ("learning", "evidence") and parts[2].isdigit():
                self.published_dirs.add("/".join(parts[:4]))
        self.published_dirs.add(AUDIT)
        for directory in sorted(self.published_dirs):
            folder = self.root / directory
            if folder.is_dir():
                for path in sorted(folder.rglob("*")):
                    if path.is_file():
                        self.add(path.relative_to(self.root).as_posix(), "published run/audit dependency")
        for ref in sorted(catalog_refs):
            self.add(ref, "catalog reference")
        # Current engineering content is a dependency root in its own right.
        # Only exact referenced files are selected; do not bulk-publish new runs.
        manage_file = self.root / "learning/manage.py"
        manage_source = manage_file.read_text(encoding="utf-8-sig") if manage_file.is_file() else None
        current_definitions = []
        for variable in ("ENGINEERING_CURRICULUM", "ENGINEERING_PATH", "CHALLENGES"):
            if manage_source is None:
                break  # Minimal policy-test fixture, not a runnable app package.
            match = re.search(r"^" + variable + r"\s*=\s*LEARNING\s*/\s*(.+)$", manage_source, re.MULTILINE)
            if not match:
                raise RuntimeError("Missing current definition pointer: " + variable)
            segments = re.findall(r'"([^"\r\n]+)"', match.group(1))
            current_definitions.append("learning/" + "/".join(segments))
        for definition in current_definitions:
            self.add(definition, "current engineering definition")
            for ref in self.references(definition):
                parts = Path(ref).parts
                if len(parts) > 4 and parts[:2] == ("learning", "evidence"):
                    self.published_dirs.add("/".join(parts[:4]))
        # Frozen builders/tests consume these exact JSON readbacks through
        # computed BASE/name expressions, which are not literal clickable URLs.
        proof_files = [
            "learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/height-state.json",
            "learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-horizontal-state.json",
            "learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-vertical-state.json",
            "learning/evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/after-cut-state.json",
            "learning/evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/reopened-state.json",
        ]
        for proof in proof_files:
            self.add(proof, "explicit frozen-builder readback dependency")
        seen = set()
        while True:
            pending = sorted(self.selected - seen)
            if not pending:
                break
            for source in pending:
                seen.add(source)
                for target in sorted(self.references(source)):
                    path = self.root / target
                    # A historical reference to excluded scratch/private storage
                    # need not be accessible. Apply path policy before stat/read.
                    structural_reason = self.local_only(target, inspect_json=False)
                    if structural_reason:
                        self.omissions[target] = structural_reason
                        self.unavailable[(source, target)] = structural_reason
                        if target.endswith(".json") and self.published_record(target) and path.is_file():
                            replacement = self.derivative(target)
                            if replacement:
                                self.add(replacement, "public derivative for referenced private metadata")
                        continue
                    if path.is_dir():
                        continue
                    if not path.is_file():
                        # Historical absent/probe references remain distinct from
                        # current clickable links; report without inventing files.
                        if Path(target).suffix.lower() in PUBLIC_EXTENSIONS:
                            self.missing.add((source, target))
                        continue
                    if not path.resolve().is_relative_to(self.root):
                        continue
                    why = self.local_only(target)
                    if not why and target.startswith("learning/evidence/"):
                        parts = Path(target).parts
                        if len(parts) > 4 and parts[2].isdigit():
                            run_dir = "/".join(parts[:4])
                            if run_dir not in self.published_dirs:
                                why = "unpublished diagnostic/probe/failed run retained locally"
                    if why:
                        self.omissions[target] = why
                        self.unavailable[(source, target)] = why
                        if target.endswith(".json") and self.published_record(target):
                            replacement = self.derivative(target)
                            if replacement:
                                self.add(replacement, "public derivative for referenced private metadata")
                    else:
                        self.add(target, "dependency referenced by " + source)
        # Inventory every unselected evidence file, with exact paths and reasons.
        for path in sorted((self.root / "learning/evidence").rglob("*")):
            if path.is_file():
                rel = path.relative_to(self.root).as_posix()
                if rel not in self.selected:
                    self.omissions.setdefault(rel, self.local_only(rel) or "unpublished/unreferenced local evidence")
        for rel in ("learning/progress.json", "learning/runtime.json", "learning/.progress.lock"):
            if (self.root / rel).is_file():
                self.omissions[rel] = self.local_only(rel)
        self.selected.discard(MANIFEST)
        self.selected.discard(PATHSPEC)
        entries = [{"path": rel, "bytes": (self.root / rel).stat().st_size,
                    "sha256": sha256(self.root / rel),
                    "kind": "redacted_public_derivative" if rel.startswith(DERIVATIVES + "/") else "original_project_file",
                    "includedBecause": sorted(self.reasons.get(rel, []))} for rel in sorted(self.selected)]
        manifest = {
            "schemaVersion": 1, "id": "curated-publication-" + RELEASE,
            "preparedOn": DATE, "timezone": "Asia/Taipei",
            "packageScope": "Curated teaching code, real screenshots, generated geometry and public audit evidence; deliberately not an exact mirror of private local execution history.",
            "localOriginalsPreserved": True,
            "progressPolicy": "Never publish learner progress/history/workspaces; fresh clones initialize their own state.",
            "sourceRightsPolicy": "Exclude third-party PDF/page/text audit caches; citations and access do not establish redistribution permission. No umbrella license grant is inferred.",
            "localOnlyRules": ["learning/progress.json, learning/.history/**, learning/workspaces/**, learning/archive/**, learning/.publication-private/** and runtime/lock data", "Any JSON containing recentCleanup/beforeLinks/afterLinks or an embedded progress state", "All raw runner-status.json; separately labelled privacy derivatives may be published", "baseline-v*.json, *publication-baseline*.json, progress-baseline-v*.json and Recent recovery inventories", "**/source-cache/**, third-party PDFs and their rendered pages/full-text extracts", "Unreferenced probe/failed runs, logs, backups, caches, environment and credential files"],
            "historicalPathPolicy": "Original project paths and timestamps are historical capture provenance, not portable installation paths. Original image pixels and event action/observed/figure are retained; current catalog adds versioned semantic annotations without rewriting frozen runs or metadata.",
            "hashBoundary": {"hashedFiles": len(entries), "notSelfHashed": [MANIFEST, PATHSPEC], "reason": "Avoid circular manifest/pathspec hashes. Both generated metadata files are nevertheless listed in the Git pathspec."},
            "publishedRunDirectories": sorted(self.published_dirs),
            "files": entries,
            "publicDerivatives": [{"originalPath": key, "publicPath": value} for key, value in sorted(self.replacements.items())],
            "localOnlyFiles": [{"path": key, "reason": value} for key, value in sorted(self.omissions.items())],
            "intentionalUnavailableReferences": [{"from": source, "target": target, "reason": reason, "publicDerivative": self.replacements.get(target)} for (source, target), reason in sorted(self.unavailable.items())],
            "historicalOrUnresolvedReferences": [{"from": source, "target": target} for source, target in sorted(self.missing)],
            "validationLimits": ["Preparing this manifest is not publication or physical qualification.", "v038 adds reference cards to reviewed v037; unfinished manual/CAD repair/motion integration is excluded. No complete per-image privacy review is claimed.", "Historical internal checks may cite local-only omitted files and hashes; their absence is intentional, not proof they were republished.", "This preparer does not stage, commit, push, delete, or change private original records."],
        }
        stable_json(self.root / MANIFEST, manifest)
        paths = sorted(self.selected | {MANIFEST, PATHSPEC})
        data = "\n".join(paths) + "\n"
        target = self.root / PATHSPEC
        if not target.exists() or target.read_text(encoding="utf-8") != data:
            target.write_text(data, encoding="utf-8", newline="\n")
        print(json.dumps({"manifest": MANIFEST, "pathspec": PATHSPEC,
                          "files": len(paths), "bytes": sum(item["bytes"] for item in entries),
                          "derivatives": len(self.replacements), "localOnlyFiles": len(self.omissions),
                          "unavailableReferences": len(self.unavailable), "historicalOrUnresolvedReferences": len(self.missing)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--verify", action="store_true", help="Read-only verification of the prepared public package; works in a fresh clone without private raw evidence.")
    args = parser.parse_args()
    if args.verify:
        verify_publication(args.root)
    else:
        Publication(args.root).build()


def verify_publication(root: Path):
    root = root.resolve()
    manifest = read_json(root / MANIFEST)
    entries = manifest["files"]
    included = {entry["path"] for entry in entries}
    if len(included) != len(entries):
        raise RuntimeError("Duplicate paths in publication manifest")
    expected_paths = included | {MANIFEST, PATHSPEC}
    actual_paths = set((root / PATHSPEC).read_text(encoding="utf-8").splitlines())
    if actual_paths != expected_paths:
        raise RuntimeError("Pathspec and manifest disagree")
    inspector = Publication(root)
    errors = []
    for entry in entries:
        rel = entry["path"]
        path = root / rel
        if not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file():
            errors.append({"path": rel, "error": "missing, symlink or outside root"})
            continue
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            errors.append({"path": rel, "error": "byte count or SHA-256 mismatch"})
        why = inspector.local_only(rel)
        if why:
            errors.append({"path": rel, "error": "local-only file bundled", "reason": why})
        if path.suffix.lower() in TEXT_EXTENSIONS and SECRET_PATTERN.search(path.read_text(encoding="utf-8-sig")):
            errors.append({"path": rel, "error": "credential marker; contents suppressed"})
        if path.suffix.lower() == ".json":
            value = inspector.json(rel)
            if has_recent(value) or has_progress_state(value) or has_workspace_snapshot(value):
                errors.append({"path": rel, "error": "private inventory or progress keys bundled"})
            if rel.startswith(DERIVATIVES + "/"):
                if not isinstance(value, dict) or value.get("kind") != "redacted_public_derivative" or not value.get("redacted_public_derivative") or value.get("originalAvailableInPublicPackage") is not False:
                    errors.append({"path": rel, "error": "missing explicit public derivative provenance"})
    omitted = {item["path"] for item in manifest["localOnlyFiles"]}
    # Whole-string catalog references are strict: real images, downloads and
    # review documents must exist, or be deliberately classified as local-only.
    catalog = read_json(root / "learning/catalog.json")
    for _, value in nodes(catalog):
        if not isinstance(value, str) or "\n" in value or len(value) >= 500:
            continue
        rel = value.replace("\\", "/")
        if rel.startswith("D:/others/study/Blender-Learning/"):
            rel = rel[len("D:/others/study/Blender-Learning/"):]
        if rel.startswith(("learning/", "sources/", "docs/", "scripts/", ".github/")) and Path(rel).suffix.lower() in PUBLIC_EXTENSIONS:
            if rel not in expected_paths and rel not in omitted:
                errors.append({"from": "learning/catalog.json", "target": rel, "error": "catalog file reference not bundled or intentionally omitted"})
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"ok": True, "hashedFiles": len(entries), "catalogReferencesChecked": True,
                      "privateOriginalsRequired": False, "selfHashExclusions": [MANIFEST, PATHSPEC]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
