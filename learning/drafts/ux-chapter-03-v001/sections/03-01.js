window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-01"] = {
  "id": "03-01",
  "title": "準備訊號站工作檔",
  "keyPoint": "另建訊號站工作檔，保留上游範例。",
  "glossary": [
    {
      "term": "來源教材",
      "label": "來源教材",
      "text": "用來參考的上游檔案，與自己的練習檔分開。"
    },
    {
      "term": "Object › Delete",
      "label": "Object › Delete",
      "text": "在物件模式刪除已選物件的功能。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-01-01",
      "title": "分清範例與自己的檔",
      "lead": "自己的 Blender 工作區 分清範例與自己的檔。",
      "actions": [
        "先確認來源教材與 workspaces/<code>02</code>/ 是不同位置。"
      ],
      "checks": [
        "來源教材路徑與自己的 workspaces/<code>02</code> 分列",
        "後續保存目的地為自己的工作區"
      ],
      "pitfalls": [],
      "locate": "自己的 Blender 工作區",
      "figures": [],
      "keys": [],
      "figureNote": "已補查現行教材及原操作序列，未找到可獨立對應本步的實拍。",
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-02-01-02",
      "title": "清出建模起點",
      "lead": "新建的 General 場景 清出建模起點。",
      "actions": [
        "依目前畫面準備自己的空白建模起點；只移除已確認不需保留的預設物件（例如在 Outliner 點 Cube，再用 3D Viewport 的 Object › Delete；Camera 與 Light 留給第 <code>04</code> 章渲染）。"
      ],
      "checks": [
        "只移除已確認不需的預設物件",
        "Outliner 中仍保留供渲染使用的 Camera 與 Light"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "Edit Mode 的 X 會開不同的網格刪除選單；不要刪除前一單元的未存作品。"
        }
      ],
      "locate": "新建的 General 場景",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-01-02-object-delete.png",
          "sha256": "806b3af007268cd66ab6425ed26227af0fb880d96c6e3e9ac6a767e63e699635",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object選單底部的Delete用來刪除選中的Cube。",
          "marks": [
            {
              "n": 1,
              "box": [
                313,
                699,
                170,
                23
              ],
              "label": "刪除物件"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-01-03-deleted.png",
          "sha256": "147b3071d840a4ab4d838939256ea3d5c76164e365dc9f56ce5534def28757f1",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Outliner 中只有 Camera 與 Light；視口中不見 Cube。",
          "marks": [
            {
              "n": 1,
              "box": [
                1229,
                26,
                263,
                178
              ],
              "label": "Outliner"
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
      "stepId": "ch03-02-01-03",
      "title": "另存訊號站 v001",
      "lead": "File › Save As… 另存訊號站 v001。",
      "actions": [
        "另存 <code>learning/workspaces/02/u02_station_v001.blend</code>。"
      ],
      "checks": [
        "保存通知或重開檔名為 <code>u02_station_v001.blend</code>",
        "資料夾位於自己的 workspaces/<code>02</code>"
      ],
      "pitfalls": [],
      "locate": "File › Save As…",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-01-04-save-as-v001.png",
          "sha256": "d112cdc5d268ff267115941c106147bb95e134f3687699acce93e47b786b8a10",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Save As 對話框中檔名為 u02_station_v001.blend，按鈕可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                394,
                8,
                318,
                25
              ],
              "label": "資料夾路徑"
            },
            {
              "n": 2,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "你要按 Save"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-01-05-saved.png",
          "sha256": "ef63a568e92f0773342f6f5c6d51f0cf0ca8a5520128cf961ba7055f6e280902",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "訊號站起始檔保存成功；物件清單保留Camera、Light。",
          "marks": [
            {
              "n": 1,
              "box": [
                620,
                996,
                234,
                21
              ],
              "label": "訊號站v001"
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
