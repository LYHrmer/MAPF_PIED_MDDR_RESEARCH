"""R20 original TRAIN queries: extraction, nested grouped fitting and freeze."""
import sys
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from position_predictor import FEATURE_NAMES, MODES, features, predict_values
from end_predictor import summarize, predict_values as end_predict

HERE = Path(__file__).resolve().parent
R18 = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_benchmark_20261005_r18')
R19MODEL = HERE.parent/'conditional_duration_20261005_r19'
ALPHAS = [.01, .1, 1., 10.]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, data):
    (HERE/name).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n')


def save_rows(name, rows):
    with (HERE/name).open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as f:
            for row in rows:
                f.write((json.dumps(row, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode())


def extract(paths, source_split='TRAIN'):
    captures, deliveries, consumers, sources = [], [], [], []
    unique = set()
    for path in paths:
        receipt_path = path.parent/'RUN_RECEIPT.json'
        receipt = json.loads(receipt_path.read_text())
        raw = json.loads(path.read_text()); spec = receipt['spec']
        if source_split == 'TRAIN':
            case = spec['case']; assert case['split'] == 'TRAIN' and case['scenario_id'] in [1, 2]
            assert spec['arm'] == 'history_rule'
            world, family = path.parent.parent.name, case['family']
        else:
            world, family = spec['world'], spec['family']
        assert sha(path) == receipt['episode_sha256'] and raw['success'] and raw['status'] == 'completed'
        starts = {(e['agent'], e['vertex']):e for e in raw['events'] if e['kind'] == 'START'}
        ends = {(e['agent'], e['vertex']):e for e in raw['events'] if e['kind'] == 'END'}
        position_events = {e['query_id']:e for e in raw['events'] if e['kind'] == 'POSITION_DELIVER'}
        action = {}; prior = {}; previous = {}
        for aid, history in raw['delivered_end_history'].items():
            prev_end = 0.0
            for i,h in enumerate(history):
                key = (aid,h['vertex']); s,e,n,d = (float(h[k]) for k in ['start','end','nominal_duration','duration'])
                assert key in starts and key in ends and abs(starts[key]['time']-s)<1e-8 and abs(ends[key]['time']-e)<1e-8
                assert abs(e-s-d)<1e-8 and d>0 and n>0 and h['delivered']==e and prev_end<=s+1e-8
                assert all(x['delivered']<=s+1e-8 for x in history[:i])
                action[key]=h;prior[key]=history[:i];previous[key]=prev_end;prev_end=e
        assert len(starts)==len(ends)==len(action)
        local = {}; world_deliveries=0; world_consumers=0
        for q in raw['queries']:
            aid, vertex = q['agent'],q['vertex']; h=action[(aid,vertex)]
            t, delivered = q['captured'],q['delivered_at']; e=t-h['start']; r=h['end']-t
            assert e>=-1e-8 and r>0 and 0<=q['progress']<=1
            hh=prior[(aid,vertex)]; assert all(x['delivered']<=t+1e-8 for x in hh)
            ev=position_events[q['query_id']]
            assert ev['agent']==aid and ev['vertex']==vertex and ev['status']==q['delivery_status']
            assert abs(ev['time']-delivered)<1e-8
            key=f'{world}|{aid}|{vertex}|{t:.17g}'
            assert key not in unique;unique.add(key)
            stats=summarize(hh); nominal=float(h['nominal_duration'])
            row=dict(key=key,world=world,family=family,agent=aid,vertex=vertex,query_id=q['query_id'],
                gate_index=q['gate_index'],nominal=nominal,start=h['start'],end=h['end'],captured=t,
                capture_elapsed=max(0.,e),progress=q['progress'],delivered=delivered,
                delivery_status=q['delivery_status'],capture_remaining=r,age=0.,remaining=r,
                dependency_wait=max(0.,h['start']-previous[(aid,vertex)]),stats=stats,
                x=features(nominal,max(0.,e),q['progress'],stats),history=hh,
                query_body_sha256=q['body_sha256'])
            captures.append(row);local[q['query_id']]=row
            if q['delivery_status']=='accepted' and h['end']>delivered+1e-8:
                deliveries.append(dict(row,key=key+'|delivery',capture_key=key,
                    age=delivered-t,remaining=h['end']-delivered,time=delivered));world_deliveries+=1
            else:
                assert q['delivery_status']=='stale_occurrence' or h['end']<=delivered+1e-8
        for solve in raw['solves']:
            t=solve['time']
            for aid,hh in raw['delivered_end_history'].items():
                active=[h for h in hh if h['start']<=t+1e-8 and h['end']>t+1e-8]
                assert len(active)<=1
                if not active: continue
                h=active[0]
                qs=[q for q in raw['queries'] if q['agent']==aid and q['vertex']==h['vertex']
                    and q['delivery_status']=='accepted' and q['delivered_at']<=t+1e-8]
                if not qs: continue
                q=max(qs,key=lambda z:(z['delivered_at'],z['query_id']));row=local[q['query_id']]
                consumers.append(dict(row,key=row['key']+'|solve'+str(solve['gate_index']),capture_key=row['key'],
                    age=t-row['captured'],remaining=h['end']-t,time=t));world_consumers+=1
        sources.append(dict(world=world,family=family,episode=str(path),episode_sha256=sha(path),
            receipt=str(receipt_path),receipt_sha256=sha(receipt_path),source_arm=spec['arm'],
            capture_rows=len(local),accepted_delivery_rows=world_deliveries,consumer_rows=world_consumers,
            stale_at_delivery=sum(q['delivery_status']=='stale_occurrence' for q in raw['queries']),
            terminal_censored_actions=0))
    return captures,deliveries,consumers,sources


def weights(rows):
    groups=defaultdict(set);count=Counter()
    for r in rows: groups[r['family']].add(r['world']);count[r['world']]+=1
    return np.asarray([1/(len(groups)*len(groups[r['family']])*count[r['world']]) for r in rows])


def fit(rows, alpha):
    w=weights(rows);x=np.asarray([r['x'] for r in rows]);y=np.log([r['capture_remaining']/r['nominal'] for r in rows])
    mean=w@x;scale=np.sqrt(w@((x-mean)**2));scale[scale<1e-10]=1.
    z=np.column_stack([np.ones(len(rows)),(x-mean)/scale]);pen=np.eye(z.shape[1])*alpha;pen[0,0]=0.
    lhs=z.T@(w[:,None]*z)+pen;rhs=z.T@(w*y);b=np.linalg.solve(lhs,rhs);res=y-z@b
    constant=float(w@y)
    return dict(schema='r20-position-capture-lognormal-v1',feature_names=FEATURE_NAMES,alpha=alpha,
        mean=mean.tolist(),scale=scale.tolist(),intercept=float(b[0]),coefficients=b[1:].tolist(),
        sigma=max(.05,math.sqrt(float(w@(res*res)))),constant=dict(mu=constant,sigma=max(.05,math.sqrt(float(w@((y-constant)**2))))),
        train_families=sorted({r['family'] for r in rows}),train_worlds=sorted({r['world'] for r in rows}),
        train_rows=len(rows),normal_equation_residual=float(np.max(abs(lhs@b-rhs))))


def predict(model, end_model, mode, r):
    n,e,p,a,s=r['nominal'],r['capture_elapsed'],r['progress'],r['age'],r['stats']
    if mode.startswith('position_'):
        return predict_values(model,n,e,p,a,s,mode=='position_constant')[0]
    if mode in ('history_linear','ewma_linear'):
        return max(0.,(1-p)*n*s['all_history' if mode=='history_linear' else 'ewma03']-a)
    if mode=='observed_average' and p>1e-6:
        return max(0.,e*(1-p)/p-a)
    end_mode='learned' if mode=='end_learned' else 'ewma03_survival'
    return end_predict(end_model,end_mode,n,e+a,s)[0]


def metrics(rows, predictions):
    w=weights(rows);err=np.asarray(predictions)-[r['remaining'] for r in rows]
    return dict(mae=float(w@abs(err)),mse=float(w@(err*err)),bias=float(w@err),
        rows=len(rows),worlds=len({r['world'] for r in rows}),families=len({r['family'] for r in rows}))


def main():
    captures,deliveries,consumers,sources=extract(sorted((R18/'episodes/TRAIN').glob('*/history_rule/episode.json')))
    assert len(sources)==54 and len({s['family'] for s in sources})==6
    for name,rows in [('TRAIN_CAPTURES.jsonl.gz',captures),('TRAIN_DELIVERIES.jsonl.gz',deliveries),('TRAIN_CONSUMERS.jsonl.gz',consumers)]:save_rows(name,rows)
    save('TRAIN_SOURCES.json',sources)
    save('DATA_AUDIT.json',dict(passed=True,source_worlds=54,source_families=6,captures=len(captures),
        deliveries=len(deliveries),consumers=len(consumers),stale_at_delivery=sum(s['stale_at_delivery'] for s in sources),
        worlds_without_queries=[s['world'] for s in sources if not s['capture_rows']],
        captures_per_family=dict(Counter(r['family'] for r in captures)),
        delivery_rows_per_family=dict(Counter(r['family'] for r in deliveries)),
        nominal_values=sorted({r['nominal'] for r in captures}),
        duplicated_capture_keys=0,terminal_censored=0,new_scientific_episodes=0,
        current_or_future_END_used_as_feature=False,private_disturbance_used_as_feature=False))
    families=sorted({s['family'] for s in sources});assert {r['family'] for r in deliveries}==set(families)
    c={f:[r for r in captures if r['family']==f] for f in families}
    d={f:[r for r in deliveries if r['family']==f] for f in families}
    cache={}
    def get(train,alpha):
        key=tuple(sorted(train))+(alpha,)
        if key not in cache:cache[key]=fit([r for f in sorted(train) for r in c[f]],alpha)
        return cache[key]
    def select(train):
        curves=[]
        for alpha in ALPHAS:
            folds=[]
            for validation in train:
                model=get([f for f in train if f!=validation],alpha)
                score=metrics(d[validation],[predict(model,None,'position_learned',r) for r in d[validation]])
                folds.append(dict(validation_family=validation,train_families=model['train_families'],**score))
            curves.append(dict(alpha=alpha,mse=float(np.mean([z['mse'] for z in folds])),folds=folds))
        best=min(z['mse'] for z in curves);chosen=max(z['alpha'] for z in curves if z['mse']<=best+1e-10)
        return chosen,curves
    old_cv=json.loads((R19MODEL/'CV.json').read_text());old_outer={o['heldout_family']:o['model'] for o in old_cv['outer']}
    outer=[];oofs={k:[] for k in ['capture','delivery','consumer']}
    for heldout in families:
        train=[f for f in families if f!=heldout];alpha,curves=select(train);model=get(train,alpha)
        end_model=old_outer[heldout];assert heldout not in end_model['train_families'] and set(train)==set(end_model['train_families'])
        scores={}
        for name,rows in [('capture',captures),('delivery',deliveries),('consumer',consumers)]:
            rows=[r for r in rows if r['family']==heldout]
            pred={mode:[predict(model,end_model,mode,r) for r in rows] for mode in MODES}
            scores[name]={mode:metrics(rows,pred[mode]) for mode in MODES}
            for i,r in enumerate(rows):
                oofs[name].append(dict(key=r['key'],world=r['world'],family=heldout,actual=r['remaining'],
                    predictions={mode:pred[mode][i] for mode in MODES}))
        outer.append(dict(heldout_family=heldout,selected_alpha=alpha,inner_cv=curves,model=model,
            end_model=end_model,metrics=scores))
        print(json.dumps(dict(heldout=heldout,alpha=alpha,delivery=scores['delivery']['position_learned'])),flush=True)
    alpha,curves=select(families);model=get(families,alpha)
    model.update(training_source_manifest_sha256=sha(HERE/'TRAIN_SOURCES.json'),
        design_card_sha256=sha(HERE/'DESIGN_CARD.md'),predictor_sha256=sha(HERE/'position_predictor.py'),
        training_script_sha256=sha(HERE/'study.py'),selection_scope='TRAIN six-family nested LOFO; accepted delivery MSE')
    save('MODEL.json',model)
    save('CV.json',dict(outer=outer,final_selection=curves,selected_alpha=alpha,fits=list(cache.values()),
        fit_count=len(cache),r19_baseline_cv_sha256=sha(R19MODEL/'CV.json')))
    results={}
    for name,rows in oofs.items():
        save_rows('OOF_'+name.upper()+'.jsonl.gz',rows)
        w=weights(rows);y=np.asarray([r['actual'] for r in rows]);results[name]={}
        for mode in MODES:
            err=np.asarray([r['predictions'][mode] for r in rows])-y
            results[name][mode]=dict(mae=float(w@abs(err)),mse=float(w@(err*err)),bias=float(w@err))
    results.update(selected_alpha=alpha,outer_folds=6,source_worlds=54,capture_rows=len(captures),
        accepted_delivery_rows=len(deliveries),consumer_rows=len(consumers),new_scientific_episodes=0,
        scope='Nested grouped OOF on R18 TRAIN queried locations only, not scheduling effect or new TEST')
    save('RESULTS.json',results)
    save('MODEL_FREEZE.json',dict(frozen_utc=datetime.now(timezone.utc).isoformat(),
        model_sha256=sha(HERE/'MODEL.json'),predictor_sha256=sha(HERE/'position_predictor.py'),
        end_predictor_sha256=sha(HERE/'end_predictor.py'),pinned_end_model_sha256=sha(HERE/'PINNED_END_MODEL.json'),
        training_script_sha256=sha(HERE/'study.py'),source_manifest_sha256=sha(HERE/'TRAIN_SOURCES.json'),
        registration_sha256=sha(HERE/'REGISTRATION.json'),no_CAL_or_TEST_training=True,new_scientific_episodes=0))
    print(json.dumps(results,indent=2),flush=True)


if __name__=='__main__': main()
