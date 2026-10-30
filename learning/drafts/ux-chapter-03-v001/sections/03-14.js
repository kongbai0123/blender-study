window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-14"] = {
  "id": "03-14",
  "title": "固定尺寸上蓋與環形唇邊",
  "keyPoint": "建立蓋板與環唇，核對盒蓋尺寸後保存。",
  "glossary": [
    {
      "term": "Lid",
      "label": "Lid",
      "text": "本分支上蓋的物件名稱。"
    },
    {
      "term": "Body",
      "label": "Body",
      "text": "本分支原盒的物件名稱。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-05-05-02",
      "title": "隱藏盒體並新增蓋板",
      "lead": "Object Mode · Body 已選取 隱藏盒體並新增蓋板。",
      "actions": [
        "按 H（Object › Show/Hide › Hide Selected）暫時隱藏 Body。",
        "Add › Mesh › Cube 新增方塊，按 <kbd>F2</kbd> 改名為 Lid。"
      ],
      "checks": [
        "Body 在視窗中隱藏",
        "新增物件命名 Lid，Outliner 可找到兩件"
      ],
      "pitfalls": [],
      "locate": "Object Mode · Body 已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-03-plate.png",
          "sha256": "dd45e229322354b15550532c8419a7f227771dadf3648d0ab7cd0eb9977bbfe4",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Lid 已選取，Body 隱藏，Lid 位置 Z 16 mm、Scale 1、尺寸 60×40×2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                318,
                228,
                142
              ],
              "label": "蓋板 60 × "
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-03",
      "title": "設定蓋板尺寸與位置",
      "lead": "Lid 已選取 · N 側欄 Item 設定蓋板尺寸與位置。",
      "actions": [
        "Dimensions 輸入 <code>60mm</code>、<code>40mm</code>、<code>2mm</code>；Location 設 <code>0</code>、<code>0</code>、<code>16mm</code>。",
        "Object › Apply › Scale（<kbd>Ctrl</kbd>+<kbd>A</kbd> › Scale）。"
      ],
      "checks": [
        "Lid Dimensions <code>60</code>×<code>40</code>×<code>2 mm</code>，Scale <code>1</code>",
        "Location Z16 mm，計算板底Z15、板頂Z17"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Ctrl</kbd>+<kbd>A</kbd> 只開選單，不直接套用 Scale；不能用它替代 Boolean／Solidify 修改器的 Apply。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Lid 已選取 · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-03-plate.png",
          "sha256": "dd45e229322354b15550532c8419a7f227771dadf3648d0ab7cd0eb9977bbfe4",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Lid 已選取，Body 隱藏，Lid 位置 Z 16 mm、Scale 1、尺寸 60×40×2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                318,
                228,
                142
              ],
              "label": "蓋板 60 × "
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-04",
      "title": "從底部選取蓋板底面",
      "lead": "Lid 已選取 從底部選取蓋板底面。",
      "actions": [
        "按 <kbd>Tab</kbd> 進 Edit Mode，按 <kbd>3</kbd> 切到面選取。",
        "View › Viewpoint › Bottom（<kbd>Ctrl</kbd>+<kbd>Numpad 7</kbd>），只點選蓋板底面。"
      ],
      "checks": [
        "模式為 Edit Mode 且面選取反白",
        "Bottom Orthographic 中只有底面被選取"
      ],
      "pitfalls": [],
      "locate": "Lid 已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-04-bottom-face.png",
          "sha256": "55405abaab833828e5e92b3413ba295a794ab0017fe037014fd96aa9085917b9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Bottom Orthographic、Edit Mode 面選模式；底部矩形面已選取，Local Median Z -1 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                28,
                96,
                20
              ],
              "label": "Edit Mod"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-05",
      "title": "內插並擠出唇外緣",
      "lead": "Edit Mode · 底面已選取 內插並擠出唇外緣。",
      "actions": [
        "按 <kbd>I</kbd>，輸入 <code>2.2mm</code> 後 <kbd>Enter</kbd>：留下 <code>55.6</code> × <code>35.6 mm</code> 的唇外輪廓。",
        "按 <kbd>E</kbd>，輸入 <code>4mm</code> 後 <kbd>Enter</kbd>：沿底面法向往下長出 <code>4 mm</code>。"
      ],
      "checks": [
        "底面出現內插輪廓，名義<code>55.6</code>×<code>35.6 mm</code>",
        "擠出後向下形成凸出部分，目標深<code>4 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Edit Mode · 底面已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-05-lip-footprint.png",
          "sha256": "89dc9643323bd2c380bf99f4617c9578d1f3f46a6f567de1897b47efedfb3cf1",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Lid底視出現第一圈內插；Local Median Z為−1 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                405,
                339,
                417,
                22
              ],
              "label": "第一圈內插"
            },
            {
              "n": 2,
              "box": [
                961,
                170,
                228,
                23
              ],
              "label": "局部面Z負1"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-06-lip-depth.png",
          "sha256": "b3dde299af17e7f358b1a32bc5dfb4f23e27692d4d64606751a61c1f63dccbb2",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "底視輪廓相同但Local Median Z變為−5 mm，顯示擠出後高度。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                170,
                228,
                23
              ],
              "label": "局部面Z負5"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-06",
      "title": "內插環壁並推回中心",
      "lead": "Edit Mode · 中心面仍選取 內插環壁並推回中心。",
      "actions": [
        "按 <kbd>I</kbd>，輸入 <code>2mm</code> 後 <kbd>Enter</kbd>：留下 <code>2 mm</code> 環壁。",
        "按 <kbd>E</kbd>，輸入 <code>-4mm</code> 後 <kbd>Enter</kbd>：把中心面推回蓋板底面的高度。"
      ],
      "checks": [
        "底視可見環狀輪廓",
        "中央面已推回蓋板底高，名義唇內<code>51.6</code>×<code>31.6 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "E 的正方向沿所選面法向，不能把所有面都當世界 +Z。Inset 厚度與擠出位移不同，並非物件絕對 Dimensions。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Edit Mode · 中心面仍選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-07-lip-wall.png",
          "sha256": "5cb9140762f03cb42d0bfbe6b2e63767c466108f3f228effa5c1f6e3939bf2f3",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "第二次內插後出現兩圈輪廓；中心面仍被選中。",
          "marks": [
            {
              "n": 1,
              "box": [
                405,
                339,
                417,
                30
              ],
              "label": "兩圈輪廓"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-08-lip-recess.png",
          "sha256": "56a321ea7661ab3448514ec5a1e105f425bc58fe53712e6b44dfb1de8844da17",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "推回中心面後Local Median Z回−1 mm；唇深不能只靠底視量得。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                170,
                228,
                23
              ],
              "label": "推回至Z負1"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-09-underside-checked.png",
          "sha256": "c97b0253251f190a6f1e4541d7ea809a0b2bcfc2acd7485bec602d3e7065afde",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "底部斜視可見環形唇邊與內凹，右側Dimensions為60×40×6 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                436,
                518,
                417,
                112
              ],
              "label": "環形唇邊"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                63
              ],
              "label": "上蓋外框"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-07",
      "title": "顯示盒體並檢查網格",
      "lead": "Edit Mode → Object Mode 顯示盒體並檢查網格。",
      "actions": [
        "按 <kbd>Tab</kbd> 回 Object Mode，按 <kbd>Alt</kbd>+<kbd>H</kbd> 顯示 Body；在 Outliner 重新選取 Lid，再以 <kbd>N</kbd> 側欄核對 Lid Dimensions 為 <code>60</code> × <code>40</code> × <code>6 mm</code>。",
        "保持 Lid 選取，用 <code>03</code>-<code>13</code> 的方法做一次 Non Manifold 檢查。"
      ],
      "checks": [
        "Body 恢復顯示，選中的 Lid 為<code>60</code>×<code>40</code>×<code>6 mm</code>",
        "Lid 執行 Non Manifold 後沒有邊反白"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "Edit Mode → Object Mode",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-09-underside-checked.png",
          "sha256": "c97b0253251f190a6f1e4541d7ea809a0b2bcfc2acd7485bec602d3e7065afde",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "底部斜視可見環形唇邊與內凹，右側Dimensions為60×40×6 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                436,
                518,
                417,
                112
              ],
              "label": "環形唇邊"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                63
              ],
              "label": "上蓋外框"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-10-non-manifold.png",
          "sha256": "0d53d105324470377605bcafff0eadd6f2eaa167449f42893b78bcf7d3dd13bb",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Select Non-Manifold後沒有邊反白，側欄顯示Nothing selected。",
          "marks": [
            {
              "n": 1,
              "box": [
                959,
                111,
                142,
                27
              ],
              "label": "未選到邊"
            },
            {
              "n": 2,
              "box": [
                64,
                894,
                160,
                26
              ],
              "label": "非流形選取"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png",
          "sha256": "bc12d5f81fd5424cef7dd64c295941c8a31de430a45818782e249f8b1d2fec64",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "盒蓋分離，上蓋下方突出環形唇邊；作用中Body尺寸60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                332,
                331,
                544,
                66
              ],
              "label": "下方環形唇邊"
            },
            {
              "n": 2,
              "box": [
                963,
                399,
                226,
                64
              ],
              "label": "盒體外框"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-05-05-08",
      "title": "保存並重新開啟",
      "lead": "File 選單 · 教學頁「檔案版本」 保存並重新開啟。",
      "actions": [
        "保存 <code>u05_lid_v001.blend</code>；File › Open 重開，核對 Body 與 Lid 的尺寸。",
        "到教學頁「檔案版本」以單元 <code>05</code> 登記上蓋場景，並核對路徑與 SHA-<code>256</code>。"
      ],
      "checks": [
        "重開後 Body 為<code>60</code>×<code>40</code>×<code>30</code>、Lid為<code>60</code>×<code>40</code>×<code>6 mm</code>",
        "版本表有 <code>u05_lid_v001.blend</code> 與來源指紋"
      ],
      "pitfalls": [],
      "locate": "File 選單 · 教學頁「檔案版本」",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-14-saved.png",
          "sha256": "89d0a195cd591adf034f0756b16805101ee4fec1dd3d55b0b1b4a12e41df607a",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "盒蓋合攏；底部顯示Saved as u05_lid_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                630,
                996,
                213,
                21
              ],
              "label": "上蓋保存提示"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-15-open-saved.png",
          "sha256": "4de364f2af466552066c5bae79e8e771645da57f0362a93d01768ae0eb1b74be",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Open 對話框列出 u05_lid_v001.blend，檔名欄同名。",
          "marks": [
            {
              "n": 1,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Open"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-16-reopened-verified.png",
          "sha256": "5dd4f07399cc16e3f2487093f2db9c6e507c771b2c9f9c7910589b465bebed0f",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "盒蓋合攏但目前活動物件是Body，右側60×40×30 mm不能當作上蓋尺寸。",
          "marks": [
            {
              "n": 1,
              "box": [
                1287,
                92,
                94,
                22
              ],
              "label": "活動盒體"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "盒體尺寸"
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
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch03-05-05-01",
    "title": "另存上蓋工作檔",
    "actions": [
      "開啟 <code>u04_box_v001.blend</code>，在 N 側欄核對 Body 外形 <code>60</code> × <code>40</code> × <code>30 mm</code>。",
      "File › Save As 另存 <code>learning/workspaces/05/u05_lid_v001.blend</code>。"
    ],
    "checks": [
      "保存通知或重開檔名為 <code>u05_lid_v001.blend</code>",
      "原盒 <code>u04_box_v001.blend</code> 保留"
    ],
    "pitfalls": [],
    "locate": "Blender · File 選單",
    "figures": [
      {
        "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-01-source-open-dialog.png",
        "sha256": "6412d82176b09f0f2b9b64c1fd32e01f2630d220af8c338bb0ae968974122164",
        "size": [
          1060,
          600
        ],
        "caption": "先開啟原盒來源；此為示範的隔離副本路徑，請選自己的原盒檢查點。",
        "tab": "開啟來源",
        "marks": [
          {
            "n": 1,
            "box": [
              250,
              63,
              258,
              26
            ],
            "label": "原盒來源檔名"
          }
        ]
      },
      {
        "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-02-source-body-checked.png",
        "sha256": "b04ade7f0a4f5ec5056fb76406b887b04e6f1e9527198d8281ffeb30e1d0e49d",
        "size": [
          1494,
          1019
        ],
        "caption": "原盒已命名Body，Dimensions60×40×30 mm。另存前置步驟請依自己的Save As視窗核對。",
        "tab": "核對原盒",
        "marks": [
          {
            "n": 1,
            "box": [
              961,
              399,
              229,
              64
            ],
            "label": "原盒尺寸"
          }
        ]
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "Blender · File 選單 另存上蓋工作檔。",
    "lead": "Blender · File 選單 另存上蓋工作檔。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
