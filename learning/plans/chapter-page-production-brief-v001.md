# 工程教材小節頁改版：整章製作指引 v001

> **給接手的 agent**：這份文件說明如何把工程教材的每一章改成新版小節頁。請整份讀完再動手。內容以 2026-10-30 使用者確認過的 01-07 樣稿為準；樣稿與本文件衝突時，以本文件為準，並在交接中回報衝突。
>
> 一律以繁體中文撰寫內容與交接。開工前另讀專案根目錄的 `AGENTS.md`；本文件沒寫到的事項依 `AGENTS.md`。

---

## 1. 背景

- **專案**：Blender 引導式學習（`D:\others\study\Blender-Learning`）。主線是 12 章「小盒工程學習路徑」，加上第 00 章速查；每章分節，節底下是小步。現行教材是 `learning/web/engineering-curriculum-v038.json`，共 85 節、243 個主線小步。
- **問題**：現行教學頁一次只展開一個小步，右欄有 6 個分頁，原圖藏在分頁裡；每步都重複限制說明，學員要讀的東西被稀釋。
- **使用者已確認的方向**（01-07 樣稿）：
  1. 一個小節該做的事，全部排在同一頁，往下捲動依序完成。
  2. 不用勾選才能前進，也不鎖章節，想看哪一節就到哪一節。
  3. 導言只留一句重點，加上名詞標籤。
  4. 保留左側章節樹，但可收合成只有編號的窄欄。
  5. 每一步採左文字、右實拍原圖，原圖上疊加編號框。
- **你的任務**：照本文件為指定的章製作新版小節頁的**資料檔**，交給使用者審。這是草稿，不改正式教學頁與教材。

## 2. 必讀與參照檔

路徑都相對專案根目錄。

| 檔案 | 用途 |
|---|---|
| `AGENTS.md` | 專案規範；特別是「教學與真實畫面」「唯一進度與版本」「協作規則」 |
| `learning/drafts/ux-section-01-07-v001/index.html` | 已確認的樣稿頁面程式（版面、互動、樣式的標準） |
| `learning/drafts/ux-section-01-07-v001/section-data.js` | **資料格式範例**：01-07 的完整內容；寫法照它 |
| `learning/drafts/ux-section-01-07-v001/course-outline.js` | 左側章節欄用的全課程大綱（章、節、主線小步數） |
| `learning/web/engineering-curriculum-v038.json` | 現行教材：每個小步的 `actions`、`success`、`detail`、`shortcuts`、`figures`、`sourceSteps`、`demonstration` |
| `learning/catalog.json` | 原 9 單元教材：`lessons[].steps[].operationRun.events[].figure` 有完整實拍序列，含尺寸、SHA-256 與標註框座標；`help` 是原排解說明 |
| `learning/web/engineering-path-v007.json` | 章節定義與章目標 |
| `learning/journal/` | 各示範的操作紀錄；圖片的拍攝脈絡查這裡 |

## 3. 硬性限制

違反任何一條都要停下來回報，不要自行繞過。

1. **不改正式檔**：`learning/web/` 底下的檔案（教材 JSON、`app.js`、`index.html`）、`learning/server.py`、`learning/manage.py`、`learning/catalog.json` 一律不動。產出只放在第 4 節指定的草稿目錄。
2. **不碰進度**：不讀寫 `learning/progress.json`，不執行 `manage.py` 的任何寫入指令（confirm、note、register-file 等）。
3. **只用實拍**：圖片必須是 `learning/evidence/` 內真實存在的截圖。不製作示意圖、不重畫介面、不修改原圖；標註只能是疊在原圖上的座標框。
4. **不新拍示範**：不執行 `learning/tutor/run_demo.py`，也不開 Blender 產生新圖。缺圖時寫進交接，由使用者決定。
5. **不 commit、不 push**，除非使用者在對話中明確要求。
6. **不改別人的檔**：只寫自己被指派的小節檔。共用檔（`index.html`、`course-outline.js`）只由指定的負責人修改（見第 12 節）。
7. **不自行決定待決事項**（第 14 節），例如進度怎麼記。

## 4. 產出位置與檔案結構

