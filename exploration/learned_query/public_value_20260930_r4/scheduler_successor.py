"""Scheduling-only successor: 10 independent worlds, reuse every hash-bound success."""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import json,threading
import numpy as np
from pipeline import HERE,ROOT,PARENT,sha,write,run

def main():
    from pathlib import Path
    original=HERE/'native_attempt_01';out=HERE/'scheduled_successor_01';out.mkdir(exist_ok=False)
    reg=json.loads((original/'REGISTRATION.json').read_text());manifest=reg['worlds'];frozen=reg['frozen'];binary=original/'joint_value_native'
    require=lambda:all(sha(HERE/f)==h for f,h in frozen.items())
    assert require()
    saved={}
    for path in original.glob('*.receipt.json'):
        e=json.loads(path.read_text())
        if e['returncode']==0:
            assert sha(Path(e['raw']))==e['raw_sha256'] and sha(Path(e['input']))==e['input_sha256']
            saved[(e['world_id'],e['policy'])]=e
    write(out/'SCHEDULE_REGISTRATION.json',dict(parent_registration_sha256=sha(original/'REGISTRATION.json'),native_binary_sha256=sha(binary),
       scheduler_sha256=sha(Path(__file__)),concurrent_independent_worlds=10,reused_successful_arms=len(saved),
       original_frozen_source_unchanged=True,science_seed_model_target_unchanged=True,interruption_record_sha256=sha(HERE/'SCHEDULER_INTERRUPTION.json'),
       train_calibration_then_frozen_model_then_test=True,deterministic_label_order='worldID/source'))
    episodes=[];rows=[];lock=threading.Lock();completed=0
    def native(w,policy,model_lines=''):
        assert require()
        key=(w['world_id'],policy);path=Path(w['input']);stem=w['world_id']+'__'+policy
        if key in saved:
            e=dict(saved[key]);e['reused_successful_original']=True
            records=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
            write(out/(stem+'.reused.json'),dict(original_receipt=str(original/(stem+'.receipt.json')),raw_sha256=e['raw_sha256']))
        else:
            if model_lines:
                path=out/(w['world_id']+'.model.input.txt')
                if not path.exists():path.write_text(Path(w['input']).read_text()+model_lines)
            b=0 if policy=='WAIT' else 1;e=run([str(binary),str(path),policy,str(b)],90)
            raw=out/(stem+'.jsonl');raw.write_text(e.pop('stdout'));e.update(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],policy=policy,
               capacity=b,raw=str(raw),raw_sha256=sha(raw),input=str(path),input_sha256=sha(path),reused_successful_original=False)
            if e['returncode']==0:
                records=[json.loads(x) for x in raw.read_text().splitlines()];e['summary']=records[-1]
            write(out/(stem+'.receipt.json'),e)
            if e['returncode']!=0:raise RuntimeError('native scheduler failure '+stem+' '+e['stderr'])
        with lock:episodes.append(e)
        return e,records
    def collect(w,model_lines='',deploy=False):
        nonlocal completed
        local=[];wait,_=native(w,'WAIT',model_lines);s=wait['summary'];v=s['service_time_sum'];wf=Fraction(v['lower']+v['upper'],2*v['denominator'])+64*(4-s['served'])
        for a in w['sources']:
            e,records=native(w,'forced_'+str(a),model_lines);s=e['summary'];v=s['service_time_sum'];af=Fraction(v['lower']+v['upper'],2*v['denominator'])+64*(4-s['served'])
            decision=next(x for x in records if x['event']=='actor_decision');candidate=next(x for x in decision['candidates'] if x['agent']==a)
            local.append(dict(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],source=a,features=candidate['features'],
                target_flow_gain=str(wf-af),extra_heads=s['served']-wait['summary']['served'],chosen_policy=e['policy']))
        if deploy:
            for policy in ['RR','probability','task_rank','structural','ridge']:native(w,policy,model_lines)
        with lock:
            rows.extend(local);completed+=1
            if completed%10==0:print('PARALLEL COMPLETE WORLDS',completed,flush=True)
    def phase(worlds,model_lines='',deploy=False):
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures=[pool.submit(collect,w,model_lines,deploy) for w in worlds]
            for f in futures:f.result()
    phase([w for w in manifest if w['split']!='test'])
    rows.sort(key=lambda r:(r['world_id'],r['source']));write(out/'TRAIN_CALIBRATION_LABELS.json',rows)
    train=[r for r in rows if r['split']=='train'];assert len(train)==208
    X=np.array([[1]+[float(Fraction(z)) for z in r['features']] for r in train]);y=np.array([float(Fraction(r['target_flow_gain'])) for r in train])
    penalty=np.eye(11);penalty[0,0]=0;coef=np.linalg.solve(X.T@X+penalty,X.T@y);fraction=[Fraction(str(round(float(z),9))) for z in coef]
    model=dict(model='ridge',lambda_value=1,intercept_penalized=False,train_rows=208,train_cohorts=sorted({r['cohort_id'] for r in train}),
       used_calibration_for_fit=False,used_test_for_fit=False,train_label_sha256=sha(out/'TRAIN_CALIBRATION_LABELS.json'),train_row_bindings=[dict(world_id=r['world_id'],source=r['source']) for r in train],
       coefficients=[str(z) for z in fraction],fit_float_coefficients=coef.tolist(),rounded_rational_precision='1e-9',train_rmse=float(np.sqrt(np.mean((X@np.array([float(z) for z in fraction])-y)**2))))
    write(out/'MODEL_FROZEN_BEFORE_TEST.json',model);model_hash=sha(out/'MODEL_FROZEN_BEFORE_TEST.json');print('MODEL FROZEN',model_hash,flush=True)
    text=''.join(f'M {z.numerator} {z.denominator}\n' for z in fraction)
    phase([w for w in manifest if w['split']=='test'],text,True)
    assert sha(out/'MODEL_FROZEN_BEFORE_TEST.json')==model_hash
    rows.sort(key=lambda r:(r['world_id'],r['source']));episodes.sort(key=lambda e:(e['world_id'],e['policy']))
    write(out/'ALL_COUNTERFACTUAL_LABELS.json',rows)
    old=json.loads((PARENT/'FROZEN_MANIFEST_20260930_r3.json').read_text());pins=reg['production_headers']
    unchanged=all(sha(PARENT/p)==h['sha256'] for p,h in old['frozen_files'].items()) and all(sha(ROOT/p)==h for p,h in pins.items())
    write(out/'RECEIPT.json',dict(complete=True,episodes=episodes,model_sha256=model_hash,binary_sha256=sha(binary),all_native_passed=True,total_native_episodes=len(episodes),
       reused_successful_original=sum(e['reused_successful_original'] for e in episodes),new_native_episodes=sum(not e['reused_successful_original'] for e in episodes),
       training_counterfactual_worlds=104,calibration_counterfactual_worlds=26,test_worlds=26,R3_and_production_unchanged=unchanged,science_unchanged_scheduler_only=True))
    print('COMPLETE',len(episodes),'native arms',flush=True)
if __name__=='__main__':main()
