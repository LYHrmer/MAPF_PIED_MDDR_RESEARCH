"""R19 TRAIN-only dataset, nested grouped fitting and reproducible freeze."""
import sys
sys.dont_write_bytecode = True
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from predictor import FEATURE_NAMES, MODES, features, summarize, predict_values

HERE = Path(__file__).resolve().parent
R18 = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_benchmark_20261005_r18')
ALPHAS = [0.1, 1.0, 10.0]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, data):
    (HERE/name).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n')


def save_rows(name, rows):
    with (HERE/name).open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as f:
            for row in rows:
                f.write((json.dumps(row,sort_keys=True,allow_nan=False,separators=(',',':'))+'\n').encode())


def load_data():
    actions, landmarks, sources = [], [], []
    global_keys = set()
    for path in sorted((R18/'episodes/TRAIN').glob('*/history_rule/episode.json')):
        receipt_path = path.parent/'RUN_RECEIPT.json'
        receipt = json.loads(receipt_path.read_text())
        case = receipt['spec']['case']
        assert case['split'] == 'TRAIN' and case['scenario_id'] in [1,2]
        assert receipt['spec']['arm'] == 'history_rule'
        assert sha(path) == receipt['episode_sha256']
        raw = json.loads(path.read_text())
        assert raw['success'] and raw['status'] == 'completed'
        world, family = path.parent.parent.name, case['family']
        event_starts = {(e['agent'],e['vertex']):e for e in raw['events'] if e['kind']=='START'}
        event_ends = {(e['agent'],e['vertex']):e for e in raw['events'] if e['kind']=='END'}
        per_action = {}
        local_count = 0
        for aid, hs in sorted(raw['delivered_end_history'].items()):
            history = []
            previous_end = 0.0
            for h in hs:
                key = (world,aid,h['vertex'])
                assert key not in global_keys
                global_keys.add(key)
                start, end, nominal, duration = (float(h[k]) for k in ['start','end','nominal_duration','duration'])
                assert abs(end-start-duration)<1e-7 and duration>0 and nominal>0
                assert h['delivered']==end and previous_end<=start+1e-8
                assert abs(event_starts[(aid,h['vertex'])]['time']-start)<1e-8
                assert abs(event_ends[(aid,h['vertex'])]['time']-end)<1e-8
                assert all(x['delivered']<=start+1e-8 for x in history)
                stats = summarize(history)
                row = dict(key='|'.join(key),world=world,family=family,agent=aid,vertex=h['vertex'],
                    start=start,end=end,nominal=nominal,duration=duration,
                    dependency_wait=max(0.0,start-previous_end),stats=stats,x=features(nominal,stats),
                    history_count=len(history),last_history_delivery=history[-1]['delivered'] if history else None)
                actions.append(row);per_action[(aid,h['vertex'])]=row
                history.append(h);previous_end=end;local_count+=1
        assert len(event_starts)==len(event_ends)==local_count
        gate_count=0
        for gate in raw['gates']:
            t=gate['capture_time']
            for agent in gate['public_snapshot']['agents']:
                if agent['status']!='IN_PROGRESS':continue
                action=per_action[(agent['agent_id'],agent['current_vertex'])]
                elapsed=t-action['start']
                assert elapsed>=-1e-8 and action['end']>t-1e-8
                assert abs(elapsed-agent['elapsed'])<1e-7
                assert agent['history_count']==action['history_count']
                assert abs(agent['history_ratio']-action['stats']['all_history'])<1e-7
                assert abs(agent['nominal_duration']-action['nominal'])<1e-7
                landmarks.append(dict(key=action['key']+'|g'+str(gate['gate_index']),action_key=action['key'],
                    world=world,family=family,nominal=action['nominal'],elapsed=max(0.0,elapsed),
                    remaining=max(0.0,action['end']-t),time=t,stats=action['stats'],x=action['x']))
                gate_count+=1
        sources.append(dict(world=world,family=family,episode=str(path),episode_sha256=sha(path),
            receipt=str(receipt_path),receipt_sha256=sha(receipt_path),action_rows=local_count,
            landmark_rows=gate_count,terminal_right_censored=0,source_arm='history_rule'))
    assert len(sources)==54 and len({r['family'] for r in sources})==6
    assert len({r['world'] for r in sources})==54
    save_rows('TRAIN_ACTIONS.jsonl.gz',actions)
    save_rows('TRAIN_LANDMARKS.jsonl.gz',landmarks)
    save('TRAIN_SOURCES.json',sources)
    save('DATA_AUDIT.json',dict(passed=True,source_worlds=len(sources),families=6,actions=len(actions),
        active_gate_landmarks=len(landmarks),unique_action_keys=len(global_keys),terminal_right_censored=0,
        duplicated_counterfactual_trajectories=0,split='TRAIN',arm='history_rule',
        family_world_counts=dict(Counter(s['family'] for s in sources)),
        action_ratio_min=min(a['duration']/a['nominal'] for a in actions),
        action_ratio_max=max(a['duration']/a['nominal'] for a in actions),
        total_dependency_wait=sum(a['dependency_wait'] for a in actions),
        total_execution_duration=sum(a['duration'] for a in actions),
        nonpublic_predictor_fields=[],feature_names=FEATURE_NAMES,
        labels_are_future_outcomes_only=True,scientific_episode_reruns=0))
    return actions, landmarks


