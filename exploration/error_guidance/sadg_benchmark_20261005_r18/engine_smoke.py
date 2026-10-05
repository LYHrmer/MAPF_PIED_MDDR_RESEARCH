#!/usr/bin/env python3
"""Bounded structural pilots; not the benchmark matrix runner."""
import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from engine import Simulator,EngineConfig,NoQueryPolicy,DensePositionPolicy,write_json,continuous_collision_audit


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--standard-plan');args=parser.parse_args()
    out=HERE/'engine_smoke';out.mkdir(exist_ok=True)
    records=[]
    if args.standard_plan:
        raw=json.loads(Path(args.standard_plan).read_text())
        case=raw if 'solution' in raw else dict(case_id='structural_standard_TRAIN8',solution=raw,
                  dimensions={'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}})
        cases=[('standard_train8',case,{'kind':'bounded_pause','pause_duration':.25,'pause_probability':.2})]
    else:
        import yaml
        old=HERE.parent/'sadg_preflight_20261004_r16'
        official=dict(case_id='official_online_structural',
            solution=yaml.safe_load((old/'official_ecbs_solution.yaml').read_text()),
            dimensions=yaml.safe_load(Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9/sadg_controller/data/roadmaps/test/dimensions.yaml').read_text()))
        resident=dict(case_id='stationary_cursor',solution={'schedule':{
            'agent0':[dict(x=9,y=9,t=t) for t in range(4)],
            'agent1':[dict(x=t,y=0,t=t) for t in range(4)]}})
        cases=[('official',official,{'kind':'stable','stable_factor':.8}),
               ('resident',resident,{'kind':'bounded_pause','pause_duration':.3,'pause_fraction':.4})]
    for name,case,disturbance in cases:
        period=4. if name=='official' else 2.
        if args.standard_plan:
            times=[p['t'] for path in case['solution']['schedule'].values() for p in path]
            period=max(4.,max(times)/4.)  # Structural pilot deliberately <=~4 normal gates.
        cfg=EngineConfig(solve_period=period,query_latency=.25,max_time=1000.,
                         cache_dir=str(out/'cache'),output_dir=str(out/name),save_models=True,save_gate_graphs=True)
        result=Simulator(case,disturbance,12,config=cfg).run(DensePositionPolicy())
        summary={k:result[k] for k in ['status','success','completed_agents','agents','sum_completion','makespan',
                                     'solver_calls','new_author_calls','query_count','episode_wall_seconds','collision_audit','failures']}
        summary['name']=name;records.append(summary)
        print(json.dumps(summary))
        assert result['success'],name+' failed; receipt retained'
        for gate in result['gates']:
            assert 'case_id' not in gate['public_snapshot'] and 'private_truth' not in str(gate['public_snapshot'])
        for query in result['queries']:
            assert abs(query['delivered_at']-query['captured']-.25)<1e-9
        if name=='official':
            repeated=Simulator(case,disturbance,12,config=EngineConfig(**dict(cfg.__dict__,output_dir=str(out/'official_cache_repeat')))).run(DensePositionPolicy())
            assert repeated['success'] and repeated['new_author_calls']==0
            assert repeated['completion_times']==result['completion_times'] and repeated['queries']==result['queries']
            assert repeated['reference_solver_seconds']==result['reference_solver_seconds']
            records.append(dict(name='official_cache_repeat',success=True,new_author_calls=0))
        assert sum(r.get('new_author_calls',0) for r in records)<=12
    collision=continuous_collision_audit([
        dict(agent='a',t0=0,t1=2,p0=[0,0],p1=[0,0],kind='GOAL_HOLD'),
        dict(agent='b',t0=0,t1=2,p0=[-1,0],p1=[1,0],kind='MOVE')],{'a':[0,0],'b':[-1,0]},2)
    assert not collision['passed'] and collision['collisions']
    write_json(out/('STANDARD_SMOKE.json' if args.standard_plan else 'CORE_SMOKE.json'),
               dict(passed=True,records=records,goal_resident_collision_negative_passed=True))


if __name__=='__main__':main()
