"""Independent root review of raw events and paired effects; no native rerun."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib
import json

here = Path(__file__).resolve().parent
raw = here/'budget_task_run_20260930_01.json'
d = json.loads(raw.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert d['status'] == 'passed' and len(d['commands']) == 49 and len(d['instances']) == 48
assert all(x['exit_code'] == 0 and not x['timed_out'] for x in d['commands'])
assert all(sha(here/name) == digest for name,digest in d['protected_sha256'].items())
assert all(sha(Path(d['source_root'])/name) == digest for name,digest in d['source_header_sha256'].items())
assert all(sha(here/name) == rec['sha256'] for name,rec in d['new_sources'].items())

def exact_interval(value):
    assert value['lower'] == value['upper']
    return F(value['lower'],value['denominator'])

rows, paired = [], []
active_terms = candidates = decisions = 0
for cmd in d['commands'][1:]:
    events = [json.loads(line) for line in cmd['stdout'].splitlines() if line.strip()]
    condition = events[0]
    assert condition['event'] == 'condition'
    begin = None
    current_rows = []
    for e in events:
        kind = e['event']
        if kind == 'policy_begin':
            assert begin is None
            begin=e; services=[]; queries=[]; moves=0; contexts=[]; terms=0
        elif begin is None:
            continue
        elif kind == 'task_service':
            services.append((e['task'],exact_interval(e['at']),exact_interval(e['assigned_at'])))
        elif kind == 'query_selected':
            queries.append(e['id'])
        elif kind == 'original_move_started':
            moves += 1
        elif kind == 'budget_context':
            assert e['capacity'] == condition['capacity'] and e['used'] == len(queries)
            assert e['remaining'] == e['capacity']-e['used'] >= 0
            contexts.append(e)
        elif kind == 'cohort_input':
            terms += sum(t['active'] for t in e['tasks'])
        elif kind == 'cohort_candidate':
            count = sum(bool(x) for x in e['sequence'])
            assert count <= contexts[-1]['remaining']
            assert len([x for x in e['sequence'] if x]) == len(set(x for x in e['sequence'] if x))
            if e['feasible']:
                assert F(e['flow']) == sum(F(t['predicted_service_at'])-F(t['assigned_at']) for t in e['terms'])
            candidates += 1
        elif kind == 'cohort_choice':
            assert e['diagnostic_query_count'] <= contexts[-1]['remaining']
            decisions += 1
        elif kind == 'policy_result':
            assert len(services) == len({t for t,_,_ in services}) == 9
            assert len(queries) == len(set(queries)) <= condition['capacity']
            assert queries == e['queries']
            assert moves == e['original_requester_moves'] == 9+2*condition['ab_tail']+condition['c_tail']
            flow = sum(t-a for _,t,a in services)
            cohort = sum(t-a for name,t,a in services if name.endswith('-task1'))
            curve = [sum(t <= F(stop) for _,t,_ in services) for stop in e['service_times']]
            assert flow == e['task_flow_sum'] and curve == e['completed_tasks']
            assert max(t for _,t,_ in services) == e['last_task_service'] and e['final_tasks'] == 9
            assert len(contexts) == 2 and not begin['native_quote_diagnostic']
            row = dict(condition=condition['id'],policy=begin['policy'],model=begin['predictor'],
                capacity=condition['capacity'],ab_tail=condition['ab_tail'],c_tail=condition['c_tail'],
                queries=queries,flow=int(flow),cohort=int(cohort),curve=curve,moves=moves,active_terms=terms)
            current_rows.append(row); rows.append(row); active_terms += terms; begin=None
    assert len(current_rows) == 8 and begin is None
    for policy in ['nominal_completion_pair_window6','current_cohort_flow_pair']:
        lag = next(r for r in current_rows if r['policy'] == policy and r['model'] == 'seasonal_lag2')
        ar = next(r for r in current_rows if r['policy'] == policy and r['model'] == 'historical_AR1_OLS')
        assert all(lag[k] == ar[k] for k in ['queries','flow','cohort','curve','active_terms'])
    for model in ['frozen_nominal','seasonal_lag2','historical_AR1_OLS']:
        window = next(r for r in current_rows if r['model'] == model and r['policy'] == 'nominal_completion_pair_window6')
        cohort = next(r for r in current_rows if r['model'] == model and r['policy'] == 'current_cohort_flow_pair')
        paired.append(dict(condition=condition['id'],model=model,flow_delta=cohort['flow']-window['flow'],
                           query_delta=len(cohort['queries'])-len(window['queries'])))
assert len(rows) == 384 and sum(r['moves'] for r in rows) == 4032
assert active_terms > 0
report = dict(status='passed',scope='independent event/accounting and pairing review; exact predictive interval audit is a separate analyst artifact',
    episodes=384,tasks=3456,moves=4032,active_input_terms=active_terms,decisions=decisions,candidates=candidates,
    target_effect_counts=dict(Counter('better' if r['flow_delta']<0 else 'worse' if r['flow_delta']>0 else 'same' for r in paired)),
    target_flow_deltas=dict(Counter(r['flow_delta'] for r in paired)),AR_equals_lag2_all_96_pairs=True,
    raw_sha256=sha(raw),verifier_sha256=sha(Path(__file__)),pairs=paired,rows=rows)
with (here/'budget_task_root_review_20260930.json').open('x') as f: json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['pairs','rows']},indent=2))
