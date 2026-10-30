window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["03-11"] = {
  "id": "03-11",
  "title": "打開頂面",
  "keyPoint": "只選頂面並刪除，留下開口外殼。",
  "glossary": [
    {
      "term": "Faces",
      "label": "Faces",
      "text": "本步刪除選單的面選項，保留其餘網格。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch03-04-04-01",
      "title": "進 Edit Mode 面選取",
      "lead": "3D Viewport 進 Edit Mode 面選取。",
      "actions": [
        "滑鼠在 3D Viewport 內按 <kbd>Tab</kbd> 進 Edit Mode，再按 <kbd>3</kbd> 切換到面選取。"
      ],
      "checks": [
        "模式選單顯示 Edit Mode",
        "面選取按鈕反白"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Tab</kbd> 是切換，不是固定設成某模式；到達目標模式就停。"
        },
        {
          "title": "操作提醒",
          "text": "主鍵盤 <code>3</code> 是本次 Emulate Numpad 關閉時的面選取；Numpad <code>3</code> 是右視圖。若已改鍵位或開 Emulate Numpad，改用面選取按鈕確認。"
        }
      ],
      "locate": "3D Viewport",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-04-01-edit-face.png",
          "sha256": "b167ee7f67848ec9f5604c3ebbd7758efefa5d876da392420b4ec01962b772a3",
          "size": [
            1494,
            1019
          ],
          "caption": "Edit Mode已開，面選取按鈕反白；此時所有面仍被選中。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                27,
                95,
                23
              ],
              "label": "編輯模式"
            },
            {
              "n": 2,
              "box": [
                192,
                27,
                21,
                23
              ],
              "label": "面選取"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-04-04-02",
      "title": "只選頂面",
      "lead": "Select › None，再點頂面 只選頂面。",
      "actions": [
        "Select › None（<kbd>Alt</kbd>+<kbd>A</kbd>）取消全選，再只點盒子頂面。"
      ],
      "checks": [
        "只有頂面反白",
        "側面與底面未被同時選取"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "Object Mode 的 <kbd>Alt</kbd>+<kbd>A</kbd> 是取消物件選取；不能把兩種模式的選取狀態混用。"
        }
      ],
      "locate": "Select › None，再點頂面",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-04-02-top-selected.png",
          "sha256": "059e3078c132003c5c89e88c0f251eaf12140f897657c3b3f6c7eaef3e45037c",
          "size": [
            1494,
            1019
          ],
          "caption": "取消全選後只選頂面；Local Median Z為15 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                440,
                322,
                401,
                173
              ],
              "label": "只選頂面"
            },
            {
              "n": 2,
              "box": [
                962,
                170,
                227,
                23
              ],
              "label": "頂面Z15"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch03-04-04-03",
      "title": "刪除頂面",
      "lead": "Mesh › Delete › Faces 刪除頂面。",
      "actions": [
        "Mesh › Delete › Faces（X › Faces）。"
      ],
      "checks": [
        "原頂面已消失，盒子上方開口",
        "其餘側面與底面保留"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "X 不是直接刪 Faces；Object Mode 的 X 會刪整件。"
        }
      ],
      "locate": "Mesh › Delete › Faces",
      "figures": [
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-04-03-delete-menu.png",
          "sha256": "f95ff212f0ff72fcac2d83808c70ec518f0ded0dd7130dc6c0fa5e2ee81a0435",
          "size": [
            1494,
            1019
          ],
          "caption": "Mesh › Delete子選單中Faces反白，背景頂面仍被選中。",
          "marks": [
            {
              "n": 1,
              "box": [
                529,
                563,
                179,
                22
              ],
              "label": "刪除面"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/04/2026-10-22-lesson04-demo-v001/04-04-04-opened.png",
          "sha256": "0e66282d00891878721b3e69dfb88a80fe95a03aad6440c20d1d9360b824803e",
          "size": [
            1494,
            1019
          ],
          "caption": "刪除後上方開口，側面與底面保留；尚未增加壁厚。",
          "marks": [
            {
              "n": 1,
              "box": [
                439,
                321,
                405,
                177
              ],
              "label": "頂面已移除"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
