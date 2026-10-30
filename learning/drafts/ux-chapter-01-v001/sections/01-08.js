window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-08"] = {
  "id": "01-08",
  "title": "Dimensions 與 Scale",
  "keyPoint": "修改 X 尺寸，分別查看尺寸與縮放係數。",
  "glossary": [
    {
      "term": "Dimensions",
      "label": "Dimensions",
      "text": "所選物件沿三個方向顯示的尺寸。"
    },
    {
      "term": "Scale",
      "label": "Scale",
      "text": "物件各軸的縮放係數，不是長度單位。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-08-01",
      "title": "找到 Dimensions 與 Scale",
      "lead": "Cube / Item › Transform 找到 Dimensions 與 Scale。",
      "actions": [
        "找到 Dimensions 與 Scale，先說出目前 X 值。"
      ],
      "checks": [
        "Item 中能看見 Dimensions 三軸",
        "Scale 三軸在另一組欄位"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "已開啟時再按 <kbd>N</kbd> 會關閉；開啟側欄不代表已設定 Dimensions、Location 或單位。"
        }
      ],
      "locate": "Cube / Item › Transform",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-08-01-dims-scale.png",
          "sha256": "39d3c87192e30ec0acbcdd2a1450560e7a4b2d615c6e9ff2f0003f2738e68a9c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube Location X/Y/Z 全部 0，Item 欄位可見 Scale 1 及 Dimensions 2 m。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                176,
                20
              ],
              "label": "Location"
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
      "stepId": "ch01-01-08-02",
      "title": "把 X 尺寸改為 3 m",
      "lead": "Dimensions X 把 X 尺寸改為 3 m。",
      "actions": [
        "若從預設 <code>2 m</code> Cube 開始，只把 X 尺寸改為 <code>3 m</code>；其他起始值則先與助教確認目標。"
      ],
      "checks": [
        "Dimensions X 顯示 <code>3 m</code>",
        "從預設方塊開始時，Y、Z 仍為 <code>2 m</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "S 的數值是倍率，不是絕對尺寸；輸入 <code>3</code> 會變成原長度三倍。Dimensions 欄位才是直接設定本步的 <code>3 m</code>。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Dimensions X",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-08-02-dimension-x.png",
          "sha256": "e78abfc32b1cdacbc90eac23d947f0f3fbc10cdbef9a0fa100b0dad8af72ac28",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube 的 Dimensions X 3 m、Y/Z 2 m；Scale X 1.500、Y/Z 1.000。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                401,
                228,
                20
              ],
              "label": "Dimensio"
            },
            {
              "n": 2,
              "box": [
                963,
                319,
                228,
                20
              ],
              "label": "Scale X"
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
      "stepId": "ch01-01-08-03",
      "title": "觀察 Scale 的變化",
      "lead": "Scale X 觀察 Scale 的變化。",
      "actions": [
        "觀察 Scale X 是否跟著變化，記錄實際值。"
      ],
      "checks": [
        "從預設方塊開始時 Dimensions X 為 <code>3 m</code>",
        "同時 Scale X 顯示 <code>1.5</code>，Y、Z 為 <code>1</code>"
      ],
      "pitfalls": [],
      "locate": "Scale X",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-08-02-dimension-x.png",
          "sha256": "e78abfc32b1cdacbc90eac23d947f0f3fbc10cdbef9a0fa100b0dad8af72ac28",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube 的 Dimensions X 3 m、Y/Z 2 m；Scale X 1.500、Y/Z 1.000。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                401,
                228,
                20
              ],
              "label": "Dimensio"
            },
            {
              "n": 2,
              "box": [
                963,
                319,
                228,
                20
              ],
              "label": "Scale X"
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
