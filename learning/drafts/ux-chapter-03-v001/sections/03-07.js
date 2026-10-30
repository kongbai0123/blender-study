window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-07"] = {
  "id": "03-07",
  "title": "保存兩份檢查點",
  "keyPoint": "分別保存訊號站與毫米方塊，逐檔重開核對。",
  "glossary": [
    {
      "term": "版本表",
      "label": "版本表",
      "text": "列出已保存檔案的路徑、用途與SHA-256的表格。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-02-07-01",
      "title": "保存訊號站檢查點",
      "lead": "訊號站工作檔 保存訊號站檢查點。",
      "actions": [
        "保存並核對自己的訊號站檢查點（例如 <code>u02_station_v002.blend</code>）。"
      ],
      "checks": [
        "訊號站工作檔有自己的路徑與檔名",
        "Outliner 可見 Station 與五個部件"
      ],
      "pitfalls": [],
      "locate": "訊號站工作檔",
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
    },
    {
      "stepId": "ch03-02-07-02",
      "title": "保存毫米方塊檢查點",
      "lead": "毫米方塊工作檔 保存毫米方塊檢查點。",
      "actions": [
        "另行保存毫米方塊檢查點，核對 <code>40</code> × <code>30</code> × <code>10 mm</code>。"
      ],
      "checks": [
        "毫米方塊另有自己的檔名",
        "重開後 Dimensions 為 <code>40</code>×<code>30</code>×<code>10 mm</code>"
      ],
      "pitfalls": [],
      "locate": "毫米方塊工作檔",
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
    },
    {
      "stepId": "ch03-02-07-03",
      "title": "登記並重開核對",
      "lead": "共用檔案紀錄 / Blender 登記並重開核對。",
      "actions": [
        "逐一登記真實檔案並各自重新開啟核對。"
      ],
      "checks": [
        "版本表有兩份獨立場景紀錄",
        "逐檔重開後各自與部件或尺寸紀錄相符"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
        }
      ],
      "locate": "共用檔案紀錄 / Blender",
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
