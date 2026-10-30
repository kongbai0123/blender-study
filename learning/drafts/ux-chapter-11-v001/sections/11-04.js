window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-04"] = {
  "id": "11-04",
  "title": "外螺紋",
  "keyPoint": "核對外牙參數與轉網格後版本。",
  "glossary": [
    {
      "term": "轉換",
      "label": "轉換",
      "text": "把修改器計算結果變成網格；之後不能再從原參數連動。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-08-02-01",
      "title": "選定路線與參數",
      "lead": "選定路線與參數。",
      "actions": [
        "將用途、P、n、l、軸向、徑向與直徑差分欄記錄；未選定值留空，再對照實際檔案及限制。"
      ],
      "checks": [
        "參數表分列P、n、l與用途",
        "軸向、徑向、直徑差各有獨立欄"
      ],
      "pitfalls": [],
      "locate": "牙型與規格草案",
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
      "stepId": "ch11-08-02-02",
      "title": "核對手工輪廓與外牙",
      "lead": "先依 11-13／11-14 保留輪廓與版本；Convert Mesh 之後修改器不再存在，不能在最終檔直接讀取它。 核對手工輪廓與外牙。",
      "actions": [
        "轉換為網格前，在 Screw 修改器或自己保存的當時紀錄核對 Z 軸、<code>360°</code>、每圈 <code>1 mm</code>、<code>4</code> 圈及 <code>32</code> 段；也可查閱 <code>11</code>-<code>14</code> 第 <code>2</code> 步的示範紀錄。",
        "轉換後另存並重開，核對自己的外牙外框與限制；示範名義外框約 <code>12</code> × <code>12</code> × <code>4.8 mm</code>。"
      ],
      "checks": [
        "轉換前紀錄列Z軸、<code>360°</code>、每圈<code>1 mm</code>、<code>4</code>圈與<code>32</code>段",
        "轉網格重開後外框約<code>12</code>×<code>12</code>×<code>4.8 mm</code>，原Screw參數須查轉換前紀錄"
      ],
      "pitfalls": [],
      "locate": "先依 11-13／11-14 保留輪廓與版本；Convert Mesh 之後修改器不再存在，不能在最終檔直接讀取它。",
      "figures": [
        {
          "path": "evidence/08/2026-10-28-external-thread-from-hand-profile-gui-v001/XTH-14-reopened.png",
          "sha256": "88b1d0be726242abea6cc8cfc144ef95d4fc20c6879a225b40cb6aa72303a147",
          "size": [
            1494,
            1019
          ],
          "caption": "重開Thread_Core外牙，Item12／12／4.8mm、Scale1；Screw已轉換不在修改器清單。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "外牙外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ]
};
