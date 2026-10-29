from pathlib import Path
import json,hashlib,collections,math
ROOT=Path(__file__).resolve().parents[2]
mesh_path=ROOT/'learning/evidence/08/2026-10-28-inner-boolean-trial-v003/drawing-mesh-v001.json'
source_path=ROOT/'learning/evidence/08/2026-10-28-inner-boolean-trial-v003/demo-files/u08_inner_boolean_trial_v003.blend'
out=ROOT/'learning/web/challenges/inner-thread-block-drawing-v001.svg'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(mesh_path)=='30026e49c248d10a1d70ffcd7a5fd1b2889e42d450f5b40d3cf4ca30b21b95d1'
assert sha(source_path)=='a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80'
d=json.loads(mesh_path.read_text(encoding='utf-8')); v=d['vertices']; tri=d['triangles']; b=d['bounds']; zmax=b[2][1]
assert all(abs((b[i][1]-b[i][0])-n)<0.0001 for i,n in enumerate([16,16,3]))
top=[q for q in tri if all(abs(v[i][2]-zmax)<0.0001 for i in q)]
counts=collections.Counter(tuple(sorted((q[i],q[(i+1)%3]))) for q in top for i in range(3))
edges=[e for e,n in counts.items() if n==1]; degree=collections.Counter(i for e in edges for i in e)
assert len(edges)==36 and all(n==2 for n in degree.values())
# Intersect original mesh triangles with the indicated Y plane. Chosen away from vertices to avoid seam ambiguity.
cut=0.123456; segments=set()
for q in tri:
 p=[v[i] for i in q]; hits=[]
 for i in range(3):
  a,c=p[i],p[(i+1)%3]; da,dc=a[1]-cut,c[1]-cut
  if da*dc<0:
   t=da/(da-dc); hits.append((a[0]+t*(c[0]-a[0]),a[2]+t*(c[2]-a[2])))
  elif abs(da)<1e-10: hits.append((a[0],a[2]))
 unique=[]
 for pt in hits:
  if not any(math.dist(pt,k)<1e-7 for k in unique): unique.append(pt)
 if len(unique)==2:
  e=tuple(sorted(tuple(round(x,6) for x in pt) for pt in unique))
  if e[0]!=e[1]: segments.add(e)
 elif len(unique)>2: raise RuntimeError('coplanar ambiguous triangle')
assert len(segments)>100
s=27.0
# Top view X to right and +Y up; section X to right and +Z up.
topxy=lambda p:(315+p[0]*s,325-p[1]*s)
sectxy=lambda p:(955+p[0]*s,245-(p[1]-2)*s)
svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="950" viewBox="0 0 1400 950" role="img" aria-labelledby="title desc"><title id="title">內螺紋試塊工程題圖，草案</title><desc id="desc">俯視輪廓及 Y 等於 0.123456 毫米的網格實際剖切線，來源為內螺紋試塊 v003。</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z"/></marker></defs><rect width="1400" height="950" fill="white"/><g fill="none" stroke="#1d2939" stroke-width="2"><rect x="20" y="20" width="1360" height="910"/><rect x="31" y="31" width="1338" height="888"/><path d="M31 100 H1369 M31 590 H1369 M31 770 H1369"/></g><g font-family="Microsoft JhengHei, Noto Sans CJK TC, sans-serif" fill="#14253e"><text x="62" y="76" font-size="27" font-weight="700">內螺紋試塊：實際網格剖面｜工程題圖草案</text><text x="62" y="125" font-size="19" font-weight="700">俯視圖：+Z 方向看向試塊</text><text x="711" y="125" font-size="19" font-weight="700">A–A 剖面：沿 Y = 0.123456 mm 實際切線</text></g>''']
svg.append('<g stroke="#172b46" fill="none" stroke-width="2" stroke-linejoin="round">')
for a,c in edges:
 x1,y1=topxy(v[a]);x2,y2=topxy(v[c]);svg.append(f'<path d="M{x1:.3f} {y1:.3f} L{x2:.3f} {y2:.3f}"/>')
