"""Append real box rendering evidence to v006, preserving every prior step."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V006 = ROOT / 'learning/web/engineering-curriculum-v006.json'
V007 = ROOT / 'learning/web/engineering-curriculum-v007.json'
EXPECTED_V006 = 'ae76637b949603e9e213c1f1f8237e0c2a8127e8ae77ab1717474bd76bb76a9e'
EVIDENCE = 'learning/evidence/12/2026-10-27-engineering-box-render-v004/'
SUMMARY_SHA = '652a6369f040354d25340e22667388e0d717318f3bb64724e855b623a07afbaf'
SCENE_SHA = 'db03247077da659ff4c4a0a5ac411e7662ab326fb6302e58496e1636f69246de'
RENDER_SHA = '71f81543cc96a7b4187521b990c7e22b572ab6b27c6025a50671c32d74b1bba1'


def ref(rel, expected, label, kind=None):
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('source escapes project')
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError('source hash mismatch: ' + rel)
    result = {'path':rel, 'sha256':actual, 'label':label}
    if kind:
        result['type'] = kind
    return result


def image(name, expected, caption):
    item = ref(EVIDENCE + name, expected, caption)
    return {'type':'screenshot', 'path':item['path'], 'sha256':item['sha256'], 'caption':caption}


def main():
    before = V006.read_bytes()
    if hashlib.sha256(before).hexdigest() != EXPECTED_V006:
        raise ValueError('v006 differs from the documented baseline')
    data = json.loads(before.decode('utf-8-sig'))
    if data.get('id') != 'engineering-curriculum-v002':
        raise ValueError('unexpected stable curriculum ID')
    summary = ref(EVIDENCE+'box-render-verification-v004.json', SUMMARY_SHA, '小盒渲染操作、幾何與輸出路徑讀值摘要', 'verification-json')
    scene = ref(EVIDENCE+'demo-files/engineering_box_render_v001.blend', SCENE_SHA, '小盒分離展示的渲染場景 v001', 'scene-blend')
    rendered = ref(EVIDENCE+'demo-files/box_lid_render_v001.png', RENDER_SHA, '640×480 渲染輸出 PNG（不是介面截圖）', 'render-output-png')
    prepared = image('12-01-01-prepared.png', '2d41fb41da7934191bcbad6f4a89ca2202bc8bae89d366646cca563d2e66dc6e', '獨立 Blender 原始截圖：程式完成佈景後的視窗；上蓋為展示暫抬高18 mm。')
    render_window = image('12-01-03-render-result.png', 'f89eed44b64ccc6d363f5388137a473172fe8a2d6ae9494e60c9475d5b89fda4', '獨立 Blender 原始截圖：原生 Render Image 後的 Render Result 視窗；不是輸出的640×480 PNG。')
    common = [
      '材質、燈光、相機、地板及上蓋上移18 mm由程式設定；Render Image 是原生 GUI 事件，並非完整手工佈景教學。',
      '上蓋抬高是分離展示，不是名義裝配位置；外觀、色彩或渲染不能證明尺寸配合、材料或實體強度。',
      'Render Result 以程式 save_render 存為640×480 PNG；輸出PNG是渲染成果，不是 Blender 介面截圖。',
      '原盒與原蓋網格與來源場景相同；實體列印、量測、試配與合格間隙仍無結果，示範不代表學員完成。',
      '場景輸出 //render_output/box_lid 相對於目前 .blend 位置；先複製或另存到個人工作區，再核對 Output Properties 輸出路徑，直接開證據原檔仍可能寫入 evidence。',
    ]
    added = [
      {'id':'ch12-box-render-safe-copy','title':'先另存個人場景並核對輸出','goal':'保護示範檔與輸出位置','context':'開啟示範場景後，File > Save As，選自己的工作區與未使用的新檔名。',
       'actions':['先將場景另存至個人工作區，再到 Output Properties 核對輸出路徑也在個人工作區。'],
       'success':'自己的 .blend 與解析後輸出目的地都在個人工作區；不得以示範 evidence 作為自己的輸出目的地。',
       'shortcuts':[],'figures':[],'sourceSteps':[],'evidenceStatus':'draft_pending_demo','limitations':list(common)+['本步是個人操作指引；尚未取得使用者實際另存與路徑核對的證據。'],'artifacts':[scene,rendered,summary]},
      {'id':'ch12-box-render-prepare','title':'觀察小盒分離展示','goal':'區分展示位置與工程模型','context':'獨立 Blender；Object Mode；展示場景由程式設定，來源為05-05盒與蓋。',
       'actions':['觀察盒口、向上暫移18 mm的上蓋，以及相機取景範圍。'],
       'success':'原始視窗可見盒與蓋分離；來源與渲染場景的原盒、原蓋網格一致由獨立數位檢查核對。',
       'shortcuts':[],'figures':[prepared],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(common)},
      {'id':'ch12-box-render-image','title':'執行 Render Image','goal':'辨認 Blender 渲染結果視窗','context':'獨立 Blender 已有示範佈景；Render 選單。',
       'actions':['觀察示範以 GUI 事件選擇 Render > Render Image，並查看 Render Result。'],
       'success':'Blender 原生 Render Result 視窗顯示分離的小盒與上蓋；渲染完成事件在摘要中另有讀值。',
       'shortcuts':[],'figures':[render_window],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(common)},
      {'id':'ch12-box-render-output','title':'區分介面截圖與渲染輸出','goal':'追溯圖片與場景版本','context':'Render Result 與本步附的場景、PNG、驗證摘要。',
       'actions':['對照 Blender 視窗截圖、640×480 渲染輸出 PNG 與其來源場景版本。'],
       'success':'能指出哪個是 GUI 截圖、哪個是程式保存的 Render Result PNG；兩者各自有檔案雜湊。',
       'shortcuts':[],'figures':[render_window],'sourceSteps':[],'evidenceStatus':'existing_demo','limitations':list(common)},
    ]
    chapter = next(c for c in data['chapters'] if c['id'] == 'ch12')
    old_ids = {s['id'] for c in data['chapters'] for s in c['steps']}
    if any(s['id'] in old_ids for s in added):
        raise ValueError('new IDs conflict with existing steps')
    chapter['steps'].extend(added)
    chapter['limitations'] = [
        '小盒已有程式佈景、原生 Render Image 的分離展示試作；完整手工設定材質、相機與燈光的逐步示範仍待製作。',
        '上蓋上移18 mm為展示位置，不是名義裝配；渲染不能判定配合、強度或材料。',
        '訊號站舊渲染教材繼續保留，不能把它的示範當作小盒手工佈景已完成。',
        '輸出位置相對場景檔，先另存至個人工作區並檢查 Output Properties。',
    ]
    data['version'] = 'v007 · 2026-10-27'
    data['description'] = '12章詳細操作參照；v007補入小盒分離渲染試作與真實來源，學員事件沿用穩定教材ID。'
    data['sourceVersions'].extend([{'path':'learning/web/engineering-curriculum-v006.json','sha256':EXPECTED_V006},
                                   {'path':summary['path'],'sha256':summary['sha256']}])
    data['boxRenderVerification'] = {'summary':summary,'scene':scene,'renderOutput':rendered,
        'scope':'來源盒蓋網格不變；上蓋暫抬18 mm；程式佈景與存PNG，GUI觸發Render Image；輸出相對場景檔，須另存個人副本並核對路徑。',
        'physicalMeasurements':None,'fitResults':None,'qualifiedClearanceMm':None}
    data['contentReview']['supplementV007'] = '第12章補分離展示渲染試作；UI 截圖與程式保存的渲染 PNG 分類，完整手工佈景仍待示範。'
    if V007.exists():
        raise FileExistsError('refusing to overwrite v007')
    if V006.read_bytes() != before:
        raise ValueError('v006 changed during build')
    V007.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f"Created {V007}: {sum(len(c['steps']) for c in data['chapters'])} microsteps, stable id {data['id']}.")


if __name__ == '__main__':
    main()
