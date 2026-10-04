#!/usr/bin/env python3
"""Author SADG preflight; no replacement optimizer or execution controller.

The native Model.optimize entry/return is profiled without replacement; input
progress is attached to individual Vertex instances only in named adapter arms.
"""
import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import inspect
import json
import logging
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
SOURCE = Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9')
sys.path.insert(0, str(SOURCE / 'sadg_controller'))
import mip
import networkx as nx
import yaml
from sadg_controller.mapf.plan import Plan
from sadg_controller.sadg.compiler import compile_sadg
from sadg_controller.sadg.status import Status

PIN = 'c2626d996121a9d6c128844a167b917db24418ac'
LOG = logging.getLogger('r16_author_core')
LOG.setLevel(logging.INFO)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')


def key(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def git(*args, cwd=SOURCE):
    return subprocess.check_output(['rtk', 'proxy', 'git', '-C', str(cwd), *args], text=True).strip()


def source_manifest():
    assert git('rev-parse', 'HEAD') == PIN
    files = git('ls-files').splitlines()
    hashes = {n: sha(SOURCE / n) for n in files if (SOURCE / n).is_file()}
    meta = dict(author_url='https://github.com/alexberndt/sadg-controller', commit=PIN,
                license='AGPL-3.0', source_files=hashes,
                submodule=git('submodule', 'status'), tracked_diff=git('diff', '--exit-code'),
                python=sys.version, executable=sys.executable, sys_path=sys.path,
                packages={d.metadata['Name']: d.version for d in importlib.metadata.distributions()},
                compile_sadg_file=inspect.getfile(compile_sadg),
                adapter_sha256=sha(__file__), ros_used=False, ros_shim_used=False)
    dump(HERE / 'SOURCE_ENVIRONMENT.json', meta)
    (HERE / 'AUTHOR_LICENSE').write_bytes((SOURCE / 'LICENSE').read_bytes())
    return meta


def small_schedule():
    # Native plan parser rotates and scales; this preserves distances/intersections.
    # A crosses first in this valid original MAPF schedule, B starts two ticks late.
    return {'schedule': {
        'agent0': [dict(x=x, y=0, t=i) for i, x in enumerate(range(-4, 4))],
        'agent1': [dict(x=0, y=y, t=i + 2) for i, y in enumerate(range(-4, 4))]}}


def register():
    dims = {'dimensions': {'resolution': 2.0, 'x_offset': 0.0, 'y_offset': 0.0}}
    base = dict(solution=small_schedule(), dimensions=dims, active_indices={'agent0': 1, 'agent1': 1},
                horizon=5.0, data_class='synthetic_mechanism_only', production_cost=None,
                observation={'decision_time': .75, 'move_starts': {'agent0': 0, 'agent1': .25},
                             'nominal_speed': 2.0, 'current_lengths': {'agent0': 2.0, 'agent1': 2.0},
                             'public_past_move_durations': {'agent0': [1.25], 'agent1': [1.0]},
                             'measured_progress': {'agent0': .25, 'agent1': .5},
                             'measurement_age': 0, 'hidden_future_used': False})
    variants = [('mini_stub', None), ('mini_public_elapsed', {'agent0': .75, 'agent1': .5}),
                ('mini_public_history', {'agent0': .6, 'agent1': .5}),
                ('mini_measured', {'agent0': .25, 'agent1': .5}),
                ('mini_low_progress', {'agent0': .05, 'agent1': .5}),
                ('mini_high_progress', {'agent0': .95, 'agent1': .5})]
    inputs = []
    for name, progress in variants:
        inputs.append(dict(base, name=name, progress=progress))
    # Official fixture exists before any SADG solve; ECBS run is separate/native.
    if (HERE / 'official_ecbs_solution.yaml').exists():
        inputs.insert(0, dict(name='official_test_staged',
            solution=yaml.safe_load((HERE / 'official_ecbs_solution.yaml').read_text()),
            dimensions=yaml.safe_load((SOURCE / 'sadg_controller/data/roadmaps/test/dimensions.yaml').read_text()),
            active_indices={}, horizon=5.0, progress=None, data_class='official_test_fixture', production_cost=None))
    for obj in inputs:
        dump(HERE / 'inputs' / (obj['name'] + '.json'), obj)
    registration = dict(max_unique_sadg_calls=12, actual_registered=len(inputs),
                        author_cap_seconds=60, outer_alarm_seconds=90,
                        registered_before_solve=True,
                        inputs={o['name']: key(o) for o in inputs},
                        pending_old_checkpoint='warehouse-10-20-10-2-1__t1_2__axis_slow',
                        remaining_slots_policy='At most two old-checkpoint mapped public/measured solves; if unsafe, mapping audit only.',
                        synthetic_range=[.05, .95],
                        historical_control='Same legal public history, duration ratio 1/1.25 for agent0; no fitting to test.')
    dump(HERE / 'REGISTRATION.json', registration)
    source_manifest()


def edge(dep):
    if dep is None:
        return None
    return [dep.get_tail().get_shorthand(), dep.get_head().get_shorthand()]


def snapshot(graph, horizon):
    vertices = []
    for aid, vs in graph.vertices_by_agent.items():
        for v in vs:
            vertices.append(dict(uid=v.get_shorthand(), agent=aid, index=v.get_vertex_idx(),
                status=v.get_status().name, nominal_duration=v.get_expected_completion_time(),
                progress=v.get_progress(), remaining=(1-v.get_progress())*v.get_expected_completion_time(),
                path_tuples=[[p.x,p.y,p.time] for p in v.plan_tuples],
                predecessor=v.get_prev().get_shorthand() if v.has_prev() else None,
                successor=v.get_next().get_shorthand() if v.has_next() else None,
                registered_incoming=[dict(edge=edge(d), active=d.is_active()) for d in v.get_dependencies()]))
    groups = []
    for aid, gs in graph.switchable_dep_groups.items():
        for g in gs:
            groups.append(dict(uid=g.get_uid(), agent=aid, group_type=g.type.name,
                switchable=g.is_switchable(), within_horizon=g.within_horizon(horizon),
                first_head_active=g.first_head_active.get_shorthand(),
                first_head_inactive=g.first_head_inactive.get_shorthand() if hasattr(g,'first_head_inactive') else None,
                contains_unswitchable=g.contains_unswitchable_dependency,
                dependencies=[dict(forward=edge(d.forward), reverse=edge(d.reverse),
                                   active=edge(d.get_active()), b=d.b, switchable=d.switchable) for d in g.get_dependencies()]))
    return dict(vertices=vertices, type1=[edge(d) for ds in graph.regular_deps.values() for d in ds], groups=groups)


def structure_audit(before, after):
    errors=[]
    bv={v['uid']:v for v in before['vertices']}; av={v['uid']:v for v in after['vertices']}
    if before['vertices'] != after['vertices']:
        # active flags in registered incoming dependencies are expected to change.
        for uid in bv:
            for field in ['status','path_tuples','nominal_duration','progress','predecessor','successor']:
                if bv[uid][field]!=av[uid][field]: errors.append(f'{uid}: changed {field}')
    if before['type1'] != after['type1']: errors.append('type1_changed')
    changed=[]
    for bg,ag in zip(before['groups'],after['groups']):
        for bd,ad in zip(bg['dependencies'],ag['dependencies']):
            if bd['active'] != ad['active']:
                changed.append(bg['uid'])
                if not (bg['switchable'] and bg['within_horizon']): errors.append('illegal_switch:'+bg['uid'])
                # all incoming heads newly introduced by a switch must still be staged
                if av[ad['active'][1]]['status'] != 'STAGED': errors.append('active_commitment_changed')
    G=nx.DiGraph(); G.add_nodes_from(av); G.add_edges_from(after['type1'])
    type2=[d['active'] for g in after['groups'] for d in g['dependencies']]
    G.add_edges_from(type2)
    if not nx.is_directed_acyclic_graph(G): errors.append('cycle')
    # For every shared location visit, require one order of leave-before-enter.
    # Terminal/start occupancy has no leave/enter vertex and is separately covered
    # by the original MAPF schedule validity audit, not invented here.
    vs=after['vertices']; covered=0; missed=[]
    for i,a in enumerate(vs):
        for b in vs[i+1:]:
            if a['agent']==b['agent']: continue
            if a['path_tuples'][-1][:2] != b['path_tuples'][-1][:2]: continue
            an=a['successor'];bn=b['successor']
            if not an or not bn: continue
            ok=(nx.has_path(G,an,b['uid']) or nx.has_path(G,bn,a['uid']))
            covered+=int(ok)
            if not ok: missed.append([a['uid'],b['uid']])
    if missed: errors.append('unprotected_shared_visits')
    return dict(pass_all=not errors, errors=errors, full_vertex_count=len(av),
        full_type1_count=len(after['type1']), full_type2_count=len(type2),
        changed_groups=sorted(set(changed)), dag=nx.is_directed_acyclic_graph(G),
        protected_shared_visits=covered, unprotected_shared_visits=missed,
        safety_scope='action dependency semantics, not physical radius/controller certification')


def solve(name):
    inp=json.loads((HERE/'inputs'/f'{name}.json').read_text())
    out=HERE/'cases'/name;out.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest()
    cache_key=key(dict(input=inp, source=manifest['source_files'], adapter=sha(__file__),
                       packages=manifest['packages']))
    old=out/'result.json'
    if old.exists():
        r=json.loads(old.read_text())
        if r['content_key']==cache_key:
            print(json.dumps({'reused':name,'content_key':cache_key}));return r
        raise RuntimeError('Refusing to overwrite differing solved case: '+name)
    graph=compile_sadg(Plan(inp['solution'],inp['dimensions']), LOG)
    for aid, idx in inp['active_indices'].items():
        for i,v in enumerate(graph.vertices_by_agent[aid]):
            v.set_status(Status.COMPLETED if i<idx else Status.IN_PROGRESS if i==idx else Status.STAGED)
        if inp['progress'] is not None:
            p=inp['progress'][aid]
            assert 0<=p<=1
            v=graph.vertices_by_agent[aid][idx]
            v.get_progress=types.MethodType(lambda self, value=p:value, v)
    before=snapshot(graph, inp['horizon']); dump(out/'graph_before.json',before)
    captures=[]
    optimize_code=mip.Model.optimize.__code__
    def observe(frame,event,arg):
        if frame.f_code is optimize_code:
            if event=='call':
                model=frame.f_locals['self']
                captures.append(dict(model=model,optimize_max_seconds=frame.f_locals['max_seconds'],
                                     started=time.perf_counter()))
                model.write(str(out/'author_model.lp'))
            elif event=='return':
                captures[-1]['solver_wall_seconds']=time.perf_counter()-captures[-1].pop('started')
                captures[-1]['returned_status']=arg.name if arg is not None else None
    error=None;t=time.perf_counter()
    try:
        with (out/'author_stdout.log').open('w') as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):
            import signal
            def alarm(signum,frame): raise TimeoutError('R16 90 second outer cap')
            previous=signal.signal(signal.SIGALRM,alarm);signal.alarm(90)
            old_profile=sys.getprofile();sys.setprofile(observe)
            try: graph.optimize(horizon=inp['horizon'])
            finally:
                sys.setprofile(old_profile);signal.alarm(0);signal.signal(signal.SIGALRM,previous)
    except Exception as exc:
        error=repr(exc)
    wall=time.perf_counter()-t
    after=snapshot(graph,inp['horizon']);dump(out/'graph_after.json',after)
    models=[]
    for c in captures:
        m=c.pop('model'); variables=[dict(name=v.name,type=v.var_type,lb=v.lb,ub=None if abs(v.ub)>1e100 else v.ub,value=v.x) for v in m.vars]
        constraints=[]
        for row in m.constrs:
            e=row.expr
            terms={v.name:coeff for v,coeff in e.expr.items()}
            lhs=e.const+sum(coeff*(v.x or 0) for v,coeff in e.expr.items())
            violation=max(0,lhs) if e.sense=='<' else max(0,-lhs) if e.sense=='>' else abs(lhs)
            constraints.append(dict(name=row.name,sense=e.sense,constant=e.const,terms=terms,
                                    evaluated_lhs=lhs,violation=violation))
        valid=m.num_solutions>0 and all(row['violation']<1e-5 for row in constraints)
        models.append(dict(c, status=m.status.name,objective=m.objective_value,
            objective_expression=dict(constant=m.objective.const,terms={v.name:c for v,c in m.objective.expr.items()}),
            objective_bound=m.objective_bound,gap=m.gap if math.isfinite(m.gap) else None,
            num_solutions=m.num_solutions,num_cols=m.num_cols,num_rows=m.num_rows,
            solver_name=m.solver_name,variables=variables,constraints=constraints,
            all_constraints_pass=valid,max_constraint_violation=max([r['violation'] for r in constraints],default=0)))
    dump(out/'models.json',models)
    audit=structure_audit(before,after)
    result=dict(name=name,content_key=cache_key,input_sha256=sha(HERE/'inputs'/f'{name}.json'),
        error=error,author_wall_seconds=wall,actual_author_calls=len(models),
        status=models[0]['status'] if models else None,
        objective=models[0]['objective'] if models else None,
        all_constraints_pass=bool(models) and all(m['all_constraints_pass'] for m in models),
        graph_audit=audit,production_cost=None,physical_suffix_run=False)
    dump(old,result);print(json.dumps(result));return result


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','solve','all','environment']);p.add_argument('--case')
    args=p.parse_args()
    if args.action=='register': register()
    elif args.action=='environment': source_manifest()
    elif args.action=='solve': solve(args.case)
    else:
        reg=json.loads((HERE/'REGISTRATION.json').read_text())
        assert len(reg['inputs'])<=12
        result=[solve(n) for n in reg['inputs']]
        dump(HERE/'RESULTS.json',result)


if __name__=='__main__':main()
