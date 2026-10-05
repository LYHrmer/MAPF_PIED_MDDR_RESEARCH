"""Semantic negative controls on copies; zero solver calls or raw-file edits."""
import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import json
from pathlib import Path
from audit_episode import Auditor, CAS, canon, ROOT

HERE = Path(__file__).resolve().parent
EP = ROOT/'episodes/random-32-32-10__s08__n32__pause_range_2to5/learned_position_structural/episode.json'
a = Auditor(EP)
a.events_and_outcomes()
assert not a.errors
original = copy.deepcopy(next(p for p in a.predictions.values()
    if p['position_predictor_input'] is not None and p['context']['elapsed'] > 0))
baseline_key = canon(original)
a.check_prediction(baseline_key)
assert not a.errors
results = []
controls = [
    ('elapsed_includes_wait', lambda p: p['context'].__setitem__('elapsed', p['context']['elapsed']+5)),
    ('future_END_feature', lambda p: p['context']['completed_history'].append(dict(nominal_duration=1, duration=9, start=p['time'], end=p['time']+9, delivered=p['time']+9))),
    ('joint_capture_age_changed', lambda p: p['position_predictor_input']['position'].__setitem__('age', 99.)),
    ('joint_wrong_occurrence', lambda p: p['position_predictor_input']['position'].__setitem__('occurrence_id', 'different-action')),
    ('joint_undelivered_position', lambda p: p['position_predictor_input']['position'].__setitem__('delivered_age', 99.)),
    ('joint_private_feature', lambda p: p['position_predictor_input'].__setitem__('private_pause', 3.)),
    ('joint_zero_remaining', lambda p: p['position_predictor_output'].__setitem__('remaining_time', 0.)),
    ('fused_remaining_wrong', lambda p: p.__setitem__('remaining_time', p['remaining_time']+5)),
    ('future_ratio_corrupted', lambda p: p.__setitem__('future_duration_ratio', 99.)),
    ('encoded_progress_corrupted', lambda p: p.__setitem__('encoded_progress', -.5)),
    ('position_silently_ignored', lambda p: p.__setitem__('delivered_position', None)),
]
for name, mutate in controls:
    p = copy.deepcopy(original)
    mutate(p)
    key = canon(p)  # Rehash each mutation: these test semantics, not only hashes.
    a.predictions[key] = p
    start = len(a.errors)
    a.check_prediction(key)
    errors = a.errors[start:]
    assert errors, name
    results.append(dict(case=name, rejected=True, failed_checks=sorted({e['check'] for e in errors})))
store = CAS(a.e['evidence_store'])
ref = a.e['initial_graph_ref']
store.get(ref)
for name, change in [('cached_CAS_size', {'raw_bytes': ref['raw_bytes']+1}), ('CAS_path_traversal', {'path': '../outside'})]:
    try:
        store.get(dict(ref, **change))
    except AssertionError:
        pass
    else:
        raise AssertionError(name)
    results.append(dict(case=name, rejected=True))
out = dict(passed=True, cases=results, source_episode=str(EP),
    source_episode_sha256=hashlib.sha256(EP.read_bytes()).hexdigest(),
    auditor_sha256=hashlib.sha256((HERE/'audit_episode.py').read_bytes()).hexdigest(),
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    raw_modified=False, new_scientific_episodes=0, new_solver_calls=0,
    scope='Prediction and CAS verifier negative controls; graph/physics verified separately.')
(HERE/'VERIFIER_SELFCHECK.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
print(json.dumps(out))