def weights(rows):
    family_worlds=defaultdict(set);counts=Counter()
    for r in rows:family_worlds[r['family']].add(r['world']);counts[r['world']]+=1
    return np.asarray([1/(len(family_worlds)*len(family_worlds[r['family']])*counts[r['world']]) for r in rows])


def fit(rows, alpha):
    w=weights(rows)
    x=np.asarray([r['x'] for r in rows]);y=np.asarray([math.log(r['duration']/r['nominal']) for r in rows])
    mean=w@x;scale=np.sqrt(w@((x-mean)**2));scale[scale<1e-10]=1.0
    z=np.column_stack([np.ones(len(rows)),(x-mean)/scale])
    penalty=np.eye(z.shape[1])*alpha;penalty[0,0]=0.0
    lhs=z.T@(w[:,None]*z)+penalty;rhs=z.T@(w*y)
    beta=np.linalg.solve(lhs,rhs)
    residual=y-z@beta
    sigma=max(.05,math.sqrt(float(w@(residual**2))))
    constant=float(w@y)
    baseline={k:max(.05,math.sqrt(float(w@((y-np.log([r['stats'][k] for r in rows]))**2))))
              for k in ['all_history','recent4','ewma03']}
    return dict(schema='r19-public-end-lognormal-v1',feature_names=FEATURE_NAMES,alpha=alpha,
        mean=mean.tolist(),scale=scale.tolist(),intercept=float(beta[0]),coefficients=beta[1:].tolist(),
        sigma=sigma,constant=dict(mu=constant,sigma=max(.05,math.sqrt(float(w@((y-constant)**2))))),
        baseline_sigma=baseline,train_families=sorted({r['family'] for r in rows}),
        train_worlds=sorted({r['world'] for r in rows}),train_rows=len(rows),
        normal_equation_residual=float(np.max(np.abs(lhs@beta-rhs))))


def predictions(model, mode, rows, active):
    return np.asarray([predict_values(model,mode,r['nominal'],r['elapsed'] if active else 0.,r['stats'])[0] for r in rows])


def metrics(rows, predicted, active):
    truth=np.asarray([r['remaining'] if active else r['duration'] for r in rows]);w=weights(rows)
    e=predicted-truth
    return dict(mae=float(w@np.abs(e)),mse=float(w@(e*e)),bias=float(w@e),rows=len(rows),
        families=len({r['family'] for r in rows}),worlds=len({r['world'] for r in rows}))


