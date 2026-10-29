"""First-chapter identification drawing derived from the actual box/lid scene."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[2]
def load(rel,digest):
 p=ROOT/rel
 if sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('readback changed '+rel)
 return json.loads(p.read_text(encoding='utf8'))
b=load('learning/evidence/01/2026-10-28-box-lid-identification-drawing-v001/body-readback-v001.json','334485951b1429f2cf219d6cb5d3605d332a84a639278f4bfc64f5e72a97047e')
l=load('learning/evidence/01/2026-10-28-box-lid-identification-drawing-v001/lid-readback-v001.json','e62590958289027d4c0983d3f0ec672dbea220403e744ff925f0f9812e595e78')
expected='ab08f331dcb26c5ffc6c6ca56c7c7f022df96791c4777e37c5f01a964fbed6ff'
if b['sceneSha256']!=expected or l['sceneSha256']!=expected or sha256((ROOT/b['sourceScene']).read_bytes()).hexdigest()!=expected:raise ValueError('source scene changed')
if (b['object'],l['object'])!=('Body','Lid') or b['cutYmm']!=l['cutYmm']:raise ValueError('source object mismatch')
if b['boundsMm']!=[[-30.0,30.0],[-20.0,20.0],[-15.0,15.0]] or l['boundsMm']!=[[-30.0,30.0],[-20.0,20.0],[11.0,17.0]]:raise ValueError('box or lid bounding dimensions changed')
ring=sorted({round(abs(p[0]),4) for seg in l['section'] for p in seg if abs(p[1]-11)<1e-4})
if not ring or abs(ring[0]-25.8)>1e-4 or abs(ring[-1]-27.8)>1e-4:raise ValueError('lip section does not match dimensions')
bottom=[p for edge in l['projections']['bottom'] for p in edge if abs(p[2]-11)<1e-4]
if sorted({round(abs(p[0]),4) for p in bottom})!=[25.8,27.8] or sorted({round(abs(p[1]),4) for p in bottom})!=[15.8,17.8]:raise ValueError('lip XY boundaries changed')
S=7
box=lambda p:(330+p[0]*S,315-p[1]*S)
underside=lambda p:(1050+p[0]*S,315-p[1]*S)
section=lambda p:(330+p[0]*S,825-p[1]*S)
detail=lambda p:(1110+(p[0]+28)*35,900-(p[1]-10)*35)
def line(a,c,project):
 x1,y1=project(a);x2,y2=project(c);return f'<path d="M{x1:.3f} {y1:.3f}L{x2:.3f} {y2:.3f}"/>'
out=ROOT/'learning/web/challenges/box-lid-identification-drawing-v001.svg'
if out.exists():raise FileExistsError(out)
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1300" role="img" aria-labelledby="title desc"><title id="title">辨認原盒、蓋板及下方環形唇邊</title><desc id="desc">依已存 Blender 原盒與原蓋真實網格投影和剖切生成的工程題圖；非 Blender 介面或使用者模型。</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker><clipPath id="detail"><rect x="990" y="590" width="330" height="330"/></clipPath></defs>
<rect width="1600" height="1300" fill="white"/><rect x="20" y="20" width="1560" height="1260" fill="none" stroke="#173548" stroke-width="3"/><g font-family="Microsoft JhengHei,sans-serif" fill="#173548"><text x="50" y="60" font-size="28" font-weight="700">認識盒體、蓋板與下方環形唇邊</text><text x="50" y="90" font-size="17">工程目標參照：來源為 Blender 真實網格；不是 Blender 介面畫面或使用者模型。</text><text x="110" y="130" font-size="21" font-weight="700">盒體俯視（+Z 朝 −Z）</text><text x="820" y="130" font-size="21" font-weight="700">上蓋底視（−Z 朝 +Z）</text><text x="110" y="610" font-size="21" font-weight="700">組合 A–A 實際網格剖切</text><text x="820" y="610" font-size="21" font-weight="700">B 局部剖切（同一切面）</text></g>''']
parts.append('<g fill="none" stroke="#1c4969" stroke-width="2" stroke-linejoin="round">')
for a,c in b['projections']['top']:parts.append(line(a,c,box))
for a,c in b['section']:parts.append(line(a,c,section))
parts.append('</g><g fill="none" stroke="#ac552a" stroke-width="2" stroke-linejoin="round">')
for a,c in l['projections']['bottom']:parts.append(line(a,c,underside))
for a,c in l['section']:parts.append(line(a,c,section))
parts.append('</g><g fill="none" stroke-width="2.5" clip-path="url(#detail)">')
for a,c in b['section']:parts.append(line(a,c,detail).replace('<path ','<path stroke="#1c4969" '))
for a,c in l['section']:parts.append(line(a,c,detail).replace('<path ','<path stroke="#ac552a" '))
parts.append('</g>')
ay=315-b['cutYmm']*S
parts.append(f'''<g stroke="#557b93" fill="none" stroke-width="1.3"><path d="M95 {ay:.3f}H565" stroke-dasharray="10 6"/><path d="M95 {ay+17:.3f}V{ay-17:.3f} M565 {ay+17:.3f}V{ay-17:.3f}" marker-end="url(#arrow)"/></g><g font-family="Microsoft JhengHei,sans-serif" fill="#244f6e" font-size="17"><text x="76" y="{ay-20:.3f}">A</text><text x="570" y="{ay-20:.3f}">A</text></g>
<g stroke="#244f6e" fill="none" stroke-width="1.2"><path d="M120 455V500 M540 455V500"/><line x1="120" y1="490" x2="540" y2="490" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M120 175H65 M120 455H65"/><line x1="75" y1="175" x2="75" y2="455" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1320 155L1180 198" marker-end="url(#arrow)"/><path d="M1340 245L1250 180" marker-end="url(#arrow)"/></g>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="18"><text x="330" y="483" text-anchor="middle">60 mm</text><text x="64" y="320" transform="rotate(-90 64 320)">40 mm</text><text x="1285" y="148" fill="#ac552a">下方環形唇邊</text><text x="1320" y="245" fill="#ac552a">蓋板</text><text x="110" y="690">B</text><text x="110" y="950">藍：盒體　橘：蓋板與下方唇邊</text><text x="820" y="960">僅名義位置；各方向間隙仍待實體試配。</text><text x="1080" y="695" fill="#ac552a">蓋板</text><text x="1190" y="820" fill="#ac552a">唇邊</text><text x="1000" y="865" fill="#1c4969">盒壁</text><text x="110" y="980">A–A 為 Y={b['cutYmm']} mm 的網格截線，非剖面填色。</text></g>
<path d="M20 1020H1580 M1010 1020V1280 M1300 1020V1280" fill="none" stroke="#173548" stroke-width="2"/>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="17"><text x="45" y="1055">盒體外框約 60 × 40 × 30 mm；盒壁及底名義 2 mm。</text><text x="45" y="1085">蓋板 60 × 40 × 2 mm；下方環形唇邊深 4 mm、壁名義 2 mm。</text><text x="45" y="1115">唇邊外框 55.6 × 35.6 mm；內口 51.6 × 31.6 mm，來源為已存網格。</text><text x="45" y="1145">盒口與唇邊同方向名義總間隙 0.4 mm；置中時單側名義 0.2 mm，均為試驗值。</text><text x="45" y="1175">可見邊為抽樣投影，非完整標準隱線；剖切為實際三角面與平面求交。</text><text x="45" y="1205">材料、公差、列印、量測與實體試配待定；不可由此圖推定配合合格。</text><text x="45" y="1235">來源 SHA-256：{expected}；工程目標圖非 Blender 介面畫面。</text><text x="1030" y="1055">圖名：盒與環形唇邊</text><text x="1030" y="1085">版次：v001</text><text x="1030" y="1115">用途：辨認草案</text><text x="1320" y="1055">單位：mm</text><text x="1320" y="1085">比例：隨畫面</text><text x="1320" y="1115">實體試配：未做</text></g></svg>''')
out.write_text('\n'.join(parts)+'\n',encoding='utf8',newline='\n')
print(out.relative_to(ROOT).as_posix(),sha256(out.read_bytes()).hexdigest())
