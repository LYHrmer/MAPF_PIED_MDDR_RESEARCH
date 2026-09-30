"""Frozen 63-episode native joint grid. No actor sees condition or private E records."""
import argparse,hashlib,json,shutil,subprocess,tempfile,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUERY=HERE.parent
ROOT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def call(cmd,timeout):
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        return dict(command=cmd,status='completed',returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,host_seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        def s(v):return v.decode() if isinstance(v,bytes) else v or ''
        return dict(command=cmd,status='timeout',returncode=None,stdout=s(e.stdout),stderr=s(e.stderr),host_seconds=time.monotonic()-start)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);a=ap.parse_args()
    out=HERE/a.attempt;out.mkdir(exist_ok=False)
    code=HERE/'joint_native_20260930_r3.cpp'
    pins=json.loads((QUERY/'legal_and_sources.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    protected=json.loads((HERE/'protected_before_20260930_r3.json').read_text())
    assert all(sha(QUERY/p)==h for p,h in protected.items())
    sup=json.loads((HERE/'support_20260930_r3.json').read_text())
    conditions=[]
    for seven in [-1,1]:
        for fortynine in [-1,1]:conditions.append(dict(name=f'first7_{seven}_first49_{fortynine}',first7=seven,first49=fortynine))
    conditions.extend([dict(name='all_eta0'),dict(name='direction_IID',seed=4409),dict(name='direction_reverse',seed=5501)])
    public=(HERE/'public_native_input_20260930_r3.txt').read_text()
    for c in conditions:
        lines=[];private=[]
        for r in sup['robots']:
            for leg,h in enumerate(r['route']):
                eta=0
                if 'first7' in c and leg==0 and r['agent'] in (7,49):eta=c['first7' if r['agent']==7 else 'first49']
                elif 'seed' in c and h!='W':
                    k=int.from_bytes(hashlib.sha256(f"{c['seed']}:{r['agent']}:{leg}".encode()).digest()[:8],'big')%10
                    preferred=-1 if h in ['NO','SO'] else 1
                    if c['name']=='direction_reverse':preferred=-preferred
                    eta=preferred if k<9 else -preferred
                private.append(dict(agent=r['agent'],leg=leg,heading=h,eta=eta))
                lines.append(f"E {r['agent']} {leg} {eta}")
        p=out/(c['name']+'.input.txt');p.write_text(public+'\n'.join(lines)+'\n');c.update(input=str(p),input_sha256=sha(p),private_world_only=private)
    files=['CONTRACT_20260930_r3.md','support_20260930_r3.json','public_training_END_20260930_r3.json',
           'public_native_input_20260930_r3.txt','joint_native_20260930_r3.cpp','prepare_20260930_r3.py','run_20260930_r3.py']
    frozen={f:sha(HERE/f) for f in files}
    shutil.copy2(code,out/'SOURCE_AT_COMPILE.cpp')
    write(out/'registration.json',dict(frozen=frozen,production_headers=pins,protected_files=len(protected),conditions=conditions,
          grid=[['WAIT',0]]+[[p,b] for p in ['RR','task_rank','global_task','task_trigger'] for b in [1,2]],
          public_source_local_R1=True,formal_external_benchmark=False,END_only_native_actor=True))
    with tempfile.TemporaryDirectory(prefix='pied-joint-r3-') as td:
        inc=Path(td)
        for p in pins:shutil.copy2(ROOT/p,inc/Path(p).name)
        lib=ROOT/'third_party/flint_host_config';sdk=ROOT/'third_party/host_sdk/usr'
        binary=out/'joint_native'
        cmd=['g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-elide-constructors',
             '-I',str(inc),'-isystem',str(sdk/'include'),'-isystem',str(lib/'src'),str(code),'-L',str(lib),
             '-L',str(sdk/'lib/x86_64-linux-gnu'),'-Wl,-rpath,'+str(lib),'-lflint','-lmpfr','-lgmp','-o',str(binary)]
        compile_result=call(cmd,120);write(out/'compile.json',compile_result)
    episodes=[]
    if compile_result['returncode']==0:
        print('compiled',sha(binary),flush=True)
        for c in conditions:
            for policy,b in [['WAIT',0]]+[[p,b] for p in ['RR','task_rank','global_task','task_trigger'] for b in [1,2]]:
                assert all(sha(HERE/p)==h for p,h in frozen.items())
                cmd=[str(binary),c['input'],policy,str(b)]
                result=call(cmd,60);raw=out/f"{c['name']}__{policy}__B{b}.jsonl"
                raw.write_text(result.pop('stdout'))
                result.update(condition=c['name'],policy=policy,capacity=b,raw=str(raw),raw_sha256=sha(raw))
                if result['returncode']==0:
                    records=[json.loads(line) for line in raw.read_text().splitlines()]
                    result['summary']=records[-1];assert result['summary']['event']=='joint_summary'
                episodes.append(result);write(out/f"{c['name']}__{policy}__B{b}.receipt.json",result)
                print(c['name'],policy,b,result['returncode'],result.get('summary',{}).get('served'),flush=True)
                if result['returncode']!=0:break
            if episodes[-1]['returncode']!=0:break
    unchanged=all(sha(QUERY/p)==h for p,h in protected.items()) and all(sha(ROOT/p)==h for p,h in pins.items())
    write(out/'receipt.json',dict(compile_returncode=compile_result['returncode'],episodes=episodes,complete_grid=len(episodes)==63,
          all_native_passed=len(episodes)==63 and all(e['returncode']==0 for e in episodes),protected_unchanged=unchanged,
          binary_sha256=sha(binary) if binary.exists() else None))
    print('receipt',out/'receipt.json',flush=True)
if __name__=='__main__':main()
