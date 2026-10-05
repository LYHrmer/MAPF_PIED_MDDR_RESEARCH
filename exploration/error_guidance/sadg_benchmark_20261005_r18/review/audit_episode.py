#!/usr/bin/env python3
"""Independent R18 receipt/trajectory verifier. Never imports engine or runs MILP.

Use --episode <episode.json> [--case case.json|yaml] [--model model.json]
    [--policy history_only|history_rule|fixed_update|learned_query|dense_position]
    --output audit.json
An audit failure is an evidence discrepancy, not necessarily a safe execution.
Collision/exception episodes remain valid negative experiment records if their
metrics and failure status agree with the independently reconstructed trajectory.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import gzip
import json
import math
from pathlib import Path
import statistics

TOL = 2e-7
PUBLIC = {'gate_index', 'time', 'budget_remaining', 'max_queries', 'agents', 'switchable_groups'}
AGENT_PUBLIC = {'agent_id', 'status', 'current_vertex', 'query_eligible', 'elapsed',
    'nominal_duration', 'history_ratio', 'history_count', 'history_variance',
    'history_cv', 'progress_estimate', 'remaining_estimate', 'last_measurement_age',
    'last_observed_residual', 'measurement_count', 'downstream_nominal',
    'outgoing_blocked_agents', 'upcoming_switchable_influence', 'blocked', 'wait_elapsed'}


def canon(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read(path):
    p = Path(path)
    if p.suffix in ('.yaml', '.yml'):
        import yaml
        return yaml.safe_load(p.read_text())
    return json.loads(p.read_text())


def close(a, b, tol=TOL):
    if a is None or b is None:
        return a is b
    return abs(float(a)-float(b)) <= tol*max(1., abs(float(a)), abs(float(b)))


def point(s, t):
    f = (t-s['t0'])/(s['t1']-s['t0'])
    return [a+f*(b-a) for a,b in zip(s['p0'], s['p1'])]


def all_edges(graph):
    return [tuple(e) for e in graph['type1']] + [tuple(d['active'])
        for g in graph['groups'] for d in g['dependencies']]


def score(a):
    d = max(1e-9, a['nominal_duration']); r = max(1., a['history_ratio'])
    age = a['last_measurement_age']
    if age is not None and age < .5*d:
        return 0.
    late = max(0., a['elapsed']-d*r)
    return a['outgoing_blocked_agents'] * min(max(a['remaining_estimate'], late, .25*d),
        d*max(.25,a['history_cv'])*r+late) * (1+min(2.,a['downstream_nominal']/d)) / (1+a['measurement_count'])


def feature_vector(s, a):
    d=max(1e-9,a['nominal_duration']); r=max(1e-9,a['history_ratio'])
    elapsed=a['elapsed']/(d*r); cv=max(0.,a['history_cv'])
    age=(a['elapsed'] if a['last_measurement_age'] is None else a['last_measurement_age'])/d
    b=a['outgoing_blocked_agents']; inf=a['upcoming_switchable_influence']
    u=max(.25,cv)*r; late=max(0.,elapsed-1); n=max(1,len(s['agents']))
    return [elapsed,r,math.log1p(a['history_count']),cv,a['progress_estimate'],
        a['remaining_estimate'],age,float(a['last_measurement_age'] is None),
        math.log1p(a['measurement_count']),float(b),float(inf),math.log1p(a['downstream_nominal']),
        float(s['budget_remaining'] or 0)/n,math.log1p(s['gate_index']),
        sum(x['query_eligible'] for x in s['agents'])/n,sum(bool(x['blocked']) for x in s['agents'])/n,
        late,b*u,late*b,inf*u,a['remaining_estimate']*b,age*b]


def policy_selection(s, policy, model=None):
    eligible=[a for a in s['agents'] if a['query_eligible']]
    cap=s['max_queries'] if s['budget_remaining'] is None else min(s['max_queries'],max(0,s['budget_remaining']))
    if policy=='history_only': return []
    if policy=='dense_position': return [a['agent_id'] for a in eligible]
    if policy=='history_rule':
        return [a['agent_id'] for a in sorted(eligible,key=lambda a:(-score(a),a['agent_id'])) if score(a)>0][:cap]
    if policy=='fixed_update':
        aa=s['agents']; k=(s['gate_index']*s['max_queries'])%len(aa) if aa else 0
        return [a['agent_id'] for a in aa[k:]+aa[:k] if a['query_eligible']][:cap]
    if policy=='learned_query' and model:
        def predict(a):
            return model['intercept']+sum((x-m)/z*c for x,m,z,c in zip(feature_vector(s,a),model['mean'],model['scale'],model['coef']))
        ranked=sorted([(predict(a),a['agent_id']) for a in eligible],key=lambda p:(-p[0],p[1]))
        return [aid for val,aid in ranked if val>1e-8][:cap]
    return None


class Auditor:
    def __init__(self, episode, case=None, policy=None, model=None):
        self.path=Path(episode); self.e=read(self.path); self.case=read(case) if case else None
        self.policy=policy; self.model=read(model) if model else None
        self.errors=[]; self.checks=0; self.limits=[]; self.stats={}
        self.evs=self.e['events']; self.initial=self.e['initial_graph']
        self.vs={v['uid']:v for v in self.initial['vertices']}
        self.byagent=defaultdict(list)
        for v in self.initial['vertices']: self.byagent[v['agent']].append(v)
        for vv in self.byagent.values(): vv.sort(key=lambda v:v['index'])
        self.starts={}; self.ends={}; self.graphs=[]; self.segments=defaultdict(list)

    def check(self, ok, label, detail=None):
        self.checks+=1
        if not ok: self.errors.append({'check':label,'detail':detail})

    def eq(self,a,b,label): self.check(close(a,b),label,{'recorded':a,'reconstructed':b})

    def graph_check(self, graph, label):
        vv={v['uid']:v for v in graph['vertices']}
        self.check(len(vv)==len(graph['vertices']),label+':unique_vertices')
        incoming={v:0 for v in vv}; adj=defaultdict(list)
        for a,b in all_edges(graph):
            self.check(a in vv and b in vv,label+':edge_identity')
            if a in vv and b in vv: incoming[b]+=1;adj[a].append(b)
        todo=[a for a,n in incoming.items() if n==0]; count=0
        while todo:
            a=todo.pop();count+=1
            for b in adj[a]:
                incoming[b]-=1
                if not incoming[b]:todo.append(b)
        self.check(count==len(vv),label+':acyclic')
        for g in graph['groups']:
            for d in g['dependencies']:
                self.check(d['active'] in (d['forward'],d['reverse']) and d['active'] is not None,label+':paired_active')

    def source_and_input(self):
        e=self.e
        self.check(e['schema']=='r18-sadg-episode-v1','schema')
        receipt_path=self.path.parent/'RUN_RECEIPT.json'
        if receipt_path.exists():
            receipt=read(receipt_path);spec=receipt['spec']
            self.check(hashlib.sha256(self.path.read_bytes()).hexdigest()==receipt['episode_sha256'],'run_receipt_episode_hash')
            self.check(canon(spec)==receipt['spec_sha256']==e['benchmark']['spec_sha256'],'run_receipt_spec_hash')
            self.check(spec['config']==e['config'],'registered_episode_config')
            self.check(spec['seed']==e['private_truth']['seed'] and spec['disturbance']==e['private_truth']['disturbance'],'registered_physical_world')
            self.check(receipt['status']==e['status'] and receipt['success']==e['success'],'receipt_outcome')
            self.check(receipt['started_utc']<=receipt['finished_utc'],'run_receipt_clock_order')
            root=self.path
            while root.parent!=root and not (root/'EXPERIMENT_REGISTRATION.json').exists():root=root.parent
            self.check((root/'EXPERIMENT_REGISTRATION.json').exists(),'registration_exists')
            if (root/'EXPERIMENT_REGISTRATION.json').exists():
                reg=read(root/'EXPERIMENT_REGISTRATION.json')
                self.check(reg['source_pins']==spec['source_pins'],'receipt_registered_sources')
                self.check(reg['registered_utc']<=receipt['started_utc'],'registered_before_run')
                for name,h in spec['source_pins'].items():
                    self.check((root/name).is_file() and hashlib.sha256((root/name).read_bytes()).hexdigest()==h,'scientific_source_pin:'+name)
                if spec['arm']=='learned_query':
                    frozen=read(root/'MODEL_FREEZE_RECEIPT.json')
                    self.check(frozen['model_sha256']==spec['model_sha256']==hashlib.sha256((root/'MODEL_FROZEN.json').read_bytes()).hexdigest(),'run_frozen_model')
                    self.check(frozen['frozen_utc']<=receipt['started_utc'],'model_frozen_before_run')
        else:self.limits.append('Structural pilot has no benchmark RUN_RECEIPT; scientific freeze chronology is not inferred.')
        for path,h in e['source_hashes'].items():
            if path in ('python-mip-version','cbcbox-version'): continue
            p=Path(path); self.check(p.is_file(),'source_exists',path)
            if p.is_file():self.check(hashlib.sha256(p.read_bytes()).hexdigest()==h,'source_hash',path)
        self.graph_check(self.initial,'initial')
        for aid,vv in self.byagent.items():
            for i,v in enumerate(vv):
                d=sum(math.dist(a[:2],b[:2]) for a,b in zip(v['path'],v['path'][1:]))/2
                self.eq(v['duration'],d,'original_nominal:'+v['uid'])
                self.check(d>0,'positive_move:'+v['uid'])
                self.check(v['predecessor']==(vv[i-1]['uid'] if i else None),'type1_prev:'+v['uid'])
                self.check(v['successor']==(vv[i+1]['uid'] if i+1<len(vv) else None),'type1_next:'+v['uid'])
                if i:self.check([vv[i-1]['uid'],v['uid']] in self.initial['type1'],'type1_edge:'+v['uid'])
                distinct=[v['path'][0][:2]]
                for p in v['path'][1:]:
                    if p[:2]!=distinct[-1]:distinct.append(p[:2])
                self.check(len(distinct)==2,'one_physical_edge:'+v['uid'])
        if self.case:
            sol=self.case.get('solution',self.case); schedule=sol['schedule']
            dims=self.case.get('dimensions',{'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}})
            if 'dimensions' not in dims:dims={'dimensions':dims}
            self.check(canon({'schedule':schedule,'dimensions':dims})==e['geometry_binding'],'input_geometry_binding')
            d=dims['dimensions'];transform=lambda p:[d['resolution']*p['y']+d['x_offset'],-d['resolution']*p['x']+d['y_offset']]
            self.check(set(schedule)==set(e['initial_positions']),'input_agent_set')
            for aid,pp in schedule.items():
                self.check(math.dist(transform(pp[0]),e['initial_positions'][aid])<TOL,'input_start:'+aid)
                route=[transform(pp[0])]
                for p in pp[1:]:
                    q=transform(p)
                    if q!=route[-1]:route.append(q)
                compiled=[v['path'][0][:2] for v in self.byagent[aid]]
                if compiled:compiled.append(self.byagent[aid][-1]['path'][-1][:2])
                else:compiled=[e['initial_positions'][aid]]
                self.check(compiled==route,'complete_input_route:'+aid)
        else:self.limits.append('No case supplied: geometry binding and complete ECBS path input not independently reconstructed.')

    def events_and_outcomes(self):
        e=self.e; previous=-math.inf
        for row in self.evs:
            t=row['time'];self.check(t>=previous-TOL,'event_monotone');previous=t
            uid=row.get('vertex');kind=row['kind']
            if kind=='START':
                self.check(uid in self.vs and uid not in self.starts,'unique_START',uid);self.starts[uid]=row
            elif kind=='END':
                self.check(uid in self.starts and uid not in self.ends,'unique_END',uid);self.ends[uid]=row
                if uid in self.starts:
                    self.eq(row['start'],self.starts[uid]['time'],'END_start:'+uid)
                    self.eq(row['duration'],t-self.starts[uid]['time'],'END_duration:'+uid)
                    self.eq(row['nominal_duration'],self.vs[uid]['duration'],'END_nominal:'+uid)
        finished={}
        for aid in e['initial_positions']:
            vv=self.byagent[aid]
            if not vv:
                finished[aid]=0.
                self.check(any(x['kind']=='STATIONARY_RESIDENT' and x['agent']==aid and x['time']==0 for x in self.evs),'resident_event:'+aid)
            for i,v in enumerate(vv):
                u=v['uid']
                if u in self.starts and i:
                    prev=vv[i-1]['uid']
                    self.check(prev in self.ends and self.ends[prev]['time']<=self.starts[u]['time']+TOL,'serial_cursor:'+u)
            if vv and vv[-1]['uid'] in self.ends:finished[aid]=self.ends[vv[-1]['uid']]['time']
            recorded=e['delivered_end_history'].get(aid,[])
            hist=[x for x in self.evs if x['kind']=='END' and x['agent']==aid]
            self.check(len(recorded)==len(hist),'history_count:'+aid)
            for a,b in zip(recorded,hist):
                self.check(a['vertex']==b['vertex'],'history_identity:'+aid)
                for key,other in [('start','start'),('duration','duration'),('nominal_duration','nominal_duration'),('end','time'),('delivered','time')]:
                    self.eq(a[key],b[other],'history_'+key+':'+aid)
        self.check(finished==e['completion_times'],'completion_times_from_END')
        self.check(len(finished)==e['completed_agents'],'completed_count')
        self.check(len(e['initial_positions'])==e['agents'],'agent_count')
        self.eq(e['restricted_sum_completion'],sum(finished.values())+(e['agents']-len(finished))*e['common_horizon'],'restricted_sum')
        complete=len(finished)==e['agents']
        self.eq(e['sum_completion'],sum(finished.values()) if complete else None,'sum_completion')
        self.eq(e['makespan'],max(finished.values(),default=0.) if complete else None,'makespan')
        self.stats['completed_from_END']=len(finished)

    def graph_adoptions(self):
        e=self.e; old=self.initial
        for s in e['solves']:
            p=self.path.parent/'solves'/f"{s['gate_index']:05d}"
            receipt=p/'receipt.json';before=p/'before.json';after=p/'after.json'
            self.check(receipt.is_file(),'solve_receipt_exists',str(p))
            if receipt.is_file():self.check(read(receipt)==s,'solve_receipt_matches',str(p))
            if not before.is_file() or not after.is_file():
                self.check(False,'full_graph_evidence_required',str(p));continue
            b=read(before);a=read(after)
            self.check(canon(b)==s['before_sha256'] and canon(a)==s['after_sha256'],'graph_hash',str(p))
            semantic=canon({'graph':b,'horizon':e['config']['horizon'],'source':e['source_hashes'],'semantics':'r18-original-author-duration-progress-v1'})
            self.check(semantic==s['semantic_key'],'exact_cache_key',str(p))
            self.graph_check(b,'before');self.graph_check(a,'after')
            self.check(b['vertices']==a['vertices'] and b['type1']==a['type1'],'adoption_no_vertex_change')
            gb={g['uid']:g for g in b['groups']};ga={g['uid']:g for g in a['groups']};go={g['uid']:g for g in old['groups']}
            self.check(set(gb)==set(ga)==set(go),'group_conservation')
            vv={v['uid']:v for v in b['vertices']}
            for uid,g in gb.items():
                self.check(g['dependencies']==go[uid]['dependencies'],'parent_directions:'+uid)
                self.check(len(g['dependencies'])==len(ga[uid]['dependencies']),'dependency_count:'+uid)
                changes=[]
                for x,y in zip(g['dependencies'],ga[uid]['dependencies']):
                    self.check(x['forward']==y['forward'] and x['reverse']==y['reverse'],'dependency_pair:'+uid)
                    changes.append(x['active']!=y['active'])
                if any(changes):
                    self.check(all(changes),'whole_group_switch:'+uid)
                    self.check(g['switchable'] and g['within_horizon'],'qualified_group:'+uid)
                    self.check(all(d['reverse'] is not None and vv[d['forward'][1]]['status']=='STAGED' and vv[d['reverse'][1]]['status']=='STAGED' for d in g['dependencies']),'all_candidate_heads_staged:'+uid)
            for v in b['vertices']:
                uid=v['uid'];start=self.starts.get(uid);end=self.ends.get(uid);t=s['time']
                if v['status']=='COMPLETED':self.check(end is not None and end['time']<=t+TOL,'graph_completed_evidence:'+uid)
                elif v['status']=='IN_PROGRESS':self.check(start is not None and start['time']<=t+TOL and (end is None or end['time']>t-TOL),'graph_running_evidence:'+uid)
                elif v['status']=='STAGED':self.check(start is None or start['time']>=t-TOL,'graph_staged_evidence:'+uid)
            self.check(sorted(s['active_commitments'])==sorted(v['uid'] for v in b['vertices'] if v['status']=='IN_PROGRESS'),'active_commitment_receipt')
            if not s['model']['feasible'] or s['model'].get('error') or not s['guard']['passed']:
                self.check(all(gb[u]['dependencies']==ga[u]['dependencies'] for u in gb),'failure_restores_parent')
            if s['cache_reused']:
                self.eq(s['new_author_calls'],0,'cache_no_author_call');self.eq(s['new_solver_seconds'],0,'cache_no_solver_work')
            model_path=p/'model.json.gz'
            if not model_path.exists() and s.get('cached_model_file'):model_path=Path(s['cached_model_file'])
            if model_path.exists():
                with gzip.open(model_path,'rt') as f:model=json.load(f)
                self.check(canon(model)==s['model'].get('model_sha256'),'full_model_hash')
                values={v['name']:v['value'] for v in model['variables']}
                finite=all(x is not None and math.isfinite(x) for x in values.values())
                self.check(finite or not s['model']['feasible'],'feasible_has_finite_variables')
                if finite:
                    bound=integral=violation=0.
                    for v in model['variables']:
                        x=v['value']
                        if v['lb'] is not None:bound=max(bound,v['lb']-x)
                        if v['ub'] is not None:bound=max(bound,x-v['ub'])
                        if v['type'] in ('B','I'):integral=max(integral,abs(x-round(x)))
                    for row in model['constraints']:
                        lhs=row['constant']+sum(c*values[n] for n,c in row['terms'].items())
                        v=max(0.,lhs) if row['sense']=='<' else max(0.,-lhs) if row['sense']=='>' else abs(lhs)
                        violation=max(violation,v);self.eq(row['lhs'],lhs,'constraint_lhs')
                        self.eq(row['violation'],v,'constraint_violation')
                    self.eq(s['model']['max_violation'],violation,'max_constraint_violation')
                    if 'max_bound_violation' in s['model']:self.eq(s['model']['max_bound_violation'],bound,'max_bound_violation')
                    if 'max_integrality_violation' in s['model']:self.eq(s['model']['max_integrality_violation'],integral,'max_integrality_violation')
                    self.check(not s['model']['feasible'] or max(bound,integral,violation)<1e-5,'independent_incumbent_feasibility')
                    obj=model['objective'];self.eq(s['model']['objective'],obj['constant']+sum(c*values[n] for n,c in obj['terms'].items()),'objective_from_incumbent')
            elif s['model']['feasible']:self.check(False,'full_model_evidence_missing',str(model_path))
            self.graphs.append((s['time'],b,a));old=a
        for uid,row in self.starts.items():
            t=row['time'];candidates=[self.initial]
            for when,b,a in self.graphs:
                if when<t-TOL:candidates=[a]
                elif abs(when-t)<=TOL:candidates=[b,a]
            declared=set(row['dependency_tails'])
            self.check(any(declared=={d['active'][0] for g in x['groups'] for d in g['dependencies'] if d['active'][1]==uid} for x in candidates),'START_actual_dependencies:'+uid)
            for tail in declared:self.check(tail in self.ends and self.ends[tail]['time']<=t+TOL,'type2_END_before_START:'+uid)
        for name,term in [('solver_calls',lambda s:1),('new_author_calls',lambda s:s['new_author_calls']),
            ('reference_solver_seconds',lambda s:s['model']['reference_solver_seconds']),('new_solver_seconds',lambda s:s['new_solver_seconds']),
            ('reference_author_seconds',lambda s:s['model']['reference_author_seconds']),('new_author_seconds',lambda s:s['new_author_wall_seconds'])]:
            self.eq(e[name],sum(term(s) for s in e['solves']),'aggregate_'+name)

    def trajectory(self):
        e=self.e; horizon=e['simulation_end']; minimum=math.inf; collisions=[]
        for s in e['segments']:self.segments[s['agent']].append(s)
        for aid,initial in e['initial_positions'].items():
            ss=sorted(self.segments[aid],key=lambda s:s['t0']);self.segments[aid]=ss
            if horizon>TOL:self.check(bool(ss),'trajectory_exists:'+aid)
            cursor=0.;position=initial
            for s in ss:
                self.check(s['t1']>s['t0'],'positive_segment:'+aid)
                self.eq(s['t0'],cursor,'full_time_coverage:'+aid)
                self.check(math.dist(s['p0'],position)<TOL,'position_continuity:'+aid)
                if s['kind']!='MOVE':self.check(math.dist(s['p0'],s['p1'])<TOL,'hold_is_stationary:'+aid)
                if s['kind'] in ('MOVE','DISTURBANCE_WAIT'):
                    uid=s['vertex'];self.check(uid in self.starts,'motion_has_START:'+aid)
                    if uid in self.starts:
                        self.check(s['t0']>=self.starts[uid]['time']-TOL and (uid not in self.ends or s['t1']<=self.ends[uid]['time']+TOL),'motion_occurrence_interval:'+uid)
                        v=self.vs[uid];start=v['path'][0][:2];goal=v['path'][-1][:2]
                        total=math.dist(start,goal)
                        for p in (s['p0'],s['p1']):self.check(abs(math.dist(start,p)+math.dist(p,goal)-total)<TOL,'on_committed_edge:'+uid)
                if s['kind']=='GOAL_HOLD':self.check(aid in e['completion_times'] and s['t0']>=e['completion_times'][aid]-TOL,'goal_hold_after_completion:'+aid)
                cursor=s['t1'];position=s['p1']
            self.eq(cursor,horizon,'trajectory_end:'+aid)
            for v in self.byagent[aid]:
                uid=v['uid']
                if uid in self.ends:
                    ssuid=[s for s in ss if s['vertex']==uid and s['kind'] in ('MOVE','DISTURBANCE_WAIT')]
                    self.check(bool(ssuid),'completed_occurrence_has_motion:'+uid)
                    if ssuid:
                        self.check(math.dist(ssuid[-1]['p1'],v['path'][-1][:2])<TOL,'END_at_goal:'+uid)
                        self.eq(sum(s['t1']-s['t0'] for s in ssuid),self.ends[uid]['duration'],'full_move_time_account:'+uid)
        aids=sorted(e['initial_positions'])
        for i,a in enumerate(aids):
            for b in aids[i+1:]:
                initial=math.dist(e['initial_positions'][a],e['initial_positions'][b]);minimum=min(minimum,initial)
                if initial<e['config']['collision_tolerance']:collisions.append([a,b,0.,initial])
                # Independent interval sweep: breakpoint union then affine relative-distance minimum.
                aa=self.segments[a];bb=self.segments[b];ia=ib=0
                points=sorted({t for s in aa+bb for t in (s['t0'],s['t1'])})
                for lo,hi in zip(points,points[1:]):
                    while ia<len(aa)-1 and aa[ia]['t1']<=lo+1e-10:ia+=1
                    while ib<len(bb)-1 and bb[ib]['t1']<=lo+1e-10:ib+=1
                    if not aa or not bb:continue
                    p=point(aa[ia],lo);q=point(bb[ib],lo);p1=point(aa[ia],hi);q1=point(bb[ib],hi)
                    r=[x-y for x,y in zip(p,q)];delta=[(x-y)-z for x,y,z in zip(p1,q1,r)]
                    denom=sum(x*x for x in delta);alpha=max(0.,min(1.,-sum(x*y for x,y in zip(r,delta))/denom)) if denom else 0.
                    d=math.sqrt(sum((x+alpha*y)**2 for x,y in zip(r,delta)));minimum=min(minimum,d)
                    if d<e['config']['collision_tolerance']:collisions.append([a,b,lo+alpha*(hi-lo),d])
        collision_free=not collisions
        self.eq(e['collision_audit']['minimum_point_distance'],minimum if math.isfinite(minimum) else None,'independent_minimum_distance')
        self.check(bool(e['collision_audit']['collisions'])==bool(collisions),'independent_collision_presence')
        self.check(not e['success'] or collision_free,'success_requires_collision_free')
        self.stats.update(collision_free=collision_free,minimum_point_distance=minimum if math.isfinite(minimum) else None,collision_examples=collisions[:10])

    def disturbance_motion(self):
        truth=self.e['private_truth'];seed=truth['seed'];d=truth['disturbance'];profiles=truth['action_profiles']
        self.check(set(profiles)==set(self.starts),'one_profile_per_started_occurrence')
        def unit(*parts):
            token='|'.join(map(str,(seed,)+parts))
            return int(hashlib.sha256(token.encode()).hexdigest()[:16],16)/2**64
        for uid,start in self.starts.items():
            if uid not in profiles:continue
            v=self.vs[uid];aid=v['agent'];profile=profiles[uid]
            affected=unit('affected',aid)<d.get('affected_fraction',1.)
            factor=d.get('stable_factor',d.get('speed_factor',1.)) if affected else 1.
            if d.get('stable_factor_range') and affected:
                lo,hi=d['stable_factor_range'];factor=lo+(hi-lo)*unit('stable',aid)
            kind=d.get('kind',d.get('mode','stable'));pause=0.;fraction=d.get('pause_fraction',.35)
            if affected and kind in ('bounded_pause','pause','short_stop') and unit('pause',aid,v['index'])<d.get('pause_probability',1.):
                pause=d.get('pause_duration',1.)
                if d.get('pause_duration_range'):
                    lo,hi=d['pause_duration_range'];pause=lo+(hi-lo)*unit('pause_duration',aid,uid)
            if affected and kind in ('speed_shift','shift') and v['index']>=int(len(self.byagent[aid])*d.get('shift_action_fraction',.35)):
                factor=d.get('shifted_factor',.5)
            self.check(profile['agent']==aid and profile['vertex']==uid,'private_profile_identity')
            self.eq(profile['speed_factor'],factor,'registered_occurrence_speed')
            self.eq(profile['pause_duration'],pause,'registered_occurrence_pause')
            self.eq(profile['pause_fraction'],fraction,'registered_occurrence_pause_fraction')
            ss=[s for s in self.segments[aid] if s['vertex']==uid and s['kind'] in ('MOVE','DISTURBANCE_WAIT')]
            for s in ss:
                speed=math.dist(s['p0'],s['p1'])/(s['t1']-s['t0'])
                self.eq(speed,2*factor if s['kind']=='MOVE' else 0.,'actual_motion_speed:'+uid)
            if uid in self.ends:
                self.eq(self.ends[uid]['duration'],v['duration']/factor+pause,'complete_disturbed_duration:'+uid)
                self.eq(sum(s['t1']-s['t0'] for s in ss if s['kind']=='DISTURBANCE_WAIT'),pause,'complete_physical_pause:'+uid)

    def public_and_queries(self):
        e=self.e; used=0;queries={q['query_id']:q for q in e['queries']}
        self.check(len(queries)==len(e['queries']),'unique_query_id')
        for k,g in enumerate(e['gates']):
            s=g['public_snapshot'];t=g['capture_time'];gid=g['gate_index']
            self.check(gid==k and s['gate_index']==gid,'sequential_gate_index')
            self.eq(t,(gid+1)*e['config']['solve_period'],'fixed_gate_clock')
            self.eq(g['solve_time'],t+e['config']['query_latency'],'common_delivery_clock')
            self.check(set(s)==PUBLIC,'public_top_level_allowlist',list(set(s)-PUBLIC))
            self.eq(s['time'],t,'snapshot_clock')
            self.check([a['agent_id'] for a in s['agents']]==sorted(e['initial_positions']),'sorted_public_agents')
            if not g['dense_unbudgeted_reference']:
                self.eq(s['budget_remaining'],e['query_budget']-used,'remaining_budget')
                cap=e['config']['max_queries_per_gate']
                if cap is None:cap=max(1,math.ceil(e['agents']/8))
                self.eq(s['max_queries'],min(cap,e['query_budget']-used),'common_gate_cap')
            selected=g['selected'];self.check(len(selected)==len(set(selected)) and len(selected)<=s['max_queries'],'selection_cap')
            self.check(set(selected)<={a['agent_id'] for a in s['agents'] if a['query_eligible']},'query_eligible_selection')
            # Rebuild public graph influence using only delivered END and the
            # last adopted graph. The author's mutable first-head horizon
            # convention is recovered from actual whole-group changes.
            graph=self.initial;heads={x['uid']:x['dependencies'][0]['active'][1] for x in graph['groups']}
            for when,before,after in self.graphs:
                if when>t+1e-9:break
                prior={x['uid']:x for x in before['groups']}
                for x in after['groups']:
                    if x['dependencies']!=prior[x['uid']]['dependencies']:heads[x['uid']]=x['dependencies'][-1]['active'][1]
                graph=after
            status={}
            ratios={}
            for aid,vv in self.byagent.items():
                done=[self.ends[v['uid']] for v in vv if v['uid'] in self.ends and self.ends[v['uid']]['time']<=t+1e-9]
                ratios[aid]=sum(x['duration'] for x in done)/sum(x['nominal_duration'] for x in done) if done else 1.
                for v in vv:
                    uid=v['uid'];status[uid]='COMPLETED' if uid in self.ends and self.ends[uid]['time']<=t+1e-9 else 'IN_PROGRESS' if uid in self.starts and self.starts[uid]['time']<=t+1e-9 else 'STAGED'
            outgoing=defaultdict(set);incoming=defaultdict(set);influence=defaultdict(int);ngroups=0
            for group in graph['groups']:
                dd=group['dependencies']
                for dep in dd:
                    tail,head=dep['active'];incoming[head].add(tail)
                    if status[tail]!='COMPLETED' and status[head]!='COMPLETED':outgoing[tail].add(self.vs[head]['agent'])
                switchable=all(d['reverse'] is not None and status[d['forward'][1]]=='STAGED' and status[d['reverse'][1]]=='STAGED' for d in dd)
                u=heads[group['uid']];estimate=0.
                while self.vs[u]['predecessor'] is not None and status[u]=='STAGED':
                    u=self.vs[u]['predecessor'];v=self.vs[u]
                    estimate+=self.ends[u]['duration'] if status[u]=='COMPLETED' else v['duration']*ratios[v['agent']]
                if switchable and estimate<e['config']['horizon']:
                    ngroups+=1;touched={self.vs[u]['agent'] for d in dd for edge in (d['forward'],d['reverse']) if edge for u in edge}
                    for aid in touched:influence[aid]+=1
            self.eq(s['switchable_groups'],ngroups,'public_switchable_groups')
            if self.policy and not g['override']:
                expected=policy_selection(s,self.policy,self.model)
                self.check(expected is not None,'policy_model_available')
                self.check(selected==expected,'independent_policy_selection',{'gate':gid,'expected':expected,'actual':selected})
            for a in s['agents']:
                aid=a['agent_id'];self.check(set(a)==AGENT_PUBLIC,'public_agent_allowlist',list(set(a)-AGENT_PUBLIC))
                vv=self.byagent[aid];done=[self.ends[v['uid']] for v in vv if v['uid'] in self.ends and self.ends[v['uid']]['time']<=t+1e-9]
                remaining=[v for v in vv if v['uid'] not in self.ends or self.ends[v['uid']]['time']>t+1e-9]
                v=remaining[0] if remaining else None;uid=v['uid'] if v else None
                start=self.starts.get(uid);active=start is not None and start['time']<=t+1e-9
                self.check(a['current_vertex']==uid,'snapshot_current_vertex:'+aid)
                self.check(a['status']==('COMPLETED' if v is None else 'IN_PROGRESS' if active else 'STAGED'),'snapshot_status:'+aid)
                self.check(a['query_eligible']==active,'snapshot_eligibility:'+aid)
                self.eq(a['outgoing_blocked_agents'],len(outgoing[uid]),'public_outgoing_blocked:'+aid)
                self.eq(a['upcoming_switchable_influence'],influence[aid],'public_upcoming_influence:'+aid)
                self.check(a['blocked']==bool(v is not None and not active and any(status[u]!='COMPLETED' for u in incoming[uid])),'public_blocked:'+aid)
                ratio=sum(x['duration'] for x in done)/sum(x['nominal_duration'] for x in done) if done else 1.
                ratios=[x['duration']/x['nominal_duration'] for x in done]
                var=statistics.pvariance(ratios) if len(ratios)>1 else 0.;cv=math.sqrt(var)/statistics.mean(ratios) if ratios else 0.
                delivered=[q for q in e['queries'] if q['agent']==aid and q['delivered_at']<=t+1e-9 and q['delivery_status']!='pending']
                current=[q for q in delivered if q['vertex']==uid and q['delivery_status']=='accepted']
                latest=max(current,key=lambda q:q['captured']) if current else None
                nominal=v['duration'] if v else 0.;elapsed=t-start['time'] if active else 0.
                progress=min(1.,max(0.,elapsed/(nominal*ratio))) if active else 0. if v else 1.
                age=t-latest['captured'] if latest else None
                if latest:progress=min(1.,latest['progress']+age/(nominal*ratio))
                expected={'elapsed':elapsed,'nominal_duration':nominal,'history_ratio':ratio,'history_count':len(done),
                    'history_variance':var,'history_cv':cv,'progress_estimate':progress,'remaining_estimate':(1-progress)*nominal*ratio,
                    'last_measurement_age':age,'last_observed_residual':nominal*(1-latest['progress']) if latest else None,
                    'measurement_count':len(delivered),'downstream_nominal':sum(x['duration'] for x in remaining),
                    'wait_elapsed':t-(done[-1]['time'] if done else 0.) if v and not active else 0.}
                for field,val in expected.items():self.eq(a[field],val,'public_'+field+':'+aid)
            gq=[q for q in e['queries'] if q['gate_index']==gid]
            self.check([q['agent'] for q in gq]==selected,'capture_matches_selection')
            for q in gq:
                body={x:v for x,v in q.items() if x not in ('body_sha256','payload_bytes','delivery_status')}
                self.check(canon(body)==q['body_sha256'],'query_body_hash')
                self.eq(len(json.dumps(dict(body,body_sha256=q['body_sha256']),sort_keys=True).encode()),q['payload_bytes'],'payload_byte_count')
                self.eq(q['captured'],t,'query_capture_clock');self.eq(q['delivered_at'],g['solve_time'],'query_delivery_clock')
                self.check(q['world_geometry_binding']==e['geometry_binding'],'query_geometry_binding')
                a=next(a for a in s['agents'] if a['agent_id']==q['agent'])
                self.check(q['vertex']==a['current_vertex'],'query_occurrence')
                uid=q['vertex'];v=self.vs[uid]
                candidates=[s for s in self.segments[q['agent']] if s['t0']<=t+1e-9 and s['t1']>=t-1e-9]
                self.check(bool(candidates),'capture_has_physical_segment')
                if candidates:
                    pos=point(candidates[-1],t);start=v['path'][0][:2];goal=v['path'][-1][:2]
                    self.eq(q['progress'],math.dist(start,pos)/math.dist(start,goal),'captured_physical_progress')
                de=[x for x in self.evs if x['kind']=='POSITION_DELIVER' and x['query_id']==q['query_id']]
                if q['delivery_status']=='pending':self.check(not de and q['delivered_at']>e['simulation_end']-TOL,'pending_query')
                else:
                    stale=uid in self.ends and self.ends[uid]['time']<=q['delivered_at']+1e-9
                    self.check(q['delivery_status']==('stale_occurrence' if stale else 'accepted'),'stale_occurrence_identity')
                    self.check(len(de)==1 and de[0]['status']==q['delivery_status'],'unique_delivery')
                    if de:self.eq(de[0]['time'],q['delivered_at'],'actual_delivery_time')
            used+=len(selected)
        self.eq(e['query_count'],used,'total_queries');self.eq(e['query_payload_bytes'],sum(q['payload_bytes'] for q in e['queries']),'total_query_bytes')
        self.check(e['dense_unbudgeted_reference'] or used<=e['query_budget'],'episode_budget')
        self.stats['queries_from_captures']=used

    def run(self):
        for stage in [self.source_and_input,self.events_and_outcomes,self.graph_adoptions,self.trajectory,self.disturbance_motion,self.public_and_queries]:
            try:stage()
            except Exception as exc:self.check(False,'auditor_stage_exception:'+stage.__name__,repr(exc))
        self.limits += ['Source pins are checked against available source files; this cannot prove inaccessible build or runtime state.',
            'Author within_horizon cached-head qualification is source-enforced; all changed candidate heads and DAG are independently checked.',
            'Private truth is used only to audit final logs; the verifier is never called as an online policy.',
            'Geometry is continuous point motion, not nonzero body or acceleration certification.']
        return {'schema':'r18-independent-episode-audit-v1','passed':not self.errors,
            'episode':str(self.path.resolve()),'episode_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),
            'scientific_episode_reruns':0,'engine_or_policy_imported':False,'checks':self.checks,
            'errors':self.errors,'stats':self.stats,'recorded_status':self.e['status'],
            'recorded_success':self.e['success'],'limitations':self.limits}


def main():
    p=argparse.ArgumentParser();p.add_argument('--episode',required=True);p.add_argument('--case');p.add_argument('--model')
    p.add_argument('--policy');p.add_argument('--output',required=True);args=p.parse_args()
    report=Auditor(args.episode,args.case,args.policy,args.model).run()
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','checks','errors','stats']}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
