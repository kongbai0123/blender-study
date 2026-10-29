"""Render actual GUI-created XZ profile vertices as an engineering teaching drawing."""
from hashlib import sha256
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[2]
if len(sys.argv)!=4:raise SystemExit('usage: <readback relative path> <sha256> <new SVG relative path>')
source=(ROOT/sys.argv[1]).resolve();source.relative_to(ROOT/'learning/evidence')
if sha256(source.read_bytes()).hexdigest()!=sys.argv[2]:raise ValueError('readback SHA mismatch')
out=(ROOT/sys.argv[3]).resolve();out.relative_to(ROOT/'learning/web/challenges')
if out.exists():raise FileExistsError(out)
d=json.loads(source.read_text(encoding='utf8'))
if sha256((ROOT/d['sourceScene']).read_bytes()).hexdigest()!=d['sourceSha256']:raise ValueError('scene SHA mismatch')
p=sorted(d['verticesMm'],key=lambda q:q[2])
if len(p)!=3 or len(d['edges'])!=3 or d['faces']!=0:raise ValueError('three-edge wire required')
if not(abs(p[0][0]-p[2][0])<1e-4 and p[1][0]>p[0][0] and all(abs(q[1])<1e-4 for q in p)):raise ValueError('unexpected profile')
base=p[0][0];apex=p[1][0];dz=p[2][2]-p[0][2];tipz=p[1][2]-p[0][2]
if not (0<dz<2 and 0<apex-base<3 and 0<tipz<dz):raise ValueError('unexpected dimension')
def line(x1,y1,x2,y2,cls='dim',arrow=False):
    return f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"'+(' marker-start="url(#a)" marker-end="url(#a)"' if arrow else '')+'/>'
def poly(coords):return ' '.join(f'{x:.3f},{y:.3f}' for x,y in coords)
# Main and enlarged detail share isotropic X/Z scale in each view.
full=[(110+q[0]*100,445-(q[2]-p[0][2])*100) for q in p]
detail=[(875+(q[0]-base)*310,420-(q[2]-p[0][2])*310) for q in p]
top=[(110+q[0]*100,720-q[1]*100) for q in p]
side=[(955+q[1]*250,825-(q[2]-p[0][2])*250) for q in p]
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1550 1100" role="img" aria-labelledby="title desc">
<title id="title">手工螺紋截面輪廓｜工程題圖</title><desc id="desc">實際 Blender 三個頂點、三條邊的平面 XZ 輪廓；前視、局部放大、俯視與側視，尺寸從頂點讀值，非 ISO 螺紋或合格配合。</desc>
<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker></defs>
<style>text{{font-family:Microsoft JhengHei,sans-serif;fill:#173548}}.edge{{stroke:#193548;stroke-width:2.5;fill:none}}.dim{{stroke:#244f6e;stroke-width:1.3;fill:none}}.axis{{stroke:#557b93;stroke-width:1.2;stroke-dasharray:12 5 3 5}}.label{{font-size:19px}}.head{{font-size:22px;font-weight:700}}.small{{font-size:17px}}</style>
<rect width="1550" height="1100" fill="white"/><rect x="20" y="20" width="1510" height="1060" fill="none" stroke="#173548" stroke-width="3"/>
<text x="50" y="60" font-size="28" font-weight="700">手工螺紋截面輪廓｜工程題圖</text><text x="50" y="90" class="small">獨立 Blender 實際三點三邊網格 · mm · 二維輪廓並非已配合的螺紋或約束式 CAD 草圖</text>
<text x="110" y="145" class="head">前視：X–Z 截面與旋轉軸</text><text x="840" y="145" class="head">A 詳細視圖（同比例放大）</text>
<line x1="110" y1="200" x2="110" y2="500" class="axis"/><text x="58" y="210" class="label">旋轉軸 X=0</text><path class="edge" d="M{full[0][0]:.3f} {full[0][1]:.3f} L{full[1][0]:.3f} {full[1][1]:.3f} L{full[2][0]:.3f} {full[2][1]:.3f} Z"/><text x="{full[2][0]-18:.3f}" y="{full[2][1]-12:.3f}" class="label">A</text>
{line(110,445,110,510)}{line(full[0][0],445,full[0][0],510)}{line(110,500,full[0][0],500,arrow=True)}<text x="{(110+full[0][0])/2:.3f}" y="493" text-anchor="middle" class="label">R {base:.3f}</text>
{line(full[1][0],full[1][1],full[1][0],550)}{line(110,445,110,550)}{line(110,540,full[1][0],540,arrow=True)}<text x="{(110+full[1][0])/2:.3f}" y="533" text-anchor="middle" class="label">R {apex:.3f}</text>
<polygon class="edge" points="{poly(detail)}"/>
<text x="{detail[0][0]-22:.3f}" y="{detail[0][1]+24:.3f}" class="label">P1</text><text x="{detail[1][0]+12:.3f}" y="{detail[1][1]+5:.3f}" class="label">P2</text><text x="{detail[2][0]-22:.3f}" y="{detail[2][1]-12:.3f}" class="label">P3</text>
{line(detail[0][0],detail[0][1],detail[0][0],480)}{line(detail[1][0],detail[1][1],detail[1][0],480)}{line(detail[0][0],470,detail[1][0],470,arrow=True)}<text x="{(detail[0][0]+detail[1][0])/2:.3f}" y="463" text-anchor="middle" class="label">徑向 {apex-base:.3f}</text>
{line(detail[0][0],detail[0][1],820,detail[0][1])}{line(detail[2][0],detail[2][1],820,detail[2][1])}{line(830,detail[0][1],830,detail[2][1],arrow=True)}<text x="815" y="{(detail[0][1]+detail[2][1])/2:.3f}" text-anchor="middle" class="label" transform="rotate(-90 815 {(detail[0][1]+detail[2][1])/2:.3f})">軸向 {dz:.3f}</text>
{line(detail[1][0],detail[1][1],1350,detail[1][1])}{line(detail[0][0],detail[0][1],1350,detail[0][1])}{line(1340,detail[1][1],1340,detail[0][1],arrow=True)}<text x="1355" y="{(detail[1][1]+detail[0][1])/2:.3f}" class="label">{tipz:.3f}</text>
<text x="110" y="630" class="head">俯視：X–Y（各邊投影重合）</text><polyline class="edge" points="{poly(top+[top[0]])}"/><text x="110" y="760" class="small">Y 均為 0；不代表實體厚度。</text>
<text x="840" y="630" class="head">右視：Y–Z（各邊投影重合）</text><polyline class="edge" points="{poly(side+[side[0]])}"/><text x="985" y="825" class="small">Y 均為 0。</text>
<line x1="20" y1="870" x2="1530" y2="870" stroke="#173548" stroke-width="2"/><line x1="980" y1="870" x2="980" y2="1080" stroke="#173548" stroke-width="2"/><line x1="1260" y1="870" x2="1260" y2="1080" stroke="#173548" stroke-width="2"/>
<text x="45" y="905" class="small">頂點 P1：({p[0][0]:.3f}, {p[0][1]:.3f}, {p[0][2]:.3f}) mm；P2：({p[1][0]:.3f}, {p[1][1]:.3f}, {p[1][2]:.3f}) mm</text>
<text x="45" y="935" class="small">頂點 P3：({p[2][0]:.3f}, {p[2][1]:.3f}, {p[2][2]:.3f}) mm；0 面，3 邊。標註為數位讀值。</text>
<text x="45" y="965" class="small">材料、牙型標準、公差、配合、列印與實體試配：待定；非 ISO 認證圖。</text>
<text x="45" y="995" class="small">來源場景 SHA-256：{d['sourceSha256'][:16]}…；依標註值，勿量螢幕。</text>
<text x="45" y="1025" class="small">圖形來源是 Blender 網格頂點；尺寸標註為工程題圖，不是 Blender 操作截圖。</text>
<text x="1000" y="905" class="small">圖名：手工牙型輪廓</text><text x="1000" y="935" class="small">版次：v001</text><text x="1000" y="965" class="small">用途：教學草案</text>
<text x="1280" y="905" class="small">單位：mm</text><text x="1280" y="935" class="small">比例：隨畫面</text><text x="1280" y="965" class="small">實體試配：未做</text></svg>'''
out.write_text(svg+'\n',encoding='utf8',newline='\n')
print('drawing',out.relative_to(ROOT).as_posix(),sha256(out.read_bytes()).hexdigest())
