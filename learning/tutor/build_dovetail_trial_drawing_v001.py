"""由示範盒與滑蓋 STL 的實際 X=0 交線產生工程題圖，不改模型。"""
from hashlib import sha256
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'learning/evidence/06/2026-10-25-lesson06-dovetail-export-demo-v001/demo-files/exports'
BODY=BASE/'u06_dovetail_body_v001.stl'
LID=BASE/'u06_dovetail_lid_v001.stl'
OUT=ROOT/'learning/web/challenges/dovetail-trial-drawing-v001.svg'
BODY_HASH='747e6186876f0e00c5c0617f0631de890a610696e42a930d5f7a0452f8ab4586'
LID_HASH='436597611a951ead9878cb330bda8a4a306f014cb70183c894987666113ee713'

def read(path,expected):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=expected: raise ValueError('STL hash 不符')
    n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n: raise ValueError('STL 長度不符')
    return [[struct.unpack_from('<3f',data,84+50*i+12+12*j) for j in range(3)] for i in range(n)]

def cut(triangles):
    """X=0 三角形與平面交線；四位小數僅用於浮點重建，非製造公差。"""
    result=set()
    for tri in triangles:
        points=set()
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3]; u,v=a[0],b[0]
            if abs(u)<1e-7: points.add((round(a[1],4),round(a[2],4)))
            if u*v<0:
                t=-u/(v-u)
                points.add((round(a[1]+t*(b[1]-a[1]),4),round(a[2]+t*(b[2]-a[2]),4)))
        if len(points)==2: result.add(tuple(sorted(points)))
        elif len(points)>2: raise ValueError('截面與三角面共面，需另行分析')
    return sorted(result)

def near(value,target): return abs(value-target)<1e-4

def inspect():
    body,lid=read(BODY,BODY_HASH),read(LID,LID_HASH)
    if len(body)!=124 or len(lid)!=68: raise ValueError('三角面數不符')
    sections=[cut(body),cut(lid)]
    if len(sections[0])!=48 or len(sections[1])!=24: raise ValueError('實際截面交線數變化，須重新審查')
    def point_present(segs,p): return any(any(near(x,p[0]) and near(y,p[1]) for x,y in seg) for seg in segs)
    for expected in [(-20,-15),(20,15),(-18.8,11.8),(-15.2,11.8),(-18.16,15),(-15.84,15),(14,10)]:
        if not point_present(sections[0],expected): raise ValueError('盒體截面關鍵點不符')
    for expected in [(-20,15.2),(20,17.2),(-18.56,12),(-15.44,12),(-17.92,15.2),(-16.08,15.2)]:
        if not point_present(sections[1],expected): raise ValueError('上蓋截面關鍵點不符')
    return sections

def build():
    body,lid=inspect()
    svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1370" role="img" aria-labelledby="title desc">
