"""第二、三單元劇本共用：讀回狀態、標示框、安全的檔案對話框、欄位輸入。

座標取自 Blender 5.2.1 LTS、1494×1019、English (US)、出廠版面的實際截圖。
學員工作區（learning/workspaces/01～03）只顯示路徑、不寫入；一有變動就中止劇本。
"""
import os
from pathlib import Path

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[3]
WORKSPACES = PROJECT / "learning" / "workspaces"
PARK = (700, 800)  # 3D Viewport 空白處：截圖前把游標移到這裡，避免按鈕提示遮住畫面。
OUTLINER_FIRST_ROW = 104  # Collection 展開時第一個子項目的列中心（圖片座標）
OUTLINER_ROW = 20


class Kit:
    def __init__(self, g):
        self.g = g
        self.do, self.click, self.key, self.move = g["do"], g["click"], g["key"], g["move"]
        self.type_text, self.drag_slow, self.record = g["type_text"], g["drag_slow"], g["record"]
        self.window, self.area, self.event, self.wait_until = g["window"], g["area"], g["_event"], g["wait_until"]
        self.demo_dir = os.path.join(g["OUT"], "demo-files") + "\\"
        os.makedirs(self.demo_dir, exist_ok=True)
        self.learner_before = {p.name: sorted(os.listdir(p)) for p in WORKSPACES.iterdir() if p.is_dir()}

    # ---- 學員工作區保護 ----
    def learner_dir(self, lesson):
        return str(WORKSPACES / lesson) + "\\"

    def guard(self):
        now = {p.name: sorted(os.listdir(p)) for p in WORKSPACES.iterdir() if p.is_dir()}
        if now != self.learner_before:
            raise RuntimeError("學員工作區內容改變，已中止示範：%s" % now)

    # ---- 讀回實際狀態 ----
    @staticmethod
    def num(value):
        return "%g" % round(value, 4)

    def triple(self, values, unit=" m", factor=1.0):
        return "(" + ", ".join(self.num(v * factor) + unit for v in values) + ")"

    def obj(self, name):
        return bpy.data.objects[name]

    def selection(self):
        names = [o.name for o in bpy.context.selected_objects]
        active = bpy.context.view_layer.objects.active
        return "已選取：%s；作用中物件：%s" % ("、".join(names) or "無", active.name if active else "無")

    def size(self, name, unit=" m", factor=1.0):
        o = self.obj(name)
        return "%s Location %s、Dimensions %s、Scale %s" % (
            name, self.triple(o.location, unit, factor), self.triple(o.dimensions, unit, factor),
            self.triple(o.scale, ""))

    def bottom_top(self, name):
        o = self.obj(name)
        return o.location.z - o.dimensions.z / 2, o.location.z + o.dimensions.z / 2

    def listing(self, path):
        return "、".join(sorted(os.listdir(path))) or "（空資料夾）"

    def browser(self):
        params = self.window("FILE_BROWSER").screen.areas[0].spaces.active.params
        directory = params.directory.decode() if isinstance(params.directory, bytes) else params.directory
        return directory, params.filename

    def view3d(self):
        return self.area("VIEW_3D").spaces.active

    # ---- 標示框（圖片座標，左上為原點） ----
    @staticmethod
    def box(x, y, w, h, label):
        return {"x": int(x), "y": int(y), "w": int(w), "h": int(h), "label": label}

    def rect(self, kind, label):
        a = self.area(kind)
        return self.box(a.x, self.window().height - (a.y + a.height), a.width, a.height, label)

    def object_box(self, name, label, pad=8):
        """把物件 8 個邊界角投影到 3D Viewport，取外接框；不在畫面內時回傳 None。"""
        view = self.area("VIEW_3D")
        region = next(r for r in view.regions if r.type == "WINDOW")
        o = self.obj(name)
        points = [location_3d_to_region_2d(region, view.spaces.active.region_3d, o.matrix_world @ Vector(c))
                  for c in o.bound_box]
        points = [p for p in points if p is not None]
        if not points:
            return None
        height = self.window().height
        left, right = region.x, region.x + region.width
        top, bottom = height - (region.y + region.height), height - region.y
        x0 = max(min(region.x + p.x for p in points) - pad, left)
        x1 = min(max(region.x + p.x for p in points) + pad, right)
        y0 = max(min(height - (region.y + p.y) for p in points) - pad, top)
        y1 = min(max(height - (region.y + p.y) for p in points) + pad, bottom)
        if x0 >= x1 or y0 >= y1:
            return None
        return self.box(x0, y0, x1 - x0, y1 - y0, label)

    def boxes(self, *items):
        # 截圖當下才計算（物件位置會隨操作改變）；不在畫面內的標示略過。
        def collect():
            values = (item() if callable(item) else item for item in items)
            return [value for value in values if value]
        return collect

    def obj_box(self, name, label):
        return lambda: self.object_box(name, label)

    def outliner_names(self):
        """Outliner 中 Collection 下的物件，依 Outliner 的字母順序排列。"""
        names = []
        for coll in bpy.context.scene.collection.children:
            names.append(("collection", coll.name))
            names += [("object", o.name) for o in sorted(coll.objects, key=lambda o: o.name.lower())]
        return names

    def outliner_y(self, name):
        rows = [n for kind, n in self.outliner_names()]
        return OUTLINER_FIRST_ROW - OUTLINER_ROW + OUTLINER_ROW * rows.index(name)

    def outliner_box(self, name, label):
        return lambda: self.box(1286, self.outliner_y(name) - 10, 150, 20, label)

    def fb_box(self, kind, label):
        w = self.window("FILE_BROWSER")
        spots = {"path": (394, 8, w.width - 742, 25), "name": (248, w.height - 34, w.width - 280, 25),
                 "confirm": (w.width - 271, w.height - 34, 126, 25)}
        return self.box(*spots[kind], label)

    # ---- 操作 ----
    def menu_item(self, x, y, wait=1.0, win="main"):
        # 先移到選單項目讓它反白，再在下一個事件循環點擊；同批送出時選單項目可能不觸發。
        self.do(lambda: self.move(x, y, win=win), 0.4)
        self.do(lambda: self.click(x, y, win=win), wait)

    def props_y(self, offset):
        """Properties 內元件的 y：以出廠版面（Properties 上緣 207）量到的位移，加上目前上緣。

        訊號站檔案存了加高的 Outliner，Properties 會整個往下移。
        """
        a = self.area("PROPERTIES")
        return self.window().height - (a.y + a.height) + offset

    def click_outliner(self, name, ctrl=False):
        self.do(lambda: self.click(1340, self.outliner_y(name), ctrl=ctrl), 0.6)

    def type_into(self, x, y, text, win="main"):
        self.do(lambda: self.click(x, y, win=win), 0.5)
        self.do(lambda: self.key("A", win=win, ctrl=True), 0.3)
        self.do(lambda: self.type_text(text, win=win), 0.3)
        self.do(lambda: self.key("RET", win=win), 1.0)

    def add_mesh(self, item_y, wait=1.0):
        """Add > Mesh > 指定項目（Plane 60、Cube 80、UV Sphere 120）。"""
        self.do(lambda: self.click(270, 38), 0.6)
        self.do(lambda: self.move(298, 61), 0.8)
        self.menu_item(468, item_y, wait)

    def wheel_out(self, notches, x=614, y=478):
        # 模擬事件不經過系統的滾輪轉換；實測 WHEELDOWNMOUSE 才是縮小（每格約 ×1.2 距離）。
        def roll():
            self.move(x, y)
            for _ in range(notches):
                self.event(self.window(), "WHEELDOWNMOUSE", "PRESS", x, y)
        self.do(roll, 1.0)

    def open_sidebar(self):
        self.do(lambda: self.click(184, 38), 0.6)
        self.menu_item(216, 81)

    def rename_active(self, name):
        """Edit > Rename Active Item…：彈出的名稱欄位已在編輯狀態。"""
        self.do(lambda: self.click(75, 13), 0.6)
        self.menu_item(147, 197, 1.0)
        self.do(lambda: self.key("A", ctrl=True), 0.3)
        self.do(lambda: self.type_text(name), 0.3)
        self.do(lambda: self.key("RET"), 0.8)

    def file_dialog(self, menu_y, directory, filename, menu_x=40, item_x=81, win="main"):
        """開 File（或渲染視窗 Image）選單的存檔／開檔項目，再以 Blender 資料寫入欄位。

        檔案瀏覽器中的按鍵是快捷鍵（I 會新增資料夾）；模擬打字一旦沒進入編輯狀態就可能寫入磁碟。
        """
        self.do(lambda: self.click(menu_x, 13, win=win), 0.6)
        self.menu_item(item_x, menu_y, 1.5, win=win)
        self.fill_dialog(directory, filename)

    def fill_dialog(self, directory, filename):
        def fill():
            w = self.window("FILE_BROWSER")
            file_area = w.screen.areas[0]
            params = file_area.spaces.active.params
            params.directory = directory.encode() if isinstance(params.directory, bytes) else directory
            params.filename = filename
            with bpy.context.temp_override(window=w, area=file_area):
                bpy.ops.file.refresh()
            file_area.tag_redraw()
            self.guard()
        self.do(fill, 1.2)

    def cancel_dialog(self):
        self.do(lambda: self.key("ESC", win="FILE_BROWSER"), 1.0)
        self.do(self.guard, 0.2)

    def confirm_dialog(self, wait=1.5):
        def press():
            w = self.window("FILE_BROWSER")
            self.click(w.width - 209, w.height - 21, win="FILE_BROWSER")
        self.do(press, wait)
        self.do(self.guard, 0.2)

    def show_learner_save(self, step, slug, lesson, filename, action, menu_y=163, menu_x=40, item_x=81, win="main",
                          confirm_label="Save As"):
        """在存檔視窗顯示學員自己的路徑與檔名後取消；再把同名檔存到示範資料夾。"""
        self.file_dialog(menu_y, self.learner_dir(lesson), filename, menu_x, item_x, win)
        self.record(step, slug, action,
                    lambda: "資料夾欄位：%s；檔名欄位：%s；該資料夾目前內容：%s。" % (
                        self.browser() + (self.listing(self.learner_dir(lesson)),)),
                    win="FILE_BROWSER",
                    highlights=lambda: [self.fb_box("path", "資料夾路徑"), self.fb_box("name", "檔名"),
                                        self.fb_box("confirm", "你要按 " + confirm_label)],
                    note="這張是你要看到的畫面；路徑與檔名由助教以程式填入欄位，避免鍵盤誤觸檔案瀏覽器快捷鍵。"
                         "助教示範到此按 Esc 取消，不寫入你的工作區，再把同名檔存到助教示範資料夾。")
        self.cancel_dialog()
        self.file_dialog(menu_y, self.demo_dir, filename, menu_x, item_x, win)
        self.confirm_dialog()

    def setup(self):
        def run():
            prefs = bpy.context.preferences
            prefs.view.language = "en_US"
            prefs.filepaths.use_auto_save_temporary_files = False
            self.key("ESC")
        self.do(run, 1.5)
