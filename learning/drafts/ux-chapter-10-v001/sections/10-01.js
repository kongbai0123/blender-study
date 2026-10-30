window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["10-01"] = {
  "id": "10-01",
  "title": "參數與估算條件",
  "keyPoint": "分清卡扣幾何參數與材料估算條件。",
  "glossary": [
    {
      "term": "δ_req",
      "label": "δ_req",
      "text": "裝配路徑要求的撓度，須與允許撓度分開。"
    },
    {
      "term": "ε_allow",
      "label": "ε_allow",
      "text": "材料允許應變，估算式中用小數比例。"
    },
    {
      "term": "Q",
      "label": "Q",
      "text": "與根部條件相關的修正量，尚待決定且非安全係數。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch10-07-01-01",
      "title": "核對原盒參照",
      "lead": "Blender · 原盒參考 核對原盒參照。",
      "actions": [
        "查看下方真實重開畫面：Object Mode 的 Body_Reference，Item › Dimensions 為<code>60</code>／<code>40</code>／<code>30 mm</code>。"
      ],
      "checks": [
        "活動物件名為 Body_Reference",
        "Dimensions 為<code>60</code>×<code>40</code>×<code>30 mm</code>，未附加卡扣"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "已開啟時再按 <kbd>N</kbd> 會關閉；開啟側欄不代表已設定 Dimensions、Location 或單位。"
        }
      ],
      "locate": "Blender · 原盒參考",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-parameters-demo-v001/07-01-12-reopened-verified.png",
          "sha256": "05ccab2799c6d1965c1878130815b63d2bbff9cd4b87417c2d63458e52bc3472",
          "size": [
            1494,
            1019
          ],
          "caption": "Body_Reference沒有卡扣，Item60／40／30mm且Scale1，作為卡扣設計原盒參照。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "原盒尺寸"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-parameters-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-01-02",
      "title": "辨認參數定義",
      "lead": "辨認參數定義。",
      "actions": [
        "辨認 L、h、b、R、u、δ_req、α、β、e、g、f 的定義；未選定的數值保留待定。"
      ],
      "checks": [
        "參數表分列 L、h、b、R、u及δ_req",
        "δ_allow、材料與允許應變未填成既定值"
      ],
      "pitfalls": [],
      "locate": "尺寸參數表",
      "figures": [],
      "keys": [],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。",
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-parameters-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-01-03",
      "title": "閱讀估算式",
      "lead": "閱讀估算式。",
      "actions": [
        "閱讀均勻矩形懸臂近似式及來源；ε_allow 用小數比例。先核對根部、接觸路徑與材料條件，材料及允許應變保留待定。"
      ],
      "checks": [
        "估算欄分列ε_allow、有效L與根部Q",
        "材料未定，允許撓度、裝拆力與強度結果空白"
      ],
      "pitfalls": [],
      "locate": "估算條件 · 尚未代入",
      "figures": [],
      "keys": [],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。",
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-parameters-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
