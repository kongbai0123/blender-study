window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-06"] = {
  "id": "08-06",
  "title": "上蓋形狀鍵與 Driver",
  "keyPoint": "用 X、Y 形狀鍵連接外框尺寸，更新內腔。",
  "glossary": [
    {
      "term": "Basis",
      "label": "Basis",
      "text": "形狀鍵的基準網格狀態。"
    },
    {
      "term": "Key 1",
      "label": "Key 1",
      "text": "本節控制X方向伸長的形狀鍵。"
    },
    {
      "term": "Key 2",
      "label": "Key 2",
      "text": "本節控制Y方向伸長的形狀鍵。"
    },
    {
      "term": "Value",
      "label": "Value",
      "text": "形狀鍵的混合值，1對應本節增加10mm的變形。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-manual-lid-link-01",
      "title": "建立 X 形狀鍵",
      "lead": "上蓋 Cube、Object Data Properties 的 Shape Keys；固定80×50版本。 建立 X 形狀鍵。",
      "actions": [
        "新增 Basis 與 <code>Key 1</code>，選 <code>Key 1</code> 並進 Edit Mode。",
        "選取 X 正側頂點，沿 X 移動<code>10 mm</code>，返回 Object Mode 並另存。"
      ],
      "checks": [
        "Shape Keys 清單出現 Basis、<code>Key 1</code>",
        "<code>Key 1</code>選中時，X正側頂點沿X移動<code>10 mm</code>"
      ],
      "pitfalls": [],
      "locate": "上蓋 Cube、Object Data Properties 的 Shape Keys；固定80×50版本。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-x-v001/KEY-02-panel.png",
          "sha256": "8bc9e35abd61f451aec25f53289e9d5f98c402c02f2e53056772e73727bfadfa",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object Data Properties的Shape Keys清單空白，右側有+按鈕；尚未建立Basis。",
          "marks": [
            {
              "n": 1,
              "box": [
                1268,
                431,
                179,
                29
              ],
              "label": "形狀鍵面板"
            },
            {
              "n": 2,
              "box": [
                1455,
                461,
                23,
                24
              ],
              "label": "新增鍵"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-x-v001/KEY-06-select-right.png",
          "sha256": "b12929603eed857e23f9e03ddbac3b9344172068ba166bf5b63033c6b3d52bb3",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Edit Mode點選取、X-Ray開，Key1作用中且Value1，右側X正側頂點橘色。",
          "marks": [
            {
              "n": 1,
              "box": [
                880,
                469,
                29,
                191
              ],
              "label": "X正側頂點"
            },
            {
              "n": 2,
              "box": [
                1275,
                488,
                168,
                27
              ],
              "label": "Key1"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-x-v001/KEY-08-x-object.png",
          "sha256": "82dc5588987c99c66512dfc0df159b5f57ac7cb05cfd6fe77dfbc867cd8aabba",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "回Object Mode，Key1 Value1.000，可見X形狀相對基準延長；當時Range為0到1，後續才擴範圍。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                628,
                107,
                25
              ],
              "label": "X鍵值1"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-x-v001/demo-files/manual_lid_shape_x_v001.blend",
          "label": "上蓋 X 形狀鍵示範"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-link-02",
      "title": "建立 Y 形狀鍵",
      "lead": "先將 Key 1 設回0，新增相對 Basis 的 Key 2。 建立 Y 形狀鍵。",
      "actions": [
        "選 <code>Key 2</code>，進 Edit Mode 選 Y 正側頂點，沿 Y 移動<code>10 mm</code>。",
        "返回 Object Mode，將兩個鍵歸零、設定本次鍵範圍 <code>-2</code>～<code>2</code>，另存。"
      ],
      "checks": [
        "清單新增 <code>Key 2</code>，Y正側頂點完成移動",
        "Object Mode 的<code>Key 1</code>、<code>Key 2</code>歸零，範圍<code>-2</code>至<code>2</code>"
      ],
      "pitfalls": [
        {
          "title": "底視中的Y正側在下方",
          "text": "本次 Bottom Orthographic 的Y軸朝畫面下方；依座標軸與頂點選取判斷，別只照畫面上方框選。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "先將 Key 1 設回0，新增相對 Basis 的 Key 2。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-y-v001/KEY-02-x-zero.png",
          "sha256": "edbaee44dc040b15332f9c4c316e9f7c433d61639b0adeae5a06d88aa2d57f6f",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Key1選取且Value0.000，Range Min -2.000、Max2.000，XRay開啟可見內外輪廓。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                627,
                106,
                68
              ],
              "label": "鍵值與範圍"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-y-v001/KEY-05-select-y.png",
          "sha256": "26491df410b97d29b651417e0dbdb658445f70f82d52ac12772f7eaba20b5dfe",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Edit Mode點選取、Key2作用中；底視下方是Y正側，對應一排頂點橘色選取。",
          "marks": [
            {
              "n": 1,
              "box": [
                612,
                636,
                293,
                25
              ],
              "label": "Y正側頂點"
            },
            {
              "n": 2,
              "box": [
                1275,
                508,
                168,
                27
              ],
              "label": "Key2"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-y-v001/KEY-07-both-zero.png",
          "sha256": "175ffd8d6199913653f2bd2e58b4f954ae6a7a20c540bc6b8699efe669fcfe8e",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Key 1、Key 2 均為0；選中的Key 2範圍−2至2。",
          "marks": [
            {
              "n": 1,
              "box": [
                1280,
                487,
                164,
                46
              ],
              "label": "鍵值歸零"
            },
            {
              "n": 2,
              "box": [
                1280,
                650,
                176,
                46
              ],
              "label": "範圍正負2"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-shapekey-y-v001/demo-files/manual_lid_shape_xy_v001.blend",
          "label": "上蓋 X／Y 形狀鍵示範"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-link-03",
      "title": "連接 X Driver",
      "lead": "外框 Body Sketch 第一個 Distance 為本次 X80。 連接 X Driver。",
      "actions": [
        "從外框 X 欄位 Copy as New Driver，貼到上蓋 <code>Key 1</code> Value。",
        "在 Edit Driver 選 Scripted Expression，依本次來源變數設為 X／<code>10</code>−<code>8</code>。"
      ],
      "checks": [
        "<code>Key 1</code>剛貼上時紫色Value為<code>2</code>",
        "改為來源X/<code>10</code>−<code>8</code>後，本次<code>80 mm</code>來源得到Value0"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "外框 Body Sketch 第一個 Distance 為本次 X80。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-x-v006/LINK-05-source-menu.png",
          "sha256": "3a32395edd9086cc4513eebd0edfd47cbbbf7f482838a8863d57de5d8c9868a6",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "外框80／50標註；第一尺寸右鍵選單末端Copy as New Driver，對應X來源。",
          "marks": [
            {
              "n": 1,
              "box": [
                944,
                853,
                220,
                25
              ],
              "label": "複製X來源"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-x-v006/LINK-09-x-pasted.png",
          "sha256": "009e7e4b8cd7e0591c37c6e403cb990c24253da32a20c871cadb0c1385ad23cc",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Key 1紫色Value為2，蓋子沿X超出盒體；這是貼上Driver後尚未修公式的過程。",
          "marks": [
            {
              "n": 1,
              "box": [
                1280,
                628,
                176,
                24
              ],
              "label": "暫為2"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-x-v006/LINK-14-x-formula.png",
          "sha256": "6d3a6020cfb117c534623227991fcab58409eb142a849b5e89a218c3ceb7e1dd",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Key 1 Driver為Scripted Expression，公式尾端/10-8，來源80，輸出0。",
          "marks": [
            {
              "n": 1,
              "box": [
                1126,
                601,
                207,
                30
              ],
              "label": "運算式類型"
            },
            {
              "n": 2,
              "box": [
                1125,
                693,
                206,
                29
              ],
              "label": "X公式"
            },
            {
              "n": 3,
              "box": [
                1238,
                927,
                87,
                25
              ],
              "label": "來源80"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-x-v006/demo-files/manual_lid_shape_x_driver_v001.blend",
          "label": "上蓋 X Driver 示範"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-link-04",
      "title": "連接 Y Driver",
      "lead": "外框 Body Sketch 第二個 Distance 為本次 Y50。 連接 Y Driver。",
      "actions": [
        "從外框 Y 欄位 Copy as New Driver，貼到上蓋 <code>Key 2</code> Value。",
        "在 Edit Driver 選 Scripted Expression，依本次來源變數設為 Y／<code>10</code>−<code>5</code>，確認後另存。"
      ],
      "checks": [
        "<code>Key 2</code>剛貼上時紫色Value為<code>2</code>",
        "改為來源Y/<code>10</code>−<code>5</code>後，本次<code>50 mm</code>來源得到Value0"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "外框 Body Sketch 第二個 Distance 為本次 Y50。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-y-v001/LINK-05-source-menu.png",
          "sha256": "5b1e9daf2179ee32d9a10d8fc81ab35e9d3270ef0252894635b47d57eb765f11",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "外框80／50標註，Y來源欄位右鍵選單末端Copy as New Driver。",
          "marks": [
            {
              "n": 1,
              "box": [
                944,
                873,
                220,
                26
              ],
              "label": "複製Y來源"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-y-v001/LINK-09-x-pasted.png",
          "sha256": "f3f7da1e6e896c689f05d7056f301f1b292e067b59446c1ddd705f19065400a4",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Key 2為紫色2，未改公式；Key 1為0。",
          "marks": [
            {
              "n": 1,
              "box": [
                1280,
                510,
                163,
                24
              ],
              "label": "Key 2暫為2"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-y-v001/LINK-14-x-formula.png",
          "sha256": "1d15ad1f6c34bbf91979a8723cb5292e2035c04db6119258050e8dd62eb645b3",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Key 2公式尾端/10-5，來源50，輸出0。",
          "marks": [
            {
              "n": 1,
              "box": [
                1125,
                694,
                206,
                27
              ],
              "label": "Y公式"
            },
            {
              "n": 2,
              "box": [
                1238,
                927,
                87,
                25
              ],
              "label": "來源50"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-driver-y-v001/demo-files/manual_lid_shape_xy_driver_v001.blend",
          "label": "上蓋 X／Y Driver 示範"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-link-05",
      "title": "外框改為 90 × 60",
      "lead": "開啟 X／Y Driver 試驗場景；選 Body 並進外框草圖。 外框改為 90 × 60。",
      "actions": [
        "將 Body Sketch 外框改為<code>90</code>×<code>60 mm</code>。",
        "進 Body.001 Sketch，先對照更新前的欄位及摘要。"
      ],
      "checks": [
        "外框 Distance 為<code>90</code>、<code>60 mm</code>",
        "內腔欄為紫色<code>86</code>、<code>56 mm</code>，但更新前輪廓仍舊"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "開啟 X／Y Driver 試驗場景；選 Body 並進外框草圖。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-03-outer-sketch.png",
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
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-04-outer-90x60.png",
          "sha256": "5034b694bc7c0117c2b29ef7073e8a635cf5dca1e53eb54289a3b9423cf09db3",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Body Sketch已全約束，側欄Distance為90mm與60mm；這張是外框狀態，不是內腔更新結果。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                629,
                143,
                40
              ],
              "label": "外框90與60"
            },
            {
              "n": 2,
              "box": [
                1000,
                151,
                174,
                27
              ],
              "label": "全約束"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-05-inner-before-solve.png",
          "sha256": "5743c50d58047b013b5158e298c3f974796f53fd40ffec21d52ac179ccdba702",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "內腔Distance已顯示86、56紫色Driver欄；中央尺寸重疊，幾何尚須更新，不能由全約束判同步。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                628,
                140,
                40
              ],
              "label": "內腔欄86與56"
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
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-link-06",
      "title": "更新內腔並保存重開",
      "lead": "更新內腔並保存重開。",
      "actions": [
        "點內腔草圖頂端更新圖示。",
        "另存並重開，對照摘要的盒體、唇邊頂點與 Driver。"
      ],
      "checks": [
        "手動更新後內腔輪廓改變",
        "重開讀值中盒口X2～<code>88</code>、Y2～<code>58</code>，唇外頂點界限約各留<code>0.2 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Body.001 Sketch，尚未更新的90×60場景。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-06-inner-after-solve.png",
          "sha256": "279c20a8b4a9d6af8543ca298d4a5ee9ab90057784a08d70395fc0b8907814de",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "更新後Body.001 Sketch紫色86／56mm，中央矩形隨之擴大；幾何界限仍應讀回。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                39
              ],
              "label": "86與56"
            },
            {
              "n": 2,
              "box": [
                1170,
                113,
                20,
                37
              ],
              "label": "更新按鈕"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-07-assembly.png",
          "sha256": "bfd27b4b85ef85f23e1cce57bbb536c1ac32e24ad0fd11405f8a87712a2314ea",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "盒蓋蓋合外觀，蓋面橘框、上蓋未分離，無法從角度量到唇邊各側間隙。",
          "marks": [
            {
              "n": 1,
              "box": [
                615,
                336,
                337,
                206
              ],
              "label": "盒蓋外觀"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/LINK-09-reopened.png",
          "sha256": "eae32281d0d86e3cb78f2c7e5bbf496cb4c1907f1ad4ea5e8f25e0f7654356ff",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "盒蓋合攏的重開外觀；內腔與Driver未展開，須另查讀值。",
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
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/demo-files/manual_box_lid_90x60_v001.blend",
          "label": "90×60 手動更新後保存重開示範"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-lid-xy-link-verify-v001/manual-lid-xy-link-one-case-v001.json",
          "label": "手工盒蓋雙軸連動單組驗證摘要"
        }
      ]
    }
  ]
};
