#!/usr/bin/env python3
"""Zero-solver lifecycle/privacy/transport/guard checks for the R18 engine."""
import copy
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from engine import Simulator,EngineConfig,DensePositionPolicy,NoQueryPolicy,adoption_guard,write_json


def main():
    straight=dict(case_id='one_move_transport',solution={'schedule':{
        'agent0':[dict(x=0,y=0,t=0),dict(x=1,y=0,t=1)]}})
    received=[]
    class Spy(DensePositionPolicy):
        def __call__(self,snapshot):
            received.append(copy.deepcopy(snapshot))
            return super().__call__(snapshot)
    drained=Simulator(straight,config=EngineConfig(solve_period=.9,query_latency=.25,max_time=10)).run(Spy())
    assert drained['success'] and drained['new_author_calls']==0
    assert abs(drained['makespan']-1)<1e-9 and abs(drained['simulation_end']-1.15)<1e-9
    assert drained['queries'][0]['delivery_status']=='stale_occurrence' and drained['pending_queries_after_transport']==0
    assert any(s['kind']=='GOAL_HOLD' and s['t1']>1 for s in drained['segments'])
    assert all(k not in str(received) for k in ['disturbance','private_truth','world_geometry_binding','case_id','seed'])
    assert received[0]['agents'][0]['history_count']==0 and received[0]['agents'][0]['history_ratio']==1
    truncated=Simulator(straight,{'kind':'stable','stable_factor':.1},config=EngineConfig(max_time=.5)).run(NoQueryPolicy())
    assert truncated['status']=='truncated' and truncated['sum_completion'] is None
    assert truncated['restricted_sum_completion']==.5 and truncated['completed_agents']==0
    missed=Simulator(straight,config=EngineConfig()).run(NoQueryPolicy(),probe_override={99:[]})
    assert missed['success'] and missed['unreached_probe_gates']==[99] and missed['new_author_calls']==0
    altered=copy.deepcopy(missed['initial_graph']);altered['vertices'][0]['status']='COMPLETED'
    assert not adoption_guard(missed['initial_graph'],altered)['passed']
    rejected=False
    try:
        Simulator({'schedule':{'agent0':[dict(x=0,y=0,t=0),dict(x=1,y=1,t=1)]}})
    except ValueError as exc:rejected='cardinal' in str(exc)
    assert rejected
    for name,result in [('transport_drain',drained),('common_horizon_truncation',truncated),('unreached_probe',missed)]:
        write_json(HERE/'engine_smoke'/'units'/f'{name}.json',result)
    write_json(HERE/'engine_smoke'/'UNIT_RESULTS.json',dict(passed=True,new_author_calls=0,
        checks=['transport_drain_after_last_END','goal_residence_during_transport','stale_occurrence_no_successor_update',
                'policy_public_fields_only','history_absence_explicit','common_H_restricted_sum','unreached_probe_retained',
                'guard_rejects_vertex_status_change','noncardinal_shortcut_rejected']))
    print('9 engine boundary checks passed; zero author solver calls')


if __name__=='__main__':main()
