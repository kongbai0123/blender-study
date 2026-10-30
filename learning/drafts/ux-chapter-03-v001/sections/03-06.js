window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-06"] = {
  "id": "03-06",
  "title": "輸入並核對毫米尺寸",
  "keyPoint": "以帶單位的數值輸入 40×30×10 mm。",
  "glossary": [
    {
      "term": "40mm",
      "label": "40mm",
      "text": "帶單位的欄位輸入，用來明確指定40毫米。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-06-01",
      "title": "輸入 X 40 mm",
      "lead": "Cube / Dimensions X 輸入 X 40 mm。",
      "actions": [
        "本回合在 Sidebar 的 Dimensions X 輸入 <code>40mm</code>（帶單位），只改 X。"
      ],
      "checks": [
        "Dimensions X 顯示 <code>40 mm</code>",
        "記錄換算 <code>40 mm</code>＝<code>0.04 m</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "已開啟時再按 <kbd>N</kbd> 會關閉；開啟側欄不代表已設定 Dimensions、Location 或單位。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Cube / Dimensions X",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-06-01-x-40.png",
          "sha256": "fb25818060bcab86da4df6c87ce71caebf066a9d4ce26d476f287d73ce3df782",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Dimensions X 40 mm、Y/Z 2000 mm，Scale X 0.020。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                401,
                228,
                20
              ],
              "label": "X = 40 m"
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
      "stepId": "ch03-02-06-02",
      "title": "輸入 Y、Z",
      "lead": "下一小回合 / Dimensions Y、Z 輸入 Y、Z。",
      "actions": [
        "分兩次再輸入 Y = <code>30 mm</code>、Z = <code>10 mm</code>。"
      ],
      "checks": [
        "Dimensions Y 顯示 <code>30 mm</code>",
        "Dimensions Z 顯示 <code>10 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "下一小回合 / Dimensions Y、Z",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-06-02-yz.png",
          "sha256": "de60a3e441aec46dde03c91ad9960eddef451261951a1ac1cacc59f24cce93a7",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Dimensions X 40 mm、Y 30 mm、Z 10 mm，方塊在視口中很小。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "40 × 30 "
            },
            {
              "n": 2,
              "box": [
                963,
                300,
                228,
                77
              ],
              "label": "Scale"
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
      "stepId": "ch03-02-06-03",
      "title": "逐欄核對",
      "lead": "Dimensions / Scale 逐欄核對。",
      "actions": [
        "逐欄核對三方向與單位，記下 Scale 實際值。"
      ],
      "checks": [
        "Dimensions 三欄依序為 <code>40</code>、<code>30</code>、<code>10 mm</code>",
        "筆記另列實際 Scale 數值，與尺寸分開"
      ],
      "pitfalls": [],
      "locate": "Dimensions / Scale",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-06-02-yz.png",
          "sha256": "de60a3e441aec46dde03c91ad9960eddef451261951a1ac1cacc59f24cce93a7",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Dimensions X 40 mm、Y 30 mm、Z 10 mm，方塊在視口中很小。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "40 × 30 "
            },
            {
              "n": 2,
              "box": [
                963,
                300,
                228,
                77
              ],
              "label": "Scale"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-06-03-framed.png",
          "sha256": "775465ea6179155996315530ff76092b657fd81ffe7c9ec4cde095df3662e199",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "選取方塊已放大且完整可見；右欄尺寸仍為 40×30×10 mm。",
          "marks": [
            {
              "n": 1,
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
  ]
};
