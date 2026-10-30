window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["04-02"] = {
  "id": "04-02",
  "title": "安排相機",
  "keyPoint": "切到相機畫框，調整一次取景。",
  "glossary": [
    {
      "term": "Camera",
      "label": "Camera",
      "text": "決定渲染觀察位置與方向的相機物件。"
    },
    {
      "term": "Active Camera",
      "label": "Active Camera",
      "text": "目前用來輸出的相機。"
    },
    {
      "term": "取景",
      "label": "取景",
      "text": "相機畫框內會輸出的範圍。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch04-03-02-01",
      "title": "選取相機",
      "lead": "Outliner 選取相機。",
      "actions": [
        "在 Outliner 點 Camera；沒有相機時用 Add › Camera 新增一部。"
      ],
      "checks": [
        "Outliner 的 Camera 列反白",
        "所選物件在視窗中呈現相機線框"
      ],
      "pitfalls": [],
      "locate": "Outliner",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-02-01-cameras-menu.png",
          "sha256": "7ae163877cc665b1d7a718cefb107d84b49ef043b63a13b77532a9d35357b142",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Camera 已選取，View › Cameras 子選單中 Active Camera 旁標 Numpad 0。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                94,
                150,
                20
              ],
              "label": "Camera"
            },
            {
              "n": 2,
              "box": [
                169,
                28,
                32,
                20
              ],
              "label": "View"
            },
            {
              "n": 3,
              "box": [
                170,
                266,
                250,
                19
              ],
              "label": "Cameras"
            }
          ]
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
      "stepId": "ch04-03-02-02",
      "title": "切到相機視角",
      "lead": "3D Viewport 的相機檢視 切到相機視角。",
      "actions": [
        "用 View › Cameras › Active Camera 切到相機取景，先看作品是否在畫框內。"
      ],
      "checks": [
        "視窗出現相機畫框",
        "畫框內外區域可區分"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "是數字鍵盤 <code>0</code>，與主鍵盤上排 <code>0</code> 分開；未驗證筆電實體鍵盤模擬效果時，保留 View &gt; Cameras &gt; Active Camera。"
        }
      ],
      "locate": "3D Viewport 的相機檢視",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-02-02-camera-view.png",
          "sha256": "df9748c3ac34ccd4560c98dfe7796d5cfd3adeb7d2ea335790a092c307099928",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Camera Perspective中模型完整落在相機畫框內。",
          "marks": [
            {
              "n": 1,
              "box": [
                66,
                83,
                170,
                24
              ],
              "label": "相機視角"
            },
            {
              "n": 2,
              "box": [
                307,
                301,
                614,
                347
              ],
              "label": "輸出畫框"
            }
          ]
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
      "stepId": "ch04-03-02-03",
      "title": "調整一次取景",
      "lead": "Camera / Transform 調整一次取景。",
      "actions": [
        "依目前畫面只調整一個軸或角度，回到取景核對。"
      ],
      "checks": [
        "本次變更的軸或角度有前後值",
        "回到相機視角，作品較完整落在畫框內"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "G 是相對位移；R 是相對旋轉，不等於直接設定 Location／Euler 欄位的絕對值。實際角度與單位依相機當前場景，不預填一組會覆寫取景的數字。"
        },
        {
          "title": "操作提醒",
          "text": "本次驗證為出廠鍵位、Global；父子關係或不同旋轉模式需先依實際畫面核對。"
        }
      ],
      "locate": "Camera / Transform",
      "figures": [
        {
          "path": "evidence/03/2026-10-22-lesson03-demo-v001/03-02-03-camera-z.png",
          "sha256": "4ef0f19f3adac1e70bb0c78ecc83278ab50c419f5c0c87ead3628c85bd509938",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Camera Location Z 5.3 m，訊號站位於相機框內。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                172,
                176,
                20
              ],
              "label": "Location"
            }
          ]
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
