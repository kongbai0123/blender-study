window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["10-04"] = {
  "id": "10-04",
  "title": "卡扣 STL 匯出與核對",
  "keyPoint": "保留候選旋轉匯出卡扣盒蓋，核對世界外框。",
  "glossary": [
    {
      "term": "Binary",
      "label": "Binary",
      "text": "本次STL採用的二進位格式。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch10-07-04-02",
      "title": "設定選項並匯出",
      "lead": "File › Export › STL (.stl) 設定選項並匯出。",
      "actions": [
        "確認Selection Only、Scale1、Scene Unit關、Binary、Y Forward／Z Up；各匯出新的v001檔。"
      ],
      "checks": [
        "選項為Selection Only開、Scale1、Scene Unit關",
        "exports產生盒與蓋兩個STL"
      ],
      "pitfalls": [],
      "locate": "File › Export › STL (.stl)",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-export-demo-v001/07-04-06-body-export-options.png",
          "sha256": "0dcb53baedfe2fb310a691c836bb7a9eda4ac9009613fb00106db98319d36a56",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Body STL匯出視窗：Selection Only勾、Scale1、Scene Unit關、ASCII關；檔名u07_snap_body_v001.stl。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                147,
                131,
                23
              ],
              "label": "僅匯出選取"
            },
            {
              "n": 2,
              "box": [
                921,
                171,
                130,
                42
              ],
              "label": "比例與單位"
            },
            {
              "n": 3,
              "box": [
                247,
                566,
                534,
                27
              ],
              "label": "Body檔名"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-export-demo-v001/07-04-13-lid-export-options.png",
          "sha256": "529a3a39621373e6c3936ca84b0dd57df94c4979dc63b91c24f7805bcc4a3b6c",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Lid STL匯出視窗同組選項；檔名u07_snap_lid_v001.stl，並已有body檔列出。",
          "marks": [
            {
              "n": 1,
              "box": [
                920,
                147,
                131,
                23
              ],
              "label": "僅匯出選取"
            },
            {
              "n": 2,
              "box": [
                921,
                171,
                130,
                42
              ],
              "label": "比例與單位"
            },
            {
              "n": 3,
              "box": [
                247,
                566,
                534,
                27
              ],
              "label": "Lid檔名"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-export-demo-v001/07-04-14-lid-stl-checked.png",
          "sha256": "de2465afcf4f52010e054dc123f3fc31574cd721305fb0c71e0f9534264a34eb",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "匯出成功通知，Lid Right Orthographic、Item60／46／7mm，RotationX180。圖上不直接顯示STL三角面或雜湊。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "上蓋尺寸"
            },
            {
              "n": 2,
              "box": [
                643,
                995,
                188,
                23
              ],
              "label": "匯出成功"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-snap-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-04-03",
      "title": "重新匯入核對",
      "lead": "空白毫米場景 · Import STL 重新匯入核對。",
      "actions": [
        "在Metric／Millimeters／Unit Scale0.001的空場景，逐件實際重匯入，核對Item尺寸、world外框及Select Non Manifold。"
      ],
      "checks": [
        "重匯入Rotation0、Scale1",
        "外框Body約<code>30</code>×<code>44.5</code>×<code>60</code>、Lid約<code>60</code>×<code>46</code>×<code>7 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "空白毫米場景 · Import STL",
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
          "path": "journal/2026-10-25-lesson07-snap-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch10-07-04-01",
    "title": "重開來源並選件",
    "actions": [
      "每件重開同hash副本；分別只選Body或Lid，隱藏另一件與建構工具，保留旋轉與世界座標。"
    ],
    "checks": [
      "每次只選Body或Lid，工具隱藏",
      "Body來源Item為<code>60</code>×<code>44.5</code>×<code>30 mm</code>、Y旋轉<code>90°</code>"
    ],
    "pitfalls": [
      {
        "title": "操作提醒",
        "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
      }
    ],
    "locate": "07-03候選方向副本 · Object Mode",
    "figures": [
      {
        "path": "evidence/07/2026-10-25-lesson07-snap-export-demo-v001/07-04-17-body-reimport-dimensions.png",
        "sha256": "119395eb4abc4d935d65e166660c7cdb2bc738e62738a3eaf68d07da08fd49e3",
        "size": [
          1494,
          1019
        ],
        "caption": "重匯入Body_STL的Item為30／44.5／60mm，Rotation三軸0、Scale1，反映候選世界姿態。",
        "marks": [
          {
            "n": 1,
            "box": [
              962,
              398,
              229,
              64
            ],
            "label": "重匯入外框"
          },
          {
            "n": 2,
            "box": [
              964,
              213,
              221,
              60
            ],
            "label": "旋轉歸零"
          }
        ],
        "tab": "操作位置"
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "07-03候選方向副本 · Object Mode 重開來源並選件。",
    "lead": "07-03候選方向副本 · Object Mode 重開來源並選件。",
    "references": [
      {
        "path": "journal/2026-10-25-lesson07-snap-export-demo-v001.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
