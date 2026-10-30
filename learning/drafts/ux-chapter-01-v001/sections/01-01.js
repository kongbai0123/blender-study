window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-01"] = {
  "id": "01-01",
  "title": "開啟 Blender 並確認畫面",
  "keyPoint": "先辨認目前畫面，保留已有作品。",
  "glossary": [
    {
      "term": "Quick Setup",
      "label": "Quick Setup",
      "text": "第一次啟動時的設定卡片。"
    },
    {
      "term": "Splash",
      "label": "Splash",
      "text": "啟動時覆在編輯區上的歡迎卡片。"
    },
    {
      "term": "Default",
      "label": "Default",
      "text": "沒有卡片遮擋的預設場景。"
    },
    {
      "term": "Existing",
      "label": "Existing",
      "text": "已開啟既有模型或檔案的狀態。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch01-01-01-01",
      "title": "辨認目前畫面",
      "lead": "你自己的完整 Blender 視窗（保留標題列） 辨認目前畫面。",
      "actions": [
        "只辨認目前畫面：Quick Setup 有首次設定選項；Splash 有啟動卡片；Default 是未被卡片遮擋的預設場景；Existing 是已有模型或檔名的作品。"
      ],
      "checks": [
        "目前視窗可對照為 Quick Setup、Splash、Default 或 Existing",
        "畫面種類與尚未保存的作品已記在自己的觀察筆記"
      ],
      "pitfalls": [],
      "locate": "你自己的完整 Blender 視窗（保留標題列）",
      "figures": [
        {
          "path": "evidence/03/2026-10-28-edit-practice-gui-v001/EDIT-01-default.png",
          "sha256": "7fefffe3d6e72145c228a60b7ed5bce3e42e9525182a5ac42463cc5c00e3a3f4",
          "size": [
            1494,
            1019
          ],
          "caption": "預設場景中Cube被選取；右上是物件清單，右下是屬性編輯區。",
          "marks": [
            {
              "n": 1,
              "box": [
                553,
                407,
                131,
                144
              ],
              "label": "Cube"
            },
            {
              "n": 2,
              "box": [
                1280,
                91,
                113,
                63
              ],
              "label": "物件清單"
            },
            {
              "n": 3,
              "box": [
                1270,
                309,
                197,
                247
              ],
              "label": "物件屬性"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ]
};
