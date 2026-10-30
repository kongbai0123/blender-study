window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["02-02"] = {
  "id": "02-02",
  "title": "列印條件與量具",
  "keyPoint": "記下已知製程條件，確認量具與零點。",
  "glossary": [
    {
      "term": "解析度",
      "label": "解析度",
      "text": "量具能顯示的最小刻度，不等於量測準確度。"
    },
    {
      "term": "量程",
      "label": "量程",
      "text": "量具可量測的尺寸範圍。"
    },
    {
      "term": "線寬",
      "label": "線寬",
      "text": "切片中規劃的擠出線寬，不能只由噴嘴直徑推定。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch02-04-01-01",
      "title": "記下列印條件",
      "lead": "教學頁「卡關與觀察筆記」 記下列印條件。",
      "actions": [
        "在空白條件欄寫下已知的印表機、材料、噴嘴、線寬、層高、切片版本與預定方向；未知保留空白。",
        "將來源場景與STL的版本／SHA一併列入；後續變更條件時建立新紀錄。"
      ],
      "checks": [
        "條件表列出機型、材料、噴嘴、線寬、層高、方向與切片版本",
        "已知噴嘴記 <code>0.4 mm</code>，其他未取得的條件標待定"
      ],
      "pitfalls": [],
      "locate": "教學頁「卡關與觀察筆記」",
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
      "stepId": "ch02-04-01-02",
      "title": "確認量具",
      "lead": "量測工具 確認量具。",
      "actions": [
        "確認可取得的量具及其量程、解析度和檢查狀態，依量具手冊核對零點。",
        "記錄目前有／沒有的工具；缺少量具時保留測量欄，不估填數值。"
      ],
      "checks": [
        "量具表列出型號、量程與解析度，未知則標待定",
        "零點檢查結果只在實際檢查後填入"
      ],
      "pitfalls": [],
      "locate": "量測工具",
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
