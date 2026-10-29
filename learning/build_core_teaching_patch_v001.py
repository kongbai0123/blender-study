"""Produce chapter 01-06 teaching evidence and blank field protocols, not results."""
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'learning/web/engineering-curriculum-v035.json'
OUT = ROOT / 'learning/patches/ch01-ch06-teaching-v001.json'
EDIT = ROOT / 'learning/evidence/03/2026-10-28-edit-practice-gui-v001'
SAVE = ROOT / 'learning/evidence/03/2026-10-28-save-body-gui-v001'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def safe_run(folder):
    raw = read(folder/'run.json')
    records = []
    for r in raw['records']:
        p = folder/r['file']
        if sha(p) != r['sha256']: raise ValueError('image changed')
        records.append({'slug':r['slug'], 'action':r['action'], 'observed':json.loads(r['observed']),
                        'path':p.relative_to(ROOT).as_posix(), 'sha256':r['sha256']})
    data = {'schemaVersion':1,'blender':raw['blender'],'construction':'geometry and save/open via isolated Blender GUI; file-browser fields set programmatically',
            'records':records,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None}
    write(folder/'safe-summary-v001.json',data)
    return {r['slug']:r for r in records}


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    edit, saved = safe_run(EDIT), safe_run(SAVE)
    base = read(BASE)
    originals = {s['id']:s for c in base['chapters'] for s in c['steps']}
    patches = {}
    templates = ROOT/'learning/journal/templates'
    protocol = templates/'printing-measurement-protocol-v001.json'
    write(protocol, {
        'schemaVersion':1,'title':'列印、量測與試配現場方法','status':'instructions_without_physical_results',
        'conditionsToRecord':['printer','material','nozzleDiameterMm','lineWidthMm','layerHeightMm','slicerVersion','profile','orientation','sourceSceneSha256','stlSha256','date'],
        'beforeSlicing':['核對件名、分支與來源版本，STL 數值按本教材 mm 解讀。', '檢查包圍盒、接觸列印床的一面、壁厚與孔細節；方向與支撐仍是候選。', '依材料與機台的已驗證設定建立副本；沒有資料時不編造溫度或速度。'],
        'beforeMeasurement':['依量具手冊檢查量具與零點，記下量程、解析度與狀態。', '排除毛邊及測量面的異物，保留原始件與量測位置說明。'],
        'measurement':['每個功能尺寸在相同方向的2～3處量測，保留每次原始讀數。', '外長寬高、內腔與壁厚分列；內孔 X/Y 開口尺寸與倒角不可混同。', '差值定義為實測減名義；實測未取得時保持空白。'],
        'fit':['插銷依六孔的凹點數或X中心位置辨認，插入方向一致，每孔記2～3次。', '記錄不能插入、卡緊、可滑動、晃動等觀察，不把主觀手感當通用合格值。', '選擇適合用途的候選間隙並寫理由；沒有可接受孔時不強選，回到尺寸、切片與製程查原因。'],
        'limits':['0.4mm噴嘴不等於線寬或合格間隙。', '單次試片不證明批次能力。', '此檔是方法，不是已列印或已量測證據。'],
        'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearanceMm':None
    })
    csv_path = templates/'fit-coupon-records-v002.csv'
    if csv_path.exists(): raise FileExistsError(csv_path)
    rows = [['record_kind','sample','role','design_x_mm','design_y_mm','design_z_mm','hole_center_x_mm','design_total_gap_mm','design_centered_side_gap_mm','measured_x_mm','measured_y_mm','measured_z_mm','repeat_index','fit_observed','source_blend_sha256','stl_sha256','conditions_reference','date']]
    rows.append(['nominal_design_only','pin','pin',10,10,8,'','','','','','','','','','','',''])
    for index in range(6):
        gap=round((index+1)/10,1)
        rows.append(['nominal_design_only',f'hole-{index+1}','square_hole',10+gap,10+gap,'',-35+14*index,gap,gap/2,'','','','','','','','',''])
    stream=io.StringIO(newline=''); csv.writer(stream).writerows(rows)
    csv_path.write_text(stream.getvalue(),encoding='utf-8',newline='')
    def artifact(path,label): return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'label':label}
    field_artifacts=[artifact(protocol,'現場列印、量測與試配方法（沒有結果）'),artifact(csv_path,'六孔名義設計與空白實測 CSV')]
    def patch(identifier,status,actions=None,success=None,records=(),artifacts=(),limits=()):
        old=originals[identifier]
        item={'evidenceStatus':status,'actions':actions or old['actions'],
              'success':success or old['success'],'limitations':list(limits),
              'detail':{'steps':actions or old['detail']['steps'], 'why':old['detail']['why']}}
        if records:
            item['figures']=[{'type':'screenshot','path':r['path'],'sha256':r['sha256'],
                             'caption':r['action']+' 原圖保留；讀值為助教示範，不是學員結果。'} for r in records]
            item['detail']['steps'] += ['示範讀值：'+json.dumps(r['observed'],ensure_ascii=False) for r in records]
        if artifacts: item['artifacts']=list(artifacts)
        patches[identifier]=item

    patch('ch01-01-01-01','existing_demo',records=[edit['default']],limits=['本圖只展示隔離 Blender 預設場景；學員可能是 Quick Setup、Splash 或既有檔案，仍依自己畫面辨認。'])
    editmap={
        'ch03-edit-01':['units','saved-start'], 'ch03-edit-02':['cube20'],
        'ch03-edit-03':['vertex','edge','face'], 'ch03-edit-04':['move-top','undo-move'],
        'ch03-edit-05':['inset','extrude'], 'ch03-edit-06':['undo-twice','hidden','shown'],
        'ch03-edit-07':['bottom','orbit'],
    }
    for identifier, slugs in editmap.items():
        patch(identifier,'existing_demo',records=[edit[x] for x in slugs],
              artifacts=[artifact(EDIT/'safe-summary-v001.json','18 個 GUI 動作與幾何讀值安全摘要')],
              limits=['檔案欄位由程式填寫，其餘列出的建模操作為獨立 Blender GUI；存檔僅到隔離示範資料夾。'])
    patches['ch03-edit-07']['actions']=['View > Viewpoint > Bottom，或按 Ctrl+Numpad7；Frame Selected 對焦。', '用數字鍵盤2轉回傾斜視角，或自行使用滑鼠中鍵旋轉。']
    patches['ch03-edit-07']['detail']['steps'] = patches['ch03-edit-07']['actions'] + ['示範實際使用 Ctrl+Numpad7、Frame Selected 及兩次 Numpad2；未示範滑鼠中鍵。']
    patch('ch03-04-06-04','existing_demo',records=[saved[x] for x in ['renamed','saved','reopened']],
          artifacts=[artifact(SAVE/'safe-summary-v001.json','原盒改名、保存及重開讀值')],
          limits=['原盒來源 SHA 已核對；此為隔離副本，不在學員工作區登記。登記方式另有隔離流程示範。'])
    original_run=read(ROOT/'learning/evidence/02/2026-10-22-lesson02-demo-v001/run.json')
    for identifier, slug in [('ch03-02-03-04','post'),('ch03-02-03-05','signal')]:
        r=next(r for r in original_run['records'] if r['slug']==slug)
        pic=ROOT/'learning/evidence/02/2026-10-22-lesson02-demo-v001'/r['file']
        if sha(pic)!=r['sha256']:raise ValueError('old source changed')
        source={'path':pic.relative_to(ROOT).as_posix(),'sha256':r['sha256'],'action':r['action'],'observed':r['observed']}
        patch(identifier,'existing_demo',records=[source],limits=['沿用 2026-10-22 的原始逐件操作圖與讀值，不是本輪重新拍攝；訊號站使用公尺單位。'])
    patch('ch02-gap-terms','documented_lesson',
          actions=['對照原盒口內寬56與唇外寬55.6 mm，列總差56−55.6=0.4 mm。', '只有同軸置中且對稱時，這個方向的名義單側為0.4÷2=0.2 mm。'],
          success='能分清此為名義設計關係，尚未量測或試配。',artifacts=field_artifacts,limits=['不將水平總差當法向或螺紋徑向間隙；0.4是試驗值。'])
    patch('ch02-04-01-01','documented_lesson',actions=['在空白條件欄寫下已知的印表機、材料、噴嘴、線寬、層高、切片版本與預定方向；未知保留空白。', '將來源場景與STL的版本／SHA一併列入；後續變更條件時建立新紀錄。'],artifacts=field_artifacts,limits=['示範沒有預填機型、材料、線寬或合格間隙；噴嘴不代線寬。'])
    patch('ch02-04-01-02','field_protocol_ready',actions=['確認可取得的量具及其量程、解析度和檢查狀態，依量具手冊核對零點。', '記錄目前有／沒有的工具；缺少量具時保留測量欄，不估填數值。'],artifacts=field_artifacts,limits=['本步方法已備妥；沒有實物量具與現場校驗結果。'])
    patch('ch02-05-01-01','documented_lesson',actions=['寫下同方向的總間隙＝孔寬−軸寬，辨認設計值與實測值。', '對置中對稱的方孔／方軸，再寫單側＝總間隙÷2；非置中或法向關係另行處理。'],artifacts=field_artifacts,limits=['公式不會自行產生合格公差或實測資料。'])
    patch('ch02-05-01-02','documented_lesson',actions=['開啟六孔名義設計 CSV；表中的量測、條件與手感欄尚未填。', '另存到自己的05工作區新版本，之後只在實際操作後填寫；保留教材原範本。'],artifacts=field_artifacts,limits=['範本已列0.1～0.6mm設計試驗點；空欄不代表零，也不是實測。'])
    for identifier in ['ch06-04-07-03','ch06-05-04-05','ch06-fit-01','ch06-fit-02','ch06-fit-03','ch06-fit-04','ch06-04-08-01','ch06-04-08-02','ch06-04-08-03']:
        patch(identifier,'field_protocol_ready',artifacts=field_artifacts,
              limits=['現場方法與空白紀錄已完成；本教材沒有代為切片、實印、量測或試配。', 'STL無單位標記，需在所用切片軟體核對mm尺寸；軟體介面依實際版本，不提供捏造畫面。', '登記流程保存來源與輸出關聯，不證明模型或實體合格。'])
    for identifier in ['ch06-fit-04','ch06-04-08-03']:
        patches[identifier]['success']='有現場資料時才記錄所選候選間隙或差值與理由；尚未取得資料則保持空白，教材方法已備妥。'
    apply_editorial_corrections(patches)
    write(OUT,{'schemaVersion':1,'base':BASE.relative_to(ROOT).as_posix(),'baseSha256':sha(BASE),
               'scope':'01-06原圖/GUI補拍與現場方法；沒有學員或實體結果','patches':patches,
               'learnerProgressChanged':False,'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None})
    print(sha(OUT))


def apply_editorial_corrections(patches):
    step=patches['ch03-edit-01']
    step['actions']=['在 Scene Properties > Units 設 Unit System=Metric、Length=Millimeters、Unit Scale=0.001。',
                     '另存自己的練習副本 u04_edit_practice_v001.blend；隔離實拍實際名為 u03_edit_practice_v001.blend，兩者不可混稱。']
    step['success']='Units 顯示 Metric／Millimeters／0.001；另存成功通知或重開後的實際檔名與預期一致。'
    step['detail']['steps'] = step['actions'] + ['示範檔名 u03_edit_practice_v001.blend；學員範例另存到自己的 04 工作區並使用 u04 前綴。']
    step=patches['ch06-fit-04']
    step['detail']['why']='方孔插銷試片的觀察可作相同材料與工藝下的上蓋候選起點；環形唇邊仍需實際盒蓋試配，不自動轉成合格間隙。'
    step=patches['ch06-fit-02']
    step['detail']['steps'].append('凹點不清時，按孔中心 X=-35、-21、-7、7、21、35 mm 對應總間隙 0.1～0.6 mm；不要憑印糊的凹點猜值。')
    patches['ch06-04-08-03']['success']='來源與條件、名義尺寸、各次實測及差值分欄；尚無實測時相關欄位保持空白。'


if __name__=='__main__': main()
