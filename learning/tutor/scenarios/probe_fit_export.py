"""Read actual STL export dialog in an isolated Blender; no export or source edits."""
import json
from pathlib import Path
import bpy
from common import Kit, PROJECT


def build(g):
    k = Kit(g)
    source = PROJECT / 'learning/evidence/05/2026-10-22-lesson05-demo-v002/demo-files/u05_fit_coupon_v001.blend'
    expected = 'c2f3edd915324ba66bbd3fb8c6ad1ea0214a539f74cbc732e37adc35f7325162'
    if g['sha256'](str(source)) != expected:
        raise RuntimeError('Verified pin source hash changed')
    copy = Path(k.demo_dir) / source.name
    copy.write_bytes(source.read_bytes())
    k.setup()
    k.file_dialog(56, k.demo_dir, copy.name)
    k.confirm_dialog(2.0)
    k.do(lambda: k.click(40, 13), 0.5)
    k.do(lambda: k.move(73, 317), 0.6)
    k.menu_item(288, 436, 1.2)
    k.fill_dialog(k.demo_dir, 'probe.stl')

    def inspect(kind='export'):
        w = k.window('FILE_BROWSER')
        op = w.screen.areas[0].spaces.active.active_operator
        properties = op.properties
        props = {p.identifier: getattr(properties, p.identifier) for p in properties.bl_rna.properties
                 if p.type in ('BOOLEAN','INT','FLOAT','STRING','ENUM') and p.identifier != 'rna_type'}
        (Path(g['OUT'])/(kind+'-options.json')).write_text(json.dumps(props, ensure_ascii=False, indent=2, default=lambda value: sorted(value) if isinstance(value, set) else str(value))+'\n', encoding='utf-8')
        return 'Active export operator %s; properties saved from actual dialog.' % op.bl_idname

    k.record('05-04', 'export-dialog-probe', '在獨立 Blender 開 STL 匯出視窗，讀回真實選項但不匯出', inspect, win='FILE_BROWSER')
    k.cancel_dialog()
    k.do(lambda: k.key('F3', x=700, y=600), .4)
    k.do(lambda: k.type_text('Import STL'), .4)
    k.do(lambda: k.key('RET'), 1.2)
    k.fill_dialog(k.demo_dir, 'probe.stl')
    k.record('05-04', 'import-dialog-probe', 'F3 搜尋 Import STL，核對重新匯入視窗，不執行匯入', lambda: inspect('import'), win='FILE_BROWSER')
    k.cancel_dialog()
