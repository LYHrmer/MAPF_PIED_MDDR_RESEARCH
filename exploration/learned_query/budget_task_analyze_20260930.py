"""Re-audit saved raw output, export all episodes and finite policy Pareto sets."""
import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
from budget_task_audit_20260930 import audit_events, require

HERE=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def analyze(source,prefix):
    data=json.loads(source.read_text())
    require(data['status']=='passed' and len(data['commands'])==49,'receipt is not complete successful 48-case run')
    root=Path(data['source_root'])
    for name,sha in data['protected_sha256'].items():
        require(digest(HERE/name)==sha,f'protected file changed: {name}')
    for name,sha in data['source_header_sha256'].items():
        require(digest(root/name)==sha,f'component header changed: {name}')
    require(digest(HERE/'BUDGET_TASK_CONTRACT_20260930.md')==data['contract_sha256'],'frozen contract changed')
    for name,record in data['new_sources'].items():
        require(digest(HERE/name)==record['sha256'],f'run source changed: {name}')
    rows=[]; active_cases=[]; raw_by_index={}
    for index,record in enumerate(data['commands'][1:]):
        require(record['exit_code']==0 and not record['timed_out'],'native command failed')
        events=[json.loads(line) for line in record['stdout'].splitlines() if line.strip()]
        audited=audit_events(events,index)
        require(audited==data['instances'][index],'saved compact audit differs from raw re-audit')
        raw_by_index[index]=events
        for row in audited['results']:
            row=dict(row,index=index,condition=audited['condition'],regime=(index//3)%4)
            rows.append(row)
            if row['active_input_terms']:active_cases.append(row['run_id'])
    require(len(rows)==384 and sum(r['tasks'] for r in rows)==3456 and sum(r['moves'] for r in rows)==4032,'frozen totals differ')
    require(active_cases,'active branch not covered')
    # Inferential units remain complete deterministic mechanism instances.
    by_case={i:[r for r in rows if r['index']==i] for i in range(48)}
    for i in range(0,48,3):
        require(len({(r['task_flow_sum'],tuple(r['curve']),tuple(r['queries'])) for r in by_case[i]})==1,'B0 physical result depends on model/rule')
    fields=('queries','cohort_flow','task_flow_sum','cohort_service','curve','last_service','moves','tasks')
    objective_pairs=[]; model_pairs=[]; comparator_pairs=[]
    for index,group in by_case.items():
        for model in ('frozen_nominal','seasonal_lag2','historical_AR1_OLS'):
            old=next(r for r in group if r['predictor']==model and r['policy']=='nominal_completion_pair_window6')
            new=next(r for r in group if r['predictor']==model and r['policy']=='current_cohort_flow_pair')
            objective_pairs.append(dict(index=index,model=model,flow_delta=new['task_flow_sum']-old['task_flow_sum'],
                                        cohort_delta=new['cohort_flow']-old['cohort_flow'],query_delta=new['query_count']-old['query_count']))
        for policy in ('nominal_completion_pair_window6','current_cohort_flow_pair'):
            lag=next(r for r in group if r['predictor']=='seasonal_lag2' and r['policy']==policy)
            ar=next(r for r in group if r['predictor']=='historical_AR1_OLS' and r['policy']==policy)
            equal=all(lag[k]==ar[k] for k in fields)
            model_pairs.append(dict(index=index,policy=policy,AR_equals_lag2=equal))
        nominal=next(r for r in group if r['predictor']=='frozen_nominal' and r['policy']=='current_cohort_flow_pair')
        for comparator in ('unit_admission_pair','original_rr'):
            simple=next(r for r in group if r['policy']==comparator)
            comparator_pairs.append(dict(index=index,comparator=comparator,nominal_cohort_flow=nominal['cohort_flow'],
                                          simple_cohort_flow=simple['cohort_flow'],nominal_all_flow=nominal['task_flow_sum'],
                                          simple_all_flow=simple['task_flow_sum'],nominal_queries=nominal['queries'],simple_queries=simple['queries']))
    capacity_pairs=[]
    for workload in range(4):
        for regime in range(4):
            groups=[by_case[12*workload+3*regime+b] for b in range(3)]
            for row in groups[0]:
                selected=[next(r for r in group if r['policy']==row['policy'] and r['predictor']==row['predictor']) for group in groups]
                capacity_pairs.append(dict(workload=workload,regime=regime,policy=row['policy'],predictor=row['predictor'],
                                           capacity=[0,1,2],queries=[r['query_count'] for r in selected],
                                           cohort_flow=[r['cohort_flow'] for r in selected],all_flow=[r['task_flow_sum'] for r in selected]))
    # Stable-fast / hidden-shock have the same *predecision information*, though future execution differs.
    for workload in range(4):
        for b in range(3):
            fast=raw_by_index[12*workload+6+b];shock=raw_by_index[12*workload+9+b]
            kinds={'historical_native_END_delivered','frozen_predictor','budget_context','cohort_input','cohort_candidate','budget_candidate_score','cohort_choice','query_selected','no_query'}
            require([e for e in fast if e['event'] in kinds]==[e for e in shock if e['event'] in kinds],'hidden-shock leaked into public choices')
    pareto=[]
    for workload in range(4):
        for regime in range(4):
            group=[r for r in rows if r['index']//12==workload and r['regime']==regime]
            points=sorted({(r['query_count'],r['cohort_flow'],r['task_flow_sum']) for r in group})
            frontier=[p for p in points if not any(q[0]<=p[0] and q[1]<=p[1] and q[2]<=p[2] and q!=p for q in points)]
            pareto.append(dict(workload=workload,regime=regime,metric_order=['queries','cohort_flow','all_task_flow'],
                               tested_policy_points=points,non_dominated_points=frontier,global_optimality_claim=False))
    durations=[(datetime.fromisoformat(c['finished_utc'])-datetime.fromisoformat(c['started_utc'])).total_seconds() for c in data['commands']]
    summary=dict(status='passed',source=str(source),source_sha256=digest(source),episodes=len(rows),tasks=sum(r['tasks'] for r in rows),
                 requester_moves=sum(r['moves'] for r in rows),native_checks=sum(c['checks'] for c in data['instances']),
                 audited_decisions=sum(r['audited_decisions'] for r in rows),audited_candidates=sum(r['audited_candidates'] for r in rows),
                 active_input_terms=sum(r['active_input_terms'] for r in rows),active_episodes=len(active_cases),
                 active_episode_ids=active_cases,protected_old_files=len(data['protected_sha256']),source_headers=len(data['source_header_sha256']),
                 all_sources_unchanged=True,compile_seconds=durations[0],native_seconds_min=min(durations[1:]),native_seconds_max=max(durations[1:]),
                 objective_pair_counts={name:sum((r['flow_delta']<0 if name=='improved' else r['flow_delta']==0 if name=='equal' else r['flow_delta']>0) for r in objective_pairs) for name in ('improved','equal','worse')},
                 all_AR_lag2_pairs_equal=all(r['AR_equals_lag2'] for r in model_pairs),
                 hidden_shock_public_inputs_identical=True,objective_pairs=objective_pairs,model_pairs=model_pairs,
                 comparator_pairs=comparator_pairs,capacity_pairs=capacity_pairs,pareto=pareto,
                 full_paid_cost=False,external_baseline_result=False,independent_random_sample_claim=False)
    json_path=prefix.with_suffix('.json');csv_path=prefix.with_suffix('.csv')
    for output in (json_path,csv_path):require(not output.exists(),f'will not overwrite {output}')
    with json_path.open('x') as stream:json.dump(summary,stream,indent=2)
    with csv_path.open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(v,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    print(json.dumps({k:summary[k] for k in ('status','episodes','tasks','requester_moves','native_checks','audited_decisions','audited_candidates','active_episodes','all_AR_lag2_pairs_equal','objective_pair_counts')},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('--output-prefix',type=Path,required=True)
    args=parser.parse_args();analyze(args.source.resolve(),args.output_prefix.resolve())
