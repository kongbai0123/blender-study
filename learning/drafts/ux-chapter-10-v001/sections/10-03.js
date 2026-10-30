window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["10-03"] = {
  "id": "10-03",
  "title": "列印方向與 Overhang",
  "keyPoint": "比較候選落床方向與 Overhang 朝下面。",
  "glossary": [
    {
      "term": "Overhang",
      "label": "Overhang",
      "text": "Mesh Analysis的懸空角度顯示項目。"
    },
    {
      "term": "Mesh Analysis",
      "label": "Mesh Analysis",
      "text": "Edit Mode中用顏色顯示網格分析結果的工具。"
    },
    {
      "term": "X-Ray",
      "label": "X-Ray",
      "text": "透視選取顯示，本次分析時關閉。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch10-07-03-01",
      "title": "比較落床姿態",
      "lead": "07-02草案副本 · Object Mode 比較落床姿態。",
      "actions": [
        "比較四種落床姿態：Body原向與繞Y90°側放；Lid原向與繞X180°翻面。只用R／G操作，保留Scale1，不套用旋轉。"
      ],
      "checks": [
        "對照四姿態：盒原向／Y90°、蓋原向／X180°",
        "各候選落床且Scale1，旋轉未套用"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "這些仍是方向／支撐候選，不由轉向推定可列印或合格；不要用 <kbd>Ctrl</kbd>+<kbd>A</kbd> 套用旋轉。"
        }
      ],
      "locate": "07-02草案副本 · Object Mode",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-overhang-demo-v001/07-03-06-body_candidate-analysis.png",
          "sha256": "c03a6f17d0432d03b9790801f6a68e473a5dc3eb095bca11259c50af6b6940e5",
          "size": [
            1494,
            1019
          ],
          "caption": "側放盒體的Mesh Analysis紅色出現在腔內壁、外面及臂下方。顏色不單獨代表可製造性。",
          "marks": [
            {
              "n": 1,
              "box": [
                466,
                178,
                281,
                141
              ],
              "label": "內壁紅色面"
            },
            {
              "n": 2,
              "box": [
                438,
                654,
                361,
                111
              ],
              "label": "另一紅色面"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-overhang-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-03-02",
      "title": "開啟 Overhang 檢查",
      "lead": "Edit Mode › Mesh Edit Mode Overlays › Mesh Analysis 開啟 Overhang 檢查。",
      "actions": [
        "Solid、X-Ray關閉；啟用Mesh Analysis，核對Overhang／−Z／Minimum0°／Maximum45°，再轉視角觀察真實色帶。"
      ],
      "checks": [
        "Mesh Analysis 為Overhang、−Z、<code>0°</code>～<code>45°</code>",
        "Solid且X-Ray關閉時可見朝下面色帶"
      ],
      "pitfalls": [
        {
          "title": "紅色不等於支撐結論",
          "text": "床接觸面也可能顯紅。需分開檢查非床接觸朝下面、支撐可移除性與切片條件。"
        },
        {
          "title": "操作提醒",
          "text": "<kbd>Tab</kbd> 是切換，不是固定設成某模式；到達目標模式就停。"
        }
      ],
      "locate": "Edit Mode › Mesh Edit Mode Overlays › Mesh Analysis",
      "figures": [
        {
          "path": "evidence/01/2026-10-27-shortcuts-demo-v001/01-05-01-tab-edit.png",
          "sha256": "ef3c94f920b0aa08cc349b691074ef4b0b112b02ad528b91d11e7414a0ebb7e6",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit Mode的頂點全選，Local Median為0；這是另一場景的模式入口參照。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                28,
                95,
                21
              ],
              "label": "編輯模式"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-overhang-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-03-03",
      "title": "比較朝下面並另存",
      "lead": "方向比較表 · 另存與Open重開 比較朝下面並另存。",
      "actions": [
        "對照床接觸、非床接觸朝下面的polygon數與面積；檢查翻面上蓋的高處凸緣。候選各自落床、分開<code>35mm</code>後另存新版本並重開。"
      ],
      "checks": [
        "比較表分列床接觸與非床接觸朝下面積",
        "候選分隔<code>35 mm</code>後另存，方向與支撐仍標候選"
      ],
      "pitfalls": [],
      "locate": "方向比較表 · 另存與Open重開",
      "figures": [
        {
          "path": "evidence/01/2026-10-22-lesson01-demo-v001/01-04-01-file-menu.png",
          "sha256": "34fb7b908b2195873b9568a38b8aa54bdef0fd7ce29eb0e74570486259fd6768",
          "size": [
            1494,
            1019
          ],
          "caption": "File選單中可見Save As與Shift Ctrl S鍵標。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                153,
                176,
                22
              ],
              "label": "另存入口"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-overhang-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