def main():
    actions,landmarks=load_data()
    families=sorted({r['family'] for r in actions})
    grouped_a={f:[r for r in actions if r['family']==f] for f in families}
    grouped_l={f:[r for r in landmarks if r['family']==f] for f in families}
    model_cache={}
    def get(train,alpha):
        key=tuple(sorted(train))+(alpha,)
        if key not in model_cache:
            model_cache[key]=fit([r for f in sorted(train) for r in grouped_a[f]],alpha)
        return model_cache[key]
    def select(train):
        curves=[]
        for alpha in ALPHAS:
            fold=[]
            for validation in train:
                m=get([f for f in train if f!=validation],alpha)
                rows=grouped_l[validation]
                score=metrics(rows,predictions(m,'learned',rows,True),True)
                fold.append(dict(validation_family=validation,train_families=m['train_families'],**score))
            curves.append(dict(alpha=alpha,mse=float(np.mean([x['mse'] for x in fold])),folds=fold))
        best=min(x['mse'] for x in curves)
        chosen=max(x['alpha'] for x in curves if x['mse']<=best+1e-10)
        return chosen,curves
    outer=[];oof_actions=[];oof_landmarks=[]
    for heldout in families:
        train=[f for f in families if f!=heldout]
        alpha,curves=select(train)
        model=get(train,alpha)
        results={}
        for active,rows,name,out in [(False,grouped_a[heldout],'action_start',oof_actions),
                                    (True,grouped_l[heldout],'active_gate',oof_landmarks)]:
            pred={mode:predictions(model,mode,rows,active) for mode in MODES}
            results[name]={mode:metrics(rows,p,active) for mode,p in pred.items()}
            for i,row in enumerate(rows):
                out.append(dict(key=row['key'],world=row['world'],family=heldout,
                    actual=row['remaining'] if active else row['duration'],
                    predictions={mode:float(p[i]) for mode,p in pred.items()}))
        outer.append(dict(heldout_family=heldout,selected_alpha=alpha,inner_cv=curves,
                          model=model,metrics=results))
        print(json.dumps(dict(heldout=heldout,alpha=alpha,active=results['active_gate']['learned'])),flush=True)
    alpha,final_curves=select(families)
    model=get(families,alpha)
    model['selection_scope']='TRAIN six-family LOFO; external six-fold nested OOF retained separately'
    model['training_source_manifest_sha256']=sha(HERE/'TRAIN_SOURCES.json')
    model['design_card_sha256']=sha(HERE/'DESIGN_CARD.md')
    model['predictor_sha256']=sha(HERE/'predictor.py')
    model['training_script_sha256']=sha(HERE/'study.py')
    save('MODEL.json',model)
    save('CV.json',dict(outer=outer,final_selection=final_curves,selected_alpha=alpha,
                        fits=list(model_cache.values()),fit_count=len(model_cache)))
    save_rows('OOF_ACTIONS.jsonl.gz',oof_actions);save_rows('OOF_LANDMARKS.jsonl.gz',oof_landmarks)
    report={}
    for name,rows in [('action_start',oof_actions),('active_gate',oof_landmarks)]:
        w=weights(rows);y=np.asarray([r['actual'] for r in rows])
        report[name]={}
        for mode in MODES:
            error=np.asarray([r['predictions'][mode] for r in rows])-y
            report[name][mode]=dict(mae=float(w@abs(error)),mse=float(w@(error*error)),bias=float(w@error))
    report.update(dict(selected_alpha=alpha,outer_folds=6,train_worlds=54,
        action_rows=len(actions),active_landmarks=len(landmarks),new_scientific_episodes=0,
        eval_scope='Nested grouped OOF on R18 TRAIN only; not R19 TEST or scheduling outcomes'))
    save('RESULTS.json',report)
    save('MODEL_FREEZE.json',dict(frozen_utc=datetime.now(timezone.utc).isoformat(),model_sha256=sha(HERE/'MODEL.json'),
        predictor_sha256=sha(HERE/'predictor.py'),training_script_sha256=sha(HERE/'study.py'),
        source_manifest_sha256=sha(HERE/'TRAIN_SOURCES.json'),design_sha256=sha(HERE/'DESIGN_CARD.md'),
        no_CAL_or_TEST_training=True,new_scientific_episodes=0))
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
