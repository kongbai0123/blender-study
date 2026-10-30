#!/usr/bin/env python3
"""以單一 progress.json 維護 Blender 學習進度與不可覆寫的檔案版本。"""

import argparse
import hashlib
import json
import os
import re
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
# 新版工程教材只在這裡指定目前版本；伺服器以固定網址提供，網頁不寫版本號。
ENGINEERING_CURRICULUM = LEARNING / "web" / "engineering-curriculum-v041.json"
ENGINEERING_PATH = LEARNING / "web" / "engineering-path-v007.json"
CHALLENGES = LEARNING / "web" / "challenges" / "challenges-v010.json"
# 工程章節共用的個人工作區；不屬於原 01～09 單元，登記檔案時以 --workspace 指定。
ENGINEERING_WORKSPACES = {"engineering-parametric": "learning/workspaces/engineering-parametric"}
# 受控尺寸面板只接受這個示範手工盒的副本（面板固定其草圖約束 UID 與上蓋拓撲簽章）。
MANUAL_BOX_BASE = ("learning/evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend",
                   "ddae8a3d3745146501d25527354352e6b71431b837c78c8269a43dc5e6a3dec6")
# 2026-10-27 工程路徑第一題的回答在專用事件出現前記在原教材 01-01：學員原話一則，緊接一則
# 第一行為 engineering:<activity>:answered 的助教標記。兩則都屬工程路徑，不當成原教材步驟的筆記。
LEGACY_ENGINEERING_MARKER = re.compile(r"engineering:(path-[a-z0-9-]+):answered")
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


def engineering_overview(progress):
    """新版主線（不含選修、待製作、速查與附錄）的確認數與下一小步；教材讀不到時回傳 None。"""
    try:
        curriculum = read_json(ENGINEERING_CURRICULUM)
    except (OSError, ValueError):
        return None
    confirmed = {(event.get("chapterId"), event.get("stepId")) for event in progress["events"]
                 if isinstance(event, dict) and event.get("type") == "engineering_step_confirmed"
                 and event.get("curriculumId") == curriculum.get("id")}
    total, done, upcoming = 0, 0, None
    for chapter in curriculum.get("chapters", []):
        sections = {section.get("id"): section for section in chapter.get("sections", []) if isinstance(section, dict)}
        for step in chapter.get("steps", []):
            if not isinstance(step, dict) or step.get("track"):
                continue
            total += 1
            if (chapter.get("id"), step.get("id")) in confirmed:
                done += 1
            elif upcoming is None:
                upcoming = (chapter, sections.get(step.get("section")), step)
    return {"total": total, "done": done, "next": upcoming}


def status(catalog, progress, args):
    if not args.lesson:
        overview = engineering_overview(progress)
        if overview is not None:
            engineering_status_summary(progress, overview)
            return
        print("讀不到新版教材（%s）；以下暫以原教材目前單元顯示。" % ENGINEERING_CURRICULUM.name)
    lesson_id = args.lesson or progress["activeLesson"]
    lesson, state = lesson_state(catalog, progress, lesson_id)
    print("原教材（只供查閱）· 進度 revision %d｜更新：%s" % (progress["revision"], progress["updatedAt"]))
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
    legacy = legacy_engineering_notes(progress)
    notes = [note for index, note in enumerate(state["notes"]) if (lesson_id, index) not in legacy]
    if notes:
        latest = notes[-1]
        if not isinstance(latest, dict):
            latest = {"text": str(latest)}
        author = {"learner": "學員", "tutor": "助教"}.get(latest.get("author"), "未標示作者")
        print("最近筆記（%s）：%s" % (author, latest.get("text", "")))
    if any(key[0] == lesson_id for key in legacy):
        print("另有工程路徑的舊格式回答記在本單元；以 engineering-status 查看，不算本單元筆記。")


