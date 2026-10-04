#!/usr/bin/env python3
"""No solves: validate receipts, MAPF fixture, native outputs and suffix reuse."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml

HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def digest(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')


def main():
    results=[];summary=[]
    for p in sorted((HERE/'cases').glob('*/result.json')):
        r=read(p);models=read(p.parent/'models.json')
        assert r['error'] is None and r['status']=='OPTIMAL' and r['all_constraints_pass'] and r['graph_audit']['pass_all']
        assert len(models)==1 and models[0]['optimize_max_seconds']==60
        assert max(x['violation'] for x in models[0]['constraints'])<1e-5
        assert all(v['value'] is not None for v in models[0]['variables'])
        results.append(r)
        summary.append(dict(case=r['name'],status=r['status'],objective=r['objective'],
            vertices=r['graph_audit']['full_vertex_count'],type2=r['graph_audit']['full_type2_count'],
            changed_groups=len(r['graph_audit']['changed_groups']),solver_seconds=models[0]['solver_wall_seconds'],
            author_wall_seconds=r['author_wall_seconds'],rows=models[0]['num_rows'],cols=models[0]['num_cols'],
            binary_vars=sum(x['type']=='B' for x in models[0]['variables']),max_seconds=60,
            production_cost=None))
    assert len(results)==12 and sum(x['actual_author_calls'] for x in results)==12
    write(HERE/'ALL_RESULTS.json',results)
    with (HERE/'SUMMARY.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
    solution=yaml.safe_load((HERE/'official_ecbs_solution.yaml').read_text())
    prob=yaml.safe_load((SOURCE/'sadg_controller/data/ecbs/test.yaml').read_text())
    schedules=solution['schedule'];T=max(max(x['t'] for x in v) for v in schedules.values())
    obstacles={tuple(x) for x in prob['map']['obstacles']};d=prob['map']['dimensions'];checks=0
    def at(agent,t):
        path=schedules[agent];return next(((x['x'],x['y']) for x in path if x['t']==min(t,path[-1]['t'])))
    for a in prob['agents']:
        assert list(at(a['name'],0))==a['start'] and list(at(a['name'],T))==a['goal']
    for t in range(T+1):
        for a in schedules:
            xy=at(a,t);assert xy not in obstacles and 0<=xy[0]<d[0] and 0<=xy[1]<d[1]
            if t:assert sum(abs(x-y) for x,y in zip(xy,at(a,t-1)))<=1
        for i,a in enumerate(schedules):
            for b in list(schedules)[i+1:]:
                assert at(a,t)!=at(b,t)
                if t:assert not(at(a,t)==at(b,t-1) and at(b,t)==at(a,t-1))
                checks+=1
    def execution_key(case):
        g=read(HERE/'cases'/case/'graph_after.json')
        return digest(dict(vertices=[{k:v[k] for k in ['uid','agent','index','path_tuples','status']} for v in g['vertices']],
            type1=g['type1'],type2=sorted(d['active'] for group in g['groups'] for d in group['dependencies']),
            true_progress={'agent0':.25,'agent1':.5},actual_future_duration=1.,actual_move_speed=2.,
            executor_sha256=sha(HERE/'replay_suffix.py'),clock='event_completion_then_dispatch'))
    suffixes={execution_key(n):n for n in ['mini_public_elapsed','mini_measured']}
    reuse=[]
    for n in ['mini_public_elapsed','mini_public_history','mini_measured','mini_public_history_rate','mini_measured_history_rate']:
        key=execution_key(n);src=suffixes[key];r=read(HERE/'suffix'/f'{src}.json')
        reuse.append(dict(case=n,execution_key=key,source_suffix=src,
            source_sha256=sha(HERE/'suffix'/f'{src}.json'),sum_completion_time=r['sum_completion_time'],makespan=r['makespan']))
    write(HERE/'SUFFIX_REUSE.json',dict(unique_executions=2,models_not_execution_durations=True,records=reuse))
    guards=[read(HERE/'cases'/n/'original_guard_audit.json') for n in ['warehouse_public_patched','warehouse_measured_patched']]
    assert all(g['original_R13_adoption_guard_pass'] and g['satisfied_directions_preserved'] for g in guards)
    assert guards[0]['candidate_sha256']==guards[1]['candidate_sha256']
    status=subprocess.check_output(['rtk','proxy','git','-C',str(SOURCE),'status','--porcelain'],text=True)
    assert status==''
    freeze=subprocess.check_output([sys.executable,'-I','-m','pip','freeze'],text=True)
    (HERE/'requirements.lock').write_text(freeze)
    write(HERE/'FINAL_AUDIT.json',dict(author_calls=12,failed_instrumentation_calls_before_optimizer=7,
        failed_instrumentation_actual_optimizer_calls=0,source_checkout_clean=True,all_solver_constraints_pass=True,
        all_graph_audits_pass=True,official_MAPF_pair_checks=checks,official_MAPF_full_valid=True,
        unique_suffix_executions=2,warehouse_same_candidate=True,warehouse_old_suffix_reexecutions=0,
        historical_same_model_POSITION_sum_gain=0.0,historical_same_model_POSITION_makespan_gain=0.0,
        scope='Local self-audit. Root independent audit is separate. No statistical generalization or production cost.'))
    print(json.dumps(read(HERE/'FINAL_AUDIT.json')))


if __name__=='__main__':main()
