window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-02"] = {
  "id": "01-02",
  "title": "介面切換為 English (US)",
  "keyPoint": "切換為 English (US)，讓介面名稱與教材一致。",
  "glossary": [
    {
      "term": "Preferences",
      "label": "Preferences（偏好設定）",
      "text": "由 Edit 選單開啟的設定視窗，語言選項在裡面的 Interface 頁。"
    },
    {
      "term": "Interface",
      "label": "Interface（介面）",
      "text": "Preferences 左側的設定頁，這裡可以找到 Language。"
    },
    {
      "term": "Language",
      "label": "Language（語言）",
      "text": "選擇介面語言的下拉欄位；本節使用 English (US)。"
    }
  ],
  "scope": "原圖為既有獨立 Blender 示範；數值以讀值與自己的畫面核對，試驗間隙不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-02-01",
      "title": "開啟偏好設定",
      "lead": "Blender 主視窗；繁中介面時，括號內是對應的中文名稱。",
      "actions": [
        "點左上 Edit（編輯）› Preferences…（偏好設定…）。",
        "在設定視窗左側選 Interface（介面），往下找到 Language（語言）區的 Language 欄位。"
      ],
      "checks": [
        "Preferences 視窗開啟",
        "左側 Interface 已選取，底部可以看到 Language 欄位"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "使用主鍵盤逗點；開啟設定不表示已選語言或儲存。"
        }
      ],
      "locate": "Blender 主視窗；繁中介面時，括號內是對應的中文名稱。",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-01-02-language-02-edit-open-v001.jpg",
          "sha256": "e9887d89c4b078f9c893e14288c9576a39e6d4d28d3c89c5f3c7eda32b9d3d5e",
          "size": [
            1494,
            1019
          ],
          "caption": "中文介面中，編輯選單底部可見偏好設定入口。",
          "marks": [
            {
              "n": 1,
              "box": [
                64,
                32,
                34,
                24
              ],
              "label": "編輯選單"
            },
            {
              "n": 2,
              "box": [
                70,
                287,
                180,
                29
              ],
              "label": "偏好設定"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/01/2026-10-22-01-02-language-03-preferences-v001.jpg",
          "sha256": "0f08682a999cef1fa440566b8d96c9e053d5b4a428529ae74642cfa3eaf97194",
          "size": [
            842,
            582
          ],
          "caption": "2026-10-22 助教實際操作原圖；點「偏好設定…」",
          "marks": [
            {
              "n": 1,
              "box": [
                10,
                68,
                143,
                27
              ],
              "label": "介面頁"
            },
            {
              "n": 2,
              "box": [
                458,
                552,
                270,
                25
              ],
              "label": "Language"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "references": [
        {
          "path": "journal/2026-10-22-interface-language-execution-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-02-02",
      "title": "選擇 English (US)",
      "lead": "Preferences › Interface › Language。",
      "actions": [
        "點 Language 欄位展開清單，捲動找到 English (US)（不是 English (UK)）並點選。"
      ],
      "checks": [
        "Language 顯示 English (US)",
        "設定視窗的選項名稱改為英文"
      ],
      "pitfalls": [],
      "locate": "Preferences › Interface › Language。",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-01-02-language-06-english-visible-v001.jpg",
          "sha256": "4c2fc688bc8a629b6c2099d8d841f878ddb3ec01148c05aee8398014c782490d",
          "size": [
            842,
            582
          ],
          "caption": "語言清單可見English (US)，位於English (UK)下方。",
          "marks": [
            {
              "n": 1,
              "box": [
                439,
                200,
                284,
                21
              ],
              "label": "美式英文"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/01/2026-10-22-01-02-language-07-english-selected-v001.jpg",
          "sha256": "769b55ec7fa43c6473cf4326da661bad5911be9e239538d4eb8a6e7263acb64f",
          "size": [
            842,
            582
          ],
          "caption": "2026-10-22 助教實際操作原圖；點 English (US)",
          "marks": [
            {
              "n": 1,
              "box": [
                10,
                68,
                143,
                27
              ],
              "label": "介面頁"
            },
            {
              "n": 2,
              "box": [
                458,
                552,
                270,
                25
              ],
              "label": "Language"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "references": [
        {
          "path": "journal/2026-10-22-interface-language-execution-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-02-03",
      "title": "保存偏好設定",
      "lead": "Preferences 視窗左下角的選單按鈕（三條線圖示）。",
      "actions": [
        "點左下角選單按鈕，選 Save Preferences；選單裡若已勾 Auto-Save Preferences，設定會自動保存。",
        "關閉設定視窗，回到主視窗。"
      ],
      "checks": [
        "Save Preferences 後出現 Preferences saved 提示，或 Auto-Save Preferences 已勾選",
        "關閉設定後，上方選單是 File、Edit、Render、Window、Help"
      ],
      "pitfalls": [],
      "locate": "Preferences 視窗左下角的選單按鈕（三條線圖示）。",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-01-02-language-08-save-menu-v001.jpg",
          "sha256": "53ac7a5fa613cf80078c77bbb823e49ebcad8369eda6e0ef93f87f93bc6a730a",
          "size": [
            842,
            582
          ],
          "caption": "2026-10-22 助教實際操作原圖；點設定視窗左下角選單",
          "marks": [
            {
              "n": 1,
              "box": [
                9,
                459,
                210,
                28
              ],
              "label": "自動保存"
            },
            {
              "n": 2,
              "box": [
                10,
                488,
                207,
                25
              ],
              "label": "保存設定"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/01/2026-10-22-01-02-language-09-preferences-saved-v001.jpg",
          "sha256": "b7052a83d263cd983dc41995451e29d9ab4f49e062424c34d0eabddf0ff8c54b",
          "size": [
            1494,
            1019
          ],
          "caption": "回到主視窗，底部顯示Preferences saved。",
          "marks": [
            {
              "n": 1,
              "box": [
                664,
                996,
                145,
                21
              ],
              "label": "保存成功"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/01/2026-10-22-01-02-language-10-main-verified-v001.jpg",
          "sha256": "79a60cc99e26fe73d0593cfc01447aeed064f0c7160af999eb616199f64767e9",
          "size": [
            1494,
            1019
          ],
          "caption": "主選單已切為英文，模式選單顯示Object Mode。",
          "marks": [
            {
              "n": 1,
              "box": [
                27,
                32,
                215,
                25
              ],
              "label": "英文選單"
            },
            {
              "n": 2,
              "box": [
                50,
                58,
                110,
                23
              ],
              "label": "物件模式"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "references": [
        {
          "path": "journal/2026-10-22-interface-language-execution-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
