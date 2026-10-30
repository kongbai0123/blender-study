window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-01"] = {
  "id": "11-01",
  "title": "螺紋規格與參數",
  "keyPoint": "保留原盒參照，建立螺紋參數空表。",
  "glossary": [
    {
      "term": "螺距",
      "label": "螺距",
      "text": "相鄰牙在軸向的距離。"
    },
    {
      "term": "導程",
      "label": "導程",
      "text": "旋轉一圈沿軸向前進的距離。"
    },
    {
      "term": "線數",
      "label": "線數",
      "text": "平行螺旋起始線的數量。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-08-01-02",
      "title": "讀取盒體位置",
      "lead": "Edit Mode · Face Select 讀取盒體位置。",
      "actions": [
        "依實際視角逐次選盒口前環面、內底及外底，讀回所選面的世界座標，再檢查Select Non Manifold。"
      ],
      "checks": [
        "面讀值表分列前壁Y−<code>20</code>～<code>-18</code>、盒口Z15",
        "另列內底Z−<code>13</code>、外底Z−<code>15 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "Edit Mode · Face Select",
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
          "path": "journal/2026-10-25-lesson08-parameters-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch11-08-01-03",
      "title": "另存並記錄參數欄",
      "lead": "另存並記錄參數欄。",
      "actions": [
        "另存u08_thread_reference_v001.blend並Open重驗；把螺距、導程、線數、各徑、牙型、端部與間隙定義分欄記錄。"
      ],
      "checks": [
        "保存通知或重開檔名為<code>u08_thread_reference_v001.blend</code>",
        "參數表分列螺距、導程、線數、各徑、端部與間隙，未定值留空"
      ],
      "pitfalls": [],
      "locate": "File › Save As / Open · 參數表",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-01-file-menu.png",
          "sha256": "34fb7b908b2195873b9568a38b8aa54bdef0fd7ce29eb0e74570486259fd6768",
          "size": [
            1494,
            1019
          ],
          "caption": "File選單中可見Save As與Shift Ctrl S鍵標。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                153,
                176,
                22
              ],
              "label": "另存入口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson08-parameters-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch11-08-01-01",
    "title": "準備原盒參照",
    "actions": [
      "只用原小盒作參照，隱藏Camera／Light，命名Body_Reference並核對Item尺寸、Scale與毫米單位。"
    ],
    "checks": [
      "所選物件為 Body_Reference",
      "Dimensions60×<code>40</code>×<code>30 mm</code>、Scale1且毫米單位"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "<kbd>F2</kbd> 不改模型尺寸；新證據改名目標為 ShortcutCube，本步仍須輸入 Body_Reference。不代表已有螺紋。"
      }
    ],
    "locate": "原04盒同hash副本 · Object Mode",
    "figures": [
      {
        "path": "evidence/08/2026-10-25-lesson08-parameters-demo-v001/08-01-08-reference-overview.png",
        "sha256": "76bd22f0091976802281b444aa8703b9cd939a107c4a70d4074a0d137816a576",
        "size": [
          1494,
          1019
        ],
        "caption": "螺紋參考場景只有原盒，Body_Reference Item60／40／30mm，Scale1；沒有螺紋或柱。",
        "marks": [
          {
            "n": 1,
            "box": [
              962,
              398,
              229,
              64
            ],
            "label": "原盒參照"
          }
        ],
        "tab": "操作位置"
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "原04盒同hash副本 · Object Mode 準備原盒參照。",
    "lead": "原04盒同一來源副本 · Object Mode 準備原盒參照。",
    "references": [
      {
        "path": "journal/2026-10-25-lesson08-parameters-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
