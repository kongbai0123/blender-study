"""Extend v003 with the verified open Screw surface without mutating prior steps."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V003 = ROOT / 'learning/web/engineering-curriculum-v003.json'
V004 = ROOT / 'learning/web/engineering-curriculum-v004.json'
EXPECTED_V003 = '0a708e4c1cb06f524db4acb3d09412ce3adb6ba66e1a99fe3bb7f30897faf9cf'
EVIDENCE = 'learning/evidence/08/2026-10-27-lesson08-screw-surface-v001/'
SUMMARY_SHA = '4b99e788095da7a0f6a7f9da47ca4d4ee4d79aca50328037434c0b81193b2886'
SCENE_SHA = 'fd61943b6199f9131ff34ef4ed21dc802884cf642356e58becbae9c75c4c7601'


def reference(rel, expected, label):
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('source escapes project')
    found = hashlib.sha256(path.read_bytes()).hexdigest()
    if found != expected:
        raise ValueError('source hash mismatch: ' + rel)
    return {'path': rel, 'sha256': found, 'label': label}


def image(name, expected, caption):
    item = reference(EVIDENCE + name, expected, caption)
    return {'type': 'screenshot', 'path': item['path'], 'sha256': item['sha256'], 'caption': caption}


def main():
    before = V003.read_bytes()
    if hashlib.sha256(before).hexdigest() != EXPECTED_V003:
        raise ValueError('v003 differs from the documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary = reference(EVIDENCE+'screw-surface-verification-v001.json', SUMMARY_SHA, '螺旋曲面實際操作與數位驗證摘要')
    scene = reference(EVIDENCE+'demo-files/u08_screw_surface_v001.blend', SCENE_SHA, '螺旋開放曲面場景 v001（示範原檔）')
    common = [
      '這是自訂任意數值的單線曲面示範，不代表已選 ISO 牙型、尺寸或公差。',
      '牙型輪廓和原盒的顯示狀態由程式準備；新增修改器和欄位設定才是獨立 Blender GUI 原生事件。',
      '結果有260條開放邊、無軸心與端封；不是閉合可列印實體，不能推定強度、配合或試鎖合格。',
      '沒有對件、有效嚙合、材料、切片、實際列印或試鎖結果；本示範不代表學員已完成。',
    ]
    examples = [
      ('profile','觀察程式建立的輪廓','辨認掃掠輸入','來源盒副本中的 Thread_Profile；Object Mode。原盒在示範中被程式隱藏。',
       '觀察程式建立的開放牙型線：半徑 5→6→5 mm、Z 0→0.3→0.6 mm。',
       '實際讀回三個頂點與兩條邊；輪廓並非 GUI 手工建立，圖中線條較小，可配合摘要查讀值。',
       '08-02-01-profile.png','f78222403bfbff0e5acf3e2fc35d0d34a86b565fb00241d417e3063c470f420b','程式建立輪廓後的獨立 Blender 原圖；不是 GUI 手工繪線。'),
      ('add-screw','以 F3 加入 Screw 修改器','辨認開啟修改器的實際操作','Object Mode；3D Viewport 聚焦，作用中為沒有 Screw 修改器的 Thread_Profile。',
       '觀察示範：按 F3 搜尋 Add Screw Modifier，選取搜尋結果。',
       '實際畫面可見 Screw 修改器：預設 Angle 360°、Screw 0 mm、Iterations 1；此時尚未形成有軸向位移的螺旋。',
       '08-02-02-screw-added.png','45bc678aa905d24ce39853fe2fc5b122c25d39e1e92e135632de78ff66618a91','獨立 Blender 原圖：F3 操作後的 Screw 預設欄位。'),
      ('lead','設定每轉軸向位移','區分 Screw 值與導程條件','選取 Thread_Profile；Properties > Modifiers > Screw。',
       '觀察示範：在 Screw 欄位輸入 1 mm，確認 Angle 360°、Z 軸且 Object Screw 關閉。',
       '在這個360°、單線、Object Screw關閉的例子，每轉導程為1 mm，單線的名義螺距也為1 mm。',
       '08-02-03-lead-one.png','edba095de3711a1056698d23338060d4e63ea06fab909b4ee320de84b2a910b1','獨立 Blender 原圖：Screw 欄位為1 mm，當時 Iterations 為1。'),
      ('iterations','設定四次掃掠','區分重複次數與螺紋線數','Properties > Modifiers > Screw；Angle 360°、Screw 1 mm。',
       '觀察示範：將 Iterations 設為4。',
       '此例為同一條單線螺旋掃掠4圈，軸向位移4 mm；Iterations 不是線數。',
       '08-02-04-four-iterations.png','5b0b187bdb70d5653b3e4f55546c45b443881ef3ad87f6aecb6bdc5198566af0','獨立 Blender 原圖：Iterations 4、Angle 360°、Screw 1 mm。'),
      ('resolution','設定視窗與渲染分段','辨認分段影響','Properties > Modifiers > Screw。',
       '觀察示範：將 Steps Viewport 與 Render 各設為32。',
       '兩欄各顯示32；此例 Angle 360°，故每次整圈採樣32段；平滑著色不會增加幾何分段。',
       '08-02-05-resolution.png','233ba945c72f6831e3c70a58c0d38c2d9606d6ae2a22df6dabb5b055fca41f8c','獨立 Blender 原圖：Viewport 與 Render Steps 各為32。'),
      ('inspect','檢查曲面與開放邊','以數位證據分清外觀與閉合性','獨立 Blender 的 Thread_Profile 已套用螺旋修改器顯示結果。',
       '觀察放大的曲面與修改器設定，再參考數位驗證摘要中的邊界數。',
       '程式讀回260條開放邊；軸向掃掠4 mm、整件外框約4.6 mm，沒有可計算的有效嚙合。',
       '08-02-06-surface-verified.png','fc1e42f175dc35f297efa4c07064f7366ca0e84ec0615d7e9a77f6a8df50836b','獨立 Blender 原圖：放大曲面；開放邊數由程式讀回，不能只憑圖片量出。'),
      ('save','另存版本','保留原盒與螺紋參照','File > Save As；示範的檔案路徑與名稱由程式填入，確認為GUI事件。',
       '觀察示範另存為 u08_screw_surface_v001.blend。',
       '安全摘要記錄新場景版本與SHA-256；原盒與原螺紋參照沒有被覆寫。',
       '08-02-07-saved.png','44a0079d9beea54eab1e74fe85f743ff9c10b39510a8d1552564372f1d229b44','獨立 Blender 原圖：已另存後的曲面與欄位，保存結果另由檔案雜湊核對。'),
      ('reopen','重開並核對','驗證保存結果','重開示範 v001 場景；Properties > Modifiers > Screw。',
       '觀察重開後的修改器設定，再對照安全摘要中的讀值。',
       '重開後360°／1 mm／4次／32段和260條開放邊的數位檢查仍通過；這不是實體合格。',
       '08-02-08-reopened.png','4c6b6f2d96bb5fd7de8a3529355198233a42cef8911da6a4e1c98bd499147314','獨立 Blender 原圖：重新開啟後的曲面與修改器欄位。'),
    ]
    added = []
    for ident, title, goal, context, action, success, img, img_hash, caption in examples:
        fig = image(img, img_hash, caption)
        entry = {'id':'ch10-screw-surface-'+ident, 'title':title, 'goal':goal, 'context':context,
                 'actions':[action], 'success':success, 'shortcuts':[], 'figures':[fig], 'sourceSteps':[],
                 'evidenceStatus':'existing_demo', 'limitations':list(common)}
        if ident == 'profile':
            entry['artifacts'] = [scene, summary]
        if ident == 'add-screw':
            entry['limitations'].append('下載場景已包含 Screw 修改器；如要重做本步，需另建無修改器的輪廓副本，目前未提供獨立起始輪廓檔。')
            entry['shortcuts'] = [{'keys':'F3 → Add Screw Modifier', 'effect':'開啟搜尋並選擇 Screw 修改器。',
                'requirements':['Object Mode，3D Viewport 聚焦，作用中為沒有該修改器的輪廓物件。'],
                'cautions':['搜尋結果依實際介面判斷；不能在成品上重複新增而宣稱與原示範相同。'],
                'evidence':[{'path':fig['path'],'sha256':fig['sha256'],'method':'native_events_and_readback','label':'獨立 Blender 新增修改器後原圖'}]}]
        if ident in ('save','reopen'):
            entry['limitations'].append('檔案瀏覽器路徑與檔名由程式填入，確認則由 GUI 原生事件送出。')
        added.append(entry)
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch10')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if any(s['id'] in old_ids for s in added):
        raise ValueError('new IDs conflict with existing steps')
    chapter['steps'].extend(added)
    chapter['limitations'] = [
        '08-01 是規格與參數紀錄；原08-02待實作文字保留歷史狀態，v004另補獨立開放曲面實拍；完整可列印螺紋與08-03～08-05仍待實作。',
        'Angle 360° 且 Object Screw 關閉時 Screw 對應導程；僅單線時導程等於螺距。',
    ]
    data['version'] = 'v004 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v004補入非標準開放螺旋曲面實證，原學員事件仍沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v003.json', 'sha256':EXPECTED_V003},
                                   {'path':summary['path'], 'sha256':summary['sha256']}])
    data['screwSurfaceVerification'] = {'summary':summary, 'scene':scene, 'scope':'自訂單線開放曲面；程式建立輪廓、GUI 新增及設定修改器、另存重開。',
        'physicalMeasurements':None, 'fitResults':None, 'qualifiedClearanceMm':None, 'strengthQualified':None}
    data['contentReview']['supplementV004'] = '08-02只示範開放曲面；程式輪廓與 GUI 修改器操作分開；未形成可列印件。'
    if V004.exists():
        raise FileExistsError('refusing to overwrite v004')
    if V003.read_bytes() != before:
        raise ValueError('v003 changed during build')
    V004.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {V004}: {sum(len(c['steps']) for c in data['chapters'])} microsteps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
