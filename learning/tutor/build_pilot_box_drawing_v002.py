"""由既有原盒 STL 的網格產生新版題目工程圖；不覆寫先前圖或場景。"""
from hashlib import sha256
from pathlib import Path

from build_pilot_box_drawing_v001 import EXPECTED, mesh, section_segments, top_boundary

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'learning/web/pilot/box-drawing-v002.svg'


def make_svg():
    triangles = mesh()  # v001 的讀取器核對來源雜湊、三角面及全部頂點。
    points = {p for tri in triangles for p in tri}
    xs = sorted({p[0] for p in points})
    ys = sorted({p[1] for p in points})
    zs = sorted({p[2] for p in points})
    assert xs == [-30, -28, 28, 30] and ys == [-20, -18, 18, 20] and zs == [-15, -13, 15]
    assert (xs[-1] - xs[0], ys[-1] - ys[0], zs[-1] - zs[0]) == (60, 40, 30)
    assert (xs[2] - xs[1], ys[2] - ys[1], zs[-1] - zs[1]) == (56, 36, 28)
    assert (xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]) == (2, 2, 2)
    top = top_boundary(triangles)
    section = section_segments(triangles)
    assert len(top) == len(section) == 8
    s = 6
    def top_xy(p): return (200 + (p[0] - xs[0]) * s, 200 + (ys[-1] - p[1]) * s)
    def section_xy(p): return (900 + (p[0] - xs[0]) * s, 205 + (zs[-1] - p[1]) * s)
    def front_xy(p): return (200 + (p[0] - xs[0]) * s, 605 + (zs[-1] - p[1]) * s)
    def side_xy(p): return (900 + (p[0] - ys[0]) * s, 605 + (zs[-1] - p[1]) * s)
    def ln(a, b, cls='edge'):
        return f'<line class="{cls}" x1="{a[0]:g}" y1="{a[1]:g}" x2="{b[0]:g}" y2="{b[1]:g}"/>'
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1120" role="img" aria-labelledby="title desc">
<title id="title">小盒工程圖 v002：三視圖與 A-A 剖面</title>
<desc id="desc">依原盒 STL 檢查後產生的試教圖，俯視、主視、右視和中央剖面。外形 60 × 40 × 30，內腔 56 × 36 × 28，壁厚及底厚 2 mm。材料、公差、製程、表面與實體驗證待定。</desc>
<defs>
 <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#264e6c"/></marker>
 <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#7c8992" stroke-width="1"/></pattern>
