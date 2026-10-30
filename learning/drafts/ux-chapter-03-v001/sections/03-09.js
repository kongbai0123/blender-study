window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-09"] = {
  "id": "03-09",
  "title": "建立毫米工作檔",
  "keyPoint": "另建原盒場景，設定毫米與 0.001 比例。",
  "glossary": [
    {
      "term": "Units",
      "label": "Units",
      "text": "Scene Properties 中的場景單位設定區。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-04-02-01",
      "title": "開新檔",
      "lead": "File › New › General 開新檔。",
      "actions": [
        "開一個新的預設場景。"
      ],
      "checks": [
        "3D Viewport 中可見預設 Cube",
        "Outliner 列出 Camera、Cube、Light"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "僅在確認可另開新場景時使用；未存作品先保存，不略過提示。"
        }
      ],
      "locate": "File › New › General",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-02-01-units-before.png",
          "sha256": "928e01f54e4a890d2a05c3032efb73607deac90ef62eaa383a186c4810170d92",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Scene Units顯示Metric、Unit Scale1.000000、LengthMeters，與units-before原圖說明相符。",
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
                477,
                216,
                22
              ],
              "label": "Unit Sca"
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
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-04-02-02",
      "title": "設定毫米單位",
      "lead": "Properties 的 Scene 分頁 › Units 設定毫米單位。",
      "actions": [
        "在 Properties 的 Scene 分頁 › Units 把 Length 改為 Millimeters，Unit Scale 輸入 <code>0.001</code>。"
      ],
      "checks": [
        "Units 的 Length 為 Millimeters，Unit Scale 為 <code>0.001</code>",
        "預設 Cube 的 Dimensions 三軸為 <code>2 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Properties 的 Scene 分頁 › Units",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-02-02-units-mm.png",
          "sha256": "851ddbd24f1e206822492068c5549f3218b9ec25b37d6a7597f0bb0d50bf5fb9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Units改為Metric/.001000/Millimeters，N面板Cube尺寸2mm三軸且Scale1。可見初始Cube在換單位後的實際尺寸，不能推後續新加primitive亦為2mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1266,
                477,
                216,
                22
              ],
              "label": "Unit Sca"
            },
            {
              "n": 2,
              "box": [
                1266,
                547,
                216,
                20
              ],
              "label": "Length：M"
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
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-04-02-03",
      "title": "另存 u04_box_v001",
      "lead": "File › Save As… 另存 u04_box_v001。",
      "actions": [
        "另存 <code>learning/workspaces/04/u04_box_v001.blend</code>。"
      ],
      "checks": [
        "保存成功通知出現 <code>u04_box_v001.blend</code>",
        "自己的 workspaces/<code>04</code> 中有該場景檔"
      ],
      "pitfalls": [],
      "locate": "File › Save As…",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-02-03-save-as-v001.png",
          "sha256": "2c68998c5343f73b051198702a970e7098b8547e626b1684adcdee95016097a5",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Save As檔案視窗檔名u04_box_v001.blend，頂欄顯示D:專案工作路徑、左側含PPT自訂捷徑與磁碟標籤；僅為待確認視窗，不能證明保存完成；公開前需個資審查。",
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
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
