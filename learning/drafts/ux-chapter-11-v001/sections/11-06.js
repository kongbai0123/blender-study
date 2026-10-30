window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-06"] = {
  "id": "11-06",
  "title": "螺絲柱",
  "keyPoint": "核對 M3 五金、柱孔與上蓋孔草案。",
  "glossary": [
    {
      "term": "ETTINGER",
      "label": "ETTINGER 001.16.342",
      "text": "本案選用的M3×10 A2螺絲料號。"
    },
    {
      "term": "ruthex",
      "label": "ruthex RX-M3x5.7",
      "text": "本案選用的M3熱熔螺母料號。"
    },
    {
      "term": "原廠建議",
      "label": "原廠建議",
      "text": "五金供應商提供的設計參考，仍須按材料與製程試裝。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-08-04-01",
      "title": "記下五金規格",
      "lead": "記下五金規格。",
      "actions": [
        "先核對五金料號與原廠表格，再把原廠推薦、設計名義值、試驗值和實測值分欄；實測空格保持空白。"
      ],
      "checks": [
        "五金表列ETTINGER <code>001.16.342</code>與ruthex RX-M3x5.7",
        "原廠建議、設計名義、試驗與實測分欄"
      ],
      "pitfalls": [],
      "locate": "規格",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "evidence/08/2026-10-28-ch11-parameter-records-v001/parameter-records-v001.json",
          "label": "螺紋／已選五金參數與官方來源表"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch11-08-04-02",
      "title": "核對已選 M3 柱與蓋孔",
      "lead": "核對已選 M3 柱與蓋孔。",
      "actions": [
        "對照 ETTINGER <code>001.16.342</code> M3×<code>10</code> 與 ruthex RX-M3x5.7 的資料，核對柱孔、蓋穿孔及版本。",
        "核對柱孔名義 Ø<code>4</code>、深 <code>9 mm</code>、蓋孔名義 Ø<code>3.4 mm</code>，分清原廠建議與自訂試驗值；另記螺絲末端的名義空間。"
      ],
      "checks": [
        "盒體內部原圖可見四支柱的孔口，上蓋圖可見四穿孔",
        "讀值表分列柱孔Ø<code>4</code>深<code>9</code>、蓋孔Ø<code>3.4 mm</code>，實際安裝欄空白"
      ],
      "pitfalls": [
        {
          "title": "原廠建議與自訂草案分開",
          "text": "原廠推薦孔Ø<code>4</code>、最小深<code>6.7 mm</code>；本案深<code>9</code>與蓋孔Ø<code>3.4 mm</code>為自訂試驗，未驗證材料或安裝。"
        }
      ],
      "locate": "先依本章 11-16 的逐步實拍操作，保留原檔；現在只做本檢查點。",
      "figures": [
        {
          "path": "evidence/08/2026-10-28-four-insert-boss-gui-v001/BOS-09-pilots-applied.png",
          "sha256": "ddfb5f57c677eabaab44fdad23d7209078c128007864a010e4bb0e98bebf9bae",
          "size": [
            1494,
            1019
          ],
          "caption": "盒內四支柱均可見孔口；Body Dimensions為60×40×30 mm。",
          "tab": "柱孔",
          "marks": [
            {
              "n": 1,
              "box": [
                384,
                263,
                87,
                42
              ],
              "label": "後側柱孔"
            },
            {
              "n": 2,
              "box": [
                757,
                345,
                88,
                41
              ],
              "label": "前側柱孔"
            },
            {
              "n": 3,
              "box": [
                966,
                399,
                223,
                64
              ],
              "label": "盒外框"
            }
          ]
        },
        {
          "path": "evidence/08/2026-10-28-four-insert-boss-gui-v001/BOS-12-lid-holes-applied.png",
          "sha256": "26d4edc0fd500ebc83a75a49b3d879c88b80c6d6f12cb9bddf542947d9157663",
          "size": [
            1494,
            1019
          ],
          "caption": "上蓋四個穿孔可見；Lid Dimensions為60×40×6 mm，孔徑需查讀值。",
          "tab": "蓋穿孔",
          "marks": [
            {
              "n": 1,
              "box": [
                778,
                334,
                44,
                20
              ],
              "label": "蓋穿孔"
            },
            {
              "n": 2,
              "box": [
                963,
                399,
                226,
                64
              ],
              "label": "蓋外框"
            }
          ]
        }
      ],
      "keys": []
    }
  ]
};
