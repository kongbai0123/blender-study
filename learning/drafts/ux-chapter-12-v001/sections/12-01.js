window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["12-01"] = {
  "id": "12-01",
  "title": "尺寸鏈",
  "keyPoint": "從外寬與壁厚追算盒口、唇寬和總差。",
  "glossary": [
    {
      "term": "尺寸鏈",
      "label": "尺寸鏈",
      "text": "把互相影響的尺寸列成可追溯的關係式。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch12-dimension-chain",
      "title": "從尺寸鏈查設計變更",
      "lead": "保留模型來源、名義尺寸、試驗值與實測的分欄 從尺寸鏈查設計變更。",
      "actions": [
        "分欄寫出外寬、側壁、盒口內寬、唇外寬與同方向總間隙。",
        "計算內寬＝外寬<code>-2</code>×側壁；唇外＝內寬−總間隙。"
      ],
      "checks": [
        "尺寸鏈表列外寬、側壁、盒口內寬、唇外寬",
        "公式分列內寬＝外寬<code>-2</code>×壁、唇外＝內寬−總差"
      ],
      "pitfalls": [],
      "locate": "保留模型來源、名義尺寸、試驗值與實測的分欄",
      "figures": [],
      "keys": [],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