每章一個草稿目錄：

```
learning/drafts/ux-chapter-NN-v001/
├── index.html            ← 頁面程式（由 01-07 樣稿通用化，見 4.1）
├── course-outline.js     ← 從樣稿複製，不需修改
└── sections/
    ├── NN-01.js          ← 每節一個資料檔
    ├── NN-02.js
    └── …
```

每個小節檔的寫法：

```js
// NN-NN 小節資料。來源：engineering-curriculum-v038.json（小步 ID 見各步 stepId）
window.SECTIONS = window.SECTIONS || {};
window.SECTIONS["01-07"] = {
  id: "01-07",
  title: "精確移動與撤回",
  // …其餘欄位見第 6 節
};
```

`chapter` 資訊（章號、章名、各節清單）只放在 `course-outline.js`，小節檔不重複寫。

### 4.1 頁面程式通用化（第 0 項工作，只由一位負責人做）

樣稿的 `index.html` 只會顯示一節。開始寫小節檔之前，負責人先完成以下調整：

1. 依網址 `#NN-NN` 決定顯示哪一節，沒有 hash 時顯示該章第一節；hash 改變時重新繪製，不重新載入頁面。
2. 載入 `sections/*.js`。可以在 `index.html` 依序寫死該章所有小節檔的 `<script>`，也可以動態插入；**尚未製作的節**要顯示「本節尚未製作」，不能讓頁面出錯。
3. 章、節標題與章節欄改讀 `course-outline.js`；原本 `section-data.js` 的 `chapter` 欄位刪除。
4. 章節欄、節尾「上一節／下一節」改成真的切換 hash；其他章的連結先顯示提示即可。
5. 其餘版面、樣式、互動與樣稿一致，不另行設計。

完成後截圖給使用者確認，再開放其他 agent 寫小節檔。

## 5. 頁面規格（摘要）

樣稿已實作以下規格，製作資料時要知道頁面會怎麼呈現。

**由上而下**：

1. 頂列：章節欄開關＋麵包屑。
2. 標題列：小節標題＋一句重點。
3. 名詞列：點擊才顯示定義。
4. 範圍說明：一行小字。
5. 小步目錄：「準備」「1」「2」…的錨點按鈕，點了直接捲到該步。
6. 小步卡：每張左文字、右原圖。
7. 節尾：上一節、下一節。

**左側章節欄**：

- **展開**：同現行教學頁的章節樹。
- **收合**：縮成約 64 px 的編號欄，顯示 `0、1、1.1…1.10、2…12`。目前節為橘底白字；滑鼠停留顯示完整標題；點章號可展開或收起該章節號；狀態記在瀏覽器中。
- **< 1100 px**：改成抽屜。

**響應式**：

- ≥ 1100 px：小步卡左文字（330～400 px）、右原圖。
- < 1100 px：單欄，原圖在上。
- < 640 px：縮小標題與內距。

**互動**：

- 頁面上沒有勾選框，也沒有完成按鈕。
- 點圖全螢幕放大，可隱藏標註、開啟原始圖檔，按 Esc 關閉。

## 6. 資料格式

### 6.1 小節層欄位

| 欄位 | 型別 | 規則 |
|---|---|---|
| `id` | 字串 | 節 ID，例如 `"01-07"`，必須與教材一致 |
| `title` | 字串 | 節標題，沿用教材；要改名須在交接中說明理由 |
| `keyPoint` | 字串 | 一句重點，約 30 字內，寫「做什麼＋做到什麼程度」 |
| `minutes` | 數字 | 預估分鐘數；不確定就省略，不要亂猜 |
| `glossary` | 陣列 | 3～6 個名詞，每個 `{ term, label, text }`，見 7.2 |
| `scope` | 字串 | 一句圖片性質說明，整節只寫一次 |
| `prep` | 物件 | 「開始前準備」卡，欄位同小步；沒有前置動作就省略 |
| `steps` | 陣列 | 小步卡，依教材順序 |

### 6.2 小步層欄位（`prep` 與 `steps[]` 共用）

