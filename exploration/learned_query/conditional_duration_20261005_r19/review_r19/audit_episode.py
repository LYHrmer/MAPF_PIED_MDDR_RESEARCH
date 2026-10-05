"""Independent R19 CAS/predictor/structure audit; no engine or solver imports.

Reuses the frozen R18 auditor's event, physical-path and disturbance mathematics.
R19 schema, receipts, CAS, prediction and structure are checked explicitly.
"""
import sys
sys.dont_write_bytecode = True
import argparse
from collections import defaultdict
import copy
import gzip
import hashlib
import heapq
import importlib.util
import json
import math
from pathlib import Path
import statistics
from scipy.special import log_ndtr

ROOT=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_structural_20261005_r19')
R18=ROOT.parent/'sadg_benchmark_20261005_r18'
BUNDLE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r18_independent_physical_auditor',Path(__file__).with_name('physical_math.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
canon,read,close,point,TOL=base.canon,base.read,base.close,base.point,base.TOL
PUBLIC=base.PUBLIC|{'solve_period','public_schema'}
AGENT_PUBLIC=base.AGENT_PUBLIC|{'legal_boundary_group_count','legal_boundary_group_ids',
    'boundary_path_time_min','blocked_frontier_count','blocked_frontier_agents',
    'direct_blocked_frontier_count','structural_eligible','prediction_provider'}


class CAS:
    def __init__(self,root):self.root=Path(root);self.cache={};self.files={};self.sizes={}
    def verify(self,ref):
        assert ref['schema']=='r19-cas-ref-v1'
        key=ref['sha256'];relative=f'objects/{key[:2]}/{key}.json.gz'
        assert ref['path']==relative
        if key not in self.sizes:
            p=self.root/relative;blob=p.read_bytes();raw=gzip.decompress(blob)
            assert hashlib.sha256(raw).hexdigest()==key and len(raw)==ref['raw_bytes']
            self.sizes[key]=len(raw);self.files[str(p)]=hashlib.sha256(blob).hexdigest()
        assert self.sizes[key]==ref['raw_bytes']
        return key
    def get(self,ref):
        assert ref['schema']=='r19-cas-ref-v1'
        key=ref['sha256'];relative=f'objects/{key[:2]}/{key}.json.gz'
        assert ref['path']==relative
        if key not in self.cache:
            p=self.root/relative;blob=p.read_bytes();raw=gzip.decompress(blob)
            assert hashlib.sha256(raw).hexdigest()==key and len(raw)==ref['raw_bytes']
            obj=json.loads(raw);assert canon(obj)==key
            self.cache[key]=obj;self.sizes[key]=len(raw);self.files[str(p)]=hashlib.sha256(blob).hexdigest()
        assert self.sizes[key]==ref['raw_bytes']
        return self.cache[key]
    def graph(self,ref):
        value=self.get(ref);assert value['schema']=='r19-graph-split-v1'
        out=copy.deepcopy(self.get(value['topology']))
        vs,gs=self.get(value['vertex_state']),self.get(value['group_state'])
        assert len(vs)==len(out['vertices']) and len(gs)==len(out['groups'])
        for v,state in zip(out['vertices'],vs):
            assert len(state)==3
            v.update(dict(zip(['status','duration','progress'],state)))
        for g,state in zip(out['groups'],gs):
            assert len(state)==3 and len(state[2])==len(g['dependencies'])
            g['switchable'],g['within_horizon']=state[:2]
            for dep,ds in zip(g['dependencies'],state[2]):
                bit,index=ds;dep['b']=bit
                if isinstance(index,dict):assert set(index)=={'literal'};dep['active']=index['literal']
                else:assert index in [0,1];dep['active']=dep['forward'] if index==0 else dep['reverse']
        assert canon(out)==value['full_sha256']
        return out


