"""Root's independent archive and first-proposal-to-ADG check; no simulation."""
from pathlib import Path
import hashlib
import importlib.util
import json

base = Path(__file__).resolve().parent
package = base/'gpibt_lsmart_integration_20260930'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
manifest = read(package/'artifact_manifest.json')
assert all(sha(package/name) == digest for name,digest in manifest.items())
assert all(sha(Path(name)) == digest for name,digest in read(package/'binary_manifest.json').items())
original = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929/lsmart_compat')
successor = original.parent.parent/'gpibt_lsmart_integration_20260930/lsmart_successor'
for name, pins in read(package/'source_manifest.json').items():
    assert sha(original/name) == pins['base'] and sha(successor/name) == pins['successor']
spec = importlib.util.spec_from_file_location('partial_audit',package/'audit.py')
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)
events = [json.loads(s) for s in (package/'attempts/nominal_attempt02/events.jsonl').read_text().splitlines()]
partial = auditor.check(events)
saved = read(package/'audit.json')
assert all(saved[k] == v for k,v in partial.items())
assert saved['full_200_tick_trial_passed'] is False
decisions = [json.loads(s) for s in (package/'attempts/nominal_attempt02/decisions.jsonl').read_text().splitlines()]
assert len(decisions) == 1
decision = decisions[0]
proposal = next(e for e in events if e['kind'] == 'proposal')['proposal']
assert decision['proposal'] == proposal
assert decision['view'] == next(e for e in events if e['kind'] == 'view')['view']
assert decision['result']['actions'] == [4,3]  # Official non-MAPFT enum: W,U.
for agent, action in enumerate(decision['result']['actions']):
    start = decision['view']['mapf_instance']['starts'][agent]['location']
    end = start + [1,5,-1,-5,0][action]
    assert proposal['plan'][agent][1][:2] == [end//5,end%5]

# The only issued MOVE is the author's two half-cell decomposition. Bind both
# starts and endpoints to the actual planner proposal, rather than accepting
# an arbitrary mutually-consistent admit/END pair.
commands = [a for e in events if e['kind'] == 'admit' for a in e['actions']]
assert len(commands) == 2 and all(a[0] == '1' and a[3] == 'M' and a[6] == -1 for a in commands)
start_rc, end_rc = (x[:2] for x in proposal['plan'][1])
start_cr, end_cr = list(reversed(start_rc)), list(reversed(end_rc))
mid_cr = [(a+b)/2 for a,b in zip(start_cr,end_cr)]
assert commands[0][4:6] == [start_cr,mid_cr]
assert commands[1][4:6] == [mid_cr,end_cr]
assert not any(e['kind'] == 'admit' and e['robot'] == '0' for e in events)
assert all(e['type'] == 'M' for e in partial['ends'])
assert partial['assigned_tasks'] == 2 and partial['task_services'] == 0
try:
    auditor.check(events,strict_settled=True)
except ValueError as error:
    assert str(error) == 'sampled_settled_gate'
else:
    raise AssertionError('old trace must fail the new physical settled gate')
report = dict(status='passed_with_explicit_incomplete_native_trial',archive_files_verified=len(manifest),
    full_trial_completed=False,first_official_joint_action_bound_to_both_ADG_half_cells=True,
    planned_wait_has_no_admitted_move=True,final_source_and_binary_hashes_verified=True,
    first_run_binary_identity_not_retroactively_certified=True,
    task_service_not_exercised=True,new_settled_gate_rejects_old_trace=True,
    final_nominal_and_pause_not_run=True,partial_metrics=partial,
    archive_manifest_sha256=sha(package/'artifact_manifest.json'),reviewer_sha256=sha(Path(__file__)))
with (base/'gpibt_lsmart_root_review_20260930.json').open('x') as f:
    json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k != 'partial_metrics'},indent=2))
