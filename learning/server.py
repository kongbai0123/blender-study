"""Blender 本機教學介面；與 manage.py 共用進度、鎖與版本盤點。"""
from __future__ import annotations

import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
import re
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
from urllib.parse import unquote, urlsplit
import webbrowser

import manage

WEB = manage.LEARNING / "web"
MAX_BODY = 65536
# 不使用示意圖：教學圖片只來自 evidence 的實際截圖。
FILE_ROOTS = ("evidence", "workspaces", "journal")
FILE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".blend", ".blend1",
                   ".stl", ".obj", ".mtl", ".3mf", ".ply", ".pdf", ".txt", ".md", ".json"}



CHALLENGE_PAGES = ("/challenges/index.html", "/challenges/app.js", "/challenges/app.css",
                   "/pilot/box-lesson.html", "/pilot/box-lesson.css")


def challenge_assets():
    """目前題目資料（manage.CHALLENGES）引用的工程圖與動畫網址。"""
    try:
        data = manage.read_json(manage.CHALLENGES)
    except (OSError, ValueError):
        return set()
    paths = set()
    for item in data.get("chapters", []) if isinstance(data, dict) else []:
        for key in ("drawing", "animation"):
            value = item.get(key) if isinstance(item, dict) else None
            path = value.get("path") if isinstance(value, dict) else None
            if isinstance(path, str) and re.fullmatch(r"/(?:challenges|pilot)/[a-z0-9-]+\.(?:svg|gif)", path):
                paths.add(path)
    return paths

class RequestError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def safe_file(value, roots=FILE_ROOTS):
    """僅允許明列的 learning 子資料夾；路徑及連結解析後都要留在白名單。"""
    if not isinstance(value, str) or len(value) > 1500 or "\0" in value or ":" in value:
        raise RequestError("檔案路徑不正確。", 403)
    relative = Path(value.replace("\\", "/"))
    if relative.is_absolute() or PureWindowsPath(value).drive or ".." in relative.parts:
        raise RequestError("檔案路徑超出允許範圍。", 403)
    if len(relative.parts) < 3 or relative.parts[0] != "learning" or relative.parts[1] not in roots:
        raise RequestError("只能讀取實際截圖、工作區或學習紀錄。", 403)
    root = (manage.LEARNING / relative.parts[1]).resolve()
    path = (manage.PROJECT / relative).resolve()
    try:
        path.relative_to(root)
        path.relative_to(manage.PROJECT)
    except ValueError:
        raise RequestError("檔案路徑超出允許範圍。", 403) from None
    if not path.is_file():
        raise RequestError("找不到檔案。", 404)
    if path.suffix.lower() not in FILE_EXTENSIONS:
        raise RequestError("這個檔案請由專案資料夾開啟。", 403)
    return path


def workspace_for(catalog, progress, lesson_id):
    _, state = manage.lesson_state(catalog, progress, lesson_id)
    value = state["workspace"]
    relative = Path(value.replace("\\", "/"))
    if relative.is_absolute() or PureWindowsPath(value).drive or ".." in relative.parts:
        raise ValueError("單元工作區設定不正確。")
    path = (manage.PROJECT / relative).resolve()
    path.relative_to((manage.LEARNING / "workspaces").resolve())
    path.relative_to(manage.PROJECT)
    if not path.is_dir():
        raise ValueError("單元工作區不存在。")
    return path


def engineering_workspace_for(workspace_id):
    if workspace_id not in manage.ENGINEERING_WORKSPACES:
        raise ValueError("不支援的工程工作區。")
    path = (manage.PROJECT / manage.ENGINEERING_WORKSPACES[workspace_id]).resolve()
    path.relative_to((manage.LEARNING / "workspaces").resolve())
    if not path.is_dir():
        raise ValueError("工程工作區尚未建立；請先執行 python learning/manage.py engineering-workspace。")
    return path


