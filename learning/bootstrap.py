#!/usr/bin/env python3
"""為新下載的專案建立個人進度；保留所有既有進度，不提供重設選項。"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from pathlib import Path, PureWindowsPath

import manage


def validate_catalog(catalog):
    """先驗證課程識別字；不把未檢查的教材字串用作目錄名稱。"""
    if not isinstance(catalog, dict) or catalog.get("schemaVersion") != 1:
        raise ValueError("catalog.json 格式版本不正確。")
    lessons = catalog.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        raise ValueError("catalog.json 必須有非空的 lessons 清單。")
    lesson_ids, step_ids = set(), set()
    for lesson in lessons:
        if not isinstance(lesson, dict):
            raise ValueError("catalog.json 的單元必須是物件。")
        lesson_id = lesson.get("id")
        if not isinstance(lesson_id, str) or not re.fullmatch(r"[0-9]{2}", lesson_id):
            raise ValueError("單元 ID 必須是兩位 ASCII 數字。")
        if lesson_id in lesson_ids:
            raise ValueError("catalog.json 有重複的單元 ID：" + lesson_id)
        lesson_ids.add(lesson_id)
        steps = lesson.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("單元 %s 必須有非空的 steps 清單。" % lesson_id)
        for step in steps:
            step_id = step.get("id") if isinstance(step, dict) else None
            if not isinstance(step_id, str) or not re.fullmatch(lesson_id + r"-[0-9]{2}", step_id):
                raise ValueError("步驟 ID 必須以所屬單元編號開頭，例如 01-01。")
            if step_id in step_ids:
                raise ValueError("catalog.json 有重複的步驟 ID：" + step_id)
            step_ids.add(step_id)
    return lessons


def _is_link(path):
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    # Python 3.10/3.11 尚無 Path.is_junction；Windows reparse point 也先拒絕。
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _workspace_paths(lessons, progress=None):
    """先驗所有工作區邊界與現有節點，再由呼叫者建立目錄。"""
    project = manage.PROJECT.resolve()
    learning = manage.LEARNING.resolve()
    learning.relative_to(project)
    root = manage.LEARNING / "workspaces"
    if _is_link(root):
        raise ValueError("工作區根目錄不能是連結或 junction。")
    resolved_root = root.resolve()
    resolved_root.relative_to(learning)
    resolved_root.relative_to(project)
    values = ["learning/workspaces/" + lesson["id"] for lesson in lessons]
    if progress is not None:
        values.extend(state["workspace"] for state in progress["lessons"].values())
    paths = []
    for value in values:
        if not isinstance(value, str) or "\0" in value:
            raise ValueError("工作區設定必須是專案相對路徑。")
        relative = Path(value.replace("\\", "/"))
        if relative.is_absolute() or PureWindowsPath(value).drive or ".." in relative.parts:
            raise ValueError("工作區設定不能是絕對路徑或包含 ..。")
        if relative.parts[:2] != ("learning", "workspaces") or len(relative.parts) < 3:
            raise ValueError("工作區必須位於 learning/workspaces 的單元子目錄。")
        path = manage.PROJECT / relative
        resolved = path.resolve()
        resolved.relative_to(resolved_root)
        resolved.relative_to(project)
        # 不跨越現有連結建立目錄，包括 Windows junction。
        for component in (root, *reversed(path.parents[:len(relative.parts) - 2]), path):
            if _is_link(component):
                raise ValueError("工作區路徑不能經過連結或 junction。")
            if component.exists() and not component.is_dir():
                raise ValueError("工作區路徑已有非目錄檔案：" + str(component))
        if path not in paths:
            paths.append(path)
    return paths


def _validate_existing(progress, lessons):
    """驗證可接續的既有狀態；不修復、補寫或改動其欄位。"""
    if not isinstance(progress, dict) or progress.get("schemaVersion") != 1:
        raise ValueError("既有 progress.json 格式版本不正確；未重設。")
    if type(progress.get("revision")) is not int or progress["revision"] < 1:
        raise ValueError("既有 progress.json 的 revision 必須是正整數；未重設。")
    for key, kind in (("lessons", dict), ("fileVersions", list), ("events", list)):
        if not isinstance(progress.get(key), kind):
            raise ValueError("既有 progress.json 缺少有效的 " + key + "；未重設。")
    states = progress["lessons"]
    if not isinstance(progress.get("activeLesson"), str) or progress["activeLesson"] not in states:
        raise ValueError("既有 progress.json 的 activeLesson 不正確；未重設。")
    catalog_lessons = {lesson["id"]: lesson for lesson in lessons}
    for lesson_id, state in states.items():
        if lesson_id not in catalog_lessons or not isinstance(state, dict):
            raise ValueError("既有 progress.json 的單元不正確；未重設。")
        if state.get("status") not in ("not_started", "in_progress", "completed"):
            raise ValueError("既有 progress.json 的單元狀態不正確；未重設。")
        completed, notes = state.get("completedSteps"), state.get("notes")
        step_ids = [step["id"] for step in catalog_lessons[lesson_id]["steps"]]
        if (not isinstance(completed, list) or any(not isinstance(step, str) or step not in step_ids for step in completed)
                or len(completed) != len(set(completed)) or not isinstance(notes, list)):
            raise ValueError("既有 progress.json 的完成步驟或筆記不正確；未重設。")
        current = state.get("currentStep")
        if state["status"] == "completed":
            if current is not None or completed != step_ids:
                raise ValueError("既有 progress.json 的完成單元不正確；未重設。")
        elif current not in step_ids or current in completed:
            raise ValueError("既有 progress.json 的 currentStep 不正確；未重設。")
        if "workspace" not in state:
            raise ValueError("既有 progress.json 缺少工作區；未重設。")
    if "learner" in progress and not isinstance(progress["learner"], dict):
        raise ValueError("既有 progress.json 的 learner 不正確；未重設。")


def initialize():
    """回傳 (created, progress)，在共用鎖內初建 revision 1 或保留合法既有檔。"""
    with manage.progress_lock():
        catalog = manage.read_json(manage.CATALOG)
        lessons = validate_catalog(catalog)
        # lstat 也能辨識失效連結；不把它當成缺檔而覆蓋。
        try:
            manage.PROGRESS.lstat()
            exists = True
        except FileNotFoundError:
            exists = False
        if exists:
            if _is_link(manage.PROGRESS) or not manage.PROGRESS.is_file():
                raise ValueError("既有 progress.json 不是一般檔案；未重設。")
            progress = manage.read_json(manage.PROGRESS)
            _validate_existing(progress, lessons)
            workspaces = _workspace_paths(lessons, progress)
            for path in workspaces:
                path.mkdir(parents=True, exist_ok=True)
            return False, progress

        workspaces = _workspace_paths(lessons)
        progress = {
            "schemaVersion": 1,
            "revision": 1,
            "updatedAt": manage.now(),
            "activeLesson": lessons[0]["id"],
            "learner": {"language": "zh-Hant", "timezone": "Asia/Taipei",
                        "interfaceLanguage": None, "blenderVersion": None},
            "decisions": {},
            "lessons": {
                lesson["id"]: {"status": "in_progress" if index == 0 else "not_started",
                               "currentStep": lesson["steps"][0]["id"], "completedSteps": [],
                               "notes": [], "workspace": "learning/workspaces/" + lesson["id"]}
                for index, lesson in enumerate(lessons)
            },
            "fileVersions": [],
            "events": [],
        }
        for path in workspaces:
            path.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(progress, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        manage.atomic_write(manage.PROGRESS, data)
        return True, progress


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        created, progress = initialize()
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error("初始化未寫入進度：" + str(error))
    if created:
        print("created: 已建立個人進度 revision 1；尚未確認任何學習步驟。")
    else:
        print("kept: 保留既有進度 revision %d；檔案內容未變更。" % progress["revision"])


if __name__ == "__main__":
    main()
