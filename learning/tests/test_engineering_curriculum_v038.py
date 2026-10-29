"""Chapter 00 (common functions and shortcuts) in curriculum v038 and learning path v007."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
LEARNING = ROOT / 'learning'
sys.path.insert(0, str(LEARNING))
import manage

OLD = LEARNING / 'web/engineering-curriculum-v037.json'
NEW = LEARNING / 'web/engineering-curriculum-v038.json'
OLD_PATH = LEARNING / 'web/engineering-path-v006.json'
NEW_PATH = LEARNING / 'web/engineering-path-v007.json'
CONTENT = LEARNING / 'engineering_v038_ch00.json'
HASHES = {
    NEW: '7f0150607d736a6bbd2b43767fba09ffb4f3bbc8aaf6228a4c08aec54dddf4df',
    NEW_PATH: '513803e0b08be50f824b7e5919a1c710540bc2ba3294d627ce1126cebf8d23cc',
    CONTENT: 'd77b15115d995aad363bae69762c959cb2fd35cadfa7c09d3f15d7a5bb9153eb',
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ChapterZeroTests(unittest.TestCase):
    def test_frozen_files_and_current_pointers(self):
        for path, digest in HASHES.items():
            self.assertEqual(sha(path), digest, path.name)
        self.assertEqual(manage.ENGINEERING_CURRICULUM.name, NEW.name)
        self.assertEqual(manage.ENGINEERING_PATH.name, NEW_PATH.name)

    def test_only_chapter_zero_is_added(self):
        old, new = read(OLD), read(NEW)
        self.assertEqual([c['id'] for c in new['chapters']], ['ch00'] + [c['id'] for c in old['chapters']])
        self.assertEqual(new['chapters'][1:], old['chapters'])
        changed = {key for key in set(old) | set(new) if old.get(key) != new.get(key)}
        self.assertEqual(changed, {'chapters', 'version', 'description', 'sourceVersions', 'contentReview', 'trackDefinitions'})
        self.assertEqual({k: v for k, v in new['trackDefinitions'].items() if k != 'reference'}, old['trackDefinitions'])
        self.assertIn('不能確認', new['trackDefinitions']['reference'])
        old_path, new_path = read(OLD_PATH), read(NEW_PATH)
        self.assertEqual(new_path['chapters'][1:], old_path['chapters'])
        self.assertEqual((new_path['chapters'][0]['id'], new_path['chapters'][0]['kind']), ('ch00', 'reference'))
        changed = {key for key in set(old_path) | set(new_path) if old_path.get(key) != new_path.get(key)}
        self.assertEqual(changed, {'chapters', 'intro', 'version', 'previousVersion', 'contentReview'})

    def test_reference_cards_are_complete_and_never_count(self):
        new = read(NEW)
        chapter = new['chapters'][0]
        self.assertEqual((chapter['id'], chapter['number'], len(chapter['steps'])), ('ch00', '00', 29))
        sections = [section['id'] for section in chapter['sections']]
        self.assertEqual(sections, ['00-%02d' % number for number in range(1, 8)])
        self.assertTrue(all(section['track'] == 'reference' for section in chapter['sections']))
        targets = {step['id']: (c, step) for c in new['chapters'] for step in c['steps']}
        order = []
        for step in chapter['steps']:
            self.assertEqual((step['track'], step['evidenceStatus'], step['sourceSteps']), ('reference', 'existing_demo', []), step['id'])
            self.assertTrue(1 <= len(step['actions']) <= 3, step['id'])
            self.assertTrue(step['detail']['steps'] and step['detail']['why'] and step['help'] and step['figures'], step['id'])
            order.append(sections.index(step['section']))
            for item in step['practice']:
                target_chapter, target = targets[item['stepId']]
                self.assertEqual((target_chapter['id'], target['section']), (item['chapterId'], item['sectionId']))
                self.assertNotEqual(item['chapterId'], 'ch00')
                self.assertNotIn(target.get('track'), ('appendix', 'pending', 'reference'), item['stepId'])
            for figure in step['figures']:
                self.assertEqual(figure['type'], 'screenshot')
                self.assertTrue(figure['path'].startswith('learning/evidence/') and figure['path'].endswith('.png'))
                self.assertEqual(sha(ROOT / figure['path']), figure['sha256'], figure['path'])
            for shortcut in step['shortcuts']:
                self.assertTrue(shortcut['keys'] and shortcut['effect'] and shortcut['evidence'], step['id'])
                for evidence in shortcut['evidence']:
                    self.assertEqual(sha(ROOT / evidence['path']), evidence['sha256'], evidence['path'])
        self.assertEqual(order, sorted(order))
        overview = manage.engineering_overview({'events': []})
        self.assertEqual(overview['total'], 243)
        self.assertEqual(overview['next'][0]['id'], 'ch01')

    def test_readings_are_copied_from_the_recorded_cases(self):
        content, new = read(CONTENT), read(NEW)
        steps = {step['id']: step for step in new['chapters'][0]['steps']}
        for card in content['cards']:
            step = steps[card['id']]
            if 'readings' not in card:
                self.assertNotIn('demonstration', step)
                continue
            demo = step['demonstration']
            source = ROOT / demo['source']['path']
            self.assertEqual(sha(source), demo['source']['sha256'])
            document = read(source)
            records = {item['case']: item['actual'] for item in document.get('cases', [])}
            records.update({item['slug']: item['observed'] for item in document.get('records', [])})
            for spec, reading in zip(card['readings']['items'], demo['readings'], strict=True):
                expected = {}
                for field in spec['fields']:
                    value = records[spec['case']]
                    for key in field.split('.'):
                        value = value[key]
                    expected[field] = value
                self.assertEqual((reading['kind'], json.loads(reading['value'])), ('readback', expected), card['id'])

    def test_manage_refuses_to_confirm_reference_cards_but_keeps_notes(self):
        progress = {'events': []}
        with mock.patch.object(manage, 'ENGINEERING_CURRICULUM', NEW):
            with self.assertRaisesRegex(ValueError, '速查'):
                manage.engineering_event(progress, SimpleNamespace(chapter='ch00', step='ch00-05-01', evidence='完成'), confirmed=True)
            event = manage.engineering_event(progress, SimpleNamespace(chapter='ch00', step='ch00-05-01', note='按 G 沒反應',
                                                                       note_kind='stuck', author='learner'), confirmed=False)
        self.assertEqual((event['type'], event['chapterId'], event['text']), ('engineering_step_note', 'ch00', '按 G 沒反應'))
        self.assertEqual(progress, {'events': []})

    def test_builders_refuse_to_overwrite(self):
        for builder, output in (('build_engineering_curriculum_v038.py', NEW), ('build_engineering_path_v007.py', NEW_PATH)):
            before = output.read_bytes()
            result = subprocess.run([sys.executable, '-X', 'utf8', 'learning/' + builder], cwd=ROOT,
                                    capture_output=True, text=True, encoding='utf8')
            self.assertNotEqual(result.returncode, 0, builder)
            self.assertIn('refusing to overwrite', result.stderr)
            self.assertEqual(before, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
