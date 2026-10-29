"""題圖須可由已核雜湊的 STL 幾何重現，不將工程草案視為實體合格。"""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('build_fit_trial_drawing_v003.py', 'fit-trial-drawing-v003.svg'),
    ('build_lip_clearance_drawing_v001.py', 'lip-clearance-drawing-v001.svg'),
    ('build_dovetail_trial_drawing_v002.py', 'dovetail-trial-drawing-v002.svg'),
    ('build_snapfit_coupons_drawing_v003.py', 'snapfit-coupons-drawing-v003.svg'),
]
PARAMETRIC_CASES = [
    ('build_parametric_challenges_drawings_v002.py', 'sketch_figure', 'sketch-constraint-drawing-v002.svg'),
    ('build_parametric_box_drawing_v003.py', 'box_figure', 'parametric-box-drawing-v003.svg'),
]

class ChallengeDrawingEvidenceTests(unittest.TestCase):
    def test_source_geometry_reproduces_exact_svg(self):
        for script, drawing in CASES:
            with self.subTest(drawing=drawing):
                spec = importlib.util.spec_from_file_location('drawing_' + script[:-3], ROOT / 'learning/tutor' / script)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                expected = (ROOT / 'learning/web/challenges' / drawing).read_bytes()
                actual = module.build().encode('utf-8')
                self.assertEqual(actual, expected)
                self.assertEqual(ET.fromstring(actual).tag, '{http://www.w3.org/2000/svg}svg')

    def test_parametric_source_readbacks_reproduce_exact_svg(self):
        for script, function, drawing in PARAMETRIC_CASES:
            with self.subTest(drawing=drawing):
                spec = importlib.util.spec_from_file_location('drawing_' + script[:-3], ROOT / 'learning/tutor' / script)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                actual = (getattr(module, function)() + '\n').encode('utf-8')
                self.assertEqual(actual, (ROOT / 'learning/web/challenges' / drawing).read_bytes())
                self.assertEqual(ET.fromstring(actual).tag, '{http://www.w3.org/2000/svg}svg')

if __name__ == '__main__':
    unittest.main()