for a,c in segments:
 x1,y1=sectxy(a);x2,y2=sectxy(c);svg.append(f'<path d="M{x1:.3f} {y1:.3f} L{x2:.3f} {y2:.3f}"/>')
svg.append('</g>')
cut_y=topxy((0,cut))[1]
svg.append(f'''<g stroke="#2c6fba" fill="none" stroke-width="1.5" stroke-dasharray="10 6"><path d="M70 {cut_y:.2f} H560"/></g><g font-family="Microsoft JhengHei, sans-serif" fill="#245c99" font-size="19"><text x="58" y="{cut_y-10:.1f}">A</text><text x="565" y="{cut_y-10:.1f}">A</text></g>''')
svg.append('''<g stroke="#46566b" fill="none" stroke-width="1.3"><path d="M99 110 V74 M531 110 V74 M99 87 H531" marker-end="url(#arrow)" marker-start="url(#arrow)"/><path d="M99 109 H55 M99 541 H55 M71 109 V541" marker-end="url(#arrow)" marker-start="url(#arrow)"/><path d="M739 204 V153 M1171 204 V153 M739 167 H1171" marker-end="url(#arrow)" marker-start="url(#arrow)"/><path d="M1171 204 H1220 M1171 285 H1220 M1205 204 V285" marker-end="url(#arrow)" marker-start="url(#arrow)"/></g><g font-family="Microsoft JhengHei, sans-serif" font-size="18" fill="#14253e"><text x="297" y="82">16</text><text x="42" y="331" transform="rotate(-90 42 331)">16</text><text x="936" y="161">16</text><text x="1230" y="251">3</text><text x="95" y="570">X →　　Y ↑</text><text x="739" y="320">X →　　Z ↑</text><text x="711" y="359">剖切線由已存網格三角面求交，並非標準牙型符號。</text><text x="711" y="394">切面偏離中心 0.123456 mm，以避免與網格接縫重合。</text><text x="711" y="429">牙端被試塊上下表面截斷；導入段尚未設計。</text><text x="711" y="464">實際曲面及其局部截線依網格多邊形近似。</text></g>''')
svg.append('''<g font-family="Microsoft JhengHei, Noto Sans CJK TC, sans-serif" fill="#14253e" font-size="18"><text x="62" y="623" font-weight="700">草案與限制</text><text x="62" y="654">尺寸單位：mm；16 × 16 × 3 為名義尺寸。以程式預建外牙草案作 Boolean 工具。</text><text x="62" y="686">工具輸入：半徑 5–6 mm、單線、螺距 1 mm；上述為建模參數，僅有局部射線抽樣核對。</text><text x="62" y="718">無配合間隙補償；非 ISO 牙型、非盒蓋或已驗證的對件。材料、製造規格與公差待定。</text><text x="62" y="750">實體列印、量測、試配及強度均未驗證；非流形邊 0 不代表可列印或配合合格。</text><text x="62" y="805" font-weight="700">來源：u08_inner_boolean_trial_v003.blend ／ 物件 Cube ／ 保存後重開版本</text><text x="62" y="836" font-size="15">來源 SHA-256：a312d1942c8198bff9ef97a18adc7a89d2f0eb882a890710dc11c8782cc74a80</text><text x="62" y="866" font-size="15">俯視輪廓取頂面三角網格邊界；剖面為 mesh 與平面求交。圖面為教學草案，非正式製造圖。</text><text x="62" y="897" font-size="15">版本：inner-thread-block-drawing-v001　　來源 Blender 5.2.1 LTS　　投影：俯視及剖面</text></g></svg>''')
with out.open('x',encoding='utf-8') as f:f.write('\n'.join(svg))
print('top boundary edges',len(edges),'cut segments',len(segments),'svg sha256',sha(out))
