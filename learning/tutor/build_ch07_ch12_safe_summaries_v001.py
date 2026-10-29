"""Publishable indexes for two isolated GUI trials; do not copy raw runner state."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[2]
for rel,description in [
 ('learning/evidence/parametric/2026-10-28-cad-install-gui-trial-v002','已核對的官方 ZIP 經獨立 Blender GUI 安裝至隔離擴充套件目錄；檔案欄位由程式填寫。'),
 ('learning/evidence/12/2026-10-28-render-safe-copy-gui-v003','渲染場景以 GUI 另存到隔離假工作區並檢查相對輸出；檔案欄位由程式填寫，未渲染。')]:
 base=ROOT/rel;target=base/'safe-summary-v001.json'
 if target.exists():raise FileExistsError(target)
 run=json.loads((base/'run.json').read_text(encoding='utf8'))
 records=[]
 for item in run['records']:
  p=base/item['file'];digest=sha256(p.read_bytes()).hexdigest()
  if digest!=item['sha256']:raise ValueError('screenshot hash mismatch')
  records.append({'action':item['action'],'image':p.relative_to(ROOT).as_posix(),'sha256':digest,'observed':item['observed']})
 result={'schemaVersion':1,'kind':'isolated_blender_gui_demonstration','description':description,'blenderVersion':run['blender'],'records':records,'limitations':['實際視窗示範，不代表學員完成；不代表實體製造或配合合格。','原始 runner-status 可能包含本機路徑或 Recent 清單，不公開。']}
 if 'cad-install' in rel:
  result['source']={'release':'https://github.com/hlorus/CAD_Sketcher/releases/tag/v0.32.1','filename':'CAD_Sketcher-0.32.1-windows_x64.zip','bytes':1283581,'sha256':'b456070e9d1cec7fea85494b7afbbae0a543e9c2381cc40349a763d2de038a59'}
  result['limitations'].append('隔離安裝不表示學員自己的 Blender 已安裝；擴充套件 ZIP 不隨教材發布。')
 else:
  scene=base/'demo-files/fake-workspace/render_safe_copy_v001.blend'
  result['source']={'path':'learning/evidence/12/2026-10-27-engineering-box-render-v004/demo-files/engineering_box_render_v001.blend','sha256':'db03247077da659ff4c4a0a5ac411e7662ab326fb6302e58496e1636f69246de'}
  result['savedScene']={'path':scene.relative_to(ROOT).as_posix(),'sha256':sha256(scene.read_bytes()).hexdigest()}
  result['limitations'].append('只在本次假工作區檢查，未寫學員工作區或實際輸出圖片；相對路徑依場景位置解析。')
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(target.relative_to(ROOT).as_posix(),sha256(target.read_bytes()).hexdigest())