| 欄位 | 型別 | 數量 | 規則 |
|---|---|---|---|
| `stepId` | 字串 | 1 | 教材小步 ID，例如 `"ch01-01-07-02"` |
| `title` | 字串 | 1 | 動作＋目標；必須與主要做法一致（見 7.3） |
| `lead` | 字串 | 1 | 粗體一句：這一步要做什麼（`prep` 用 `summary`） |
| `keys` | 字串陣列 | 0～3 | 主要按鍵，例如 `["Ctrl","Z"]` |
| `actions` | HTML 字串陣列 | 1～3 | 依序的操作 |
| `checks` | HTML 字串陣列 | 2～3 | 「做完應該看到」，可直接在畫面上觀察的結果 |
| `pitfalls` | 陣列 | 0～3 | `{ title, text }`：`title` 寫現象，`text` 寫原因與做法 |
| `locate` | 字串 | 0～1 | 「找不到位置？」的位置描述 |
| `alternative` | 物件 | 0～1 | `{ title, text, figure }`：另一種做法＋對照圖 |
| `figure` | 物件 | — | 只有一張圖時用（`prep` 常用） |
| `figures` | 陣列 | 1～3 | 圖片序列，見 6.3 |

### 6.3 圖片欄位

```js
{
  path: "evidence/01/2026-10-22-lesson01-demo-v001/01-07-04-location-x.png", // 相對 learning/，不含開頭的 learning/
  sha256: "37c217eb…",       // 64 字元完整雜湊
  size: [1494, 1019],         // 原圖寬、高（像素）
  tab: "輸入完成",            // 序列分頁名，2～6 字；單張圖可省略
  caption: "輸入後：側欄和右下 Properties 的 Location X 都是 0.5 m。",
  marks: [                    // 0～3 個框，依操作順序編號
    { n: 1, box: [961, 132, 190, 21], label: "側欄顯示 0.5 m" }   // [x, y, 寬, 高]，原圖像素
  ]
}
```

**注意**：教材與 catalog 中的路徑以 `learning/` 開頭；寫進資料檔時要去掉 `learning/`。

## 7. 內容寫作規則

### 7.1 通則

1. **用學員的話**：不出現 `existing_demo`、revision、證據狀態、版本號、「不表示學員完成」這類維護用語。
2. **不重複限制句**：圖片性質只在 `scope` 說一次。真的會影響操作的提醒，才寫進 `pitfalls`。
3. **介面名稱照 Blender 英文原文**（File › Save As、Item 分頁、Location X），不自行翻譯。選單路徑用「›」連接。
4. **按鍵用 `<kbd>`**：組合鍵用「+」，例如 `<kbd>Shift</kbd>+<kbd>Ctrl</kbd>+<kbd>S</kbd>`；連續按鍵用空格，例如 `<kbd>G</kbd> <kbd>X</kbd> <kbd>0.5</kbd> <kbd>Enter</kbd>`。
5. **數值、檔名、路徑用 `<code>`**，數字一律半形。
6. **不憑記憶寫 Blender 行為**：每一句操作描述都要能在教材、catalog、journal 或原圖中找到依據。找不到依據的寫法，標註在交接中，請使用者確認。

### 7.2 一句重點與名詞

- `keyPoint` 例：「用數字把 Cube 精確放到 X＝0.5 m，放錯就用 Ctrl+Z 撤回。」
- 名詞只收本節第一次出現、學員可能不懂的詞：
  - `term`：內文中要比對的字串，必須真的出現在內文裡。
  - `label`：按鈕上的顯示名稱，例如「側欄 Sidebar（N 面板）」。
  - `text`：一句白話定義，說清楚「它是什麼、在哪裡、跟什麼不同」。
- 前面章節已定義過的名詞，除非本節用法不同，否則不重複收錄。

### 7.3 小步

