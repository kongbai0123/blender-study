"""第三單元 03-01～03-06：相機、燈光、材質、EEVEE 渲染與重現的助教實際操作示範。

從第二單元示範的訊號站 v002 開始（learning/evidence/02/…/demo-files）。示範檔與輸出圖只存到本次輸出資料夾的
demo-files；存檔視窗會顯示學員單元 03 練習資料夾供對照，但一律取消。
"""
import hashlib
import os
import struct

import bpy
from bpy_extras.object_utils import world_to_camera_view
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from common import PARK, PROJECT, Kit

STATION_DIR = str(PROJECT / "learning" / "evidence" / "02" / "2026-10-22-lesson02-demo-v001" / "demo-files") + "\\"
STATION_FILE = "u02_station_v002.blend"
# 探測試算：預設相機 Z 4.96 時 Station 在畫框中 Y 0.161～1.010（訊號球頂端超出）；
# Z 5.0～5.67 都完整入框，取 5.3 讓上下留白接近。只改這一個軸。
CAMERA_Z = "5.3"
LIGHT_POWER = "2000"
BLUE_HEX = "2F6FD8"
HEX_ABOVE_SWATCH = 30      # 顏色選擇器 Hex 欄位在 Base Color 色塊上方的距離（實拍量得）
IMAGE_SAVE_AS = (216, 197)  # 渲染視窗 Image 選單中 Save As… 的位置（實拍量得）


