window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-06"] = {
  "id": "01-06",
  "title": "視角與找回物件",
  "keyPoint": "旋轉視角並找回 Cube，確認 Transform 未改變。",
  "glossary": [
    {
      "term": "Transform",
      "label": "Transform",
      "text": "記錄物件位置、旋轉與縮放的欄位組。"
    },
    {
      "term": "Frame Selected",
      "label": "Frame Selected",
      "text": "把視角對焦到所選物件的功能。"
    },
    {
      "term": "Rotation",
      "label": "Rotation",
      "text": "物件沿各軸的旋轉數值，與觀察視角不同。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-06-01",
      "title": "旋轉視角",
      "lead": "3D Viewport 右上導覽軸 旋轉視角。",
      "actions": [
        "本回合只試拖曳導覽軸旋轉視角；先不改物件 Transform。"
      ],
      "checks": [
        "模型在畫面中的朝向改變",
        "Cube 仍是所選物件"
      ],
      "pitfalls": [],
      "locate": "3D Viewport 右上導覽軸",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-06-01-orbit-gizmo.png",
          "sha256": "09e86034ef690a2ee09d358485f508f6b0fa6ecba8886f378e15e24001b63bff",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "User Perspective 方塊已選取；右側 Location 為 0 m，Rotation 為 0°，右上可見導覽軸。",
          "marks": [
            {
              "n": 1,
              "box": [
                1132,
                86,
                88,
                88
              ],
              "label": "導覽軸"
            },
            {
              "n": 2,
              "box": [
                558,
                402,
                119,
                147
              ],
              "label": "Cube 換了角"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-06-02",
      "title": "確認物件沒有被移動",
      "lead": "作用中 Cube / Transform 確認物件沒有被移動。",
      "actions": [
        "保持 Cube 選取，在 Properties 的物件 Transform 查看 Location 與 Rotation。",
        "旋轉視角前後比對數值，確認這是視角改變；N › Item 是可自行使用的替代入口。"
      ],
      "checks": [
        "Transform 的 Location 前後一致",
        "Rotation 前後一致"
      ],
      "pitfalls": [],
      "locate": "作用中 Cube / Transform",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-06-02-transform-unchanged.png",
          "sha256": "09e86034ef690a2ee09d358485f508f6b0fa6ecba8886f378e15e24001b63bff",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "User Perspective 方塊已選取；右側 Location 為 0 m，Rotation 為 0°，右上可見導覽軸。",
          "marks": [
            {
              "n": 1,
              "box": [
                1132,
                86,
                88,
                88
              ],
              "label": "導覽軸"
            },
            {
              "n": 2,
              "box": [
                558,
                402,
                119,
                147
              ],
              "label": "Cube 換了角"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-06-03",
      "title": "找回物件",
      "lead": "3D Viewport / Outliner 找回物件。",
      "actions": [
        "若看不到 Cube，先在 Outliner 點 Cube，再用 3D Viewport 的 View › Frame Selected 找回；畫面太近時，滑鼠放在 3D Viewport 內把滾輪往後滾縮小。"
      ],
      "checks": [
        "Outliner 的 Cube 列保持選取",
        "執行 Frame Selected 後，Cube 回到視野內"
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
      "locate": "3D Viewport / Outliner",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-06-04-view-frame-selected.png",
          "sha256": "fd46511c619b367af5f564d080e489ff5ee811950f0db230764455a2164b05f8",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "View選單有Frame Selected，右上Cube列反白。",
          "marks": [
            {
              "n": 1,
              "box": [
                189,
                156,
                232,
                23
              ],
              "label": "對焦所選"
            },
            {
              "n": 2,
              "box": [
                1284,
                113,
                207,
                21
              ],
              "label": "選取Cube"
            }
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-06-05-framed.png",
          "sha256": "3aa3cd8721d3dcb3459489a73b2d0084d800d813d3d39a63952dc0aa727894b6",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Frame Selected後方塊過近，被視窗邊界裁切；下一張需縮小。",
          "marks": [
            {
              "n": 1,
              "box": [
                68,
                83,
                134,
                37
              ],
              "label": "目前視角"
            }
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-06-06-zoom-out.png",
          "sha256": "48fd79d0db00e99165627c13b037837fbc0bde8bf49e31a9071d6ef56ddd99a4",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "縮小後Cube完整呈現在中央，右上仍選取Cube。",
          "marks": [
            {
              "n": 1,
              "box": [
                1284,
                113,
                207,
                21
              ],
              "label": "仍選取Cube"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
