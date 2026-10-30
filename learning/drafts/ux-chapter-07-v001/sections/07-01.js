window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["07-01"] = {
  "id": "07-01",
  "title": "安裝 CAD Sketcher 與工程工作區",
  "keyPoint": "核對安裝檔，啟用 CAD Sketcher 並另存練習。",
  "glossary": [
    {
      "term": "CAD Sketcher",
      "label": "CAD Sketcher",
      "text": "在Blender內建立尺寸約束草圖的外掛。"
    },
    {
      "term": "Install from Disk",
      "label": "Install from Disk",
      "text": "從本機ZIP安裝外掛的入口。"
    },
    {
      "term": "Add-ons",
      "label": "Add-ons",
      "text": "Preferences中檢查外掛啟用狀態的位置。"
    }
  ],
  "scope": "圖片沿用既有 Blender 實拍；圖中可見內容與讀值分開核對，試驗尺寸不代表實體合格。",
  "steps": [
    {
      "stepId": "ch07-setup-01",
      "title": "取得安裝檔並核對",
      "lead": "瀏覽器與 Windows PowerShell；本章使用 CAD Sketcher 0.32.1。 取得安裝檔並核對。",
      "actions": [
        "從 CAD Sketcher <code>0.32.1</code> 官方 release 下載 Windows x64 ZIP，保留原檔。",
        "在 PowerShell 對該 ZIP 執行 Get-FileHash &lt;檔案完整路徑› -Algorithm SHA256，並核對檔案大小。"
      ],
      "checks": [
        "下載ZIP的檔案大小為<code>1</code>,<code>283</code>,<code>581 bytes</code>",
        "SHA-<code>256</code>與本節指定的完整指紋相同"
      ],
      "pitfalls": [],
      "locate": "瀏覽器與 Windows PowerShell；本章使用 CAD Sketcher 0.32.1。",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-cad-install-gui-trial-v002/safe-summary-v001.json",
          "label": "隔離安裝使用的 ZIP 來源與讀值"
        }
      ],
      "figureNote": "已補查現行教材及原操作序列，未找到可獨立對應本步的實拍。"
    },
    {
      "stepId": "ch07-setup-02",
      "title": "安裝並啟用",
      "lead": "Blender 5.2.1：Edit › Preferences › Get Extensions。 安裝並啟用。",
      "actions": [
        "Edit › Preferences › Get Extensions，展開右上選單並選 Install from Disk...，選上一步核對過的 ZIP。",
        "到 Add-ons 確認 CAD Sketcher 已啟用；回 3D Viewport 按 <kbd>N</kbd>，查看 Sketcher 分頁。"
      ],
      "checks": [
        "Add-ons 中 CAD Sketcher 已勾選",
        "回到3D Viewport，N側欄出現 Sketcher 分頁"
      ],
      "pitfalls": [],
      "locate": "Blender 5.2.1：Edit › Preferences › Get Extensions。",
      "figures": [
        {
          "path": "evidence/parametric/2026-10-28-cad-install-gui-trial-v002/CAD-INSTALL-01-menu.png",
          "sha256": "c5f7b5a9ae7006a46b1d96f7eb2acd75b5e3daa96e34e0dff251a64a88e9e9ee",
          "size": [
            840,
            550
          ],
          "caption": "Get Extensions 頁，右上選單有 Install from Disk；目前尚未安裝結果。",
          "marks": [
            {
              "n": 1,
              "box": [
                641,
                123,
                184,
                24
              ],
              "label": "從磁碟安裝"
            }
          ],
          "tab": "操作位置"
        },
        {
          "path": "evidence/parametric/2026-10-28-cad-install-gui-trial-v002/CAD-INSTALL-03-addons.png",
          "sha256": "e93c4600306dfef79b09260f790ad3163967fc8eee1c0eee517108acf64e7ec6",
          "size": [
            840,
            550
          ],
          "caption": "Add-ons 的 CAD Sketcher 核取方塊已勾選。",
          "marks": [
            {
              "n": 1,
              "box": [
                191,
                42,
                138,
                22
              ],
              "label": "啟用擴充"
            }
          ],
          "tab": "過程狀態"
        },
        {
          "path": "evidence/parametric/2026-10-28-cad-install-gui-trial-v002/CAD-INSTALL-04-sidebar.png",
          "sha256": "8b7fa61b0c51b4344b9a946103113f954d00fd8f0ba4da84d63571f31e9e37c7",
          "size": [
            1494,
            1019
          ],
          "caption": "Object Mode 預設方塊；N 側欄右緣可見 Sketcher 分頁，還沒點開。",
          "marks": [
            {
              "n": 1,
              "box": [
                1202,
                290,
                21,
                66
              ],
              "label": "Sketcher"
            }
          ],
          "tab": "核對結果"
        }
      ],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-cad-install-gui-trial-v002/safe-summary-v001.json",
          "label": "隔離 GUI 安裝、版本和啟用讀回"
        }
      ]
    },
    {
      "stepId": "ch07-setup-03",
      "title": "建立工作區與毫米草圖檔",
      "lead": "Windows PowerShell（專案根目錄）與 Blender 5.2.1。 建立工作區與毫米草圖檔。",
      "actions": [
        "在 PowerShell 執行 python learning/manage.py engineering-workspace，建立並顯示 learning/workspaces/engineering-parametric/。",
        "在 Blender 依第 <code>03</code> 章「建立毫米工作檔」的設定新開檔：Scene 的 Units 把 Length 改為 Millimeters、Unit Scale 改為 <code>0.001</code>。",
        "另存為 <code>learning/workspaces/engineering-parametric/sketch_practice_v001.blend</code>。"
      ],
      "checks": [
        "工作區命令列出 engineering-parametric 路徑",
        "保存通知或重開檔名為 <code>sketch_practice_v001.blend</code>，預設Cube為<code>2 mm</code>"
      ],
      "pitfalls": [
        {
          "title": "輸入格式",
          "text": "切換英文輸入法，使用半形數字、小數點與負號；勿用全形數字、逗號小數點或混入其他符號。"
        }
      ],
      "locate": "Windows PowerShell（專案根目錄）與 Blender 5.2.1。",
      "figures": [],
      "keys": [],
      "references": [
        {
          "path": "evidence/parametric/2026-10-28-workspace-isolated-cli-v002/safe-summary-v001.json",
          "label": "假專案工作區建立與檔案登記 CLI 實證"
        },
        {
          "path": "journal/2026-10-22-lesson04-demo-v001.md",
          "label": "本次操作與讀值說明"
        }
      ],
      "figureNote": "已補查現行教材及原操作序列，未找到可獨立對應本步的實拍。"
    }
  ]
};
