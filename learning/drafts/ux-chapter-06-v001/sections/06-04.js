window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["06-04"] = {
  "id": "06-04",
  "title": "列印原盒並量測",
  "keyPoint": "量測原盒各處，記下名義與實測差值。",
  "glossary": [
    {
      "term": "差值",
      "label": "差值",
      "text": "本紀錄以實測減去名義尺寸計算。"
    },
    {
      "term": "壁厚",
      "label": "壁厚",
      "text": "盒內外表面之間的厚度。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch06-04-08-01",
      "title": "列印原盒",
      "lead": "印表機 列印原盒。",
      "actions": [
        "用 <code>06</code>-<code>01</code> 匯出的 <code>u04_box_v001.stl</code> 列印，列印條件與試片相同並記在紀錄表。"
      ],
      "checks": [
        "紀錄表關聯 <code>u04_box_v001.stl</code> 及列印條件",
        "實際取得原盒後才填列印日期與結果"
      ],
      "pitfalls": [],
      "locate": "印表機",
      "figures": [],
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
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch06-04-08-02",
      "title": "量測尺寸",
      "lead": "卡尺 量測尺寸。",
      "actions": [
        "量外長寬高、內腔、壁厚，各量 <code>2</code>–<code>3</code> 處。"
      ],
      "checks": [
        "量測表列外長寬高、內腔與壁厚",
        "每項預留<code>2</code>～<code>3</code>處讀值，未量測留空"
      ],
      "pitfalls": [],
      "locate": "卡尺",
      "figures": [],
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
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch06-04-08-03",
      "title": "記錄差值",
      "lead": "筆記 記錄差值。",
      "actions": [
        "記下名義尺寸、實測值、差值與列印條件。"
      ],
      "checks": [
        "名義、各次實測、差值與條件各有獨立欄",
        "尚無實測時，差值與合格判定仍空白"
      ],
      "pitfalls": [],
      "locate": "筆記",
      "figures": [],
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
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
