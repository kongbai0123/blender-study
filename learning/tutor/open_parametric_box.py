"""Open a NEW user-selected copy of the isolated CAD Sketcher box experiment.

Example (PowerShell; run from the project root):
  python learning/tutor/open_parametric_box.py --copy-to learning/workspaces/engineering-parametric/my_box_v001.blend

To reopen your saved copy use --open-existing <your-copy.blend>.
The output may not already exist. The program preserves the evidence original,
uses isolated Blender preferences, and does not enable event simulation, so
the launched Blender accepts the user's real input. An official CAD Sketcher
installation in the recorded private profile is required on this computer.
If CAD Sketcher fails to enable, its controls or model links may not work;
check Blender before editing. Automatic recovery is disabled for this isolated
profile: save checkpoints under new names. Existing copies are not protected
against being overwritten by the user.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLENDER = Path(os.environ.get('BLENDER_EXE', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'))
EXTENSIONS = ROOT / 'learning/.publication-private/cad-sketcher-0.32.1-v001/profile/extensions'
SOURCE = ROOT / 'learning/evidence/parametric/2026-10-27-cad-sketcher-parametric-box-v004/demo-files/parametric_box_80x40_v003.blend'
SOURCE_SHA256 = 'a86cef672d274522c4461433e96c45e26c9da37efe116ecb53472dc3dca143c2'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument('--copy-to', help='New .blend path; must not already exist')
    choices.add_argument('--open-existing', help='Reopen your own editable .blend copy')
    args = parser.parse_args()
    dest = Path(args.copy_to or args.open_existing).resolve()
    if dest.suffix.lower() != '.blend': parser.error('destination must end in .blend')
    if dest.is_relative_to((ROOT/'learning/evidence').resolve()):
        parser.error('use a learner copy outside preserved evidence')
    for path in ((BLENDER, SOURCE) if args.copy_to else (BLENDER,)):
        if not path.is_file(): parser.error('required file unavailable: '+str(path))
    if not (EXTENSIONS / 'user_default' / 'CAD_Sketcher').is_dir():
        parser.error('isolated official CAD Sketcher profile is missing: '+str(EXTENSIONS))
    if args.copy_to:
        if dest.exists(): parser.error('destination already exists; choose a new version')
        if digest(SOURCE) != SOURCE_SHA256:
            parser.error('source scene SHA-256 does not match the recorded v003; no copy created')
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation avoids overwriting an existing learner file.
        with SOURCE.open('rb') as original, dest.open('xb') as copy:
            shutil.copyfileobj(original, copy)
        if digest(dest) != SOURCE_SHA256:
            raise RuntimeError('Copy verification failed; inspect destination before using it.')
    else:
        if not dest.is_file(): parser.error('editable copy not found')
    bootstrap = ("import addon_utils,bpy; "
                 "addon_utils.enable('bl_ext.user_default.CAD_Sketcher',default_set=True,persistent=True); "
                 "bpy.context.preferences.filepaths.use_auto_save_temporary_files=False")
    with tempfile.TemporaryDirectory(prefix='blender-parametric-user-') as profile:
        temp = Path(profile) / 'temp'; temp.mkdir()
        env = dict(os.environ, BLENDER_USER_CONFIG=profile,
                   BLENDER_USER_SCRIPTS=str(Path(profile)/'scripts'),
                   BLENDER_USER_DATAFILES=str(Path(profile)/'datafiles'),
                   BLENDER_USER_EXTENSIONS=str(EXTENSIONS), TEMP=str(temp), TMP=str(temp))
        print('Opening editable copy:', dest, flush=True)
        print('Sketch dimensions drive both parts. Preserve this file by Save As before a major change.', flush=True)
        print('CAD Sketcher 若啟用失敗，控制項或連動可能無效；編輯前請先在 Blender 確認。', flush=True)
        print('此隔離環境停用自動存檔，不可依靠它復原；請手動另存新版本。既有副本沒有防覆寫保護。', flush=True)
        result = subprocess.run([str(BLENDER), '--factory-startup', '--python-expr', bootstrap, str(dest)], env=env)
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
