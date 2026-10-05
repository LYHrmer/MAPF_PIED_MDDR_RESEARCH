#!/usr/bin/env python3
"""One new public-history native input and an unchanged-parent event control."""
from pathlib import Path
import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common_engine import GSESCommonSimulator,EngineConfig,DensePositionPolicy,write_json,file_sha,r19
from fraction_oracle import enumerate_legal


class KeepParent(GSESCommonSimulator):
    def _solve(self,gate):
        self._update_predictor()
        graph=r19.graph_snapshot(self.graph,self.config.horizon)
        ref=self.store.put_graph(graph)
        self.solves.append(dict(gate_index=gate['gate_index'],time=self.now,
            before_ref=ref,after_ref=ref,prediction_keys=dict(self._last_predictions),
            adopted=False,guard=r19.adoption_guard(graph,graph),new_author_calls=0,
            new_solver_seconds=0.,new_author_wall_seconds=0.,
            model=dict(status='REGISTERED_KEEP_PARENT_CONTROL',reference_solver_seconds=0.,reference_author_seconds=0.)))


def register():
    path=HERE/'PHASE3_REGISTRATION.json'
    if path.exists():raise RuntimeError('refuse registration overwrite')
    write_json(path,dict(registered_utc=datetime.now(timezone.utc).isoformat(),
        case_path=str(HERE/'phase2_case.json'),case_sha256=file_sha(HERE/'phase2_case.json'),
        purpose='positive legal-switch mechanism test, not heldout performance',
        seed=1,disturbance=dict(kind='stable',affected_fraction=.85,stable_factor=.25),
        design='Seed1 affected hashes A=.779185 and B=.921794 set A speed=.25 and B=1. This private setup is fixed before the call. After A END at4, full public history identifies its ratio4. No truth is supplied to the optimizer.',
        first_capture_time=4.5,query_latency=.25,solve_period=100.,max_time=100.,
        arms=['gses_surrogate','keep_parent_control'],policy='dense current active POSITION at the one gate',
        native_invocation_cap=1,source_pins={n:file_sha(HERE/n) for n in ('common_engine.py','fraction_oracle.py','phase3_switch.py')},
        acceptance='Enumerate both legal native orientations with Fraction; guard must protect active A2; full continuous suffix audit; report either no flip or actual flip and all failures.',
        call_accounting='Previous9 program invocations include4 constructor failures,4 phase1 Astar inputs,1 unique phase2 Astar input; this phase adds at most1.'))
    print('registered',file_sha(path))


def run():
    reg=json.loads((HERE/'PHASE3_REGISTRATION.json').read_text())
    for name,value in reg['source_pins'].items():assert file_sha(HERE/name)==value
    assert file_sha(reg['case_path'])==reg['case_sha256']
    case=json.loads(Path(reg['case_path']).read_text());results=[]
    for arm in reg['arms']:
        out=HERE/'positive_switch'/arm
        if out.exists():raise RuntimeError('refuse completed/unfinished repeat')
        out.mkdir(parents=True);write_json(out/'STARTED.json',dict(registration_sha256=file_sha(HERE/'PHASE3_REGISTRATION.json'),arm=arm))
        cfg=EngineConfig(solve_period=reg['solve_period'],query_latency=reg['query_latency'],
            max_time=reg['max_time'],query_budget=2,max_queries_per_gate=2,horizon=5.,
            gses_max_new_calls=1,evidence_dir=str(HERE/'common_evidence'),
            output_dir=str(out),cache_dir=str(HERE/'common_cache'))
        cls=GSESCommonSimulator if arm=='gses_surrogate' else KeepParent
        sim=cls(case,reg['disturbance'],reg['seed'],config=cfg);sim.next_gate=reg['first_capture_time']
        result=sim.run(DensePositionPolicy())
        if arm=='keep_parent_control':
            result['optimizer']['name']='registered keep-parent control, zero search'
            write_json(out/'episode.json',result)
        audits=[]
        for solve in result['solves']:
            if arm=='keep_parent_control':continue
            encoded=sim.store.get(solve['encoded_public_input_ref'])
            before=sim.store.get_graph(solve['before_ref'])
            eligible={g['uid'] for g in before['groups'] if g['switchable'] and g['within_horizon']}
            choices=[e['active'] for e in encoded['mapping'] if not e['pruned_satisfied'] and e['reverse'] is not None and e['group'] in eligible]
            assert len(choices)<=1
            oracle=enumerate_legal(dict(solver_graph=encoded['solver_graph'],reversible_edges=choices))
            audits.append(dict(oracle=oracle,actual=solve.get('native_graph_objective'),
                native_optimal=Fraction(solve['native_graph_objective']['sum_completion'])==Fraction(oracle['optimum']),guard=solve.get('guard')))
        write_json(out/'FRACTION_AUDIT.json',audits)
        row={k:result[k] for k in ('success','status','completion_times','sum_completion','makespan','query_count','new_author_calls','collision_audit','failures')}
        row.update(arm=arm,audits=audits,episode_path=str(out/'episode.json'),episode_sha256=file_sha(out/'episode.json'))
        results.append(row);print(arm,result['status'],result['sum_completion'],[s.get('guard') for s in result['solves']],flush=True)
    assert sum(r['new_author_calls'] for r in results)<=1
    write_json(HERE/'PHASE3_RESULTS.json',dict(registration_sha256=file_sha(HERE/'PHASE3_REGISTRATION.json'),records=results,
        claim='constructed legal-switch execution witness only; no learned predictor or benchmark generalization claim'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['register','run']);args=parser.parse_args()
    register() if args.command=='register' else run()
