window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["02-01"] = {
  "id": "02-01",
  "title": "總間隙與單側間隙",
  "keyPoint": "算出總間隙，置中對稱時再換算單側。",
  "glossary": [
    {
      "term": "總間隙",
      "label": "總間隙",
      "text": "同方向孔寬減去軸寬的差。"
    },
    {
      "term": "單側",
      "label": "單側",
      "text": "對稱置中時，總差的一半。"
    },
    {
      "term": "名義",
      "label": "名義",
      "text": "設計指定的數值，尚非實測結果。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch02-gap-terms",
      "title": "先分清總間隙與單側",
      "lead": "同一 X 方向，先區分兩件名義尺寸 先分清總間隙與單側。",
      "actions": [
        "對照原盒口內寬<code>56</code>與唇外寬<code>55.6 mm</code>，列總差<code>56</code>−<code>55.6</code>=<code>0.4 mm</code>。",
        "只有同軸置中且對稱時，這個方向的名義單側為<code>0.4</code>÷<code>2</code>=<code>0.2 mm</code>。"
      ],
      "checks": [
        "計算記錄為 <code>56</code>−<code>55.6</code>＝<code>0.4 mm</code> 總間隙",
        "置中對稱條件下，單側記為 <code>0.2 mm</code>；實測欄仍空白"
      ],
      "pitfalls": [],
      "locate": "同一 X 方向，先區分兩件名義尺寸",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png",
          "sha256": "bc12d5f81fd5424cef7dd64c295941c8a31de430a45818782e249f8b1d2fec64",
          "size": [
            1494,
            1019
          ],
          "caption": "盒蓋分離，上蓋下方突出環形唇邊；作用中Body尺寸60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                332,
                331,
                544,
                66
              ],
              "label": "下方環形唇邊"
            },
            {
              "n": 2,
              "box": [
                963,
                399,
                226,
                64
              ],
              "label": "盒體外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/printing-measurement-protocol-v001.json",
          "label": "現場列印、量測與試配方法（沒有結果）"
        },
        {
          "path": "journal/templates/fit-coupon-records-v002.csv",
          "label": "六孔名義設計與空白實測 CSV"
        }
      ]
    }
  ]
};
