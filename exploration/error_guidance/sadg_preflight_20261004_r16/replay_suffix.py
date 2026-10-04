#!/usr/bin/env python3
"""Event adapter using original Vertex.can_execute / status / next methods."""
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r16_core',HERE/'run_preflight.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def replay(case):
    inp=json.loads((HERE/'inputs'/f'{case}.json').read_text())
    saved=json.loads((HERE/'cases'/case/'graph_after.json').read_text())
    g=c.compile_sadg(c.Plan(inp['solution'],inp['dimensions']),c.LOG)
    for gs in g.switchable_dep_groups.values():
        for group in gs:
            target=next(t for t in saved['groups'] if t['uid']==group.get_uid())
            bits=[x['b'] for x in target['dependencies']]
            assert len(set(bits))==1
            if bits[0]: group.switch()
    current={};active={};positions={};last_end={};events=[];segments=[];finished={};time=0.0
    true_progress={'agent0':.25,'agent1':.5}
    for aid,vs in g.vertices_by_agent.items():
        idx=inp['active_indices'][aid]
        for i,v in enumerate(vs):
            v.set_status(c.Status.COMPLETED if i<idx else c.Status.IN_PROGRESS if i==idx else c.Status.STAGED)
        v=vs[idx];current[aid]=v
        start=v.get_start_loc();goal=v.get_goal_loc();p=true_progress[aid]
        positions[aid]=[start.x+p*(goal.x-start.x),start.y+p*(goal.y-start.y)]
        duration=(1-p)*v.get_expected_completion_time();active[aid]=duration;last_end[aid]=0.0
        segments.append(dict(agent=aid,vertex=v.get_shorthand(),t0=0.,t1=duration,p0=positions[aid],p1=[goal.x,goal.y],kind='COMMITTED_REMAINDER'))
        events.append(dict(t=0.,kind='RESUME_COMMITTED',agent=aid,vertex=v.get_shorthand(),true_progress=p,remaining=duration))
    while len(finished)<len(current):
        for aid,v in current.items():
            if aid in active or aid in finished:continue
            if v.get_status()==c.Status.STAGED and v.can_execute():
                deps=[d.get_tail().get_shorthand() for d in v.get_dependencies() if d.is_active()]
                assert all(d.get_tail().get_status()==c.Status.COMPLETED for d in v.get_dependencies() if d.is_active())
                if time>last_end[aid]:
                    segments.append(dict(agent=aid,vertex=v.get_shorthand(),t0=last_end[aid],t1=time,p0=positions[aid],p1=positions[aid],kind='WAIT'))
                v.set_status(c.Status.IN_PROGRESS);duration=v.get_expected_completion_time();active[aid]=time+duration
                goal=v.get_goal_loc()
                segments.append(dict(agent=aid,vertex=v.get_shorthand(),t0=time,t1=time+duration,p0=positions[aid],p1=[goal.x,goal.y],kind='MOVE'))
                events.append(dict(t=time,kind='START',agent=aid,vertex=v.get_shorthand(),active_dependency_tails=deps))
        assert active,'deadlock'
        time=min(active.values())
        due=[a for a,t in active.items() if abs(t-time)<1e-12]
        for aid in due:
            v=current[aid];v.set_status(c.Status.COMPLETED);del active[aid]
            goal=v.get_goal_loc();positions[aid]=[goal.x,goal.y];last_end[aid]=time
            events.append(dict(t=time,kind='COMPLETE',agent=aid,vertex=v.get_shorthand()))
            if v.has_next():current[aid]=v.get_next()
            else:finished[aid]=time
    for aid in current:
        if last_end[aid]<time:
            segments.append(dict(agent=aid,vertex=current[aid].get_shorthand(),t0=last_end[aid],t1=time,p0=positions[aid],p1=positions[aid],kind='GOAL_HOLD'))
    # All pairs of simultaneous continuous affine segments, including waits/holds.
    checks=0;min_distance=math.inf;collisions=[]
    def at(s,t):
        f=(t-s['t0'])/(s['t1']-s['t0'])
        return [x+f*(y-x) for x,y in zip(s['p0'],s['p1'])]
    for i,a in enumerate(segments):
        for b in segments[i+1:]:
            if a['agent']==b['agent']:continue
            lo=max(a['t0'],b['t0']);hi=min(a['t1'],b['t1'])
            if lo>hi:continue
            checks+=1;pa=at(a,lo);pb=at(b,lo)
            delta=[x-y for x,y in zip(pa,pb)]
            va=[(y-x)/(a['t1']-a['t0']) for x,y in zip(a['p0'],a['p1'])]
            vb=[(y-x)/(b['t1']-b['t0']) for x,y in zip(b['p0'],b['p1'])]
            dv=[x-y for x,y in zip(va,vb)];norm=sum(x*x for x in dv)
            tau=max(0,min(hi-lo,-sum(x*y for x,y in zip(delta,dv))/norm)) if norm else 0
            distance=math.sqrt(sum((x+tau*y)**2 for x,y in zip(delta,dv)))
            min_distance=min(min_distance,distance)
            if distance<1e-8:collisions.append(dict(a=a,b=b,t=lo+tau))
    result=dict(case=case,source_graph_sha256=c.sha(HERE/'cases'/case/'graph_after.json'),
        true_progress=true_progress,completed_agents=len(finished),completion_times=finished,
        sum_completion_time=sum(finished.values()),makespan=time,events=events,segments=segments,
        collision_audit=dict(all_cross_agent_overlap_pairs=checks,min_point_distance=min_distance,collisions=collisions),
        author_can_execute_file=c.inspect.getfile(c.compile_sadg).replace('compiler.py','vertex.py'),
        data_class='synthetic_event_adapter_on_author_graph',production_cost=None,
        semantics='All author statuses and active type2 dependencies; event dispatch, not 2-second ROS timer; point geometry only.')
    c.dump(HERE/'suffix'/f'{case}.json',result)
    return result


def main():
    # Two unique graphs; historical/public arms are graph-identical and share suffix.
    names=['mini_public_elapsed','mini_measured']
    rs=[replay(n) for n in names]
    summary=[{k:r[k] for k in ['case','true_progress','completion_times','sum_completion_time','makespan','collision_audit']} for r in rs]
    c.dump(HERE/'SUFFIX_RESULTS.json',dict(unique_suffix_runs=2,results=summary,
        elapsed_vs_measured_sum_gain=rs[0]['sum_completion_time']-rs[1]['sum_completion_time'],
        elapsed_vs_measured_makespan_gain=rs[0]['makespan']-rs[1]['makespan'],
        public_history_suffix_reused='mini_public_elapsed',cost=None))
    print(json.dumps(summary))


if __name__=='__main__':main()
