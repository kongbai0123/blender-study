import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT/'learning/tutor/inspect_stl_v001.py'
spec = importlib.util.spec_from_file_location('inspect_stl', SCRIPT)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def binary(triangles):
    out = bytearray(b'solid is still binary'.ljust(80,b'\0') + struct.pack('<I',len(triangles)))
    for points in triangles:
        out.extend(struct.pack('<12fH',0,0,1,*[x for p in points for x in p],0))
    return bytes(out)


class InspectStlTests(unittest.TestCase):
    def test_unicode_filename_is_valid_json_even_through_a_cp950_pipe(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'coupon_\U0001f9ea.stl'
            path.write_bytes(binary([((0,0,0),(1,0,0),(0,1,1))]))
            result=subprocess.run([sys.executable,str(SCRIPT),'--file',str(path),'--units','mm'],
                                  env=dict(os.environ,PYTHONIOENCODING='cp950:strict'),capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout.decode('ascii'))
            self.assertEqual(data['inputName'],path.name)

    def test_opposite_winding_duplicate_stays_visible_and_file_stays_identical(self):
        triangle = ((0,0,0),(12,0,0),(0,9,4))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'source.stl'; path.write_bytes(binary([triangle,triangle[::-1]])); before=path.read_bytes()
            data = module.inspect(path,'mm',[12,9,4])
            self.assertEqual(data['exactCoordinateDuplicateGroups'],1)
            self.assertEqual(data['exactCoordinateDuplicateExcessTriangles'],1)
            self.assertTrue(data['numericalComparison']['withinNumericEpsilon'])
            self.assertEqual(path.read_bytes(),before)
            self.assertIsNone(data['qualifiedClearance'])

    def test_invalid_data_does_not_produce_approval(self):
        triangle = ((0,0,0),(1,0,0),(0,1,1))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'source.stl'
            for raw in (b'solid ascii only',binary([triangle])[:-1],binary([((0,0,0),(float('nan'),0,0),(0,1,1))])):
                path.write_bytes(raw)
                with self.assertRaises(ValueError): module.inspect(path,'mm')
            path.write_bytes(binary([triangle]))
            with self.assertRaises(ValueError): module.inspect(path,'m')
            mismatch = module.inspect(path,'mm',[2,1,1])
            self.assertFalse(mismatch['numericalComparison']['withinNumericEpsilon'])
            self.assertIsNone(mismatch['physicalFit'])

    def test_real_lesson_stls_are_reproducible_without_writes(self):
        doc=json.loads((ROOT/'learning/lesson11_stl_export_optional_steps_v002.json').read_text(encoding='utf8'))
        for item in doc['items']:
            path=ROOT/item['stl']; before=hashlib.sha256(path.read_bytes()).hexdigest()
            result=module.inspect(path,'mm',item['dimensionsMm'])
            self.assertEqual(result['sha256'],item['stlSha256'])
            self.assertEqual(result['binaryTriangles'],item['binaryTriangles'])
            self.assertEqual(result['exactCoordinateDuplicateExcessTriangles'],0)
            self.assertTrue(result['numericalComparison']['withinNumericEpsilon'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
        first=doc['items'][0]
        process=subprocess.run([sys.executable,str(SCRIPT),'--file',str(ROOT/first['stl']),'--units','mm'],capture_output=True,text=True,encoding='utf8')
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual(json.loads(process.stdout)['sha256'],first['stlSha256'])
