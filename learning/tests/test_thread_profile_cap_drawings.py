import hashlib
import json
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
class ThreadProfileCapDrawingsTest(unittest.TestCase):
 def test_profile_image_and_existing_readback(self):
  svg=ROOT/'learning/web/challenges/manual-thread-profile-drawing-v001.svg'
  self.assertEqual(sha(svg),'989e11e99b8d6ba10c4658aa7b5ce40c02b856d66fc05d955d73a3c39d557c7e')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for x in ('R 4.800','R 6.000','0.600','0.300','並非已配合','CAD 草圖'):self.assertIn(x,xml)
  read=ROOT/'learning/evidence/08/2026-10-28-hand-profile-drawing-v001/profile-readback-v001.json'
  if read.exists():
   self.assertEqual(sha(read),'70b8c5995baaea458d632f653f9101b2d907fe88f5a20c4223f05d4dd05a7045')
   d=json.loads(read.read_text(encoding='utf8'));self.assertEqual(len(d['verticesMm']),3);self.assertEqual(len(d['edges']),3);self.assertEqual(d['faces'],0)
 def test_cap_image_and_existing_readback(self):
  svg=ROOT/'learning/web/challenges/side-thread-cap-drawing-v001.svg'
  self.assertEqual(sha(svg),'91a280379638cdfc820a3270b9eb64b58eb93fd50b6afa7f0a4b3bad085794c8')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for x in ('5.500','15.381','0.200','0.400','軸向端面間隙未設計','非既有平面上蓋'):self.assertIn(x,xml)
  read=ROOT/'learning/evidence/08/2026-10-28-side-cap-drawing-v001/cap-mesh-readback-v001.json'
  if read.exists():
   self.assertEqual(sha(read),'5a68bb446fcbc3ce8bac2a4f9ab10e8a28792970b7b6ac0c3f61c6999dd32ba2')
   d=json.loads(read.read_text(encoding='utf8'));self.assertTrue(all(d['projections'][k] for k in ('top','front','openEnd')));self.assertGreater(len(d['section']),0)
 def test_relief_cap_image_and_source_readback(self):
  svg=ROOT/'learning/web/challenges/side-thread-cap-drawing-v002.svg'
  self.assertEqual(sha(svg),'a4f44ea14b7f4a9cbaf42dc112c35864683d2dbc872f64211aed2c187a0d1880')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for x in ('5.500','15.381','0.200','0.400','軸向端隙名義','1.300','41 點'):self.assertIn(x,xml)
  read=ROOT/'learning/evidence/08/2026-10-28-side-cap-drawing-v002/cap-mesh-readback-v003.json'
  if read.exists():
   self.assertEqual(sha(read),'db8d549ff2b26dc50e704449c6f4d0b0ed7782b7a800432c6a0274d069140201')
   d=json.loads(read.read_text(encoding='utf8'));self.assertGreater(d['openingPlaneBoundaryCount'],0);self.assertGreater(len(d['section']),0)
 def test_hardware_table_retains_provenance_and_classification(self):
  p=ROOT/'learning/hardware-selection-v001.json'
  self.assertEqual(sha(p),'f6b3f32cff1a6e7a0396353960a81087055859e4b399751e4991362b13f4c6dc')
  spec=importlib.util.spec_from_file_location('ch_v008',ROOT/'learning/build_challenges_v008.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  table=module.hardware_info(json.loads(p.read_text(encoding='utf8')))
  self.assertEqual([s['url'].split('/')[2] for s in table['sources']],['www.ruthex.de','www.ettinger.de'])
  rows={row['label']:row['value'] for row in table['items']}
  self.assertIn('3.4',rows['小盒平面蓋（本案試驗值）']);self.assertIn('6.7',rows['螺母孔（原廠建議）'])
  self.assertIn('未驗證',rows['小盒平面蓋（本案試驗值）']);self.assertIn('001.16.342',rows['螺絲（已選）'])
 def test_four_boss_drawing_and_real_mesh_reference(self):
  svg=ROOT/'learning/web/challenges/m3-four-boss-layout-drawing-v001.svg'
  self.assertEqual(sha(svg),'1c64559e52a5d59d616aa629c482b2e7bcfba9d5289c91af90272891601337e5')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for token in ('42 柱心距','22 柱心距','Ø3.4','Ø8.0','Ø4.0','名義深 9.0','未建金屬實體','自訂試驗值'):self.assertIn(token,xml)
  for name,digest in [('body','ea98df6776ebe5ac718f7e367ffe21de1c669a848ba90a4a1696002d00ae658d'),('lid','72556a5931564138208ab46236ff3cab14c815df12261af5b5abd0ba5ee3f126')]:
   read=ROOT/f'learning/evidence/08/2026-10-28-m3-layout-drawing-v001/{name}-readback-v002.json'
   if read.exists():
    self.assertEqual(sha(read),digest);d=json.loads(read.read_text(encoding='utf8'));self.assertGreater(d['topPlaneBoundaryCount'],0)
 def test_first_chapter_box_lid_drawing(self):
  svg=ROOT/'learning/web/challenges/box-lid-identification-drawing-v001.svg'
  self.assertEqual(sha(svg),'26da9f1187fd9b8dbb8c08d1d968803ac4f72eb1d3b2497047dc7c8a2478fd12')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for token in ('下方環形唇邊','不是 Blender 介面畫面或使用者模型','55.6 × 35.6','51.6 × 31.6','試驗值','實體試配待定'):self.assertIn(token,xml)
  for name,digest in [('body','334485951b1429f2cf219d6cb5d3605d332a84a639278f4bfc64f5e72a97047e'),('lid','e62590958289027d4c0983d3f0ec672dbea220403e744ff925f0f9812e595e78')]:
   read=ROOT/f'learning/evidence/01/2026-10-28-box-lid-identification-drawing-v001/{name}-readback-v001.json'
   if read.exists():self.assertEqual(sha(read),digest)
 def test_cad_constraint_drawing_not_pitch_or_solid(self):
  svg=ROOT/'learning/web/challenges/cad-thread-constraint-drawing-v001.svg'
  self.assertEqual(sha(svg),'243f81c9b74d2cc290b2ad69613482018d6bd1286a053d27a197acb0cbe72db6')
  xml=svg.read_text(encoding='utf8');ET.fromstring(xml)
  for token in ('5.97047','6.000','0.600','0.800','不是螺距','未建立 XZ 螺旋或三維實體'):self.assertIn(token,xml)
if __name__=='__main__':unittest.main()
