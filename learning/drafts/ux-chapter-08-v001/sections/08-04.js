window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-04"] = {
  "id": "08-04",
  "title": "內腔 Y 方向與安全檢查",
  "keyPoint": "加入 Y Driver，分別核對欄位與生成幾何。",
  "glossary": [
    {
      "term": "Driver",
      "label": "Driver",
      "text": "讓目標數值依來源屬性計算的連結。"
    },
    {
      "term": "更新圖示",
      "label": "更新圖示",
      "text": "Sketcher頂端Leave右邊重新求解草圖的按鈕。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-xy-driver-01",
      "title": "複製外框 Y 作來源",
      "lead": "本次外框 Body Sketch 為70×40 mm；第二個 Distance 是 Y。 複製外框 Y 作來源。",
      "actions": [
        "右鍵第二個 Distance，選 Copy as New Driver。",
        "離開外框草圖，從 Body 的 Edit Sketch 選 Body.001 Sketch。"
      ],
      "checks": [
        "外框Y來源欄右鍵選單有 Copy as New Driver",
        "離開後進入 Body.001 Sketch"
      ],
      "pitfalls": [],
      "locate": "本次外框 Body Sketch 為70×40 mm；第二個 Distance 是 Y。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-02-source-menu.png",
          "sha256": "c41c57cc0db0161045cab16371a4be214cab6a2b2af9ac8de0323fef6e95cd21",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "外框Y欄右鍵選單最下方可見Copy as New Driver。",
          "marks": [
            {
              "n": 1,
              "box": [
                944,
                873,
                220,
                26
              ],
              "label": "複製來源"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-04-sketch-menu.png",
          "sha256": "d75e8310edd9bcfca193aa2a3797733ae48cd2396a4d9bad6018a14d56a4170c",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "右鍵選Body.001 Sketch進入內腔，圖上兩個草圖選項可辨。",
          "marks": [
            {
              "n": 1,
              "box": [
                755,
                455,
                228,
                25
              ],
              "label": "內腔草圖"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-05-inner-sketch.png",
          "sha256": "d3e9fab4e4bd33568ed001f39b9283fa09029aaaa9478e5453fdde519906eac7",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "內腔Body.001 Sketch的X Driver66mm，Y仍36mm；這是建立Y Driver前狀態。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "內腔起點"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json",
          "label": "X／Y 驅動與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-driver-02",
      "title": "建立內腔 Y Driver",
      "lead": "Body.001 Sketch；本例第二個 Distance 是內腔 Y。 建立內腔 Y Driver。",
      "actions": [
        "右鍵第二個 Distance，選 Paste Driver。",
        "選 Edit Driver，改為 Scripted Expression，使用本次來源變數減<code>4</code>。"
      ],
      "checks": [
        "內腔Y貼上後為紫色<code>40 mm</code>",
        "運算式改為來源減<code>4</code>後顯示<code>36 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body.001 Sketch；本例第二個 Distance 是內腔 Y。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-07-pasted.png",
          "sha256": "6ab19c3477d9eb53846d8a5155329a0b4887793e8dc3030cc3d3c230c612a00e",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "內腔兩個紫色欄66／40mm，Y剛貼上來源尚未減4；不是目標66／36。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "貼上暫態"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-10-type-menu.png",
          "sha256": "1ac68d62a745b1c7f40787c6f6899e87bf66dc6284ff3f553833e1862d0f6a6c",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Y Driver的Type選單展開，Scripted Expression可選；來源仍40，結果暫40。",
          "marks": [
            {
              "n": 1,
              "box": [
                895,
                736,
                160,
                25
              ],
              "label": "運算式類型"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-12-formula.png",
          "sha256": "6c81a492e2a4ed6f3829dd70a58d633c1b8d5edee4415d8ef3c3d0757d7d987d",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Scripted Expression的減4公式；Driver Value36、來源Value40，Y欄紫色36mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                842,
                694,
                202,
                22
              ],
              "label": "來源減4"
            },
            {
              "n": 2,
              "box": [
                842,
                627,
                160,
                24
              ],
              "label": "結果36"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json",
          "label": "X／Y 驅動與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-driver-03",
      "title": "更新並保存",
      "lead": "Body.001 Sketch，兩個內腔欄位各有 Driver。 更新並保存。",
      "actions": [
        "點草圖頂端 Leave 按鈕右邊的更新圖示。",
        "另存獨立示範版本。"
      ],
      "checks": [
        "更新後內腔兩個尺寸欄為紫色",
        "另存通知顯示本次新版本"
      ],
      "pitfalls": [],
      "locate": "Body.001 Sketch，兩個內腔欄位各有 Driver。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-13-solve.png",
          "sha256": "f80c1580477ce2b8c7b50dd3add2b97ad0d92cd4bdebcd9edcbd4c112daf05fe",
          "size": [
            1494,
            1019
          ],
          "caption": "手動更新後紫色66／36mm；Leave右側圓箭頭可見；中央標註重疊仍不可量界限。",
          "marks": [
            {
              "n": 1,
              "box": [
                1170,
                113,
                20,
                37
              ],
              "label": "更新按鈕"
            },
            {
              "n": 2,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "66與36"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-14-saved.png",
          "sha256": "d9d61769d6c93c604ccf4d493aa2709badfaee0f230bf1688cb3ed42782f7577",
          "size": [
            1494,
            1019
          ],
          "caption": "雙Driver66／36mm與底部Saved as manual_box_xy_drivers_v001.blend可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                590,
                995,
                294,
                23
              ],
              "label": "雙軸存檔"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/demo-files/manual_box_xy_drivers_v001.blend",
          "label": "X／Y 驅動初始示範場景"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json",
          "label": "X／Y 驅動與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-driver-04",
      "title": "外框改為 80 × 50",
      "lead": "重開 X／Y Driver 草案；切換到 Body Sketch。 外框改為 80 × 50。",
      "actions": [
        "離開內腔草圖、點盒體側面選 Body，進入 Body Sketch。",
        "將 X 改為<code>80</code>、Y 改為<code>50 mm</code>。"
      ],
      "checks": [
        "Body Sketch 的Distance為<code>80</code>、<code>50 mm</code>",
        "更新前讀值仍是切割體X2～<code>68</code>、Y2～<code>38</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "重開 X／Y Driver 草案；切換到 Body Sketch。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-04-sketch-menu.png",
          "sha256": "12cd87dc122677e0c7db29c7e86c5d84efcc98f418ca825ef37d367a935db6ff",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Body右鍵Edit Sketch可選Body Sketch外框，操作入口可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                755,
                435,
                228,
                23
              ],
              "label": "外框草圖"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-05-outer-sketch.png",
          "sha256": "a257d6c5fd5893741bf7f9097703ebe4117e05df8e0ae6984ac171437d89e0b7",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "外框草圖起始70／40mm，Fully defined；下一步才改成80／50。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "起始70與40"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-06-outer-80x50.png",
          "sha256": "02365cb298ebdee4af988fffcb219927ba9ce5f56ff65ee2d3324a9dc3baed93",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Body Sketch改成80／50mm，Fully defined，內部輪廓仍舊，尚未更新內腔。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "外框80與50"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json",
          "label": "X／Y 驅動與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-driver-05",
      "title": "更新並重開核對",
      "lead": "外框80×50 mm；切換進入 Body.001 Sketch。 更新並重開核對。",
      "actions": [
        "對照兩個 Driver 欄位，點頂端更新圖示。",
        "另存獨立版本並重開，核對摘要。"
      ],
      "checks": [
        "更新後內腔欄為<code>76</code>、<code>46 mm</code>",
        "重開後讀值X2～<code>78</code>、Y2～<code>48</code>且兩個Driver有效"
      ],
      "pitfalls": [],
      "locate": "外框80×50 mm；切換進入 Body.001 Sketch。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-07-inner-before-solve.png",
          "sha256": "950ef1a4047ebea00e493f41f3d63d03509ece8de427ddf1d7935bcd6247ea4f",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "更新前內腔欄76／46mm但黑色生成範圍仍小於尺寸線，Fully defined不能證幾何同步。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "Driver值"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-08-inner-after-solve.png",
          "sha256": "f4c80bd0d33261947924670ceb30564b8885958d80114a47275e41c49ddc7293",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "點更新後內矩形拉大，仍是76／46mm，右上更新箭頭位置可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                1170,
                113,
                20,
                37
              ],
              "label": "更新按鈕"
            },
            {
              "n": 2,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "76與46"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-10-reopened.png",
          "sha256": "722fa9bb3f0e82e0dc3fc88d9319e5ae0e4906354739b155cdafa6c77db46288",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "重開後Body.001 Sketch紫色76／46mm，Fully defined；tooltip部分遮住中央標註，仍應看側欄。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "重開內腔值"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/demo-files/manual_box_xy_80x50_v002.blend",
          "label": "X80 Y50 手動更新後另存場景"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/xy-manual-update-verification-v001.json",
          "label": "X／Y 驅動與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-safety-01",
      "title": "貼上後先核對公式",
      "lead": "貼上後先核對公式。",
      "actions": [
        "對照本節第<code>1</code>～<code>2</code>步的原圖及讀值，辨認剛貼上來源時的紫色 Y 欄與暫時狀態。",
        "比較公式設為來源變數減<code>4</code>前後的示範摘要，不需要在目前成果中重新貼上。"
      ],
      "checks": [
        "過程原圖顯示貼上後Y暫為<code>40 mm</code>",
        "對照讀值表，修正前Y2～<code>42</code>、修正後Y2～<code>38</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "回看同一示範較早的外框Y40、內腔尚未設定減4公式階段；不改動目前已保存的80×50成果。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-07-pasted.png",
          "sha256": "6ab19c3477d9eb53846d8a5155329a0b4887793e8dc3030cc3d3c230c612a00e",
          "size": [
            1494,
            1019
          ],
          "caption": "內腔兩個紫色欄66／40mm，Y剛貼上來源尚未減4；不是目標66／36。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "貼上暫態"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-y-driver-v002/Y-12-formula.png",
          "sha256": "6c81a492e2a4ed6f3829dd70a58d633c1b8d5edee4415d8ef3c3d0757d7d987d",
          "size": [
            1494,
            1019
          ],
          "caption": "Scripted Expression的減4公式；Driver Value36、來源Value40，Y欄紫色36mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                842,
                694,
                202,
                22
              ],
              "label": "來源減4"
            },
            {
              "n": 2,
              "box": [
                842,
                627,
                160,
                24
              ],
              "label": "結果36"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-safety-review-v001/xy-intermediate-review-v001.json",
          "label": "手工 X／Y 驅動中間狀態安全核對摘要"
        }
      ]
    },
    {
      "stepId": "ch08-xy-safety-02",
      "title": "Fully defined 仍要更新",
      "lead": "回看本節第4～5步更新前的80×50場次；目前已更新成果不需倒退修改。 Fully defined 仍要更新。",
      "actions": [
        "對照更新前的 Fully defined／紫色欄位與程式讀值。",
        "再對照更新後的摘要與自己已保存模型；若自行重演，先另存新副本。"
      ],
      "checks": [
        "更新前原圖可同時看到 Fully defined 與紫色尺寸",
        "前後讀值分別列舊界限與更新後X2～<code>78</code>、Y2～<code>48</code>"
      ],
      "pitfalls": [],
      "locate": "回看本節第4～5步更新前的80×50場次；目前已更新成果不需倒退修改。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-verify-v001/VERIFY-07-inner-before-solve.png",
          "sha256": "950ef1a4047ebea00e493f41f3d63d03509ece8de427ddf1d7935bcd6247ea4f",
          "size": [
            1494,
            1019
          ],
          "caption": "更新前內腔欄76／46mm但黑色生成範圍仍小於尺寸線，Fully defined不能證幾何同步。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "Driver值"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-xy-safety-review-v001/xy-intermediate-review-v001.json",
          "label": "手工 X／Y 驅動中間狀態安全核對摘要"
        }
      ]
    }
  ]
};
