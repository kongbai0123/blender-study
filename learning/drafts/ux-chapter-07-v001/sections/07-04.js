window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["07-04"] = {
  "id": "07-04",
  "title": "內腔草圖與切割",
  "keyPoint": "定義內腔寬高與位置，再向內切割。",
  "glossary": [
    {
      "term": "Body.001 Sketch",
      "label": "Body.001 Sketch",
      "text": "本示範建立的內腔草圖名稱。"
    },
    {
      "term": "Auto Boolean",
      "label": "Auto Boolean",
      "text": "本次CAD拉伸時自動處理布林的選項。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch07-cavity-01",
      "title": "在頂面建立草圖",
      "lead": "Object Mode；Body 已選取；使用既有 60×40×30 mm 實心體副本。 在頂面建立草圖。",
      "actions": [
        "在 3D 視圖按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> 進入挑選工作平面；點頂面。"
      ],
      "checks": [
        "選頂面後進入 Body.001 Sketch",
        "工作平面位於本次盒體頂面"
      ],
      "pitfalls": [],
      "locate": "Object Mode；Body 已選取；使用既有 60×40×30 mm 實心體副本。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-01-opened-solid.png",
          "sha256": "5406efc2b7771d4e0fa0f47c30ed09b9b7d8a4fcf689d26c7bc8f570f96ce161",
          "size": [
            1494,
            1019
          ],
          "caption": "既有實心Body被選取，頂面可見，尚未開始新草圖。",
          "marks": [
            {
              "n": 1,
              "box": [
                615,
                300,
                339,
                355
              ],
              "label": "既有實心體"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-02-pick-workplane.png",
          "sha256": "ac251d8329661225e284e7b8b3a32b194e9a7f03c956c334af1a49cc242588ba",
          "size": [
            1494,
            1019
          ],
          "caption": "選工作平面工具已啟動；左上Origin Workplanes欄出現，底部Add Sketch；頂面尚未選。",
          "marks": [
            {
              "n": 1,
              "box": [
                615,
                350,
                274,
                115
              ],
              "label": "頂面目標"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-03-picked-top-face.png",
          "sha256": "dda9b4d3505070a0aadebbb9d0b42182a0ef08155494b96c637dc983f0099a84",
          "size": [
            1494,
            1019
          ],
          "caption": "頂面轉為正交視圖，標題Body.001 Sketch；尚未畫內矩形。",
          "marks": [
            {
              "n": 1,
              "box": [
                1016,
                27,
                100,
                23
              ],
              "label": "內腔草圖"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    },
    {
      "stepId": "ch07-cavity-02",
      "title": "畫近似內矩形",
      "lead": "Body.001 Sketch 活動、焦點在3D視圖。 畫近似內矩形。",
      "actions": [
        "按 <kbd>R</kbd>，在頂面內點選矩形兩個角點；按 <kbd>Esc</kbd> 結束工具。"
      ],
      "checks": [
        "頂面內出現近似矩形",
        "矩形尚未完成全部尺寸與定位約束"
      ],
      "pitfalls": [],
      "locate": "Body.001 Sketch 活動、焦點在3D視圖。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-04-rectangle.png",
          "sha256": "25e1fc86a9c56d363aed6ae06089bb4131af580e1a18b5f732e5be0d65e8b8f5",
          "size": [
            1494,
            1019
          ],
          "caption": "頂面內有近似矩形四邊及角點；沒有尺寸標註，不能從圖得準確寬高。",
          "marks": [
            {
              "n": 1,
              "box": [
                506,
                404,
                214,
                140
              ],
              "label": "近似矩形"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    },
    {
      "stepId": "ch07-cavity-03",
      "title": "標註內矩形長寬",
      "lead": "Body.001 Sketch 中的矩形，3D視圖。 標註內矩形長寬。",
      "actions": [
        "按 <kbd>D</kbd> 點選水平邊並輸入<code>56</code>，確認後結束工具。",
        "再按 <kbd>D</kbd> 點垂直邊輸入<code>36</code>並確認。"
      ],
      "checks": [
        "側欄可逐欄找到<code>56</code>、<code>36 mm</code>尺寸",
        "定位尚未完成，草圖仍有剩餘自由度"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body.001 Sketch 中的矩形，3D視圖。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-05-width.png",
          "sha256": "0a2265047c41858002083ce34eb07c4819006f7fb7c1f33e24c33ae84c0be45b",
          "size": [
            1494,
            1019
          ],
          "caption": "水平尺寸56.000mm清楚可見，tooltip遮住矩形中央，沒有其他尺寸欄位。",
          "marks": [
            {
              "n": 1,
              "box": [
                553,
                428,
                101,
                25
              ],
              "label": "寬度56mm"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-06-height.png",
          "sha256": "d88ff500de8747178aa41f9af1916094a5fc42f99fb8e350aabefcd5f277c1bb",
          "size": [
            1494,
            1019
          ],
          "caption": "垂直尺寸線已出現，但數字與56mm文字重疊；不能僅憑圖讀36或自由度。",
          "marks": [
            {
              "n": 1,
              "box": [
                552,
                427,
                104,
                27
              ],
              "label": "重疊標註"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    },
    {
      "stepId": "ch07-cavity-04",
      "title": "水平定位角點",
      "lead": "Body.001 Sketch，選取工具依本次畫面；頂面草圖原點是面中心。 水平定位角點。",
      "actions": [
        "按 <kbd>Alt</kbd>+<kbd>H</kbd>，依序選內矩形角點與草圖原點，放置標註並輸入<code>28</code>；確認後退出工具。"
      ],
      "checks": [
        "側欄新增水平定位<code>28 mm</code>",
        "垂直方向仍待下一步約束"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Body.001 Sketch，選取工具依本次畫面；頂面草圖原點是面中心。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/CENTER-01-horizontal.png",
          "sha256": "066160fddcd720b9cd70611c7a09f4a403c578768446265f88ce343780b165fa",
          "size": [
            1494,
            1019
          ],
          "caption": "多個尺寸文字重疊，同時可見定位線；28mm須依原讀值，圖不清楚。",
          "marks": [
            {
              "n": 1,
              "box": [
                552,
                427,
                104,
                27
              ],
              "label": "重疊標註"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    },
    {
      "stepId": "ch07-cavity-05",
      "title": "垂直定位角點",
      "lead": "仍在同一草圖，使用相同角點與頂面草圖原點。 垂直定位角點。",
      "actions": [
        "按 <kbd>Alt</kbd>+<kbd>V</kbd>，依序選角點與草圖原點，放置標註並輸入<code>18</code>；確認後退出工具。"
      ],
      "checks": [
        "側欄新增垂直定位<code>18 mm</code>",
        "求解後顯示 Fully defined"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "仍在同一草圖，使用相同角點與頂面草圖原點。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/CENTER-02-vertical.png",
          "sha256": "482f37a2ee471bb27bfce1225efbaf257c90dc21987e94839bba7faef69e3ab2",
          "size": [
            1494,
            1019
          ],
          "caption": "再加入垂直定位線，文字仍重疊；18mm與求解自由度需讀值佐證。",
          "marks": [
            {
              "n": 1,
              "box": [
                552,
                427,
                104,
                27
              ],
              "label": "重疊標註"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    },
    {
      "stepId": "ch07-cavity-06",
      "title": "拉伸切割體並核對",
      "lead": "內矩形草圖完成；本次場景 Unit Scale 0.001。 拉伸切割體並核對。",
      "actions": [
        "按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> 離開草圖，按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd> 啟動 Extrude。",
        "本次輸入 <code>-28</code> 並確認；觀察 Auto Boolean 勾選及結果。"
      ],
      "checks": [
        "拉伸輸入為<code>-28</code>且 Auto Boolean勾選",
        "確認後盒體外觀出現內腔凹陷"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "內矩形草圖完成；本次場景 Unit Scale 0.001。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-07-left-inner-sketch.png",
          "sha256": "e89d94e614a08a6e03dcc0865336bf440b7aae5248c91ce09949a9882c697d07",
          "size": [
            1494,
            1019
          ],
          "caption": "離開Body.001 Sketch後內矩形生成面橘框被選，頂面有Z-fighting條紋，尚未切割。",
          "marks": [
            {
              "n": 1,
              "box": [
                622,
                353,
                254,
                109
              ],
              "label": "生成平面"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-08-extrude-tool.png",
          "sha256": "79bda88daf039199a0c43bc24251e8edba8de9b482c818ec5105e0b4f9a9d2cc",
          "size": [
            1494,
            1019
          ],
          "caption": "左上Auto Boolean勾選、Extrude預覽；底部Offset -24.197，還沒有輸入最終-28。",
          "marks": [
            {
              "n": 1,
              "box": [
                5,
                55,
                112,
                21
              ],
              "label": "自動布林"
            },
            {
              "n": 2,
              "box": [
                310,
                999,
                109,
                18
              ],
              "label": "預覽偏移"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/LINEDIM-09-after-cut.png",
          "sha256": "db669724e3735b81cee3a670d6beff861ef10d55c45a73754c8e8090b1d49e0a",
          "size": [
            1494,
            1019
          ],
          "caption": "拉伸確認後外觀凹入，Body.001仍是作用中物件；圖片未顯示尺寸或封閉性結果。",
          "marks": [
            {
              "n": 1,
              "box": [
                617,
                351,
                272,
                239
              ],
              "label": "內凹外觀"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-cad-sketcher-cavity-center-constraints-probe-v001/center-constraints-fixed-probe-v001.json",
          "label": "固定尺寸內腔切割體探測摘要"
        }
      ]
    }
  ]
};
