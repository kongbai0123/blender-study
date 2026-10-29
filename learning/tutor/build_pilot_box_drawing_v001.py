"""由既有小盒 STL 的三角網格產生教學題圖；不修改任何模型或進度。"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'learning/evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.stl'
OUTPUT = ROOT / 'learning/web/pilot/box-drawing.svg'
EXPECTED = '0e8fc0863ea9f392e6231f8e0c7444148c000f00010454e263fae0e09f145bb9'

def mesh():
    data = SOURCE.read_bytes()
    assert sha256(data).hexdigest() == EXPECTED, '來源檔雜湊與記錄不符'
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + count * 50 and count == 28
    triangles = [[struct.unpack_from('<3f', data, 84 + i * 50 + 12 + j * 12)
                  for j in range(3)] for i in range(count)]
    points = {point for triangle in triangles for point in triangle}
    expected = {(x, y, z) for x in (-30., 30.) for y in (-20., 20.) for z in (-15., 15.)}
    expected |= {(x, y, z) for x in (-28., 28.) for y in (-18., 18.) for z in (-13., 15.)}
    assert points == expected, '頂點與原盒幾何不符，請重新審查'
    return triangles

def top_boundary(triangles):
    # 由頂面三角形的邊計數得到開口邊及外邊；共享的三角化斜線排除。
    edges = Counter()
    for tri in triangles:
        if all(p[2] == 15 for p in tri):
            for i in range(3):
                a, b = tri[i], tri[(i + 1) % 3]
                edges[tuple(sorted(((a[0], a[1]), (b[0], b[1]))))] += 1
    boundary = [edge for edge, count in edges.items() if count == 1]
    assert len(boundary) == 8
    return boundary

def section_segments(triangles):
    # 沿 y=0 切每個三角形，將共線且相連的片段合併。
    spans = {}
    for tri in triangles:
        points = set()
        for i in range(3):
            a, b = tri[i], tri[(i + 1) % 3]
            if a[1] == 0:
                points.add((a[0], a[2]))
            if a[1] * b[1] < 0:
                t = -a[1] / (b[1] - a[1])
                points.add((a[0] + t * (b[0] - a[0]), a[2] + t * (b[2] - a[2])))
        if len(points) != 2:
            continue
        a, b = sorted(points)
        if a[0] == b[0]:
            key, span = ('v', a[0]), sorted((a[1], b[1]))
        elif a[1] == b[1]:
            key, span = ('h', a[1]), sorted((a[0], b[0]))
        else:
            raise ValueError('剖面出現非預期斜邊')
        spans.setdefault(key, []).append(span)
    result = []
    for key, items in spans.items():
        merged = []
        for lo, hi in sorted(items):
            if merged and lo <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        for lo, hi in merged:
            result.append(((key[1], lo), (key[1], hi)) if key[0] == 'v'
                          else ((lo, key[1]), (hi, key[1])))
    assert len(result) == 8, result
    return result

def main():
    triangles = mesh()
    top = top_boundary(triangles)
    section = section_segments(triangles)
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 620" role="img" aria-labelledby="title desc">
<title id="title">開口盒：題目用工程圖</title><desc id="desc">小盒俯視圖與 A-A 中央剖面，單位毫米。外形 60 × 40 × 30，內腔 56 × 36 × 28，壁底厚 2。由既有小盒 STL 網格推導，試教草案，並非已驗證製造圖。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#316397"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#7895ab" stroke-width="1"/></pattern></defs>
<rect width="1120" height="620" rx="12" fill="#fff"/>
<g font-family="Microsoft JhengHei, Noto Sans TC, sans-serif" fill="#17324b"><text x="40" y="48" font-size="27" font-weight="700">開口盒｜試教題目工程圖</text><text x="40" y="78" font-size="16">單位：mm　｜　名義尺寸草案　｜　非正式製造圖</text>
<text x="180" y="145" font-size="20" font-weight="700">俯視圖</text><text x="712" y="145" font-size="20" font-weight="700">A–A 中央剖面</text></g>
<g stroke="#9cb3c3" stroke-width="1" stroke-dasharray="6 5"><line x1="100" y1="305" x2="495" y2="305"/></g>
<g fill="#385b75" font-family="sans-serif" font-size="15"><text x="66" y="293">A</text><text x="495" y="295">A</text></g>''']
    scale = 5.5
    # 左側俯視：由 STL 顶面三角網格的真實邊界轉換座標。
    def top_xy(p): return (130 + (p[0] + 30) * scale, 195 + (20 - p[1]) * scale)
    # 右側剖面：來自 STL 與 y=0 的實際交線。
    def section_xy(p): return (690 + (p[0] + 30) * scale, 195 + (15 - p[1]) * scale)
    def line(a, b, klass='edge'):
        return f'<line class="{klass}" x1="{a[0]:g}" y1="{a[1]:g}" x2="{b[0]:g}" y2="{b[1]:g}"/>'
    svg.append('<style>.edge{stroke:#19374e;stroke-width:2;fill:none;stroke-linecap:square}.dim{stroke:#316397;stroke-width:1.3;fill:none}.label{fill:#255078;font:16px sans-serif}</style>')
    # 橫斷材料區由本模型外邊界與實際內腔邊界構成，剖線幫助辨識。
    svg.append('<path d="M690 195H701V349H1009V195H1020V360H690Z" fill="url(#hatch)"/>')
    svg.extend(line(top_xy(a), top_xy(b)) for a, b in top)
    svg.extend(line(section_xy(a), section_xy(b)) for a, b in section)
    # 尺寸線指向由 STL 極值及剖面所得的位置。
    svg.append('''<g class="dim">
<path d="M130 195V165 M460 195V165 M141 195V182 M449 195V182"/>
<path d="M130 170H460" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M141 185H449" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M130 195H92 M130 415H92 M141 206H115 M141 404H115"/>
<path d="M98 195V415" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M116 206V404" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M690 360V398 M1020 360V398 M690 393H1020" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M1020 195H1065 M1020 360H1065 M1060 195V360" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M1009 195H1043 M1009 349H1043 M1038 195V349" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
<path d="M702 349 L652 374 M702 206 L652 225"/>
</g>
<g class="label" text-anchor="middle"><text x="295" y="163">60</text><text x="295" y="181">56</text><text x="91" y="305" transform="rotate(-90 91 305)">40</text><text x="109" y="305" transform="rotate(-90 109 305)">36</text><text x="855" y="416">60</text><text x="1075" y="280" transform="rotate(-90 1075 280)">30</text><text x="1052" y="280" transform="rotate(-90 1052 280)">28</text></g>
<g class="label"><text x="618" y="225">壁厚 2</text><text x="618" y="385">底厚 2</text></g>
<g font-family="Microsoft JhengHei, Noto Sans TC, sans-serif" fill="#40596b" font-size="16"><text x="40" y="492">原盒名義尺寸：外形 60 × 40 × 30；內腔 56 × 36 × 28；壁厚與底厚 2。</text><text x="40" y="521">依既有 STL 網格取得投影與中央剖面，尺寸依原示範模型核對；非實體量測值。</text><text x="40" y="550">原模型：u04_box_v001.stl　｜　SHA-256：0e8fc0863ea9f392…</text><text x="40" y="579">用途：題目尺寸說明；材料、製程、公差與實體配合尚未驗證。</text></g></svg>''')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        raise FileExistsError('拒絕覆寫既有工程圖')
    OUTPUT.write_text('\n'.join(svg), encoding='utf-8', newline='\n')
    print('source', EXPECTED, 'triangles', len(triangles), 'top edges', len(top), 'section edges', len(section))
    print('output', OUTPUT, 'sha256', sha256(OUTPUT.read_bytes()).hexdigest(), 'bytes', OUTPUT.stat().st_size)

if __name__ == '__main__':
    main()
