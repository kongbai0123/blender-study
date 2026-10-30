window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["06-05"] = {
  "id": "06-05",
  "title": "匯出上蓋並核對",
  "keyPoint": "只匯出上蓋，重匯入核對外框與環唇。",
  "glossary": [
    {
      "term": "Forward Axis",
      "label": "Forward Axis",
      "text": "匯出時的前向座標軸選項。"
    },
    {
      "term": "Up Axis",
      "label": "Up Axis",
      "text": "匯出時的向上座標軸選項。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch06-05-06-02",
      "title": "匯出 Lid STL",
      "lead": "File › Export › STL (.stl) 匯出 Lid STL。",
      "actions": [
        "File › Export › STL (.stl)。",
        "右側選項：勾 Selection Only、Scale <code>1</code>、Scene Unit 不勾、Apply Modifiers 勾、ASCII 不勾、Forward Axis Y、Up Axis Z。存成 <code>learning/workspaces/05/exports/u05_lid_v001.stl</code>。"
      ],
      "checks": [
        "匯出選項與<code>06</code>-<code>02</code>一致，Selection Only開",
        "自己的exports目錄有 <code>u05_lid_v001.stl</code>"
      ],
      "pitfalls": [],
      "locate": "File › Export › STL (.stl)",
      "figures": [
        {
          "path": "evidence/05/2026-10-25-lesson05-lid-export-demo-v001/05-06-03-export-menu.png",
          "sha256": "bbdd40b730bd3881bdcf1cc615bfddfb501b4b65c1e0b8d9e80ed36189218b01",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "File › Export 子選單展開，STL (.stl) 突出。",
          "marks": [
            {
              "n": 1,
              "box": [
                28,
                307,
                202,
                20
              ],
              "label": "Export"
            },
            {
              "n": 2,
              "box": [
                236,
                426,
                244,
                20
              ],
              "label": "STL (.st"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-25-lesson05-lid-export-demo-v001/05-06-05-export-options.png",
          "sha256": "2ba670fbc9592b460fb36d1ca2b9f66d41ff4468bfed130802b076b93ba63c8e",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Selection Only 已勾、Scale 1、Scene Unit 未勾。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                148,
                135,
                22
              ],
              "label": "Selectio"
            },
            {
              "n": 2,
              "box": [
                920,
                170,
                135,
                43
              ],
              "label": "Scale 1 "
            },
            {
              "n": 3,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Export S"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-25-lesson05-lid-export-demo-v001/05-06-06-stl-checked.png",
          "sha256": "6a1fc291fed85dc0c59e4efd82367235e20cd38f534d11d1359ff2f40cb64596",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Lid底部環唇可見，Dimensions60×40×6 mm，底部顯示匯出成功。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "上蓋外框"
            },
            {
              "n": 2,
              "box": [
                643,
                996,
                186,
                21
              ],
              "label": "匯出成功"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson05-lid-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-05-06-03",
      "title": "重新匯入核對",
      "lead": "新的獨立毫米場景 · Import STL / Item 重新匯入核對。",
      "actions": [
        "File › New › General 開新檔；在 Properties 的 Scene 分頁 › Units 把 Length 改為 Millimeters、Unit Scale 輸入 <code>0.001</code>。 File › Import › STL (.stl) 匯入 <code>u05_lid_v001.stl</code>。",
        "核對 <code>60</code> × <code>40</code> × <code>6 mm</code>，並做一次 Non Manifold 檢查。"
      ],
      "checks": [
        "重匯入外框<code>60</code>×<code>40</code>×<code>6 mm</code>，底視可辨環唇",
        "記錄自己的 Non Manifold 檢查反白結果"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "新的獨立毫米場景 · Import STL / Item",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-07-05-edit-undo-menu.png",
          "sha256": "a322cbd6bb3ce61bc9a0151c0d21ca198704301322fd4faf31897e0f9b2f48ae",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit選單的Undo旁顯示Ctrl Z；這是基礎場景的撤回入口參照。",
          "marks": [
            {
              "n": 1,
              "box": [
                67,
                26,
                195,
                22
              ],
              "label": "撤回入口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson05-lid-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch06-05-06-01",
    "title": "開啟上蓋並選 Lid",
    "actions": [
      "開啟你的 <code>u05_lid_v001.blend</code>，選 Body 按 <kbd>H</kbd> 隱藏，只選 Lid。",
      "在 N 側欄核對 Lid <code>60</code> × <code>40</code> × <code>6 mm</code>、Scale <code>1</code>，底部斜視看環形唇邊。"
    ],
    "checks": [
      "Body 隱藏且只選 Lid",
      "Item 的 Dimensions 為<code>60</code>×<code>40</code>×<code>6 mm</code>、Scale1"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
      }
    ],
    "locate": "05-05 來源副本 · Object Mode / Lid",
    "figures": [
      {
        "path": "evidence/05/2026-10-25-lesson05-lid-export-demo-v001/05-06-10-reimport-underside.png",
        "sha256": "c31773df47bd9714268cf1a9715c419d09c163e8f1a903091bb8251f953e48d8",
        "size": [
          1494,
          1019
        ],
        "caption": "匯入蓋底視，定位環及凹區可見，Dimensions 60×40×6 mm、Location Z 0。",
        "marks": [
          {
            "n": 1,
            "box": [
              963,
              383,
              228,
              77
            ],
            "label": "整高 6 = 板"
          }
        ],
        "tab": "操作位置"
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "05-05 來源副本 · Object Mode / Lid 開啟上蓋並選 Lid。",
    "lead": "05-05 來源副本 · Object Mode / Lid 開啟上蓋並選 Lid。",
    "references": [
      {
        "path": "journal/2026-10-25-lesson05-lid-export-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