def engineering_status_summary(progress, overview):
    """預設的 status：學習進度以新版小步為主，原教材只供查閱。"""
    print("進度 revision %d｜更新：%s" % (progress["revision"], progress["updatedAt"]))
    print("新版主線：%d / %d 小步已確認（選修、待製作、第 00 章速查與附錄不計入）" % (overview["done"], overview["total"]))
    pilot_status_summary(progress)
    if overview["next"] is None:
        print("主線小步都已確認。")
    else:
        chapter, section, step = overview["next"]
        where = "第 %s 章 %s" % (chapter.get("number") or chapter["id"][2:], chapter.get("title", ""))
        if section:
            where += " › %s %s" % (section.get("id"), section.get("title", ""))
        print("下一小步 %s：%s › %s" % (step["id"], where, step.get("title", "")))
        if step.get("goal"):
            print("小目標：" + step["goal"])
        for number, action in enumerate(step.get("actions", []), 1):
            print("操作 %d：%s" % (number, action))
        if step.get("success"):
            print("成功畫面：" + step["success"])
        for record in legacy_engineering_records(progress):
            if record["role"] == "answer" and record["activity"] == step.get("legacyActivity"):
                note = progress["lessons"][record["lessonId"]]["notes"][record["noteIndex"]]
                print("學員先前在聊天的回答（尚未確認本步）：" + note["text"])
    print("Blender 介面語言：" + (learner_state(progress).get("interfaceLanguage") or "尚未記錄"))
    print("原教材只供查閱；以 status --lesson <單元> 查看原單元內容與舊紀錄。")


def legacy_engineering_notes(progress):
    """回傳 {(單元, 筆記索引): {"activity", "role"}}；只認標記及其前一則同時間、同步驟的學員原話。"""
    found = {}
    for lesson_id, state in progress["lessons"].items():
        notes = state.get("notes") if isinstance(state, dict) else None
        if not isinstance(notes, list):
            continue
        for index, note in enumerate(notes):
            if not isinstance(note, dict) or note.get("author") != "tutor" or not isinstance(note.get("text"), str):
                continue
            match = LEGACY_ENGINEERING_MARKER.fullmatch(note["text"].split("\n", 1)[0].strip())
            if not match:
                continue
            found[(lesson_id, index)] = {"activity": match.group(1), "role": "marker"}
            previous = notes[index - 1] if index else None
            if (isinstance(previous, dict) and previous.get("author") == "learner"
                    and previous.get("at") == note.get("at") and previous.get("step") == note.get("step")):
                found[(lesson_id, index - 1)] = {"activity": match.group(1), "role": "answer"}
    return found


def legacy_engineering_records(progress):
    """供網頁使用的清單形式：哪一則原教材筆記其實是工程路徑的回答或標記。"""
    return [dict(info, lessonId=lesson_id, noteIndex=index)
            for (lesson_id, index), info in sorted(legacy_engineering_notes(progress).items())]


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


def file_owner(catalog, progress, args):
    """登記對象是原教材單元或工程工作區，二擇一；回傳紀錄欄位與工作區相對路徑。"""
    workspace_id = getattr(args, "workspace", None)
    if workspace_id is None:
        _, state = lesson_state(catalog, progress, args.lesson)
        return {"lesson": args.lesson}, state["workspace"]
    if args.lesson is not None:
        raise ValueError("單元與工程工作區只能擇一。")
    if workspace_id not in ENGINEERING_WORKSPACES:
        raise ValueError("不支援的工程工作區：%s" % workspace_id)
    return {"workspace": workspace_id}, ENGINEERING_WORKSPACES[workspace_id]


