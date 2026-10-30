window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-04"] = {
  "id": "04-04",
  "title": "指定材質",
  "keyPoint": "替 Platform 新增材質並設定藍色。",
  "glossary": [
    {
      "term": "Material",
      "label": "Material",
      "text": "指派給表面的材質資料。"
    },
    {
      "term": "Base Color",
      "label": "Base Color",
      "text": "材質的基本顏色輸入。"
    },
    {
      "term": "Hex",
      "label": "Hex",
      "text": "用十六進位文字輸入顏色的欄位。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-04-01",
      "title": "只選 Platform",
      "lead": "Outliner / Platform 只選 Platform。",
      "actions": [
        "先只選 Platform，核對所選部件。"
      ],
      "checks": [
        "Outliner 的 Platform 列反白",
        "中央平台顯示作用中外框"
      ],
      "pitfalls": [],
      "locate": "Outliner / Platform",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-04-01-material-tab.png",
          "sha256": "4fda4b00fd0093a6528345b0ae33b8b2814bf254a7cc7dde5fafdbdb2e73d1ce",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Platform 已選取；Material 分頁空白並顯示 New 按鈕。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                194,
                150,
                20
              ],
              "label": "Platform"
            },
            {
              "n": 2,
              "box": [
                1236,
                807,
                20,
                20
              ],
              "label": "Material"
            },
            {
              "n": 3,
              "box": [
                1298,
                536,
                185,
                20
              ],
              "label": "New"
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
      "stepId": "ch04-03-04-02",
      "title": "新增材質",
      "lead": "Material Properties 新增材質。",
      "actions": [
        "在 Properties 的 Material 分頁按 New 建立材質，點名稱欄位改為 Platform_Blue。"
      ],
      "checks": [
        "Material 中已有 Platform_Blue",
        "材質指派在 Platform 上"
      ],
      "pitfalls": [],
      "locate": "Material Properties",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-04-02-material-named.png",
          "sha256": "a7ac0a814248955fc812f5f64f263e19d5a545e5d67dca9cbcca075e1786ddda",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Platform 被選取，材質名稱顯示 Platform_Blue，Base Color 白色。",
          "marks": [
            {
              "n": 1,
              "box": [
                1298,
                536,
                100,
                20
              ],
              "label": "Platform"
            },
            {
              "n": 2,
              "box": [
                1370,
                662,
                86,
                20
              ],
              "label": "Base Col"
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
      "stepId": "ch04-03-04-03",
      "title": "設定 Base Color",
      "lead": "材質 Base Color 設定 Base Color。",
      "actions": [
        "點 Base Color 色塊，在顏色選擇器的 Hex 欄輸入藍色（示範用 2F6FD8），以合適預覽核對。"
      ],
      "checks": [
        "Base Color 的 Hex 為 2F6FD8",
        "材質預覽中 Platform 呈藍色"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "材質 Base Color",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-04-03-hex.png",
          "sha256": "bb1ae9f80f65412610408dfc916ac632d4f01152032c69586bbc9527490897c4",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "色彩選擇器開啟，Hex 欄位正在編輯，內容為 2F6FD8。",
          "marks": [
            {
              "n": 1,
              "box": [
                1292,
                631,
                130,
                22
              ],
              "label": "Hex"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-04-04-blue.png",
          "sha256": "b2f9b7fdb7c406080ab021fc1ce4502d984675fdae41ad2e560b36aaeb23b1fc",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "平台顯示藍色，其他站台物件仍為灰白；Base Color 色塊為藍色。",
          "marks": [
            {
              "n": 1,
              "box": [
                478,
                421,
                270,
                147
              ],
              "label": "Platform"
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
