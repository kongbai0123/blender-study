window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-12"] = {
  "id": "03-12",
  "title": "加上 2 mm 壁厚",
  "keyPoint": "用 Solidify 向內增加 2 mm 壁厚。",
  "glossary": [
    {
      "term": "Solidify",
      "label": "Solidify",
      "text": "替開放表面增加厚度的修改器。"
    },
    {
      "term": "Thickness",
      "label": "Thickness",
      "text": "Solidify 的厚度欄位。"
    },
    {
      "term": "Offset",
      "label": "Offset",
      "text": "控制厚度向表面哪側延伸的參數。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-04-05-01",
      "title": "回 Object Mode",
      "lead": "Tab 回到 Object Mode 回 Object Mode。",
      "actions": [
        "滑鼠在 3D Viewport 內按 <kbd>Tab</kbd>。"
      ],
      "checks": [
        "模式選單顯示 Object Mode",
        "整個外殼顯示物件外框"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Tab</kbd> 是切換，不是固定設成某模式；到達目標模式就停。"
        }
      ],
      "locate": "Tab 回到 Object Mode",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-05-01-add-solidify.png",
          "sha256": "9040f6dc8c226ee666821de7e4b3cc831f0d6b4c274aeeb31d18fa0f350ca6b4",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object Mode；Add Modifier › Generate 子選單展開，Solidify 被突出顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                1242,
                323,
                172,
                20
              ],
              "label": "Generate"
            },
            {
              "n": 2,
              "box": [
                1064,
                622,
                172,
                20
              ],
              "label": "Solidify"
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
      "stepId": "ch03-04-05-02",
      "title": "加入 Solidify",
      "lead": "Properties 的 Modifier 分頁 › Add Modifier › Generate › Solidify 加入 Solidify。",
      "actions": [
        "在 Properties 點扳手圖示（Modifiers）› Add Modifier › Generate › Solidify。"
      ],
      "checks": [
        "Modifier 清單出現 Solidify",
        "開口邊緣可見新增厚度"
      ],
      "pitfalls": [],
      "locate": "Properties 的 Modifier 分頁 › Add Modifier › Generate › Solidify",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-05-01-add-solidify.png",
          "sha256": "9040f6dc8c226ee666821de7e4b3cc831f0d6b4c274aeeb31d18fa0f350ca6b4",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object Mode；Add Modifier › Generate 子選單展開，Solidify 被突出顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                1242,
                323,
                172,
                20
              ],
              "label": "Generate"
            },
            {
              "n": 2,
              "box": [
                1064,
                622,
                172,
                20
              ],
              "label": "Solidify"
            }
          ]
        },
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-05-02-solidify-default.png",
          "sha256": "81c61b4dd39497bea66e2e680ffb4bf71feadc081196c1f04888299af44027d3",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Solidify Modifier 顯示 Thickness 0.01 mm、Offset -1，外形 Dimensions 60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1352,
                365,
                103,
                20
              ],
              "label": "Thicknes"
            },
            {
              "n": 2,
              "box": [
                1352,
                390,
                103,
                20
              ],
              "label": "Offset −"
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
      "stepId": "ch03-04-05-03",
      "title": "設定壁厚 2 mm",
      "lead": "Solidify › Thickness 設定壁厚 2 mm。",
      "actions": [
        "Thickness 輸入 <code>2mm</code>，Offset 保持 <code>-1</code>（厚度往內長）。"
      ],
      "checks": [
        "Thickness 為 <code>2 mm</code>、Offset 為 <code>-1</code>",
        "Dimensions 仍為 <code>60</code>×<code>40</code>×<code>30 mm</code>，計算內寬<code>56</code>×<code>36 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Solidify › Thickness",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-05-03-solidify-wall.png",
          "sha256": "4478d502422e66e765358cc806d94d278573050c3071ca40c4fd30b8c58b3f38",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Solidify Thickness 2 mm、Offset -1、Even Thickness 已勾選；外尺寸 60×40×30 mm，視口可見內壁。",
          "marks": [
            {
              "n": 1,
              "box": [
                1352,
                365,
                103,
                20
              ],
              "label": "Thicknes"
            },
            {
              "n": 2,
              "box": [
                1352,
                415,
                103,
                20
              ],
              "label": "Even Thi"
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
    }
  ]
};