</defs>
<style>
 text{font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif;fill:#142f42} .edge{stroke:#192e3b;stroke-width:2.5;fill:none}
 .hidden{stroke:#627582;stroke-width:1.4;stroke-dasharray:9 6;fill:none} .center{stroke:#416984;stroke-width:1.4;stroke-dasharray:14 5 3 5;fill:none}
 .dim{stroke:#264e6c;stroke-width:1.3;fill:none} .label{fill:#264e6c;font-size:19px} .viewtitle{font-size:22px;font-weight:700} .small{font-size:17px} .block{font-size:16px}
</style>
<rect width="1600" height="1120" fill="white"/>
<rect x="22" y="22" width="1556" height="1076" fill="none" stroke="#17364c" stroke-width="3"/>
<text x="50" y="62" font-size="29" font-weight="700">開口小盒｜工程題尺寸圖</text>
<text x="50" y="91" class="small">教學草案 · 尺寸為名義值 · 未完成製造及實體驗證 · 圖內數值以 mm 表示</text>
<text x="200" y="122" class="viewtitle">俯視圖（由 +Z 朝 −Z）</text>
<text x="900" y="122" class="viewtitle">A–A 中央剖面（由 −Y 朝 +Y）</text>
<text x="200" y="566" class="viewtitle">主視圖（由 −Y 朝 +Y）</text>
<text x="900" y="566" class="viewtitle">右視圖（由 +X 朝 −X）</text>
''']
    svg += [ln(top_xy(a), top_xy(b)) for a, b in top]
    # 剖線穿過材料；剖面邊線仍以 STL / y=0 的三角面交線繪製。
    a = section_xy((xs[0], zs[-1])); b = section_xy((xs[-1], zs[0]))
    c = section_xy((xs[1], zs[1])); d = section_xy((xs[2], zs[-1]))
    svg.append(f'<path d="M{a[0]} {a[1]} H{c[0]} V{c[1]} H{d[0]} V{d[1]} H{b[0]} V{b[1]} H{a[0]} Z" fill="url(#hatch)"/>')
    svg += [ln(section_xy(a), section_xy(b)) for a, b in section]
    # 外立面投影及其遮擋的內壁、腔底，後者以隱線表示。
    for project, limits in ((front_xy, xs), (side_xy, ys)):
        rect = [(limits[0], zs[0]), (limits[-1], zs[0]), (limits[-1], zs[-1]), (limits[0], zs[-1])]
        svg += [ln(project(rect[i]), project(rect[(i + 1) % 4])) for i in range(4)]
        svg += [ln(project((x, zs[1])), project((x, zs[-1])), 'hidden') for x in limits[1:3]]
        svg.append(ln(project((limits[1], zs[1])), project((limits[2], zs[1])), 'hidden'))
    svg.append('''
<!-- A-A is y=0; upward arrows mean from -Y toward +Y in the top view. -->
<line class="center" x1="175" y1="320" x2="585" y2="320"/>
<line class="dim" x1="180" y1="335" x2="180" y2="300" marker-end="url(#arrow)"/>
<line class="dim" x1="580" y1="335" x2="580" y2="300" marker-end="url(#arrow)"/>
<text x="158" y="294" class="label">A</text><text x="588" y="294" class="label">A</text>
<!-- Nominal dimensions reference actual mesh edges; all units mm. -->
<g class="dim">
 <path d="M200 200V151 M560 200V151 M212 212V177 M548 212V177 M200 200H118 M200 440H118 M212 212H146 M212 428H146 M200 605H145 M200 785H145 M900 205V167 M1260 205V167 M912 205V190 M1248 205V190 M1260 205H1330 M1260 385H1330 M1248 205H1303 M1248 373H1303"/>
 <path d="M200 154H560" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M212 180H548" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M121 200V440" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M149 212V428" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M148 605V785" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M900 170H1260" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M912 193H1248" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M1327 205V385" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M1300 205V373" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
 <path d="M906 242 L855 257 L820 257"/>
 <path d="M1080 379 L1120 425 L1175 425"/>
</g>
<g class="label" text-anchor="middle">
 <text x="380" y="148">60</text><text x="380" y="174">56</text>
 <text x="112" y="320" transform="rotate(-90 112 320)">40</text>
 <text x="142" y="320" transform="rotate(-90 142 320)">36</text>
 <text x="141" y="695" transform="rotate(-90 141 695)">30</text>
 <text x="1080" y="164">60</text><text x="1080" y="187">56</text>
 <text x="1346" y="295" transform="rotate(-90 1346 295)">30</text>
 <text x="1317" y="289" transform="rotate(-90 1317 289)">28</text>
</g>
<g class="label"><text x="715" y="263">壁厚 2（四周）</text><text x="1180" y="431">底厚 2</text></g>
<text x="200" y="824" class="small">虛線：被外壁遮擋的內腔輪廓；剖線：切到的材料。</text>
<text x="200" y="852" class="small">各視圖依同一模型；A–A 以 Y = 0 的平面切開，箭頭指示觀察方向。</text>
<line x1="22" y1="890" x2="1578" y2="890" stroke="#17364c" stroke-width="2"/>
<line x1="22" y1="990" x2="1578" y2="990" stroke="#17364c" stroke-width="1.5"/>
<line x1="900" y1="890" x2="900" y2="1098" stroke="#17364c" stroke-width="1.5"/>
<line x1="1260" y1="890" x2="1260" y2="1098" stroke="#17364c" stroke-width="1.5"/>
<text x="45" y="920" class="block">技術狀態：教學草案；不作正式製造圖。材料、製程、表面處理：待定。</text>
<text x="45" y="947" class="block">尺寸公差、幾何公差、檢驗及配合要求：待定；實體列印、量測與試配：未執行。</text>
<text x="45" y="974" class="block">來源 STL 無單位標記，依本教材按毫米解讀。請以標註數字為準，勿量螢幕或列印影像。</text>
<text x="45" y="1017" class="block">來源：u04_box_v001.stl · SHA-256 0e8fc0863ea9f392e6231f8e0c744414…</text>
<text x="45" y="1045" class="block">視圖排列：第三角式排列；各視圖方向如圖所示。網頁會縮放，不提供可量測列印比例。</text>
<text x="45" y="1073" class="block">來源幾何：外形 60 × 40 × 30；內腔 56 × 36 × 28；壁／底厚 2。</text>
<text x="920" y="920" class="block">圖名</text><text x="920" y="952" font-size="22" font-weight="700">通用開口小盒</text>
<text x="920" y="1020" class="block">單位：mm</text><text x="920" y="1050" class="block">比例：隨畫面縮放</text>
<text x="1280" y="920" class="block">圖號：BOX-EDU-001</text><text x="1280" y="950" class="block">版次：v002</text>
<text x="1280" y="1020" class="block">圖面用途：教學試題</text><text x="1280" y="1050" class="block">製造核准：待定</text>
</svg>''')
    return '\n'.join(svg) + '\n'


def main():
    if OUTPUT.exists():
        raise FileExistsError('拒絕覆寫既有工程圖：' + str(OUTPUT))
    content = make_svg()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(content)
    print('source', EXPECTED)
    print('output', OUTPUT, 'sha256', sha256(OUTPUT.read_bytes()).hexdigest(), 'bytes', OUTPUT.stat().st_size)


if __name__ == '__main__':
    main()
