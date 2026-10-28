"""Test learner-copy protection and isolated-launch command without opening a UI."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / 'tutor' / 'open_parametric_box.py'
spec = importlib.util.spec_from_file_location('parametric_launcher', MODULE_PATH)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class ParametricLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'learning/evidence/source.blend'
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b'original evidence')
        self.extensions = self.root / 'extensions'
        (self.extensions / 'user_default/CAD_Sketcher').mkdir(parents=True)
        self.blender = self.root / 'blender.exe'
        self.blender.write_bytes(b'fake')
        for name, value in [('ROOT',self.root),('SOURCE',self.source),('SOURCE_SHA256',hashlib.sha256(b'original evidence').hexdigest()),('EXTENSIONS',self.extensions),('BLENDER',self.blender)]:
            p=patch.object(launcher,name,value); p.start(); self.addCleanup(p.stop)

    def call(self,*args):
        with patch.object(sys,'argv',['open_parametric_box.py',*map(str,args)]), \
             patch.object(launcher.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            value=launcher.main()
            return value,run

    def test_new_copy_uses_isolated_profile_and_real_input(self):
        target=self.root/'learning/workspaces/engineering/my_box_v001.blend'
        value, run=self.call('--copy-to',target)
        self.assertEqual(value,0)
        self.assertEqual(target.read_bytes(),self.source.read_bytes())
        args=run.call_args.args[0]; env=run.call_args.kwargs['env']
        self.assertIn('--factory-startup',args)
        self.assertNotIn('--enable-event-simulate',args)
        self.assertEqual(env['BLENDER_USER_EXTENSIONS'],str(self.extensions))
        self.assertEqual(args[-1],str(target.resolve()))
        self.assertNotEqual(env['BLENDER_USER_CONFIG'],env.get('APPDATA'))

    def test_cannot_overwrite_or_copy_to_evidence(self):
        existing=self.root/'my_box.blend'; existing.write_bytes(b'keep me')
        with self.assertRaises(SystemExit): self.call('--copy-to',existing)
        self.assertEqual(existing.read_bytes(),b'keep me')
        with self.assertRaises(SystemExit): self.call('--copy-to',self.source.parent/'another.blend')
        with self.assertRaises(SystemExit): self.call('--open-existing',self.source)
        self.assertEqual(self.source.read_bytes(),b'original evidence')

    def test_reopen_existing_does_not_require_source(self):
        saved=self.root/'saved.blend'; saved.write_bytes(b'user copy')
        self.source.unlink()
        value,run=self.call('--open-existing',saved)
        self.assertEqual(value,0)
        self.assertEqual(saved.read_bytes(),b'user copy')
        self.assertEqual(run.call_args.args[0][-1],str(saved.resolve()))

    def test_changed_source_is_rejected_before_creating_destination_or_launching(self):
        self.source.write_bytes(b'changed evidence')
        target=self.root/'new-folder/my_box_v001.blend'
        with patch.object(sys,'argv',['open_parametric_box.py','--copy-to',str(target)]), \
             patch.object(launcher.subprocess,'run') as run, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                launcher.main()
            run.assert_not_called()
        self.assertFalse(target.exists())
        self.assertFalse(target.parent.exists())


if __name__=='__main__': unittest.main()
