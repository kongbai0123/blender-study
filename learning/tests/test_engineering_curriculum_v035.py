"""Availability changes require real evidence and never imply learner completion."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'learning/web/engineering-curriculum-v034.json'
NEW = ROOT / 'learning/web/engineering-curriculum-v035.json'
READY = {'ch11-08-02-02', 'ch11-08-03-01', 'ch11-08-03-02', 'ch11-08-04-02'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manage():
    spec = importlib.util.spec_from_file_location('manage_v035', ROOT / 'learning/manage.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurriculumV035Tests(unittest.TestCase):
    def test_content_availability_is_supported_by_original_images(self):
        old, new = read(OLD), read(NEW)
        a = {s['id']: s for c in old['chapters'] for s in c['steps']}
        b = {s['id']: s for c in new['chapters'] for s in c['steps']}
        self.assertEqual(new['id'], old['id'])
        self.assertTrue(a.keys() <= b.keys())
        available = {k for k, s in a.items() if s.get('track') == 'pending' and not b[k].get('track')}
        self.assertEqual(available, READY)
        additions = [s for k, s in b.items() if k not in a]
        self.assertEqual(len(additions), 59)
        self.assertEqual({s['section'] for s in additions}, {'11-13', '11-14', '11-15', '11-16'})
        for step in additions + [b[k] for k in READY]:
            image = step['figures'][0]
            self.assertEqual(sha(ROOT / image['path']), image['sha256'], step['id'])
            self.assertTrue(step['limitations'])
        self.assertEqual(sum(not s.get('track') for s in b.values()), 243)
        self.assertEqual({k for k, s in b.items() if s.get('track') == 'pending'}, {'ch11-08-05-01', 'ch11-08-05-02'})
        review = new['contentReview']['reviewV035']
        self.assertFalse(review['learnerProgressChanged'])
        for key in ('physicalPrint', 'physicalMeasurement', 'physicalFit', 'qualifiedClearance', 'qualifiedStrength'):
            self.assertIsNone(review[key])

    def test_hardware_has_sources_and_trial_values_are_not_qualified(self):
        hardware = read(ROOT / 'learning/hardware-selection-v001.json')
        self.assertEqual(hardware['screw']['partNumber'], '001.16.342')
        self.assertEqual(hardware['insert']['partNumber'], 'RX-M3x5.7')
        self.assertTrue(hardware['screw']['source'].startswith('https://www.ettinger.de/'))
        self.assertTrue(hardware['insert']['source'].startswith('https://www.ruthex.de/'))
        self.assertEqual(hardware['designDraft']['coverClearanceHoleNominalDiameterMm'], 3.4)
        self.assertIn('試驗', hardware['designDraft']['coverClearanceHoleStatus'])
        for key in ('physicalPrint', 'physicalMeasurement', 'physicalFit', 'tighteningTorqueNm', 'strengthQualification'):
            self.assertIsNone(hardware[key])

    def test_historical_curriculum_and_remaining_physical_step_cannot_confirm(self):
        module = manage()
        # Historical behavior must not depend on the application's live pointer.
        module.ENGINEERING_CURRICULUM = NEW
        progress = {'events': []}
        args = SimpleNamespace(chapter='ch11', step='ch11-08-05-02', evidence='完成')
        with self.assertRaisesRegex(ValueError, '待製作'):
            module.engineering_event(progress, args, confirmed=True)
        self.assertEqual(progress, {'events': []})
        self.assertEqual(module.engineering_overview(progress)['total'], 243)

    def test_path_overview_matches_new_evidence_without_changing_order(self):
        old = read(ROOT / 'learning/web/engineering-path-v003.json')
        path = ROOT / 'learning/web/engineering-path-v004.json'
        new = read(path)
        self.assertEqual([c['id'] for c in old['chapters']], [c['id'] for c in new['chapters']])
        for a, b in zip(old['chapters'], new['chapters']):
            if a['id'] != 'ch11':
                self.assertEqual(a, b)
        chapter = next(c for c in new['chapters'] if c['id'] == 'ch11')
        self.assertIn('實體試驗待進行', chapter['availabilityLabel'])
        self.assertFalse(any(r['label'].startswith('待製作') for r in chapter['references']))
        before = path.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_path_v004.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_builder_refuses_overwrite(self):
        before = NEW.read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/build_engineering_curriculum_v035.py'], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(NEW.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
