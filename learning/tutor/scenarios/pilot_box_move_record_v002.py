"""連續採樣獨立 Blender 視窗，記錄 G X 5 Enter 移動原盒的示範。"""
import json
import os
import time
from pathlib import Path

import bpy

SOURCE = Path(__file__).resolve().parents[2] / 'evidence/04/2026-10-22-lesson04-demo-v001/demo-files/u04_box_v001.blend'


def build(g):
    do, key, capture, record = g['do'], g['key'], g['capture'], g['record']
    out = Path(g['OUT'])
    frames = []

    def load_source():
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=True)

    def check_start():
        obj = bpy.context.view_layer.objects.active
        if not obj or obj.name != 'Cube' or bpy.context.mode != 'OBJECT':
            raise ValueError('原盒不是作用中物件或不是 Object Mode')
        if any(abs(float(obj.location[i])) > 1e-5 for i in range(3)):
            raise ValueError('來源小盒位置不在原點')
        if any(abs(float(obj.dimensions[i]) - val) > 1e-4 for i, val in enumerate((60., 40., 30.))):
            raise ValueError('來源小盒外框不符合預期')

    def frame():
        entry = capture('frame-%03d' % len(frames))
        entry['monotonic'] = time.monotonic()
        frames.append(entry)

    def frames_for(count):
        for _ in range(count):
            do(frame, 0.16)

    def check_result():
        obj = bpy.context.view_layer.objects.active
        values = [float(x) for x in obj.location]
        if any(abs(a-b) > 1e-4 for a, b in zip(values, (5., 0., 0.))):
            raise ValueError('實際位移與預期不同：%r' % values)
        (out / 'frames.json').write_text(json.dumps({
            'source': str(SOURCE), 'operation': '3D Viewport: G, X, 5, Enter',
            'recording': '由 Blender 原生視窗在操作過程以計時器連續採樣，非使用舊截圖',
            'object': obj.name, 'locationBlenderUnits': values,
            'sceneScaleLength': float(bpy.context.scene.unit_settings.scale_length),
            'frames': frames,
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    do(load_source, 3.0)
    do(check_start, 0.3)
    record('pilot', 'before', '讀取獨立示範的既有小盒；起點位置與外框核對',
           lambda: 'Cube location %s；dimensions %s；scale_length %s' % (tuple(bpy.context.active_object.location), tuple(bpy.context.active_object.dimensions), bpy.context.scene.unit_settings.scale_length))
    frames_for(7)
    do(lambda: key('G', x=700, y=600), 0.25)
    frames_for(5)
    do(lambda: key('X', x=700, y=600), 0.25)
    frames_for(5)
    do(lambda: g['type_text']('5'), 0.25)
    frames_for(6)
    do(lambda: key('RET', x=700, y=600), 0.3)
    frames_for(8)
    do(check_result, 0.2)
    record('pilot', 'after', '在 3D Viewport 按 G、X、5、Enter，將原盒沿 X 正向移動 5 mm',
           lambda: 'Cube location %s；dimensions %s；scale_length %s' % (tuple(bpy.context.active_object.location), tuple(bpy.context.active_object.dimensions), bpy.context.scene.unit_settings.scale_length))
