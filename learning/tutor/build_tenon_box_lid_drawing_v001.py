"""Draw the 06-01 locating pin and lid from frozen evaluated meshes.

The orthographic outlines use sampled depth visibility, not a complete hidden-line
algorithm.  The Y=13 section intersects the original world-mm triangles.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'learning/evidence/06/2026-10-25-lesson06-tenon-demo-v006'
MODEL = BASE / 'demo-files/u06_locating_tenon_v001.blend'
OUT = ROOT / 'learning/web/challenges/tenon-box-lid-drawing-v001.svg'
RECORD = ROOT / 'learning/journal/2026-10-29-tenon-box-lid-drawing-record-v001.json'
EXPECTED = {
    'scene': 'f94dc6c5d342f04c41dddc37a4682805a5f7d87b5cf7a8b7bda37cd8ec51040f',
    'body': '930fcafdf6e09ba60bf7ea20e3e448f3cbdac9056d7a44e98e4369ca75ffde08',
    'lid': '4ae28e1981fa44e9be4d504a2d62b5fcecda16ec9634c84127aaa8191e797d9a',
    'fit': '4991be96553a02c34c37f871fa4c29417eee2190438204d3b4742dcf4b25b867',
}
digest = lambda p: sha256(p.read_bytes()).hexdigest()

def load_mesh(name):
    file = BASE / (name + '_mesh.json')
    if digest(file) != EXPECTED[name]:
        raise ValueError('mesh source changed: ' + name)
    mesh = json.loads(file.read_text(encoding='utf8'))
    if mesh['cad_metadata']['object_name'] != {'body': 'Body', 'lid': 'Lid'}[name]:
        raise ValueError('unexpected source object')
    return mesh

def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))

def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def triangles(mesh):
    return [tuple(mesh['vertices'][i] for i in t) for t in mesh['triangles']]

def feature_edges(mesh):
    adjacency=defaultdict(list)
    for inds in mesh['triangles']:
        pts=[mesh['vertices'][i] for i in inds]
        n=cross(sub(pts[1],pts[0]),sub(pts[2],pts[0])); length=math.sqrt(dot(n,n))
        if not length:
            raise ValueError('zero area input triangle')
        n=tuple(v/length for v in n)
        for i in range(3):adjacency[tuple(sorted((inds[i],inds[(i+1)%3])))].append(n)
    return [(mesh['vertices'][a],mesh['vertices'][b]) for (a,b),ns in adjacency.items()
            if len(ns)!=2 or abs(dot(ns[0],ns[1])) < .999999]

def projection(p, axes):
    return (p[axes[0]],p[axes[1]],p[axes[2]]*axes[3])

def depth_at(point,tri,axes):
    u,v,_=projection(point,axes)
    a,b,c=(projection(p,axes) for p in tri)
    denom=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(denom)<1e-10:return None
    w=((b[1]-c[1])*(u-c[0])+(c[0]-b[0])*(v-c[1]))/denom
    t=((c[1]-a[1])*(u-c[0])+(a[0]-c[0])*(v-c[1]))/denom
    s=1-w-t
    if min(w,t,s)<-1e-8:return None
    return w*a[2]+t*b[2]+s*c[2]

def visible_segments(mesh, all_triangles, axes, samples=10):
    result=[]
    for a,b in feature_edges(mesh):
        if sum((a[axes[i]]-b[axes[i]])**2 for i in (0,1)) < 1e-14:continue
        for k in range(samples):
            lo,hi=k/samples,(k+1)/samples; mid=(lo+hi)/2
            p=tuple(a[i]+mid*(b[i]-a[i]) for i in range(3));depth=projection(p,axes)[2]
            if any((z:=depth_at(p,t,axes)) is not None and z>depth+1e-5 for t in all_triangles):continue
            p0=tuple(a[i]+lo*(b[i]-a[i]) for i in range(3));p1=tuple(a[i]+hi*(b[i]-a[i]) for i in range(3))
            result.append((p0,p1))
    return result

def cut(mesh,y=13.0):
    result=set()
    for tri in triangles(mesh):
        if all(abs(p[1]-y)<1e-7 for p in tri):raise ValueError('coplanar triangle needs review')
        hits=set()
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3];u=a[1]-y;v=b[1]-y
            if abs(u)<1e-7:hits.add((round(a[0],6),round(a[2],6)))
            if u*v<0:
                t=-u/(v-u);hits.add((round(a[0]+t*(b[0]-a[0]),6),round(a[2]+t*(b[2]-a[2]),6)))
        if len(hits)==2:result.add(tuple(sorted(hits)))
        elif len(hits)>2:raise ValueError('ambiguous section')
    return sorted(result)

def bounds(mesh):
    return [[min(p[i] for p in mesh['vertices']), max(p[i] for p in mesh['vertices'])] for i in range(3)]

def svg_paths(segments,project):
    out=[]
    for a,b in segments:
        x1,y1=project(a);x2,y2=project(b)
        if (x1-x2)**2+(y1-y2)**2 > .0001:out.append(f'<path d="M{x1:.3f} {y1:.3f}L{x2:.3f} {y2:.3f}"/>')
    return ''.join(out)

def main():
    if OUT.exists() or RECORD.exists():raise FileExistsError('refusing to overwrite drawing or record')
    if digest(MODEL)!=EXPECTED['scene']:raise ValueError('scene SHA mismatch')
    fitfile=BASE/'trial-fit-record-v001.json'
    if digest(fitfile)!=EXPECTED['fit']:raise ValueError('fit readback SHA mismatch')
    fit=json.loads(fitfile.read_text(encoding='utf8'))['actual_cad_measurements']
    if (fit['pin_polygon']['segments'],fit['hole_polygon']['segments'])!=(32,32):raise ValueError('polygon count mismatch')
    if fit['pin_polygon']['centre_mm']!=[23.0,13.0] or fit['hole_polygon']['centre_mm']!=[23.0,13.0]:raise ValueError('hole or pin centre mismatch')
    if abs(fit['min_normal_gap_mm']-0.1990362137307402)>1e-10 or fit['final_pin']['exposed_height_mm']!=29.5:raise ValueError('fit or sidewall readback mismatch')
    body,lid=load_mesh('body'),load_mesh('lid')
    if (len(body['vertices']),len(body['triangles']),len(lid['vertices']),len(lid['triangles']))!=(80,156,89,178):raise ValueError('mesh count mismatch')
    if bounds(body)!=[[-30.0,30.0],[-20.0,20.0],[-15.0,16.5]] or bounds(lid)!=[[-30.0,30.0],[-20.0,20.0],[11.0,17.0]]:raise ValueError('unexpected bounds')
    bs,ls=cut(body),cut(lid); all_tris=triangles(body)+triangles(lid)
    # Each view is a real projection from the two meshes in their saved nominal assembly position.
    views={
      'top':((0,1,2,1),lambda p:(100+(p[0]+30)*8,485-(p[1]+20)*8)),
      'front':((0,2,1,-1),lambda p:(100+(p[0]+30)*8,880-(p[2]+15)*8)),
      'right':((1,2,0,1),lambda p:(730+(p[1]+20)*8,455-(p[2]+15)*8)),
    }
    data={k:{'body':visible_segments(body,all_tris,a),'lid':visible_segments(lid,all_tris,a)} for k,(a,_) in views.items()}
    sec=lambda p:(730+(p[0]+30)*8,880-(p[1]+15)*8)
    det=lambda p:(1250+(p[0]-19)*45,420-(p[1]-12)*45)
    s=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1320" role="img" aria-labelledby="title desc"><title id="title">定位柱及蓋孔：網格工程題圖</title><desc id="desc">既有盒體和蓋的真實三角網格，名義組合位置三面正投影及通過定位柱中心的 Y 等於 13 mm 的剖切，數位試驗草案。</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#245573"/></marker><clipPath id="detail"><rect x="1245" y="130" width="380" height="305"/></clipPath></defs><style>text{font-family:Microsoft JhengHei,Noto Sans TC,sans-serif;fill:#173548}.head{font-size:26px;font-weight:700}.sub{font-size:21px;font-weight:700}.note{font-size:18px}.dim{stroke:#245573;stroke-width:1.4;fill:none}.body{stroke:#1a4868;stroke-width:2;fill:none}.lid{stroke:#b15b2c;stroke-width:2;fill:none}.center{stroke:#7390a3;stroke-width:1.2;stroke-dasharray:10 5;fill:none}</style><rect width="1800" height="1320" fill="white"/><rect x="20" y="20" width="1760" height="1280" fill="none" stroke="#173548" stroke-width="3"/><text class="head" x="55" y="60">定位柱與蓋板穿孔｜實際網格工程題圖</text><text class="note" x="55" y="92">06-01 示範場景 · 組合名義位置 · 數位試驗草案，並非 Blender 畫面或學員模型</text><text class="sub" x="100" y="135">俯視（沿 −Z）</text><text class="sub" x="730" y="135">右視（沿 −X）</text><text class="sub" x="100" y="610">前視（沿 +Y）</text><text class="sub" x="730" y="610">A–A 組合剖切：Y = 13 mm</text><text class="sub" x="1245" y="110">B 柱孔局部（A–A 放大）</text>''']
    for name,(_,project) in views.items():
        for key in ('body','lid'):s.append(f'<g class="{key}">{svg_paths(data[name][key],project)}</g>')
    for key,segs in [('body',bs),('lid',ls)]:s.append(f'<g class="{key}">{svg_paths(segs,sec)}</g>')
    s.append('<rect x="1245" y="130" width="380" height="305" fill="#f6fafc" stroke="#9bb3c4"/><g clip-path="url(#detail)">')
    for key,segs in [('body',bs),('lid',ls)]:s.append(f'<g class="{key}">{svg_paths(segs,det)}</g>')
    s.append('''</g><g class="center"><path d="M80 221H600"/><path d="M524 135V500"/><path d="M1430 130V435"/></g><g class="dim"><path d="M100 485V530 M580 485V530 M100 520H580" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M100 165H60 M100 485H60 M70 165V485" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M100 880V920 M580 880V920 M100 910H580" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M580 640H620 M580 880H620 M610 640V880" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1340 240H1520" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1331 212H1529" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M1537 195H1570 M1537 285H1570 M1560 195V285" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g><g class="note"><text x="340" y="514" text-anchor="middle">60</text><text x="48" y="310" transform="rotate(-90 48 310)" text-anchor="middle">40</text><text x="340" y="904" text-anchor="middle">60</text><text x="640" y="830" transform="rotate(-90 640 830)" text-anchor="middle">盒殼 30</text><text x="1430" y="235" text-anchor="middle">柱 Ø4</text><text x="1430" y="205" text-anchor="middle">孔 Ø4.4</text><text x="1580" y="260">板厚 2</text><text x="78" y="211">A</text><text x="595" y="211">A</text><text x="100" y="565">柱／孔中心 X23，Y13</text><text x="1270" y="478">柱頂 Z16.5；蓋板頂 Z17</text><text x="1270" y="510">柱伸入蓋孔 1.5；柱頂餘量 0.5</text><text x="1270" y="542">名義直徑差 0.4；徑向各側 0.2</text><text x="1270" y="574">32邊相位對齊，最小法向讀值約 0.1990</text><text x="730" y="925">藍：盒體含定位柱　橘：上蓋含穿孔</text><text x="100" y="945">三視圖可見稜線採抽樣，非完整標準隱線。</text></g>
<path d="M20 980H1780 M1160 980V1300 M1450 980V1300" fill="none" stroke="#173548" stroke-width="2"/><g class="note"><text x="45" y="1015">原盒殼 60×40×30；含柱 Body 外框 60×40×31.5。原盒內腔 56×36×28。</text><text x="45" y="1048">最終柱側壁 Z −13～16.5，外露 29.5；獨立建構工具高30，非最終有效力學長度。</text><text x="45" y="1081">上蓋外框 60×40×6；板厚2、唇深4；孔 Z15～17 貫穿蓋板。</text><text x="45" y="1114">柱與孔皆為32邊形，標註 Ø 為名義外接直徑；直徑差0.4／徑向0.2均為試驗值。</text><text x="45" y="1147">環形唇邊與定位柱可能形成重複定位；單柱不能完全限制旋轉，需實際組裝驗證。</text><text x="45" y="1180">材料、製程、公差待定；尚未切片、列印、量測或試配，不作強度／配合合格判定。</text><text x="45" y="1213">來源為示範 Blender 場景實際網格；剖切取 Y13 mm 三角面交線，不是剖面填色。</text><text x="45" y="1246">來源 SHA-256 f94dc6c5d342f04c41dddc37a4682805a5f7d87b5cf7a8b7bda37cd8ec51040f</text><text x="1180" y="1015">圖名：定位柱與蓋孔</text><text x="1180" y="1048">圖號：TENON-EDU-001</text><text x="1180" y="1081">版次：v001</text><text x="1470" y="1015">單位：mm</text><text x="1470" y="1048">比例：隨畫面</text><text x="1470" y="1081">試配：未做</text></g></svg>''')
    svg='\n'.join(s)+'\n'
    OUT.write_text(svg,encoding='utf8',newline='\n')
    record={'schemaVersion':1,'title':'06-01 定位柱／蓋孔網格工程題圖','drawing':{'path':OUT.relative_to(ROOT).as_posix(),'sha256':digest(OUT)},'sourceScene':{'path':MODEL.relative_to(ROOT).as_posix(),'sha256':EXPECTED['scene']},'meshes':[{'path':(BASE/(n+'_mesh.json')).relative_to(ROOT).as_posix(),'sha256':EXPECTED[n],'boundsMm':bounds(m)} for n,m in [('body',body),('lid',lid)]], 'sourceVerification':{'path':(BASE/'trial-fit-record-v001.json').relative_to(ROOT).as_posix(),'sha256':digest(BASE/'trial-fit-record-v001.json')},'readback':{'bodyBoundsMm':bounds(body),'lidBoundsMm':bounds(lid),'sectionPlaneYmm':13,'sectionSegmentCounts':[len(bs),len(ls)],'pinNominalCircumdiameterMm':4,'holeNominalCircumdiameterMm':4.4,'nominalDiametralTrialMm':0.4,'nominalRadialTrialMm':0.2,'sampledMinimumNormalClearanceMm':0.1990362137307402,'exposedSidewallMm':29.5,'pinEngagementMm':1.5,'pinToLidTopMm':0.5},'limitations':['三視圖採網格鄰面稜線與抽樣可見性，非完整標準隱線。','剖切採示範場景Y=13的三角面交線；無剖面填色。','外露側壁高度不等於力學有效長度，單柱不完全限制旋轉；環唇及定位柱可能重複定位。','0.4／0.2為名義試驗值；最小法向值為此網格計算，非實測合格。','未完成材料選擇、製造公差、實際列印、量測或試配，不作強度或配合合格判定。'],'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'qualifiedClearance':None}
    RECORD.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print('drawing',digest(OUT));print('record',digest(RECORD));print('section',len(bs),len(ls))
if __name__=='__main__':main()
