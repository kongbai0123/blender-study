window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["07-03"] = {
  "id": "07-03",
  "title": "拉伸成實心體",
  "keyPoint": "從 60×40 草圖拉伸 30，另存並重開。",
  "glossary": [
    {
      "term": "Extrude",
      "label": "Extrude",
      "text": "CAD Sketcher把草圖輪廓拉伸成體積的操作，與原生網格擠出分開。"
    },
    {
      "term": "預覽",
      "label": "預覽",
      "text": "尚未確認操作時的暫時幾何。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch07-solid-01",
      "title": "確認草圖並離開",
      "lead": "使用先前60×40 mm草圖副本；Body Sketch 活動，3D 視圖中操作。 確認草圖並離開。",
      "actions": [
        "核對側欄 Distance <code>60 mm</code>、<code>40 mm</code>及 Fully defined；先另存個人副本。",
        "在3D視圖按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> 離開草圖。"
      ],
      "checks": [
        "起始副本 Distance 為<code>60</code>、<code>40 mm</code>",
        "離開草圖後 Body 選中且平面可見"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "版本或其他狀態快捷鍵可能不同；先核對畫面。"
        }
      ],
      "locate": "使用先前60×40 mm草圖副本；Body Sketch 活動，3D 視圖中操作。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-01-opened-sketch.png",
          "sha256": "4d1898ecc22882b8921795558f6dadbec38585b2f3cd595af5e69e144eef6f85",
          "size": [
            1494,
            1019
          ],
          "caption": "60／40mm與Fully defined；底部黃色 Tool sketcher.slvs_select not found 警告清楚可見。",
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
                560,
                996,
                365,
                22
              ],
              "label": "工具警告"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-02-left-sketch.png",
          "sha256": "4be731ed2a5072db8802d144a6e9e31c623633ac1d72d1edfe769f38db599c05",
          "size": [
            1494,
            1019
          ],
          "caption": "Body平面橘框被選取；Sketcher Node Tools中可見Extrude。",
          "marks": [
            {
              "n": 1,
              "box": [
                964,
                302,
                223,
                22
              ],
              "label": "Extrude"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/manual-extrude-verification-v002.json",
          "label": "手工草圖拉伸試驗、讀值和失敗版本摘要"
        }
      ]
    },
    {
      "stepId": "ch07-solid-02",
      "title": "啟動拉伸預覽",
      "lead": "Object Mode，Body 已選取，焦點在3D視圖。 啟動拉伸預覽。",
      "actions": [
        "按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd> 啟動本次 CAD Sketcher 拉伸；先不要點擊確認。"
      ],
      "checks": [
        "按快捷鍵後出現有厚度的預覽",
        "操作仍未確認，可繼續輸入目標值"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "預覽數值尚非確認結果；本次早期試探點擊曾提前接受約<code>3.9 mm</code>。"
        }
      ],
      "locate": "Object Mode，Body 已選取，焦點在3D視圖。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-03-tool-invoked.png",
          "sha256": "c22906fa830e47b9f23083ced37e4ac5a6ec6a0c3008bcd177e6348e5515df49",
          "size": [
            1494,
            1019
          ],
          "caption": "Auto Boolean已勾；平面出現暫時厚度，底部Offset 3.902，尚非30。",
          "marks": [
            {
              "n": 1,
              "box": [
                5,
                55,
                112,
                21
              ],
              "label": "自動布林"
            },
            {
              "n": 2,
              "box": [
                310,
                999,
                95,
                18
              ],
              "label": "預覽偏移"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/manual-extrude-verification-v002.json",
          "label": "手工草圖拉伸試驗、讀值和失敗版本摘要"
        }
      ]
    },
    {
      "stepId": "ch07-solid-03",
      "title": "輸入 30 並確認",
      "lead": "本次拉伸工具仍在等待輸入；Blender 5.2.1、CAD Sketcher 0.32.1、Unit Scale 0.001。 輸入 30 並確認。",
      "actions": [
        "直接輸入 <code>30</code>（不加 mm），觀察預覽與狀態列；按 <kbd>Enter</kbd> 確認。"
      ],
      "checks": [
        "確認後畫面呈實心體",
        "Modifier 清單保留 CAD Sketcher Convert 與 Extrude"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "本次拉伸工具仍在等待輸入；Blender 5.2.1、CAD Sketcher 0.32.1、Unit Scale 0.001。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-04-numeric-entry.png",
          "sha256": "2eade80ff0fe73966c8b2cf5cafbab9e775458580eb850392181ab2dec68062c",
          "size": [
            1494,
            1019
          ],
          "caption": "拉伸立體預覽；底部 DISTANCE: [*30]，尚待確認。",
          "marks": [
            {
              "n": 1,
              "box": [
                310,
                999,
                120,
                18
              ],
              "label": "輸入30"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-05-confirmed.png",
          "sha256": "0d924b33a67dfd3b4d92b04559f4a9ee2bee37ea81bea6d35ba1ed8bde153c75",
          "size": [
            1494,
            1019
          ],
          "caption": "確認後Body立體橘框，底部沒有輸入模式；畫面不能直接量出60×40×30。",
          "marks": [
            {
              "n": 1,
              "box": [
                1080,
                27,
                135,
                23
              ],
              "label": "已離開草圖"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/manual-extrude-verification-v002.json",
          "label": "手工草圖拉伸試驗、讀值和失敗版本摘要"
        }
      ]
    },
    {
      "stepId": "ch07-solid-04",
      "title": "另存並重開",
      "lead": "確認實心體後，在 Blender 另存自己獨立的新版本，再重新開啟。 另存並重開。",
      "actions": [
        "另存新版本，保留草圖來源。",
        "重開後檢查模型；並以可用工具另行核對尺寸。"
      ],
      "checks": [
        "另存副本重開後仍可見實心外形",
        "自己的尺寸檢查紀錄列出<code>60</code>×<code>40</code>×<code>30 mm</code>"
      ],
      "pitfalls": [],
      "locate": "確認實心體後，在 Blender 另存自己獨立的新版本，再重新開啟。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-06-saved.png",
          "sha256": "30e41249f7d4718ba94705599b6474bc07fdae4dc3d7fbacabadfb1c840596e5",
          "size": [
            1494,
            1019
          ],
          "caption": "底部Saved as manual_sketch_extrude_60x40x30_v001.blend訊息；畫面立體外形仍在。",
          "marks": [
            {
              "n": 1,
              "box": [
                559,
                995,
                361,
                23
              ],
              "label": "存檔通知"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/EXTRUDE-07-reopened.png",
          "sha256": "5406efc2b7771d4e0fa0f47c30ed09b9b7d8a4fcf689d26c7bc8f570f96ce161",
          "size": [
            1494,
            1019
          ],
          "caption": "既有實心Body被選取，頂面可見，尚未開始新草圖。",
          "marks": [
            {
              "n": 1,
              "box": [
                615,
                300,
                339,
                355
              ],
              "label": "既有實心體"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/demo-files/manual_sketch_extrude_60x40x30_v001.blend",
          "label": "手工草圖拉伸實心體 v001（助教示範）"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-extrude-trial-v002/manual-extrude-verification-v002.json",
          "label": "手工草圖拉伸試驗、讀值和失敗版本摘要"
        }
      ]
    }
  ]
};