def learning_files(catalog, progress):
    files = []
    registered = {manage.path_key(item["path"]): item for item in progress["fileVersions"]}
    workspaces = []
    for lesson in catalog["lessons"]:
        # catalog 剛加入、尚未用 add-lessons 補進進度的單元沒有工作區；略過而不讓整頁讀取失敗。
        if lesson["id"] not in progress["lessons"]:
            continue
        try:
            workspaces.append(workspace_for(catalog, progress, lesson["id"]))
        except ValueError:
            # 工作區資料夾被刪除或設定不正確時，只略過該單元的檔案清單，不讓整頁讀取失敗。
            continue
    for workspace_id in manage.ENGINEERING_WORKSPACES:
        try:
            workspaces.append(engineering_workspace_for(workspace_id))
        except ValueError:
            continue
    for workspace in workspaces:
        for folder, directories, names in os.walk(workspace, followlinks=False):
            directories[:] = sorted(name for name in directories
                                     if not (Path(folder) / name).is_symlink())
            for name in sorted(names):
                path = Path(folder) / name
                try:
                    resolved = path.resolve()
                    resolved.relative_to(workspace)
                    if not resolved.is_file() or path.is_symlink():
                        continue
                    stat = resolved.stat()
                    relative = path.relative_to(manage.PROJECT).as_posix()
                except (OSError, ValueError):
                    continue
                record = registered.get(manage.path_key(relative))
                entry = {"path": relative, "bytes": stat.st_size,
                         "modifiedAt": datetime.fromtimestamp(stat.st_mtime, manage.TAIPEI).isoformat(timespec="seconds"),
                         "registered": record is not None}
                if record:
                    entry["role"] = record["role"]
                files.append(entry)
                if len(files) >= 500:
                    return files
    return files


def learning_journal():
    items = []
    folder = manage.LEARNING / "journal"
    for path in sorted(folder.glob("*.md"), reverse=True):
        if path.is_symlink():
            continue
        relative = path.relative_to(manage.PROJECT).as_posix()
        try:
            safe_file(relative, roots=("journal",))
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, ValueError):
            continue
        title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
        items.append({"path": relative, "title": title})
    return items


def blender_executable():
    # 只接受本機已存在的安裝程式；不接受 HTTP 傳入的執行路徑或命令列。
    program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    candidates = sorted((program_files / "Blender Foundation").glob("Blender */blender.exe"), reverse=True)
    found = shutil.which("blender.exe")
    if found:
        candidates.append(Path(found))
    for path in candidates:
        if path.is_file() and path.name.lower() == "blender.exe":
            return path.resolve()
    raise ValueError("未找到已安裝的 Blender；請從 Windows 開始選單開啟。")


def open_target(payload):
    catalog, progress = manage.load_state()
    target = payload.get("target")
    if payload.get("workspaceId") is not None:
        if target != "workspace":
            raise ValueError("工程工作區只能開啟資料夾。")
        workspace = engineering_workspace_for(payload.get("workspaceId"))
    else:
        workspace = workspace_for(catalog, progress, payload.get("lessonId"))
    if target not in ("workspace", "blender"):
        raise ValueError("target 必須是 workspace 或 blender。")
    if os.name != "nt":
        raise ValueError("此啟動方式供 Windows 使用。")
    if target == "workspace":
        os.startfile(str(workspace))
        return {"ok": True, "path": str(workspace)}
    executable = blender_executable()
    subprocess.Popen([str(executable)], cwd=str(manage.PROJECT), shell=False,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"ok": True, "path": str(executable)}


