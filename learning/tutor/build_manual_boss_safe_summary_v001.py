"""Build a portable summary of recorded GUI evidence without publishing local paths."""
from pathlib import Path
from hashlib import sha256
import json

root = Path(__file__).resolve().parents[2]
base = root / 'learning/evidence/08/2026-10-28-manual-boss-gui-trial-v003'
output = base / 'safe-summary-v001.json'
if output.exists():
    raise FileExistsError(output)
run = json.loads((base / 'run.json').read_text(encoding='utf-8'))
read = json.loads((base / 'blind-hole-readback.json').read_text(encoding='utf-8'))
geo = json.loads((root / 'learning/evidence/08/2026-10-28-manual-boss-drawing-v002/geometry-readback-v002.json').read_text(encoding='utf-8'))
pics = []
for item in run['records']:
    p = base / item['file']
    actual = sha256(p.read_bytes()).hexdigest()
    if actual != item['sha256']:
        raise ValueError('Screenshot hash mismatch: ' + item['file'])
    pics.append({'seq': item['seq'], 'action': item['action'], 'relativePath': p.relative_to(root).as_posix(), 'sha256': actual, 'observed': item['observed']})
if len(pics) != 8:
    raise ValueError('Expected eight GUI screenshots')
scene = root / geo['sourceScene']
if sha256(scene.read_bytes()).hexdigest() != geo['sourceSha256']:
    raise ValueError('Scene hash mismatch')
hole = geo['rings']['2@8']
result = {
    'schemaVersion': 1,
    'kind': 'isolated_blender_gui_blind_boss_draft',
    'blenderVersion': run['blender'],
    'sourceScene': {'relativePath': 'learning/evidence/08/2026-10-25-lesson08-parameters-demo-v001/demo-files/u08_thread_reference_v001.blend', 'sha256': read['sourceSha256']},
    'outputScene': {'relativePath': geo['sourceScene'], 'sha256': geo['sourceSha256']},
    'records': pics,
    'geometryReadback': {'outerDimensionsMm': read['dimensionsMm'], 'oppositeVertexHoleWidthMm': max(p[0] for p in hole)-min(p[0] for p in hole), 'vertices': read['vertices'], 'faces': read['faces'], 'nonManifoldEdges': read['nonManifoldEdges'], 'rays': read['rays']},
    'status': {'material': None, 'hardware': None, 'print': None, 'measurement': None, 'fit': None, 'strengthQualification': None},
    'limitations': ['Standalone boss; box is hidden and is not connected to this boss.', '32-sided mesh; opposite-vertex opening is not a verified hardware hole.', 'The recorded non-manifold and three ray checks do not establish absence of self-intersections, manufacturability, or fit.', 'The file dialog location and name were entered programmatically; mesh changes were Blender GUI events.', 'v001 stopped on the unexpected default size; v002 geometry succeeded but its overhead view was unclear; v003 used an angled view.'],
}
output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(output.relative_to(root).as_posix(), sha256(output.read_bytes()).hexdigest())
