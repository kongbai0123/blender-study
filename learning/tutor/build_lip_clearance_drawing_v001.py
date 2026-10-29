"""由盒體與環唇上蓋實際 STL 取 Y=0 剖面，提供配合概念題。"""
from hashlib import sha256
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
BODY=ROOT/'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.stl'
LID=ROOT/'learning/evidence/05/2026-10-25-lesson05-lid-export-demo-v001/demo-files/exports/u05_lid_v001.stl'
OUT=ROOT/'learning/web/challenges/lip-clearance-drawing-v001.svg'
BODY_HASH='0e8fc0863ea9f392e6231f8e0c7444148c000f00010454e263fae0e09f145bb9'
LID_HASH='0b226cf405bc70f42b5ce28fee9f46cb55eff67b84c6d786c091a2043f5f2408'

def load(path,expected,count):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=expected: raise ValueError('來源 STL 雜湊不符')
    n=struct.unpack_from('<I',data,80)[0]
    if n!=count or len(data)!=84+50*n: raise ValueError('來源 STL 長度或面數不符')
    return [[struct.unpack_from('<3f',data,84+50*i+12+12*j) for j in range(3)] for i in range(n)]

def cross(tris):
    """Y=0 與三角面交線，四位小數僅作浮點重建。"""
    result=set()
    for tri in tris:
        pts=set()
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3]; u,v=a[1],b[1]
            if abs(u)<1e-7: pts.add((round(a[0],4),round(a[2],4)))
            if u*v<0:
                t=-u/(v-u);pts.add((round(a[0]+t*(b[0]-a[0]),4),round(a[2]+t*(b[2]-a[2]),4)))
        if len(pts)==2: result.add(tuple(sorted(pts)))
        elif len(pts)>2:raise ValueError('出現與切面共面的三角形')
    return sorted(result)

def inspect():
    body,lid=load(BODY,BODY_HASH,28),load(LID,LID_HASH,44)
    b,l=cross(body),cross(lid)
    if len(b)!=16 or len(l)!=24:raise ValueError('截面交線與來源基準不符')
    def has(segs,p):return any(any(abs(x-p[0])<1e-4 and abs(z-p[1])<1e-4 for x,z in seg) for seg in segs)
    for p in [(-30,-15),(30,15),(-28,15),(28,15)]:
        if not has(b,p):raise ValueError('盒體剖面缺少關鍵點')
    for p in [(-30,15),(30,17),(27.8,11),(25.8,11),(-27.8,11),(-25.8,11)]:
        if not has(l,p):raise ValueError('上蓋剖面缺少關鍵點')
    return b,l

def build():
    body,lid=inspect()
    svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1370" role="img" aria-labelledby="title desc">
