"""第四單元 04-02～04-07：通用小盒（毫米單位、開口、壁厚、網格檢查、匯出 STL）的助教實際操作示範。

壁厚 2 mm 只是示範值；課程中的壁厚待依噴嘴與線寬決定。示範檔與 STL 只存到本次輸出資料夾的 demo-files。
"""
import os
import struct

import bmesh
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import PARK, Kit

DEMO_WALL = "2mm"


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box

    def cube():
        return bpy.data.objects["Cube"]

    def units():
        u = bpy.context.scene.unit_settings
        return "Length %s、Unit Scale %s" % (u.length_unit, k.num(u.scale_length))

    def size():
        o = cube()
        return "Cube Dimensions %s、Scale %s" % (k.triple(o.dimensions, " mm"), k.triple(o.scale, ""))

    def shell():
        """讀回修改器套用後的實際網格：外形、內腔、底厚（1 個 Blender 單位 = 1 mm）。"""
        o = cube()
        mesh = o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        xs = sorted({round(v.co.x, 4) for v in mesh.vertices})
        ys = sorted({round(v.co.y, 4) for v in mesh.vertices})
        zs = sorted({round(v.co.z, 4) for v in mesh.vertices})
        faces = len(mesh.polygons)
        o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
        outer = (xs[-1] - xs[0], ys[-1] - ys[0], zs[-1] - zs[0])
        text = "外形 %s" % k.triple(outer, " mm")
        if len(xs) >= 4 and len(ys) >= 4 and len(zs) >= 3:
            text += "、內腔 %s × %s mm、底厚 %s mm" % (k.num(xs[-2] - xs[1]), k.num(ys[-2] - ys[1]), k.num(zs[1] - zs[0]))
        return text + "、%d 個面" % faces

    def non_manifold_edges():
        o = cube()
        if o.mode == "EDIT":
            bm = bmesh.from_edit_mesh(o.data)
            return sum(1 for e in bm.edges if not e.is_manifold), sum(1 for e in bm.edges if e.select)
        bm = bmesh.new()
        bm.from_mesh(o.data)
        count = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        return count, 0

    def stl_size(path):
        with open(path, "rb") as handle:
            data = handle.read()
        count = struct.unpack("<I", data[80:84])[0]
        lo, hi = [1e9] * 3, [-1e9] * 3
        for i in range(count):
            base = 84 + i * 50 + 12
            for v in range(3):
                point = struct.unpack("<fff", data[base + v * 12: base + v * 12 + 12])
                lo = [min(a, b) for a, b in zip(lo, point)]
                hi = [max(a, b) for a, b in zip(hi, point)]
        return [h - l for l, h in zip(lo, hi)], count

    def top_face_point():
        view = k.area("VIEW_3D")
        region = next(r for r in view.regions if r.type == "WINDOW")
        p = location_3d_to_region_2d(region, view.spaces.active.region_3d, Vector((0, 0, 15)))
        return region.x + p.x, k.window().height - (region.y + p.y)

    def top_face_box(label):
        def build_box():
            x, y = top_face_point()
            return B(x - 40, y - 25, 80, 50, label)
        return build_box

    k.setup()

    # ===== 04-02 建立毫米工作檔 =====
    do(lambda: click(40, 13), 0.6)
    do(lambda: move(67, 36), 0.8)
    k.menu_item(285, 35, 2.0)
    do(lambda: click(1245, 374), 0.8)
    do(lambda: click(1302, 433), 0.8)
    record("04-02", "units-before", "File > New > General，開 Properties 的 Scene 分頁並展開 Units：目前是 Meters、Unit Scale 1",
           lambda: "場景物件：%s；%s。" % ("、".join(o.name for o in bpy.data.objects), units()),
           highlights=[B(1236, 364, 20, 20, "Scene 分頁"), B(1266, 477, 216, 22, "Unit Scale"),
                       B(1266, 547, 216, 20, "Length")], park=PARK)
    do(lambda: click(1418, 557), 1.0)
    k.menu_item(1397, 668)
    k.type_into(1417, 488, "0.001")
    k.open_sidebar()
    record("04-02", "units-mm", "Length 選 Millimeters，Unit Scale 輸入 0.001，再用 View > Sidebar 打開側欄：Cube 顯示 2 mm",
           lambda: "%s；%s。" % (units(), size()),
           highlights=[B(1266, 477, 216, 22, "Unit Scale 0.001"), B(1266, 547, 216, 20, "Length：Millimeters"),
                       B(963, 383, 228, 77, "Dimensions 2 mm")], park=PARK,
           note="Unit Scale 0.001 表示 1 個 Blender 單位 = 1 mm。實測：這樣匯出的 STL 數值才是 mm；第二單元的 Unit Scale 1 匯出後會小 1000 倍。")
    k.show_learner_save("04-02", "save-as-v001", "04", "u04_box_v001.blend",
                        "File > Save As…：資料夾換成自己的單元 04 練習資料夾，檔名 u04_box_v001.blend")

    # ===== 04-03 外形與 Apply Scale =====
    for field_y, value in ((411, "60mm"), (430, "40mm"), (450, "30mm")):
        k.type_into(1075, field_y, value)
    record("04-03", "dimensions", "Sidebar 的 Dimensions 依序輸入 60mm、40mm、30mm：Scale 跟著變成 30、20、15",
           lambda: size() + "。",
           highlights=[B(963, 383, 228, 77, "Dimensions 60 × 40 × 30 mm"), B(963, 318, 176, 59, "Scale 30、20、15")],
           park=PARK)
    do(lambda: click(313, 38), 0.8)
    do(lambda: move(336, 141), 0.8)
    do(lambda: move(533, 180), 0.6)
    record("04-03", "apply-menu", "3D Viewport 的 Object > Apply，指到 Scale",
           lambda: "Object 與 Apply 子選單展開；" + size() + "。",
           highlights=[B(289, 28, 48, 20, "Object"), B(292, 131, 192, 20, "Apply"), B(492, 170, 220, 20, "Scale")],
           clicks=[{"x": 313, "y": 38}])
    k.menu_item(533, 180, 1.0)
    record("04-03", "applied", "點 Scale：Scale 回到 1，Dimensions 不變",
           lambda: size() + "。",
           highlights=[B(963, 318, 176, 59, "Scale 1、1、1"), B(963, 383, 228, 77, "Dimensions 不變")], park=PARK)

    # ===== 04-04 打開頂面 =====
    do(lambda: click(184, 38), 0.6)
    k.menu_item(236, 168, 1.5)
    k.wheel_out(3)
    do(lambda: key("TAB", x=700, y=600), 1.0)
    do(lambda: key("THREE", x=700, y=600), 0.8)
    record("04-04", "edit-face", "View > Frame Selected 再把滾輪往後滾 3 格；滑鼠在 3D Viewport 內按 Tab 進 Edit Mode、按 3 切換面選取",
           lambda: "模式：%s；面選取：%s；目前選取 %d 個面。" % (
               bpy.context.mode, "是" if tuple(bpy.context.tool_settings.mesh_select_mode)[2] else "否",
               cube().data.total_face_sel),
           highlights=[B(49, 28, 96, 20, "Edit Mode"), B(191, 29, 20, 19, "面選取")], park=PARK)
    do(lambda: click(280, 38), 0.6)
    k.menu_item(303, 81, 0.8)
    do(lambda: click(*top_face_point()), 0.8)
    record("04-04", "top-selected", "Select > None 取消全選，再點盒子頂面",
           lambda: "選取 %d 個面；Sidebar 的 Median Z 是頂面高度。" % cube().data.total_face_sel,
           highlights=k.boxes(top_face_box("頂面"), B(963, 172, 226, 20, "Median Z = 15 mm")), park=PARK)
    do(lambda: click(362, 38), 0.6)
    do(lambda: move(390, 530), 0.8)
    do(lambda: move(574, 573), 0.6)
    record("04-04", "delete-menu", "開 Mesh 選單 > Delete，指到 Faces",
           lambda: "Mesh 與 Delete 子選單展開。",
           highlights=[B(343, 28, 38, 20, "Mesh"), B(344, 520, 180, 20, "Delete"), B(528, 563, 182, 20, "Faces")],
           clicks=[{"x": 362, "y": 38}])
    k.menu_item(574, 573, 1.0)
    record("04-04", "opened", "點 Faces：頂面刪除，盒子上方打開（還沒有厚度）",
           lambda: "網格剩 %d 個面；不封閉的邊 %d 條（開口邊緣，加厚度後會封閉）。" % (
               len(cube().data.polygons) if cube().mode != "EDIT" else len(bmesh.from_edit_mesh(cube().data).faces),
               non_manifold_edges()[0]),
           highlights=k.boxes(top_face_box("開口")), park=PARK)

    # ===== 04-05 加上壁厚 =====
    do(lambda: key("TAB", x=700, y=600), 1.0)
    do(lambda: click(1245, 503), 0.8)
    do(lambda: click(1383, 287), 1.0)
    do(lambda: move(1300, 333), 0.8)
    do(lambda: move(1112, 632), 0.6)
    record("04-05", "add-solidify", "按 Tab 回 Object Mode；Properties 的 Modifier 分頁 > Add Modifier > Generate，指到 Solidify",
           lambda: "模式：%s；Add Modifier 與 Generate 子選單展開。" % bpy.context.mode,
           highlights=[B(1242, 323, 172, 20, "Generate"), B(1064, 622, 172, 20, "Solidify")],
           clicks=[{"x": 1383, "y": 287}])
    k.menu_item(1112, 632, 1.0)
    record("04-05", "solidify-default", "點 Solidify：預設 Thickness 只有 0.01 mm，幾乎看不出厚度",
           lambda: "Solidify Thickness %s mm、Offset %s；%s。" % (
               k.num(cube().modifiers["Solidify"].thickness), k.num(cube().modifiers["Solidify"].offset), shell()),
           highlights=[B(1352, 365, 103, 20, "Thickness"), B(1352, 390, 103, 20, "Offset −1")], park=PARK)
    do(lambda: click(1403, 375), 0.5)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text(DEMO_WALL), 0.3)
    do(lambda: key("RET"), 0.8)
    do(lambda: click(1358, 425), 1.0)
    record("04-05", "solidify-wall", "Thickness 輸入 2mm（示範值）並勾 Even Thickness：外形不變，厚度往內長",
           lambda: "Solidify Thickness %s mm、Offset %s、Even Thickness %s；%s。" % (
               k.num(cube().modifiers["Solidify"].thickness), k.num(cube().modifiers["Solidify"].offset),
               "開" if cube().modifiers["Solidify"].use_even_offset else "關", shell()),
           highlights=[B(1352, 365, 103, 20, "Thickness 2 mm"), B(1352, 415, 103, 20, "Even Thickness")], park=PARK,
           note="2 mm 只是示範值。你的壁厚待定：等噴嘴與線寬確定後，取線寬的整數倍。")

    # ===== 04-06 檢查可列印網格 =====
    do(lambda: click(1424, 320), 1.0)
    record("04-06", "apply-menu", "Solidify 標題列的下拉選單，找到 Apply",
           lambda: "修改器：%s。" % "、".join(m.name for m in cube().modifiers),
           highlights=[B(1416, 311, 18, 18, "下拉選單"), B(1287, 333, 145, 20, "Apply")], clicks=[{"x": 1424, "y": 320}])
    k.menu_item(1331, 343, 1.0)
    record("04-06", "applied", "點 Apply：厚度寫進網格，Modifier 清單變空",
           lambda: "修改器：%s；%s。" % ("、".join(m.name for m in cube().modifiers) or "無", shell()),
           highlights=[B(1266, 277, 216, 20, "Modifier 清單空了")], park=PARK)
    do(lambda: key("TAB", x=700, y=600), 1.0)
    do(lambda: key("TWO", x=700, y=600), 0.8)
    do(lambda: click(280, 38), 0.6)
    k.menu_item(303, 81, 0.6)
    do(lambda: click(280, 38), 0.6)
    do(lambda: move(335, 309), 0.8)
    do(lambda: move(540, 308), 0.6)
    record("04-06", "trait-menu", "按 Tab 進 Edit Mode、按 2 切換邊選取、Select > None；再開 Select > Select All by Trait，指到 Non Manifold",
           lambda: "模式：%s；邊選取：%s。" % (bpy.context.mode, "是" if tuple(bpy.context.tool_settings.mesh_select_mode)[1] else "否"),
           highlights=[B(171, 29, 20, 19, "邊選取"), B(260, 299, 208, 20, "Select All by Trait"),
                       B(476, 298, 208, 20, "Non Manifold")], clicks=[{"x": 280, "y": 38}],
           note="面選取模式下這個子選單沒有 Non Manifold（實測），一定要先切到邊選取或頂點選取。")
    k.menu_item(540, 308, 1.0)
    record("04-06", "non-manifold", "點 Non Manifold：沒有選到任何邊，網格是封閉的",
           lambda: "不封閉的邊 %d 條；目前選到 %d 條邊。" % non_manifold_edges(),
           highlights=[B(955, 82, 242, 52, "Nothing selected")], park=PARK)
    do(lambda: key("TAB", x=700, y=600), 1.0)
    do(lambda: click(40, 13), 0.6)
    k.menu_item(68, 143, 1.5)

    # ===== 04-07 匯出 STL =====
    do(lambda: click(40, 13), 0.6)
    do(lambda: move(73, 317), 0.8)
    do(lambda: move(288, 436), 0.6)
    record("04-07", "export-menu", "按 Tab 回 Object Mode、File > Save 存檔後，開 File > Export，指到 STL (.stl)",
           lambda: "已存檔：%s；File 與 Export 子選單展開。" % os.path.basename(bpy.data.filepath),
           highlights=[B(30, 3, 27, 21, "File"), B(28, 307, 202, 20, "Export"), B(236, 426, 244, 20, "STL (.stl)")],
           clicks=[{"x": 40, "y": 13}])
    learner_exports = k.learner_dir("04") + "exports\\"
    k.menu_item(288, 436, 1.5)
    k.fill_dialog(learner_exports, "u04_box_v001.stl")
    record("04-07", "export-dialog", "點 STL (.stl)：資料夾換成單元 04 的 exports，檔名 u04_box_v001.stl；確認 Scale 1、Scene Unit 不勾",
           lambda: "資料夾欄位：%s；檔名欄位：%s；該資料夾目前內容：%s。" % (k.browser() + (k.listing(learner_exports),)),
           win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("path", "exports 資料夾"), k.fb_box("name", "檔名"),
                               B(922, 171, 130, 20, "Scale 1.000"), B(922, 193, 110, 20, "Scene Unit 不勾"),
                               k.fb_box("confirm", "你要按 Export STL")],
           note="這張是你要看到的畫面；路徑與檔名由助教以程式填入欄位。助教示範到此按 Esc 取消，不寫入你的工作區，再把 STL 存到助教示範資料夾。")
    k.cancel_dialog()
    do(lambda: click(40, 13), 0.6)
    do(lambda: move(73, 317), 0.8)
    k.menu_item(288, 436, 1.5)
    k.fill_dialog(k.demo_dir, "u04_box_v001.stl")
    k.confirm_dialog(2.0)

    def exported():
        path = k.demo_dir + "u04_box_v001.stl"
        dims, triangles = stl_size(path)
        return "STL：u04_box_v001.stl（%d bytes、%d 個三角形）；檔案內的尺寸 %s（切片軟體以 mm 讀取）。" % (
            os.path.getsize(path), triangles, k.triple(dims, ""))
    record("04-07", "stl-checked", "按 Export STL 後，讀 STL 檔案本身的尺寸核對",
           exported, highlights=[B(0, 997, 1494, 22, "狀態列")], park=PARK,
           note="STL 尺寸由助教直接解析檔案讀出。匯入切片軟體核對（切片軟體待定）要由你做，和這裡的檔案檢查分開記錄。")
