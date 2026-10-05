"""Independent raw-history/math/weight check; does not import the scorer/predictor."""
import sys
sys.dont_write_bytecode=True
from collections import defaultdict,Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import log_ndtr

P=Path(__file__).resolve().parent;B=P.parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(name):
    with gzip.open(P/name,'rt') as f:return [json.loads(s) for s in f]


def features(history,nominal):
    qs=[h['duration']/h['nominal_duration'] for h in history]
    ratio=sum(h['duration'] for h in history)/sum(h['nominal_duration'] for h in history) if qs else 1.
    hh=history[-4:];recent=sum(h['duration'] for h in hh)/sum(h['nominal_duration'] for h in hh) if qs else 1.
    ewma=1.
    for q in qs:ewma=.7*ewma+.3*q
    cv=float(np.std(qs)/np.mean(qs)) if qs else 0.
    x=[math.log(nominal),math.log1p(len(qs)),math.log(ratio),math.log(recent),math.log(ewma),
        math.log(qs[-1] if qs else 1.),cv,math.log(recent)-math.log(ratio)]
    return x,dict(nominal=1.,all_history=ratio,recent4=recent,ewma03=ewma)


def main():
    registration=read(P/'REGISTRATION.json');model=read(B/'MODEL.json');report=read(P/'RESULTS.json');sources=read(P/'SOURCES.json')
    assert sha(B/'MODEL.json')==registration['model_sha256']==report['model_sha256']
    assert sha(B/'predictor.py')==registration['predictor_sha256']==report['predictor_sha256']
    assert sha(P/'score.py')==registration['score_sha256'] and sha(P/'PROTOCOL.md')==registration['protocol_sha256']
    data={'action_start':rows('ACTION_PREDICTIONS.jsonl.gz'),'active_gate':rows('ACTIVE_PREDICTIONS.jsonl.gz')}
    byworld={name:defaultdict(list) for name in data}
    for name,rr in data.items():
        assert len({r['key'] for r in rr})==len(rr)
        for r in rr:byworld[name][r['world']].append(r)
    max_error=0.;checked=0
    for source in sources:
        raw=read(source['episode']);receipt=read(source['receipt'])
        assert sha(source['episode'])==source['episode_sha256']==receipt['episode_sha256']
        assert sha(source['receipt'])==source['receipt_sha256']
        assert receipt['spec']['arm']=='history_no_query' and raw['query_count']==0
        starts={e['vertex']:e for e in raw['events'] if e['kind']=='START'}
        ends={e['vertex']:e for e in raw['events'] if e['kind']=='END'}
        for name in data:
            rr=byworld[name][source['world']];xx=[];ratios=[];ages=[];nominals=[]
            for r in rr:
                tokens=r['key'].split('|');aid,uid=tokens[1:3];t=r['time']
                assert starts[uid]['agent']==aid
                history=[h for h in raw['delivered_end_history'][aid] if h['delivered']<=t+1e-9 and h['vertex']!=uid]
                assert all(h['end']<=t+1e-9 and h['delivered']==h['end'] for h in history)
                age=t-starts[uid]['time'] if name=='active_gate' else 0.
                if name=='action_start':assert t==starts[uid]['time']
                else:assert abs(age-r['elapsed'])<1e-8 and raw['gates'][int(tokens[3][1:])]['capture_time']==t
                if uid in ends:
                    assert abs((ends[uid]['time']-t)-r['label'])<1e-8
                    assert abs(ends[uid]['nominal_duration']-r['nominal_duration'])<1e-8
                else:assert r['label'] is None
                f,rs=features(history,r['nominal_duration']);xx.append(f);ratios.append(rs);ages.append(age);nominals.append(r['nominal_duration'])
                assert r['history_stats']['count']==len(history)
                assert r['last_history_delivery']==(history[-1]['delivered'] if history else None)
                for k in ['all_history','recent4','ewma03']:assert abs(rs[k]-r['history_stats'][k])<1e-10
            x=np.array(xx);age=np.array(ages);nominal=np.array(nominals)
            for mode in registration['modes']:
                if mode in ['nominal','all_history','recent4','ewma03']:
                    pred=np.maximum(0,nominal*np.array([d[mode] for d in ratios])-age)
                else:
                    if mode=='learned':mu=(x-model['mean'])/model['scale']@np.array(model['coefficients'])+model['intercept'];sigma=model['sigma']
                    elif mode=='constant_survival':mu=np.full(len(rr),model['constant']['mu']);sigma=model['constant']['sigma']
                    else:
                        key=mode[:-9];sigma=model['baseline_sigma'][key];mu=np.log([d[key] for d in ratios])-.5*sigma*sigma
                    sigma=max(.05,min(5.,sigma));mu=np.clip(mu,-20,20)+np.log(nominal)
                    pred=np.exp(mu+.5*sigma*sigma);positive=age>0
                    z=(np.log(age[positive])-mu[positive])/sigma
                    logtotal=mu[positive]+.5*sigma*sigma+log_ndtr(sigma-z)-log_ndtr(-z)
                    pred[positive]=np.maximum(1e-9,age[positive]*np.expm1(np.maximum(0,logtotal-np.log(age[positive]))))
                actual=np.array([r['predictions'][mode] for r in rr])
                max_error=max(max_error,float(np.max(abs(pred-actual))))
                checked+=len(rr)
    assert max_error<1e-6
    metric_checks=0
    for stratum in report['results']:
        for name,rr in data.items():
            rs=[r for r in rr if r['stratum']==stratum and r['label'] is not None]
            fs=defaultdict(set);counts=Counter(r['world'] for r in rs)
            for r in rs:fs[r['family']].add(r['world'])
            w=np.array([1/(len(fs)*len(fs[r['family']])*counts[r['world']]) for r in rs])
            assert abs(float(sum(w))-1)<1e-10
            summary=report['results'][stratum][name]
            assert len(rs)==summary['uncensored_rows'] and len(fs)==summary['family_count'] and len(counts)==summary['world_count']
            for mode in registration['modes']:
                error=np.array([r['predictions'][mode]-r['label'] for r in rs])
                vals={'mae':float(w@abs(error)),'mse':float(w@(error*error)),'bias':float(w@error)}
                for k,v in vals.items():assert abs(v-summary['metrics'][mode][k])<1e-10;metric_checks+=1
                for world,n in counts.items():
                    ee=np.array([r['predictions'][mode]-r['label'] for r in rs if r['world']==world])
                    for k,v in [('mae',float(np.mean(abs(ee)))),('mse',float(np.mean(ee*ee))),('bias',float(np.mean(ee)))]:
                        assert abs(v-summary['worlds'][world]['metrics'][mode][k])<1e-10;metric_checks+=1
    result=dict(passed=True,canonical_worlds=len(sources),action_rows=len(data['action_start']),active_rows=len(data['active_gate']),
        independently_recomputed_predictions=checked,max_scipy_prediction_difference=max_error,metric_checks=metric_checks,
        scorer_or_predictor_imported=False,training_performed=False,new_solver_or_physical_episodes=0,
        source_manifest_sha256=sha(P/'SOURCES.json'),results_sha256=sha(P/'RESULTS.json'))
    (P/'VERIFICATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
