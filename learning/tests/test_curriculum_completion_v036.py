"""Regression checks for v036 evidence, STL exports, and learner-state safety.

These tests validate recorded digital evidence; they do not substitute for visual
inspection, a fresh Blender reimport, printing, measurement, or qualification.
"""
import hashlib
import json
import math
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / 'learning'
CURRICULUM = LEARNING / 'web/engineering-curriculum-v036.json'
OLD = LEARNING / 'web/engineering-curriculum-v035.json'
PATH = LEARNING / 'web/engineering-path-v005.json'
PROGRESS = LEARNING / 'progress.json'
SUMMARY = LEARNING / 'evidence/08/2026-10-28-ch11-stl-summary-v002/safe-summary-v001.json'
PATCH = LEARNING / 'patches/shared-source-review-v001.json'
OPTIONAL = {
    '11-17': ('lesson11_stl_export_optional_steps_v002.json', 44),
    '11-18': ('lesson11_cad_thread_optional_steps_v001.json', 16),
    '11-19': ('lesson11_cad_detached_screw_optional_steps_v001.json', 12),
    '11-20': ('lesson11_cad_tool_recovery_optional_steps_v001.json', 7),
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def steps(doc):
    return {s['id']: s for c in doc['chapters'] for s in c['steps']}


def binary_stl(path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError('truncated binary STL')
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + 50 * count or count == 0:
        raise ValueError('invalid binary STL length or empty mesh')
    points = []
    for offset in range(84, len(data), 50):
        values = struct.unpack_from('<12fH', data, offset)
        points.extend(zip(values[3:12:3], values[4:12:3], values[5:12:3]))
    if not all(math.isfinite(v) for point in points for v in point):
        raise ValueError('non-finite STL vertex')
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    return count, bounds


class CurriculumV036CompletionTests(unittest.TestCase):
    def test_active_drafts_have_a_real_evidence_or_document_replacement(self):
        old, new = steps(read(OLD)), steps(read(CURRICULUM))
        catalog = read(LEARNING / 'catalog.json')
        references = {(l['id'], s['id']): s for l in catalog['lessons'] for s in l['steps']}
        allowed = {'existing_demo', 'source_step_demo', 'documented_lesson', 'field_protocol_ready'}
        for identifier, before in old.items():
            if before.get('track') in ('pending', 'appendix') or before.get('evidenceStatus') not in ('draft_pending_demo', 'concept_only'):
                continue
            after = new[identifier]
            self.assertIn(after.get('evidenceStatus'), allowed, identifier)
            self.assertTrue(after.get('actions'), identifier)
            status = after['evidenceStatus']
            if status == 'existing_demo':
                self.assertTrue(after.get('figures') or after.get('artifacts'), identifier)
            elif status == 'source_step_demo':
                self.assertTrue(after.get('sourceSteps'), identifier)
                for ref in after['sourceSteps']:
                    self.assertTrue(references[(ref['lessonId'], ref['stepId'])].get('operationRun'), identifier)
            elif status in ('field_protocol_ready', 'documented_lesson'):
                self.assertTrue(after.get('limitations'), identifier)
                self.assertTrue(after.get('detail', {}).get('steps'), identifier)
        for s in new.values():
            if s.get('track') not in ('pending', 'appendix'):
                self.assertNotIn(s.get('evidenceStatus'), ('draft_pending_demo', 'concept_only'), s['id'])

    def test_shared_source_corrections_are_not_silently_dropped(self):
        corrections = read(PATCH)['patches']
        self.assertEqual(len(corrections), 16)
        current = steps(read(CURRICULUM))
        for identifier, changes in corrections.items():
            self.assertEqual(current[identifier]['actions'], changes['actions'], identifier)
            self.assertEqual(current[identifier]['evidenceStatus'], changes['evidenceStatus'], identifier)
            self.assertEqual(current[identifier]['detail'], changes['detail'], identifier)
            for caveat in changes.get('limitations', []):
                self.assertIn(caveat, current[identifier]['limitations'], identifier)
        idx = read(LEARNING / 'patches/shared-source-review-index-v001.json')
        self.assertEqual(len(idx['items']), 61)
        self.assertIn('不是 61 張', idx['scope'])

    def test_79_optional_steps_link_exact_raw_screenshots(self):
        curriculum = read(CURRICULUM)
        chapter = next(c for c in curriculum['chapters'] if c['id'] == 'ch11')
        all_ids = set()
        for section, (filename, count) in OPTIONAL.items():
            source = read(LEARNING / filename)
            records = source['steps']
            actual = [s for s in chapter['steps'] if s['section'] == section]
            self.assertEqual(len(records), count, section)
            self.assertEqual(len(actual), count, section)
            by_id = {s['id']: s for s in actual}
            for record in records:
                identifier = 'ch11-' + record['id'].lower()
                self.assertNotIn(identifier, all_ids)
                all_ids.add(identifier)
                item = by_id[identifier]
                self.assertEqual(item['track'], 'optional')
                self.assertEqual(item['evidenceStatus'], 'existing_demo')
                raw = record['screenshot']
                image_path = raw.get('path', raw.get('relativePath'))
                self.assertEqual(sha(ROOT / image_path), raw['sha256'], identifier)
                self.assertEqual(item['figures'][0]['path'], image_path, identifier)
                self.assertEqual(item['figures'][0]['sha256'], raw['sha256'], identifier)
                self.assertTrue(item['limitations'], identifier)
        self.assertEqual(len(all_ids), 79)
        recovery = read(LEARNING / OPTIONAL['11-20'][0])
        self.assertEqual(sha(ROOT / recovery['sourceSummary']), recovery['sourceSummarySha256'])
        for key in ('startingScene', 'demonstrationScene'):
            self.assertEqual(sha(ROOT / recovery[key]['path']), recovery[key]['sha256'])

    def test_six_real_binary_stls_and_recorded_independent_reimports(self):
        data = read(SUMMARY)
        self.assertEqual(len(data['items']), 6)
        self.assertEqual(len({item['id'] for item in data['items']}), 6)
        for item in data['items']:
            with self.subTest(item=item['id']):
                file = ROOT / item['stl']
                self.assertEqual(sha(file), item['stlSha256'])
                self.assertEqual(file.stat().st_size, item['stlBytes'])
                self.assertEqual(sha(ROOT / item['sourceScene']), item['sourceSha256'])
                count, bounds = binary_stl(file)
                self.assertEqual(count, item['binaryTriangles'])
                audit = read(ROOT / item['independentAudit'])
                self.assertEqual(audit['stlSha256'], item['stlSha256'])
                self.assertEqual(audit['binaryTriangles'], count)
                self.assertEqual(audit['reimport'], item['independentReimport'])
                self.assertEqual(item['guiReimport']['triangles'], count)
                self.assertEqual(item['independentReimport']['triangles'], count)
                for i in range(3):
                    for j in range(2):
                        for other in (item['boundsMm'], audit['binaryBoundsMm'], item['guiReimport']['boundsMm'], item['independentReimport']['boundsMm']):
                            self.assertAlmostEqual(bounds[i][j], other[i][j], delta=1e-5)
                    self.assertAlmostEqual(bounds[i][1] - bounds[i][0], item['dimensionsMm'][i], delta=1e-5)
                for k in ('boundaryEdges', 'nonManifoldEdges'):
                    self.assertEqual(item['guiReimport'][k], item['independentReimport'][k])
                for k in ('physicalPrint', 'physicalMeasurement', 'physicalFit', 'qualifiedClearance', 'qualifiedStrength'):
                    self.assertIsNone(audit[k], (item['id'], k))

    def test_field_results_are_blank_and_path_describes_digital_scope(self):
        curriculum, path = read(CURRICULUM), read(PATH)
        review = curriculum['contentReview']['reviewV036']
        for key in ('physicalPrint', 'physicalMeasurement', 'physicalInstallation', 'physicalFit', 'qualifiedClearance', 'qualifiedStrength'):
            self.assertIsNone(review[key], key)
        self.assertFalse(review['learnerProgressChanged'])
        self.assertRegex(review['learnerProgressSha256'], r'^[0-9a-f]{64}$')
        for name in ('engineering-measurement-fit-v001.json', 'engineering-compensation-v001.json', 'engineering-assembly-trace-v001.json'):
            template = read(LEARNING / 'journal/templates' / name)
            for group in ('records', 'parts'):
                for record in template.get(group, []):
                    self.assertTrue(all(v is None or v == [] for v in record.values()), (name, record))
            for v in template.get('assembly', {}).values():
                self.assertIsNone(v)
        coupon = (LEARNING / 'journal/templates/fit-coupon-records-v002.csv').read_text(encoding='utf-8-sig')
        import csv, io
        for row in csv.DictReader(io.StringIO(coupon)):
            self.assertEqual(row['record_kind'], 'nominal_design_only')
            for name in ('measured_x_mm', 'measured_y_mm', 'measured_z_mm', 'fit_observed', 'date'):
                self.assertEqual(row[name], '')
        pending = steps(curriculum)
        for identifier in ('ch11-08-05-01', 'ch11-08-05-02'):
            self.assertEqual(pending[identifier]['track'], 'pending')
            self.assertEqual(pending[identifier]['evidenceStatus'], 'field_protocol_ready')
        self.assertEqual([c['id'] for c in path['chapters']], [c['id'] for c in curriculum['chapters']])
        for key in ('physicalPrint', 'physicalMeasurement', 'physicalFit'):
            self.assertIsNone(path['contentReview']['revisionV005'][key])

    def test_builders_refuse_overwrite_and_preserve_progress(self):
        progress_before = sha(PROGRESS)
        for name, output in (('build_engineering_curriculum_v036.py', CURRICULUM), ('build_engineering_path_v005.py', PATH)):
            with self.subTest(builder=name):
                before = sha(output)
                result = subprocess.run([sys.executable, '-X', 'utf8', str(LEARNING / name)], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('refusing to overwrite', result.stderr)
                self.assertEqual(sha(output), before)
                self.assertEqual(sha(PROGRESS), progress_before)


if __name__ == '__main__':
    unittest.main()
