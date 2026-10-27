"""Verify missing shortcut semantics in an isolated Blender 5.2.1 UI.

Only event simulation changes scene/selection/mode/transforms. Python reads
native results, captures original screenshots, and writes new-run evidence.
No scene or STL is saved, no learner workspace or preference file is written.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy

from common import Kit, PARK, PROJECT


def build(g):
    k = Kit(g)
    do, key, click, move, record = k.do, k.key, k.click, k.move, k.record
    out = Path(g["OUT"])
    snapshots = out / "source-snapshot"
    snapshots.mkdir()
    files = []
    for rel in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py",
                "learning/tutor/scenarios/common.py", "learning/tutor/scenarios/shortcut_probe.py"):
        target = snapshots / Path(rel).name
        target.write_bytes((PROJECT / rel).read_bytes())
        files.append(dict(source=rel, snapshot="source-snapshot/" + target.name,
                          sha256=g["sha256"](str(target))))
    (snapshots / "manifest.json").write_text(json.dumps(dict(files=files), indent=2) + "\n", "utf-8")
    cases = []
    memo = {}

    def active():
        return bpy.context.view_layer.objects.active

    def state():
        o = active()
        v = k.view3d()
        return dict(active=o.name if o else None, selected=sorted(o.name for o in bpy.context.selected_objects),
                    mode=bpy.context.mode, objects=sorted(bpy.data.objects.keys()),
                    location=list(o.location) if o else None,
                    rotationDegrees=[math.degrees(x) for x in o.rotation_euler] if o else None,
                    scale=list(o.scale) if o else None, dimensions=list(o.dimensions) if o else None,
                    collections=sorted(c.name for c in o.users_collection) if o else None,
                    sidebarVisible=v.show_region_ui,
                    viewDistance=v.region_3d.view_distance,
                    viewLocation=list(v.region_3d.view_location),
                    viewPerspective=v.region_3d.view_perspective,
                    emulateNumpad=bpy.context.preferences.inputs.use_emulate_numpad,
                    sceneUnitSystem=bpy.context.scene.unit_settings.system,
                    sceneScaleLength=bpy.context.scene.unit_settings.scale_length)

    def close(a, b, eps=1e-5):
        return len(a) == len(b) and all(abs(x-y) < eps for x, y in zip(a, b))

    def observe(case, action, events, expect=None, check=None, step="01-07", note=None):
        def read():
            actual = state()
            result = None if check is None else bool(check(actual))
            evidence = dict(case=case, events=events, expected=expect, actual=actual,
                            passed=result, verification="native_events_and_readback")
            cases.append(evidence)
            if result is False:
                raise RuntimeError("Shortcut case failed: " + json.dumps(evidence, ensure_ascii=False))
            return actual
        record(step, case, action, read, note=note, park=PARK)

    def send(kind, **flags):
        do(lambda: key(kind, x=700, y=600, **flags), .25)

    def number(text):
        do(lambda: k.type_text(text), .25)

    def transform(kind, axis, text, end="RET"):
        send(kind)
        if axis:
            send(axis)
        number(text)
        if end == "RIGHTMOUSE":
            do(lambda: click(700, 600, button="RIGHTMOUSE"), .55)
        else:
            send(end)

    def remember(name):
        do(lambda: memo.update({name: state()}), .1)

    def menu_capture(case, action, events, step="01-05"):
        # Parking while a popup is open can close submenus; leave pointer alone.
        record(step, case, action, state,
               note="選單是否展開請以原圖核對；旁列數值只是同時讀回的場景狀態，不把固定描述當成程式讀值。")
        do(lambda: cases.append(dict(case=case, events=events,
            expected="Inspect native popup in original screenshot", actual=state(), passed=None,
            verification="native_event_screenshot")), .1)

    k.setup()
    observe("baseline", "核對隔離出廠場景及 Cube 的初始位置。", [],
            dict(version="5.2.1 LTS", location=[0, 0, 0]),
            lambda s: bpy.app.version == (5, 2, 1) and s["active"] == "Cube" and close(s["location"], [0, 0, 0]))
    send("N")
    observe("sidebar-n", "滑鼠在 3D Viewport，按 N 開啟 Sidebar。", ["N"], True,
            lambda s: s["sidebarVisible"] is True)

    transform("G", "X", "0.5")
    observe("translate-x-from-zero", "從 X=0 按 G → X → 0.5 → Enter。", ["G", "X", "0.5", "RET"],
            [0.5, 0, 0], lambda s: close(s["location"], [.5, 0, 0]))
    transform("G", "X", "0.5")
    observe("translate-x-start-one", "再按 G → X → 0.5，準備 X=1 的對照起點。", ["G", "X", "0.5", "RET"],
            [1, 0, 0], lambda s: close(s["location"], [1, 0, 0]))
    transform("G", "X", "0.5")
    observe("translate-x-from-one", "從 X=1 按 G → X → 0.5 → Enter，驗相對移動。", ["G", "X", "0.5", "RET"],
            [1.5, 0, 0], lambda s: close(s["location"], [1.5, 0, 0]))
    transform("G", "X", "-0.5")
    observe("translate-x-negative", "按 G → X → -0.5 → Enter，往負 X 移動。", ["G", "X", "-0.5", "RET"],
            [1, 0, 0], lambda s: close(s["location"], [1, 0, 0]))

    remember("beforeUnconstrained")
    transform("G", None, "0.5")
    observe("translate-no-axis", "在出廠透視視角按 G → 0.5 → Enter，不加軸向；讀回三軸。", ["G", "0.5", "RET"],
            "Observe actual unconstrained numeric translation; no assumed axis", None)
    remember("beforeCancel")
    transform("G", "X", "3", "ESC")
    observe("translate-cancel-esc", "G → X → 3 後按 Esc 取消。", ["G", "X", "3", "ESC"],
            "Location equals preceding result", lambda s: close(s["location"], memo["beforeCancel"]["location"]))
    transform("G", "X", "3", "RIGHTMOUSE")
    observe("translate-cancel-rightmouse", "G → X → 3 後按滑鼠右鍵取消。", ["G", "X", "3", "RIGHTMOUSE"],
            "Location equals preceding result", lambda s: close(s["location"], memo["beforeCancel"]["location"]))

    k.type_into(1050, 143, "0.5")
    observe("location-field-absolute", "在 Item 的 Location X 欄輸入 0.5，讀回絕對 X 值。", ["CLICK_LOCATION_X", "CTRL_A", "0.5", "RET"],
            .5, lambda s: abs(s["location"][0]-.5)<1e-5)
    for axis in ("Y", "Z"):
        remember("beforeMove" + axis)
        transform("G", axis, "0.25")
        idx = "XYZ".index(axis)
        observe("translate-" + axis.lower(), "按 G → %s → 0.25 → Enter。" % axis,
                ["G", axis, "0.25", "RET"], "Only selected global axis increases by .25",
                lambda s, axis=axis, idx=idx: close(s["location"], [v + (.25 if i==idx else 0) for i,v in enumerate(memo["beforeMove"+axis]["location"])]))

    for axis in ("X", "Y", "Z"):
        transform("R", axis, "30")
        expected = [30 if axis==a else 0 for a in "XYZ"]
        observe("rotate-" + axis.lower(), "按 R → %s → 30 → Enter（角度為度）。" % axis,
                ["R", axis, "30", "RET"], expected,
                lambda s, expected=expected: close(s["rotationDegrees"], expected, 1e-3), step="01-08")
        transform("R", axis, "-30")
        observe("rotate-" + axis.lower() + "-restore", "沿同軸旋回 -30°，供下一軸隔離對照。",
                ["R", axis, "-30", "RET"], [0,0,0], lambda s: close(s["rotationDegrees"], [0,0,0], 1e-3), step="01-08")
    for axis in ("X", "Y", "Z"):
        transform("S", axis, "1.5")
        expected = [1.5 if axis==a else 1 for a in "XYZ"]
        observe("scale-" + axis.lower(), "按 S → %s → 1.5 → Enter（倍率，非絕對尺寸）。" % axis,
                ["S", axis, "1.5", "RET"], expected,
                lambda s, expected=expected: close(s["scale"], expected), step="01-08")
        transform("S", axis, "0.6666666667")
        observe("scale-" + axis.lower() + "-restore", "同軸乘 2/3，恢復 Scale=1，供下一軸隔離對照。",
                ["S", axis, "0.6666666667", "RET"], [1,1,1], lambda s: close(s["scale"],[1,1,1]), step="01-08")

    send("TAB")
    observe("tab-edit", "Cube 已選取，在 3D Viewport 按 Tab 進入 Edit Mode。", ["TAB"], "EDIT_MESH",
            lambda s: s["mode"]=="EDIT_MESH", step="01-05")
    send("TAB")
    observe("tab-object", "再按 Tab 回 Object Mode。", ["TAB"], "OBJECT", lambda s: s["mode"]=="OBJECT", step="01-05")
    send("A")
    observe("select-all", "Object Mode 按 A，全選三個場景物件。", ["A"], ["Camera","Cube","Light"],
            lambda s: s["selected"]==["Camera","Cube","Light"], step="01-05")
    send("A", alt=True)
    observe("deselect-all", "Object Mode 按 Alt+A，取消全部選取。", ["ALT_A"], [], lambda s: s["selected"]==[], step="01-05")
    k.click_outliner("Cube")
    remember("beforeFrame")
    send("NUMPAD_PERIOD")
    observe("frame-selected", "在 3D Viewport 按數字鍵盤小數點，對焦選取的 Cube。", ["NUMPAD_PERIOD"],
            "View centers on Cube, object location unchanged",
            lambda s: close(s["location"], memo["beforeFrame"]["location"]) and close(s["viewLocation"],s["location"]), step="01-06")

    send("A", shift=True)
    menu_capture("shift-a-menu", "按 Shift+A，核對原生 Add 選單。", ["SHIFT_A"], step="02-02")
    send("ESC")
    send("X")
    menu_capture("x-delete-menu", "按 X，核對刪除確認；本次按 Esc 保留 Cube。", ["X"], step="01-05")
    send("ESC")
    send("F2")
    menu_capture("f2-rename-dialog", "按 F2，核對 Rename Active Item 名稱輸入框。", ["F2"], step="02-03")
    send("A", ctrl=True)
    number("ShortcutCube")
    send("RET")
    observe("f2-renamed", "在 F2 名稱欄輸入 ShortcutCube 並 Enter。", ["F2","CTRL_A","ShortcutCube","RET"],
            "ShortcutCube", lambda s: s["active"]=="ShortcutCube", step="02-03")
    send("M")
    menu_capture("m-collection-menu", "按 M，核對 Move to Collection 選單；此圖尚未移入新集合。", ["M"], step="02-03")
    send("ESC")
    send("A", ctrl=True)
    menu_capture("ctrl-a-apply-menu", "按 Ctrl+A，核對 Apply 選單；此圖尚未套用變換。", ["CTRL_A"], step="02-07")
    send("ESC")

    # Preferences belongs to this isolated process. F3 is used only to open the
    # native window; it is not proposed as an additional taught shortcut here.
    send("F3")
    number("Preferences")
    send("RET")
    do(lambda: setattr(bpy.context.preferences, "active_section", "INPUT"), 1.0)
    record("01-06", "preferences-emulate-numpad", "開啟隔離 Blender 的 Preferences，顯示 Input 中的 Emulate Numpad 欄位；未儲存偏好設定。",
           lambda: dict(activeSection=bpy.context.preferences.active_section,
                        emulateNumpad=bpy.context.preferences.inputs.use_emulate_numpad,
                        changedActiveSectionBy="Python UI-section property only; no input setting changed"), win="PREFERENCES")

    def finish_evidence():
        k.guard()
        images = {r["slug"]: dict(path=Path(r["file"]).name, sha256=r["sha256"], width=r["width"], height=r["height"],
                                  recordedAt=r["recordedAt"]) for r in g["records"] if "file" in r}
        for item in cases:
            item["screenshot"] = images[item["case"]]
        manifest = dict(schemaVersion=1, kind="native_shortcut_verification", runId=out.name,
            recordedAt=datetime.now(timezone.utc).isoformat(), blender=bpy.app.version_string,
            buildHash=bpy.app.build_hash.decode(), factoryStartup=True,
            eventSimulate=True, sceneUnitSystem=bpy.context.scene.unit_settings.system,
            sceneScaleLength=bpy.context.scene.unit_settings.scale_length,
            sourceSnapshot="source-snapshot/manifest.json", cases=cases,
            unqualifiedCases=[i["case"] for i in cases if i["passed"] is None],
            learnerCompletionAssessed=False, physicalFitAssessed=False,
            sceneSaved=False, workspaceWritesPerformed=False,
            workspaceContentsComparison="See runner-status after process exit; does not identify writes or writers",
            preferencesScreenshot=images["preferences-emulate-numpad"])
        (out/"shortcut-verification-v001.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n", "utf-8")
    do(finish_evidence, .1)
