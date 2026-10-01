from pathlib import Path
import hashlib
import json
import shutil

root = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance')
old = root / 'published_continuous_execution_20261001_r6'
new = root / 'published_continuous_execution_20261001_r6b'
assert not new.exists(), new
new.mkdir()
names = ['PROTOCOL.md', 'prepare.py', 'build.py', 'freeze.py', 'run_trial.py', 'run_matrix.py', 'mapping_replay.py', 'audit.py', 'adapt_audit.py', 'official_bridge.cpp', 'summarize_results.py', 'archive_raw.py', 'reproduce_move_merge.py']
for name in names:
    shutil.copyfile(old / name, new / name)
protocol = (new / 'PROTOCOL.md').read_text()
protocol = protocol.replace('# R6 published planners', '# R6b published planners')
protocol += '''
## R6b successor correction, frozen before native runs

R6 was frozen but its nominal S1 patch disabled only insertActions merging; updateQueue still merged consecutive half-MOVE nodes. The exact-function two-node regression fails on the retained R6 source. R6b disables both merge entry points for both methods, preserving all other controller equations, normal ACK rules, maps, complete FIFO streams, seeds, configurations, model weights, time limits, and the 24-run matrix. No R6 outcome is used to select any arm. R6 freeze and evidence are retained without modification; the regression is a source-function check and is not counted as a native run.

The R6b audit additionally checks the unfiltered native sequence, that every MOVE front has exactly one node, that every MOVE ACK has the same single current front node and the original internal stop predicate abs(prevVelocity_) <= dt * velocity = 20 cm/s. This controller state is not the measured Chipmunk body velocity and is not a continuous safety certificate. Active-pause resume is also checked at trigger+20. The strict point threshold remains the native EPS=.03m.
'''
(new / 'PROTOCOL.md').write_text(protocol)
prepare = (new / 'prepare.py').read_text()
needle = "assert old.count(needle)==1;f.write_text(old.replace(needle,'if (false && not q.empty() and q.back().type == Action::MOVE) { // R6 S1: each ADG point has its own MOVE target'))"
replacement = """assert old.count(needle)==1
fixed=old.replace(needle,'if (false && not q.empty() and q.back().type == Action::MOVE) { // R6b S1: keep every original MOVE endpoint')
second='while (not q.empty() and q.front().type == Action::MOVE) {'
assert fixed.count(second)==1
fixed=fixed.replace(second,'while (false && not q.empty() and q.front().type == Action::MOVE) { // R6b S1: prevent per-tick re-merging')
f.write_text(fixed)"""
assert prepare.count(needle) == 1
(new / 'prepare.py').write_text(prepare.replace(needle, replacement))
audit = (new / 'audit.py').read_text()
needle = ' filtered=[]\n'
replacement = ''' require([e['sequence'] for e in es]==list(range(len(es))),'unfiltered_native_sequence')
 move_front={};move_end_count=0;max_move_ack_speed=0.
 for e in es:
  if e['kind']=='control' and e['control']['phase']=='front' and e['control']['type']==0:
   c=e['control'];require(len(c['nodes'])==1,'MOVE_front_must_not_merge');move_front[(e['robot'],c['nodes'][0])]=(e['tick'],c)
  elif e['kind']=='end' and (e['robot'],e['node']) in move_front:
   tick,c=move_front[(e['robot'],e['node'])];require(tick==e['tick'] and c['nodes']==[e['node']],'MOVE_ACK_current_single_node')
   speed=abs(e['observation']['speed_cm_s']);require(speed<=20.,'original_MOVE_stop_predicate');max_move_ack_speed=max(max_move_ack_speed,speed);move_end_count+=1
 filtered=[]
'''
assert audit.count(needle) == 1
audit = audit.replace(needle, replacement)
needle = " if spec['condition']=='unknown_pause':\n"
replacement = " resumes=[e for e in es if e['kind']=='control' and e['control']['phase']=='active_resume']\n if spec['condition']=='unknown_pause':\n  require(len(resumes)==1 and resumes[0]['tick']==T+20,'actual_pause_resume')\n"
assert audit.count(needle) == 1
audit = audit.replace(needle, replacement)
needle = "'strict_all_ACK_points_passed':True,"
replacement = "'strict_all_ACK_points_passed':True,'unfiltered_native_sequence_verified':True,'no_merged_MOVE_front_verified':True,'original_MOVE_stop_predicate_verified':True,'move_ACK_count':move_end_count,'maximum_MOVE_ACK_internal_speed_cm_s':max_move_ack_speed,"
assert audit.count(needle) == 1
(new / 'audit.py').write_text(audit.replace(needle, replacement))
provenance = {
    'parent': str(old),
    'parent_freeze_sha256': hashlib.sha256((old / 'freeze.json').read_bytes()).hexdigest(),
    'parent_native_runs_at_successor_preparation': sorted(p.name for p in (Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / old.name / 'runs').glob('*')),
    'reason': 'Second controller merge entry point remained active; exact-function regression violates declared strict no-merge S1 contract.',
    'regression': json.loads((old / 'merge_bug_reproduction.json').read_text()),
    'shared_changes': ['Disable per-tick updateQueue MOVE merge for both methods', 'Audit unfiltered sequence, single-node MOVE front, original internal stop predicate, and active-pause resume'],
    'matrix_model_task_selection_changes': [],
}
(new / 'successor_provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
shutil.copyfile('/tmp/prepare_r6b_successor.py', new / 'prepare_successor.py')
print(new)
