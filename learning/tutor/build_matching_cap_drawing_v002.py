"""Draw sampled actual cap projections and triangle section from verified source files."""
from hashlib import sha256
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
if len(sys.argv)!=6:raise SystemExit('usage: <mesh readback> <sha> <parameter record> <sha> <new output SVG>')
def checked(rel,digest):
 p=(ROOT/rel).resolve();p.relative_to(ROOT)
 if sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('hash mismatch: '+rel)
 return p
d=json.loads(checked(sys.argv[1],sys.argv[2]).read_text(encoding='utf8'))
spec=json.loads(checked(sys.argv[3],sys.argv[4]).read_text(encoding='utf8'))
if d['sceneSha256']!=spec['modelSha256']:raise ValueError('model and parameter record differ')
checked(d['sourceScene'],d['sceneSha256'])
parameters=spec['nominalParameters']; radial_offset=parameters['radialExpansionMm']; pitch=parameters['nominalPitchMm']
if radial_offset<=0 or pitch<=0:raise ValueError('invalid nominal trial parameters')
out=(ROOT/sys.argv[5]).resolve();out.relative_to(ROOT/'learning/web/challenges')
if out.exists():raise FileExistsError(out)
b=d['boundsMm'];center=[sum(pair)/2 for pair in b];length=[pair[1]-pair[0] for pair in b]
if not (all(0<v<50 for v in length) and len(d['section'])>0):raise ValueError('unexpected model')
scale=25
projections={
 'top':lambda p:(350+(p[0]-center[0])*scale,340-(p[1]-center[1])*scale),
 'front':lambda p:(350+(p[0]-center[0])*scale,825-(p[2]-center[2])*scale),
 'openEnd':lambda p:(1020+(p[1]-center[1])*scale,340-(p[2]-center[2])*scale),
}
section=lambda p:(1020+(p[0]-center[0])*scale,825-(p[1]-center[2])*scale)
def path_segment(a,c,project):
 x1,y1=project(a);x2,y2=project(c);return f'<path d="M{x1:.3f} {y1:.3f}L{x2:.3f} {y2:.3f}"/>'
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="1550" height="1300" viewBox="0 0 1550 1300" role="img" aria-labelledby="title desc"><title id="title">盒側匹配內牙帽工程題圖草案</title><desc id="desc">從實際數位帽網格提取三方向抽樣投影與 Y={d['cutYmm']} mm 三角面剖切線；材料、公差及實體試配待定。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#244f6e"/></marker></defs>
<rect width="1550" height="1300" fill="white"/><rect x="20" y="20" width="1510" height="1260" fill="none" stroke="#173548" stroke-width="3"/>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548"><text x="50" y="60" font-size="28" font-weight="700">盒側匹配內牙帽｜工程題圖草案</text><text x="50" y="90" font-size="17">來源為獨立 Blender 保存後重開的帽體網格；非既有平面上蓋，未完成實體試配。</text><text x="135" y="130" font-size="22" font-weight="700">俯視（+Z 朝 −Z）</text><text x="785" y="130" font-size="22" font-weight="700">開口端視（−X 朝 +X）</text><text x="135" y="610" font-size="22" font-weight="700">前視（−Y 朝 +Y）</text><text x="785" y="610" font-size="22" font-weight="700">A–A 網格剖切線（Y={d['cutYmm']} mm）</text></g>''']
parts.append('<g fill="none" stroke="#193548" stroke-width="1.6" stroke-linejoin="round">')
for key,project in projections.items():
 for a,c in d['projections'][key]:parts.append(path_segment(a,c,project))
for a,c in d['section']:parts.append(path_segment(a,c,section))
parts.append('</g>')
top_lo=350-length[0]*scale/2;top_hi=350+length[0]*scale/2
end_l=1020-length[1]*scale/2;end_r=1020+length[1]*scale/2;end_top=340-length[2]*scale/2;end_bottom=340+length[2]*scale/2
cut_screen=340-(d['cutYmm']-center[1])*scale
parts.append(f'''<g fill="none" stroke="#244f6e" stroke-width="1.2"><path d="M{top_lo:.3f} 540V575 M{top_hi:.3f} 540V575"/><line x1="{top_lo:.3f}" y1="565" x2="{top_hi:.3f}" y2="565" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M{end_l:.3f} 540V575 M{end_r:.3f} 540V575"/><line x1="{end_l:.3f}" y1="565" x2="{end_r:.3f}" y2="565" marker-start="url(#arrow)" marker-end="url(#arrow)"/><path d="M{end_r:.3f} {end_top:.3f}H1280 M{end_r:.3f} {end_bottom:.3f}H1280"/><line x1="1270" y1="{end_top:.3f}" x2="1270" y2="{end_bottom:.3f}" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="18"><text x="350" y="558" text-anchor="middle">X 外框 {length[0]:.3f}</text><text x="1020" y="558" text-anchor="middle">Y 外框 {length[1]:.3f}</text><text x="1290" y="340">Z 外框 {length[2]:.3f}</text><text x="135" y="1028">X →　Z ↑</text><text x="785" y="1028">X →　Z ↑；切面非螺紋標準符號</text></g>
<path d="M100 {cut_screen:.3f}H600" stroke="#557b93" stroke-width="1.2" stroke-dasharray="10 6"/><path d="M100 {cut_screen+18:.3f}V{cut_screen-18:.3f} M600 {cut_screen+18:.3f}V{cut_screen-18:.3f}" stroke="#557b93" stroke-width="1.2" marker-end="url(#arrow)"/><text x="80" y="{cut_screen-22:.3f}" font-family="Microsoft JhengHei,sans-serif" font-size="17" fill="#173548">A</text><text x="605" y="{cut_screen-22:.3f}" font-family="Microsoft JhengHei,sans-serif" font-size="17" fill="#173548">A</text>
<path d="M20 1050H1530 M980 1050V1280 M1260 1050V1280" fill="none" stroke="#173548" stroke-width="2"/>
<g font-family="Microsoft JhengHei,sans-serif" fill="#173548" font-size="17"><text x="45" y="1085">刀具頂點徑向外移 {radial_offset:.3f} mm；名義直徑差 {2*radial_offset:.3f}，非全域法向間隙。</text><text x="45" y="1115">P={pitch:.3f}、中心壁 {parameters['nominalCenterEndWallMm']:.3f}、軸向端隙名義 {parameters['nominalCentralAxialGapMm']:.3f} mm；僅九點檢查。</text><text x="45" y="1145">外視密線為 64 邊網格面界、非溝槽；可見邊抽樣非完整標準隱線。</text><text x="45" y="1175">材料、公差、列印、量測、試配與合格間隙待定；局部數位檢查不保證可製造。</text><text x="45" y="1205">來源 SHA-256：{d['sceneSha256']}；尺寸為數位讀值，勿量螢幕。</text><text x="45" y="1235">末端牙局部修削；內壁 216 點中 41 點數位差異超 0.0001 mm，原因待查。</text><text x="1000" y="1085">圖名：側向內牙帽</text><text x="1000" y="1115">版次：v002</text><text x="1000" y="1145">用途：教學草案</text><text x="1280" y="1085">單位：mm</text><text x="1280" y="1115">比例：隨畫面</text><text x="1280" y="1145">實體試配：未做</text></g></svg>''')
out.write_text('\n'.join(parts)+'\n',encoding='utf8',newline='\n')
print('drawing',out.relative_to(ROOT).as_posix(),sha256(out.read_bytes()).hexdigest())
