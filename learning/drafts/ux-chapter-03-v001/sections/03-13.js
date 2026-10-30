window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-13"] = {
  "id": "03-13",
  "title": "檢查網格並保存原盒",
  "keyPoint": "套用壁厚並檢查非流形邊，保存原盒。",
  "glossary": [
    {
      "term": "Non Manifold",
      "label": "Non Manifold",
      "text": "用來挑出不符合封閉流形條件的邊的選取功能。"
    },
    {
      "term": "Modifier",
      "label": "Modifier",
      "text": "在網格之上計算幾何效果的修改器。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-04-06-01",
      "title": "套用 Solidify",
      "lead": "Solidify 標題列的下拉選單 › Apply 套用 Solidify。",
      "actions": [
        "在 Solidify 修改器標題列右側的下拉箭頭選 Apply。"
      ],
      "checks": [
        "套用後 Modifier 清單不再有 Solidify",
        "開口外殼的厚度保留"
      ],
      "pitfalls": [],
      "locate": "Solidify 標題列的下拉選單 › Apply",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-06-01-apply-menu.png",
          "sha256": "20abdf9e186cc58bbd98ae06dac6b4bfdd3f8a393b320984e992c37d34c155e7",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Solidify 標題列下拉選單已展開，列出 Apply。",
          "marks": [
            {
              "n": 1,
              "box": [
                1416,
                311,
                18,
                18
              ],
              "label": "下拉選單"
            },
            {
              "n": 2,
              "box": [
                1287,
                333,
                145,
                20
              ],
              "label": "Apply"
            }
          ]
        },
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-06-02-applied.png",
          "sha256": "6d62257d00aeefb5285d7c3fb959339fdc19197c05e97a06fa2b83b0d940250c",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "盒有可見厚度，Modifier 分頁只顯示 Add Modifier，未列任何修改器。",
          "marks": [
            {
              "n": 1,
              "box": [
                1266,
                277,
                216,
                20
              ],
              "label": "Modifier"
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
      "stepId": "ch03-04-06-02",
      "title": "取消全選",
      "lead": "Edit Mode、邊選取（按 2）、Select › None 取消全選。",
      "actions": [
        "<kbd>Tab</kbd> 進 Edit Mode，按 <kbd>2</kbd> 切到邊選取，Select › None（<kbd>Alt</kbd>+<kbd>A</kbd>）。"
      ],
      "checks": [
        "Edit Mode 中沒有反白元素",
        "目前為邊選取模式"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "Object Mode 的 <kbd>Alt</kbd>+<kbd>A</kbd> 是取消物件選取；不能把兩種模式的選取狀態混用。"
        }
      ],
      "locate": "Edit Mode、邊選取（按 2）、Select › None",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-06-03-trait-menu.png",
          "sha256": "a03603f9caae0dff9978360dcd58da412b9e72e9d4688904c983da48c24de925",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Edit Mode 邊選取模式且 Nothing selected；Select › Select All by Trait 子選單顯示 Non Manifold。",
          "marks": [
            {
              "n": 1,
              "box": [
                171,
                29,
                20,
                19
              ],
              "label": "邊選取"
            },
            {
              "n": 2,
              "box": [
                260,
                299,
                208,
                20
              ],
              "label": "Select A"
            },
            {
              "n": 3,
              "box": [
                476,
                298,
                208,
                20
              ],
              "label": "Non Mani"
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
      "stepId": "ch03-04-06-03",
      "title": "選取不封閉的邊",
      "lead": "Select › Select All by Trait › Non Manifold 選取不封閉的邊。",
      "actions": [
        "Select › Select All by Trait › Non Manifold。"
      ],
      "checks": [
        "執行 Non Manifold 後沒有邊反白",
        "盒口環面與內外壁仍可見"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "Select › Select All by Trait › Non Manifold",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-06-03-trait-menu.png",
          "sha256": "a03603f9caae0dff9978360dcd58da412b9e72e9d4688904c983da48c24de925",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Edit Mode 邊選取模式且 Nothing selected；Select › Select All by Trait 子選單顯示 Non Manifold。",
          "marks": [
            {
              "n": 1,
              "box": [
                171,
                29,
                20,
                19
              ],
              "label": "邊選取"
            },
            {
              "n": 2,
              "box": [
                260,
                299,
                208,
                20
              ],
              "label": "Select A"
            },
            {
              "n": 3,
              "box": [
                476,
                298,
                208,
                20
              ],
              "label": "Non Mani"
            }
          ]
        },
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-06-04-non-manifold.png",
          "sha256": "5141ce34c27e3fa59203ddb267cf7f8404ec2f4c46801a59a0fe6c80dc5cce78",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Edit Mode 無邊被選取，左下最後操作 Select Non-Manifold。",
          "marks": [
            {
              "n": 1,
              "box": [
                955,
                82,
                242,
                52
              ],
              "label": "Nothing "
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
      "stepId": "ch03-04-06-04",
      "title": "改名並保存原盒",
      "lead": "Object Mode · Outliner · 教學頁「檔案版本」 改名並保存原盒。",
      "actions": [
        "<kbd>Tab</kbd> 回 Object Mode，在 Outliner 把盒子改名為 Body（<kbd>F2</kbd>）。",
        "File › Save（<kbd>Ctrl</kbd>+<kbd>S</kbd>）保存 <code>u04_box_v001.blend</code>，到教學頁以單元 <code>04</code> 登記（場景 .blend）。"
      ],
      "checks": [
        "Outliner 物件改名 Body，Dimensions <code>60</code>×<code>40</code>×<code>30 mm</code>",
        "保存並登記的原盒版本有路徑與 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode · Outliner · 教學頁「檔案版本」",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-save-body-gui-v001/SAVE-02-renamed.png",
          "sha256": "815d64f3cfa991c30c268577d8cea74b61cb2d54494c920801153adfad56dd83",
          "size": [
            1494,
            1019
          ],
          "caption": "Outliner名稱為Body；開口盒Dimensions為60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1293,
                92,
                91,
                22
              ],
              "label": "盒體名稱"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                228,
                63
              ],
              "label": "盒體尺寸"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/03/2026-10-28-save-body-gui-v001/SAVE-03-saved.png",
          "sha256": "ed09bb0ef3ece0d97698f5d59834bf2a15a41aa42eb85fab98e62b4d90d87ce2",
          "size": [
            1494,
            1019
          ],
          "caption": "底部顯示已保存u03_body_saved_v001.blend；此為示範保存檔名。",
          "marks": [
            {
              "n": 1,
              "box": [
                607,
                997,
                260,
                20
              ],
              "label": "示範保存檔名"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/03/2026-10-28-save-body-gui-v001/SAVE-04-reopened.png",
          "sha256": "8f2e3f6b7ab7b6fcea5b739bb08f65c0c290d83cda8a70e01ddc0acfa89df232",
          "size": [
            1494,
            1019
          ],
          "caption": "Body開口盒被選中，尺寸60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                228,
                63
              ],
              "label": "盒體尺寸"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/03/2026-10-28-save-body-gui-v001/safe-summary-v001.json",
          "label": "原盒改名、保存及重開讀值"
        },
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
