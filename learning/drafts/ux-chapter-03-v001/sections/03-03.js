window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-03"] = {
  "id": "03-03",
  "title": "基座、立柱與訊號球",
  "keyPoint": "依高度關係堆出基座、立柱與訊號球。",
  "glossary": [
    {
      "term": "BeaconBase",
      "label": "BeaconBase",
      "text": "平台上方的基座物件名稱。"
    },
    {
      "term": "Post",
      "label": "Post",
      "text": "連接基座與訊號球的立柱。"
    },
    {
      "term": "UV Sphere",
      "label": "UV Sphere",
      "text": "以經緯線分段建立的球形網格。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-03-01",
      "title": "新增基座",
      "lead": "訊號站工作檔 / Object Mode 新增基座。",
      "actions": [
        "本回合只新增一個 Cube 作為 BeaconBase。"
      ],
      "checks": [
        "新方塊有作用中外框",
        "Outliner 中對應的新物件列反白"
      ],
      "pitfalls": [],
      "locate": "訊號站工作檔 / Object Mode",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-03-01-base.png",
          "sha256": "b0dff50098c1e7872b318efa1356da8c6efc4e3dc8f18280587f7dd1dc32590c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube.001 基座選取，尺寸 0.7×0.7×0.3 m、Location Z 0.35 m。",
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
                586,
                437,
                59,
                47
              ],
              "label": "基座"
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
      "stepId": "ch03-02-03-02",
      "title": "設定基座尺寸",
      "lead": "BeaconBase / Dimensions 設定基座尺寸。",
      "actions": [
        "在 N 側欄 Item 把基座 Dimensions 依序設為 <code>0.7</code>、<code>0.7</code>、<code>0.3 m</code>。"
      ],
      "checks": [
        "基座 Dimensions X、Y 各 <code>0.7 m</code>",
        "Dimensions Z 為 <code>0.3 m</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "BeaconBase / Dimensions",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-03-01-base.png",
          "sha256": "b0dff50098c1e7872b318efa1356da8c6efc4e3dc8f18280587f7dd1dc32590c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube.001 基座選取，尺寸 0.7×0.7×0.3 m、Location Z 0.35 m。",
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
                586,
                437,
                59,
                47
              ],
              "label": "基座"
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
      "stepId": "ch03-02-03-03",
      "title": "核對基座位置",
      "lead": "BeaconBase / Location 核對基座位置。",
      "actions": [
        "把基座 Location 設為 <code>0</code>、<code>0</code>、<code>0.35 m</code>。"
      ],
      "checks": [
        "基座 Location Z 為 <code>0.35 m</code>",
        "記錄計算底面 Z0.2、頂面 Z0.5 m"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "BeaconBase / Location",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-03-01-base.png",
          "sha256": "b0dff50098c1e7872b318efa1356da8c6efc4e3dc8f18280587f7dd1dc32590c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube.001 基座選取，尺寸 0.7×0.7×0.3 m、Location Z 0.35 m。",
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
                586,
                437,
                59,
                47
              ],
              "label": "基座"
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
      "stepId": "ch03-02-03-04",
      "title": "新增立柱 Post",
      "lead": "訊號站工作檔 · Object Mode · N 側欄 Item 新增立柱 Post。",
      "actions": [
        "Add › Mesh › Cube 新增方塊，在 N 側欄把 Dimensions 設為 <code>0.12</code>、<code>0.12</code>、<code>1.2 m</code>。",
        "Location 設為 <code>0</code>、<code>0</code>、<code>1.1 m</code>。"
      ],
      "checks": [
        "Post 的 Dimensions 為 <code>0.12</code>×<code>0.12</code>×<code>1.2 m</code>",
        "Location Z 為 <code>1.1 m</code>，計算底頂為 <code>0.5</code>／<code>1.7 m</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "訊號站工作檔 · Object Mode · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-03-02-post.png",
          "sha256": "a17872962700afd6ad7cf42b99472731281a547e6eb284852654cd4752749f9c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cube.002 立柱選取，尺寸 0.12×0.12×1.2 m、Location Z 1.1 m。",
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
                604,
                392,
                23,
                71
              ],
              "label": "立柱"
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
      "stepId": "ch03-02-03-05",
      "title": "新增訊號球 Signal",
      "lead": "訊號站工作檔 · Object Mode · N 側欄 Item 新增訊號球 Signal。",
      "actions": [
        "Add › Mesh › UV Sphere 新增球體，Dimensions 設為 <code>0.5</code>、<code>0.5</code>、<code>0.5 m</code>。",
        "Location 設為 <code>0</code>、<code>0</code>、<code>1.95 m</code>。"
      ],
      "checks": [
        "Signal 三軸 Dimensions 均為 <code>0.5 m</code>",
        "Location Z 為 <code>1.95 m</code>，計算底頂為 <code>1.7</code>／<code>2.2 m</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "訊號站工作檔 · Object Mode · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-03-03-signal.png",
          "sha256": "ff97adac4e842e40013102a164e49b21947f74d2853ecdd0448ff7f9775f5a91",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Sphere 已選取，Dimensions 0.5×0.5×0.5 m、Location Z 1.95 m。",
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
                592,
                365,
                48,
                50
              ],
              "label": "訊號球"
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