1. **標題與做法一致**。01-07 就是反例：現行標題寫「設為 0.5 m」（在欄位輸入，屬於絕對位置），配的卻是 `G X 0.5`（相對移動）。發現這類不一致時，主要做法以標題與原教材 `operationRun` 為準，另一種做法放進 `alternative`，並在交接中列出。
2. **前置動作移到 `prep`**：存檔、開檔、建立工作區等前置動作放「開始前準備」，不佔編號小步。`prep` 的 `stepId` 仍要對應教材的小步。
3. **`actions` 先說「在哪裡」，再說「做什麼」**，例如「滑鼠移到中間的 3D 畫面，按 <kbd>N</kbd>…」。
4. **`checks` 寫可觀察的結果**，例如「側欄 Location X 顯示 `0.5 m`」，不要寫「能說明…」「已理解…」這類無法從畫面判斷的句子。
5. **`pitfalls` 的來源依序為**：原教材的 `help`、`shortcuts[].cautions`、journal 裡的失敗案例、使用者回報。每步只挑最容易遇到的 1～3 條。
6. **需要在欄位輸入數值的步驟，都要檢查是否加上輸入格式這一條**（使用者指定）：中文輸入法打出的全形字（例如「０．５」）、用逗號當小數點、混入其他符號。
7. **`locate` 用編輯區、面板與相對位置描述**，例如「側欄在 3D Viewport 右緣，打開後右邊有直排的 Item／Tool／View 分頁」。

## 8. 原圖與標註

1. **找完整序列**：優先使用 catalog `operationRun.events[]` 的連續截圖，順序與主要做法一致。只有找不到序列時，才退而使用教材小步 `figures` 或 `demonstration.figures` 的單張圖。
2. **分配到小步**：同一個原教材步驟的事件，常常分屬好幾個新小步。例如 01-07 的事件 1 是存檔（→ `prep`）、事件 2～4 是開側欄與輸入（→ 第 1 步）、事件 5～6 是撤回（→ 第 2 步）。依每張圖的 `action` 說明來分配。
3. **標註框以 catalog 的 `highlights` 為起點，但每個框都要看原圖核對**。已知 01-07 存檔視窗的「檔名」框寬 780 px，延伸超過了 Save As 按鈕，樣稿改成 492 px。核對方式：用能顯示圖片的工具開啟原圖，確認框真的框住目標。
4. **每張圖最多 3 個框**：
   - 標籤 8 字內，寫「是什麼」或「要做什麼」。
   - 範圍過大的框（例如框住整個側欄）改框到真正要看的欄位。
   - 貼近上緣（y < 16）的框，頁面會自動把編號移到右側。
   - 兩個框太近、編號互相遮擋時，在 `caption` 寫清楚位置。
5. **序列分頁名**（`tab`）用動作或狀態，例如「打開側欄 → 找到欄位 → 輸入完成」。
6. **`sha256` 與 `size`**：catalog 有就直接沿用；沒有就用以下指令計算（在專案根目錄執行）：

   ```bash
   python -c "import hashlib,struct,sys; b=open(sys.argv[1],'rb').read(); print(struct.unpack('>II',b[16:24]), hashlib.sha256(b).hexdigest())" learning/evidence/<路徑>.png
   ```

   這行只適用 PNG。
7. **缺圖**：某步完全沒有可用實拍時，`figures` 留空陣列，並在交接中列出，不要借用不相干的圖。

## 9. 每節製作流程

**第 1 步：列出本節小步與可用原圖。** 在專案根目錄執行以下指令（把 `SEC` 改成目標節）：

```bash
python -X utf8 - <<'EOF'
import json
SEC = "01-07"
cur = json.load(open("learning/web/engineering-curriculum-v038.json", encoding="utf-8"))
cat = json.load(open("learning/catalog.json", encoding="utf-8"))
legacy = {s["id"]: s for l in cat["lessons"] for s in l["steps"]}
seen = set()
for ch in cur["chapters"]:
    for st in ch["steps"]:
        if st.get("section") != SEC or st.get("track") in ("optional", "appendix", "pending", "reference"):
            continue
        print("==", st["id"], st["title"])
        print("   actions:", st["actions"])
        print("   success:", st["success"])
        print("   detail :", st.get("detail"))
        for sc in st["shortcuts"]:
            print("   shortcut:", sc["keys"], "| cautions:", sc.get("cautions"))
        for f in st["figures"] + (st.get("demonstration") or {}).get("figures", []):
            print("   figure:", f["path"])
        for src in st["sourceSteps"]:
            step = legacy.get(src["stepId"]) or {}
            if src["stepId"] in seen:
                continue
            seen.add(src["stepId"])
            print(f"   [原教材 {src['stepId']}] help:", step.get("help"))
            for ev in (step.get("operationRun") or {}).get("events", []):
                fig = ev.get("figure")
                if fig:
                    hl = [(h["x"], h["y"], h["w"], h["h"], h["label"]) for h in fig.get("highlights", [])]
                    print(f"     #{ev['seq']} {ev['action']}\n        {fig['path']} {fig['width']}x{fig['height']} {fig['sha256']}\n        highlights={hl}")
EOF
```

