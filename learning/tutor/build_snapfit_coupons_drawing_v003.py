"""以三件卡扣試片 STL 真實切面製作比較圖，僅供教學。"""
from hashlib import sha256
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'learning/evidence/07/2026-10-25-lesson07-coupon-export-demo-v001/demo-files/exports'
OUT=ROOT/'learning/web/challenges/snapfit-coupons-drawing-v003.svg'
CASES=(
 ('A_L19',-12.,19.,24.,'bb40b5f669601e11bc97d41f48e8a65552bfe99bb21645d47d359098c62af168'),
 ('B_L17',0.,17.,22.,'ac0f9ca920197544f7c47465901beb98059b69b99d5aa9ad88ac9d73d16d017a'),
 ('C_L21',12.,21.,26.,'1e3bb7cb883fd5d00319ebd9f44b761843b3c1b8f4c644e3333ac7a463083788'),
)

def read_stl(name,expected):
    data=(BASE/f'u07_{name}_v001.stl').read_bytes()
    if sha256(data).hexdigest()!=expected: raise ValueError('來源 STL 雜湊不符：'+name)
    n=struct.unpack_from('<I',data,80)[0]
    if n!=80 or len(data)!=84+50*n: raise ValueError('STL 三角面數或長度不符')
    return [[struct.unpack_from('<3f',data,84+50*i+12+12*j) for j in range(3)] for i in range(n)]

def section(tris,ycentre):
    """Z=4.5 與三角面真實交線，畫圖時僅將 Y 中心對齊。"""
    result=set()
    for tri in tris:
        points=set()
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3];u,v=a[2]-4.5,b[2]-4.5
            if abs(u)<1e-7: points.add((round(a[0],4),round(a[1]-ycentre,4)))
            if u*v<0:
                t=-u/(v-u)
                points.add((round(a[0]+t*(b[0]-a[0]),4),round(a[1]+t*(b[1]-a[1])-ycentre,4)))
        if len(points)==2: result.add(tuple(sorted(points)))
        elif len(points)>2: raise ValueError('剖面與三角面共面，須另行分析')
    return sorted(result)

def inspect():
    results=[]
    for name,ycenter,length,total,digest in CASES:
        tris=read_stl(name,digest)
        verts=[v for tri in tris for v in tri]
        mins=[min(v[i] for v in verts) for i in range(3)]
        maxs=[max(v[i] for v in verts) for i in range(3)]
        if any(abs((maxs[i]-mins[i])-val)>1e-4 for i,val in enumerate((total,4.6,9.))):
            raise ValueError('世界外框不符 '+name)
        if abs((mins[1]+maxs[1])/2-ycenter)>1e-4 or abs(mins[2])>1e-4:
            raise ValueError('STL 世界位置不符 '+name)
        segs=section(tris,ycenter)
        if len(segs)!=38: raise ValueError('截面交線數不符 '+name)
        def point(x,y):return any(any(abs(a-x)<1e-4 and abs(b-y)<1e-4 for a,b in seg) for seg in segs)
        # x=1.5 為 anchor / 臂根交界，承接面 x=1.5+L。
        for x,y in [(1.5,-1.4),(1.5,1.4),(2.1,-.8),(2.1,.8),(1.5+length,-.8),(1.5+length,-2.),(-1.5,-2.3),(-1.5,2.3)]:
            if not point(x,y): raise ValueError('缺失截面關鍵點 '+name+' '+str((x,y)))
        results.append(segs)
    return results

def build():
    sections=inspect(); scale=42
    svg=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1630" role="img" aria-labelledby="title desc">
