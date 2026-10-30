window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["12-05"] = {
  "id": "12-05",
  "title": "小盒成品渲染",
  "keyPoint": "用個人副本渲染，分清視窗實拍與輸出圖。",
  "glossary": [
    {
      "term": "Render Result",
      "label": "Render Result",
      "text": "Blender顯示渲染結果的影像。"
    },
    {
      "term": "Output Properties",
      "label": "Output Properties",
      "text": "設定解析度、輸出格式與目的地的屬性分頁。"
    },
    {
      "term": "相對路徑",
      "label": "相對路徑",
      "text": "以雙斜線開頭、相對目前blend檔解析的輸出位置。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch12-box-render-prepare",
      "title": "觀察分離展示",
      "lead": "獨立 Blender；Object Mode；展示場景由程式設定，來源為05-05盒與蓋。 觀察分離展示。",
      "actions": [
        "觀察盒口、向上暫移<code>18 mm</code>的上蓋，以及相機取景範圍。"
      ],
      "checks": [
        "視窗可見盒與蓋分離",
        "暫抬上蓋<code>18 mm</code>，盒口與環唇可辨"
      ],
      "pitfalls": [],
      "locate": "獨立 Blender；Object Mode；展示場景由程式設定，來源為05-05盒與蓋。",
      "figures": [
        {
          "path": "evidence/12/2026-10-27-engineering-box-render-v004/12-01-01-prepared.png",
          "sha256": "2d41fb41da7934191bcbad6f4a89ca2202bc8bae89d366646cca563d2e66dc6e",
          "size": [
            1494,
            1019
          ],
          "caption": "Camera Orthographic中盒蓋分離，Body Item60／40／30mm；18mm抬蓋量不是圖中直接顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                305,
                244,
                616,
                463
              ],
              "label": "相機取景"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch12-box-render-image",
      "title": "執行 Render Image",
      "lead": "獨立 Blender 已有示範佈景；Render 選單。 執行 Render Image。",
      "actions": [
        "觀察示範以 GUI 事件選擇 Render › Render Image，並查看 Render Result。"
      ],
      "checks": [
        "Render Result視窗出現分離盒蓋影像",
        "渲染完成事件在來源摘要中有獨立讀值"
      ],
      "pitfalls": [],
      "locate": "獨立 Blender 已有示範佈景；Render 選單。",
      "figures": [
        {
          "path": "evidence/12/2026-10-27-engineering-box-render-v004/12-01-03-render-result.png",
          "sha256": "f89eed44b64ccc6d363f5388137a473172fe8a2d6ae9494e60c9475d5b89fda4",
          "size": [
            670,
            540
          ],
          "caption": "獨立Render Result視窗，顯示藍色盒與抬高上蓋；這張是含介面的截圖，不是640×480輸出PNG本體。",
          "marks": [
            {
              "n": 1,
              "box": [
                228,
                1,
                125,
                25
              ],
              "label": "Render結果"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch12-box-render-output",
      "title": "分清截圖與渲染輸出",
      "lead": "分清截圖與渲染輸出。",
      "actions": [
        "對照 Blender 視窗截圖、<code>640</code>×<code>480</code> 渲染輸出 PNG 與其來源場景版本。"
      ],
      "checks": [
        "檔案清單區分GUI截圖與<code>640</code>×<code>480</code>輸出PNG",
        "兩個檔案分別有SHA-<code>256</code>且關聯同一渲染場景"
      ],
      "pitfalls": [],
      "locate": "Render Result 與本步附的場景、PNG、驗證摘要。",
      "figures": [
        {
          "path": "evidence/12/2026-10-27-engineering-box-render-v004/12-01-03-render-result.png",
          "sha256": "f89eed44b64ccc6d363f5388137a473172fe8a2d6ae9494e60c9475d5b89fda4",
          "size": [
            670,
            540
          ],
          "caption": "獨立Render Result視窗，顯示藍色盒與抬高上蓋；這張是含介面的截圖，不是640×480輸出PNG本體。",
          "marks": [
            {
              "n": 1,
              "box": [
                228,
                1,
                125,
                25
              ],
              "label": "Render結果"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ],
  "prep": {
    "stepId": "ch12-box-render-safe-copy",
    "title": "另存個人場景並核對輸出",
    "actions": [
      "先將場景另存至個人工作區，再到 Output Properties 核對輸出路徑也在個人工作區。"
    ],
    "checks": [
      "目前blend另存到個人工作區",
      "Output Properties的相對路徑解析後仍在個人工作區"
    ],
    "pitfalls": [],
    "locate": "開啟示範場景後，File › Save As，選自己的工作區與未使用的新檔名。",
    "figures": [
      {
        "path": "evidence/12/2026-10-28-render-safe-copy-gui-v003/12-COPY-02-saved.png",
        "sha256": "633b0445de2d4bcbb52b341a374474529d0b36efe255fe82171f090dfdf536c4",
        "size": [
          1494,
          1019
        ],
        "caption": "相機視圖內盒蓋分離；底部Saved as my_box_for_render_v001.blend，圖片本身不顯示完整保存路徑。",
        "marks": [
          {
            "n": 1,
            "box": [
              607,
              995,
              260,
              23
            ],
            "label": "場景存檔"
          },
          {
            "n": 2,
            "box": [
              305,
              244,
              616,
              463
            ],
            "label": "相機畫框"
          }
        ],
        "tab": "操作位置"
      },
      {
        "path": "evidence/12/2026-10-28-render-safe-copy-gui-v003/12-COPY-03-output.png",
        "sha256": "9084b9b4ad27381fbdac4da40a5282a70f8f808fb1f0282b9ae26a2687b5283a",
        "size": [
          1494,
          1019
        ],
        "caption": "Output Properties可見640×480、100%、PNG RGBA及相對路徑//render_output\\box_lid；目的地解析到哪裡需結合場景位置。",
        "marks": [
          {
            "n": 1,
            "box": [
              1277,
              302,
              199,
              61
            ],
            "label": "輸出尺寸"
          },
          {
            "n": 2,
            "box": [
              1275,
              677,
              202,
              24
            ],
            "label": "相對輸出路徑"
          }
        ],
        "tab": "過程狀態"
      }
    ],
    "keys": [],
    "references": [
      {
        "path": "evidence/12/2026-10-27-engineering-box-render-v004/demo-files/engineering_box_render_v001.blend",
        "label": "小盒分離展示的渲染場景 v001"
      },
      {
        "path": "evidence/12/2026-10-27-engineering-box-render-v004/demo-files/box_lid_render_v001.png",
        "label": "640×480 渲染輸出 PNG（不是介面截圖）"
      },
      {
        "path": "evidence/12/2026-10-27-engineering-box-render-v004/box-render-verification-v004.json",
        "label": "小盒渲染操作、幾何與輸出路徑讀值摘要"
      }
    ],
    "kind": "prep",
    "summary": "開啟示範場景後，File › Save As，選自己的工作區與未使用的新檔名。 另存個人場景並核對輸出。",
    "lead": "開啟示範場景後，File › Save As，選自己的工作區與未使用的新檔名。 另存個人場景並核對輸出。"
  }
};
