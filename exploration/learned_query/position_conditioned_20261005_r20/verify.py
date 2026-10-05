"""Raw-data and mathematical verification; no trainer import or physical rerun."""
import sys
sys.dont_write_bytecode=True
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from independent_math import evaluate_position,evaluate_end,feature_vector,history_summary,make_context
from position_predictor import PositionPredictor

HERE=Path(__file__).resolve().parent
checks=0


def check(v,msg):
    global checks
    checks+=1
    if not v:raise AssertionError(msg)


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name):return json.loads((HERE/name).read_text())


def rows(name):
    with gzip.open(HERE/name,'rt') as f:return [json.loads(line) for line in f]


def weighting(records):
    groups=defaultdict(set);counts=Counter()
    for r in records:groups[r['family']].add(r['world']);counts[r['world']]+=1
    return np.array([1/len(groups)/len(groups[r['family']])/counts[r['world']] for r in records])


def main():
    capture=rows('TRAIN_CAPTURES.jsonl.gz');deliver=rows('TRAIN_DELIVERIES.jsonl.gz');consume=rows('TRAIN_CONSUMERS.jsonl.gz')
    sources=load('TRAIN_SOURCES.json');cv=load('CV.json');model=load('MODEL.json');freeze=load('MODEL_FREEZE.json')
    check(sha(HERE/'MODEL.json')==freeze['model_sha256'],'model freeze')
    check(sha(HERE/'position_predictor.py')==freeze['predictor_sha256'],'code freeze')
    check(sha(HERE/'end_predictor.py')==freeze['end_predictor_sha256'],'arithmetic source freeze')
    check(load('REGISTRATION.json')['registered_utc']<load('IMPLEMENTATION_REGISTRATION.json')['registered_utc']<freeze['frozen_utc'],'registration chronology')
    byworld=defaultdict(list)
    for r in capture:byworld[r['world']].append(r)
    max_feature=0.;max_capture_position=0.;raw_queries=0;wait_rows=0
    for source in sources:
        p=Path(source['episode']);rp=Path(source['receipt'])
        check(sha(p)==source['episode_sha256'] and sha(rp)==source['receipt_sha256'],'source hashes')
        raw=json.loads(p.read_text());receipt=json.loads(rp.read_text())
        check(receipt['spec']['case']['split']=='TRAIN' and receipt['spec']['arm']=='history_rule','TRAIN only')
        check(raw['success'] and raw['status']=='completed','complete trajectory')
        vertices={v['uid']:v for v in raw['initial_graph']['vertices']}
        queries={q['query_id']:q for q in raw['queries']}
        check(len(byworld[source['world']])==len(queries),'all captures retained including stale')
        raw_queries+=len(queries)
        for r in byworld[source['world']]:
            q=queries[r['query_id']];history=raw['delivered_end_history'][q['agent']]
            current=next(h for h in history if h['vertex']==q['vertex'])
            hh=[h for h in history if h['delivered']<=q['captured']+1e-8]
            check(current not in hh and hh==r['history'],'public history delivery cut')
            check(current['start']<=q['captured']<current['end'],'active capture and future label')
            check(abs(r['capture_elapsed']-(q['captured']-current['start']))<1e-8,'elapsed excludes wait')
            check(abs(r['capture_remaining']-(current['end']-q['captured']))<1e-8,'remaining label')
            prev=max([h['end'] for h in hh],default=0.)
            check(abs(r['dependency_wait']-max(0.,current['start']-prev))<1e-8,'WAIT separate')
            wait_rows+=r['dependency_wait']>0
            v=vertices[q['vertex']];a=np.array(v['path'][0][:2],float);b=np.array(v['path'][-1][:2],float)
            length=float(np.linalg.norm(b-a));check(abs(r['nominal']-length/2)<1e-8,'public nominal geometry')
            ss=[s for s in raw['segments'] if s['agent']==q['agent'] and s['vertex']==q['vertex'] and s['t0']<=q['captured']+1e-8 and s['t1']>=q['captured']-1e-8]
            check(bool(ss),'physical capture segment present')
            segment=ss[-1];fraction=(q['captured']-segment['t0'])/(segment['t1']-segment['t0'])
            point=np.array(segment['p0'])+fraction*(np.array(segment['p1'])-segment['p0'])
            progress=float((point-a)@(b-a)/(length*length));max_capture_position=max(max_capture_position,abs(progress-r['progress']))
            check(abs(progress-r['progress'])<1e-7,'actual public queried position')
            body={k:v for k,v in q.items() if k not in ['body_sha256','payload_bytes','delivery_status']}
            check(hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==q['body_sha256'],'query body digest')
            f=feature_vector(r['nominal'],r['capture_elapsed'],r['progress'],hh)
            delta=max(abs(x-y) for x,y in zip(f,r['x']));max_feature=max(max_feature,delta)
            check(delta<1e-10,'independent feature vector')
    check(raw_queries==len(capture)==len({r['key'] for r in capture}),'unique complete capture coverage')
    for records in [deliver,consume]:
        for r in records:
            check(r['delivered']<=r['time']+1e-8<r['end'] and r['delivery_status']=='accepted','only delivered active occurrence consumption')
            check(abs(r['remaining']-(r['end']-r['time']))<1e-8 and abs(r['age']-(r['time']-r['captured']))<1e-8,'consumer age/label')
    max_normal=0.;fits={}
    for fitted in cv['fits']:
        fam=set(fitted['train_families']);rr=[r for r in capture if r['family'] in fam];w=weighting(rr)
        x=np.array([feature_vector(r['nominal'],r['capture_elapsed'],r['progress'],r['history']) for r in rr])
        y=np.log([r['capture_remaining']/r['nominal'] for r in rr]);mean=w@x;scale=np.sqrt(w@((x-mean)**2));scale[scale<1e-10]=1.
        check(np.max(abs(mean-fitted['mean']))<1e-10 and np.max(abs(scale-fitted['scale']))<1e-10,'fold-only standardization')
        z=np.column_stack([np.ones(len(rr)),(x-mean)/scale]);pen=np.diag([0.]+[fitted['alpha']]*(z.shape[1]-1))
        b=np.array([fitted['intercept']]+fitted['coefficients']);res=np.max(abs((z.T@(w[:,None]*z)+pen)@b-z.T@(w*y)))
        max_normal=max(max_normal,float(res));check(res<1e-9,'weighted ridge normal equations')
        sig=max(.05,math.sqrt(float(w@((y-z@b)**2))));check(abs(sig-fitted['sigma'])<1e-10,'sigma training only')
        check(set(fitted['train_worlds'])=={r['world'] for r in rr} and fitted['train_rows']==len(rr),'fit membership')
        for family in fam:check(abs(sum(w[i] for i,r in enumerate(rr) if r['family']==family)-1/len(fam))<1e-10,'equal family weights')
        fits[(tuple(sorted(fam)),fitted['alpha'])]=fitted
    allfamilies=set(r['family'] for r in capture)
    for outer in cv['outer']+[{'heldout_family':None,'inner_cv':cv['final_selection'],'selected_alpha':cv['selected_alpha']}]:
        heldout=outer['heldout_family'];train=allfamilies-({heldout} if heldout else set())
        for curve in outer['inner_cv']:
            computed=[]
            for fold in curve['folds']:
                f=fold['validation_family'];check(set(fold['train_families'])==train-{f},'family isolation')
                fm=fits[(tuple(sorted(train-{f})),curve['alpha'])];rr=[r for r in deliver if r['family']==f]
                pred=np.array([evaluate_position(make_context(r),fm)['remaining_time'] for r in rr])
                err=pred-[r['remaining'] for r in rr];mse=float(weighting(rr)@(err*err))
                check(abs(mse-fold['mse'])<1e-8,'inner score recomputed');computed.append(mse)
            check(abs(np.mean(computed)-curve['mse'])<1e-8,'inner macro MSE')
        best=min(x['mse'] for x in outer['inner_cv']);chosen=max(x['alpha'] for x in outer['inner_cv'] if x['mse']<=best+1e-10)
        check(chosen==outer['selected_alpha'],'registered alpha and tie rule')
        if heldout:check(heldout not in outer['model']['train_families'] and heldout not in outer['end_model']['train_families'],'both models exclude heldout')
    outer={o['heldout_family']:o for o in cv['outer']};max_prediction=0.;prediction_count=0
    for label,records in [('capture',capture),('delivery',deliver),('consumer',consume)]:
        stored={r['key']:r for r in rows('OOF_'+label.upper()+'.jsonl.gz')}
        check(set(stored)=={r['key'] for r in records},'OOF complete')
        for r in records:
            fm=outer[r['family']]['model'];em=outer[r['family']]['end_model'];s=history_summary(r['history']);n=r['nominal'];e=r['capture_elapsed'];a=r['age'];p=r['progress']
            context=make_context(r)
            predictions={'position_learned':evaluate_position(context,fm)['remaining_time'],
                'position_constant':evaluate_position(context,fm,True)['remaining_time'],
                'history_linear':max(0.,(1-p)*n*s['all_history']-a),
                'ewma_linear':max(0.,(1-p)*n*s['ewma03']-a),
                'end_learned':evaluate_end(em,r['history'],n,e+a,'learned'),
                'end_ewma_survival':evaluate_end(em,r['history'],n,e+a,'ewma03_survival')}
            predictions['observed_average']=max(0.,e*(1-p)/p-a) if p>1e-6 else predictions['end_ewma_survival']
            for mode,value in predictions.items():
                delta=abs(value-stored[r['key']]['predictions'][mode]);max_prediction=max(max_prediction,delta)
                check(delta<1e-6*max(1.,abs(value)),'OOF numerical reproduction');prediction_count+=1
        report=load('RESULTS.json')[label];rr=list(stored.values());w=weighting(rr)
        for mode,score in report.items():
            err=np.array([r['predictions'][mode]-r['actual'] for r in rr])
            for k,v in [('mse',float(w@(err*err))),('mae',float(w@abs(err))),('bias',float(w@err))]:check(abs(v-score[k])<1e-10,'aggregate score')
    runtime=PositionPredictor(model);max_runtime=0.
    for r in deliver:
        ctx=make_context(r);actual=runtime(ctx)['remaining_time'];expected=evaluate_position(ctx,model)['remaining_time']
        delta=abs(actual-expected);max_runtime=max(max_runtime,delta);check(delta<1e-6*max(1.,expected),'frozen runtime independent math')
    controls={};base=make_context(deliver[0])
    for name,edit in [
        ('stale_occurrence',lambda c:c['position'].update(occurrence_id='foreign')),
        ('not_delivered',lambda c:c['position'].update(delivered_age=c['position']['age']+1)),
        ('WAIT_not_START_age',lambda c:c.update(elapsed=c['elapsed']+2)),
        ('STAGED_wait',lambda c:c.update(status='STAGED')),
        ('private_feature',lambda c:c.update(private_disturbance='pause')),
        ('current_END_leak',lambda c:c['completed_history'].append({'vertex':c['occurrence_id'],'nominal_duration':1,'duration':4})),
        ('missing_position',lambda c:c.update(position=None)),
        ('negative_age',lambda c:c['position'].update(age=-1)),
        ('nan_progress',lambda c:c['position'].update(progress=float('nan'))),
    ]:
        ctx=deepcopy(base);edit(ctx);rejected=[]
        for fun in [runtime,lambda c:evaluate_position(c,model)]:
            try:fun(ctx);rejected.append(False)
            except ValueError:rejected.append(True)
        check(all(rejected),'negative control '+name);controls[name]='rejected'
    check(runtime({'status':'COMPLETED'})['remaining_time']==0.,'END does not read position/history')
    controls['COMPLETED_without_other_fields']='zero without reading other fields'
    for p in [0.,1.]:
        ctx=deepcopy(base);ctx['position']['progress']=p
        value=runtime(ctx)['remaining_time'];check(math.isfinite(value) and value>0,'zero or endpoint POSITION never manufactures END')
        controls['progress_'+str(p)]=value
    aged=deepcopy(base);aged['position']['age']=100.;aged['elapsed']=aged['position']['captured_elapsed']+100.
    rr=runtime(aged)['remaining_time'];ref=evaluate_position(aged,model)['remaining_time']
    check(math.isfinite(rr) and abs(rr-ref)<1e-6*max(1.,ref),'old same-occurrence survival update')
    controls['old_same_occurrence_age100']=rr
    out=dict(schema='r20-position-independent-validation-v1',passed=True,verified_utc=datetime.now(timezone.utc).isoformat(),
        checks=checks,source_worlds=len(sources),raw_queries=raw_queries,capture_rows=len(capture),delivery_rows=len(deliver),
        fits=len(cv['fits']),oof_predictions=prediction_count,max_normal_equation_residual=max_normal,
        max_feature_difference=max_feature,max_capture_progress_difference=max_capture_position,
        max_oof_prediction_difference=max_prediction,max_runtime_difference=max_runtime,
        queries_after_nonzero_dependency_wait=wait_rows,mechanical_controls=controls,
        model_sha256=sha(HERE/'MODEL.json'),predictor_sha256=sha(HERE/'position_predictor.py'),
        independent_math_sha256=sha(HERE/'independent_math.py'),verifier_sha256=sha(HERE/'verify.py'),
        trainer_imported=False,new_physical_or_solver_episodes=0,
        limits=['History cut and genuine START age require adapter receipt verification; arithmetic alone cannot authenticate caller input.',
                'Group OOF is on historically selected query locations, not randomized query interventions or calibrated probabilities.'])
    (HERE/'VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
