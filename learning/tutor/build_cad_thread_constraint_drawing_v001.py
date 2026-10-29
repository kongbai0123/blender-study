"""Draw the two actual CAD Sketcher XY states from independent Blender readbacks."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[2]
def load(rel,expected):
 p=ROOT/rel
 if sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('audit hash changed')
 return json.loads(p.read_text(encoding='utf8'))
a=load('learning/evidence/parametric/2026-10-28-cad-thread-triangle-restore-v001/independent-audit-v001.json','5ec4481e979c1032f06f9d64728140596d33857b1b8c607f51215a8d6897ef68')
b=load('learning/evidence/parametric/2026-10-28-cad-thread-drawing-v001/changed-080-audit-v001.json','02d6929ea69f5403c077106de0afa1adba6d1504a17d14c7fe135d9fe12486ef')
scenes=[('learning/evidence/parametric/2026-10-28-cad-thread-triangle-restore-v001/demo-files/cad_thread_triangle_060_restored_v003.blend',a),('learning/evidence/parametric/2026-10-28-cad-thread-triangle-trial-v001/demo-files/cad_thread_triangle_080_v002.blend',b)]
for path,d in scenes:
 if sha256((ROOT/path).read_bytes()).hexdigest()!=d['sourceSha256'] or d['solver']!='OKAY' or d['dof']!=0:raise ValueError('scene or solver mismatch')
 if sorted(c['type'] for c in d['constraints'])!=['DISTANCE','DISTANCE','EQUAL','VERTICAL']:raise ValueError('constraints changed')
def points(d):
 uniq={(round(p[0],7),round(p[1],7)) for p in d['coordinatesXYMm']}
 if len(uniq)!=3:raise ValueError('expected three unique vertices')
 return sorted(uniq,key=lambda p:p[1])
p0,p1=points(a),points(b)
if abs(a['baseDimensionMm']-.6)>1e-4 or abs(b['baseDimensionMm']-.8)>1e-4 or abs(a['slopeDimensionMm']-b['slopeDimensionMm'])>1e-5:raise ValueError('unexpected dimensions')
out=ROOT/'learning/web/challenges/cad-thread-constraint-drawing-v001.svg'
if out.exists():raise FileExistsError(out)
S=300
def coords(ps,x):return [(x+(p[0]-ps[0][0])*S,530-(p[1]-ps[0][1])*S) for p in ps]
def poly(ps):return ' '.join(f'{x:.3f},{y:.3f}' for x,y in ps)
u,v=coords(p0,240),coords(p1,900)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1550 1050" role="img" aria-labelledby="title desc"><title id="title">CAD Sketcher 約束截面尺寸變更</title><desc id="desc">實際 GUI 生成、另存及獨立讀取的 XY 三角草圖，展示截面高度 0.6 與 0.8 mm；不等於螺距。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker></defs><rect width="1550" height="1050" fill="white"/><rect x="20" y="20" width="1510" height="1010" fill="none" stroke="#173548" stroke-width="3"/>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548"><text x="50" y="60" font-size="28" font-weight="700">CAD Sketcher 約束截面：兩個已存尺寸狀態</text><text x="50" y="90" font-size="17">從 Blender 已存草圖的真實頂點與約束讀值製圖；不是 Blender 介面截圖。</text><text x="130" y="155" font-size="22" font-weight="700">還原 0.6 mm（XY）</text><text x="790" y="155" font-size="22" font-weight="700">更改 0.8 mm（XY）</text></g>
<g fill="none" stroke="#193548" stroke-width="3"><polygon points="{poly(u)}"/><polygon points="{poly(v)}"/></g>
<g fill="#ac552a"><circle cx="{u[0][0]:.3f}" cy="{u[0][1]:.3f}" r="5"/><circle cx="{v[0][0]:.3f}" cy="{v[0][1]:.3f}" r="5"/></g>
<g stroke="#244f6e" fill="none" stroke-width="1.3"><path d="M{u[0][0]:.3f} {u[0][1]:.3f}H185 M{u[2][0]:.3f} {u[2][1]:.3f}H185"/><line x1="195" y1="{u[0][1]:.3f}" x2="195" y2="{u[2][1]:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M{v[0][0]:.3f} {v[0][1]:.3f}H845 M{v[2][0]:.3f} {v[2][1]:.3f}H845"/><line x1="855" y1="{v[0][1]:.3f}" x2="855" y2="{v[2][1]:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="19"><text x="174" y="430" transform="rotate(-90 174 430)">截面高度 {a['baseDimensionMm']:.3f}</text><text x="834" y="430" transform="rotate(-90 834 430)">截面高度 {b['baseDimensionMm']:.3f}</text><text x="{u[1][0]+12:.3f}" y="{u[1][1]:.3f}">尖點 X={p0[1][0]:.3f}</text><text x="{v[1][0]+12:.3f}" y="{v[1][1]:.3f}">尖點 X={p1[1][0]:.5f}</text><text x="240" y="570">X →　Y ↑；橘點為固定基準點</text><text x="900" y="570">X →　Y ↑；左下基準位置未變</text><text x="240" y="220">斜邊 Distance {a['slopeDimensionMm']:.6f} mm</text><text x="900" y="220">斜邊 Distance {b['slopeDimensionMm']:.6f} mm</text></g>
<path d="M20 640H1530 M1010 640V1030 M1270 640V1030" fill="none" stroke="#173548" stroke-width="2"/><g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="17"><text x="45" y="675">兩個 Distance、Equal、Vertical；左下點為固定屬性。求解器 OKAY，DoF 0。</text><text x="45" y="705">P1 約 (4.8, 0) mm 固定；0.6→0.8 mm 時，兩斜邊等長，尖點 X 改變。</text><text x="45" y="735">0.6、0.8 是 XY 截面高度，不是螺距；此圖未建立 XZ 螺旋或三維實體。</text><text x="45" y="765">非 ISO 牙型；材料、公差、列印、量測、試配與強度均待定。</text><text x="45" y="795">0.6 還原場景 SHA：{a['sourceSha256']}</text><text x="45" y="825">0.8 改動場景 SHA：{b['sourceSha256']}</text><text x="45" y="855">圖中連線直接使用兩份獨立讀取的草圖頂點；尺寸為名義數位值，勿量螢幕。</text><text x="1030" y="675">圖名：約束截面</text><text x="1030" y="705">版次：v001</text><text x="1030" y="735">用途：教學草案</text><text x="1290" y="675">單位：mm</text><text x="1290" y="705">比例：隨畫面</text><text x="1290" y="735">實體試配：未做</text></g></svg>'''
out.write_text(svg+'\n',encoding='utf8',newline='\n');print(out.relative_to(ROOT).as_posix(),sha256(out.read_bytes()).hexdigest())
