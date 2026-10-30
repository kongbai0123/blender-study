window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["09-02"] = {
  "id": "09-02",
  "title": "燕尾滑蓋",
  "keyPoint": "做導軌、燕尾槽與滑蓋，核對滑動關係。",
  "glossary": [
    {
      "term": "Union",
      "label": "Union",
      "text": "合併兩個體積的布林模式。"
    },
    {
      "term": "SlidingLid",
      "label": "SlidingLid",
      "text": "這條燕尾分支的滑蓋名稱。"
    },
    {
      "term": "Right Orthographic",
      "label": "Right Orthographic",
      "text": "沿X觀察端面的右側正交視圖。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch09-06-02-01",
      "title": "建立導軌",
      "lead": "原04盒副本 · Object Mode / GuideTool 建立導軌。",
      "actions": [
        "先重驗原盒<code>60</code> × <code>40</code> × <code>30</code>、壁底<code>2 mm</code>。新建<code>60</code> × <code>6</code> × <code>5</code>方塊，中心Y17／Z12.5，Edit Mode複製Y−<code>34</code>，將兩條導軌工具Union到Body。"
      ],
      "checks": [
        "盒內兩側可見新增導軌",
        "Body外框維持<code>60</code>×<code>40</code>×<code>30 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "導軌底面水平懸空",
          "text": "開口朝上列印時，導軌下方有約<code>60 mm</code>長、<code>4 mm</code>寬的水平朝下面；支撐或斜面方案仍待切片與實測。"
        }
      ],
      "locate": "原04盒副本 · Object Mode / GuideTool",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-03-guide-blocks.png",
          "sha256": "0a2fe628ad11e6b0ebd89a88a399dc7563eb2ed2cc102e4ed85ee0673dc5d3c0",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "GuideTool是兩條長條，整組外框60×40×5 mm；單條寬不能由整組外框直接讀得。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "整組工具外框"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-04-guide-union.png",
          "sha256": "b1bcc1c5a15a82effaa45275052a670b6d095e8e50abf2b29ea6350257438965",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Body的Boolean設Union，工具為GuideTool；兩側加厚可見，修改器尚未套用。",
          "marks": [
            {
              "n": 1,
              "box": [
                1337,
                338,
                137,
                73
              ],
              "label": "導軌聯集設定"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-05-guides-applied.png",
          "sha256": "026367974362bd7bca5bc6c69f4273ef5dfa0ae8e632a9c66d39085e5d567e79",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "套用後Modifier清單為空，導軌加厚保留；懸空量需另查幾何。",
          "marks": [
            {
              "n": 1,
              "box": [
                1267,
                276,
                216,
                24
              ],
              "label": "聯集已套用"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-02-02",
      "title": "切出燕尾槽",
      "lead": "GrooveTool · 頂面縮放 / Boolean Difference 切出燕尾槽。",
      "actions": [
        "建立長<code>62</code>、底寬<code>3.6</code>、高<code>4 mm</code>工具，頂面沿Y縮至寬<code>2</code>，複製到Y−<code>17</code>。用Body Difference並Apply，再沿X看Right Orthographic端面。"
      ],
      "checks": [
        "Right Orthographic 可見兩個燕尾槽端面",
        "Difference已套用，槽兩端貫通"
      ],
      "pitfalls": [],
      "locate": "GrooveTool · 頂面縮放 / Boolean Difference",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-06-groove-tools.png",
          "sha256": "1116896ca9d646839c8dbee7279f08d42e353ffcbdb17e4d26922cee6434c3a8",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "兩條GrooveTool可見，整組外框62×37.6×4 mm；單槽截面須查讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "槽工具整組外框"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-08-body-grooves.png",
          "sha256": "a7f9a013a829ccfb55037488e188dc7fca264a855fde2ed258f15f8efbc48b37",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Difference套用後可見兩條長槽，盒外框仍60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                397,
                199,
                518,
                147
              ],
              "label": "後側長槽"
            },
            {
              "n": 2,
              "box": [
                310,
                467,
                532,
                155
              ],
              "label": "前側長槽"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-09-body-end-profile.png",
          "sha256": "75f83513063b274cbc10fbea3761154118f574a7c75823ef87089e47863b2afd",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Right Orthographic沿X看兩個下寬上窄的槽口；槽深、槽寬未在此圖標值。",
          "marks": [
            {
              "n": 1,
              "box": [
                435,
                339,
                47,
                36
              ],
              "label": "左端槽口"
            },
            {
              "n": 2,
              "box": [
                748,
                339,
                44,
                36
              ],
              "label": "右端槽口"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-02-03",
      "title": "建立滑蓋與燕尾榫",
      "lead": "SlidingLid · 板與燕尾榫 Union 建立滑蓋與燕尾榫。",
      "actions": [
        "建<code>60</code> × <code>40</code> × <code>2</code>板，中心Z16.2；兩榫工具長<code>60</code>、底寬<code>3.12</code>／頂寬<code>1.76</code>、高<code>3.4</code>、Y±<code>17</code>／Z13.7。Union並Apply，檢查底部及端面，再執行Select Non Manifold。"
      ],
      "checks": [
        "底視或端面可辨兩條燕尾榫",
        "SlidingLid高度約<code>5.2 mm</code>，Non Manifold檢查結果另記"
      ],
      "pitfalls": [],
      "locate": "SlidingLid · 板與燕尾榫 Union",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-11-lid-plate.png",
          "sha256": "22cd7d1b9dc4f3cd0ef8b28b5fcab08047085787754d310dc14b2fa7970c61a9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "SlidingLid初始板60×40×2 mm、Location Z16.2 mm，尚未加燕尾榫。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "初始滑蓋板"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-14-lid-underside.png",
          "sha256": "a524c1369371e2c3134cd56ba7e3ff1caa66c04904c243b7924c0c4d3f304b4b",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "滑蓋底視可辨兩條榫，Modifier清單為空；Dimensions60×40×5.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "滑蓋含榫外框"
            }
          ]
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-15-lid-end-profile.png",
          "sha256": "7d6f39f90b987a1b6d2dc1444ce9d5d7bee1c13fd286aeba973f00e148867d63",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Right Orthographic可辨兩個下寬上窄榫；盒體隱藏，不能從本圖量間隙。",
          "marks": [
            {
              "n": 1,
              "box": [
                445,
                468,
                34,
                32
              ],
              "label": "左側榫端面"
            },
            {
              "n": 2,
              "box": [
                748,
                468,
                34,
                32
              ],
              "label": "右側榫端面"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-02-04",
      "title": "核對滑動間距並另存",
      "lead": "實際網格讀值 · X方向平移 / Save As / Open 核對滑動間距並另存。",
      "actions": [
        "核對水平與法向間距，將SlidingLid移到X+<code>30</code>、<code>+62</code>並保存world mesh，再回X0。另存<code>u06_dovetail_slide_v001.blend</code>，重開比對hash及幾何。"
      ],
      "checks": [
        "移動對照包含X+<code>30</code>、<code>+62</code>及回X0",
        "紀錄將水平總差<code>0.4 mm</code>與最小法向約<code>0.196114 mm</code>分列"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "G 輸入相對位移，不是目標絕對 X；連按 <code>+30</code>、<code>+62</code> 會到 <code>+92</code>，不能替代原步要求的 X＝<code>30</code>／<code>62</code>。"
        }
      ],
      "locate": "實際網格讀值 · X方向平移 / Save As / Open",
      "figures": [
        {
          "path": "evidence/01/2026-10-27-shortcuts-demo-v001/01-07-03-translate-x-from-zero.png",
          "sha256": "e50fc34ea7578b53e759b58985c08a14e30406a812104c35432fa410326dadc5",
          "size": [
            1494,
            1019
          ],
          "caption": "Location X為0.5 m、Y與Z為0；這是基礎方塊定位結果。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                130,
                176,
                64
              ],
              "label": "位置欄位"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
