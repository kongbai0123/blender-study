"""Build a metre-unit teaching drawing from actual extracted Blender vertices.

Object silhouettes are convex hulls of each real mesh's orthographic projected
vertices. Camera and lights are not geometry; hidden edges are not reconstructed.
"""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source=root/'learning/evidence/04/2026-10-28-station-drawing-v001/geometry-readback-v001.json'
data=json.loads(source.read_text(encoding='utf8'))
for key in ('sourceScene','renderScene'):
 if hashlib.sha256((root/data[key]).read_bytes()).hexdigest()!=data['source' if key=='sourceScene' else 'render']['sceneSha256']:raise ValueError('scene SHA mismatch')
if not all(data['sameWorldMeshFingerprints'].values()):raise ValueError('render station geometry differs')
obj=data['source']['objects'];names=['Ground','Platform','BeaconBase','Post','Signal']
def hull(points):
 pts=sorted(set((round(x,8),round(y,8)) for x,y in points))
 if len(pts)<=2:return pts
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pts:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def outlines(axes,cx,base,scale,depth_name):
 shapes=[]
 for name in names:
  coords=hull([(p[axes[0]],p[axes[1]]) for p in obj[name]['worldVerticesM']])
  xy=[(cx+scale*x,base-scale*y) for x,y in coords]
  pts=' '.join(f'{x:.3f},{y:.3f}' for x,y in xy)
  if len(xy)==2:shapes.append(f'<polyline class="outline ground" points="{pts}"/>')
  else:shapes.append(f'<polygon class="outline {"ground" if name=="Ground" else "body"}" points="{pts}"/>')
 return '\n'.join(shapes)
def line(x1,y1,x2,y2,kind='dim',arrow=False):
 return f'<line class="{kind}" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"'+(' marker-start="url(#arrow)" marker-end="url(#arrow)"' if arrow else '')+'/>'
def t(x,y,text,cls='note',anchor='start'):
 return f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}">{text}</text>'
def dim_horizontal(x1,x2,base,y,text):
 return '\n'.join((line(x1,base,x1,y+8,'ext'),line(x2,base,x2,y+8,'ext'),line(x1,y,x2,y,'dim',True),t((x1+x2)/2,y-9,text,'label','middle')))
def dim_vertical(y1,y2,base,x,text):
 return '\n'.join((line(base,y1,x+8,y1,'ext'),line(base,y2,x+8,y2,'ext'),line(x,y1,x,y2,'dim',True),
   f'<text x="{x-10:.2f}" y="{(y1+y2)/2:.2f}" class="label" text-anchor="middle" transform="rotate(-90 {x-10:.2f} {(y1+y2)/2:.2f})">{text}</text>'))
def size(name):
 b=obj[name]['worldBoundsM'];return [row[1]-row[0] for row in b]
s=145;fc=400;fb=505;tc=1195;ty=480;rc=400;rb=1090
front=outlines((0,2),fc,fb,s,'Y');top=outlines((0,1),tc,ty,s,'Z');right=outlines((1,2),rc,rb,s,'X')
rows=[]
for idx,(n,label) in enumerate([('Ground','地面（平面）'),('Platform','平台'),('BeaconBase','訊號底座'),('Post','立柱'),('Signal','訊號球')]):
 dims=size(n);y=912+idx*43
 rows.append(t(865,y,label,'table')+t(1090,y,f'{dims[0]:.2f} × {dims[1]:.2f} × {dims[2]:.2f}','table'))
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1450" role="img" aria-labelledby="title desc">
<title id="title">訊號站渲染題：實際 mesh 三視圖</title><desc id="desc">由五個 Blender 零件世界頂點投影得到的前視、俯視與右視輪廓及尺寸，單位 m；地面為零厚度平面，非列印件。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#29465a"/></marker></defs>
<style>text{{font-family:'Microsoft JhengHei','Noto Sans CJK TC',sans-serif;fill:#172f40}} .title{{font-size:33px;font-weight:700}} .head{{font-size:24px;font-weight:700}} .label{{font-size:21px}} .table{{font-size:21px}} .note{{font-size:18px}} .small{{font-size:16px}} .outline{{stroke:#143244;stroke-width:2;stroke-linejoin:round}} .ground{{fill:#f6f8fa}} .body{{fill:#fff}} .dim{{stroke:#29465a;stroke-width:1.5;fill:none}} .ext{{stroke:#7d97a8;stroke-width:1.1;fill:none}} .frame{{fill:none;stroke:#173548;stroke-width:2}} .rule{{stroke:#173548;stroke-width:1.4}}</style>
<rect width="1600" height="1450" fill="white"/><rect class="frame" x="20" y="20" width="1560" height="1410"/>
{t(48,68,'訊號站渲染題｜mesh 三視圖與部件尺寸','title')}
{t(49,100,'資料來源：u02_station_v002；與 u03_render_v001 的五件世界幾何指紋一致','note')}
{t(65,155,'前視 X–Z（Y 方向投影）','head')}{front}
{dim_horizontal(fc-2*s,fc+2*s,fb,550,'4.00 m　Ground 外框')}
{dim_horizontal(fc-1.2*s,fc+1.2*s,fb,595,'2.40 m　Platform 外框')}
{dim_vertical(fb-2.2*s,fb,fc+2*s,735,'2.20 m　最高至地面')}
{t(855,155,'俯視 X–Y（Z 方向投影）','head')}{top}
{dim_horizontal(tc-2*s,tc+2*s,ty+2*s,805,'4.00 m　Ground 外框')}
{t(65,735,'右視 Y–Z（X 方向投影）','head')}{right}
{dim_horizontal(rc-2*s,rc+2*s,rb,1135,'4.00 m　Ground 外框')}
{dim_vertical(rb-2.2*s,rb,rc+2*s,735,'2.20 m　最高至地面')}
{t(855,850,'部件世界外框（X × Y × Z，m）','head')}
<line class="rule" x1="855" y1="870" x2="1530" y2="870"/>{''.join(rows)}
{t(855,1150,'Signal 為 mesh 頂點外框；非光源瓦數或材質參數。','small')}
<line class="rule" x1="20" y1="1190" x2="1580" y2="1190"/><line class="rule" x1="1050" y1="1190" x2="1050" y2="1430"/><line class="rule" x1="1330" y1="1190" x2="1330" y2="1430"/>
{t(45,1227,'輪廓取自實際 Blender 頂點的正交投影凸包；不包含完整標準隱線。','note')}
{t(45,1262,'Ground 是 4 × 4 m、厚度 0 的平面；本題用於材質、燈光、相機與渲染。','note')}
{t(45,1297,'尺寸是數位場景值；非 3D 列印模型、製造規格或公差。','note')}
{t(45,1332,'各視圖標示坐標軸；未聲稱符合特定工程投影法及標準。','note')}
{t(45,1367,'來源 SHA-256：'+data['source']['sceneSha256'][:20]+'…','small')}
{t(1070,1227,'圖名：訊號站','note')}{t(1070,1262,'用途：渲染教學','note')}{t(1070,1297,'版次：v001','note')}
{t(1350,1227,'單位：m','note')}{t(1350,1262,'尺度：隨畫面','note')}{t(1350,1297,'公差：待定','note')}
</svg>'''
out=root/'learning/web/challenges/station-render-drawing-v001.svg'
if out.exists():raise FileExistsError('preserve previous version')
out.write_text(svg+'\n',encoding='utf8',newline='\n')
print('drawing',out.relative_to(root).as_posix(),'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
