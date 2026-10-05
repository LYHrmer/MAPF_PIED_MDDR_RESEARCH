#!/usr/bin/env python3
"""Four preregistered transport arms, at most four new native input keys."""
from pathlib import Path
import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common_engine import (GSESCommonSimulator,EngineConfig,NoQueryPolicy,
    DensePositionPolicy,write_json,file_sha,encode_arrivals,lift_candidate,r19)
from fraction_oracle import enumerate_legal


def setup():
    regpath=HERE/'PHASE2_REGISTRATION.json'
    if regpath.exists():raise RuntimeError('refuse registration overwrite')
    case=dict(case_id='r20_new_crossing_transport_mechanism',solution={'schedule':{
        'agent0':[dict(x=x,y=0,t=i) for i,x in enumerate(range(-3,4))],
        'agent1':[dict(x=0,y=y,t=i+2) for i,y in enumerate(range(-3,4))]}})
    casepath=HERE/'phase2_case.json';write_json(casepath,case)
    cfg=dict(solve_period=100.,max_time=100.,query_budget=2,max_queries_per_gate=2,
        horizon=5.,gses_quantum=1.,gses_max_new_calls=4,save_gate_graphs=True,
        evidence_dir=str(HERE/'common_evidence'),cache_dir=str(HERE/'common_cache'))
    write_json(regpath,dict(registered_utc=datetime.now(timezone.utc).isoformat(),
        purpose='common event-executor mechanism only; no new scientific comparison',
        case_path=str(casepath),case_sha256=file_sha(casepath),config=cfg,
        disturbance={'kind':'stable','stable_factor_range':[.5,1.]},seed=20,
        first_capture_time=.5,subsequent_capture_period=100.,
        arms=[dict(name=f'{q}_age{age}',query=q,latency=age)
              for age in (0.,.25) for q in ('none','position')],
        sources={n:file_sha(HERE/n) for n in ('common_engine.py','phase2.py','fraction_oracle.py')},
        native_invocation_cap=4,exact_input_reuse=True,
        acceptance=['native full graph oracle is feasible','all adopted graph changes pass original R19 guard',
                    'complete continuous point event suffix with WAIT and GOAL_HOLD audit',
                    'capture progress only enters predictor after matching delivery',
                    'report null effects and all rejections'],
        limitations=['unit native type2 surrogate, not weighted continuous equivalence',
                     'one common capture gate, not a performance study',
                     'original 16-second Improved GSES search and 20-second outer watchdog']))
    print('registered',file_sha(regpath))


def run():
    reg=json.loads((HERE/'PHASE2_REGISTRATION.json').read_text())
    for name,value in reg['sources'].items():assert file_sha(HERE/name)==value
    assert file_sha(reg['case_path'])==reg['case_sha256']
    case=json.loads(Path(reg['case_path']).read_text());rows=[]
    for arm in reg['arms']:
        out=HERE/'common_runs'/arm['name']
        if out.exists():raise RuntimeError('refuse completed/unfinished repeat: '+str(out))
        out.mkdir(parents=True);write_json(out/'STARTED.json',dict(registration_sha256=file_sha(HERE/'PHASE2_REGISTRATION.json'),arm=arm))
        cfg=EngineConfig(**reg['config'],query_latency=arm['latency'],output_dir=str(out))
        sim=GSESCommonSimulator(case,reg['disturbance'],reg['seed'],config=cfg)
        sim.next_gate=reg['first_capture_time']
        result=sim.run(NoQueryPolicy() if arm['query']=='none' else DensePositionPolicy())
        audits=[]
        for solve in result['solves']:
            if 'author_reply_ref' not in solve or solve['author_reply_ref'] is None:
                audits.append(dict(passed=False,reason='no author output'));continue
            encoded=sim.store.get(solve['encoded_public_input_ref'])
            reply=sim.store.get(solve['author_reply_ref'])
            before=sim.store.get_graph(solve['before_ref'])
            eligible={g['uid'] for g in before['groups'] if g['switchable'] and g['within_horizon']}
            choices=[e['active'] for e in encoded['mapping'] if not e['pruned_satisfied'] and e['reverse'] is not None and e['group'] in eligible]
            # This micro-case has one reversible dependency. No independent-edge
            # enumeration is presented as grouped enumeration on larger graphs.
            assert len(choices)<=1
            oracle=enumerate_legal(dict(solver_graph=encoded['solver_graph'],reversible_edges=choices))
            actual=solve['native_graph_objective']
            unchanged=lift_candidate(before,encoded,encoded['solver_graph'])
            assert r19.adoption_guard(before,unchanged)['passed']
            broken=copy.deepcopy(encoded['solver_graph']);broken['type1'][0][2]+=1
            try:lift_candidate(before,encoded,broken)
            except ValueError:immutable_negative=True
            else:immutable_negative=False
            commitment_negative=None
            for group in before['groups']:
                if group['uid'] in eligible and group['dependencies'][0]['reverse'] is not None:
                    parent=copy.deepcopy(before);candidate=copy.deepcopy(before)
                    pg=next(g for g in parent['groups'] if g['uid']==group['uid'])
                    cg=next(g for g in candidate['groups'] if g['uid']==group['uid'])
                    for dep in cg['dependencies']:
                        dep['active']=dep['reverse'] if dep['active']==dep['forward'] else dep['forward'];dep['b']=not dep['b']
                    target=cg['dependencies'][0]['active'][1]
                    for graph in (parent,candidate):
                        next(v for v in graph['vertices'] if v['uid']==target)['status']='IN_PROGRESS'
                    commitment_negative=r19.adoption_guard(parent,candidate)
                    assert not commitment_negative['passed']
                    break
            audits.append(dict(passed=actual['feasible'] and immutable_negative,
                native_optimal=Fraction(actual['sum_completion'])==Fraction(oracle['optimum']),
                oracle=oracle,actual=actual,immutable_type1_negative=immutable_negative,
                active_commitment_negative=commitment_negative,
                guard=solve.get('guard'),cache_reused=solve.get('cache_reused')))
        write_json(out/'MECHANICAL_AUDIT.json',audits)
        row={k:result[k] for k in ('success','status','sum_completion','makespan','query_count',
            'solver_calls','new_author_calls','collision_audit','failures')}
        row.update(arm=arm,episode_path=str(out/'episode.json'),episode_sha256=file_sha(out/'episode.json'),
                   audits=audits,solve_times=[s['time'] for s in result['solves']],
                   captured_times=[q['captured'] for q in result['queries']],
                   delivery_times=[q['delivered_at'] for q in result['queries']])
        rows.append(row);print(arm['name'],result['status'],result['sum_completion'],'new',result['new_author_calls'],flush=True)
    assert sum(r['new_author_calls'] for r in rows)<=reg['native_invocation_cap']
    write_json(HERE/'PHASE2_RESULTS.json',dict(registration_sha256=file_sha(HERE/'PHASE2_REGISTRATION.json'),
        new_author_calls=sum(r['new_author_calls'] for r in rows),records=rows))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['register','run']);args=parser.parse_args()
    setup() if args.command=='register' else run()
