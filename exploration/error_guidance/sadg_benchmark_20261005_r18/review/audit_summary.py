#!/usr/bin/env python3
"""Independent complete-matrix/aggregate check. Reads no TEST before freeze."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from audit_episode import close, read


def main():
    root=Path(__file__).resolve().parent.parent
    frozen=read(root/'MODEL_FREEZE_RECEIPT.json')
    assert hashlib.sha256((root/'MODEL_FROZEN.json').read_bytes()).hexdigest()==frozen['model_sha256']
    reg=read(root/'EXPERIMENT_REGISTRATION.json');summary=read(root/'SUMMARY.json');analysis=read(root/'ANALYSIS.json')
    checks=0;errors=[]
    def check(ok,name,detail=None):
        nonlocal checks
        checks+=1
        if not ok:errors.append({'check':name,'detail':detail})
    check(not summary['missing'],'full_requested_matrix')
    check(analysis['summary_sha256']==hashlib.sha256((root/'SUMMARY.json').read_bytes()).hexdigest(),'analysis_summary_hash')
    expected={(c['case_id'],dist,arm) for c in reg['cases'] if c['split'] in ('CAL','TEST') for dist in reg['disturbances'] for arm in reg['arms']}
    rows=summary['rows'];idx={(r['case_id'],r['disturbance'],r['arm']):r for r in rows}
    check(len(idx)==len(rows) and set(idx)==expected,'matrix_exact_membership')
    raw={}
    failures={}
    for key,row in idx.items():
        if not row.get('episode_path'):
            check(row['status'].startswith('initial_planner_'),'omitted_only_planner_failure');continue
        path=root/row['episode_path'];e=read(path);receipt=read(path.parent/'RUN_RECEIPT.json');raw[key]=e
        failures[row['episode_path']]=dict(Counter(f['kind'] for f in e['failures']))
        h=hashlib.sha256(path.read_bytes()).hexdigest()
        check(h==row['episode_sha256']==receipt['episode_sha256'],'summary_raw_hash',key)
        for field in ('status','success','completed_agents','sum_completion','restricted_sum_completion','makespan',
            'query_count','query_payload_bytes','solver_calls','new_author_calls','reference_solver_seconds','new_solver_seconds','reference_author_seconds','episode_wall_seconds'):
            x=row.get(field);y=e.get(field)
            check(close(x,y,1e-11) if isinstance(x,(int,float)) and isinstance(y,(int,float)) else x==y,'summary_field:'+field,key)
        check(row['stale_queries']==sum(q['delivery_status']=='stale_occurrence' for q in e['queries']),'summary_stale_count',key)
        check(row['pending_queries']==sum(q['delivery_status']=='pending' for q in e['queries']),'summary_pending_count',key)
        check(row['solver_failure_count']==sum(f['kind']=='SOLVER_FAILURE_PARENT_GRAPH_RETAINED' for f in e['failures']),'summary_solver_failures',key)
        check(row['family']==e['benchmark']['family'] and row['split']==e['benchmark']['split'],'summary_group_and_split',key)
    inventory={r['episode_path']:r for r in analysis['failure_inventory']}
    check(len(inventory)==len(analysis['failure_inventory'])==len(raw),'failure_inventory_exact_count')
    check(set(inventory)==set(failures),'failure_inventory_exact_membership')
    for row in rows:
        if not row.get('episode_path'):continue
        item=inventory[row['episode_path']];e=raw[(row['case_id'],row['disturbance'],row['arm'])]
        check(item['episode_sha256']==row['episode_sha256'] and item['status']==row['status'],'failure_inventory_binding')
        check(item['failure_counts']==failures[row['episode_path']] and item['error']==e.get('error'),'failure_inventory_actual_events')
    for total in analysis['totals']:
        rr=[r for r in rows if r['split']==total['split'] and r['arm']==total['arm']];available=[r for r in rr if r.get('episode_path')]
        expected_total=dict(registered_worlds=len(rr),executed_worlds=len(available),successful_worlds=sum(r['success'] for r in rr),
            completed_agents=sum(r.get('completed_agents') or 0 for r in available),safely_completed_agents=sum(r['completed_agents'] for r in available if r['success']),
            registered_agents=sum(r['num_agents'] for r in rr),restricted_sum=sum(r.get('restricted_sum_completion') or 0. for r in available),
            queries=sum(r.get('query_count') or 0 for r in available),stale_queries=sum(r.get('stale_queries') or 0 for r in available),
            solver_calls=sum(r.get('solver_calls') or 0 for r in available),new_author_calls=sum(r.get('new_author_calls') or 0 for r in available),
            reference_solver_seconds=sum(r.get('reference_solver_seconds') or 0. for r in available),statuses=dict(Counter(r['status'] for r in rr)))
        counts=Counter()
        for r in available:counts.update(failures[r['episode_path']])
        expected_total.update(solver_failure_count=counts['SOLVER_FAILURE_PARENT_GRAPH_RETAINED'],
            adoption_rejection_count=counts['ADOPTION_REJECTED_PARENT_GRAPH_RETAINED'],
            pending_queries=sum(r['pending_queries'] for r in available),failure_events=dict(counts))
        for k,v in expected_total.items():check(total[k]==v if isinstance(v,dict) else close(total[k],v,1e-11),'aggregate:'+k,{'split':total['split'],'arm':total['arm']})
    import numpy as np
    for comparison in analysis['paired_learned']:
        ref=comparison['reference'];groups=defaultdict(list)
        for key,row in idx.items():
            if row['split']!='TEST' or row['arm']!='learned_query':continue
            other=idx[(row['case_id'],row['disturbance'],ref)]
            if not row['success'] or not other['success']:continue
            groups[row['family']].append({'time':row['restricted_sum_completion']-other['restricted_sum_completion'],
                'relative_time':(row['restricted_sum_completion']/other['restricted_sum_completion']-1)*100,
                'queries':row['query_count']-other['query_count'],'makespan':row['makespan']-other['makespan']})
        check(comparison['total_registered_worlds']==54 and comparison['legal_paired_worlds']==sum(map(len,groups.values())),'paired_complete_denominator',ref)
        check(set(comparison['family_means'])==set(groups),'paired_family_membership',ref)
        delta=[v['time'] for group in groups.values() for v in group]
        check(comparison['completion_time_outcomes']==dict(lower=sum(x< -1e-8 for x in delta),
            equal=sum(abs(x)<=1e-8 for x in delta),higher=sum(x>1e-8 for x in delta)),'paired_lower_equal_higher',ref)
        for metric in ('time','relative_time','queries','makespan'):
            means=[]
            for f,values in groups.items():
                avg=sum(v[metric] for v in values)/len(values);means.append(avg)
                check(close(comparison['family_means'][f][metric],avg,1e-10),'family_aggregate:'+metric,ref)
            ci=comparison['uncertainty'][metric]
            if not means:check(ci is None,'empty_pair_has_no_CI');continue
            check(ci['families']==len(means),'bootstrap_unit_count')
            check(close(ci['mean'],sum(means)/len(means),1e-10),'bootstrap_center')
            # Reproduce registered Monte Carlo using index draws, independent
            # from the plotter's direct value-choice implementation.
            rng=np.random.default_rng(20261005);indices=rng.integers(0,len(means),size=(10000,len(means)))
            samples=np.asarray(means)[indices].mean(axis=1);lo,hi=np.quantile(samples,[.025,.975])
            check(close(ci['lower'],lo,1e-9) and close(ci['upper'],hi,1e-9),'bootstrap_family_interval',{'reference':ref,'metric':metric})
    test=[r for r in rows if r['split']=='TEST']
    expected_strata={}
    for keys in (('map_name',),('num_agents',),('disturbance',),('map_name','num_agents','disturbance')):
        for r in test:
            key=(keys,tuple(r[k] for k in keys),r['arm'])
            expected_strata.setdefault(key,[]).append(r)
    strata={}
    for item in analysis['test_strata']:
        keys=tuple(item['group_by']);key=(keys,tuple(item['group'][k] for k in keys),item['arm'])
        check(key not in strata,'unique_stratum');strata[key]=item
    check(set(strata)==set(expected_strata),'strata_exact_membership')
    for key,rr in expected_strata.items():
        item=strata[key]
        for name,value in dict(worlds=len(rr),successful_worlds=sum(r['success'] for r in rr),
            agents=sum(r['num_agents'] for r in rr),restricted_sum=sum(r['restricted_sum_completion'] for r in rr),
            queries=sum(r['query_count'] for r in rr),stale_queries=sum(r['stale_queries'] for r in rr)).items():
            check(close(item[name],value,1e-11),'stratum_'+name,str(key))
    figure_path=root/'figures/FIGURE_DATA.json'
    if figure_path.exists():
        figure=read(figure_path)
        check(len(figure)==15 and len({(r['arm'],r['condition']) for r in figure})==15,'figure_exact_15_bars')
        for item in figure:
            rr=[r for r in test if r['arm']==item['arm'] and r['disturbance']==item['condition']]
            legal=[r for r in rr if r['success'] and idx[(r['case_id'],r['disturbance'],'history_only')]['success']]
            check(item['registered_worlds']==len(rr) and item['legal_paired_worlds']==len(legal),'figure_paired_denominator')
            check(close(item['query_fraction'],sum(r['query_count']/r['num_agents'] for r in rr)/len(rr),1e-11),'figure_query_fraction')
            grouped=defaultdict(list)
            for r in legal:grouped[r['family']].append(100*(r['restricted_sum_completion']/idx[(r['case_id'],r['disturbance'],'history_only')]['restricted_sum_completion']-1))
            means=[sum(v)/len(v) for v in grouped.values()];ci=item['relative_time_percent']
            if means:
                rng=np.random.default_rng(20261005);ids=rng.integers(0,len(means),size=(10000,len(means)))
                samples=np.asarray(means)[ids].mean(axis=1);lo,hi=np.quantile(samples,[.025,.975])
                check(ci['families']==len(means) and close(ci['mean'],sum(means)/len(means),1e-10),'figure_family_center')
                check(close(ci['lower'],lo,1e-9) and close(ci['upper'],hi,1e-9),'figure_family_interval')
            else:check(ci is None,'figure_empty_CI')
    else:check(False,'figure_data_required')
    report={'passed':not errors,'checks':checks,'errors':errors,'registered_matrix_rows':len(expected),
        'raw_episode_receipts':len(raw),'verified_strata':len(strata),'scientific_episode_reruns':0,'engine_policy_plotter_imported':False,
        'scope':'Matrix identity, raw-to-summary accounting, totals, legal paired family means and fixed bootstrap; episode safety is separately audited.'}
    (root/'review/SUMMARY_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
