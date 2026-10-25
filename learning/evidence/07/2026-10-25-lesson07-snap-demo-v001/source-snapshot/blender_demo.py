"""在獨立 Blender 實例中以模擬滑鼠／鍵盤事件實際操作，逐步截圖並讀回實際狀態。

由 run_demo.py 以下列方式啟動（不使用學員的偏好設定，也不寫入學員工作區）：
  blender --factory-startup --enable-event-simulate --window-geometry 0 0 1494 1019 --python blender_demo.py
環境變數 DEMO_SCENARIO 指定 scenarios/ 下的劇本模組，DEMO_OUT 指定輸出資料夾。
"""
import hashlib
import importlib.util
import json
import os
import struct
import sys
import time
import traceback
from datetime import datetime, timezone

import bpy

OUT = os.environ["DEMO_OUT"]
SCENARIO = os.environ["DEMO_SCENARIO"]
records = []
queue = []
state = {"seq": 0}

KEYS = {**{c: c.upper() for c in "abcdefghijklmnopqrstuvwxyz"},
        **{d: n for d, n in zip("0123456789", ("ZERO", "ONE", "TWO", "THREE", "FOUR",
                                               "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"))},
        ".": "PERIOD", "-": "MINUS", "\\": "BACK_SLASH", "/": "SLASH", " ": "SPACE"}
SHIFTED = {"_": "MINUS", ":": "SEMI_COLON"}


def window(kind="main"):
    windows = list(bpy.context.window_manager.windows)
    if kind == "main":
        return windows[0]
    return next(w for w in windows[1:] if w.screen.areas[0].type == kind)


def area(kind, win=None):
    win = win or window()
    return next(a for a in win.screen.areas if a.type == kind)


def _event(win, kind, value, x=None, y=None, **flags):
    # 圖片座標以左上為原點；Blender 視窗事件以左下為原點。
    position = {} if x is None else {"x": int(x), "y": int(win.height - y)}
    win.event_simulate(kind, value, **position, **flags)


def move(x, y, win="main"):
    w = window(win)
    _event(w, "MOUSEMOVE", "NOTHING", x, y)


def click(x, y, win="main", button="LEFTMOUSE", **flags):
    # 模擬事件不支援 DOUBLE_CLICK；需要雙擊的地方改用選單或快捷鍵。
    w = window(win)
    _event(w, "MOUSEMOVE", "NOTHING", x, y)
    _event(w, button, "PRESS", x, y, **flags)
    _event(w, button, "RELEASE", x, y, **flags)


def drag(points, win="main", button="LEFTMOUSE", **flags):
    w = window(win)
    _event(w, "MOUSEMOVE", "NOTHING", *points[0])
    _event(w, button, "PRESS", *points[0], **flags)
    for x, y in points[1:]:
        _event(w, "MOUSEMOVE", "NOTHING", x, y, **flags)
    _event(w, button, "RELEASE", *points[-1], **flags)


def drag_slow(points, win="main", button="LEFTMOUSE", step=0.08, **flags):
    """按下、分段移動、放開各自在不同事件循環處理，像真人拖曳；插到佇列最前面依序執行。"""
    def at(kind, value, x, y):
        return lambda: _event(window(win), kind, value, x, y, **flags)
    items = [(at("MOUSEMOVE", "NOTHING", *points[0]), step), (at(button, "PRESS", *points[0]), step)]
    items += [(at("MOUSEMOVE", "NOTHING", x, y), step) for x, y in points[1:]]
    items.append((at(button, "RELEASE", *points[-1]), 0.6))
    queue[0:0] = items


def key(kind, win="main", x=None, y=None, **flags):
    # 快捷鍵依游標所在區域生效（例如 3D Viewport 的 M）；需要時帶上座標。
    w = window(win)
    _event(w, kind, "PRESS", x, y, **flags)
    _event(w, kind, "RELEASE", x, y, **flags)


def wait_until(condition, timeout=120.0, step=0.5):
    """排入等待：條件成立才繼續（例如渲染完成），逾時則中止劇本。"""
    deadline = []

    def check():
        if not deadline:
            deadline.append(time.monotonic() + timeout)
        if condition():
            return
        if time.monotonic() > deadline[0]:
            raise RuntimeError("等待逾時")
        queue.insert(0, (check, step))
    queue.append((check, step))


def type_text(text, win="main"):
    w = window(win)
    for char in text:
        if char in SHIFTED:
            kind, flags = SHIFTED[char], {"shift": True}
        elif char.isupper():
            kind, flags = char, {"shift": True}
        else:
            kind, flags = KEYS[char], {}
        _event(w, kind, "PRESS", unicode=char, **flags)
        _event(w, kind, "RELEASE", **flags)


def png_size(path):
    with open(path, "rb") as handle:
        header = handle.read(24)
    return struct.unpack(">II", header[16:24])


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capture(name, win="main"):
    w = window(win)
    path = os.path.join(OUT, name + ".png")
    with bpy.context.temp_override(window=w, area=w.screen.areas[0]):
        bpy.ops.screen.screenshot(filepath=path, check_existing=False)
    width, height = png_size(path)
    return {"file": os.path.basename(path), "width": width, "height": height, "sha256": sha256(path)}


def record(step, slug, action, observe, win="main", highlights=(), clicks=(), note=None, park=None):
    """排入一筆：截圖當下畫面，並以 observe() 讀回 Blender 實際狀態。

    park：截圖前先把游標移到不會觸發提示的位置（選單開著時不要用，移開會關閉選單）。
    """
    if park:
        queue.append((lambda: move(*park, win=win), 0.8))

    def run():
        state["seq"] += 1
        name = "%s-%02d-%s" % (step, sum(r["step"] == step for r in records) + 1, slug)
        item = {"seq": state["seq"], "step": step, "slug": slug,
                "recordedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "action": action, "observed": observe(), "window": win,
                "highlights": highlights() if callable(highlights) else list(highlights),
                "clicks": list(clicks)}
        item.update(capture(name, win))
        if note:
            item["note"] = note
        records.append(item)
    queue.append((run, 0.4))


def do(fn, wait=0.8):
    queue.append((fn, wait))


def finish():
    with open(os.path.join(OUT, "run.json"), "w", encoding="utf-8") as handle:
        json.dump({"scenario": SCENARIO, "blender": bpy.app.version_string,
                   "buildHash": bpy.app.build_hash.decode(), "records": records},
                  handle, ensure_ascii=False, indent=1)
    bpy.context.preferences.view.use_save_prompt = False
    bpy.ops.wm.quit_blender()


def tick():
    if not queue:
        return None
    fn, wait = queue.pop(0)
    try:
        fn()
    except Exception:
        records.append({"error": traceback.format_exc(), "queueLeft": len(queue)})
        queue.clear()
        queue.append((finish, 0.1))
    return wait


bpy.context.preferences.filepaths.temporary_directory = os.environ.get("TEMP", "")
sys.path.insert(0, os.path.dirname(SCENARIO))  # 劇本可 import 同資料夾的 common
spec = importlib.util.spec_from_file_location("scenario", SCENARIO)
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)
scenario.build(globals())
queue.append((finish, 0.1))
# persistent：重新開啟 .blend 後計時器仍要繼續執行劇本。
bpy.app.timers.register(tick, first_interval=2.0, persistent=True)
