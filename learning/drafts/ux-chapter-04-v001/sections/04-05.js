window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-05"] = {
  "id": "04-05",
  "title": "保存場景並輸出第一張圖",
  "keyPoint": "保存渲染條件，輸出 PNG 並關聯場景。",
  "glossary": [
    {
      "term": "EEVEE",
      "label": "EEVEE",
      "text": "本節使用的渲染引擎。"
    },
    {
      "term": "Resolution",
      "label": "Resolution",
      "text": "輸出影像像素與比例設定。"
    },
    {
      "term": "PNG",
      "label": "PNG",
      "text": "本節保存渲染影像的格式。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-05-01",
      "title": "確認輸出設定並保存",
      "lead": "Render / Output Properties 確認輸出設定並保存。",
      "actions": [
        "Properties 的 Render 分頁核對 Render Engine 為 EEVEE；Output 分頁把 Resolution 下方的 % 調到 <code>50%</code>，記下 X、Y。",
        "<kbd>Ctrl</kbd>+<kbd>S</kbd> 保存 <code>u03_render_v001.blend</code>，到教學頁以單元 <code>03</code> 登記。"
      ],
      "checks": [
        "Render Engine 為 EEVEE，Resolution 比例為<code>50%</code>",
        "已保存場景在版本表有路徑與 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "Render / Output Properties",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-01-render-engine.png",
          "sha256": "eb96a798a0192783a8f22fa22f4362e925aa1d1d3174b53bb4564a0091f03d66",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Render Properties 顯示 Render Engine EEVEE。",
          "marks": [
            {
              "n": 1,
              "box": [
                1236,
                454,
                20,
                20
              ],
              "label": "Render 分"
            },
            {
              "n": 2,
              "box": [
                1358,
                451,
                125,
                22
              ],
              "label": "EEVEE"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-02-resolution.png",
          "sha256": "963a1c38ec1803b36c32dcf1e778d396e2c0629a101c3295b38eb7aa7cfacdea",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Output Format 顯示解析度 1920×1080、百分比 50%。",
          "marks": [
            {
              "n": 1,
              "box": [
                1236,
                482,
                20,
                20
              ],
              "label": "Output 分"
            },
            {
              "n": 2,
              "box": [
                1358,
                478,
                118,
                58
              ],
              "label": "Resoluti"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-03-scene-saved.png",
          "sha256": "54e4eb5bbf6e287a9a54c991c8d97956e8a2f4de80cd3ae43e17f08feb7e40ba",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Output Format為1920×1080、50%；底部顯示已保存u03_render_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                1357,
                475,
                120,
                64
              ],
              "label": "輸出解析度"
            },
            {
              "n": 2,
              "box": [
                626,
                996,
                219,
                21
              ],
              "label": "場景保存提示"
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
      "stepId": "ch04-03-05-02",
      "title": "渲染一張圖",
      "lead": "上方 Render › Render Image 渲染一張圖。",
      "actions": [
        "Render › Render Image（<kbd>F12</kbd>），等渲染視窗出現結果並核對取景。"
      ],
      "checks": [
        "Render Result 顯示訊號站影像",
        "畫框中的取景與本次場景相符"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>F12</kbd> 不會把結果另存 PNG；Image &gt; Save As 與輸出關聯仍照常規方法。"
        }
      ],
      "locate": "上方 Render › Render Image",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-04-render-menu.png",
          "sha256": "ed0ee355a415423f58a746500201feeb48604fdd1100f5ac99225b65bf992ac9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Render選單的Render Image列顯示F12。",
          "marks": [
            {
              "n": 1,
              "box": [
                100,
                26,
                193,
                23
              ],
              "label": "開始渲染"
            }
          ]
        },
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-05-render-window.png",
          "sha256": "cce130454b2c4ba2620b991087947221d0d6c4a72c3270306d31e8f6eeb691f5",
          "size": [
            990,
            600
          ],
          "tab": "過程狀態",
          "caption": "Render Result 顯示藍色平台、白色立柱和球及地面陰影，頂端有渲染時間。",
          "marks": [
            {
              "n": 1,
              "box": [
                167,
                3,
                36,
                20
              ],
              "label": "Image 選單"
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
      "stepId": "ch04-03-05-03",
      "title": "另存 PNG 並登記",
      "lead": "渲染圖視窗 Image › Save As… 另存 PNG 並登記。",
      "actions": [
        "在渲染視窗 Image › Save As... 保存 PNG，核對檔案與來源場景。",
        "到教學頁登記該圖（用途「渲染圖」，來源選 <code>u03_render_v001.blend</code>）。"
      ],
      "checks": [
        "自己的工作區產生 PNG",
        "版本表的圖像來源指向 <code>u03_render_v001.blend</code>"
      ],
      "pitfalls": [],
      "locate": "渲染圖視窗 Image › Save As…",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-06-save-png.png",
          "sha256": "7bec66d9d6e838f00812b6d59501f9ec2bf1b8c4a2a38f5e6ce82332234732d1",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Save As Image 對話框，File Format PNG，檔名為 u03_render_v001_preview.png。",
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
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-05-07-png-saved.png",
          "sha256": "cce130454b2c4ba2620b991087947221d0d6c4a72c3270306d31e8f6eeb691f5",
          "size": [
            990,
            600
          ],
          "tab": "過程狀態",
          "caption": "Render Result 顯示藍色平台、白色立柱和球及地面陰影，頂端有渲染時間。",
          "marks": [
            {
              "n": 1,
              "box": [
                167,
                3,
                36,
                20
              ],
              "label": "Image 選單"
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
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
