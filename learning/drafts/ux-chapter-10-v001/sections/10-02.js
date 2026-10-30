window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["10-02"] = {
  "id": "10-02",
  "title": "卡扣建模",
  "keyPoint": "建立懸臂、外鉤與對件凸緣草案。",
  "glossary": [
    {
      "term": "anchor",
      "label": "anchor",
      "text": "卡扣臂連接盒體的根部錨座。"
    },
    {
      "term": "OFFSET",
      "label": "OFFSET",
      "text": "本次Bevel輸入的偏移量模式。"
    },
    {
      "term": "Bevel",
      "label": "Bevel",
      "text": "在指定邊上建立倒角或分段過渡的操作。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch10-07-02-01",
      "title": "建立懸臂與外鉤",
      "lead": "原盒與外掛懸臂 · Edit Mode 建立懸臂與外鉤。",
      "actions": [
        "在既有SnapTool的Edit Mode，選anchor頂面，按 <kbd>I</kbd> 輸入 <code>1.5mm</code>，形成直臂截面。",
        "保持中央面選取，按 <kbd>E</kbd> 輸入 <code>19mm</code>，確認後再擠出 <code>2mm</code>。",
        "選最高 <code>2mm</code> 的外側面，按 <kbd>E</kbd> 輸入 <code>1.2mm</code>，沿面法向形成外鉤。"
      ],
      "checks": [
        "外觀可辨根部錨座、直臂與外鉤",
        "讀值分列直臂寬<code>6</code>、厚<code>1.6</code>、幾何L19與全直臂<code>21 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "起始幾何",
          "text": "本序列接續已有的anchor工具。先由來源操作說明取得同分支起點；本步不把程式預建的基塊冒稱為手工建立。"
        }
      ],
      "locate": "原盒與外掛懸臂 · Edit Mode",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-04-beam-inset.png",
          "sha256": "a5d7b5fedbdc7fba842bf9b1048159ecf781a02c1858d3cfd4549aab24e21323",
          "size": [
            1494,
            1019
          ],
          "caption": "根部基塊頂面內插後，中央長方形面反白。",
          "tab": "操作位置",
          "marks": [
            {
              "n": 1,
              "box": [
                435,
                425,
                357,
                98
              ],
              "label": "直臂截面"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-05-beam-extruded.png",
          "sha256": "b5c5733263019f34bf999fd9b254d397986b82af251d7015bb065180fab78c6e",
          "size": [
            1494,
            1019
          ],
          "caption": "直臂擠出後頂面反白；Local Median Z22.5 mm是局部座標，並非世界臂頂Z。",
          "tab": "過程狀態",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                170,
                227,
                23
              ],
              "label": "局部頂面座標"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-06-hook-extruded.png",
          "sha256": "da5c5212f2d879e6cff41e0dc5baa148b84101b7a8b95d0f9835407b46648202",
          "size": [
            1494,
            1019
          ],
          "caption": "外鉤面在正視圖反白；Y向突出深度不能直接從這張正視圖量得。",
          "tab": "核對結果",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                151,
                227,
                43
              ],
              "label": "局部面座標"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-snap-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-02-02",
      "title": "根部倒角與導入斜面",
      "lead": "真正的臂根凹邊 · Bevel 根部倒角與導入斜面。",
      "actions": [
        "在Edit Mode選鉤外頂的一條X向邊，<kbd>Ctrl</kbd>+<kbd>B</kbd> 設 <code>0.8</code>、<code>1</code> 段，形成導入斜面。",
        "用X-Ray只選臂腳與anchor頂面的兩條凹根部邊，<kbd>Ctrl</kbd>+<kbd>B</kbd> 設 <code>0.6</code>、<code>3</code> 段。",
        "數值用純半形數字，核對Bevel的OFFSET模式；返回Object Mode查看根部過渡。"
      ],
      "checks": [
        "只對兩條臂根凹邊做Bevel",
        "本次OFFSET0.6、<code>3</code>段，鉤端另有導入斜面"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "倒角量是草案，不能由 Bevel 成功推定強度改善或合格。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "真正的臂根凹邊 · Bevel",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-08-hook-bevel.png",
          "sha256": "7b2a90308506aeb2af3818c6a086d868e4d2a88bccec590bf2eeff21f23e07a2",
          "size": [
            1494,
            1019
          ],
          "caption": "鉤外頂邊倒角後形成導入斜面；左下顯示Bevel。",
          "tab": "操作位置",
          "marks": [
            {
              "n": 1,
              "box": [
                536,
                246,
                144,
                47
              ],
              "label": "鉤端導入斜面"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-09-root-edges.png",
          "sha256": "e1f2fe071d2110f727fc930a108e4e48725099a2b88c76de05140a50996a2ccb",
          "size": [
            1494,
            1019
          ],
          "caption": "X-Ray中臂腳根部邊反白；選取邊數另查操作讀值。",
          "tab": "過程狀態",
          "marks": [
            {
              "n": 1,
              "box": [
                538,
                641,
                149,
                39
              ],
              "label": "臂根選取邊"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-10-root-bevel.png",
          "sha256": "d865ea78ef61836a85a4763fb1f21565906123191d06a1776d7a20c7ead756f3",
          "size": [
            1494,
            1019
          ],
          "caption": "臂根倒角後出現分段過渡面；0.6 mm與3段需對照原生操作讀值。",
          "tab": "核對結果",
          "marks": [
            {
              "n": 1,
              "box": [
                528,
                616,
                180,
                59
              ],
              "label": "根部過渡面"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-snap-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch10-07-02-03",
      "title": "檢查上蓋凸緣並另存",
      "lead": "新上蓋與局部承接凸緣 · 靜態擺位 檢查上蓋凸緣並另存。",
      "actions": [
        "查看操作<code>17</code>／<code>19</code>的實際內側凸緣、<code>21</code>的暫抬<code>12mm</code>展示及<code>22</code>的回位讀值；完成後另存、重開。"
      ],
      "checks": [
        "暫抬上蓋時可見內側凸緣",
        "回位後保存新版本，讀值另列蓋板<code>60</code>×<code>46</code>×<code>2</code>、整高約<code>7 mm</code>"
      ],
      "pitfalls": [],
      "locate": "新上蓋與局部承接凸緣 · 靜態擺位",
      "figures": [
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-17-flange-tool.png",
          "sha256": "fb8ec958f4c9067afa5a94d69a4f2cc2ff961b14b8f66ba4424d567ab9fc8a23",
          "size": [
            1494,
            1019
          ],
          "caption": "FlangeTool可見承接凸緣，Dimensions10×2.7×5.2 mm。",
          "tab": "操作位置",
          "marks": [
            {
              "n": 1,
              "box": [
                336,
                536,
                556,
                132
              ],
              "label": "承接凸緣"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "凸緣工具外框"
            }
          ]
        },
        {
          "path": "evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-19-lid-applied.png",
          "sha256": "6675dba6fd84226747e36d5fa56dba5719d35239ba6df889f04193e79f2dc0a6",
          "size": [
            1494,
            1019
          ],
          "caption": "Union後凸緣與蓋板合併；Lid外框60×46×7 mm。",
          "tab": "過程狀態",
          "marks": [
            {
              "n": 1,
              "box": [
                611,
                548,
                103,
                64
              ],
              "label": "蓋下凸緣"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "含凸緣蓋外框"
            }
          ]
        },
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
          "tab": "暫抬檢視"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-25-lesson07-snap-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ]
};
