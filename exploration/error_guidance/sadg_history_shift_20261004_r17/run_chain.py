#!/usr/bin/env python3
"""Frozen synthetic capture/history adapter around the unchanged author SADG.

The public predictor never receives world truth. Capture and suffix modules do.
R16 complete solver inputs/results may be reused after full graph equality.
"""
import argparse
import copy
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'sadg_preflight_20261004_r16'
spec = importlib.util.spec_from_file_location('r16_core', OLD / 'run_preflight.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
c.HERE = HERE
sys.path.insert(0, str(OLD / 'isolated_patch'))
spec = importlib.util.spec_from_file_location('r16_compiler_patch', OLD / 'isolated_patch/compiler.py')
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


def load(path):
    return json.loads(Path(path).read_text())


def write_once(path, obj):
    path = Path(path)
    if path.exists():
        assert load(path) == obj, 'refuse changed frozen file: ' + str(path)
    else:
        c.dump(path, obj)


def q(x):
    return str(F(x))


def actual_prefix(world, at):
    """Integrate only segments ending at/before actual capture, never future."""
    at = F(at)
    out = F(0)
    for part in world['A_prefix_segments']:
        left = F(part['start'])
        if at <= left:
            break
        right = min(at, F(part['end']))
        out += (right-left)*F(part['rate'])
    return out


def predict(public, evidence=None):
    """Whitelisted input interface: no scene label, world profile or decision q."""
    now = F(public['decision_time'])
    hist = {}
    for aid in ['agent0', 'agent1']:
        events = [x for x in public['completed_history'] if x['agent'] == aid]
        assert events and all(F(e['delivered']) <= now for e in events)
        # All available completed distance/time history; no selective last sample.
        hist[aid] = sum(F(e['end'])-F(e['start']) for e in events) / sum(
            F(e['length']) for e in events) * F(public['action_length'])
    progress = {aid: min(F(1), (now-F(start))/hist[aid])
                for aid, start in public['current_start'].items()}
    projection = None
    if evidence is not None:
        assert evidence['world_binding'] == public['world_binding']
        assert evidence['agent'] == 'agent0' and evidence['occurrence'] == 'v_0_1'
        assert F(evidence['delivered']) == now and F(evidence['captured']) <= now
        p = F(evidence['progress'])
        age = now-F(evidence['captured'])
        assert 0 <= p <= 1
        progress['agent0'] = min(F(1), p+age/hist['agent0'])
        projection = dict(captured=evidence['captured'], delivered=q(now), age=q(age),
            lower=q(p), upper=q(min(F(1), p+age*F(public['max_progress_rate']))),
            point=q(progress['agent0']), finite_completion_upper=False,
            safety_authority=False)
    return dict(progress={k:float(v) for k,v in progress.items()},
        durations={k:float(v) for k,v in hist.items()}, projection=projection,
        public_sha256=c.key(public), evidence_sha256=c.key(evidence) if evidence else None,
        estimator='all_completed_distance_time_history_plus_optional_capture_age')


def register():
    paths = c.small_schedule()
    public = dict(world_binding=c.key(dict(paths=paths, length=2, max_progress_rate=1)),
        decision_time='3/4', action_length='2', max_progress_rate='1',
        current_start={'agent0':'0', 'agent1':'1/4'},
        completed_history=[
            dict(agent='agent0', occurrence='v_0_0', start='-1', end='0', delivered='0', length='2'),
            dict(agent='agent1', occurrence='v_1_0', start='-3/4', end='1/4', delivered='1/4', length='2')],
        delivered_end_for_current=False)
    write_once(HERE/'public.json', public)
    worlds = {
        'stable': dict(A_prefix_segments=[dict(start='0',end='3/4',rate='1')], suffix_rate='1'),
        'short_stop': dict(A_prefix_segments=[dict(start='0',end='1/2',rate='0'),
                                            dict(start='1/2',end='3/4',rate='1')], suffix_rate='1'),
        'speed_shift': dict(A_prefix_segments=[dict(start='0',end='3/4',rate='1/2')], suffix_rate='1/2')}
    records = []
    for scene, world in worlds.items():
        world = dict(world, agent_B_rate='1', world_binding=public['world_binding'],
                     truth_scope='synthetic piecewise affine execution; no ROS/controller claim')
        write_once(HERE/'worlds'/f'{scene}.json', world)
        for arm, age in [('public_history', None), ('position_age0', F(0)), ('position_age025', F(1,4))]:
            evidence = None
            if age is not None:
                captured = F(public['decision_time'])-age
                evidence = dict(world_binding=public['world_binding'], agent='agent0', occurrence='v_0_1',
                    captured=q(captured), delivered=public['decision_time'],
                    progress=q(actual_prefix(world, captured)), cap='1',
                    source_kind='simulated_position_capture_not_production_AUTH',
                    observed_prefix=[dict(start=s['start'],end=q(min(captured,F(s['end']))),rate=s['rate'])
                        for s in world['A_prefix_segments'] if F(s['start']) < captured])
                # Encoder deliberately strips the private segment explanation.
                body = {k:v for k,v in evidence.items() if k != 'observed_prefix'}
                write_once(HERE/'captures'/f'{scene}_{arm}.json', evidence)
            else:
                body = None
            predicted = predict(public, body)
            name = f'{scene}_{arm}'
            inp = dict(name=name, solution=paths,
                dimensions={'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}},
                active_indices={'agent0':1,'agent1':1}, horizon=5.0,
                progress=predicted['progress'], duration_model=predicted['durations'],
                prediction=predicted, compiler_variant='isolated_k0_plus_all_heads',
                data_class='registered_synthetic_mechanism_R17', production_cost=None,
                optimizer_unchanged=True, runner_sha256=c.sha(__file__))
            write_once(HERE/'inputs'/f'{name}.json', inp)
            records.append(dict(name=name, scene=scene, arm=arm, input_sha256=c.sha(HERE/'inputs'/f'{name}.json')))
    write_once(HERE/'REGISTRATION.json', dict(protocol_sha256=c.sha(HERE/'PROTOCOL.md'),
        runner_sha256=c.sha(__file__), author_commit=c.PIN,
        optimizer_sha256=c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/sadg.py'),
        compiler_hashes={n:c.sha(OLD/'isolated_patch'/n) for n in ['compiler.py','r16_guard_group.py']},
        author_max_seconds=60, outer_alarm_seconds=90, max_new_author_calls=6,
        max_new_suffixes=6, cases=records, public_sha256=c.sha(HERE/'public.json'),
        world_sha256={s:c.sha(HERE/'worlds'/f'{s}.json') for s in worlds},
        completed_before_any_new_solve=True))
    c.source_manifest()
    print(json.dumps(dict(registered=len(records), max_calls=6, max_suffixes=6)))


def graph_for(inp):
    graph = pc.compile_sadg(c.Plan(inp['solution'], inp['dimensions']), c.LOG)
    for aid, idx in inp['active_indices'].items():
        for i,v in enumerate(graph.vertices_by_agent[aid]):
            v.set_status(c.Status.COMPLETED if i < idx else c.Status.IN_PROGRESS if i == idx else c.Status.STAGED)
            if i >= idx:
                v.expected_completion_time *= inp['duration_model'][aid]
        p = inp['progress'][aid]
        graph.vertices_by_agent[aid][idx].get_progress = types.MethodType(lambda self, value=p:value,
                                                                       graph.vertices_by_agent[aid][idx])
    return graph


def graph_semantics(snap):
    # Full pre-solve object, including each head's switchability/horizon predicate.
    return c.key(snap)


def execution_graph(snap):
    # Optimizer estimates must never become execution duration truth.
    return dict(vertices=[{k:v[k] for k in ['uid','agent','index','status','path_tuples','predecessor','successor']}
                          for v in snap['vertices']], type1=snap['type1'],
        type2=sorted([d['active'] for g in snap['groups'] for d in g['dependencies']]))


def solve_or_reuse(name, previous):
    inp=load(HERE/'inputs'/f'{name}.json')
    graph=graph_for(inp)
    before=c.snapshot(graph,inp['horizon'])
    target_key=graph_semantics(before)
    out=HERE/'cases'/name
    assert not (out/'result.json').exists(), 'already processed, use summary (no reruns)'
    candidates=[OLD/'cases'/n for n in [
        'mini_public_elapsed','mini_measured','mini_stub','mini_public_history',
        'mini_low_progress','mini_high_progress','mini_public_history_rate','mini_measured_history_rate']]
    candidates += [HERE/'cases'/n for n in previous]
    result=None
    for candidate in candidates:
        if not (candidate/'graph_before.json').exists():
            continue
        if graph_semantics(load(candidate/'graph_before.json')) != target_key:
            continue
        old=load(candidate/'result.json')
        assert old['status']=='OPTIMAL' and old['all_constraints_pass']
        after=load(candidate/'graph_after.json')
        c.dump(out/'graph_before.json',before)
        c.dump(out/'graph_after.json',after)
        result=dict(old, name=name, actual_author_calls=0,
            reused_from=str(candidate.relative_to(HERE.parent)), reuse_source_result_sha256=c.sha(candidate/'result.json'),
            same_complete_input_semantics_sha256=target_key, graph_audit=c.structure_audit(before,after),
            source_optimizer_sha256=c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/sadg.py'),
            model_source=str(candidate.relative_to(HERE.parent)), new_solver_work_seconds=0,
            note='Reused exact complete author graph input; original elapsed time remains historical, not new cost.')
        c.dump(out/'result.json',result)
        break
    if result is None:
        def compile_duration(plan,logger):
            g=pc.compile_sadg(plan,logger)
            for aid,idx in inp['active_indices'].items():
                for i,v in enumerate(g.vertices_by_agent[aid]):
                    if i >= idx: v.expected_completion_time *= inp['duration_model'][aid]
            return g
        c.compile_sadg=compile_duration
        result=c.solve(name)
        result['same_complete_input_semantics_sha256']=target_key
        result['source_optimizer_sha256']=c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/sadg.py')
        result['new_solver_work_seconds']=sum(m['solver_wall_seconds'] for m in load(out/'models.json'))
        c.dump(out/'result.json',result)
    assert result['graph_audit']['pass_all'] and result['all_constraints_pass']
    after=load(out/'graph_after.json')
    # Common adoption guard sees commitments and candidate graph, never truth.
    committed=[v['uid'] for v in before['vertices'] if v['status']=='IN_PROGRESS']
    assert committed==[v['uid'] for v in after['vertices'] if v['status']=='IN_PROGRESS']
    after_vertices={v['uid']:v for v in after['vertices']}
    added=set(map(tuple,execution_graph(after)['type2']))-set(map(tuple,execution_graph(before)['type2']))
    assert all(after_vertices[head]['status']=='STAGED' for _,head in added)
    c.dump(out/'adoption_guard.json',dict(pass_all=True, active_commitments=committed,
        added_dependencies=sorted(added), candidate_execution_graph_sha256=c.key(execution_graph(after)),
        same_common_guard=True, uses_private_truth=False, audit=result['graph_audit'],
        scope='Full author DAG/relations plus immutable active commitment; point execution verified separately'))
    return result


def exact_geometry_audit(segments, makespan):
    # Wait and goal holds are present; exact rational distance minimization.
    pairs=0; minimum=None; collisions=[]
    def at(s,t):
        f=(t-F(s['t0']))/(F(s['t1'])-F(s['t0']))
        return [F(x)+f*(F(y)-F(x)) for x,y in zip(s['p0'],s['p1'])]
    for aid in ['agent0','agent1']:
        ordered=sorted([s for s in segments if s['agent']==aid],key=lambda s:F(s['t0']))
        assert F(ordered[0]['t0'])==0 and F(ordered[-1]['t1'])==makespan
        for a,b in zip(ordered,ordered[1:]):
            assert a['t1']==b['t0'] and a['p1']==b['p0']
    for i,a in enumerate(segments):
        for b in segments[i+1:]:
            if a['agent']==b['agent']:continue
            lo=max(F(a['t0']),F(b['t0']));hi=min(F(a['t1']),F(b['t1']))
            if lo>hi:continue
            pairs+=1;d=[x-y for x,y in zip(at(a,lo),at(b,lo))]
            va=[(F(y)-F(x))/(F(a['t1'])-F(a['t0'])) for x,y in zip(a['p0'],a['p1'])]
            vb=[(F(y)-F(x))/(F(b['t1'])-F(b['t0'])) for x,y in zip(b['p0'],b['p1'])]
            dv=[x-y for x,y in zip(va,vb)];n=sum(x*x for x in dv)
            dt=max(F(0),min(hi-lo,-sum(x*y for x,y in zip(d,dv))/n)) if n else F(0)
            squared=sum((x+dt*y)**2 for x,y in zip(d,dv))
            minimum=squared if minimum is None else min(minimum,squared)
            if squared==0:collisions.append(dict(a=a['agent'],b=b['agent'],t=q(lo+dt)))
    return dict(full_wait_goal_coverage=True, overlap_pairs=pairs,
        minimum_squared_point_distance=q(minimum), point_collisions=collisions,
        certified_footprint_or_controller_safety=False)


def replay(inp, saved, state):
    g=graph_for(inp)
    for groups in g.switchable_dep_groups.values():
        for group in groups:
            target=next(t for t in saved['groups'] if t['uid']==group.get_uid())
            bits=[d['b'] for d in target['dependencies']]
            assert len(set(bits))==1
            if bits[0]:group.switch()
    current={};active={};pos={};last_end={};events=[];segments=[];finished={};now=F(0)
    def segment(aid,v,t0,t1,p0,p1,kind):
        if t0==t1:return
        segments.append(dict(agent=aid,vertex=v.get_shorthand(),t0=q(t0),t1=q(t1),
                             p0=list(map(q,p0)),p1=list(map(q,p1)),kind=kind))
    for aid,vs in g.vertices_by_agent.items():
        v=vs[inp['active_indices'][aid]];current[aid]=v
        p=F(state['progress'][aid]);s=v.get_start_loc();goal=v.get_goal_loc()
        pos[aid]=[F(s.x)+p*F(goal.x-s.x),F(s.y)+p*F(goal.y-s.y)]
        duration=(1-p)/F(state['rate'][aid]);active[aid]=duration;last_end[aid]=now
        segment(aid,v,now,duration,pos[aid],[goal.x,goal.y],'COMMITTED_REMAINDER')
        events.append(dict(t='0',kind='RESUME_COMMITTED',agent=aid,vertex=v.get_shorthand(),remaining=q(duration)))
    while len(finished)<len(current):
        for aid,v in current.items():
            if aid in active or aid in finished:continue
            if v.get_status()==c.Status.STAGED and v.can_execute():
                deps=[d.get_tail().get_shorthand() for d in v.get_dependencies() if d.is_active()]
                assert all(d.get_tail().get_status()==c.Status.COMPLETED for d in v.get_dependencies() if d.is_active())
                segment(aid,v,last_end[aid],now,pos[aid],pos[aid],'WAIT')
                v.set_status(c.Status.IN_PROGRESS)
                duration=1/F(state['rate'][aid]);active[aid]=now+duration;goal=v.get_goal_loc()
                segment(aid,v,now,now+duration,pos[aid],[goal.x,goal.y],'MOVE')
                events.append(dict(t=q(now),kind='START',agent=aid,vertex=v.get_shorthand(),active_dependency_tails=deps))
        assert active,'deadlock'
        now=min(active.values())
        for aid in [a for a,t in active.items() if t==now]:
            v=current[aid];v.set_status(c.Status.COMPLETED);del active[aid]
            goal=v.get_goal_loc();pos[aid]=[goal.x,goal.y];last_end[aid]=now
            events.append(dict(t=q(now),kind='COMPLETE',agent=aid,vertex=v.get_shorthand()))
            if v.has_next():current[aid]=v.get_next()
            else:finished[aid]=now
    for aid,v in current.items():segment(aid,v,last_end[aid],now,pos[aid],pos[aid],'GOAL_HOLD')
    audit=exact_geometry_audit(segments,now)
    assert not audit['point_collisions']
    return dict(completed_agents=len(finished), completion_times={a:q(t) for a,t in finished.items()},
        sum_completion_time=float(sum(finished.values())),makespan=float(now),events=events,segments=segments,
        collision_audit=audit,truth_state=state,production_cost=None,
        data_class='synthetic_event_execution_author_can_execute_no_ROS',
        author_vertex_sha256=c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/vertex.py'))


def run():
    reg=load(HERE/'REGISTRATION.json')
    assert reg['runner_sha256']==c.sha(__file__) and reg['protocol_sha256']==c.sha(HERE/'PROTOCOL.md')
    assert reg['optimizer_sha256']==c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/sadg.py')
    results=[];completed=[];suffix_cache={};rows=[];new_calls=0;new_suffixes=0
    # Reuse R16 only if the entire execution graph and actual state are equal.
    legacy_state=dict(progress={'agent0':'1/4','agent1':'1/2'},rate={'agent0':'1','agent1':'1'})
    for name in ['mini_public_elapsed','mini_measured']:
        path=OLD/'suffix'/f'{name}.json';saved=load(OLD/'cases'/name/'graph_after.json')
        key=c.key(dict(graph=execution_graph(saved),state=legacy_state))
        suffix_cache[key]=dict(path=str(path.relative_to(HERE.parent)),sha256=c.sha(path),result=load(path),reused_R16=True)
    for record in reg['cases']:
        name=record['name'];inp=load(HERE/'inputs'/f'{name}.json')
        assert c.sha(HERE/'inputs'/f'{name}.json')==record['input_sha256']
        result=solve_or_reuse(name,completed);completed.append(name);results.append(result)
        new_calls+=result['actual_author_calls'];assert new_calls<=reg['max_new_author_calls']
        saved=load(HERE/'cases'/name/'graph_after.json')
        world=load(HERE/'worlds'/f'{record["scene"]}.json')
        truth=actual_prefix(world,F(3,4))
        state=dict(progress={'agent0':q(truth),'agent1':'1/2'},rate={'agent0':world['suffix_rate'],'agent1':'1'})
        execution_key=c.key(dict(graph=execution_graph(saved),state=state))
        if execution_key not in suffix_cache:
            assert new_suffixes<reg['max_new_suffixes']
            suffix=replay(inp,saved,state);path=HERE/'suffix'/f'{execution_key}.json'
            c.dump(path,suffix);new_suffixes+=1
            suffix_cache[execution_key]=dict(path=str(path.relative_to(HERE.parent)),sha256=c.sha(path),result=suffix,reused_R16=False)
        entry=suffix_cache[execution_key];suffix=entry['result']
        c.dump(HERE/'cases'/name/'suffix_receipt.json',dict(execution_key=execution_key,
            source=entry['path'],source_sha256=entry['sha256'],reused_R16=entry['reused_R16'],
            actual_state=state,graph_key=c.key(execution_graph(saved))))
        estimated=F(str(inp['progress']['agent0']))
        actual_remaining=(1-truth)/F(world['suffix_rate'])
        predicted_remaining=(1-estimated)*F(str(inp['duration_model']['agent0']))
        proj=inp['prediction']['projection']
        if proj:assert F(proj['lower'])<=truth<=F(proj['upper'])
        direction='B_first' if any(d['b'] for g in saved['groups'] for d in g['dependencies']) else 'A_first'
        rows.append(dict(scene=record['scene'],arm=record['arm'],name=name,
            A_true_progress=float(truth),A_predicted_progress=float(estimated),
            progress_absolute_error=float(abs(estimated-truth)),
            A_true_remaining=float(actual_remaining),A_predicted_remaining=float(predicted_remaining),
            remaining_absolute_error=float(abs(predicted_remaining-actual_remaining)),
            direction=direction,objective=result['objective'],solver_status=result['status'],
            new_author_calls=result['actual_author_calls'],
            new_solver_work_seconds=result.get('new_solver_work_seconds'),
            model_reused_from=result.get('reused_from'),
            graph_key=c.key(execution_graph(saved)),guard_pass=True,
            sum_completion_time=suffix['sum_completion_time'],makespan=suffix['makespan'],
            execution_key=execution_key,suffix_reused_R16=entry['reused_R16'],
            query_count=0 if record['arm']=='public_history' else 1,
            measurement_age=None if proj is None else float(F(proj['age'])),production_cost=None))
        c.dump(HERE/'PROGRESS.json',dict(completed=completed,new_calls=new_calls,new_suffixes=new_suffixes))
    for row in rows:
        baseline=next(r for r in rows if r['scene']==row['scene'] and r['arm']=='public_history')
        row['sum_gain_vs_public']=baseline['sum_completion_time']-row['sum_completion_time']
        row['makespan_gain_vs_public']=baseline['makespan']-row['makespan']
        row['graph_differs_from_public']=row['graph_key']!=baseline['graph_key']
    c.dump(HERE/'RESULTS.json',dict(rows=rows,new_unique_author_calls=new_calls,
        new_unique_suffixes=new_suffixes,all_constraints_and_guards_pass=True,
        optimizer_unchanged=True,production_cost=None,scope='fixed_path_single_decision_not_LMAPF_throughput'))
    import csv
    with (HERE/'SUMMARY.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(new_calls=new_calls,new_suffixes=new_suffixes,rows=rows),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','run'])
    args=parser.parse_args()
    register() if args.action=='register' else run()
