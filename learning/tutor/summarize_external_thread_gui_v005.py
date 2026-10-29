"""Create shareable evidence: omit runner host paths and Windows Recent data."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
e = root / 'learning/evidence/08/2026-10-28-external-thread-gui-trial-v005'
run = json.loads((e / 'run.json').read_text(encoding='utf-8'))
status = json.loads((e / 'runner-status.json').read_text(encoding='utf-8'))
audit = json.loads((e / 'independent-audit-v001.json').read_text(encoding='utf-8'))
actions = [
    '程式預先建立三邊閉合輪廓並隱藏既有盒體，此步不是 GUI 手繪。',
    'GUI 新增 Screw，輸入導程 1 mm、4 圈、32 段。',
    'GUI 將修改器結果轉為網格，讀回六條開口邊。',
    'GUI 進入編輯模式並選擇非流形邊。',
    'GUI 按 F 封閉端部並讀回邊界。',
    'GUI 全選並重新計算法線。',
    'GUI 新增圓柱、縮放、移動、套用縮放並命名。',
    'GUI 初次指定布林對象；此時欄位尚未指定成功。',
    'GUI 選擇 Union、Exact、牙條，確認對象已指定。',
    'GUI 在 Outliner 隱藏牙條，保留工具物件。',
    'GUI 套用 Union；讀回尺寸與拓樸。',
    'GUI 聚焦並轉動視角，保留實際畫面。',
    'GUI 另存新檔；檔案瀏覽器欄位由程式填入。',
    'GUI 重開新檔並重新讀取幾何。',
]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
records = []
for record, action in zip(run['records'], actions, strict=True):
    path = e / record['file']
    observed = record['observed']
    try:
        observed = json.loads(observed)
    except (ValueError, TypeError):
        observed = None  # original caption text is corrupted; no inference from it
    records.append({'sequence': record['seq'], 'action': action, 'image': path.relative_to(root).as_posix(),
                    'imageSha256': sha(path), 'imageSizePx': [record['width'], record['height']], 'observed': observed})
scenario = root / 'learning/tutor/scenarios/external_thread_gui_trial_v005.py'
model = e / 'demo-files/u08_external_gui_draft_v001.blend'
source = root / 'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend'
summary = {
    'status': 'geometry draft awaiting repair; not cleared for print or as an authoritative closed screw model',
    'runnerStatus': status['status'], 'runnerExitCode': status['blenderExitCode'],
    'workspaceSnapshotUnchanged': status['workspacesUnchanged'],
    'runnerPrivacy': 'Full runner-status contains machine-local Windows Recent paths; share this summary instead.',
    'blenderVersion': run['blender'],
    'source': {'path': source.relative_to(root).as_posix(), 'sha256': sha(source)},
    'scenario': {'path': scenario.relative_to(root).as_posix(), 'sha256': sha(scenario)},
    'model': {'path': model.relative_to(root).as_posix(), 'sha256': sha(model)},
    'independentAudit': audit,
    'records': records,
    'physicalPrint': None, 'physicalMeasurements': None, 'physicalFit': None,
    'material': None, 'qualifiedClearance': None, 'qualifiedStrength': None,
    'notes': [
        '輪廓及檔案對話框填寫由程式處理；其餘建模操作為獨立 Blender 視窗 GUI 模擬事件。',
        '原始 run.json 的部分中文 action 因編碼損壞；本摘要逐項重新整理文字，不改動原始證據。',
        'BVH 的三個候選交疊及退化薄三角形尚未排除；零非流形邊不代表無自交。',
        '360 度、單頭等部分欄位為劇本設計與畫面；逐步數位讀值僅含程式明確檢查的參數，不聲稱有額外讀回。',
        '工作區前後快照一致不代表能證明期間未發生短暫寫入。',
        '本草案非 ISO 螺紋與製造合格證明。',
    ],
}
(e / 'safe-summary-v001.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote safe summary:', len(records), 'records; audit candidates:', audit['nonAdjacentTriangleOverlapPairs'])
