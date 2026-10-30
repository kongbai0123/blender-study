window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["08-05"] = {
  "id": "08-05",
  "title": "手工固定上蓋",
  "keyPoint": "在參數盒上手工建立固定蓋板與環唇。",
  "glossary": [
    {
      "term": "Cube",
      "label": "Cube",
      "text": "這組實拍中上蓋沿用的物件名稱。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch08-manual-lid-fixed-01",
      "title": "新增並定位蓋板",
      "lead": "獨立試驗盒80×50×30 mm，離開草圖並選取 Body。 新增並定位蓋板。",
      "actions": [
        "H 隱藏盒體，新增 Cube。",
        "依本次單位設定縮放為約<code>80</code>×<code>50</code>×<code>2 mm</code>，套用縮放，再移至盒口 Z30～<code>32 mm</code>。"
      ],
      "checks": [
        "新增物件在這組實拍中名為 Cube",
        "定位後形成覆蓋<code>80</code>×<code>50</code>盒口的薄蓋板"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "獨立試驗盒80×50×30 mm，離開草圖並選取 Body。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-02-body-selected.png",
          "sha256": "d59d15608dae79716dc9e0cffa49c992027070182103b91a5ade6c98e05c684f",
          "size": [
            1494,
            1019
          ],
          "tab": "操作位置",
          "caption": "Object Mode、Body作用中，凹盒可見；即將隱藏盒體以建上蓋。",
          "marks": [
            {
              "n": 1,
              "box": [
                65,
                100,
                119,
                23
              ],
              "label": "活動Body"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-03-cube.png",
          "sha256": "e61e1e6f4c69d2d5e26557d8bb92866e63170492438e966ad8520d86b1f98630",
          "size": [
            1494,
            1019
          ],
          "tab": "過程狀態",
          "caption": "新Cube被選取，因尺寸大到超出視野，只見斜角邊；底部1 object(s) hidden。",
          "marks": [
            {
              "n": 1,
              "box": [
                1238,
                84,
                160,
                22
              ],
              "label": "新增Cube"
            },
            {
              "n": 2,
              "box": [
                663,
                995,
                146,
                23
              ],
              "label": "盒體已隱藏"
            }
          ]
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-04-plate.png",
          "sha256": "4e02787f9f7ee72adfdb38950d74f2db6e13e49b15a5714f01571307b194bc25",
          "size": [
            1494,
            1019
          ],
          "tab": "核對結果",
          "caption": "新Cube縮放移動後呈薄蓋板，Body隱藏；此圖未顯示蓋板尺寸欄位。",
          "marks": [
            {
              "n": 1,
              "box": [
                615,
                341,
                338,
                198
              ],
              "label": "固定蓋板"
            }
          ]
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json",
          "label": "固定尺寸上蓋幾何與讀值摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-fixed-02",
      "title": "內插並擠出唇外緣",
      "lead": "Cube 的 Edit Mode、面選取；切底視並選取底面。 內插並擠出唇外緣。",
      "actions": [
        "底面 I 內插<code>2.2 mm</code>。",
        "對選定面 E 拉伸<code>4 mm</code>。"
      ],
      "checks": [
        "底視可見內插後的外輪廓",
        "擠出後仍選中唇邊端面，深度另查頂點讀值"
      ],
      "pitfalls": [],
      "locate": "Cube 的 Edit Mode、面選取；切底視並選取底面。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-05-bottom-face.png",
          "sha256": "bb699be8014a77bc61e603807bf76c3096409ce32e63bec9e2174bf47e492fb5",
          "size": [
            1494,
            1019
          ],
          "caption": "Bottom Orthographic、Edit Mode面選取，蓋板底面反白；物件仍名Cube。",
          "marks": [
            {
              "n": 1,
              "box": [
                65,
                82,
                177,
                22
              ],
              "label": "底部正交"
            },
            {
              "n": 2,
              "box": [
                617,
                477,
                283,
                177
              ],
              "label": "選取底面"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-06-inset-outer.png",
          "sha256": "496f11074111129ec839e1340a5d5ae051b99349dc657683db37bcdcd111666c",
          "size": [
            1494,
            1019
          ],
          "caption": "底視中第一次Inset形成邊框，左下Inset Faces；數字2.2mm不在此圖可讀。",
          "marks": [
            {
              "n": 1,
              "box": [
                617,
                477,
                283,
                177
              ],
              "label": "內插輪廓"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-07-lip-extrude.png",
          "sha256": "83980518070dc3b94d877ef9091fb26f0d0b8341f69e42407112ecf0b5595cbc",
          "size": [
            1494,
            1019
          ],
          "caption": "底視沿法向Extrude前後外輪廓近似相同，左下Extrude Region and Move；高度不能由這角度看出。",
          "marks": [
            {
              "n": 1,
              "box": [
                62,
                892,
                212,
                25
              ],
              "label": "擠出紀錄"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json",
          "label": "固定尺寸上蓋幾何與讀值摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-fixed-03",
      "title": "形成環形唇邊",
      "lead": "保持 Edit Mode、所選中心面與底視。 形成環形唇邊。",
      "actions": [
        "I 再內插<code>2 mm</code>。",
        "E 輸入 <code>-4 mm</code>，將中心面推回。"
      ],
      "checks": [
        "底視可辨兩圈環狀輪廓",
        "讀值表按Z列出<code>26</code>、<code>30</code>、<code>32 mm</code>三組頂點"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "保持 Edit Mode、所選中心面與底視。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-08-inset-inner.png",
          "sha256": "8a79ea03a626a47b80d532ac3afd968a9b7bb0b5c82a2e042cbbc482d7821373",
          "size": [
            1494,
            1019
          ],
          "caption": "第二次Inset後有兩圈邊線，中心面反白；內緣形成，沒有數字尺寸顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                617,
                477,
                283,
                177
              ],
              "label": "內外輪廓"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-09-lip-recess.png",
          "sha256": "cd5b7ef66d7141cc3858e9253ba851a07e82a314a07eb4b201328fd7e71f79a9",
          "size": [
            1494,
            1019
          ],
          "caption": "中心面推回後底視輪廓與擠出前近似，不能憑這張圖單獨確認凹深，須看讀值。",
          "marks": [
            {
              "n": 1,
              "box": [
                62,
                891,
                212,
                26
              ],
              "label": "擠出紀錄"
            }
          ],
          "tab": "過程狀態"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json",
          "label": "固定尺寸上蓋幾何與讀值摘要"
        }
      ]
    },
    {
      "stepId": "ch08-manual-lid-fixed-04",
      "title": "保存固定上蓋",
      "lead": "Object Mode；顯示已隱藏的盒體。 保存固定上蓋。",
      "actions": [
        "顯示盒體，另存獨立版本，再重新開啟。",
        "對照安全摘要中的頂點座標、non-manifold 邊數與檔案 SHA。"
      ],
      "checks": [
        "恢復顯示後可見盒與蓋",
        "保存與重開原圖對應同一新版本，讀值表列Body／Cube非流形邊<code>0</code>"
      ],
      "pitfalls": [],
      "locate": "Object Mode；顯示已隱藏的盒體。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-10-assembly.png",
          "sha256": "73c456d2717a72dcfc42a49d3fe0a1c6e64d085dae20cadd79b2eefe767ca781",
          "size": [
            1494,
            1019
          ],
          "caption": "Object Mode、Show Hidden Objects剛執行；底視被面遮住，配合面不可見。",
          "marks": [
            {
              "n": 1,
              "box": [
                62,
                891,
                164,
                26
              ],
              "label": "恢復顯示"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-11-saved.png",
          "sha256": "b94567bc718665978b4dfcec3e5b7e93d5375ccb1cbd7c22361988ef7e073007",
          "size": [
            1494,
            1019
          ],
          "caption": "底部Saved as manual_box_lid_fixed_80x50_v001.blend；固定上蓋存檔畫面。",
          "marks": [
            {
              "n": 1,
              "box": [
                574,
                995,
                325,
                23
              ],
              "label": "固定蓋存檔"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/LID-12-reopened.png",
          "sha256": "75ca1e8b0d975a4e8e2e64d584462bc692a2238d29cbb471e68022ad6a2f4671",
          "size": [
            1494,
            1019
          ],
          "caption": "固定蓋重開後仍是底視；只看到整片外表面，不能視為間隙驗證。",
          "marks": [
            {
              "n": 1,
              "box": [
                65,
                82,
                177,
                22
              ],
              "label": "底部正交"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-geometry-v002/demo-files/manual_box_lid_fixed_80x50_v001.blend",
          "label": "固定80×50盒蓋示範場景（未連動）"
        },
        {
          "path": "evidence/parametric/2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json",
          "label": "固定尺寸上蓋幾何與讀值摘要"
        }
      ]
    }
  ]
};
