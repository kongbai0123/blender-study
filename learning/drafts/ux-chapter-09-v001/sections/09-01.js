window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["09-01"] = {
  "id": "09-01",
  "title": "定位榫",
  "keyPoint": "建立定位柱與孔，分清直徑差和法向間隙。",
  "glossary": [
    {
      "term": "TenonTool",
      "label": "TenonTool",
      "text": "併入盒體的定位柱工具名稱。"
    },
    {
      "term": "HoleTool",
      "label": "HoleTool",
      "text": "在上蓋開柱孔的工具名稱。"
    },
    {
      "term": "法向",
      "label": "法向",
      "text": "垂直於實際表面的方向，與水平或直徑方向不同。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch09-06-01-01",
      "title": "建立定位柱併入盒體",
      "lead": "既有盒蓋副本 · Object Mode / Body 建立定位柱併入盒體。",
      "actions": [
        "重驗原盒殼 <code>60</code> × <code>40</code> × <code>30</code>、壁與底 <code>2 mm</code>。Add Cylinder 建 <code>32</code> 段、<code>4</code> × <code>4</code> × <code>30 mm</code> 的柱，Apply Scale，移到 (<code>23</code>,<code>13</code>,<code>1.5</code>)；用 Body 的 Boolean Union 指定 TenonTool，再 Apply。"
      ],
      "checks": [
        "柱工具為<code>32</code>段、<code>4</code>×<code>4</code>×<code>30 mm</code>且中心<code>23</code>、<code>13</code>、<code>1.5 mm</code>",
        "Union套用後Body含柱外框為<code>60</code>×<code>40</code>×<code>31.5 mm</code>"
      ],
      "pitfalls": [],
      "locate": "既有盒蓋副本 · Object Mode / Body",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-tenon-demo-v006/06-01-03-pin-tool.png",
          "sha256": "489aacf7e93ea671b4f96b71d4882f13ffb978a4eebdcba42c4d7fa62b827093",
          "size": [
            1494,
            1019
          ],
          "caption": "TenonTool尺寸4×4×30 mm、中心23、13、1.5 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "定位柱中心"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "定位柱尺寸"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/06/2026-10-25-lesson06-tenon-demo-v006/06-01-06-union-applied.png",
          "sha256": "cb3cf4356056079dc33059d598cd84463c6137093c25cec14ffa3ef8add298dc",
          "size": [
            1494,
            1019
          ],
          "caption": "Union套用後盒內可見定位柱；Body含柱高度為31.5 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                822,
                338,
                42,
                164
              ],
              "label": "定位柱"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "含柱外框"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-tenon-demo-v006.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-01-02",
      "title": "在上蓋開柱孔",
      "lead": "Lid · Boolean Difference / Object 搜尋 在上蓋開柱孔。",
      "actions": [
        "新增同相位 <code>32</code> 段、<code>4.4</code> × <code>4.4</code> × <code>10 mm</code> 的 HoleTool，中心 (<code>23</code>,<code>13</code>,<code>16</code>)。在 Lid 的 Boolean Object 欄搜尋並確認 HoleTool，隱藏工具後 Apply；檢查最終孔壁與 Select Non Manifold。"
      ],
      "checks": [
        "Lid 的Difference工具指向 HoleTool",
        "套用後可見柱孔，Lid尺寸仍<code>60</code>×<code>40</code>×<code>6 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Lid · Boolean Difference / Object 搜尋",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-tenon-demo-v006/06-01-14-lid-underside.png",
          "sha256": "2d1931fecd2342a85faa70cdaa12ac6ab5210f7bf5d23fad51eb2f6c8ee7bb09",
          "size": [
            1494,
            1019
          ],
          "caption": "上蓋底視可辨柱孔與原有環唇；Lid外框60×40×6 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                817,
                509,
                47,
                35
              ],
              "label": "上蓋柱孔"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "上蓋外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-tenon-demo-v006.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch09-06-01-03",
      "title": "核對間隙並另存",
      "lead": "最終網格讀值 · Save As / Open 核對間隙並另存。",
      "actions": [
        "從柱孔實際輪廓核對 <code>32</code> 個轉角、相位及逐邊法向間隙；暫抬蓋檢視後移回，另存 <code>u06_locating_tenon_v001.blend</code>，再重新開啟核對 hash 與幾何。"
      ],
      "checks": [
        "計算記錄分列名義直徑總差<code>0.4</code>與單邊<code>0.2 mm</code>",
        "另存重開後，實際多邊形法向差約<code>0.199036 mm</code>另列於讀值"
      ],
      "pitfalls": [
        {
          "title": "定位可能互相干涉",
          "text": "環形唇邊與定位柱同時限制位置，列印偏差可能使兩者卡住；細長柱亦需檢查列印穩定性。"
        }
      ],
      "locate": "最終網格讀值 · Save As / Open",
      "figures": [
        {
          "path": "evidence/06/2026-10-25-lesson06-tenon-demo-v006/06-01-16-assembly-geometry.png",
          "sha256": "a01cae28fb6a90012c0d64889f99e40e5cecd6a307033a2336da30bf65385fb4",
          "size": [
            1494,
            1019
          ],
          "caption": "定位柱與孔在組裝位置；本角度不能直接讀出配合間隙。",
          "marks": [
            {
              "n": 1,
              "box": [
                819,
                335,
                44,
                38
              ],
              "label": "柱孔位置"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "含柱外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson06-tenon-demo-v006.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
