window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["11-02"] = {
  "id": "11-02",
  "title": "Screw 開放曲面（觀察示範）",
  "keyPoint": "觀察 Screw 每轉位移與開放邊界。",
  "glossary": [
    {
      "term": "Screw",
      "label": "Screw",
      "text": "本節沿Z旋轉並位移輪廓的修改器。"
    },
    {
      "term": "Iterations",
      "label": "Iterations",
      "text": "掃掠重複次數，不是螺紋線數。"
    },
    {
      "term": "Steps Viewport",
      "label": "Steps Viewport",
      "text": "視窗中每次掃掠的採樣分段。"
    },
    {
      "term": "Angle",
      "label": "Angle",
      "text": "每次掃掠的旋轉角度。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch11-screw-surface-profile",
      "title": "觀察輪廓",
      "lead": "來源盒副本中的 Thread_Profile；Object Mode。原盒在示範中被程式隱藏。 觀察輪廓。",
      "actions": [
        "觀察程式建立的開放牙型線：半徑 <code>5</code>→<code>6</code>→<code>5 mm</code>、Z <code>0</code>→<code>0.3</code>→<code>0.6 mm</code>。"
      ],
      "checks": [
        "視窗中可見開放折線輪廓",
        "讀值表列三頂點半徑<code>5</code>→<code>6</code>→<code>5</code>、Z0→<code>0.3</code>→<code>0.6 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "起始輪廓由程式建立",
          "text": "本節觀察修改器與開放曲面，不把起始三點線當作手工建模紀錄。"
        }
      ],
      "locate": "來源盒副本中的 Thread_Profile；Object Mode。原盒在示範中被程式隱藏。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-01-profile.png",
          "sha256": "f78222403bfbff0e5acf3e2fc35d0d34a86b565fb00241d417e3063c470f420b",
          "size": [
            1494,
            1019
          ],
          "caption": "Thread_Profile線很小；Item外框1／0／0.6mm。三頂點與半徑座標不在圖片中直接讀出。",
          "marks": [
            {
              "n": 1,
              "box": [
                962,
                398,
                229,
                64
              ],
              "label": "輪廓外框"
            },
            {
              "n": 2,
              "box": [
                635,
                473,
                35,
                19
              ],
              "label": "開放輪廓"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/demo-files/u08_screw_surface_v001.blend",
          "label": "螺旋開放曲面場景 v001（示範原檔）"
        },
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/screw-surface-verification-v001.json",
          "label": "螺旋曲面實際操作與數位驗證摘要"
        }
      ]
    },
    {
      "stepId": "ch11-screw-surface-add-screw",
      "title": "加入 Screw 修改器",
      "lead": "Object Mode；3D Viewport 聚焦，作用中為沒有 Screw 修改器的 Thread_Profile。 加入 Screw 修改器。",
      "actions": [
        "觀察示範：按 <kbd>F3</kbd> 搜尋 Add Screw Modifier，選取搜尋結果。"
      ],
      "checks": [
        "Modifier清單出現 Screw",
        "預設Angle360°、Screw0 mm、Iterations1"
      ],
      "pitfalls": [
        {
          "title": "操作提醒",
          "text": "搜尋結果依實際介面判斷；不能在成品上重複新增而宣稱與原示範相同。"
        }
      ],
      "locate": "Object Mode；3D Viewport 聚焦，作用中為沒有 Screw 修改器的 Thread_Profile。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-02-screw-added.png",
          "sha256": "45bc678aa905d24ce39853fe2fc5b122c25d39e1e92e135632de78ff66618a91",
          "size": [
            1494,
            1019
          ],
          "caption": "Screw修改器預設Angle360、Screw0mm、Iterations1，Z軸，Viewport／Render16。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                340,
                108,
                66
              ],
              "label": "預設掃掠值"
            },
            {
              "n": 2,
              "box": [
                1276,
                499,
                181,
                45
              ],
              "label": "預設分段"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-lead",
      "title": "設定每轉位移",
      "lead": "選取 Thread_Profile；Properties › Modifiers › Screw。 設定每轉位移。",
      "actions": [
        "觀察示範：在 Screw 欄位輸入 <code>1 mm</code>，確認 Angle <code>360°</code>、Z 軸且 Object Screw 關閉。"
      ],
      "checks": [
        "Screw欄為<code>1 mm</code>、Angle360°、Axis Z",
        "Object Screw關閉，畫面出現軸向延伸"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "選取 Thread_Profile；Properties › Modifiers › Screw。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-03-lead-one.png",
          "sha256": "edba095de3711a1056698d23338060d4e63ea06fab909b4ee320de84b2a910b1",
          "size": [
            1494,
            1019
          ],
          "caption": "Screw改1mm，Angle360、Iterations仍1，Item Z變1.6mm。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                340,
                108,
                66
              ],
              "label": "單次位移"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-iterations",
      "title": "設定掃掠次數",
      "lead": "Properties › Modifiers › Screw；Angle 360°、Screw 1 mm。 設定掃掠次數。",
      "actions": [
        "觀察示範：將 Iterations 設為<code>4</code>。"
      ],
      "checks": [
        "Iterations顯示<code>4</code>",
        "讀值表分列<code>4</code>圈、軸向位移<code>4 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Properties › Modifiers › Screw；Angle 360°、Screw 1 mm。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-04-four-iterations.png",
          "sha256": "5b0b187bdb70d5653b3e4f55546c45b443881ef3ad87f6aecb6bdc5198566af0",
          "size": [
            1494,
            1019
          ],
          "caption": "Iterations4，Angle360、Screw1mm；Item Z4.6mm，不把外框4.6混成導程。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                340,
                108,
                66
              ],
              "label": "四次掃掠"
            },
            {
              "n": 2,
              "box": [
                962,
                438,
                229,
                25
              ],
              "label": "外框高度"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-resolution",
      "title": "設定分段",
      "lead": "Properties › Modifiers › Screw。 設定分段。",
      "actions": [
        "觀察示範：將 Steps Viewport 與 Render 各設為<code>32</code>。"
      ],
      "checks": [
        "Steps Viewport為<code>32</code>",
        "Render分段同為<code>32</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Properties › Modifiers › Screw。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-05-resolution.png",
          "sha256": "233ba945c72f6831e3c70a58c0d38c2d9606d6ae2a22df6dabb5b055fca41f8c",
          "size": [
            1494,
            1019
          ],
          "caption": "Screw的Steps Viewport與Render皆32，Angle360／Screw1／Iterations4；環形外觀看不出確切段數，欄位可讀。",
          "marks": [
            {
              "n": 1,
              "box": [
                1276,
                499,
                181,
                45
              ],
              "label": "分段32"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-inspect",
      "title": "檢查開放邊",
      "lead": "已新增 Screw 修改器並顯示評估結果；修改器未套用（Apply）。 檢查開放邊。",
      "actions": [
        "觀察放大的曲面與修改器設定，再參考數位驗證摘要中的邊界數。"
      ],
      "checks": [
        "放大後可見曲面端部仍開放",
        "讀值摘要列<code>260</code>條開放邊及整高約<code>4.6 mm</code>"
      ],
      "pitfalls": [],
      "locate": "已新增 Screw 修改器並顯示評估結果；修改器未套用（Apply）。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-06-surface-verified.png",
          "sha256": "fc1e42f175dc35f297efa4c07064f7366ca0e84ec0615d7e9a77f6a8df50836b",
          "size": [
            1494,
            1019
          ],
          "caption": "放大後螺旋曲面可見多圈與開放端，Screw設定360／1／4／32；開放邊260不在畫面直接顯示。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                340,
                108,
                66
              ],
              "label": "螺旋設定"
            },
            {
              "n": 2,
              "box": [
                1276,
                499,
                181,
                45
              ],
              "label": "分段32"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-save",
      "title": "另存版本",
      "lead": "File › Save As；示範的檔案路徑與名稱由程式填入，確認為GUI事件。 另存版本。",
      "actions": [
        "觀察示範另存為 <code>u08_screw_surface_v001.blend</code>。"
      ],
      "checks": [
        "另存成功通知顯示<code>u08_screw_surface_v001.blend</code>",
        "版本摘要列新路徑與SHA-<code>256</code>"
      ],
      "pitfalls": [],
      "locate": "File › Save As；示範的檔案路徑與名稱由程式填入，確認為GUI事件。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-07-saved.png",
          "sha256": "44a0079d9beea54eab1e74fe85f743ff9c10b39510a8d1552564372f1d229b44",
          "size": [
            1494,
            1019
          ],
          "caption": "底部Saved as u08_screw_surface_v001.blend；螺旋修改器設定保留。",
          "marks": [
            {
              "n": 1,
              "box": [
                600,
                995,
                275,
                23
              ],
              "label": "曲面存檔"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    },
    {
      "stepId": "ch11-screw-surface-reopen",
      "title": "重開核對",
      "lead": "重開示範 v001 場景；Properties › Modifiers › Screw。 重開核對。",
      "actions": [
        "觀察重開後的修改器設定，再對照安全摘要中的讀值。"
      ],
      "checks": [
        "重開後Screw為<code>360°</code>、<code>1 mm</code>、<code>4</code>次",
        "Viewport與Render分段均<code>32</code>"
      ],
      "pitfalls": [],
      "locate": "重開示範 v001 場景；Properties › Modifiers › Screw。",
      "figures": [
        {
          "path": "evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-08-reopened.png",
          "sha256": "4c6b6f2d96bb5fd7de8a3529355198233a42cef8911da6a4e1c98bd499147314",
          "size": [
            1494,
            1019
          ],
          "caption": "重新開啟後仍顯示同螺旋曲面、360／1／4／32設定；不代表封閉實體或可製造。",
          "marks": [
            {
              "n": 1,
              "box": [
                1350,
                340,
                108,
                66
              ],
              "label": "重開設定"
            },
            {
              "n": 2,
              "box": [
                1276,
                499,
                181,
                45
              ],
              "label": "重開分段"
            }
          ],
          "tab": "操作位置"
        }
      ],
      "keys": []
    }
  ]
};
