"""把 run_demo.py 產生的 run.json 寫入 catalog 各步驟的 operationRun，並輸出證據 metadata。

用法：python learning/tutor/import_run.py <run_id>
run 資料夾：learning/evidence/<單元>/<run_id>/（單元取 run_id 中 lesson 後兩碼）
"""
import copy
import hashlib
import json
import math
import os
import struct
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
CATALOG = PROJECT / "learning" / "catalog.json"

RUNS = {
    "2026-10-25-lesson08-parameters-demo-v001": {
        "lesson": "08",
        "journal": "learning/journal/2026-10-25-lesson08-parameters-demo-v001.md",
        "source_scene_sha256": "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530",
        "data_bindings": {
            "learning/plans/08-01-thread-parameters-v001.json": {
                "snapshot": "source-snapshot/parameter-template-v001.json",
                "sha256": "92c0bf94ede81a48a5c16179ae1558bb8c61c521f960c79cd4ad05830f0d79bb"
            },
            "sources/engineering/thread-source-facts-v001.json": {
                "snapshot": "source-snapshot/thread-source-facts-v001.json",
                "sha256": "78a0b7b1092287e7956b9a11da17f4b1ef838c7da50473e989d05cc759b67834"
            }
        },
        "authorization": "依使用者要求延續獨立Blender真實操作、實拍與版本紀錄，先整理08-01螺紋規格與建模參數，僅核對乾淨原盒、另存重開參照。助教首候選不是學員選定路線；未授予任何螺紋尺寸或合格製造參數。",
        "summaries": {
            "08-01": "助教從原04盒同hash副本核對外形60×40×30、內腔56×36×28、壁底2 mm，實選盒口／內底／外底並另存重開螺紋參照場景。24個規格與建模參數仍為null／draft_pending，三條路線未選；Screw的Angle／軸移／Iterations／分段只作文件映射，未建立修改器、螺紋、柱、導孔或對件。第五單元0.1～0.6 mm是未試配的幾何試驗點，未轉作螺紋合格間隙；材料、硬體、列印與實體結果待定。"
        },
        "content_review_summary": "已核對固定原盒、六份執行腳本與參數模板／官方來源facts快照；以原生實選面與世界網格重算核對盒尺寸、來源與新參照版本。文件定義、未設定的修改器映射和待補尺寸草案均與Blender原盒實測分欄，不標成已建螺紋、標準規格、已選路線或製造合格值。",
        "completion_scope": "08-01 原盒實測與另存重開、螺紋規格／建模映射的待定參數表；未選路線／尺寸／標準／五金，未建螺紋或柱、計算強度、匯出STL、切片、列印或試配",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 0.0001,
            "purpose": "僅作原盒世界座標與實選面的浮點重建，不是螺紋尺寸、公差等級、扭矩、強度或實體配合門檻。"
        },
        "geometry_evidence_files": [
            "source_body_mesh.json",
            "reference_body_mesh.json"
        ],
        "data_evidence_files": [
            "parameter-record-v001.json",
            "face-measurements.json"
        ],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": []
    },
    "2026-10-25-lesson07-coupon-export-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-coupon-export-demo-v001.md",
        "source_scene_sha256": "22072532eed0f6fcc506bb435ed8d65fcaeaef583ea41d90c4e8c9665b82e9b8",
        "source_coupon_record_sha256": "1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d",
        "draft_plan_sha256": "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33",
        "data_bindings": {
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/coupon-record-v001.json": {
                "snapshot": "source-snapshot/source-coupon-record-v001.json",
                "sha256": "1180c5194a5ec09af9186e2e3f69761e5460a4350f9019e9d1020a44e127c01d"
            },
            "learning/plans/07-05-coupon-length-draft-v001.json": {
                "snapshot": "source-snapshot/coupon-plan-v001.json",
                "sha256": "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33"
            },
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/verification.json": {
                "snapshot": "source-snapshot/source-coupon-verification.json",
                "sha256": "ecea0a82400931113ad34f9c1fe054d6711835558d268973680a029ea656950b"
            },
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/source_snap_tool_mesh.json": {
                "snapshot": "source-snapshot/source-snap-tool-reference.json",
                "sha256": "cb01f749d093467ec90742d38f90243067cdec00eee545c6c81f3f7b20a6aee7"
            },
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/A_L19_candidate_mesh.json": {
                "snapshot": "source-snapshot/source-A_L19-candidate-mesh.json",
                "sha256": "5646200083769661833503b5177306fa0d80e0117597dad691b83f97b7b7530c"
            },
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/B_L17_candidate_mesh.json": {
                "snapshot": "source-snapshot/source-B_L17-candidate-mesh.json",
                "sha256": "dc7cb34b232c1853fad6ae67f5de3149a63f0da2bbf7eac595fa062ef4acbcc7"
            },
            "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001/C_L21_candidate_mesh.json": {
                "snapshot": "source-snapshot/source-C_L21-candidate-mesh.json",
                "sha256": "0a40675dd41b0c8d6eb96376295ca0aaa090696b3349360187b3f0e23bcfc8c2"
            }
        },
        "data_evidence_files": ["coupon-stl-export-record-v001.json", "A_L19-stl-verification.json", "B_L17-stl-verification.json", "C_L21-stl-verification.json"],
        "authorization": "依使用者要求延續同一07-05步驟，從三個已保存的獨立長度試片候選分件原生匯出STL、實際重新匯入核對並記版本。未改原形或候選姿態、不Apply、不另存blend；未指定試扣對件、夾持或列印／實體改善結論。",
        "summaries": {"07-05": "助教以固定三coupon場景同hash副本，分別只選A_L19／B_L17／C_L21匯出v001二進位STL，排除其餘試片及四個隱藏來源件。保留Ry90候選world坐標，實檔外框約24／22／26 × 4.6 × 9 mm；Selection Only開、Scale1、Scene Unit關、Y Forward／Z Up。解析完整有向表面與逆姿態／逆長度語義，再於空白毫米場景實際重匯入，R0／Location0／Scale1核對world尺寸、閉合及分列擺位。只完成三件STL數位準備，沒有重新改幾何、指定對件／夾具、切片、列印、試扣或已驗證改善。"},
        "content_review_summary": "已核對固定三試片場景、coupon紀錄／單參數計畫、原SnapTool與三candidate世界網格及腳本快照。分件只選單件，實際File Browser確認前選項與產出的STL／新匯入mesh分別留證；不假造缺少的operator歷程。STL無自身rotation metadata，來源姿態參考與重匯入R0狀態分開驗證；合法重編索引／面細分與實際幾何L、原形回算及床接觸／離床特徵分開。對件、定位、夾持、材料、力學、支撐及實體合格結果仍空白。",
        "completion_scope": "07-05 三個既有獨立長度coupon的STL匯出、實檔及實際重匯入數位核對；對件／夾持／整盒邊界、支撐、切片、列印、力學、試配與改善尚未驗證",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4, "coordinateWeldMm": 1e-5, "volumeRelativeTolerance": 1e-5,
                               "purpose": "僅處理三coupon STL與CAD世界表面、逆姿態／逆長度及體積的浮點重建；不是製造公差、有效力學長度、支撐、強度／試配／改善合格門檻。"},
        "geometry_evidence_files": ["source_A_L19_mesh.json", "reimport_A_L19_mesh.json", "source_B_L17_mesh.json",
                                    "reimport_B_L17_mesh.json", "source_C_L21_mesh.json", "reimport_C_L21_mesh.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson07-coupons-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-coupons-demo-v001.md",
        "source_scene_sha256": "360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d",
        "source_tool_sha256": "c60a6ed737f426277e0157ad1f7554a3070ba4395aec319693d6a2d9104c6140",
        "source_tool_local_sha256": "70aa7799e1bb0110ab65ab94b0f5135ec365c936773f43d49bfa651077bae2b2",
        "draft_plan_sha256": "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33",
        "data_bindings": {
            "learning/plans/07-05-coupon-length-draft-v001.json": {
                "snapshot": "source-snapshot/coupon-plan-v001.json",
                "sha256": "35905a851b846b757bbdbb9321708606b4497a0dc4d5d1cdea0f8735d303dd33"},
            "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/verification.json": {
                "snapshot": "source-snapshot/source-orientation-verification.json",
                "sha256": "ab84fcc47ee59d2303a1174a8b67c27c898255c5c556e3b0deaee616741b9dc7"},
            "learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/snap_tool_mesh.json": {
                "snapshot": "source-snapshot/source-snap-tool-reference.json",
                "sha256": "c60a6ed737f426277e0157ad1f7554a3070ba4395aec319693d6a2d9104c6140"},
            "learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/geometry-draft-record-v001.json": {
                "snapshot": "source-snapshot/source-geometry-record-v001.json",
                "sha256": "4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a"},
            "learning/evidence/07/2026-10-25-lesson07-snap-export-demo-v001/stl-export-record-v001.json": {
                "snapshot": "source-snapshot/source-export-record-v001.json",
                "sha256": "b3b3745d714a628b5155b01fbfeca81cda50855aaeb95aa757f616ea58ee268a"},
        },
        "authorization": "依使用者要求延續獨立 Blender 卡扣工程示範，由助教建立三個僅改幾何臂長的獨立 anchor／臂／鉤試片，保存實拍、讀值與新版本。這不是整盒邊界、已驗證改善、材料或實體合格結論。",
        "summaries": {"07-05": "助教從 07-03 固定場景的隱藏 SnapTool 建立三個獨立網格 A_L19／B_L17／C_L21，只移動原上端14頂點的Z量0／−2／+2 mm，保留其餘28點、錨座、臂寬厚、扣鉤與原生根部圓角。幾何根平面至承接面長度為19／17／21，與全臂高21／19／23、整件高24／22／26分開。三件Ry90側放、Y排開並另存重開；原Body／Lid及Tools形狀與矩陣不改且隱藏。只有anchor側面接觸Z0，直臂與部分根部離床；方向／支撐、夾持、材料、力學及試配仍待定，未匯出STL、切片或列印，沒有改善結論。"},
        "content_review_summary": "已核對固定原場景及SnapTool、助教單參數長度計畫、三件編輯前後與候選姿態世界網格。分別保護原物件未改與新B／C試片確有幾何修改；原生根部miter及上端扣鉤保留。獨立anchor試片的固定條件未定，不能視作整盒邊界或已證實力學有效長度；落床、離床部位與支撐待切片，實體／改善合格欄位保留空值。",
        "completion_scope": "07-05 三個單一幾何臂長的獨立anchor試片、候選擺位與另存重開；夾持／整盒邊界、力學、支撐、STL、切片、列印、試扣及改善尚未驗證",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4, "volumeRelativeTolerance": 1e-5,
                               "purpose": "僅處理單參數網格、逆姿態、圓角與落床的浮點重建；不是製造公差、力學有效長度、支撐、強度、實體配合或改善合格門檻。"},
        "geometry_evidence_files": ["source_snap_tool_mesh.json", "A_L19_source_frame_mesh.json", "A_L19_candidate_mesh.json",
                                    "B_L17_source_frame_mesh.json", "B_L17_candidate_mesh.json",
                                    "C_L21_source_frame_mesh.json", "C_L21_candidate_mesh.json"],
        "data_evidence_files": ["coupon-record-v001.json", "upper-vertex-selection-proofs.json", "vertex-motion-proofs.json",
                                "duplicate-proofs.json", "source-object-inventory.json", "native-display-settings.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson07-snap-export-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-snap-export-demo-v001.md",
        "source_scene_sha256": "360417f208287a94ca13501f4365b70b3396ca6aba579231e0f8d2a442ecf47d",
        "source_orientation_sha256": "b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986",
        "data_bindings": {
            "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/print-orientation-record-v001.json": {
                "snapshot": "source-snapshot/source-orientation-record-v001.json",
                "sha256": "b515d433f7c6b8e65e3247337f135a07bf56b0f6f9817efbab446fbf5c708986"},
            "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/verification.json": {
                "snapshot": "source-snapshot/source-orientation-verification.json",
                "sha256": "ab84fcc47ee59d2303a1174a8b67c27c898255c5c556e3b0deaee616741b9dc7"},
            "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/body_candidate_mesh.json": {
                "snapshot": "source-snapshot/source-body-candidate-mesh.json",
                "sha256": "e87e0387385977798febd880956379e5e9694928cac1f20d43a94d92f03caec8"},
            "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001/lid_candidate_mesh.json": {
                "snapshot": "source-snapshot/source-lid-candidate-mesh.json",
                "sha256": "99e7b3aced9fb8892f37d5480c1d7326cb48a11c987ff7ceee8f809ce1d27573"},
        },
        "authorization": "依使用者要求，沿用獨立 Blender 將 07-03 卡扣方向候選的 Body 與 Lid 分件匯出 STL、實際重新匯入核對並記錄版本。本次不改幾何或姿態、不另存場景，也未列印試片、試扣或作材料／強度／支撐合格判定。",
        "summaries": {"07-04": "助教從 07-03 固定方向候選同 hash 副本，分別只選 Body／Lid 原生匯出二進位 STL，排除兩隱藏建構工具。Selection Only 開、Scale1、Scene Unit 關、Y Forward／Z Up；解析兩份實檔、核對來源有向表面及逆姿態卡扣剖面，再在空白毫米場景實際重新匯入。Body 的世界外框約30 × 44.5 × 60，Lid約60 × 46 × 7，保留原候選落床座標及兩件分離距離。本次只完成既有單一草案兩件的 STL 數位準備；沒有建立2–3組參數試片或完成列印／試扣。材料、力學、支撐及實體合格結果仍待定。"},
        "content_review_summary": "已核對固定 07-03 場景、方向紀錄及讀取副本；逐件 Selection Only 原生匯出、兩份實際 STL、來源與重匯入世界網格、有向表面覆蓋及逆回07-02的完整卡扣幾何分別重算。STL 按 mm 解讀且保留候選世界座標；來源物件軸尺寸與世界外框不同。接受合法三角面細分／重新索引，不將數位核對推成列印、支撐、強度或實體試扣合格。",
        "completion_scope": "07-04 單一既有卡扣草案 Body／Lid 的 STL 匯出、實檔與實際重匯入數位核對部分；參數試片比較、切片、支撐、列印、力學與實體試扣尚未完成",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4, "volumeRelativeTolerance": 1e-5,
                               "purpose": "僅處理 STL／CAD 世界網格、有向表面、剛體逆姿態及體積的浮點重建；不是製造公差、支撐／強度或實體配合合格門檻。"},
        "geometry_evidence_files": ["source_body_mesh.json", "source_lid_mesh.json", "reimport_body_mesh.json", "reimport_lid_mesh.json"],
        "data_evidence_files": ["stl-export-record-v001.json", "body-stl-verification.json", "lid-stl-verification.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson07-overhang-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-overhang-demo-v001.md",
        "source_scene_sha256": "5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305",
        "source_geometry_sha256": "4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a",
        "draft_plan_sha256": "33831347ce131a3f29c107d18f24f0015b3314e8e8672dc2159b1d9badd4f6ac",
        "data_bindings": {
            "learning/plans/07-03-print-orientation-draft-v001.json": {
                "snapshot": "source-snapshot/print-orientation-plan-v001.json",
                "sha256": "33831347ce131a3f29c107d18f24f0015b3314e8e8672dc2159b1d9badd4f6ac"},
            "sources/engineering/overhang-source-facts-v001.json": {
                "snapshot": "source-snapshot/overhang-source-facts-v001.json",
                "sha256": "a2fa8d6c556cacb533b94648a994e2cb92baa33fccd4b513d9681d34187d8c05"},
            "sources/engineering/snapfit-source-facts-v001.json": {
                "snapshot": "source-snapshot/snapfit-source-facts-v001.json",
                "sha256": "291d1704ea12834969e74e79b948cf2677524fda7a852fa8434c017a674169f8"},
            "learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/geometry-draft-record-v001.json": {
                "snapshot": "source-snapshot/source-geometry-record-v001.json",
                "sha256": "4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a"},
        },
        "authorization": "依使用者要求延續獨立 Blender 的工程教學，以原卡扣草案做剛體方向比較、原生 Overhang 實拍、讀值與版本紀錄。0～45°是助教選用的顯示範圍，材料、支撐、強度及實體配合尚未合格。",
        "summaries": {"07-03": "助教以 07-02 同 hash 副本，分別將 Body／Lid 原向及候選方向放到世界 Z0，實際開啟原生 Mesh Analysis／Overhang、世界負 Z、名義 0～45°並保留 RNA rad／deg。Body 候選側放令臂長與名義彎曲方向平行 XY；Lid 候選翻面讓大板面成為床接觸面。原形狀只做旋轉平移且未 Apply Rotation，另存重開核對。polygon 與 loop triangle 的另算角度／面積分欄，床接觸面與離床朝下面分開；這些不是 GPU 面數或切片支撐判定。列印方向、支撐與材料仍待後續切片／實測，未匯出、列印或試配。"},
        "content_review_summary": "已核對固定 07-02 場景及幾何草案、方向計畫與精確 build 的原生 Overhang 定義、四姿態原圖／設定／Edit Mode 上下文、polygon rings／法線及剛體逆變換重算。未將幾何平行層平面推成層間強度，也未將著色、落床接觸或法線角度推成免支撐／可列印；材料與所有力學、實體、合格欄位保留空值。",
        "completion_scope": "07-03 剛體方向草案、原生 Overhang 視覺檢查與另算角度／面積、保存重開；支撐方案、床幅、橋接、切片、STL、列印、強度與試配尚未驗證",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4, "angleBoundaryBandDeg": 1e-4,
                               "volumeRelativeTolerance": 1e-5,
                               "purpose": "僅處理剛體姿態、落床高度、法線角度及體積的浮點重建，角度邊界單列；不是製造公差、支撐／列印允許角、附著、強度或配合合格門檻。"},
        "geometry_evidence_files": ["source_body_mesh.json", "source_lid_mesh.json", "body_baseline_mesh.json",
                                    "body_candidate_mesh.json", "lid_baseline_mesh.json", "lid_candidate_mesh.json"],
        "data_evidence_files": ["print-orientation-record-v001.json", "analysis-settings-by-pose.json",
                                "pose-verification.json", "source-tool-inventory.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson07-snap-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-snap-demo-v001.md",
        "source_scene_sha256": "6a6b6c03295c8b6047b97c3efdea9884954b714da87b45b7aa36b4d2b612d3a9",
        "source_parameter_sha256": "57d411f24486aad351056854b8eb427aae853b99f290372c9d0294d367ac6ead",
        "draft_plan_sha256": "f4f0fab02a47eaade189c3b1c6cb8094753b435fe1a3ab570843af65fb2044be",
        "data_bindings": {
            "learning/plans/07-02-cantilever-geometry-draft-v001.json": {
                "snapshot": "source-snapshot/geometry-plan-v001.json",
                "sha256": "f4f0fab02a47eaade189c3b1c6cb8094753b435fe1a3ab570843af65fb2044be"},
            "learning/evidence/07/2026-10-25-lesson07-parameters-demo-v001/parameter-record-v001.json": {
                "snapshot": "source-snapshot/parameter-source-v001.json",
                "sha256": "57d411f24486aad351056854b8eb427aae853b99f290372c9d0294d367ac6ead"},
            "sources/engineering/snapfit-source-facts-v001.json": {
                "snapshot": "source-snapshot/snapfit-source-facts-v001.json",
                "sha256": "291d1704ea12834969e74e79b948cf2677524fda7a852fa8434c017a674169f8"},
        },
        "authorization": "依使用者要求延續獨立 Blender 的卡扣建模示範與原始實拍、讀值及版本紀錄。新增尺寸由助教選為幾何草案，材料與允許應變仍待定，沒有強度、裝配行程或配合合格判定。",
        "summaries": {"07-02": "助教在獨立 Blender 以 07-01 固定原盒參考副本，實際擠出 anchor、直臂與扣鉤，精確選邊 Bevel，再 Union 入盒體；另做一體蓋板、蓋裙及承接凸緣。原盒核心 60 × 40 × 30 mm 保留，含外掛 anchor 的 Body 為 60 × 44.5 × 30；新蓋板 60 × 46 × 2。根部 offset 與實際三段圓角擬合值、19 mm 根部至承接面長度與21 mm全臂高度分別讀取。另存重開並核對靜態間距；直臂空隙與根部局部空隙不是可用撓度。所有尺寸仍是助教幾何草案，材料、ε、δ_req、允許撓度及裝拆力未定，未匯出、切片、列印或試配。"},
        "content_review_summary": "已核對固定 07-01 場景及空白參數紀錄、新幾何草案、來源及工具／成品世界網格、實際原生 Bevel 與所選邊、另存重開和靜態組裝。保留材料與所有力學／實體結果的空值；不把倒扣、投影重疊或未變形空隙當作裝配所需或材料允許撓度。",
        "completion_scope": "07-02 卡扣／配合蓋的實驗幾何建模、Bevel、靜態擺位及另存重開；材料、力學估算、接觸／裝配路徑、STL、切片、列印與試配尚未完成",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4, "declaredParametersAbsToleranceMm": 1e-6,
                               "volumeRelativeTolerance": 1e-5,
                               "purpose": "僅處理實際網格、斜面／圓角與靜態距離的浮點讀回，不是製造公差、允許撓度或強度／配合合格門檻。"},
        "geometry_evidence_files": ["source_body_mesh.json", "snap_tool_mesh.json", "body_mesh.json", "flange_tool_mesh.json", "lid_mesh.json"],
        "data_evidence_files": ["geometry-draft-record-v001.json", "bevel-operations.json", "selected-root-hook-edges.json", "operand-attempts.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson07-parameters-demo-v001": {
        "lesson": "07",
        "journal": "learning/journal/2026-10-25-lesson07-parameters-demo-v001.md",
        "authorization": "依使用者要求，以獨立 Blender 的真實操作、實拍、讀值及版本紀錄接續 07-01 參數定義與估算條件；材料及允許應變未定，不建立卡扣臂、不代入數值或作強度與配合判定。",
        "source_scene_sha256": "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530",
        "data_bindings": {
            "learning/plans/07-01-cantilever-parameters-v001.json": {
                "snapshot": "source-snapshot/parameter-template-v001.json",
                "sha256": "11d4ac441bb213c3f1b14aeecdb35f581cfcf7398a55ad0142a8f37972c74e36"},
            "sources/engineering/snapfit-source-facts-v001.json": {
                "snapshot": "source-snapshot/snapfit-source-facts-v001.json",
                "sha256": "291d1704ea12834969e74e79b948cf2677524fda7a852fa8434c017a674169f8"},
        },
        "summaries": {
            "07-01": "助教在獨立 Blender 開啟原 04 盒體副本，實際選取盒口環面、內底與外底，讀回壁／底厚參考，核對非空封閉盒體未改，再另存並重開原盒參考場景。參數表區分倒扣 u、所需撓度 δ_req 與允許撓度 δ_allow，綁定原廠公式的核對紀錄；材料、允許應變與卡扣參數仍待定。原盒壁厚 2 mm 不是卡扣臂厚。本次只完成參數與估算條件，不建卡扣臂、不代入公式，不宣稱強度或實體配合合格。",
        },
        "content_review_summary": "已核對固定原盒、讀取副本、兩份世界座標網格、三個實選面的角點與跨度、另存重開，以及固定參數模板和原廠來源核對紀錄。保留材料、ε_allow、Q、卡扣幾何與所有估算／實體結果的空值；原冊 0.67 與古典 2/3 係數分開說明，不以數位盒體檢查推定卡扣已建模或合格。",
        "completion_scope": "07-01 參數定義、來源與估算條件及未修改原盒參考版本；卡扣建模、數值估算、強度、匯出、切片、列印和試配尚未執行",
        "numeric_comparison": {"meshReadbackAbsToleranceMm": 1e-4,
                               "purpose": "僅處理原盒網格與實選面座標的浮點讀回；不是製造公差、材料允許應變或強度／配合驗收門檻。"},
        "geometry_evidence_files": ["source_body_mesh.json", "reference_body_mesh.json"],
        "data_evidence_files": ["parameter-record-v001.json", "face-measurements.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson06-dovetail-export-demo-v001": {
        "lesson": "06",
        "journal": "learning/journal/2026-10-25-lesson06-dovetail-export-demo-v001.md",
        "authorization": "依使用者要求接續獨立 Blender 工程教學，逐步實際匯出燕尾盒 Body 與 SlidingLid 的 STL，保存原圖、數位讀回與檔案版本；本次不包含定位榫 STL、切片、列印或實體試配。",
        "source_scene_sha256": "b7da592c4b080163566cb6e1a90390832eae6db8421fbf7be23bfb9071ae0c3e",
        "summaries": {
            "06-03": "助教在獨立 Blender 從 06-02 固定場景副本，分別只選 Body／SlidingLid 匯出首次版本 STL，排除三組隱藏建構工具。解析實檔及其燕尾剖面，再於空白毫米場景實際重新匯入兩件、核對尺寸、世界座標與組裝間距。原來源與副本未改寫，未保存新場景。0.4 mm 水平總差／每側 0.2 mm 仍是幾何試驗，與實際法向間距分開。本次只完成燕尾兩件的 STL 匯出與數位核對；定位榫 STL、Overhang 介面分析、切片、列印與試配未做，沒有合格間隙。",
        },
        "content_review_summary": "已核對固定 06-02 場景與副本、只選單件的匯出選項、兩份二進位 STL 實檔、四份來源／重匯入世界座標網格及腳本快照。STL 按毫米解讀並保留原座標，尚未核對落床方向；來源、STL 與實際重新匯入的燕尾剖面及名義擺位分別驗證，不將數位讀回推成列印或實體配合合格。",
        "completion_scope": "06-03 燕尾 Body／SlidingLid 的 STL 匯出與數位讀回部分；定位榫 STL、Overhang 介面分析、切片、列印、實測及試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "volumeRelativeTolerance": 1e-5,
            "purpose": "僅處理 STL 與 CAD 世界座標網格、斜面間距及體積的浮點重建誤差；不是製造公差或實體配合合格門檻。",
        },
        "geometry_evidence_files": ["source_body_mesh.json", "source_lid_mesh.json", "reimport_body_mesh.json", "reimport_lid_mesh.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson06-dovetail-demo-v001": {
        "lesson": "06",
        "journal": "learning/journal/2026-10-25-lesson06-dovetail-demo-v001.md",
        "authorization": "使用者要求接續獨立 Blender 工程教學的逐步實拍、讀值與版本紀錄。本次從第四單元原盒另做燕尾槽與滑蓋幾何分支；水平總差 0.4 mm／每側 0.2 mm 為助教選用的幾何試驗值，不是實體合格間隙。",
        "source_scene_sha256": "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530",
        "summaries": {
            "06-02": "助教在獨立 Blender 從原 60 × 40 × 30 mm 通用盒建立兩側燕尾導槽與滑蓋，分別核對建構工具及 Boolean 後的實際剖面、斜面間距、入口與 X 位移 0／30／62 mm 的數位擺位，再移回原位另存並重開。名義水平總差 0.4 mm／每側 0.2 mm 與斜面法向實際間距分開記錄。本次只完成幾何示範；Overhang 介面分析、STL 匯出、切片、列印及試配未執行，沒有合格間隙。",
        },
        "content_review_summary": "已核對第四單元固定原盒與讀取副本、世界座標網格、腳本快照、新場景版本及重開。斜面水平間距與法向間距、工具完整剖面與材料邊界裁切後的剖面分別記錄；0／30／62 mm 為數位擺位核對，不等於實體滑動或配合合格。Overhang 畫面分析尚未執行，不宣稱已標出懸空區域或選定支撐策略。",
        "completion_scope": "06-02 燕尾剖面、滑蓋數位擺位與另存重開；Overhang 介面分析、STL、切片、列印、實測與試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "volumeRelativeTolerance": 1e-5,
            "purpose": "僅處理世界座標網格、斜面間距及體積的浮點重建誤差；不是製造公差、斜面合格間隙或列印支撐判定門檻。",
        },
        "geometry_evidence_files": ["source_body_mesh.json", "guide_tool_mesh.json", "groove_tool_mesh.json", "male_tool_mesh.json",
                                    "body_mesh.json", "lid_mesh.json", "travel_30_lid_mesh.json", "travel_62_lid_mesh.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson06-tenon-demo-v001": {
        "lesson": "06",
        "journal": "learning/journal/2026-10-25-lesson06-tenon-demo-v001.md",
        "authorization": "使用者要求延續獨立 Blender 的工程結構逐步實拍與紀錄。本次以既有盒蓋場景製作單柱與定位穿孔，只驗證數位幾何；0.4 mm 名義直徑總間隙／0.2 mm 名義徑向間隙為助教選用的試驗值，並非合格尺寸。",
        "source_scene_sha256": "ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff",
        "summaries": {
            "06-01": "助教在獨立 Blender 以 05-05 原盒蓋快照製作單一定位柱與蓋板穿孔，保留 32 邊形實際相位與數位間距讀值。盒殼仍高 30 mm，含柱的 Body 整高 31.5 mm；上蓋整高 6 mm、蓋板厚 2 mm。另存新場景並重開核對原來源不變、兩件最終網格與名義擺位。0.4 mm 直徑總量／0.2 mm 徑向間隙只是幾何試驗，與多邊形最小間距分別記錄；尚未匯出 STL、切片、列印或試配，沒有合格間隙。",
        },
        "content_review_summary": "已核對固定來源與副本雜湊、建構工具讀值、另存重開、最終網格與腳本快照。Body 原殼高 30 mm，含柱整高 31.5 mm；建構柱嵌入盒底的部分與 Union 後可讀的外露柱側壁分開記錄。從最終世界座標網格重算 32 邊形柱／孔及最小間距，只描述數位幾何，未作實體合格判定或學員完成確認。",
        "completion_scope": "06-01 單柱與定位穿孔數位幾何示範；STL 匯出、切片、列印、實測與試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "volumeRelativeTolerance": 1e-5,
            "purpose": "僅處理世界座標網格、多邊形間距與體積的浮點重建誤差；不是製造公差或列印配合合格門檻。",
        },
        "geometry_evidence_files": ["body_mesh.json", "lid_mesh.json", "pin_tool_mesh.json", "hole_tool_mesh.json"],
        "snapshot_manifest": "source-snapshot/manifest.json",
        "guide_edits": [],
    },
    "2026-10-25-lesson05-lid-export-demo-v001": {
        "lesson": "05",
        "journal": "learning/journal/2026-10-25-lesson05-lid-export-demo-v001.md",
        "authorization": "依使用者要求延續工程教學，以獨立 Blender 逐步操作、實拍、讀值及保留版本；本次只完成 05-06 的蓋子 STL 匯出與 CAD 重新匯入讀回，切片、列印及試配尚未執行。",
        "source_scene_sha256": "ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff",
        "summaries": {
            "05-06": "助教在獨立 Blender 只選 Lid 匯出 u05_lid_v001.stl，核對原場景與讀取快照雜湊，再解析 STL 的尺寸、封閉拓樸、蓋板與中空定位環幾何，重新匯入 Blender 讀回。STL 保留 world Z 11～17 mm：整高 6 mm，蓋板厚 2 mm。本次只完成 STL 匯出與 CAD 讀回；尚未切片、列印或試配，0.4 mm 總間隙／0.2 mm 單邊仍是幾何試驗值，沒有合格間隙。",
        },
        "content_review_summary": "已核對既有蓋子場景、讀取快照與 STL 雜湊、STL 實檔中空定位環與蓋板、world Z 11～17 mm，及 Blender 重新匯入後的網格讀值。只完成數位匯出與 CAD 讀回；尚未做切片、列印、實測或試配，不推定 0.4 mm 試驗總間隙合格，也不更新學員完成度。",
        "completion_scope": "05-06 蓋子 STL 匯出與 CAD 讀回；切片、列印、實測與試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "volumeRelativeTolerance": 1e-5,
            "volumeAbsToleranceMm3": 1e-3,
            "purpose": "僅處理 STL 與 CAD 網格的浮點重建及讀回誤差；不是製造公差、配合間隙或列印試配合格門檻。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson05-lid-demo-v001": {
        "lesson": "05",
        "journal": "learning/journal/2026-10-22-lesson05-lid-demo-v001.md",
        "authorization": "使用者允許延續獨立 Blender 的逐步實拍與幾何試驗。助教從既有試驗點選 0.4 mm 總間隙／0.2 mm 單邊作本次蓋子幾何示範；此數值不是使用者指定的合格間隙，尚未列印或試配。",
        "source_scene_sha256": "b918ee87d26e289f4c8a2f6633beceb854c7d0511e3eddcc969a0696afcd2530",
        "summaries": {
            "05-05": "助教以獨立 Blender 讀取第四單元已保存的通用盒快照，製作一體蓋子：蓋板 60 × 40 × 2 mm，定位環外形 55.6 × 35.6 mm、環壁 2 mm、伸入盒內 4 mm。整個蓋子高 6 mm，蓋板本身厚 2 mm。0.4 mm 總間隙／0.2 mm 單邊是助教選用的幾何試驗值；另存並重開後核對盒身與蓋子網格，尚未列印或試配，沒有已驗證的合格間隙。",
        },
        "content_review_summary": "已核對原盒檢查點與讀取快照雜湊、盒身／蓋子的實際網格、另存與重開結果。蓋板厚 2 mm；包含定位環的整體高度為 6 mm。本次只驗證數位幾何，0.4 mm 總間隙／0.2 mm 單邊仍是試驗值，不代表列印或裝配合格，也不更新學員完成度。",
        "completion_scope": "05-05 蓋子數位幾何示範；切片、列印、實測與試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "volumeRelativeTolerance": 1e-5,
            "volumeAbsToleranceMm3": 1e-3,
            "purpose": "僅處理數位網格浮點重建與讀回誤差；不是製造公差、配合間隙或列印試配合格門檻。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson05-export-demo-v001": {
        "lesson": "05",
        "journal": "learning/journal/2026-10-22-lesson05-export-demo-v001.md",
        "authorization": "依使用者要求延續工程教學，以獨立 Blender 逐步操作、實拍、讀值及保留版本；本次只完成 05-04 的 STL 匯出部分，切片、列印與試配待後續實作。",
        "summaries": {
            "05-04": "助教以獨立 Blender 讀取已驗證的插銷及六孔板場景快照，逐一只選 FitPin／Plate，透過 File > Export > STL 匯出並核對檔案、尺寸與拓樸。孔板的隱藏 Cutters 未匯出。本次只完成 05-04 的 STL 匯出部分；尚未切片、列印或試配，0.1～0.6 mm 總間隙仍是試驗點，沒有已驗證的合格值。",
        },
        "content_review_summary": "已核對插銷與孔板的原場景、讀取快照及 STL 雜湊，以及匯出後尺寸與拓樸讀值。本次只完成 STL 匯出示範；切片、實際列印、實測與試配均未完成，不由數位檢查推定合格間隙或學員完成。",
        "completion_scope": "05-04 STL 匯出部分；切片、列印、實測與試配尚未完成",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "purpose": "僅處理 STL 浮點重建與網格讀回誤差；不是製造公差、配合間隙或列印試配合格門檻。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson05-holes-demo-v001": {
        "lesson": "05",
        "journal": "learning/journal/2026-10-22-lesson05-holes-demo-v001.md",
        "authorization": "使用者要求：「請繼續做 05-03 孔板示範，先用草案的 0.1～0.6 mm 總間隙作為試驗點，沿用獨立 Blender 逐步操作、實拍與讀值，做好檔案版本紀錄並更新網頁，不要把試驗值當成已驗證的合格間隙。」",
        "summaries": {
            "05-03": "助教在獨立 Blender 製作 96 × 26 × 4 mm 孔板，對 10 mm 名義插銷設置 0.1～0.6 mm 總間隙試驗點（孔寬 10.1～10.6 mm），逐一讀回實際網格、檢查六個穿孔與識別標記，另存並重開示範場景。這些是草案試驗值；尚未列印、試配，沒有已驗證的合格間隙。",
        },
        "content_review_summary": "助教已在獨立 Blender 逐一實際操作並截圖，尺寸與孔板幾何由實際網格讀回；數位幾何檢查不等於列印或配合驗證，0.1～0.6 mm 總間隙只作試驗點，尚無合格值。這是示範，不代表你已完成。",
        "numeric_comparison": {
            "meshReadbackAbsToleranceMm": 1e-4,
            "declaredParametersAbsToleranceMm": 1e-6,
            "purpose": "僅處理網格世界座標的單精度浮點讀回誤差；此數值比較門檻不是製造公差、不是配合間隙，也不是合格判定。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson05-demo-v001": {
        "lesson": "05",
        "journal": "learning/journal/2026-10-22-lesson05-demo-v001.md",
        "authorization": "使用者要求：「先瀏覽claude的作業內容，以及如何操作，延續他後面的內容」。",
        "summaries": {
            "05-02": "助教在獨立 Blender 實作 10 × 10 × 8 mm 方形插銷，Apply Scale 後另存示範檔並重新開啟核對尺寸、Scale 與封閉網格；印表機條件與正式配合間隙仍待定。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson01-demo-v001": {
        "lesson": "01",
        "journal": "learning/journal/2026-10-22-lesson01-demo-v001.md",
        "authorization": "使用者要求：「可以麻煩你幫我做教學內容的精細操作與紀錄結果嗎?」並指出原內容只有口頭描述位置、沒有實際呈現圖。",
        "summaries": {
            "01-03": "助教在獨立 Blender 實際核對預設場景（Camera／Cube／Light、Object Mode），並展開 File > New 子選單示範 General 的位置；沒有新建場景。",
            "01-04": "實際操作 File > Save As…：存檔視窗填入你的單元 01 練習資料夾與 u01_basics_v001.blend 後按 Esc 取消，你的工作區保持空白；同名示範檔另存到助教示範資料夾，底部出現 Saved 訊息。",
            "01-05": "實際展開模式選單核對 Object Mode，點空白處取消選取，再單擊 Cube；每次都讀回選取與作用中物件。",
            "01-06": "實際拖曳導覽軸旋轉視角（Cube 數值不變）、拖曳手形圖示平移到看不到 Cube，再用 Outliner 與 View > Frame Selected 找回，最後用滾輪縮小。",
            "01-07": "實際用 View > Sidebar 開側欄，在 Location X 輸入 0.5，再用 Edit > Undo 撤回；讀回的 Location X 由 0.5 m 回到 0 m。",
            "01-08": "實際在 Sidebar 的 Dimensions X 輸入 3：讀回 Dimensions 為 (3, 2, 2) m，Scale X 自動變成 1.5。",
            "01-09": "實際用 File > Save 存 v002（底部出現 Saved），再用 File > Open… 重新開啟；讀回的 Scale 與 Dimensions 與存檔前相同。所用檔案是助教示範檔。",
        },
        # 依實際操作補上確切路徑；只改說明，不改步驟目標與完成條件。
        "guide_edits": [
            ("01-03", 0, "do", "啟動畫面可選 New File 的 General；", "啟動畫面可選 New File 的 General，或用 File > New > General；"),
            ("01-06", 2, "do", "若看不到 Cube，先以 Outliner 選取並回報目前畫面，再用對焦引導找回。",
             "若看不到 Cube，先在 Outliner 點 Cube，再用 3D Viewport 的 View > Frame Selected 找回；畫面太近時，滑鼠放在 3D Viewport 內把滾輪往後滾縮小。"),
            ("01-07", 1, "do", "如果找不到 Item 側欄，先回報畫面。",
             "右側沒有 Item 側欄時，用 3D Viewport 的 View > Sidebar 打開（滑鼠在 3D Viewport 內按 N 也可以）。"),
        ],
    },
    "2026-10-22-lesson02-demo-v001": {
        "lesson": "02",
        "journal": "learning/journal/2026-10-22-lesson02-03-demo-v001.md",
        "authorization": "使用者要求：「照第一單元的方式，繼續做第二、三單元的實作示範與截圖紀錄。」",
        "summaries": {
            "02-01": "從 General 預設場景開始，用 Object > Delete 刪除預設 Cube（Camera、Light 留給第三單元）；存檔視窗填入你的單元 02 練習資料夾與 u02_station_v001.blend 後取消，示範檔另存到助教資料夾。",
            "02-02": "實際用 Add > Mesh > Plane 建地面，在 Sidebar 輸入 Dimensions 4、4；再用 Add > Mesh > Cube 建平台，輸入 2.4、2.4、0.2 與 Location Z 0.1。讀回平台底面 Z 0 m、頂面 0.2 m。",
            "02-03": "實際新增基座（0.7 × 0.7 × 0.3 m、Z 0.35）、立柱（0.12 × 0.12 × 1.2 m、Z 1.1）與 UV Sphere 訊號球（直徑 0.5 m、Z 1.95）；讀回每件的底面正好接在下一件的頂面（0.2、0.5、1.7 m）。",
            "02-04": "拖曳邊界加高 Outliner，用 Edit > Rename Active Item 改名為 BeaconBase、Platform、Ground、Post、Signal；選取五個部件後按 M > New Collection 建立 Station；存檔視窗示範 u02_station_v002.blend。",
            "02-05": "File > New > General 開新檔並示範另存 u02_mm_block_v001.blend；在 Scene 分頁的 Units 把 Length 改成 Millimeters、Unit Scale 維持 1，讀回同一個 Cube 顯示 2000 mm，實際大小沒變。",
            "02-06": "實際在 Dimensions 依序輸入 40mm、30mm、10mm：讀回 40 × 30 × 10 mm，Scale 變成 0.02、0.015、0.005；再用 Frame Selected 與滾輪看清方塊。",
            "02-07": "File > Save 保存毫米方塊，再用 File > Open… 分別重新開啟訊號站 v002 與毫米方塊；讀回 Station Collection、平台尺寸與 40 × 30 × 10 mm 都和存檔前相同。",
        },
        "guide_edits": [
            ("02-01", 1, "do", "只移除已確認不需保留的預設物件。",
             "只移除已確認不需保留的預設物件（例如在 Outliner 點 Cube，再用 3D Viewport 的 Object > Delete；Camera 與 Light 留給第三單元）。"),
            ("02-02", 0, "do", "本回合先建立 Plane 地面，", "本回合先用 3D Viewport 的 Add > Mesh > Plane 建立地面，在 Sidebar（View > Sidebar）把 "),
            ("02-02", 1, "do", "再建立 Cube 平台，", "再用 Add > Mesh > Cube 建立平台，"),
            ("02-04", 0, "do", "先把基座名稱改為 BeaconBase，",
             "在 Outliner 點基座，用 Edit > Rename Active Item（F2）把名稱改為 BeaconBase，"),
            ("02-04", 1, "do", "下個小回合建立 Station Collection，將已建立的訊號站部件整理進去。",
             "下個小回合在 Outliner 點第一個部件、Ctrl+點其餘部件，滑鼠移到 3D Viewport 按 M > New Collection，命名為 Station。"),
            ("02-05", 1, "do", "下一小回合將 Unit System 設為 Metric、Length 設為 Millimeters。",
             "下一小回合在 Properties 的 Scene 分頁展開 Units，確認 Unit System 為 Metric，把 Length 改為 Millimeters。"),
            ("02-06", 0, "do", "本回合先輸入 40 mm，只改 X。", "本回合在 Sidebar 的 Dimensions X 輸入 40mm（帶單位），只改 X。"),
        ],
    },
    "2026-10-22-lesson04-demo-v001": {
        "lesson": "04",
        "journal": "learning/journal/2026-10-22-lesson04-demo-v001.md",
        "authorization": "使用者要求：「草案方向可以，未定的項目先標待定。請寫進課程，並從第 04 單元可實拍的步驟開始示範。」",
        "summaries": {
            "04-02": "實際用 File > New > General 開新檔，在 Scene 分頁 Units 把 Length 改 Millimeters、Unit Scale 輸入 0.001：讀回預設 Cube 為 2 mm。存檔視窗填入你的單元 04 練習資料夾與 u04_box_v001.blend 後取消，示範檔另存到助教資料夾。",
            "04-03": "在 Sidebar 的 Dimensions 輸入 60mm、40mm、30mm，讀回 Scale 變成 30、20、15；用 Object > Apply > Scale 後 Scale 回到 1，Dimensions 不變。",
            "04-04": "Tab 進 Edit Mode、按 3 面選取、Select > None 後點頂面（讀回選取 1 個面、Median Z 15 mm），再用 Mesh > Delete > Faces：網格剩 5 個面，開口邊緣有 4 條不封閉的邊。",
            "04-05": "Tab 回 Object Mode，Modifier 分頁 Add Modifier > Generate > Solidify：預設厚度只有 0.01 mm。Thickness 輸入 2mm（示範值）並勾 Even Thickness：讀回外形仍 60 × 40 × 30 mm、內腔 56 × 36 mm、底厚 2 mm。",
            "04-06": "用 Solidify 的下拉選單 Apply；Edit Mode 切邊選取、Select > None，再 Select > Select All by Trait > Non Manifold：讀回 0 條不封閉的邊。實測面選取模式下沒有 Non Manifold 選項。",
            "04-07": "File > Save 後開 File > Export > STL (.stl)：匯出視窗填入單元 04 的 exports 與 u04_box_v001.stl，確認 Scale 1、Scene Unit 不勾後取消；示範 STL 另存到助教資料夾，直接解析檔案讀回 60 × 40 × 30（切片軟體以 mm 讀取）。",
        },
        "guide_edits": [],
    },
    "2026-10-22-lesson03-demo-v001": {
        "lesson": "03",
        "journal": "learning/journal/2026-10-22-lesson02-03-demo-v001.md",
        "authorization": "使用者要求：「照第一單元的方式，繼續做第二、三單元的實作示範與截圖紀錄。」",
        "summaries": {
            "03-01": "實際用 File > Open… 開啟第二單元示範的訊號站 v002，記下其 SHA-256；存檔視窗填入你的單元 03 練習資料夾與 u03_render_v001.blend 後取消，示範檔另存到助教資料夾。",
            "03-02": "Outliner 點 Camera，用 View > Cameras > Active Camera 進入相機取景：預設位置下訊號球頂端超出畫框。只改 Location Z（4.96 → 5.3 m），讀回五個部件都在畫框內。",
            "03-03": "Outliner 點 Light、開 Light 分頁，3D Viewport 切到 Rendered 預覽；只把 Power 由 1000 W 改成 2000 W，比較前後亮度。",
            "03-04": "只選 Platform，在 Material 分頁按 New 並改名 Platform_Blue，在 Base Color 的 Hex 輸入 2F6FD8；讀回只有 Platform 有材質，其他部件沒有。",
            "03-05": "Render 分頁確認 EEVEE、Output 分頁把 Resolution % 改成 50（960 × 540 px），先 File > Save 保存場景檢查點並記下 SHA-256，再 Render > Render Image；在渲染視窗用 Image > Save As… 存 PNG。",
            "03-06": "關閉渲染視窗後按 File > Open…，Blender 先問是否儲存變更：核對磁碟上的雜湊和登記時相同後按 Don't Save。重新開啟後相機、燈光、材質與輸出設定都在；再渲染一次另存 repeat.png，逐像素比較兩張完全相同。",
        },
        "guide_edits": [
            ("03-02", 1, "do", "切到相機取景，", "用 View > Cameras > Active Camera 切到相機取景，"),
            ("03-03", 2, "do", "比較亮度與陰影；",
             "3D Viewport 右上把著色切到 Rendered（四個圓形按鈕的最右邊），比較亮度與陰影；"),
            ("03-04", 1, "do", "建立或指定基本材質，取名 Platform_Blue。",
             "在 Properties 的 Material 分頁按 New 建立材質，點名稱欄位改為 Platform_Blue。"),
            ("03-04", 2, "do", "只改成容易分辨的藍色，",
             "點 Base Color 色塊，在顏色選擇器的 Hex 欄輸入藍色（示範用 2F6FD8），"),
            ("03-06", 0, "do", "重新開啟已登記的渲染場景，先核對路徑與版本。",
             "關閉渲染視窗後用 File > Open… 重新開啟已登記的渲染場景，先核對路徑與版本。若跳出 Save changes before closing?，"
             "先確認場景沒有再改：已登記的檢查點不要按 Save 覆寫，按 Don't Save；不確定就按 Cancel 並回報。"),
        ],
    },
}

# v001 保留第一次失敗的真實證據；v002 是修正數值驗證後的新執行版本。
# 固定列出這個接續版本，不接受未核對的任意 run_id。
RUNS["2026-10-22-lesson05-demo-v002"] = copy.deepcopy(RUNS["2026-10-22-lesson05-demo-v001"])
RUNS["2026-10-22-lesson05-demo-v002"]["journal"] = "learning/journal/2026-10-22-lesson05-demo-v002.md"
RUNS["2026-10-22-lesson05-holes-demo-v002"] = copy.deepcopy(RUNS["2026-10-22-lesson05-holes-demo-v001"])
RUNS["2026-10-22-lesson05-holes-demo-v002"]["journal"] = "learning/journal/2026-10-22-lesson05-holes-demo-v002.md"
RUNS["2026-10-22-lesson05-export-demo-v002"] = copy.deepcopy(RUNS["2026-10-22-lesson05-export-demo-v001"])
RUNS["2026-10-22-lesson05-export-demo-v002"]["journal"] = "learning/journal/2026-10-22-lesson05-export-demo-v002.md"
RUNS["2026-10-22-lesson05-export-demo-v003"] = copy.deepcopy(RUNS["2026-10-22-lesson05-export-demo-v001"])
RUNS["2026-10-22-lesson05-export-demo-v003"]["journal"] = "learning/journal/2026-10-22-lesson05-export-demo-v003.md"
RUNS["2026-10-25-lesson06-tenon-demo-v002"] = copy.deepcopy(RUNS["2026-10-25-lesson06-tenon-demo-v001"])
RUNS["2026-10-25-lesson06-tenon-demo-v002"]["journal"] = "learning/journal/2026-10-25-lesson06-tenon-demo-v002.md"
RUNS["2026-10-25-lesson06-tenon-demo-v003"] = copy.deepcopy(RUNS["2026-10-25-lesson06-tenon-demo-v001"])
RUNS["2026-10-25-lesson06-tenon-demo-v003"]["journal"] = "learning/journal/2026-10-25-lesson06-tenon-demo-v003.md"
RUNS["2026-10-25-lesson06-tenon-demo-v004"] = copy.deepcopy(RUNS["2026-10-25-lesson06-tenon-demo-v001"])
RUNS["2026-10-25-lesson06-tenon-demo-v004"]["journal"] = "learning/journal/2026-10-25-lesson06-tenon-demo-v004.md"
RUNS["2026-10-25-lesson06-tenon-demo-v005"] = copy.deepcopy(RUNS["2026-10-25-lesson06-tenon-demo-v001"])
RUNS["2026-10-25-lesson06-tenon-demo-v005"]["journal"] = "learning/journal/2026-10-25-lesson06-tenon-demo-v005.md"
RUNS["2026-10-25-lesson06-tenon-demo-v006"] = copy.deepcopy(RUNS["2026-10-25-lesson06-tenon-demo-v001"])
RUNS["2026-10-25-lesson06-tenon-demo-v006"]["journal"] = "learning/journal/2026-10-25-lesson06-tenon-demo-v006.md"
RUNS["2026-10-25-lesson06-dovetail-demo-v002"] = copy.deepcopy(RUNS["2026-10-25-lesson06-dovetail-demo-v001"])
RUNS["2026-10-25-lesson06-dovetail-demo-v002"]["journal"] = "learning/journal/2026-10-25-lesson06-dovetail-demo-v002.md"


class ImportValidationError(ValueError):
    """證據不完整或不相符；匯入前拒絕，不更新 catalog。"""


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ImportValidationError("無法讀取 %s：%s" % (path.name, exc)) from exc


def _contained_file(path, root, label):
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ImportValidationError("%s 不存在或不在指定證據資料夾內：%s" % (label, path)) from exc
    if not resolved.is_file():
        raise ImportValidationError("%s 不是檔案：%s" % (label, path))
    return resolved


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_records(run, run_dir, spec, lesson_steps):
    records = run.get("records")
    if not isinstance(records, list) or not records:
        raise ImportValidationError("run.json 必須含至少一筆操作紀錄")
    if run.get("errors"):
        raise ImportValidationError("run.json 含錯誤，不匯入")
    for record in records:
        if not isinstance(record, dict) or "error" in record:
            raise ImportValidationError("run.json 含錯誤操作，不匯入")
        if record.get("step") not in spec["summaries"] or record.get("step") not in lesson_steps:
            raise ImportValidationError("操作步驟不在本次劇本與本課 catalog：%s" % record.get("step"))
        for key in ("file", "action", "observed", "recordedAt", "sha256"):
            if not isinstance(record.get(key), str) or not record[key]:
                raise ImportValidationError("操作紀錄缺少有效 %s" % key)
        name = Path(record["file"])
        if name.is_absolute() or name.suffix.lower() != ".png":
            raise ImportValidationError("截圖必須是 run 資料夾內的相對 PNG 路徑")
        path = _contained_file(run_dir / name, run_dir, "截圖")
        data = path.read_bytes()
        if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[8:16] != b"\x00\x00\x00\rIHDR":
            raise ImportValidationError("截圖不是有效 PNG：%s" % name)
        width, height = struct.unpack(">II", data[16:24])
        if (type(record.get("width")) is not int or type(record.get("height")) is not int
                or width < 1 or height < 1 or (width, height) != (record["width"], record["height"])):
            raise ImportValidationError("截圖尺寸不符：%s" % name)
        if hashlib.sha256(data).hexdigest() != record["sha256"].lower():
            raise ImportValidationError("截圖 SHA-256 不符：%s" % name)
        if not isinstance(record.get("highlights", []), list):
            raise ImportValidationError("截圖 highlights 必須是清單")
    for key in ("blender", "buildHash", "scenario"):
        if not isinstance(run.get(key), str) or not run[key]:
            raise ImportValidationError("run.json 缺少實際環境欄位：%s" % key)


def _numeric_equal(actual, expected):
    """只處理浮點讀回誤差；這不是製造公差或配合合格值。"""
    return (isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and math.isfinite(actual) and math.isclose(actual, expected, rel_tol=0, abs_tol=1e-6))


def _mesh_numeric_equal(actual, expected):
    """孔板世界座標網格的浮點誤差比較門檻；不是製造公差。"""
    return (isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and math.isfinite(actual) and math.isclose(actual, expected, rel_tol=0, abs_tol=1e-4))


def _validate_lesson05(run, run_dir):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    for field in ("passed", "closed_volume", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("插銷驗證未通過：%s" % field)
    for field, expected in (("dimensions_mm", (10, 10, 8)), ("scale", (1, 1, 1))):
        values = verification.get(field)
        if (not isinstance(values, list) or len(values) != 3
                or not all(_numeric_equal(value, target) for value, target in zip(values, expected))):
            raise ImportValidationError("插銷驗證數值不符：%s" % field)
    if not _numeric_equal(verification.get("unit_scale"), 0.001) or verification.get("length_unit") != "MILLIMETERS":
        raise ImportValidationError("插銷驗證單位不符")
    if type(verification.get("non_manifold_edges")) is not int or verification["non_manifold_edges"] != 0:
        raise ImportValidationError("插銷網格未通過 Non Manifold 檢查")
    if verification.get("errors"):
        raise ImportValidationError("verification.json 含錯誤")
    if not isinstance(verification.get("scene_path"), str) or not verification["scene_path"]:
        raise ImportValidationError("verification.json 缺少場景路徑")
    scene = Path(verification["scene_path"])
    if not scene.is_absolute():
        scene = run_dir / scene
    scene = _contained_file(scene, run_dir / "demo-files", "示範場景")
    if scene.name != "u05_fit_coupon_v001.blend" or not scene.stat().st_size:
        raise ImportValidationError("示範場景名稱或內容不符")
    if _digest(scene) != verification.get("scene_sha256"):
        raise ImportValidationError("示範場景 SHA-256 不符")

    return verification, _validate_runner(run, run_dir, "lesson05")


def _validate_runner(run, run_dir, scenario):
    runner = _read_json(run_dir / "runner-status.json")
    if not isinstance(runner, dict):
        raise ImportValidationError("runner-status.json 必須是物件")
    if runner.get("status") != "completed" or type(runner.get("blenderExitCode")) is not int or runner["blenderExitCode"] != 0:
        raise ImportValidationError("獨立 Blender runner 未成功完成")
    if runner.get("workspacesUnchanged") is not True or runner.get("runErrors") != []:
        raise ImportValidationError("runner 工作區檢查失敗或含執行錯誤")
    if runner.get("scenario") != scenario or Path(run["scenario"].replace("\\", "/")).stem != scenario:
        raise ImportValidationError("runner 劇本不符")
    if not isinstance(runner.get("outputDir"), str) or Path(runner["outputDir"]).resolve() != run_dir.resolve():
        raise ImportValidationError("runner 輸出資料夾不符")
    for key in ("startedAt", "endedAt"):
        if not isinstance(runner.get(key), str) or not runner[key]:
            raise ImportValidationError("runner 缺少執行時間：%s" % key)
    return runner


def _validate_lesson05_holes(run, run_dir):
    """檢查孔板的數位幾何證據；passed 不代表列印或配合合格。"""
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("kind") != "hole_plate":
        raise ImportValidationError("孔板驗證類型不符")
    for field in ("passed", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("孔板數位幾何驗證未通過：%s" % field)
    # 三個欄位都需明示，避免漏填被誤解為已驗證的製造間隙。
    for field in ("printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("孔板尚未實際列印或試配：%s 必須為 false" % field)
    if "qualified_clearance_mm" not in verification or verification["qualified_clearance_mm"] is not None:
        raise ImportValidationError("孔板試驗點不得標為已驗證的合格間隙")
    if verification.get("errors"):
        raise ImportValidationError("verification.json 含錯誤")

    for field, expected, equal in (("board_dimensions_mm", (96, 26, 4), _mesh_numeric_equal),
                                   ("trial_total_clearances_mm", (0.1, 0.2, 0.3, 0.4, 0.5, 0.6), _numeric_equal)):
        values = verification.get(field)
        if (not isinstance(values, list) or len(values) != len(expected)
                or not all(equal(value, target) for value, target in zip(values, expected))):
            raise ImportValidationError("孔板驗證數值不符：%s" % field)
    if not _numeric_equal(verification.get("pin_nominal_mm"), 10):
        raise ImportValidationError("孔板參照插銷名義尺寸不符")
    measured = verification.get("measured_hole_widths_mm")
    if (not isinstance(measured, list) or len(measured) != 6
            or any(not isinstance(pair, list) or len(pair) != 2
                   or not all(_mesh_numeric_equal(value, 10 + (index + 1) / 10) for value in pair)
                   for index, pair in enumerate(measured))):
        raise ImportValidationError("實際網格讀回的六孔寬度不符草案試驗點")
    for field, expected in (("non_manifold_edges", 0), ("through_holes", 6)):
        if type(verification.get(field)) is not int or verification[field] != expected:
            raise ImportValidationError("孔板幾何檢查不符：%s" % field)
    markers = verification.get("marker_counts")
    if (not isinstance(markers, list) or len(markers) != 6
            or any(type(value) is not int or value != index + 1 for index, value in enumerate(markers))):
        raise ImportValidationError("孔板識別標記不符 1～6")

    if not isinstance(verification.get("scene_path"), str) or not verification["scene_path"]:
        raise ImportValidationError("verification.json 缺少場景路徑")
    scene = Path(verification["scene_path"])
    if not scene.is_absolute():
        scene = run_dir / scene
    scene = _contained_file(scene, run_dir / "demo-files", "示範孔板場景")
    if scene.name != "u05_hole_plate_v001.blend" or not scene.stat().st_size:
        raise ImportValidationError("示範孔板場景名稱或內容不符")
    if _digest(scene) != verification.get("scene_sha256"):
        raise ImportValidationError("示範孔板場景 SHA-256 不符")
    return verification, _validate_runner(run, run_dir, "lesson05_holes")


def _read_binary_stl(path):
    """由實檔重算尺寸、封閉邊、連通體、genus 與體積，不依賴旁記宣告。"""
    data = path.read_bytes()
    if len(data) < 84:
        raise ImportValidationError("STL 檔案太短")
    triangles = struct.unpack_from("<I", data, 80)[0]
    if triangles < 1 or len(data) != 84 + 50 * triangles:
        raise ImportValidationError("STL triangle count 或二進位檔案長度不符")
    vertices, faces, edges, volumes = {}, [], {}, []
    for index in range(triangles):
        values = struct.unpack_from("<9f", data, 84 + 50 * index + 12)
        if not all(math.isfinite(value) for value in values):
            raise ImportValidationError("STL 含非有限座標")
        points = [tuple(values[offset:offset + 3]) for offset in (0, 3, 6)]
        ids = []
        for point in points:
            if point not in vertices:
                vertices[point] = len(vertices)
            ids.append(vertices[point])
        if len(set(ids)) != 3:
            raise ImportValidationError("STL 含退化三角面")
        faces.append(ids)
        for a, b in ((ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[0])):
            edges.setdefault(tuple(sorted((a, b))), []).append(index)
        a, b, c = points
        volumes.append((a[0] * (b[1] * c[2] - b[2] * c[1]) +
                        a[1] * (b[2] * c[0] - b[0] * c[2]) +
                        a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0)

    neighbours = [set() for _ in faces]
    for face_ids in edges.values():
        for index in face_ids:
            neighbours[index].update(other for other in face_ids if other != index)
    pending = set(range(len(faces)))
    shells = 0
    while pending:
        shells += 1
        stack = [pending.pop()]
        while stack:
            for other in neighbours[stack.pop()]:
                if other in pending:
                    pending.remove(other)
                    stack.append(other)
    non_manifold = sum(len(face_ids) != 2 for face_ids in edges.values())
    euler = len(vertices) - len(edges) + len(faces)
    genus = (2 * shells - euler) / 2
    dimensions = [max(v[axis] for v in vertices) - min(v[axis] for v in vertices) for axis in range(3)]
    return {"bytes": len(data), "triangles": triangles, "dimensions_mm": dimensions,
            "non_manifold_edges": non_manifold, "connected_shells": shells,
            "genus": genus, "volume_mm3": math.fsum(volumes)}


def _validate_lesson05_export(run, run_dir):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("passed") is not True or verification.get("kind") != "fit_coupon_stl_exports":
        raise ImportValidationError("STL 匯出驗證未通過或類型不符")
    if verification.get("errors"):
        raise ImportValidationError("STL 匯出 verification.json 含錯誤")
    for field in ("printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("匯出部分不可宣稱已列印或試配：%s" % field)
    for field in ("qualified_clearance_mm", "physical_measurements", "fit_results"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("STL 匯出不得填入未取得的實體合格證據：%s" % field)
    trials = verification.get("trial_total_clearances_mm")
    if (not isinstance(trials, list) or len(trials) != 6
            or not all(_numeric_equal(value, index / 10) for index, value in enumerate(trials, 1))):
        raise ImportValidationError("STL 試驗點總間隙不符 0.1～0.6 mm")
    numeric = verification.get("numericComparison")
    if not isinstance(numeric, dict) or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]:
        raise ImportValidationError("STL 驗證缺少浮點比較用途說明")
    exports = verification.get("exports")
    if not isinstance(exports, list) or len(exports) != 2 or any(not isinstance(item, dict) for item in exports):
        raise ImportValidationError("STL 驗證必須含插銷與孔板兩項匯出")
    if sorted(item.get("kind", "") for item in exports) != ["hole_plate", "pin"]:
        raise ImportValidationError("STL 匯出種類必須各有一份 pin 與 hole_plate")
    project = run_dir.resolve().parents[3]
    source_specs = {
        "pin": ("2026-10-22-lesson05-demo-v002", "u05_fit_coupon_v001", "FitPin", (10, 10, 8), 0),
        "hole_plate": ("2026-10-22-lesson05-holes-demo-v002", "u05_hole_plate_v001", "Plate", (96, 26, 4), 6),
    }
    for entry in exports:
        source_run, filename, obj, dimensions, genus = source_specs[entry["kind"]]
        source_dir = project / "learning" / "evidence" / "05" / source_run
        expected_source = source_dir / "demo-files" / (filename + ".blend")
        for field in ("source_scene_path", "opened_scene_path", "stl_path"):
            if not isinstance(entry.get(field), str) or not Path(entry[field]).is_absolute():
                raise ImportValidationError("匯出路徑必須是絕對路徑：%s" % field)
        source = _contained_file(Path(entry["source_scene_path"]), source_dir / "demo-files", "原場景")
        if source != expected_source.resolve() or entry.get("source_object") != obj:
            raise ImportValidationError("STL 原場景或選取物件不符已驗證來源")
        source_verification = _read_json(source_dir / "verification.json")
        if (not isinstance(source_verification, dict) or source_verification.get("passed") is not True
                or _digest(source) != source_verification.get("scene_sha256")
                or entry.get("source_scene_sha256") != source_verification.get("scene_sha256")):
            raise ImportValidationError("原場景雜湊與先前已驗證的檢查點不符")
        opened = _contained_file(Path(entry["opened_scene_path"]), run_dir / "demo-files" / "sources", "場景讀取快照")
        if (opened.name != filename + ".blend" or _digest(opened) != entry.get("source_scene_sha256")
                or entry.get("opened_scene_sha256") != entry.get("source_scene_sha256")):
            raise ImportValidationError("讀取快照與原場景雜湊不符")
        for field in ("source_unchanged", "opened_copy_unchanged", "only_selected", "apply_modifiers"):
            if entry.get(field) is not True:
                raise ImportValidationError("STL 來源或匯出選項不符：%s" % field)
        if (not _numeric_equal(entry.get("global_scale"), 1.0) or entry.get("use_scene_unit") is not False
                or entry.get("forward_axis") != "Y" or entry.get("up_axis") != "Z"):
            raise ImportValidationError("STL Scale／Scene Unit／座標軸選項不符")
        for field in ("source_dimensions_mm", "stl_dimensions_mm"):
            actual = entry.get(field)
            if (not isinstance(actual, list) or len(actual) != 3
                    or not all(_mesh_numeric_equal(value, target) for value, target in zip(actual, dimensions))):
                raise ImportValidationError("STL 尺寸不符：%s" % field)
        for field, expected in (("stl_non_manifold_edges", 0), ("stl_connected_shells", 1), ("stl_genus", genus)):
            if type(entry.get(field)) is not int or entry[field] != expected:
                raise ImportValidationError("STL 拓樸檢查不符：%s" % field)
        stl = _contained_file(Path(entry["stl_path"]), run_dir / "demo-files" / "exports", "STL 輸出")
        if stl.name != filename + ".stl" or _digest(stl) != entry.get("stl_sha256"):
            raise ImportValidationError("STL 檔名或 SHA-256 不符")
        actual_stl = _read_binary_stl(stl)
        for field, actual in (("stl_bytes", actual_stl["bytes"]), ("stl_triangles", actual_stl["triangles"]),
                              ("stl_non_manifold_edges", actual_stl["non_manifold_edges"]),
                              ("stl_connected_shells", actual_stl["connected_shells"]), ("stl_genus", actual_stl["genus"])):
            if type(entry.get(field)) is not int or entry[field] != actual:
                raise ImportValidationError("STL 實檔讀回與驗證欄位不符：%s" % field)
        if not all(_mesh_numeric_equal(value, target) for value, target in zip(actual_stl["dimensions_mm"], dimensions)):
            raise ImportValidationError("STL 實檔尺寸與來源不符")
        volume = entry.get("stl_volume_mm3")
        if (not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(volume)
                or volume <= 0 or not math.isclose(volume, actual_stl["volume_mm3"], rel_tol=1e-6, abs_tol=1e-4)):
            raise ImportValidationError("STL 實檔有向體積讀回不符")
    return verification, _validate_runner(run, run_dir, "lesson05_export")


def _validate_body_lid_readbacks(body, lid, lid_name="Lid", lid_is_stl=False):
    """核對來源或重新匯入的名義網格；不推定實體配合。"""
    def vector(record, field, expected, label):
        actual = record.get(field)
        if (not isinstance(actual, list) or len(actual) != len(expected)
                or not all(_mesh_numeric_equal(value, target) for value, target in zip(actual, expected))):
            raise ImportValidationError("%s 網格讀值不符：%s" % (label, field))

    def scalar(record, field, expected, label):
        if not _mesh_numeric_equal(record.get(field), expected):
            raise ImportValidationError("%s 網格讀值不符：%s" % (label, field))

    for label, record, obj_name, volume in (("body", body, "Body", 15552.0), ("lid", lid, lid_name, 6195.2)):
        if (not isinstance(record, dict) or record.get("passed") is not True
                or record.get("kind") != ("box_body" if label == "body" else "lid")):
            raise ImportValidationError("缺少已識別的盒身或蓋子網格：%s" % label)
        if not (label == "lid" and lid_is_stl):
            if (record.get("object_name") != obj_name if obj_name is not None else
                    not isinstance(record.get("object_name"), str) or not record["object_name"]):
                raise ImportValidationError("缺少已識別的 CAD 網格：%s" % label)
        counts = record.get("mesh_counts")
        if (not isinstance(counts, dict) or any(type(counts.get(field)) is not int or counts[field] <= 0
                                               for field in ("vertices", "edges", "faces", "triangles"))):
            raise ImportValidationError("%s 網格不得為空" % label)
        for field, expected in (("non_manifold_edges", 0), ("non_manifold_vertex_links", 0),
                                ("inconsistent_winding_edges", 0), ("connected_shells", 1),
                                ("euler_characteristic", 2), ("genus", 0)):
            if type(record.get(field)) is not int or record[field] != expected:
                raise ImportValidationError("%s 拓樸檢查不符：%s" % (label, field))
        measured_volume = record.get("volume_mm3")
        if (not isinstance(measured_volume, (int, float)) or isinstance(measured_volume, bool)
                or not math.isfinite(measured_volume)
                or not math.isclose(measured_volume, volume, rel_tol=1e-5, abs_tol=1e-3)):
            raise ImportValidationError("%s 網格體積不符" % label)
        if not (label == "lid" and lid_is_stl):
            vector(record, "scale", (1, 1, 1), label)
            if not _numeric_equal(record.get("unit_scale"), 0.001) or record.get("length_unit") != "MILLIMETERS":
                raise ImportValidationError("%s 網格單位不符" % label)
        for field in ("printed", "fit_tested"):
            if record.get(field) is not False:
                raise ImportValidationError("%s 不得宣稱已實體驗證：%s" % (label, field))
        for field in ("qualified_clearance_mm", "physical_interference"):
            if field not in record or record[field] is not None:
                raise ImportValidationError("%s 不得填入未取得的實體驗證：%s" % (label, field))
    vector(body, "dimensions_mm", (60, 40, 30), "body")
    vector(body, "outer_dimensions_mm", (60, 40, 30), "body")
    vector(body, "cavity_dimensions_mm", (56, 36, 28), "body")
    vector(body, "wall_thicknesses_mm", (2, 2, 2, 2), "body")
    scalar(body, "floor_thickness_mm", 2, "body")
    scalar(body, "rim_z_mm", 15, "body")
    vector(lid, "dimensions_mm", (60, 40, 6), "lid")
    vector(lid, "plate_dimensions_mm", (60, 40, 2), "lid")
    scalar(lid, "plate_thickness_mm", 2, "lid")
    vector(lid, "plate_z_mm", (15, 17), "lid")
    vector(lid, "ring_outer_mm", (55.6, 35.6), "lid")
    vector(lid, "ring_inner_mm", (51.6, 31.6), "lid")
    vector(lid, "ring_z_mm", (11, 15), "lid")
    scalar(lid, "ring_wall_mm", 2, "lid")
    vector(lid, "ring_wall_thicknesses_mm", (2, 2, 2, 2), "lid")
    scalar(lid, "ring_depth_mm", 4, "lid")
    scalar(lid, "engagement_mm", 4, "lid")
    if (lid.get("trial_status") != "experimental_geometry_only"
            or not _numeric_equal(lid.get("trial_total_clearance_mm"), 0.4)
            or not _numeric_equal(lid.get("trial_per_side_clearance_mm"), 0.2)):
        raise ImportValidationError("蓋子網格的試驗狀態或名義間隙不符")
    assembly = lid.get("assembly")
    if (not isinstance(assembly, dict) or assembly.get("geometric_nonintersection") is not True
            or not _numeric_equal(assembly.get("interior_volume_overlap_mm3"), 0)):
        raise ImportValidationError("蓋子未通過名義網格擺位核對")
    vector(assembly, "per_side_clearances_mm", (0.2, 0.2, 0.2, 0.2), "assembly")
    vector(assembly, "total_clearances_mm", (0.4, 0.4), "assembly")
    for field, expected in (("engagement_mm", 4), ("cavity_depth_mm", 28),
                            ("floor_reserve_mm", 24), ("rim_contact_z_mm", 15)):
        scalar(assembly, field, expected, "assembly")
    for field in ("printed", "fit_tested"):
        if assembly.get(field) is not False:
            raise ImportValidationError("名義擺位核對不可宣稱已列印或試配")
    for field in ("qualified_clearance_mm", "physical_interference"):
        if field not in assembly or assembly[field] is not None:
            raise ImportValidationError("名義擺位核對不可填入實體合格結果")


def _validate_lesson05_lid(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("passed") is not True or verification.get("kind") != "lid_geometry_demo":
        raise ImportValidationError("蓋子數位幾何驗證未通過或類型不符")
    if verification.get("errors"):
        raise ImportValidationError("蓋子 verification.json 含錯誤")
    for field in ("reopened", "source_unchanged", "opened_copy_unchanged"):
        if verification.get(field) is not True:
            raise ImportValidationError("蓋子來源或重開驗證不符：%s" % field)
    for field in ("printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("幾何示範不可宣稱已列印或試配：%s" % field)
    for field in ("qualified_clearance_mm", "physical_measurements", "fit_results"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("蓋子不得填入未取得的實體合格證據：%s" % field)
    trial = verification.get("trial")
    if (not isinstance(trial, dict) or trial.get("status") != "experimental_geometry_only"
            or not _numeric_equal(trial.get("total_clearance_mm"), 0.4)
            or not _numeric_equal(trial.get("per_side_clearance_mm"), 0.2)
            or "qualified_clearance_mm" not in trial or trial["qualified_clearance_mm"] is not None):
        raise ImportValidationError("蓋子只接受明示尚未合格的 0.4 mm 總量／0.2 mm 單邊幾何試驗值")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("蓋子驗證缺少正確的浮點比較用途與門檻")

    project = run_dir.resolve().parents[3]
    source_dir = project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files"
    for field in ("source_scene_path", "opened_scene_path", "scene_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("蓋子場景路徑必須是絕對路徑：%s" % field)
    source = _contained_file(Path(verification["source_scene_path"]), source_dir, "原盒檢查點")
    expected_hash = spec["source_scene_sha256"]
    if (source != (source_dir / "u04_box_v001.blend").resolve()
            or _digest(source) != expected_hash or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("原盒與第四單元已保存的固定檢查點不符")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "原盒讀取快照")
    if (opened.name != "u04_box_v001.blend" or _digest(opened) != expected_hash
            or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("原盒讀取快照與固定檢查點雜湊不符")
    scene = _contained_file(Path(verification["scene_path"]), run_dir / "demo-files", "盒身與蓋子場景")
    if (scene != (run_dir / "demo-files" / "u05_lid_v001.blend").resolve()
            or not scene.stat().st_size or _digest(scene) != verification.get("scene_sha256")):
        raise ImportValidationError("盒身與蓋子輸出場景版本或雜湊不符")

    _validate_body_lid_readbacks(verification.get("body"), verification.get("lid"))
    return verification, _validate_runner(run, run_dir, "lesson05_lid")


def _same_numeric_evidence(actual, expected):
    """只比對同一數位模型的浮點重建證據，不判定製造公差。"""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and actual.keys() == expected.keys()
                and all(_same_numeric_evidence(actual[key], value) for key, value in expected.items()))
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_same_numeric_evidence(a, b) for a, b in zip(actual, expected)))
    if type(expected) is int:
        return type(actual) is int and actual == expected
    if isinstance(expected, float):
        return (isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isfinite(actual)
                and math.isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-4))
    return type(actual) is type(expected) and actual == expected


def _validate_lesson05_lid_export(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("passed") is not True or verification.get("kind") != "lid_stl_export":
        raise ImportValidationError("蓋子 STL 匯出驗證未通過或類型不符")
    if verification.get("errors"):
        raise ImportValidationError("蓋子 STL 匯出 verification.json 含錯誤")
    for field in ("source_unchanged", "opened_copy_unchanged", "only_selected", "apply_modifiers", "reimport_verified"):
        if verification.get(field) is not True:
            raise ImportValidationError("蓋子 STL 來源、匯出選項或 CAD 讀回不符：%s" % field)
    for field in ("use_scene_unit", "ascii_format", "use_batch", "slicer_checked", "printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("蓋子 STL 匯出選項或未完成階段標示不符：%s" % field)
    if (verification.get("source_object") != "Lid" or not _numeric_equal(verification.get("global_scale"), 1)
            or verification.get("forward_axis") != "Y" or verification.get("up_axis") != "Z"):
        raise ImportValidationError("蓋子 STL 必須只匯出 Lid，維持 Scale 1／Y Forward／Z Up")
    for field in ("qualified_clearance_mm", "physical_measurements", "fit_results"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("蓋子 STL 不得填入未取得的實體結果：%s" % field)
    if (verification.get("trial_status") != "experimental_geometry_only"
            or not _numeric_equal(verification.get("trial_total_clearance_mm"), 0.4)
            or not _numeric_equal(verification.get("trial_per_side_clearance_mm"), 0.2)):
        raise ImportValidationError("蓋子 STL 必須保留 0.4 mm 總量／0.2 mm 單邊幾何試驗狀態")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("蓋子 STL 缺少正確的浮點比較門檻與用途說明")

    project = run_dir.resolve().parents[3]
    source_run = project / "learning" / "evidence" / "05" / "2026-10-22-lesson05-lid-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "stl_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("蓋子 STL 場景與輸出路徑必須是絕對路徑：%s" % field)
    source = _contained_file(Path(verification["source_scene_path"]), source_run / "demo-files", "原蓋子場景")
    source_metadata = _read_json(source_run / "verification.json")
    expected_hash = spec["source_scene_sha256"]
    if (source != (source_run / "demo-files" / "u05_lid_v001.blend").resolve()
            or not isinstance(source_metadata, dict) or source_metadata.get("passed") is not True
            or source_metadata.get("kind") != "lid_geometry_demo"
            or source_metadata.get("scene_sha256") != expected_hash
            or Path(source_metadata.get("scene_path", "")).resolve() != source
            or _digest(source) != expected_hash or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("蓋子來源與既有固定檢查點或驗證雜湊不符")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "蓋子讀取快照")
    if (opened != (run_dir / "demo-files" / "sources" / "u05_lid_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("蓋子讀取快照與原固定檢查點不符")
    _validate_body_lid_readbacks(verification.get("source_body"), verification.get("source_lid"))
    _validate_body_lid_readbacks(verification.get("source_body"), verification.get("reimport_lid"), lid_name=None)

    stl = _contained_file(Path(verification["stl_path"]), run_dir / "demo-files" / "exports", "蓋子 STL")
    if (stl != (run_dir / "demo-files" / "exports" / "u05_lid_v001.stl").resolve()
            or _digest(stl) != verification.get("stl_sha256")):
        raise ImportValidationError("蓋子 STL 檔名、位置或雜湊不符")
    actual_binary = _read_binary_stl(stl)
    for field, actual in (("stl_bytes", actual_binary["bytes"]), ("stl_triangles", actual_binary["triangles"]),
                          ("stl_non_manifold_edges", actual_binary["non_manifold_edges"]),
                          ("stl_connected_shells", actual_binary["connected_shells"]), ("stl_genus", actual_binary["genus"])):
        if type(verification.get(field)) is not int or verification[field] != actual:
            raise ImportValidationError("蓋子 STL 實檔拓樸或長度讀回不符：%s" % field)
    dimensions = verification.get("stl_dimensions_mm")
    if (not isinstance(dimensions, list) or len(dimensions) != 3
            or not all(_mesh_numeric_equal(a, b) for a, b in zip(dimensions, (60, 40, 6)))
            or not all(_mesh_numeric_equal(a, b) for a, b in zip(actual_binary["dimensions_mm"], (60, 40, 6)))):
        raise ImportValidationError("蓋子 STL 尺寸不符；蓋板厚 2 mm，含定位環整高 6 mm")
    volume = verification.get("stl_volume_mm3")
    if (not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(volume)
            or not math.isclose(volume, actual_binary["volume_mm3"], rel_tol=1e-5, abs_tol=1e-4)
            or not math.isclose(actual_binary["volume_mm3"], 6195.2, rel_tol=1e-5, abs_tol=1e-4)):
        raise ImportValidationError("蓋子 STL 實檔體積與中空定位環不符")

    # Helper 是純標準函式庫的唯讀 STL／名義幾何檢查，不啟動 Blender。
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from lid_stl_checks import validate_lid_stl
        # 實際劇本只傳量測子集，所以 helper 的來源 path/hash 為 null；
        # 頂層已固定核對來源，這裡仍用舊檢查點的量測值重新計算。
        actual_stl = validate_lid_stl(stl, {"passed": True, "body": source_metadata["body"], "lid": source_metadata["lid"]})
    except (OSError, ValueError, RuntimeError) as exc:
        raise ImportValidationError("蓋子 STL 實際環唇幾何驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    reported_stl = verification.get("stl_verification")
    if not _same_numeric_evidence(reported_stl, actual_stl):
        raise ImportValidationError("蓋子 STL 詳細證據與實檔重新量測不符")
    _validate_body_lid_readbacks(verification.get("source_body"), reported_stl.get("lid_geometry"), lid_is_stl=True)
    return verification, _validate_runner(run, run_dir, "lesson05_lid_export")


def _same_mesh_readback(actual, expected, path=""):
    """06-01 尺寸只用絕對誤差；只有體積欄位允許相對浮點誤差。"""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and actual.keys() == expected.keys()
                and all(_same_mesh_readback(actual[key], value, path + "." + key) for key, value in expected.items()))
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_same_mesh_readback(a, b, path) for a, b in zip(actual, expected)))
    if type(expected) is int:
        return type(actual) is int and actual == expected
    if isinstance(expected, float):
        if not isinstance(actual, (int, float)) or isinstance(actual, bool) or not math.isfinite(actual):
            return False
        if ".numericComparison." in path:
            return math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12)
        relative = 1e-5 if "volume" in path.rsplit(".", 1)[-1].lower() else 0
        return math.isclose(actual, expected, rel_tol=relative, abs_tol=1e-4)
    return type(actual) is type(expected) and actual == expected


def _readback_subset_matches(reported, actual, label):
    """Wrapper 可附 CAD metadata；每個純網格重算欄位仍必須完整相符。"""
    if (not isinstance(reported, dict) or any(key not in reported for key in actual)
            or not _same_mesh_readback({key: reported[key] for key in actual}, actual)):
        raise ImportValidationError("%s 與世界座標網格重新量測不符" % label)


def _validate_script_snapshot(run_dir, source, opened, expected_hash, required):
    folder = run_dir / "source-snapshot"
    manifest = _read_json(folder / "manifest.json")
    if (not isinstance(manifest, dict) or not isinstance(manifest.get("recordedAt"), str)
            or not manifest["recordedAt"] or not isinstance(manifest.get("files"), list) or not manifest["files"]):
        raise ImportValidationError("缺少完整的實際腳本快照 manifest")
    for field, expected in (("sourceScene", source), ("sourceCopy", opened)):
        if (not isinstance(manifest.get(field), str) or not Path(manifest[field]).is_absolute()
                or Path(manifest[field]).resolve() != expected):
            raise ImportValidationError("腳本快照的來源／副本路徑不符")
    if manifest.get("sourceSha256") != expected_hash:
        raise ImportValidationError("腳本快照的固定來源雜湊不符")
    seen = set()
    for item in manifest["files"]:
        if not isinstance(item, dict) or not isinstance(item.get("source"), str) or not isinstance(item.get("snapshot"), str):
            raise ImportValidationError("腳本快照紀錄格式不符")
        name = Path(item["snapshot"])
        src = Path(item["source"])
        if (name.is_absolute() or src.is_absolute() or name.suffix != ".py" or src.suffix != ".py"
                or ".." in name.parts or ".." in src.parts or src.as_posix() in seen
                or not src.as_posix().startswith("learning/tutor/")):
            raise ImportValidationError("腳本快照路徑不符或重複")
        snapshot = _contained_file(run_dir / name, folder, "執行腳本快照")
        if snapshot.name != src.name or _digest(snapshot) != item.get("sha256"):
            raise ImportValidationError("執行腳本快照名稱或雜湊不符")
        seen.add(src.as_posix())
    if not required.issubset(seen):
        raise ImportValidationError("執行腳本快照缺少必要來源")


def _validate_tenon_snapshot(run_dir, source, opened, expected_hash):
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson06_tenon.py", "learning/tutor/scenarios/tenon_checks.py",
                "learning/tutor/scenarios/lid_checks.py", "learning/tutor/scenarios/stl_checks.py"}
    return _validate_script_snapshot(run_dir, source, opened, expected_hash, required)


def _validate_lesson06_tenon(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("passed") is not True or verification.get("kind") != "locating_tenon_geometry_demo":
        raise ImportValidationError("定位榫幾何驗證未通過或類型不符")
    if verification.get("errors"):
        raise ImportValidationError("定位榫 verification.json 含錯誤")
    for field in ("source_unchanged", "opened_copy_unchanged", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("定位榫來源或重開驗證不符：%s" % field)
    if "source_body_geometry_unchanged" in verification and verification["source_body_geometry_unchanged"] is not False:
        raise ImportValidationError("新增定位柱後不可宣稱最終盒身幾何未改變")
    for field in ("exported_stl", "slicer_checked", "printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("定位榫幾何示範不可宣稱已完成後續階段：%s" % field)
    for field in ("physical_measurements", "fit_results", "physical_interference", "qualified_clearance_mm"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("定位榫不可填入未取得的實體結果：%s" % field)
    trial = verification.get("trial")
    if (not isinstance(trial, dict) or trial.get("status") != "experimental_geometry_only"
            or trial.get("selected_by") != "tutor"
            or not _numeric_equal(trial.get("diameter_total_clearance_mm"), 0.4)
            or not _numeric_equal(trial.get("nominal_radial_clearance_mm"), 0.2)
            or "qualified_clearance_mm" not in trial or trial["qualified_clearance_mm"] is not None):
        raise ImportValidationError("定位榫必須保留助教選用的 0.4／0.2 mm 名義幾何試驗狀態")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("volumeRelative"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("定位榫缺少正確的浮點比較門檻與用途")

    project = run_dir.resolve().parents[3]
    source_run = project / "learning" / "evidence" / "05" / "2026-10-22-lesson05-lid-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "scene_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("定位榫場景路徑必須是絕對路徑：%s" % field)
    source = _contained_file(Path(verification["source_scene_path"]), source_run / "demo-files", "原盒蓋檢查點")
    expected_hash = spec["source_scene_sha256"]
    prior = _read_json(source_run / "verification.json")
    if (source != (source_run / "demo-files" / "u05_lid_v001.blend").resolve()
            or not isinstance(prior, dict) or prior.get("passed") is not True or prior.get("kind") != "lid_geometry_demo"
            or not isinstance(prior.get("scene_path"), str) or Path(prior["scene_path"]).resolve() != source
            or prior.get("scene_sha256") != expected_hash or _digest(source) != expected_hash
            or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("定位榫來源與 05-05 固定檢查點不符")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "盒蓋讀取快照")
    if (opened != (run_dir / "demo-files" / "sources" / "u05_lid_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("定位榫讀取副本與原固定檢查點不符")
    _validate_body_lid_readbacks(verification.get("source_body"), verification.get("source_lid"))
    _readback_subset_matches(verification["source_body"], prior.get("body", {}), "改前盒身")
    _readback_subset_matches(verification["source_lid"], prior.get("lid", {}), "改前上蓋")
    scene = _contained_file(Path(verification["scene_path"]), run_dir / "demo-files", "定位榫新場景")
    if (scene != (run_dir / "demo-files" / "u06_locating_tenon_v001.blend").resolve()
            or not scene.stat().st_size or type(verification.get("scene_bytes")) is not int
            or verification["scene_bytes"] != scene.stat().st_size or _digest(scene) != verification.get("scene_sha256")):
        raise ImportValidationError("定位榫新場景的版本、大小或雜湊不符")
    _validate_tenon_snapshot(run_dir, source, opened, expected_hash)

    objects = verification.get("final_objects")
    if not isinstance(objects, dict) or set(objects) != {"Body", "Lid", "TenonTool", "HoleTool"}:
        raise ImportValidationError("定位榫最終場景物件紀錄不符")
    for name, obj in objects.items():
        if (not isinstance(obj, dict) or obj.get("object_name") != name or obj.get("type") != "MESH"
                or type(obj.get("hidden")) is not bool):
            raise ImportValidationError("定位榫最終物件名稱、型態或隱藏狀態不符")
        if name in ("TenonTool", "HoleTool"):
            if obj["hidden"] is not True:
                raise ImportValidationError("定位榫建構工具另存後必須隱藏")
        else:
            scale = obj.get("scale")
            if (obj["hidden"] is not False or type(obj.get("modifier_count")) is not int or obj["modifier_count"] != 0
                    or not isinstance(scale, list) or len(scale) != 3 or not all(_mesh_numeric_equal(value, 1) for value in scale)):
                raise ImportValidationError("最終 Body／Lid 必須可見、Scale 1、修改器已套用")

    dumps = {}
    for role, name, filename in (("body", "Body", "body_mesh.json"), ("lid", "Lid", "lid_mesh.json"),
                                 ("construction_pin", "TenonTool", "pin_tool_mesh.json"),
                                 ("construction_cutter", "HoleTool", "hole_tool_mesh.json")):
        mesh_path = _contained_file(run_dir / filename, run_dir, "世界座標網格證據")
        data = _read_json(mesh_path)
        if (not isinstance(data, dict) or not isinstance(data.get("vertices"), list) or not data["vertices"]
                or not isinstance(data.get("triangles"), list) or not data["triangles"]):
            raise ImportValidationError("定位榫缺少非空的世界座標網格：%s" % role)
        cad = data.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name
                or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not _numeric_equal(cad.get("unit_scale"), 0.001) or cad.get("length_unit") != "MILLIMETERS"
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(value, 1) for value in cad["scale"])):
            raise ImportValidationError("定位榫世界座標網格的 CAD metadata 不符：%s" % role)
        _readback_subset_matches(verification.get(role), cad, "%s CAD metadata" % role)
        dumps[role] = data

    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from tenon_checks import validate_body_pin_mesh, validate_lid_hole_mesh, validate_tenon_assembly, validate_tool_mesh
        actual_pin = validate_tool_mesh(dumps["construction_pin"]["vertices"], dumps["construction_pin"]["triangles"], "pin")
        actual_cutter = validate_tool_mesh(dumps["construction_cutter"]["vertices"], dumps["construction_cutter"]["triangles"], "hole_cutter")
        _readback_subset_matches(verification.get("construction_pin"), actual_pin, "建構柱工具")
        _readback_subset_matches(verification.get("construction_cutter"), actual_cutter, "建構孔工具")
        actual_body = validate_body_pin_mesh(dumps["body"]["vertices"], dumps["body"]["triangles"],
                                              prior["body"], verification.get("construction_pin"))
        actual_lid = validate_lid_hole_mesh(dumps["lid"]["vertices"], dumps["lid"]["triangles"], prior["lid"])
        actual_assembly = validate_tenon_assembly(actual_body, actual_lid)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("定位榫世界座標網格重新驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    _readback_subset_matches(verification.get("body"), actual_body, "最終含柱盒身")
    _readback_subset_matches(verification.get("lid"), actual_lid, "最終穿孔上蓋")
    _readback_subset_matches(verification.get("assembly"), actual_assembly, "定位榫名義擺位")
    return verification, _validate_runner(run, run_dir, "lesson06_tenon")


def _validate_lesson06_dovetail(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if not isinstance(verification, dict):
        raise ImportValidationError("verification.json 必須是物件")
    if verification.get("passed") is not True or verification.get("kind") != "dovetail_slide_geometry_demo":
        raise ImportValidationError("燕尾滑蓋幾何驗證未通過或類型不符")
    if verification.get("errors"):
        raise ImportValidationError("燕尾滑蓋 verification.json 含錯誤")
    for field in ("source_unchanged", "opened_copy_unchanged", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("燕尾滑蓋來源或重開驗證不符：%s" % field)
    if "source_body_geometry_unchanged" in verification and verification["source_body_geometry_unchanged"] is not False:
        raise ImportValidationError("新增導軌與燕尾槽後不可宣稱最終盒身幾何未變")
    for field in ("mesh_analysis_overhang_checked", "exported_stl", "slicer_checked", "printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("燕尾幾何示範不可宣稱已完成待執行階段：%s" % field)
    for field in ("physical_measurements", "fit_results", "physical_interference", "qualified_clearance_mm"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("燕尾滑蓋不可填入未取得的實體結果：%s" % field)
    trial = verification.get("trial")
    if (not isinstance(trial, dict) or trial.get("status") != "experimental_geometry_only"
            or trial.get("selected_by") != "tutor"
            or not _numeric_equal(trial.get("horizontal_total_clearance_mm"), 0.4)
            or not _numeric_equal(trial.get("horizontal_side_clearance_mm"), 0.2)
            or "qualified_clearance_mm" not in trial or trial["qualified_clearance_mm"] is not None):
        raise ImportValidationError("燕尾滑蓋必須保留水平總差 0.4 mm／每側 0.2 mm 的幾何試驗狀態")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("volumeRelative"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("燕尾滑蓋缺少正確的浮點比較門檻與用途")

    project = run_dir.resolve().parents[3]
    source_folder = project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files"
    for field in ("source_scene_path", "opened_scene_path", "scene_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("燕尾滑蓋場景路徑必須是絕對路徑：%s" % field)
    source = _contained_file(Path(verification["source_scene_path"]), source_folder, "原第四單元盒體")
    expected_hash = spec["source_scene_sha256"]
    if (source != (source_folder / "u04_box_v001.blend").resolve()
            or _digest(source) != expected_hash or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("燕尾滑蓋來源與第四單元固定檢查點不符")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "原盒讀取副本")
    if (opened != (run_dir / "demo-files" / "sources" / "u04_box_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("燕尾滑蓋讀取副本與原盒固定雜湊不符")
    scene = _contained_file(Path(verification["scene_path"]), run_dir / "demo-files", "燕尾滑蓋新場景")
    if (scene != (run_dir / "demo-files" / "u06_dovetail_slide_v001.blend").resolve()
            or not scene.stat().st_size or type(verification.get("scene_bytes")) is not int
            or verification["scene_bytes"] != scene.stat().st_size or _digest(scene) != verification.get("scene_sha256")
            or verification.get("scene_sha256") == expected_hash):
        raise ImportValidationError("燕尾滑蓋新場景的版本、大小或雜湊不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson06_dovetail.py", "learning/tutor/scenarios/lid_checks.py",
                "learning/tutor/scenarios/stl_checks.py", "learning/tutor/scenarios/tenon_checks.py",
                "learning/tutor/scenarios/dovetail_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, expected_hash, required)

    objects = verification.get("final_objects")
    expected_objects = {"Body", "SlidingLid", "GuideTool", "GrooveTool", "MaleTool"}
    if not isinstance(objects, dict) or set(objects) != expected_objects:
        raise ImportValidationError("燕尾滑蓋最終物件清單不符")
    for name, obj in objects.items():
        scale = obj.get("scale") if isinstance(obj, dict) else None
        if (not isinstance(obj, dict) or obj.get("object_name") != name or obj.get("type") != "MESH"
                or type(obj.get("hidden")) is not bool or obj["hidden"] != name.endswith("Tool")
                or type(obj.get("modifier_count")) is not int or obj["modifier_count"] != 0
                or not isinstance(scale, list) or len(scale) != 3 or not all(_mesh_numeric_equal(value, 1) for value in scale)):
            raise ImportValidationError("燕尾最終 Body／SlidingLid 須可見，工具須隱藏，Scale 1 且修改器已套用")

    dumps = {}
    roles = (("source_body", "Cube", "source_body_mesh.json"), ("construction_guides", "GuideTool", "guide_tool_mesh.json"),
             ("construction_grooves", "GrooveTool", "groove_tool_mesh.json"), ("construction_males", "MaleTool", "male_tool_mesh.json"),
             ("body", "Body", "body_mesh.json"), ("lid", "SlidingLid", "lid_mesh.json"),
             ("travel_30", "SlidingLid", "travel_30_lid_mesh.json"), ("travel_62", "SlidingLid", "travel_62_lid_mesh.json"))
    for role, name, filename in roles:
        path = _contained_file(run_dir / filename, run_dir, "燕尾世界座標網格")
        data = _read_json(path)
        if (not isinstance(data, dict) or not isinstance(data.get("vertices"), list) or not data["vertices"]
                or not isinstance(data.get("triangles"), list) or not data["triangles"]):
            raise ImportValidationError("燕尾缺少非空世界座標網格：%s" % role)
        cad = data.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name
                or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(value, 1) for value in cad["scale"])
                or not _numeric_equal(cad.get("unit_scale"), 0.001) or cad.get("length_unit") != "MILLIMETERS"
                or not isinstance(cad.get("object_location_mm"), list) or len(cad["object_location_mm"]) != 3
                or not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                           for value in cad["object_location_mm"])):
            raise ImportValidationError("燕尾世界座標網格的 CAD metadata 不符：%s" % role)
        if role == "source_body":
            expected = {key: cad[key] for key in ("object_name", "scale", "unit_scale", "length_unit")}
            _readback_subset_matches(verification.get("source_body"), expected, "改前原盒 CAD metadata")
        dumps[role] = data
    base_location = dumps["lid"]["cad_metadata"]["object_location_mm"]
    for distance in (30, 62):
        moved = dumps["travel_%d" % distance]["cad_metadata"]["object_location_mm"]
        expected = [base_location[0] + distance, base_location[1], base_location[2]]
        if not all(_mesh_numeric_equal(a, b) for a, b in zip(moved, expected)):
            raise ImportValidationError("燕尾移動網格的 CAD 物件位置與實際 X 行程不符")

    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from lid_checks import validate_body_mesh as validate_source_body
        from dovetail_checks import validate_tool_mesh, validate_body_mesh, validate_lid_mesh, validate_assembly, validate_travel
        data = dumps["source_body"]
        measured_source = validate_source_body(data["vertices"], data["triangles"])
        _readback_subset_matches(verification.get("source_body"), measured_source, "改前原盒")
        for role, kind in (("construction_guides", "guide"), ("construction_grooves", "groove"), ("construction_males", "male")):
            data = dumps[role]
            measured = validate_tool_mesh(data["vertices"], data["triangles"], kind)
            _readback_subset_matches(verification.get(role), measured, role)
        measured_body = validate_body_mesh(dumps["body"]["vertices"], dumps["body"]["triangles"])
        measured_lid = validate_lid_mesh(dumps["lid"]["vertices"], dumps["lid"]["triangles"])
        measured_assembly = validate_assembly(measured_body, measured_lid)
        moved = {str(distance): dumps["travel_%d" % distance] for distance in (30, 62)}
        measured_travel = validate_travel(measured_body, measured_lid, moved)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("燕尾世界座標網格重新驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    for role, measured in (("body", measured_body), ("lid", measured_lid), ("assembly", measured_assembly), ("travel", measured_travel)):
        _readback_subset_matches(verification.get(role), measured, role)
    return verification, _validate_runner(run, run_dir, "lesson06_dovetail")


def _validate_lesson06_dovetail_export(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if (not isinstance(verification, dict) or verification.get("passed") is not True
            or verification.get("kind") != "dovetail_stl_exports" or verification.get("errors")):
        raise ImportValidationError("燕尾 STL 匯出驗證未通過或類型不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "reimport_verified", "exported_stl"):
        if verification.get(field) is not True:
            raise ImportValidationError("燕尾 STL 來源或數位讀回狀態不符：%s" % field)
    for field in ("saved_new_scene", "mesh_analysis_overhang_checked", "slicer_checked", "printed", "fit_tested"):
        if verification.get(field) is not False:
            raise ImportValidationError("燕尾 STL 不可宣稱已完成待執行階段：%s" % field)
    for field in ("physical_measurements", "fit_results", "physical_interference", "qualified_clearance_mm"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("燕尾 STL 不得填入未取得的實體結果：%s" % field)
    trial = verification.get("trial")
    if (not isinstance(trial, dict) or trial.get("status") != "experimental_geometry_only"
            or trial.get("selected_by") != "tutor"
            or not _numeric_equal(trial.get("horizontal_total_clearance_mm"), 0.4)
            or not _numeric_equal(trial.get("horizontal_side_clearance_mm"), 0.2)
            or "qualified_clearance_mm" not in trial or trial["qualified_clearance_mm"] is not None):
        raise ImportValidationError("燕尾 STL 必須保留水平總差 0.4／每側 0.2 mm 的幾何試驗狀態")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("volumeRelative"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("燕尾 STL 缺少正確的浮點比較門檻與用途")

    project = run_dir.resolve().parents[3]
    source_dir = project / "learning" / "evidence" / "06" / "2026-10-25-lesson06-dovetail-demo-v002"
    for field in ("source_scene_path", "opened_scene_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("燕尾 STL 來源路徑必須是絕對路徑：%s" % field)
    source = _contained_file(Path(verification["source_scene_path"]), source_dir / "demo-files", "原燕尾場景")
    source_metadata = _read_json(source_dir / "verification.json")
    expected_hash = spec["source_scene_sha256"]
    if (source != (source_dir / "demo-files" / "u06_dovetail_slide_v001.blend").resolve()
            or not isinstance(source_metadata, dict) or source_metadata.get("passed") is not True
            or source_metadata.get("kind") != "dovetail_slide_geometry_demo" or source_metadata.get("reopened") is not True
            or source_metadata.get("scene_sha256") != expected_hash
            or Path(source_metadata.get("scene_path", "")).resolve() != source
            or _digest(source) != expected_hash or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("燕尾 STL 來源與既有 06-02 固定場景不符")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "燕尾讀取副本")
    if (opened != (run_dir / "demo-files" / "sources" / "u06_dovetail_slide_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("燕尾 STL 讀取副本與原固定場景不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson06_dovetail_export.py", "learning/tutor/scenarios/lid_checks.py",
                "learning/tutor/scenarios/stl_checks.py", "learning/tutor/scenarios/tenon_checks.py",
                "learning/tutor/scenarios/dovetail_checks.py", "learning/tutor/scenarios/dovetail_stl_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, expected_hash, required)
    for role in ("body", "lid", "assembly"):
        original = source_metadata.get(role)
        if not isinstance(original, dict) or original.get("passed") is not True:
            raise ImportValidationError("原燕尾固定檢查點缺少完整讀值：%s" % role)
        _readback_subset_matches(verification.get("source_" + role), original, "原燕尾固定讀值 " + role)

    dumps = {}
    for role, name, filename in (("source_body", "Body", "source_body_mesh.json"),
                                 ("source_lid", "SlidingLid", "source_lid_mesh.json"),
                                 ("reimport_body", "Body_STL", "reimport_body_mesh.json"),
                                 ("reimport_lid", "SlidingLid_STL", "reimport_lid_mesh.json")):
        data = _read_json(_contained_file(run_dir / filename, run_dir, "燕尾 STL 世界座標網格"))
        if (not isinstance(data, dict) or not isinstance(data.get("vertices"), list) or not data["vertices"]
                or not isinstance(data.get("triangles"), list) or not data["triangles"]):
            raise ImportValidationError("燕尾 STL 缺少非空網格：%s" % role)
        cad = data.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name
                or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(value, 1) for value in cad["scale"])
                or not _numeric_equal(cad.get("unit_scale"), 0.001) or cad.get("length_unit") != "MILLIMETERS"
                or not isinstance(cad.get("object_location_mm"), list) or len(cad["object_location_mm"]) != 3
                or not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                           for value in cad["object_location_mm"])):
            raise ImportValidationError("燕尾 STL 網格 CAD metadata 不符：%s" % role)
        if role.startswith("reimport_") and not all(_mesh_numeric_equal(value, 0) for value in cad["object_location_mm"]):
            raise ImportValidationError("STL 已烘焙世界座標；重新匯入物件須保留原點 0，不能重套來源 Location")
        dumps[role] = data
    exports = verification.get("exports")
    if (not isinstance(exports, list) or len(exports) != 2 or any(not isinstance(item, dict) for item in exports)
            or sorted(item.get("kind", "") for item in exports) != ["body", "lid"]):
        raise ImportValidationError("燕尾 STL 必須各含一份 body 與 lid")

    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from dovetail_checks import validate_body_mesh, validate_lid_mesh, validate_assembly
        from dovetail_stl_checks import validate_dovetail_stl
        for prefix in ("source", "reimport"):
            raw_body, raw_lid = dumps[prefix + "_body"], dumps[prefix + "_lid"]
            body = validate_body_mesh(raw_body["vertices"], raw_body["triangles"])
            lid = validate_lid_mesh(raw_lid["vertices"], raw_lid["triangles"])
            _readback_subset_matches(verification.get(prefix + "_body"), body, prefix + " body")
            _readback_subset_matches(verification.get(prefix + "_lid"), lid, prefix + " lid")
            _readback_subset_matches(verification.get(prefix + "_assembly"), validate_assembly(body, lid), prefix + " assembly")
        stl_parts = {}
        for entry in exports:
            part = entry["kind"]
            obj_name = "Body" if part == "body" else "SlidingLid"
            reimport_name = "Body_STL" if part == "body" else "SlidingLid_STL"
            filename = "u06_dovetail_%s_v001.stl" % part
            if (entry.get("source_object") != obj_name or entry.get("selected_names") != [obj_name]
                    or entry.get("reimport_object") != reimport_name):
                raise ImportValidationError("燕尾 STL 必須只選單件 Body／SlidingLid，排除隱藏建構工具")
            options = entry.get("export_options")
            expected_options = {"only_selected": True, "global_scale": 1.0, "use_scene_unit": False,
                                "apply_modifiers": True, "forward_axis": "Y", "up_axis": "Z",
                                "ascii_format": False, "use_batch": False}
            if (not isinstance(options, dict) or any(key not in options for key in expected_options)
                    or not all(options[key] is value if isinstance(value, bool) else
                               _numeric_equal(options[key], value) if isinstance(value, (int, float)) else options[key] == value
                               for key, value in expected_options.items())):
                raise ImportValidationError("燕尾 STL 匯出選項須 Selection Only／Scale 1／Scene Unit 關閉／Y Forward／Z Up")
            import_options = entry.get("import_options")
            expected_import = {"global_scale": 1.0, "use_scene_unit": False, "forward_axis": "Y", "up_axis": "Z"}
            if (not isinstance(import_options, dict) or any(key not in import_options for key in expected_import)
                    or not all(import_options[key] is value if isinstance(value, bool) else
                               _numeric_equal(import_options[key], value) if isinstance(value, (int, float)) else import_options[key] == value
                               for key, value in expected_import.items())):
                raise ImportValidationError("燕尾 STL 重新匯入選項不符毫米座標解讀")
            if not isinstance(entry.get("stl_path"), str) or not Path(entry["stl_path"]).is_absolute():
                raise ImportValidationError("燕尾 STL 輸出必須是絕對路徑")
            path = _contained_file(Path(entry["stl_path"]), run_dir / "demo-files" / "exports", "燕尾 STL 輸出")
            if path != (run_dir / "demo-files" / "exports" / filename).resolve() or _digest(path) != entry.get("stl_sha256"):
                raise ImportValidationError("燕尾 STL 檔名、版本或雜湊不符")
            binary = _read_binary_stl(path)
            for field, actual in (("stl_bytes", binary["bytes"]), ("stl_triangles", binary["triangles"]),
                                  ("stl_non_manifold_edges", binary["non_manifold_edges"]),
                                  ("stl_connected_shells", binary["connected_shells"]), ("stl_genus", binary["genus"])):
                if type(entry.get(field)) is not int or entry[field] != actual:
                    raise ImportValidationError("燕尾 STL 實檔大小或拓樸讀值不符：%s" % field)
            dimensions = entry.get("stl_dimensions_mm")
            if (not isinstance(dimensions, list) or len(dimensions) != 3
                    or not all(_mesh_numeric_equal(a, b) for a, b in zip(dimensions, binary["dimensions_mm"]))):
                raise ImportValidationError("燕尾 STL 實檔尺寸讀值不符")
            volume = entry.get("stl_volume_mm3")
            if (not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(volume)
                    or not math.isclose(volume, binary["volume_mm3"], rel_tol=1e-5, abs_tol=1e-4)):
                raise ImportValidationError("燕尾 STL 實檔體積讀值不符")
            actual = validate_dovetail_stl(path, part, source_metadata)
            _readback_subset_matches(entry.get("stl_verification"), actual, part + " STL geometry")
            stl_parts[part] = actual["geometry_readback"]
        _readback_subset_matches(verification.get("stl_assembly"), validate_assembly(stl_parts["body"], stl_parts["lid"]), "STL assembly")
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("燕尾 STL 實檔或重新匯入網格驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    return verification, _validate_runner(run, run_dir, "lesson06_dovetail_export")


def _validate_reference_faces(measurements, raw):
    expected = {
        "rim": [[-30, -20, 15], [30, -20, 15], [28, -18, 15], [-28, -18, 15]],
        "inner_floor": [[-28, -18, -13], [28, -18, -13], [28, 18, -13], [-28, 18, -13]],
        "outer_floor": [[-30, -20, -15], [30, -20, -15], [30, 20, -15], [-30, 20, -15]],
    }
    if not isinstance(measurements, dict) or set(measurements) != set(expected):
        raise ImportValidationError("原盒參考必須含三個實選面")
    for role, corners in expected.items():
        item = measurements[role]
        if (not isinstance(item, dict) or item.get("object_name") != "Body_Reference"
                or type(item.get("selected_face_count")) is not int or item["selected_face_count"] != 1
                or type(item.get("selected_vertex_count")) is not int or item["selected_vertex_count"] != 4):
            raise ImportValidationError("原盒參考必須實選一個四角面：%s" % role)
        points = item.get("vertices_mm")
        if (not isinstance(points, list) or len(points) != 4
                or any(not isinstance(point, list) or len(point) != 3
                       or any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) for c in point)
                       for point in points)):
            raise ImportValidationError("原盒實選面缺少有限世界座標角點：%s" % role)
        same_point = lambda a, b: all(_mesh_numeric_equal(x, y) for x, y in zip(a, b))
        if (any(sum(same_point(point, corner) for point in points) != 1 for corner in corners)
                or any(not any(same_point(point, vertex) for vertex in raw["vertices"]) for point in points)):
            raise ImportValidationError("實選面角點與指定原盒面或實際網格不符：%s" % role)
        bounds = {"min": [min(point[a] for point in points) for a in range(3)],
                  "max": [max(point[a] for point in points) for a in range(3)]}
        spans = [bounds["max"][a] - bounds["min"][a] for a in range(3)]
        if not _same_mesh_readback(item.get("bounds_mm"), bounds) or not _same_mesh_readback(item.get("spans_mm"), spans):
            raise ImportValidationError("實選面 bounds／spans 與角點重算不符：%s" % role)


def _validate_lesson07_parameters(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if (not isinstance(verification, dict) or verification.get("passed") is not True
            or verification.get("kind") != "snapfit_parameter_reference" or verification.get("errors")
            or verification.get("scene_role") != "unmodified_box_reference"):
        raise ImportValidationError("卡扣參數參考驗證未通過或角色不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "source_body_geometry_unchanged", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("原盒參考來源／重開狀態不符：%s" % field)
    for field in ("snap_arm_modeled", "calculations_performed", "strength_analysis_performed", "fit_qualification",
                  "printed", "fit_tested", "slicer_checked", "exported"):
        if verification.get(field) is not False:
            raise ImportValidationError("參數步驟不得宣稱已執行建模、計算或實體階段：%s" % field)
    for field in ("physical_measurements", "fit_results", "qualified_strength_N", "qualified_clearance_mm"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("參數步驟不得填入未取得的合格結果：%s" % field)
    if type(verification.get("non_manifold_selected_edges")) is not int or verification["non_manifold_selected_edges"] != 0:
        raise ImportValidationError("原盒參考 Select Non Manifold 須實際選到零邊")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("原盒面座標缺少浮點比較門檻與用途")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files"
    for field in ("source_scene_path", "opened_scene_path", "scene_path", "parameter_record_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("參數參考路徑須為絕對路徑：%s" % field)
    expected_hash = spec["source_scene_sha256"]
    source = _contained_file(Path(verification["source_scene_path"]), source_dir, "原第四單元盒體")
    if (source != (source_dir / "u04_box_v001.blend").resolve() or _digest(source) != expected_hash
            or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("卡扣參數來源不符固定原盒檢查點")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "原盒讀取副本")
    if (opened != (run_dir / "demo-files" / "sources" / "u04_box_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("原盒讀取副本與固定來源不符")
    scene = _contained_file(Path(verification["scene_path"]), run_dir / "demo-files", "卡扣原盒參考版本")
    if (scene != (run_dir / "demo-files" / "u07_snap_reference_v001.blend").resolve()
            or not scene.stat().st_size or type(verification.get("scene_bytes")) is not int
            or verification["scene_bytes"] != scene.stat().st_size or verification.get("scene_sha256") != _digest(scene)
            or verification["scene_sha256"] == expected_hash):
        raise ImportValidationError("原盒參考場景版本、大小或雜湊不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_parameters.py", "learning/tutor/scenarios/lid_checks.py",
                "learning/tutor/scenarios/tenon_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, expected_hash, required)
    manifest = _read_json(run_dir / "source-snapshot" / "manifest.json")
    bindings = manifest.get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("參數模板與原廠事實核對紀錄的 dataBindings 不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("參數模板／來源核對紀錄的固定版本不符")
        original = _contained_file(project / item["source"], project, "固定參數來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "參數來源資料快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("參數模板／來源核對紀錄與實際快照雜湊不符")
    template = _read_json(run_dir / "source-snapshot" / "parameter-template-v001.json")
    dumps = {}
    for role, name, filename in (("source_body", "Cube", "source_body_mesh.json"),
                                 ("reference_body", "Body_Reference", "reference_body_mesh.json")):
        raw = _read_json(_contained_file(run_dir / filename, run_dir, "原盒世界座標網格"))
        if (not isinstance(raw, dict) or not isinstance(raw.get("vertices"), list) or not raw["vertices"]
                or not isinstance(raw.get("triangles"), list) or not raw["triangles"]):
            raise ImportValidationError("卡扣參考缺少非空原盒網格")
        cad = raw.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name
                or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(value, 1) for value in cad["scale"])
                or not _numeric_equal(cad.get("unit_scale"), .001) or cad.get("length_unit") != "MILLIMETERS"):
            raise ImportValidationError("卡扣原盒參考 CAD metadata 不符")
        dumps[role] = raw
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from lid_checks import validate_body_mesh
        for role, raw in dumps.items():
            _readback_subset_matches(verification.get(role), validate_body_mesh(raw["vertices"], raw["triangles"]), role)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("卡扣參考原盒網格驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    _readback_subset_matches(verification["reference_body"], verification["source_body"], "未修改原盒")
    measurements = verification.get("face_measurements")
    _validate_reference_faces(measurements, dumps["reference_body"])
    face_file = _read_json(_contained_file(run_dir / "face-measurements.json", run_dir, "實選面座標紀錄"))
    if not _same_mesh_readback(face_file, measurements):
        raise ImportValidationError("三個實選面檔案與 verification 不符")
    parameter_path = _contained_file(Path(verification["parameter_record_path"]), run_dir, "參數表")
    if (parameter_path != (run_dir / "parameter-record-v001.json").resolve()
            or _digest(parameter_path) != verification.get("parameter_record_sha256")):
        raise ImportValidationError("參數表版本或雜湊不符")
    parameter = _read_json(parameter_path)
    extra_keys = {"recordedAt", "source_scene", "reference_scene", "measured_box", "face_measurements"}
    if (not isinstance(parameter, dict) or set(parameter) != set(template) | extra_keys
            or not isinstance(parameter.get("recordedAt"), str) or not parameter["recordedAt"]
            or json.dumps({key: parameter[key] for key in template}, sort_keys=True, ensure_ascii=False)
            != json.dumps(template, sort_keys=True, ensure_ascii=False)):
        raise ImportValidationError("參數表須完整保留固定模板及所有未定空值，不得代入數字")
    if (parameter["source_scene"] != {"path": str(source), "sha256": expected_hash}
            or parameter["reference_scene"] != {"path": str(scene), "sha256": _digest(scene), "bytes": scene.stat().st_size,
                                                "scene_role": "unmodified_box_reference"}):
        raise ImportValidationError("參數表與來源／原盒參考場景的版本關聯不符")
    _readback_subset_matches(parameter["measured_box"], verification["reference_body"], "參數表原盒量測")
    if not _same_mesh_readback(parameter["face_measurements"], measurements):
        raise ImportValidationError("參數表與實選面座標不符")
    return verification, _validate_runner(run, run_dir, "lesson07_parameters")


def _validate_lesson08_parameters(run, run_dir, spec):
    verification = _read_json(run_dir / "verification.json")
    if (not isinstance(verification, dict) or verification.get("passed") is not True
            or verification.get("kind") != "thread_parameter_reference" or verification.get("errors")
            or verification.get("scene_role") != "unmodified_box_thread_reference"):
        raise ImportValidationError("螺紋參數參考驗證未通過或角色不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "source_body_geometry_unchanged", "reopened"):
        if verification.get(field) is not True:
            raise ImportValidationError("原盒參考來源／重開狀態不符：%s" % field)
    for field in ("thread_modeled", "boss_modeled", "pilot_hole_modeled", "counterpart_modeled", "geometry_modified", "modifier_created", "screw_modifier_created", "calculations_performed", "strength_analysis_performed", "fit_qualification",
                  "printed", "fit_tested", "slicer_checked", "exported", "exported_stl"):
        if verification.get(field) is not False:
            raise ImportValidationError("參數步驟不得宣稱已執行建模、計算或實體階段：%s" % field)
    for field in ("physical_measurements", "fit_results", "physical_interference", "material_grade", "thread_route_selected", "thread_standard_selected", "qualified_strength_N", "qualified_clearance_mm", "qualified_torque_Nm"):
        if field not in verification or verification[field] is not None:
            raise ImportValidationError("參數步驟不得填入未取得的合格結果：%s" % field)
    if type(verification.get("non_manifold_selected_edges")) is not int or verification["non_manifold_selected_edges"] != 0:
        raise ImportValidationError("原盒參考 Select Non Manifold 須實際選到零邊")
    numeric = verification.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("原盒面座標缺少浮點比較門檻與用途")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning" / "evidence" / "04" / "2026-10-22-lesson04-demo-v001" / "demo-files"
    for field in ("source_scene_path", "opened_scene_path", "scene_path", "parameter_record_path"):
        if not isinstance(verification.get(field), str) or not Path(verification[field]).is_absolute():
            raise ImportValidationError("參數參考路徑須為絕對路徑：%s" % field)
    expected_hash = spec["source_scene_sha256"]
    source = _contained_file(Path(verification["source_scene_path"]), source_dir, "原第四單元盒體")
    if (source != (source_dir / "u04_box_v001.blend").resolve() or _digest(source) != expected_hash
            or verification.get("source_scene_sha256") != expected_hash):
        raise ImportValidationError("螺紋參數來源不符固定原盒檢查點")
    opened = _contained_file(Path(verification["opened_scene_path"]), run_dir / "demo-files" / "sources", "原盒讀取副本")
    if (opened != (run_dir / "demo-files" / "sources" / "u04_box_v001.blend").resolve()
            or _digest(opened) != expected_hash or verification.get("opened_scene_sha256") != expected_hash):
        raise ImportValidationError("原盒讀取副本與固定來源不符")
    scene = _contained_file(Path(verification["scene_path"]), run_dir / "demo-files", "螺紋原盒參考版本")
    if (scene != (run_dir / "demo-files" / "u08_thread_reference_v001.blend").resolve()
            or not scene.stat().st_size or type(verification.get("scene_bytes")) is not int
            or verification["scene_bytes"] != scene.stat().st_size or verification.get("scene_sha256") != _digest(scene)
            or verification["scene_sha256"] == expected_hash):
        raise ImportValidationError("原盒參考場景版本、大小或雜湊不符")
    if (set((run_dir / "demo-files").rglob("*.blend")) != {source_path for source_path in (opened, scene)}
            or list((run_dir / "demo-files").rglob("*.stl"))):
        raise ImportValidationError("08-01只可保存原盒讀取副本及新參考場景，不得有螺紋模型或STL")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson08_parameters.py", "learning/tutor/scenarios/lid_checks.py",
                "learning/tutor/scenarios/tenon_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, expected_hash, required)
    manifest = _read_json(run_dir / "source-snapshot" / "manifest.json")
    bindings = manifest.get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("參數模板與原廠事實核對紀錄的 dataBindings 不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("參數模板／來源核對紀錄的固定版本不符")
        original = _contained_file(project / item["source"], project, "固定參數來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "參數來源資料快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("參數模板／來源核對紀錄與實際快照雜湊不符")
    template = _read_json(run_dir / "source-snapshot" / "parameter-template-v001.json")
    for field, relative in (("parameter_template", "learning/plans/08-01-thread-parameters-v001.json"),
                             ("source_facts", "sources/engineering/thread-source-facts-v001.json")):
        path = verification.get(field + "_path")
        expected = spec["data_bindings"][relative]
        if (not isinstance(path, str) or not Path(path).is_absolute() or Path(path).resolve() != (project / relative).resolve()
                or verification.get(field + "_sha256") != expected["sha256"]):
            raise ImportValidationError("螺紋模板／官方事實紀錄路徑與固定hash不符")
    if (not _same_mesh_readback(verification.get("route"), template["route"])
            or not _same_mesh_readback(verification.get("blender_mapping"), template["blender_mapping"])):
        raise ImportValidationError("路線未選、修改器僅文件映射，不能寫成已設定或由學員選定")
    required_slugs = {"rim-face", "inner-floor", "outer-floor", "non-manifold", "saved", "reopened-verified"}
    if not required_slugs <= {r.get("slug") for r in run.get("records", [])}:
        raise ImportValidationError("螺紋參考缺少原生實選面／NM／另存／重開實拍")
    dumps = {}
    for role, name, filename in (("source_body", "Cube", "source_body_mesh.json"),
                                 ("reference_body", "Body_Reference", "reference_body_mesh.json")):
        raw = _read_json(_contained_file(run_dir / filename, run_dir, "原盒世界座標網格"))
        if (not isinstance(raw, dict) or not isinstance(raw.get("vertices"), list) or not raw["vertices"]
                or not isinstance(raw.get("triangles"), list) or not raw["triangles"]):
            raise ImportValidationError("螺紋參考缺少非空原盒網格")
        cad = raw.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name
                or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(value, 1) for value in cad["scale"])
                or not _numeric_equal(cad.get("unit_scale"), .001) or cad.get("length_unit") != "MILLIMETERS"):
            raise ImportValidationError("螺紋原盒參考 CAD metadata 不符")
        identity = [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        if (not _same_mesh_readback(cad.get("matrix_world"), identity)
                or not _same_mesh_readback(cad.get("object_rotation_euler_radians"), [0.,0.,0.])
                or not isinstance(cad.get("mesh_data_name"), str) or not cad["mesh_data_name"]
                or not isinstance(cad.get("local_mesh_sha256"), str) or len(cad["local_mesh_sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in cad["local_mesh_sha256"])):
            raise ImportValidationError("原盒的local mesh與未改世界矩陣／物件旋轉證據不符")
        dumps[role] = raw
    source_raw, reference_raw = dumps["source_body"], dumps["reference_body"]
    if (any(source_raw[field] != reference_raw[field] for field in ("vertices", "triangles"))
            or any(source_raw["cad_metadata"][field] != reference_raw["cad_metadata"][field] for field in
                   ("matrix_world", "scale", "modifier_count", "local_mesh_sha256", "mesh_data_name"))):
        raise ImportValidationError("螺紋參考只可重新命名／另存，原盒完整網格、local mesh與姿態不得修改")
    final = verification.get("final_objects")
    if (not isinstance(final, dict) or set(final) != {"Body_Reference", "Camera", "Light"}
            or any(not isinstance(item, dict) for item in final.values())):
        raise ImportValidationError("08-01場景須只有原盒、Camera與Light，沒有thread／boss／對件")
    for name, kind in (("Body_Reference","MESH"),("Camera","CAMERA"),("Light","LIGHT")):
        item = final[name]
        if (item.get("type") != kind or item.get("hidden") is not (name != "Body_Reference")
                or type(item.get("modifier_count")) is not int or item["modifier_count"] != 0
                or not _same_mesh_readback(item.get("scale"), [1.,1.,1.])):
            raise ImportValidationError("原盒須可見／Scale1／modifier0；Camera與Light只隱藏")
    if not _same_mesh_readback(final["Body_Reference"].get("matrix_world"), reference_raw["cad_metadata"]["matrix_world"]):
        raise ImportValidationError("參考盒inventory與world raw矩陣不符")
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from lid_checks import validate_body_mesh
        for role, raw in dumps.items():
            _readback_subset_matches(verification.get(role), validate_body_mesh(raw["vertices"], raw["triangles"]), role)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("螺紋參考原盒網格驗證失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    _readback_subset_matches(verification["reference_body"], verification["source_body"], "未修改原盒")
    measurements = verification.get("face_measurements")
    _validate_reference_faces(measurements, dumps["reference_body"])
    face_file = _read_json(_contained_file(run_dir / "face-measurements.json", run_dir, "實選面座標紀錄"))
    if not _same_mesh_readback(face_file, measurements):
        raise ImportValidationError("三個實選面檔案與 verification 不符")
    parameter_path = _contained_file(Path(verification["parameter_record_path"]), run_dir, "參數表")
    if (parameter_path != (run_dir / "parameter-record-v001.json").resolve()
            or _digest(parameter_path) != verification.get("parameter_record_sha256")):
        raise ImportValidationError("參數表版本或雜湊不符")
    parameter = _read_json(parameter_path)
    extra_keys = {"recordedAt", "source_scene_readback", "reference_scene", "measured_box", "face_measurements"}
    if (not isinstance(parameter, dict) or set(parameter) != set(template) | extra_keys
            or not isinstance(parameter.get("recordedAt"), str) or not parameter["recordedAt"]
            or json.dumps({key: parameter[key] for key in template}, sort_keys=True, ensure_ascii=False)
            != json.dumps(template, sort_keys=True, ensure_ascii=False)):
        raise ImportValidationError("參數表須完整保留固定模板及所有未定空值，不得代入數字")
    if (parameter["source_scene_readback"] != {"path": str(source), "sha256": expected_hash, "bytes": source.stat().st_size}
            or parameter["reference_scene"] != {"path": str(scene), "sha256": _digest(scene), "bytes": scene.stat().st_size,
                                                "scene_role": "unmodified_box_thread_reference"}):
        raise ImportValidationError("參數表與來源／原盒參考場景的版本關聯不符")
    _readback_subset_matches(parameter["measured_box"], verification["reference_body"], "參數表原盒量測")
    if not _same_mesh_readback(parameter["face_measurements"], measurements):
        raise ImportValidationError("參數表與實選面座標不符")
    return verification, _validate_runner(run, run_dir, "lesson08_parameters")


def _validate_snap_bevel_evidence(verification, run_dir, unit_scale):
    operations = verification.get("bevel_operations")
    if not isinstance(operations, dict) or set(operations) != {"hook", "root"}:
        raise ImportValidationError("卡扣須保存 hook／root 的原生 Bevel 實讀")
    if not _same_mesh_readback(_read_json(run_dir / "bevel-operations.json"), operations):
        raise ImportValidationError("Bevel 操作檔案與 verification 不符")
    for role, amount, segments in (("hook", .8, 1), ("root", .6, 3)):
        item = operations[role]
        if (not isinstance(item, dict) or item.get("operator_id") != "MESH_OT_bevel"
                or item.get("offset_type") != "OFFSET" or item.get("affect") != "EDGES"
                or type(item.get("segments")) is not int or item["segments"] != segments
                or not _numeric_equal(item.get("profile"), .5) or type(item.get("clamp_overlap")) is not bool
                or not _numeric_equal(item.get("offset_mm"), amount)
                or not isinstance(item.get("offset"), (int, float)) or isinstance(item["offset"], bool)
                or not math.isfinite(item["offset"])
                or not _mesh_numeric_equal(item["offset"] * unit_scale * 1000, item["offset_mm"])):
            raise ImportValidationError("實際 Bevel offset／segments／profile 或角色不符：%s" % role)
    edges = _read_json(run_dir / "selected-root-hook-edges.json")
    expected = {"hook": [[[-3, -24.2, 13], [3, -24.2, 13]]],
                "root": [[[-3, -23, -8], [3, -23, -8]], [[-3, -21.4, -8], [3, -21.4, -8]]]}
    if not isinstance(edges, dict) or set(edges) != set(expected):
        raise ImportValidationError("缺少 hook／root 實選邊座標")
    for role, targets in expected.items():
        actual = edges[role]
        if (not isinstance(actual, list) or len(actual) != len(targets)
                or any(not isinstance(edge, list) or len(edge) != 2
                       or any(not isinstance(point, list) or len(point) != 3
                              or any(not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c)
                                     for c in point) for point in edge) for edge in actual)):
            raise ImportValidationError("Bevel 實選邊格式不符")
        used = set()
        for target in targets:
            target = [[float(c) for c in point] for point in target]
            found = [i for i, edge in enumerate(actual) if i not in used
                     and _same_mesh_readback(sorted(edge), sorted(target))]
            if len(found) != 1:
                raise ImportValidationError("Bevel 須選指定鉤頂／兩條凹根部邊")
            used.add(found[0])
    attempts = _read_json(run_dir / "operand-attempts.json")
    pairs = {"Body": "SnapTool", "Lid": "FlangeTool"}
    if not isinstance(attempts, list) or not attempts:
        raise ImportValidationError("卡扣缺少實際 Boolean 指定紀錄")
    for target, tool in pairs.items():
        rows = [row for row in attempts if isinstance(row, dict) and row.get("target") == target]
        if (not rows or any(row.get("tool") != tool or type(row.get("attempt")) is not int for row in rows)
                or [row["attempt"] for row in rows] != list(range(len(rows))) or len(rows) > 3
                or rows[-1].get("operation") != "UNION" or rows[-1].get("operand") != tool
                or rows[-1].get("solver") != "EXACT"):
            raise ImportValidationError("卡扣 Boolean 最後指定須為正確工具的 Union／Exact")
    if any(not isinstance(row, dict) or row.get("target") not in pairs for row in attempts):
        raise ImportValidationError("Boolean 紀錄含非本次建模物件")


def _validate_lesson07_snap(run, run_dir, spec):
    v = _read_json(run_dir / "verification.json")
    if (not isinstance(v, dict) or v.get("passed") is not True or v.get("kind") != "cantilever_snap_geometry_demo"
            or v.get("errors") or v.get("geometry_modified") is not True):
        raise ImportValidationError("卡扣幾何草案驗證未通過或角色不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "reopened"):
        if v.get(field) is not True:
            raise ImportValidationError("卡扣來源／重開驗證不符：%s" % field)
    if "source_body_geometry_unchanged" in v and v["source_body_geometry_unchanged"] is not False:
        raise ImportValidationError("整合外掛卡扣後不可宣稱整個 Body 未修改")
    for field in ("strength_analysis_performed", "fit_qualification", "exported_stl", "slicer_checked", "printed", "fit_tested"):
        if v.get(field) is not False:
            raise ImportValidationError("幾何草案不得宣稱未執行階段已完成：%s" % field)
    for field in ("material_grade", "epsilon_allow", "Q", "delta_allow_mm", "required_deflection_mm", "forces",
                  "physical_measurements", "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm"):
        if field not in v or v[field] is not None:
            raise ImportValidationError("材料／力學／實體結果必須保留 null：%s" % field)
    numeric = v.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("卡扣幾何缺少浮點比較門檻與用途")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning" / "evidence" / "07" / "2026-10-25-lesson07-parameters-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "scene_path", "source_snap_parameter_path", "draft_plan_path", "draft_record_path"):
        if not isinstance(v.get(field), str) or not Path(v[field]).is_absolute():
            raise ImportValidationError("卡扣版本路徑須為絕對路徑：%s" % field)
    source = _contained_file(Path(v["source_scene_path"]), source_dir / "demo-files", "原07-01盒參考場景")
    old = _read_json(source_dir / "verification.json")
    if (source != (source_dir / "demo-files" / "u07_snap_reference_v001.blend").resolve()
            or _digest(source) != spec["source_scene_sha256"] or v.get("source_scene_sha256") != spec["source_scene_sha256"]
            or not isinstance(old, dict) or old.get("passed") is not True or old.get("kind") != "snapfit_parameter_reference"
            or old.get("scene_sha256") != spec["source_scene_sha256"] or Path(old.get("scene_path", "")).resolve() != source
            or old.get("reopened") is not True):
        raise ImportValidationError("卡扣來源不符已保存的07-01固定參考版本")
    parameter = _contained_file(Path(v["source_snap_parameter_path"]), source_dir, "原07-01空白參數紀錄")
    if (parameter != (source_dir / "parameter-record-v001.json").resolve()
            or _digest(parameter) != spec["source_parameter_sha256"]
            or v.get("source_snap_parameter_sha256") != spec["source_parameter_sha256"]
            or old.get("parameter_record_sha256") != spec["source_parameter_sha256"]):
        raise ImportValidationError("原07-01參數紀錄已變更或版本不符")
    opened = _contained_file(Path(v["opened_scene_path"]), run_dir / "demo-files" / "sources", "07-01讀取副本")
    if (opened != (run_dir / "demo-files" / "sources" / "u07_snap_reference_v001.blend").resolve()
            or _digest(opened) != spec["source_scene_sha256"] or v.get("opened_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("卡扣讀取副本與原參考版本不符")
    scene = _contained_file(Path(v["scene_path"]), run_dir / "demo-files", "新卡扣草案版本")
    if (scene != (run_dir / "demo-files" / "u07_cantilever_snap_v001.blend").resolve()
            or not scene.stat().st_size or type(v.get("scene_bytes")) is not int or v["scene_bytes"] != scene.stat().st_size
            or _digest(scene) != v.get("scene_sha256") or v["scene_sha256"] == spec["source_scene_sha256"]):
        raise ImportValidationError("新卡扣場景檔名、大小或雜湊不符")
    draft_path = _contained_file(Path(v["draft_plan_path"]), project / "learning" / "plans", "固定卡扣幾何草案")
    if (draft_path != (project / "learning" / "plans" / "07-02-cantilever-geometry-draft-v001.json").resolve()
            or _digest(draft_path) != spec["draft_plan_sha256"] or v.get("draft_plan_sha256") != spec["draft_plan_sha256"]):
        raise ImportValidationError("固定幾何草案版本不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_snap.py", "learning/tutor/scenarios/lid_checks.py",
                "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/snapfit_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, spec["source_scene_sha256"], required)
    bindings = _read_json(run_dir / "source-snapshot" / "manifest.json").get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("卡扣草案／原參數／事實紀錄的 dataBindings 不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("卡扣資料綁定版本不符")
        original = _contained_file(project / item["source"], project, "卡扣來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "卡扣來源快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("卡扣來源資料／快照雜湊不符")
    if not isinstance(old.get("reference_body"), dict) or old["reference_body"].get("passed") is not True:
        raise ImportValidationError("原07-01缺少已驗證的盒體讀值")
    _readback_subset_matches(v.get("source_body"), old["reference_body"], "原07-01盒體讀值")
    objects = v.get("final_objects")
    if not isinstance(objects, dict) or set(objects) != {"Body", "Lid", "SnapTool", "FlangeTool"}:
        raise ImportValidationError("卡扣最終物件須恰為兩成品與兩隱藏工具")
    for name, item in objects.items():
        if (not isinstance(item, dict) or item.get("object_name") != name or item.get("type") != "MESH"
                or type(item.get("hidden")) is not bool or item["hidden"] != name.endswith("Tool")
                or type(item.get("modifier_count")) is not int or item["modifier_count"] != 0
                or not isinstance(item.get("scale"), list) or len(item["scale"]) != 3
                or not all(_mesh_numeric_equal(x, 1) for x in item["scale"])):
            raise ImportValidationError("卡扣成品／工具可見性、Scale或修改器狀態不符")
    dumps = {}
    for role, name, filename in (("source_body", "Body_Reference", "source_body_mesh.json"),
                                 ("construction_snap", "SnapTool", "snap_tool_mesh.json"), ("body", "Body", "body_mesh.json"),
                                 ("construction_flange", "FlangeTool", "flange_tool_mesh.json"), ("lid", "Lid", "lid_mesh.json")):
        raw = _read_json(_contained_file(run_dir / filename, run_dir, "卡扣世界座標網格"))
        if (not isinstance(raw, dict) or not isinstance(raw.get("vertices"), list) or not raw["vertices"]
                or not isinstance(raw.get("triangles"), list) or not raw["triangles"]):
            raise ImportValidationError("卡扣來源／工具／成品網格不得為空")
        cad = raw.get("cad_metadata")
        if (not isinstance(cad, dict) or cad.get("object_name") != name or cad.get("length_unit") != "MILLIMETERS"
                or not _numeric_equal(cad.get("unit_scale"), .001) or type(cad.get("modifier_count")) is not int
                or cad["modifier_count"] != 0 or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_mesh_numeric_equal(x, 1) for x in cad["scale"])):
            raise ImportValidationError("卡扣世界網格 CAD metadata 不符：%s" % role)
        dumps[role] = raw
    _validate_snap_bevel_evidence(v, run_dir, dumps["source_body"]["cad_metadata"]["unit_scale"])
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from lid_checks import validate_body_mesh as validate_source_body
        from snapfit_checks import validate_tool_mesh, validate_body_mesh, validate_lid_mesh, validate_assembly
        raw = dumps["source_body"]
        source_body = validate_source_body(raw["vertices"], raw["triangles"])
        _readback_subset_matches(v.get("source_body"), source_body, "改前原盒")
        for role, kind in (("construction_snap", "snap"), ("construction_flange", "flange")):
            raw = dumps[role]
            _readback_subset_matches(v.get(role), validate_tool_mesh(raw["vertices"], raw["triangles"], kind), role)
        raw = dumps["body"]
        body = validate_body_mesh(raw["vertices"], raw["triangles"], source_body)
        raw = dumps["lid"]
        lid = validate_lid_mesh(raw["vertices"], raw["triangles"])
        assembly = validate_assembly(body, lid)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        raise ImportValidationError("卡扣實際網格重算失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    for role, actual in (("body", body), ("lid", lid), ("assembly", assembly)):
        _readback_subset_matches(v.get(role), actual, role)
    path = _contained_file(Path(v["draft_record_path"]), run_dir, "幾何草案結果紀錄")
    if path != (run_dir / "geometry-draft-record-v001.json").resolve() or _digest(path) != v.get("draft_record_sha256"):
        raise ImportValidationError("幾何草案結果版本或雜湊不符")
    plan, record = _read_json(draft_path), _read_json(path)
    additions = {"recordedAt", "source_scene", "reference_scene", "geometry_readback"}
    if (not isinstance(record, dict) or set(record) != set(plan) | additions
            or not isinstance(record.get("recordedAt"), str) or not record["recordedAt"]
            or json.dumps({key: record[key] for key in plan}, sort_keys=True, ensure_ascii=False)
            != json.dumps(plan, sort_keys=True, ensure_ascii=False)):
        raise ImportValidationError("幾何草案紀錄須完整保留助教草案、限制與材料／結果空值")
    if (record["source_scene"] != {"path": str(source), "sha256": spec["source_scene_sha256"]}
            or record["reference_scene"] != {"path": str(scene), "sha256": _digest(scene), "bytes": scene.stat().st_size,
                                             "scene_role": "experimental_cantilever_geometry"}):
        raise ImportValidationError("幾何草案紀錄的來源／新版本關聯不符")
    if not _same_mesh_readback(record["geometry_readback"], {"body": v["body"], "lid": v["lid"], "assembly": v["assembly"]}):
        raise ImportValidationError("幾何草案紀錄與實際網格讀值不符")
    return v, _validate_runner(run, run_dir, "lesson07_snap")


def _validate_lesson07_overhang(run, run_dir, spec):
    v = _read_json(run_dir / "verification.json")
    if not isinstance(v, dict) or v.get("passed") is not True or v.get("kind") != "snapfit_print_orientation_demo" or v.get("errors"):
        raise ImportValidationError("列印方向／Overhang 證據未通過或角色不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "source_geometry_draft_unchanged", "reopened",
                  "rigid_geometry_only", "mesh_analysis_overhang_checked"):
        if v.get(field) is not True:
            raise ImportValidationError("方向草案來源／剛體／原生檢查狀態不符：%s" % field)
    for field in ("geometry_modified", "rotation_applied_to_mesh", "strength_analysis_performed", "fit_qualification",
                  "exported_stl", "slicer_checked", "printed", "fit_tested", "support_generation_performed"):
        if v.get(field) is not False:
            raise ImportValidationError("方向草案不得宣稱已改形或完成後續驗證：%s" % field)
    for field in ("material_grade", "epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces",
                  "physical_measurements", "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm",
                  "support_required", "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified"):
        if field not in v or v[field] is not None:
            raise ImportValidationError("方向／支撐／材料與實體結果必須保留 null：%s" % field)
    numeric = v.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("angleBoundaryBandDeg"), 1e-4)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("方向草案缺少浮點重建及角度邊界用途")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning/evidence/07/2026-10-25-lesson07-snap-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "scene_path", "source_geometry_draft_path", "draft_plan_path", "orientation_record_path"):
        if not isinstance(v.get(field), str) or not Path(v[field]).is_absolute():
            raise ImportValidationError("方向草案版本路徑須為絕對路徑：%s" % field)
    source = _contained_file(Path(v["source_scene_path"]), source_dir / "demo-files", "07-02固定卡扣場景")
    old = _read_json(source_dir / "verification.json")
    if (source != (source_dir / "demo-files/u07_cantilever_snap_v001.blend").resolve()
            or _digest(source) != spec["source_scene_sha256"] or v.get("source_scene_sha256") != spec["source_scene_sha256"]
            or not isinstance(old, dict) or old.get("passed") is not True or old.get("kind") != "cantilever_snap_geometry_demo"
            or old.get("reopened") is not True or old.get("scene_sha256") != spec["source_scene_sha256"]
            or Path(old.get("scene_path", "")).resolve() != source):
        raise ImportValidationError("方向草案來源不符已驗證的07-02固定版本")
    geometry_record = _contained_file(Path(v["source_geometry_draft_path"]), source_dir, "07-02原幾何草案紀錄")
    if (geometry_record != (source_dir / "geometry-draft-record-v001.json").resolve()
            or _digest(geometry_record) != spec["source_geometry_sha256"]
            or v.get("source_geometry_draft_sha256") != spec["source_geometry_sha256"]
            or old.get("draft_record_sha256") != spec["source_geometry_sha256"]):
        raise ImportValidationError("原07-02幾何草案紀錄已變更或版本不符")
    old_record = _read_json(geometry_record)
    if (not isinstance(old_record, dict) or not _same_mesh_readback(old_record.get("geometry_readback"),
                                                                {key: old.get(key) for key in ("body", "lid", "assembly")})):
        raise ImportValidationError("07-02原草案紀錄與已驗證場景讀值不符")
    opened = _contained_file(Path(v["opened_scene_path"]), run_dir / "demo-files/sources", "卡扣場景讀取副本")
    if (opened != (run_dir / "demo-files/sources/u07_cantilever_snap_v001.blend").resolve()
            or _digest(opened) != spec["source_scene_sha256"] or v.get("opened_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("方向草案讀取副本與原固定場景不符")
    scene = _contained_file(Path(v["scene_path"]), run_dir / "demo-files", "新方向比較場景")
    if (scene != (run_dir / "demo-files/u07_print_orientation_v001.blend").resolve() or not scene.stat().st_size
            or type(v.get("scene_bytes")) is not int or v["scene_bytes"] != scene.stat().st_size
            or _digest(scene) != v.get("scene_sha256") or v["scene_sha256"] == spec["source_scene_sha256"]):
        raise ImportValidationError("方向比較新場景檔名／大小／雜湊不符")
    plan_path = _contained_file(Path(v["draft_plan_path"]), project / "learning/plans", "固定方向草案")
    if (plan_path != (project / "learning/plans/07-03-print-orientation-draft-v001.json").resolve()
            or _digest(plan_path) != spec["draft_plan_sha256"] or v.get("draft_plan_sha256") != spec["draft_plan_sha256"]):
        raise ImportValidationError("固定方向計畫版本不符")
    plan = _read_json(plan_path)
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_overhang.py", "learning/tutor/scenarios/overhang_checks.py",
                "learning/tutor/scenarios/snapfit_checks.py", "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, spec["source_scene_sha256"], required)
    bindings = _read_json(run_dir / "source-snapshot/manifest.json").get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("方向計畫／來源幾何／原生定義的 dataBindings 不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("方向來源資料綁定版本不符")
        original = _contained_file(project / item["source"], project, "方向來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "方向來源快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("方向來源資料／快照雜湊不符")
    labels = {kind + "_" + pose for kind in ("body", "lid") for pose in ("baseline", "candidate")}
    by_pose, contexts, reported = v.get("analysis_settings_by_pose"), v.get("analysis_contexts"), v.get("poses")
    if any(not isinstance(value, dict) or set(value) != labels for value in (by_pose, contexts, reported)):
        raise ImportValidationError("四姿態的原生設定、上下文與量測須完整")
    settings = v.get("analysis_settings")
    for label in labels:
        native = by_pose[label]
        if (not isinstance(native, dict) or native.get("show_overlays") is not True
                or not _same_mesh_readback(native, settings)):
            raise ImportValidationError("四姿態須各自保留相同且開啟的原生Overlay設定")
        name = "Body" if label.startswith("body_") else "Lid"
        if contexts[label] != {"mode": "EDIT_MESH", "active_object": name, "only_finished_part_visible": name,
                               "source_tools_hidden": True, "native_popover_checked": True}:
            raise ImportValidationError("Overhang必須在正確且單獨可見成品的Edit Mode查核")
    required_slugs = {label + suffix for label in labels for suffix in ("-controls", "-analysis")}
    if not required_slugs <= {r.get("slug") for r in run.get("records", [])}:
        raise ImportValidationError("四姿態缺少原生設定及著色視角的原始實拍")
    if (not _same_mesh_readback(_read_json(run_dir / "analysis-settings-by-pose.json"), by_pose)
            or not _same_mesh_readback(_read_json(run_dir / "pose-verification.json"), reported)):
        raise ImportValidationError("各姿態獨立紀錄與最終verification不符")
    raws = {}
    for label in ("source_body", "source_lid", "body_baseline", "body_candidate", "lid_baseline", "lid_candidate"):
        raw = _read_json(_contained_file(run_dir / (label + "_mesh.json"), run_dir, "原生polygon世界網格"))
        kind = "body" if "body" in label else "lid"
        cad = raw.get("cad_metadata") if isinstance(raw, dict) else None
        if (not isinstance(cad, dict) or cad.get("object_name") != kind.title() or cad.get("length_unit") != "MILLIMETERS"
                or not _numeric_equal(cad.get("unit_scale"), .001) or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3
                or not all(_numeric_equal(x, 1) for x in cad["scale"])):
            raise ImportValidationError("方向網格CAD物件、單位、Scale或modifier不符：%s" % label)
        source_pose = label.startswith("source_")
        rotation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] if source_pose else plan["poses"][label]["world_rotation_rows"]
        matrix, location = cad.get("matrix_world"), cad.get("object_location_mm")
        nominal_location = ([0, 0, 0] if kind == "body" else [0, -3, 16.2]) if source_pose else plan["poses"][label]["object_location_mm_nominal"]
        if (not isinstance(matrix, list) or len(matrix) != 4 or any(not isinstance(row, list) or len(row) != 4 for row in matrix)
                or not isinstance(location, list) or len(location) != 3
                or not all(_mesh_numeric_equal(a, b) for a, b in zip(location, nominal_location))
                or not all(_mesh_numeric_equal(matrix[i][j], rotation[i][j]) for i in range(3) for j in range(3))
                or not all(_mesh_numeric_equal(matrix[i][3], location[i]) for i in range(3))
                or not all(_numeric_equal(a, b) for a, b in zip(matrix[3], (0, 0, 0, 1)))):
            raise ImportValidationError("方向world矩陣／Object Location與固定剛體草案不符：%s" % label)
        radians, degrees = cad.get("object_rotation_euler_radians"), cad.get("object_rotation_euler_degrees")
        wanted = [0, 0, 0] if source_pose else plan["poses"][label]["rotation_degrees"]
        if (not isinstance(radians, list) or not isinstance(degrees, list) or len(radians) != 3 or len(degrees) != 3
                or not all(_mesh_numeric_equal(a, b) for a, b in zip(degrees, wanted))
                or not all(_mesh_numeric_equal(math.degrees(a), b) for a, b in zip(radians, degrees))):
            raise ImportValidationError("Object旋轉須保留原生Euler，不可Apply或改值")
        raws[label] = raw
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from overhang_checks import validate_orientation, validate_layout
        actual = {label: validate_orientation(raws["source_" + label.split("_")[0]], raws[label],
                                             label.split("_")[0], by_pose[label], label.split("_")[1]) for label in labels}
        layout = validate_layout(actual["body_candidate"], actual["lid_candidate"])
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError) as exc:
        raise ImportValidationError("方向／polygon角度與剛體網格重算失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    if not _same_mesh_readback(reported, actual) or not _same_mesh_readback(v.get("layout"), layout):
        raise ImportValidationError("方向／床接觸／離床朝下面統計與實際網格重算不符")
    for kind in ("body", "lid"):
        # The previous body was compared to its ancestor; this pure orientation
        # readback has no ancestor argument. Exclude only that provenance flag.
        expected = {key: value for key, value in old[kind].items() if key != "source_body_metadata_compared"}
        current = actual[kind + "_candidate"]["source_geometry_readback"]
        _readback_subset_matches(current, expected, "固定07-02來源" + kind)
    source_tools, final_tools = v.get("source_tools"), v.get("final_tools")
    if (not isinstance(source_tools, dict) or set(source_tools) != {"SnapTool", "FlangeTool"}
            or source_tools != final_tools or source_tools != _read_json(run_dir / "source-tool-inventory.json")):
        raise ImportValidationError("原隱藏工具必須保留相同local mesh雜湊、transform及隱藏狀態")
    objects = v.get("final_objects")
    if not isinstance(objects, dict) or set(objects) != {"Body", "Lid", "SnapTool", "FlangeTool"}:
        raise ImportValidationError("最終方向場景須恰為兩成品與兩隱藏原工具")
    for name, item in objects.items():
        if (not isinstance(item, dict) or item.get("object_name") != name or item.get("type") != "MESH"
                or type(item.get("hidden")) is not bool or item["hidden"] != name.endswith("Tool")
                or type(item.get("modifier_count")) is not int or item["modifier_count"] != 0
                or not isinstance(item.get("scale"), list) or len(item["scale"]) != 3
                or not all(_numeric_equal(x, 1) for x in item["scale"])):
            raise ImportValidationError("最終成品／工具狀態不符")
        if name.endswith("Tool"):
            tool = source_tools[name]
            digest = tool.get("local_mesh_sha256", "")
            if (tool.get("type") != "MESH" or tool.get("hidden") is not True or tool.get("modifier_count") != 0
                    or tool.get("scale") != [1, 1, 1] or not isinstance(digest, str) or len(digest) != 64
                    or any(c not in "0123456789abcdef" for c in digest)
                    or item.get("location_mm") != tool.get("location")
                    or item.get("rotation_euler_radians") != tool.get("rotation") or item.get("matrix_world") != tool.get("matrix_world")):
                raise ImportValidationError("隱藏工具的原形狀hash或最終transform不符")
        else:
            cad = raws[name.lower() + "_candidate"]["cad_metadata"]
            for field, cad_field in (("location_mm", "object_location_mm"), ("rotation_euler_radians", "object_rotation_euler_radians"), ("matrix_world", "matrix_world")):
                if not _same_mesh_readback(item.get(field), cad[cad_field]):
                    raise ImportValidationError("重開後物件姿態與候選網格不符")
    record_path = _contained_file(Path(v["orientation_record_path"]), run_dir, "方向比較結果紀錄")
    if record_path != (run_dir / "print-orientation-record-v001.json").resolve() or _digest(record_path) != v.get("orientation_record_sha256"):
        raise ImportValidationError("方向比較結果版本或雜湊不符")
    record = _read_json(record_path)
    additions = {"recordedAt", "source_scene", "reference_scene", "analysis_settings", "poses", "layout"}
    if (not isinstance(record, dict) or set(record) != set(plan) | additions
            or not isinstance(record.get("recordedAt"), str) or not record["recordedAt"]
            # The immutable plan retains declared poses. Its record replaces
            # source_scene and poses with resolved provenance and measurements;
            # both replacements are checked independently below.
            or json.dumps({key: record[key] for key in plan if key not in {"source_scene", "poses"}}, sort_keys=True, ensure_ascii=False)
            != json.dumps({key: plan[key] for key in plan if key not in {"source_scene", "poses"}}, sort_keys=True, ensure_ascii=False)
            or record["source_scene"] != {"path": str(source), "sha256": spec["source_scene_sha256"]}
            or record["reference_scene"] != {"path": str(scene), "sha256": _digest(scene), "bytes": scene.stat().st_size,
                                             "scene_role": "print_orientation_comparison_draft"}
            or not _same_mesh_readback({key: record[key] for key in ("analysis_settings", "poses", "layout")},
                                       {key: v[key] for key in ("analysis_settings", "poses", "layout")})):
        raise ImportValidationError("方向紀錄須完整保留草案、待定值及實際場景／姿態讀值")
    return v, _validate_runner(run, run_dir, "lesson07_overhang")


def _validate_snapfit_stl_entry(entry, run_dir, part):
    name = "Body" if part == "body" else "Lid"
    if (entry.get("source_object") != name or entry.get("selected_names") != [name]
            or entry.get("reimport_object") != name + "_STL"):
        raise ImportValidationError("卡扣 STL 須單選 Body／Lid，排除另一成品及隱藏建構工具")
    for field, expected in (
            ("export_options", {"only_selected": True, "global_scale": 1.0, "use_scene_unit": False,
                                "apply_modifiers": True, "forward_axis": "Y", "up_axis": "Z",
                                "ascii_format": False, "use_batch": False, "evaluation_mode": "DAG_EVAL_RENDER"}),
            ("import_options", {"global_scale": 1.0, "use_scene_unit": False, "forward_axis": "Y", "up_axis": "Z"})):
        options = entry.get(field)
        if (not isinstance(options, dict) or any(key not in options for key in expected)
                or not all(options[key] is value if isinstance(value, bool) else
                           _numeric_equal(options[key], value) if isinstance(value, (int, float)) else options[key] == value
                           for key, value in expected.items())):
            raise ImportValidationError("卡扣 STL 選項須 Binary／Selection Only／Scale1／Scene Unit關／Y Forward／Z Up")
    if not isinstance(entry.get("stl_path"), str) or not Path(entry["stl_path"]).is_absolute():
        raise ImportValidationError("卡扣 STL 路徑須為絕對路徑")
    filename = "u07_snap_%s_v001.stl" % part
    path = _contained_file(Path(entry["stl_path"]), run_dir / "demo-files/exports", "卡扣 STL 輸出")
    if path != (run_dir / "demo-files/exports" / filename).resolve() or _digest(path) != entry.get("stl_sha256"):
        raise ImportValidationError("卡扣 STL 檔名／版本／雜湊不符")
    binary = _read_binary_stl(path)
    for field, actual in (("stl_bytes", binary["bytes"]), ("stl_triangles", binary["triangles"]),
                          ("stl_non_manifold_edges", binary["non_manifold_edges"]),
                          ("stl_connected_shells", binary["connected_shells"]), ("stl_genus", binary["genus"])):
        if type(entry.get(field)) is not int or entry[field] != actual:
            raise ImportValidationError("卡扣 STL 實檔長度／拓樸不符：%s" % field)
    dimensions = entry.get("stl_dimensions_mm")
    if (not isinstance(dimensions, list) or len(dimensions) != 3
            or not all(_mesh_numeric_equal(a, b) for a, b in zip(dimensions, binary["dimensions_mm"]))):
        raise ImportValidationError("卡扣 STL 世界外框須從實檔頂點讀回，不能以來源物件軸尺寸替代")
    volume = entry.get("stl_volume_mm3")
    if (not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(volume)
            or not math.isclose(volume, binary["volume_mm3"], rel_tol=1e-5, abs_tol=1e-4)):
        raise ImportValidationError("卡扣 STL 實檔體積不符")
    return path, binary


def _validate_lesson07_snap_export(run, run_dir, spec):
    v = _read_json(run_dir / "verification.json")
    if not isinstance(v, dict) or v.get("passed") is not True or v.get("kind") != "snapfit_stl_exports" or v.get("errors"):
        raise ImportValidationError("卡扣 STL 數位匯出驗證未通過或角色不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "source_orientation_record_unchanged", "reimport_verified", "exported_stl", "source_overhang_comparison_completed"):
        if v.get(field) is not True:
            raise ImportValidationError("卡扣 STL 來源／方向／重匯入狀態不符：%s" % field)
    for field in ("saved_new_scene", "geometry_modified", "rotation_applied_to_mesh", "mesh_analysis_overhang_checked",
                  "strength_analysis_performed", "fit_qualification", "slicer_checked", "printed", "fit_tested", "support_generation_performed"):
        if v.get(field) is not False:
            raise ImportValidationError("卡扣 STL 不可宣稱已改形、重做分析或完成實體階段：%s" % field)
    for field in ("material_grade", "epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces", "physical_measurements",
                  "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm", "support_required",
                  "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified"):
        if field not in v or v[field] is not None:
            raise ImportValidationError("卡扣 STL 仍須保留材料／力學／支撐／實體空值：%s" % field)
    numeric = v.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("coordinateWeldMm"), 1e-5) or not _numeric_equal(numeric.get("volumeRelative"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]
            or not isinstance(v.get("stl_unit_interpretation"), str) or not v["stl_unit_interpretation"]):
        raise ImportValidationError("卡扣 STL 缺少mm座標解讀與浮點用途／門檻")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning/evidence/07/2026-10-25-lesson07-overhang-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "source_orientation_record_path", "export_record_path"):
        if not isinstance(v.get(field), str) or not Path(v[field]).is_absolute():
            raise ImportValidationError("卡扣 STL 來源與結果路徑須為絕對路徑：%s" % field)
    source = _contained_file(Path(v["source_scene_path"]), source_dir / "demo-files", "07-03固定方向場景")
    if (source != (source_dir / "demo-files/u07_print_orientation_v001.blend").resolve()
            or _digest(source) != spec["source_scene_sha256"] or v.get("source_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("卡扣 STL 來源不符07-03固定候選場景")
    opened = _contained_file(Path(v["opened_scene_path"]), run_dir / "demo-files/sources", "卡扣方向讀取副本")
    if (opened != (run_dir / "demo-files/sources/u07_print_orientation_v001.blend").resolve()
            or _digest(opened) != spec["source_scene_sha256"] or v.get("opened_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("卡扣 STL 副本與原候選場景不符")
    if set((run_dir / "demo-files").rglob("*.blend")) != {opened}:
        raise ImportValidationError("本次只能讀取來源blend副本，不得另存新場景")
    orientation_path = _contained_file(Path(v["source_orientation_record_path"]), source_dir, "07-03固定方向紀錄")
    if (orientation_path != (source_dir / "print-orientation-record-v001.json").resolve()
            or _digest(orientation_path) != spec["source_orientation_sha256"]
            or v.get("source_orientation_record_sha256") != spec["source_orientation_sha256"]):
        raise ImportValidationError("卡扣 STL 來源方向紀錄版本不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_snap_export.py", "learning/tutor/scenarios/snapfit_stl_checks.py",
                "learning/tutor/scenarios/overhang_checks.py", "learning/tutor/scenarios/snapfit_checks.py",
                "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py", "learning/tutor/scenarios/stl_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, spec["source_scene_sha256"], required)
    manifest = _read_json(run_dir / "source-snapshot/manifest.json")
    bindings = manifest.get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("卡扣 STL 來源方向／verification／候選網格的dataBindings不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("卡扣 STL 來源資料綁定版本不符")
        original = _contained_file(project / item["source"], project, "固定卡扣方向資料")
        copy = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "卡扣方向資料快照")
        if _digest(original) != expected["sha256"] or _digest(copy) != expected["sha256"]:
            raise ImportValidationError("卡扣方向資料／快照雜湊不符")
    prior = _read_json(source_dir / "verification.json")
    if (prior.get("passed") is not True or prior.get("kind") != "snapfit_print_orientation_demo" or prior.get("reopened") is not True
            or prior.get("scene_sha256") != spec["source_scene_sha256"]
            or prior.get("orientation_record_sha256") != spec["source_orientation_sha256"]):
        raise ImportValidationError("來源必須是已驗證並重開的07-03候選")
    for field in ("body", "lid"):
        if not _same_mesh_readback(v.get("source_" + field), prior["poses"][field + "_candidate"]):
            raise ImportValidationError("來源方向讀值不可換成物件軸尺寸或重新宣稱GPU統計")
    if (not _same_mesh_readback(v.get("source_layout"), prior["layout"])
            or v.get("source_tools") != prior.get("final_tools")):
        raise ImportValidationError("來源擺位或隱藏工具已變更")
    exports = v.get("exports")
    if (not isinstance(exports, list) or len(exports) != 2 or any(not isinstance(x, dict) for x in exports)
            or sorted(x.get("kind", "") for x in exports) != ["body", "lid"]):
        raise ImportValidationError("卡扣 STL 必須恰有body與lid兩件")
    dumps = {}
    for prefix in ("source", "reimport"):
        for part in ("body", "lid"):
            raw = _read_json(_contained_file(run_dir / (prefix + "_" + part + "_mesh.json"), run_dir, "卡扣 STL 世界網格"))
            name = part.title() + ("_STL" if prefix == "reimport" else "")
            cad = raw.get("cad_metadata") if isinstance(raw, dict) else None
            if (not isinstance(raw, dict) or not raw.get("vertices") or not raw.get("triangles")
                    or not isinstance(cad, dict) or cad.get("object_name") != name or cad.get("length_unit") != "MILLIMETERS"
                    or not _numeric_equal(cad.get("unit_scale"), .001) or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                    or not isinstance(cad.get("scale"), list) or len(cad["scale"]) != 3 or not all(_numeric_equal(a, 1) for a in cad["scale"])):
                raise ImportValidationError("來源／重新匯入網格的物件、單位、Scale或modifier不符")
            if prefix == "source":
                original = _read_json(source_dir / (part + "_candidate_mesh.json"))
                if any(raw.get(field) != original[field] for field in ("vertices", "triangles", "polygons", "triangle_polygon_indices", "polygon_normals_world")):
                    raise ImportValidationError("07-03來源候選world網格／polygon法線不得修改")
                if any(cad.get(field) != original["cad_metadata"][field] for field in ("scale", "modifier_count", "object_location_mm", "object_rotation_euler_radians", "matrix_world")):
                    raise ImportValidationError("來源候選物件姿態不得Apply或移動")
                inverse = prior["poses"][part + "_candidate"]["inverse_geometry_readback"]
                if not _same_mesh_readback(cad.get("object_axis_dimensions_mm"), inverse["dimensions_mm"]):
                    raise ImportValidationError("來源Item尺寸須保留物件軸定義")
            else:
                identity = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]
                for field in ("object_location_mm", "object_rotation_euler_radians", "object_rotation_euler_degrees"):
                    if (not isinstance(cad.get(field), list) or len(cad[field]) != 3
                            or not all(_mesh_numeric_equal(a, 0) for a in cad[field])):
                        raise ImportValidationError("STL重匯入的origin／rotation須0，world座標保留於頂點")
                if not _same_mesh_readback(cad.get("matrix_world"), identity):
                    raise ImportValidationError("STL重匯入不得另加剛體transform或scale")
                bounds = {key: [fn(point[a] for point in raw["vertices"]) for a in range(3)] for key, fn in (("min", min), ("max", max))}
                dimensions = [bounds["max"][a] - bounds["min"][a] for a in range(3)]
                if not _same_mesh_readback(cad.get("object_axis_dimensions_mm"), dimensions):
                    raise ImportValidationError("rotation0的重匯入Item尺寸須與world外框一致")
            dumps[prefix + "_" + part] = raw
    def layout(parts):
        values = []
        for part in ("body", "lid"):
            mesh = parts[part]
            bounds = {key: [fn(point[a] for point in mesh["vertices"]) for a in range(3)] for key, fn in (("min", min), ("max", max))}
            values.append({"passed": True, "pose": "candidate", "part_kind": part,
                           "bounds_mm": bounds, "minimum_world_z_mm": bounds["min"][2]})
        return validate_layout(*values)
    scenarios = str(Path(__file__).resolve().parent / "scenarios")
    sys.path.insert(0, scenarios)
    try:
        from overhang_checks import validate_layout
        from snapfit_stl_checks import validate_snapfit_stl, validate_snapfit_export_mesh
        from stl_checks import read_stl
        stl_parts = {}
        for entry in exports:
            part = entry["kind"]
            path, binary = _validate_snapfit_stl_entry(entry, run_dir, part)
            if not _same_mesh_readback(entry.get("stl_bounds_mm"), read_stl(path)["bounds_mm"]):
                raise ImportValidationError("卡扣 STL world bounds與實檔不符")
            if not _same_mesh_readback(entry.get("source_item_dimensions_mm"), dumps["source_" + part]["cad_metadata"]["object_axis_dimensions_mm"]):
                raise ImportValidationError("來源物件軸尺寸與STL世界外框不可互換")
            for field, idname, optionkey in (("export_operator", "WM_OT_stl_export", "export_options"), ("import_operator", "WM_OT_stl_import", "import_options")):
                operator = entry.get(field)
                execution = ("native UI confirmation and new binary STL readback" if field == "export_operator"
                             else "native UI confirmation and newly created mesh readback")
                if (not isinstance(operator, dict) or operator.get("idname") != idname
                        or not _same_mesh_readback(operator.get("options"), entry[optionkey])
                        or not isinstance(operator.get("filepath"), str) or Path(operator["filepath"]).resolve() != path
                        or operator.get("captured_at") != "live_file_browser_before_native_confirm"
                        or type(operator.get("operator_history_available")) is not bool
                        or operator.get("execution_verified_by") != execution):
                    raise ImportValidationError("實際原生匯出／匯入operator讀值不符")
                history = operator.get("operator_history_entry")
                if operator["operator_history_available"]:
                    if not _same_mesh_readback(history, {key: operator[key] for key in ("idname", "options", "filepath")}):
                        raise ImportValidationError("可用的原生operator歷程須與確認前活頁視窗讀值一致")
                elif "operator_history_entry" in operator:
                    raise ImportValidationError("原生operator歷程不可用時，不得填入虛構歷程")
            actual = validate_snapfit_stl(path, part, prior, dumps["source_" + part])
            if (not _same_mesh_readback(entry.get("stl_verification"), actual)
                    or not _same_mesh_readback(_read_json(run_dir / (part + "-stl-verification.json")), actual)):
                raise ImportValidationError("卡扣 STL 詳細證據與實檔重算不符")
            reimport = dumps["reimport_" + part]
            actual_reimport = validate_snapfit_export_mesh(reimport["vertices"], reimport["triangles"], part, prior, dumps["source_" + part])
            if not _same_mesh_readback(v.get("reimport_" + part), actual_reimport):
                raise ImportValidationError("實際重匯入網格與有向表面／逆姿態重算不符")
            stl_parts[part] = read_stl(path)
        for field, parts in (("stl_layout", stl_parts), ("reimport_layout", {part: dumps["reimport_" + part] for part in ("body", "lid")})):
            if not _same_mesh_readback(v.get(field), layout(parts)):
                raise ImportValidationError("分件候選落床／35mm分隔不得改成扣合裝配")
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError) as exc:
        raise ImportValidationError("卡扣STL／實際重匯入完整網格重算失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    source_objects = v.get("source_objects")
    if not isinstance(source_objects, dict) or set(source_objects) != {"Body", "Lid", "SnapTool", "FlangeTool"}:
        raise ImportValidationError("來源inventory只能含兩成品與兩隱藏工具")
    for name, item in source_objects.items():
        original = prior["final_objects"][name]
        if not isinstance(item, dict) or any(item.get(key) != original[key] for key in ("type", "scale", "location_mm", "rotation_euler_radians", "matrix_world", "modifier_count")):
            raise ImportValidationError("來源物件inventory的幾何transform不可變更")
        if name.endswith("Tool") and item.get("hidden") is not True:
            raise ImportValidationError("來源建構工具須保持隱藏")
    final_objects = v.get("final_objects")
    if not isinstance(final_objects, dict) or set(final_objects) != {"Body_STL", "Lid_STL"}:
        raise ImportValidationError("重匯入場景只能含兩件STL成品，不得有Tools")
    for part in ("body", "lid"):
        name = part.title() + "_STL"
        item, cad = final_objects[name], dumps["reimport_" + part]["cad_metadata"]
        if (not isinstance(item, dict) or item.get("type") != "MESH" or item.get("hidden") is not False
                or type(item.get("modifier_count")) is not int or item["modifier_count"] != 0
                or item.get("scale") != [1, 1, 1]):
            raise ImportValidationError("最終STL物件須可見、Scale1、modifier0")
        for key, cad_key in (("location_mm", "object_location_mm"), ("rotation_euler_radians", "object_rotation_euler_radians"),
                             ("object_axis_dimensions_mm", "object_axis_dimensions_mm"), ("matrix_world", "matrix_world")):
            if not _same_mesh_readback(item.get(key), cad[cad_key]):
                raise ImportValidationError("重匯入最終inventory與實際world網格不符")
    record_path = _contained_file(Path(v["export_record_path"]), run_dir, "卡扣STL版本紀錄")
    if record_path != (run_dir / "stl-export-record-v001.json").resolve() or _digest(record_path) != v.get("export_record_sha256"):
        raise ImportValidationError("STL匯出紀錄檔名或雜湊不符")
    record = _read_json(record_path)
    expected = {"schema_version": 1, "lesson_step": "07-04", "stage": "digital_stl_export_only",
                "source_scene": {"path": str(source), "sha256": spec["source_scene_sha256"]},
                "source_orientation_record": {"path": str(orientation_path), "sha256": spec["source_orientation_sha256"]},
                "exports": exports, **{key: v[key] for key in ("reimport_body", "reimport_lid", "reimport_layout")},
                "saved_new_scene": False, "printed": False, "fit_tested": False, "slicer_checked": False,
                "physical_measurements": None, "fit_results": None, "qualified_clearance_mm": None, "qualified_strength_N": None,
                "support_required": None, "final_print_orientation_approved": None}
    if (not isinstance(record, dict) or set(record) != set(expected) | {"recordedAt"}
            or not isinstance(record.get("recordedAt"), str) or not record["recordedAt"]
            or not _same_mesh_readback({key: record[key] for key in expected}, expected)):
        raise ImportValidationError("STL版本紀錄須完整綁定來源、兩件實檔、重匯入及未填實體結果")
    return v, _validate_runner(run, run_dir, "lesson07_snap_export")


def _validate_lesson07_coupons(run, run_dir, spec):
    v = _read_json(run_dir / "verification.json")
    if not isinstance(v, dict) or v.get("passed") is not True or v.get("kind") != "snapfit_length_coupons_geometry_demo" or v.get("errors"):
        raise ImportValidationError("獨立長度試片幾何驗證未通過或角色不符")
    for key in ("source_unchanged", "opened_copy_unchanged", "reopened", "independent_coupon_meshes", "coupon_geometry_modified"):
        if v.get(key) is not True:
            raise ImportValidationError("試片來源／重開／獨立網格／新幾何狀態不符：%s" % key)
    for key in ("source_geometry_modified", "full_box_modified", "rotation_applied_to_mesh", "exported_stl", "mesh_analysis_overhang_checked",
                "improvement_assessed", "strength_analysis_performed", "deformation_analysis_performed", "fit_qualification",
                "support_generation_performed", "slicer_checked", "printed", "fit_tested"):
        if v.get(key) is not False:
            raise ImportValidationError("試片不可宣稱原盒修改、改善或實體階段完成：%s" % key)
    nulls = ("full_box_boundary_equivalence", "anchor_clamping_or_fixture", "effective_mechanical_length_mm", "support_required",
             "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified", "improvement_validated",
             "material_grade", "epsilon_allow", "Q", "required_deflection_mm", "delta_allow_mm", "forces", "physical_measurements",
             "fit_results", "physical_interference", "qualified_strength_N", "qualified_clearance_mm")
    if any(key not in v or v[key] is not None for key in nulls):
        raise ImportValidationError("獨立試片邊界／夾持／力學／改善／實體結果須保留null")
    numeric = v.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("positionEpsilonMm"), 1e-4)
            or not _numeric_equal(numeric.get("volumeRelativeEpsilon"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]):
        raise ImportValidationError("試片缺少浮點重建比較用途／門檻")
    names = ("A_L19", "B_L17", "C_L21")
    modified = {"A_L19": False, "B_L17": True, "C_L21": True}
    if v.get("per_variant_geometry_modified") != modified:
        raise ImportValidationError("A為原草案、B/C改幾何，不能把source未改旗標套在全部試片")
    project = run_dir.resolve().parents[3]
    for key in ("source_scene_path", "opened_scene_path", "draft_plan_path", "source_tool_mesh_path", "source_geometry_record_path",
                "continuity_reference_path", "scene_path", "coupon_record_path"):
        if not isinstance(v.get(key), str) or not Path(v[key]).is_absolute():
            raise ImportValidationError("試片版本路徑須為絕對路徑：%s" % key)
    plan_path = _contained_file(Path(v["draft_plan_path"]), project / "learning/plans", "固定單參數試片草案")
    if (plan_path != (project / "learning/plans/07-05-coupon-length-draft-v001.json").resolve()
            or _digest(plan_path) != spec["draft_plan_sha256"] or v.get("draft_plan_sha256") != spec["draft_plan_sha256"]):
        raise ImportValidationError("單參數試片計畫版本不符")
    plan = _read_json(plan_path)
    for key, plan_key in (("source_scene", "source_scene"), ("source_tool_mesh", "source_tool_mesh"),
                          ("source_geometry_record", "source_geometry_record"), ("continuity_reference", "continuity_reference")):
        expected = plan[plan_key]
        path = _contained_file(Path(v[key + "_path"]), project / "learning/evidence", "試片固定來源")
        if path != (project / expected["path"]).resolve() or _digest(path) != expected["sha256"] or v.get(key + "_sha256") != expected["sha256"]:
            raise ImportValidationError("試片來源／原幾何／舊輸出沿革版本不符：%s" % key)
    source = Path(v["source_scene_path"]).resolve()
    opened = _contained_file(Path(v["opened_scene_path"]), run_dir / "demo-files/sources", "試片讀取副本")
    if (opened != (run_dir / "demo-files/sources/u07_print_orientation_v001.blend").resolve()
            or _digest(opened) != spec["source_scene_sha256"] or v.get("opened_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("試片讀取副本與07-03固定場景不符")
    scene = _contained_file(Path(v["scene_path"]), run_dir / "demo-files", "新獨立試片場景")
    if (scene != (run_dir / "demo-files/u07_cantilever_length_coupons_v001.blend").resolve() or not scene.stat().st_size
            or type(v.get("scene_bytes")) is not int or v["scene_bytes"] != scene.stat().st_size
            or _digest(scene) != v.get("scene_sha256") or v["scene_sha256"] == spec["source_scene_sha256"]):
        raise ImportValidationError("新試片場景檔名／大小／hash不符")
    if list((run_dir / "demo-files").rglob("*.stl")):
        raise ImportValidationError("本次只有試片blend幾何，不應新增STL")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_coupons.py", "learning/tutor/scenarios/coupon_checks.py",
                "learning/tutor/scenarios/overhang_checks.py", "learning/tutor/scenarios/snapfit_checks.py",
                "learning/tutor/scenarios/snapfit_stl_checks.py", "learning/tutor/scenarios/stl_checks.py",
                "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, spec["source_scene_sha256"], required)
    bindings = _read_json(run_dir / "source-snapshot/manifest.json").get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings)
            or {item.get("source") for item in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("試片計畫／原tool／幾何／版本沿革的dataBindings不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("試片來源資料綁定版本不符")
        original = _contained_file(project / item["source"], project, "試片來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "試片來源快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("試片固定來源資料／快照hash不符")
    prior = _read_json(run_dir / "source-snapshot/source-orientation-verification.json")
    before, after, final = v.get("source_objects"), v.get("final_source_objects"), v.get("final_objects")
    originals = {"Body", "Lid", "SnapTool", "FlangeTool"}
    if (not isinstance(before, dict) or set(before) != originals or not isinstance(after, dict) or set(after) != originals
            or not isinstance(final, dict) or set(final) != originals | set(names)):
        raise ImportValidationError("試片場景須保留4原件加3新件，不能取代原盒／蓋")
    for name in originals:
        item, last, old = before[name], after[name], prior["final_objects"][name]
        if (not isinstance(item, dict) or not isinstance(last, dict) or last.get("hidden") is not True
                or item.get("hidden") != old["hidden"]
                or {key: val for key, val in item.items() if key != "hidden"} != {key: val for key, val in last.items() if key != "hidden"}
                or final[name] != last or not isinstance(item.get("mesh_data_name"), str) or not item["mesh_data_name"]):
            raise ImportValidationError("原4物件只可隱藏，mesh、data及matrix不可變更")
        for field in ("type", "scale", "modifier_count", "matrix_world", "location_mm", "rotation_euler_radians"):
            if item.get(field) != old[field]:
                raise ImportValidationError("原4物件與固定07-03姿態不符")
    if before["SnapTool"].get("local_mesh_sha256") != spec["source_tool_local_sha256"]:
        raise ImportValidationError("原SnapTool local mesh不符固定native來源")
    if before != _read_json(run_dir / "source-object-inventory.json"):
        raise ImportValidationError("來源inventory紀錄不符")
    display = {"show_statvis": False, "shading": "SOLID", "deactivated_with": "native Edit Mesh Overlays / Mesh Analysis checkbox", "new_overhang_analysis_performed": False}
    if v.get("display_settings") != display or _read_json(run_dir / "native-display-settings.json") != display:
        raise ImportValidationError("繼承的Mesh Analysis須實際關閉，不可冒充新Overhang檢查")
    for key in ("source_frame", "candidates", "selection_proofs", "motion_proofs", "duplicate_proofs"):
        if not isinstance(v.get(key), dict) or set(v[key]) != set(names):
            raise ImportValidationError("三件試片的姿態與UI動作證據不完整：%s" % key)
    for key, filename in (("selection_proofs", "upper-vertex-selection-proofs.json"), ("motion_proofs", "vertex-motion-proofs.json"), ("duplicate_proofs", "duplicate-proofs.json")):
        if not _same_mesh_readback(v[key], _read_json(run_dir / filename)):
            raise ImportValidationError("試片動作獨立檔與verification不符")
    required_slugs = {name + suffix for name in names for suffix in ("-duplicate", "-upper-selection", "-source-frame", "-candidate", "-non-manifold")}
    required_slugs.add("inherited-analysis-off")
    if not required_slugs <= {record.get("slug") for record in run.get("records", [])}:
        raise ImportValidationError("試片缺少原生duplicate／14點選取／移動／候選／NM實拍")
    raws = {"source": _read_json(run_dir / "source_snap_tool_mesh.json")}
    source_raw = raws["source"]
    source_reference = _read_json(Path(v["source_tool_mesh_path"]))
    if (len(source_raw.get("vertices", [])) != 42 or len(source_raw.get("triangles", [])) != 80
            or not _same_mesh_readback(source_raw["vertices"], source_reference["vertices"])):
        raise ImportValidationError("UI來源須是固定原42點／80三角面的SnapTool")
    source_cad = source_raw.get("cad_metadata", {})
    if (source_cad.get("object_name") != "SnapTool" or source_cad.get("mesh_data_name") != before["SnapTool"]["mesh_data_name"]
            or source_cad.get("matrix_world") != before["SnapTool"]["matrix_world"]):
        raise ImportValidationError("原SnapTool raw的data與matrix須對應原inventory")
    upper = [i for i, point in enumerate(source_raw["vertices"]) if point[2] >= 10.9999]
    lower = [i for i in range(42) if i not in upper]
    if len(upper) != 14 or len(lower) != 28:
        raise ImportValidationError("原source-frame頂點分區不是14上端／28保留點")
    expected_upper = [source_raw["vertices"][i] for i in upper]
    for variant in plan["coupon_objects"]:
        name, delta = variant["name"], variant["upper_vertex_translation_z_mm"]
        for pose, filename in (("source_frame", name + "_source_frame_mesh.json"), ("candidate", name + "_candidate_mesh.json")):
            raw = _read_json(run_dir / filename);cad = raw.get("cad_metadata", {})
            if (len(raw.get("vertices", [])) != 42 or len(raw.get("triangles", [])) != 80
                    or raw.get("polygons") != source_raw.get("polygons") or cad.get("object_name") != name):
                raise ImportValidationError("原生UI三試片須保留42點／80三角面及polygon拓樸")
            radians = [0., 0., 0.] if pose == "source_frame" else [0., math.pi/2, 0.]
            rotation = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]] if pose == "source_frame" else [[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]]
            location = plan["source_object_origin_mm"] if pose == "source_frame" else variant["candidate_object_location_mm"]
            matrix = [rotation[i] + [float(location[i])] for i in range(3)] + [[0.,0.,0.,1.]]
            if (not _same_mesh_readback(cad.get("matrix_world"), matrix)
                    or not all(_mesh_numeric_equal(a,b) for a,b in zip(cad.get("object_rotation_euler_radians", []), radians))
                    or len(cad.get("object_rotation_euler_radians", [])) != 3):
                raise ImportValidationError("三試片須保留R0編輯／Ry90候選及固定Object Location，不能Apply")
            raws[name + "_" + pose] = raw
        frame = raws[name + "_source_frame"]
        residual = 0.
        for i, (old, point) in enumerate(zip(source_raw["vertices"], frame["vertices"])):
            expected = [old[0], old[1], old[2] + (delta if i in upper else 0)]
            residual = max(residual, max(abs(a-b) for a,b in zip(expected, point)))
        if residual > 1e-4:
            raise ImportValidationError("只能將原14上端點沿Z移指定量，其餘28點不可動")
        proof = {"variant": name, "upper_vertex_count": 14, "unchanged_vertex_count": 28, "upper_source_vertex_indices": upper,
                 "unchanged_source_vertex_indices": lower, "translation_z_mm": delta, "maximum_coordinate_residual_mm": residual,
                 "polygon_topology_unchanged": True, "coupon_geometry_modified": delta != 0, "source_frame_origin_unchanged": True}
        if not _same_mesh_readback(v["motion_proofs"][name], proof):
            raise ImportValidationError("原生頂點移動紀錄與實網格不符")
        selected = v["selection_proofs"][name]
        points = selected.get("selected_world_vertices_mm", [])
        if (selected.get("variant") != name or type(selected.get("selected_count")) is not int or selected["selected_count"] != 14
                or type(selected.get("expected_count")) is not int or selected["expected_count"] != 14
                or not isinstance(points, list) or len(points) != 14
                or any(not isinstance(point, list) or len(point) != 3 for point in points)
                or not _same_mesh_readback(selected.get("original_upper_vertices_mm"), expected_upper)
                or any(sum(all(_mesh_numeric_equal(a,b) for a,b in zip(point, expected)) and len(point)==3 for point in points) != 1 for expected in expected_upper)
                or selected.get("selection_method") != "Front orthographic / Vertex / Xray / native B box select"):
            raise ImportValidationError("B框選必須實際選中原14個上端點，不可僅回報數量")
        data_name = frame["cad_metadata"].get("mesh_data_name")
        duplicate = {"source_object": "SnapTool", "operation": "native Shift+D then Esc", "mesh_data_name": data_name,
                     "independent_from_source": True, "location_mm": [float(x) for x in plan["source_object_origin_mm"]], "rotation_euler_radians": [0.,0.,0.]}
        if not _same_mesh_readback(v["duplicate_proofs"][name], duplicate):
            raise ImportValidationError("試片須從原SnapTool獨立複製，不是從前個已改試片或linked data複製")
        item, cad = final[name], raws[name + "_candidate"]["cad_metadata"]
        if (item.get("type") != "MESH" or item.get("hidden") is not False or item.get("modifier_count") != 0 or item.get("scale") != [1,1,1]
                or item.get("mesh_data_name") != data_name or cad.get("mesh_data_name") != data_name
                or any(not _same_mesh_readback(item.get(key), cad[cadkey]) for key,cadkey in
                       (("matrix_world","matrix_world"),("location_mm","object_location_mm"),("rotation_euler_radians","object_rotation_euler_radians")))):
            raise ImportValidationError("重開後可見試片inventory／mesh data／姿態與實網格不符")
    data_names = [final[name].get("mesh_data_name") for name in names]
    if (any(not isinstance(name,str) or not name for name in data_names) or len(set(data_names)) != 3
            or set(data_names) & {item["mesh_data_name"] for item in before.values()}):
        raise ImportValidationError("三試片mesh資料必須彼此獨立，且不與任何來源件共享")
    scenarios = str(Path(__file__).resolve().parent / "scenarios");sys.path.insert(0, scenarios)
    try:
        from coupon_checks import validate_source_snap_tool, validate_coupon, validate_coupon_layout
        actual_source = validate_source_snap_tool(source_raw)
        frames = {name:validate_coupon(source_raw, raws[name+"_source_frame"], name, "source_frame", plan) for name in names}
        candidates = {name:validate_coupon(source_raw, raws[name+"_candidate"], name, "print_candidate", plan) for name in names}
        layout = validate_coupon_layout(candidates, plan)
    except (ImportError,OSError,ValueError,RuntimeError,KeyError,TypeError,IndexError) as exc:
        raise ImportValidationError("單參數試片完整來源／逆長度／候選幾何重算失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    for key, actual in (("source_tool",actual_source),("source_frame",frames),("candidates",candidates),("layout",layout)):
        if not _same_mesh_readback(v.get(key), actual):
            raise ImportValidationError("試片幾何長度、保留特徵或床接觸／離床讀值與網格不符")
    record_path = _contained_file(Path(v["coupon_record_path"]), run_dir, "試片幾何對照紀錄")
    if record_path != (run_dir / "coupon-record-v001.json").resolve() or _digest(record_path) != v.get("coupon_record_sha256"):
        raise ImportValidationError("試片幾何紀錄檔名／hash不符")
    record = _read_json(record_path)
    added = {"recordedAt","reference_scene","geometry_readback","source_geometry_modified","coupon_geometry_modified","per_variant_geometry_modified"}
    if (not isinstance(record,dict) or set(record) != set(plan)|added or not isinstance(record.get("recordedAt"),str) or not record["recordedAt"]
            or json.dumps({key:record[key] for key in plan},sort_keys=True,ensure_ascii=False) != json.dumps(plan,sort_keys=True,ensure_ascii=False)
            or record.get("reference_scene") != {"path":str(scene),"sha256":_digest(scene),"bytes":scene.stat().st_size,"scene_role":"standalone_length_geometry_comparison_draft"}
            or record.get("source_geometry_modified") is not False or record.get("coupon_geometry_modified") is not True
            or record.get("per_variant_geometry_modified") != modified
            or not _same_mesh_readback(record.get("geometry_readback"), {key:v[key] for key in ("source_tool","source_frame","candidates","layout")})):
        raise ImportValidationError("試片紀錄須保留完整草案、未驗證邊界／結果及新場景與網格關聯")
    return v, _validate_runner(run, run_dir, "lesson07_coupons")


def _validate_lesson07_coupon_export(run, run_dir, spec):
    """Validate three existing coupons, without advancing learner/physical state."""
    v = _read_json(run_dir / "verification.json")
    if not isinstance(v, dict) or v.get("passed") is not True or v.get("kind") != "cantilever_coupon_stl_exports" or v.get("errors"):
        raise ImportValidationError("三試片STL數位驗證角色或結果不符")
    for field in ("source_unchanged", "opened_copy_unchanged", "source_coupon_record_unchanged", "reimport_verified", "exported_stl", "reimport_mesh_datablocks_created"):
        if v.get(field) is not True:
            raise ImportValidationError("三試片來源／重匯入狀態不符：%s" % field)
    for field in ("saved_new_scene", "geometry_modified", "source_geometry_modified", "new_geometry_created", "full_box_modified",
                  "rotation_applied_to_mesh", "mesh_analysis_overhang_checked", "improvement_assessed", "strength_analysis_performed",
                  "deformation_analysis_performed", "fit_qualification", "slicer_checked", "printed", "fit_tested", "support_generation_performed", "new_specimen_design_created"):
        if v.get(field) is not False:
            raise ImportValidationError("本次僅既有三試片STL輸出，不可填改形／實體／改善旗標：%s" % field)
    for field in ("material_grade", "epsilon_allow", "Q", "effective_mechanical_length_mm", "full_box_boundary_equivalence",
                  "anchor_clamping_or_fixture", "required_deflection_mm", "delta_allow_mm", "forces", "physical_measurements", "fit_results",
                  "physical_interference", "qualified_strength_N", "qualified_clearance_mm", "improvement_validated", "support_required",
                  "final_print_orientation_approved", "slicer_support_settings", "bridge_or_support_qualified"):
        if field not in v or v[field] is not None:
            raise ImportValidationError("三試片材料／力學／夾持／實體／改善結果須維持null：%s" % field)
    if not isinstance(v.get("geometry_scope"), str) or not v["geometry_scope"]:
        raise ImportValidationError("須說明重匯入建立mesh資料，但沒有新試片設計")
    numeric = v.get("numericComparison")
    if (not isinstance(numeric, dict) or not _numeric_equal(numeric.get("dimensionsAbsMm"), 1e-4)
            or not _numeric_equal(numeric.get("coordinateWeldMm"), 1e-5) or not _numeric_equal(numeric.get("volumeRelative"), 1e-5)
            or not isinstance(numeric.get("purpose"), str) or not numeric["purpose"]
            or not isinstance(v.get("stl_unit_interpretation"), str) or not v["stl_unit_interpretation"]):
        raise ImportValidationError("STL須說明mm解讀與浮點門檻用途")
    project = run_dir.resolve().parents[3]
    source_dir = project / "learning/evidence/07/2026-10-25-lesson07-coupons-demo-v001"
    for field in ("source_scene_path", "opened_scene_path", "source_coupon_record_path", "draft_plan_path", "export_record_path"):
        if not isinstance(v.get(field), str) or not Path(v[field]).is_absolute():
            raise ImportValidationError("三試片版本路徑須為絕對路徑：%s" % field)
    source = _contained_file(Path(v["source_scene_path"]), source_dir / "demo-files", "07-05固定試片場景")
    opened = _contained_file(Path(v["opened_scene_path"]), run_dir / "demo-files/sources", "三試片讀取副本")
    filename = "u07_cantilever_length_coupons_v001.blend"
    if (source != (source_dir / "demo-files" / filename).resolve() or opened != (run_dir / "demo-files/sources" / filename).resolve()
            or any(_digest(p) != spec["source_scene_sha256"] for p in (source, opened))
            or v.get("source_scene_sha256") != spec["source_scene_sha256"] or v.get("opened_scene_sha256") != spec["source_scene_sha256"]):
        raise ImportValidationError("原三試片與同hash副本不符固定v001")
    if set((run_dir / "demo-files").rglob("*.blend")) != {opened}:
        raise ImportValidationError("STL數位輸出不得另存新blend")
    source_record = _contained_file(Path(v["source_coupon_record_path"]), source_dir, "來源coupon紀錄")
    plan_path = _contained_file(Path(v["draft_plan_path"]), project / "learning/plans", "單參數試片草案")
    if (source_record != (source_dir / "coupon-record-v001.json").resolve()
            or _digest(source_record) != spec["source_coupon_record_sha256"] or v.get("source_coupon_record_sha256") != spec["source_coupon_record_sha256"]
            or plan_path != (project / "learning/plans/07-05-coupon-length-draft-v001.json").resolve()
            or _digest(plan_path) != spec["draft_plan_sha256"] or v.get("draft_plan_sha256") != spec["draft_plan_sha256"]):
        raise ImportValidationError("原試片紀錄或單參數草案版本不符")
    required = {"learning/tutor/run_demo.py", "learning/tutor/blender_demo.py", "learning/tutor/scenarios/common.py",
                "learning/tutor/scenarios/lesson07_coupon_export.py", "learning/tutor/scenarios/coupon_stl_checks.py",
                "learning/tutor/scenarios/coupon_checks.py", "learning/tutor/scenarios/snapfit_stl_checks.py", "learning/tutor/scenarios/overhang_checks.py",
                "learning/tutor/scenarios/snapfit_checks.py", "learning/tutor/scenarios/stl_checks.py", "learning/tutor/scenarios/tenon_checks.py", "learning/tutor/scenarios/lid_checks.py"}
    _validate_script_snapshot(run_dir, source, opened, spec["source_scene_sha256"], required)
    bindings = _read_json(run_dir / "source-snapshot/manifest.json").get("dataBindings")
    if (not isinstance(bindings, list) or len(bindings) != len(spec["data_bindings"])
            or any(not isinstance(item, dict) for item in bindings) or {x.get("source") for x in bindings} != set(spec["data_bindings"])):
        raise ImportValidationError("三試片計畫／原工具／三candidate／紀錄綁定不完整")
    for item in bindings:
        expected = spec["data_bindings"][item["source"]]
        if item.get("snapshot") != expected["snapshot"] or item.get("sha256") != expected["sha256"]:
            raise ImportValidationError("三試片資料綁定版本不符")
        original = _contained_file(project / item["source"], project, "固定試片來源資料")
        snapshot = _contained_file(run_dir / item["snapshot"], run_dir / "source-snapshot", "試片來源資料快照")
        if _digest(original) != expected["sha256"] or _digest(snapshot) != expected["sha256"]:
            raise ImportValidationError("三試片來源或快照hash不符")
    prior = _read_json(source_dir / "verification.json")
    names = ("A_L19", "B_L17", "C_L21")
    if (prior.get("passed") is not True or prior.get("kind") != "snapfit_length_coupons_geometry_demo" or prior.get("reopened") is not True
            or prior.get("scene_sha256") != spec["source_scene_sha256"] or prior.get("coupon_record_sha256") != spec["source_coupon_record_sha256"]):
        raise ImportValidationError("來源須為已另存重開的固定三試片版本")
    if (not _same_mesh_readback(v.get("source_candidates"), prior["candidates"])
            or not _same_mesh_readback(v.get("source_layout"), prior["layout"])):
        raise ImportValidationError("來源三試片長度或候選擺位讀值不得變更")
    originals = {"Body", "Lid", "SnapTool", "FlangeTool"}
    inventory = v.get("source_objects")
    if not isinstance(inventory, dict) or set(inventory) != originals | set(names):
        raise ImportValidationError("來源須保留原四件及三個獨立coupon")
    for name, item in inventory.items():
        old = prior["final_objects"][name]
        if (not isinstance(item, dict) or any(item.get(field) != old[field] for field in
                ("type", "scale", "modifier_count", "matrix_world", "local_mesh_sha256", "mesh_data_name", "location_mm", "rotation_euler_radians", "object_axis_dimensions_mm"))
                or item.get("data_name") != item.get("mesh_data_name")):
            raise ImportValidationError("來源七物件local mesh／矩陣／獨立data不得變更")
        if name in originals and item.get("hidden") is not True:
            raise ImportValidationError("四個來源盒／蓋／工具須保持hidden")
    if len({inventory[n]["mesh_data_name"] for n in names}) != 3:
        raise ImportValidationError("三來源coupon須保留獨立mesh data")
    exports = v.get("exports")
    if (not isinstance(exports, list) or len(exports) != 3 or any(not isinstance(e, dict) for e in exports)
            or sorted(e.get("kind", "") for e in exports) != sorted(names)
            or any(e.get("variant") != e.get("kind") for e in exports)):
        raise ImportValidationError("須恰有三份同名kind／variant的coupon STL")
    if not isinstance(v.get("reimport"), dict) or set(v["reimport"]) != set(names):
        raise ImportValidationError("須有三件實際重新匯入的完整幾何讀回")
    required_slugs = {name + suffix for name in names for suffix in
        ("-source-selected", "-source-profile", "-export-options", "-stl-checked", "-import-dialog", "-reimport-dimensions", "-reimport-profile", "-reimport-non-manifold")}
    if not required_slugs <= {r.get("slug") for r in run.get("records", [])}:
        raise ImportValidationError("缺少三試片單選／匯出選項／實檔／重匯入／NM原生實拍")
    dumps = {}
    for name in names:
        for prefix in ("source", "reimport"):
            raw = _read_json(_contained_file(run_dir / (prefix + "_" + name + "_mesh.json"), run_dir, "三試片世界raw"))
            cad = raw.get("cad_metadata") if isinstance(raw, dict) else None
            if (not isinstance(raw, dict) or not raw.get("vertices") or not raw.get("triangles") or not isinstance(cad, dict)
                    or cad.get("object_name") != name + ("_STL" if prefix == "reimport" else "")
                    or cad.get("length_unit") != "MILLIMETERS" or not _numeric_equal(cad.get("unit_scale"), .001)
                    or type(cad.get("modifier_count")) is not int or cad["modifier_count"] != 0
                    or not _same_mesh_readback(cad.get("scale"), [1., 1., 1.])):
                raise ImportValidationError("coupon來源／重匯入物件名、單位、Scale或修改器不符")
            if prefix == "source":
                old = _read_json(source_dir / (name + "_candidate_mesh.json"))
                if any(raw.get(field) != old[field] for field in ("vertices", "triangles", "polygons", "triangle_polygon_indices", "polygon_normals_world")):
                    raise ImportValidationError("來源candidate的完整world網格／原生polygon不得變更")
                if any(cad.get(field) != old["cad_metadata"][field] for field in
                       ("scale", "modifier_count", "object_location_mm", "object_rotation_euler_radians", "matrix_world", "object_axis_dimensions_mm")):
                    raise ImportValidationError("來源Ry90候選及Item物件軸尺寸須保持，不得Apply")
            else:
                identity = [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
                for field in ("object_location_mm", "object_rotation_euler_radians", "object_rotation_euler_degrees"):
                    if (not isinstance(cad.get(field), list) or len(cad[field]) != 3 or not all(_mesh_numeric_equal(a, 0) for a in cad[field])):
                        raise ImportValidationError("實際STL重匯入須Location0／Rotation0，不可誤採reference Ry90")
                bounds = {key:[fn(point[a] for point in raw["vertices"]) for a in range(3)] for key,fn in (("min",min),("max",max))}
                dims = [bounds["max"][i]-bounds["min"][i] for i in range(3)]
                if not _same_mesh_readback(cad.get("matrix_world"), identity) or not _same_mesh_readback(cad.get("object_axis_dimensions_mm"), dims):
                    raise ImportValidationError("實際重匯入R0的Item尺寸須等於world外框，矩陣須identity")
            dumps[prefix + "_" + name] = raw
    scenarios = str(Path(__file__).resolve().parent / "scenarios"); sys.path.insert(0, scenarios)
    try:
        from coupon_stl_checks import validate_coupon_stl, validate_coupon_export_mesh, validate_export_layout
        from stl_checks import read_stl
        source_tool = _read_json(run_dir / "source-snapshot/source-snap-tool-reference.json")
        stl_results, imported_results = {}, {}
        for entry in exports:
            name = entry["kind"]
            if (entry.get("source_object") != name or entry.get("selected_names") != [name] or entry.get("reimport_object") != name + "_STL"):
                raise ImportValidationError("每份coupon STL只能選本件，排除另兩試片及四個hidden來源件")
            expected_options = {"export_options": {"only_selected":True,"global_scale":1.,"use_scene_unit":False,"apply_modifiers":True,
                "forward_axis":"Y","up_axis":"Z","ascii_format":False,"use_batch":False,"evaluation_mode":"DAG_EVAL_RENDER"},
                "import_options":{"global_scale":1.,"use_scene_unit":False,"forward_axis":"Y","up_axis":"Z"}}
            for field, expected in expected_options.items():
                if not _same_mesh_readback(entry.get(field), expected):
                    raise ImportValidationError("coupon匯出／匯入須Binary／Selection Only／Scale1／SceneUnit關／YZ")
            if not isinstance(entry.get("stl_path"), str) or not Path(entry["stl_path"]).is_absolute():
                raise ImportValidationError("coupon STL須為絕對路徑")
            path = _contained_file(Path(entry["stl_path"]), run_dir / "demo-files/exports", "coupon STL")
            if path != (run_dir / ("demo-files/exports/u07_" + name + "_v001.stl")).resolve() or _digest(path) != entry.get("stl_sha256"):
                raise ImportValidationError("coupon STL版本檔名／hash不符")
            binary, mesh = _read_binary_stl(path), read_stl(path)
            for field, value in (("stl_bytes",binary["bytes"]),("stl_triangles",binary["triangles"]),("stl_non_manifold_edges",binary["non_manifold_edges"]),
                                 ("stl_connected_shells",binary["connected_shells"]),("stl_genus",binary["genus"])):
                if type(entry.get(field)) is not int or entry[field] != value:
                    raise ImportValidationError("coupon STL實檔bytes／triangles／拓樸不符")
            if (not _same_mesh_readback(entry.get("stl_dimensions_mm"), mesh["dimensions_mm"])
                    or not _same_mesh_readback(entry.get("stl_bounds_mm"), mesh["bounds_mm"])
                    or not _mesh_numeric_equal(entry.get("stl_volume_mm3"), mesh["volume_mm3"])
                    or not _same_mesh_readback(entry.get("source_item_dimensions_mm"), dumps["source_"+name]["cad_metadata"]["object_axis_dimensions_mm"])):
                raise ImportValidationError("coupon STL世界尺寸／體積與來源Item尺寸分欄不符")
            for field, idname, options_key in (("export_operator","WM_OT_stl_export","export_options"),("import_operator","WM_OT_stl_import","import_options")):
                op = entry.get(field)
                execution = "native UI confirmation and new binary STL readback" if field == "export_operator" else "native UI confirmation and newly created mesh readback"
                if (not isinstance(op, dict) or op.get("idname") != idname or not _same_mesh_readback(op.get("options"), entry[options_key])
                        or not isinstance(op.get("filepath"),str) or Path(op["filepath"]).resolve() != path
                        or op.get("captured_at") != "live_file_browser_before_native_confirm" or type(op.get("operator_history_available")) is not bool
                        or op.get("execution_verified_by") != execution):
                    raise ImportValidationError("原生File Browser確認前operator讀值或執行證據不符")
                if op["operator_history_available"]:
                    if not _same_mesh_readback(op.get("operator_history_entry"), {k:op[k] for k in ("idname","options","filepath")}):
                        raise ImportValidationError("可用operator歷程須與live dialog一致")
                elif "operator_history_entry" in op:
                    raise ImportValidationError("不可捏造不可用的原生operator歷程")
            actual = validate_coupon_stl(path, name, prior, dumps["source_"+name], source_tool)
            raw = dumps["reimport_"+name]
            imported = validate_coupon_export_mesh(raw["vertices"], raw["triangles"], name, prior, dumps["source_"+name], source_tool)
            if (not _same_mesh_readback(entry.get("stl_verification"), actual)
                    or not _same_mesh_readback(_read_json(run_dir / (name+"-stl-verification.json")), actual)
                    or not _same_mesh_readback(v["reimport"][name], imported)):
                raise ImportValidationError("coupon STL／實際重匯入有向表面／逆長度／床特徵重算不符")
            stl_results[name], imported_results[name] = actual, imported
        if (not _same_mesh_readback(v.get("stl_layout"), validate_export_layout(stl_results, prior))
                or not _same_mesh_readback(v.get("reimport_layout"), validate_export_layout(imported_results, prior))):
            raise ImportValidationError("三件候選world分列間距／數值落床布局不符")
    except (ImportError,OSError,ValueError,RuntimeError,KeyError,TypeError,IndexError) as exc:
        raise ImportValidationError("三coupon STL／重匯入完整幾何重算失敗：%s" % exc) from exc
    finally:
        sys.path.pop(0)
    if set((run_dir / "demo-files").rglob("*.stl")) != {Path(e["stl_path"]) for e in exports}:
        raise ImportValidationError("本run只應輸出三件指定coupon STL")
    final = v.get("final_objects")
    if not isinstance(final, dict) or set(final) != {n+"_STL" for n in names}:
        raise ImportValidationError("最終場景只能含三個真實匯入coupon")
    data_names = []
    for name in names:
        item, cad = final[name+"_STL"], dumps["reimport_"+name]["cad_metadata"]
        if (not isinstance(item,dict) or item.get("type") != "MESH" or item.get("hidden") is not False
                or type(item.get("modifier_count")) is not int or item["modifier_count"] != 0 or not _same_mesh_readback(item.get("scale"), [1.,1.,1.])
                or not isinstance(item.get("mesh_data_name"),str) or not item["mesh_data_name"] or item.get("data_name") != item["mesh_data_name"]):
            raise ImportValidationError("最終三STL須可見／Scale1／修改器0／獨立mesh data")
        for field, key in (("location_mm","object_location_mm"),("rotation_euler_radians","object_rotation_euler_radians"),
                           ("object_axis_dimensions_mm","object_axis_dimensions_mm"),("matrix_world","matrix_world")):
            if not _same_mesh_readback(item.get(field), cad[key]):
                raise ImportValidationError("最終inventory與實際重匯入raw姿態不符")
        data_names.append(item["mesh_data_name"])
    if len(set(data_names)) != 3:
        raise ImportValidationError("三個STL重匯入物件不能共用mesh datablock")
    record_path = _contained_file(Path(v["export_record_path"]), run_dir, "三試片STL版本紀錄")
    if record_path != (run_dir / "coupon-stl-export-record-v001.json").resolve() or _digest(record_path) != v.get("export_record_sha256"):
        raise ImportValidationError("三試片STL紀錄檔名／hash不符")
    record = _read_json(record_path)
    expected = {"schema_version":1,"lesson_step":"07-05","stage":"standalone_coupon_digital_stl_export_only",
        "source_scene":{"path":str(source),"sha256":spec["source_scene_sha256"]},
        "source_coupon_record":{"path":str(source_record),"sha256":spec["source_coupon_record_sha256"]},
        "draft_plan":{"path":str(plan_path),"sha256":spec["draft_plan_sha256"]},"exports":exports,"reimport":v["reimport"],"reimport_layout":v["reimport_layout"],
        "saved_new_scene":False,"geometry_modified":False,"full_box_modified":False,"exported_stl":True,"printed":False,"fit_tested":False,"slicer_checked":False,
        "geometry_scope":"No new specimen design or source shape edit; actual STL reimport creates three new mesh datablocks from the retained world vertices.",
        "reimport_mesh_datablocks_created":True,"new_specimen_design_created":False,
        "material_grade":None,"epsilon_allow":None,"effective_mechanical_length_mm":None,"improvement_validated":None,"physical_measurements":None,"fit_results":None,
        "qualified_clearance_mm":None,"qualified_strength_N":None,"support_required":None,"final_print_orientation_approved":None}
    if (not isinstance(record,dict) or set(record) != set(expected)|{"recordedAt"}
            or not isinstance(record.get("recordedAt"),str) or not record["recordedAt"]
            or not _same_mesh_readback({key:record[key] for key in expected}, expected)):
        raise ImportValidationError("三試片STL紀錄須綁來源／三件新STL／重匯入，不得代填實體或改善結果")
    return v, _validate_runner(run, run_dir, "lesson07_coupon_export")



def _atomic_json(path, value):
    """同資料夾暫存檔完成後才替換，避免中斷留下半份 JSON。"""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         prefix=".%s." % path.name, suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def import_run(run_id, project=PROJECT):
    """匯入固定、已核准的劇本；project 可供隔離的測試目錄使用。"""
    if run_id not in RUNS:
        raise ImportValidationError("未定義的 run_id：%s" % run_id)
    project = Path(project).resolve()
    spec = RUNS[run_id]
    run_dir = project / "learning" / "evidence" / spec["lesson"] / run_id
    catalog_path = project / "learning" / "catalog.json"
    original_catalog = catalog_path.read_bytes()
    catalog = json.loads(original_catalog.decode("utf-8"))
    lessons = [lesson for lesson in catalog["lessons"] if lesson["id"] == spec["lesson"]]
    if len(lessons) != 1:
        raise ImportValidationError("catalog 找不到唯一的本次單元：%s" % spec["lesson"])
    lesson_steps = {step["id"]: step for step in lessons[0]["steps"]}
    run = _read_json(run_dir / "run.json")
    if not isinstance(run, dict):
        raise ImportValidationError("run.json 必須是物件")
    _validate_records(run, run_dir, spec, lesson_steps)
    checked = None
    if run_id in ("2026-10-22-lesson05-demo-v001", "2026-10-22-lesson05-demo-v002"):
        checked = _validate_lesson05(run, run_dir)
    elif run_id in ("2026-10-22-lesson05-holes-demo-v001", "2026-10-22-lesson05-holes-demo-v002"):
        checked = _validate_lesson05_holes(run, run_dir)
    elif run_id in ("2026-10-22-lesson05-export-demo-v001", "2026-10-22-lesson05-export-demo-v002",
                    "2026-10-22-lesson05-export-demo-v003"):
        checked = _validate_lesson05_export(run, run_dir)
    elif run_id == "2026-10-22-lesson05-lid-demo-v001":
        checked = _validate_lesson05_lid(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson05-lid-export-demo-v001":
        checked = _validate_lesson05_lid_export(run, run_dir, spec)
    elif run_id in ("2026-10-25-lesson06-tenon-demo-v001", "2026-10-25-lesson06-tenon-demo-v002",
                    "2026-10-25-lesson06-tenon-demo-v003", "2026-10-25-lesson06-tenon-demo-v004",
                    "2026-10-25-lesson06-tenon-demo-v005", "2026-10-25-lesson06-tenon-demo-v006"):
        checked = _validate_lesson06_tenon(run, run_dir, spec)
    elif run_id in ("2026-10-25-lesson06-dovetail-demo-v001", "2026-10-25-lesson06-dovetail-demo-v002"):
        checked = _validate_lesson06_dovetail(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson06-dovetail-export-demo-v001":
        checked = _validate_lesson06_dovetail_export(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson08-parameters-demo-v001":
        checked = _validate_lesson08_parameters(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-parameters-demo-v001":
        checked = _validate_lesson07_parameters(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-snap-demo-v001":
        checked = _validate_lesson07_snap(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-overhang-demo-v001":
        checked = _validate_lesson07_overhang(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-snap-export-demo-v001":
        checked = _validate_lesson07_snap_export(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-coupons-demo-v001":
        checked = _validate_lesson07_coupons(run, run_dir, spec)
    elif run_id == "2026-10-25-lesson07-coupon-export-demo-v001":
        checked = _validate_lesson07_coupon_export(run, run_dir, spec)
    relative = run_dir.relative_to(project).as_posix()
    events = {}
    for record in run["records"]:
        caption = "%s 助教示範實拍：獨立 Blender %s（English (US)、出廠設定），不是你的畫面；橘框為網頁標示，原圖未修改。" % (
            record["recordedAt"][:10], run["blender"])
        figure = {"type": "screenshot", "path": "%s/%s" % (relative, Path(record["file"]).as_posix()),
                  "alt": record["action"], "caption": caption, "width": record["width"], "height": record["height"],
                  "sha256": record["sha256"], "highlights": record.get("highlights", [])}
        event = {"seq": len(events.get(record["step"], [])) + 1, "at": record["recordedAt"],
                 "action": record["action"], "observed": record["observed"], "figure": figure}
        if record.get("note"):
            event["note"] = record["note"]
        events.setdefault(record["step"], []).append(event)

    for step_id, step_events in events.items():
        step = lesson_steps[step_id]
        step["operationRun"] = {
            "id": run_id, "performedBy": "tutor", "status": "completed",
            "environment": "獨立 Blender %s（build %s）、English (US)、出廠設定與獨立設定資料夾；不使用學員的 Blender 視窗與偏好設定" % (
                run["blender"], run["buildHash"]),
            "summary": spec["summaries"][step_id], "journal": spec["journal"], "events": step_events}
        if spec.get("completion_scope"):
            step["operationRun"]["completionScope"] = spec["completion_scope"]
        # 舊的繁中介面截圖已過時（介面已切換為英文）；本步改由上方實拍呈現。
        step["figures"] = [f for f in step.get("figures", []) if not f["path"].endswith("2026-10-22-blender-default.png")]
        references = ["%s/run.json" % relative, "%s.json" % relative, spec["journal"]]
        if checked:
            references.extend(["%s/verification.json" % relative, "%s/runner-status.json" % relative])
        step["contentReview"] = {
            "status": "actual_operation_verified",
            "summary": spec.get("content_review_summary", "助教已在獨立 Blender 逐一實際操作並截圖，結果數值由 Blender 讀回；這是示範，不代表你已完成。"),
            "references": references}
    for step_id, index, key, old, new in spec["guide_edits"]:
        text = lesson_steps[step_id]["guide"][index][key]
        if old not in text and new not in text:
            raise ImportValidationError("找不到要更新的說明：%s %s" % (step_id, old))
        lesson_steps[step_id]["guide"][index][key] = text.replace(old, new)

    metadata = {
        "id": run_id, "actor": "tutor", "authorization": spec["authorization"],
        "application": "Blender %s" % run["blender"], "buildHash": run["buildHash"],
        "captureMethod": "Blender bpy.ops.screen.screenshot；獨立實例 --factory-startup --enable-event-simulate，"
                         "滑鼠／鍵盤以 Window.event_simulate 模擬；檔案瀏覽器的資料夾與檔名欄位由程式寫入",
        "script": "learning/tutor/scenarios/%s" % run["scenario"].replace("\\", "/").split("/")[-1],
        "pixelEdits": False, "highlightsDrawnBy": "教學頁 CSS 疊框（原圖未修改）",
        "learnerWorkspaceWrites": False, "demoFiles": "%s/demo-files/" % relative,
        "records": [dict(r, path="%s/%s" % (relative, Path(r["file"]).as_posix())) for r in run["records"]]}
    if checked:
        metadata["verification"] = checked[0]
        metadata["runnerStatus"] = checked[1]
        metadata["verificationEvidence"] = {
            "path": "%s/verification.json" % relative, "sha256": _digest(run_dir / "verification.json")}
        metadata["runnerEvidence"] = {
            "path": "%s/runner-status.json" % relative, "sha256": _digest(run_dir / "runner-status.json")}
    if spec.get("numeric_comparison"):
        metadata["numericComparison"] = copy.deepcopy(spec["numeric_comparison"])
    if spec.get("completion_scope"):
        metadata["completionScope"] = spec["completion_scope"]
    if spec.get("geometry_evidence_files"):
        metadata["geometryEvidence"] = [{"path": "%s/%s" % (relative, name), "sha256": _digest(run_dir / name)}
                                        for name in spec["geometry_evidence_files"]]
    if spec.get("data_evidence_files"):
        metadata["dataEvidence"] = [{"path": "%s/%s" % (relative, name), "sha256": _digest(run_dir / name)}
                                    for name in spec["data_evidence_files"]]
    if spec.get("snapshot_manifest"):
        metadata["sourceSnapshotEvidence"] = {"path": "%s/%s" % (relative, spec["snapshot_manifest"]),
                                              "sha256": _digest(run_dir / spec["snapshot_manifest"])}
    # 序列化和所有驗證先完成；metadata 成功寫入後才可替換 catalog。
    json.dumps(catalog, ensure_ascii=False)
    json.dumps(metadata, ensure_ascii=False)
    metadata_path = run_dir.parent / (run_id + ".json")
    _atomic_json(metadata_path, metadata)
    if catalog_path.read_bytes() != original_catalog:
        raise ImportValidationError("catalog 已被其他程序更新，請重新核對後匯入")
    _atomic_json(catalog_path, catalog)
    return {"steps": len(events), "records": sum(len(v) for v in events.values()), "metadata": metadata_path}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        raise SystemExit("用法：python learning/tutor/import_run.py <run_id>")
    try:
        result = import_run(sys.argv[1])
    except (ImportValidationError, OSError, ValueError, KeyError) as exc:
        raise SystemExit("不匯入：%s" % exc) from exc
    print("匯入 %d 個步驟、%d 筆操作" % (result["steps"], result["records"]))


if __name__ == "__main__":
    main()
