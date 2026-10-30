window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["05-01"] = {
  "id": "05-01",
  "title": "方形插銷",
  "keyPoint": "製作 10×10×8 mm 插銷並保存檢查點。",
  "glossary": [
    {
      "term": "FitPin",
      "label": "FitPin",
      "text": "本節方形插銷的物件名稱。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch05-05-02-02",
      "title": "做 10 × 10 × 8 mm 插銷",
      "lead": "Sidebar › Dimensions 做 10 × 10 × 8 mm 插銷。",
      "actions": [
        "選 Cube，在 N 側欄把 Dimensions 輸入 <code>10mm</code>、<code>10mm</code>、<code>8mm</code>，按 <kbd>F2</kbd> 改名 FitPin。",
        "Object › Apply › Scale（<kbd>Ctrl</kbd>+<kbd>A</kbd> › Scale）。"
      ],
      "checks": [
        "Outliner 名稱為 FitPin，Dimensions為<code>10</code>×<code>10</code>×<code>8 mm</code>",
        "Scale 三軸均為<code>1</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Ctrl</kbd>+<kbd>A</kbd> 只開選單，不直接套用 Scale；不能用它替代 Boolean／Solidify 修改器的 Apply。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Sidebar › Dimensions",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-03-02-apply-menu.png",
          "sha256": "534165b57a361df62655ab91e707b378382f53ad9ad1b3c794ded18519306a18",
          "size": [
            1494,
            1019
          ],
          "caption": "Object › Apply子選單的Scale已反白；右側Scale尚為30、20、15。",
          "marks": [
            {
              "n": 1,
              "box": [
                492,
                168,
                216,
                24
              ],
              "label": "套用縮放"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-02-03",
      "title": "保存並登記插銷檔",
      "lead": "File 選單 · 教學頁「檔案版本」 保存並登記插銷檔。",
      "actions": [
        "在 Blender 保存第<code>2</code>步對 FitPin 的改動：File › Save 或 <kbd>Ctrl</kbd>+<kbd>S</kbd>；若檔案已登記，先另存尚未使用的新版本。",
        "重開剛保存的檔案，確認 FitPin <code>10</code>×<code>10</code>×<code>8 mm</code>，再到教學頁「檔案版本」選單元<code>05</code>、實際保存的檔案與「場景 .blend」登記。",
        "登記後核對路徑與 SHA-<code>256</code>；後續修改先另存新版本。"
      ],
      "checks": [
        "重開後 FitPin 尺寸仍為<code>10</code>×<code>10</code>×<code>8 mm</code>",
        "版本表列出實際場景路徑及 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "File 選單 · 教學頁「檔案版本」",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-demo-v002/05-02-11-saved.png",
          "sha256": "8253b0f090fcffbdca00dbc3184cddde5230f8bb3bc5913bbd09b4ebd7d22473",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "FitPin尺寸10×10×8 mm，底部顯示已保存u05_fit_coupon_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "插銷尺寸"
            },
            {
              "n": 2,
              "box": [
                576,
                996,
                288,
                21
              ],
              "label": "插銷保存提示"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-demo-v002/05-02-12-reopen-dialog.png",
          "sha256": "c9f6702dea5c70fa8137e7b4007c5a2aa2f10b4528343507f2facd21d5f57486",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Open 對話框列出 u05_fit_coupon_v001.blend，檔名欄同名。",
          "marks": [
            {
              "n": 1,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Open"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-demo-v002/05-02-13-reopened-verified.png",
          "sha256": "80a7a51e87961d9be3d03a796ca0017ef15b31d53f79a3af5367b2e96b292f44",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "FitPin 被選取，尺寸 10×10×8 mm、Scale 三軸 1。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                318,
                228,
                142
              ],
              "label": "10 × 10 "
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json",
          "label": "隔離假專案的 CLI 版本登記與來源關聯示範；不是原次網頁登記"
        },
        {
          "path": "journal/2026-10-22-lesson05-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch05-05-02-01",
    "title": "建立試片檔",
    "actions": [
      "File › New › General 開新檔；在 Properties 的 Scene 分頁 › Units 把 Length 改為 Millimeters、Unit Scale 輸入 <code>0.001</code>。",
      "另存 <code>learning/workspaces/05/u05_fit_coupon_v001.blend</code>。"
    ],
    "checks": [
      "Units 為 Millimeters、<code>0.001</code>",
      "保存通知或重開檔名為 <code>u05_fit_coupon_v001.blend</code>"
    ],
    "pitfalls": [
      {
        "title": "輸入格式",
        "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
      }
    ],
    "locate": "新檔與單位",
    "figures": [
      {
        "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-01-file-menu.png",
        "sha256": "34fb7b908b2195873b9568a38b8aa54bdef0fd7ce29eb0e74570486259fd6768",
        "size": [
          1494,
          1019
        ],
        "caption": "File選單中可見Save As與Shift Ctrl S鍵標。",
        "marks": [
          {
            "n": 1,
            "box": [
              49,
              153,
              176,
              22
            ],
            "label": "另存入口"
          }
        ],
        "tab": "操作位置"
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "新檔與單位 建立試片檔。",
    "lead": "新檔與單位 建立試片檔。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson05-demo-v002.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
