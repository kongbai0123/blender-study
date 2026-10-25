"""05-02 方形插銷：獨立 Blender、模擬事件、逐步實拍與重開檔驗證。

只使用已核准的 10 × 10 × 8 mm；不填入尚未決定的配合間隙。
模型操作一律經事件模擬；直接 Python 僅用於欄位安全填寫、截圖及驗證。
"""
import json
import math
import os
from pathlib import Path

import bmesh
import bpy

from common import PARK, Kit


def build(g):
    k = Kit(g)
    do, click, move, record = k.do, k.click, k.move, k.record
    B = k.box
    filename = "u05_fit_coupon_v001.blend"
    saved = {}

    def pin():
        obj = bpy.context.view_layer.objects.active
        if obj is None or obj.type != "MESH":
            raise RuntimeError("作用中物件不是插銷網格")
        return obj

    def dimensions_mm():
        factor = bpy.context.scene.unit_settings.scale_length * 1000
        return [round(v * factor, 6) for v in pin().dimensions]

    def size():
        obj = pin()
        return "%s Dimensions %s、Scale %s" % (
            obj.name, k.triple(dimensions_mm(), " mm"), k.triple(obj.scale, ""))

    def units():
        u = bpy.context.scene.unit_settings
        return "Unit System %s、Length %s、Unit Scale %s" % (
            u.system, u.length_unit, k.num(u.scale_length))

    def mesh_result():
        obj = pin()
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            count = sum(not edge.is_manifold for edge in bm.edges)
            factor = bpy.context.scene.unit_settings.scale_length * 1000
            volume = bm.calc_volume(signed=True) * factor ** 3
            return count, round(volume, 6)
        finally:
            bm.free()

    def verify_geometry():
        dims = dimensions_mm()
        obj = pin()
        u = bpy.context.scene.unit_settings
        if u.system != "METRIC" or u.length_unit != "MILLIMETERS" or not math.isclose(u.scale_length, 0.001, abs_tol=1e-9):
            raise RuntimeError("場景單位不符合毫米工程設定：" + units())
        if any(not math.isclose(v, target, rel_tol=0, abs_tol=1e-6) for v, target in zip(dims, (10, 10, 8))) or any(not math.isclose(v, 1, abs_tol=1e-6) for v in obj.scale):
            raise RuntimeError("插銷尺寸或 Scale 驗證失敗：" + size())
        non_manifold, volume = mesh_result()
        # 單位與網格用單精度浮點儲存，立方後誤差會放大；這是數值比較，並非製造允差。
        if non_manifold != 0 or not math.isclose(volume, 800, rel_tol=1e-6, abs_tol=1e-6):
            raise RuntimeError("插銷封閉體積驗證失敗：%s、%s" % (non_manifold, volume))

    k.setup()
    record("05-02", "factory-scene", "在獨立 Blender 的出廠場景開始；不接管學員的視窗",
           lambda: "Blender %s；模式 %s；%s。" % (bpy.app.version_string, bpy.context.mode, size()),
           highlights=k.boxes(k.obj_box("Cube", "預設 Cube")), park=PARK)

    # 單位沿用 lesson04 已實拍核對的位置。
    do(lambda: click(1245, 374), 0.8)
    do(lambda: click(1302, 433), 0.8)
    record("05-02", "units-before", "Properties 點 Scene 分頁，展開 Units",
           lambda: units() + "。",
           highlights=[B(1236, 364, 20, 20, "Scene"), B(1266, 452, 216, 115, "Units")], park=PARK)
    do(lambda: click(1418, 557), 0.8)
    k.menu_item(1397, 668)
    k.type_into(1417, 488, "0.001")
    k.open_sidebar()
    record("05-02", "units-mm", "Length 選 Millimeters，Unit Scale 輸入 0.001，再開啟 View > Sidebar",
           lambda: "%s；%s。" % (units(), size()),
           highlights=[B(1266, 477, 216, 22, "Unit Scale 0.001"), B(1266, 547, 216, 20, "Millimeters"),
                       B(963, 383, 228, 77, "目前 2 × 2 × 2 mm")], park=PARK)

    # 每個尺寸欄位單獨操作、截圖與讀回，不能由輸入文字推定成功。
    for axis, field_y, value in (("X", 411, "10mm"), ("Y", 430, "10mm"), ("Z", 450, "8mm")):
        k.type_into(1075, field_y, value)
        record("05-02", "dimension-" + axis.lower(), "Dimensions %s 輸入 %s，按 Enter" % (axis, value),
               lambda: size() + "。",
               highlights=[B(963, field_y - 10, 228, 20, "Dimensions " + axis)], park=PARK)

    do(lambda: click(313, 38), 0.8)
    do(lambda: move(336, 141), 0.8)
    do(lambda: move(533, 180), 0.6)
    record("05-02", "apply-menu", "Object > Apply，移到 Scale",
           lambda: "選單已展開；" + size() + "。",
           highlights=[B(289, 28, 48, 20, "Object"), B(292, 131, 192, 20, "Apply"), B(492, 170, 220, 20, "Scale")])
    k.menu_item(533, 180)
    record("05-02", "scale-applied", "點 Scale：把縮放套用到網格",
           lambda: size() + "。",
           highlights=[B(963, 318, 176, 59, "Scale 1、1、1"), B(963, 383, 228, 77, "Dimensions 不變")], park=PARK)

    k.rename_active("FitPin")
    do(lambda: click(184, 38), 0.6)
    k.menu_item(236, 168, 1.2)
    k.wheel_out(3)
    do(verify_geometry, 0.2)
    record("05-02", "pin-checked", "Edit > Rename Active Item 命名 FitPin；View > Frame Selected 後縮小視角，讀回尺寸與封閉體積",
           lambda: "%s；不封閉的邊 %d 條，體積 %g mm³。" % ((size(),) + mesh_result()),
           highlights=k.boxes(k.obj_box("FitPin", "10 × 10 × 8 mm 插銷"), B(963, 318, 228, 142, "Scale／Dimensions")),
           park=PARK, note="不封閉邊數及體積由 Blender 網格讀回；尚未列印或試配，正式配合間隙待定。")

    # 直接把瀏覽器欄位填入示範資料夾，絕不以學員工作區當儲存目標。
    k.file_dialog(163, k.demo_dir, filename)
    record("05-02", "save-dialog", "File > Save As…：資料夾填入本次 demo-files，檔名 u05_fit_coupon_v001.blend",
           lambda: "資料夾：%s；檔名：%s。" % k.browser(), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("path", "助教示範資料夾"), k.fb_box("name", "v001"), k.fb_box("confirm", "Save As")],
           note="只有資料夾與檔名欄位用程式安全填入，其餘操作用事件模擬；這是助教示範檔，不是學員成果。")

    def assert_save_target():
        directory, name = k.browser()
        if Path(directory).resolve() != Path(k.demo_dir).resolve() or name != filename:
            raise RuntimeError("存檔目的地不是本次示範資料夾")
        if (Path(directory) / name).exists():
            raise RuntimeError("示範版本已存在，拒絕覆寫")
        k.guard()

    do(assert_save_target, 0.2)
    k.confirm_dialog(2.0)

    def saved_result():
        expected = (Path(k.demo_dir) / filename).resolve()
        if Path(bpy.data.filepath).resolve() != expected or not expected.is_file():
            raise RuntimeError("示範檔未成功存到指定位置")
        verify_geometry()
        saved["sha256"] = g["sha256"](str(expected))
        saved["path"] = str(expected)
        return "已存檔 %s（%d bytes）；SHA-256 %s；%s。" % (
            expected.name, expected.stat().st_size, saved["sha256"], size())

    record("05-02", "saved", "按 Save As 後，核對實際檔案存在、大小與 SHA-256", saved_result,
           highlights=[B(0, 997, 1494, 22, "存檔狀態")], park=PARK)
    k.file_dialog(56, k.demo_dir, filename)
    record("05-02", "reopen-dialog", "File > Open…：選剛儲存的 u05_fit_coupon_v001.blend",
           lambda: "開啟資料夾：%s；檔名：%s。" % k.browser(), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("name", "同一個 v001"), k.fb_box("confirm", "Open")])
    k.confirm_dialog(2.5)

    def reopened_result():
        verify_geometry()
        path = Path(bpy.data.filepath).resolve()
        if str(path) != saved["path"] or g["sha256"](str(path)) != saved["sha256"]:
            raise RuntimeError("重新開啟的檔案路徑或雜湊不一致")
        k.guard()
        non_manifold, volume = mesh_result()
        verification = {
            "passed": True, "dimensions_mm": dimensions_mm(), "scale": [round(v, 6) for v in pin().scale],
            "unit_scale": round(bpy.context.scene.unit_settings.scale_length, 9),
            "length_unit": bpy.context.scene.unit_settings.length_unit, "non_manifold_edges": non_manifold,
            "closed_volume": non_manifold == 0 and volume > 0, "volume_mm3": volume,
            "scene_path": str(path), "scene_sha256": saved["sha256"], "reopened": True,
            "clearance_mm": None, "printed": False, "fit_tested": False,
            "numericComparison": {"purpose": "Floating point reconstruction only; not manufacturing tolerance", "dimensionsAbsMm": 1e-6, "volumeRelative": 1e-6},
        }
        (Path(g["OUT"]) / "verification.json").write_text(
            json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return "重開 %s；%s；不封閉的邊 %d 條，體積 %g mm³；磁碟檔 SHA-256 與存檔時相同。" % (
            path.name, size(), non_manifold, volume)

    record("05-02", "reopened-verified", "按 Open，重新讀回尺寸、Scale、封閉體積及同一檔案雜湊", reopened_result,
           highlights=k.boxes(k.obj_box("FitPin", "重新開啟的插銷"), B(963, 318, 228, 142, "10 × 10 × 8 mm／Scale 1")),
           park=PARK, note="此結果只驗證模型與檔案重開一致；不代表印出尺寸合格或已找到合適間隙。")
