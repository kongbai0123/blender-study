"""Generate a traceable drawing from the actual saved 07-02 Blender scene.

Run Blender in background with --factory-startup and the source .blend loaded.
Projections include all triangle edges, not hidden-line-removed views. The X=0
section is the exact intersection with the two evaluated meshes.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'learning/evidence/07/2026-10-25-lesson07-snap-demo-v001'
SCENE = RUN / 'demo-files/u07_cantilever_snap_v001.blend'
OUTPUT = ROOT / 'learning/web/challenges/snapfit-box-lid-drawing-v001.svg'
RECORD = ROOT / 'learning/web/challenges/snapfit-box-lid-drawing-v001.json'
EXPECTED = {
    'scene': '5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305',
    'body': 'f40578c09793b6418afaf6b3f5508016a7186022f46bf37695f0c9d25e6df86f',
    'lid': '54bcbdce1ca5ab3ee8b1118d6f5135c44ff2519fa2c5821b0ce30ed746c08dd8',
    'record': '4f201124cbf51dc849c7978ee85f7ff5e58ca4273cdd9b006d3eba6c52521b7a',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical(tris):
    return sorted(tuple(sorted(tuple(round(float(n), 5) for n in p) for p in t)) for t in tris)

def get_mesh(name, raw_path, digest):
    if sha(raw_path) != digest:
        raise ValueError('raw mesh hash mismatch')
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_tris = [[raw['vertices'][i] for i in t] for t in raw['triangles']]
    obj = bpy.data.objects[name]
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        v = [tuple(obj.matrix_world @ x.co) for x in mesh.vertices]
        tris = [[v[i] for i in t.vertices] for t in mesh.loop_triangles]
        if canonical(tris) != canonical(raw_tris):
            raise ValueError(name + ' scene and raw geometry disagree')
        return tris, v
    finally:
        ev.to_mesh_clear()

def section(tris):
    """World X=0 intersects the triangular surfaces; no coplanar triangles."""
    result = set()
    for tri in tris:
        pts = set()
        for i in range(3):
            a, b = tri[i], tri[(i+1) % 3]
            if abs(a[0]) < 1e-7:
                pts.add((round(a[1], 5), round(a[2], 5)))
            if a[0] * b[0] < 0:
                t = -a[0] / (b[0] - a[0])
                pts.add((round(a[1] + t*(b[1]-a[1]), 5), round(a[2] + t*(b[2]-a[2]), 5)))
        if len(pts) == 2:
            result.add(tuple(sorted(pts)))
        elif len(pts) > 2:
            raise ValueError('coplanar cut requires explicit handling')
    return sorted(result)

def near(value, expected):
    return abs(value - expected) < 0.0001

def main():
    if OUTPUT.exists() or RECORD.exists():
        raise FileExistsError('refuse to overwrite prior drawing or record')
    if Path(bpy.data.filepath).resolve() != SCENE.resolve() or sha(SCENE) != EXPECTED['scene']:
        raise ValueError('wrong Blender scene or source hash')
    if sha(RUN / 'geometry-draft-record-v001.json') != EXPECTED['record']:
        raise ValueError('geometry record hash mismatch')
    body, bv = get_mesh('Body', RUN / 'body_mesh.json', EXPECTED['body'])
    lid, lv = get_mesh('Lid', RUN / 'lid_mesh.json', EXPECTED['lid'])
    bb = [[min(v[i] for v in bv), max(v[i] for v in bv)] for i in range(3)]
    lb = [[min(v[i] for v in lv), max(v[i] for v in lv)] for i in range(3)]
    for x, y in zip([b[1]-b[0] for b in bb], [60,44.5,30]):
        if not near(x,y): raise ValueError('body size mismatch')
    for x, y in zip([b[1]-b[0] for b in lb], [60,46,7]):
        if not near(x,y): raise ValueError('lid size mismatch')
    bodycut, lidcut = section(body), section(lid)
    def has(segs, y, z):
        return any(any(near(p[0], y) and near(p[1], z) for p in s) for s in segs)
    for yz in [(-23,11),(-24.2,11),(-21.4,11),(-24.5,-8),(-20,15)]:
        if not has(bodycut,*yz): raise ValueError('missing body section point '+str(yz))
    for yz in [(-26,10.8),(-24.5,10.8),(-23.3,10.8),(-26,15.2)]:
        if not has(lidcut,*yz): raise ValueError('missing lid section point '+str(yz))
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1470" role="img" aria-labelledby="t d">
<title id="t">整盒懸臂卡扣與蓋裙草案工程圖</title><desc id="d">原 07-02 真實 Body 與 Lid 三角網格的三方向投影及 X 等於零的實際組合剖面；標示幾何試驗參數，不代表列印、材料、強度與配合合格。</desc>
<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#285572"/></marker><clipPath id="local"><rect x="1160" y="205" width="220" height="710"/></clipPath></defs>
<style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#18384b}.body{fill:none;stroke:#18384b;stroke-width:1.5;opacity:.72}.lid{fill:none;stroke:#b56925;stroke-width:1.5;opacity:.72}.cutbody{fill:none;stroke:#18384b;stroke-width:3}.cutlid{fill:none;stroke:#b56925;stroke-width:3}.dim{fill:none;stroke:#285572;stroke-width:1.5}.dash{fill:none;stroke:#617f91;stroke-dasharray:9 5;stroke-width:1.2}.big{font-size:25px;font-weight:700}.small{font-size:19px}.label{font-size:20px;fill:#285572}</style>
<rect width="1900" height="1470" fill="white"/><rect x="20" y="20" width="1860" height="1430" fill="none" stroke="#17384c" stroke-width="3"/>
<text x="55" y="65" class="big">整盒懸臂卡扣與蓋裙｜工程題圖</text><text x="55" y="100" class="small">單位 mm · 07-02 靜態名義擺位 · 材料、允許應變與製造公差待定</text>
<text x="100" y="155" class="big">俯視 XY（沿 +Z 朝 −Z）</text><text x="100" y="182" class="small">盒體與蓋的投影線框，含遮蔽邊</text>
<text x="100" y="665" class="big">前視 XZ（沿 −Y 朝 +Y）</text><text x="100" y="692" class="small">卡扣位於盒外負 Y 側</text>
<text x="670" y="155" class="big">側視 YZ（沿 +X 朝 −X）</text><text x="670" y="182" class="small">所有網格三角邊投影，非標準隱線圖</text>
<text x="1135" y="155" class="big">A–A 局部截面（X=0）</text><text x="1135" y="182" class="small">真實網格交線；未變形名義位置</text>''']
    def lines_projection(tris, axes, sx, sy, ox, oy, cls):
        edges = set()
        for tri in tris:
            for i in range(3):
                a,b=tri[i],tri[(i+1)%3]
                p=(round(a[axes[0]],5),round(a[axes[1]],5));q=(round(b[axes[0]],5),round(b[axes[1]],5))
                if p != q: edges.add(tuple(sorted((p,q))))
        for a,b in sorted(edges):
            svg.append(f'<line class="{cls}" x1="{ox+a[0]*sx:.3f}" y1="{oy-a[1]*sy:.3f}" x2="{ox+b[0]*sx:.3f}" y2="{oy-b[1]*sy:.3f}"/>')
    for t, cls in ((body,'body'),(lid,'lid')):
        lines_projection(t,(0,1),7,7,325,370,cls)
        lines_projection(t,(0,2),7,7,325,830,cls)
        lines_projection(t,(1,2),7,7,900,365,cls)
    svg += ['<line class="dash" x1="325" y1="205" x2="325" y2="565"/><text x="333" y="246" class="label">A</text><text x="333" y="560" class="label">A</text>',
            '<path class="dim" d="M115 230V205 M535 230V205 M115 210H535" marker-start="url(#arr)" marker-end="url(#arr)"/><text x="325" y="202" class="label" text-anchor="middle">60</text>',
            '<path class="dim" d="M111 718V700 M539 718V700 M115 706H535" marker-start="url(#arr)" marker-end="url(#arr)"/><text x="325" y="700" class="label" text-anchor="middle">60</text>',
            '<text x="670" y="550" class="small">Body 外框 60 × 44.5 × 30；44.5 包含外掛卡扣。</text>',
            '<text x="670" y="580" class="small">Lid 外框 60 × 46 × 約 7；含蓋裙／凸緣。</text>',
            '<text x="670" y="610" class="small">原盒核心 60 × 40 × 30；原盒壁與底 2。</text>',
            '<text x="670" y="640" class="small">蓋板 60 × 46 × 2；約 7 是含裙整高。</text>',
            '<line x1="670" y1="690" x2="725" y2="690" class="cutbody"/><text x="735" y="697" class="small">Body：盒體＋卡扣</text>',
            '<line x1="670" y1="725" x2="725" y2="725" class="cutlid"/><text x="735" y="732" class="small">Lid：蓋板＋裙／凸緣</text>',
            '<text x="670" y="790" class="small">投影同時包含前後遮蔽邊及三角化線，</text><text x="670" y="820" class="small">不是隱線消除或標準製造工程圖。</text>',
            '<rect x="1160" y="205" width="220" height="710" fill="#f8fbfd" stroke="#b6c9d4"/><g clip-path="url(#local)">']
    # Plot y -27..-18.2 and z -11..17.4 at 25 px/mm.
    def loc(p): return (1160+(p[0]+27)*25, 205+(17.4-p[1])*25)
    for segs,cls in ((bodycut,'cutbody'),(lidcut,'cutlid')):
        for a,b in segs:
            x1,y1=loc(a);x2,y2=loc(b)
            svg.append(f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"/>')
    svg += ['</g>']
    def dim_vertical(y1,y2,x,label):
        p1=loc((-23,y1))[1];p2=loc((-23,y2))[1]
        mid=(p1+p2)/2
        svg.append(f'<path class="dim" d="M{x} {p1:.2f}V{p2:.2f}" marker-start="url(#arr)" marker-end="url(#arr)"/><text x="{x+16}" y="{mid:.1f}" class="label" text-anchor="middle" transform="rotate(-90 {x+16} {mid:.1f})">{label}</text>')
    dim_vertical(-8,11,1390,'幾何 L 19')
    svg += ['<text x="1430" y="230" class="big">局部名義尺寸（mm）</text>',
            '<text x="1430" y="267" class="small">直臂厚 h 1.6（Y 向）</text>',
            '<text x="1430" y="299" class="small">直臂寬 b 6（X 向）</text>',
            '<text x="1430" y="331" class="small">扣鉤突出 u 1.2（Y 向）</text>',
            '<text x="1430" y="363" class="small">鉤與凸緣 Y 投影重疊 0.9</text>',
            '<text x="1430" y="395" class="small">鉤底至凸緣頂 Z 間距 0.2</text>',
            '<text x="1430" y="427" class="small">臂外側至凸緣內端 Y 間距 0.3</text>',
            '<text x="1430" y="459" class="small">鉤外端至裙內側 Y 間距 0.3</text>',
            '<text x="1430" y="491" class="small">蓋裙 Y 厚 1.5；板厚 Z 2</text>',
            '<text x="1430" y="545" class="small">L：Z −8 根面至 Z 11 承接面。</text>',
            '<text x="1430" y="577" class="small">幾何 L 不等於已驗證力學有效長。</text>',
            '<text x="1430" y="609" class="small">u、投影重疊不等於所需撓度。</text>',
            '<text x="1430" y="641" class="small">上列間距僅是靜態幾何試驗值。</text>',
            '<text x="55" y="1000" class="big">驗證範圍與限制</text>',
            '<text x="55" y="1035" class="small">此圖是既有 Body／Lid 完成場景的實際網格投影與截面；與 A_L19、B_L17、C_L21 獨立試片不同分支。</text>',
            '<text x="55" y="1070" class="small">圖中位置未變形；沒有接觸或裝入路徑模擬。靜態空隙不等於可用變形行程。</text>',
            '<text x="55" y="1105" class="small">材料、允許應變、所需及允許撓度、製程、方向、支撐與製造公差待定；非 ISO／驗收圖。</text>',
            '<text x="55" y="1140" class="small">尚未實體列印、量測與試配；不據圖面、封閉性或名義間距判斷強度、配合或製造合格。</text>',
            '<line x1="20" y1="1200" x2="1880" y2="1200" stroke="#17384c" stroke-width="2"/><line x1="1310" y1="1200" x2="1310" y2="1450" stroke="#17384c" stroke-width="2"/>',
            '<text x="55" y="1240" class="small">來源場景：u07_cantilever_snap_v001.blend（07-02，另存並重開）</text>',
            '<text x="55" y="1274" class="small">SHA-256：5fec09b934f2935839d615376beaf598962d47f1b7ac2504f2666c7880a26305</text>',
            '<text x="55" y="1308" class="small">來源網格及尺寸讀值、抽取方法與限制另見同名 JSON。</text>',
            '<text x="55" y="1342" class="small">三視圖同一網格投影；截面 X=0；請依標註與來源讀值，不量螢幕。</text>',
            '<text x="1340" y="1240" class="small">圖號：SNAP-BOX-EDU-001　版次：v001</text>',
            '<text x="1340" y="1274" class="small">單位：mm　比例：隨畫面縮放</text>',
            '<text x="1340" y="1308" class="small">材料／公差／製造／檢驗：待定</text>',
            '<text x="1340" y="1342" class="small">狀態：幾何教學草案</text></svg>']
    output='\n'.join(svg)+'\n'
    OUTPUT.write_text(output,encoding='utf-8',newline='\n')
    rec={'schemaVersion':1,'title':'07-02 整盒卡扣與蓋裙真實網格工程題圖','sourceScene':{'path':str(SCENE.relative_to(ROOT)).replace('\\','/'),'sha256':EXPECTED['scene']},'bodyRaw':{'path':str((RUN/'body_mesh.json').relative_to(ROOT)).replace('\\','/'),'sha256':EXPECTED['body']},'lidRaw':{'path':str((RUN/'lid_mesh.json').relative_to(ROOT)).replace('\\','/'),'sha256':EXPECTED['lid']},'sourceReadback':{'path':str((RUN/'geometry-draft-record-v001.json').relative_to(ROOT)).replace('\\','/'),'sha256':EXPECTED['record']},'method':'以隔離背景 Blender 重開來源場景，取得 Body／Lid evaluated world-space loop triangles；各三角面的座標取五位小數後逐三角與當時 raw 比對，投影畫出所有三角邊，X=0 平面以三角面交線計算。五位數是資料比對，不是製造公差。','sceneMeshMatchesRaw':True,'bodyBoundsMm':bb,'lidBoundsMm':lb,'triangleCounts':{'Body':len(body),'Lid':len(lid)},'sectionSegments':{'Body':len(bodycut),'Lid':len(lidcut)},'nominalMm':{'boxCore':[60,40,30],'bodyBounds':[60,44.5,30],'lidBounds':[60,46,7],'lidPlate':[60,46,2],'geometricLengthZminus8To11':19,'straightArmThicknessY':1.6,'straightArmWidthX':6,'hookProjectionY':1.2,'hookFlangeProjectedOverlapY':0.9,'verticalHookFlangeGap':0.2,'armOuterFlangeGap':0.3,'hookSkirtGap':0.3,'skirtThicknessY':1.5},'limitation':'未變形名義狀態；三方向均為所有邊投影而非可見線剔除，截面局部不是完整的公差設計或驗收圖；幾何L不等於力學有效長，u和投影重疊不等於所需撓度；不等於獨立試片分支。材料、允許應變、製造公差、實印、量測、試配、強度／配合合格待定。','drawing':{'path':str(OUTPUT.relative_to(ROOT)).replace('\\','/'),'sha256':sha(OUTPUT)}}
    RECORD.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('DRAWING',sha(OUTPUT),'RECORD',sha(RECORD),'BODY/LID SEGMENTS',len(bodycut),len(lidcut))

main()
