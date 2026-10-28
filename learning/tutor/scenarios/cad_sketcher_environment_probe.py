"""Isolated stable CAD Sketcher bootstrap and native-event sketch trial.

Extension enabling and millimetre scene setup are explicitly environment setup.
Sketch creation/editing is sent as native UI events; Python only observes geometry.
"""
import importlib
import json
import os
import sys
from pathlib import Path

import addon_utils
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    out = Path(g["OUT"])
    source = out / "source-snapshot"
    source.mkdir()
    files = []
    for rel in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py",
                "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/cad_sketcher_environment_probe.py"):
        target = source / Path(rel).name
        target.write_bytes((PROJECT / rel).read_bytes())
        files.append({"source": rel, "snapshot": target.name, "sha256": g["sha256"](target)})
    (source / "manifest.json").write_text(json.dumps(files, indent=2), "utf-8")
    module_name = "bl_ext.user_default.CAD_Sketcher"
    memo = {}

    def bootstrap():
        addon_utils.enable(module_name, default_set=True, persistent=True)
        if module_name not in bpy.context.preferences.addons:
            raise RuntimeError("CAD Sketcher did not enable")
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.scale_length = .001
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        ref = importlib.import_module(module_name + ".model.sketch_ref")
        memo["ref"] = ref
        import slvs
        details = {"blender": bpy.app.version_string, "buildHash": bpy.app.build_hash.decode(),
                   "python": sys.version, "module": module_name, "version": "0.32.1",
                   "slvsModule": Path(slvs.__file__).name,
                   "unitScale": bpy.context.scene.unit_settings.scale_length,
                   "setupMethod": "programmatic isolated extension enable and scene units; not UI teaching actions",
                   "learnerPreferencesSaved": False}
        (out / "environment-readback.json").write_text(json.dumps(details, indent=2), "utf-8")

    def read_state():
        value = {"mode": bpy.context.mode,
                 "objects": [{"name": o.name, "type": o.type} for o in bpy.context.scene.objects]}
        ref = memo.get("ref")
        sketch = ref.get_active_sketch(bpy.context) if ref else None
        if sketch:
            value["sketch"] = {"name": sketch.name, "dof": sketch.dof,
                               "solverState": sketch.solver_state,
                               "geometrySolved": sketch.geometry_solved}
            obj = sketch.target_object
            value["sketch"]["positions"] = [list(p.vector) for p in obj.data.attributes["position"].data] if "position" in obj.data.attributes else []
            value["sketch"]["attributes"] = [{"name":a.name,"domain":a.domain,"type":a.data_type} for a in obj.data.attributes]
            value["sceneProperties"] = {key: val for key,val in bpy.context.scene.items() if key.startswith("slvs:c:") and isinstance(val,(float,int))}
        (out / "latest-state.json").write_text(json.dumps(value, indent=2), "utf-8")
        return value

    def send(key, **kw):
        k.do(lambda: k.key(key, x=600, y=450, **kw), .5)

    def search(text):
        send("F3")
        k.do(lambda: k.type_text(text), .4)
        send("RET")

    def at_world(co, click=False):
        a=k.area("VIEW_3D")
        region=next(r for r in a.regions if r.type=="WINDOW")
        point=location_3d_to_region_2d(region,a.spaces.active.region_3d,Vector(co))
        xy=(int(region.x+point.x),int(k.window().height-region.y-point.y))
        (k.click if click else k.move)(*xy)

    k.setup()
    k.do(bootstrap, 2)
    k.record("CAD-ENV", "enabled", "環境啟用：獨立 CAD Sketcher 0.32.1 與毫米設定（程式設定）", read_state)
    send("A")
    send("X")
    send("RET")
    send("A", ctrl=True, shift=True)
    k.record("CAD-ENV", "sketch-plane-picker", "Ctrl+Shift+A 啟動 Add Sketch，觀察工作平面選擇", read_state)
    send("Z")
    k.record("CAD-ENV", "origin-sketch", "Add Sketch 工具內按 Z 選 XY 草圖平面", read_state)
    send("N")
    k.do(lambda:k.click(1214,264), .7)
    k.record("CAD-ENV", "sidebar", "開啟 Sidebar，觀察擴充套件面板", read_state)
    k.wheel_out(9)
    send("R")
    k.do(lambda:k.click(614,475), .7)
    k.do(lambda:k.move(850,300), .4)
    k.do(lambda:k.type_text("60"), .4)
    send("TAB")
    k.do(lambda:k.type_text("40"), .4)
    k.record("CAD-ENV", "rectangle-numeric", "Corner Rectangle 第一點取原點，輸入 60、Tab、40", read_state)
    send("RET")
    send("ESC")
    k.record("CAD-ENV", "rectangle", "確認矩形，讀回草圖點座標與約束狀態", read_state)
    k.do(lambda:k.drag_slow([(600,450),(400,550)],button="MIDDLEMOUSE",shift=True), .8)
    send("D")
    k.do(lambda:at_world((30,0,0),True),.5)
    k.do(lambda:at_world((30,-8,0)),.5)
    k.do(lambda:k.type_text("60"),.4)
    send("RET")
    send("ESC")
    k.record("CAD-ENV", "width-dimension", "Dimension 選底邊並輸入 60 mm，新增驅動尺寸", read_state)
    send("D")
    k.do(lambda:at_world((60,20,0),True),.5)
    k.do(lambda:at_world((70,20,0)),.5)
    k.do(lambda:k.type_text("40"),.4)
    send("RET")
    send("ESC")
    k.record("CAD-ENV", "height-dimension", "Dimension 選右邊並輸入 40 mm，讀回自由度", read_state)
