"""05-03：以事件操作建立六孔配合試片；試驗值不代表合格間隙。"""
import json
import math
from pathlib import Path

import bmesh
import bpy

from common import Kit, PARK, PROJECT
from holeplate_checks import read_and_validate

CENTERS = (-35, -21, -7, 7, 21, 35)
CLEARANCES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
FILENAME = "u05_hole_plate_v001.blend"


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    saved = {}
    source_pin = PROJECT / "learning/evidence/05/2026-10-22-lesson05-demo-v002/demo-files/u05_fit_coupon_v001.blend"

    def active():
        obj = bpy.context.view_layer.objects.active
        if obj is None or obj.type != "MESH":
            raise RuntimeError("作用中物件不是網格")
        return obj

    def measured(obj=None):
        obj = obj or active()
        factor = bpy.context.scene.unit_settings.scale_length * 1000
        return "%s Dimensions %s、Location %s、Scale %s" % (
            obj.name, k.triple(obj.dimensions, " mm", factor), k.triple(obj.location, " mm", factor), k.triple(obj.scale, ""))

    def search(text):
        do(lambda: key("F3", x=700, y=600), 0.35)
        do(lambda: k.type_text(text), 0.35)
        do(lambda: key("RET"), 0.8)

    def transform(kind, axis, text, shift=False):
        do(lambda: key(kind, shift=shift, x=700, y=600), 0.2)
        do(lambda: key(axis), 0.15)
        do(lambda: k.type_text(text), 0.15)
        do(lambda: key("RET"), 0.45)

    def apply_scale():
        do(lambda: click(313, 38), 0.5)
        do(lambda: move(336, 141), 0.5)
        k.menu_item(533, 180, 0.6)

    def plate():
        return bpy.data.objects["Plate"]

    def assert_units():
        u = bpy.context.scene.unit_settings
        if u.system != "METRIC" or u.length_unit != "MILLIMETERS" or not math.isclose(u.scale_length, 0.001, abs_tol=1e-9):
            raise RuntimeError("毫米單位未設定成功")

    def plate_size():
        return measured(plate())

    def boolean():
        return next(m for m in plate().modifiers if m.type == "BOOLEAN")

    def bool_info():
        m = boolean()
        return "Operation %s、Solver %s、Operand %s。" % (m.operation, m.solver, m.object.name if m.object else "未指定")

    k.setup()
    # 清空的只有本次獨立出廠場景，學員視窗與檔案不在此程序。
    do(lambda: key("A", x=700, y=600), 0.3)
    do(lambda: key("X", x=700, y=600), 0.4)
    do(lambda: key("RET"), 0.8)

    def empty_scene():
        if len(bpy.data.objects):
            raise RuntimeError("獨立出廠場景未清空")
        return "本次獨立場景物件數 0；原插銷檔不改寫。"

    record("05-03", "new-scene", "在獨立 Blender 選取出廠物件、X > Delete，準備孔板新場景", empty_scene, park=PARK)
    k.add_mesh(80)
    do(lambda: click(1245, 374), 0.6)
    do(lambda: click(1302, 433), 0.6)
    do(lambda: click(1418, 557), 0.6)
    k.menu_item(1397, 668, 0.6)
    k.type_into(1417, 488, "0.001")
    k.open_sidebar()
    do(assert_units, 0.1)
    record("05-03", "units", "Scene > Units：Length 選 Millimeters、Unit Scale 0.001，再開啟 Sidebar",
           lambda: "Unit Scale %g；Length %s；%s。" % (bpy.context.scene.unit_settings.scale_length, bpy.context.scene.unit_settings.length_unit, measured()),
           highlights=[B(1266, 477, 216, 22, "0.001"), B(963, 383, 228, 77, "Dimensions")], park=PARK)

    for y, value in ((411, "96mm"), (430, "26mm"), (450, "4mm")):
        k.type_into(1075, y, value)
    apply_scale()
    k.rename_active("Plate")
    do(lambda: click(184, 38), 0.5)
    k.menu_item(236, 168, 0.8)
    k.wheel_out(2)
    record("05-03", "board", "Dimensions 輸入 96、26、4 mm，Object > Apply > Scale，命名 Plate 並對焦",
           lambda: plate_size() + "。", highlights=k.boxes(k.obj_box("Plate", "示範孔板"), B(963, 318, 228, 142, "96 × 26 × 4 mm／Scale 1")), park=PARK)
    do(lambda: key("H", x=700, y=600), 0.5)

    # 建六個方形切割體；尺寸與位移透過鍵盤變換事件輸入，直接讀回實際物件。
    for index, (x, clearance) in enumerate(zip(CENTERS, CLEARANCES), 1):
        width = 10 + clearance
        k.add_mesh(80, 0.6)
        transform("S", "X", "%g" % (width / 2))
        transform("S", "Y", "%g" % (width / 2))
        transform("S", "Z", "4")
        transform("G", "X", "%gmm" % x)
        transform("G", "Y", "2mm")

        def cutter_result(i=index, w=width, target_x=x):
            obj = active()
            factor = bpy.context.scene.unit_settings.scale_length * 1000
            expected = (w, w, 8)
            if any(not math.isclose(v * factor, target, abs_tol=1e-4) for v, target in zip(obj.dimensions, expected)):
                raise RuntimeError("方孔切割體尺寸輸入失敗：" + measured())
            if abs(obj.location.x * factor - target_x) > 1e-4 or abs(obj.location.y * factor - 2) > 1e-4:
                raise RuntimeError("方孔切割體位置輸入失敗")
            return "第 %d 個切割體：%s；這只是切割幾何，最終孔壁另行量測。" % (i, measured())

        record("05-03", "cutter-%d" % index,
               "Add > Mesh > Cube，設第 %d 孔切割體 %g × %g × 8 mm，中心 X %g、Y 2 mm（總間隙試驗點 %.1f mm）" % (index, width, width, x, clearance),
               cutter_result, highlights=[B(963, 133, 228, 59, "Location"), B(963, 383, 228, 77, "切割體 Dimensions")], park=PARK)

    # 一個圓柱，再用 Shift+D 沿 X 移動複製，形成 1～6 個盲凹點。
    search("Add Cylinder")
    # F3 Add Cylinder 的預設尺寸可依場景單位換算為 2000 mm，不能假設是 2 mm。
    for y, value in ((411, "1.2mm"), (430, "1.2mm"), (450, "2mm")):
        k.type_into(1075, y, value)
    transform("G", "X", "-35mm")
    transform("G", "Y", "-8.5mm")
    transform("G", "Z", "2.2mm")

    def assert_marker_base():
        obj = active()
        factor = bpy.context.scene.unit_settings.scale_length * 1000
        if any(not math.isclose(v * factor, target, abs_tol=1e-4) for v, target in zip(obj.dimensions, (1.2, 1.2, 2))):
            raise RuntimeError("凹點圓柱尺寸錯誤，拒絕繼續複製：" + measured())

    do(assert_marker_base, 0.1)
    record("05-03", "marker-base", "F3 搜尋 Add Cylinder，設直徑 1.2 mm、高 2 mm，中心 Z 2.2 mm，作為 0.8 mm 深的盲凹點切割體",
           lambda: measured() + "；板頂面 Z 2 mm，凹點名義底 Z 1.2 mm。",
           highlights=[B(963, 133, 228, 59, "Location"), B(963, 383, 228, 77, "圓柱 Dimensions")], park=PARK,
           note="凹點尺寸與板厚是本示範的幾何安排，沒有宣稱已通過 0.4 mm 噴嘴的列印辨識驗證。")
    previous_x = -35.0
    for index, center in enumerate(CENTERS, 1):
        for j in range(index):
            x = center + (j - (index - 1) / 2) * 1.6
            if index == 1 and j == 0:
                continue
            transform("D", "X", "%gmm" % (x - previous_x), shift=True)
            previous_x = x
        record("05-03", "markers-%d" % index, "用 Shift+D > X 複製圓柱，讓第 %d 孔下方有 %d 個凹點切割體" % (index, index),
               lambda i=index: "第 %d 組完成；目前可見切割物件 %d 個；末個物件 %s。" % (
                   i, sum(o.type == "MESH" and not o.hide_get() for o in bpy.data.objects), measured()),
               park=PARK, note="此時仍是切割體；最終孔板盲凹點數會從差集後的網格讀回。")

    def cutters_before_join():
        visible = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_get()]
        if len(visible) != 27 or not plate().hide_get():
            raise RuntimeError("切割體選取範圍錯誤：需要 6 方孔＋21 圓柱，Plate 必須隱藏")

    do(cutters_before_join, 0.1)
    do(lambda: key("A", x=700, y=600), 0.3)
    do(lambda: key("J", ctrl=True, x=700, y=600), 1.0)
    apply_scale()
    k.rename_active("Cutters")

    def joined_result():
        obj = active()
        factor = bpy.context.scene.unit_settings.scale_length * 1000
        if any(not math.isclose(v * factor, target, abs_tol=1e-4) for v, target in zip(obj.dimensions, (80.35, 16.4, 8))):
            raise RuntimeError("合併後切割體範圍錯誤，拒絕差集：" + measured())
        return "%s；場景網格物件：%s。" % (measured(), "、".join(o.name for o in bpy.context.scene.objects if o.type == "MESH"))

    record("05-03", "cutters-joined", "A 選取可見的 27 個切割體，Ctrl+J 合併、Apply Scale，命名 Cutters；Plate 仍隱藏",
           joined_result, park=PARK)
    do(lambda: key("H", alt=True, x=700, y=600), 0.6)
    k.click_outliner("Plate")
    do(lambda: click(1245, 503), 0.6)
    search("Add Boolean Modifier")
    record("05-03", "boolean-empty", "選 Plate，F3 搜尋 Add Boolean Modifier，確認 Difference 與 Object 欄位", bool_info,
           highlights=[B(1409, 340, 66, 21, "Difference"), B(1351, 389, 104, 22, "Object／滴管")], park=PARK)
    do(lambda: click(1445, 400), 0.4)
    do(lambda: click(1340, k.outliner_y("Cutters")), 0.8)

    def assigned():
        m = boolean()
        if m.operation != "DIFFERENCE" or m.object is None or m.object.name != "Cutters":
            raise RuntimeError("Boolean 的 Difference／Cutters 指定失敗：" + bool_info())
        return bool_info()

    record("05-03", "boolean-assigned", "點 Object 滴管，再點 Outliner 的 Cutters，指定為 Difference 切割物件", assigned,
           highlights=[B(1351, 389, 104, 22, "Cutters")], park=PARK)
    k.click_outliner("Cutters")
    do(lambda: key("H", x=700, y=600), 0.6)
    k.click_outliner("Plate")
    do(lambda: key("NUMPAD_7", x=700, y=600), 0.6)
    do(lambda: click(184, 38), 0.5)
    k.menu_item(236, 168, 0.8)
    k.wheel_out(1)
    record("05-03", "holes-preview", "隱藏 Cutters，選 Plate，數字鍵盤 7 看俯視圖並 Frame Selected：六個方孔與凹點出現",
           lambda: bool_info() + "Cutters 隱藏 %s；%s。" % (bpy.data.objects["Cutters"].hide_get(), plate_size()),
           highlights=k.boxes(k.obj_box("Plate", "六孔與 1～6 點標記")), park=PARK)
    do(lambda: click(1424, 320), 0.6)
    record("05-03", "apply-boolean-menu", "Boolean 標題列下拉選單，找到 Apply", bool_info,
           highlights=[B(1287, 333, 145, 20, "Apply")])
    k.menu_item(1331, 343, 1.0)

    def applied_result():
        obj = plate()
        if obj.modifiers or not obj.data.vertices or not obj.data.polygons:
            raise RuntimeError("Boolean 未套用或結果為空，不能以 Non Manifold 0 當成功")
        return "Plate 修改器數 %d、頂點 %d、邊 %d、面 %d；%s。" % (
            len(obj.modifiers), len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons), plate_size())

    record("05-03", "applied", "點 Apply，把 Difference 結果寫進 Plate 網格；隱藏的 Cutters 保留作建構來源",
           applied_result,
           highlights=k.boxes(k.obj_box("Plate", "最終孔板")), park=PARK)

    # 實際操作 Non Manifold 選取，再由只讀模組量測最終網格。
    do(lambda: key("TAB", x=700, y=600), 0.6)
    do(lambda: key("TWO", x=700, y=600), 0.3)
    do(lambda: click(280, 38), 0.4)
    k.menu_item(303, 81, 0.5)
    search("Select Non Manifold")

    def selected_edges():
        bm = bmesh.from_edit_mesh(plate().data)
        if not bm.verts or not bm.faces:
            raise RuntimeError("空網格不能通過可列印幾何檢查")
        selected = sum(e.select for e in bm.edges)
        non_manifold = sum(not e.is_manifold for e in bm.edges)
        if selected != 0 or non_manifold != 0:
            raise RuntimeError("Non Manifold 檢查未通過")
        return "Edit Mode，邊選取；Non Manifold %d、選到的邊 %d。" % (non_manifold, selected)

    record("05-03", "non-manifold", "Tab > 邊選取 > Select None，再 F3 搜尋 Select Non Manifold", selected_edges,
           highlights=[B(49, 28, 96, 20, "Edit Mode")], park=PARK)
    do(lambda: key("TAB", x=700, y=600), 0.5)

    def checked():
        result = read_and_validate(plate())
        saved["measured"] = result
        return "最終孔寬 X／Y mm：%s；六通孔 %d；凹點 %s；Non Manifold %d。" % (
            result["measured_hole_widths_mm"], result["through_holes"], result["marker_counts"], result["non_manifold_edges"])

    # 只把本次新成果另存到 demo-files；不開啟學員工作區。
    k.file_dialog(163, k.demo_dir, FILENAME)
    record("05-03", "save-dialog", "File > Save As…：指定本次 demo-files 與 u05_hole_plate_v001.blend",
           lambda: "示範資料夾 %s；檔名 %s。" % k.browser(), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("path", "示範資料夾"), k.fb_box("name", "孔板 v001"), k.fb_box("confirm", "Save As")])

    def validate_target():
        folder, name = k.browser()
        target = Path(folder).resolve() / name
        if target.parent != Path(k.demo_dir).resolve() or name != FILENAME or target.exists():
            raise RuntimeError("存檔目的地或版本不安全")
        k.guard()

    do(validate_target, 0.1)
    k.confirm_dialog(2.0)

    def saved_result():
        path = Path(bpy.data.filepath).resolve()
        if path != (Path(k.demo_dir) / FILENAME).resolve() or not path.is_file():
            raise RuntimeError("孔板未儲存到指定位置")
        saved["sha256"] = g["sha256"](str(path))
        saved["path"] = str(path)
        return "已存 %s，%d bytes，SHA-256 %s。" % (path.name, path.stat().st_size, saved["sha256"])

    record("05-03", "saved", "按 Save As，讀回孔板檔案大小與雜湊", saved_result, park=PARK)
    record("05-03", "mesh-measured", "從差集後的 Plate 網格量六孔內壁、射線確認通孔與凹點底面；不以切割體尺寸代替結果", checked,
           highlights=k.boxes(k.obj_box("Plate", "已量測的六孔板")), park=PARK,
           note="孔寬 10.1～10.6 mm 是 0.1～0.6 mm 總間隙的設計試驗點；尚未列印或試配，合格間隙仍為空。")
    k.file_dialog(56, k.demo_dir, FILENAME)
    record("05-03", "open-dialog", "File > Open…，選同一份孔板 v001 核對重開後幾何",
           lambda: "資料夾 %s；檔名 %s。" % k.browser(), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("name", "同一孔板"), k.fb_box("confirm", "Open")])
    k.confirm_dialog(2.5)

    def reopened_result():
        path = Path(bpy.data.filepath).resolve()
        if str(path) != saved["path"] or g["sha256"](str(path)) != saved["sha256"]:
            raise RuntimeError("重開孔板路徑／雜湊不一致")
        result = read_and_validate(plate())
        result.update(passed=True, kind="hole_plate", scene_path=str(path), scene_sha256=saved["sha256"], reopened=True,
                      printed=False, fit_tested=False, qualified_clearance_mm=None,
                      nominal_pin_source=str(source_pin), nominal_pin_source_sha256=g["sha256"](str(source_pin)))
        out = Path(g["OUT"])
        (out / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        k.guard()
        return "重開孔板；實際孔寬 %s；通孔 %d；各孔凹點 %s；檔案 SHA-256 一致。未列印、未試配。" % (
            result["measured_hole_widths_mm"], result["through_holes"], result["marker_counts"])

    record("05-03", "reopened-verified", "按 Open，再由最終網格重新量孔與凹點，核對雜湊並保存 verification.json", reopened_result,
           highlights=k.boxes(k.obj_box("Plate", "重開驗證的試驗孔板")), park=PARK,
           note="六個總間隙都是試驗點，沒有任何一個被標為已驗證的合格間隙。")
