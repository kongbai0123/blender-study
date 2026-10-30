window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-10"] = {
  "id": "01-10",
  "title": "認識要做的小盒",
  "keyPoint": "找出環形唇邊與盒口內壁的配合表面。",
  "glossary": [
    {
      "term": "環形唇邊",
      "label": "環形唇邊",
      "text": "上蓋底部伸入盒口的一圈凸緣。"
    },
    {
      "term": "蓋板",
      "label": "蓋板",
      "text": "覆蓋盒口的上蓋平板部分。"
    },
    {
      "term": "盒口內側壁",
      "label": "盒口內側壁",
      "text": "盒口朝向內腔的表面，與唇邊外側相對。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-observe-lip",
      "title": "辨認蓋板與唇邊",
      "lead": "教學頁原圖；本步只觀察，不在 Blender 操作。 辨認蓋板與唇邊。",
      "actions": [
        "先看分離視圖：找出下方開口盒和暫時抬高的上蓋。",
        "再看上蓋底面：找出外側蓋板與向下突出的環形唇邊。",
        "回答：組裝時，哪個部分伸入盒口、限制上蓋左右移動：整片蓋板，還是下方的環形唇邊？"
      ],
      "checks": [
        "分離圖中上蓋位於盒口上方",
        "上蓋底部可辨認向下突出的環形唇邊"
      ],
      "pitfalls": [],
      "locate": "教學頁原圖；本步只觀察，不在 Blender 操作。",
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
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-09-underside-checked.png",
          "sha256": "c97b0253251f190a6f1e4541d7ea809a0b2bcfc2acd7485bec602d3e7065afde",
          "size": [
            1494,
            1019
          ],
          "caption": "底部斜視可見環形唇邊與內凹，右側Dimensions為60×40×6 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                436,
                518,
                417,
                112
              ],
              "label": "環形唇邊"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                63
              ],
              "label": "上蓋外框"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch01-fit-surfaces",
      "title": "辨認配合的兩個表面",
      "lead": "觀察 05-05 分離圖；上蓋暫抬高 辨認配合的兩個表面。",
      "actions": [
        "先看分離圖：上蓋暫時抬高，留意板下環形唇邊的外側面。",
        "再看盒體原圖：找到盒口內側壁與盒體外壁，判斷水平配合間隙要看哪兩個面。"
      ],
      "checks": [
        "上蓋可指出唇邊外側面",
        "盒體可指出與它相對的盒口內側壁"
      ],
      "pitfalls": [],
      "locate": "觀察 05-05 分離圖；上蓋暫抬高",
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
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-02-source-body-checked.png",
          "sha256": "b04ade7f0a4f5ec5056fb76406b887b04e6f1e9527198d8281ffeb30e1d0e49d",
          "size": [
            1494,
            1019
          ],
          "caption": "Body 已選取，畫面可見開口及內側壁，外形尺寸 60×40×30 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1286,
                94,
                150,
                20
              ],
              "label": "原盒 Body"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-lid-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
