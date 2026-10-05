"""Frozen nine-mode predictions on common new-TEST reference trajectories."""
import sys
sys.dont_write_bytecode=True
from collections import defaultdict,Counter
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent;BUNDLE=HERE.parent
sys.path.insert(0,str(BUNDLE));sys.path.insert(0,str(BUNDLE/'review_r19'))
from predictor import MODES,summarize,predict_values
from audit_episode import CAS
ROOT=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_structural_20261005_r19')


def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name,data):(HERE/name).write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
def save_rows(name,rows):
    with (HERE/name).open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
            for row in rows:f.write((json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())


def predictions(model,nominal,elapsed,history):
    stats=summarize(history)
    return {mode:predict_values(model,mode,nominal,elapsed,stats)[0] for mode in MODES},stats


def aggregate(rows):
    worlds=defaultdict(list)
    for row in rows:
        if row['label'] is not None:worlds[row['world']].append(row)
    world_results={}
    for world,rs in worlds.items():
        mode_results={}
        for mode in MODES:
            errors=[r['predictions'][mode]-r['label'] for r in rs]
            mode_results[mode]=dict(mae=statistics.mean(abs(e) for e in errors),
                mse=statistics.mean(e*e for e in errors),bias=statistics.mean(errors))
        world_results[world]=dict(family=rs[0]['family'],rows=len(rs),metrics=mode_results)
    families=defaultdict(list)
    for world,values in world_results.items():families[values['family']].append(world)
    family_results={}
    for family,ww in families.items():
        family_results[family]=dict(worlds=len(ww),metrics={mode:{metric:statistics.mean(world_results[w]['metrics'][mode][metric] for w in ww)
            for metric in ['mae','mse','bias']} for mode in MODES})
    overall={mode:{metric:statistics.mean(family_results[f]['metrics'][mode][metric] for f in families)
        for metric in ['mae','mse','bias']} for mode in MODES}
    return dict(uncensored_rows=sum(len(r) for r in worlds.values()),right_censored_rows=sum(r['label'] is None for r in rows),
        family_count=len(families),world_count=len(worlds),metrics=overall,families=family_results,worlds=world_results)


def main():
    registered=read(HERE/'REGISTRATION.json');freeze=read(BUNDLE/'MODEL_FREEZE.json')
    assert registered['model_sha256']==sha(BUNDLE/'MODEL.json')==freeze['model_sha256']
    assert registered['predictor_sha256']==sha(BUNDLE/'predictor.py')==freeze['predictor_sha256']
    assert registered['score_sha256']==sha(__file__)
    reg=read(ROOT/'EXPERIMENT_REGISTRATION.json');assert sha(ROOT/'EXPERIMENT_REGISTRATION.json')==registered['science_registration_sha256']
    model=read(BUNDLE/'MODEL.json');store=CAS(ROOT/'evidence_store')
    actions=[];landmarks=[];sources=[];initial_failures=[];missing=[];keys=set()
    for case in reg['cases']:
        for disturbance in reg['disturbances']:
            world=case['case_id']+'__'+disturbance
            family=f"{case['map_name']}__s{case['scenario_id']:02d}"
            stratum='scale_extension' if case['num_agents']==64 else 'core'
            if case['status']!='valid':
                initial_failures.append(dict(world=world,family=family,stratum=stratum,status=case['status']));continue
            path=ROOT/'episodes'/world/'history_no_query';receipt_path=path/'RUN_RECEIPT.json'
            if not receipt_path.exists():missing.append(world);continue
            receipt=read(receipt_path);episode_path=path/'episode.json';raw=read(episode_path)
            assert receipt['episode_sha256']==sha(episode_path)
            assert receipt['spec']['query_policy']=='none' and receipt['spec']['predictor_mode']=='all_history'
            assert receipt['spec']['family']==family and case['scenario_id'] in [6,7]
            assert raw['query_count']==0
            assert freeze['frozen_utc']<=receipt['started_utc']
            graph=store.graph(raw['initial_graph_ref']);vertices={v['uid']:v for v in graph['vertices']}
            starts={e['vertex']:e for e in raw['events'] if e['kind']=='START'}
            ends={e['vertex']:e for e in raw['events'] if e['kind']=='END'}
            action_count=landmark_count=0
            for uid,event in starts.items():
                aid=event['agent'];t=event['time'];v=vertices[uid];nominal=v['duration']
                history=[h for h in raw['delivered_end_history'].get(aid,[]) if h['delivered']<=t+1e-9 and h['vertex']!=uid]
                assert all(h['end']<=t+1e-9 and h['delivered']==h['end'] for h in history)
                key=world+'|'+aid+'|'+uid;assert key not in keys;keys.add(key)
                pred,stats=predictions(model,nominal,0.,history)
                end=ends.get(uid);label=end['time']-t if end else None
                if end:assert abs(label-end['duration'])<1e-8 and label>0
                actions.append(dict(key=key,world=world,family=family,stratum=stratum,time=t,nominal_duration=nominal,
                    history_stats=stats,last_history_delivery=history[-1]['delivered'] if history else None,
                    dependency_wait=t-(history[-1]['end'] if history else 0.),label=label,
                    censor_lower_bound=raw['simulation_end']-t if end is None else None,predictions=pred))
                action_count+=1
            for gate in raw['gates']:
                snapshot=store.get(gate['public_snapshot_ref']);t=gate['capture_time']
                for a in snapshot['agents']:
                    if a['status']!='IN_PROGRESS':continue
                    aid,uid=a['agent_id'],a['current_vertex'];start=starts[uid]['time'];age=t-start;nominal=vertices[uid]['duration']
                    history=[h for h in raw['delivered_end_history'].get(aid,[]) if h['delivered']<=t+1e-9 and h['vertex']!=uid]
                    assert len(history)==a['history_count'] and abs(age-a['elapsed'])<1e-8 and age>=0
                    pred,stats=predictions(model,nominal,age,history)
                    assert abs(stats['all_history']-a['history_ratio'])<1e-8
                    end=ends.get(uid);label=end['time']-t if end else None
                    if label is not None:assert label>=-1e-8
                    landmarks.append(dict(key=world+'|'+aid+'|'+uid+'|g'+str(gate['gate_index']),world=world,family=family,
                        stratum=stratum,time=t,elapsed=age,nominal_duration=nominal,history_stats=stats,
                        last_history_delivery=history[-1]['delivered'] if history else None,label=label,
                        censor_lower_bound=raw['simulation_end']-t if end is None else None,predictions=pred))
                    landmark_count+=1
            sources.append(dict(world=world,family=family,stratum=stratum,status=raw['status'],
                canonical_arm='history_no_query',episode=str(episode_path),episode_sha256=sha(episode_path),
                receipt=str(receipt_path),receipt_sha256=sha(receipt_path),action_rows=action_count,active_rows=landmark_count))
    coverage=dict(expected_executable_worlds=42,found_worlds=len(sources),missing=missing,
        registered_initial_failure_worlds=initial_failures,by_stratum=dict(Counter(s['stratum'] for s in sources)))
    save('COVERAGE.json',coverage)
    assert not missing and len(sources)==42,'Canonical references incomplete; coverage retained, no final score released'
    save('SOURCES.json',sources);save_rows('ACTION_PREDICTIONS.jsonl.gz',actions);save_rows('ACTIVE_PREDICTIONS.jsonl.gz',landmarks)
    results={}
    for stratum in ['core','scale_extension']:
        results[stratum]=dict(action_start=aggregate([r for r in actions if r['stratum']==stratum]),
            active_gate=aggregate([r for r in landmarks if r['stratum']==stratum]))
    result=dict(schema='r19-frozen-heldout-secondary-prediction-v1',scored_utc=datetime.now(timezone.utc).isoformat(),
        post_registration_secondary_diagnostic=True,model_sha256=sha(BUNDLE/'MODEL.json'),
        predictor_sha256=sha(BUNDLE/'predictor.py'),source_manifest_sha256=sha(HERE/'SOURCES.json'),
        registration_sha256=sha(HERE/'REGISTRATION.json'),coverage=coverage,results=results,
        trained_or_tuned=False,new_solver_calls=0,new_physical_episodes=0,
        interpretation='Frozen predictions on common history_no_query states; separate from deployed-policy scheduling performance.')
    save('RESULTS.json',result)
    print(json.dumps({s:{k:{'rows':v['uncensored_rows'],'metrics':v['metrics']} for k,v in result['results'][s].items()} for s in results},indent=2))


if __name__=='__main__':main()
