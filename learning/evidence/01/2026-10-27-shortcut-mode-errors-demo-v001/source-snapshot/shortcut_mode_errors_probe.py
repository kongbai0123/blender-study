"""Object Mode shortcut mistakes: native events, raw screenshots, readback only.

No scene/prefs file is saved. Scene changes, view changes and Undo are delivered
through window.event_simulate. Only evidence and source snapshots are written.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import bpy

from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g["OUT"])
    cases, memo = [], {}
    snapshot = out / "source-snapshot"
    snapshot.mkdir()
    sources = []
    for rel in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py",
                "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/shortcut_mode_errors_probe.py"):
        target = snapshot / Path(rel).name
        target.write_bytes((PROJECT / rel).read_bytes())
        sources.append(dict(source=rel, snapshot="source-snapshot/" + target.name,
                            sha256=g["sha256"](str(target))))
    (snapshot / "manifest.json").write_text(json.dumps(dict(files=sources), indent=2)+"\n", "utf-8")

    def channel_read(fcurve):
        return dict(dataPath=fcurve.data_path, arrayIndex=fcurve.array_index,
                    points=[dict(co=list(p.co), interpolation=p.interpolation,
                                 selected=bool(p.select_control_point)) for p in fcurve.keyframe_points])

    def animation_read(obj):
        ad = obj.animation_data
        action = ad.action if ad else None
        result = dict(animationData=ad is not None, action=action.name if action else None,
                      actionSlot=getattr(getattr(ad, "action_slot", None), "identifier", None),
                      channels=[], layers=[], legacyFcurvesAvailable=False)
        if not action:
            return result
        for layer in getattr(action, "layers", []):
            layer_data = dict(name=layer.name, strips=[])
            for strip in layer.strips:
                strip_data = dict(type=strip.type, channelbags=[])
                for bag in getattr(strip, "channelbags", []):
                    channels = [channel_read(fc) for fc in bag.fcurves]
                    strip_data["channelbags"].append(dict(slotHandle=bag.slot_handle, channels=channels))
                    result["channels"].extend(channels)
                layer_data["strips"].append(strip_data)
            result["layers"].append(layer_data)
        if hasattr(action, "fcurves"):
            result["legacyFcurvesAvailable"] = True
            # Do not count a compatibility collection twice if slots exist.
            if not result["channels"]:
                result["channels"] = [channel_read(fc) for fc in action.fcurves]
        result["pointCount"] = sum(len(fc["points"]) for fc in result["channels"])
        result["keyedFrames"] = sorted(set(p["co"][0] for fc in result["channels"] for p in fc["points"]))
        return result

    def state():
        obj = bpy.context.view_layer.objects.active
        view = k.view3d()
        render = bpy.context.scene.render
        wm = bpy.context.window_manager
        return dict(version=bpy.app.version_string, buildHash=bpy.app.build_hash.decode(),
                    active=obj.name if obj else None, mode=bpy.context.mode,
                    selected=sorted(o.name for o in bpy.context.selected_objects),
                    location=list(obj.location) if obj else None,
                    rotation=list(obj.rotation_euler) if obj else None,
                    scale=list(obj.scale) if obj else None,
                    mesh=dict(vertices=len(obj.data.vertices), edges=len(obj.data.edges),
                              polygons=len(obj.data.polygons)) if obj and obj.type == "MESH" else None,
                    animation=animation_read(obj) if obj else None,
                    allActions=sorted(a.name for a in bpy.data.actions),
                    frame=bpy.context.scene.frame_current,
                    viewPerspective=view.region_3d.view_perspective,
                    viewShading=view.shading.type,
                    viewRenderBorder=dict(enabled=view.use_render_border,
                        xmin=view.render_border_min_x, xmax=view.render_border_max_x,
                        ymin=view.render_border_min_y, ymax=view.render_border_max_y),
                    sceneRenderBorder=dict(enabled=render.use_border, xmin=render.border_min_x,
                        xmax=render.border_max_x, ymin=render.border_min_y, ymax=render.border_max_y),
                    recentOperators=[op.bl_idname for op in wm.operators][-8:],
                    modalOperators=[op.bl_idname for op in getattr(k.window(), "modal_operators", [])],
                    timelineEditors=[dict(type=a.type, uiType=a.ui_type, width=a.width, height=a.height)
                                     for a in k.window().screen.areas if a.type in {"DOPESHEET_EDITOR", "TIMELINE"}])

    def summary(s):
        return {key: s[key] for key in ("active", "mode", "selected", "location", "rotation", "scale", "mesh",
                                       "animation", "viewPerspective", "viewShading", "viewRenderBorder", "sceneRenderBorder")}

    def observe(case, action, events, expectation=None, check=None, note=None):
        def read():
            actual = state()
            passed = bool(check(actual)) if check else None
            entry = dict(case=case, events=events, expected=expectation,
                         actual=actual, passed=passed, method="native_events_and_readback")
            cases.append(entry)
            memo[case] = actual
            if passed is False:
                raise RuntimeError("Mode error probe failed: " + json.dumps(entry, ensure_ascii=False))
            return actual
        # Modal border crosshair is evidence: never move/park before capture.
        k.record("shortcut-mode", case, action, read, note=note)

    def send(kind, **flags):
        k.do(lambda: k.key(kind, x=700, y=600, **flags), .7)

    def keymap_read():
        result = []
        keyconfig = bpy.context.window_manager.keyconfigs.default
        for km in keyconfig.keymaps:
            for item in km.keymap_items:
                ordinary = item.type in {"I", "E"} and not any((item.shift, item.ctrl, item.alt, item.oskey))
                border = item.type == "B" and item.ctrl and not any((item.shift, item.alt, item.oskey))
                if ordinary or border or "clear_render_border" in item.idname:
                    result.append(dict(map=km.name, spaceType=km.space_type, regionType=km.region_type,
                        idname=item.idname, type=item.type, value=item.value, ctrl=item.ctrl,
                        shift=item.shift, alt=item.alt, oskey=item.oskey, any=item.any, active=item.active))
        path = out / "factory-keymap-mode-errors-v001.json"
        path.write_text(json.dumps(dict(version=bpy.app.version_string, buildHash=bpy.app.build_hash.decode(),
            keyconfig=keyconfig.name, matches=result), ensure_ascii=False, indent=2)+"\n", "utf-8")

    k.setup()
    k.do(keymap_read, .1)
    observe("baseline", "核對 Object Mode、Cube 與尚無動畫的出廠場景。", [],
            "Blender 5.2.1, Object Mode, Cube, no animation",
            lambda s: bpy.app.version == (5, 2, 1) and s["mode"] == "OBJECT" and s["active"] == "Cube"
                      and s["animation"]["animationData"] is False)
    send("I")
    observe("object-i-keyframe", "滑鼠在 3D Viewport、Object Mode 選取 Cube，按 I，讀回動畫與時間軸。", ["I"],
            "Observe actual animation action, channels and keyframe points; no assumption from keymap")
    # Undo only after I is known to have created keys; do not consume an earlier operation.
    def undo_i():
        if not memo["object-i-keyframe"]["animation"].get("pointCount", 0):
            raise RuntimeError("I created no keyframe points; refusing blind Undo")
        k.key("Z", x=700, y=600, ctrl=True)
    k.do(undo_i, .9)
    observe("object-i-undo", "I 插入鍵後立刻 Ctrl+Z，核對動畫是否回到操作前。", ["CTRL_Z"],
            "Cube animationData is false and transforms/mesh match baseline",
            lambda s: s["animation"]["animationData"] is False
                      and s["location"] == memo["baseline"]["location"] and s["mesh"] == memo["baseline"]["mesh"])
    send("E")
    observe("object-e", "Object Mode、Cube 已選取、游標在 3D Viewport 按 E，核對實際反應。", ["E"],
            "Observe this factory Object Mode context only; do not infer other editors/keymaps",
            lambda s: summary(s) == summary(memo["object-i-undo"]))

    send("B", ctrl=True)
    observe("perspective-border-invoke-esc", "一般透視 Object Mode 按 Ctrl+B，保留游標與原生框選指示。", ["CTRL_B"],
            "Inspect original screenshot and native modal operator")
    send("ESC")
    observe("perspective-border-esc", "按 Esc 取消一般透視的 Ctrl+B 指令，讀回資料。", ["ESC"],
            "State equals state before Ctrl+B", lambda s: summary(s) == summary(memo["object-e"]))
    send("B", ctrl=True)
    observe("perspective-border-invoke-rmb", "一般透視再按 Ctrl+B，準備右鍵取消對照。", ["CTRL_B"])
    k.do(lambda: k.click(700, 600, button="RIGHTMOUSE"), .7)
    observe("perspective-border-rmb", "滑鼠右鍵取消 Ctrl+B，讀回資料。", ["RIGHTMOUSE"],
            "State equals state before Ctrl+B", lambda s: summary(s) == summary(memo["object-e"]))

    send("B", ctrl=True)
    k.do(lambda: k.drag_slow([(430, 320), (500, 370), (650, 470), (800, 580)]), .3)
    observe("perspective-border-complete", "一般透視 Ctrl+B 後左鍵拖曳矩形並放開，讀回是否產生 render border。",
            ["CTRL_B", "LEFTMOUSE_DRAG_430_320_TO_800_580"], "Observe real result in Solid perspective")
    # Camera view is changed via its verified native shortcut, not by setting region_3d.
    send("NUMPAD_0")
    observe("camera-baseline", "按數字鍵盤 0 切相機視圖，準備 Object Mode 的 render-border 對照。", ["NUMPAD_0"],
            "CAMERA", lambda s: s["viewPerspective"] == "CAMERA")
    send("B", ctrl=True)
    observe("camera-border-invoke", "相機視圖、Object Mode 按 Ctrl+B，記錄原生十字游標與 modal。", ["CTRL_B"])
    send("ESC")
    observe("camera-border-esc", "相機視圖 Ctrl+B 後按 Esc 取消。", ["ESC"],
            "Render settings unchanged", lambda s: s["sceneRenderBorder"] == memo["camera-baseline"]["sceneRenderBorder"])
    send("B", ctrl=True)
    k.do(lambda: k.click(700, 600, button="RIGHTMOUSE"), .7)
    observe("camera-border-rmb", "相機視圖再按 Ctrl+B，右鍵取消。", ["CTRL_B", "RIGHTMOUSE"],
            "Render settings unchanged", lambda s: s["sceneRenderBorder"] == memo["camera-baseline"]["sceneRenderBorder"])
    send("B", ctrl=True)
    k.do(lambda: k.drag_slow([(430, 320), (500, 370), (650, 470), (800, 580)]), .3)
    observe("camera-border-complete", "相機視圖 Ctrl+B 後拖出矩形並放開，讀回 scene render border。",
            ["CTRL_B", "LEFTMOUSE_DRAG_430_320_TO_800_580"], "Observe scene border actual values")
    def undo_border():
        before = memo["camera-baseline"]["sceneRenderBorder"]
        after = memo["camera-border-complete"]["sceneRenderBorder"]
        if before == after:
            raise RuntimeError("No camera render-border change; refusing blind Undo")
        k.key("Z", x=700, y=600, ctrl=True)
    k.do(undo_border, .9)
    observe("camera-border-undo", "已建立相機 render border 後立刻 Ctrl+Z，讀回是否回到原設定。", ["CTRL_Z"],
            "Observe Undo, do not assume render-border undoability")

    def clear_border_by_keymap():
        # Inspect the installed default map before delivering the event. The
        # resulting enabled flag is read again; mapping alone is not proof.
        km = bpy.context.window_manager.keyconfigs.default.keymaps.get("3D View")
        found = [item for item in km.keymap_items if item.active and item.idname == "view3d.clear_render_border"]
        if len(found) != 1:
            raise RuntimeError("Expected one active native clear_render_border mapping")
        item = found[0]
        memo["clearBorderKey"] = dict(type=item.type, ctrl=item.ctrl, alt=item.alt,
                                      shift=item.shift, oskey=item.oskey)
        k.key(item.type, x=700, y=600, ctrl=item.ctrl, alt=item.alt, shift=item.shift, oskey=item.oskey)
    k.do(clear_border_by_keymap, .9)
    observe("camera-border-clear", "讀出出廠 Clear Render Region 鍵位並原生送出，讀回取消框選範圍。",
            ["DEFAULT_KEYMAP_view3d.clear_render_border"], "Render use_border disabled",
            lambda s: s["sceneRenderBorder"]["enabled"] is False)

    def finish():
        k.guard()
        images = {r["slug"]: dict(path=r["file"], sha256=r["sha256"], width=r["width"], height=r["height"],
                                recordedAt=r["recordedAt"]) for r in g["records"] if "file" in r}
        for case in cases:
            case["screenshot"] = images[case["case"]]
        result = dict(schemaVersion=1, kind="native_shortcut_mode_error_verification", runId=out.name,
            recordedAt=datetime.now(timezone.utc).isoformat(), blender=bpy.app.version_string,
            buildHash=bpy.app.build_hash.decode(), factoryStartup=True, eventSimulate=True,
            sourceSnapshot="source-snapshot/manifest.json", keymap="factory-keymap-mode-errors-v001.json",
            sceneSaved=False, preferencesSaved=False, learnerCompletionAssessed=False,
            workspaceContentsComparison="See runner-status; snapshots do not prove no intervening write or writer",
            clearRenderBorderKey=memo.get("clearBorderKey"), cases=cases)
        (out / "shortcut-mode-errors-verification-v001.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", "utf-8")
    k.do(finish, .1)
