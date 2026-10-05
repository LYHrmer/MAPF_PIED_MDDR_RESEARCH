"""Verbatim R18 independent physical/math checks; see BASE_PROVENANCE.json.
No R18 schema/source/graph/public audit method is included or called.
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
