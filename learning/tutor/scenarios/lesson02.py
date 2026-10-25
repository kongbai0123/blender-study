"""第二單元 02-01～02-07：訊號站建模與毫米尺寸方塊的助教實際操作示範。

尺寸依 sources/secourses/week01-observed-facts-2026-10-22.json 與 catalog（公尺尺度）；
毫米方塊 40 × 30 × 10 mm 為本專案自編補充。示範檔只存到本次輸出資料夾的 demo-files。
"""
import os

import bpy

from common import PARK, Kit

PARTS = ("Ground", "Platform", "BeaconBase", "Post", "Signal")


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box

    def names():
        return "、".join(o.name for o in sorted(bpy.data.objects, key=lambda o: o.name.lower()))

    def stack(name):
        bottom, top = k.bottom_top(name)
        return "%s；底面 Z %s m、頂面 Z %s m" % (k.size(name), k.num(bottom), k.num(top))

    k.setup()

    # ===== 02-01 準備訊號站工作檔 =====
    record("02-01", "start", "從 General 預設場景開始，先核對畫面與物件",
           lambda: "場景物件：%s；%s；檔案：%s。" % (names(), k.selection(), bpy.data.filepath or "未存檔"),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Outliner：Camera／Cube／Light"),
                              k.obj_box("Cube", "預設 Cube（不需要）")), park=PARK)
    k.click_outliner("Cube")
    do(lambda: click(313, 38), 0.8)
    record("02-01", "object-delete", "在 Outliner 點 Cube，再開 3D Viewport 的 Object 選單，找到 Delete",
           lambda: k.selection() + "；Object 選單展開。",
           highlights=[B(1286, 114, 140, 20, "Outliner：Cube"), B(289, 28, 48, 20, "Object"),
                       B(296, 701, 188, 20, "Delete")],
           clicks=[{"x": 1340, "y": 124}, {"x": 313, "y": 38}])
    k.menu_item(337, 711)
    record("02-01", "deleted", "點 Delete：只刪除預設 Cube，Camera 與 Light 留給第三單元",
           lambda: "場景物件：%s。" % names(),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Outliner：剩 Camera、Light")), park=PARK)
    k.show_learner_save("02-01", "save-as-v001", "02", "u02_station_v001.blend",
                        "File > Save As…：資料夾換成自己的單元 02 練習資料夾，檔名 u02_station_v001.blend")
    record("02-01", "saved", "存檔後底部出現 Saved（示範檔在助教資料夾）",
           lambda: "目前檔案：%s（%d bytes）；你的單元 02 工作區：%s。" % (
               bpy.data.filepath, os.path.getsize(bpy.data.filepath), k.listing(k.learner_dir("02"))),
           highlights=[B(0, 997, 1494, 22, "狀態列：Saved")], park=PARK)

    # ===== 02-02 地面與平台 =====
    do(lambda: click(270, 38), 0.6)
    do(lambda: move(298, 61), 0.8)
    do(lambda: move(468, 60), 0.6)
    record("02-02", "add-mesh-plane", "3D Viewport 的 Add > Mesh，指到 Plane",
           lambda: "Add 選單與 Mesh 子選單展開。",
           highlights=[B(255, 28, 32, 20, "Add"), B(255, 51, 164, 20, "Mesh"), B(426, 50, 162, 20, "Plane")],
           clicks=[{"x": 270, "y": 38}])
    k.menu_item(468, 60)
    k.open_sidebar()
    record("02-02", "plane-added", "點 Plane 新增地面，並用 View > Sidebar 打開側欄",
           lambda: k.size("Plane") + "。",
           highlights=k.boxes(k.obj_box("Plane", "新增的 Plane"), B(955, 82, 242, 382, "Sidebar：Item")), park=PARK)
    k.type_into(1075, 411, "4")
    record("02-02", "plane-x", "Dimensions X 輸入 4 後按 Enter",
           lambda: k.size("Plane") + "。",
           highlights=k.boxes(B(963, 401, 228, 20, "Dimensions X = 4 m"), k.obj_box("Plane", "Plane")), park=PARK)
    k.type_into(1075, 430, "4")
    record("02-02", "plane-y", "Dimensions Y 輸入 4 後按 Enter：地面 4 m × 4 m",
           lambda: k.size("Plane") + "。",
           highlights=k.boxes(B(963, 420, 228, 20, "Dimensions Y = 4 m"), B(963, 172, 176, 20, "Location Z = 0 m"),
                              k.obj_box("Plane", "地面 4 × 4 m")), park=PARK)
    k.add_mesh(80)
    record("02-02", "platform-added", "Add > Mesh > Cube 新增平台（先是 2 m 方塊）",
           lambda: k.size("Cube") + "。",
           highlights=k.boxes(k.obj_box("Cube", "新增的 Cube"), B(963, 383, 228, 77, "Dimensions")), park=PARK)
    for field_y, value in ((411, "2.4"), (430, "2.4"), (450, "0.2")):
        k.type_into(1075, field_y, value)
    record("02-02", "platform-size", "Dimensions 依序輸入 X 2.4、Y 2.4、Z 0.2（一次一欄）",
           lambda: k.size("Cube") + "。",
           highlights=k.boxes(B(963, 383, 228, 77, "Dimensions 2.4 × 2.4 × 0.2 m"), k.obj_box("Cube", "平台")),
           park=PARK)
    k.type_into(1050, 182, "0.1")
    record("02-02", "platform-z", "Location Z 輸入 0.1：平台底面剛好在 Z = 0",
           lambda: stack("Cube") + "。",
           highlights=k.boxes(B(963, 172, 176, 20, "Location Z = 0.1 m"), k.obj_box("Cube", "平台")), park=PARK)

    # ===== 02-03 基座、立柱、訊號球 =====
    def part(mesh_y, name, dims, z):
        k.add_mesh(mesh_y)
        for field_y, value in zip((411, 430, 450), dims):
            k.type_into(1075, field_y, value)
        k.type_into(1050, 182, z)

    part(80, "Cube.001", ("0.7", "0.7", "0.3"), "0.35")
    record("02-03", "base", "Add > Mesh > Cube 新增基座：Dimensions 0.7、0.7、0.3，Location Z 0.35",
           lambda: stack("Cube.001") + "；平台頂面 Z %s m。" % k.num(k.bottom_top("Cube")[1]),
           highlights=k.boxes(B(963, 383, 228, 77, "Dimensions"), B(963, 172, 176, 20, "Location Z"),
                              k.obj_box("Cube.001", "基座")), park=PARK,
           note="用 Dimensions 改尺寸時，Blender 實際改的是 Scale（此處變成 0.35、0.35、0.15），狀態列會提醒 non-uniform scale。"
                "這在訊號站練習沒有問題；之後做卡扣、螺紋與公差時，會先確認何時要 Apply Scale，避免尺寸與厚度計算出錯。")
    part(80, "Cube.002", ("0.12", "0.12", "1.2"), "1.1")
    record("02-03", "post", "同樣步驟新增立柱：Dimensions 0.12、0.12、1.2，Location Z 1.1",
           lambda: stack("Cube.002") + "；基座頂面 Z %s m。" % k.num(k.bottom_top("Cube.001")[1]),
           highlights=k.boxes(B(963, 383, 228, 77, "Dimensions"), k.obj_box("Cube.002", "立柱")), park=PARK)
    part(120, "Sphere", ("0.5", "0.5", "0.5"), "1.95")
    record("02-03", "signal", "Add > Mesh > UV Sphere 新增訊號球：直徑 0.5，Location Z 1.95",
           lambda: stack("Sphere") + "；立柱頂面 Z %s m；場景物件：%s。" % (k.num(k.bottom_top("Cube.002")[1]), names()),
           highlights=k.boxes(B(963, 383, 228, 77, "Dimensions 0.5 m"), k.obj_box("Sphere", "訊號球")), park=PARK)

    # ===== 02-04 命名與 Collection =====
    do(lambda: k.drag_slow([(1360, 206), (1360, 260), (1360, 320), (1360, 380)]), 0.2)
    record("02-04", "outliner-taller", "往下拖曳 Outliner 與 Properties 之間的邊界，讓物件清單完整可見",
           lambda: "Outliner 列出：%s。" % "、".join(n for _, n in k.outliner_names()),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Outliner 變高")), clicks=[{"x": 1360, "y": 206}],
           park=PARK)
    k.click_outliner("Cube.001")
    do(lambda: click(75, 13), 0.6)
    do(lambda: move(147, 197), 0.6)
    record("02-04", "rename-menu", "在 Outliner 點基座（Cube.001），開 Edit 選單找到 Rename Active Item",
           lambda: k.selection() + "；Edit 選單展開。",
           highlights=k.boxes(k.outliner_box("Cube.001", "Cube.001"), B(65, 3, 22, 21, "Edit"),
                              B(64, 187, 198, 20, "Rename Active Item")))
    k.menu_item(147, 197)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text("BeaconBase"), 0.6)
    record("02-04", "rename-popup", "名稱欄位已在編輯狀態：輸入 BeaconBase",
           lambda: "改名前：%s。" % k.selection(), highlights=[B(10, 155, 300, 60, "Object Name")])
    do(lambda: key("RET"), 0.8)
    record("02-04", "renamed", "按 Enter：Outliner 與 3D Viewport 都是同一件基座",
           lambda: k.selection() + "。",
           highlights=k.boxes(k.outliner_box("BeaconBase", "BeaconBase"), k.obj_box("BeaconBase", "基座")), park=PARK)
    for old, new in (("Cube", "Platform"), ("Plane", "Ground"), ("Cube.002", "Post"), ("Sphere", "Signal")):
        k.click_outliner(old)
        k.rename_active(new)
    record("02-04", "all-renamed", "同樣方法把其他部件改名：Platform、Ground、Post、Signal",
           lambda: "Outliner 列出：%s。" % "、".join(n for _, n in k.outliner_names()),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "名稱可辨認")), park=PARK)
    for index, name in enumerate(PARTS):
        k.click_outliner(name, ctrl=index > 0)
    do(lambda: key("M", x=700, y=600), 1.0)
    record("02-04", "move-to-collection", "Outliner 點 Ground，再 Ctrl+點其餘部件；滑鼠在 3D Viewport 內按 M",
           lambda: k.selection() + "；Move to Collection 選單展開。",
           highlights=k.boxes(lambda: k.rect("OUTLINER", "五個部件已選取"), B(556, 616, 176, 20, "New Collection")))
    k.menu_item(626, 626, 1.2)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text("Station"), 0.6)
    record("02-04", "new-collection-name", "點 New Collection：命名視窗的 Name 欄位已在編輯狀態，輸入 Station",
           lambda: k.selection() + "；命名視窗開啟。",
           highlights=[B(630, 624, 116, 22, "Name：Station"), B(546, 655, 96, 20, "Create")])
    do(lambda: key("RET"), 0.6)
    do(lambda: key("RET"), 1.0)
    record("02-04", "station", "輸入 Station 並確認：五個部件移到 Station Collection",
           lambda: "Collections：%s。" % "；".join(
               "%s：%s" % (c.name, "、".join(o.name for o in c.objects)) for c in bpy.context.scene.collection.children),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Station Collection")), park=PARK)
    k.show_learner_save("02-04", "save-as-v002", "02", "u02_station_v002.blend",
                        "File > Save As…：另存 u02_station_v002.blend（v001 保留不動）")
    record("02-04", "saved-v002", "存檔後底部出現 Saved（示範檔在助教資料夾）",
           lambda: "目前檔案：%s（%d bytes）。" % (bpy.data.filepath, os.path.getsize(bpy.data.filepath)),
           highlights=[B(0, 997, 1494, 22, "狀態列：Saved")], park=PARK)

    # ===== 02-05 另開毫米尺寸方塊 =====
    do(lambda: click(40, 13), 0.6)
    do(lambda: move(67, 36), 0.8)
    k.menu_item(285, 35, 2.0)
    record("02-05", "new-general", "File > New > General：開新的預設場景（訊號站已存檔）",
           lambda: "場景物件：%s；檔案：%s。" % (names(), bpy.data.filepath or "未存檔"),
           highlights=k.boxes(k.obj_box("Cube", "預設 Cube")), park=PARK)
    k.show_learner_save("02-05", "save-as-mm", "02", "u02_mm_block_v001.blend",
                        "File > Save As…：另存 u02_mm_block_v001.blend（和訊號站分開）")
    do(lambda: click(1245, 374), 0.8)
    do(lambda: click(1302, 433), 0.8)
    record("02-05", "units", "Properties 的 Scene 分頁，展開 Units：Unit System Metric、Unit Scale 1.000000",
           lambda: "Unit System %s、Unit Scale %s、Length %s。" % (
               bpy.context.scene.unit_settings.system, k.num(bpy.context.scene.unit_settings.scale_length),
               bpy.context.scene.unit_settings.length_unit),
           highlights=[B(1236, 364, 20, 20, "Scene 分頁"), B(1266, 452, 216, 47, "Unit System／Unit Scale"),
                       B(1266, 547, 216, 20, "Length")], clicks=[{"x": 1245, "y": 374}], park=PARK)
    do(lambda: click(1418, 557), 1.0)
    record("02-05", "length-list", "點 Length 下拉選單，找到 Millimeters",
           lambda: "Length 清單展開。", highlights=[B(1361, 658, 112, 20, "Millimeters")],
           clicks=[{"x": 1418, "y": 557}])
    k.menu_item(1397, 668)
    k.open_sidebar()
    record("02-05", "millimeters", "選 Millimeters 並打開 Sidebar：同一個 Cube 顯示為 2000 mm，物件沒有變小",
           lambda: "Length %s、Unit Scale %s；%s。" % (
               bpy.context.scene.unit_settings.length_unit, k.num(bpy.context.scene.unit_settings.scale_length),
               k.size("Cube", " mm", 1000)),
           highlights=k.boxes(B(1266, 547, 216, 20, "Length：Millimeters"), B(1266, 477, 216, 22, "Unit Scale 1"),
                              B(963, 383, 228, 77, "Dimensions 2000 mm")), park=PARK)

    # ===== 02-06 輸入毫米尺寸 =====
    k.type_into(1075, 411, "40mm")
    record("02-06", "x-40", "Dimensions X 輸入 40mm 後按 Enter（只改 X）",
           lambda: k.size("Cube", " mm", 1000) + "。",
           highlights=[B(963, 401, 228, 20, "X = 40 mm")], park=PARK)
    k.type_into(1075, 430, "30mm")
    k.type_into(1075, 450, "10mm")
    record("02-06", "yz", "再分兩次輸入 Y 30mm、Z 10mm",
           lambda: k.size("Cube", " mm", 1000) + "。",
           highlights=[B(963, 383, 228, 77, "40 × 30 × 10 mm"), B(963, 300, 228, 77, "Scale")], park=PARK)
    do(lambda: click(184, 38), 0.6)
    k.menu_item(236, 168, 1.5)
    k.wheel_out(4)
    record("02-06", "framed", "方塊很小：View > Frame Selected 拉近，再把滾輪往後滾 4 格看清整個方塊",
           lambda: k.size("Cube", " mm", 1000) + "；視角距離 %s m。" % k.num(k.view3d().region_3d.view_distance),
           highlights=k.boxes(k.obj_box("Cube", "40 × 30 × 10 mm 方塊"), B(963, 383, 228, 77, "Dimensions")),
           park=PARK)

    # ===== 02-07 保存兩份檔案並各自重新開啟 =====
    do(lambda: click(40, 13), 0.6)
    k.menu_item(68, 143, 1.5)
    record("02-07", "mm-saved", "File > Save：保存毫米方塊",
           lambda: "已存檔：%s（%d bytes）；%s。" % (
               os.path.basename(bpy.data.filepath), os.path.getsize(bpy.data.filepath), k.size("Cube", " mm", 1000)),
           highlights=[B(0, 997, 1494, 22, "狀態列：Saved")], park=PARK)
    k.file_dialog(56, k.demo_dir, "u02_station_v002.blend")
    record("02-07", "open-station", "File > Open…：選 u02_station_v002.blend",
           lambda: "開啟視窗資料夾內容：%s。" % k.listing(k.demo_dir), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("name", "檔名"), k.fb_box("confirm", "按 Open")],
           note="此為助教示範資料夾；你要開的是自己單元 02 練習資料夾中已登記的檔案。")
    k.confirm_dialog(2.5)
    record("02-07", "station-reopened", "重新開啟訊號站：部件、Collection 與尺寸都在",
           lambda: "目前檔案：%s；Collections：%s；平台 %s。" % (
               os.path.basename(bpy.data.filepath),
               "；".join("%s：%s" % (c.name, "、".join(o.name for o in c.objects))
                        for c in bpy.context.scene.collection.children), k.size("Platform")),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Station Collection")), park=PARK)
    k.file_dialog(56, k.demo_dir, "u02_mm_block_v001.blend")
    k.confirm_dialog(2.5)
    record("02-07", "mm-reopened", "再用 File > Open… 開 u02_mm_block_v001.blend：尺寸仍是 40 × 30 × 10 mm",
           lambda: "目前檔案：%s；Length %s；%s。" % (
               os.path.basename(bpy.data.filepath), bpy.context.scene.unit_settings.length_unit,
               k.size("Cube", " mm", 1000)),
           highlights=k.boxes(B(963, 383, 228, 77, "40 × 30 × 10 mm")), park=PARK)
