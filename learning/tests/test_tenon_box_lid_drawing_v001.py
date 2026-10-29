import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('tenon_drawing', ROOT/'learning/tutor/build_tenon_box_lid_drawing_v001.py')
draw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(draw)

class TenonDrawingTest(unittest.TestCase):
    def test_saved_geometry_section_and_scope(self):
        self.assertEqual(draw.digest(draw.MODEL), draw.EXPECTED['scene'])
        body, lid = draw.load_mesh('body'), draw.load_mesh('lid')
        self.assertEqual(draw.bounds(body), [[-30,30],[-20,20],[-15,16.5]])
        self.assertEqual(draw.bounds(lid), [[-30,30],[-20,20],[11,17]])
        section_b, section_l = draw.cut(body), draw.cut(lid)
        def contains(segs,x,z):
            return any(abs(p[0]-x)<1e-4 and abs(p[1]-z)<1e-4 for seg in segs for p in seg)
        for x,z in [(21,16.5),(25,16.5),(21,-13),(25,-13)]:self.assertTrue(contains(section_b,x,z),(x,z))
        for x,z in [(20.8,15),(25.2,15),(20.8,17),(25.2,17)]:self.assertTrue(contains(section_l,x,z),(x,z))
        data=json.loads(draw.RECORD.read_text(encoding='utf8'))
        self.assertEqual(data['drawing']['sha256'],hashlib.sha256(draw.OUT.read_bytes()).hexdigest())
        self.assertIsNone(data['physicalPrint']);self.assertIsNone(data['physicalFit']);self.assertIsNone(data['qualifiedClearance'])
        svg=draw.OUT.read_text(encoding='utf8');ET.fromstring(svg)
        for phrase in ['力學長度','均為試驗值','未切片','非完整標準隱線']:
            self.assertIn(phrase,svg)

    def test_rebuild_matches_saved_svg_without_overwrite(self):
        original_out,original_record=draw.OUT,draw.RECORD
        try:
            scratch=ROOT/'learning/tests/.scratch'
            scratch.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='tenon-drawing-test-',dir=scratch) as folder:
                draw.OUT=Path(folder)/'tenon-box-lid-drawing-v001.svg'
                draw.RECORD=Path(folder)/'record.json'
                draw.main()
                self.assertEqual(draw.OUT.read_bytes(),original_out.read_bytes())
                with self.assertRaises(FileExistsError):draw.main()
        finally:
            draw.OUT,draw.RECORD=original_out,original_record

if __name__=='__main__':unittest.main()
