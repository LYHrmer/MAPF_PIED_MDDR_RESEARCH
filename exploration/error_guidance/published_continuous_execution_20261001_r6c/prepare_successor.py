from pathlib import Path
import hashlib
import json
import shutil

root = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance')
old = root / 'published_continuous_execution_20261001_r6b'
new = root / 'published_continuous_execution_20261001_r6c'
assert not new.exists(), new
new.mkdir()
names = ['PROTOCOL.md', 'prepare.py', 'build.py', 'freeze.py', 'run_trial.py', 'run_matrix.py', 'mapping_replay.py', 'audit.py', 'adapt_audit.py', 'official_bridge.cpp', 'summarize_results.py', 'archive_raw.py', 'reproduce_move_merge.py', 'verify_geometry_registration.py']
for name in names:
    shutil.copyfile(old / name, new / name)
protocol = (new / 'PROTOCOL.md').read_text().replace('# R6b published planners', '# R6c published planners')
protocol += '''
## R6c coordinate-registration correction, frozen before native runs

The author server has flipped_coord=true. Its parser stores (col,row), and the unchanged controller maps those ADG coordinates to physical (x,y)=(-row,-col). R6/R6b input preparation incorrectly placed robots and obstacles at (-col,-row). The retained input-to-auditor preflight found 244 mismatches out of 252 checks before any native execution. R6c corrects both robot and obstacle XML positions to (-row,-col) for both methods. The original MovingAI map/scenario, scenario ordering, integer planner cells, complete FIFO streams, all 24 run specifications and official planner/model files are unchanged. This shared adapter correction is not an outcome-dependent map or parameter selection. The square arena boundary is invariant under this coordinate exchange. R6 and R6b frozen packages, failed preflight receipts, and any native failure artifacts are retained.

R6c must pass both exact-function no-merge regression and the complete registered input/start/obstacle coordinate test before the matrix starts. Body poses in all raw logs use the declared author coordinate transform; geometric clearance analysis must use these actual XML obstacle positions.
'''
(new / 'PROTOCOL.md').write_text(protocol)
prepare = (new / 'prepare.py').read_text()
needle = "position=f'{-x},{-y},0'"
assert prepare.count(needle) == 2
(new / 'prepare.py').write_text(prepare.replace(needle, "position=f'{-y},{-x},0'"))
provenance = {
    'parent': str(old),
    'parent_freeze_sha256': hashlib.sha256((old / 'freeze.json').read_bytes()).hexdigest(),
    'parent_native_runs_at_successor_preparation': sorted(p.name for p in (Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / old.name / 'runs').glob('*')),
    'reason': 'Physical robot/obstacle placement did not match the unchanged author flipped-coordinate mapping.',
    'failed_preflight': json.loads((old / 'geometry_preflight_failure.json').read_text()),
    'shared_changes': ['Physical robot and obstacle placement: planner(row,col) maps to physical(-row,-col) for both methods'],
    'planner_map_FIFO_model_matrix_changes': [],
}
(new / 'successor_provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
shutil.copyfile('/tmp/prepare_r6c_successor.py', new / 'prepare_successor.py')
print(new)
