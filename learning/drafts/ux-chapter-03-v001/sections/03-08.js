window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-08"] = {
  "id": "03-08",
  "title": "Edit Mode 基礎：選取、移動、內插與擠出",
  "keyPoint": "練習點邊面選取、內插與擠出，再撤回。",
  "glossary": [
    {
      "term": "Edit Mode",
      "label": "Edit Mode",
      "text": "編輯物件內部網格元素的模式。"
    },
    {
      "term": "Median",
      "label": "Median",
      "text": "所選元素的位置統計欄位，本節觀察頂面Z。"
    },
    {
      "term": "Inset",
      "label": "Inset",
      "text": "在選定面內側建立一圈輪廓。"
    },
    {
      "term": "Extrude",
      "label": "Extrude",
      "text": "從選定元素延伸出新幾何。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-edit-02",
      "title": "把練習方塊設為 20 mm",
      "lead": "Object Mode · Cube 已選取 · N 側欄 Item 把練習方塊設為 20 mm。",
      "actions": [
        "在 N 側欄把 Cube 的 Dimensions 依序輸入 <code>20mm</code>、<code>20mm</code>、<code>20mm</code>。",
        "Object › Apply › Scale（<kbd>Ctrl</kbd>+<kbd>A</kbd> › Scale）。"
      ],
      "checks": [
        "Dimensions 為 <code>20</code>×<code>20</code>×<code>20 mm</code>",
        "Scale 三欄均為 <code>1</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Ctrl</kbd>+<kbd>A</kbd> 只開選單，不直接套用 Scale；不能用它替代 Boolean／Solidify 修改器的 Apply。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Object Mode · Cube 已選取 · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-04-cube20.png",
          "sha256": "23e7bd0894cb894c01b2f2f9fc93445b4478065ef02f5813d1611d01b54f8fe6",
          "size": [
            1494,
            1019
          ],
          "caption": "Cube尺寸20×20×20 mm，Scale各1，左下顯示Apply Object Transform。",
          "marks": [
            {
              "n": 1,
              "box": [
                964,
                315,
                225,
                64
              ],
              "label": "縮放為1"
            },
            {
              "n": 2,
              "box": [
                964,
                400,
                225,
                64
              ],
              "label": "尺寸20毫米"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    },
    {
      "stepId": "ch03-edit-03",
      "title": "進 Edit Mode 切換點、邊、面",
      "lead": "滑鼠在 3D Viewport 內 進 Edit Mode 切換點、邊、面。",
      "actions": [
        "按 <kbd>Tab</kbd>（或左上模式選單）進 Edit Mode。",
        "按主鍵盤上排 <code>1</code>、<code>2</code>、<code>3</code> 分別切到點、邊、面選取，每換一種就點一下方塊上的一個元素。"
      ],
      "checks": [
        "模式選單顯示 Edit Mode",
        "點、邊、面按鈕依上排<code>1</code>、<code>2</code>、<code>3</code>切換反白"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Tab</kbd> 是切換，不是固定設成某模式；到達目標模式就停。"
        },
        {
          "title": "操作提醒",
          "text": "主鍵盤 <code>3</code> 是本次 Emulate Numpad 關閉時的面選取；Numpad <code>3</code> 是右視圖。若已改鍵位或開 Emulate Numpad，改用面選取按鈕確認。"
        }
      ],
      "locate": "滑鼠在 3D Viewport 內",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-05-vertex.png",
          "sha256": "11cfb679a6e8ad854b21f03583e134f8dcf56ff8c6f4cf062c642fda0be47278",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit Mode中選中單一頂點；Local Vertex為10、−10、10 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                150,
                27,
                22,
                23
              ],
              "label": "點選取"
            },
            {
              "n": 2,
              "box": [
                961,
                131,
                230,
                85
              ],
              "label": "局部頂點座標"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-06-edge.png",
          "sha256": "3db95ffd00a537bde39141ff773d8b1bb49be3029a561506758db2c0095165e8",
          "size": [
            1494,
            1019
          ],
          "caption": "邊選取啟用，頂部左邊線被選中；Local Median為0、−10、10 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                173,
                27,
                22,
                23
              ],
              "label": "邊選取"
            },
            {
              "n": 2,
              "box": [
                961,
                131,
                230,
                85
              ],
              "label": "局部中位座標"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-07-face.png",
          "sha256": "20ca5eb1024caefb70b94142985824c68a53c6333192a70c2c7f36dbad631f32",
          "size": [
            1494,
            1019
          ],
          "caption": "面選取啟用，頂面反白；Local Median Z為10 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                192,
                27,
                22,
                23
              ],
              "label": "面選取"
            },
            {
              "n": 2,
              "box": [
                962,
                170,
                227,
                22
              ],
              "label": "頂面Z10"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    },
    {
      "stepId": "ch03-edit-04",
      "title": "沿 Z 軸精確移動頂面",
      "lead": "Edit Mode · 面選取 · N 側欄 Item 沿 Z 軸精確移動頂面。",
      "actions": [
        "點選方塊頂面，按 <kbd>G</kbd>、再按 Z，輸入 <code>5mm</code> 後按 <kbd>Enter</kbd>。",
        "看 N 側欄 Item 的 Median Z，再按 <kbd>Ctrl</kbd>+<kbd>Z</kbd> 撤回。"
      ],
      "checks": [
        "頂面移動後 Median Z 為 <code>15 mm</code>",
        "撤回後 Median Z 回到 <code>10 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "G 是相對移動：X＝<code>1</code> 時 G X <code>0.5</code> 會到 <code>1.5</code>；欄位設 <code>0.5</code> 則直接到 <code>0.5</code>。起點為 <code>0</code> 時兩者才相同。"
        },
        {
          "title": "操作提醒",
          "text": "G X <code>-0.5</code> 向 X 負方向再移 <code>0.5</code>；正數可直接輸入 <code>0.5</code>。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Edit Mode · 面選取 · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-08-move-top.png",
          "sha256": "f6f0bebda894dca6732e8fccc29b625e35b41b89975cad52e94dd79962906d56",
          "size": [
            1494,
            1019
          ],
          "caption": "頂面上移後，Local Median Z為15 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                170,
                227,
                22
              ],
              "label": "頂面Z15"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-09-undo-move.png",
          "sha256": "9c9d08425a7784aff780d49610396de48db7e3ad0db6adbe6940fbf60b7bca97",
          "size": [
            1494,
            1019
          ],
          "caption": "撤回後頂面Local Median Z恢復10 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                170,
                227,
                22
              ],
              "label": "撤回至Z10"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    },
    {
      "stepId": "ch03-edit-05",
      "title": "內插與擠出頂面",
      "lead": "Edit Mode · 頂面已選取 內插與擠出頂面。",
      "actions": [
        "按 <kbd>I</kbd>，輸入 <code>3mm</code> 後 <kbd>Enter</kbd>：頂面內側留下一圈 <code>3 mm</code> 寬的邊。",
        "在3D Viewport保持中央面選取，按 <kbd>E</kbd> 執行 Extrude，輸入 <code>5mm</code> 後按 <kbd>Enter</kbd>：中間面沿法向往上擠出。"
      ],
      "checks": [
        "頂面內插後留一圈邊",
        "擠出後中央形成凸台，目標<code>14</code>×<code>14 mm</code>且高<code>5 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Edit Mode · 頂面已選取",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-10-inset.png",
          "sha256": "06d1e1781172dbb7d7c3eaacc4b5739afd4413698c1909220b7e88032445b1d0",
          "size": [
            1494,
            1019
          ],
          "caption": "頂面內插後中央面反白，四周形成一圈邊。",
          "marks": [
            {
              "n": 1,
              "box": [
                437,
                249,
                384,
                102
              ],
              "label": "內插中央面"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-11-extrude.png",
          "sha256": "31067761ec394371fe1e28d0cea32cab020634b89e6559d7197c7a50dd2d96a0",
          "size": [
            1494,
            1019
          ],
          "caption": "中央面擠出後形成凸台，Local Median Z為15 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                429,
                155,
                404,
                60
              ],
              "label": "擠出頂面"
            },
            {
              "n": 2,
              "box": [
                962,
                170,
                227,
                22
              ],
              "label": "頂面Z15"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    },
    {
      "stepId": "ch03-edit-06",
      "title": "撤回、隱藏與顯示",
      "lead": "Edit Mode → Object Mode 撤回、隱藏與顯示。",
      "actions": [
        "按 <kbd>Ctrl</kbd>+<kbd>Z</kbd> 兩次撤回擠出與內插，按 <kbd>Tab</kbd> 回 Object Mode。",
        "按 H（Object › Show/Hide › Hide Selected）隱藏方塊，再按 <kbd>Alt</kbd>+<kbd>H</kbd>（Show Hidden Objects）顯示回來。"
      ],
      "checks": [
        "兩次撤回後方塊恢復原狀",
        "H 後消失，<kbd>Alt</kbd>+<kbd>H</kbd> 後重新出現"
      ],
      "pitfalls": [],
      "locate": "Edit Mode → Object Mode",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-12-undo-twice.png",
          "sha256": "758cfef07c4d771be94e6e905647dc4606e26826639caf9b8fa59ebabf2bcfdb",
          "size": [
            1494,
            1019
          ],
          "caption": "撤回擠出與內插後，頂面回到完整平面，Local Median Z為10 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                170,
                227,
                22
              ],
              "label": "恢復頂面Z10"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-13-hidden.png",
          "sha256": "f1a07be0d61ec1422201268c76a52d6744b92be425737299af06bc6b0157545f",
          "size": [
            1494,
            1019
          ],
          "caption": "Cube隱藏後從視窗消失；Outliner的眼睛關閉，底部有隱藏通知。",
          "marks": [
            {
              "n": 1,
              "box": [
                1438,
                111,
                29,
                23
              ],
              "label": "隱藏狀態"
            },
            {
              "n": 2,
              "box": [
                663,
                996,
                147,
                21
              ],
              "label": "隱藏提示"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-14-shown.png",
          "sha256": "50eb09c5536ff26b34f240b0959c7b76c199626dbd4d2f032b14fe58988e9079",
          "size": [
            1494,
            1019
          ],
          "caption": "Cube重新出現，左下顯示Show Hidden Objects。",
          "marks": [
            {
              "n": 1,
              "box": [
                64,
                893,
                158,
                25
              ],
              "label": "重新顯示"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    },
    {
      "stepId": "ch03-edit-07",
      "title": "切到底部視角",
      "lead": "Object Mode · 3D Viewport 切到底部視角。",
      "actions": [
        "View › Viewpoint › Bottom，或按 <kbd>Ctrl</kbd>+<kbd>Numpad7</kbd>；Frame Selected 對焦。",
        "用數字鍵盤<code>2</code>轉回傾斜視角，或自行使用滑鼠中鍵旋轉。"
      ],
      "checks": [
        "左上視角文字顯示 Bottom Orthographic",
        "可見方塊底面，轉回後視角文字改變"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "Numpad . 是數字鍵盤小數點，與主鍵盤句點不同；本次實測主句點開 Pivot Point，數字鍵盤小數點才對焦選取。"
        },
        {
          "title": "操作提醒",
          "text": "沒有數字鍵盤的筆電可到 Edit &gt; Preferences &gt; Input &gt; Keyboard 開啟 Emulate Numpad；Blender <code>5.2.1</code> 介面提示說主鍵盤 <code>1</code>～<code>0</code> 可作數字鍵盤數字。這不表示主句點也變成 Numpad .。"
        }
      ],
      "locate": "Object Mode · 3D Viewport",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-15-bottom.png",
          "sha256": "c0a53bf7265f8a1fecb0050d84f7444171d8088b7c937a286f8719144494df7c",
          "size": [
            1494,
            1019
          ],
          "caption": "底部視角文字為Bottom Orthographic，尺寸仍20×20×20 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                64,
                83,
                149,
                23
              ],
              "label": "底部正交視圖"
            },
            {
              "n": 2,
              "box": [
                964,
                399,
                225,
                64
              ],
              "label": "尺寸不變"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-16-orbit.png",
          "sha256": "a83e50e3d13d4075d31471f385fb37cf727ee6b561f509ef4c110442f5850adc",
          "size": [
            1494,
            1019
          ],
          "caption": "轉為User Orthographic，圖中方塊又過近，尺寸仍20×20×20 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                64,
                83,
                150,
                23
              ],
              "label": "使用者正交視圖"
            },
            {
              "n": 2,
              "box": [
                964,
                399,
                225,
                64
              ],
              "label": "尺寸不變"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
          "label": "18 個 GUI 動作與幾何讀值安全摘要"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch03-edit-01",
    "title": "建立編輯練習檔",
    "actions": [
      "先保存前一個練習成果；File › New › General 新建隔離的方塊練習場景。",
      "在 Scene Properties › Units 設 Unit System=Metric、Length=Millimeters、Unit Scale=<code>0.001</code>。",
      "另存自己的練習副本 <code>u04_edit_practice_v001.blend</code>；示範實際名為 <code>u03_edit_practice_v001.blend</code>。"
    ],
    "checks": [
      "Units 為 Metric、Millimeters、<code>0.001</code>",
      "保存通知顯示自己的練習檔名"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "僅在確認可另開新場景時使用；未存作品先保存，不略過提示。"
      }
    ],
    "locate": "Blender 主視窗",
    "figures": [
      {
        "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-02-units.png",
        "sha256": "249151cac127f355174cceffd805e87ab6d86c8d09f214f192ff806372ca27f4",
        "size": [
          1494,
          1019
        ],
        "caption": "Scene Units顯示Metric、0.001000與Millimeters；Cube為2 mm。",
        "marks": [
          {
            "n": 1,
            "box": [
              1358,
              449,
              119,
              118
            ],
            "label": "毫米設定"
          },
          {
            "n": 2,
            "box": [
              964,
              399,
              224,
              63
            ],
            "label": "預設2毫米"
          }
        ],
        "tab": "操作位置"
      },
      {
        "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-03-saved-start.png",
        "sha256": "93bf1fef5b41bc2556df40748890fef5d8e6165e30d25065869d2e77d85396d0",
        "size": [
          1494,
          1019
        ],
        "caption": "底部顯示已保存u03_edit_practice_v001.blend；與學員練習檔名稱不同。",
        "marks": [
          {
            "n": 1,
            "box": [
              603,
              996,
              264,
              21
            ],
            "label": "示範保存檔名"
          }
        ],
        "tab": "過程狀態"
      }
    ],
    "keys": [],
    "references": [
      {
        "path": "evidence/03/2026-10-28-edit-practice-gui-v001/safe-summary-v001.json",
        "label": "18 個 GUI 動作與幾何讀值安全摘要"
      }
    ],
    "kind": "prep",
    "summary": "Blender 主視窗 建立編輯練習檔。",
    "lead": "Blender 主視窗 建立編輯練習檔。"
  }
};