def estimate(context,model,mode):
    """Separate public-feature and scipy survival implementation."""
    history=context['completed_history'];nominal=context['nominal_duration'];age=context['elapsed']
    q=[h['duration']/h['nominal_duration'] for h in history]
    whole=sum(h['duration'] for h in history)/sum(h['nominal_duration'] for h in history) if q else 1.
    recent=history[-4:];r4=sum(h['duration'] for h in recent)/sum(h['nominal_duration'] for h in recent) if q else 1.
    ewma=1.
    for r in q:ewma=.7*ewma+.3*r
    cv=statistics.pstdev(q)/statistics.mean(q) if q else 0.
    ratios={'nominal':1.,'all_history':whole,'recent4':r4,'ewma03':ewma}
    if mode in ratios:return max(0.,nominal*ratios[mode]-age),ratios[mode]
    if mode=='learned':
        x=[math.log(nominal),math.log1p(len(q)),math.log(whole),math.log(r4),math.log(ewma),
            math.log(q[-1] if q else 1.),cv,math.log(r4)-math.log(whole)]
        mu=model['intercept']+sum((a-b)/c*d for a,b,c,d in zip(x,model['mean'],model['scale'],model['coefficients']))
        sigma=model['sigma']
    elif mode=='constant_survival':mu=model['constant']['mu'];sigma=model['constant']['sigma']
    elif mode in ['all_history_survival','recent4_survival','ewma03_survival']:
        key=mode[:-9];sigma=model['baseline_sigma'][key];mu=math.log(ratios[key])-.5*sigma*sigma
    else:raise ValueError('Unknown registered predictor mode '+str(mode))
    mu=min(20.,max(-20.,mu));sigma=min(5.,max(.05,sigma));ratio=math.exp(mu+.5*sigma*sigma)
    if age<=0:return nominal*ratio,ratio
    mu+=math.log(nominal);z=(math.log(age)-mu)/sigma
    total_log=mu+.5*sigma*sigma+float(log_ndtr(sigma-z))-float(log_ndtr(-z))
    return max(1e-9,age*math.expm1(max(0.,total_log-math.log(age)))),ratio


def structural(graph,agents):
    vertices={v['uid']:v for v in graph['vertices']};edges=base.all_edges(graph)
    outgoing=defaultdict(set)
    for tail,head in edges:
        if vertices[tail]['status']!='COMPLETED' and vertices[head]['status']!='COMPLETED':outgoing[tail].add(head)
    boundaries={g['uid']:{d[k][0] for d in g['dependencies'] for k in ['forward','reverse']}
        for g in graph['groups'] if g['switchable'] and g['within_horizon']}
    blocked={a['current_vertex']:a['agent_id'] for a in agents if a['blocked']}
    result={}
    # DAG relaxation, independent of the engine's heap-based shortest path.
    degree={u:0 for u in vertices}
    for tail in outgoing:
        for head in outgoing[tail]:degree[head]+=1
    queue=[u for u,d in degree.items() if d==0];order=[]
    while queue:
        u=queue.pop();order.append(u)
        for v in outgoing[u]:
            degree[v]-=1
            if not degree[v]:queue.append(v)
    assert len(order)==len(vertices)
    for a in agents:
        source=a['current_vertex'];distance={}
        if source:
            v=vertices[source];distance[source]=v['duration']*(1-v['progress']) if v['status']=='IN_PROGRESS' else v['duration']
        for u in order:
            if u not in distance:continue
            for v in outgoing[u]:distance[v]=min(distance.get(v,math.inf),distance[u]+vertices[v]['duration'])
        reached={g:min(distance[u] for u in tails if u in distance) for g,tails in boundaries.items() if tails&distance.keys()}
        frontier=sorted({aid for u,aid in blocked.items() if u in distance and aid!=a['agent_id']})
        direct={blocked[u] for u in outgoing[source] if u in blocked and blocked[u]!=a['agent_id']}
        result[a['agent_id']]=dict(legal_boundary_group_count=len(reached),legal_boundary_group_ids=sorted(reached),
            boundary_path_time_min=min(reached.values(),default=None),blocked_frontier_count=len(frontier),
            blocked_frontier_agents=frontier,direct_blocked_frontier_count=len(direct),
            structural_eligible=bool(a['query_eligible'] and (reached or frontier)))
    return result


