"""Build and run the unchanged published SUM_OVC baseline; no optimizer."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
R3=HERE.parent/'onlineggo_training_20260930_r3'
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/'published_guidance_comparison_20260930_r4'
UP=MAIN/'baseline_selection_20260929/OnlineGGO'
OLD=MAIN/'onlineggo_training_20260930_r3_attempt02'
SEEDS=[930101,930103,930107]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module
def source_audit():
    tree=subprocess.check_output(['rtk','proxy','git','-C',str(UP),'ls-tree','-rz','HEAD'])
    count=0;links={}
    for row in tree.split(b'\0'):
        if not row:continue
        info,name=row.split(b'\t',1);mode,kind,digest=info.split()
        if kind==b'commit':links[name.decode()]=digest.decode();continue
        p=UP/name.decode();data=os.readlink(p).encode() if mode==b'120000' else p.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==digest.decode()
        count+=1
    return {'unchanged_tracked_blobs':count,'gitlink_references':links,'gitlink_contents_reaudited':False}
def command(label,argv,cwd,limit=120):
    d=RAW/label;d.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    with (d/'stdout.log').open('w') as out,(d/'stderr.log').open('w') as err:
        try:
            result=subprocess.run(argv,cwd=cwd,stdout=out,stderr=err,timeout=limit+10)
            code=result.returncode;timeout=False
        except subprocess.TimeoutExpired:code=None;timeout=True
    rec={'argv':argv,'cwd':str(cwd),'returncode':code,'timed_out':timeout,
         'elapsed_seconds':time.monotonic()-start,'finished_utc':datetime.now(timezone.utc).isoformat(),
         'stdout_sha256':sha(d/'stdout.log'),'stderr_sha256':sha(d/'stderr.log')}
    write(d/'receipt.json',rec)
    assert code==0 and not timeout, str(d)
    return rec
def main():
    assert not RAW.exists(),'Never overwrite or silently rerun an attempt'
    before=source_audit()
    prior=read(R3/'training_02/holdout.json')
    pins={str(p):sha(p) for p in [HERE/'PROTOCOL.md',Path(__file__),R3/'native_worker.py',R3/'audit.py',R3/'training_02/trained_checkpoint.json',R3/'training_02/freeze.json',R3/'training_02/holdout.json']}
    for row in prior:
        for name in ['job.json','job.result.json','receipt.json','trace.json']:
            p=OLD/row['raw_label']/name;pins[str(p)]=sha(p)
    write(HERE/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'holdout_seeds':SEEDS,'pins':pins,'source_before':before,'objective':3,'new_training':False})
    build=RAW/'build_hm'
    argv=read(MAIN/'onlineggo_neural_r0_20260930_r2/configure_01/receipt.json')['argv']
    argv[argv.index('-B')+1]=str(build)
    argv[argv.index('-DOBJECTIVE=4')]='-DOBJECTIVE=3'
    configure=command('configure',argv,UP)
    compiled=command('build',['rtk','proxy','timeout','--kill-after=5s','120s','cmake','--build',str(build),'--target','py_driver','-j','4'],UP)
    module=next(build.glob('py_driver*.so'))
    flags=next(build.glob('CMakeFiles/py_driver.dir/flags.make')).read_text()
    assert '-DOBJECTIVE=3' in flags and '-DFOCAL_SEARCH' not in flags and '-DGUIDANCE_LNS' not in flags
    write(HERE/'build.json',{'configure':configure,'build':compiled,'module_sha256':sha(module),'flags':flags})
    rows=[]
    for seed in SEEDS:
        previous=next(r for r in prior if r['seed']==seed and r['policy']=='initial')
        job=read(OLD/previous['raw_label']/'job.json')
        label=f'hm_seed_{seed}';d=RAW/label;d.mkdir()
        job.update(label=label,module_path=str(module),module_sha256=sha(module))
        job['kwargs']['save_path']=str(d/'trace.json')
        write(d/'job.json',job)
        rec=command(label+'_process',['rtk','proxy','timeout','--kill-after=5s','120s',sys.executable,str(R3/'native_worker.py'),str(d/'job.json')],d)
        result=read(d/'job.result.json')
        rows.append({'seed':seed,'policy':'hm_GPIBT','raw_label':label,'throughput':result['result']['throughput'],'job_sha256':sha(d/'job.json'),'result_sha256':sha(d/'job.result.json'),'process_receipt':rec})
        write(HERE/'results.json',rows)
        print(json.dumps({'seed':seed,'policy':'hm_GPIBT','throughput':result['result']['throughput']}),flush=True)
    audit=load('r4_frozen_r3_trace_audit',R3/'audit.py')
    traces={r['raw_label']:audit.trace_check(RAW/r['raw_label']/'trace.json',RAW/r['raw_label']/'job.json',RAW/r['raw_label']/'job.result.json') for r in rows}
    agreement=[]
    for r in rows:
        hm=read(RAW/r['raw_label']/'trace.json')
        for policy in ['initial','trained']:
            old=next(x for x in prior if x['seed']==r['seed'] and x['policy']==policy)
            other=read(OLD/old['raw_label']/'trace.json')
            def streams(x):
                goals={t[0]:t[1:3] for t in x['tasks']}
                return [[goals[t] for t,_,kind in ev if kind=='assigned'] for ev in x['events']]
            a,b=streams(hm),streams(other)
            agreement.append({'seed':r['seed'],'comparator':policy,'same_starts':hm['start']==other['start'],'same_initial_task_goals':all(x[0]==y[0] for x,y in zip(a,b)),'agents_with_different_full_task_streams':sum(x!=y for x,y in zip(a,b))})
    for p,digest in pins.items():assert sha(p)==digest,p
    after=source_audit();assert after==before
    means={p:sum(r['throughput'] for r in prior+rows if r['policy']==p)/3 for p in ['initial','trained','hm_GPIBT']}
    write(HERE/'audit.json',{'passed':True,'source_after':after,'new_full_trajectory_audits':traces,'task_stream_agreement':agreement,'frozen_input_hashes_unchanged':True})
    write(HERE/'summary.json',{'means':means,'trained_relative_to_hm_percent':100*(means['trained']/means['hm_GPIBT']-1),'formal_comparator':'hm+GPIBT, unchanged OnlineGGO authors implementation','seeds':SEEDS,'full_author_benchmark':False,'same_per_agent_exogenous_task_stream':False,'execution_error_test':False})
    print(json.dumps(read(HERE/'summary.json')),flush=True)
if __name__=='__main__':main()
