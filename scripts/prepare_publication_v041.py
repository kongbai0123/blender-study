"""Refresh the local inventory for the correspondence correction; no Git mutations."""
import prepare_publication_v040 as previous

base=previous.base
base.RELEASE='2026-10-30-engineering-v041'
base.MANIFEST=f'docs/publication-manifest-{base.RELEASE}.json'
base.PATHSPEC=f'docs/publication-paths-{base.RELEASE}.txt'
AUDIT='learning/patches/2026-10-30-v040-correspondence-audit-v001/'


class CorrespondencePublication(previous.CompletionPublication):
    def local_only(self,rel,inspect_json=True):
        if rel.startswith(AUDIT):
            return 'local correspondence audit, candidate, browser diagnostics or protected baseline'
        if rel.startswith('learning/evidence/chapters/2026-10-30-efficient-plate-coordinates-v001/'):
            return 'failed selection probe; current lesson uses v002'
        return super().local_only(rel,inspect_json)

    def build(self):
        super().build()
        path=self.root/base.MANIFEST;data=base.read_json(path)
        data['validationLimits']=[x.replace('v040 completes','v041 preserves') for x in data['validationLimits']]
        data['validationLimits'].append('v041 adds explicit reference-image roles and same-coordinate cutter operation photographs; no physical results are claimed.')
        base.stable_json(path,data)


base.Publication=CorrespondencePublication

if __name__=='__main__':base.main()
