window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["05-02"] = {
  "id": "05-02",
  "title": "六孔試驗孔板",
  "keyPoint": "建立六種試驗孔寬與凹點，再做布林切割。",
  "glossary": [
    {
      "term": "Plate",
      "label": "Plate",
      "text": "六孔試驗孔板的物件名稱。"
    },
    {
      "term": "Cutters",
      "label": "Cutters",
      "text": "合併後用來開孔的切割工具物件。"
    },
    {
      "term": "Boolean",
      "label": "Boolean",
      "text": "把物件體積做聯集或差集等運算的修改器。"
    },
    {
      "term": "Difference",
      "label": "Difference",
      "text": "從目標物件扣除工具體積的布林模式。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch05-05-03-02",
      "title": "建立 Plate",
      "lead": "Object Mode · Cube 已選取 · N 側欄 Item 建立 Plate。",
      "actions": [
        "Dimensions 輸入 <code>96mm</code>、<code>26mm</code>、<code>4mm</code>，Object › Apply › Scale，按 <kbd>F2</kbd> 改名 Plate。",
        "按 <kbd>H</kbd> 暫時隱藏 Plate，方便做切割體。"
      ],
      "checks": [
        "Plate 尺寸為<code>96</code>×<code>26</code>×<code>4 mm</code>，Scale1",
        "H 後 Plate 暫時不在視窗中"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "<kbd>Ctrl</kbd>+<kbd>A</kbd> 只開選單，不直接套用 Scale；不能用它替代 Boolean／Solidify 修改器的 Apply。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Object Mode · Cube 已選取 · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-03-board.png",
          "sha256": "42d749d6442e623bceddcdeae942cb4c02730ea4abee896318c378836e628399",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Plate 已選取，尺寸 96×26×4 mm，Scale 三軸 1。",
          "marks": [
            {
              "n": 1,
              "box": [
                483,
                377,
                318,
                248
              ],
              "label": "示範孔板"
            },
            {
              "n": 2,
              "box": [
                963,
                318,
                228,
                142
              ],
              "label": "96 × 26 "
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-03",
      "title": "建立第 1 孔切割體",
      "lead": "Object Mode · N 側欄 Item 建立第 1 孔切割體。",
      "actions": [
        "Add › Mesh › Cube 新增方塊；原示範以 <kbd>S</kbd> X <code>5.05</code>、S Y <code>5.05</code>、S Z <code>4</code> 將 <code>2 mm</code> 預設方塊縮成 <code>10.1</code> × <code>10.1</code> × <code>8 mm</code>。",
        "用 G X <code>-35mm</code>、G Y <code>2mm</code> 移至中心 (<code>-35</code>, <code>2</code>, <code>0</code>) mm，從 N 側欄核對。"
      ],
      "checks": [
        "切割體尺寸<code>10.1</code>×<code>10.1</code>×<code>8 mm</code>，中心<code>-35</code>、<code>2</code>、<code>0 mm</code>",
        "筆記算出本孔名義總差<code>10.1</code>−<code>10</code>＝<code>0.1 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-04-cutter-1.png",
          "sha256": "a3f91c05485ffeda73bf50b40067db2091cda96ca45f8b6fe2610cc0864e67ec",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "第一切割體 Dimensions 10.1×10.1×8 mm，Location X -35、Y 2 mm，Plate 隱藏。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-04",
      "title": "新增第 2、3 孔切割體",
      "lead": "Object Mode · 上一個切割體已選取 新增第 2、3 孔切割體。",
      "actions": [
        "逐一 Add › Mesh › Cube 新增第 <code>2</code>、<code>3</code> 個方塊；示範將 <code>2 mm</code> 預設方塊以 <kbd>S</kbd> X、S Y 分別設 <code>5.1</code> 或 <code>5.15</code>，S Z <code>4</code>。",
        "以 <kbd>G</kbd> X 分別移至 <code>-21</code>、<code>-7 mm</code>、G Y <code>2mm</code>，核對寬 <code>10.2</code>／<code>10.3 mm</code>。"
      ],
      "checks": [
        "兩切割體寬為<code>10.2</code>、<code>10.3 mm</code>",
        "Location X為<code>-21</code>、<code>-7 mm</code>，Y各為<code>2 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode · 上一個切割體已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-05-cutter-2.png",
          "sha256": "b8710f95a8ed81ce359c41ada1be5d1f721904d373ccec99ec7c1f4b0993284e",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "第二切割體 Dimensions 10.2×10.2×8 mm，Location X -21、Y 2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-06-cutter-3.png",
          "sha256": "687671a796a6883b8ef8c16b039e55cde22aea4235b732261125e70d4b0ae63a",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "第三切割體 Dimensions 10.3×10.3×8 mm，Location X -7、Y 2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-05",
      "title": "新增第 4～6 孔切割體",
      "lead": "Object Mode · 第 3 孔切割體已選取 新增第 4～6 孔切割體。",
      "actions": [
        "逐一新增第 <code>4</code>～<code>6</code> 個 Cube，以 <kbd>S</kbd> X、S Y 分別設 <code>5.2</code>、<code>5.25</code>、<code>5.3</code>，S Z <code>4</code>。",
        "以 <kbd>G</kbd> X 分別移至 <code>7</code>、<code>21</code>、<code>35 mm</code>，G Y <code>2mm</code>；核對寬 <code>10.4</code>、<code>10.5</code>、<code>10.6 mm</code>。"
      ],
      "checks": [
        "新增三切割體寬為<code>10.4</code>、<code>10.5</code>、<code>10.6 mm</code>",
        "中心X依序<code>7</code>、<code>21</code>、<code>35 mm</code>，Y均<code>2 mm</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode · 第 3 孔切割體已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-07-cutter-4.png",
          "sha256": "73ef90c9a4153ff85a9fd1efc7eac37e0c5bc8f6b6dc7e934cb4a481514692e3",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "第四切割體 Dimensions 10.4×10.4×8 mm，Location X 7、Y 2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-08-cutter-5.png",
          "sha256": "1e0a1322b2241759527b5aa5adc306f90b55284cce3cd30c5401da8d4f44aee5",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "第五切割體 Dimensions 10.5×10.5×8 mm，Location X 21、Y 2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-09-cutter-6.png",
          "sha256": "11bd92615f3ffe1d521ea102aab809e4c55a52b7b8441d6a4810a4e97ca407ef",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "第六切割體 Dimensions 10.6×10.6×8 mm，Location X 35、Y 2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "切割體 Dime"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-06",
      "title": "建立第一個凹點圓柱",
      "lead": "Object Mode · N 側欄 Item 建立第一個凹點圓柱。",
      "actions": [
        "Add › Mesh › Cylinder，先看 N 側欄 Dimensions：改成 <code>1.2mm</code>、<code>1.2mm</code>、<code>2mm</code>（新增時若顯示 <code>2000 mm</code> 之類的大數字，同樣直接改）。",
        "Location 設 X <code>-35mm</code>、Y <code>-8.5mm</code>、Z <code>2.2mm</code>。"
      ],
      "checks": [
        "圓柱尺寸為<code>1.2</code>×<code>1.2</code>×<code>2 mm</code>",
        "Location 為<code>-35</code>、<code>-8.5</code>、<code>2.2 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Object Mode · N 側欄 Item",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-10-marker-base.png",
          "sha256": "52f080793529e67f5a60886fbbd39e2c933a657a5facf4b840ddec00d9655a6d",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cylinder 選取，Dimensions 1.2×1.2×2 mm、Location X -35、Y -8.5、Z 2.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                963,
                133,
                228,
                59
              ],
              "label": "Location"
            },
            {
              "n": 2,
              "box": [
                963,
                383,
                228,
                77
              ],
              "label": "圓柱 Dimen"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-07",
      "title": "複製第 2、3 組凹點",
      "lead": "Object Mode · 凹點圓柱已選取 複製第 2、3 組凹點。",
      "actions": [
        "沿用第 <code>1</code> 組原圓柱，按 <kbd>Shift</kbd>+<kbd>D</kbd>、X，依下一目標 X 與目前 X 的差值輸入相對位移，按 <kbd>Enter</kbd>。",
        "第 <code>2</code> 組目標 X 為 <code>-21.8</code>、<code>-20.2 mm</code>；第 <code>3</code> 組為 <code>-8.6</code>、<code>-7</code>、<code>-5.4 mm</code>，Y、Z 不變。"
      ],
      "checks": [
        "第<code>2</code>組有<code>2</code>個、第<code>3</code>組有<code>3</code>個凹點工具",
        "同組目標X間距<code>1.6 mm</code>，Y、Z保持不變"
      ],
      "pitfalls": [
        {
          "title": "凹點間只剩薄肉",
          "text": "凹點直徑<code>1.2 mm</code>、中心距<code>1.6 mm</code>，名義餘肉只有<code>0.4 mm</code>；不由噴嘴<code>0.4 mm</code>推定線寬或印製成功。"
        },
        {
          "title": "操作提醒",
          "text": "複製後仍要依原方法定位及逐件核對尺寸；<kbd>Ctrl</kbd>+<kbd>J</kbd> 是 Join，不是 Boolean Union。Boolean Difference／修改器 Apply 照原方法，不能用 <kbd>Ctrl</kbd>+<kbd>A</kbd> 替代。"
        },
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Object Mode · 凹點圓柱已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-12-markers-2.png",
          "sha256": "29569acafe436ee75f55ab9b561cd3503f39cab9c1769d46318a44db8fe3a9b9",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "複製第2組凹點，所選Cylinder.002的X為−20.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "凹點位置"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-13-markers-3.png",
          "sha256": "4ca41d5baed9524e7dcfff4e0f0e435b01d39a0f39d3f0d608efec047048a04b",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "第3組末個凹點Cylinder.005，X為−5.4 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "凹點位置"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-08",
      "title": "複製第 4～6 組凹點",
      "lead": "Object Mode · 凹點圓柱已選取 複製第 4～6 組凹點。",
      "actions": [
        "繼續 <kbd>Shift</kbd>+<kbd>D</kbd> › X，用目標 X 減前一圓柱的 X 算相對位移；第 <code>4</code> 組為 <code>4.6</code>、<code>6.2</code>、<code>7.8</code>、<code>9.4 mm</code>。",
        "第 <code>5</code> 組為 <code>17.8</code>、<code>19.4</code>、<code>21</code>、<code>22.6</code>、<code>24.2</code>；第 <code>6</code> 組為 <code>31</code>、<code>32.6</code>、<code>34.2</code>、<code>35.8</code>、<code>37.4</code>、<code>39 mm</code>；Y、Z 不變。"
      ],
      "checks": [
        "第<code>4</code>至<code>6</code>組分別有<code>4</code>、<code>5</code>、<code>6</code>個凹點工具",
        "凹點總<code>21</code>個，加<code>6</code>個方孔工具共<code>27</code>個"
      ],
      "pitfalls": [],
      "locate": "Object Mode · 凹點圓柱已選取",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-14-markers-4.png",
          "sha256": "bd862c6526db86ac99db6e7e5a3e6ef9d5cad43aeae365d079ab01a6839fe47a",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "第4組末個凹點Cylinder.009，X為9.4 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "凹點位置"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-15-markers-5.png",
          "sha256": "5c502d69ba60b6c214074319ff210a45e463b2255b260eb2ceb7c28d8a033737",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "第5組末個凹點Cylinder.014，X為24.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "凹點位置"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-16-markers-6.png",
          "sha256": "85076eaaa57cc61347279db3f920eb0ff3d89ba44a6dc302e23d1c4579aaf9cf",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "第6組末個凹點Cylinder.020，Location X39、Y−8.5、Z2.2 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                131,
                178,
                63
              ],
              "label": "第6組末點位置"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-09",
      "title": "合併成 Cutters",
      "lead": "Object Mode · Plate 隱藏中 合併成 Cutters。",
      "actions": [
        "滑鼠在 3D Viewport 內按 <kbd>A</kbd> 選取全部 <code>27</code> 個切割體，<kbd>Ctrl</kbd>+<kbd>J</kbd> 合併。",
        "Object › Apply › Scale，按 <kbd>F2</kbd> 改名 Cutters。"
      ],
      "checks": [
        "Outliner 中工具合為一個 Cutters",
        "Item 外框約<code>80.35</code>×<code>16.4</code>×<code>8 mm</code>；X可能顯示四捨五入<code>80.4</code>"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "複製後仍要依原方法定位及逐件核對尺寸；<kbd>Ctrl</kbd>+<kbd>J</kbd> 是 Join，不是 Boolean Union。Boolean Difference／修改器 Apply 照原方法，不能用 <kbd>Ctrl</kbd>+<kbd>A</kbd> 替代。"
        }
      ],
      "locate": "Object Mode · Plate 隱藏中",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-17-cutters-joined.png",
          "sha256": "f6d74f882fd8915f6f1aa93b17f593560adc5d038800495c8ec3819a4393bef6",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Cutters已合併為單一物件，Scale1；X外框畫面四捨五入為80.4 mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1293,
                92,
                110,
                22
              ],
              "label": "工具合併後"
            },
            {
              "n": 2,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "工具顯示尺寸"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-10",
      "title": "用 Boolean 開孔",
      "lead": "Object Mode · Properties 扳手分頁 用 Boolean 開孔。",
      "actions": [
        "按 <kbd>Alt</kbd>+<kbd>H</kbd> 顯示 Plate，只選 Plate；Properties 扳手圖示 › Add Modifier › Generate › Boolean。",
        "Operation 選 Difference，Object 欄選 Cutters。"
      ],
      "checks": [
        "Plate 的 Boolean 為 Difference、Object為 Cutters",
        "預覽可見六孔與凹點切割效果"
      ],
      "pitfalls": [],
      "locate": "Object Mode · Properties 扳手分頁",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-18-boolean-empty.png",
          "sha256": "ecbff875c5d4b9a0e430ca3d32e21c03b6af5f2d04fa5889117249b139feaf03",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Plate 選取，Boolean Modifier Difference、Exact，Object 欄空。",
          "marks": [
            {
              "n": 1,
              "box": [
                1409,
                340,
                66,
                21
              ],
              "label": "Differen"
            },
            {
              "n": 2,
              "box": [
                1351,
                389,
                104,
                22
              ],
              "label": "Object／滴"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-19-boolean-assigned.png",
          "sha256": "d0bb24fc86da2b3d9b9675dcdf44b63f65086cf0189b2f75e53bf87c73824cdc",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "Plate 的 Boolean Difference Modifier 的 Object 欄為 Cutters。",
          "marks": [
            {
              "n": 1,
              "box": [
                1351,
                389,
                104,
                22
              ],
              "label": "Cutters"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-20-holes-preview.png",
          "sha256": "c6292c819628b2a08ad86cd4baae8714ed8864e40f9a51d6a4dadf5a832eff09",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Cutters隱藏後可見六通孔；Difference仍在預覽。此角度凹點不明顯。",
          "marks": [
            {
              "n": 1,
              "box": [
                1314,
                338,
                164,
                72
              ],
              "label": "差集工具設定"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-11",
      "title": "套用並檢查孔板",
      "lead": "Object Mode → Edit Mode 套用並檢查孔板。",
      "actions": [
        "選 Cutters 按 <kbd>H</kbd> 隱藏；選 Plate，在 Boolean 標題列下拉選單選 Apply。",
        "<kbd>Tab</kbd> 進 Edit Mode、按 <kbd>2</kbd>，Select › None 後 Select › Select All by Trait › Non Manifold。"
      ],
      "checks": [
        "套用後斜視可見六通孔與凹點",
        "執行 Non Manifold 後沒有邊反白"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "既有原圖證明 <kbd>F3</kbd> 的搜尋鍵標，並未驗證該檢查有獨立直接快捷鍵。搜尋及閉合檢查不代表可列印或配合合格。"
        }
      ],
      "locate": "Object Mode → Edit Mode",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-21-apply-boolean-menu.png",
          "sha256": "b7ee68f89912455d2f146b72e7b444357ce3f62084b29da39da1c8b4de67b971",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Boolean 標題下拉選單展開並列出 Apply。",
          "marks": [
            {
              "n": 1,
              "box": [
                1287,
                333,
                145,
                20
              ],
              "label": "Apply"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-22-applied.png",
          "sha256": "251ebfa8e68ce120c62db2a196e8b503a9ffcb807081f9ec3eb7f772d8933a31",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "套用後Modifier僅剩Add Modifier，六孔保留。",
          "marks": [
            {
              "n": 1,
              "box": [
                1268,
                275,
                213,
                24
              ],
              "label": "修改器已套用"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-23-non-manifold.png",
          "sha256": "254f77b796216bc85a3a9461642282b32a4c247ba9a0b9d6c0c31fd4ba99a2b0",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "Edit Mode 邊選取、Nothing selected，左下 Select Non-Manifold；線框中可見六孔和多個點輪廓。",
          "marks": [
            {
              "n": 1,
              "box": [
                49,
                28,
                96,
                20
              ],
              "label": "Edit Mod"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    },
    {
      "stepId": "ch05-05-03-12",
      "title": "保存並重新開啟",
      "lead": "Edit Mode 檢查 · File › Save As / Open 保存並重新開啟。",
      "actions": [
        "若尚未保存，File › Save As 至單元<code>05</code>工作區的新檔名，例如 <code>u05_hole_plate_v001.blend</code>；確認儲存完成。",
        "到教學頁以單元<code>05</code>登記實際保存的孔板檔，再重新開啟核對。"
      ],
      "checks": [
        "重開後 Plate 幾何與保存前相符",
        "版本表有實際孔板檔名、路徑與 SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "Edit Mode 檢查 · File › Save As / Open",
      "figures": [
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-25-saved.png",
          "sha256": "fbca8f4f712b57feada96bff953b81de1146f9678c656383e519fe0e3b83fb8f",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "孔板保存成功，底部顯示u05_hole_plate_v001.blend。",
          "marks": [
            {
              "n": 1,
              "box": [
                579,
                996,
                310,
                21
              ],
              "label": "孔板保存提示"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-27-open-dialog.png",
          "sha256": "4219c8d2e151e80af25cdf338ee8fcf3f0e35e54cced1943d9ad24c90216c9a6",
          "size": [
            1060,
            600
          ],
          "tab": "過程狀態",
          "caption": "Open 對話框列出 u05_hole_plate_v001.blend，大小顯示 148 KiB。",
          "marks": [
            {
              "n": 1,
              "box": [
                789,
                566,
                126,
                25
              ],
              "label": "Open"
            }
          ]
        },
        {
          "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-28-reopened-verified.png",
          "sha256": "c095e81a5bd43caf63f7784f6a31dca1223ccad7892a7c82113009cd59d64479",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "重開後Plate尺寸96×26×4 mm，六孔可見且Cutters隱藏。",
          "marks": [
            {
              "n": 1,
              "box": [
                961,
                399,
                229,
                64
              ],
              "label": "孔板外框"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
          "label": "本次操作與讀值說明"
        }
      ]
    }
  ],
  "prep": {
    "stepId": "ch05-05-03-01",
    "title": "建立孔板檔",
    "actions": [
      "保留現有作品後，從獨立新場景開始；示範選取出廠物件並 X › Delete，再 Add › Mesh › Cube。",
      "Scene › Units 設 Unit System Metric、Length Millimeters、Unit Scale <code>0.001</code>；保存孔板檔的動作在後續完成。"
    ],
    "checks": [
      "場景 Units 為 Metric、Millimeters、<code>0.001</code>",
      "已新增供製作孔板的 Cube"
    ],
    "pitfalls": [],
    "locate": "Blender 主視窗",
    "figures": [
      {
        "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-01-new-scene.png",
        "sha256": "bbc3fc0d8153d6b40a2755c4777b15b314e113bfe2848df371d97cc05dff7cef",
        "size": [
          1494,
          1019
        ],
        "tab": "操作位置",
        "caption": "刪除三個出廠物件後，Collection為空，底部有Deleted 3 object(s)通知。",
        "marks": [
          {
            "n": 1,
            "box": [
              1258,
              74,
              227,
              42
            ],
            "label": "空集合"
          },
          {
            "n": 2,
            "box": [
              662,
              996,
              154,
              21
            ],
            "label": "刪除提示"
          }
        ]
      },
      {
        "path": "evidence/05/2026-10-22-lesson05-holes-demo-v002/05-03-02-units.png",
        "sha256": "7019a1000e5c66d571e7eb8b44949d1bbe55c33446b61affc88e38e3f6afa81c",
        "size": [
          1494,
          1019
        ],
        "tab": "過程狀態",
        "caption": "新 Cube 已出現在 Outliner，Scene Units Scale 0.001、Length Millimeters。",
        "marks": [
          {
            "n": 1,
            "box": [
              1266,
              477,
              216,
              22
            ],
            "label": "0.001"
          },
          {
            "n": 2,
            "box": [
              963,
              383,
              228,
              77
            ],
            "label": "Dimensio"
          }
        ]
      }
    ],
    "keys": [],
    "kind": "prep",
    "summary": "Blender 主視窗 建立孔板檔。",
    "lead": "Blender 主視窗 建立孔板檔。",
    "references": [
      {
        "path": "journal/2026-10-22-lesson05-holes-demo-v002.md",
        "label": "本次操作與讀值說明"
      }
    ]
  }
};
