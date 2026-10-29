"""Draw actual GUI-created blind boss vertex rings; never overwrite a released figure."""
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
READ=ROOT/'learning/evidence/08/2026-10-28-manual-boss-drawing-v002/geometry-readback-v002.json'
READ_HASH='99b68b65b527f93bf4369808391d77b56fb5bddae805e63051131809983b8d67'
SCENE=ROOT/'learning/evidence/08/2026-10-28-manual-boss-gui-trial-v003/demo-files/u08_manual_boss_gui_v003.blend'
SCENE_HASH='fdeaccd41f4c73d8dc2323528f5dc760b46c498083ff1408d58a1c4c5924f2ca'
OUT=ROOT/'learning/web/challenges/manual-boss-drawing-v002.svg'

def build():
    if sha256(READ.read_bytes()).hexdigest()!=READ_HASH or sha256(SCENE.read_bytes()).hexdigest()!=SCENE_HASH:raise ValueError('來源 hash 不符')
    d=json.loads(READ.read_text(encoding='utf8')); rings=d['rings']
    if d['sourceSha256']!=SCENE_HASH or d['vertexCount']!=128 or any(len(rings[k])!=32 for k in ('4@0','4@8','2@8','2@1')):raise ValueError('來源頂點不符')
    out=rings['4@8']; hole=rings['2@8']; bottom=rings['2@1']; xs=[p[0] for p in out]; hx=[p[0] for p in hole]
    width=max(xs)-min(xs);holewidth=max(hx)-min(hx); ztop=sum(p[2] for p in out)/32; zbottom=sum(p[2] for p in rings['4@0'])/32; zfloor=sum(p[2] for p in bottom)/32
    if not (abs(width-8)<.001 and abs(holewidth-3.98066)<.001 and abs((ztop-zfloor)-7)<.001 and abs((zfloor-zbottom)-1)<.001):raise ValueError('幾何與指定來源不符')
    for ring in (out, hole, bottom):
        on_cut=[p[0] for p in ring if abs(p[1])<.001]
        if len(on_cut)!=2 or abs(min(on_cut)-min(p[0] for p in ring))>.001 or abs(max(on_cut)-max(p[0] for p in ring))>.001:raise ValueError('Y=0 截面與頂點邊界不符')
    S=40; origin=(250,315)
    def pt(p):return (origin[0]+p[0]*S,origin[1]-p[1]*S)
    def polygon(points):return ' '.join(f'{x:.3f},{y:.3f}' for x,y in map(pt,points))
    # Y=0 對頂截面的 X 邊界實讀；側壁以實際 N 邊形幾何投影，不假稱真圓。
    xleft,xright=min(xs),max(xs);hleft,hright=min(hx),max(hx)
    def section(x,z):return (970+x*S,190+(ztop-z)*S)
    sec=[(xleft,ztop),(hleft,ztop),(hleft,zfloor),(hright,zfloor),(hright,ztop),(xright,ztop),(xright,zbottom),(xleft,zbottom)]
    sect=' '.join(f'{x:.3f},{y:.3f}' for x,y in map(lambda p:section(*p),sec))
    center=250;left=center+min(xs)*S;right=center+max(xs)*S;hl=center+min(hx)*S;hr=center+max(hx)*S
    fleft,fright=left,right;ftop,fbottom=655,975
    sleft,sright=970+xleft*S,970+xright*S;stop,sbottom=655,975
    svg=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1550 1240" role="img" aria-labelledby="title desc">
