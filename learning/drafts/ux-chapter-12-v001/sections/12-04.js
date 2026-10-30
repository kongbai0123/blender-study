window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["12-04"] = {
  "id": "12-04",
  "title": "總組裝",
  "keyPoint": "按同一分支核對零件、場景與匯出版本。",
  "glossary": [
    {
      "term": "分支",
      "label": "分支",
      "text": "固定環唇、燕尾、卡扣或五金等不同配合方案，不能任意混裝。"
    }
  ],
  "scope": "本節以計算或紀錄表練習為主；未取得的實體列印、量測與試配結果保持空白。",
  "steps": [
    {
      "stepId": "ch12-09-03-01",
      "title": "組裝所有零件",
      "lead": "組裝 組裝所有零件。",
      "actions": [
        "複製組裝與版本關聯範本，先選定同一分支及對應零件。",
        "取得相容實物後依選定設計試組，記日期與觀察；若尚未印製則留空。"
      ],
      "checks": [
        "組裝表明列採用的同一配合分支與零件版本",
        "未取得實物時開合、鎖附、損傷觀察欄空白"
      ],
      "pitfalls": [],
      "locate": "組裝",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/engineering-assembly-trace-v001.json",
          "label": "零件版本與組裝空白紀錄範本"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    },
    {
      "stepId": "ch12-09-03-02",
      "title": "核對檔案關聯",
      "lead": "檔案紀錄 核對檔案關聯。",
      "actions": [
        "在空白版本關聯表記場景及各匯出檔案路徑與 SHA-<code>256</code>。",
        "在版本紀錄核對每個 export 或 render 的來源 .blend，內容變更後另存並重新輸出。"
      ],
      "checks": [
        "版本表每個export或render指向對應blend",
        "尚未產生的檔案不填路徑或SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "檔案紀錄",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "journal/templates/engineering-assembly-trace-v001.json",
          "label": "零件與版本關聯空白紀錄範本"
        },
        {
          "path": "evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json",
          "label": "隔離假專案的場景與合成 fixture 關聯紀錄"
        }
      ],
      "figureNote": "本步是紀錄表、公式或現場方法；不以Blender畫面代替實際紀錄。"
    }
  ]
};
