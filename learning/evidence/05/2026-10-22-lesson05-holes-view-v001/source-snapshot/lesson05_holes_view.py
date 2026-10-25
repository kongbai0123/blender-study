"""05-03 supplemental actual views; open the verified source without saving it."""
import json
from datetime import datetime, timezone
from pathlib import Path

import bpy

from common import PARK, PROJECT, Kit
from holeplate_checks import read_and_validate


SOURCE = PROJECT / "learning/evidence/05/2026-10-22-lesson05-holes-demo-v002/demo-files/u05_hole_plate_v001.blend"
SOURCE_SHA256 = "10bfffd651d1583d8704164288aa0757fa617f67a30e21176d7fc892aef3e692"


def build(g):
    k = Kit(g)
    do, key, move, record = k.do, k.key, k.move, k.record
    out = Path(g["OUT"])
    if g["sha256"](str(SOURCE)) != SOURCE_SHA256:
        raise RuntimeError("Supplemental view source hash differs from verified v002")
    snapshot_dir = out / "source-snapshot"
    snapshot_dir.mkdir()
    files = []
    for relative in ("learning/tutor/run_demo.py", "learning/tutor/blender_demo.py",
                     "learning/tutor/scenarios/common.py", "learning/tutor/scenarios/lesson05_holes_view.py",
                     "learning/tutor/scenarios/holeplate_checks.py"):
        source = PROJECT / relative
        target = snapshot_dir / source.name
        target.write_bytes(source.read_bytes())
        files.append({"source": relative, "snapshot": "source-snapshot/" + source.name,
                      "sha256": g["sha256"](str(target))})
    (snapshot_dir / "manifest.json").write_text(json.dumps({
        "recordedAt": datetime.now(timezone.utc).isoformat(), "files": files,
        "supplementalSource": str(SOURCE), "supplementalSourceSha256": SOURCE_SHA256,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def source_check():
        if Path(bpy.data.filepath).resolve() != SOURCE.resolve() or g["sha256"](str(SOURCE)) != SOURCE_SHA256:
            raise RuntimeError("Opened source path/hash mismatch or source was modified")
        k.guard()
        return "以唯讀補充示範方式開啟 v002 的孔板 v001；來源 SHA-256 與主示範相同，沒有另存或覆寫。"

    k.setup()
    k.file_dialog(56, str(SOURCE.parent) + "\\", SOURCE.name)
    record("05-03", "supplement-open-dialog", "File > Open…，指定已驗證的主示範孔板 v001；不另存",
           lambda: "資料夾 %s；檔名 %s。" % k.browser(), win="FILE_BROWSER",
           highlights=lambda: [k.fb_box("name", "主示範的同一檔案"), k.fb_box("confirm", "Open")])
    k.confirm_dialog(2.5)
    record("05-03", "supplement-source-opened", "開啟後先核對來源檔案路徑與 SHA-256", source_check, park=PARK)
    do(lambda: key("N", x=700, y=600), 0.5)
    do(lambda: key("NUMPAD_2", x=700, y=600), 0.5)
    record("05-03", "supplement-orbit-15", "在 3D Viewport 按 N 收起側欄，再按數字鍵盤 2，向下旋轉視角 15 度",
           source_check, highlights=k.boxes(k.obj_box("Plate", "實際通孔板與盲凹點")), park=PARK)
    do(lambda: key("NUMPAD_2", x=700, y=600), 0.5)
    do(lambda: key("NUMPAD_2", x=700, y=600), 0.5)
    do(lambda: key("NUMPAD_6", x=700, y=600), 0.5)

    def zoom():
        move(614, 478)
        for _ in range(2):
            g["_event"](k.window(), "WHEELUPMOUSE", "PRESS", 614, 478)
    do(zoom, 1.0)

    def verified():
        source_check()
        result = read_and_validate(bpy.data.objects["Plate"])
        result.update(kind="hole_plate_supplemental_view", scene_path=str(SOURCE),
                      scene_sha256=SOURCE_SHA256, reopened=True, source_unchanged=True,
                      authoritative_run="learning/evidence/05/2026-10-22-lesson05-holes-demo-v002",
                      supplemental_only=True, saved_new_scene=False,
                      printed=False, fit_tested=False, qualified_clearance_mm=None)
        (out / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return "傾斜視角的同一孔板：六通孔 %d；盲凹點各列 %s；Non Manifold %d；來源 SHA-256 不變。" % (
            result["through_holes"], result["marker_counts"], result["non_manifold_edges"])

    record("05-03", "supplement-oblique-verified", "再按數字鍵盤 2 兩次、6 一次，滾輪放大兩格，以傾斜視角核對凹點與板厚",
           verified, highlights=k.boxes(k.obj_box("Plate", "實拍：六方孔及 1～6 點盲凹標記")), park=PARK,
           note="只改獨立視窗的觀察視角，不儲存 .blend。總間隙 0.1～0.6 mm 仍為未列印、未試配的試驗點。")
