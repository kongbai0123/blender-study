# 工作區語義、觀察分類與規範精簡交接 v001

2026-10-27。依本聊天轉交的使用者核准方案，由 Codex 實作，交由 Claude 審查。這是工作樹候選修改，沒有 commit、push、Blender 重跑或學員 confirm。下一位開工先讀本檔並執行 `python learning/manage.py status`，不要把本交接當作學員完成紀錄或審查核准。

## 開工狀態與分工

- 開工工作樹乾淨，HEAD 為 `4b613f47c91f8eca51cf357097670718d8d31a77`。本 clone status 為 revision 6、01-01、0 已確認、0 已登記學員檔案；原 progress SHA-256 `26130175ef80a9fb83699f93a8c33de7b098b17ffa2c10aef794808390d19325`，本次未改。
- Codex/root 唯一整合 catalog、匯入器、套用工具、候選清單與交接；分類代理只寫分類／盤點註記；前端代理只改 app.js／新增標籤與 catalog 隔離測試；編輯代理只精簡 AGENTS、保存原文與映射。沒有同時執行會重建 catalog 或 metadata 的程式。
- Claude 負責後續審查，本次沒有代其核准。共用匯入器與前端的變更，是為實作已核准的欄位與顯示修正；沒有修改 Claude 原有 01～04 劇本或舊執行器證據。原檔的作者歸屬不作寫入者判定。

## 實際變更

1. `import_run.py` 不再把 `learnerWorkspaceWrites` 寫死為 false，而是 unknown/null。`workspaceContentsUnchanged` 僅取 runner 的 `workspacesUnchanged` 布林旗標；不推論期間未寫入，也不判定寫入者。01～04 四個舊 run 一律 null，明示舊 runner 只比第一層檔名、沒有前後雜湊。舊 metadata 沒有新欄位時，直接重新匯入會拒絕，改走版本化語義註記。
2. 工作區更正另存 `workspace-semantics-v001.json`，20 個 run 中 15 個引用既有公開刪節 runner 摘要（同時綁原件／摘要 hash），四個舊示範及一個人工語言操作保持未知。沒有回填或改原 metadata、run、runner-status。公開摘要的刪節不會被誤認為原件。
3. 逐來源盤點 425 筆 catalog 事件，建立 212 筆明示分類：83 `scripted_description`、129 `mixed`；213 保留 `unclassified`。四筆已知舊選單描述全涵蓋，05～08 的 15 個正式 demo 均查來源快照／callback／helper。固定回傳文字即使先呼叫 checker，也仍屬文字描述；動態讀回與固定解說共存才混合。沒有靠句型猜讀值；純讀回未明示分類時也只稱觀察紀錄。
4. 分類綁 run ID、step、圖片 path/hash、observed 文字 hash、來源程式 path/hash/line、理由。01～04 無凍結 scenario 的限制另註明，現行程式碼不等於當次執行證據。11 筆舊人工語言圖片沒有 catalog figure hash，保持原樣且未分類，不補原欄位。
5. `apply_evidence_semantics.py` 只將註記套到 catalog，目前 42 個 operationRun／previousOperationRuns 段落、425 事件；保留所有原 action、observed、figure、輸出、幾何數值與路線內容。只加語義欄位／contentPolicy，並修正 27 處把所有結果統稱讀值的通用 contentReview 句子。預設只讀；`--write` 才更新，寫前再比 catalog bytes，衝突停止。多餘／錯誤綁定拒絕；撤回分類會移除舊來源註記。
6. 前端將固定文字標為「文字描述，請對照原圖」、混合紀錄另標；missing／unknown 只顯示「觀察紀錄」，支援明示 readback，但本次沒有將未分類強行升格。工作區欄位分一致、不同、未知，均不反推寫入者。截圖、程式讀回、幾何檢查、學員理解、實體合格各需不同依據。
7. AGENTS 30,620 → 13,540 bytes，減少 55.78%。完整舊 bytes 保存於歷史 journal，SHA-256 `746e9b231de6aeb86aec12663b943b8f4cd2bd54c00bea03a3b58bfe4c9a9cbe`。46 段映射保留全部 41 個舊 bullet／54 個非空非標題行，示範與確認位置分列，協作規則獨立 7 行。舊原文快照只屬歷史，不能取代現行規範。
8. 候選清單改產 2026-10-27 新版本，保留 2026-10-26 清單原 bytes。公開摘要若只換整理日期則沿用原版本／原 bytes；若輸入或刪節政策變更，另建 v002，不覆寫 v001。明確排除 publication-private，納入 annotations。CI 增加只讀語義核對與 Node 標籤測試；本次未推送，沒有新的 hosted CI 結果。

## 變更檔案清單

