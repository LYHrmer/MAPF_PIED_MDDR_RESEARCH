import hashlib,json,shutil,subprocess,tempfile,time
from fractions import Fraction
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH');PARENT=HERE.parent/'public_joint_20260930_r3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
def run(cmd,timeout):
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        return dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        def txt(x):return x.decode() if isinstance(x,bytes) else x or ''
        return dict(command=cmd,returncode=None,stdout=txt(e.stdout),stderr=txt(e.stderr),seconds=time.monotonic()-start,timeout=True)
def main():
    out=HERE/'native_attempt_01';out.mkdir(exist_ok=False)
    sup=json.loads((HERE/'SUPPORT_AUDIT_60.json').read_text());pins=json.loads((HERE.parent/'legal_and_sources.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    old=json.loads((PARENT/'FROZEN_MANIFEST_20260930_r3.json').read_text());assert all(sha(PARENT/p)==h['sha256'] for p,h in old['frozen_files'].items())
    history=(PARENT/'public_native_input_20260930_r3.txt').read_text().splitlines();history=[line for line in history if line.startswith('H ')]
    manifest=[]
    for c in sup['cohorts']:
        cid=c['cohort_id'];sources=sorted({x[0] for x in c['initial_follow_pairs']});assert len(sources)==2
        seeds=range({'train':1001,'calibration':2001,'test':3001}[c['split']],{'train':1009,'calibration':2009,'test':3009}[c['split']])
        cases=[dict(name=f'IID_{seed}',seed=seed) for seed in seeds]+[dict(name='eta0')]
        cases.extend(dict(name=f'corner_{x}_{y}',corner=[x,y]) for x in [-1,1] for y in [-1,1])
        public=[f'C {x} {y}' for x,y in c['resource_cells']]
        for r in c['robots']:public.append(' '.join(map(str,['R',r['agent'],r['task'],*r['start'],*r['goal'],','.join(r['route'])])))
        public.extend(history)
        for k in cases:
            private=[]
            for r in c['robots']:
                for leg,h in enumerate(r['route']):
                    eta=0
                    if 'corner' in k and leg==0 and r['agent'] in sources:eta=k['corner'][sources.index(r['agent'])]
                    elif 'seed' in k and h!='W':
                        word=hashlib.sha256(f"{k['seed']}:{cid}:{r['agent']}:{leg}".encode()).digest()[:8];v=int.from_bytes(word,'big')%10
                        preferred=-1 if h in ['NO','SO'] else 1;eta=preferred if v<9 else -preferred
                    private.append(dict(agent=r['agent'],leg=leg,heading=h,eta=eta))
            wid=cid+'__'+k['name'];p=out/(wid+'.input.txt');p.write_text('\n'.join(public+[f"E {x['agent']} {x['leg']} {x['eta']}" for x in private])+'\n')
            manifest.append(dict(world_id=wid,cohort_id=cid,split=c['split'],case=k,input=str(p),input_sha256=sha(p),private_world_only=private,sources=sources))
    frozen={p.name:sha(p) for p in [HERE/'CONTRACT.md',HERE/'SOURCE_REGISTRATION_20260930_r4.json',HERE/'SUPPORT_AUDIT_60.json',HERE/'prepare.py',HERE/'pipeline.py',HERE/'joint_value_native.cpp']}
    write(out/'REGISTRATION.json',dict(frozen=frozen,worlds=manifest,production_headers=pins,R3_manifest_sha256=sha(PARENT/'FROZEN_MANIFEST_20260930_r3.json'),
           model='ridge lambda1 intercept unpenalized fixed10features train-only rational1e-9',heldout_cohorts=[c['cohort_id'] for c in sup['cohorts'] if c['split']=='test']))
    shutil.copy2(HERE/'joint_value_native.cpp',out/'SOURCE_AT_COMPILE.cpp')
    with tempfile.TemporaryDirectory(prefix='pied-value-r4-') as td:
        inc=Path(td)
        for p in pins:shutil.copy2(ROOT/p,inc/Path(p).name)
        lib=ROOT/'third_party/flint_host_config';sdk=ROOT/'third_party/host_sdk/usr';binary=out/'joint_value_native'
        cmd=['g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-elide-constructors','-I',str(inc),
             '-isystem',str(sdk/'include'),'-isystem',str(lib/'src'),str(HERE/'joint_value_native.cpp'),'-L',str(lib),'-L',str(sdk/'lib/x86_64-linux-gnu'),
             '-Wl,-rpath,'+str(lib),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
        compiled=run(cmd,120);write(out/'COMPILE.json',compiled)
    if compiled['returncode']!=0:print('COMPILE FAILED',compiled['stderr'],flush=True);return
    print('COMPILED',sha(binary),flush=True)
    episodes=[];rows=[];completed=0
    def native(w,policy,model_lines=''):
        assert all(sha(HERE/f)==h for f,h in frozen.items())
        path=Path(w['input'])
        if model_lines:
            path=out/(w['world_id']+'.model.input.txt')
            if not path.exists():path.write_text(Path(w['input']).read_text()+model_lines)
        b=0 if policy=='WAIT' else 1
        e=run([str(binary),str(path),policy,str(b)],90)
        stem=w['world_id']+'__'+policy;raw=out/(stem+'.jsonl');raw.write_text(e.pop('stdout'))
        e.update(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],policy=policy,capacity=b,raw=str(raw),raw_sha256=sha(raw),input=str(path),input_sha256=sha(path))
        if e['returncode']==0:
            records=[json.loads(x) for x in raw.read_text().splitlines()];e['summary']=records[-1];assert e['summary']['event']=='joint_summary'
        write(out/(stem+'.receipt.json'),e);episodes.append(e)
        if e['returncode']!=0:
            write(out/'FAILED_RECEIPT.json',dict(episodes=episodes,error=e));raise RuntimeError('native failure '+stem+' '+e['stderr'])
        return e,records
    def collect(w,model_lines=''):
        nonlocal completed
        wait,_=native(w,'WAIT',model_lines);s=wait['summary'];v=s['service_time_sum'];wf=Fraction(v['lower']+v['upper'],2*v['denominator'])+64*(4-s['served'])
        for a in w['sources']:
            e,records=native(w,'forced_'+str(a),model_lines);s=e['summary'];v=s['service_time_sum'];af=Fraction(v['lower']+v['upper'],2*v['denominator'])+64*(4-s['served'])
            decision=next(x for x in records if x['event']=='actor_decision');candidate=next(x for x in decision['candidates'] if x['agent']==a)
            rows.append(dict(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],source=a,features=candidate['features'],
              target_flow_gain=str(wf-af),extra_heads=s['served']-wait['summary']['served'],chosen_policy=e['policy']))
        completed+=1
        if completed%10==0:print('COUNTERFACTUAL WORLDS',completed,flush=True)
    for w in manifest:
        if w['split']!='test':collect(w)
    write(out/'TRAIN_CALIBRATION_LABELS.json',rows)
    train=[r for r in rows if r['split']=='train'];assert len(train)==8*13*2
    X=np.array([[1]+[float(Fraction(z)) for z in r['features']] for r in train]);y=np.array([float(Fraction(r['target_flow_gain'])) for r in train])
    penalty=np.eye(11);penalty[0,0]=0;coef=np.linalg.solve(X.T@X+penalty,X.T@y)
    fractions=[Fraction(str(round(float(x),9))) for x in coef]
    model=dict(model='ridge',lambda_value=1,intercept_penalized=False,train_rows=len(train),train_cohorts=sorted({r['cohort_id'] for r in train}),
      used_calibration_for_fit=False,used_test_for_fit=False,train_label_sha256=sha(out/'TRAIN_CALIBRATION_LABELS.json'),
      train_row_bindings=[dict(world_id=r['world_id'],source=r['source']) for r in train],coefficients=[str(x) for x in fractions],
      fit_float_coefficients=coef.tolist(),rounded_rational_precision='1e-9',train_rmse=float(np.sqrt(np.mean((X@np.array([float(x) for x in fractions])-y)**2))))
    write(out/'MODEL_FROZEN_BEFORE_TEST.json',model);model_hash=sha(out/'MODEL_FROZEN_BEFORE_TEST.json')
    print('MODEL FROZEN',model_hash,'train rows',len(train),flush=True)
    model_lines=''.join(f'M {x.numerator} {x.denominator}\n' for x in fractions)
    for w in manifest:
        if w['split']=='test':
            assert sha(out/'MODEL_FROZEN_BEFORE_TEST.json')==model_hash
            collect(w,model_lines)
            # WAIT is actual native collection above, no second duplicate baseline.
            for policy in ['RR','probability','task_rank','structural','ridge']:native(w,policy,model_lines)
    write(out/'ALL_COUNTERFACTUAL_LABELS.json',rows)
    old_unchanged=all(sha(PARENT/p)==h['sha256'] for p,h in old['frozen_files'].items()) and all(sha(ROOT/p)==h for p,h in pins.items())
    write(out/'RECEIPT.json',dict(complete=True,episodes=episodes,model_sha256=model_hash,binary_sha256=sha(binary),all_native_passed=True,
          training_counterfactual_worlds=8*13,calibration_counterfactual_worlds=2*13,test_worlds=2*13,total_native_episodes=len(episodes),
          R3_and_production_unchanged=old_unchanged))
    print('COMPLETE',len(episodes),'native episodes',flush=True)
if __name__=='__main__':main()