<title id="title">懸臂卡扣 A／B／C 試片工程題圖</title><desc id="desc">三件獨立卡扣試片在 Z=4.5 的實際 STL 截面比較；幾何臂長 19、17、21 mm，材料和允許應變待定，無強度合格判定。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker></defs>
<style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#18384b}.edge{stroke:#17364a;stroke-width:2.7;fill:none}.dim{stroke:#244f6e;stroke-width:1.5;fill:none}.center{stroke:#6b899b;stroke-width:1.2;stroke-dasharray:10 4 3 4;fill:none}.big{font-size:25px;font-weight:700}.small{font-size:19px}.label{font-size:20px;fill:#244f6e}</style>
<rect width="1900" height="1630" fill="white"/><rect x="20" y="20" width="1860" height="1590" fill="none" stroke="#17384c" stroke-width="3"/>
<text x="55" y="65" class="big">懸臂卡扣比較試片｜工程題尺寸圖</text><text x="55" y="100" class="small">單位：mm（STL 無單位，依教材按 mm 解讀） · 幾何草案 · 非製造或強度合格圖</text>
<text x="55" y="145" class="small">A／B／C：Z=4.5 mm 平面之真實 STL 交線；圖面將 Y 中心各自對齊比較，非三件組裝。</text>''']
    for (name,ycentre,L,total,digest),segs,cy in zip(CASES,sections,(300,600,900)):
        svg.append(f'<text x="55" y="{cy+135}" class="big">{name}</text>')
        def pos(p):return (200+(p[0]+1.5)*scale,cy-p[1]*scale)
        for a,b in segs:
            x1,y1=pos(a);x2,y2=pos(b)
            svg.append(f'<line class="edge" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"/>')
        root,bearing=pos((1.5,0))[0],pos((1.5+L,0))[0]
        svg += [f'<path class="center" d="M{root:.1f} {cy-105}V{cy+110} M{bearing:.1f} {cy-105}V{cy+110}"/>',
                f'<path class="dim" d="M{root:.1f} {cy-108}H{bearing:.1f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>',
                f'<text x="{(root+bearing)/2:.1f}" y="{cy-118}" class="label" text-anchor="middle">幾何 L {L:g}</text>',
                f'<text x="{200+(total*scale)/2:.1f}" y="{cy+136}" class="small" text-anchor="middle">此件世界 X 外框 {total:g} mm；根面至承接面 L={L:g} mm</text>']
    svg += ['<text x="1390" y="205" class="big">A 試片端視外框</text>',
            '<text x="1390" y="236" class="small">沿 X 看 anchor 外形</text>',
            '<rect x="1450" y="280" width="184" height="360" class="edge"/>',
            '<g class="dim"><path d="M1450 280V250 M1634 280V250 M1634 280H1690 M1634 640H1690"/><path d="M1450 253H1634" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1686 280V640" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>',
            '<text x="1542" y="245" text-anchor="middle" class="label">4.6</text><text x="1710" y="460" text-anchor="middle" class="label" transform="rotate(-90 1710 460)">9</text>',
            '<text x="1390" y="680" class="small">端視投影輪廓；內部細節參考截面</text>',
            '<text x="1390" y="715" class="small">外框數值按候選 world XYZ</text>',
            '<text x="1390" y="750" class="small">三件的夾具及對件均待定</text>',
            '<line x1="20" y1="1140" x2="1880" y2="1140" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1180" class="big">比較與驗證範圍</text>',
            '<text x="55" y="1215" class="small">L 是幾何根平面至扣鉤承接面的距離，不是已測定的力學有效長度；端部與臂頂另有 2 mm。</text>',
            '<text x="55" y="1249" class="small">A／B／C 為獨立 anchor + 臂 + 鉤；不等同原盒、上蓋或已指定的試扣對件。</text>',
            '<text x="55" y="1283" class="small">材料、允許應變、根部柔度、夾持與試驗載入條件：待定；未評估強度、改善或合格。</text>',
            '<text x="55" y="1317" class="small">列印方向及支撐僅候選；尚未切片、列印、量測或試配。原 STL 坐標已保留候選旋轉與分列位置。</text>',
            '<text x="55" y="1351" class="small">各截面僅為圖面 Y 對齊以利比較，未改 STL；請以名義標註為準，勿量螢幕或影像。</text>',
            '<line x1="20" y1="1380" x2="1880" y2="1380" stroke="#17384c" stroke-width="2"/><line x1="1200" y1="1380" x2="1200" y2="1610" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1420" class="small">來源：u07_A_L19_v001.stl／u07_B_L17_v001.stl／u07_C_L21_v001.stl。</text>',
            '<text x="55" y="1454" class="small">來源 SHA-256 依序 bb40b5f669601e11…／ac0f9ca920197544…／1e3bb7cb883fd5d0…</text>',
            '<text x="55" y="1488" class="small">A/B/C 世界外框依序約 24／22／26 × 4.6 × 9 mm；STL 無單位標記。</text>',
            '<text x="55" y="1522" class="small">定位、夾持及有效機械長待定；圖面僅供教學，不作正式製造、驗收或強度認定。</text>',
            '<text x="1230" y="1420" class="small">圖名：懸臂卡扣試片對照</text><text x="1230" y="1454" class="small">圖號：SNAP-EDU-001　版次：v003</text>',
            '<text x="1230" y="1488" class="small">單位：mm　比例：隨畫面縮放</text><text x="1230" y="1522" class="small">材料／公差／製程：待定</text>',
            '</svg>']
    return '\n'.join(svg)

if __name__=='__main__':
    if OUT.exists():raise FileExistsError('拒絕覆寫既有試教題圖')
    data=build();OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x',encoding='utf-8',newline='\n') as f:f.write(data)
    print('written',OUT,'SHA-256',sha256(OUT.read_bytes()).hexdigest(),'bytes',OUT.stat().st_size)
