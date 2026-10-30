window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-04"] = {
  "id": "01-04",
  "title": "第一次另存 v001",
  "keyPoint": "把練習另存為 v001，核對檔名與版本表。",
  "glossary": [
    {
      "term": "Save As",
      "label": "Save As",
      "text": "另存到指定路徑與檔名的功能。"
    },
    {
      "term": "SHA-256",
      "label": "SHA-256",
      "text": "依檔案內容計算的指紋，用來核對版本。"
    },
    {
      "term": "檢查點",
      "label": "檢查點",
      "text": "保存並登記、可供回復的場景版本。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-04-01",
      "title": "開啟另存對話框",
      "lead": "Blender 上方 File › Save As… 開啟另存對話框。",
      "actions": [
        "開啟另存對話框，將資料夾設為 learning/workspaces/<code>01</code>/（完整路徑可在原教材 <code>01</code>-<code>04</code> 頁的「我的練習檔案」複製）。"
      ],
      "checks": [
        "Save As 檔案視窗已開啟",
        "資料夾欄指向自己的 workspaces/<code>01</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Blender 上方 File › Save As…",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-01-file-menu.png",
          "sha256": "34fb7b908b2195873b9568a38b8aa54bdef0fd7ce29eb0e74570486259fd6768",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
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
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-02-learner-path.png",
          "sha256": "cb6fd3a376d45216503bccc7c90cd4242ff69ac153e5c6869ff4917935be79a1",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Save As 檔名欄顯示 u01_basics_v001.blend，路徑欄顯示工作區但被截斷；未按存檔。",
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
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-04-02",
      "title": "輸入檔名並儲存",
      "lead": "另存對話框的檔名 輸入檔名並儲存。",
      "actions": [
        "輸入 <code>u01_basics_v001.blend</code>，核對後執行 Save As；若再出確認，依畫面核對同名檔案。"
      ],
      "checks": [
        "檔名為 <code>u01_basics_v001.blend</code>",
        "保存完成後返回 Blender，成功通知或重開檔名與此一致"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "另存對話框的檔名",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-02-learner-path.png",
          "sha256": "cb6fd3a376d45216503bccc7c90cd4242ff69ac153e5c6869ff4917935be79a1",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Save As 檔名欄顯示 u01_basics_v001.blend，路徑欄顯示工作區但被截斷；未按存檔。",
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
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-03-saved-demo.png",
          "sha256": "ec587c018a9d38947f7652fcafb7457ee891d87f6b16ac968c2d9bf38bcfb740",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "底部通知顯示已保存u01_basics_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                622,
                996,
                232,
                21
              ],
              "label": "v001保存提示"
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
      "stepId": "ch01-01-04-03",
      "title": "登記 v001 檢查點",
      "lead": "教學頁檔案版本紀錄 登記 v001 檢查點。",
      "actions": [
        "先核對已保存的 <code>u01_basics_v001.blend</code>，到教學頁「檔案版本」選單元 <code>01</code>、該檔案與「場景 .blend」並登記。",
        "登記後核對路徑與 SHA-<code>256</code>；後續修改先另存未使用的新版本。"
      ],
      "checks": [
        "版本表中有 <code>u01_basics_v001.blend</code>",
        "該列有實際路徑與 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "教學頁檔案版本紀錄",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json",
          "label": "隔離假專案的 CLI 版本登記與來源關聯示範；不是原次網頁登記"
        },
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步核對教學頁的檔案版本表；沒有登記畫面實拍，請以自己的實際紀錄為準。"
    }
  ]
};
