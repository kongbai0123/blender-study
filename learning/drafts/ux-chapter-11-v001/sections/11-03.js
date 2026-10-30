window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-03"] = {
  "id": "11-03",
  "title": "盲孔柱草案（觀察示範）",
  "keyPoint": "分開查看盲孔柱外框、孔深與底厚。",
  "glossary": [
    {
      "term": "對頂",
      "label": "對頂",
      "text": "量到多邊形相對頂點的距離。"
    },
    {
      "term": "對邊",
      "label": "對邊",
      "text": "量到相對平邊的距離。"
    },
    {
      "term": "孔深",
      "label": "孔深",
      "text": "孔口到孔底的軸向距離。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-boss-draft-observe",
      "title": "辨識盲孔柱",
      "lead": "獨立 Blender；Object Mode，作用中為 Boss_Blind_Polygon32，原盒 Body_Reference 隱藏。 辨識盲孔柱。",
      "actions": [
        "觀察柱體、上方孔口與右側外框尺寸。"
      ],
      "checks": [
        "視窗可辨獨立柱與上方孔口",
        "Item的Dimensions為<code>8</code>×<code>8</code>×<code>8 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "這不是手工建柱示範",
          "text": "本柱由程式建立，原生GUI只做觀察、保存與重開；柱與原盒尚未接合。"
        }
      ],
      "locate": "獨立 Blender；Object Mode，作用中為 Boss_Blind_Polygon32，原盒 Body_Reference 隱藏。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/08-04-01-boss-draft.png",
          "sha256": "73f87e8383b44db72ef06401537a653f74b742d0b413f3a4dcc4916a534787cf",
          "size": [
            1494,
            1019
          ],
          "caption": "獨立盲孔柱，孔口和孔壁可見但孔底被遮；Item8／8／8mm、Scale1。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "柱體外框"
            },
            {
              "n": 2,
              "box": [
                503,
                265,
                220,
                198
              ],
              "label": "孔口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/demo-files/u08_blind_boss_draft_v001.blend",
          "label": "獨立盲孔柱示範場景 v001"
        },
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/boss-draft-verification-v002.json",
          "label": "盲孔柱草案：操作方式及網格讀值摘要"
        },
        {
          "path": "journal/2026-10-27-boss-polygon-correction-v001.md",
          "label": "對邊距更正"
        }
      ]
    },
    {
      "stepId": "ch11-boss-draft-diameter",
      "title": "分清對頂與對邊",
      "lead": "對頂尺寸使用網格讀值；對邊距使用理想正32邊形公式，不當成實際投影量測。 分清對頂與對邊。",
      "actions": [
        "對照摘要中的外徑與孔徑對頂值，分別乘以 cos(π／<code>32</code>) 推算理想對邊距。"
      ],
      "checks": [
        "讀值表分列外／孔對頂<code>8</code>／<code>4 mm</code>",
        "理想<code>32</code>邊形計算的對邊約<code>7.9615</code>／<code>3.9807 mm</code>另列"
      ],
      "pitfalls": [],
      "locate": "對頂尺寸使用網格讀值；對邊距使用理想正32邊形公式，不當成實際投影量測。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/08-04-03-reopened.png",
          "sha256": "98a98a08f6e3f0e72ca315d7ef7701182ae3203038eeafa27870c3c3dac82c66",
          "size": [
            1494,
            1019
          ],
          "caption": "重開後獨立柱仍8／8／8mm；孔底不可見，不能從本圖確認7mm孔深及1mm底厚。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "重開外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-27-boss-polygon-correction-v001.md",
          "label": "對邊距更正"
        }
      ]
    },
    {
      "stepId": "ch11-boss-draft-depth",
      "title": "讀取孔深與底厚",
      "lead": "讀取孔深與底厚。",
      "actions": [
        "對照網格讀回的孔底Z、孔口Z與柱底Z，分別相減推得孔深與底厚。"
      ],
      "checks": [
        "座標計算列出孔深<code>7</code>、底厚<code>1 mm</code>",
        "Non Manifold檢查讀值為<code>0</code>"
      ],
      "pitfalls": [],
      "locate": "摘要 reopened 網格 Z 邊界讀值：孔Z1～8 mm、外框Z0～8 mm。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/08-04-03-reopened.png",
          "sha256": "98a98a08f6e3f0e72ca315d7ef7701182ae3203038eeafa27870c3c3dac82c66",
          "size": [
            1494,
            1019
          ],
          "caption": "重開後獨立柱仍8／8／8mm；孔底不可見，不能從本圖確認7mm孔深及1mm底厚。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "重開外框"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-27-boss-polygon-correction-v001.md",
          "label": "對邊距更正"
        }
      ]
    },
    {
      "stepId": "ch11-boss-draft-save",
      "title": "另存並重開",
      "lead": "File › Save As／Open；檔案路徑及名稱程式填入、確認與視角使用GUI原生事件。 另存並重開。",
      "actions": [
        "觀察示範保存與重開的原圖，再對照三組各七項網格檢查。"
      ],
      "checks": [
        "另存與重開原圖對應同一柱體版本",
        "摘要保存前、保存後、重開後各有<code>7</code>項檢查結果"
      ],
      "pitfalls": [],
      "locate": "File › Save As／Open；檔案路徑及名稱程式填入、確認與視角使用GUI原生事件。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-boss-draft-v002/08-04-02-saved.png",
          "sha256": "2d26b28a85c10822c74620625540115057f3bd66cbc615111ca0577a1f6962f1",
          "size": [
            1494,
            1019
          ],
          "caption": "底部Saved as u08_blind_boss_draft_v001.blend，獨立柱外框8／8／8mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                595,
                995,
                289,
                23
              ],
              "label": "柱體存檔"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-27-boss-polygon-correction-v001.md",
          "label": "對邊距更正"
        }
      ]
    }
  ]
};
