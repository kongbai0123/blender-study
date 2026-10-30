window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-04"] = {
  "id": "03-04",
  "title": "命名與整理 Collection",
  "keyPoint": "替五個部件命名，移入 Station 集合。",
  "glossary": [
    {
      "term": "Collection",
      "label": "Collection",
      "text": "Outliner 中用來整理物件的集合。"
    },
    {
      "term": "Station",
      "label": "Station",
      "text": "本節收納五個訊號站部件的集合名稱。"
    },
    {
      "term": "New Collection",
      "label": "New Collection",
      "text": "Move to Collection選單中建立新集合的項目。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-04-01",
      "title": "替五個部件改名",
      "lead": "Outliner / 已建立的基座 替五個部件改名。",
      "actions": [
        "在 Outliner 依序點地面、平台、基座、立柱、訊號球，各按 <kbd>F2</kbd>（Edit › Rename Active Item）改名為 Ground、Platform、BeaconBase、Post、Signal。"
      ],
      "checks": [
        "Outliner 列出 Ground、Platform、BeaconBase",
        "另有 Post、Signal，名稱分別對上各部件"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "本次實測將 Cube 改為 ShortcutCube 以驗證功能；練習請輸入本步的 BeaconBase。物件名不同於網格或材質資料塊名。"
        }
      ],
      "locate": "Outliner / 已建立的基座",
      "figures": [
        {
          "path": "evidence/02/2026-10-22-lesson02-demo-v001/02-04-02-rename-menu.png",
          "sha256": "bb945a2e6b0d47123c9c5c604a1f711b794f00f2c6c3992715bda88303947653",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit選單可見Rename Active Item與F2；目前尚未完成改名。",
          "marks": [
            {
              "n": 1,
              "box": [
                62,
                186,
                199,
                23
              ],
              "label": "改名入口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-02-04-02",
      "title": "建立 Station 集合",
      "lead": "Outliner / Collection 建立 Station 集合。",
      "actions": [
        "下個小回合在 Outliner 點第一個部件、Ctrl+點其餘部件，滑鼠移到 3D Viewport 按 <kbd>M</kbd> › New Collection，命名為 Station。"
      ],
      "checks": [
        "Outliner 出現 Station 集合",
        "展開後可見五個訊號站部件"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "本次原生事件驗證到選單展開，沒有替你建立 Station；建立後仍須展開 Outliner 核對。"
        }
      ],
      "locate": "Outliner / Collection",
      "figures": [
        {
          "path": "evidence/01/2026-10-27-shortcuts-demo-v001/02-03-03-m-collection-menu.png",
          "sha256": "e9426fdd706de16750ee3300ce9d9a3855532b3ffbe4289908070886c2733467",
          "size": [
            1494,
            1019
          ],
          "caption": "Move to Collection選單中可見New Collection；這張是另一方塊的入口參照。",
          "marks": [
            {
              "n": 1,
              "box": [
                561,
                614,
                168,
                24
              ],
              "label": "新增集合"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-02-04-03",
      "title": "另存 v002 並登記",
      "lead": "File › Save As… 另存 v002 並登記。",
      "actions": [
        "另存 <code>u02_station_v002.blend</code>，保存後登記檢查點。"
      ],
      "checks": [
        "保存通知或重開檔名為 <code>u02_station_v002.blend</code>",
        "版本表的路徑、SHA-<code>256</code>對應此檔"
      ],
      "pitfalls": [],
      "locate": "File › Save As…",
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
          "path": "journal/2026-10-22-lesson02-03-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
