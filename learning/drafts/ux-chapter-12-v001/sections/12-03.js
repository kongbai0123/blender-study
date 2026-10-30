window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["12-03"] = {
  "id": "12-03",
  "title": "設計補償值",
  "keyPoint": "有實測後才計算補償，保留重印驗證。",
  "glossary": [
    {
      "term": "補償",
      "label": "補償",
      "text": "依實測差值提出的尺寸調整草案，需再驗證。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch12-09-02-01",
      "title": "寫出補償值",
      "lead": "補償值 寫出補償值。",
      "actions": [
        "複製補償空白範本到工作區，記下對應實測來源與製程條件。",
        "有實測後依實測−名義記錄差值，再記補償草案；切片器和模型補償避免重複。"
      ],
      "checks": [
        "補償表分列實測、名義、差值與補償草案",
        "無實測時補償、重印結果與合格欄均空白"
      ],
      "pitfalls": [],
      "locate": "補償值",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/engineering-compensation-v001.json",
          "label": "製程補償空白紀錄範本"
        },
        {
          "path": "journal/templates/engineering-measurement-fit-v001.json",
          "label": "實體量測與試配空白紀錄範本"
        }
      ],
      "figureNote": "本步核對教學頁的檔案版本表；沒有登記畫面實拍，請以自己的實際紀錄為準。"
    }
  ]
};
