window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-07"] = {
  "id": "08-07",
  "title": "多組尺寸與超界反例",
  "keyPoint": "測三組尺寸，再用超界反例辨認失配。",
  "glossary": [
    {
      "term": "範圍",
      "label": "範圍",
      "text": "本例形狀鍵Value的上下限−2至2，超出時會被夾住。"
    },
    {
      "term": "超界",
      "label": "超界",
      "text": "來源尺寸要求的變形超出形狀鍵可表達的範圍。"
    },
    {
      "term": "Key 1",
      "label": "Key 1",
      "text": "本節X方向形狀鍵，Value上限2會限制可伸長的尺寸。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-manual-lid-cases-01",
      "title": "改為 90 × 50",
      "lead": "雙 Driver 試驗場景，基準80×50。 改為 90 × 50。",
      "actions": [
        "選 Body 並進 Body Sketch，將 X80改<code>90</code>，Y維持<code>50</code>。",
        "進 Body.001 Sketch 手動更新，再核對摘要。"
      ],
      "checks": [
        "外框 Distance 為<code>90</code>、<code>50 mm</code>",
        "更新後讀值X2～<code>88</code>、Y2～<code>48</code>，<code>Key 1</code>／<code>2</code>為<code>1</code>／<code>0</code>"
      ],
      "pitfalls": [],
      "locate": "雙 Driver 試驗場景，基準80×50。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/LINK-03-outer-sketch.png",
          "sha256": "1de32f144a69380cc467c2048ce5dedd73946b89bae43304601cb47565844cc8",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "下一組試驗起點仍為Body Sketch80／50mm，Fully defined。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "基準80與50"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-01-x90y50-before.png",
          "sha256": "73461d86d18eb389d6cfc3da1c98aeb882367ea7a809ded7ddd9a99fac5289cb",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "外框Distance90、50且全約束，內腔仍為前態。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                628,
                140,
                40
              ],
              "label": "外框90與50"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-02-x90y50-after.png",
          "sha256": "efab0ab30bceb0e776e00a9804a2209ffdba880df965d11dee42291ba2a4353f",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Body.001 Sketch內腔Distance86、46；畫面幾何與標註已更新，中央部分文字仍重疊。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                628,
                140,
                40
              ],
              "label": "內腔86與46"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/manual-lid-multicase-verification-v001.json",
          "label": "盒蓋多組尺寸手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-cases-02",
      "title": "改為 80 × 60",
      "lead": "前一步已更新90×50內腔；重新進 Body Sketch。 改為 80 × 60。",
      "actions": [
        "將 X90改回<code>80</code>、同時將 Y50改為<code>60</code>。",
        "進 Body.001 Sketch 手動更新，再核對摘要。"
      ],
      "checks": [
        "本步同時把X改<code>80</code>、Y改<code>60 mm</code>",
        "更新後讀值X2～<code>78</code>、Y2～<code>58</code>，<code>Key 1</code>／<code>2</code>為<code>0</code>／<code>1</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "前一步已更新90×50內腔；重新進 Body Sketch。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-03-x80y60-before.png",
          "sha256": "ca10c281bd1741282fab3778249867ec676a90e34e5ed3f637f4dcc11cbcd290",
          "size": [
            1494,
            1019
          ],
          "caption": "外框Body Sketch80／60mm；內部舊矩形向右超出外框，顯示更新前不同步。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "80與60"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-04-x80y60-after.png",
          "sha256": "bcf688bbad75e6e652f8d17edc60c7d0c23f362e59009a3bb6fcc14b1865d729",
          "size": [
            1494,
            1019
          ],
          "caption": "更新內腔後紫色76／56mm，Fully defined，矩形回到外框內；界限須查讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "76與56"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/manual-lid-multicase-verification-v001.json",
          "label": "盒蓋多組尺寸手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-cases-03",
      "title": "雙軸縮小並保存",
      "lead": "前一步已更新80×60內腔；重新進 Body Sketch。 雙軸縮小並保存。",
      "actions": [
        "將外框改為<code>70</code>×<code>40</code>，再進內腔草圖手動更新。",
        "另存獨立試驗版本並重開，對照摘要。"
      ],
      "checks": [
        "外框縮成<code>70</code>、<code>40 mm</code>",
        "更新重開後X2～<code>68</code>、Y2～<code>38</code>，兩個Key皆<code>-1</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "前一步已更新80×60內腔；重新進 Body Sketch。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-05-x70y40-before.png",
          "sha256": "e40b6f3ba25f13d0dcf629de40e70662b5e267ab99e934bb13e861d9fcbf5d3e",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "外框70／40mm，舊內腔輪廓向右上突出；雙軸縮小後未更新的反例。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "70與40"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-06-x70y40-after.png",
          "sha256": "cdc7e0ec2a61ac415d93936551a5801bc2ca79d15898ce588fd3726529af937c",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "更新內腔後紫色66／36mm，Fully defined；幾何界限不以標註重疊文字當讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "66與36"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/CASES-08-reopened.png",
          "sha256": "777d0fc7809b78926dedec53e751f5e739f4e289aaaccbe8b04975c60babc5ab",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "較窄盒蓋的重開外觀；尺寸與鍵值不能從透視外觀精讀。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                63,
                101,
                22
              ],
              "label": "上蓋舊名Cube"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/demo-files/manual_box_lid_70x40_v001.blend",
          "label": "70×40 手動更新後重開試驗版本"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-cases-v001/manual-lid-multicase-verification-v001.json",
          "label": "盒蓋多組尺寸手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-clamp-01",
      "title": "超界 X 尺寸",
      "lead": "從80×50的獨立手工盒蓋試驗版出發。 超界 X 尺寸。",
      "actions": [
        "選 Body 並進外框草圖，將 X80改<code>110</code>，Y保持<code>50</code>。",
        "查看內腔草圖與本次 Driver／形狀鍵讀值。"
      ],
      "checks": [
        "外框欄為<code>110</code>、<code>50 mm</code>",
        "讀值表顯示<code>Key 1</code>被夾為<code>2</code>，而公式理論值應為<code>3</code>"
      ],
      "pitfalls": [],
      "locate": "從80×50的獨立手工盒蓋試驗版出發。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-03-outer-sketch.png",
          "sha256": "1de32f144a69380cc467c2048ce5dedd73946b89bae43304601cb47565844cc8",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "下一組試驗起點仍為Body Sketch80／50mm，Fully defined。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "基準80與50"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-04-outer-110x50.png",
          "sha256": "9327a61b2246755ae4aa87481f3e71b2a8f28cc9911726a5dc8c3aa8b1ed5d1e",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "外框X110、Y50，全約束；這是超界反例，非允許範圍通過。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                628,
                140,
                40
              ],
              "label": "超界110與50"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-05-inner-before-solve.png",
          "sha256": "c9c78905be29dc2e2245d9ed1f2df86edeeef8d28646d9e90e343fd41b94cf2d",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Body.001內腔欄106、46為紫色，中央圖仍有舊線；需按更新後再核對幾何。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                628,
                141,
                41
              ],
              "label": "內腔欄位"
            },
            {
              "n": 2,
              "box": [
                1170,
                114,
                20,
                37
              ],
              "label": "更新草圖"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/out-of-range-counterexample-v001.json",
          "label": "形狀鍵超界夾限反例摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-clamp-02",
      "title": "辨認上蓋失配",
      "lead": "辨認上蓋失配。",
      "actions": [
        "點內腔草圖更新圖示，另存反例並重開。",
        "比較摘要中盒口與唇邊的頂點界限。"
      ],
      "checks": [
        "重開外觀可見上蓋短於盒體",
        "讀值表中盒口X2～<code>108</code>、唇外X約<code>2.2005</code>～<code>97.7995 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "形狀鍵夾住後盒蓋失配",
          "text": "X110要求Value3，但上限<code>2</code>只伸長到約<code>100 mm</code>；這是反例，請保留正常版，不以擴大範圍代替重新檢查幾何。"
        }
      ],
      "locate": "110×50 反例場景，內腔草圖尚未手動更新。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-06-inner-after-solve.png",
          "sha256": "dc30e54509bf6fa5f359f62e6044ea71c5d963f800de3d418832d658e63a2ab1",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "超界X試驗更新後內腔106／46mm，外框X110的關係由本圖欄位及來源讀值佐證，沒有顯示上蓋鍵值。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "106與46"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-07-assembly.png",
          "sha256": "94592f6804cb675bdc1e7bd05ea0bed075038ffc2dabdb483714c7aa99d280c4",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "超界試驗蓋合外觀可見右側露出的盒口邊；此角度不能讀出10.2005mm界限差。",
          "marks": [
            {
              "n": 1,
              "box": [
                854,
                540,
                96,
                52
              ],
              "label": "失配外觀"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/LINK-09-reopened.png",
          "sha256": "6e571e9d8d71679b11dd930ba300d1d60d078a345c8bc081b182a4d0cfd6fe95",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "超界反例：蓋短於盒體，右端露出邊緣，不能當作盒蓋連動成功。",
          "marks": [
            {
              "n": 1,
              "box": [
                857,
                543,
                257,
                47
              ],
              "label": "超界失配"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/demo-files/manual_box_lid_110x50_v001.blend",
          "label": "110×50 超界反例（非完成品）"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-out-of-range-v001/out-of-range-counterexample-v001.json",
          "label": "形狀鍵超界夾限反例摘要"
        }
      ]
    }
  ]
};
