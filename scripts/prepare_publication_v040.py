"""Prepare/verify a new local publication inventory; never stage, commit or push."""
import json
from pathlib import Path

import prepare_publication as base

base.DATE = '2026-10-30'
base.RELEASE = '2026-10-30-engineering-v040'
base.MANIFEST = f'docs/publication-manifest-{base.RELEASE}.json'
base.PATHSPEC = f'docs/publication-paths-{base.RELEASE}.txt'
PATCH = 'learning/patches/2026-10-30-chapter-completion-v040/'


class CompletionPublication(base.Publication):
    def local_only(self, rel, inspect_json=True):
        # Browser QA, raw execution records and failed candidates are not teaching assets.
        if rel.startswith('learning/drafts/') and '/checks/' in rel:
            return 'local browser QA and protected source baselines; not runtime teaching assets'
        if rel.startswith(PATCH) and any('/'+p in rel for p in ['candidate/', 'smoke', 'visual-review', 'before.json', 'pending-failure']):
            return 'local candidate, browser QA or state-protection baseline'
        if rel.startswith('learning/evidence/chapters/'):
            path = Path(rel)
            if path.name in ['run.json', 'runner-status.json'] or '/source-snapshot/' in rel:
                return 'raw operation/provenance retained locally; the lesson uses exact PNG and saved scene dependencies'
            if 'independent-step-reference-v00' in rel and 'independent-step-reference-v005' not in rel:
                return 'superseded or failed capture; current lessons use v005'
            if 'efficient-duplicate-v00' in rel and 'efficient-duplicate-v003' not in rel:
                return 'earlier framing/probe revision; current shortcut lesson uses v003'
            if path.name.endswith('-reference.blend') or path.name.startswith('related-'):
                return 'temporary source copy; final prepared scene is separately versioned'
        return super().local_only(rel, inspect_json)

    def build(self):
        for name in ['capture-plan-v003.json', 'shortcut-sources.json', 'source-snapshot/engineering-path.js']:
            self.add(PATCH+name, 'reviewed completion source facts or previous renderer snapshot')
        super().build()
        path = self.root / base.MANIFEST
        data = base.read_json(path)
        data['validationLimits'] = [
            'This is a local publication inventory, not a commit, push or public deployment.',
            'v040 completes 85 page layouts and adds digital-reference photographs; no physical printing, measurement or fit is qualified.',
            'Raw runner, Recent/workspace snapshots, candidate browser captures and superseded runs remain local.',
            'Some historical/local replay tests require intentionally omitted raw execution records; this inventory does not certify that every development test runs without them.',
            'Hash and reference validation is not a complete image-by-image or binary Blender-file privacy audit.'
        ]
        base.stable_json(path, data)


base.Publication = CompletionPublication

if __name__ == '__main__':
    base.main()
