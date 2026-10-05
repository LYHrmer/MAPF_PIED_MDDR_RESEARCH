#!/usr/bin/env python3
"""Read all recorded failed solver calls; no reruns and no engine import."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def read(path):return json.loads(path.read_text())


def main():
    root=Path(__file__).resolve().parent.parent;records=[];by_split=Counter();total=0
    for receipt in sorted((root/'episodes').glob('*/*/*/RUN_RECEIPT.json')):
        path=receipt.parent/'episode.json';e=read(path);r=read(receipt);total+=1
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r['episode_sha256']
        failed=[s for s in e['solves'] if not s['model']['feasible'] or s['model'].get('error')]
        events=[f for f in e['failures'] if f['kind']=='SOLVER_FAILURE_PARENT_GRAPH_RETAINED']
        assert len(failed)==len(events)
        for s in failed:
            m=s['model'];folder=path.parent/'solves'/f"{s['gate_index']:05d}"
            candidates=[folder/'model.json.gz']
            if s.get('cached_model_file'):candidates.append(Path(s['cached_model_file']))
            models=[str(p) for p in candidates if p.exists()]
            before=read(folder/'before.json');after=read(folder/'after.json')
            assert before==after,'Failed solve did not retain the exact parent graph'
            assert any(f['time']==s['time'] and f['detail']==m for f in events)
            categories=[]
            if m.get('max_violation') is not None and m['max_violation']>=1e-5:categories.append('logged_constraint_residual_rejection')
            if m.get('max_bound_violation') is not None and m['max_bound_violation']>=1e-5:categories.append('logged_bound_rejection')
            if m.get('max_integrality_violation') is not None and m['max_integrality_violation']>=1e-5:categories.append('logged_integrality_rejection')
            if m.get('all_values_finite') is False:categories.append('logged_nonfinite_or_missing_solution')
            if m.get('error'):categories.append('author_exception')
            if not categories:categories.append('no_accepted_feasible_incumbent')
            split=e['benchmark']['split'];by_split[split]+=1
            records.append({'episode':str(path.relative_to(root)),'split':split,'world':e['benchmark']['world'],
                'arm':e['benchmark']['arm'],'probe':e['benchmark']['probe'],'gate_index':s['gate_index'],
                'time':s['time'],'semantic_key':s['semantic_key'],'status':m['status'],'feasible':m['feasible'],
                'error':m.get('error'),'max_violation':m.get('max_violation'),
                'max_bound_violation':m.get('max_bound_violation'),'max_integrality_violation':m.get('max_integrality_violation'),
                'cache_reused':s['cache_reused'],'new_author_calls':s['new_author_calls'],
                'episode_status':e['status'],'episode_success':e['success'],'exact_parent_graph_retained':True,
                'failure_categories':categories,'full_failed_model_payloads':models,
                'residual_independently_reconstructed_from_full_model':False,
                'scope':'Residual/status/error are original logged diagnostics checked against the source-enforced rejection branch. Exact parent retention and resulting complete physical trace are independently audited; absent failed-model payloads are not reconstructed.'})
    groups=defaultdict(list)
    for r in records:groups[r['semantic_key']].append(r)
    grouped=[{'semantic_key':key,'calls':len(rr),'splits':dict(Counter(r['split'] for r in rr)),
        'worlds':sorted({r['world'] for r in rr}),'arms':dict(Counter(r['arm'] for r in rr)),
        'gates':sorted({r['gate_index'] for r in rr}),'status_counts':dict(Counter(r['status'] for r in rr)),
        'max_violation_range':[min(r['max_violation'] for r in rr if r['max_violation'] is not None),max(r['max_violation'] for r in rr if r['max_violation'] is not None)],
        'all_uncached':all(not r['cache_reused'] for r in rr)} for key,rr in sorted(groups.items())]
    scopes={}
    for label,allowed in [('TRAIN',{'TRAIN'}),('CAL',{'CAL'}),('TEST',{'TEST'}),('EVALUATION',{'CAL','TEST'}),('ALL',{'TRAIN','CAL','TEST'})]:
        rr=[r for r in records if r['split'] in allowed]
        scopes[label]={'calls':len(rr),'unique_failed_inputs':len({r['semantic_key'] for r in rr}),
            'status_counts':dict(Counter(r['status'] for r in rr)),
            'categories':dict(Counter(c for r in rr for c in r['failure_categories'])),
            'maximum_logged_constraint_violation':max((r['max_violation'] or 0 for r in rr),default=0.),
            'new_author_calls':sum(r['new_author_calls'] for r in rr),
            'all_episodes_physically_completed':all(r['episode_success'] for r in rr),
            'all_exact_parent_retained':all(r['exact_parent_graph_retained'] for r in rr)}
    report={'passed':True,'science_episode_count':total,'scopes':scopes,'failed_input_groups':grouped,'records':records,
        'new_scientific_or_solver_episodes':0,'failed_models_rerun':False,
        'interpretation':'Solver OPTIMAL status does not imply an accepted feasible model. Failed inputs are not stored as reusable feasible cache hits; identical failed keys can incur repeated real author calls across distinct registered episodes. Physical completion and fallback success are separate from solver acceptance.'}
    (root/'review/FAILURE_DIAGNOSTICS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'science_episodes':total,'scopes':scopes,'failed_input_groups':grouped},indent=2))


if __name__=='__main__':main()
