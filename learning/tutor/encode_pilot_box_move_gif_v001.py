"""將本次獨立 Blender 原生視窗連續採樣影格轉成 GIF；保留每張原圖。"""
from hashlib import sha256
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'learning/evidence/04/2026-10-28-pilot-box-move-record-v002'
OUTPUT = ROOT / 'learning/web/pilot/box-demo.gif'
if OUTPUT.exists():
    raise RuntimeError('拒絕覆寫既有 GIF')
data = json.loads((RUN / 'frames.json').read_text(encoding='utf-8'))
assert data['locationBlenderUnits'] == [5.0, 0.0, 0.0]
frames = []
times = []
for entry in data['frames']:
    path = RUN / entry['file']
    assert sha256(path.read_bytes()).hexdigest() == entry['sha256']
    with Image.open(path) as image:
        # 全視窗原尺寸；GIF 會限制色盤，與原始 PNG 相異。
        frames.append(image.convert('RGB').quantize(colors=96))
    times.append(float(entry['monotonic']))
assert len(frames) == 31
durations = [max(10, round((b-a)*100)*10) for a, b in zip(times, times[1:])] + [500]
frames[0].save(OUTPUT, save_all=True, append_images=frames[1:], duration=durations,
               loop=0, optimize=True, disposal=1)
print(json.dumps({'path': str(OUTPUT), 'bytes': OUTPUT.stat().st_size,
                  'sha256': sha256(OUTPUT.read_bytes()).hexdigest(), 'sourceFrames': len(frames),
                  'dimensions': frames[0].size, 'durationMs': sum(durations)}, ensure_ascii=False))
