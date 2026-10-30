window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-03"] = {
  "id": "04-03",
  "title": "安排燈光",
  "keyPoint": "只改燈光 Power，用預覽比較亮度。",
  "glossary": [
    {
      "term": "Power",
      "label": "Power",
      "text": "所選燈光的功率欄位。"
    },
    {
      "term": "Rendered",
      "label": "Rendered",
      "text": "使用場景光照與材質計算的視窗預覽模式。"
    },
    {
      "term": "Object Data",
      "label": "Object Data",
      "text": "Properties 中所選燈光資料的分頁。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-03-01",
      "title": "選取燈光",
      "lead": "Outliner / Light 選取燈光。",
      "actions": [
        "先選取一盞燈；沒有燈時，依實況新增一盞再核對。"
      ],
      "checks": [
        "Outliner 中本次燈光列反白",
        "Properties 可切到燈光的 Object Data"
      ],
      "pitfalls": [],
      "locate": "Outliner / Light",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-03-01-rendered-before.png",
          "sha256": "5c1e7b8c993e0f852734c9b14cad7d905208c26f251d739145b8b7344054fd11",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Light 已選取，右側光源分頁及 Power 1000.000，Rendered 模式啟用，可見陰影。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                114,
                150,
                20
              ],
              "label": "Light"
            },
            {
              "n": 2,
              "box": [
                1179,
                29,
                19,
                19
              ],
              "label": "Rendered"
            },
            {
              "n": 3,
              "box": [
                1352,
                624,
                103,
                20
              ],
              "label": "Power"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch04-03-03-02",
      "title": "只調整 Power",
      "lead": "Light Data / Power 只調整 Power。",
      "actions": [
        "在 Properties 的燈泡圖示分頁（Object Data）記下 Power 原值，只改這一個數值。"
      ],
      "checks": [
        "Power 欄顯示本次設定值",
        "筆記分列修改前後的 Power"
      ],
      "pitfalls": [],
      "locate": "Light Data / Power",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-03-01-rendered-before.png",
          "sha256": "5c1e7b8c993e0f852734c9b14cad7d905208c26f251d739145b8b7344054fd11",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Light 已選取，右側光源分頁及 Power 1000.000，Rendered 模式啟用，可見陰影。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                114,
                150,
                20
              ],
              "label": "Light"
            },
            {
              "n": 2,
              "box": [
                1179,
                29,
                19,
                19
              ],
              "label": "Rendered"
            },
            {
              "n": 3,
              "box": [
                1352,
                624,
                103,
                20
              ],
              "label": "Power"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-03-02-power-after.png",
          "sha256": "f7965606c7c212e483694a04ebae21d8c50c26b00c6313939f449c25960872c5",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Light 的 Power 為 2000.000；前後相較受照部分變亮。",
          "marks": [
            {
              "n": 1,
              "box": [
                1352,
                624,
                103,
                20
              ],
              "label": "Power"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch04-03-03-03",
      "title": "用 Rendered 預覽比較",
      "lead": "當前可用的光照預覽 用 Rendered 預覽比較。",
      "actions": [
        "3D Viewport 右上把著色切到 Rendered（四個圓形按鈕的最右邊），比較亮度與陰影；看不到變化時先回報預覽模式。"
      ],
      "checks": [
        "視窗著色切到 Rendered",
        "同一取景下的亮度或陰影變化可比較"
      ],
      "pitfalls": [],
      "locate": "當前可用的光照預覽",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-03-01-rendered-before.png",
          "sha256": "5c1e7b8c993e0f852734c9b14cad7d905208c26f251d739145b8b7344054fd11",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Light 已選取，右側光源分頁及 Power 1000.000，Rendered 模式啟用，可見陰影。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                114,
                150,
                20
              ],
              "label": "Light"
            },
            {
              "n": 2,
              "box": [
                1179,
                29,
                19,
                19
              ],
              "label": "Rendered"
            },
            {
              "n": 3,
              "box": [
                1352,
                624,
                103,
                20
              ],
              "label": "Power"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-03-02-power-after.png",
          "sha256": "f7965606c7c212e483694a04ebae21d8c50c26b00c6313939f449c25960872c5",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Light 的 Power 為 2000.000；前後相較受照部分變亮。",
          "marks": [
            {
              "n": 1,
              "box": [
                1352,
                624,
                103,
                20
              ],
              "label": "Power"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
