"""Verify moved repository/CAS paths against an existing pilot; no simulation."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import shutil
import tempfile
from audit_episode import Auditor,ROOT,R18

HERE=Path(__file__).resolve().parent
source=ROOT/'r0/capture_binding/episode.json';raw=json.loads(source.read_text())
class LegacyPilotBudgetAuditor(Auditor):
    def eq(self,a,b,label):
        if label=='registered_query_budget' and b is None:
            # Saved R0 uses the inherited None -> 2N default; scientific R19
            # explicitly registers N. Normalize the assertion, never the receipt.
            b=2*self.e['agents']
        return super().eq(a,b,label)

with tempfile.TemporaryDirectory(prefix='r19-readonly-relocation-') as directory:
    temp=Path(directory);newroot=temp/'relocated_r19';newroot.mkdir()
    inherited=temp/'sadg_benchmark_20261005_r18';inherited.mkdir()
    shutil.copy2(R18/'engine.py',inherited/'engine.py')
    for name in raw['adapter_source_hashes']:shutil.copy2(ROOT/name,newroot/name)
    target=newroot/'r0/capture_binding';shutil.copytree(source.parent,target)
    newstore=temp/'relocated_store'
    shutil.copytree(Path(raw['evidence_store']),newstore)
    for solve in raw['solves']:
        if solve['cache_source']:
            original=Path(solve['cache_source']);destination=newroot/original.relative_to(ROOT)
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,destination)
    report=LegacyPilotBudgetAuditor(target/'episode.json',policy='structural',root=newroot,store=newstore).run()
    assert report['passed'],report['errors']
    output=dict(passed=True,checks=report['checks'],original_episode=str(source),
        episode_sha256=report['episode_sha256'],moved_repository_and_evidence_store=True,
        original_receipts_modified=False,new_scientific_episodes=0,new_solver_calls=0,
        pilot_default_budget='R0 config None independently resolved to inherited 2N; scientific R19 uses explicit N.',
        external_author_checkout='Retained original read-only author source paths; --path-map supports explicit relocation of those separately.',
        scope='Mechanical relocation check on saved R0 capture_binding; not an additional scientific sample.')
(HERE/'RELOCATION_CHECK.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
print(json.dumps(output))