class Auditor(base.Auditor):
    def __init__(self,episode,case=None,policy=None,model=None,root=None,store=None,path_maps=None,bundle=None):
        self.root=Path(root or ROOT).resolve();self.r18=self.root.parent/'sadg_benchmark_20261005_r18'
        self.bundle=Path(bundle or BUNDLE).resolve()
        self.path_maps={str(ROOT):str(self.root),str(R18):str(self.r18)}
        self.path_maps.update(path_maps or {})
        self.path=Path(episode);self.e=read(self.path)
        assert self.e['schema']=='r19-sadg-episode-v1','R19 schema required; no schema substitution'
        self.store=CAS(store or self.resolve_path(self.e['evidence_store']));self.initial=self.store.graph(self.e['initial_graph_ref'])
        self.e['initial_graph']=self.initial
        for g in self.e['gates']:g['public_snapshot']=self.store.get(g['public_snapshot_ref'])
        self.predictions=self.store.get(self.e['prediction_evidence_ref'])
        self.model=self.store.get(self.e['predictor_model_ref']) if self.e.get('predictor_model_ref') else None
        self.case=read(case) if case else None;self.policy=policy
        self.errors=[];self.checks=0;self.limits=[];self.stats={};self.evs=self.e['events']
        self.vs={v['uid']:v for v in self.initial['vertices']};self.byagent=defaultdict(list)
        for v in self.initial['vertices']:self.byagent[v['agent']].append(v)
        for vv in self.byagent.values():vv.sort(key=lambda v:v['index'])
        self.starts={};self.ends={};self.graphs=[];self.segments=defaultdict(list)
        self.heads={g['uid']:g['dependencies'][0]['active'][1] for g in self.initial['groups']}
        self.dependencies={};self.checked_prediction_keys=set()

    def qualification(self,graph,heads,label):
        vertices={v['uid']:v for v in graph['vertices']}
        for group in graph['groups']:
            allowed=all(d['reverse'] is not None and vertices[d['forward'][1]]['status']=='STAGED' and
                vertices[d['reverse'][1]]['status']=='STAGED' for d in group['dependencies'])
            self.check(group['switchable']==allowed,label+':all_head_qualification')
            uid=heads[group['uid']];duration=0.
            while vertices[uid]['predecessor'] is not None and vertices[uid]['status']=='STAGED':
                uid=vertices[uid]['predecessor'];duration+=vertices[uid]['duration']
            self.check(group['within_horizon']==(duration<self.e['config']['horizon']),label+':author_cached_head_horizon')

    def resolve_path(self,path):
        path=Path(path)
        for old,new in sorted(self.path_maps.items(),key=lambda x:-len(x[0])):
            try:return Path(new)/path.relative_to(old)
            except ValueError:pass
        return path

    def file_hash(self,path):
        path=self.resolve_path(path);value=hashlib.sha256(path.read_bytes()).hexdigest();self.dependencies[str(path)]=value;return value

    def source_and_input(self):
        e=self.e;receipt_path=self.path.parent/'RUN_RECEIPT.json'
        if receipt_path.exists():
            receipt=read(receipt_path);self.file_hash(receipt_path);spec=receipt['spec']
            self.check(self.file_hash(self.path)==receipt['episode_sha256'],'run_receipt_hash')
            self.check(canon(spec)==receipt['spec_sha256']==e['benchmark']['spec_sha256'],'spec_hash')
            self.check(spec['config']==e['config'],'registered_config')
            self.check(spec['disturbance']==e['private_truth']['disturbance'] and spec['seed']==e['private_truth']['seed'],'registered_world')
            self.check(receipt['status']==e['status'] and receipt['success']==e['success'],'receipt_outcome')
            reg=read(self.root/'EXPERIMENT_REGISTRATION.json');self.file_hash(self.root/'EXPERIMENT_REGISTRATION.json')
            self.check(reg['registered_utc']<=receipt['started_utc']<=receipt['finished_utc'],'registration_clock')
            self.check(reg['source_pins']==spec['source_pins'],'source_contract')
            for name,h in spec['source_pins'].items():
                path=self.r18/name.split('/')[-1] if name.startswith('inherited:') else self.root/name
                self.check(self.file_hash(path)==h,'scientific_source:'+name)
            if spec.get('predictor_mode') is not None:self.check(spec['predictor_mode']==e['predictor_mode'],'predictor_mode')
            if self.policy is None:self.policy=spec.get('query_policy')
            if self.case is None:
                cp=Path(spec['case_path']);cp=cp if cp.is_absolute() else self.root/cp
                self.case=read(self.resolve_path(cp));self.check(self.file_hash(cp)==spec['case_sha256'],'case_file_hash')
            if self.model:
                frozen=read(self.bundle/'MODEL_FREEZE.json');self.file_hash(self.bundle/'MODEL_FREEZE.json')
                self.check(frozen['frozen_utc']<=receipt['started_utc'],'model_before_execution')
                self.check(self.file_hash(self.bundle/'MODEL.json')==frozen['model_sha256'],'frozen_model_file')
                self.check(self.file_hash(self.bundle/'predictor.py')==frozen['predictor_sha256'],'frozen_predictor_code')
                self.check(canon(self.model)==canon(read(self.bundle/'MODEL.json')),'actual_model_matches_freeze')
                self.check(spec['model_sha256']==frozen['model_sha256'] and spec['predictor_sha256']==frozen['predictor_sha256'],'registered_predictor_identity')
        else:self.limits.append('No benchmark RUN_RECEIPT: this is a pilot, not registered scientific-matrix acceptance.')
        for name,h in e['source_hashes'].items():
            if name not in ['python-mip-version','cbcbox-version']:self.check(self.file_hash(name)==h,'author_source:'+name)
        for name,h in e['adapter_source_hashes'].items():self.check(self.file_hash(self.root/name)==h,'adapter_source:'+name)
        self.check(self.file_hash(self.r18/'engine.py')==e['r18_engine_sha256'],'frozen_inheritance')
        self.check(self.file_hash(self.root/'engine.py')==e['engine_sha256'],'engine_hash')
        self.check(e['public_schema_sha256']==e['adapter_source_hashes']['PUBLIC_SCHEMA.json'],'public_schema_hash')
        self.graph_check(self.initial,'initial')
        for aid,vv in self.byagent.items():
            for i,v in enumerate(vv):
                duration=sum(math.dist(a[:2],b[:2]) for a,b in zip(v['path'],v['path'][1:]))/2
                self.eq(v['duration'],duration,'original_nominal:'+v['uid']);self.check(duration>0,'positive_move')
                self.check(v['predecessor']==(vv[i-1]['uid'] if i else None),'type1_previous')
                self.check(v['successor']==(vv[i+1]['uid'] if i+1<len(vv) else None),'type1_next')
                distinct=[]
                for p in v['path']:
                    if not distinct or p[:2]!=distinct[-1]:distinct.append(p[:2])
                self.check(len(distinct)==2,'single_physical_edge')
        if self.case:
            sol=self.case.get('solution',self.case);schedule=sol['schedule']
            dims=self.case.get('dimensions',{'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}})
            if 'dimensions' not in dims:dims={'dimensions':dims}
            self.check(canon(dict(schedule=schedule,dimensions=dims))==e['geometry_binding'],'geometry_binding')
            d=dims['dimensions'];transform=lambda p:[d['resolution']*p['y']+d['x_offset'],-d['resolution']*p['x']+d['y_offset']]
            self.check(set(schedule)==set(e['initial_positions']),'input_agent_set')
            for aid,path in schedule.items():
                expected=[]
                for p in path:
                    q=transform(p)
                    if not expected or q!=expected[-1]:expected.append(q)
                actual=[v['path'][0][:2] for v in self.byagent[aid]]
                actual.append(self.byagent[aid][-1]['path'][-1][:2] if self.byagent[aid] else e['initial_positions'][aid])
                self.check(actual==expected,'complete_original_path:'+aid)
        else:self.limits.append('No original input case supplied for pilot geometry binding.')

    def check_prediction(self,key):
        if key in self.checked_prediction_keys:return self.predictions[key]
        p=self.predictions[key];self.check(canon(p)==key,'prediction_content_hash')
        aid,uid,t=p['agent'],p['vertex'],p['time'];c=p['context'];v=self.vs[uid]
        self.check(set(c)=={'status','nominal_duration','elapsed','completed_history'},'predictor_whitelist')
        self.check(v['agent']==aid,'predictor_occurrence_owner')
        done=[x for x in self.e['delivered_end_history'].get(aid,[]) if x['delivered']<=t+1e-9]
        expected=[{k:h[k] for k in ['nominal_duration','duration','start','end','delivered']} for h in done]
        self.check(c['completed_history']==expected,'predictor_delivered_END_history')
        self.eq(c['nominal_duration'],v['duration'],'predictor_original_nominal')
        if c['status']=='IN_PROGRESS':
            self.check(uid in self.starts and self.starts[uid]['time']<=t+TOL,'predictor_active_START')
            self.eq(c['elapsed'],t-self.starts[uid]['time'],'predictor_age_since_START')
            self.check(uid not in self.ends or self.ends[uid]['time']>t-1e-9,'predictor_active_survival')
        else:
            self.check(c['status']=='STAGED','predictor_status')
            self.eq(c['elapsed'],0.,'predictor_wait_excluded')
            self.check(uid not in self.starts or self.starts[uid]['time']>=t-TOL,'predictor_staged_not_started')
        residual,ratio=estimate(c,self.model,self.e['predictor_mode'])
        self.eq(p['predictor_output']['remaining_time'],residual,'conditional_remaining_independent')
        self.eq(p['predictor_output']['future_duration_ratio'],ratio,'unconditional_future_ratio')
        available=[q for q in self.e['queries'] if q['agent']==aid and q['vertex']==uid and
            q['delivery_status']=='accepted' and q['delivered_at']<=t+1e-9]
        latest=max(available,key=lambda q:q['captured']) if available else None
        if latest:
            observed={k:latest[k] for k in ['vertex','captured','delivered_at','progress','query_id']}
            self.check(p['delivered_position']==observed,'latest_delivered_current_POSITION')
            hr=sum(h['duration'] for h in done)/sum(h['nominal_duration'] for h in done) if done else 1.
            residual=max(0.,(1-latest['progress'])*v['duration']*hr-(t-latest['captured']))
            self.check(p['provider']=='position_linear_all_history','position_provider')
        else:
            self.check(p['delivered_position'] is None and p['provider']=='end_history_predictor','END_only_provider')
        self.eq(p['remaining_time'],residual,'actual_fused_remaining')
        self.eq(p['future_duration_ratio'],ratio,'preserved_future_ratio')
        duration=max(v['duration']*ratio,residual,1e-9)
        progress=1-residual/duration if c['status']=='IN_PROGRESS' else 0.
        self.eq(p['encoded_duration'],duration,'author_encoded_duration')
        self.eq(p['encoded_progress'],progress,'author_encoded_progress')
        if c['status']=='IN_PROGRESS':self.eq(duration*(1-progress),residual,'author_effective_remaining')
        self.checked_prediction_keys.add(key);return p

    def bind_graph_predictions(self,graph,keys,t,label):
        vv={v['uid']:v for v in graph['vertices']}
        for aid,key in keys.items():
            p=self.check_prediction(key);self.eq(p['time'],t,label+':prediction_time')
            self.check(p['agent']==aid,label+':prediction_owner')
            for v in self.byagent[aid]:
                actual=vv[v['uid']];status=actual['status']
                if status=='COMPLETED':
                    duration=self.ends[v['uid']]['duration'];progress=1.
                elif status=='IN_PROGRESS':
                    self.check(v['uid']==p['vertex'],label+':current_prediction_occurrence')
                    duration=p['encoded_duration'];progress=p['encoded_progress']
                else:duration=v['duration']*p['future_duration_ratio'];progress=0.
                self.eq(actual['duration'],duration,label+':consumed_duration')
                self.eq(actual['progress'],progress,label+':consumed_progress')
        for v in graph['vertices']:
            if v['status']!='COMPLETED':self.check(v['agent'] in keys,label+':all_live_agents_predicted')
            else:
                self.eq(v['duration'],self.ends[v['uid']]['duration'],label+':completed_actual_duration')
                self.eq(v['progress'],1.,label+':completed_progress')
        for aid,key in keys.items():
            p=self.predictions[key]
            self.check(vv[p['vertex']]['status']==p['context']['status'],label+':context_graph_status')

    def graph_adoptions(self):
        old=self.initial;e=self.e;heads=dict(self.heads)
        for s in e['solves']:
            receipt=self.path.parent/'solves'/f"{s['gate_index']:05d}"/'receipt.json'
            self.check(receipt.is_file() and read(receipt)==s,'solve_receipt');self.file_hash(receipt)
            b=self.store.graph(s['before_ref']);a=self.store.graph(s['after_ref']);candidate=self.store.graph(s['candidate_ref'])
            self.check(canon(b)==s['before_sha256'] and canon(a)==s['after_sha256'],'solve_graph_hash')
            semantic=canon(dict(graph=b,horizon=e['config']['horizon'],source=e['source_hashes'],
                semantics='r18-original-author-duration-progress-v1',author_max_seconds=60))
            self.check(semantic==s['semantic_key'],'R19_semantic_key')
            self.graph_check(b,'before');self.graph_check(a,'after')
            self.qualification(b,heads,'solve_before')
            self.check(b['type1']==self.initial['type1'],'original_type1_preserved')
            for v in b['vertices']:
                self.check({k:x for k,x in v.items() if k not in ['status','duration','progress']}==
                    {k:x for k,x in self.vs[v['uid']].items() if k not in ['status','duration','progress']},'static_vertex_identity')
            self.bind_graph_predictions(b,s['prediction_keys'],s['time'],'solve')
            self.check(b['vertices']==a['vertices'] and b['type1']==a['type1'],'adoption_preserves_vertices_type1')
            gb={g['uid']:g for g in b['groups']};ga={g['uid']:g for g in a['groups']};go={g['uid']:g for g in old['groups']}
            self.check(set(gb)==set(ga)==set(go),'group_conservation');vv={v['uid']:v for v in b['vertices']}
            for uid,g in gb.items():
                self.check(g['dependencies']==go[uid]['dependencies'],'parent_directions')
                self.check(len(g['dependencies'])==len(ga[uid]['dependencies']),'dependency_count')
                changes=[]
                for x,y in zip(g['dependencies'],ga[uid]['dependencies']):
                    self.check(x['forward']==y['forward'] and x['reverse']==y['reverse'],'paired_relations_preserved')
                    changes.append(x['active']!=y['active'])
                if any(changes):
                    self.check(all(changes) and g['switchable'] and g['within_horizon'],'qualified_whole_group_switch')
                    self.check(all(d['reverse'] and vv[d['forward'][1]]['status']=='STAGED' and vv[d['reverse'][1]]['status']=='STAGED' for d in g['dependencies']),'all_candidate_heads_staged')
                    heads[uid]=ga[uid]['dependencies'][-1]['active'][1]
            self.qualification(a,heads,'solve_after')
            self.check(sorted(s['active_commitments'])==sorted(v['uid'] for v in b['vertices'] if v['status']=='IN_PROGRESS'),'active_commitments')
            if not s['adopted']:self.check(b==a,'rejected_candidate_exact_parent')
            else:self.check(a==candidate,'adopted_actual_candidate')
            if not s['model']['feasible'] or s['model'].get('error') or not s['guard']['passed']:
                self.check(not s['adopted'] and b==a,'failed_candidate_never_installed')
            if s['model_ref'] is not None:
                self.check(self.store.verify(s['model_ref'])==s['model']['model_sha256'],'all_candidate_payload_hash')
            else:self.check(s['model']['status']=='NO_MODEL','payload_required_if_model_existed')
            self.store.get(s['author_log_ref'])
            if s['cache_reused']:
                self.eq(s['new_author_calls'],0,'cache_no_author_call');self.eq(s['new_solver_seconds'],0,'cache_no_solver_time')
            if s.get('cache_source'):
                cache=read(self.resolve_path(s['cache_source']));self.file_hash(s['cache_source'])
                for k in ['semantic_key','before_sha256','model','model_ref','candidate_ref','after_ref','adopted']:
                    self.check(cache[k]==s[k],'cache_receipt:'+k)
            self.graphs.append((s['time'],b,a));old=a
        for uid,row in self.starts.items():
            t=row['time'];candidates=[self.initial]
            for when,b,a in self.graphs:
                if when<t-TOL:candidates=[a]
                elif abs(when-t)<=TOL:candidates=[b,a]
            declared=set(row['dependency_tails'])
            self.check(any(declared=={d['active'][0] for g in graph['groups'] for d in g['dependencies'] if d['active'][1]==uid} for graph in candidates),'START_actual_dependencies')
            for tail in declared:self.check(tail in self.ends and self.ends[tail]['time']<=t+TOL,'dependency_END_before_START')
        for name,term in [('solver_calls',lambda s:1),('new_author_calls',lambda s:s['new_author_calls']),
            ('reference_solver_seconds',lambda s:s['model']['reference_solver_seconds']),('new_solver_seconds',lambda s:s['new_solver_seconds']),
            ('reference_author_seconds',lambda s:s['model']['reference_author_seconds']),('new_author_seconds',lambda s:s['new_author_wall_seconds'])]:
            self.eq(e[name],sum(term(s) for s in e['solves']),'aggregate_'+name)
        self.limits.append('All candidate model/CAS hashes are bound here. Full constraint/bound/integrality residual reconstruction is the separate solver-payload audit, not claimed by this report.')

    def public_and_queries(self):
        e=self.e;used=0
        self.check(len({q['query_id'] for q in e['queries']})==len(e['queries']),'unique_query_ids')
        self.eq(e['query_budget'],e['config']['query_budget'],'registered_query_budget')
        for index,g in enumerate(e['gates']):
            s=g['public_snapshot'];t=g['capture_time'];gid=g['gate_index']
            self.check(gid==index and s['gate_index']==gid,'sequential_gate_identity')
            self.check([a['agent_id'] for a in s['agents']]==sorted(e['initial_positions']),'public_agent_set')
            self.check(set(s)==PUBLIC and s['public_schema']=='r19-history-structure-v1','R19_public_schema')
            self.eq(s['solve_period'],e['config']['solve_period'],'public_solve_period')
            self.eq(t,(gid+1)*e['config']['solve_period'],'fixed_gate_clock')
            self.eq(g['solve_time'],t+e['config']['query_latency'],'common_query_delivery_clock')
            self.eq(s['time'],t,'snapshot_clock');self.eq(s['budget_remaining'],e['query_budget']-used,'query_budget_remaining')
            cap=e['config']['max_queries_per_gate'] or max(1,math.ceil(e['agents']/8))
            self.eq(s['max_queries'],min(cap,e['query_budget']-used),'query_cap')
            graph=self.store.graph(g['capture_graph_ref']);keys=g['prediction_keys']
            self.graph_check(graph,'capture_graph');self.bind_graph_predictions(graph,keys,t,'capture')
            parent=self.initial;heads=dict(self.heads)
            for when,before,after in self.graphs:
                if when>t+1e-9:break
                old={group['uid']:group for group in before['groups']}
                for group in after['groups']:
                    if group['dependencies']!=old[group['uid']]['dependencies']:
                        heads[group['uid']]=group['dependencies'][-1]['active'][1]
                parent=after
            self.check(graph['type1']==self.initial['type1'],'capture_original_type1')
            self.check([g['dependencies'] for g in graph['groups']]==[g['dependencies'] for g in parent['groups']],'capture_actual_parent_directions')
            self.qualification(graph,heads,'capture')
            vertices={v['uid']:v for v in graph['vertices']};incoming=defaultdict(set);outgoing=defaultdict(set);influence=defaultdict(set)
            for uid,v in vertices.items():
                status='COMPLETED' if uid in self.ends and self.ends[uid]['time']<=t+1e-9 else 'IN_PROGRESS' if uid in self.starts and self.starts[uid]['time']<=t+1e-9 else 'STAGED'
                self.check(v['status']==status,'capture_actual_status')
            for group in graph['groups']:
                allowed=all(d['reverse'] is not None and vertices[d['forward'][1]]['status']=='STAGED' and vertices[d['reverse'][1]]['status']=='STAGED' for d in group['dependencies'])
                self.check(group['switchable']==allowed,'capture_all_head_switchability')
                for d in group['dependencies']:
                    tail,head=d['active'];incoming[head].add(tail)
                    if vertices[tail]['status']!='COMPLETED' and vertices[head]['status']!='COMPLETED':outgoing[tail].add(vertices[head]['agent'])
                if group['switchable'] and group['within_horizon']:
                    for d in group['dependencies']:
                        for edge in [d['forward'],d['reverse']]:
                            for u in edge:influence[vertices[u]['agent']].add(group['uid'])
            self.eq(s['switchable_groups'],sum(g['switchable'] and g['within_horizon'] for g in graph['groups']),'public_switchable_group_count')
            for a in s['agents']:
                self.check(set(a)==AGENT_PUBLIC,'R19_agent_whitelist')
                aid=a['agent_id'];done=[h for h in e['delivered_end_history'].get(aid,[]) if h['delivered']<=t+1e-9]
                remain=[v for v in self.byagent[aid] if v['uid'] not in self.ends or self.ends[v['uid']]['time']>t+1e-9]
                v=remain[0] if remain else None;uid=v['uid'] if v else None
                active=v is not None and uid in self.starts and self.starts[uid]['time']<=t+1e-9
                self.check(a['current_vertex']==uid and a['query_eligible']==active,'public_current_occurrence')
                status='COMPLETED' if not v else 'IN_PROGRESS' if active else 'STAGED'
                self.check(a['status']==status,'public_status')
                ratio=sum(h['duration'] for h in done)/sum(h['nominal_duration'] for h in done) if done else 1.
                qs=[h['duration']/h['nominal_duration'] for h in done];variance=statistics.pvariance(qs) if qs else 0.;cv=math.sqrt(variance)/statistics.mean(qs) if qs else 0.
                delivered=[q for q in e['queries'] if q['agent']==aid and q['delivered_at']<=t+1e-9 and q['delivery_status']!='pending']
                current=[q for q in delivered if q['vertex']==uid and q['delivery_status']=='accepted'];latest=max(current,key=lambda q:q['captured']) if current else None
                p=self.predictions[keys[aid]] if v else None
                expected=dict(elapsed=t-self.starts[uid]['time'] if active else 0.,nominal_duration=v['duration'] if v else 0.,
                    history_ratio=ratio,history_count=len(done),history_variance=variance,history_cv=cv,
                    progress_estimate=p['encoded_progress'] if p else 1.,remaining_estimate=p['remaining_time'] if p else 0.,
                    last_measurement_age=t-latest['captured'] if latest else None,last_observed_residual=v['duration']*(1-latest['progress']) if latest else None,
                    measurement_count=len(delivered),downstream_nominal=sum(v['duration'] for v in remain),
                    outgoing_blocked_agents=len(outgoing[uid]),upcoming_switchable_influence=len(influence[aid]),
                    wait_elapsed=t-(done[-1]['end'] if done else 0.) if v and not active else 0.)
                for name,value in expected.items():self.eq(a[name],value,'public_'+name)
                self.check(a['prediction_provider']==(p['provider'] if p else 'completed'),'public_prediction_provider')
                self.check(a['blocked']==bool(v and not active and any(vertices[u]['status']!='COMPLETED' for u in incoming[uid])),'public_dependency_blocked')
            derived=structural(graph,s['agents'])
            for a in s['agents']:
                for key,value in derived[a['agent_id']].items():
                    if isinstance(value,(list,bool)):self.check(a[key]==value,'public_structure:'+key)
                    else:self.eq(a[key],value,'public_structure:'+key)
            selected=g['selected']
            self.check(len(selected)==len(set(selected)) and len(selected)<=s['max_queries'],'selection_cap')
            self.check(set(selected)<={a['agent_id'] for a in s['agents'] if a['query_eligible']},'selection_active')
            if self.policy and not g['override']:
                if self.policy in ['structural','structural_history_stop']:
                    ranked=[]
                    for a in s['agents']:
                        value=0.
                        if a['structural_eligible']:
                            nominal=max(1e-9,a['nominal_duration']*a['history_ratio'])
                            age=a['elapsed'] if a['last_measurement_age'] is None else a['last_measurement_age']
                            uncertainty=a['history_cv']+max(0.,a['elapsed']/nominal-1)+age/nominal
                            distance=a['boundary_path_time_min'];urgency=1. if distance is None else 1/(1+distance/max(s['solve_period'],1e-9))
                            value=uncertainty*(a['legal_boundary_group_count']+a['blocked_frontier_count'])*urgency
                        ranked.append((-value,a['agent_id']))
                    expected=[aid for value,aid in sorted(ranked)[:s['max_queries']] if value<0]
                else:expected=base.policy_selection(s,{'noquery':'history_only','none':'history_only','no':'history_only','fixed':'fixed_update'}.get(self.policy,self.policy))
                self.check(expected is not None and selected==expected,'registered_query_policy',dict(expected=expected,actual=selected))
            captures=[q for q in e['queries'] if q['gate_index']==gid]
            self.check([q['agent'] for q in captures]==selected,'capture_matches_selection')
            for q in captures:
                body={k:v for k,v in q.items() if k not in ['body_sha256','payload_bytes','delivery_status']}
                self.check(canon(body)==q['body_sha256'],'query_body_hash')
                self.eq(len(json.dumps(dict(body,body_sha256=q['body_sha256']),sort_keys=True).encode()),q['payload_bytes'],'query_payload_bytes')
                self.eq(q['captured'],t,'query_capture');self.eq(q['delivered_at'],g['solve_time'],'query_delivery')
                self.check(q['world_geometry_binding']==e['geometry_binding'],'query_geometry')
                a=next(a for a in s['agents'] if a['agent_id']==q['agent']);self.check(q['vertex']==a['current_vertex'],'query_occurrence')
                vv=self.vs[q['vertex']];candidates=[z for z in self.segments[q['agent']] if z['t0']<=t+1e-9 and z['t1']>=t-1e-9]
                self.check(bool(candidates),'capture_physical_segment')
                if candidates:
                    position=point(candidates[-1],t)
                    self.eq(q['progress'],math.dist(vv['path'][0][:2],position)/math.dist(vv['path'][0][:2],vv['path'][-1][:2]),'actual_capture_progress')
                deliveries=[x for x in self.evs if x['kind']=='POSITION_DELIVER' and x['query_id']==q['query_id']]
                if q['delivery_status']=='pending':self.check(not deliveries and q['delivered_at']>e['simulation_end']-TOL,'pending_query')
                else:
                    stale=q['vertex'] in self.ends and self.ends[q['vertex']]['time']<=q['delivered_at']+1e-9
                    self.check(q['delivery_status']==('stale_occurrence' if stale else 'accepted'),'stale_never_successor')
                    self.check(len(deliveries)==1 and deliveries[0]['status']==q['delivery_status'],'one_actual_delivery')
                    if deliveries:self.eq(deliveries[0]['time'],q['delivered_at'],'actual_delivery_clock')
            used+=len(selected)
        self.eq(e['query_count'],used,'total_queries');self.eq(e['query_payload_bytes'],sum(q['payload_bytes'] for q in e['queries']),'total_query_bytes')
        self.check(used<=e['query_budget'],'budget_not_exceeded')
        for key in self.predictions:self.check_prediction(key)
        self.stats.update(prediction_records=len(self.predictions),queries_from_captures=used,CAS_objects=len(self.store.cache))

    def run(self):
        for stage in [self.source_and_input,self.events_and_outcomes,self.graph_adoptions,self.trajectory,self.disturbance_motion,self.public_and_queries]:
            try:stage()
            except Exception as exc:self.check(False,'stage_exception:'+stage.__name__,repr(exc))
        self.dependencies.update(self.store.files)
        self.file_hash(Path(__file__).with_name('physical_math.py'));self.file_hash(Path(__file__).with_name('BASE_PROVENANCE.json'))
        self.limits+=['Continuous point safety only; no body/acceleration or real-time robot claim.',
            'Private disturbance data is read only by this post-execution auditor, never the predictor.',
            'Public shortest-path structure ignores AND dependencies and is not an exact ETA or guarantee.',
            'Author horizon uses full predecessor duration rather than current residual; its mutable head is reconstructed from actual whole-group switches.']
        return dict(schema='r19-independent-episode-audit-v1',passed=not self.errors,checks=self.checks,errors=self.errors,
            episode=str(self.path),episode_sha256=self.file_hash(self.path),recorded_status=self.e['status'],recorded_success=self.e['success'],
            stats=self.stats,limitations=self.limits,dependencies=self.dependencies,scientific_episode_reruns=0,
            engine_or_policy_imported=False,predictor_imported=False,auditor_sha256=self.file_hash(__file__))


def main():
    p=argparse.ArgumentParser();p.add_argument('--episode',required=True);p.add_argument('--case');p.add_argument('--policy');p.add_argument('--output',required=True)
    p.add_argument('--root');p.add_argument('--store');p.add_argument('--bundle');p.add_argument('--path-map',action='append',default=[],metavar='OLD=NEW')
    a=p.parse_args();maps=dict(x.split('=',1) for x in a.path_map)
    report=Auditor(a.episode,a.case,a.policy,root=a.root,store=a.store,bundle=a.bundle,path_maps=maps).run()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','checks','errors','stats']}));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
