"""由既有草圖與網格讀值產生第 07／08 章題圖；原始 Blender 模型不修改。"""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'learning/evidence/parametric'
OUT = ROOT / 'learning/web/challenges'
SOURCES = {
    'sketch60': ('2026-10-27-cad-sketcher-rectangle-v002/rectangle-60-verification.json', 'f025c42f3bcbfe67df4ebf0e48077542c4e10167e67f33f40ef9809e8caac766'),
    'sketch80': ('2026-10-27-cad-sketcher-rectangle-v002/rectangle-80-verification.json', '235dc960ae116a1e9b871d7df3c79c865e1e3d4d0fc0c2bdb3839bbef201a9bb'),
    'fixed': ('2026-10-27-manual-box-lid-inspect-v001/fixed-lid-mesh-verification-v001.json', '3c4829f5b1ac01010dc1e4e98a3220388f3fc139e96b5e79c3b898736decf599'),
    'fixedScene': ('2026-10-27-manual-box-lid-geometry-v002/demo-files/manual_box_lid_fixed_80x50_v001.blend', 'c870ffe0366bee23e44f1a13d12259460f100a723f7753de0f28f8e84c43f508'),
}


def read_source(key):
    rel, expected = SOURCES[key]
    data = (BASE / rel).read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError('來源 SHA 不符：' + rel)
    return data


def pos_bounds(key, expected):
    data = json.loads(read_source(key))
    sketch = data['actual']['sketch']
    xyz = sketch['positions']
    bounds = tuple((min(p[i] for p in xyz), max(p[i] for p in xyz)) for i in range(3))
    if bounds != expected or sketch['solverState'] != 'OKAY' or sketch['dof'] != 0:
        raise ValueError('草圖位置／求解狀態與已驗證來源不符：' + key)
    return bounds


