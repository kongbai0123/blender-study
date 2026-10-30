window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["06-03"] = {
  "id": "06-03",
  "title": "列印試片並逐孔試配",
  "keyPoint": "用實際量測與逐孔試插選出候選間隙。",
  "glossary": [
    {
      "term": "切片",
      "label": "切片",
      "text": "把模型轉成列印路徑的製程準備。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch06-fit-01",
      "title": "切片並列印試片",
      "lead": "切片軟體 · 印表機 · 紀錄表 切片並列印試片。",
      "actions": [
        "把兩份 STL 拖進切片軟體，核對 <code>10</code> × <code>10</code> × <code>8</code> 與 <code>96</code> × <code>26</code> × <code>4 mm</code>，平放在列印床上。",
        "在紀錄表寫下印表機、材料、噴嘴、層高、切片軟體與擺放方向後列印。"
      ],
      "checks": [
        "尚無實物時，條件表與STL版本先備妥",
        "實際列印後才勾記取得插銷、孔板與日期"
      ],
      "pitfalls": [],
      "locate": "切片軟體 · 印表機 · 紀錄表",
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
        },
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch06-fit-02",
      "title": "量測插銷與六孔",
      "lead": "數位游標卡尺 · 紀錄表 量測插銷與六孔。",
      "actions": [
        "用卡尺量插銷 X、Y 各 <code>2</code>～<code>3</code> 處。",
        "量六個孔的 X、Y 寬度（依凹點數 <code>1</code>～<code>6</code> 辨認；看不清楚時依孔中心由 X <code>-35</code> 到 <code>+35</code> 的順序），填入紀錄表。"
      ],
      "checks": [
        "表格分列插銷與六孔的X、Y測量位置",
        "實測後才填各次讀值與孔減軸的總差"
      ],
      "pitfalls": [],
      "locate": "數位游標卡尺 · 紀錄表",
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
        },
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch06-fit-03",
      "title": "逐孔試插",
      "lead": "插銷 · 孔板 · 紀錄表 逐孔試插。",
      "actions": [
        "把插銷依序插入 <code>1</code>～<code>6</code> 點孔，每孔試 <code>2</code>～<code>3</code> 次，方向保持一致。",
        "記錄插不進、很緊、滑順或晃動。"
      ],
      "checks": [
        "每孔預留<code>2</code>～<code>3</code>次同方向試插欄",
        "實際試插後才填插不進、緊、滑順或晃動"
      ],
      "pitfalls": [],
      "locate": "插銷 · 孔板 · 紀錄表",
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
        },
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch06-fit-04",
      "title": "選定自己的總間隙",
      "lead": "紀錄表 選定自己的總間隙。",
      "actions": [
        "從試插結果選出你要的配合（例如能順利開合又不晃的那一孔），寫下它的設計總間隙、實測值與選擇理由。"
      ],
      "checks": [
        "候選選擇欄對應到孔號與製程條件",
        "尚未試配時，候選結果與理由保持空白"
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
        },
        {
          "path": "journal/2026-10-22-lesson05-export-demo-v003.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
