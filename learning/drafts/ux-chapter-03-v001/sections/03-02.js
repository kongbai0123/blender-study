window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-02"] = {
  "id": "03-02",
  "title": "地面與平台",
  "keyPoint": "建立地面與平台，核對尺寸與接地高度。",
  "glossary": [
    {
      "term": "Plane",
      "label": "Plane",
      "text": "沒有初始厚度的平面網格。"
    },
    {
      "term": "Location",
      "label": "Location",
      "text": "物件位置欄位，本節用 Z 決定高低。"
    },
    {
      "term": "平台",
      "label": "平台",
      "text": "本節尺寸為2.4×2.4×0.2 m的方塊。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-02-01",
      "title": "建立 4 m 地面",
      "lead": "自己的訊號站場景 / Ground 建立 4 m 地面。",
      "actions": [
        "本回合先用 3D Viewport 的 Add › Mesh › Plane 建立地面，在 Sidebar（View › Sidebar）把 Dimensions X、Y 以分回合方式設為 <code>4 m</code>。"
      ],
      "checks": [
        "Plane 的 Dimensions X、Y 均為 <code>4 m</code>",
        "Location Z 為 <code>0 m</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "自己的訊號站場景 / Ground",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-01-add-mesh-plane.png",
          "sha256": "9d5a76b54dcfee8dccdbeb14044b5fc656641bc2fd6276ffafb72f4627b9ba9f",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Add › Mesh 子選單展開且 Plane 被突出顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                255,
                28,
                32,
                20
              ],
              "label": "Add"
            },
            {
              "n": 2,
              "box": [
                255,
                51,
                164,
                20
              ],
              "label": "Mesh"
            },
            {
              "n": 3,
              "box": [
                426,
                50,
                162,
                20
              ],
              "label": "Plane"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-03-plane-x.png",
          "sha256": "a617246fa3631ef63f41ec7cd5b30eaee111a5e4cb7ad21cb5185c9cab3a3db9",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Plane 被選取，Dimensions X 4 m、Y 2 m；Scale X 2.000。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                401,
                228,
                20
              ],
              "label": "Dimensio"
            },
            {
              "n": 2,
              "box": [
                533,
                425,
                176,
                109
              ],
              "label": "Plane"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-04-plane-y.png",
          "sha256": "cdf26c6c1f755262db5691cd239a49daab1a0b7c6fc8d81819133e0f43050294",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Plane 尺寸 X/Y 4 m、Z 0 m；Scale X/Y 2。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                420,
                228,
                20
              ],
              "label": "Dimensio"
            },
            {
              "n": 2,
              "box": [
                963,
                172,
                176,
                20
              ],
              "label": "Location"
            },
            {
              "n": 3,
              "box": [
                492,
                418,
                260,
                126
              ],
              "label": "地面 4 × 4"
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
      "stepId": "ch03-02-02-02",
      "title": "建立平台",
      "lead": "下一小回合 / Platform 建立平台。",
      "actions": [
        "再用 Add › Mesh › Cube 建立平台，分次設 Dimensions = <code>2.4</code>、<code>2.4</code>、<code>0.2 m</code>。"
      ],
      "checks": [
        "平台 Dimensions X、Y 均為 <code>2.4 m</code>",
        "Dimensions Z 為 <code>0.2 m</code>"
      ],
      "pitfalls": [],
      "locate": "下一小回合 / Platform",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-05-platform-added.png",
          "sha256": "6bf4b8574ec4887b5fb8fa75ae44689e397c5c4a3b2e483cbd809e369ca96cfb",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube 被選取，尺寸 2×2×2 m；Plane 在下方。",
          "marks": [
            {
              "n": 1,
              "box": [
                547,
                401,
                141,
                153
              ],
              "label": "新增的 Cube"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "Dimensio"
            }
          ]
        },
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-06-platform-size.png",
          "sha256": "02b8069d77acfe764a6d918b7153547a1fd7f9003881eee49b1413e84c33c350",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Cube 尺寸 2.4×2.4×0.2 m，Scale 1.2/1.2/0.1。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "Dimensio"
            },
            {
              "n": 2,
              "box": [
                537,
                432,
                162,
                89
              ],
              "label": "平台"
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
      "stepId": "ch03-02-02-03",
      "title": "核對平台位置",
      "lead": "Platform / Location 核對平台位置。",
      "actions": [
        "在 N 側欄 Item 的 Location，將 X、Y 設為 <code>0 m</code>，將 Z 輸入 <code>0.1 m</code>。",
        "確認 Dimensions Z 為 <code>0.2 m</code>，平台底面貼近 Z=<code>0</code> 的地面。"
      ],
      "checks": [
        "Location 為 <code>0</code>、<code>0</code>、<code>0.1 m</code>",
        "用 <code>0.1</code>−<code>0.2</code>÷<code>2</code> 計算平台底面為 Z0"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Platform / Location",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-02-07-platform-z.png",
          "sha256": "5b1d50a694b344f7b0cb6f9007c47da5a7e0b47b3c9a4a5025ff72bbe610369d",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube Location Z 0.1 m，尺寸 Z 0.2 m。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                172,
                176,
                20
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                536,
                428,
                163,
                89
              ],
              "label": "平台"
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