def frame(title, desc, width, height):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{desc}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#244c6b"/></marker>
<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line y2="8" stroke="#82909a" stroke-width="1"/></pattern></defs>
<style>text{{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#173247}} .edge{{fill:none;stroke:#142c3a;stroke-width:2.4}} .dim{{fill:none;stroke:#244c6b;stroke-width:1.2}} .center{{fill:none;stroke:#57778d;stroke-width:1.1;stroke-dasharray:12 5 3 5}} .num{{fill:#244c6b;font-size:20px}} .small{{font-size:19px}} .minor{{font-size:17px}} .head{{font-size:25px;font-weight:700}}</style>
<rect width="{width}" height="{height}" fill="white"/><rect x="22" y="22" width="{width-44}" height="{height-44}" fill="none" stroke="#173247" stroke-width="3"/>
<text x="50" y="60" font-size="29" font-weight="700">{title}</text>
<text x="50" y="90" class="small">教學草案 · 標示值為名義尺寸 · 單位 mm · 不作正式製造／驗收圖</text>'''


def rect(x, y, w, h):
    return f'<rect class="edge" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"/>'


def horizontal(x1, x2, ypart, ydim, label):
    return (f'<path class="dim" d="M{x1:.3f} {ypart:.3f} V{ydim:.3f} M{x2:.3f} {ypart:.3f} V{ydim:.3f}"/>'
            f'<line class="dim" x1="{x1:.3f}" y1="{ydim:.3f}" x2="{x2:.3f}" y2="{ydim:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
            f'<text class="num" x="{(x1+x2)/2:.3f}" y="{ydim-7:.3f}" text-anchor="middle">{label}</text>')


def vertical(y1, y2, xpart, xdim, label):
    return (f'<path class="dim" d="M{xpart:.3f} {y1:.3f} H{xdim:.3f} M{xpart:.3f} {y2:.3f} H{xdim:.3f}"/>'
            f'<line class="dim" x1="{xdim:.3f}" y1="{y1:.3f}" x2="{xdim:.3f}" y2="{y2:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
            f'<text class="num" x="{xdim-8:.3f}" y="{(y1+y2)/2:.3f}" text-anchor="middle" transform="rotate(-90 {xdim-8:.3f} {(y1+y2)/2:.3f})">{label}</text>')


def sketch_figure():
    b60=pos_bounds('sketch60',((0.,60.),(0.,40.),(0.,0.)))
    b80=pos_bounds('sketch80',((0.,80.),(0.,40.),(0.,0.)))
    svg=[frame('第 07 章｜XY 矩形草圖尺寸題圖','CAD Sketcher 兩個不同版本的草圖尺寸，先 60×40 再改成 80×40 mm。',1600,1030)]
    svg += ['<text class="head" x="170" y="145">步驟 A · 原始草圖（俯視 XY）</text>',
            '<text class="head" x="880" y="145">步驟 B · X 修改後（俯視 XY）</text>']
    scale=7
    for (x,y,bounds) in ((170,220,b60),(880,220,b80)):
        w=(bounds[0][1]-bounds[0][0])*scale; h=(bounds[1][1]-bounds[1][0])*scale
        svg += [rect(x,y,w,h),horizontal(x,x+w,y,y-35,str(int(w/scale))),vertical(y,y+h,x,x-40,str(int(h/scale))),
                f'<circle cx="{x}" cy="{y+h}" r="4" fill="#a44b20"/><text class="small" x="{x+10}" y="{y+h+28}">原點 (0, 0)</text>',
                f'<path class="dim" d="M{x} {y+h+48} h80 M{x} {y+h+48} v-70"/><text class="small" x="{x+85}" y="{y+h+54}">+X</text><text class="small" x="{x-5}" y="{y+h-28}">+Y</text>']
    svg += ['<text class="small" x="50" y="640">A 與 B 是同一草圖在不同保存階段的名義尺寸，不是兩個零件。</text>',
            '<text class="small" x="50" y="675">60×40 → 80×40：本次讀值記錄 solver OKAY、DoF 0；只表示此示範草圖的狀態。</text>',
            '<text class="small" x="50" y="710">平面草圖不含盒底、內腔或上蓋；拉伸與後續布林結果需另行核對。</text>',
            '<line x1="22" y1="770" x2="1578" y2="770" stroke="#173247" stroke-width="2"/>',
            '<text class="minor" x="50" y="804">來源：獨立 Blender／CAD Sketcher 草圖驗證 rectangle-60 與 rectangle-80，圖面由已讀回的草圖座標重建。</text>',
            '<text class="minor" x="50" y="833">60×40 摘要 SHA-256 f025c42f3bcbfe67…　｜　80×40 摘要 SHA-256 235dc960ae116a1e…</text>',
            '<text class="minor" x="50" y="862">草圖座標基準：(0,0)；視圖縮放不供量尺。材料、製程、公差、實體結果：待定。</text>',
            '<line x1="22" y1="900" x2="1578" y2="900" stroke="#173247" stroke-width="1.5"/>',
            '<text class="minor" x="50" y="935">圖號 SKETCH-EDU-001　　版次 v001　　單位 mm　　比例：隨螢幕縮放</text>',
            '<text class="minor" x="50" y="966">教學用途：依草圖實際讀值辨識尺寸與約束；未確認學員完成。</text></svg>']
    return '\n'.join(svg)


def close(actual, nominal, eps=0.001):
    if abs(actual-nominal)>eps:
        raise ValueError('幾何讀值不符預期：%s vs %s'%(actual,nominal))


def box_figure():
    raw=json.loads(read_source('fixed')); read_source('fixedScene')
    if raw['scene']['sha256']!=SOURCES['fixedScene'][1]: raise ValueError('場景 SHA 與摘要不一致')
    body=raw['bodyAndLidEvaluation']['Body']['levels']; cutter=raw['bodyAndLidEvaluation']['Body.001']['levels']; lid=raw['bodyAndLidEvaluation']['Cube']['levels']
    bx=body['30.0']['x']; by=body['30.0']['y']; lx=lid['26.0']['x']; ly=lid['26.0']['y']
    for actual, expected in zip(bx,[0,2,78,80]): close(actual,expected)
    for actual, expected in zip(by,[0,2,48,50]): close(actual,expected)
    for actual, expected in zip(lx,[2.2,4.2,75.8,77.8]): close(actual,expected)
    for actual, expected in zip(ly,[2.2,4.2,45.8,47.8]): close(actual,expected)
    for actual, expected in zip(cutter['30.0']['x'],[2,78]): close(actual,expected)
    for actual, expected in zip(cutter['30.0']['y'],[2,48]): close(actual,expected)
    platex=lid['32.0']['x'];platey=lid['32.0']['y']
    close(platex[0],0);close(platex[1],80);close(platey[0],0);close(platey[1],50)
    svg=[frame('第 08 章｜固定基準盒體與上蓋','依固定 80×50 版本已驗證的 Body、Body.001 切割體及 Cube 上蓋頂點界限製作的名義尺寸圖。',1800,1440)]
    svg += ['<text class="head" x="170" y="145">Body 盒體俯視</text>', '<text class="head" x="1010" y="145">Cube 上蓋底視（環唇）</text>']
    s=7; x=170; y=215; x2=1010
    svg += [rect(x,y,80*s,50*s),rect(x+2*s,y+2*s,76*s,46*s),
            horizontal(x,x+80*s,y,y-56,'80'),horizontal(x+2*s,x+78*s,y+2*s,y-27,'76'),
            vertical(y,y+50*s,x,x-57,'50'),vertical(y+2*s,y+48*s,x+2*s,x-29,'46')]
    # Top coordinates use the actual readback vertex levels, including minor GUI resize residuals.
    ox=x2+platex[0]*s; oy=y+(50-platey[1])*s
    svg += [rect(ox,oy,(platex[1]-platex[0])*s,(platey[1]-platey[0])*s),
            rect(x2+lx[0]*s,y+(50-ly[3])*s,(lx[3]-lx[0])*s,(ly[3]-ly[0])*s),
            rect(x2+lx[1]*s,y+(50-ly[2])*s,(lx[2]-lx[1])*s,(ly[2]-ly[1])*s),
            horizontal(x2,x2+80*s,y,y-56,'80（名義）'),horizontal(x2+lx[0]*s,x2+lx[3]*s,y+(50-ly[3])*s,y-27,'75.6（名義）'),
            vertical(y,y+50*s,x2,x2-55,'50（名義）'),vertical(y+(50-ly[3])*s,y+(50-ly[0])*s,x2+lx[0]*s,x2-28,'45.6（名義）')]
    svg += ['<line class="center" x1="130" y1="390" x2="770" y2="390"/><text class="num" x="112" y="385">A</text><text class="num" x="777" y="385">A</text>',
            '<text class="head" x="170" y="680">A–A 中央剖面（Y = 25 mm，沿 +Y 觀看）</text>']
    # X-Z section read from the actual level boundaries; body and lid are separate objects.
    sx=200; baseline=1110; scale=10
    xp=lambda n:sx+n*scale; zp=lambda n:baseline-n*scale
    svg += [f'<path d="M{xp(0)} {zp(30)} H{xp(2)} V{zp(2)} H{xp(78)} V{zp(30)} H{xp(80)} V{zp(0)} H{xp(0)} Z" fill="url(#hatch)" stroke="#142c3a" stroke-width="2"/>',
            f'<path d="M{xp(platex[0])} {zp(32)} H{xp(platex[1])} V{zp(30)} H{xp(lx[3])} V{zp(26)} H{xp(lx[2])} V{zp(30)} H{xp(lx[1])} V{zp(26)} H{xp(lx[0])} V{zp(30)} H{xp(platex[0])} Z" fill="url(#hatch)" stroke="#496e86" stroke-width="2"/>',
            horizontal(xp(0),xp(80),zp(0),1155,'80'),
            vertical(zp(30),zp(0),xp(80),xp(80)+65,'30'),
            vertical(zp(30),zp(2),xp(78),xp(80)+35,'28'),
            '<text class="small" x="1075" y="808">上蓋板厚名義 2；環唇向下 4，唇壁名義厚 2。</text>',
            '<text class="small" x="1075" y="844">盒壁及底厚名義 2；內腔 76 × 46 × 28。</text>',
            '<text class="small" x="1075" y="880">盒口內寬 76；唇外名義寬 75.6。</text>',
            '<text class="small" x="1075" y="916">名義總間隙 0.4；置中每側約 0.2，僅為試驗值。</text>',
            '<text class="small" x="1075" y="952">真實頂點有約 0.0005 mm 建模殘差；標註為名義值。</text>',
            '<text class="small" x="1075" y="988">此為固定基準幾何，不代表本圖已建立自動連動。</text>',
            '<text class="small" x="1075" y="1024">原生欄位可繞過受控面板；更新／幾何需另行核對。</text>',
            '<text class="small" x="1075" y="1060">未做完整干涉、實體列印、量測及試配。</text>',
            '<line x1="22" y1="1200" x2="1778" y2="1200" stroke="#173247" stroke-width="2"/>',
            '<text class="minor" x="50" y="1233">Body 盒體、Body.001 切割體與 Cube 上蓋頂點讀值：fixed-lid-mesh-verification-v001.json　SHA 3c4829f5b1ac0101…</text>',
            '<text class="minor" x="50" y="1260">來源 Blender 固定版本 manual_box_lid_fixed_80x50_v001.blend　SHA c870ffe0366bee23…；兩件非學員作品。</text>',
            '<text class="minor" x="50" y="1287">實體公差、材料、製程、強度與配合：待定。標註按 mm，畫面比例隨縮放，不可量螢幕。</text>',
            '<line x1="22" y1="1320" x2="1778" y2="1320" stroke="#173247" stroke-width="1.5"/>',
            '<text class="minor" x="50" y="1353">圖號 PARAM-BOX-EDU-001　　版次 v001　　單位 mm　　比例：隨螢幕縮放　　製造核准：待定</text>',
            '<text class="minor" x="50" y="1383">此圖僅用於理解固定基準與名義尺寸；參數連動的各狀態須另依示範讀值核對。</text></svg>']
    return '\n'.join(svg)


def main():
    paths=[OUT/'sketch-constraint-drawing-v001.svg',OUT/'parametric-box-drawing-v001.svg']
    if any(p.exists() for p in paths): raise FileExistsError('題圖已存在，拒絕覆寫')
    values=[sketch_figure(),box_figure()]
    OUT.mkdir(parents=True,exist_ok=True)
    for path,text in zip(paths,values):
        with path.open('x',encoding='utf-8',newline='\n') as handle:handle.write(text+'\n')
        print(path.name,'bytes',path.stat().st_size,'sha256',sha256(path.read_bytes()).hexdigest())


if __name__=='__main__': main()
