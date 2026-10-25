#!/usr/bin/env python3
"""以單一 progress.json 維護 Blender 學習進度與不可覆寫的檔案版本。"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace


LEARNING = Path(__file__).resolve().parent
PROJECT = LEARNING.parent
PROGRESS = LEARNING / "progress.json"
CATALOG = LEARNING / "catalog.json"
TAIPEI = timezone(timedelta(hours=8))
# catalog 步驟的 setsLearner 與 CLI 只能寫入這些學員設定與值。
LEARNER_CHOICES = {"interfaceLanguage": ("en", "zh-Hant")}
# 網頁筆記一律是學員寫的；命令列預設由助教記錄，必要時可標為學員原話。
NOTE_AUTHORS = ("learner", "tutor")
LOCK_WAIT_SECONDS = 3.0


class RevisionConflict(ValueError):
    """另一個入口已寫入；呼叫者必須重新讀取，不能盲目覆蓋。"""


class ProgressBusy(ValueError):
    """另一個寫入者持有鎖超過等待時間；本次未寫入，可稍後重試。"""


def now():
    return datetime.now(TAIPEI).isoformat(timespec="seconds")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_state():
    catalog, progress = read_json(CATALOG), read_json(PROGRESS)
    if catalog.get("schemaVersion") != 1 or progress.get("schemaVersion") != 1:
        raise ValueError("不支援的資料格式版本。")
    if type(progress.get("revision")) is not int or progress["revision"] < 1:
        raise ValueError("progress.json 的 revision 必須是正整數。")
    if not isinstance(catalog.get("lessons"), list):
        raise ValueError("catalog.json 缺少 lessons 清單。")
    for key, kind in (("lessons", dict), ("fileVersions", list), ("events", list)):
        if not isinstance(progress.get(key), kind):
            raise ValueError("progress.json 缺少有效的 " + key + "。")
    return catalog, progress


@contextmanager
def progress_lock(wait=LOCK_WAIT_SECONDS):
    """所有寫入者共用 OS 鎖；被占用時短暫重試，逾時不寫入。程序結束時 OS 亦會釋放。"""
    if os.name == "nt":
        import msvcrt
    else:
        import fcntl
    with (LEARNING / ".progress.lock").open("a+b") as lock:
        lock.seek(0, os.SEEK_END)
        if lock.tell() == 0:
            lock.write(b"\0")
            lock.flush()
        deadline = time.monotonic() + wait
        while True:
            lock.seek(0)
            try:
                if os.name == "nt":
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise ProgressBusy("另一個視窗或聊天正在寫入進度，請稍候幾秒再試；本次未寫入。") from None
                time.sleep(0.05)
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == "nt":
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def atomic_write(path, data):
    """暫存檔與目標同目錄，再以 os.replace 原子替換。"""
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def commit(progress, previous, event):
    revision = progress["revision"] + 1
    timestamp = now()
    progress["revision"] = revision
    progress["updatedAt"] = timestamp
    progress["events"].append(dict(event, revision=revision, at=timestamp))
    history = LEARNING / ".history"
    history.mkdir(exist_ok=True)
    backup = history / ("progress-r%06d.json" % (revision - 1))
    if backup.exists():
        if backup.read_bytes() != previous:
            raise ValueError("歷史 revision 已存在但內容不同；請先檢查資料，未寫入進度。")
    else:
        atomic_write(backup, previous)
    data = (json.dumps(progress, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    atomic_write(PROGRESS, data)
    print("已保存進度 revision %d。" % revision)


def lesson_state(catalog, progress, lesson_id):
    lesson = next((item for item in catalog["lessons"] if item["id"] == lesson_id), None)
    if lesson is None or lesson_id not in progress["lessons"]:
        raise ValueError("找不到單元：" + lesson_id)
    state = progress["lessons"][lesson_id]
    if not isinstance(state.get("completedSteps"), list) or not isinstance(state.get("notes"), list):
        raise ValueError("單元的 completedSteps / notes 格式錯誤。")
    return lesson, state


def status(catalog, progress, args):
    lesson_id = args.lesson or progress["activeLesson"]
    lesson, state = lesson_state(catalog, progress, lesson_id)
    print("進度 revision %d｜更新：%s" % (progress["revision"], progress["updatedAt"]))
    print("單元 %s：%s｜%s" % (lesson_id, lesson["title"], state["status"]))
    print("工作區：" + state["workspace"])
    print("Blender 介面語言：" + (learner_state(progress).get("interfaceLanguage") or "尚未記錄"))
    step = next((item for item in lesson["steps"] if item["id"] == state["currentStep"]), None)
    if state["status"] == "completed":
        print("本單元已由學習者逐步確認完成。")
    elif step:
        print("目前步驟 %s：%s" % (step["id"], step["title"]))
        print("操作：" + step["action"])
        print("成功畫面：" + step["success"])
    else:
        raise ValueError("目前步驟不存在於 catalog.json。")
    print("已確認：%d / %d 步｜已登錄檔案：%d" % (
        len(state["completedSteps"]), len(lesson["steps"]),
        sum(item.get("lesson") == lesson_id for item in progress["fileVersions"])))
    if state["notes"]:
        latest = state["notes"][-1]
        if not isinstance(latest, dict):
            latest = {"text": str(latest)}
        author = {"learner": "學員", "tutor": "助教"}.get(latest.get("author"), "未標示作者")
        print("最近筆記（%s）：%s" % (author, latest.get("text", "")))


def learner_state(progress):
    learner = progress.setdefault("learner", {})
    if not isinstance(learner, dict):
        raise ValueError("progress.json 的 learner 必須是物件。")
    return learner


def learner_updates(values):
    """只接受 LEARNER_CHOICES 明列的欄位與值，避免 catalog 或命令列寫入任意設定。"""
    if not isinstance(values, dict):
        raise ValueError("setsLearner 必須是物件。")
    for key, value in values.items():
        if value not in LEARNER_CHOICES.get(key, ()):
            raise ValueError("不支援的學員設定：%s=%s" % (key, value))
    return dict(values)


def confirm(catalog, progress, args):
    lesson, state = lesson_state(catalog, progress, args.lesson)
    if args.lesson != progress["activeLesson"]:
        raise ValueError("只能確認目前 activeLesson 的步驟。")
    if state["status"] == "completed" or args.step != state["currentStep"]:
        raise ValueError("只能確認目前尚未完成的 currentStep。")
    step_ids = [step["id"] for step in lesson["steps"]]
    if args.step not in step_ids or args.step in state["completedSteps"]:
        raise ValueError("步驟不存在或已確認。")
    position = step_ids.index(args.step)
    if any(step_id not in state["completedSteps"] for step_id in step_ids[:position]):
        raise ValueError("前面的步驟尚未確認；請先檢查進度。")
    evidence = args.evidence.strip()
    if not evidence:
        raise ValueError("--evidence 必須提供學習者的畫面／操作確認文字。")
    learner = learner_updates(lesson["steps"][position].get("setsLearner", {}))
    learner_state(progress).update(learner)
    state["completedSteps"].append(args.step)
    state["status"] = "in_progress"
    if position + 1 < len(step_ids):
        state["currentStep"] = step_ids[position + 1]
    else:
        state["status"] = "completed"
        state["currentStep"] = None
        ids = [item["id"] for item in catalog["lessons"]]
        for next_id in ids[ids.index(args.lesson) + 1:]:
            next_state = progress["lessons"][next_id]
            if next_state["status"] != "completed":
                progress["activeLesson"] = next_id
                next_state["status"] = "in_progress"
                break
    event = {"type": "learner_confirmed", "lesson": args.lesson,
             "step": args.step, "evidence": evidence}
    if learner:
        event["learner"] = learner
    return event


def set_interface_language(progress, args):
    """更正學員的介面語言；只記設定，不確認任何步驟。"""
    updates = learner_updates({"interfaceLanguage": args.language})
    evidence = args.evidence.strip()
    if not evidence:
        raise ValueError("--evidence 必須提供學習者的畫面或口頭回報。")
    learner = learner_state(progress)
    previous = learner.get("interfaceLanguage")
    if previous == args.language:
        print("介面語言已是 %s；未變更進度。" % args.language)
        return None
    learner.update(updates)
    return {"type": "learner_updated", "field": "interfaceLanguage",
            "from": previous, "to": args.language, "evidence": evidence}


def workspace_file(value):
    """路徑必須是專案相對路徑，解析連結後也必須留在工作區。"""
    relative = Path(value.replace("\\", "/"))
    if relative.is_absolute() or PureWindowsPath(value).drive or ".." in relative.parts:
        raise ValueError("請使用不含 .. 的專案相對路徑。")
    resolved = (PROJECT / relative).resolve(strict=True)
    try:
        resolved.relative_to(PROJECT)
        resolved.relative_to((LEARNING / "workspaces").resolve())
    except ValueError:
        raise ValueError("檔案必須位於專案內的 learning/workspaces。") from None
    if not resolved.is_file():
        raise ValueError("指定路徑必須是已存在的檔案。")
    return resolved, resolved.relative_to(PROJECT).as_posix()


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(handle.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("讀取時檔案正在變更；請等待儲存完成再登錄。")
    return {"sha256": digest.hexdigest(), "bytes": after.st_size,
            "modifiedAt": datetime.fromtimestamp(after.st_mtime, TAIPEI).isoformat(timespec="seconds")}


def path_key(value):
    return os.path.normcase(os.path.normpath(value.replace("\\", "/")))


def register_file(catalog, progress, args):
    if args.role not in ("source_scene", "render", "export"):
        raise ValueError("role 必須是 source_scene、render 或 export。")
    _, state = lesson_state(catalog, progress, args.lesson)
    path, relative = workspace_file(args.path)
    workspace = (PROJECT / state["workspace"]).resolve()
    try:
        path.relative_to(workspace)
    except ValueError:
        raise ValueError("檔案必須屬於指定單元的工作區：" + state["workspace"]) from None
    source = None
    if args.role == "source_scene":
        if path.suffix.lower() != ".blend":
            raise ValueError("source_scene 必須是 .blend 檔。")
        if args.source:
            raise ValueError("source_scene 不使用 --source。")
    else:
        if not args.source:
            raise ValueError("render / export 必須指定 --source，連結已登錄的 .blend。")
        source_path, source_relative = workspace_file(args.source)
        registered = next((item for item in progress["fileVersions"]
                           if path_key(item["path"]) == path_key(source_relative)
                           and item["role"] == "source_scene"
                           and item["lesson"] == args.lesson), None)
        if registered is None or source_path.suffix.lower() != ".blend":
            raise ValueError("來源 .blend 必須先登錄為同單元的 source_scene。")
        source_hash = fingerprint(source_path)["sha256"]
        if source_hash != registered["sha256"]:
            raise ValueError("來源 .blend 內容已改變；請另存新版、登錄後再關聯成果。")
        source = {"path": source_relative, "sha256": source_hash}
    details = fingerprint(path)
    existing = next((item for item in progress["fileVersions"]
                     if path_key(item["path"]) == path_key(relative)), None)
    if existing:
        if existing["sha256"] != details["sha256"]:
            raise ValueError("此路徑已登錄不同內容；請另存新版本檔名，禁止覆寫既有版本。")
        old_source = existing.get("source")
        same_source = old_source is None and source is None
        if isinstance(old_source, dict) and isinstance(source, dict):
            same_source = (path_key(old_source.get("path", "")) == path_key(source["path"])
                           and old_source.get("sha256") == source["sha256"])
        if existing.get("role") != args.role or not same_source:
            raise ValueError("此路徑已登錄不同用途或來源；請使用新的版本檔名，不能更改既有版本關聯。")
        print("相同路徑與 SHA256 已登錄；未變更進度。")
        return None
    record = dict(details, path=relative, role=args.role, lesson=args.lesson,
                  registeredAt=now(), revision=progress["revision"] + 1)
    if source:
        record["source"] = source
    progress["fileVersions"].append(record)
    return {"type": "file_registered", "lesson": args.lesson,
            "path": relative, "sha256": details["sha256"], "role": args.role}


def add_note(catalog, progress, args):
    """網頁和 CLI 共用筆記格式；兼容原有只有 at/text 的筆記。"""
    _, state = lesson_state(catalog, progress, args.lesson)
    text = args.note.strip()
    if not text or len(text) > 12000:
        raise ValueError("筆記須為 1–12000 字。")
    note_kind = getattr(args, "note_kind", "note")
    if note_kind not in ("note", "stuck"):
        raise ValueError("noteKind 必須是 note 或 stuck。")
    step_id = getattr(args, "step", None) or state["currentStep"]
    if step_id != state["currentStep"]:
        raise ValueError("筆記請對應此單元目前的 currentStep。")
    author = getattr(args, "author", "tutor")
    if author not in NOTE_AUTHORS:
        raise ValueError("author 必須是 learner 或 tutor。")
    note = {"at": now(), "text": text, "noteKind": note_kind, "author": author}
    event = {"type": "note_added", "lesson": args.lesson,
             "text": text, "noteKind": note_kind, "author": author}
    if step_id:
        note["step"] = step_id
        event["step"] = step_id
    state["notes"].append(note)
    return event


def add_lessons(catalog, progress, args):
    """catalog 新增單元後，替進度補上尚未開始的單元與工作區；不改動既有單元。"""
    reason = args.reason.strip()
    if not reason:
        raise ValueError("--reason 必須說明加入單元的依據。")
    added = []
    for lesson in catalog["lessons"]:
        lesson_id = lesson.get("id")
        if lesson_id in progress["lessons"]:
            continue
        if not isinstance(lesson_id, str) or len(lesson_id) != 2 or not lesson_id.isdigit():
            raise ValueError("單元 ID 必須是兩位數字：%r" % lesson_id)
        if not lesson.get("steps"):
            raise ValueError("單元 %s 沒有步驟。" % lesson_id)
        (LEARNING / "workspaces" / lesson_id).mkdir(parents=True, exist_ok=True)
        progress["lessons"][lesson_id] = {
            "status": "not_started", "currentStep": lesson["steps"][0]["id"], "completedSteps": [],
            "notes": [], "workspace": "learning/workspaces/" + lesson_id}
        added.append(lesson_id)
    if not added:
        print("catalog 的單元都已在進度中；未變更進度。")
        return None
    # 目前單元已全部完成時，接到第一個新單元。
    active = progress["lessons"].get(progress["activeLesson"], {})
    if active.get("status") == "completed":
        progress["activeLesson"] = added[0]
        progress["lessons"][added[0]]["status"] = "in_progress"
    return {"type": "lessons_added", "lessons": added, "reason": reason}


def mutate(action, lesson, revision, **values):
    """唯一寫入入口：CLI 與 HTTP 都在同一 OS 鎖下檢查 revision。"""
    if type(revision) is not int or revision < 1:
        raise ValueError("expectedRevision 必須是正整數。")
    if action not in ("set_interface_language", "add_lessons") and not isinstance(lesson, str):
        raise ValueError("lessonId 必須是字串。")
    args = SimpleNamespace(lesson=lesson, **values)
    with progress_lock():
        catalog, progress = load_state()
        previous = PROGRESS.read_bytes()
        if revision != progress["revision"]:
            raise RevisionConflict("revision 已變更：目前是 %d；請重新讀取進度。" % progress["revision"])
        if action == "confirm_step":
            if not isinstance(getattr(args, "evidence", None), str) or len(args.evidence) > 12000:
                raise ValueError("evidence 必須是 1–12000 字的確認文字。")
            event = confirm(catalog, progress, args)
        elif action == "register_file":
            if not isinstance(getattr(args, "path", None), str):
                raise ValueError("path 必須是字串。")
            args.source = getattr(args, "source", None)
            if args.source is not None and not isinstance(args.source, str):
                raise ValueError("source 必須是字串。")
            event = register_file(catalog, progress, args)
        elif action == "add_note":
            if not isinstance(getattr(args, "note", None), str):
                raise ValueError("note 必須是字串。")
            event = add_note(catalog, progress, args)
        elif action == "set_interface_language":
            if not isinstance(getattr(args, "evidence", None), str) or len(args.evidence) > 12000:
                raise ValueError("evidence 必須是 1–12000 字的確認文字。")
            event = set_interface_language(progress, args)
        elif action == "add_lessons":
            if not isinstance(getattr(args, "reason", None), str) or len(args.reason) > 12000:
                raise ValueError("reason 必須是 1–12000 字的說明。")
            event = add_lessons(catalog, progress, args)
        else:
            raise ValueError("不支援的操作。")
        if event is not None:
            commit(progress, previous, event)
        return progress


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    status_parser = commands.add_parser("status", help="讀取目前步驟與成功畫面")
    status_parser.add_argument("--lesson", help="單元 ID；預設目前單元")
    for name, help_text in (("note", "新增筆記，不確認完成"),
                            ("confirm", "依學習者提供的證據確認目前步驟"),
                            ("register-file", "盤點已存在的工作檔，不確認完成")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--lesson", required=True)
        command.add_argument("--revision", required=True, type=int, help="status 顯示的目前 revision")
        if name == "note":
            command.add_argument("--note-file", required=True, help="UTF-8 筆記檔路徑")
            command.add_argument("--note-kind", default="note", choices=("note", "stuck"))
            command.add_argument("--author", default="tutor", choices=NOTE_AUTHORS,
                                 help="預設 tutor；只有記錄學員原話時才用 learner")
            command.add_argument("--step", help="目前步驟 ID；預設 currentStep")
        elif name == "confirm":
            command.add_argument("--step", required=True)
            command.add_argument("--evidence", required=True, help="學習者的畫面或操作確認文字")
        else:
            command.add_argument("--path", required=True, help="專案相對路徑")
            command.add_argument("--role", required=True, choices=("source_scene", "render", "export"))
            command.add_argument("--source", help="render / export 的來源 .blend 專案相對路徑")
    language = commands.add_parser("set-interface-language", help="更正 Blender 介面語言，不確認步驟")
    language.add_argument("--revision", required=True, type=int, help="status 顯示的目前 revision")
    language.add_argument("--language", required=True, choices=LEARNER_CHOICES["interfaceLanguage"])
    language.add_argument("--evidence", required=True, help="學習者的畫面或口頭回報")
    lessons = commands.add_parser("add-lessons", help="catalog 新增單元後補進進度與工作區，不確認步驟")
    lessons.add_argument("--revision", required=True, type=int, help="status 顯示的目前 revision")
    lessons.add_argument("--reason", required=True, help="加入單元的依據，例如學員核准的草案")
    return parser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "status":
            catalog, progress = load_state()
            status(catalog, progress, args)
            return
        if args.command == "confirm":
            mutate("confirm_step", args.lesson, args.revision,
                   step=args.step, evidence=args.evidence)
        elif args.command == "register-file":
            mutate("register_file", args.lesson, args.revision,
                   path=args.path, role=args.role, source=args.source)
        elif args.command == "set-interface-language":
            mutate("set_interface_language", None, args.revision,
                   language=args.language, evidence=args.evidence)
        elif args.command == "add-lessons":
            mutate("add_lessons", None, args.revision, reason=args.reason)
        else:
            mutate("add_note", args.lesson, args.revision,
                   note=Path(args.note_file).read_text(encoding="utf-8-sig"),
                   note_kind=args.note_kind, step=args.step, author=args.author)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