- `.github/workflows/verify.yml`
- `AGENTS.md`
- `learning/catalog.json`
- `learning/tutor/import_run.py`
- `learning/web/app.js`
- `scripts/prepare_publication.py`
- `scripts/apply_evidence_semantics.py`（新增）
- `learning/annotations/workspace-semantics-v001.json`（新增）
- `learning/annotations/observed-kinds-v001.json`（新增）
- `learning/annotations/observed-inventory-v001.json`（新增）
- `learning/annotations/agents-requirements-map-v001.json`（新增）
- `learning/tutor/tests/test_evidence_semantics.py`（新增）
- `learning/tutor/tests/test_catalog_semantics.py`（新增）
- `learning/tutor/tests/test_publication_semantics.py`（新增）
- `learning/web/tests/observation_labels.test.js`（新增）
- `learning/journal/2026-10-27-agents-history-v001.md`（新增）
- 本交接 journal（新增）
- `docs/evidence-semantics-checks-2026-10-27-v001.json`（新增）
- `docs/publication-manifest-2026-10-27.json`（新增候選清單）
- `docs/publication-paths-2026-10-27.txt`（新增候選 pathspec）

新增 journal 仍受既有 .gitignore 忽略，但納入新候選 pathspec；本次沒有 stage，審查者不能只用普通 `git diff` 判定所有新增檔案。私密驗證基線與測試暫存不列公開包。

## 驗證與可重現方式

本機使用 bundled Python 3.12.14；python／rg 不在本回合 PATH，使用完整 Python 路徑及 Python／PowerShell 搜尋。以下命令的 `python` 應換成可用的 Python 3.10 以上執行檔。

```text
python -X utf8 -m unittest discover -s learning/tests -v
python -X utf8 -m unittest discover -s learning/tutor/tests -v
node --check learning/web/app.js
node --test learning/web/tests/observation_labels.test.js
python -X utf8 scripts/apply_evidence_semantics.py
python -X utf8 scripts/prepare_publication.py --verify
```

結果與驗證邊界以 [本次驗證紀錄](../../docs/evidence-semantics-checks-2026-10-27-v001.json) 為準：server／bootstrap 30 項（28 通過、2 既有 symlink 權限跳過），tutor 完整 283 項（282 通過、1 同類跳過），前端 6 項全通過，JavaScript 語法通過。沒有以 skip 隱藏本次失敗，沒有放寬幾何 EPS。新隔離測試驗證分類綁定、防篡改、未分類回退、舊 metadata 防覆寫、catalog 窄範圍／重複驗證、原始檔 bytes/mtime 保真及公開摘要跨版本保真。

與開工基線逐項比對 1,982 個既有 evidence／工作區／progress 檔案 hash 均未變；另比較 HEAD 的 catalog，去除本次新增語義欄位及通用句修正後深層完全一致。新清單核對包含既有公開包依賴、分類來源與 hash；不要求公開包取得 private raw runner 原件。舊清單屬歷史基線，不拿舊 hash 宣稱新檔未改。

另依候選 pathspec 建立 1,134 檔的隔離公開副本，確認不含作者 progress 或任何原始 runner-status；在副本內執行 manifest verify（1,132 份檔案雜湊；兩份清單自身不自我雜湊）及語義 verify 均通過。這只驗證候選資料依賴可攜性，沒有啟動或操作學員 Blender，也沒有替新使用者確認課程。

## 過程中未交付的失敗初稿

- 第一次套用工具遇到人工語言圖的 figure 無 sha256，於寫 catalog 前停止（KeyError）。修正為舊人工圖片不補欄位、維持未分類，新增隔離回歸測試。
- 新註記初稿的部分中文字串經 PowerShell ASCII 管線變問號；校對時發現，改以明確 UTF-8 重建兩份註記與工作區註記後重新套用。事件身份／分類／圖片與文字／來源 hash 保持，修復後新增註記連續問號掃描為 0。此初稿不是釋出版本，也不是 Blender 失敗 run。
- review 發現撤回分類時可能殘留舊來源註記，已清除並加回歸測試。沒有新增／重跑失敗 Blender run。
- 新候選清單初稿曾在舊紀錄指向受限 .scratch 路徑時遇 PermissionError；改為先套路徑排除政策，不探測已排除儲存區。另一初稿曾遞迴追蹤舊清單的省略項目，擴大候選清單；已將歷史 manifest／pathspec 視為不可追依賴的存檔，重建後相較舊清單僅新增本次檔案、沒有多加 evidence。新增回歸測試涵蓋兩情境；這些初稿未提交、未推送。

## 未做與下一步

- 未重跑 Blender、未改原圖／run／舊 metadata／場景／STL，因既有證據足以完成語義修正；無新畫面或幾何驗證宣稱。
- 未更改 progress、學員狀態、檔案登記或 confirm。教學實作停在原有 08-01，學員確認仍以最新 status 為準。
- 未填材料／允許應變、實體列印／試配／改善／強度或合格值，沒有把試驗間隙升格。
- 未 commit、push、對 Claude 或其他外部服務發訊息；新 CI 工作流程只在本機修好，hosted 檢查待使用者決定推送後執行。
- 下一步由 Claude 檢查分類理由／來源映射、舊值更正界線及 AGENTS 搬移是否完整，將問題寫新交接；修改前重讀 catalog／最新檔案，不同時執行匯入或清單產生器。使用者決定是否提交與推送。