def register_file(catalog, progress, args):
    if args.role not in ("source_scene", "render", "export"):
        raise ValueError("role 必須是 source_scene、render 或 export。")
    owner, workspace_path = file_owner(catalog, progress, args)
    path, relative = workspace_file(args.path)
    workspace = (PROJECT / workspace_path).resolve()
    try:
        path.relative_to(workspace)
    except ValueError:
        raise ValueError("檔案必須屬於指定的工作區：" + workspace_path) from None
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
                           and all(item.get(key) == value for key, value in owner.items())), None)
        if registered is None or source_path.suffix.lower() != ".blend":
            raise ValueError("來源 .blend 必須先登錄為同一工作區的 source_scene。")
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
    record = dict(details, path=relative, role=args.role, **owner,
                  registeredAt=now(), revision=progress["revision"] + 1)
    if source:
        record["source"] = source
    progress["fileVersions"].append(record)
    return {"type": "file_registered", **owner,
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


def engineering_step(chapter_id, step_id):
    """Validate both IDs against the current versioned engineering curriculum."""
    if not isinstance(chapter_id, str) or not isinstance(step_id, str):
        raise ValueError("chapterId 與 stepId 必須是字串。")
    curriculum = read_json(ENGINEERING_CURRICULUM)
    if curriculum.get("schemaVersion") != 1 or not isinstance(curriculum.get("chapters"), list):
        raise ValueError("工程教材格式錯誤。")
    curriculum_id = curriculum.get("id")
    if not isinstance(curriculum_id, str) or not curriculum_id:
        raise ValueError("工程教材缺少版本 ID。")
    matches = [c for c in curriculum["chapters"] if isinstance(c, dict) and c.get("id") == chapter_id]
    if len(matches) != 1 or not isinstance(matches[0].get("steps"), list):
        raise ValueError("找不到工程章節。")
    steps = [s for s in matches[0]["steps"] if isinstance(s, dict) and s.get("id") == step_id]
    if len(steps) != 1:
        raise ValueError("找不到此工程章節中的步驟。")
    return curriculum_id, matches[0], steps[0]


def engineering_event(progress, args, *, confirmed):
    curriculum_id, _, step = engineering_step(getattr(args, "chapter", None), getattr(args, "step", None))
    event = {"type": "engineering_step_confirmed" if confirmed else "engineering_step_note",
             "curriculumId": curriculum_id, "chapterId": args.chapter, "stepId": args.step}
    if confirmed and step.get("track") == "appendix":
        raise ValueError("附錄是開發與驗證紀錄，不需要也不能確認完成。")
    if confirmed and step.get("track") == "pending":
        raise ValueError("這一小步標為待製作：所需的模型或示範還沒完成，不能確認完成。")
    if confirmed and step.get("track") == "reference":
        raise ValueError("這是第 00 章的速查卡，只供閱讀與查找，不需要也不能確認；正式練習在卡片列出的小步。")
    if confirmed:
        evidence = getattr(args, "evidence", None)
        if not isinstance(evidence, str) or not evidence.strip() or len(evidence) > 12000:
            raise ValueError("evidence 必須是 1–12000 字的學員確認文字。")
        if any(isinstance(previous, dict) and previous.get("type") == event["type"]
               and previous.get("curriculumId") == curriculum_id
               and previous.get("chapterId") == args.chapter and previous.get("stepId") == args.step
               for previous in progress["events"]):
            raise ValueError("此工程步驟已確認，未重複記錄。")
        event.update(author="learner", evidence=evidence)
    else:
        note = getattr(args, "note", None)
        if not isinstance(note, str) or not note.strip() or len(note) > 12000:
            raise ValueError("note 必須是 1–12000 字的筆記。")
        note_kind = getattr(args, "note_kind", "note")
        author = getattr(args, "author", "tutor")
        if note_kind not in ("note", "stuck"):
            raise ValueError("noteKind 必須是 note 或 stuck。")
        if author not in NOTE_AUTHORS:
            raise ValueError("author 必須是 learner 或 tutor。")
        # Keep whitespace and line breaks exactly as supplied by the learner.
        event.update(author=author, noteKind=note_kind, text=note)
    return event


PILOT_CHALLENGE_ID = "box-opening-v001"


def pilot_events(progress):
    return [event for event in progress["events"] if isinstance(event, dict)
            and event.get("challengeId") == PILOT_CHALLENGE_ID
            and event.get("type") in ("pilot_challenge_confirmed", "pilot_challenge_note")]


def pilot_status_summary(progress):
    events = pilot_events(progress)
    confirmed = any(event.get("type") == "pilot_challenge_confirmed" for event in events)
    print("小盒試教題：%s（與主線小步分開；pilot-status 查看紀錄）" % ("學員已確認" if confirmed else "尚未由學員確認"))


def pilot_event(progress, args, *, confirmed):
    if getattr(args, "challenge", None) != PILOT_CHALLENGE_ID:
        raise ValueError("找不到此試教題。")
    event = {"challengeId": PILOT_CHALLENGE_ID}
    if confirmed:
        evidence = getattr(args, "evidence", None)
        if not isinstance(evidence, str) or not evidence.strip() or len(evidence) > 12000:
            raise ValueError("evidence 必須是 1–12000 字的學員確認文字。")
        if any(item.get("type") == "pilot_challenge_confirmed" for item in pilot_events(progress)):
            raise ValueError("此試教題已確認，未重複記錄。")
        event.update(type="pilot_challenge_confirmed", author="learner", evidence=evidence)
        source = getattr(args, "source_path", None)
        if source is not None:
            if not isinstance(source, str) or not source.strip():
                raise ValueError("sourcePath 必須是已登記的 .blend 路徑或留空。")
            source_path, source_relative = workspace_file(source)
            registered = next((item for item in progress["fileVersions"]
                               if item.get("lesson") == "04" and item.get("role") == "source_scene"
                               and path_key(item.get("path", "")) == path_key(source_relative)), None)
            if registered is None or source_path.suffix.lower() != ".blend":
                raise ValueError("請選擇已在原盒工作區登記的 .blend。")
            actual = fingerprint(source_path)["sha256"]
            if actual != registered.get("sha256"):
                raise ValueError("已登記的 .blend 內容已改變；請另存新版並重新登記。")
            event.update(sourcePath=source_relative, sourceSha256=actual)
    else:
        note = getattr(args, "note", None)
        author = getattr(args, "author", "tutor")
        if not isinstance(note, str) or not note.strip() or len(note) > 12000:
            raise ValueError("note 必須是 1–12000 字的筆記。")
        if author not in NOTE_AUTHORS:
            raise ValueError("author 必須是 learner 或 tutor。")
        event.update(type="pilot_challenge_note", author=author, noteKind="stuck", text=note)
    return event


def challenge_definition(challenge_id):
    """唯讀版本化題目資料；03 保留原小盒 pilot，不建立第二份確認。"""
    if not isinstance(challenge_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,100}", challenge_id):
        raise ValueError("challengeId 格式不正確。")
    data = read_json(CHALLENGES)
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or not isinstance(data.get("chapters"), list):
        raise ValueError("題目資料格式不正確。")
    matches = [item for item in data["chapters"] if isinstance(item, dict)
               and item.get("challengeId") == challenge_id]
    if len(matches) != 1:
        raise ValueError("找不到唯一的挑戰題。")
    item = matches[0]
    if item.get("chapterId") == "ch03" or challenge_id == PILOT_CHALLENGE_ID:
        raise ValueError("第 03 章小盒題使用原有 pilot 進度。")
    if not isinstance(item.get("chapterId"), str) or not re.fullmatch(r"ch(?:0[1-9]|1[0-2])", item["chapterId"]):
        raise ValueError("題目章節代號不正確。")
    owner = item.get("workspaceLesson")
    if owner is not None and (not isinstance(owner, str) or not re.fullmatch(r"0[1-9]", owner)):
        raise ValueError("題目工作區設定不正確。")
    workspace_id = item.get("workspaceId")
    if workspace_id is not None and (not isinstance(workspace_id, str) or workspace_id not in ENGINEERING_WORKSPACES):
        raise ValueError("題目工程工作區設定不正確。")
    if owner is not None and workspace_id is not None:
        raise ValueError("題目不能同時指定單元與工程工作區。")
    return item


def challenge_events(progress, challenge_id=None):
    return [event for event in progress["events"] if isinstance(event, dict)
            and event.get("type") in ("challenge_confirmed", "challenge_note")
            and (challenge_id is None or event.get("challengeId") == challenge_id)]


def challenge_event(progress, args, *, confirmed):
    challenge = challenge_definition(getattr(args, "challenge", None))
    challenge_id, owner = challenge["challengeId"], challenge.get("workspaceLesson")
    workspace_id = challenge.get("workspaceId")
    event = {"challengeId": challenge_id, "chapterId": challenge["chapterId"]}
    if confirmed:
        evidence = getattr(args, "evidence", None)
        if not isinstance(evidence, str) or not evidence.strip() or len(evidence) > 12000:
            raise ValueError("evidence 必須是 1–12000 字的學員確認文字。")
        if any(item.get("type") == "challenge_confirmed" for item in challenge_events(progress, challenge_id)):
            raise ValueError("此挑戰題已確認，未重複記錄。")
        event.update(type="challenge_confirmed", author="learner", evidence=evidence)
        source = getattr(args, "source_path", None)
        if source is not None:
            if not owner and not workspace_id:
                raise ValueError("此題沒有指定檔案工作區，無法關聯版本。")
            if not isinstance(source, str) or not source.strip():
                raise ValueError("sourcePath 必須是已登記的 .blend 路徑或留空。")
            path, relative = workspace_file(source)
            expected_workspace = (PROJECT / (ENGINEERING_WORKSPACES[workspace_id] if workspace_id
                                  else progress["lessons"][owner]["workspace"])).resolve()
            try:
                expected_workspace.relative_to((LEARNING / "workspaces").resolve())
                path.relative_to(expected_workspace)
            except ValueError:
                raise ValueError("所選檔案不在此題的工作區。") from None
            registered = next((item for item in progress["fileVersions"]
                               if (item.get("workspace") == workspace_id if workspace_id
                                   else item.get("lesson") == owner)
                               and item.get("role") == "source_scene"
                               and path_key(item.get("path", "")) == path_key(relative)), None)
            if registered is None or path.suffix.lower() != ".blend":
                raise ValueError("請選擇此題工作區已登記的 .blend。")
            actual = fingerprint(path)["sha256"]
            if actual != registered.get("sha256"):
                raise ValueError("已登記的 .blend 內容已改變；請另存新版並重新登記。")
            event.update(sourcePath=relative, sourceSha256=actual)
    else:
        note, author = getattr(args, "note", None), getattr(args, "author", "tutor")
        if not isinstance(note, str) or not note.strip() or len(note) > 12000:
            raise ValueError("note 必須是 1–12000 字的筆記。")
        if author not in NOTE_AUTHORS:
            raise ValueError("author 必須是 learner 或 tutor。")
        event.update(type="challenge_note", author=author, noteKind="stuck", text=note)
    return event


def _is_link(path):
    info = os.lstat(path)
    return os.path.islink(path) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def engineering_workspace(copy_name=None):
    """建立工程工作區，可選擇以雜湊核對後複製示範手工盒；不寫入進度、不覆寫既有檔案。"""
    folder = PROJECT / ENGINEERING_WORKSPACES["engineering-parametric"]
    if os.path.lexists(folder) and (_is_link(folder) or not folder.is_dir()):
        raise ValueError("工程工作區必須是一般資料夾，不可是連結或檔案：" + str(folder))
    folder.mkdir(parents=True, exist_ok=True)
    try:
        folder.resolve().relative_to((LEARNING / "workspaces").resolve())
    except ValueError:
        raise ValueError("工程工作區解析後不在 learning/workspaces 內。") from None
    print("工程工作區：" + str(folder.resolve()))
    if copy_name is None:
        return None
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,80}\.blend", copy_name) or ".." in copy_name:
        raise ValueError("副本檔名只能使用英數、底線、連字號與點，並以 .blend 結尾。")
    data = (PROJECT / MANUAL_BOX_BASE[0]).read_bytes()
    if hashlib.sha256(data).hexdigest() != MANUAL_BOX_BASE[1]:
        raise ValueError("示範手工盒內容與紀錄不符；未複製。")
    target = folder / copy_name
    try:
        with target.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        raise ValueError("目標檔已存在；請換新檔名，不覆寫既有檔案。") from None
    print("個人副本：%s\nSHA-256：%s（與示範基準相同，尚未修改）" % (target.resolve(), MANUAL_BOX_BASE[1]))
    return target


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
    lesson_optional = action in ("set_interface_language", "add_lessons", "engineering_confirm", "engineering_note", "pilot_confirm", "pilot_note", "challenge_confirm", "challenge_note") or (
        action == "register_file" and values.get("workspace") is not None)
    if not lesson_optional and not isinstance(lesson, str):
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
            args.workspace = getattr(args, "workspace", None)
            if args.workspace is not None and not isinstance(args.workspace, str):
                raise ValueError("workspace 必須是字串。")
            event = register_file(catalog, progress, args)
        elif action == "add_note":
            if not isinstance(getattr(args, "note", None), str):
                raise ValueError("note 必須是字串。")
            event = add_note(catalog, progress, args)
        elif action in ("engineering_confirm", "engineering_note"):
            event = engineering_event(progress, args, confirmed=action == "engineering_confirm")
        elif action in ("pilot_confirm", "pilot_note"):
            event = pilot_event(progress, args, confirmed=action == "pilot_confirm")
        elif action in ("challenge_confirm", "challenge_note"):
            event = challenge_event(progress, args, confirmed=action == "challenge_confirm")
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
        if name == "register-file":
            owner = command.add_mutually_exclusive_group(required=True)
            owner.add_argument("--lesson")
            owner.add_argument("--workspace", choices=sorted(ENGINEERING_WORKSPACES), help="工程章節的個人工作區")
        else:
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
    eng_status = commands.add_parser("engineering-status", help="只讀工程教材確認及筆記事件")
    eng_status.add_argument("--chapter", help="篩選工程章節 ID，例如 ch01")
    eng_workspace = commands.add_parser("engineering-workspace", help="建立工程工作區；可複製受控面板用的示範手工盒，不寫入進度")
    eng_workspace.add_argument("--copy-manual-box", metavar="檔名.blend", help="在工作區建立示範手工盒的新副本；同名檔存在時拒絕")
    commands.add_parser("pilot-status", help="只讀小盒試教題的確認與筆記")
    pilot_confirm = commands.add_parser("pilot-confirm", help="記錄學員對小盒試教題的明確完成回報")
    pilot_confirm.add_argument("--revision", required=True, type=int)
    pilot_confirm.add_argument("--evidence", required=True, help="學員明確確認的原話")
    pilot_confirm.add_argument("--source-path", help="選填已登記的原盒 .blend 路徑")
    pilot_note = commands.add_parser("pilot-note", help="記錄小盒試教題卡關筆記")
    pilot_note.add_argument("--revision", required=True, type=int)
    pilot_note.add_argument("--note-file", required=True, help="保留原始內容的 UTF-8 筆記檔")
    pilot_note.add_argument("--author", default="tutor", choices=NOTE_AUTHORS,
                            help="只有逐字記學員原話時才用 learner")
    challenge_status = commands.add_parser("challenge-status", help="只讀挑戰題確認與筆記")
    challenge_status.add_argument("--challenge", help="只顯示指定題目 ID")
    challenge_confirm = commands.add_parser("challenge-confirm", help="記錄學員對挑戰題的明確完成回報")
    challenge_confirm.add_argument("--challenge", required=True)
    challenge_confirm.add_argument("--revision", required=True, type=int)
    challenge_confirm.add_argument("--evidence", required=True, help="學員明確確認的原話")
    challenge_confirm.add_argument("--source-path", help="選填已登記的對應工作區 .blend")
    challenge_note = commands.add_parser("challenge-note", help="記錄挑戰題卡關筆記")
    challenge_note.add_argument("--challenge", required=True)
    challenge_note.add_argument("--revision", required=True, type=int)
    challenge_note.add_argument("--note-file", required=True, help="保留原始內容的 UTF-8 筆記檔")
    challenge_note.add_argument("--author", default="tutor", choices=NOTE_AUTHORS,
                                help="只有逐字記學員原話時才用 learner")
    for name in ("engineering-confirm", "engineering-note"):
        command = commands.add_parser(name, help="記錄工程步驟確認" if name.endswith("confirm") else "記錄工程步驟筆記")
        command.add_argument("--revision", required=True, type=int)
        command.add_argument("--chapter", required=True)
        command.add_argument("--step", required=True)
        if name.endswith("confirm"):
            command.add_argument("--evidence", required=True, help="學員明確確認的原話")
        else:
            command.add_argument("--note-file", required=True, help="保留原始內容的 UTF-8 筆記檔")
            command.add_argument("--note-kind", default="note", choices=("note", "stuck"))
            command.add_argument("--author", default="tutor", choices=NOTE_AUTHORS,
                                 help="僅學員主動提供原話時選 learner")
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
        if args.command == "engineering-status":
            _, progress = load_state()
            print("進度 revision %d" % progress["revision"])
            for event in progress["events"]:
                if isinstance(event, dict) and event.get("type") in ("engineering_step_confirmed", "engineering_step_note") and (not args.chapter or event.get("chapterId") == args.chapter):
                    print(json.dumps(event, ensure_ascii=False))
            for record in legacy_engineering_records(progress):
                if record["role"] == "answer" and not args.chapter:
                    note = progress["lessons"][record["lessonId"]]["notes"][record["noteIndex"]]
                    print("舊格式工程路徑回答 %s（記在原教材 %s）：%s" % (record["activity"], note.get("step"), note["text"]))
            return
        if args.command == "engineering-workspace":
            engineering_workspace(args.copy_manual_box)
            return
        if args.command == "pilot-status":
            _, progress = load_state()
            print("進度 revision %d" % progress["revision"])
            pilot_status_summary(progress)
            for event in pilot_events(progress):
                print(json.dumps(event, ensure_ascii=False))
            return
        if args.command == "challenge-status":
            _, progress = load_state()
            if args.challenge:
                challenge_definition(args.challenge)
            print("進度 revision %d" % progress["revision"])
            for event in challenge_events(progress, args.challenge):
                print(json.dumps(event, ensure_ascii=False))
            return
        if args.command == "confirm":
            mutate("confirm_step", args.lesson, args.revision,
                   step=args.step, evidence=args.evidence)
        elif args.command == "register-file":
            mutate("register_file", args.lesson, args.revision,
                   path=args.path, role=args.role, source=args.source, workspace=args.workspace)
        elif args.command == "set-interface-language":
            mutate("set_interface_language", None, args.revision,
                   language=args.language, evidence=args.evidence)
        elif args.command == "add-lessons":
            mutate("add_lessons", None, args.revision, reason=args.reason)
        elif args.command == "engineering-confirm":
            mutate("engineering_confirm", None, args.revision,
                   chapter=args.chapter, step=args.step, evidence=args.evidence)
        elif args.command == "engineering-note":
            mutate("engineering_note", None, args.revision, chapter=args.chapter, step=args.step,
                   note=Path(args.note_file).read_bytes().decode("utf-8-sig"),
                   note_kind=args.note_kind, author=args.author)
        elif args.command == "pilot-confirm":
            mutate("pilot_confirm", None, args.revision, challenge=PILOT_CHALLENGE_ID,
                   evidence=args.evidence, source_path=args.source_path)
        elif args.command == "pilot-note":
            mutate("pilot_note", None, args.revision, challenge=PILOT_CHALLENGE_ID,
                   note=Path(args.note_file).read_bytes().decode("utf-8-sig"), author=args.author)
        elif args.command == "challenge-confirm":
            mutate("challenge_confirm", None, args.revision, challenge=args.challenge,
                   evidence=args.evidence, source_path=args.source_path)
        elif args.command == "challenge-note":
            mutate("challenge_note", None, args.revision, challenge=args.challenge,
                   note=Path(args.note_file).read_bytes().decode("utf-8-sig"), author=args.author)
        else:
            mutate("add_note", args.lesson, args.revision,
                   note=Path(args.note_file).read_text(encoding="utf-8-sig"),
                   note_kind=args.note_kind, step=args.step, author=args.author)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
