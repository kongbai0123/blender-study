window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-06"] = {
  "id": "04-06",
  "title": "重新開檔再渲染",
  "keyPoint": "重開場景再渲染，對照取景與材質。",
  "glossary": [
    {
      "term": "Render Image",
      "label": "Render Image",
      "text": "執行場景影像渲染的選單命令。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-06-01",
      "title": "重新開啟渲染場景",
      "lead": "File › Open… / 檔案紀錄 重新開啟渲染場景。",
      "actions": [
        "關閉渲染視窗後用 File › Open… 重新開啟已登記的渲染場景，先核對路徑與版本。若跳出 Save changes before closing?，先確認場景沒有再改：已登記的檢查點不要按 Save 覆寫，按 Don&#x27;t Save；不確定就按 Cancel 並回報。"
      ],
      "checks": [
        "重開路徑為已登記的渲染場景",
        "Outliner 中訊號站部件與原紀錄相符"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
        }
      ],
      "locate": "File › Open… / 檔案紀錄",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-06-01-unsaved-dialog.png",
          "sha256": "805ecb478849d646da780ea172cc91627793304685eb69aac37046af372855ae",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "畫面彈出 Save changes before closing?，提供 Save、Don’t Save、Cancel。",
          "marks": [
            {
              "n": 1,
              "box": [
                527,
                456,
                440,
                108
              ],
              "label": "Save cha"
            },
            {
              "n": 2,
              "box": [
                716,
                528,
                115,
                22
              ],
              "label": "按 Don't "
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-06-02-reopened.png",
          "sha256": "40dad05b1d59b29090b087a7b81c4d87b9633ebe98b04ddb6241be94b73f6588",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "重開後相機視角可見訊號站；Solid模式下平台呈灰色，不能由此判材質遺失。",
          "marks": [
            {
              "n": 1,
              "box": [
                1140,
                27,
                21,
                22
              ],
              "label": "實體預覽"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "平台尺寸"
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
      "stepId": "ch04-03-06-02",
      "title": "核對引擎與設定",
      "lead": "Render / Output 設定與相機取景 核對引擎與設定。",
      "actions": [
        "逐回合核對引擎、輸出像素、相機、燈光與材質。"
      ],
      "checks": [
        "引擎與輸出像素和保存紀錄一致",
        "Camera、燈光與材質仍對應原部件"
      ],
      "pitfalls": [],
      "locate": "Render / Output 設定與相機取景",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-06-02-reopened.png",
          "sha256": "40dad05b1d59b29090b087a7b81c4d87b9633ebe98b04ddb6241be94b73f6588",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "重開後相機視角可見訊號站；Solid模式下平台呈灰色，不能由此判材質遺失。",
          "marks": [
            {
              "n": 1,
              "box": [
                1140,
                27,
                21,
                22
              ],
              "label": "實體預覽"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "平台尺寸"
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
      "stepId": "ch04-03-06-03",
      "title": "再渲染一次並另存",
      "lead": "Render Image / PNG 另存 再渲染一次並另存。",
      "actions": [
        "<kbd>F12</kbd> 再渲染一次，在渲染視窗 Image › Save As... 存成 <code>u03_render_v001_repeat.png</code>，與第一張比對取景與材質。"
      ],
      "checks": [
        "工作區有 <code>u03_render_v001_repeat.png</code>",
        "與第一張對照時，取景與材質可逐項比較"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>F12</kbd> 不會把結果另存 PNG；Image &gt; Save As 與輸出關聯仍照常規方法。"
        }
      ],
      "locate": "Render Image / PNG 另存",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-06-03-render-again.png",
          "sha256": "49e199a6d5bf336c69973666702acb3323f53708853de50eaed94b45bd8d9859",
          "size": [
            990,
            600
          ],
          "tab": "操作位置",
          "caption": "Render Result顯示藍色平台、站體與投影，左上有渲染時間。",
          "marks": [
            {
              "n": 1,
              "box": [
                11,
                27,
                172,
                17
              ],
              "label": "渲染時間"
            },
            {
              "n": 2,
              "box": [
                390,
                1,
                113,
                22
              ],
              "label": "渲染結果"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-06-04-compare.png",
          "sha256": "49e199a6d5bf336c69973666702acb3323f53708853de50eaed94b45bd8d9859",
          "size": [
            990,
            600
          ],
          "tab": "過程狀態",
          "caption": "Render Result顯示藍色平台、站體與投影，左上有渲染時間。",
          "marks": [
            {
              "n": 1,
              "box": [
                11,
                27,
                172,
                17
              ],
              "label": "渲染時間"
            },
            {
              "n": 2,
              "box": [
                390,
                1,
                113,
                22
              ],
              "label": "渲染結果"
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
