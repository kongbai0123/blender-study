window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-10"] = {
  "id": "03-10",
  "title": "外形尺寸與 Apply Scale",
  "keyPoint": "設定原盒外形，再套用縮放保持尺寸。",
  "glossary": [
    {
      "term": "Apply",
      "label": "Apply",
      "text": "Object選單中套用物件變換的子選單，本節選Scale。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-04-03-01",
      "title": "輸入 60 × 40 × 30 mm",
      "lead": "Sidebar › Item › Dimensions 輸入 60 × 40 × 30 mm。",
      "actions": [
        "依序輸入 X <code>60mm</code>、Y <code>40mm</code>、Z <code>30mm</code>。"
      ],
      "checks": [
        "Dimensions 顯示 <code>60</code>×<code>40</code>×<code>30 mm</code>",
        "從<code>2 mm</code>方塊開始時 Scale 為 <code>30</code>、<code>20</code>、<code>15</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "已開啟時再按 <kbd>N</kbd> 會關閉；開啟側欄不代表已設定 Dimensions、Location 或單位。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Sidebar › Item › Dimensions",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-07-02-view-sidebar.png",
          "sha256": "7c2aa6418bc22092bd1ec89d617e99692402f9a8c5a5f669055b65c550b34bb9",
          "size": [
            1494,
            1019
          ],
          "caption": "View選單的Sidebar列右側標N；此圖尚未打開側欄。",
          "marks": [
            {
              "n": 1,
              "box": [
                172,
                69,
                247,
                22
              ],
              "label": "側欄入口"
            }
          ],
          "tab": "操作位置"
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
      "stepId": "ch03-04-03-02",
      "title": "套用縮放",
      "lead": "3D Viewport 的 Object › Apply › Scale 套用縮放。",
      "actions": [
        "Object › Apply › Scale（<kbd>Ctrl</kbd>+<kbd>A</kbd> › Scale）。"
      ],
      "checks": [
        "Scale 三欄回到 <code>1</code>",
        "Dimensions 仍為 <code>60</code>×<code>40</code>×<code>30 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Ctrl</kbd>+<kbd>A</kbd> 只開選單，不直接套用 Scale；不能用它替代 Boolean／Solidify 修改器的 Apply。"
        }
      ],
      "locate": "3D Viewport 的 Object › Apply › Scale",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-03-02-apply-menu.png",
          "sha256": "534165b57a361df62655ab91e707b378382f53ad9ad1b3c794ded18519306a18",
          "size": [
            1494,
            1019
          ],
          "caption": "Object › Apply子選單的Scale已反白；右側Scale尚為30、20、15。",
          "marks": [
            {
              "n": 1,
              "box": [
                492,
                168,
                216,
                24
              ],
              "label": "套用縮放"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
