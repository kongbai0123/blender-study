window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-03"] = {
  "id": "01-03",
  "title": "準備自己的練習場景",
  "keyPoint": "準備預設場景，找到物件清單與屬性區。",
  "glossary": [
    {
      "term": "Outliner",
      "label": "Outliner",
      "text": "右上方列出場景物件的清單。"
    },
    {
      "term": "Properties",
      "label": "Properties",
      "text": "右側以直排圖示切換的屬性編輯區。"
    },
    {
      "term": "General",
      "label": "General",
      "text": "File › New 中的通用場景範本。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-03-02",
      "title": "找到 Cube、Camera、Light",
      "lead": "3D Viewport / Outliner 找到 Cube、Camera、Light。",
      "actions": [
        "在預設場景找到中央 Cube 與右上 Outliner 的 Cube、Camera、Light。"
      ],
      "checks": [
        "中央可見 Cube",
        "右上 Outliner 列出 Cube、Camera、Light"
      ],
      "pitfalls": [],
      "locate": "3D Viewport / Outliner",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-03-01-default-scene.png",
          "sha256": "e13488de369a02a0437d128539be91c82e2941e5d93b43f48052bd063056d676",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "預設 Object Mode 場景可見選中的 Cube 及 Camera、Light，沒有開啟選單。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "1 Cube（3"
            },
            {
              "n": 2,
              "box": [
                1229,
                26,
                263,
                178
              ],
              "label": "2 Outlin"
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
      "stepId": "ch01-01-03-03",
      "title": "找到 Properties 區",
      "lead": "右側 Properties 找到 Properties 區。",
      "actions": [
        "找到右側 Properties 區域，暫時不用更改設定。"
      ],
      "checks": [
        "Outliner 位於右上並列出物件名稱",
        "Properties 在它下方，以直排圖示切換屬性"
      ],
      "pitfalls": [],
      "locate": "右側 Properties",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-03-01-default-scene.png",
          "sha256": "e13488de369a02a0437d128539be91c82e2941e5d93b43f48052bd063056d676",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "預設 Object Mode 場景可見選中的 Cube 及 Camera、Light，沒有開啟選單。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "1 Cube（3"
            },
            {
              "n": 2,
              "box": [
                1229,
                26,
                263,
                178
              ],
              "label": "2 Outlin"
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
  ],
  "prep": {
    "stepId": "ch01-01-03-01",
    "title": "依畫面決定開新檔或保留",
    "actions": [
      "先依 <code>01</code>-<code>01</code> 結果處理：首次設定先核對設定；啟動畫面可選 New File 的 General，或用 File › New › General；已是預設場景就保留。"
    ],
    "checks": [
      "目前場景保留了已存在的作品，或已安全切到 General",
      "新建時預設場景出現在編輯區"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "僅在確認可另開新場景時使用；未存作品先保存，不略過提示。"
      },
      {
        "title": "輸入格式",
        "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
      }
    ],
    "locate": "目前畫面",
    "figures": [
      {
        "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-03-01-default-scene.png",
        "sha256": "e13488de369a02a0437d128539be91c82e2941e5d93b43f48052bd063056d676",
        "size": [
          1494,
          1019
        ],
        "tab": "操作位置",
        "caption": "預設 Object Mode 場景可見選中的 Cube 及 Camera、Light，沒有開啟選單。",
        "marks": [
          {
            "n": 1,
            "box": [
              547,
              401,
              141,
              153
            ],
            "label": "1 Cube（3"
          },
          {
            "n": 2,
            "box": [
              1229,
              26,
              263,
              178
            ],
            "label": "2 Outlin"
          }
        ]
      },
      {
        "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-03-02-file-new-general.png",
        "sha256": "8e8629e4825d5df1f05802c023df1e221e102d9fbce3d67ee9bbeafce09de526",
        "size": [
          1494,
          1019
        ],
        "tab": "過程狀態",
        "caption": "File › New 子選單已展開並可見 General；單張截圖不能證明已點擊 General。",
        "marks": [
          {
            "n": 1,
            "box": [
              30,
              3,
              27,
              21
            ],
            "label": "File"
          },
          {
            "n": 2,
            "box": [
              28,
              26,
              202,
              20
            ],
            "label": "New"
          },
          {
            "n": 3,
            "box": [
              240,
              26,
              200,
              20
            ],
            "label": "General"
          }
        ]
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "目前畫面 依畫面決定開新檔或保留。",
    "lead": "目前畫面 依畫面決定開新檔或保留。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson01-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