<title id="title">手工盲孔柱｜工程題圖草案</title><desc id="desc">由獨立 Blender GUI 建立的 32 邊盲孔柱實際網格得出的俯視、主視、右視及 Y=0 剖面。外框約 8 × 8 × 8 mm；孔口對頂約 3.981 mm，孔深 7、底厚 1 mm；五金、公差、材料與實體適配均待定。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#244f6e"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#8a99a2" stroke-width="1"/></pattern></defs>
<style>text{{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#173548}}.edge{{stroke:#193548;stroke-width:2.4;fill:none}}.hidden{{stroke:#647c8a;stroke-width:1.4;stroke-dasharray:9 6;fill:none}}.dim{{stroke:#244f6e;stroke-width:1.3;fill:none}}.center{{stroke:#557b93;stroke-width:1.3;stroke-dasharray:12 5 3 5}}.label{{font-size:19px;fill:#244f6e}}.small{{font-size:17px}}.heading{{font-size:22px;font-weight:700}}</style>
<rect width="1550" height="1240" fill="white"/><rect x="20" y="20" width="1510" height="1200" fill="none" stroke="#173548" stroke-width="3"/>
<text x="50" y="60" font-size="28" font-weight="700">手工盲孔柱｜工程題尺寸圖</text><text x="50" y="89" class="small">GUI 示範模型 · 尺寸為數位讀值／名義草案 · 單位 mm · 非製造或配合合格</text>
<text x="130" y="115" class="heading">俯視（+Z 朝 −Z）</text><text x="825" y="115" class="heading">A–A 中央剖面（−Y 朝 +Y）</text>
<polygon class="edge" points="{polygon(out)}"/><polygon class="edge" points="{polygon(hole)}"/>
<line class="center" x1="55" y1="315" x2="445" y2="315"/><line class="center" x1="250" y1="120" x2="250" y2="510"/>
<line class="dim" x1="65" y1="333" x2="65" y2="296" marker-end="url(#arrow)"/><line class="dim" x1="435" y1="333" x2="435" y2="296" marker-end="url(#arrow)"/><text x="47" y="294" class="label">A</text><text x="444" y="294" class="label">A</text>
<polygon points="{sect}" fill="url(#hatch)" stroke="#193548" stroke-width="2.4"/>
<text x="130" y="600" class="heading">主視（−Y 朝 +Y）</text><text x="895" y="600" class="heading">右視（+X 朝 −X）</text>
<rect class="edge" x="{fleft:.3f}" y="{ftop}" width="{fright-fleft:.3f}" height="{fbottom-ftop}"/><path class="hidden" d="M{hl:.3f} {ftop} V{ftop+(ztop-zfloor)*S:.3f} H{hr:.3f} V{ftop}"/>
<rect class="edge" x="{sleft}" y="{stop}" width="{sright-sleft}" height="{sbottom-stop}"/><path class="hidden" d="M{970+hleft*S:.3f} {stop} V{stop+(ztop-zfloor)*S:.3f} H{970+hright*S:.3f} V{stop}"/>
<g class="dim"><path d="M{left:.3f} 155 V185 M{right:.3f} 155 V185"/><line x1="{left:.3f}" y1="159" x2="{right:.3f}" y2="159" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M{hl:.3f} 228 V194 M{hr:.3f} 228 V194"/><line x1="{hl:.3f}" y1="198" x2="{hr:.3f}" y2="198" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M{fleft:.3f} {ftop} H45 M{fleft:.3f} {fbottom} H45"/><line x1="48" y1="{ftop}" x2="48" y2="{fbottom}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M{970+xright*S:.3f} 190 H1237 M{970+xright*S:.3f} {190+(ztop-zfloor)*S:.3f} H1237"/><line x1="1233" y1="190" x2="1233" y2="{190+(ztop-zfloor)*S:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M{970+xright*S:.3f} {190+(ztop-zfloor)*S:.3f} H1290 M{970+xright*S:.3f} {190+(ztop-zbottom)*S:.3f} H1290"/><line x1="1286" y1="{190+(ztop-zfloor)*S:.3f}" x2="1286" y2="{190+(ztop-zbottom)*S:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>
<g class="label"><text x="250" y="151" text-anchor="middle">Ø8 對頂</text><text x="250" y="190" text-anchor="middle">約 Ø{holewidth:.3f} 對頂</text><text x="39" y="815" text-anchor="middle" transform="rotate(-90 39 815)">8</text><text x="1252" y="330" text-anchor="middle" transform="rotate(-90 1252 330)">孔深 7</text><text x="1302" y="500">底厚 1</text></g>
<text x="55" y="1020" class="small">Ø 為 32 邊形頂點對頂點數位讀值，非真圓、非五金匹配孔徑；孔深與底厚以 Z 範圍與射線核對。</text>
<line x1="20" y1="1045" x2="1530" y2="1045" stroke="#173548" stroke-width="2"/><line x1="20" y1="1130" x2="1530" y2="1130" stroke="#173548" stroke-width="1.5"/><line x1="985" y1="1045" x2="985" y2="1220" stroke="#173548" stroke-width="1.5"/><line x1="1285" y1="1045" x2="1285" y2="1220" stroke="#173548" stroke-width="1.5"/>
<text x="45" y="1074" class="small">材料、五金、孔徑公差、製程與強度：待定；未切片、列印或試配。</text><text x="45" y="1101" class="small">來源為 GUI 另存重開的獨立柱；與小盒的接合為另一份示範，非此圖成果。</text>
<text x="45" y="1162" class="small">來源 SHA-256：fdeaccd41f4c73d8…；單位：mm；以標註值為準，勿量螢幕。</text><text x="45" y="1190" class="small">Inset 2 mm 的結果實讀孔口約 {holewidth:.3f} mm，不能把 4 mm 視為實際孔口。</text>
<text x="1005" y="1075" class="small">圖名：獨立盲孔柱</text><text x="1005" y="1105" class="small">圖號：BOSS-EDU-001</text><text x="1005" y="1162" class="small">版次：v002</text><text x="1005" y="1190" class="small">投影：第三角式排列</text>
<text x="1305" y="1075" class="small">用途：教學草案</text><text x="1305" y="1105" class="small">製造核准：待定</text><text x="1305" y="1162" class="small">比例：隨畫面縮放</text><text x="1305" y="1190" class="small">實體試配：未做</text></svg>''']
    return '\n'.join(svg)+'\n'

def main():
    if OUT.exists():raise FileExistsError('拒絕覆寫現有工程圖')
    content=build().encode('utf8');OUT.write_bytes(content)
    print('sha256',sha256(content).hexdigest(),'bytes',len(content))
if __name__=='__main__':main()
