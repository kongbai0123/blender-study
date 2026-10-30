window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-05"] = {
  "id": "03-05",
  "title": "毫米尺寸方塊",
  "keyPoint": "切換毫米顯示，確認 Unit Scale 仍為 1。",
  "glossary": [
    {
      "term": "Unit Scale",
      "label": "Unit Scale",
      "text": "場景長度換算的比例，與顯示格式不同。"
    },
    {
      "term": "Millimeters",
      "label": "Millimeters",
      "text": "以毫米顯示長度。"
    },
    {
      "term": "Metric",
      "label": "Metric",
      "text": "公制單位系統。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-05-02",
      "title": "顯示單位改為毫米",
      "lead": "Scene Properties › Units 顯示單位改為毫米。",
      "actions": [
        "下一小回合在 Properties 的 Scene 分頁展開 Units，確認 Unit System 為 Metric，把 Length 改為 Millimeters。"
      ],
      "checks": [
        "Units 的 Unit System 為 Metric",
        "Length 顯示 Millimeters"
      ],
      "pitfalls": [],
      "locate": "Scene Properties › Units",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-03-units.png",
          "sha256": "9f5143fef9b6c82c507d8f0931b3006dc19315ad494232bd7c5e914ea2a4e446",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Scene Units 顯示 Metric、Unit Scale 1.000000、Length Meters；底部有已存檔提示。",
          "marks": [
            {
              "n": 1,
              "box": [
                1236,
                364,
                20,
                20
              ],
              "label": "Scene 分頁"
            },
            {
              "n": 2,
              "box": [
                1266,
                452,
                216,
                47
              ],
              "label": "Unit Sys"
            },
            {
              "n": 3,
              "box": [
                1266,
                547,
                216,
                20
              ],
              "label": "Length"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-04-length-list.png",
          "sha256": "ea238de84132d14c0c6d96b2710fbd02c36454eb78566a560c673d60edf32509",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Length 選單展開，當前 Meters，列表含 Millimeters。",
          "marks": [
            {
              "n": 1,
              "box": [
                1361,
                658,
                112,
                20
              ],
              "label": "Millimet"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-05-millimeters.png",
          "sha256": "84fdc99919ecf23ae59a9766fbf3ee7ff88bc297afdb4d747eeb8d9b5559a6f8",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Scene Length 設為 Millimeters；Cube 的 Dimensions X/Y/Z 均 2000 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1266,
                547,
                216,
                20
              ],
              "label": "Length：M"
            },
            {
              "n": 2,
              "box": [
                1266,
                477,
                216,
                22
              ],
              "label": "Unit Sca"
            },
            {
              "n": 3,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "Dimensio"
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
      "stepId": "ch03-02-05-03",
      "title": "核對 Unit Scale",
      "lead": "同一 Units 區域 核對 Unit Scale。",
      "actions": [
        "核對本練習 Unit Scale = <code>1.000</code>，記錄實際值。"
      ],
      "checks": [
        "Unit Scale 顯示 <code>1.000</code>",
        "未縮小的預設 Cube 尺寸仍是 <code>2000 mm</code>"
      ],
      "pitfalls": [],
      "locate": "同一 Units 區域",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-03-units.png",
          "sha256": "9f5143fef9b6c82c507d8f0931b3006dc19315ad494232bd7c5e914ea2a4e446",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Scene Units 顯示 Metric、Unit Scale 1.000000、Length Meters；底部有已存檔提示。",
          "marks": [
            {
              "n": 1,
              "box": [
                1236,
                364,
                20,
                20
              ],
              "label": "Scene 分頁"
            },
            {
              "n": 2,
              "box": [
                1266,
                452,
                216,
                47
              ],
              "label": "Unit Sys"
            },
            {
              "n": 3,
              "box": [
                1266,
                547,
                216,
                20
              ],
              "label": "Length"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-05-millimeters.png",
          "sha256": "84fdc99919ecf23ae59a9766fbf3ee7ff88bc297afdb4d747eeb8d9b5559a6f8",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Scene Length 設為 Millimeters；Cube 的 Dimensions X/Y/Z 均 2000 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1266,
                547,
                216,
                20
              ],
              "label": "Length：M"
            },
            {
              "n": 2,
              "box": [
                1266,
                477,
                216,
                22
              ],
              "label": "Unit Sca"
            },
            {
              "n": 3,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "Dimensio"
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
  ],
  "prep": {
    "stepId": "ch03-02-05-01",
    "title": "另存毫米方塊檔",
    "actions": [
      "先另開獨立練習並存為 <code>learning/workspaces/02/u02_mm_block_v001.blend</code>。"
    ],
    "checks": [
      "目前檔名為 <code>u02_mm_block_v001.blend</code>",
      "原訊號站檢查點仍保留在自己的工作區"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "僅在確認可另開新場景時使用；未存作品先保存，不略過提示。"
      }
    ],
    "locate": "File › New / Save As…",
    "figures": [
      {
        "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-01-new-general.png",
        "sha256": "214496c6e05b11b6f0681e97a9ae4d81f771e7807a035becca4824d1474bf455",
        "size": [
          1494,
          1019
        ],
        "tab": "操作位置",
        "caption": "畫面顯示預設 Cube、Camera、Light；Cube 選取。",
        "marks": [
          {
            "n": 1,
            "box": [
              547,
              401,
              141,
              153
            ],
            "label": "預設 Cube"
          }
        ]
      },
      {
        "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-05-02-save-as-mm.png",
        "sha256": "7a2eb6f75d5807776e767f6345e70351c20f0a4bca83f0b9615c81c2eee9d25c",
        "size": [
          1060,
          600
        ],
        "tab": "過程狀態",
        "caption": "Save As 對話框中檔名 u02_mm_block_v001.blend。",
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
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "File › New / Save As… 另存毫米方塊檔。",
    "lead": "File › New / Save As… 另存毫米方塊檔。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
