"""從既有孔板與插銷 STL 推導試教題圖；不修改原始模型或學員進度。"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'learning/evidence/05/2026-10-22-lesson05-export-demo-v003'
PLATE = RUN / 'demo-files/exports/u05_hole_plate_v001.stl'
PIN = RUN / 'demo-files/exports/u05_fit_coupon_v001.stl'
VERIFY = RUN / 'hole_plate-stl-verification.json'
OUT = ROOT / 'learning/web/challenges/fit-trial-drawing-v001.svg'
PLATE_HASH = '8105d1ebdc04ed12a2b7f98cc3b728db74063c453961c33d165ac50e694c7c8b'
PIN_HASH = 'bc10342c54a94d87c15eccb050fb9b30a7ae00bf4079d4c7869ac53d199db784'

def read_stl(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError('STL 來源雜湊不符')
    n = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + 50 * n:
        raise ValueError('STL 長度不符')
    return [[struct.unpack_from('<3f', data, 84 + i * 50 + 12 + j * 12)
             for j in range(3)] for i in range(n)]

def boundaries(tris):
    """由 Z=2 的頂面三角片計數保留實際外輪廓、方孔與凹點邊界。"""
    edges = Counter()
    for tri in tris:
        if all(abs(p[2] - 2) < 1e-4 for p in tri):
            for i in range(3):
                a = tuple(round(v, 5) for v in tri[i][:2])
                b = tuple(round(v, 5) for v in tri[(i + 1) % 3][:2])
                edges[tuple(sorted((a, b)))] += 1
    adj = defaultdict(list)
    for (a, b), count in edges.items():
        if count == 1:
            adj[a].append(b); adj[b].append(a)
        elif count != 2:
            raise ValueError('頂面邊界次數不符')
    if not adj or any(len(ns) != 2 for ns in adj.values()):
        raise ValueError('頂面邊界不閉合')
    seen, loops = set(), []
    for start in sorted(adj):
        if start in seen:
            continue
        cur, previous, loop = start, None, []
        while cur not in seen:
            seen.add(cur); loop.append(cur)
            ns = adj[cur]; following = ns[0] if ns[0] != previous else ns[1]
            previous, cur = cur, following
        if cur != start:
            raise ValueError('頂面環未返回起點')
        loops.append(loop)
    return loops

def extents(loop):
    return (min(p[0] for p in loop), max(p[0] for p in loop),
            min(p[1] for p in loop), max(p[1] for p in loop))

def check_geometry():
    tris, pin = read_stl(PLATE, PLATE_HASH), read_stl(PIN, PIN_HASH)
    vs = json.loads(VERIFY.read_text(encoding='utf-8'))
    if len(tris) != 2854 or len(pin) != 12 or vs['through_holes'] != 6:
        raise ValueError('STL 數量或通孔審查不符')
    pvs = [p for tri in pin for p in tri]
    pd = [max(p[i] for p in pvs) - min(p[i] for p in pvs) for i in range(3)]
    if any(abs(a-b) > 1e-4 for a,b in zip(pd, (10,10,8))):
        raise ValueError('插銷外框不符')
    loops = boundaries(tris)
    if len(loops) != 28:
        raise ValueError('頂面環數不符（1 外框、6 孔、21 凹點）')
    boxes = [extents(loop) for loop in loops]
    outer = [b for b in boxes if abs(b[1]-b[0]-96)<1e-4 and abs(b[3]-b[2]-26)<1e-4]
    holes = sorted((b for b in boxes if 10 < b[1]-b[0] < 11 and 10 < b[3]-b[2] < 11), key=lambda b:b[0])
    dots = [b for b in boxes if 1.19 < b[1]-b[0] < 1.21 and 1.19 < b[3]-b[2] < 1.21]
    if len(outer) != 1 or len(holes) != 6 or len(dots) != 21:
        raise ValueError('頂面外框、孔或凹點分組不符')
    widths = [10.1,10.2,10.3,10.4,10.5,10.6]
    for index, (b, w) in enumerate(zip(holes, widths)):
        if abs((b[0]+b[1])/2 - (-35+14*index)) > 1e-4 or abs((b[2]+b[3])/2-2) > 1e-4:
            raise ValueError('孔中心不符')
        if abs(b[1]-b[0]-w)>1e-4 or abs(b[3]-b[2]-w)>1e-4:
            raise ValueError('孔寬不符')
    return loops, holes

def build():
    loops, holes = check_geometry()
    # A-A is y=2; six through-holes from independent STL inspection.
    x0, y0, scale = 200, 185, 14
    def top(p): return (x0+(p[0]+48)*scale, y0+(13-p[1])*scale)
    def line(a,b,cls='edge'):
        return f'<line class="{cls}" x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}"/>'
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1380" role="img" aria-labelledby="title desc">
<title id="title">六孔配合試片工程題圖</title><desc id="desc">依實際 STL 網格投影的孔板俯視與中央切面，標註六個方孔及插銷的名義尺寸，所有間隙均為待實配試驗值。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#244f6e"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#8b99a2" stroke-width="1"/></pattern></defs>
<style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#18384b}.edge{stroke:#152f40;stroke-width:2;fill:none}.dim{stroke:#244f6e;stroke-width:1.5;fill:none}.center{stroke:#527993;stroke-width:1.2;stroke-dasharray:12 5 3 5;fill:none}.big{font-size:25px;font-weight:700}.small{font-size:18px}.label{font-size:19px;fill:#244f6e}.meta{font-size:17px}</style>
<rect width="1900" height="1380" fill="white"/><rect x="20" y="20" width="1860" height="1340" fill="none" stroke="#17384c" stroke-width="3"/>
<text x="55" y="65" class="big">六孔配合試片｜工程題尺寸圖</text><text x="55" y="98" class="small">單位 mm（STL 本身無單位） · 名義試驗值 · 尚未切片、列印或試配 · 非正式製造圖</text>
<text x="200" y="147" class="big">孔板俯視圖（由 +Z 朝 −Z）</text>''']
    for loop in loops:
        coords = [top(p) for p in loop]
        svg.append('<path class="edge" d="M' + ' L'.join(f'{x:.3f} {y:.3f}' for x,y in coords) + ' Z"/>')
    # Dimensions based on mesh extents and origin, drawn as extension lines plus separate arrows.
    svg += ['<g class="dim">',
            '<path d="M200 185V118 M1544 185V118 M200 549V590 M1544 549V590 M200 185H126 M200 549H126"/>',
            '<path d="M200 122H1544" marker-start="url(#arrow)" marker-end="url(#arrow)"/>',
            '<path d="M130 185V549" marker-start="url(#arrow)" marker-end="url(#arrow)"/>',
            '<path d="M200 586H1544" marker-start="url(#arrow)" marker-end="url(#arrow)"/>',
            '</g>',
            '<text x="872" y="114" class="label" text-anchor="middle">96</text>',
            '<text x="120" y="365" class="label" text-anchor="middle" transform="rotate(-90 120 365)">26</text>',
            '<text x="872" y="611" class="label" text-anchor="middle">96</text>']
    cut_y = top((0,2))[1]
    svg += [f'<path class="center" d="M180 {cut_y:.1f}H1564"/>',
            f'<path class="dim" d="M180 {cut_y+18:.1f}v-37" marker-end="url(#arrow)"/><path class="dim" d="M1564 {cut_y+18:.1f}v-37" marker-end="url(#arrow)"/>',
            f'<text class="label" x="158" y="{cut_y-25:.1f}">A</text><text class="label" x="1574" y="{cut_y-25:.1f}">A</text>']
    for i, b in enumerate(holes):
        cx = (b[0]+b[1])/2
        x, y = top((cx,2))
        svg += [f'<line class="center" x1="{x-15:.2f}" y1="{y:.2f}" x2="{x+15:.2f}" y2="{y:.2f}"/>',
                f'<line class="center" x1="{x:.2f}" y1="{y-15:.2f}" x2="{x:.2f}" y2="{y+15:.2f}"/>',
                f'<text x="{x:.2f}" y="175" text-anchor="middle" class="label">孔 {i+1}</text>']
    # Solid intervals in the A-A section are bounded by actual hole wall coordinates.
    ztop,zbottom = 690,746
    svg.append('<text x="200" y="660" class="big">A–A 剖面（Y = 2；由 −Y 朝 +Y，六孔貫穿）</text>')
    spans=[]; left=-48.
    for b in holes:
        spans.append((left,b[0])); left=b[1]
    spans.append((left,48.))
    for lo,hi in spans:
        xlo,xhi=top((lo,0))[0],top((hi,0))[0]
        svg.append(f'<rect x="{xlo:.3f}" y="{ztop}" width="{xhi-xlo:.3f}" height="56" fill="url(#hatch)" stroke="#152f40" stroke-width="2"/>')
    svg += ['<g class="dim"><path d="M1544 690H1608 M1544 746H1608"/><path d="M1604 690V746" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>',
            '<text class="label" x="1627" y="720" transform="rotate(-90 1627 720)" text-anchor="middle">4</text>',
            '<text x="200" y="790" class="small">孔中心 X = −35、−21、−7、7、21、35；Y = 2（以板中心為原點），相鄰孔距 14。</text>',
            '<text x="200" y="820" class="small">凹點：每組 1～6 點、名義直徑 1.2、深 0.8；凹點薄肉約 0.4 mm，實印可辨性待驗。</text>',
            '<text x="200" y="850" class="small">插銷外形：10 × 10 × 8 mm；以插銷 10 mm 名義寬度與方孔寬差，定義總間隙。</text>']
    svg += ['<line x1="20" y1="885" x2="1880" y2="885" stroke="#17384c" stroke-width="2"/>',
            '<text x="60" y="920" class="big">試驗點表（mm；全部僅為草案，無合格判定）</text>',
            '<text x="60" y="955" class="small">孔號</text><text x="300" y="955" class="small">1</text><text x="480" y="955" class="small">2</text><text x="660" y="955" class="small">3</text><text x="840" y="955" class="small">4</text><text x="1020" y="955" class="small">5</text><text x="1200" y="955" class="small">6</text>',
            '<text x="60" y="990" class="small">方孔寬 X／Y</text>']
    for i,w in enumerate((10.1,10.2,10.3,10.4,10.5,10.6)):
        svg.append(f'<text x="{300+180*i}" y="990" class="small">{w:.1f}</text>')
    svg.append('<text x="60" y="1025" class="small">總間隙</text>')
    for i,w in enumerate((0.1,0.2,0.3,0.4,0.5,0.6)):
        svg.append(f'<text x="{300+180*i}" y="1025" class="small">{w:.1f}</text>')
    svg += ['<text x="60" y="1064" class="small">方孔寬與插銷寬之差為總間隙；置中單邊值為總間隙的一半。</text>',
            '<line x1="20" y1="1090" x2="1880" y2="1090" stroke="#17384c" stroke-width="2"/>',
            '<line x1="1250" y1="1090" x2="1250" y2="1360" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1130" class="small">來源：u05_hole_plate_v001.stl；SHA-256 8105d1ebdc04ed12a2b7f98cc3b728d…</text>',
            '<text x="55" y="1162" class="small">頂面輪廓來自 STL 三角網格，剖面孔邊取實際頂面與通孔審查；浮點容差僅用於模型讀取。</text>',
            '<text x="55" y="1194" class="small">尺寸公差、幾何公差、材料、製程、表面及檢驗：待定；實體列印、量測及試配：未執行。</text>',
            '<text x="55" y="1226" class="small">標註為名義尺寸，請勿直接量取螢幕；試驗結果及合格間隙待實體驗證。</text>',
            '<text x="1280" y="1130" class="small">圖名：六孔配合試片</text>',
            '<text x="1280" y="1162" class="small">圖號：FIT-EDU-001　版次：v001</text>',
            '<text x="1280" y="1194" class="small">單位：mm　比例：隨畫面縮放</text>',
            '<text x="1280" y="1226" class="small">製造核准：待定　用途：教學草案</text>',
            '</svg>']
    return '\n'.join(svg)

if __name__ == '__main__':
    if OUT.exists():
        raise FileExistsError('拒絕覆寫舊圖')
    content=build()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x',encoding='utf-8',newline='\n') as f: f.write(content)
    print('written',OUT,'SHA-256',sha256(OUT.read_bytes()).hexdigest(),'bytes',OUT.stat().st_size)
