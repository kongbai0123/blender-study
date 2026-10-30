window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-05"] = {
  "id": "11-05",
  "title": "匹配內牙對件（盒側保護蓋）",
  "keyPoint": "核對盒側帽的內牙、徑向差與端隙。",
  "glossary": [
    {
      "term": "relief",
      "label": "relief",
      "text": "端部的局部退讓幾何。"
    },
    {
      "term": "徑向",
      "label": "徑向",
      "text": "由旋轉軸向外的方向，徑向增量不等於直徑增量。"
    },
    {
      "term": "端隙",
      "label": "端隙",
      "text": "兩件沿軸向端部的名義空間。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-08-03-01",
      "title": "建立匹配盒側保護蓋",
      "lead": "建立匹配盒側保護蓋。",
      "actions": [
        "依 <code>11</code>-<code>15</code> 開啟起始副本並確認帽體與刀具名稱，沿 Difference 流程另存。",
        "保留 v001 零端隙對照與 v002 端隙版本，確認原平面上蓋仍保留。"
      ],
      "checks": [
        "盒側帽內部原圖可辨螺旋內牙與端部退讓",
        "保留v001零端隙、v002端隙版本及原平面上蓋"
      ],
      "pitfalls": [],
      "locate": "先依本章 11-15 的逐步實拍操作，保留原檔；現在只做本檢查點。",
      "figures": [
        {
          "path": "evidence/08/2026-10-28-side-cap-relief-gui-v001/REL-05-difference.png",
          "sha256": "5c428da67a9560f22f397cf75f9db4a8c4f8017866a56cdd4e65f27208033637",
          "size": [
            1494,
            1019
          ],
          "caption": "帽體外側封閉端面，Side_Cap_Blank Item5.5／15.4／15.4mm；這角度看不到內牙與relief。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                419,
                229,
                64
              ],
              "label": "帽體外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-08-03-02",
      "title": "核對保護蓋網格與試驗間隙",
      "lead": "核對保護蓋網格與試驗間隙。",
      "actions": [
        "核對帽體版本與讀值；記錄徑向展開 <code>0.2 mm</code>、名義直徑差 <code>0.4 mm</code>、名義中心端隙 <code>0.2 mm</code>。",
        "查閱非流形、射線及離散旋轉檢查，說明它們沒有涵蓋的範圍。"
      ],
      "checks": [
        "紀錄分列徑向展開<code>0.2</code>、直徑差<code>0.4</code>、中心端隙<code>0.2 mm</code>",
        "非流形、射線與離散姿態檢查分欄，實體試鎖欄空白"
      ],
      "pitfalls": [
        {
          "title": "有限檢查不能證明完整旋入",
          "text": "局部射線與離散旋轉姿態不涵蓋全部連續裝配路徑；實體試鎖及合格值仍留空。"
        }
      ],
      "locate": "先依本章 11-15 的逐步實拍操作，保留原檔；現在只做本檢查點。",
      "figures": [
        {
          "path": "evidence/08/2026-10-28-side-cap-relief-inspect-v001/RELV-02-interior.png",
          "sha256": "032da2ea8dd60433c1e6a9f1e92d4832d7e1b442c0cf7f95228ca61fd7726edf",
          "size": [
            1494,
            1019
          ],
          "caption": "帽內腔可見內牙和近口端的退刀區，Item5.5／15.4／15.4mm；不是實體試鎖。",
          "marks": [
            {
              "n": 1,
              "box": [
                478,
                201,
                350,
                216
              ],
              "label": "內牙與退刀"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ]
};
