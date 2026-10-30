window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["06-01"] = {
  "id": "06-01",
  "title": "匯出原盒並在切片軟體核對",
  "keyPoint": "只匯出 Body，核對 STL 毫米外框。",
  "glossary": [
    {
      "term": "STL",
      "label": "STL",
      "text": "以三角面記錄表面的檔案，沒有單位標記。"
    },
    {
      "term": "Selection Only",
      "label": "Selection Only",
      "text": "只匯出選取物件的選項。"
    },
    {
      "term": "Scene Unit",
      "label": "Scene Unit",
      "text": "匯出時是否套用場景單位換算的選項。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch06-04-07-01",
      "title": "開啟匯出視窗",
      "lead": "File › Export › STL (.stl) 開啟匯出視窗。",
      "actions": [
        "開啟 <code>u04_box_v001.blend</code>，選取 Body，File › Export › STL (.stl)。"
      ],
      "checks": [
        "所選物件為 Body",
        "STL 檔案視窗右側出現匯出選項"
      ],
      "pitfalls": [],
      "locate": "File › Export › STL (.stl)",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-07-01-export-menu.png",
          "sha256": "5d9ede8476909290870ebbfa4fb09a7ec95eb3f7da33320c7ae1a7c411c508e5",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "File › Export 子選單展開，STL (.stl) 突出；底部保存提示可見。",
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
                307,
                202,
                20
              ],
              "label": "Export"
            },
            {
              "n": 3,
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
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-07-02-export-dialog.png",
          "sha256": "a97d9f50c4f31dce935ebaf0b861563297d0d8825068e90b50e7ae6a60c8859d",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "STL 匯出視窗，Scale 1.000、Scene Unit 未勾、Selection Only 也未勾；檔名 u04_box_v001.stl。",
          "marks": [
            {
              "n": 1,
              "box": [
                394,
                8,
                318,
                25
              ],
              "label": "exports "
            },
            {
              "n": 2,
              "box": [
                922,
                171,
                130,
                20
              ],
              "label": "Scale 1."
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-04-07-02",
      "title": "設定選項並匯出",
      "lead": "匯出選項 設定選項並匯出。",
      "actions": [
        "在 STL 匯出視窗勾 Selection Only、Scale <code>1</code>、Scene Unit 不勾、Apply Modifiers 勾、ASCII 不勾、Forward Y、Up Z。",
        "確認選取 Body，存至自己的單元 <code>04</code> exports 資料夾，檔名 <code>u04_box_v001.stl</code>，按 Export STL。"
      ],
      "checks": [
        "Selection Only開、Scale1、Scene Unit關",
        "Export STL 後回主視窗，指定目錄有 <code>u04_box_v001.stl</code>"
      ],
      "pitfalls": [],
      "locate": "匯出選項",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-07-02-export-dialog.png",
          "sha256": "a97d9f50c4f31dce935ebaf0b861563297d0d8825068e90b50e7ae6a60c8859d",
          "size": [
            1060,
            600
          ],
          "tab": "操作位置",
          "caption": "STL 匯出視窗，Scale 1.000、Scene Unit 未勾、Selection Only 也未勾；檔名 u04_box_v001.stl。",
          "marks": [
            {
              "n": 1,
              "box": [
                394,
                8,
                318,
                25
              ],
              "label": "exports "
            },
            {
              "n": 2,
              "box": [
                922,
                171,
                130,
                20
              ],
              "label": "Scale 1."
            }
          ]
        },
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-07-03-stl-checked.png",
          "sha256": "df19115dfbafb1efe87f7e43d99a06613339ea5f7a32088a013e5b8038eb8c21",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "底部顯示匯出成功，外框60×40×30 mm；這張歷史實拍中的盒體仍名為Cube。",
          "marks": [
            {
              "n": 1,
              "box": [
                643,
                996,
                186,
                21
              ],
              "label": "匯出成功"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "盒體外框"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch06-04-07-03",
      "title": "登記並在切片軟體核對",
      "lead": "教學頁檔案版本紀錄、切片軟體 登記並在切片軟體核對。",
      "actions": [
        "到教學頁「檔案版本」以單元 <code>04</code> 登記這個 STL（用途：列印／其他輸出，來源：<code>u04_box_v001.blend</code>）。",
        "把 STL 拖進切片軟體看尺寸。"
      ],
      "checks": [
        "版本表的STL來源為原盒場景",
        "實際使用切片軟體核對外框為<code>60</code>×<code>40</code>×<code>30 mm</code>"
      ],
      "pitfalls": [],
      "locate": "教學頁檔案版本紀錄、切片軟體",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/printing-measurement-protocol-v001.json",
          "label": "現場列印、量測與試配方法（沒有結果）"
        },
        {
          "path": "journal/templates/fit-coupon-records-v002.csv",
          "label": "六孔名義設計與空白實測 CSV"
        },
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
