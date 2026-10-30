window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["02-03"] = {
  "id": "02-03",
  "title": "配合名詞與紀錄表",
  "keyPoint": "建立六孔試驗紀錄，分開設計值與實測值。",
  "glossary": [
    {
      "term": "CSV",
      "label": "CSV",
      "text": "以欄位分隔保存的表格文字檔。"
    },
    {
      "term": "實測值",
      "label": "實測值",
      "text": "實際使用量具取得並記錄的尺寸。"
    },
    {
      "term": "方軸",
      "label": "方軸",
      "text": "本練習插入方孔的方形插銷。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch02-05-01-01",
      "title": "寫下間隙公式",
      "lead": "筆記 寫下間隙公式。",
      "actions": [
        "寫下同方向的總間隙＝孔寬−軸寬，辨認設計值與實測值。",
        "對置中對稱的方孔／方軸，再寫單側＝總間隙÷<code>2</code>；非置中或法向關係另行處理。"
      ],
      "checks": [
        "筆記列出總間隙＝孔寬−軸寬",
        "另列單側＝總間隙÷<code>2</code>及置中對稱條件"
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
    },
    {
      "stepId": "ch02-05-01-02",
      "title": "準備自己的紀錄表",
      "lead": "紀錄表 準備自己的紀錄表。",
      "actions": [
        "開啟六孔名義設計 CSV；表中的量測、條件與手感欄尚未填。",
        "另存到自己的<code>05</code>工作區新版本，之後只在實際操作後填寫；保留教材原範本。"
      ],
      "checks": [
        "自己的 CSV 副本位於 workspaces/<code>05</code>",
        "設計孔寬有值，實測與試配欄保持空白"
      ],
      "pitfalls": [],
      "locate": "紀錄表",
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