class Handler(BaseHTTPRequestHandler):
    server_version = "BlenderLearning/1"

    def log_request(self, code="-", size="-"):
        # 網頁每 5 秒輪詢；只記錄失敗的請求，真正的錯誤才不會被成功紀錄淹沒。
        if isinstance(code, int) and code >= 400:
            super().log_request(code, size)

    def _check_host(self):
        host = self.headers.get("Host", "")
        valid = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if host not in valid:
            raise RequestError("請從本機教學入口開啟。", 403)
        return host

    def send_bytes(self, data, content_type, status=200, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'; form-action 'self'")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, value, status=200, extra=None):
        self.send_bytes(json.dumps(value, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8", status, extra)

    def file(self, path, attachment=False):
        if not path.is_file():
            raise RequestError("找不到檔案。", 404)
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or path.suffix == ".js":
            content_type += "; charset=utf-8"
        extra = {"Content-Disposition": "attachment"} if attachment else None
        self.send_bytes(path.read_bytes(), content_type, extra=extra)

    def do_GET(self):
        try:
            self._check_host()
            route = unquote(urlsplit(self.path).path)
            if route == "/api/health":
                return self.send_json({"application": "blender-guided-learning", "project": str(manage.PROJECT), "ready": True})
            if route == "/api/bootstrap":
                catalog, progress = manage.load_state()
                return self.send_json({"projectRoot": str(manage.PROJECT), "catalog": catalog,
                                       "progress": progress, "files": learning_files(catalog, progress),
                                       "journal": learning_journal(),
                                       "engineeringWorkspaces": manage.ENGINEERING_WORKSPACES,
                                       "legacyEngineeringNotes": manage.legacy_engineering_records(progress)})
            if route == "/api/export":
                _, progress = manage.load_state()
                return self.send_json(progress, extra={"Content-Disposition": 'attachment; filename="Blender-learning-progress.json"'})
            if route in ("/", "/index.html", "/app.js", "/app.css", "/engineering-path.js"):
                return self.file(WEB / ("index.html" if route in ("/", "/index.html") else route[1:]))
            # 工程教材以固定網址提供目前版本；版本只在 manage.py 指定，歷史版本不經網頁提供。
            if route == "/engineering-path.json":
                return self.file(manage.ENGINEERING_PATH)
            if route == "/engineering-curriculum.json":
                return self.file(manage.ENGINEERING_CURRICULUM)
            if route == "/challenges/manifest.json":
                return self.file(manage.CHALLENGES)
            # 練習題頁只提供固定的頁面檔，以及目前題目資料引用的工程圖與動畫；歷史版本不經網頁提供。
            if route in CHALLENGE_PAGES or route in challenge_assets():
                folder = route.split("/")[1]
                root = (WEB / folder).resolve()
                asset = (root / route.rsplit("/", 1)[1]).resolve()
                try:
                    root.relative_to(WEB.resolve())
                    asset.relative_to(root)
                except ValueError:
                    raise RequestError("題目資源超出允許範圍。", 403) from None
                return self.file(asset)
            if route.startswith("/reports/"):
                name = route[len("/reports/"):]
                if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.(?:html|css)", name):
                    raise RequestError("報告頁路徑不正確。", 403)
                report = (WEB / "reports" / name).resolve()
                try:
                    report.relative_to((WEB / "reports").resolve())
                    report.relative_to(WEB.resolve())
                except ValueError:
                    raise RequestError("報告頁超出允許範圍。", 403) from None
                return self.file(report)
            if route.startswith("/files/"):
                path = safe_file(route[len("/files/"):])
                return self.file(path, attachment=path.suffix.lower() in (".blend", ".blend1", ".stl", ".obj", ".3mf", ".ply"))
            if route.startswith("/read/"):
                path = safe_file(route[len("/read/"):], roots=("journal",))
                if path.suffix.lower() != ".md":
                    raise RequestError("只能閱讀學習紀錄。", 403)
                # 紀錄視為純文字，不執行 Markdown 內的 HTML 或 JavaScript。
                return self.send_bytes(path.read_text(encoding="utf-8-sig").encode("utf-8"), "text/plain; charset=utf-8")
            if route == "/favicon.ico":
                return self.send_bytes(b"", "image/x-icon", 204)
            raise RequestError("找不到這個頁面。", 404)
        except RequestError as error:
            self.send_json({"error": str(error)}, error.status)
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.log_error("讀取學習資料失敗：%s", error)
            self.send_json({"error": "讀取學習資料失敗：" + str(error)}, 500)

    def _payload(self):
        if self.headers.get("Transfer-Encoding"):
            raise RequestError("不接受分段傳送。", 400)
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise RequestError("Content-Length 格式不正確。", 400) from None
        if length <= 0:
            raise RequestError("操作內容大小不正確。", 413)
        # 先讀取有上限的 request body，避免 Windows 對尚有未讀資料的連線
        # 發送 RST，導致瀏覽器收不到 403/415/413 的說明。內容仍須通過下方驗證。
        body = self.rfile.read(min(length, MAX_BODY + 1))
        if length > MAX_BODY:
            raise RequestError("操作內容大小不正確。", 413)
        host = self._check_host()
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + host:
            raise RequestError("請由同一個本機教學入口操作。", 403)
        fetch_site = self.headers.get("Sec-Fetch-Site")
        if fetch_site and fetch_site not in ("same-origin", "none"):
            raise RequestError("不接受跨網站操作。", 403)
        if self.headers.get_content_type() != "application/json":
            raise RequestError("請使用 application/json。", 415)
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise RequestError("操作內容必須是有效的 JSON。", 400) from None
        if not isinstance(payload, dict):
            raise RequestError("操作內容必須是 JSON 物件。", 400)
        return payload

    def do_POST(self):
        try:
            payload = self._payload()
            route = urlsplit(self.path).path
            if route == "/api/open":
                return self.send_json(open_target(payload))
            lesson, revision = payload.get("lessonId"), payload.get("expectedRevision")
            if route == "/api/progress":
                action = payload.get("action")
                if action == "confirm_step":
                    progress = manage.mutate(action, lesson, revision, step=payload.get("stepId"), evidence=payload.get("evidence"))
                elif action == "add_note":
                    progress = manage.mutate(action, lesson, revision, step=payload.get("stepId"),
                                             note=payload.get("note"), note_kind=payload.get("noteKind", "note"),
                                             author="learner")
                elif action == "engineering_confirm":
                    progress = manage.mutate(action, None, revision, chapter=payload.get("chapterId"),
                                             step=payload.get("stepId"), evidence=payload.get("evidence"))
                elif action == "engineering_note":
                    progress = manage.mutate(action, None, revision, chapter=payload.get("chapterId"),
                                             step=payload.get("stepId"), note=payload.get("note"),
                                             note_kind=payload.get("noteKind", "note"), author="learner")
                elif action == "pilot_confirm":
                    progress = manage.mutate(action, None, revision, challenge=payload.get("challengeId"),
                                             evidence=payload.get("evidence"), source_path=payload.get("sourcePath"))
                elif action == "pilot_note":
                    progress = manage.mutate(action, None, revision, challenge=payload.get("challengeId"),
                                             note=payload.get("note"), author="learner")
                elif action == "challenge_confirm":
                    progress = manage.mutate(action, None, revision, challenge=payload.get("challengeId"),
                                             evidence=payload.get("evidence"), source_path=payload.get("sourcePath"))
                elif action == "challenge_note":
                    progress = manage.mutate(action, None, revision, challenge=payload.get("challengeId"),
                                             note=payload.get("note"), author="learner")
                else:
                    raise RequestError("不支援的進度操作。")
                return self.send_json({"progress": progress})
            if route == "/api/register-file":
                progress = manage.mutate("register_file", lesson, revision, path=payload.get("path"),
                                         role=payload.get("role"), source=payload.get("source"),
                                         workspace=payload.get("workspaceId"))
                return self.send_json({"progress": progress})
            raise RequestError("找不到這個操作。", 404)
        except RequestError as error:
            self.send_json({"error": str(error)}, error.status)
        except manage.RevisionConflict as error:
            self.send_json({"error": str(error)}, 409)
        except manage.ProgressBusy as error:
            self.send_json({"error": str(error)}, 503)
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.send_json({"error": "操作未寫入：" + str(error)}, 400)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    manage.load_state()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Blender learning: http://127.0.0.1:{args.port}/", flush=True)
    if args.open:
        webbrowser.open(f"http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
