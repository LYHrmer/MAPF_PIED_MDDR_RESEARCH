"""Frozen R20 position-fusion confirmation. Resume exact receipts, never rerun them."""
from pathlib import Path
import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import sys
import time

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R18=HERE.parent/'sadg_benchmark_20261005_r18'
LEARNING=Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/conditional_duration_20261005_r19')
POSITION=Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/position_conditioned_20261005_r20')
sys.path.insert(0,str(HERE))

ARMS={
    'history_structural':('all_history','structural'),
    'ewma_structural':('ewma03_survival','structural'),
    'learned_linear_structural':('learned','structural'),
    'learned_position_structural':('learned','structural'),
    'learned_no_query':('learned','none'),
}
DISTURBANCES={
    'stable':dict(kind='stable',affected_fraction=0.,stable_factor=1.),
    'pause_range_2to5':dict(kind='bounded_pause',affected_fraction=.5,stable_factor=1.,pause_probability=.25,pause_duration_range=[2.,5.],pause_fraction=.35),
    'speed_shift_065':dict(kind='speed_shift',affected_fraction=.5,stable_factor=1.,shift_action_fraction=.35,shifted_factor=.65),
}
PIN_FILES=('run_study.py','engine.py','solver_adapter.py','structural.py','evidence.py','PUBLIC_SCHEMA.json',
    'THREE_ROUTE_DECISION.md','model/MODEL.json','model/predictor.py','model/PROVENANCE.json',
    'position_model/MODEL.json','position_model/predictor.py','position_model/end_predictor.py','position_model/PROVENANCE.json',
    'position_model/MODEL_FREEZE.json','position_model/VALIDATION.json','r0/VALIDATION.json','r0/INDEPENDENT_DENSE_JOINT_AUDIT.json',
    'data/REGISTERED_MATRIX.json','data/CASES.json')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text())
