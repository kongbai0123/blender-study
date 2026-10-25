"""啟動獨立 Blender，保存真實示範與 runner-status.json。

用法：python learning/tutor/run_demo.py <劇本名稱> <新的 evidence 輸出資料夾>
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BLENDER = Path(os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"))
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent / "evidence"
WORKSPACES = HERE.parent / "workspaces"
TIMEOUT = 600


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def resolve_scenario(name):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("劇本名稱只能包含英數字、底線或連字號")
    root = (HERE / "scenarios").resolve()
    scenario = (root / (name + ".py")).resolve()
    if scenario.parent != root or not scenario.is_file():
        raise ValueError("找不到 scenarios 內的劇本：" + name)
    return scenario


def prepare_output(path):
    out, root = Path(path).resolve(), EVIDENCE.resolve()
    if out == root or not out.is_relative_to(root):
        raise ValueError("示範輸出必須是 learning/evidence 內的獨立 run 資料夾")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("輸出資料夾已有內容，請使用新的 run 版本：" + str(out))
    out.mkdir(parents=True, exist_ok=True)
    return out


def workspace_snapshot(root=WORKSPACES):
    """遞迴保存路徑及檔案內容雜湊；不跟隨 symlink／junction 到其他位置。"""
    root = Path(root)
    if not root.exists():
        return {".": {"kind": "missing"}}
    snapshot = {".": {"kind": "directory"}}

    def unreadable(error):
        raise error

    for base, directories, files in os.walk(root, followlinks=False, onerror=unreadable):
        base = Path(base)
        for name in sorted(directories + files):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                snapshot[relative] = {"kind": "link", "target": os.readlink(path)}
                if name in directories:
                    directories.remove(name)
            elif path.is_dir():
                snapshot[relative] = {"kind": "directory"}
            else:
                digest = hashlib.sha256()
                size = 0
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1 << 20), b""):
                        digest.update(chunk)
                        size += len(chunk)
                snapshot[relative] = {"kind": "file", "size": size, "sha256": digest.hexdigest()}
    return snapshot


def validate_run(path):
    try:
        run = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError("run.json 缺失或無法讀取：" + str(error)) from error
    records = run.get("records") if isinstance(run, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("run.json 必須包含非空的 records 清單")
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            raise ValueError("run.json 第 %d 筆紀錄不是物件" % index)
        if "error" in record:
            raise ValueError("Blender 劇本第 %d 筆紀錄失敗：%s" % (index, record["error"]))
    return run


def recent_links():
    if os.name != "nt":
        return set()
    root = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Recent"
    return {str(path.resolve()) for path in root.glob("*.lnk") if path.is_file()}


def clean_windows_recent(root, before):
    """只處理本次新增且目標屬本次 run 的捷徑；保留執行前已存在的所有捷徑。"""
    if os.name != "nt":
        return []
    candidates = sorted(recent_links() - set(before))
    if not candidates:
        return []
    # 一個 PowerShell 全程驗證及刪除精確檔案；不把路徑拼接進 shell 程式碼。
    script = (
        "$ErrorActionPreference = 'Stop'; "
        "[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); "
        "$shell = New-Object -ComObject WScript.Shell; "
        "$demoRoot = [IO.Path]::GetFullPath($env:DEMO_OUT_ROOT).TrimEnd('\\') + '\\'; "
        "$recentRoot = [IO.Path]::GetFullPath((Join-Path $env:APPDATA 'Microsoft\\Windows\\Recent')); "
        "ConvertFrom-Json $env:DEMO_RECENT_CANDIDATES | ForEach-Object { "
        "$link = [IO.Path]::GetFullPath([string]$_); "
        "if ([IO.Path]::GetDirectoryName($link).Equals($recentRoot, [StringComparison]::OrdinalIgnoreCase) "
        "-and [IO.Path]::GetExtension($link) -ieq '.lnk' "
        "-and (Test-Path -LiteralPath $link -PathType Leaf)) { "
        "$target = $shell.CreateShortcut($link).TargetPath; "
        "if ($target -and [IO.Path]::IsPathRooted($target)) { "
        "$target = [IO.Path]::GetFullPath($target); "
        "if ($target.StartsWith($demoRoot, [StringComparison]::OrdinalIgnoreCase)) "
        "{ Remove-Item -LiteralPath $link -ErrorAction Stop; Write-Output $link } } } }")
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True,
        encoding="utf-8", env=dict(os.environ, DEMO_OUT_ROOT=str(Path(root).resolve()),
                                   DEMO_RECENT_CANDIDATES=json.dumps(candidates)),
        timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise RuntimeError("最近使用捷徑清理失敗：" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line.strip()]


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    try:
        scenario = resolve_scenario(args.scenario)
        out = prepare_output(args.output)
    except (OSError, ValueError) as error:
        print("無法啟動示範：", error, file=sys.stderr)
        return 2

    status = {"status": "failed", "scenario": scenario.stem, "outputDir": str(out),
              "startedAt": utc_now(), "endedAt": None, "blenderExitCode": None,
              "timeoutSeconds": TIMEOUT, "workspacesUnchanged": False, "runErrors": [],
              "workspacesBefore": None, "workspacesAfter": None, "workspaceChanges": [],
              "recentCleanup": {"removed": [], "warnings": []}}
    before_recent = None
    returncode = 1
    try:
        status["workspacesBefore"] = workspace_snapshot(WORKSPACES)
        try:
            before_recent = recent_links()
        except Exception as error:
            status["recentCleanup"]["warnings"].append("無法記錄執行前捷徑，停用清理：" + str(error))
        with tempfile.TemporaryDirectory(prefix="blender-demo-config-") as config:
            temp = os.path.join(config, "temp")
            os.makedirs(temp)
            env = dict(os.environ, DEMO_OUT=str(out), DEMO_SCENARIO=str(scenario),
                       BLENDER_USER_CONFIG=config, BLENDER_USER_SCRIPTS=os.path.join(config, "scripts"),
                       BLENDER_USER_DATAFILES=os.path.join(config, "datafiles"), TEMP=temp, TMP=temp)
            command = [str(BLENDER), "--factory-startup", "--enable-event-simulate",
                       "--window-geometry", "0", "0", "1494", "1019", "--python", str(HERE / "blender_demo.py")]
            with (out / "blender.log").open("w", encoding="utf-8", errors="replace") as log:
                result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=TIMEOUT)
            status["blenderExitCode"] = result.returncode
            if result.returncode:
                returncode = result.returncode if result.returncode > 0 else 1
                raise RuntimeError("Blender 結束碼：%s" % result.returncode)
            validate_run(out / "run.json")
            returncode = 0
    except subprocess.TimeoutExpired:
        returncode = 124
        status["runErrors"].append("Blender 示範超過 %d 秒，已中止" % TIMEOUT)
    except Exception as error:
        status["runErrors"].append(str(error))
    finally:
        try:
            after = status["workspacesAfter"] = workspace_snapshot(WORKSPACES)
            before = status["workspacesBefore"]
            if before is not None:
                status["workspaceChanges"] = sorted(key for key in set(before) | set(after)
                                                    if before.get(key) != after.get(key))
                status["workspacesUnchanged"] = not status["workspaceChanges"]
                if not status["workspacesUnchanged"]:
                    status["runErrors"].append("學員工作區內容變更：" + "、".join(status["workspaceChanges"]))
        except Exception as error:
            status["runErrors"].append("無法核對學員工作區：" + str(error))
        if before_recent is not None:
            try:
                status["recentCleanup"]["removed"] = clean_windows_recent(out, before_recent)
            except Exception as error:
                status["recentCleanup"]["warnings"].append(str(error))
        if status["runErrors"] or not status["workspacesUnchanged"]:
            returncode = returncode or 1
        status["status"] = "completed" if returncode == 0 else "failed"
        status["endedAt"] = utc_now()
        try:
            temporary = out / "runner-status.json.tmp"
            temporary.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(out / "runner-status.json")
        except OSError as error:
            print("無法保存 runner-status.json：", error, file=sys.stderr)
            returncode = returncode or 1

    print("blender exit", status["blenderExitCode"], "runner", status["status"], "->", out)
    for error in status["runErrors"]:
        print(error, file=sys.stderr)
    for warning in status["recentCleanup"]["warnings"]:
        print("捷徑清理警告：", warning, file=sys.stderr)
    return returncode


if __name__ == "__main__":
    sys.exit(main())
