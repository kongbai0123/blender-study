"""Engineering draft from GUI-built box/lid mesh projections and recorded hardware."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[2]
def load(rel,digest):
 p=ROOT/rel
 if sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('source changed: '+rel)
 return json.loads(p.read_text(encoding='utf8'))
body=load('learning/evidence/08/2026-10-28-m3-layout-drawing-v001/body-readback-v002.json','ea98df6776ebe5ac718f7e367ffe21de1c669a848ba90a4a1696002d00ae658d')
lid=load('learning/evidence/08/2026-10-28-m3-layout-drawing-v001/lid-readback-v002.json','72556a5931564138208ab46236ff3cab14c815df12261af5b5abd0ba5ee3f126')
hardware=load('learning/hardware-selection-v001.json','f6b3f32cff1a6e7a0396353960a81087055859e4b399751e4991362b13f4c6dc')
audit=load('learning/evidence/08/2026-10-28-four-insert-boss-gui-v001/independent-audit-v002.json','e006b2ad5d472d82e4da8d1dbee7d82323f3fa34d6613994515f49052502d6a9')
steps=load('learning/lesson11_four_insert_bosses_optional_steps_v001.json','eeac1704e502c5336517dc7e18b9f7313a294eb4c5c7d8254005e04a0356fe9c')
scene=ROOT/body['sourceScene'];expected='70f6687edc450438d21ada9b61b9295cf24079c64884947b9c4081de88e23462'
if sha256(scene.read_bytes()).hexdigest()!=expected or any(d['sceneSha256']!=expected for d in (body,lid,audit)):raise ValueError('different source scene')
if [body['object'],lid['object']]!=['Body','Lid'] or body['cutYmm']!=lid['cutYmm']:raise ValueError('inconsistent objects or cut')
if steps['demonstrationSceneSha256']!=expected:raise ValueError('step record source mismatch')
draft=hardware['designDraft'];insert=hardware['insert'];screw=hardware['screw']
assert draft['bossCentersXYMm']==[[-21,-11],[-21,11],[21,-11],[21,11]]
assert all(len(x['section'])>0 and len(x['projections']['top'])>0 for x in (body,lid))
out=ROOT/'learning/web/challenges/m3-four-boss-layout-drawing-v001.svg'
if out.exists():raise FileExistsError(out)
S=7
top_body=lambda p:(330+p[0]*S,315-p[1]*S)
top_lid=lambda p:(1050+p[0]*S,315-p[1]*S)
sect=lambda p:(330+p[0]*S,825-p[1]*S)
detail=lambda p:(1080+(p[0]-21)*19,945-(p[1]-4)*19)
def line(a,b,project):
 x1,y1=project(a);x2,y2=project(b);return f'<path d="M{x1:.3f} {y1:.3f}L{x2:.3f} {y2:.3f}"/>'
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1340" role="img" aria-labelledby="title desc"><title id="title">四柱上蓋孔與盒體剖切工程題圖</title><desc id="desc">實際 Blender 盒體和上蓋網格的俯視與 Y={body['cutYmm']} mm 三角面剖切；五金資料為原廠名義包絡，未做實體安裝。</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker><clipPath id="detail"><rect x="965" y="700" width="275" height="255"/></clipPath></defs>
<rect width="1600" height="1340" fill="white"/><rect x="20" y="20" width="1560" height="1300" fill="none" stroke="#173548" stroke-width="3"/><g font-family="Microsoft JhengHei,sans-serif" fill="#173548"><text x="50" y="60" font-size="28" font-weight="700">四柱、連壁肋與上蓋孔｜工程題圖草案</text><text x="50" y="90" font-size="17">獨立 Blender 接合場景的數位網格；金屬五金只列原廠尺寸，未建金屬實體。</text><text x="110" y="130" font-size="21" font-weight="700">盒體俯視（+Z → −Z）</text><text x="820" y="130" font-size="21" font-weight="700">上蓋俯視（+Z → −Z）</text><text x="110" y="660" font-size="21" font-weight="700">盒體 A–A 網格剖切（Y={body['cutYmm']} mm）</text><text x="820" y="660" font-size="21" font-weight="700">B 局部剖切（右上柱；同 Y 平面）</text></g>''']
parts.append('<g fill="none" stroke="#193548" stroke-width="1.25" stroke-linejoin="round">')
for a,b in body['projections']['top']:parts.append(line(a,b,top_body))
for a,b in lid['projections']['top']:parts.append(line(a,b,top_lid))
for a,b in body['section']:parts.append(line(a,b,sect))
parts.append('</g><g fill="none" stroke="#193548" stroke-width="1.3" clip-path="url(#detail)">')
for a,b in body['section']:parts.append(line(a,b,detail))
parts.append('</g>')
ay=315-body['cutYmm']*S
parts.append(f'''<g stroke="#557b93" fill="none" stroke-width="1.3"><path d="M95 {ay:.3f}H565" stroke-dasharray="10 6"/><path d="M95 {ay+17:.3f}V{ay-17:.3f} M565 {ay+17:.3f}V{ay-17:.3f}" marker-end="url(#arrow)"/></g><g font-family="Microsoft JhengHei,sans-serif" fill="#244f6e" font-size="17"><text x="76" y="{ay-20:.3f}">A</text><text x="570" y="{ay-20:.3f}">A</text></g>
<g stroke="#244f6e" fill="none" stroke-width="1.2"><path d="M120 455V500 M540 455V500"/><line x1="120" y1="490" x2="540" y2="490" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M120 175H65 M120 455H65"/><line x1="75" y1="175" x2="75" y2="455" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M903 238V153 M1197 238V153"/><line x1="903" y1="163" x2="1197" y2="163" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1197 238H1315 M1197 392H1315"/><line x1="1305" y1="238" x2="1305" y2="392" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>
<g font-family="Microsoft JhengHei,sans-serif" font-size="18" fill="#173548"><text x="330" y="483" text-anchor="middle">60</text><text x="64" y="320" transform="rotate(-90 64 320)">40</text><text x="1050" y="156" text-anchor="middle">42 柱心距</text><text x="1320" y="320">22 柱心距</text><text x="820" y="520">4 處蓋孔 Ø{draft['coverClearanceHoleNominalDiameterMm']:.1f} mm 對頂名義：試驗值</text><text x="470" y="708">B</text><text x="110" y="970">外框約 60 × 40 × 30 mm；截線為實際網格而非剖面填色。</text><text x="820" y="980">肋頂 Z10；Lid 未顯示，另件外框最低 Z11。</text></g>
<path d="M20 1020H1580 M1010 1020V1320 M1300 1020V1320" fill="none" stroke="#173548" stroke-width="2"/>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="17"><text x="45" y="1055">四柱中心 X=±21、Y=±11 mm；柱外 Ø{draft['bossOutsideDiameterMm']:.1f} 對頂、導孔 Ø{draft['pilotNominalDiameterMm']:.1f} 對頂、名義深 {draft['pilotNominalDepthMm']:.1f}。</text><text x="45" y="1085">32 邊形名義對頂；Z=14.9 mm 的數位壁厚樣點中最低約 1.990 mm，非實測。</text><text x="45" y="1115">連壁肋名義厚 {steps['nominalDraft']['ribThicknessMm']}、肋頂 Z=10；與唇邊的 1 mm 為靜態外框差，不代表運動或強度合格。</text><text x="45" y="1145">已選 ruthex {insert['partNumber']}：原廠導孔 {insert['manufacturerRecommendedHoleDiameterMm']:.1f}、最小深 {insert['manufacturerMinimumHoleDepthMm']:.1f}、周壁 W {insert['manufacturerMinimumWallWMm']:.1f} mm。</text><text x="45" y="1175">已選 ETTINGER {screw['partNumber']}：M3×{screw['underHeadLengthMm']} A2，頭徑 {screw['headDiameterMm']}、頭高 {screw['headHeightMm']}、內六角 {screw['hexKeyMm']} mm。</text><text x="45" y="1205">上蓋孔 Ø{draft['coverClearanceHoleNominalDiameterMm']:.1f} 為自訂試驗值；材料、扭矩、實印、量測、安裝及試配待定。</text><text x="45" y="1235">可見邊為網格抽樣，非完整標準隱線；剖切偏離柱心 0.123456 mm，非實體試配。</text><text x="45" y="1265">來源 SHA-256：{expected}；名義資料非尺寸公差或製造核准。</text><text x="1030" y="1055">圖名：四柱與蓋孔</text><text x="1030" y="1085">版次：v001</text><text x="1030" y="1115">用途：教學草案</text><text x="1320" y="1055">單位：mm</text><text x="1320" y="1085">比例：隨畫面</text><text x="1320" y="1115">實物安裝：未做</text></g></svg>''')
out.write_text('\n'.join(parts)+'\n',encoding='utf8',newline='\n')
print('drawing',out.relative_to(ROOT).as_posix(),sha256(out.read_bytes()).hexdigest())
