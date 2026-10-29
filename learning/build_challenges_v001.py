"""建立 12 章題目資料；引用 v030 原圖，不改教材、模型或學員進度。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / 'learning/web/engineering-curriculum-v030.json'
CATALOG = ROOT / 'learning/catalog.json'
OUTPUT = ROOT / 'learning/web/challenges/challenges-v001.json'
EXPECTED = '55d0cc4c731a550fbe2c17635426dd14efca2894cf99455b322d0ed9f8d8515b'


DATA = [
    dict(chapterId='ch01', challengeId='ch01-scene-v001', title='辨認畫面並保存練習場景', workspaceLesson='01',
         goal='辨認自己的 Blender 畫面，保存可重新開啟的個人練習檔，並辨認小盒與唇邊。',
         requirements=['保留目前既有作品及未儲存內容；依實際畫面決定後續操作。', '在自己的工作區另存 v001 與 v002；回報操作前的模式與選取物件。', '觀察示範中蓋板、唇邊與配合表面。'],
         deliverable='個人 .blend 檢查點及觀察紀錄。',
         hints=[('先觀察完整視窗，確認是設定、啟動卡片、預設場景或既有作品。','01-01'),('先另存自己的 v001，再練習選取、視角與精確移動。','01-04'),('另存 v002 並重新開啟；再看盒蓋與唇邊的原圖。','01-09')],
         checks=['能說明目前模式及選取物件；檔案在自己的工作區並可重開。','指出蓋板及下方唇邊；看圖不等於量到間隙。'],
         limitations=['既有示範和學員完成分開。看到示範圖不代表已理解或完成。'],
         sourceSections=['01-01','01-04','01-09','01-10'], screenshotPath='learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png'),
    dict(chapterId='ch02', challengeId='ch02-clearance-v001', title='算出總間隙並準備量測紀錄', workspaceLesson=None,
         goal='分清名義尺寸、總間隙、單側間隙與實測。',
         requirements=['使用教材名義盒口內寬 56 mm 與唇邊外寬 55.6 mm，計算總間隙。','在唇邊置中條件下計算每側間隙；列出印表機、材料、噴嘴、切片條件及量具，不知道寫待定。'],
         deliverable='分欄記錄名義值、總／單側間隙、列印條件及未來實測值。',
         hints=[('同方向名義尺寸相減；寫明這個差是兩側合計。','02-01'),('只有置中假設成立時，才能用總間隙除以二。','02-01'),('先列測量及列印條件，不以噴嘴直徑推定線寬或合格間隙。','02-02')],
         checks=['56 − 55.6 = 0.4 mm 總間隙；置中假設下每側 0.2 mm。','實測和配合結果沒有資料時維持空白。'],
         limitations=['0.4 mm 是名義試驗值，不是實測或合格配合。'],
         sourceSections=['02-01','02-02','02-03'], screenshotPath='learning/evidence/05/2026-10-22-lesson05-lid-demo-v001/05-05-11-separated-view.png'),
    dict(chapterId='ch03', challengeId='box-opening-v001', title='依工程圖建立毫米開口盒', workspaceLesson='04',
         goal='依原盒工程圖建立頂部開口的小盒，辨認壁厚與內腔。',
         requirements=['外框名義尺寸 60 × 40 × 30 mm。','內腔 56 × 36 × 28 mm；四周壁厚及底厚各 2 mm。','建立自己的工作檔並依教學登記版本。'],
         deliverable='可重開的個人 .blend 開口盒。',
         hints=[('設定毫米並檢查外框尺寸；先確認縮放。','03-09'),('在 Edit Mode 確認選取頂面再刪除。','03-11'),('使用 Solidify 核對方向與 2 mm 厚度。','03-12')],
         checks=['對照名義外框、內腔及開口，並檢查網格與檔案版本。','確認前由學員回報，不以登記或示範作完成證據。'],
         limitations=['工程圖為名義草案，公差、材料與製程待定；本題不自動判題。'],
         sourceSections=['03-09','03-10','03-11','03-12','03-13'], screenshotPath='learning/evidence/04/2026-10-22-lesson04-demo-v001/04-05-03-solidify-wall.png',
         drawing={'path':'/pilot/box-drawing-v002.svg','title':'原盒工程圖 v002（名義草案）'}, pilotPath='/pilot/box-lesson.html'),
    dict(chapterId='ch04', challengeId='ch04-render-v001', title='為訊號站製作並重現一張渲染', workspaceLesson='03',
         goal='使用自己的訊號站練習相機、燈光、材質與可重現渲染。',
         requirements=['從第 03 章的個人場景另存渲染工作檔。','安排相機、燈光及材質，輸出一張圖；重開場景再渲染。'],
         deliverable='場景檢查點與其關聯的兩次渲染輸出。',
         hints=[('先另存場景，再切換到相機視角檢查取景。','04-01'),('逐項調整燈光與材質，再執行 Render Image。','04-03'),('保存輸出並重開場景；再次渲染以核對來源。','04-05')],
         checks=['渲染輸出可辨識訊號站且記錄來源場景版本。','重新開啟後可渲染；兩次結果差異如有發現應記錄。'],
         limitations=['渲染是外觀展示，不能證明尺寸、可列印性或配合。'],
         sourceSections=['04-01','04-02','04-03','04-04','04-05','04-06'], screenshotPath='learning/evidence/03/2026-10-22-lesson03-demo-v001/03-05-04-render-menu.png'),
    dict(chapterId='ch05', challengeId='ch05-fit-coupon-v001', title='建立插銷與六孔配合試片', workspaceLesson='05',
         goal='建立可用於比較配合的試片，區分名義總間隙與實測。',
         requirements=['依既有示範建立名義 10 × 10 × 8 mm 的方形插銷。','參照既有孔板示範建立六個試驗點：0.1～0.6 mm 總間隙。','保留試片版本與每個孔的識別方式。'],
         deliverable='插銷及六孔孔板的草案 .blend 與孔位、試驗點紀錄。',
         hints=[('先建立並核對插銷。','05-01'),('依孔板步驟依序建立切割體與名義孔尺寸。','05-02'),('逐一核對孔位及凹點識別，另存版本。','05-02')],
         checks=['記錄六個總間隙各自的名義值，辨認孔對應的數字。','檢查薄肉、孔位與模型；實體能否辨識待切片及列印。'],
         limitations=['0.1～0.6 mm 是試驗點，不是已驗證可用範圍。','凹點間薄肉約 0.4 mm；是否保留需切片與實印確認。'],
         sourceSections=['05-01','05-02'], screenshotPath='learning/evidence/05/2026-10-22-lesson05-holes-view-v001/05-03-04-supplement-oblique-verified.png',
         drawing={'path':'/challenges/fit-trial-drawing-v003.svg','title':'插銷與孔板工程題圖（名義草案；不代表已匯出或實印）'}),
    dict(chapterId='ch06', challengeId='ch06-export-measure-v001', title='匯出試片並規劃量測試配', workspaceLesson='05',
         goal='將插銷與孔板匯出，核對數位尺寸並規劃可追溯的實體試配。',
         requirements=['分別匯出插銷與孔板 STL，記錄對應場景版本。','重新匯入或在切片器核對尺寸、方向及落床。','實際列印後逐孔記錄量測、試插及條件；尚未執行時留空。'],
         deliverable='模型與 STL 版本關聯、數位尺寸核對及待實測表。',
         hints=[('先確認匯出選取物件與 STL 選項，再分別輸出。','06-02'),('STL 本身不標示單位，本教材按 mm 檢查。','06-02'),('實印後記錄材料、條件、量具及各孔試配。','06-03')],
         checks=['數位外框、來源場景與匯出檔可追溯。','尚無實體資料時不得填寫通過或選定合格間隙。'],
         limitations=['目前不預設材料、機型、線寬、方向或支撐；實測與合格狀態待實際證據。'],
         sourceSections=['06-01','06-02','06-03','06-04','06-05'], screenshotPath='learning/evidence/05/2026-10-22-lesson05-export-view-v001/05-04-03-pin-dimensions.png',
         drawing={'path':'/challenges/fit-trial-drawing-v003.svg','title':'插銷與孔板工程題圖（名義草案；不代表已匯出或實印）'}),
    dict(chapterId='ch07', challengeId='ch07-sketch-v001', title='畫矩形草圖並標尺寸', workspaceLesson=None, workspaceId='engineering-parametric',
         goal='用草圖、尺寸約束及拉伸，理解外框與內腔如何建立。',
         requirements=['確認 CAD Sketcher 擴充套件與環境；在工程練習副本中畫矩形並標長寬。','依教材建立實心體，再建立內腔草圖及切割。','以自己的檔案另存並核對約束狀態。'],
         deliverable='可重開的個人草圖與盒體草案。',
         hints=[('先確認 CAD Sketcher 與獨立工作區。','07-01'),('建立 XY 草圖、畫矩形並標註 X／Y。','07-02'),('先拉伸成實心體，再建立並定位內腔。','07-03')],
         checks=['標註與選取的是正確草圖和方向；另存後能重開核對。','內腔位置與尺寸需實際檢查，不能只看外框。'],
         limitations=['CAD Sketcher 需額外安裝；本章詳細文字與操作仍須逐步改寫及實測。','示範原圖不代表學員已完成。'],
         sourceSections=['07-01','07-02','07-03','07-04'], screenshotPath='learning/evidence/parametric/2026-10-27-cad-sketcher-rectangle-v002/CAD-ENV-08-height-dimension.png'),
    dict(chapterId='ch08', challengeId='ch08-linked-box-v001', title='讓盒體、內腔與上蓋連動', workspaceLesson=None, workspaceId='engineering-parametric',
         goal='理解外框、內腔及蓋板的參數來源並試驗變更。',
         requirements=['從固定內腔反例辨認尺寸變動後的失配。','在適用範本及操作流程中連接 X／Y，檢查內腔與上蓋。','挑多組尺寸記錄讀值；超界和不支援操作需如實標記。'],
         deliverable='參數來源紀錄、連動草案與多尺寸數位核對結果。',
         hints=[('先把固定內腔的結果另存，觀察外框改變後的差別。','08-02'),('先確認內腔 X，再處理 Y 和所需更新／求解。','08-03'),('建立上蓋連動後，逐組核對尺寸；受控面板為選修。','08-06')],
         checks=['記錄各組外框、內腔與上蓋讀值及其對應檔案版本。','有錯誤或無法確認回復時停止並保留原副本。'],
         limitations=['手工面板僅支援指定示範模板副本；原生欄位、存檔與匯出可繞過防護。','理論未夾限範圍不是製造或配合合格範圍；無完整干涉或實體試配證據。'],
         sourceSections=['08-02','08-03','08-04','08-06','08-07','08-08'], screenshotPath='learning/evidence/parametric/2026-10-27-cad-sketcher-outer-edit-probe-v004/EDIT-06-x70y50.png'),
    dict(chapterId='ch09', challengeId='ch09-join-v001', title='比較定位榫與燕尾滑蓋', workspaceLesson='06',
         goal='以既有盒體觀察兩種定位與滑動機構，並分別核對版本。',
         requirements=['依定位榫示範建立獨立草案；辨認環唇與定位柱可能互相牽制。','依燕尾示範建立獨立草案，記錄水平總間隙與候選方向。','匯出示範分支並重新匯入核對尺寸。'],
         deliverable='定位榫與燕尾的分支模型、來源及數位核對紀錄。',
         hints=[('先查看定位柱、柱孔與環唇之間的關係。','09-01'),('在另一個分支觀察導軌及上蓋的移動。','09-02'),('分別匯出盒體與滑蓋，再核對 STL 外框。','09-03')],
         checks=['清楚記錄兩分支來源、方向與名義間隙。','辨識燕尾導軌下方水平懸空面；支撐及方向待評估。'],
         limitations=['0.4 mm 水平總間隙是試驗值，非合格值。','定位柱與環唇重複定位及燕尾懸空是待驗風險，不表示已實印失敗。'],
         sourceSections=['09-01','09-02','09-03'], screenshotPath='learning/evidence/06/2026-10-25-lesson06-dovetail-demo-v002/06-02-18-slide-x30.png'),
    dict(chapterId='ch10', challengeId='ch10-snap-fit-v001', title='分析卡扣與臂長對照試片', workspaceLesson='07',
         goal='辨識懸臂卡扣參數、候選列印方向與對照試片的用途。',
         requirements=['區分臂長 L、臂厚 h、倒扣 u、所需及允許撓度；未確定的材料與允許應變留待定。','依示範比較卡扣草案及 A_L19、B_L17、C_L21 對照試片。','列出方向、支撐、試配及量測紀錄欄位。'],
         deliverable='草案參數、候選方向與試片版本比較表。',
         hints=[('先核對原盒尺寸；不要把盒壁厚直接當臂厚。','10-01'),('觀察卡扣及上蓋的幾何關係，再看朝下表面。','10-02'),('比較三種臂長並記錄 STL 來源，實印結果留空。','10-05')],
         checks=['L、h、u、δ_req 與 δ_allow 定義不混淆。','記錄候選方向與需要實測的條件，未測試項目留空。'],
         limitations=['材料、允許應變與根部條件待定；方向與支撐為候選。','三個臂長僅為幾何對照，不代表已改善、配合或強度合格。'],
         sourceSections=['10-01','10-02','10-03','10-04','10-05'], screenshotPath='learning/evidence/07/2026-10-25-lesson07-snap-demo-v001/07-02-21-lid-raised.png'),
    dict(chapterId='ch11', challengeId='ch11-thread-v001', title='比較列印螺紋與金屬緊固件', workspaceLesson='08',
         goal='辨認兩條螺紋／固定路線與建模前仍缺少的規格。',
         requirements=['分別列出自訂列印螺紋，以及螺絲／熱熔螺母與螺絲柱的規格需求。','觀察 Screw 開放曲面示範及獨立盲孔柱草案。','材料、標準、五金尺寸、間隙及未實作項目維持待定。'],
         deliverable='兩條路線的參數表、示範限制與後續試驗計畫。',
         hints=[('先把螺距、導程、頭數和迭代次數分開。','11-01'),('觀察 Screw 設定與未封閉的曲面。','11-02'),('盲孔柱草案未接盒體；查看其對邊／對頂與孔深定義。','11-03')],
         checks=['Angle 360° 且 Object Screw 關閉時 Screw 對應導程；單線時導程才等於螺距。','記錄尚未完成的外／內螺紋、配套五金與實體試鎖。'],
         limitations=['Screw 開放曲面不等於可列印封閉螺紋；盲孔柱是未接盒體草案。','不推定完整 ISO 標準、公差表、配合或強度合格。'],
         sourceSections=['11-01','11-02','11-03','11-04','11-05','11-06','11-07'], screenshotPath='learning/evidence/08/2026-10-27-lesson08-screw-surface-v001/08-02-04-four-iterations.png'),
    dict(chapterId='ch12', challengeId='ch12-delivery-v001', title='整理尺寸鏈、交付與成品渲染', workspaceLesson=None,
         goal='把小盒名義尺寸、設計變更及後續實測連到來源版本。',
         requirements=['寫出盒口內寬＝外寬−2×側壁；唇邊外寬＝盒口內寬−總間隙。','分欄記錄名義值、允許偏差、數位讀值、實測、試配及列印條件。','整理場景、輸出、版本及渲染圖的關聯；未實測欄位留空。'],
         deliverable='可追溯的尺寸鏈與交付清單，附個人場景及渲染輸出。',
         hints=[('先辨認設計式中的尺寸方向及總間隙。','12-01'),('先整理既有實測；若尚未列印就保留空白。','12-02'),('重開來源場景、保存並關聯輸出。','12-05')],
         checks=['每次設計變更都能找到來源檔及其尺寸條件。','不由單一試片或數位外框推定批量能力或實體合格。'],
         limitations=['實測、補償、總裝及驗收均需實際結果；圖像僅展示外觀。'],
         sourceSections=['12-01','12-02','12-03','12-04','12-05'], screenshotPath='learning/evidence/12/2026-10-27-engineering-box-render-v004/12-01-03-render-result.png'),
]


def main():
    raw = CURRICULUM.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED:
        raise ValueError('教材版本雜湊不符；請重新核對題目與來源。')
    course = json.loads(raw)
    catalog = json.loads(CATALOG.read_bytes())
    chapters = {item['id']: item for item in course['chapters']}
    def figures(value):
        if isinstance(value, dict):
            if value.get('type') == 'screenshot' and value.get('path') and value.get('sha256'):
                yield value
            for child in value.values():
                yield from figures(child)
        elif isinstance(value, list):
            for child in value:
                yield from figures(child)
    results = []
    for draft in DATA:
        item = dict(draft)
        chapter = chapters[item['chapterId']]
        section_lookup = {section['id']: section['title'] for section in chapter['sections']}
        item['chapterTitle'] = chapter['title']
        item['hints'] = [{'text': text, 'section': section} for text, section in item['hints']]
        item['sourceSteps'] = [{'chapterId': item['chapterId'], 'sectionId': sec,
                                'label': section_lookup[sec]} for sec in item.pop('sourceSections')]
        for hint in item['hints']:
            if hint['section'] not in section_lookup:
                raise ValueError('小節不存在：' + hint['section'])
        expected_path = item.pop('screenshotPath')
        figure = next((fig for fig in figures(chapter) if fig.get('path') == expected_path), None)
        if figure is None:
            figure = next((fig for fig in figures(catalog) if fig.get('path') == expected_path), None)
        if figure is None:
            raise ValueError('找不到對應的既有 Blender 原圖：' + expected_path)
        file_path = ROOT / expected_path
        if hashlib.sha256(file_path.read_bytes()).hexdigest() != figure['sha256']:
            raise ValueError('原圖雜湊不符：' + expected_path)
        caption = figure.get('alt') or figure.get('caption') or '既有原始操作截圖'
        item['screenshot'] = {'path': expected_path, 'sha256': figure['sha256'],
                              'caption': '相關教學操作參照，並非本題完整示範：' + caption}
        item.setdefault('drawing', None)
        item['drawingStatus'] = '題目工程圖為名義草案，非實體或製造合格證據。' if item['drawing'] else '本題專屬工程圖尚待製作；不得以其他零件圖冒充。'
        item['evidenceStatus'] = '題目草案；圖片為既有獨立 Blender 示範參照，並非此題逐步驗證或學員完成。'
        results.append(item)
    if OUTPUT.exists():
        raise FileExistsError('拒絕覆寫既有題目版本：' + str(OUTPUT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {'schemaVersion': 1, 'version': 'v001', 'title': '小盒工程學習路徑：章節練習題',
               'description': '12 章各一題試用草案；維持原課程進度，不等同實體驗證。',
               'source': {'path': 'learning/web/engineering-curriculum-v030.json', 'sha256': EXPECTED},
               'chapters': results}
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('saved', OUTPUT, 'sha256', hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), 'chapters', len(results))


if __name__ == '__main__':
    main()