def build(g):
    k = Kit(g)
    do, click, key, move, record = k.do, k.click, k.key, k.move, k.record
    B = k.box
    flags = {"renders": 0}
    memo = {}

    @bpy.app.handlers.persistent
    def render_done(*_):
        flags["renders"] += 1
    bpy.app.handlers.render_complete.append(render_done)

    def sha(path):
        return hashlib.sha256(open(path, "rb").read()).hexdigest()

    def png_size(path):
        with open(path, "rb") as handle:
            return struct.unpack(">II", handle.read(24)[16:24])

    def station_box(label):
        """Station Collection 所有部件在 3D Viewport 的外接框。"""
        def build_box():
            boxes = [k.object_box(o.name, "") for o in bpy.data.collections["Station"].objects]
            boxes = [b for b in boxes if b]
            if not boxes:
                return None
            x0, y0 = min(b["x"] for b in boxes), min(b["y"] for b in boxes)
            x1 = max(b["x"] + b["w"] for b in boxes)
            y1 = max(b["y"] + b["h"] for b in boxes)
            return B(x0, y0, x1 - x0, y1 - y0, label)
        return build_box

    def camera_frame_box(label):
        """相機檢視中的畫框：把相機 view_frame 四角投影到 3D Viewport。"""
        def build_box():
            view = k.area("VIEW_3D")
            region = next(r for r in view.regions if r.type == "WINDOW")
            cam = bpy.data.objects["Camera"]
            corners = [cam.matrix_world @ c for c in cam.data.view_frame(scene=bpy.context.scene)]
            points = [location_3d_to_region_2d(region, view.spaces.active.region_3d, c) for c in corners]
            height = k.window().height
            xs = [region.x + p.x for p in points]
            ys = [height - (region.y + p.y) for p in points]
            return B(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), label)
        return build_box

    def framing():
        """Station 各部件邊界角在相機畫面中的位置（0～1 為畫框內）。"""
        scene, cam = bpy.context.scene, bpy.data.objects["Camera"]
        cut = []
        xs, ys = [], []
        for o in bpy.data.collections["Station"].objects:
            pts = [world_to_camera_view(scene, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
            xs += [p.x for p in pts]
            ys += [p.y for p in pts]
            if any(not (0 <= p.x <= 1 and 0 <= p.y <= 1) for p in pts):
                cut.append(o.name)
        return "相機 Location %s；Station 在畫框中佔 X %s～%s、Y %s～%s；超出畫框的部件：%s" % (
            k.triple(cam.location), k.num(min(xs)), k.num(max(xs)), k.num(min(ys)), k.num(max(ys)),
            "、".join(cut) or "無")

    def render_settings():
        r = bpy.context.scene.render
        return "Render Engine %s；Resolution %d × %d、%d%%（輸出 %d × %d px）" % (
            r.engine, r.resolution_x, r.resolution_y, r.resolution_percentage,
            r.resolution_x * r.resolution_percentage // 100, r.resolution_y * r.resolution_percentage // 100)

    def material_state():
        mat = bpy.data.objects["Platform"].active_material
        if not mat:
            return "Platform 沒有材質"
        color = mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
        return "Platform 材質：%s；Base Color RGB (%s, %s, %s)" % (mat.name, k.num(color[0]), k.num(color[1]), k.num(color[2]))

    def tab(offset):
        return lambda: click(1245, k.props_y(offset))

    def render_image(count):
        do(lambda: click(119, 13), 0.6)
        k.menu_item(163, 36, 1.0)
        k.wait_until(lambda: flags["renders"] >= count, timeout=300)
        do(lambda: None, 1.5)

    k.setup()

    # ===== 03-01 準備渲染工作檔 =====
    k.file_dialog(56, STATION_DIR, STATION_FILE)
    record("03-01", "open-station", "File > Open…：選第二單元保存的訊號站 v002",
           lambda: "開啟視窗資料夾內容：%s。" % k.listing(STATION_DIR), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("name", "檔名 u02_station_v002.blend"), k.fb_box("confirm", "按 Open")],
           note="此為助教第二單元示範的訊號站；你要開的是自己單元 02 練習資料夾中已登記的 v002。")
    k.confirm_dialog(2.5)

    def remember_source():
        memo["source"] = bpy.data.filepath
        memo["sha"] = sha(bpy.data.filepath)
    do(remember_source, 0.2)
    record("03-01", "station-opened", "開啟後先核對來源：檔名、Station 部件與雜湊",
           lambda: "目前檔案：%s；SHA-256 %s；Station：%s。" % (
               os.path.basename(memo["source"]), memo["sha"][:16],
               "、".join(o.name for o in bpy.data.collections["Station"].objects)),
           highlights=k.boxes(lambda: k.rect("OUTLINER", "Station Collection"), station_box("訊號站")), park=PARK)
    k.show_learner_save("03-01", "save-as-render", "03", "u03_render_v001.blend",
                        "File > Save As…：資料夾換成自己的單元 03 練習資料夾，檔名 u03_render_v001.blend")
    record("03-01", "saved", "存檔後底部出現 Saved；把來源檔名與雜湊記進筆記",
           lambda: "目前檔案：%s；來源：%s（SHA-256 %s）。" % (
               os.path.basename(bpy.data.filepath), os.path.basename(memo["source"]), memo["sha"]),
           highlights=[B(0, 997, 1494, 22, "狀態列：Saved")], park=PARK)

    # ===== 03-02 安排相機 =====
    k.click_outliner("Camera")
    do(lambda: click(184, 38), 0.6)
    do(lambda: move(219, 275), 0.8)
    do(lambda: move(494, 294), 0.6)
    record("03-02", "cameras-menu", "Outliner 點 Camera，開 View > Cameras，找到 Active Camera",
           lambda: k.selection() + "；View 與 Cameras 子選單展開。",
           highlights=k.boxes(k.outliner_box("Camera", "Camera"), B(169, 28, 32, 20, "View"),
                              B(170, 266, 250, 19, "Cameras"), B(428, 284, 282, 20, "Active Camera")))
    k.menu_item(494, 294, 1.5)
    record("03-02", "camera-view", "點 Active Camera：進入相機取景，核對訊號站是否完整在畫框內",
           lambda: framing() + "。",
           highlights=k.boxes(camera_frame_box("相機畫框"), station_box("訊號站")), park=PARK)
    k.type_into(1050, 182, CAMERA_Z)
    record("03-02", "camera-z", "只改一個軸：Sidebar 的 Location Z 輸入 %s，訊號站移到畫框中央" % CAMERA_Z,
           lambda: framing() + "。",
           highlights=k.boxes(B(963, 172, 176, 20, "Location Z"), camera_frame_box("相機畫框"), station_box("訊號站")),
           park=PARK)

    # ===== 03-03 安排燈光 =====
    k.click_outliner("Light")
    do(tab(352), 0.8)
    do(lambda: click(1188, 38), 4.0)

    def remember_light():
        memo["power"] = bpy.data.objects["Light"].data.energy
    do(remember_light, 0.2)
    record("03-03", "rendered-before", "Outliner 點 Light，開 Light 分頁；3D Viewport 右上切到 Rendered 預覽",
           lambda: "Light Power %s W；視圖著色：%s。" % (k.num(memo["power"]), k.view3d().shading.type),
           highlights=lambda: [k.outliner_box("Light", "Light")(), B(1179, 29, 19, 19, "Rendered"),
                               B(1352, k.props_y(243), 103, 20, "Power")], park=PARK)
    do(lambda: click(1403, k.props_y(253)), 0.5)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text(LIGHT_POWER), 0.3)
    do(lambda: key("RET"), 4.0)
    record("03-03", "power-after", "只改 Power：輸入 %s 後按 Enter，比較亮度" % LIGHT_POWER,
           lambda: "Power %s W → %s W。" % (k.num(memo["power"]), k.num(bpy.data.objects["Light"].data.energy)),
           highlights=k.boxes(lambda: B(1352, k.props_y(243), 103, 20, "Power"), station_box("訊號站")), park=PARK)

    # ===== 03-04 指定材質 =====
    k.click_outliner("Platform")
    do(tab(436), 0.8)
    record("03-04", "material-tab", "Outliner 只點 Platform，開 Material 分頁：目前沒有材質，有 New 按鈕",
           lambda: k.selection() + "；" + material_state() + "。",
           highlights=lambda: [k.outliner_box("Platform", "Platform")(), B(1236, k.props_y(426), 20, 20, "Material 分頁"),
                               B(1298, k.props_y(155), 185, 20, "New")], park=PARK)
    do(lambda: click(1399, k.props_y(165)), 1.0)
    # 名稱欄位要先移過去讓它反白，下一個事件循環再點，才會進入編輯狀態。
    do(lambda: move(1338, k.props_y(165)), 0.5)
    do(lambda: click(1338, k.props_y(165)), 0.6)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text("Platform_Blue"), 0.3)
    do(lambda: key("RET"), 1.0)
    record("03-04", "material-named", "按 New 建立材質，再點名稱欄位改成 Platform_Blue",
           lambda: material_state() + "。",
           highlights=lambda: [B(1298, k.props_y(155), 100, 20, "Platform_Blue"), B(1370, k.props_y(281), 86, 20, "Base Color")],
           park=PARK)
    do(lambda: click(1412, k.props_y(291)), 1.0)
    do(lambda: click(1357, k.props_y(291) - HEX_ABOVE_SWATCH), 0.5)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text(BLUE_HEX), 0.3)
    record("03-04", "hex", "點 Base Color 色塊，在顏色選擇器的 Hex 欄輸入 %s" % BLUE_HEX,
           lambda: material_state() + "（尚未按 Enter）。",
           highlights=lambda: [B(1292, k.props_y(291) - HEX_ABOVE_SWATCH - 11, 130, 22, "Hex")])
    do(lambda: key("RET"), 0.6)
    # 實測：游標移開不會關閉選擇器；點底部狀態列空白處關閉（這一下只關選擇器，不改任何設定）。
    do(lambda: click(700, 1008), 0.6)
    do(lambda: move(*PARK), 3.0)
    record("03-04", "blue", "按 Enter，再點一下底部狀態列空白處關閉選擇器：Rendered 預覽中只有平台變藍",
           lambda: material_state() + "；其他部件材質：%s。" % "、".join(
               "%s=%s" % (o.name, o.active_material.name if o.active_material else "無")
               for o in bpy.data.collections["Station"].objects if o.name != "Platform"),
           highlights=k.boxes(k.obj_box("Platform", "Platform_Blue")), park=PARK)

    # ===== 03-05 設定、保存、渲染、存 PNG =====
    do(tab(83), 0.8)
    record("03-05", "render-engine", "Properties 的 Render 分頁：Render Engine 是 EEVEE",
           lambda: render_settings() + "。",
           highlights=lambda: [B(1236, k.props_y(73), 20, 20, "Render 分頁"), B(1358, k.props_y(70), 125, 22, "EEVEE")],
           park=PARK)
    do(tab(111), 0.8)
    do(lambda: click(1417, k.props_y(146)), 0.5)
    do(lambda: key("A", ctrl=True), 0.3)
    do(lambda: k.type_text("50"), 0.3)
    do(lambda: key("RET"), 1.0)
    record("03-05", "resolution", "Output 分頁：Resolution % 輸入 50，輸出變成 960 × 540 px",
           lambda: render_settings() + "。",
           highlights=lambda: [B(1236, k.props_y(101), 20, 20, "Output 分頁"), B(1358, k.props_y(97), 118, 58, "Resolution")],
           park=PARK)
    do(lambda: click(40, 13), 0.6)
    k.menu_item(68, 143, 1.5)

    def remember_scene():
        memo["scene_sha"] = sha(bpy.data.filepath)
    do(remember_scene, 0.2)
    record("03-05", "scene-saved", "先 File > Save 保存場景檢查點，再渲染",
           lambda: "已存檔：%s（SHA-256 %s）；%s。" % (os.path.basename(bpy.data.filepath), memo["scene_sha"][:16], render_settings()),
           highlights=[B(0, 997, 1494, 22, "狀態列：Saved")], park=PARK)
    do(lambda: click(119, 13), 0.6)
    do(lambda: move(163, 36), 0.6)
    record("03-05", "render-menu", "上方 Render 選單，找到 Render Image（F12）",
           lambda: "Render 選單展開。", highlights=[B(94, 3, 50, 21, "Render"), B(98, 27, 194, 19, "Render Image")])
    k.menu_item(163, 36, 1.0)
    k.wait_until(lambda: flags["renders"] >= 1, timeout=300)
    do(lambda: None, 1.5)
    record("03-05", "render-window", "點 Render Image：另開渲染視窗，等它算完",
           lambda: "渲染完成 %d 次；%s；%s。" % (flags["renders"], render_settings(), material_state()),
           win="IMAGE_EDITOR", highlights=[B(167, 3, 36, 20, "Image 選單")])
    k.show_learner_save("03-05", "save-png", "03", "u03_render_v001_preview.png",
                        "渲染視窗的 Image > Save As…：資料夾換成單元 03 練習資料夾，檔名含來源版本",
                        menu_y=IMAGE_SAVE_AS[1], menu_x=183, item_x=IMAGE_SAVE_AS[0], win="IMAGE_EDITOR",
                        confirm_label="Save As Image")
    record("03-05", "png-saved", "PNG 存好後核對：檔案、尺寸與來源場景",
           lambda: "PNG：%s（%d × %d px、%d bytes）；來源場景 u03_render_v001.blend SHA-256 %s。" % (
               ("u03_render_v001_preview.png",) + png_size(k.demo_dir + "u03_render_v001_preview.png") +
               (os.path.getsize(k.demo_dir + "u03_render_v001_preview.png"), memo["scene_sha"][:16])),
           win="IMAGE_EDITOR", highlights=[])

    # ===== 03-06 重新開檔再渲染 =====
    do(lambda: key("ESC", win="IMAGE_EDITOR"), 1.0)
    do(lambda: click(40, 13), 0.6)
    k.menu_item(81, 56, 1.5)
    # 實測：渲染與另存圖片後 Blender 把檔案標成有變更，File > Open… 會先跳出 Save changes 對話框。
    record("03-06", "unsaved-dialog", "在渲染視窗按 Esc 關閉，再按 File > Open…：先跳出 Save changes before closing?",
           lambda: "Blender 標記有未存變更：%s；磁碟上的 u03_render_v001.blend SHA-256 %s（%s登記時的 %s）。" % (
               "是" if bpy.data.is_dirty else "否", sha(bpy.data.filepath)[:16],
               "等於" if sha(bpy.data.filepath) == memo["scene_sha"] else "不同於", memo["scene_sha"][:16]),
           highlights=[B(527, 456, 440, 108, "Save changes before closing?"),
                       B(716, 528, 115, 22, "按 Don't Save（不要按 Save）")],
           note="存檔後只做了渲染與另存 PNG，Blender 仍把檔案標成有變更。v001 已是登記過的檢查點：按 Save 會覆寫它、改變雜湊。"
                "助教先核對磁碟上的雜湊和登記時相同、場景沒有再改，才按 Don't Save；不確定時按 Cancel 並先回報。")
    k.menu_item(773, 539, 1.5)
    k.fill_dialog(k.demo_dir, "u03_render_v001.blend")
    k.confirm_dialog(3.0)
    do(lambda: None, 2.0)
    record("03-06", "reopened", "按 Don't Save 後選 u03_render_v001.blend 開啟，核對設定是否都還在",
           lambda: "目前檔案：%s（SHA-256 %s）；%s；Camera Location Z %s m；Light Power %s W；%s。" % (
               os.path.basename(bpy.data.filepath), sha(bpy.data.filepath)[:16], render_settings(),
               k.num(bpy.data.objects["Camera"].location.z), k.num(bpy.data.objects["Light"].data.energy),
               material_state()) + "3D Viewport 著色：%s。" % k.view3d().shading.type,
           highlights=k.boxes(station_box("訊號站")), park=PARK,
           note="實測：重新開檔後 3D Viewport 回到 Solid 著色，所以平台看起來是灰色；材質仍在（讀回 Platform_Blue），"
                "按右上 Rendered 才會再看到藍色。下一張渲染圖可確認顏色沒有遺失。")
    render_image(2)
    record("03-06", "render-again", "再按 Render > Render Image",
           lambda: "渲染完成 %d 次；%s。" % (flags["renders"], render_settings()), win="IMAGE_EDITOR", highlights=[])
    k.file_dialog(IMAGE_SAVE_AS[1], k.demo_dir, "u03_render_v001_repeat.png", menu_x=183,
                  item_x=IMAGE_SAVE_AS[0], win="IMAGE_EDITOR")
    k.confirm_dialog()

    def compare():
        first = bpy.data.images.load(k.demo_dir + "u03_render_v001_preview.png", check_existing=False)
        second = bpy.data.images.load(k.demo_dir + "u03_render_v001_repeat.png", check_existing=False)
        if tuple(first.size) != tuple(second.size):
            return "兩張尺寸不同：%s 與 %s" % (tuple(first.size), tuple(second.size))
        a, b = list(first.pixels), list(second.pixels)
        diffs = [abs(x - y) for x, y in zip(a, b)]
        changed = sum(1 for d in diffs if d > 1 / 255)
        return "兩張都是 %d × %d px；平均差 %s、最大差 %s（0～1），超過 1/255 的通道值 %d / %d" % (
            first.size[0], first.size[1], k.num(sum(diffs) / len(diffs)), k.num(max(diffs)), changed, len(diffs))
    record("03-06", "compare", "另存 u03_render_v001_repeat.png，和第一次的 PNG 逐像素比較",
           lambda: compare() + "。", win="IMAGE_EDITOR", highlights=[])
