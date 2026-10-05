"""Registered frozen prediction scoring on one common new R20 trajectory/world.

Independent raw extraction: no engine, runner, trainer or development parser is
imported. It never runs an episode or solver and waits for every final receipt.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import gzip
import hashlib
import json
import math
from independent_math import evaluate_position,evaluate_end,history_summary
from position_predictor import PositionPredictor

DEFAULT_ROOT=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_fusion_20261005_r20')
MODES=['position_learned','position_constant','history_linear','ewma_linear','end_learned','end_ewma_survival','observed_average']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def read(path):return json.loads(Path(path).read_text())


def save(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def save_rows(name,values):
    with (HERE/name).open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as g:
            for value in values:g.write((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())


def mean_metrics(records,mode):
    if not records:return dict(rows=0,worlds=0,families=0,mae=None,mse=None,bias=None)
    groups=defaultdict(lambda:defaultdict(list))
    for r in records:groups[r['family']][r['world']].append(r['predictions'][mode]-r['actual'])
    family_scores=[]
    for worlds in groups.values():
        scores=[]
        for errors in worlds.values():scores.append(dict(mae=sum(abs(e) for e in errors)/len(errors),mse=sum(e*e for e in errors)/len(errors),bias=sum(errors)/len(errors)))
        family_scores.append({k:sum(s[k] for s in scores)/len(scores) for k in ['mae','mse','bias']})
    return dict(rows=len(records),worlds=sum(len(w) for w in groups.values()),families=len(groups),
        **{k:sum(s[k] for s in family_scores)/len(family_scores) for k in ['mae','mse','bias']})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--coverage-only',action='store_true');args=parser.parse_args();root=args.root
    reg=read(HERE/'REGISTRATION.json');mainreg=read(root/'EXPERIMENT_REGISTRATION.json')
    assert mainreg['registered_utc']<reg['registered_utc']
    assert sha(HERE.parent/'MODEL.json')==reg['model_sha256']
    assert sha(HERE.parent/'PINNED_END_MODEL.json')==reg['end_model_sha256']
    assert sha(HERE.parent/'position_predictor.py')==reg['position_predictor_sha256']
    assert sha(HERE.parent/'independent_math.py')==reg['independent_math_sha256']
    expected=[]
    for case in mainreg['cases']:
        for disturbance in mainreg['disturbances']:
            world=case['case_id']+'__'+disturbance
            folder=root/'episodes'/world/reg['reference_arm'];rp=folder/'RUN_RECEIPT.json'
            receipt=read(rp) if rp.exists() else None
            expected.append(dict(world=world,family=f"{case['map_name']}__s{case['scenario_id']:02d}",
                case_status=case['status'],directory=str(folder),receipt=str(rp),
                ready=bool(receipt and receipt.get('finished_utc') and (folder/'episode.json').exists())))
    assert len(expected)==18 and len({x['world'] for x in expected})==18
    coverage=dict(registered_worlds=18,ready=sum(x['ready'] for x in expected),worlds=expected,
        main_registration_sha256=sha(root/'EXPERIMENT_REGISTRATION.json'),secondary_registration_sha256=sha(HERE/'REGISTRATION.json'))
    save('COVERAGE.json',coverage)
    if args.coverage_only or not all(x['ready'] for x in expected):
        print(json.dumps({'ready':coverage['ready'],'expected':18,'scored':False}));return
    model=read(HERE.parent/'MODEL.json');end_model=read(HERE.parent/'PINNED_END_MODEL.json');runtime=PositionPredictor(model)
    sources=[];outputs={name:[] for name in ['capture','delivery','consumer']};censored=[]
    verification=dict(raw_history_cuts=0,query_body_hashes=0,actual_position_checks=0,runtime_predictions=0,
        max_runtime_difference=0.,actual_linear_provider_checks=0)
    for entry in expected:
        folder=Path(entry['directory']);ep=read(folder/'episode.json');receipt=read(entry['receipt']);spec=receipt['spec']
        assert receipt['episode_sha256']==sha(folder/'episode.json') and digest(spec)==receipt['spec_sha256']
        assert ep['schema']=='r20-sadg-position-episode-v1' and spec['arm']==reg['reference_arm']
        assert spec['world']==entry['world'] and spec['family']==entry['family']
        assert spec['registration_sha256']==coverage['main_registration_sha256']
        store=Path(ep['evidence_store']);cas_hashes={}
        def cas(ref):
            assert ref['schema']=='r19-cas-ref-v1' and ref['path']==f"objects/{ref['sha256'][:2]}/{ref['sha256']}.json.gz"
            path=store/ref['path'];raw=gzip.decompress(path.read_bytes())
            assert len(raw)==ref['raw_bytes'] and hashlib.sha256(raw).hexdigest()==ref['sha256']
            v=json.loads(raw);assert digest(v)==ref['sha256'];cas_hashes[str(path)]=sha(path);return v
        graph=cas(ep['initial_graph_ref']);top=cas(graph['topology']);vertices={v['uid']:v for v in top['vertices']}
        assert cas(ep['predictor_model_ref'])==end_model
        predictions=cas(ep['prediction_evidence_ref'])
        starts={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='START'}
        ends={(e['agent'],e['vertex']):e['time'] for e in ep['events'] if e['kind']=='END'}
        history=ep['delivered_end_history'];queries={q['query_id']:q for q in ep['queries']};rows={}
        delivery_events={e['query_id']:e for e in ep['events'] if e['kind']=='POSITION_DELIVER'}
        world_count=Counter()
        for qid,q in queries.items():
            aid,uid=q['agent'],q['vertex'];key=(aid,uid);t=q['captured'];start=starts[key];end=ends.get(key)
            assert start<=t+1e-8 and (end is None or end>t)
            public=[h for h in history[aid] if h['delivered']<=t+1e-8]
            assert all(h['vertex']!=uid and h['delivered']<=start+1e-8 for h in public)
            for h in public:
                assert abs(h['duration']-(h['end']-h['start']))<1e-8
                assert starts[(aid,h['vertex'])]==h['start'] and ends[(aid,h['vertex'])]==h['end'] and h['delivered']==h['end']
            verification['raw_history_cuts']+=1
            vv=vertices[uid];a=vv['path'][0][:2];b=vv['path'][-1][:2];length=math.dist(a,b);nominal=length/2
            ss=[s for s in ep['segments'] if s['agent']==aid and s['vertex']==uid and s['t0']<=t+1e-8 and s['t1']>=t-1e-8]
            assert ss
            segment=ss[-1];f=(t-segment['t0'])/(segment['t1']-segment['t0'])
            point=[u+f*(v-u) for u,v in zip(segment['p0'],segment['p1'])]
            progress=sum((point[i]-a[i])*(b[i]-a[i]) for i in [0,1])/(length*length)
            assert abs(progress-q['progress'])<1e-7;verification['actual_position_checks']+=1
            body={k:v for k,v in q.items() if k not in ['body_sha256','payload_bytes','delivery_status']}
            assert digest(body)==q['body_sha256'];verification['query_body_hashes']+=1
            assert qid in delivery_events and delivery_events[qid]['status']==q['delivery_status']
            assert abs(delivery_events[qid]['time']-q['delivered_at'])<1e-8
            base=dict(key=f"{entry['world']}|{aid}|{uid}|q{qid}",world=entry['world'],family=entry['family'],
                agent=aid,vertex=uid,query_id=qid,nominal=nominal,start=start,end=end,captured=t,delivered=q['delivered_at'],
                capture_elapsed=t-start,progress=q['progress'],history=public,delivery_status=q['delivery_status'])
            rows[qid]=base
        def add(cohort,row,time,suffix):
            age=time-row['captured'];context=dict(status='IN_PROGRESS',occurrence_id=row['vertex'],nominal_duration=row['nominal'],
                elapsed=time-row['start'],completed_history=row['history'],position=dict(occurrence_id=row['vertex'],progress=row['progress'],
                captured_elapsed=row['capture_elapsed'],age=age,delivered_age=0. if cohort=='capture' else row['delivered']-row['captured']))
            # Capture scores are counterfactual zero-latency predictions, not a claim of online use before delivery.
            if row['end'] is None:
                censored.append(dict(key=row['key']+suffix,cohort=cohort,world=row['world'],family=row['family'],
                    time=time,context=context,final_simulation_time=ep['simulation_end'],label=None));world_count['censored_'+cohort]+=1
                return
            actual=row['end']-time;assert actual>0
            pp=evaluate_position(context,model)['remaining_time'];rr=runtime(context)['remaining_time']
            verification['runtime_predictions']+=1;verification['max_runtime_difference']=max(verification['max_runtime_difference'],abs(pp-rr))
            assert abs(pp-rr)<1e-6*max(1.,abs(pp))
            s=history_summary(row['history']);n=row['nominal'];p=row['progress'];e=row['capture_elapsed']
            pred={'position_learned':pp,'position_constant':evaluate_position(context,model,True)['remaining_time'],
                'history_linear':max(0.,(1-p)*n*s['all_history']-age),'ewma_linear':max(0.,(1-p)*n*s['ewma03']-age),
                'end_learned':evaluate_end(end_model,row['history'],n,e+age,'learned'),
                'end_ewma_survival':evaluate_end(end_model,row['history'],n,e+age,'ewma03_survival')}
            pred['observed_average']=max(0.,e*(1-p)/p-age) if p>1e-6 else pred['end_ewma_survival']
            outputs[cohort].append(dict(key=row['key']+suffix,world=row['world'],family=row['family'],time=time,
                actual=actual,predictions=pred,context=context));world_count[cohort]+=1
        for qid,row in rows.items():
            add('capture',row,row['captured'],'|capture')
            if row['delivery_status']=='accepted' and (row['end'] is None or row['end']>row['delivered']+1e-8):add('delivery',row,row['delivered'],'|delivery')
        seen=set()
        for solve in ep['solves']:
            for aid,key in solve['prediction_keys'].items():
                record=predictions[key];assert digest(record)==key
                if record['provider']!='position_linear_all_history':continue
                query_id=record['delivered_position']['query_id'];row=rows[query_id];time=solve['time']
                assert row['agent']==aid and record['vertex']==row['vertex'] and row['delivered']<=time+1e-8
                assert abs(time-record['time'])<1e-8 and record['context']['status']=='IN_PROGRESS'
                assert row['end'] is None or row['end']>time+1e-8
                assert all(h['delivered']<=row['captured']+1e-8 for h in record['context']['completed_history'])
                latest=max((q for q in queries.values() if q['agent']==aid and q['vertex']==row['vertex'] and q['delivery_status']=='accepted' and q['delivered_at']<=time+1e-8),key=lambda q:(q['delivered_at'],q['query_id']))
                assert latest['query_id']==query_id
                linear=max(0.,(1-row['progress'])*row['nominal']*history_summary(row['history'])['all_history']-(time-row['captured']))
                assert abs(linear-record['remaining_time'])<1e-7;verification['actual_linear_provider_checks']+=1
                pair=(solve['gate_index'],aid);assert pair not in seen;seen.add(pair)
                add('consumer',row,time,'|solve'+str(solve['gate_index']))
        sources.append(dict(**entry,episode_sha256=sha(folder/'episode.json'),receipt_sha256=sha(entry['receipt']),
            started_utc=receipt['started_utc'],finished_utc=receipt['finished_utc'],recorded_status=ep['status'],recorded_success=ep['success'],
            queries=len(queries),stale_queries=sum(q['delivery_status']=='stale_occurrence' for q in queries.values()),
            rows=dict(world_count),cas_hashes=cas_hashes))
    save('SOURCES.json',sources);save_rows('CENSORED.jsonl.gz',censored)
    result={}
    for cohort,records in outputs.items():
        assert len(records)==len({r['key'] for r in records})
        save_rows(cohort.upper()+'_PREDICTIONS.jsonl.gz',records)
        result[cohort]=dict(metrics={mode:mean_metrics(records,mode) for mode in MODES},
            per_family={family:{mode:mean_metrics([r for r in records if r['family']==family],mode) for mode in MODES} for family in sorted({r['family'] for r in records})},
            per_world={world:{mode:mean_metrics([r for r in records if r['world']==world],mode) for mode in MODES} for world in sorted({r['world'] for r in records})})
    result.update(schema='r20-post-start-secondary-fixed-prediction-scores-v1',scored_utc=datetime.now(timezone.utc).isoformat(),
        registered_worlds=18,source_worlds=len(sources),source_families=len({s['family'] for s in sources}),
        reference_arm=reg['reference_arm'],reference_statuses=dict(Counter(s['recorded_status'] for s in sources)),
        worlds_without_queries=[s['world'] for s in sources if s['queries']==0],censored_rows=len(censored),
        model_sha256=reg['model_sha256'],secondary_registration_sha256=sha(HERE/'REGISTRATION.json'),
        main_registration_sha256=coverage['main_registration_sha256'],scorer_sha256=sha(__file__),
        independent_math_sha256=reg['independent_math_sha256'],new_training_runs=0,new_solver_or_physical_episodes=0,
        scope='Secondary prediction scoring registered after main experiment started; common reference states, not scheduling efficacy or calibrated probability')
    verification.update(passed=True,source_worlds=18,engine_runner_trainer_imported=False,new_solver_or_physical_episodes=0)
    save('VERIFICATION.json',verification);save('RESULTS.json',result)
    print(json.dumps({'reference_worlds':18,'censored':len(censored),'delivery':result['delivery']['metrics'],'verification':verification},indent=2))


if __name__=='__main__':main()
