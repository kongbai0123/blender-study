window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-03"] = {
  "id": "08-03",
  "title": "內腔 X 方向的 Driver",
  "keyPoint": "連接 X Driver，手動更新後核對內腔。",
  "glossary": [
    {
      "term": "Copy as New Driver",
      "label": "Copy as New Driver",
      "text": "複製目前屬性作為驅動來源的選單項目。"
    },
    {
      "term": "Paste Driver",
      "label": "Paste Driver",
      "text": "把已複製的驅動連結貼到目標欄位。"
    },
    {
      "term": "Scripted Expression",
      "label": "Scripted Expression",
      "text": "以運算式決定目標值的Driver類型。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-driver-partial-01",
      "title": "複製外框 X 作來源",
      "lead": "固定盒獨立副本；Object Mode、選取 Body。 複製外框 X 作來源。",
      "actions": [
        "右鍵 Body，選 Edit Sketch › Body Sketch，觀察側欄第一個 Distance。",
        "右鍵 X60 mm 欄位，選 Copy as New Driver。"
      ],
      "checks": [
        "Body Sketch 的第一個 Distance 為<code>60 mm</code>",
        "該欄右鍵選單出現 Copy as New Driver"
      ],
      "pitfalls": [],
      "locate": "固定盒獨立副本；Object Mode、選取 Body。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/EDIT-04-sidebar.png",
          "sha256": "b29d9ed27db7cdcd709efdafb64de009264b4e27a74322f6a0283775e5287432",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Body Sketch側欄Fully defined，Distance60／40mm；固定版外框起點。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "外框尺寸"
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
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-01-source-context.png",
          "sha256": "f082cfdebf178a42a45066de4d35b2a6195ae74f796dda9087120d628779ff02",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "外框60／40的X欄右鍵選單含Copy as New Driver，是來源欄位選單。",
          "marks": [
            {
              "n": 1,
              "box": [
                944,
                853,
                220,
                26
              ],
              "label": "複製X來源"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-02-copy-source.png",
          "sha256": "a378f364bf6fd994dd209d65f3d5a0140d29195a48bbe34855aa0fd93543c3a2",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "選單已關閉，外框側欄60／40；畫面本身不顯示剪貼簿內容或已複製狀態。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "來源尺寸"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/native-driver-xy-partial-verification-v001.json",
          "label": "原生 Driver 部分成功與失敗試驗摘要"
        }
      ]
    },
    {
      "stepId": "ch08-driver-partial-02",
      "title": "進入內腔草圖",
      "lead": "離開外框草圖；選取本次 Body。 進入內腔草圖。",
      "actions": [
        "右鍵 Body，選 Edit Sketch › Body.001 Sketch。",
        "查看本次內部草圖側欄中的<code>56</code>／<code>36</code>／<code>28</code>／<code>18 mm</code>。"
      ],
      "checks": [
        "草圖名稱切到 Body.001 Sketch",
        "側欄列出<code>56</code>、<code>36</code>、<code>28</code>、<code>18 mm</code>"
      ],
      "pitfalls": [],
      "locate": "離開外框草圖；選取本次 Body。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-03-select-cutter-menu.png",
          "sha256": "ca496fdbb11bd961ab7dac0a07e57249305706d443e7b7e1808a68a5890942ef",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit Sketch子選單可選Body.001 Sketch，右側Sketcher列Body與Body.001節點。",
          "marks": [
            {
              "n": 1,
              "box": [
                756,
                455,
                226,
                25
              ],
              "label": "內腔草圖"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-04-cutter-sketch.png",
          "sha256": "edf810da62bd64c22e5f667703260a326b6717af1515734e90d85166faf55435",
          "size": [
            1494,
            1019
          ],
          "caption": "內腔Fully defined；側欄Distance依序56、36、28、18mm；中央文字仍重疊。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                154,
                74
              ],
              "label": "內腔四尺寸"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/native-driver-xy-partial-verification-v001.json",
          "label": "原生 Driver 部分成功與失敗試驗摘要"
        }
      ]
    },
    {
      "stepId": "ch08-driver-partial-03",
      "title": "貼上 Driver",
      "lead": "Body.001 Sketch，右側第一個 Distance 本次原值56 mm。 貼上 Driver。",
      "actions": [
        "右鍵內部 X 尺寸，選 Paste Driver。",
        "對照欄位顏色和此時的數值。"
      ],
      "checks": [
        "目標 X 欄轉為紫色",
        "剛貼上時顯示<code>60 mm</code>，尚未減<code>4</code>"
      ],
      "pitfalls": [],
      "locate": "Body.001 Sketch，右側第一個 Distance 本次原值56 mm。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-05-target-context.png",
          "sha256": "2b48235f1a861167d7275afe5a554c168f5460dd76610af9e4a69e324dbb2728",
          "size": [
            1494,
            1019
          ],
          "caption": "內腔第一尺寸右鍵選單含Paste Driver，此圖尚未貼上。",
          "marks": [
            {
              "n": 1,
              "box": [
                947,
                678,
                199,
                25
              ],
              "label": "貼上Driver"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-06-pasted.png",
          "sha256": "03f34c46ec1b314ef33928845d3c29cadf9409f88a8cbe520fbf4202e6ef59ee",
          "size": [
            1494,
            1019
          ],
          "caption": "貼上後第一個Distance紫色60mm；其餘36、28、18不變。不是最終減4公式。",
          "marks": [
            {
              "n": 1,
              "box": [
                1094,
                630,
                65,
                24
              ],
              "label": "暫為60mm"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/native-driver-xy-partial-verification-v001.json",
          "label": "原生 Driver 部分成功與失敗試驗摘要"
        }
      ]
    },
    {
      "stepId": "ch08-driver-partial-04",
      "title": "把公式改成減 4",
      "lead": "在已貼上的內部 X 欄位操作；此例生成的變數名稱須依實際 Driver。 把公式改成減 4。",
      "actions": [
        "右鍵目標欄位選 Edit Driver，在 Type 選 Scripted Expression。",
        "依此例變數名稱加上 <code>-4</code>；核對輸入後的值。"
      ],
      "checks": [
        "Edit Driver 顯示 Scripted Expression與來源變數減<code>4</code>",
        "目標欄回到<code>56 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "在已貼上的內部 X 欄位操作；此例生成的變數名稱須依實際 Driver。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-07-edit-context.png",
          "sha256": "adc558a8dd59d7893beaa07bba4cb71ebcbfa3f062847dc8d1c0a949f98aec0c",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "已存在Driver的目標右鍵選單，Edit Driver可見，非新增普通關鍵影格。",
          "marks": [
            {
              "n": 1,
              "box": [
                944,
                669,
                205,
                26
              ],
              "label": "編輯Driver"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-09-type-menu.png",
          "sha256": "06edef2c2523d54244a0c196ecae006d95f55e51e91211e3303e0a52c33196a3",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Type下拉原值Averaged Value，清單含Scripted Expression；值仍60。",
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
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/DRIVER-11-formula-attempt.png",
          "sha256": "058bd4f5676582a6d27b3bea21495f90d2c001875e937cea8b94e2cbc7144bb1",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Scripted Expression來源變數減4，Driver Value56.000、來源Value60、目標紫色56mm。",
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
              "label": "結果56"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-native-driver-xy-trial-v001/native-driver-xy-partial-verification-v001.json",
          "label": "原生 Driver 部分成功與失敗試驗摘要"
        }
      ]
    },
    {
      "stepId": "ch08-x-refresh-01",
      "title": "點選盒體進外框草圖",
      "lead": "Object Mode；畫面可見盒體的側面。 點選盒體進外框草圖。",
      "actions": [
        "點盒體可見側面，確認活動物件為 Body。",
        "右鍵選 Edit Sketch，再選 Body Sketch。"
      ],
      "checks": [
        "點盒體側面後活動物件為 Body",
        "進入的名稱為 Body Sketch"
      ],
      "pitfalls": [],
      "locate": "Object Mode；畫面可見盒體的側面。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-02-select-body.png",
          "sha256": "8583533e1641cff63e8cbf9427838a36e64da846d2b0112a28e77968334ff6f5",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "點側面後左上活動物件Body，Outliner Body反白；可避開原先選到Body.001。",
          "marks": [
            {
              "n": 1,
              "box": [
                66,
                99,
                116,
                23
              ],
              "label": "活動Body"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-03-context-menu.png",
          "sha256": "6a14c45322b78d5879e4c3c91701e2f8450a68edc1ddd7755eb43cf22273a85a",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Body右鍵Edit Sketch子選單含外框Body Sketch及內腔Body.001 Sketch。",
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
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-04-body-sketch.png",
          "sha256": "742e50637ad833b68cf32ea8bd561c58f8f8910bd91e2db84a1ce9fce2a171af",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Body Sketch側欄60／40mm及Fully defined，尚未把X改70。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "外框起點"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json",
          "label": "X 尺寸與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-x-refresh-02",
      "title": "把 X 改為 70 並另存",
      "lead": "Body Sketch；第一個 Distance 是本次 X 尺寸。 把 X 改為 70 並另存。",
      "actions": [
        "將第一個 Distance 由<code>60</code>改為<code>70 mm</code>。",
        "另存本次獨立示範版本，再重新開啟。"
      ],
      "checks": [
        "外框X欄為<code>70 mm</code>",
        "另存重開後來源讀值中切割體仍為X2～<code>58</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body Sketch；第一個 Distance 是本次 X 尺寸。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-06-x70.png",
          "sha256": "e20641700abf6cda62ef8c60b058a75c22dbda35fb8833f60135646034250761",
          "size": [
            1494,
            1019
          ],
          "caption": "外框第一Distance70mm、第二40mm，Fully defined；內腔尚未更新。",
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
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-07-saved.png",
          "sha256": "e5d30bbc6ac1b601891e859497091964fbeb7705e60069e25d39508436102750",
          "size": [
            1494,
            1019
          ],
          "caption": "底部Saved as x_driver_resize_probe_v001.blend，外框70／40mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                595,
                995,
                289,
                23
              ],
              "label": "X試驗存檔"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/EDIT-08-reopened.png",
          "sha256": "5ae61f6b86d3a7c09257e96be01a326610f449e08804099e77922dc45ab7e09e",
          "size": [
            1494,
            1019
          ],
          "caption": "重開外框70／40mm、Fully defined；圖片沒有幾何界限讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "重開尺寸"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-select-body-v002/demo-files/x_driver_resize_probe_v001.blend",
          "label": "X70、尚未手動更新的試驗場景（非完成品）"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json",
          "label": "X 尺寸與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-x-refresh-03",
      "title": "進內腔草圖看欄位",
      "lead": "重開 X70 試驗場景並確認 Body。 進內腔草圖看欄位。",
      "actions": [
        "離開外框草圖，右鍵選 Edit Sketch 中的 Body.001 Sketch。",
        "核對紫色 Driver 尺寸欄位及摘要中的切割體界限。"
      ],
      "checks": [
        "內腔X欄為紫色<code>66 mm</code>",
        "更新前讀值中切割體仍是X2～<code>58</code>"
      ],
      "pitfalls": [],
      "locate": "重開 X70 試驗場景並確認 Body。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/UPDATE-01-opened.png",
          "sha256": "3cc2abe67e23b72cfa721255e255832eeb4e4ba7f11c4884e396670507fec1f9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "重開X70外框；底部黃色工具未找到訊息，必須保留警告提醒。",
          "marks": [
            {
              "n": 1,
              "box": [
                560,
                996,
                366,
                22
              ],
              "label": "工具警告"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/UPDATE-03-context-menu.png",
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
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/UPDATE-04-enter-inner.png",
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
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json",
          "label": "X 尺寸與手動更新驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch08-x-refresh-04",
      "title": "手動更新內腔",
      "lead": "Body.001 Sketch；欄位顯示66 mm。 手動更新內腔。",
      "actions": [
        "點 Sketcher 面板頂端 Leave 按鈕右邊的更新圖示。",
        "離開內腔草圖，對照程式讀回的切割體界限。"
      ],
      "checks": [
        "按 Leave 右邊更新圖示後內腔輪廓改變",
        "更新後讀值列出X2～<code>68</code>、兩側界限差<code>2 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "欄位跟隨但幾何未更新",
          "text": "本例需要進入內腔草圖，按Leave右邊更新圖示。這次X70更新後未另存，後續請保存自己的新版本再重開。"
        }
      ],
      "locate": "Body.001 Sketch；欄位顯示66 mm。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/UPDATE-05-solve-inner.png",
          "sha256": "dce2606e3a779a39eb62482ecaad596bfc007da29edf2d91e8295e22da0b30e2",
          "size": [
            1494,
            1019
          ],
          "caption": "更新後內腔第一Driver紫色66mm、第二36mm；Fully defined。Leave右側圓箭頭是更新位置。",
          "marks": [
            {
              "n": 1,
              "box": [
                1170,
                113,
                20,
                37
              ],
              "label": "更新草圖"
            },
            {
              "n": 2,
              "box": [
                1094,
                630,
                65,
                24
              ],
              "label": "內寬66mm"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/UPDATE-06-leave-inner.png",
          "sha256": "c52d5f3922b563ba0cfa8e10eceda0a947bcdda22b91d86ecb57f26d6369ef83",
          "size": [
            1494,
            1019
          ],
          "caption": "離開內腔後可見凹盒外形，Body.001為活動物件；沒有顯示界限數字。",
          "marks": [
            {
              "n": 1,
              "box": [
                67,
                100,
                149,
                23
              ],
              "label": "內腔活動物件"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-x-driver-solve-v001/x-driver-manual-solve-verification-v001.json",
          "label": "X 尺寸與手動更新驗證摘要"
        }
      ]
    }
  ]
};