def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def save(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n'); tmp.replace(p)
def freeze(p,obj):
    if Path(p).exists(): assert read(p)==obj, f'frozen artifact mismatch: {p}'
    else: save(p,obj)
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def prepare_model():
    target=HERE/'model';target.mkdir(exist_ok=True)
    for name in ('MODEL.json','predictor.py','MODEL_FREEZE.json','MODEL_BUNDLE_MANIFEST.json'):
        dest=target/name
        if dest.exists(): assert sha(dest)==sha(LEARNING/name)
        else: dest.write_bytes((LEARNING/name).read_bytes())
    freeze(target/'PROVENANCE.json',dict(source_directory=str(LEARNING),
        source_branch='explore/learned-query',
        source_hashes={name:sha(LEARNING/name) for name in ('MODEL.json','predictor.py','MODEL_FREEZE.json','MODEL_BUNDLE_MANIFEST.json')},
        training='R18 TRAIN scenario1/2 only; nested grouped CV; no new execution test data'))

def prepare_position_model():
    target=HERE/'position_model';target.mkdir(exist_ok=True)
    files={'MODEL.json':'MODEL.json','predictor.py':'position_predictor.py','end_predictor.py':'end_predictor.py','MODEL_FREEZE.json':'MODEL_FREEZE.json'}
    for name,source in files.items():
        dest=target/name
        if dest.exists():assert sha(dest)==sha(POSITION/source)
        else:dest.write_bytes((POSITION/source).read_bytes())
    freeze(target/'PROVENANCE.json',dict(source_directory=str(POSITION),
        source_branch='explore/learned-query',file_mapping=files,source_hashes={n:sha(POSITION/n) for n in files.values()},
        scope='R18 TRAIN actual captured POSITION only; no new scenario8/9 outcomes'))

def register():
    prepare_model()
    prepare_position_model()
    assert read(HERE/"r0/VALIDATION.json")["passed"]
    assert read(HERE/"position_model/VALIDATION.json")["passed"]
    assert read(HERE/"r0/INDEPENDENT_DENSE_JOINT_AUDIT.json")["passed"]
    cases=read(HERE/'data/CASES.json')['cases']
    assert len(cases)==6 and all(c['status']!='pending' for c in cases)
    for c in cases: assert sha(c['case_path'])==c['plan_sha256']
    pins={p:sha(HERE/p) for p in PIN_FILES}
    pins['inherited:R18/engine.py']=sha(R18/'engine.py')
    pins['inherited:R18/policies.py']=sha(R18/'policies.py')
    path=HERE/'EXPERIMENT_REGISTRATION.json'
    if path.exists():
        result=read(path); assert result['source_pins']==pins
        assert result['cases']==cases and result['arms']=={k:list(v) for k,v in ARMS.items()}
        return result
    result=dict(schema='r20-position-fusion-confirmation-v1',registered_utc=now(),
        source_pins=pins,cases=cases,arms={k:list(v) for k,v in ARMS.items()},disturbances=DISTURBANCES,
        planned_rows=90, core_rows=90, scale_extension_rows=0,
        primary_contrast=["learned_position_structural","learned_linear_structural"],
        evaluation_only=True,initial_failure_rows_in_denominator=True,no_retuning_after_test=True,
        common_config=dict(period='max(4,nominal_makespan/12)',query_latency=.25,query_budget='N',
            max_queries_per_gate='ceil(N/8)',horizon=5.,max_time='max(100,8*public_move_count+10)',
            outer_solver_seconds=90, original_author_internal_limit_seconds=60),
        paired_disturbance_seed='sha256(r18|map_name__sXX)[:8]; policy independent',
        independent_unit='map_name x scenario_id; six new families, scenarios8/9,N32',
        initial_solver=dict(wall_cap_seconds=30,suboptimality=1.5,address_space_bytes=4294967296,no_retry=True),
        inference_cost='wall runtime includes adapter/evidence; parallel contention prevents clean speed claims',
        user_scope='mechanism and author-code reproduction; fixed paths, point robots; not full LMAPF')
    save(path,result); return result

def assert_pins(reg):
    for p,h in reg['source_pins'].items():
        path=R18/p.split('/')[-1] if p.startswith('inherited:') else HERE/p
        assert sha(path)==h, f'source changed after freeze: {p}'

def config(case,directory):
    import engine
    schedules=case['solution']['schedule'];n=len(schedules)
    makespan=max(float(p[-1]['t']) for p in schedules.values())
    moves=sum(sum((a['x'],a['y'])!=(b['x'],b['y']) for a,b in zip(p,p[1:])) for p in schedules.values())
    return engine.EngineConfig(solve_period=max(4.,makespan/12),query_latency=.25,query_budget=n,
        max_queries_per_gate=math.ceil(n/8),horizon=5.,max_time=max(100.,8.*moves+10.),
        cache_dir=str(HERE/'author_cache'),output_dir=str(directory),evidence_dir=str(HERE/'evidence_store'),
        save_models=True,save_gate_graphs=True)

def constructors(arm):
    import engine
    from structural import StructuralStopPolicy
    mode,policy=ARMS[arm]
    runtime=load_module('r19_frozen_duration_predictor',HERE/'model/predictor.py')
    predictor=engine.HistoryPredictor() if mode=='all_history' else runtime.DurationPredictor(HERE/'model/MODEL.json',mode)
    inherited=load_module('r19_frozen_query_controls',R18/'policies.py')
    policies={'none':inherited.NoQuery,'structural':StructuralStopPolicy,
        'fixed_update':inherited.FixedUpdate,'history_rule':inherited.HistoryRule}
    load_module('end_predictor',HERE/'position_model/end_predictor.py')
    position_module=load_module('r20_frozen_position_predictor',HERE/'position_model/predictor.py')
    position_predictor=position_module.PositionPredictor(HERE/'position_model/MODEL.json') if arm=='learned_position_structural' else None
    return predictor,policies[policy](),position_predictor

def episode(reg,record,disturbance,arm):
    import engine
    assert_pins(reg)
    case=read(record['case_path']); assert sha(record['case_path'])==record['plan_sha256']
    world=record['case_id']+'__'+disturbance
    folder=HERE/'episodes'/world/arm
    family=f'{record["map_name"]}__s{record["scenario_id"]:02d}'
    seed=int(hashlib.sha256(('r18|'+family).encode()).hexdigest()[:8],16)
    cfg=config(case,folder)
    spec=dict(world=world,family=family,arm=arm,predictor_mode=ARMS[arm][0],query_policy=ARMS[arm][1],
        case_path=record['case_path'],case_sha256=record['plan_sha256'],disturbance=DISTURBANCES[disturbance],seed=seed,
        model_sha256=sha(HERE/'model/MODEL.json'),predictor_sha256=sha(HERE/'model/predictor.py'),
        position_model_sha256=sha(HERE/'position_model/MODEL.json'),position_predictor_sha256=sha(HERE/'position_model/predictor.py'),
        source_pins=reg['source_pins'],
        config=engine.asdict(cfg),registration_sha256=sha(HERE/'EXPERIMENT_REGISTRATION.json'))
    spec_hash=digest(spec)
    receipt=folder/'RUN_RECEIPT.json'
    if receipt.exists():
        old=read(receipt);assert old['spec_sha256']==spec_hash and sha(folder/'episode.json')==old['episode_sha256']
        return read(folder/'episode.json'),True
    assert not (folder/'STARTED.json').exists(), f'incomplete attempt; inspect process before any recovery: {folder}'
    start=dict(started_utc=now(),process_id=os.getpid(),spec=spec,spec_sha256=spec_hash)
    freeze(folder/'STARTED.json',start)
    t0=time.perf_counter()
    try:
        predictor,policy,position_predictor=constructors(arm)
        result=engine.Simulator(case,DISTURBANCES[disturbance],seed,predictor=predictor,position_predictor=position_predictor,config=cfg).run(policy)
    except Exception as exc:
        result=dict(schema='r20-constructor-failure',status='constructor_failure',success=False,
            error=repr(exc),agents=record['num_agents'],completed_agents=0,query_count=0,
            restricted_sum_completion=cfg.max_time*record['num_agents'],sum_completion=None,
            makespan=None,common_horizon=cfg.max_time,gates=[],events=[],queries=[],solves=[],segments=[],
            failures=[dict(kind='RUNNER_EXCEPTION',error=repr(exc))],config=engine.asdict(cfg))
    result['benchmark']=dict(world=world,family=family,arm=arm,disturbance=disturbance,
        stratum='scale_extension' if record['num_agents']==64 else 'core',spec_sha256=spec_hash)
    save(folder/'episode.json',result)
    freeze(receipt,dict(**start,finished_utc=now(),elapsed_seconds=time.perf_counter()-t0,
        episode_sha256=sha(folder/'episode.json'),status=result['status'],success=result['success']))
    return result,False

def run(reg,map_name=None,limit=None):
    count=0
    for record in reg['cases']:
        if map_name and record['map_name']!=map_name: continue
        if record['status']!='valid': continue
        arms=list(ARMS)[:6] if record['num_agents']==64 else list(ARMS)
        for dist in DISTURBANCES:
            for arm in arms:
                if limit is not None and count>=limit:return
                result,reused=episode(reg,record,dist,arm)
                count+=int(not reused)
                print(json.dumps(dict(time=now(),case=record['case_id'],disturbance=dist,arm=arm,
                    status=result['status'],success=result['success'],query_count=result['query_count'],
                    completion=result['restricted_sum_completion'],reused=reused)),flush=True)

def summarize(reg):
    rows=[];missing=[]
    for c in reg['cases']:
        for d in DISTURBANCES:
            for arm in (list(ARMS)[:6] if c['num_agents']==64 else ARMS):
                row=dict(case_id=c['case_id'],map_name=c['map_name'],scenario_id=c['scenario_id'],
                    family=f'{c["map_name"]}__s{c["scenario_id"]:02d}',num_agents=c['num_agents'],
                    stratum='scale_extension' if c['num_agents']==64 else 'core',disturbance=d,arm=arm)
                if c['status']!='valid':
                    row.update(status='initial_'+c['status'],success=False,completed_agents=0,query_count=0,
                        restricted_sum_completion=None,sum_completion=None,makespan=None)
                else:
                    folder=HERE/'episodes'/(c['case_id']+'__'+d)/arm
                    if not (folder/'RUN_RECEIPT.json').exists(): missing.append(row);continue
                    e=read(folder/'episode.json'); r=read(folder/'RUN_RECEIPT.json')
                    assert sha(folder/'episode.json')==r['episode_sha256']
                    row.update({k:e[k] for k in ('status','success','completed_agents','query_count','restricted_sum_completion','sum_completion','makespan')})
                    row['elapsed_seconds']=r['elapsed_seconds']
                    row['solver_calls']=sum(s['new_author_calls'] for s in e['solves'])
                    row['solve_failures']=sum(not s.get('adopted',False) for s in e['solves'])
                rows.append(row)
    save(HERE/'SUMMARY.json',dict(rows=rows,missing=missing,registered_rows=90,
        registration_sha256=sha(HERE/'EXPERIMENT_REGISTRATION.json')))
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (HERE/'SUMMARY.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(rows=len(rows),missing=len(missing),successful=sum(r['success'] for r in rows))))
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['register','run','summarize'])
    ap.add_argument('--map');ap.add_argument('--limit',type=int);args=ap.parse_args()
    reg=register()
    if args.stage=='run':run(reg,args.map,args.limit)
    if args.stage=='summarize':summarize(reg)
    if args.stage=='register':print(json.dumps(dict(registration_sha256=sha(HERE/'EXPERIMENT_REGISTRATION.json'),registered_utc=reg['registered_utc'])))
