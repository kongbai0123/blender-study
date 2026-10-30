// 01-07 小節頁樣稿的呈現資料。文字、標註座標與來源都寫在這裡，頁面程式只負責排版。
// 原圖全部來自 learning/evidence 的獨立 Blender 示範；標註框是疊在原圖上的座標框，不修改原圖。
// 座標以原圖像素記錄（x, y, w, h），頁面換算成百分比。
window.SECTION = {
  prototype: "ux-section-01-07-v001",
  basedOn: { curriculum: "engineering-curriculum-v038.json", section: "01-07" },
  chapter: {
    id: "ch01", number: "01", title: "基本操作與小盒用途",
    // 小節清單取自 engineering-curriculum-v038.json；樣稿只有 01-07 有內容
    sections: [
      { id: "01-01", title: "開啟 Blender 並確認畫面" },
      { id: "01-02", title: "介面切換為 English (US)" },
      { id: "01-03", title: "準備自己的練習場景" },
      { id: "01-04", title: "第一次另存 v001" },
      { id: "01-05", title: "選取物件與 Object Mode" },
      { id: "01-06", title: "視角與找回物件" },
      { id: "01-07", title: "精確移動與撤回" },
      { id: "01-08", title: "Dimensions 與 Scale" },
      { id: "01-09", title: "保存 v002 並重新開啟" },
      { id: "01-10", title: "認識要做的小盒" }
    ]
  },
  id: "01-07",
  title: "精確移動與撤回",
  minutes: 5,
  neighbors: { prev: { id: "01-06", title: "視角與找回物件" }, next: { id: "01-08", title: "Dimensions 與 Scale" } },
  keyPoint: "用數字把 Cube 精確放到 X＝0.5 m，放錯就用 Ctrl+Z 撤回。",
  scope: "圖片都是助教在另一個獨立 Blender 的示範畫面，用來對照位置；你的畫面以自己的 Blender 為準。",
  glossary: [
    { term: "Location", label: "Location（位置）", text: "物件原點在場景中的座標，分 X、Y、Z 三個數字。在欄位裡輸入數字，是直接指定「最後要停在哪裡」。" },
    { term: "相對移動", label: "相對移動", text: "從目前位置「再移動多少」。按 G → X → 0.5 就是相對移動，起點不同，結果就不同。" },
    { term: "側欄", label: "側欄 Sidebar（N 面板）", text: "3D Viewport 右側可以開關的面板。Item 分頁的 Transform 會列出選取物件的位置、旋轉、縮放。" },
    { term: "Undo", label: "Undo（撤銷）", text: "撤回最近一個操作，可以連按往回退。它不是回到舊的檔案版本。" },
    { term: "檢查點", label: "檢查點", text: "另存後就不再修改的版本檔，例如 v001。練習改壞了可以回去重開。" }
  ],
  prep: {
    stepId: "ch01-01-07-01",
    title: "開始前：另存工作檔 v002",
    summary: "先換到新檔再練習，v001 就一直是乾淨的檢查點。",
    actions: [
      "按 <kbd>Shift</kbd>+<kbd>Ctrl</kbd>+<kbd>S</kbd>，或從 File › Save As 開啟存檔視窗。",
      "資料夾保持 <code>learning/workspaces/01/</code>，檔名改成 <code>u01_basics_v002.blend</code>，按 Save As。"
    ],
    checks: [
      "存檔視窗的資料夾路徑在 <code>workspaces\\01</code>",
      "畫面底部或標題列出現 <code>u01_basics_v002.blend</code>"
    ],
    figure: {
      path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-01-save-as-v002.png",
      sha256: "b9f8d823d0c07e644ead5b4081c794d2a2d4d7f806610ff84d4f18b68b3f949f",
      size: [1060, 600],
      caption: "Save As 視窗：上方是資料夾路徑，左下是檔名，右下是 Save As 按鈕。",
      marks: [
        { n: 1, box: [393, 6, 321, 29], label: "資料夾路徑" },
        { n: 2, box: [246, 565, 492, 28], label: "檔名改成 v002" },
        { n: 3, box: [787, 565, 130, 28], label: "按 Save As" }
      ]
    }
  },
  steps: [
    {
      stepId: "ch01-01-07-02",
      title: "把 Location X 設為 0.5 m",
      lead: "打開側欄，在 Location X 輸入 0.5。",
      keys: ["N"],
      actions: [
        "滑鼠移到中間的 3D 畫面，按 <kbd>N</kbd>（或 View › Sidebar）打開側欄，切到 Item 分頁。",
        "在 Location X 欄位上<strong>點兩下</strong>進入輸入，打 <code>0.5</code>，按 <kbd>Enter</kbd>。"
      ],
      checks: [
        "側欄 Location X 顯示 <code>0.5 m</code>",
        "Cube 沿紅色 X 軸方向移動了一段"
      ],
      pitfalls: [
        { title: "按 N 沒反應", text: "N 只對滑鼠下方的編輯區有效。先把滑鼠移進中間的 3D 畫面再按。" },
        { title: "打字後 Cube 跑掉或選單跳出", text: "欄位沒有進入輸入狀態時打字，按鍵會被當成快捷鍵。先在欄位上點兩下，看到游標再輸入；打錯就按 <kbd>Esc</kbd> 取消這次輸入。" },
        { title: "按 Enter 後數值沒變", text: "可能是輸入格式有問題：中文輸入法打出的全形字（例如「０．５」）、用逗號當小數點，或混入其他符號。切回英文輸入法，重新輸入半形的 <code>0.5</code>。" }
      ],
      locate: "側欄在 3D Viewport 右緣，打開後右邊會有直排的 Item／Tool／View 分頁。Location 在 Item 分頁最上方的 Transform 裡。",
      figures: [
        {
          path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-02-view-sidebar.png",
          sha256: "7c2aa6418bc22092bd1ec89d617e99692402f9a8c5a5f669055b65c550b34bb9",
          size: [1494, 1019],
          tab: "打開側欄",
          caption: "沒有 N 鍵時：3D Viewport 的 View 選單 › Sidebar。底部可以看到剛才另存的 v002 檔名。",
          marks: [
            { n: 1, box: [165, 28, 37, 20], label: "View 選單" },
            { n: 2, box: [170, 71, 250, 20], label: "Sidebar（快捷鍵 N）" },
            { n: 3, box: [620, 997, 232, 21], label: "另存 v002 的提示" }
          ]
        },
        {
          path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-03-sidebar-open.png",
          sha256: "eed3b7670df49679c43ef14b9ad26a511e4dc78254bf2752a5b16bbef6e3d458",
          size: [1494, 1019],
          tab: "找到欄位",
          caption: "側欄打開後，在 Item 分頁找到 Location X，目前是 0 m。",
          marks: [
            { n: 1, box: [1204, 84, 20, 40], label: "Item 分頁" },
            { n: 2, box: [961, 132, 190, 21], label: "Location X 欄位" }
          ]
        },
        {
          path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-04-location-x.png",
          sha256: "37c217ebbf340bb551c76d0f299e7ebaac6f85677055dc19b81c92f21d61d243",
          size: [1494, 1019],
          tab: "輸入完成",
          caption: "輸入後：側欄和右下 Properties 的 Location X 都是 0.5 m。",
          marks: [
            { n: 1, box: [961, 132, 190, 21], label: "側欄顯示 0.5 m" },
            { n: 2, box: [1350, 339, 87, 21], label: "Properties 也同步" }
          ]
        }
      ],
      alternative: {
        title: "另一種方法：G → X → 0.5",
        text: "在 3D 畫面依序按 <kbd>G</kbd> <kbd>X</kbd> <kbd>0.5</kbd> <kbd>Enter</kbd> 也能移動，但這是<strong>相對移動</strong>：從目前位置再移 0.5。起點是 0 時兩種方法結果相同；下圖示範起點是 1 m，結果變成 1.5 m。",
        figure: {
          path: "evidence/01/2026-10-27-shortcuts-demo-v001/01-07-05-translate-x-from-one.png",
          sha256: "4b2597d510ca80aeb4b986b660482a44dec5441d9bfd464ea8aa7bd052e04f02",
          size: [1494, 1019],
          caption: "起點 X＝1 m 時按 G → X → 0.5 → Enter，結果是 1.5 m。",
          marks: [
            { n: 1, box: [961, 132, 190, 21], label: "1 + 0.5 = 1.5 m" },
            { n: 2, box: [62, 894, 162, 25], label: "剛才的 Move 操作" }
          ]
        }
      }
    },
    {
      stepId: "ch01-01-07-03",
      title: "撤回這次移動",
      lead: "按 Ctrl+Z，讓 Cube 回到 0。",
      keys: ["Ctrl", "Z"],
      actions: [
        "按 <kbd>Ctrl</kbd>+<kbd>Z</kbd> 一次，或從上方 Edit › Undo。",
        "看側欄 Location X 回到移動前的值。"
      ],
      checks: [
        "側欄 Location X 回到 <code>0 m</code>",
        "Cube 回到原本的位置"
      ],
      pitfalls: [
        { title: "按一次沒回到 0", text: "Undo 撤回的是「最近一個操作」。中間若做了別的，要多按幾次；Edit › Undo History 可以看清單。" },
        { title: "想用 Undo 救回舊檔", text: "Undo 只在這次開啟的工作階段內有效，不會回到 v001。要回到舊版本，請重新開啟檢查點檔案。" }
      ],
      locate: "Edit 在最上排選單、File 的右邊；打開後第一項就是 Undo。",
      figures: [
        {
          path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-05-edit-undo-menu.png",
          sha256: "a322cbd6bb3ce61bc9a0151c0d21ca198704301322fd4faf31897e0f9b2f48ae",
          size: [1494, 1019],
          tab: "Edit › Undo",
          caption: "撤回前：Location X 還是 0.5 m；Edit 選單第一項是 Undo（Ctrl Z）。",
          marks: [
            { n: 1, box: [61, 3, 30, 20], label: "Edit 選單" },
            { n: 2, box: [64, 26, 199, 20], label: "Undo" },
            { n: 3, box: [961, 132, 190, 21], label: "撤回前 0.5 m" }
          ]
        },
        {
          path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-06-undone.png",
          sha256: "39d3c87192e30ec0acbcdd2a1450560e7a4b2d615c6e9ff2f0003f2738e68a9c",
          size: [1494, 1019],
          tab: "撤回完成",
          caption: "撤回後：Location X 回到 0 m，Cube 回到原位。",
          marks: [
            { n: 1, box: [961, 132, 190, 21], label: "回到 0 m" }
          ]
        }
      ]
    }
  ]
};