<title id="title">環唇與盒口間隙工程題圖</title><desc id="desc">依盒體與上蓋 STL 原有世界位置的 Y=0 真實交線，解釋名義總間隙與每側間隙；數值尚未實配驗證。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker><clipPath id="detail"><rect x="130" y="715" width="600" height="555"/></clipPath></defs>
<style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#18384b}.body{stroke:#17364a;stroke-width:3;fill:none}.lid{stroke:#a65a20;stroke-width:3;fill:none}.dim{stroke:#244f6e;stroke-width:1.4;fill:none}.center{stroke:#6b899b;stroke-width:1.2;stroke-dasharray:10 4 3 4;fill:none}.big{font-size:25px;font-weight:700}.small{font-size:19px}.label{font-size:20px;fill:#244f6e}</style>
<rect width="1900" height="1370" fill="white"/><rect x="20" y="20" width="1860" height="1330" fill="none" stroke="#17384c" stroke-width="3"/>
<text x="55" y="65" class="big">環形唇邊與盒口｜配合間隙題圖</text><text x="55" y="100" class="small">單位 mm（STL 無單位，依教材按 mm 解讀） · 數位幾何草案 · 尚未實體試配</text>
<text x="120" y="150" class="big">頂部外框（由 +Z 朝 −Z）</text><rect x="120" y="190" width="600" height="400" fill="none" stroke="#a65a20" stroke-width="3"/>
<path class="center" d="M100 390H740"/><path class="dim" d="M105 405V375" marker-end="url(#arrow)"/><path class="dim" d="M735 405V375" marker-end="url(#arrow)"/><text x="78" y="370" class="label">A</text><text x="745" y="370" class="label">A</text>
<text x="805" y="100" class="big">A–A 組合剖面（Y = 0，由 −Y 朝 +Y）</text>''']
    def full(p):return (820+(p[0]+30)*14,650-(p[1]+15)*14)
    def detail(p):return (130+(p[0]-24)*100,715+(17-p[1])*100)
    def lines(segs,cls,fn):
        for a,b in segs:
            x1,y1=fn(a);x2,y2=fn(b)
            svg.append(f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"/>')
    lines(body,'body',full);lines(lid,'lid',full)
    svg += ['<g class="dim"><path d="M820 650V690 M1660 650V690 M1660 650H1710 M1660 230H1710"/><path d="M820 685H1660" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1706 230V650" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>',
            '<text x="1240" y="715" class="label" text-anchor="middle">盒體外寬 60</text><text x="1730" y="440" class="label" text-anchor="middle" transform="rotate(-90 1730 440)">盒體高 30</text>',
            '<text x="120" y="670" class="big">右側環唇及盒口局部放大（相同截面）</text>',
            '<rect x="130" y="715" width="600" height="555" fill="#f7fafc" stroke="#aac0cd" stroke-width="1"/><g clip-path="url(#detail)">']
    lines(body,'body',detail);lines(lid,'lid',detail)
    svg += ['</g>',
            '<g class="dim"><path d="M510 1065H530" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>',
            '<path class="dim" d="M520 1065L625 1100L690 1100"/><text x="630" y="1130" class="label">單側 0.2</text>',
            '<text x="800" y="780" class="big">名義尺寸與間隙（mm）</text>',
            '<text x="800" y="820" class="small">盒口內形 X × Y：56 × 36；上蓋唇邊外形：55.6 × 35.6。</text>',
            '<text x="800" y="855" class="small">X、Y 方向總間隙各 0.4；置中時各側名義 0.2。</text>',
            '<text x="800" y="890" class="small">唇邊內形：51.6 × 31.6；環壁 2，向下深度 4。</text>',
            '<text x="800" y="925" class="small">示範 STL 讀值單側約 0.200000763、總約 0.400001526。</text>',
            '<text x="800" y="960" class="small">上述為數位名義試驗值，不是量測後的公差或合格間隙。</text>',
            '<line class="body" x1="800" y1="1000" x2="860" y2="1000"/><text x="875" y="1007" class="small">盒體實際截面</text>',
            '<line class="lid" x1="1120" y1="1000" x2="1180" y2="1000"/><text x="1195" y="1007" class="small">上蓋實際截面</text>',
            '<text x="800" y="1045" class="small">兩 STL 保留來源世界位置，未額外平移；局部只做圖面放大。</text>',
            '<text x="800" y="1080" class="small">材料、製程、尺寸與幾何公差、檢驗：待定。</text>',
            '<text x="800" y="1115" class="small">實體列印、量測及試配：未執行；實體合格間隙：待定。</text>',
            '<text x="800" y="1150" class="small">外框視圖為上蓋投影；尺寸以標註值為準，請勿量取螢幕。</text>',
            '<text x="800" y="1185" class="small">來源：u04_box_v001.stl、u05_lid_v001.stl。</text>',
            '<text x="800" y="1220" class="small">來源 SHA-256：0e8fc0863ea9f392…／0b226cf405bc70f4…</text>',
            '<line x1="20" y1="1288" x2="1880" y2="1288" stroke="#17384c" stroke-width="2"/><line x1="1200" y1="1288" x2="1200" y2="1350" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1328" class="small">教學草案：資料取自 STL 剖面與既有數位讀值，不作正式製造圖。</text>',
            '<text x="1230" y="1328" class="small">圖號 LIP-EDU-001　版次 v001　比例隨畫面縮放</text></svg>']
    return '\n'.join(svg)

if __name__=='__main__':
    if OUT.exists():raise FileExistsError('拒絕覆寫既有試教題圖')
    content=build();OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x',encoding='utf-8',newline='\n') as f:f.write(content)
    print('written',OUT,'sha256',sha256(OUT.read_bytes()).hexdigest(),'bytes',OUT.stat().st_size)
