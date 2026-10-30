window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-01"] = {
  "id": "08-01",
  "title": "尺寸來源規劃",
  "keyPoint": "列出唯一尺寸來源，寫出內腔與唇邊公式。",
  "glossary": [
    {
      "term": "尺寸來源",
      "label": "尺寸來源",
      "text": "供其他尺寸取值的主尺寸或欄位。"
    },
    {
      "term": "主尺寸",
      "label": "主尺寸",
      "text": "供內腔與唇邊公式取用的盒長或盒寬。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch08-param-plan",
      "title": "安排單一尺寸來源",
      "lead": "安排單一尺寸來源。",
      "actions": [
        "先列出盒長、盒寬作為主尺寸，再列側壁、底厚、蓋厚、唇深及同方向的總間隙。",
        "寫出內腔＝外寬<code>-2</code>×側壁、唇外＝內腔−總間隙；未完成個人試配時 <code>0.4 mm</code> 僅是試驗值。"
      ],
      "checks": [
        "參數表分列盒長寬、壁厚、底厚、蓋厚、唇深與總差",
        "公式表有內腔＝外寬<code>-2</code>×側壁、唇外＝內腔−總間隙"
      ],
      "pitfalls": [],
      "locate": "另建副本；參數模型技術示範需另行核對",
      "figures": [],
      "keys": [],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
