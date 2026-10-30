window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["10-05"] = {
  "id": "10-05",
  "title": "對照試片",
  "keyPoint": "逐件匯出三種臂長試片，重匯入合看。",
  "glossary": [
    {
      "term": "A_L19",
      "label": "A_L19",
      "text": "名義幾何臂長19mm的基準對照試片。"
    },
    {
      "term": "B_L17",
      "label": "B_L17",
      "text": "名義幾何臂長17mm的對照試片。"
    },
    {
      "term": "C_L21",
      "label": "C_L21",
      "text": "名義幾何臂長21mm的對照試片。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch10-07-05-02",
      "title": "逐件匯出",
      "lead": "File › Export › STL (.stl) 逐件匯出。",
      "actions": [
        "核對Selection Only開、Scale1、Scene Unit關、Binary、Y Forward／Z Up，逐件匯出<code>u07_A_L19_v001.stl</code>、<code>u07_B_L17_v001.stl</code>、<code>u07_C_L21_v001.stl</code>。"
      ],
      "checks": [
        "三個匯出檔名各對應指定試片",
        "每次Selection Only開、Scale1、Scene Unit關"
      ],
      "pitfalls": [],
      "locate": "File › Export › STL (.stl)",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-coupon-export-demo-v001/07-05-06-A_L19-export-options.png",
          "sha256": "787fb50995b0e44804a9248170bd2d1e77cb9be6527929af45df330d68b3e796",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "A_L19匯出檔名與Selection Only勾、Scale1、Scene Unit關、ASCII關皆可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                147,
                131,
                23
              ],
              "label": "僅匯出選取"
            },
            {
              "n": 2,
              "box": [
                921,
                171,
                130,
                42
              ],
              "label": "比例與單位"
            },
            {
              "n": 3,
              "box": [
                247,
                566,
                534,
                27
              ],
              "label": "A_L19檔名"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-coupon-export-demo-v001/07-05-13-B_L17-export-options.png",
          "sha256": "5b3a83b925809fbe66987d616e918c3269014c416da0ae5ceea5bad6881a29ad",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "B_L17匯出檔名及相同選項；視窗已有A_L19檔，未把兩者當同一檔。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                147,
                131,
                23
              ],
              "label": "僅匯出選取"
            },
            {
              "n": 2,
              "box": [
                921,
                171,
                130,
                42
              ],
              "label": "比例與單位"
            },
            {
              "n": 3,
              "box": [
                247,
                566,
                534,
                27
              ],
              "label": "B_L17檔名"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-coupon-export-demo-v001/07-05-20-C_L21-export-options.png",
          "sha256": "9ea4b96d526988f6c327ad563b26ffe2391d21f4fd5d980c866be13a2b40c113",
          "size": [
            1060,
            600
          ],
          "tab": "核對結果",
          "caption": "C_L21匯出檔名與Selection Only勾、Scale1、Scene Unit關、ASCII關；已有A、B兩檔。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                147,
                131,
                23
              ],
              "label": "僅匯出選取"
            },
            {
              "n": 2,
              "box": [
                921,
                171,
                130,
                42
              ],
              "label": "比例與單位"
            },
            {
              "n": 3,
              "box": [
                247,
                566,
                534,
                27
              ],
              "label": "C_L21檔名"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-coupon-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-05-03",
      "title": "重新匯入合看",
      "lead": "空白毫米場景 · Import STL 重新匯入合看。",
      "actions": [
        "設Metric／Millimeters／Unit Scale0.001，逐件實際重匯入，核對N面板、世界頂點與Select Non Manifold；最後合看三件。"
      ],
      "checks": [
        "三件重匯入後Rotation0、Scale1",
        "外框依序<code>24</code>×<code>4.6</code>×<code>9</code>、<code>22</code>×<code>4.6</code>×<code>9</code>、<code>26</code>×<code>4.6</code>×<code>9 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "空白毫米場景 · Import STL",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-07-05-edit-undo-menu.png",
          "sha256": "a322cbd6bb3ce61bc9a0151c0d21ca198704301322fd4faf31897e0f9b2f48ae",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit選單的Undo旁顯示Ctrl Z；這是基礎場景的撤回入口參照。",
          "marks": [
            {
              "n": 1,
              "box": [
                67,
                26,
                195,
                22
              ],
              "label": "撤回入口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-coupon-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch10-07-05-01",
    "title": "選取單一試片",
    "actions": [
      "每件重開來源副本，只選A_L19、B_L17或C_L21，隱藏其餘兩試片；原Body／Lid及兩工具保持隱藏。"
    ],
    "checks": [
      "作用中名稱為A_L19、B_L17或C_L21之一",
      "其餘試片、原盒、蓋與工具隱藏"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
      }
    ],
    "locate": "07-05同hash副本 · Object Mode",
    "figures": [
      {
        "path": "evidence/07/2026-10-25-lesson07-coupon-export-demo-v001/07-05-24-A_L19-reimport-dimensions.png",
        "sha256": "5a3634959a94caac6d6a50ad0a4aed7b79dc5a0f0ddaf9e4abaf4c8f54120cb0",
        "size": [
          1494,
          1019
        ],
        "caption": "A_L19_STL重新匯入，Item24／4.6／9mm，Rotation0、Scale1，臂形可見。",
        "marks": [
          {
            "n": 1,
            "box": [
              962,
              398,
              229,
              64
            ],
            "label": "A試片外框"
          }
        ],
        "tab": "操作位置"
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "07-05同hash副本 · Object Mode 選取單一試片。",
    "lead": "07-05同一來源副本 · Object Mode 選取單一試片。",
    "references": [
      {
        "path": "journal/2026-10-25-lesson07-coupon-export-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