**第 2 步：看圖。** 逐張開啟上一步列出的原圖，確認畫面內容與 `action` 說明一致，並判斷每張圖該分給哪一個新小步。

**第 3 步：核對做法。** 確認每個小步的標題、主要做法和原圖是同一種操作；不一致的記下來（見 7.3 第 1 條）。

**第 4 步：寫小節層。** 依 6.1 與 7.2 寫 `keyPoint`、`glossary`、`scope`。

**第 5 步：寫小步。** 依 6.2 與 7.3 寫 `prep` 與 `steps`。

**第 6 步：標註。** 依第 8 節，逐張核對或量取框座標，寫上標籤與 `caption`。

**第 7 步：存檔。** 寫入 `learning/drafts/ux-chapter-NN-v001/sections/NN-NN.js`。

**第 8 步：驗證。** 依第 10 節檢查。

## 10. 驗證

**啟動預覽服務**（在 `learning/` 目錄執行，保持在背景）：

```bash
python -m http.server 8790 --bind 127.0.0.1
```

開啟 `http://127.0.0.1:8790/drafts/ux-chapter-NN-v001/index.html#NN-NN`。

不要用 `file://` 直接開：部分預覽環境只顯示靜態快照，不會執行程式。

**截圖**（Windows，用無頭 Edge，在 PowerShell 執行）：

```powershell
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$out  = "<你的暫存資料夾>"
& $edge --headless=new --disable-gpu --hide-scrollbars "--user-data-dir=$out\edge-profile" --window-size=1366,768 "--screenshot=$out\NN-NN-1366.png" "http://127.0.0.1:8790/drafts/ux-chapter-NN-v001/index.html#NN-NN"
& $edge --headless=new --disable-gpu --hide-scrollbars "--user-data-dir=$out\edge-profile" --window-size=1366,2600 "--screenshot=$out\NN-NN-full.png" "http://127.0.0.1:8790/drafts/ux-chapter-NN-v001/index.html#NN-NN"
```

無頭 Edge 的視窗寬度似乎有下限（約 500 px），比這更窄的截圖會失真。窄畫面要用瀏覽器實際縮窄視窗來檢查。

**逐項檢查**：

- [ ] 1366×768 第一屏可以看到：標題、名詞列，以及第一張小步卡原圖的上半部。
- [ ] 每個標註框都框在正確目標上，編號沒有互相遮擋到看不出是哪一個。
- [ ] 圖例、`caption` 與框的內容一致。
- [ ] 每個 `glossary.term` 都在內文中出現，且頁面上有虛線底線。
- [ ] 每張圖都載入成功（沒有破圖），點圖可以放大，Esc 可以關閉。
- [ ] 任何寬度都沒有橫向捲動。
- [ ] 瀏覽器主控台沒有錯誤。

## 11. 完成定義

一節符合以下所有條件才算完成：

- [ ] 小節檔放在指定路徑，格式符合第 6 節。
- [ ] 教材中該節所有主線小步都有對應，`stepId` 完整且正確（含 `prep`）。
- [ ] 每張圖都是 `learning/evidence/` 內的實拍，`path`、`sha256`、`size` 正確。
- [ ] 第 10 節的檢查全部通過，並保留 1366 寬的截圖。
- [ ] 不一致、缺圖、找不到依據的寫法，全部列入交接。
- [ ] 第 3 節的硬性限制都沒有違反。

## 12. 分工與並行

