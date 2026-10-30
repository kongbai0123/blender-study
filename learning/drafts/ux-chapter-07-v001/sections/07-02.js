window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["07-02"] = {
  "id": "07-02",
  "title": "草圖與尺寸約束",
  "keyPoint": "畫 XY 矩形，加尺寸約束再改寬度。",
  "glossary": [
    {
      "term": "XY",
      "label": "XY",
      "text": "本節草圖所在的平面。"
    },
    {
      "term": "Distance",
      "label": "Distance",
      "text": "本節矩形尺寸約束的欄位。"
    },
    {
      "term": "Fully defined",
      "label": "Fully defined",
      "text": "草圖自由度已消除的狀態，不保證後續生成幾何已更新。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch07-sketch-01",
      "title": "建立 XY 草圖",
      "lead": "3D Viewport；CAD Sketcher 已啟用；Unit Scale 0.001、Millimeters 建立 XY 草圖。",
      "actions": [
        "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> 開啟 Add Sketch；在平面選擇時按 Z 選 XY。"
      ],
      "checks": [
        "Sketcher 進入 XY 草圖",
        "頂端出現 Leave Sketch 或對應離開草圖按鈕"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "此鍵位為隔離 Blender <code>5.2.1</code> 與 CAD Sketcher <code>0.32.1</code> 的試驗；先對照實際畫面，未核對替代選單路徑。"
        }
      ],
      "locate": "3D Viewport；CAD Sketcher 已啟用；Unit Scale 0.001、Millimeters",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/CAD-ENV-03-origin-sketch.png",
          "sha256": "4ec33da3eeda90ba738c770b73ebfdbbcf7505ab8a6d4c50acb3c29582248bd4",
          "size": [
            1494,
            1019
          ],
          "caption": "空白 Body Sketch，紅X與綠Y交於草圖原點；標題列 Leave Sketch。",
          "marks": [
            {
              "n": 1,
              "box": [
                1038,
                27,
                178,
                24
              ],
              "label": "草圖標題"
            },
            {
              "n": 2,
              "box": [
                597,
                459,
                35,
                34
              ],
              "label": "草圖原點"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch07-sketch-02",
      "title": "建立數值矩形",
      "lead": "XY 草圖內、矩形工具作用中 建立數值矩形。",
      "actions": [
        "確認 XY 草圖作用中，在 3D Viewport 按 <kbd>R</kbd> 啟動矩形工具。",
        "依畫面點草圖原點作第一角，移動游標，輸入 <code>60</code>、按 <kbd>Tab</kbd>、輸入 <code>40</code>，按 <kbd>Enter</kbd> 確認，再按 <kbd>Esc</kbd> 結束工具。"
      ],
      "checks": [
        "畫面出現矩形四邊",
        "數值輸入寬<code>60</code>、高<code>40</code>；尺寸約束尚待下一步加入"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "此鍵位為隔離 Blender <code>5.2.1</code> 與 CAD Sketcher <code>0.32.1</code> 的試驗；先對照實際畫面，未核對替代選單路徑。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "XY 草圖內、矩形工具作用中",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/CAD-ENV-06-rectangle.png",
          "sha256": "f4cff5646bb13155931c8ea88d1fab9659e0c01ed0b4a3af60eca8e521e0f1c3",
          "size": [
            1494,
            1019
          ],
          "caption": "數值矩形右半部被側欄遮擋；Sketcher 明示 Degrees of freedom: 2，不是已完全約束。",
          "marks": [
            {
              "n": 1,
              "box": [
                996,
                152,
                195,
                27
              ],
              "label": "自由度為2"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch07-sketch-03",
      "title": "標註寬度與高度",
      "lead": "草圖內，確認選對矩形邊線 標註寬度與高度。",
      "actions": [
        "D Dimension 選邊，加上 <code>60 mm</code> 寬度；再選高度邊，加 <code>40 mm</code>。"
      ],
      "checks": [
        "側欄 Distance 為<code>60</code>、<code>40 mm</code>",
        "Sketcher 顯示 Fully defined"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "此鍵位為隔離 Blender <code>5.2.1</code> 與 CAD Sketcher <code>0.32.1</code> 的試驗；先對照實際畫面，未核對替代選單路徑。"
        }
      ],
      "locate": "草圖內，確認選對矩形邊線",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/CAD-ENV-08-height-dimension.png",
          "sha256": "87164ea22af1d7cac054f96f513dd16ddfbcc39ef06098083524cfd659e34f9d",
          "size": [
            1494,
            1019
          ],
          "caption": "Sketcher 顯示 Fully defined sketch，Dimensional 兩列60 mm、40 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1002,
                151,
                184,
                28
              ],
              "label": "完全約束"
            },
            {
              "n": 2,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "寬高尺寸"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch07-sketch-04",
      "title": "變更尺寸並重開",
      "lead": "草圖側欄中的尺寸約束；另存新版本 變更尺寸並重開。",
      "actions": [
        "先將<code>60</code>×<code>40</code>草圖以尚未使用的新檔名另存，保留供下一節使用。",
        "將寬度約束由<code>60</code>改為<code>80 mm</code>，另存另一個新檔名後重新開啟。"
      ],
      "checks": [
        "保存的兩份副本各自保留<code>60</code>×<code>40</code>與<code>80</code>×<code>40</code>草圖",
        "重開<code>80</code>×<code>40</code>版後，Distance與全約束狀態仍相符"
      ],
      "pitfalls": [
        {
          "title": "重開出現工具警告",
          "text": "既有場次曾出現 sketcher.slvs_select 工具未找到；出現時先保留副本、記錄完整訊息，不能把全約束當作已修復警告。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "草圖側欄中的尺寸約束；另存新版本",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/CAD-ENV-12-reopened-80.png",
          "sha256": "cee4e6454edd9c8357ff76a086fbebee82e0006a273d5b8e17d20e3b7108ce43",
          "size": [
            1494,
            1019
          ],
          "caption": "重開後側欄明示80／40mm、Fully defined；矩形完整寬度不在此裁切內。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "寬高尺寸"
            },
            {
              "n": 2,
              "box": [
                1002,
                151,
                184,
                28
              ],
              "label": "完全約束"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ]
};
