"""Run unchanged published author modules on frozen paired per-agent task files."""
from datetime import datetime, timezone
import hashlib, importlib.util, json, random, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW = MAIN / 'paired_published_guidance_20260930_r5'
R4 = HERE.parent / 'published_guidance_comparison_20260930_r4'
R3 = HERE.parent / 'onlineggo_training_20260930_r3'
OLD = MAIN / 'onlineggo_training_20260930_r3_attempt02'
SEEDS = [930101, 930103, 930107]
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, x):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, allow_nan=False) + '\n')
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    spec.loader.exec_module(mod); return mod

def main():
    assert not RAW.exists() and not (HERE/'freeze.json').exists(), 'Never overwrite attempts'
    RAW.mkdir(); inp = RAW/'inputs'; inp.mkdir()
    oldhelper = load('r5_frozen_r4_source_audit', R4/'run.py')
    source = oldhelper.source_audit()
    hjob = read(MAIN/'published_guidance_comparison_20260930_r4/hm_seed_930101/job.json')
    map_path = Path(hjob['kwargs']['map_path']); lines = map_path.read_text().splitlines()
    grid = lines[4:]; height, width = len(grid), len(grid[0])
    groups = {c:[i*width+j for i,row in enumerate(grid) for j,v in enumerate(row) if v==c] for c in 'WE'}
    assert groups['W'] and groups['E']
    minimum = min(abs(w//width-e//width)+abs(w%width-e%width) for w in groups['W'] for e in groups['E'])
    assert minimum > 0
    task_count = 1000//minimum + 2
    mapped = [''.join('.' if c in 'WE' else c for c in row) for row in grid]
    assert all((a in '@T')==(b in '@T') for ra,rb in zip(grid,mapped) for a,b in zip(ra,rb))
    derived = inp/'sortation_small_fixed.map'
    derived.write_text('\n'.join(lines[:4]+mapped)+'\n')
    manifests = []
    for seed in SEEDS:
        oldtrace = read(MAIN/f'published_guidance_comparison_20260930_r4/hm_seed_{seed}/trace.json')
        starts = [row*width+col for row,col,*_ in oldtrace['start']]
        goals = {t[0]:t[1]*width+t[2] for t in oldtrace['tasks']}
        streams = []
        for agent, events in enumerate(oldtrace['events']):
            first = goals[next(t for t,_,kind in events if kind=='assigned')]
            rng = random.Random(f'paired-r5:{seed}:{agent}')
            seq = [first]
            while len(seq) < task_count:
                prev = grid[seq[-1]//width][seq[-1]%width]
                seq.append(rng.choice(groups['E' if prev=='W' else 'W']))
            streams.append(seq)
        assert len(set(starts)) == 800
        agentfile = inp/f'starts_{seed}.agents'; taskfile = inp/f'tasks_{seed}.tasks'
        agentfile.write_text('800\n'+'\n'.join(map(str,starts))+'\n')
        flat = [streams[a][i] for i in range(task_count) for a in range(800)]
        taskfile.write_text(str(len(flat))+'\n'+'\n'.join(map(str,flat))+'\n')
        config = inp/f'instance_{seed}.json'
        write(config, {'mapFile':derived.name, 'teamSize':800, 'agentFile':agentfile.name,
                       'taskFile':taskfile.name, 'taskAssignmentStrategy':'roundrobin_fixed', 'numTasksReveal':1})
        manifests.append({'seed':seed, 'config':str(config), 'old_trace_sha256':sha(MAIN/f'published_guidance_comparison_20260930_r4/hm_seed_{seed}/trace.json'),
                          'tasks_per_agent':task_count, 'input_hashes':{p.name:sha(p) for p in [config,agentfile,taskfile]}})
    prior = read(R3/'training_02/holdout.json'); checkpoint = read(R3/'training_02/trained_checkpoint.json')
    jobs = []
    for item in manifests:
        seed = item['seed']
        for policy in ['hm_GPIBT','trained']:
            if policy=='hm_GPIBT':
                job = read(MAIN/f'published_guidance_comparison_20260930_r4/hm_seed_{seed}/job.json')
            else:
                previous = next(r for r in prior if r['policy']=='trained' and r['seed']==seed)
                job = read(OLD/previous['raw_label']/'job.json')
                assert json.loads(job['kwargs']['network_params']) == checkpoint['parameters']
            label = f'{policy}_{seed}'; work = RAW/label; work.mkdir()
            job['label'] = label; job['map_sha256'] = sha(derived)
            job['kwargs'].update(gen_tasks=False, all_json_path=item['config'], map_path=str(derived),
                                 task_assignment_strategy='roundrobin_fixed', num_tasks_reveal=1,
                                 num_tasks=800*task_count, save_path=str(work/'trace.json'))
            assert sha(job['module_path']) == job['module_sha256']
            write(work/'job.json',job); jobs.append((label, policy, seed, work))
    pins = {str(p):sha(p) for p in [HERE/'PROTOCOL.md',Path(__file__),HERE/'verify.py',R3/'native_worker.py',R3/'training_02/trained_checkpoint.json',map_path,derived]}
    for p in inp.iterdir(): pins[str(p)]=sha(p)
    for _,_,_,work in jobs: pins[str(work/'job.json')]=sha(work/'job.json')
    write(HERE/'freeze.json', {'utc':datetime.now(timezone.utc).isoformat(), 'pins':pins, 'source_before':source,
                              'seeds':SEEDS, 'workloads':manifests, 'minimum_WE_Manhattan':minimum,
                              'tasks_per_agent':task_count, 'native_modules':{label:read(work/'job.json')['module_sha256'] for label,_,_,work in jobs}})
    results = []
    for label,policy,seed,work in jobs:
        argv = ['rtk','proxy','timeout','--kill-after=5s','120s',sys.executable,str(R3/'native_worker.py'),str(work/'job.json')]
        start=time.monotonic()
        with (work/'stdout.log').open('w') as out, (work/'stderr.log').open('w') as err:
            try:
                proc=subprocess.run(argv,cwd=work,stdout=out,stderr=err,timeout=130)
                code=proc.returncode; timed_out=False
            except subprocess.TimeoutExpired: code=None; timed_out=True
        receipt={'argv':argv,'cwd':str(work),'returncode':code,'timed_out':timed_out,'elapsed_seconds':time.monotonic()-start,
                 'job_sha256':sha(work/'job.json'),'stdout_sha256':sha(work/'stdout.log'),'stderr_sha256':sha(work/'stderr.log')}
        write(work/'receipt.json',receipt)
        row={'label':label,'seed':seed,'policy':policy,**receipt}
        if code==0:
            row['throughput']=read(work/'job.result.json')['result']['throughput']
            row['trace_sha256']=sha(work/'trace.json'); row['result_sha256']=sha(work/'job.result.json')
        results.append(row); write(HERE/'results.json',results)
        print(json.dumps({k:row.get(k) for k in ['label','returncode','throughput','elapsed_seconds']}),flush=True)
    assert all(r['returncode']==0 and not r['timed_out'] for r in results), 'Native failures retained'
    assert oldhelper.source_audit()==source
    for p,digest in pins.items(): assert sha(p)==digest,p
    verifier=load('paired_r5_verifier',HERE/'verify.py')
    verifier.main()
if __name__=='__main__': main()