<title id="title">燕尾滑蓋組合截面工程題圖</title><desc id="desc">示範盒體及滑蓋 STL 在 X=0 的真實交線，搭配俯視外框及一側導槽放大圖；0.4 毫米為未經實配的水平總間隙試驗值。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker><clipPath id="detail"><rect x="150" y="755" width="480" height="496"/></clipPath></defs>
<style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#18384b}.body{stroke:#17364a;stroke-width:3;fill:none}.lid{stroke:#a65a20;stroke-width:3;fill:none}.dim{stroke:#244f6e;stroke-width:1.4;fill:none}.center{stroke:#527993;stroke-width:1.3;stroke-dasharray:12 5 3 5;fill:none}.big{font-size:26px;font-weight:700}.small{font-size:19px}.label{font-size:20px;fill:#244f6e}</style>
<rect width="1900" height="1370" fill="white"/><rect x="20" y="20" width="1860" height="1330" fill="none" stroke="#17384c" stroke-width="3"/>
<text x="55" y="65" class="big">燕尾滑蓋｜組合截面工程題圖</text><text x="55" y="98" class="small">單位 mm（STL 無單位標記，依教材按 mm 解讀） · 數位幾何草案 · 實體試配尚未執行</text>
<text x="150" y="145" class="big">頂部外框（由 +Z 朝 −Z）</text><rect x="150" y="195" width="600" height="400" fill="none" stroke="#a65a20" stroke-width="3"/>
<path class="center" d="M450 175V615"/><path class="dim" d="M465 190H435" marker-end="url(#arrow)"/><path class="dim" d="M465 600H435" marker-end="url(#arrow)"/><text x="415" y="170" class="label">A</text><text x="415" y="640" class="label">A</text>
<g class="dim"><path d="M150 195V165 M750 195V165 M150 195H95 M150 595H95"/><path d="M150 168H750" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M98 195V595" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>
<text x="450" y="160" class="label" text-anchor="middle">60</text><text x="88" y="395" class="label" text-anchor="middle" transform="rotate(-90 88 395)">40</text>
<text x="830" y="145" class="big">A–A 組合截面（X = 0，由 +X 朝 −X）</text>''']
    # Actual world coordinates of STL plane intersection, using same scale in Y and Z.
    def full(p): return (880+(p[0]+20)*16,650-(p[1]+15)*16)
    def detail(p): return (150+(p[0]-14)*80,755+(17.4-p[1])*80)
    def add(segs,cls,transform):
        for a,b in segs:
            x1,y1=transform(a); x2,y2=transform(b)
            svg.append(f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"/>')
    add(body,'body',full); add(lid,'lid',full)
    svg += ['<g class="dim"><path d="M880 650V685 M1520 650V685 M1520 650H1580 M1520 170H1580"/><path d="M880 680H1520" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1576 170V650" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>',
            '<text x="1200" y="710" class="label" text-anchor="middle">盒體 40</text><text x="1600" y="410" class="label" transform="rotate(-90 1600 410)" text-anchor="middle">盒體 30</text>',
            '<text x="150" y="720" class="big">右側燕尾局部放大（與 A–A 相同交線）</text>',
            '<rect x="150" y="755" width="480" height="496" fill="#f7fafc" stroke="#aac0cd" stroke-width="1"/><g clip-path="url(#detail)">']
    add(body,'body',detail); add(lid,'lid',detail)
    svg += ['</g>',
            '<text x="710" y="780" class="big">名義幾何條件（mm）</text>',
            '<text x="710" y="822" class="small">盒體外形 60 × 40 × 30；蓋板 60 × 40 × 2。</text>',
            '<text x="710" y="856" class="small">上蓋含燕尾榫外框總厚約 5.2；不等於蓋板厚度。</text>',
            '<text x="710" y="890" class="small">槽：底寬約 3.6、盒頂槽口寬約 2.32、深約 3.2。</text>',
            '<text x="710" y="924" class="small">榫：底寬約 3.12、與蓋板接合處寬約 1.84、外露深約 3.2。</text>',
            '<text x="710" y="958" class="small">同高度水平總間隙 0.4（每側名義 0.2）：僅為試驗值。</text>',
            '<text x="710" y="992" class="small">水平間隙與斜面法向間隙不同；圖像放大後請勿量螢幕。</text>',
            '<text x="710" y="1026" class="small">盒內導軌底部有朝下水平懸空面；切片、支撐與方向待驗。</text>',
            '<line class="body" x1="710" y1="1065" x2="765" y2="1065"/><text x="780" y="1072" class="small">盒體截面交線</text>',
            '<line class="lid" x1="1030" y1="1065" x2="1085" y2="1065"/><text x="1100" y="1072" class="small">上蓋截面交線</text>',
            '<text x="710" y="1110" class="small">公差、材料、製程、表面、檢驗及製造核准：待定。</text>',
            '<text x="710" y="1144" class="small">尚未列印、量測或試配；此圖不得作配合合格或強度判定。</text>',
            '<text x="710" y="1178" class="small">來源：u06_dovetail_body_v001.stl / u06_dovetail_lid_v001.stl。</text>',
            '<text x="710" y="1212" class="small">剖面為 STL 三角網格與 X=0 的實際交線；頂視為上蓋外框。</text>',
            '<line x1="20" y1="1270" x2="1880" y2="1270" stroke="#17384c" stroke-width="2"/><line x1="1250" y1="1270" x2="1250" y2="1350" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1303" class="small">來源 SHA-256：盒體 747e6186876f0e00…；上蓋 436597611a951ead…</text>',
            '<text x="55" y="1335" class="small">教學草案：保留本機原始資料及讀值；來源 STL 不含單位。</text>',
            '<text x="1280" y="1303" class="small">圖號：DOVETAIL-EDU-001　版次：v001</text><text x="1280" y="1335" class="small">單位：mm　比例：隨畫面縮放</text></svg>']
    return '\n'.join(svg)

if __name__=='__main__':
    if OUT.exists(): raise FileExistsError('拒絕覆寫舊圖')
    value=build();OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x',encoding='utf-8',newline='\n') as f:f.write(value)
    print('written',OUT,'sha256',sha256(OUT.read_bytes()).hexdigest(),'bytes',OUT.stat().st_size)
