#!/usr/bin/env python3
"""R18 online event adapter around the pinned, unchanged author SADG optimizer.

No policy receives the private disturbance schedule or current true progress.
The fixed author compiler uses the separately named R16 k0/all-head patch.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import defaultdict
import contextlib
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import logging
import math
import os
from pathlib import Path
import signal
import statistics
import sys
import subprocess
import tempfile
import time
import types

PIN = 'c2626d996121a9d6c128844a167b917db24418ac'
SOURCE = Path('/home/lyh/.cache/mapf_research/sadg-controller-c2626d9')
R16 = Path(__file__).resolve().parent.parent / 'sadg_preflight_20261004_r16'
EPS = 1e-9
_AUTHOR = None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    # Cache and receipts become visible only as complete files.
    temporary=None
    try:
        with tempfile.NamedTemporaryFile('w',dir=path.parent,prefix=path.name+'.tmp.',delete=False) as stream:
            temporary=stream.name
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
        os.replace(temporary,path)
    finally:
        if temporary and os.path.exists(temporary):os.unlink(temporary)


def _write_model(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.tmp.');os.close(fd)
    try:
        with gzip.open(temporary,'wt') as stream:json.dump(value,stream,sort_keys=True,allow_nan=False)
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)


def _within(group,horizon):
    # The author prints "hello" for every out-of-horizon group; retain its
    # predicate but keep that diagnostic out of the public API/stdout.
    with contextlib.redirect_stdout(io.StringIO()):return group.within_horizon(horizon)


def _author():
    global _AUTHOR
    if _AUTHOR is None:
        head=subprocess.check_output(['rtk','proxy','git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()
        if head!=PIN:raise RuntimeError('author checkout revision differs from frozen R16')
        subprocess.check_call(['rtk','proxy','git','-C',str(SOURCE),'diff','--exit-code','HEAD'],stdout=subprocess.DEVNULL)
        sys.path.insert(0, str(SOURCE/'sadg_controller'))
        sys.path.insert(0, str(R16/'isolated_patch'))
        import mip
        from sadg_controller.mapf.plan import Plan
        from sadg_controller.sadg.status import Status
        spec = importlib.util.spec_from_file_location('r18_pinned_compiler', R16/'isolated_patch/compiler.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        source_files = sorted((SOURCE/'sadg_controller/sadg_controller/sadg').glob('*.py'))
        source_files += sorted((SOURCE/'sadg_controller/sadg_controller/mapf').glob('*.py'))
        source_files += [SOURCE/'sadg_controller/sadg_controller/core/geometry.py',
                         R16/'isolated_patch/compiler.py', R16/'isolated_patch/r16_guard_group.py']
        hashes = {str(p):file_sha(p) for p in source_files}
        from importlib import metadata
        hashes['python-mip-version'] = metadata.version('mip')
        hashes['cbcbox-version'] = metadata.version('cbcbox')
        _AUTHOR = dict(mip=mip, Plan=Plan, Status=Status, compiler=module.compile_sadg,
                       hashes=hashes, semantic_version='r18-original-author-duration-progress-v1')
    return _AUTHOR


@dataclass(frozen=True)
class EngineConfig:
    solve_period: float = 4.0
    query_latency: float = 0.25
    query_budget: int | None = None  # None defaults to 2N, not unlimited.
    max_queries_per_gate: int | None = None  # None defaults to ceil(N/8).
    max_time: float = 2000.0
    horizon: float = 5.0
    cache_dir: str | None = None
    output_dir: str | None = None
    save_models: bool = False
    save_gate_graphs: bool = False
    outer_solver_seconds: int = 90
    collision_tolerance: float = 1e-7


class NoQueryPolicy:
    def __call__(self, snapshot): return []


class DensePositionPolicy:
    unbudgeted_dense_reference = True
    def __call__(self, snapshot):
        return [a['agent_id'] for a in snapshot['agents'] if a['query_eligible']]


class PeriodicPolicy:
    """Round-robin fixed update rule; index derived from public gate, no state."""
    def __call__(self, snapshot):
        agents = [a['agent_id'] for a in snapshot['agents'] if a['query_eligible']]
        if not agents: return []
        offset = snapshot['gate_index'] % len(agents)
        return (agents[offset:]+agents[:offset])[:snapshot['max_queries']]


class HistoryRulePolicy:
    """Public uncertainty times dependency influence, fixed documented rule."""
    def __call__(self, snapshot):
        candidates = [a for a in snapshot['agents'] if a['query_eligible']]
        def score(a):
            expected = a['nominal_duration']*a['history_ratio']
            overdue = max(0., a['elapsed']/max(expected, EPS)-1.)
            age = a['elapsed'] if a['last_measurement_age'] is None else a['last_measurement_age']
            uncertainty = a['history_cv']+overdue+age/max(expected, EPS)
            influence = 1+a['outgoing_blocked_agents']+a['upcoming_switchable_influence']
            return uncertainty*influence
        candidates.sort(key=lambda a:(-score(a), a['agent_id']))
        return [a['agent_id'] for a in candidates[:snapshot['max_queries']] if score(a)>0]


def _edge(dep):
    return None if dep is None else [dep.get_tail().get_shorthand(), dep.get_head().get_shorthand()]


def graph_snapshot(graph, horizon):
    vertices=[]
    for aid, vs in graph.vertices_by_agent.items():
        for v in vs:
            vertices.append(dict(uid=v.get_shorthand(),agent=aid,index=v.get_vertex_idx(),
                status=v.get_status().name,duration=v.get_expected_completion_time(),progress=v.get_progress(),
                path=[[p.x,p.y,p.time] for p in v.plan_tuples],
                predecessor=v.get_prev().get_shorthand() if v.has_prev() else None,
                successor=v.get_next().get_shorthand() if v.has_next() else None))
    groups=[]
    for _, gs in graph.switchable_dep_groups.items():
        for g in gs:
            groups.append(dict(uid=g.get_uid(),switchable=g.is_switchable(),within_horizon=_within(g,horizon),
                dependencies=[dict(forward=_edge(d.forward),reverse=_edge(d.reverse),active=_edge(d.get_active()),b=d.b)
                              for d in g.get_dependencies()]))
    return dict(vertices=vertices,type1=[_edge(d) for ds in graph.regular_deps.values() for d in ds],groups=groups)


def adoption_guard(before, after):
    """Complete immutable-commitment/DAG guard, independent of world truth."""
    if before['vertices']!=after['vertices'] or before['type1']!=after['type1']:
        return dict(passed=False,reason='vertex_or_type1_changed')
    vertices={v['uid']:v for v in before['vertices']}
    old={g['uid']:g for g in before['groups']};changed=[]
    edges=list(map(tuple,after['type1']))
    for g in after['groups']:
        prior=old[g['uid']]
        if len(g['dependencies'])!=len(prior['dependencies']):
            return dict(passed=False,reason='dependency_family_changed')
        for a,b in zip(prior['dependencies'],g['dependencies']):
            if a['forward']!=b['forward'] or a['reverse']!=b['reverse']:
                return dict(passed=False,reason='dependency_pair_changed')
            if a['active']!=b['active']:
                changed.append(g['uid'])
                if not (prior['switchable'] and prior['within_horizon']):
                    return dict(passed=False,reason='switched_unqualified_group')
                if vertices[b['active'][1]]['status']!='STAGED':
                    return dict(passed=False,reason='changed_active_commitment')
            edges.append(tuple(b['active']))
    indegree={u:0 for u in vertices};outgoing=defaultdict(list)
    for a,b in edges:
        if a not in vertices or b not in vertices:return dict(passed=False,reason='unknown_vertex')
        outgoing[a].append(b);indegree[b]+=1
    ready=[u for u,d in indegree.items() if d==0];seen=0
    while ready:
        a=ready.pop();seen+=1
        for b in outgoing[a]:
            indegree[b]-=1
            if indegree[b]==0:ready.append(b)
    return dict(passed=seen==len(vertices),reason=None if seen==len(vertices) else 'cycle',
                changed_groups=sorted(set(changed)),vertices=len(vertices),edges=len(edges))


def continuous_collision_audit(segments, initial_positions, end_time, tolerance=1e-7):
    by_agent=defaultdict(list)
    for s in segments:by_agent[s['agent']].append(s)
    agents=sorted(initial_positions);errors=[];minimum=math.inf;pairs=0;collisions=[]
    for aid in agents:
        ss=by_agent[aid]
        if end_time>EPS:
            if not ss or abs(ss[0]['t0'])>EPS or abs(ss[-1]['t1']-end_time)>EPS:
                errors.append('incomplete_coverage:'+aid)
            for a,b in zip(ss,ss[1:]):
                if abs(a['t1']-b['t0'])>EPS or math.dist(a['p1'],b['p0'])>EPS:
                    errors.append('discontinuous_trace:'+aid)
    def point(s,t):
        f=(t-s['t0'])/(s['t1']-s['t0'])
        return [x+f*(y-x) for x,y in zip(s['p0'],s['p1'])]
    for i,aid in enumerate(agents):
        for bid in agents[i+1:]:
            a_list=by_agent[aid];b_list=by_agent[bid];ia=ib=0
            minimum=min(minimum,math.dist(initial_positions[aid],initial_positions[bid]))
            if math.dist(initial_positions[aid],initial_positions[bid])<tolerance:
                collisions.append(dict(agents=[aid,bid],time=0.,kind='INITIAL'))
            while ia<len(a_list) and ib<len(b_list):
                a=a_list[ia];b=b_list[ib];lo=max(a['t0'],b['t0']);hi=min(a['t1'],b['t1'])
                if hi>=lo-EPS:
                    pairs+=1;d=[x-y for x,y in zip(point(a,lo),point(b,lo))]
                    va=[(y-x)/(a['t1']-a['t0']) for x,y in zip(a['p0'],a['p1'])]
                    vb=[(y-x)/(b['t1']-b['t0']) for x,y in zip(b['p0'],b['p1'])]
                    dv=[x-y for x,y in zip(va,vb)];norm=sum(x*x for x in dv)
                    dt=max(0.,min(max(0.,hi-lo),-sum(x*y for x,y in zip(d,dv))/norm)) if norm else 0.
                    distance=math.sqrt(sum((x+dt*y)**2 for x,y in zip(d,dv)))
                    minimum=min(minimum,distance)
                    if distance<tolerance:collisions.append(dict(agents=[aid,bid],time=lo+dt,distance=distance))
                if a['t1']<b['t1']-EPS:ia+=1
                elif b['t1']<a['t1']-EPS:ib+=1
                else:ia+=1;ib+=1
    return dict(passed=not errors and not collisions,coverage_errors=errors,collisions=collisions,
                minimum_point_distance=None if math.isinf(minimum) else minimum,overlap_pairs=pairs,
                end_time=end_time,includes_initial_wait_and_goal_hold=True,
                scope='continuous affine point trajectories; not footprint/acceleration safety')


class Simulator:
    def __init__(self, case, disturbance=None, seed=0, *, config=None, **config_kwargs):
        self.case=copy.deepcopy(case);self.disturbance=copy.deepcopy(disturbance or {'kind':'stable'})
        self.seed=int(seed);self.config=config or EngineConfig(**config_kwargs)
        if config is not None and config_kwargs:raise ValueError('config or keyword config, not both')
        cfg=self.config
        if not all(math.isfinite(x) for x in [cfg.solve_period,cfg.query_latency,cfg.max_time,cfg.horizon]) or cfg.solve_period<=0 or cfg.query_latency<0 or cfg.query_latency>=cfg.solve_period or cfg.max_time<=0:
            raise ValueError('Require 0<=latency<period and finite positive time horizon')
        self.author=_author();self.Status=self.author['Status'];self.now=0.;self._ran=False
        self.solution=copy.deepcopy(case.get('solution',case))
        if 'schedule' not in self.solution:raise ValueError('case requires solution.schedule or schedule')
        self.dimensions=copy.deepcopy(case.get('dimensions',{'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}}))
        if 'dimensions' not in self.dimensions:self.dimensions={'dimensions':self.dimensions}
        logger=logging.getLogger('r18.author')
        if not logger.handlers:logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.WARNING)
        self.plan=self.author['Plan'](self.solution,self.dimensions)
        self.graph=self.author['compiler'](self.plan,logger)
        self.events=[];self.segments=[];self.gates=[];self.queries=[];self.solves=[];self.failures=[]
        self.agents={};self.nominal={};self.vertices={};self.private_profiles={};self.latest={};self.pending=[]
        self.initial_positions={};self.history=defaultdict(list);self.measurement_count=defaultdict(int)
        self.query_count=0;self.gate_index=0;self.next_gate=cfg.solve_period;self.pending_solve=None
        self.geometry_binding=digest(dict(schedule=self.solution['schedule'],dimensions=self.dimensions))
        for aid, points in self.plan.plans.items():
            if not points:raise ValueError('empty MAPF path: '+aid)
            vs=self.graph.vertices_by_agent[aid]
            self.initial_positions[aid]=[float(points[0].x),float(points[0].y)]
            self.agents[aid]=dict(cursor=0,vertex=vs[0] if vs else None,progress=0.,start=None,
                waiting_since=0.,completion=0. if not vs else None,paused_until=None,pause_used=False,
                position=list(self.initial_positions[aid]))
            for v in vs:
                uid=v.get_shorthand();duration=v.get_expected_completion_time()
                if duration<=0:raise ValueError('nonpositive author MOVE duration: '+uid)
                moves=[(a,b) for a,b in zip(v.plan_tuples,v.plan_tuples[1:]) if a.x!=b.x or a.y!=b.y]
                if len(moves)!=1 or (moves[0][0].x!=moves[0][1].x and moves[0][0].y!=moves[0][1].y):
                    raise ValueError('event affine MOVE requires bundled WAITs plus one cardinal segment: '+uid)
                self.nominal[uid]=duration;self.vertices[uid]=v
            if not vs:
                # Explicit resident adapter: author has no MOVE and would index
                # vertices[-1]. Resident remains in world/occupancy/result.
                del self.graph.vertices_by_agent[aid]
                self.events.append(dict(time=0.,kind='STATIONARY_RESIDENT',agent=aid))
            elif math.dist([vs[-1].get_goal_loc().x,vs[-1].get_goal_loc().y],
                           [points[-1].x,points[-1].y])>EPS:
                raise ValueError('compiler did not cover terminal location: '+aid)
        self.agent_ids=sorted(self.agents);n=len(self.agents)
        self.budget=2*n if cfg.query_budget is None else cfg.query_budget
        self.gate_cap=max(1,math.ceil(n/8)) if cfg.max_queries_per_gate is None else cfg.max_queries_per_gate
        if self.budget<0 or self.gate_cap<0:raise ValueError('negative query cap')
        self.cache=Path(cfg.cache_dir) if cfg.cache_dir else None
        if self.cache:self.cache.mkdir(parents=True,exist_ok=True)
        self._segments_by_agent=defaultdict(list)
        initial=graph_snapshot(self.graph,cfg.horizon)
        check=adoption_guard(initial,initial)
        if not check['passed']:raise ValueError('initial author graph invalid: '+str(check))
        self.initial_graph=initial

    def _unit(self, *parts):
        return int(hashlib.sha256(('|'.join(map(str,(self.seed,)+parts))).encode()).hexdigest()[:16],16)/2**64

    def _profile(self, aid, vertex):
        uid=vertex.get_shorthand()
        if uid in self.private_profiles:return self.private_profiles[uid]
        d=self.disturbance;kind=d.get('kind',d.get('mode','stable'))
        affected=self._unit('affected',aid)<float(d.get('affected_fraction',1.))
        factor=float(d.get('stable_factor',d.get('speed_factor',1.))) if affected else 1.
        if isinstance(d.get('stable_factor_range'),(list,tuple)) and affected:
            lo,hi=d['stable_factor_range'];factor=float(lo)+(float(hi)-float(lo))*self._unit('stable',aid)
        pause=0.;fraction=float(d.get('pause_fraction',0.35))
        if kind in ('bounded_pause','pause','short_stop') and affected:
            if self._unit('pause',aid,vertex.get_vertex_idx())<float(d.get('pause_probability',1.)):
                pause=float(d.get('pause_duration',1.))
                if d.get('pause_duration_range'):
                    lo,hi=d['pause_duration_range'];pause=float(lo)+(float(hi)-float(lo))*self._unit('pause_duration',aid,uid)
        if kind in ('speed_shift','shift') and affected:
            threshold=int(len(self.graph.vertices_by_agent[aid])*float(d.get('shift_action_fraction',0.35)))
            if vertex.get_vertex_idx()>=threshold:factor=float(d.get('shifted_factor',0.5))
        if kind not in ('stable','bounded_pause','pause','short_stop','speed_shift','shift'):
            raise ValueError('unknown private disturbance kind '+str(kind))
        if not (math.isfinite(factor) and factor>0 and math.isfinite(pause) and pause>=0 and 0<=fraction<1):
            raise ValueError('invalid private speed/pause profile')
        p=dict(agent=aid,vertex=uid,speed_factor=factor,pause_duration=pause,pause_fraction=fraction)
        self.private_profiles[uid]=p
        return p

    def _dispatch(self):
        for aid in self.agent_ids:
            a=self.agents[aid];v=a['vertex']
            if v is None or v.get_status()!=self.Status.STAGED:continue
            if v.has_prev() and v.get_prev().get_status()!=self.Status.COMPLETED:
                raise RuntimeError('cursor would bypass type1 commitment')
            if v.can_execute():
                v.set_status(self.Status.IN_PROGRESS);a.update(progress=0.,start=self.now,paused_until=None,pause_used=False)
                self._profile(aid,v)
                self.events.append(dict(time=self.now,kind='START',agent=aid,vertex=v.get_shorthand(),
                    dependency_tails=[d.get_tail().get_shorthand() for d in v.get_dependencies() if d.is_active()]))

    def _next_physical(self):
        times=[]
        for aid,a in self.agents.items():
            v=a['vertex']
            if v is None or v.get_status()!=self.Status.IN_PROGRESS:continue
            if a['paused_until'] is not None:times.append(a['paused_until']);continue
            p=self._profile(aid,v);target=1.
            if p['pause_duration']>0 and not a['pause_used']:target=p['pause_fraction']
            duration=max(0.,target-a['progress'])*self.nominal[v.get_shorthand()]/p['speed_factor']
            times.append(self.now+duration)
        return min(times,default=math.inf)

    def _segment(self, aid, v, start, end, p0, p1, kind):
        if end-start<=EPS:return
        ss=self._segments_by_agent[aid];uid=v.get_shorthand() if v is not None else None
        item=dict(agent=aid,vertex=uid,t0=start,t1=end,p0=p0,p1=p1,kind=kind)
        if ss:
            prev=ss[-1]
            va=[(y-x)/(prev['t1']-prev['t0']) for x,y in zip(prev['p0'],prev['p1'])]
            vb=[(y-x)/(end-start) for x,y in zip(p0,p1)]
            if prev['kind']==kind and prev['vertex']==uid and abs(prev['t1']-start)<EPS and math.dist(va,vb)<EPS:
                prev['t1']=end;prev['p1']=p1;return
        ss.append(item)

    def _advance(self, end):
        dt=end-self.now
        if dt< -EPS:raise RuntimeError('clock moved backwards')
        for aid,a in self.agents.items():
            v=a['vertex'];p0=list(a['position']);p1=p0
            if v is not None and v.get_status()==self.Status.IN_PROGRESS:
                if a['paused_until'] is not None:kind='DISTURBANCE_WAIT'
                else:
                    kind='MOVE';profile=self._profile(aid,v)
                    a['progress']=min(1.,a['progress']+dt*profile['speed_factor']/self.nominal[v.get_shorthand()])
                    s=v.get_start_loc();g=v.get_goal_loc();p=a['progress']
                    p1=[s.x+p*(g.x-s.x),s.y+p*(g.y-s.y)];a['position']=p1
            else:kind='GOAL_HOLD' if a['completion'] is not None else 'WAIT'
            self._segment(aid,v,self.now,end,p0,list(p1),kind)
        self.now=end

    def _physical_events(self):
        for aid,a in self.agents.items():
            v=a['vertex']
            if v is None or v.get_status()!=self.Status.IN_PROGRESS:continue
            p=self._profile(aid,v)
            if a['paused_until'] is not None:
                if a['paused_until']<=self.now+EPS:
                    a['paused_until']=None
                    self.events.append(dict(time=self.now,kind='PAUSE_END',agent=aid,vertex=v.get_shorthand(),private=True))
                continue
            if p['pause_duration']>0 and not a['pause_used'] and a['progress']>=p['pause_fraction']-EPS:
                a['pause_used']=True;a['paused_until']=self.now+p['pause_duration']
                self.events.append(dict(time=self.now,kind='PAUSE_START',agent=aid,vertex=v.get_shorthand(),private=True))
                continue
            if a['progress']>=1-EPS:
                uid=v.get_shorthand();v.set_status(self.Status.COMPLETED)
                g=v.get_goal_loc();a['position']=[g.x,g.y]
                history=dict(agent=aid,vertex=uid,start=a['start'],end=self.now,delivered=self.now,
                             nominal_duration=self.nominal[uid],duration=self.now-a['start'])
                self.history[aid].append(history)
                self.events.append(dict(time=self.now,kind='END',**{k:x for k,x in history.items() if k not in ['end','delivered']}))
                self.latest.pop(aid,None)
                if v.has_next():
                    a.update(vertex=v.get_next(),cursor=a['cursor']+1,progress=0.,start=None,waiting_since=self.now)
                else:a.update(vertex=None,completion=self.now,start=None)

    def _history(self, aid):
        history=self.history[aid]
        if not history:return 1.,0.,0.
        ratios=[h['duration']/h['nominal_duration'] for h in history]
        ratio=sum(h['duration'] for h in history)/sum(h['nominal_duration'] for h in history)
        variance=statistics.pvariance(ratios) if len(ratios)>1 else 0.
        cv=math.sqrt(variance)/statistics.mean(ratios)
        return ratio,variance,cv

    def _estimate(self, aid):
        a=self.agents[aid];v=a['vertex'];ratio,variance,cv=self._history(aid)
        if v is None:return dict(progress=1.,remaining=0.,ratio=ratio,variance=variance,cv=cv,age=None,residual=None)
        nominal=self.nominal[v.get_shorthand()];elapsed=0. if a['start'] is None else self.now-a['start']
        estimate=min(1.,max(0.,elapsed/(nominal*ratio))) if a['start'] is not None else 0.
        latest=self.latest.get(aid);age=residual=None
        if latest is not None and latest['vertex']==v.get_shorthand():
            age=self.now-latest['captured'];residual=nominal*(1-latest['progress'])
            estimate=min(1.,latest['progress']+age/(nominal*ratio))
        return dict(progress=estimate,remaining=(1-estimate)*nominal*ratio,
                    ratio=ratio,variance=variance,cv=cv,age=age,residual=residual)

    def _update_predictor(self):
        estimates={aid:self._estimate(aid) for aid in self.agent_ids}
        for aid,vs in self.graph.vertices_by_agent.items():
            ratio=estimates[aid]['ratio']
            for v in vs:
                # Completed durations are also frozen to their delivered actual
                # value; future/current preserve ORIGINAL length/2 baseline.
                history=next((h for h in self.history[aid] if h['vertex']==v.get_shorthand()),None)
                v.expected_completion_time=history['duration'] if history else self.nominal[v.get_shorthand()]*ratio
                progress=1. if v.get_status()==self.Status.COMPLETED else estimates[aid]['progress'] if v.get_status()==self.Status.IN_PROGRESS else 0.
                v.get_progress=types.MethodType(lambda self,value=progress:value,v)
        return estimates

    def public_snapshot(self, dense=False):
        estimates=self._update_predictor();influence=defaultdict(int);groups=0
        for gs in self.graph.switchable_dep_groups.values():
            for g in gs:
                if not (g.is_switchable() and _within(g,self.config.horizon)):continue
                groups+=1;touched=set()
                for d in g.get_dependencies():
                    for edge in [d.forward,d.reverse]:
                        if edge is not None:touched.update(['agent'+str(edge.get_tail().get_agent_id()),'agent'+str(edge.get_head().get_agent_id())])
                for aid in touched:influence[aid]+=1
        outgoing=defaultdict(set)
        for gs in self.graph.switchable_dep_groups.values():
            for g in gs:
                for d in g.get_dependencies():
                    edge=d.get_active();head=edge.get_head();tail=edge.get_tail()
                    if head.get_status()!=self.Status.COMPLETED and tail.get_status()!=self.Status.COMPLETED:
                        outgoing[tail.get_shorthand()].add('agent'+str(head.get_agent_id()))
        records=[]
        for aid in self.agent_ids:
            a=self.agents[aid];v=a['vertex'];e=estimates[aid]
            active=v is not None and v.get_status()==self.Status.IN_PROGRESS
            remaining=sum(self.nominal[x.get_shorthand()] for x in self.graph.vertices_by_agent.get(aid,[]) if x.get_status()!=self.Status.COMPLETED)
            records.append(dict(agent_id=aid,status='COMPLETED' if v is None else v.get_status().name,
                current_vertex=None if v is None else v.get_shorthand(),query_eligible=active,
                elapsed=self.now-a['start'] if active else 0.,nominal_duration=0. if v is None else self.nominal[v.get_shorthand()],
                history_ratio=e['ratio'],history_count=len(self.history[aid]),history_variance=e['variance'],history_cv=e['cv'],
                progress_estimate=e['progress'],remaining_estimate=e['remaining'],last_measurement_age=e['age'],
                last_observed_residual=e['residual'],measurement_count=self.measurement_count[aid],downstream_nominal=remaining,
                outgoing_blocked_agents=len(outgoing[v.get_shorthand()]) if v is not None else 0,
                upcoming_switchable_influence=influence[aid],blocked=v is not None and not active and not v.can_execute(),
                wait_elapsed=self.now-a['waiting_since'] if v is not None and not active else 0.))
        cap=sum(r['query_eligible'] for r in records) if dense else min(self.gate_cap,max(0,self.budget-self.query_count))
        return dict(gate_index=self.gate_index,time=self.now,budget_remaining=None if dense else self.budget-self.query_count,
                    max_queries=cap,agents=records,switchable_groups=groups)

    def _capture_gate(self, policy, override):
        dense=bool(getattr(policy,'unbudgeted_dense_reference',False));public=self.public_snapshot(dense)
        selected=override[self.gate_index] if self.gate_index in override else policy(copy.deepcopy(public))
        if not isinstance(selected,(list,tuple)) or any(not isinstance(x,str) for x in selected):
            raise ValueError('policy must return list[str]')
        if len(selected)!=len(set(selected)) or len(selected)>public['max_queries']:
            raise ValueError('policy exceeds query cap or repeats agents')
        eligible={a['agent_id'] for a in public['agents'] if a['query_eligible']}
        if not set(selected)<=eligible:raise ValueError('policy queried nonactive agent')
        gate=dict(gate_index=self.gate_index,capture_time=self.now,solve_time=self.now+self.config.query_latency,
                  public_snapshot=public,selected=list(selected),override=self.gate_index in override,
                  dense_unbudgeted_reference=dense)
        for aid in selected:
            a=self.agents[aid];body=dict(query_id=len(self.queries),gate_index=self.gate_index,agent=aid,
                vertex=a['vertex'].get_shorthand(),captured=self.now,delivered_at=self.now+self.config.query_latency,
                progress=a['progress'],world_geometry_binding=self.geometry_binding,cap=1.,
                provenance='simulated_capture_not_production_AUTH')
            body['body_sha256']=digest(body);body['payload_bytes']=len(json.dumps(body,sort_keys=True).encode())
            body['delivery_status']='pending';self.queries.append(body);self.pending.append(body);self.query_count+=1
        self.gates.append(gate);self.pending_solve=gate;self.gate_index+=1;self.next_gate+=self.config.solve_period

    def _deliver(self):
        remaining=[]
        for body in self.pending:
            if body['delivered_at']>self.now+EPS:remaining.append(body);continue
            aid=body['agent'];a=self.agents[aid];self.measurement_count[aid]+=1
            if a['vertex'] is None or a['vertex'].get_shorthand()!=body['vertex']:
                body['delivery_status']='stale_occurrence'
            else:
                body['delivery_status']='accepted';self.latest[aid]=dict(body)
            self.events.append(dict(time=self.now,kind='POSITION_DELIVER',query_id=body['query_id'],agent=aid,
                                    vertex=body['vertex'],status=body['delivery_status']))
        self.pending=remaining

    def _restore_directions(self, saved, saved_heads=None):
        bits={g['uid']:[d['b'] for d in g['dependencies']] for g in saved['groups']}
        for gs in self.graph.switchable_dep_groups.values():
            for g in gs:
                current=[d.b for d in g.get_dependencies()];target=bits[g.get_uid()]
                if current!=target:
                    if len(set(current))!=1 or len(set(target))!=1:raise RuntimeError('partial group switch')
                    g.switch()
                if saved_heads is not None:
                    g.first_head_active=saved_heads[g.get_uid()][0]
                    if saved_heads[g.get_uid()][1] is not None:g.first_head_inactive=saved_heads[g.get_uid()][1]

    def _solve(self, gate):
        self._update_predictor();before=graph_snapshot(self.graph,self.config.horizon)
        # Rollback must restore the author's derived horizon-head handles too,
        # not merely switch twice (the author's switch() recomputes them).
        saved_heads={g.get_uid():(g.first_head_active,getattr(g,'first_head_inactive',None))
                     for gs in self.graph.switchable_dep_groups.values() for g in gs}
        semantic=digest(dict(graph=before,horizon=self.config.horizon,source=self.author['hashes'],
                             semantics=self.author['semantic_version']))
        cache_file=self.cache/f'{semantic}.json' if self.cache else None
        reused=False;model_record=None;model_data=None;stdout='';new_wall=0.
        if cache_file and cache_file.exists():
            cached=json.loads(cache_file.read_text())
            if cached['semantic_key']!=semantic or cached['before_sha256']!=digest(before):
                raise RuntimeError('cache semantic mismatch')
            self._restore_directions(cached['after']);model_record=copy.deepcopy(cached['model']);reused=True
        else:
            mip=self.author['mip'];code=mip.Model.optimize.__code__;captures=[]
            def observer(frame,event,arg):
                if frame.f_code is code:
                    if event=='call':captures.append(dict(model=frame.f_locals['self'],start=time.perf_counter(),cap=frame.f_locals['max_seconds']))
                    elif event=='return':captures[-1]['wall']=time.perf_counter()-captures[-1]['start']
            def alarm(signum,frame):raise TimeoutError('author outer watchdog')
            start=time.perf_counter();old_profile=sys.getprofile();old_alarm=None;error=None;stream=io.StringIO()
            try:
                old_alarm=signal.signal(signal.SIGALRM,alarm);signal.alarm(self.config.outer_solver_seconds)
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                    sys.setprofile(observer)
                    self.graph.optimize(horizon=self.config.horizon)
            except Exception as exc:error=repr(exc)
            finally:
                sys.setprofile(old_profile);signal.alarm(0)
                if old_alarm is not None:signal.signal(signal.SIGALRM,old_alarm)
                new_wall=time.perf_counter()-start;stdout=stream.getvalue()
            model_record=dict(status='NO_MODEL',error=error,reference_solver_seconds=0.,
                              reference_author_seconds=new_wall,objective=None,bound=None,feasible=False,actual_author_calls=len(captures))
            if captures:
                capture=captures[-1];m=capture['model'];values={v.name:v.x for v in m.vars};rows=[];maximum=0.
                for row in m.constrs:
                    e=row.expr;terms={v.name:co for v,co in e.expr.items()};lhs=None;violation=None
                    if all(values[n] is not None for n in terms):
                        lhs=e.const+sum(co*values[n] for n,co in terms.items())
                        violation=max(0.,lhs) if e.sense=='<' else max(0.,-lhs) if e.sense=='>' else abs(lhs)
                        maximum=max(maximum,violation)
                    rows.append(dict(name=row.name,sense=e.sense,constant=e.const,terms=terms,lhs=lhs,violation=violation))
                values_finite=all(value is not None and math.isfinite(value) for value in values.values())
                bound_violation=max((max(0.,v.lb-v.x,v.x-v.ub) for v in m.vars),default=0.) if values_finite else None
                integral_violation=max((abs(v.x-round(v.x)) for v in m.vars if v.var_type in ['B','I']),default=0.) if values_finite else None
                model_data=dict(variables=[dict(name=v.name,type=v.var_type,lb=None if abs(v.lb)>1e100 else v.lb,
                    ub=None if abs(v.ub)>1e100 else v.ub,value=v.x) for v in m.vars],constraints=rows,
                    objective=dict(constant=m.objective.const,terms={v.name:co for v,co in m.objective.expr.items()}))
                model_record.update(status=m.status.name,objective=m.objective_value,bound=m.objective_bound,
                    reference_solver_seconds=capture.get('wall',new_wall),author_max_seconds=capture['cap'],
                    feasible=m.num_solutions>0 and values_finite and maximum<1e-5 and bound_violation<1e-5 and integral_violation<1e-5,
                    max_violation=maximum,max_bound_violation=bound_violation,max_integrality_violation=integral_violation,
                    all_values_finite=values_finite,
                    variables=m.num_cols,constraints=m.num_rows,model_sha256=digest(model_data))
            if error or not model_record['feasible']:
                self._restore_directions(before,saved_heads)
                self.failures.append(dict(time=self.now,kind='SOLVER_FAILURE_PARENT_GRAPH_RETAINED',detail=copy.deepcopy(model_record)))
        after=graph_snapshot(self.graph,self.config.horizon);guard=adoption_guard(before,after)
        if not guard['passed']:
            self._restore_directions(before,saved_heads);after=graph_snapshot(self.graph,self.config.horizon)
            self.failures.append(dict(time=self.now,kind='ADOPTION_REJECTED_PARENT_GRAPH_RETAINED',detail=guard))
        if cache_file and not reused and model_record['feasible'] and guard['passed'] and not model_record.get('error'):
            model_path=self.cache/f'{semantic}.model.json.gz'
            _write_model(model_path,model_data)
            write_json(cache_file,dict(semantic_key=semantic,before_sha256=digest(before),after=after,model=model_record,
                                      model_file=str(model_path),model_file_sha256=file_sha(model_path)))
        record=dict(gate_index=gate['gate_index'],time=self.now,semantic_key=semantic,cache_reused=reused,
            new_author_calls=0 if reused else model_record['actual_author_calls'],new_author_wall_seconds=new_wall,
            new_solver_seconds=0. if reused else model_record['reference_solver_seconds'],
            model=model_record,guard=guard,before_sha256=digest(before),after_sha256=digest(after),
            cache_source=str(cache_file) if cache_file else None,
            cached_model_file=str(self.cache/f'{semantic}.model.json.gz') if self.cache and (self.cache/f'{semantic}.model.json.gz').exists() else None,
            active_commitments=[v['uid'] for v in before['vertices'] if v['status']=='IN_PROGRESS'])
        self.solves.append(record)
        if self.config.output_dir:
            out=Path(self.config.output_dir)/'solves'/f'{gate["gate_index"]:05d}'
            write_json(out/'receipt.json',record)
            if self.config.save_gate_graphs or self.config.save_models:
                write_json(out/'before.json',before);write_json(out/'after.json',after)
            if not reused:
                (out/'author_stdout.log').write_text(stdout)
                if self.config.save_models and model_data is not None:
                    _write_model(out/'model.json.gz',model_data)
            elif self.config.save_models:write_json(out/'REUSED_MODEL.json',dict(cache_source=str(cache_file),model_sha256=model_record.get('model_sha256')))

    def run(self, policy=None, probe_override=None):
        if self._ran:raise RuntimeError('Simulator is single-use; construct a fresh one for matched replay')
        self._ran=True;policy=policy or NoQueryPolicy();override={int(k):v for k,v in (probe_override or {}).items()};start=time.perf_counter()
        status='completed';error=None
        try:
            self._dispatch()
            while any(a['completion'] is None for a in self.agents.values()):
                if self.now>=self.config.max_time-EPS:status='truncated';break
                physical=self._next_physical()
                if math.isinf(physical):status='deadlock';break
                decision=self.pending_solve['solve_time'] if self.pending_solve else math.inf
                next_time=min(physical,self.next_gate,decision,self.config.max_time)
                self._advance(next_time);self._physical_events();self._deliver();self._dispatch()
                if all(a['completion'] is not None for a in self.agents.values()):break
                if self.pending_solve is not None and self.pending_solve['solve_time']<=self.now+EPS:
                    self._solve(self.pending_solve);self.pending_solve=None;self._dispatch()
                if self.next_gate<=self.now+EPS:
                    self._capture_gate(policy,override)
                    if self.config.query_latency<=EPS:
                        self._deliver();self._solve(self.pending_solve);self.pending_solve=None;self._dispatch()
        except Exception as exc:
            status='exception';error=repr(exc);self.failures.append(dict(time=self.now,kind='EXCEPTION',error=error))
        task_finish_time=max((a['completion'] for a in self.agents.values() if a['completion'] is not None),default=0.)
        if all(a['completion'] is not None for a in self.agents.values()) and self.pending:
            # Drain charged captures without altering task completion metrics;
            # every agent remains at its goal during transport delivery.
            self._advance(max(q['delivered_at'] for q in self.pending));self._deliver()
            if self.pending_solve is not None:
                self.events.append(dict(time=self.now,kind='SOLVE_SKIPPED_ALL_COMPLETED',gate_index=self.pending_solve['gate_index']))
                self.pending_solve=None
        self.segments=[s for aid in self.agent_ids for s in self._segments_by_agent[aid]]
        collision=continuous_collision_audit(self.segments,self.initial_positions,self.now,self.config.collision_tolerance)
        if not collision['passed'] and status=='completed':status='collision'
        finished={aid:a['completion'] for aid,a in self.agents.items() if a['completion'] is not None}
        complete=len(finished)==len(self.agents)
        # Restricted sum uses the COMMON registered H for unfinished agents,
        # not the policy-dependent early deadlock/exception time.
        restricted=sum(finished.values())+(len(self.agents)-len(finished))*self.config.max_time
        result=dict(schema='r18-sadg-episode-v1',case_id=self.case.get('case_id'),status=status,error=error,
            success=status=='completed' and complete and collision['passed'],completed_agents=len(finished),agents=len(self.agents),
            completion_times=finished,sum_completion=sum(finished.values()) if complete else None,
            makespan=max(finished.values(),default=0.) if complete else None,restricted_sum_completion=restricted,
            simulation_end=self.now,common_horizon=self.config.max_time,query_count=self.query_count,
            task_finish_time=task_finish_time,pending_queries_after_transport=len(self.pending),
            query_payload_bytes=sum(q['payload_bytes'] for q in self.queries),query_budget=self.budget,
            dense_unbudgeted_reference=bool(getattr(policy,'unbudgeted_dense_reference',False)),
            solver_calls=len(self.solves),new_author_calls=sum(s['new_author_calls'] for s in self.solves),
            reference_solver_seconds=sum(s['model']['reference_solver_seconds'] for s in self.solves),
            new_solver_seconds=sum(s['new_solver_seconds'] for s in self.solves),
            reference_author_seconds=sum(s['model']['reference_author_seconds'] for s in self.solves),
            new_author_seconds=sum(s['new_author_wall_seconds'] for s in self.solves),
            episode_wall_seconds=time.perf_counter()-start,production_cost=None,
            config=asdict(self.config),author_pin=PIN,source_hashes=self.author['hashes'],
            engine_sha256=file_sha(__file__),public_schema_sha256=file_sha(Path(__file__).with_name('PUBLIC_SCHEMA.json')),
            requested_probe_overrides=override,
            unreached_probe_gates=sorted(set(override)-{g['gate_index'] for g in self.gates}),
            compiler_variant='R16_isolated_k0_all_heads_plus_explicit_stationary_residents',
            geometry_binding=self.geometry_binding,initial_graph=self.initial_graph,initial_positions=self.initial_positions,
            events=self.events,gates=self.gates,queries=self.queries,solves=self.solves,segments=self.segments,
            delivered_end_history=dict(self.history),collision_audit=collision,failures=self.failures,
            private_truth=dict(seed=self.seed,disturbance=self.disturbance,action_profiles=self.private_profiles),
            scope='fixed-path online scheduling; continuous point motion; no ROS/footprint/production charging')
        if self.config.output_dir:write_json(Path(self.config.output_dir)/'episode.json',result)
        return result
