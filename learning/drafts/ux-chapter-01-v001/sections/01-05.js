window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-05"] = {
  "id": "01-05",
  "title": "選取物件與 Object Mode",
  "keyPoint": "選取 Cube，對照模式、外框與清單反白。",
  "glossary": [
    {
      "term": "Object Mode",
      "label": "Object Mode",
      "text": "以整個物件為選取與變換單位的模式。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-05-01",
      "title": "核對 Object Mode",
      "lead": "3D Viewport 左上 核對 Object Mode。",
      "actions": [
        "找到模式選單並核對 Object Mode；若不是，先回報目前模式。"
      ],
      "checks": [
        "左上模式選單顯示 Object Mode",
        "目前編輯區為 3D Viewport"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Tab</kbd> 是切換，不是固定設成某模式；到達目標模式就停。"
        }
      ],
      "locate": "3D Viewport 左上",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-05-01-mode-menu.png",
          "sha256": "e97ee7415f69534627ac273b82aa517df317f0c2ac04b49a27031d5a49494f5a",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "模式下拉選單已展開並選 Object Mode。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                28,
                112,
                20
              ],
              "label": "目前模式"
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
      "stepId": "ch01-01-05-02",
      "title": "選取 Cube",
      "lead": "3D Viewport 中央 Cube 選取 Cube。",
      "actions": [
        "單擊 Cube，只選一個物件。"
      ],
      "checks": [
        "Cube 周圍出現作用中外框",
        "其他物件沒有同時被選取"
      ],
      "pitfalls": [],
      "locate": "3D Viewport 中央 Cube",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-05-02-deselect.png",
          "sha256": "7397e48014f30ba07aae1f23ca3ed934fe39f4cccc7275872aa4a4549d852c9d",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "中央方塊不再呈橘色選取外框，為裁切視圖，不能從圖檢查 Outliner。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "Cube 沒有橘"
            }
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-05-03-select-cube.png",
          "sha256": "01bf238d99bcd2469a79916d7f8e3677f23c3d444a09ed8136b5d87a9d9f710d",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Object Mode、完整 Cube，未看到新增擠出幾何；可作模式錯誤的狀態參照，單張圖不能證明 E 的事件本身。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "Cube 橘色外"
            },
            {
              "n": 2,
              "box": [
                1286,
                114,
                140,
                20
              ],
              "label": "Outliner"
            },
            {
              "n": 3,
              "box": [
                49,
                28,
                112,
                20
              ],
              "label": "Object M"
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
      "stepId": "ch01-01-05-03",
      "title": "對照 Outliner",
      "lead": "右上 Outliner 對照 Outliner。",
      "actions": [
        "對照反白項目是否為 Cube。"
      ],
      "checks": [
        "Outliner 的 Cube 列反白",
        "反白名稱對應中央有外框的方塊"
      ],
      "pitfalls": [],
      "locate": "右上 Outliner",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-05-03-select-cube.png",
          "sha256": "01bf238d99bcd2469a79916d7f8e3677f23c3d444a09ed8136b5d87a9d9f710d",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object Mode、完整 Cube，未看到新增擠出幾何；可作模式錯誤的狀態參照，單張圖不能證明 E 的事件本身。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "Cube 橘色外"
            },
            {
              "n": 2,
              "box": [
                1286,
                114,
                140,
                20
              ],
              "label": "Outliner"
            },
            {
              "n": 3,
              "box": [
                49,
                28,
                112,
                20
              ],
              "label": "Object M"
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
