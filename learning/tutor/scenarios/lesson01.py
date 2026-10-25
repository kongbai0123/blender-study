"""第一單元 01-03～01-09：助教在獨立 Blender 中實際操作，逐步截圖並讀回狀態。

座標取自同版本（5.2.1 LTS、1494×1019、English (US)）的實際截圖；Cube 的標示框由
物件邊界實際投影到畫面計算。Save As 對話框會顯示學員工作區路徑供對照，但示範一律按 Esc
取消，不寫入學員工作區；需要真的存檔時，存到本次輸出資料夾的 demo-files。
"""
import os
from pathlib import Path

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[3]
LEARNER_DIR = str(PROJECT / "learning" / "workspaces" / "01") + "\\"
PARK = (700, 800)  # 3D Viewport 空白處：截圖前把游標移到這裡，避免按鈕提示遮住畫面。


def build(g):
    do, click, key, type_text, move = g["do"], g["click"], g["key"], g["type_text"], g["move"]
    drag_slow, record, window, area, event = g["drag_slow"], g["record"], g["window"], g["area"], g["_event"]
    demo_dir = os.path.join(g["OUT"], "demo-files") + "\\"
    os.makedirs(demo_dir, exist_ok=True)
    learner_before = sorted(os.listdir(LEARNER_DIR))
    memo = {}

    # ---- 讀回實際狀態 ----
    def cube():
        return bpy.data.objects["Cube"]

    def num(value):
        return "%g" % round(value, 4)

    def triple(values, unit=" m"):
        return "(" + ", ".join(num(v) + unit for v in values) + ")"

    def selection():
        names = [o.name for o in bpy.context.selected_objects]
        active = bpy.context.view_layer.objects.active
        return "已選取：%s；作用中物件：%s；模式：%s" % (
            "、".join(names) or "無", active.name if active else "無", bpy.context.mode)

    def transform():
        c = cube()
        return "Cube Location %s、Rotation %s、Scale %s、Dimensions %s" % (
            triple(c.location), triple([v * 57.29578 for v in c.rotation_euler], "°"),
            triple(c.scale, ""), triple(c.dimensions))

    def view3d():
        return area("VIEW_3D").spaces.active.region_3d

    def view_state():
        rv = view3d()
        return "視角距離 %s m、視角中心 %s" % (num(rv.view_distance), triple(rv.view_location))

    def browser():
        params = window("FILE_BROWSER").screen.areas[0].spaces.active.params
        directory = params.directory.decode() if isinstance(params.directory, bytes) else params.directory
        return directory, params.filename

    def listing(path):
        return "、".join(sorted(os.listdir(path))) or "（空資料夾）"

    def guard():
        # 示範絕不能寫入學員工作區；一有變化就中止整個劇本。
        if sorted(os.listdir(LEARNER_DIR)) != learner_before:
            raise RuntimeError("學員工作區內容改變，已中止示範：%s" % os.listdir(LEARNER_DIR))

    # ---- 標示框（圖片座標，左上為原點） ----
    def box(x, y, w, h, label):
        return {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "label": label}

    def rect(kind, label):
        a = area(kind)
        return box(a.x, window().height - (a.y + a.height), a.width, a.height, label)

    def object_box(label, name="Cube", pad=8):
        """把物件的 8 個邊界角投影到 3D Viewport，取外接框；不在畫面內時回傳 None。"""
        view = area("VIEW_3D")
        region = next(r for r in view.regions if r.type == "WINDOW")
        obj = bpy.data.objects[name]
        points = [location_3d_to_region_2d(region, view.spaces.active.region_3d, obj.matrix_world @ Vector(c))
                  for c in obj.bound_box]
        points = [p for p in points if p is not None]
        if not points:
            return None
        height = window().height
        left, right = region.x, region.x + region.width
        top, bottom = height - (region.y + region.height), height - region.y
        x0 = max(min(region.x + p.x for p in points) - pad, left)
        x1 = min(max(region.x + p.x for p in points) + pad, right)
        y0 = max(min(height - (region.y + p.y) for p in points) - pad, top)
        y1 = min(max(height - (region.y + p.y) for p in points) + pad, bottom)
        if x0 >= x1 or y0 >= y1:
            return None
        return box(x0, y0, x1 - x0, y1 - y0, label)

    def boxes(*items):
        # 截圖當下才計算（物件位置會隨操作改變）；不在畫面內的標示略過。
        def collect():
            values = (item() if callable(item) else item for item in items)
            return [value for value in values if value]
        return collect

    def cube_box(label):
        return lambda: object_box(label)

    def fb_box(kind, label):
        w = window("FILE_BROWSER")
        spots = {"path": (394, 8, w.width - 742, 25), "name": (248, w.height - 34, w.width - 280, 25),
                 "confirm": (w.width - 271, w.height - 34, 126, 25)}
        return box(*spots[kind], label)

    # ---- 檔案對話框：選單用真實點擊，欄位用 Blender 資料寫入 ----
    def file_dialog(menu_y, directory, filename):
        do(lambda: click(40, 13))
        do(lambda: click(81, menu_y), 1.5)

        def fill():
            # 檔案瀏覽器中的按鍵是快捷鍵（例如 I 會新增資料夾）；若模擬打字沒進入編輯狀態
            # 就可能寫入磁碟，所以資料夾與檔名改由 Blender 資料寫入欄位。
            w = window("FILE_BROWSER")
            file_area = w.screen.areas[0]
            params = file_area.spaces.active.params
            params.directory = directory.encode() if isinstance(params.directory, bytes) else directory
            params.filename = filename
            with bpy.context.temp_override(window=w, area=file_area):
                bpy.ops.file.refresh()
            file_area.tag_redraw()
            guard()
        do(fill, 1.2)

    def cancel_dialog():
        do(lambda: key("ESC", win="FILE_BROWSER"), 1.0)
        do(guard, 0.2)

    def confirm_dialog(wait=1.5):
        def press():
            w = window("FILE_BROWSER")
            click(w.width - 209, w.height - 21, win="FILE_BROWSER")
        do(press, wait)
        do(guard, 0.2)

    def type_into(x, y, text):
        do(lambda: click(x, y), 0.5)
        do(lambda: key("A", ctrl=True), 0.3)
        do(lambda: type_text(text), 0.3)
        do(lambda: key("RET"), 1.0)

    def wheel_out(notches, x, y):
        # 模擬事件不經過系統的滾輪轉換；實測 WHEELDOWNMOUSE 才是縮小（每格約 ×1.2 距離）。
        def roll():
            move(x, y)
            for _ in range(notches):
                event(window(), "WHEELDOWNMOUSE", "PRESS", x, y)
        do(roll, 1.0)

    def setup():
        prefs = bpy.context.preferences
        prefs.view.language = "en_US"
        prefs.filepaths.use_auto_save_temporary_files = False
        key("ESC")

    do(setup, 1.5)

    # ===== 01-03 準備預設場景：只辨認，不新建 =====
    record("01-03", "default-scene", "開啟後先核對畫面：這是預設場景，不新建也不關閉",
           lambda: "場景物件：%s；%s；檔案：%s" % (
               "、".join(o.name for o in bpy.data.objects), selection(), bpy.data.filepath or "未存檔"),
           highlights=boxes(cube_box("1 Cube（3D Viewport）"), lambda: rect("OUTLINER", "2 Outliner：Camera／Cube／Light"),
                            lambda: rect("PROPERTIES", "3 Properties")), park=PARK)
    do(lambda: click(40, 13))
    do(lambda: move(67, 36), 1.0)
    record("01-03", "file-new-general", "畫面不是預設場景時才用：File > New > General（本示範沒有點選）",
           lambda: "File 選單與 New 子選單展開；場景仍是 %s，未新建。" % "、".join(o.name for o in bpy.data.objects),
           highlights=[box(30, 3, 27, 21, "File"), box(28, 26, 202, 20, "New"), box(240, 26, 200, 20, "General")],
           clicks=[{"x": 40, "y": 13}])
    do(lambda: key("ESC"))
    do(lambda: key("ESC"))

    # ===== 01-04 第一次另存檔 v001：顯示學員路徑後取消 =====
    do(lambda: click(40, 13))
    record("01-04", "file-menu", "點左上 File，找到 Save As…",
           lambda: "File 選單展開；目前檔案：%s。" % (bpy.data.filepath or "未存檔"),
           highlights=[box(30, 3, 27, 21, "File"), box(28, 153, 202, 20, "Save As…")], clicks=[{"x": 40, "y": 13}])
    # 不截存檔視窗剛開啟的預設資料夾：那是本機「文件」資料夾，會拍到個人資料夾名稱。
    do(lambda: key("ESC"))
    file_dialog(163, LEARNER_DIR, "u01_basics_v001.blend")
    record("01-04", "learner-path", "點 Save As… 開啟存檔視窗；資料夾換成自己的單元 01 練習資料夾，檔名改為 u01_basics_v001.blend",
           lambda: "資料夾欄位：%s；檔名欄位：%s；該資料夾目前內容：%s。" % (browser() + (listing(LEARNER_DIR),)),
           win="FILE_BROWSER",
           highlights=lambda: [fb_box("path", "資料夾路徑"), fb_box("name", "檔名"), fb_box("confirm", "你要按 Save As")],
           note="這張是你要看到的畫面；路徑與檔名由助教以程式填入欄位，避免鍵盤誤觸檔案瀏覽器快捷鍵。助教示範到此按 Esc 取消，不寫入你的工作區。")
    cancel_dialog()
    file_dialog(163, demo_dir, "u01_basics_v001.blend")
    confirm_dialog()
    record("01-04", "saved-demo", "按下 Save As 後回到主視窗，底部出現存檔訊息",
           lambda: "目前檔案：%s（%d bytes）；你的工作區內容：%s。" % (
               bpy.data.filepath, os.path.getsize(bpy.data.filepath), listing(LEARNER_DIR)),
           highlights=[box(0, 997, 1494, 22, "狀態列：Saved")], park=PARK,
           note="這份檔案在助教示範資料夾，不是你的 v001；你的檔案要自己存到單元 01 練習資料夾。")

    # ===== 01-05 模式與選取 =====
    do(lambda: click(106, 38))
    record("01-05", "mode-menu", "看 3D Viewport 左上的模式選單：目前是 Object Mode",
           lambda: "模式選單展開；%s。" % selection(),
           highlights=[box(49, 28, 112, 20, "目前模式")], clicks=[{"x": 106, "y": 38}])
    do(lambda: key("ESC"))
    do(lambda: click(300, 760))
    record("01-05", "deselect", "先點 3D Viewport 空白處，取消選取",
           lambda: selection() + "。", highlights=boxes(cube_box("Cube 沒有橘色外框")),
           clicks=[{"x": 300, "y": 760}])
    do(lambda: click(617, 478))
    record("01-05", "select-cube", "單擊中央 Cube",
           lambda: selection() + "。",
           highlights=boxes(cube_box("Cube 橘色外框"), box(1286, 114, 140, 20, "Outliner 的 Cube 反白"),
                            box(49, 28, 112, 20, "Object Mode")),
           clicks=[{"x": 617, "y": 478}])

    # ===== 01-06 視角：導覽軸旋轉、核對數值、平移後找回、縮放 =====
    def remember_view():
        memo["rotation"] = tuple(view3d().view_rotation)
        memo["transform"] = transform()

    do(remember_view, 0.2)
    do(lambda: drag_slow([(1175, 130), (1168, 132), (1160, 135), (1150, 138), (1140, 141), (1130, 144), (1120, 147)]), 0.2)
    record("01-06", "orbit-gizmo", "按住右上導覽軸往左拖曳，旋轉視角",
           lambda: "視角方向%s；%s。" % ("已改變" if tuple(view3d().view_rotation) != memo["rotation"] else "未改變", transform()),
           highlights=boxes(box(1132, 86, 88, 88, "導覽軸"), cube_box("Cube 換了角度")),
           clicks=[{"x": 1175, "y": 130}], park=PARK)
    record("01-06", "transform-unchanged", "核對 Properties 的 Location／Rotation：轉視角不會改物件",
           lambda: "拖曳前：%s；拖曳後：%s。" % (memo["transform"], transform()),
           highlights=[box(1266, 338, 216, 128, "Location／Rotation 仍是 0")], park=PARK)
    do(lambda: drag_slow([(1203, 217)] + [(1203 - 50 * i, 217) for i in range(1, 19)]), 0.2)
    record("01-06", "pan-away", "按住右側手形圖示往左拖曳，平移視角",
           lambda: "%s；Cube 在畫面內：%s；%s。" % (view_state(), "是" if object_box("") else "否", selection()),
           highlights=boxes(box(1190, 204, 26, 26, "平移（手形）"), cube_box("Cube")),
           clicks=[{"x": 1203, "y": 217}], park=PARK)
    do(lambda: click(1328, 124))
    do(lambda: click(184, 38))
    record("01-06", "view-frame-selected", "在 Outliner 點 Cube，再開 3D Viewport 的 View 選單",
           lambda: selection() + "；View 選單展開。",
           highlights=[box(1286, 114, 140, 20, "Outliner：Cube"), box(169, 28, 32, 20, "View"),
                       box(170, 159, 250, 19, "Frame Selected")],
           clicks=[{"x": 1328, "y": 124}, {"x": 184, "y": 38}])
    do(lambda: click(236, 168), 1.5)
    record("01-06", "framed", "點 Frame Selected：視角對準 Cube，並拉近到填滿畫面",
           lambda: "%s；%s。" % (view_state(), transform()),
           highlights=boxes(cube_box("Cube")), clicks=[{"x": 236, "y": 168}], park=PARK)
    wheel_out(6, 614, 478)
    record("01-06", "zoom-out", "滑鼠在 3D Viewport 內，滾輪往後滾 6 格縮小視角",
           lambda: "%s；Cube 在畫面內：%s。" % (view_state(), "是" if object_box("") else "否"),
           highlights=boxes(cube_box("Cube")), park=PARK)

    # ===== 01-07 另存 v002 工作檔、Location X、Undo =====
    file_dialog(163, LEARNER_DIR, "u01_basics_v002.blend")
    record("01-07", "save-as-v002", "File > Save As…，檔名改為 u01_basics_v002.blend（v001 保留不動）",
           lambda: "資料夾欄位：%s；檔名欄位：%s。" % browser(), win="FILE_BROWSER",
           highlights=lambda: [fb_box("path", "資料夾路徑"), fb_box("name", "檔名 v002"), fb_box("confirm", "你要按 Save As")],
           note="路徑與檔名由助教以程式填入欄位。助教示範到此按 Esc 取消，再把 v002 存到示範資料夾。")
    cancel_dialog()
    file_dialog(163, demo_dir, "u01_basics_v002.blend")
    confirm_dialog()
    do(lambda: click(184, 38))
    record("01-07", "view-sidebar", "開 3D Viewport 的 View 選單，找到 Sidebar（快捷鍵 N）",
           lambda: "目前檔案：%s；View 選單展開。" % os.path.basename(bpy.data.filepath),
           highlights=[box(169, 28, 32, 20, "View"), box(170, 72, 250, 19, "Sidebar")], clicks=[{"x": 184, "y": 38}])
    do(lambda: click(216, 81), 1.0)
    record("01-07", "sidebar-open", "點 Sidebar：右側出現 Item 分頁的 Transform",
           lambda: "Sidebar 開啟：%s；%s。" % ("是" if area("VIEW_3D").spaces.active.show_region_ui else "否", transform()),
           highlights=[box(955, 82, 242, 382, "Sidebar：Item > Transform"), box(1204, 84, 20, 36, "Item")],
           clicks=[{"x": 216, "y": 81}], park=PARK)
    type_into(1050, 143, "0.5")
    record("01-07", "location-x", "點 Location X 欄位，輸入 0.5 後按 Enter",
           lambda: transform() + "。",
           highlights=boxes(box(963, 133, 176, 20, "Location X"), cube_box("Cube 往 X 方向移動")),
           clicks=[{"x": 1050, "y": 143}], park=PARK)
    do(lambda: click(75, 13))
    record("01-07", "edit-undo-menu", "開左上 Edit 選單，找到 Undo",
           lambda: transform() + "；Edit 選單展開。",
           highlights=[box(65, 3, 22, 21, "Edit"), box(64, 27, 198, 19, "Undo")], clicks=[{"x": 75, "y": 13}])
    do(lambda: click(104, 36), 1.0)
    record("01-07", "undone", "點 Undo，撤回剛才的移動",
           lambda: transform() + "。",
           highlights=boxes(box(963, 133, 176, 20, "Location X 回到 0 m"), cube_box("Cube 回到原位")),
           clicks=[{"x": 104, "y": 36}], park=PARK)

    # ===== 01-08 Dimensions 與 Scale =====
    record("01-08", "dims-scale", "在 Sidebar 找到 Scale 與 Dimensions 兩組欄位",
           lambda: transform() + "。",
           highlights=[box(963, 300, 228, 77, "Scale"), box(963, 383, 228, 77, "Dimensions")], park=PARK)
    type_into(1075, 411, "3")
    record("01-08", "dimension-x", "點 Dimensions X，輸入 3 後按 Enter，觀察 Scale X",
           lambda: transform() + "。",
           highlights=boxes(box(963, 401, 228, 20, "Dimensions X"), box(963, 319, 228, 20, "Scale X"),
                            cube_box("Cube 沿 X 變寬")),
           clicks=[{"x": 1075, "y": 411}], park=PARK)

    # ===== 01-09 儲存 v002 並重新開啟 =====
    do(lambda: click(40, 13))
    record("01-09", "file-save", "開 File 選單，找到 Save",
           lambda: "目前檔案：%s；%s。" % (os.path.basename(bpy.data.filepath), transform()),
           highlights=[box(30, 3, 27, 21, "File"), box(28, 133, 202, 20, "Save")], clicks=[{"x": 40, "y": 13}])
    do(lambda: click(68, 143), 1.5)
    record("01-09", "saved", "點 Save：底部出現存檔訊息",
           lambda: "已存檔：%s（%d bytes）。" % (bpy.data.filepath, os.path.getsize(bpy.data.filepath)),
           highlights=[box(0, 997, 1494, 22, "狀態列：Saved")], clicks=[{"x": 68, "y": 143}], park=PARK)
    file_dialog(56, demo_dir, "u01_basics_v002.blend")
    record("01-09", "open-dialog", "File > Open…，選 u01_basics_v002.blend",
           lambda: "開啟視窗：資料夾 %s；檔名 %s；資料夾內容：%s。" % (browser() + (listing(demo_dir),)),
           win="FILE_BROWSER",
           highlights=lambda: [fb_box("path", "資料夾"), fb_box("name", "檔名 v002"), fb_box("confirm", "按 Open")],
           note="此為助教示範資料夾；你要開的是自己單元 01 練習資料夾中已登記的 v002。")
    confirm_dialog(2.5)
    record("01-09", "reopened", "按 Open：重新開啟後核對路徑與數值",
           lambda: "目前檔案：%s；%s。" % (bpy.data.filepath, transform()),
           highlights=boxes(box(963, 300, 228, 160, "Scale／Dimensions 與存檔前相同"), cube_box("Cube")), park=PARK)
