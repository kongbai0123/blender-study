window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-02"] = {
  "id": "08-02",
  "title": "為什麼需要連動：固定內腔的反例",
  "keyPoint": "放大外框，觀察固定內腔造成的不對稱。",
  "glossary": [
    {
      "term": "Body Sketch",
      "label": "Body Sketch",
      "text": "本示範外框草圖名稱。"
    },
    {
      "term": "界限差",
      "label": "界限差",
      "text": "同方向兩組邊界座標的差，用於比較幾何位置。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-link-counterexample-02",
      "title": "進入外框草圖",
      "lead": "Object Mode，選取 Body；這是固定版的獨立副本。 進入外框草圖。",
      "actions": [
        "右鍵 Body，選 Edit Sketch › Body Sketch。",
        "對照 Sketcher 側欄兩個 Distance：<code>60</code>／<code>40 mm</code>。"
      ],
      "checks": [
        "Sketcher 名稱為 Body Sketch",
        "兩個 Distance 為<code>60</code>、<code>40 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode，選取 Body；這是固定版的獨立副本。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-02-context-menu.png",
          "sha256": "530857d37c33c58c529edf05aad4be2785f9fe2344a040e13f447d249f28f433",
          "size": [
            1494,
            1019
          ],
          "caption": "右鍵Edit Sketch子選單分列Body Sketch與Body.001 Sketch，正是外框／內腔選擇位置。",
          "marks": [
            {
              "n": 1,
              "box": [
                762,
                435,
                191,
                21
              ],
              "label": "外框草圖"
            },
            {
              "n": 2,
              "box": [
                762,
                456,
                191,
                21
              ],
              "label": "內腔草圖"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-03-body-sketch.png",
          "sha256": "b76fcf743b4b819375965c72134738cfd88d4306964b6953b2fcca602a25d4dc",
          "size": [
            1494,
            1019
          ],
          "caption": "進Body Sketch，畫面左下可見60.000mm標註；側欄未展開。",
          "marks": [
            {
              "n": 1,
              "box": [
                282,
                762,
                90,
                28
              ],
              "label": "寬60mm"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-04-sidebar.png",
          "sha256": "b29d9ed27db7cdcd709efdafb64de009264b4e27a74322f6a0283775e5287432",
          "size": [
            1494,
            1019
          ],
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
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/outer-dimension-linkage-negative-v001.json",
          "label": "固定盒尺寸變更反例摘要"
        }
      ]
    },
    {
      "stepId": "ch08-link-counterexample-03",
      "title": "把 X 從 60 改成 70",
      "lead": "Body Sketch；右側第一個 Distance 為本次 X。 把 X 從 60 改成 70。",
      "actions": [
        "將第一個 Distance 設為<code>70 mm</code>，維持第二個<code>40 mm</code>。",
        "對照摘要中外框與切割體界限。"
      ],
      "checks": [
        "第一個 Distance 為<code>70 mm</code>，第二個<code>40 mm</code>",
        "來源讀值表中切割體X仍為<code>2</code>～<code>58</code>，右側差成<code>12 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body Sketch；右側第一個 Distance 為本次 X。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-05-x70.png",
          "sha256": "36435c057d0d05e3194139f53a4ec86fe282aaa6ec5beea98fb1458be8058669",
          "size": [
            1494,
            1019
          ],
          "caption": "Body Sketch側欄70／40mm；內部矩形未同幅增大，圖上尺寸文字重疊。",
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
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/outer-dimension-linkage-negative-v001.json",
          "label": "固定盒尺寸變更反例摘要"
        }
      ]
    },
    {
      "stepId": "ch08-link-counterexample-04",
      "title": "把 Y 從 40 改成 50",
      "lead": "Body Sketch；本次第二個 Distance 為 Y。 把 Y 從 40 改成 50。",
      "actions": [
        "將第二個 Distance 改為<code>50 mm</code>，第一個維持<code>70 mm</code>。",
        "比較摘要中的 X／Y 兩側界限差。"
      ],
      "checks": [
        "兩個 Distance 為<code>70</code>、<code>50 mm</code>",
        "讀值表中切割體仍為X2～<code>58</code>、Y2～<code>38</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body Sketch；本次第二個 Distance 為 Y。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-06-x70y50.png",
          "sha256": "816042142fb0f65b36e0d0e50b84f596feccd83028e61859aa77390bcf88d986",
          "size": [
            1494,
            1019
          ],
          "caption": "Body Sketch側欄70／50mm；內矩形保持原範圍，未同步的反例。",
          "marks": [
            {
              "n": 1,
              "box": [
                1020,
                630,
                153,
                39
              ],
              "label": "70與50"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/outer-dimension-linkage-negative-v001.json",
          "label": "固定盒尺寸變更反例摘要"
        }
      ]
    },
    {
      "stepId": "ch08-link-counterexample-05",
      "title": "另存並重開反例",
      "lead": "70×50 反例；以不同檔名另存，保留固定版。 另存並重開反例。",
      "actions": [
        "對照另存與重開畫面，再核對摘要。"
      ],
      "checks": [
        "重開後外框欄仍為<code>70</code>、<code>50 mm</code>",
        "保存前後的讀值表皆保留固定內腔與不對稱界限差"
      ],
      "pitfalls": [
        {
          "title": "重開工具警告仍需處理",
          "text": "既有重開畫面可見 sketcher.slvs_select 提示；本例用於觀察固定內腔，不宣稱已消除警告。"
        }
      ],
      "locate": "70×50 反例；以不同檔名另存，保留固定版。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-07-saved.png",
          "sha256": "37fab175f1c812591731349cc32dea8e9ef05c776618a530fe9815aa1094b45f",
          "size": [
            1494,
            1019
          ],
          "caption": "側欄70／50mm，底部Saved as outer_dimension_trial_70x50_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                574,
                995,
                326,
                23
              ],
              "label": "反例存檔"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-08-reopened.png",
          "sha256": "c4263e447033abda8ac15e6c5b0e785739eddbfbe66716598333c2e1f26399e3",
          "size": [
            1494,
            1019
          ],
          "caption": "重開後側欄70／50mm且Fully defined，仍能看到內部範圍沒有跟外框增大；精確差值須讀回。",
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
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/demo-files/outer_dimension_trial_70x50_v001.blend",
          "label": "70×50 未連動反例 v001"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/outer-dimension-linkage-negative-v001.json",
          "label": "固定盒尺寸變更反例摘要"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch08-link-counterexample-01",
    "title": "記錄固定尺寸版本",
    "actions": [
      "對照固定版另存和重開畫面，記錄版本。"
    ],
    "checks": [
      "固定版保存通知可找到本次檔名",
      "來源紀錄保留外框<code>60</code>×<code>40</code>×<code>30</code>與固定內腔界限"
    ],
    "pitfalls": [],
    "locate": "60×40×30 手工固定盒獨立副本；原圖另存於較早的保存試驗。",
    "figures": [
      {
        "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-saved-probe-v001/SAVE-01-saved.png",
        "sha256": "a201849891ba6ccd6740dbc0b8349897a96266f72571adf74bf6a36c860843ed",
        "size": [
          1494,
          1019
        ],
        "caption": "底部Saved as manual_fixed_box_60x40x30_v001.blend；凹盒外形可見。",
        "marks": [
          {
            "n": 1,
            "box": [
              575,
              995,
              324,
              23
            ],
            "label": "固定版存檔"
          }
        ],
        "tab": "操作位置"
      },
      {
        "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-saved-probe-v001/SAVE-02-reopened.png",
        "sha256": "29d494f64e6b5cd4d977be94580e9c65753f51a3367b6bf2c8bfe2c00cca1b5f",
        "size": [
          1494,
          1019
        ],
        "caption": "Object Mode固定盒副本，尚未進草圖或建立Driver。",
        "marks": [
          {
            "n": 1,
            "box": [
              615,
              350,
              276,
              239
            ],
            "label": "固定盒副本"
          }
        ],
        "tab": "過程狀態"
      },
      {
        "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-01-opened.png",
        "sha256": "29d494f64e6b5cd4d977be94580e9c65753f51a3367b6bf2c8bfe2c00cca1b5f",
        "size": [
          1494,
          1019
        ],
        "caption": "Object Mode固定盒副本，尚未進草圖或建立Driver。",
        "marks": [
          {
            "n": 1,
            "box": [
              615,
              350,
              276,
              239
            ],
            "label": "固定盒副本"
          }
        ],
        "tab": "核對結果"
      }
    ],
    "keys": [],
    "references": [
      {
        "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-saved-probe-v001/demo-files/manual_fixed_box_60x40x30_v001.blend",
        "label": "固定尺寸盒體副本 v001"
      },
      {
        "path": "evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/outer-dimension-linkage-negative-v001.json",
        "label": "固定盒尺寸變更反例摘要"
      }
    ],
    "kind": "prep",
    "summary": "60×40×30 手工固定盒獨立副本；原圖另存於較早的保存試驗。 記錄固定尺寸版本。",
    "lead": "60×40×30 手工固定盒獨立副本；原圖另存於較早的保存試驗。 記錄固定尺寸版本。"
  }
};
