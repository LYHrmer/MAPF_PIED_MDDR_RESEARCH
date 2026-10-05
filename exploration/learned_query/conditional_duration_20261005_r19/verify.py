"""Read-only algebra/data/runtime checks; no training or scientific execution."""
import sys
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import log_ndtr
from predictor import DurationPredictor, conditional_mean, MODES

P=Path(__file__).resolve().parent


def read(name):return json.loads((P/name).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows(name):
    with gzip.open(P/name,'rt') as f:return [json.loads(line) for line in f]


def weights(rs):
    counts=Counter(r['world'] for r in rs);fs=defaultdict(set)
    for r in rs:fs[r['family']].add(r['world'])
    return np.array([1/(len(fs)*len(fs[r['family']])*counts[r['world']]) for r in rs])


def independent_stats(history, nominal):
    q=[float(h['duration'])/float(h['nominal_duration']) for h in history]
    whole=sum(h['duration'] for h in history)/sum(h['nominal_duration'] for h in history) if q else 1.
    recent=history[-4:]
    last4=sum(h['duration'] for h in recent)/sum(h['nominal_duration'] for h in recent) if q else 1.
    ewma=1.
    for ratio in q:ewma=.7*ewma+.3*ratio
    cv=float(np.std(q)/np.mean(q)) if q else 0.
    x=[math.log(nominal),math.log1p(len(q)),math.log(whole),math.log(last4),
       math.log(ewma),math.log(q[-1] if q else 1.),cv,math.log(last4)-math.log(whole)]
    return x


def independent_predictions(model, rs, mode, active):
    nominal=np.array([r['nominal'] for r in rs])
    age=np.array([r['elapsed'] if active else 0. for r in rs])
    if mode in ['nominal','all_history','recent4','ewma03']:
        ratio=np.ones(len(rs)) if mode=='nominal' else np.array([r['stats'][mode] for r in rs])
        return np.maximum(0,nominal*ratio-age)
    if mode=='learned':
        x=np.array([r['x'] for r in rs]);mu=(x-model['mean'])/model['scale']@np.array(model['coefficients'])+model['intercept']
        sigma=model['sigma']
    elif mode=='constant_survival':mu=np.full(len(rs),model['constant']['mu']);sigma=model['constant']['sigma']
    else:
        key=mode[:-9];sigma=model['baseline_sigma'][key]
        mu=np.log([r['stats'][key] for r in rs])-.5*sigma*sigma
    mu=np.clip(mu,-20,20)+np.log(nominal);sigma=max(.05,min(5.,sigma))
    result=np.exp(mu+.5*sigma*sigma);positive=age>0
    z=(np.log(age[positive])-mu[positive])/sigma
    log_total=mu[positive]+.5*sigma*sigma+log_ndtr(sigma-z)-log_ndtr(-z)
    result[positive]=np.maximum(1e-9,age[positive]*np.expm1(np.maximum(0,log_total-np.log(age[positive]))))
    return result


def main():
    actions=rows('TRAIN_ACTIONS.jsonl.gz');landmarks=rows('TRAIN_LANDMARKS.jsonl.gz')
    source=read('TRAIN_SOURCES.json');cv=read('CV.json');freeze=read('MODEL_FREEZE.json')
    registration=read('REGISTRATION.json')
    for name,key in [('MODEL.json','model_sha256'),('predictor.py','predictor_sha256'),('study.py','training_script_sha256'),
                     ('TRAIN_SOURCES.json','source_manifest_sha256'),('DESIGN_CARD.md','design_sha256')]:
        assert sha(P/name)==freeze[key]
    for name,digest in registration['files'].items():assert sha(P/name)==digest
    assert registration['registered_utc']<freeze['frozen_utc']
    indexed={r['key']:r for r in actions};assert len(indexed)==len(actions)
    histories={};max_feature_error=0.
    for s in source:
        assert '/TRAIN/' in s['episode'] and s['source_arm']=='history_rule'
        assert sha(s['episode'])==s['episode_sha256'] and sha(s['receipt'])==s['receipt_sha256']
        raw=json.loads(Path(s['episode']).read_text())
        receipt=json.loads(Path(s['receipt']).read_text())
        assert receipt['spec']['case']['split']=='TRAIN'
        for aid,hs in raw['delivered_end_history'].items():
            earlier=[];previous_end=0.
            for h in hs:
                key='|'.join([s['world'],aid,h['vertex']]);row=indexed[key]
                x=independent_stats(earlier,h['nominal_duration'])
                max_feature_error=max(max_feature_error,max(abs(a-b) for a,b in zip(x,row['x'])))
                assert all(e['delivered']<=h['start'] for e in earlier)
                assert abs(row['duration']-(h['end']-h['start']))<1e-8
                assert abs(row['dependency_wait']-(h['start']-previous_end))<1e-8
                histories[key]=list(earlier)
                earlier.append(h);previous_end=h['end']
    assert max_feature_error<1e-10
    max_gradient=max_moment_error=0.
    for fit in cv['fits']:
        selected=[r for r in actions if r['family'] in fit['train_families']]
        assert len(selected)==fit['train_rows']
        assert sorted({r['world'] for r in selected})==fit['train_worlds']
        x=np.array([r['x'] for r in selected]);y=np.log([r['duration']/r['nominal'] for r in selected]);w=weights(selected)
        mean=w@x;scale=np.sqrt(w@((x-mean)**2));scale[scale<1e-10]=1.
        max_moment_error=max(max_moment_error,float(np.max(abs(mean-fit['mean']))),float(np.max(abs(scale-fit['scale']))))
        z=np.column_stack([np.ones(len(selected)),(x-mean)/scale]);beta=np.array([fit['intercept']]+fit['coefficients'])
        penalty=fit['alpha']*beta;penalty[0]=0.
        grad=z.T@(w*(z@beta-y))+penalty
        max_gradient=max(max_gradient,float(max(abs(grad))))
        assert abs(fit['sigma']-max(.05,math.sqrt(float(w@((y-z@beta)**2)))))<1e-10
    assert max_gradient<1e-9 and max_moment_error<1e-10
    max_prediction_error=0.
    oof={name:{r['key']:r for r in rows(file)} for name,file in
         [('action_start','OOF_ACTIONS.jsonl.gz'),('active_gate','OOF_LANDMARKS.jsonl.gz')]}
    for outer in cv['outer']:
        held=outer['heldout_family'];assert held not in outer['model']['train_families']
        for curve in outer['inner_cv']:
            for fold in curve['folds']:
                assert held not in fold['train_families'] and held!=fold['validation_family']
                assert fold['validation_family'] not in fold['train_families']
                train=fold['train_families']
                m=next(m for m in cv['fits'] if m['train_families']==train and m['alpha']==curve['alpha'])
                rs=[r for r in landmarks if r['family']==fold['validation_family']]
                residual=independent_predictions(m,rs,'learned',True)-np.array([r['remaining'] for r in rs])
                assert abs(float(weights(rs)@(residual**2))-fold['mse'])<1e-6
            assert abs(curve['mse']-np.mean([f['mse'] for f in curve['folds']]))<1e-10
        best=min(c['mse'] for c in outer['inner_cv'])
        assert outer['selected_alpha']==max(c['alpha'] for c in outer['inner_cv'] if c['mse']<=best+1e-10)
        for active,rs,name in [(False,[r for r in actions if r['family']==held],'action_start'),
                               (True,[r for r in landmarks if r['family']==held],'active_gate')]:
            for mode in MODES:
                pred=independent_predictions(outer['model'],rs,mode,active)
                original=np.array([oof[name][r['key']]['predictions'][mode] for r in rs])
                max_prediction_error=max(max_prediction_error,float(np.max(abs(pred-original))))
    assert max_prediction_error<1e-5
    # Runtime interface is checked at every actual landmark using only its prior ENDs.
    predictor=DurationPredictor(P/'MODEL.json')
    max_runtime_error=0.
    direct=independent_predictions(read('MODEL.json'),landmarks,'learned',True)
    for i,row in enumerate(landmarks):
        context=dict(status='IN_PROGRESS',nominal_duration=row['nominal'],elapsed=row['elapsed'],
                     completed_history=histories[row['action_key']])
        result=predictor(context)
        max_runtime_error=max(max_runtime_error,abs(result['remaining_time']-direct[i]))
        # Unused metadata must never become a hidden feature.
        changed=dict(context,private_truth='forbidden sentinel',case_id='unseen',seed=999,latest_position={'progress':.999})
        assert predictor(changed)==result
        assert result['remaining_time']>0 and result['future_duration_ratio']>0
    assert max_runtime_error<1e-5
    worst=0.
    for mu in [-2.,0.,2.]:
        for sigma in [.05,.2,.5,1.,2.]:
            for age in [0.,.01,.25,.5,1.,2.,4.,20.,100.,10000.]:
                got,_=conditional_mean(mu,sigma,age)
                if age==0:reference=math.exp(mu+.5*sigma*sigma)
                else:
                    z=(math.log(age)-mu)/sigma
                    reference=age*math.expm1(mu+.5*sigma*sigma+log_ndtr(sigma-z)-log_ndtr(-z)-math.log(age))
                worst=max(worst,abs(got-reference)/max(1.,abs(reference)))
    assert worst<1e-5
    try:predictor(dict(status='STAGED',nominal_duration=1,elapsed=5,completed_history=[]))
    except ValueError:pass
    else:raise AssertionError('Dependency waiting accepted as elapsed')
    report=dict(passed=True,source_worlds=len(source),actions=len(actions),landmarks=len(landmarks),
        fits_checked=len(cv['fits']),outer_folds=6,max_feature_error=max_feature_error,
        max_weighted_normal_equation_residual=max_gradient,max_fold_moment_error=max_moment_error,
        max_scipy_oof_prediction_difference=max_prediction_error,max_runtime_prediction_difference=max_runtime_error,
        survival_boundary_cases=150,max_survival_relative_error=worst,
        private_metadata_invariance=True,dependency_wait_rejected=True,
        new_scientific_episodes=0,training_repeated=False,solver_imported=False,
        runtime_requires_scipy=False,scope='Internal implementation validation; separate from root independent audit')
    (P/'VALIDATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
