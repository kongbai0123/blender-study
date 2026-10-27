"""Verify main-row versus numeric-keypad input and isolated Emulate Numpad.

The checkbox is actually clicked in the isolated Preferences window. Closing
that auxiliary window uses the window-close operator solely to resume event
tests in the main viewport; no scene geometry/transform is written by Python.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import bpy
from common import Kit, PARK, PROJECT


def build(g):
    k = Kit(g)
    do, key, click, record = k.do, k.key, k.click, k.record
    out = Path(g["OUT"])
    snaps = out / "source-snapshot"
    snaps.mkdir()
    files=[]
    for rel in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py",
                "learning/tutor/scenarios/common.py", "learning/tutor/scenarios/shortcut_keyboard_probe.py"):
        target=snaps/Path(rel).name
        target.write_bytes((PROJECT/rel).read_bytes())
        files.append(dict(source=rel, snapshot="source-snapshot/"+target.name, sha256=g["sha256"](str(target))))
    (snaps/"manifest.json").write_text(json.dumps(dict(files=files),indent=2)+"\n", "utf-8")
    cases=[]
    memory={}

    def state():
        v=k.view3d().region_3d
        return dict(viewPerspective=v.view_perspective, viewRotation=list(v.view_rotation),
                    viewLocation=list(v.view_location), viewDistance=v.view_distance,
                    emulateNumpad=bpy.context.preferences.inputs.use_emulate_numpad,
                    selected=sorted(o.name for o in bpy.context.selected_objects))

    def same(a,b):
        return len(a)==len(b) and all(abs(x-y)<1e-5 for x,y in zip(a,b))

    def send(kind,**flags):
        do(lambda:key(kind,x=700,y=600,**flags),.5)

    def shot(case,action,events,expect,check=None,win="main",note=None,park=True):
        def observe():
            s=state()
            passed=None if check is None else bool(check(s))
            cases.append(dict(case=case,events=events,expected=expect,actual=s,passed=passed))
            if passed is False: raise RuntimeError("Keyboard check failed: "+json.dumps(cases[-1]))
            return s
        record("01-06",case,action,observe,win=win,note=note,park=PARK if park and win=="main" else None)

    k.setup()
    do(lambda:memory.update(initial=state()),.1)
    send("ONE")
    shot("main-one-no-emulation", "Emulate Numpad 關閉時按主鍵盤上排 1，核對視角不會切成 Front。", ["ONE"],
         "Initial user-perspective view unchanged", lambda s: s["emulateNumpad"] is False and s["viewPerspective"]==memory["initial"]["viewPerspective"] and same(s["viewRotation"],memory["initial"]["viewRotation"]))
    send("NUMPAD_1")
    shot("numpad-one-front", "同樣設定下按數字鍵盤 1，切到 Front Orthographic。", ["NUMPAD_1"],
         "Front orthographic",lambda s:s["viewPerspective"]=="ORTHO")
    do(lambda:memory.update(front=state()),.1)
    send("NUMPAD_3")
    shot("numpad-three-right", "數字鍵盤 3 切到 Right Orthographic，供模擬設定對照。", ["NUMPAD_3"],
         "Right orthographic different from front",lambda s:s["viewPerspective"]=="ORTHO" and not same(s["viewRotation"],memory["front"]["viewRotation"]))
    send("F3")
    do(lambda:k.type_text("Preferences"),.3)
    send("RET")
    do(lambda:setattr(bpy.context.preferences,"active_section","INPUT"),.7)
    shot("emulate-checkbox-before", "隔離 Preferences 的 Input 頁中，Emulate Numpad 尚未勾選。", ["F3", "Preferences", "RET"],
         False,lambda s:s["emulateNumpad"] is False,win="PREFERENCES",park=False,
         note="只有 Preferences 的 active_section 由 Python 設為 INPUT 以顯示頁面；輸入設定仍由下一步真實點擊改變。")
    do(lambda:click(466,44,win="PREFERENCES"),.7)
    shot("emulate-checkbox-after", "點 Keyboard 下的 Emulate Numpad 方框；只作用於隔離示範，不按 Save Preferences。", ["CLICK",466,44],
         True,lambda s:s["emulateNumpad"] is True,win="PREFERENCES",park=False)

    def close_preferences():
        w=k.window("PREFERENCES")
        with bpy.context.temp_override(window=w,area=w.screen.areas[0]):
            bpy.ops.wm.window_close()
    do(close_preferences,.7)
    send("ONE")
    shot("main-one-emulated-observation", "開啟 Emulate Numpad 後送主鍵盤上排 1 事件；核對實際視角，不預設模擬事件有經過實體鍵盤的重映射。", ["ONE"],
         "Observe whether simulated ONE matches NUMPAD_1; the previous v001 assertion failed")
    def unicode_one():
        g["_event"](k.window(),"ONE","PRESS",700,600,unicode="1")
        g["_event"](k.window(),"ONE","RELEASE",700,600)
    do(unicode_one,.7)
    shot("main-one-unicode-observation", "同設定再送含 unicode=1 的主 ONE 事件作對照，仍只記實際結果。", ["ONE unicode=1"],
         "Observe result; no promotion of setting-on to effective emulation")
    send("PERIOD")
    shot("main-period-pivot", "主鍵盤句點鍵是 Pivot Point 選單；Emulate Numpad 不把它變成 Numpad Decimal。", ["PERIOD"],
         "Inspect native Pivot Point popup",win="main",park=False)
    send("ESC")
    send("NUMPAD_PERIOD")
    shot("numpad-period-framed", "數字鍵盤小數點仍是 Frame Selected，核對視角距離。", ["NUMPAD_PERIOD"],
         "View distance changes to frame Cube",lambda s:s["viewDistance"] < memory["front"]["viewDistance"])

    def finish():
        k.guard()
        images={r["slug"]:dict(path=r["file"],sha256=r["sha256"],width=r["width"],height=r["height"],recordedAt=r["recordedAt"]) for r in g["records"] if "file" in r}
        for c in cases:c["screenshot"]=images[c["case"]]
        value=dict(schemaVersion=1,kind="native_keyboard_emulation_verification",runId=out.name,
            recordedAt=datetime.now(timezone.utc).isoformat(),blender=bpy.app.version_string,
            buildHash=bpy.app.build_hash.decode(),factoryStartup=True,eventSimulate=True,cases=cases,
            preferencesSaved=False,preferencesScope="isolated temporary runner config only",
            sceneSaved=False,learnerCompletionAssessed=False,physicalFitAssessed=False,
            emulateEffectViaSimulatedOneVerified=any(same(c["actual"]["viewRotation"],memory["front"]["viewRotation"]) for c in cases if c["case"] in ("main-one-emulated-observation","main-one-unicode-observation")),
            limitation="The v001 simulated-ONE front-view assertion failed after the checkbox was enabled. This v002 records both plain and unicode-bearing events without treating failure as success. Actual physical-keyboard emulation remains unverified if neither matches NUMPAD_1.",
            workspaceWriteAttribution=None,workspaceContentsComparison="See runner-status; not proof of no intervening writes",
            auxiliaryNonEventSetup=["preferences.active_section = INPUT", "wm.window_close for Preferences only"])
        (out/"keyboard-verification-v001.json").write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n", "utf-8")
    do(finish,.1)
