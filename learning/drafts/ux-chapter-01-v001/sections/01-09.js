window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-09"] = {
  "id": "01-09",
  "title": "保存 v002 並重新開啟",
  "keyPoint": "保存 v002，從版本紀錄找回同一份場景。",
  "glossary": [
    {
      "term": "File › Save",
      "label": "File › Save",
      "text": "保存目前工作檔的功能，會寫回目前路徑。"
    },
    {
      "term": "重新開啟",
      "label": "重新開啟",
      "text": "從磁碟讀回已保存的檔案，以核對保存結果。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-09-01",
      "title": "保存 v002",
      "lead": "Blender 的 v002 工作檔 保存 v002。",
      "actions": [
        "File › Save（<kbd>Ctrl</kbd>+<kbd>S</kbd>）保存目前的 <code>u01_basics_v002.blend</code>。",
        "回報本次物件名稱與一組已練過的 Transform 數值。"
      ],
      "checks": [
        "保存通知或目前檔名為 <code>u01_basics_v002.blend</code>",
        "筆記中有本次 Cube 的實際 Transform 數值"
      ],
      "pitfalls": [],
      "locate": "Blender 的 v002 工作檔",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-09-01-file-save.png",
          "sha256": "7bbaab16f1d4b17aca93a7099407885ffc9a727e93f32db3bb09c5990fc9b6fc",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "File 選單展開且列出 Save 與 Ctrl S。",
          "marks": [
            {
              "n": 1,
              "box": [
                30,
                3,
                27,
                21
              ],
              "label": "File"
            },
            {
              "n": 2,
              "box": [
                28,
                133,
                202,
                20
              ],
              "label": "Save"
            }
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-09-02-saved.png",
          "sha256": "bbdd2c52f783dec61a33ce2e40a4f8d2e94cd35ec18c9b00835e69c38a405a6b",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "底部保存通知為u01_basics_v002.blend；尺寸3×2×2 m。",
          "marks": [
            {
              "n": 1,
              "box": [
                627,
                996,
                218,
                21
              ],
              "label": "v002保存提示"
            },
            {
              "n": 2,
              "box": [
                965,
                402,
                223,
                60
              ],
              "label": "尺寸讀值"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-01-09-02",
      "title": "登記 v002",
      "lead": "教學頁檔案版本紀錄 登記 v002。",
      "actions": [
        "先核對已保存的 <code>u01_basics_v002.blend</code>，到教學頁「檔案版本」選單元 <code>01</code>、該檔案與「場景 .blend」並登記。",
        "登記後核對路徑與 SHA-<code>256</code>；後續修改先另存未使用的新版本。"
      ],
      "checks": [
        "版本表出現 v002 的路徑",
        "同列有實檔 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "教學頁檔案版本紀錄",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json",
          "label": "隔離假專案的 CLI 版本登記與來源關聯示範；不是原次網頁登記"
        },
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步核對教學頁的檔案版本表；沒有登記畫面實拍，請以自己的實際紀錄為準。"
    },
    {
      "stepId": "ch01-01-09-03",
      "title": "重新開啟核對",
      "lead": "File › Open… 重新開啟核對。",
      "actions": [
        "自行選取剛登記的 v002，重新開啟後核對名稱、路徑與 Transform。"
      ],
      "checks": [
        "File › Open 選到自己的 v002",
        "重開後 Cube 的 Transform 與保存前筆記相符"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
        }
      ],
      "locate": "File › Open…",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-09-03-open-dialog.png",
          "sha256": "df3e6a754358116a8062fc4b1435e6d2dd66a650049954a81b1707ca2f3098c5",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "Open 對話框列出 u01_basics_v001.blend 與 v002，檔名欄是 v002。",
          "marks": [
            {
              "n": 1,
              "box": [
                394,
                8,
                318,
                25
              ],
              "label": "資料夾"
            },
            {
              "n": 2,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "按 Open"
            }
          ]
        },
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-09-04-reopened.png",
          "sha256": "3dc246c3eae28ec8686a53bffd7633c18cce50fdf8ce71fccede5de63b059e99",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "選取 Cube，右欄顯示 Dimensions 3×2×2 m 及 Scale X 1.500。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                300,
                228,
                160
              ],
              "label": "Scale／Di"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson01-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
