#!/usr/bin/env python3
"""Read-only artifact audit: zero author solves and zero suffix executions."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent


def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',', ':')).encode()).hexdigest()


def main():
    reg=load(HERE/'REGISTRATION.json');summary=load(HERE/'RESULTS.json');public=load(HERE/'public.json')
    assert sha(HERE/'PROTOCOL.md')==reg['protocol_sha256']
    assert sha(HERE/'run_chain.py')==reg['runner_sha256']
    assert sha(HERE/'public.json')==reg['public_sha256']
    for name,h in reg['world_sha256'].items():assert sha(HERE/'worlds'/f'{name}.json')==h
    records=[];model_paths=set();suffix_paths=set();new_calls=0
    for rec in reg['cases']:
        name=rec['name'];case=HERE/'cases'/name
        inp=load(HERE/'inputs'/f'{name}.json');r=load(case/'result.json')
        assert sha(HERE/'inputs'/f'{name}.json')==rec['input_sha256']
        assert r['all_constraints_pass'] and r['graph_audit']['pass_all'] and r['status']=='OPTIMAL'
        assert load(case/'adoption_guard.json')['pass_all']
        new_calls+=r['actual_author_calls']
        model_case=case;model_result=r
        while 'reused_from' in model_result:
            previous=BASE/model_result['reused_from']
            assert sha(previous/'result.json')==model_result['reuse_source_result_sha256']
            assert load(previous/'graph_before.json')==load(case/'graph_before.json')
            assert load(previous/'graph_after.json')==load(case/'graph_after.json')
            model_case=previous;model_result=load(previous/'result.json')
        model_paths.add(str(model_case.relative_to(BASE)))
        models=load(model_case/'models.json');assert len(models)==1
        m=models[0];assert m['status']=='OPTIMAL' and m['optimize_max_seconds']==60
        values={v['name']:v['value'] for v in m['variables']}
        for row in m['constraints']:
            lhs=row['constant']+sum(co*values[var] for var,co in row['terms'].items())
            violation=max(0,lhs) if row['sense']=='<' else max(0,-lhs) if row['sense']=='>' else abs(lhs)
            assert violation<1e-5
        objective=m['objective_expression']['constant']+sum(co*values[var] for var,co in m['objective_expression']['terms'].items())
        assert abs(objective-r['objective'])<1e-6
        # Current boundary matches only authorized estimator values.
        for aid,index in [('agent0',0),('agent1',1)]:
            boundary=next(x for x in m['constraints'] if x['name']==f'boundary_v_{index}_1_g')
            expected=(1-inp['progress'][aid])*inp['duration_model'][aid]
            assert abs(boundary['constant']+expected)<1e-9
        truth=load(HERE/'worlds'/f'{rec["scene"]}.json')
        if rec['arm']!='public_history':
            cap=load(HERE/'captures'/f'{name}.json');t=F(cap['captured']);now=F(public['decision_time'])
            integrated=sum(max(F(0),min(t,F(s['end']))-F(s['start']))*F(s['rate'])
                           for s in truth['A_prefix_segments'])
            assert integrated==F(cap['progress'])
            age=F(0) if rec['arm']=='position_age0' else F(1,4)
            assert now-t==age
            history_duration=sum(F(e['end'])-F(e['start']) for e in public['completed_history'] if e['agent']=='agent0')
            assert F(str(inp['progress']['agent0']))==min(F(1),integrated+age/history_duration)
            assert 'observed_prefix' not in json.dumps(inp)
        receipt=load(case/'suffix_receipt.json');path=BASE/receipt['source'];suffix_paths.add(str(path.relative_to(BASE)))
        assert sha(path)==receipt['source_sha256'];suffix=load(path)
        assert suffix['completed_agents']==2
        completed={e['vertex'] for e in suffix['events'] if e['kind']=='COMPLETE'}
        assert len(completed)==12
        assert sum(F(str(x)) for x in suffix['completion_times'].values()) == F(str(suffix['sum_completion_time']))
        audit=suffix['collision_audit']
        assert not audit.get('point_collisions',audit.get('collisions'))
        records.append(dict(name=name,model_source=str(model_case.relative_to(BASE)),
            model_sha256=sha(model_case/'models.json'),suffix_source=str(path.relative_to(BASE)),
            suffix_sha256=sha(path),capture_age_checked=rec['arm']!='public_history',
            all_saved_constraint_rows_checked=True))
    assert new_calls==summary['new_unique_author_calls']==1
    out=dict(pass_all=True,registered_records=len(records),unique_model_artifacts=len(model_paths),
        unique_suffix_artifacts=len(suffix_paths),new_author_calls=1,new_suffixes=3,
        additional_optimizer_calls=0,additional_suffix_executions=0,records=records,
        auditor_scope='same-agent saved-output cross-check; parent independent audit separate')
    (HERE/'ARTIFACT_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))


if __name__=='__main__':main()
