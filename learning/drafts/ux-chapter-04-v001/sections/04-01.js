window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-01"] = {
  "id": "04-01",
  "title": "準備渲染工作檔",
  "keyPoint": "從訊號站檢查點另存渲染副本。",
  "glossary": [
    {
      "term": "渲染工作檔",
      "label": "渲染工作檔",
      "text": "用來調相機、材質與燈光的獨立場景副本。"
    },
    {
      "term": "來源版本",
      "label": "來源版本",
      "text": "渲染副本另存之前使用的訊號站檢查點。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-01-02",
      "title": "另存渲染工作檔",
      "lead": "File › Save As… 另存渲染工作檔。",
      "actions": [
        "File › Save As 另存 <code>learning/workspaces/03/u03_render_v001.blend</code>。"
      ],
      "checks": [
        "保存通知顯示 <code>u03_render_v001.blend</code>",
        "目的地在自己的 workspaces/<code>03</code>"
      ],
      "pitfalls": [],
      "locate": "File › Save As…",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-01-03-save-as-render.png",
          "sha256": "c481a67e270a994bc8940dcf597dffff5b8c59c8dfa78352b291bced4d0ee4d7",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Save As 對話框檔名為 u03_render_v001.blend。",
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
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-01-04-saved.png",
          "sha256": "5c7e4c8eda1fba7f007f85e512af3a579ffe3597467ac582b1a48328f3698cef",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "底部通知為已保存u03_render_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                621,
                996,
                235,
                21
              ],
              "label": "渲染副本保存"
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
      "stepId": "ch04-03-01-03",
      "title": "記下來源版本",
      "lead": "本次筆記 / 版本紀錄 記下來源版本。",
      "actions": [
        "把實際來源 .blend 路徑與其已登記的版本／雜湊記入筆記。渲染或匯出成果再關聯本單元的場景版本；目前場景另存本身沒有跨單元來源關聯欄位。"
      ],
      "checks": [
        "筆記列出來源訊號站的路徑與版本",
        "另列渲染副本的路徑，兩者可逐一對照"
      ],
      "pitfalls": [],
      "locate": "本次筆記 / 版本紀錄",
      "figures": [],
      "keys": [],
      "figureNote": "已補查現行教材及原操作序列，未找到可獨立對應本步的實拍。",
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch04-03-01-01",
    "title": "開啟訊號站檢查點",
    "actions": [
      "File › Open（<kbd>Ctrl</kbd>+<kbd>O</kbd>）開啟第 <code>03</code> 章保存的訊號站檢查點；在檔案視窗核對路徑及檔名。",
      "開啟後核對 Outliner 的 Station 部件；若視窗有標題列可再比對檔名。"
    ],
    "checks": [
      "File › Open 選到自己的訊號站檢查點",
      "重開後 Outliner 中有 Station 部件"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
      }
    ],
    "locate": "File › Open…",
    "figures": [
      {
        "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-01-01-open-station.png",
        "sha256": "c4494ed5e691b534828b4c42d24179f6ed3c972b1c1c9fab20720e7155b164a9",
        "size": [
          1060,
          600
        ],
        "tab": "操作位置",
        "caption": "Open 對話框列出 station v002，檔名欄已填同名。",
        "marks": [
          {
            "n": 1,
            "box": [
              789,
              566,
              126,
              25
            ],
            "label": "按 Open"
          }
        ]
      },
      {
        "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-01-02-station-opened.png",
        "sha256": "02d2e8273660026ea0daa69d4bc95534a8957e6bd63ae8ce859a8803666e1721",
        "size": [
          1494,
          1019
        ],
        "tab": "過程狀態",
        "caption": "Outliner的Station已展開並列出五個訊號站部件。",
        "marks": [
          {
            "n": 1,
            "box": [
              1254,
              129,
              175,
              124
            ],
            "label": "部件與集合"
          }
        ]
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "File › Open… 開啟訊號站檢查點。",
    "lead": "File › Open… 開啟訊號站檢查點。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
