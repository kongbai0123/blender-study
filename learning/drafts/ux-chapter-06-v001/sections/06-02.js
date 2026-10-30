window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["06-02"] = {
  "id": "06-02",
  "title": "匯出試片並重新匯入核對",
  "keyPoint": "分別匯出插銷與孔板，重匯入核對。",
  "glossary": [
    {
      "term": "Apply Modifiers",
      "label": "Apply Modifiers",
      "text": "匯出時使用修改器計算後結果的選項。"
    },
    {
      "term": "ASCII",
      "label": "ASCII",
      "text": "STL的文字形式；本節不勾選而使用二進位形式。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch06-05-04-01",
      "title": "匯出插銷 STL",
      "lead": "Object Mode · File › Export › STL (.stl) 匯出插銷 STL。",
      "actions": [
        "開啟 <code>u05_fit_coupon_v001.blend</code>，只選 FitPin，File › Export › STL (.stl)。",
        "右側選項：勾 Selection Only、Scale <code>1</code>、Scene Unit 不勾、Apply Modifiers 勾、ASCII 不勾、Forward Axis Y、Up Axis Z。存成 <code>learning/workspaces/05/exports/u05_fit_pin_v001.stl</code>。"
      ],
      "checks": [
        "匯出前只選 FitPin",
        "指定目錄產生 <code>u05_fit_pin_v001.stl</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
        }
      ],
      "locate": "Object Mode · File › Export › STL (.stl)",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-03-pin-export-menu.png",
          "sha256": "449f2cc07be4845ce96756aa76ac98265d5b7846e4ae30f7969a1fb9491bf2f1",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "File › Export 子選單展開，STL (.stl) 醒目顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                28,
                307,
                202,
                20
              ],
              "label": "Export"
            },
            {
              "n": 2,
              "box": [
                236,
                426,
                244,
                20
              ],
              "label": "STL (.st"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-05-pin-export-options.png",
          "sha256": "316c22ebed0ae2b4865c65f15d66dce8570e445e9530efaa3af09ac23f18d5c9",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "同一匯出對話框，Selection Only 已勾、Scale 1、Scene Unit 未勾。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                148,
                135,
                22
              ],
              "label": "Selectio"
            },
            {
              "n": 2,
              "box": [
                920,
                170,
                135,
                43
              ],
              "label": "Scale 1 "
            },
            {
              "n": 3,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Export S"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-06-pin-stl-checked.png",
          "sha256": "ab6c2ae598a26036bb38974629197f93fe188a8a9a60609aa3b43bc9e7fd47e2",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "FitPin尺寸10×10×8 mm，底部顯示匯出成功。",
          "marks": [
            {
              "n": 1,
              "box": [
                643,
                996,
                186,
                21
              ],
              "label": "匯出成功"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "插銷外框"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-05-04-04",
      "title": "匯出孔板 STL",
      "lead": "u05_hole_plate_v001.blend · Object Mode 匯出孔板 STL。",
      "actions": [
        "開啟 <code>u05_hole_plate_v001.blend</code>，只選 Plate（Cutters 保持隱藏）。",
        "用相同選項匯出 <code>learning/workspaces/05/exports/u05_hole_plate_v001.stl</code>。"
      ],
      "checks": [
        "匯出前只選 Plate，Cutters保持隱藏",
        "指定目錄產生 <code>u05_hole_plate_v001.stl</code>"
      ],
      "pitfalls": [],
      "locate": "u05_hole_plate_v001.blend · Object Mode",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-09-hole_plate-export-menu.png",
          "sha256": "ba2974caa1d85f469cdb2e1418e6e472b2ecbb576cf31b820613611db1a818df",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "File › Export 子選單中 STL (.stl) 醒目。",
          "marks": [
            {
              "n": 1,
              "box": [
                28,
                307,
                202,
                20
              ],
              "label": "Export"
            },
            {
              "n": 2,
              "box": [
                236,
                426,
                244,
                20
              ],
              "label": "STL (.st"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-11-hole_plate-export-options.png",
          "sha256": "6d259aaad42e4b4fb7eba90e0bcc2966a186e7e9922eaf511a68d453c106fef7",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "匯出對話框 Selection Only 已勾、Scale 1、Scene Unit 未勾。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                148,
                135,
                22
              ],
              "label": "Selectio"
            },
            {
              "n": 2,
              "box": [
                920,
                170,
                135,
                43
              ],
              "label": "Scale 1 "
            },
            {
              "n": 3,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Export S"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-12-hole_plate-stl-checked.png",
          "sha256": "0f02d0924db0fe28e4230b27478820b768bb49874f7a35ba4f4c8bb00c3b9583",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Plate六孔俯視，底部顯示匯出成功；目前仍是來源物件。",
          "marks": [
            {
              "n": 1,
              "box": [
                643,
                996,
                186,
                21
              ],
              "label": "孔板匯出成功"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-05-04-02",
      "title": "重新匯入核對尺寸",
      "lead": "STL 實檔解析 · 空白毫米場景重新匯入 重新匯入核對尺寸。",
      "actions": [
        "保留既有作品，File › New › General；Scene Units 設 Millimeters 與 Unit Scale <code>0.001</code>。File › Import › STL，依序匯入兩份 STL（Scale <code>1</code>）。",
        "分別選取插銷與孔板，在 N 側欄核對尺寸；逐一在 Edit Mode 切邊選取、取消選取，再執行 Select › Select All by Trait › Non Manifold。"
      ],
      "checks": [
        "重匯入後插銷<code>10</code>×<code>10</code>×<code>8</code>、孔板<code>96</code>×<code>26</code>×<code>4 mm</code>",
        "逐件執行 Non Manifold，記錄實際反白結果"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "只加速對焦與開欄；不能代替 STL 尺寸解析、重匯入、單位或非流形檢查。主鍵盤句點不等於 Numpad .。"
        }
      ],
      "locate": "STL 實檔解析 · 空白毫米場景重新匯入",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-13-empty-mm-scene.png",
          "sha256": "df2a5c2a188dd9ee9da153082857debb20fb38264747d612dd577c367cbc4056",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "重新匯入前，空場景已設Metric、Millimeters與Unit Scale0.001。",
          "marks": [
            {
              "n": 1,
              "box": [
                1357,
                449,
                123,
                119
              ],
              "label": "匯入場景單位"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-15-pin-reimported.png",
          "sha256": "500102cce1362e4b7d1245888a1f7c268fe9952b2e34aadb614d13e2dab53cd7",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "插銷STL已匯入並被選中；此圖未展開Item，尺寸需看後續欄位或讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                1284,
                91,
                169,
                23
              ],
              "label": "匯入的插銷"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-export-demo-v003/05-04-17-hole_plate-reimported.png",
          "sha256": "6e0a57531b4341284eaae57cee320aa6698313f10de4e8df094359607c20a7fc",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "匯入孔板斜視可見六通孔及各組凹點；Item尚未展開。",
          "marks": [
            {
              "n": 1,
              "box": [
                397,
                460,
                421,
                84
              ],
              "label": "凹點識別"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-05-04-05",
      "title": "登記兩份 STL",
      "lead": "教學頁「檔案版本」 登記兩份 STL。",
      "actions": [
        "以單元 <code>05</code> 登記兩份 STL（用途：列印／其他輸出；來源分別選插銷與孔板的 .blend）。"
      ],
      "checks": [
        "版本表有兩份STL",
        "兩列各自關聯正確插銷或孔板來源場景"
      ],
      "pitfalls": [],
      "locate": "教學頁「檔案版本」",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/printing-measurement-protocol-v001.json",
          "label": "現場列印、量測與試配方法（沒有結果）"
        },
        {
          "path": "journal/templates/fit-coupon-records-v002.csv",
          "label": "六孔名義設計與空白實測 CSV"
        },
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步核對教學頁的檔案版本表；沒有登記畫面實拍，請以自己的實際紀錄為準。"
    }
  ]
};
