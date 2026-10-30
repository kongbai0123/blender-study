window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["09-03"] = {
  "id": "09-03",
  "title": "匯出與數位核對",
  "keyPoint": "分件匯出燕尾盒蓋，核對重匯入尺寸。",
  "glossary": [
    {
      "term": "Scale",
      "label": "Scale",
      "text": "本節重匯入後的物件縮放係數，應為1。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch09-06-03-01",
      "title": "分別匯出兩件",
      "lead": "06-02同一來源副本 · 單件選取 / Export STL 分別匯出兩件。",
      "actions": [
        "每件匯出前重新開啟來源副本，只選Body或SlidingLid，隱藏另一件並保持三個工具隱藏。File › Export › STL，核對新檔名，勾Selection Only，Scale1、Scene Unit不勾後各自匯出。"
      ],
      "checks": [
        "每次匯出只選Body或SlidingLid",
        "exports中有兩個獨立STL且工具未混入"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "先保留未存內容；已登記版本沒有再修改時，重開提示不要用 Save 覆寫；不確定就 Cancel。"
        }
      ],
      "locate": "06-02同hash副本 · 單件選取 / Export STL",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001/06-03-06-body-export-options.png",
          "sha256": "6a2a89f809465e8117320d19b53ef0720de5a10516cd39306a892d79ff6019e0",
          "size": [
            1060,
            600
          ],
          "caption": "Body匯出選項：Selection Only開、Scale1、Scene Unit關。",
          "marks": [
            {
              "n": 1,
              "box": [
                921,
                147,
                131,
                22
              ],
              "label": "僅選取物件"
            },
            {
              "n": 2,
              "box": [
                921,
                170,
                131,
                42
              ],
              "label": "尺度與單位"
            },
            {
              "n": 3,
              "box": [
                249,
                568,
                529,
                23
              ],
              "label": "盒體STL檔名"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001/06-03-13-lid-export-options.png",
          "sha256": "6cfd473cb51411f616ef230f4e3d7ed8690b4f988f130172d36fd50c900d7012",
          "size": [
            1060,
            600
          ],
          "caption": "SlidingLid以獨立檔名匯出，使用相同選項。",
          "marks": [
            {
              "n": 1,
              "box": [
                921,
                147,
                131,
                22
              ],
              "label": "僅選取物件"
            },
            {
              "n": 2,
              "box": [
                921,
                170,
                131,
                42
              ],
              "label": "尺度與單位"
            },
            {
              "n": 3,
              "box": [
                249,
                568,
                529,
                23
              ],
              "label": "滑蓋STL檔名"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-03-02",
      "title": "重新匯入核對",
      "lead": "空白毫米場景 · Import STL / Item Dimensions 重新匯入核對。",
      "actions": [
        "新建空白Metric／Millimeters／Unit Scale0.001場景，實際匯入兩份剛產生的STL。首件匯入後才切Item；核對Dimensions、燕尾端面及Select Non Manifold，再顯示兩件讀回組裝間距。"
      ],
      "checks": [
        "重匯入外框Body60×<code>40</code>×<code>30</code>、Lid約<code>60</code>×<code>40</code>×<code>5.2 mm</code>",
        "兩件Scale1，非流形邊檢查各自記錄"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "空白毫米場景 · Import STL / Item Dimensions",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001/06-03-17-body-reimport-dimensions.png",
          "sha256": "594e402e24bc477199fb729a2ae876e6699a4ac7aad224df23e7d55f9b51f301",
          "size": [
            1494,
            1019
          ],
          "caption": "實際重匯入Body_STL，Dimensions60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "盒體STL尺寸"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001/06-03-21-lid-reimport-dimensions.png",
          "sha256": "2f347072775f85671a78161395323f414fb658609ae9ad6c068c9c2916a1ba00",
          "size": [
            1494,
            1019
          ],
          "caption": "實際重匯入SlidingLid_STL，Dimensions60×40×5.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "滑蓋STL尺寸"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-03-03",
      "title": "保留試配欄位",
      "lead": "後續列印與試配 · 本次留空 保留試配欄位。",
      "actions": [
        "在試配紀錄標示 <code>0.4 mm</code> 水平總差、置中時每側 <code>0.2 mm</code> 是名義試驗值。",
        "方向、切片、實體尺寸、滑入狀態及合格值目前留空；取得實體結果後才記錄。"
      ],
      "checks": [
        "試配表的水平總差<code>0.4</code>標為試驗值",
        "方向、切片、實測與滑入結果仍空白"
      ],
      "pitfalls": [],
      "locate": "後續列印與試配 · 本次留空",
      "figures": [],
      "keys": [],
      "figureNote": "已補查現行教材及原操作序列，未找到可獨立對應本步的實拍。",
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-dovetail-export-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