1. **第 0 項工作**（4.1 頁面程式通用化）由一位負責人完成，並經使用者確認後，才開始寫小節檔。
2. **推廣順序**：先做第 01 章 10 節，經使用者審過後再做其他章；不要一次鋪開到全部 12 章。
3. **並行**：可以多個 agent 同時做同一章的不同節，但每位只寫自己的 `sections/NN-NN.js`。`index.html` 與 `course-outline.js` 只有負責人能改；需要調整時寫進交接，由負責人處理。
4. **名詞一致性**：同一章的名詞由負責人在全部完成後統一檢查，消除重複與用詞不一致。
5. **審查**：依 `AGENTS.md`「協作規則」，每輪由使用者指定實作者與審查者；審查者照第 10、11 節獨立核對。

## 13. 交接

每位 agent 收工時，在 `learning/journal/` 新增交接檔，命名為 `YYYY-MM-DD-ux-chapter-NN-<你負責的節>-v001.md`，內容包含：

1. **完成的節**與檔案路徑。
2. **做法與標題不一致**之處：節、小步、現行寫法、你採用的寫法、理由。
3. **缺圖或圖文不符**的小步。
4. **找不到依據的寫法**：需要使用者確認的句子。
5. **標註框修正**：與 catalog `highlights` 不同的框，以及修改原因。
6. **驗證範圍**：做了哪些檢查、截圖存放位置、哪些沒有檢查到。
7. **建議使用者決定的事項**。

## 14. 待決事項

以下事項由使用者決定，agent 不自行處理：

1. **進度記錄**：拿掉確認動作後，`progress.json`、章節欄的「0 / N 小步已確認」，以及聊天接續的「下一小步」要怎麼處理。草稿頁面先照樣稿顯示「0 / N」。
2. **用詞審查**：名詞定義與常見失誤由使用者逐節細查。
3. **接入正式頁面**：依 `AGENTS.md`，要由教材 builder 出新版本並附測試。新增欄位（`keyPoint`、`glossary`、`prep`、`pitfalls`、`locate`、`marks` 等）如何納入教材格式另行決定。
4. **第 00 章速查與第 08、11 章的選修／附錄步驟**：本指引只處理主線小步；這些步驟怎麼呈現另行決定。

## 15. 範例：01-07 前後對照

| 項目 | 現行 v038 | 新版（樣稿） |
|---|---|---|
| 呈現 | 一步一頁展開，右欄 6 個分頁 | 3 張卡排在同一頁，左文右圖 |
| 導言 | 章頁長段說明 | 一句重點＋5 個名詞標籤 |
| 存檔步驟 | 第 1 個小步，需要確認 | 「開始前準備」卡 |
| 原圖 | 藏在「原圖」分頁 | 直接顯示，含編號框與圖例 |
| 第 1 步配圖 | `G X 0.5` 的快捷鍵測試圖 | catalog 原序列三張；`G X` 移到「另一種方法」 |
| 快捷鍵陷阱 | 快捷鍵分頁裡 4 條注意事項之一 | 常見失誤 3 條，含使用者補充的輸入格式問題 |
| 「找不到按鈕」 | 原教材排解說明 | 實際位置描述 |
| 限制說明 | 每步重複一句 | 整節一行範圍說明 |
| 完成 | 填寫文字框後按確認 | 不需操作 |

完整內容請直接看 `learning/drafts/ux-section-01-07-v001/section-data.js`。

## 附錄：已知陷阱

- **`[hidden]` 被覆蓋**：元素有 `display:flex` 這類樣式時，`hidden` 屬性會失效；樣式表要加上 `[hidden]{display:none!important}`。
- **背景分頁的圖片**：在背景分頁中，`img.decode()` 可能一直不結束，自動測試不要等它。
- **鍵盤事件**：鍵盤處理程式中，`e.target` 可能是 `document`，沒有 `closest()`，呼叫前要先檢查。
- **瀏覽器儲存**：`localStorage` 在部分環境會丟出錯誤，讀寫都要包在 `try/catch` 裡。
- **單位**：第 01 章的練習場景使用公尺（Unit Scale 1）；毫米工作檔從第 03 章「建立毫米工作檔」開始，但並非每一節都用毫米場景。寫數值與單位前，先看該節原圖與教材中實際顯示的單位。
