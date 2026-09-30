"""Independent saved-training and full held-out trajectory audit; no native runs."""
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/'onlineggo_training_20260930_r3_attempt02'
UPSTREAM=MAIN/'baseline_selection_20260929/OnlineGGO'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def trace_check(trace_path,job_path,result_path):
    x=read(trace_path);job=read(job_path);result=read(result_path)['result']
    assert x['AllValid']=='Yes' and not x['errors'] and x['teamSize']==800 and x['makespan']==1000
    grid=Path(job['kwargs']['map_path']).read_text().splitlines()[4:]
    starts=[tuple(s[:2]) for s in x['start']]
    paths=[];deltas={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1),'W':(0,0)}
    for start,text in zip(starts,x['actualPaths']):
        pos=start;path=[pos];actions=text.split(',')
        assert len(actions)==1000
        for a in actions:
            dr,dc=deltas[a];pos=(pos[0]+dr,pos[1]+dc)
            assert 0<=pos[0]<len(grid) and 0<=pos[1]<len(grid[0]) and grid[pos[0]][pos[1]] not in '@T'
            path.append(pos)
        paths.append(path)
    for tick in range(1001):
        now={p[tick]:i for i,p in enumerate(paths)};assert len(now)==800
        if tick:
            before={p[tick-1]:i for i,p in enumerate(paths)}
            for i,p in enumerate(paths):
                j=before.get(p[tick])
                assert j is None or j==i or paths[j][tick]!=p[tick-1]
    goals={t[0]:tuple(t[1:3]) for t in x['tasks']};assert len(goals)==len(x['tasks'])
    assigned=set();finished=set();pending=0
    for agent,evs in enumerate(x['events']):
        q=deque();last=-1
        for tid,tick,kind in evs:
            assert last<=tick<=1000;last=tick
            if kind=='assigned':
                assert tid not in assigned and tid in goals;assigned.add(tid);q.append(tid)
            elif kind=='finished':
                assert q and q.popleft()==tid and tid not in finished
                assert paths[agent][tick]==goals[tid];finished.add(tid)
            else:raise AssertionError(kind)
        pending+=len(q)
    assert len(finished)==x['numTaskFinished'] and pending==800
    assert abs(result['throughput']-len(finished)/1000)<1e-12
    return {'actions_replayed':800000,'joint_positions':800800,'finished_tasks':len(finished),
            'pending_tasks':pending,'throughput':result['throughput'],'trace_sha256':sha(trace_path)}

def main():
    t=HERE/'training_02';freeze=read(t/'freeze.json')
    assert sha(HERE/'TRAINING_PROTOCOL.md')==freeze['protocol_sha256']
    for path,digest in freeze['code_sha256'].items():assert sha(HERE/path)==digest
    for path,digest in freeze['official_sources'].items():assert sha(UPSTREAM/'CMAES'/path)==digest
    tree=subprocess.check_output(['rtk','proxy','git','-C',str(UPSTREAM),'ls-tree','-rz','HEAD'])
    tracked=0;gitlinks={}
    for row in tree.split(b'\0'):
        if not row:continue
        info,name=row.split(b'\t',1);mode,kind,digest=info.split()
        if mode==b'160000' and kind==b'commit':
            gitlinks[name.decode()]=digest.decode()
            continue
        assert kind==b'blob'
        path=UPSTREAM/name.decode()
        data=os.readlink(path).encode() if mode==b'120000' else path.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==digest.decode()
        tracked+=1
    all_seeds=[];all_candidates=[];values=[];native_count=0
    for g in range(2):
        c=read(t/f'generation_{g}_candidates.json');r=read(t/f'generation_{g}_results.json')
        assert len(c['solutions'])==len(c['seeds'])==len(r)==100
        for i,(weights,seeds,rec) in enumerate(zip(c['solutions'],c['seeds'],r)):
            assert len(weights)==560 and rec['candidate']==i
            replicas=[]
            for k,seed in enumerate(seeds):
                label=f'g{g}_c{i:03d}_r{k}';p=RAW/label
                receipt=read(p/'receipt.json');job=read(p/'job.json');result=read(p/'job.result.json')
                assert receipt['returncode']==0 and not receipt['timed_out']
                assert job['kwargs']['seed']==seed and json.loads(job['kwargs']['network_params'])==weights
                assert job['kwargs']['num_agents']==800 and job['kwargs']['simu_time']==1000
                assert sha(p/'job.json')==rec['replicas'][k]['job_sha256']==receipt['job_sha256']
                assert sha(p/'job.result.json')==rec['replicas'][k]['result_sha256']==receipt['result_sha256']
                assert job['module_sha256']==freeze['module_sha256'] and job['map_sha256']==freeze['map_sha256']
                throughput=result['result']['throughput']
                assert throughput==rec['replicas'][k]['throughput']==receipt['result']['throughput']
                replicas.append(throughput);all_seeds.append(seed);native_count+=1
            mean=sum(replicas)/2;assert abs(rec['objective']-mean)<1e-12
            all_candidates.append(weights);values.append(mean)
    selected=read(t/'trained_checkpoint.json');best=max(values)
    assert selected['trained'] and not selected['full_author_R0'] and selected['selected_training_objective']==best
    assert any(w==selected['parameters'] and v==best for w,v in zip(all_candidates,values))
    holdout=read(t/'holdout.json');assert len(holdout)==6
    assert not set(all_seeds).intersection(freeze['holdout_seeds'])
    full_traces={}
    for row in holdout:
        label=row['raw_label'];p=RAW/label;job=read(p/'job.json')
        assert row['seed'] in freeze['holdout_seeds'] and job['kwargs']['seed']==row['seed']
        expected=selected['parameters'] if row['policy']=='trained' else [5.]*560
        assert json.loads(job['kwargs']['network_params'])==expected
        assert sha(p/'job.json')==row['job_sha256'] and sha(p/'job.result.json')==row['result_sha256']
        full_traces[label]=trace_check(p/'trace.json',p/'job.json',p/'job.result.json')
        assert full_traces[label]['throughput']==row['throughput']
    means={label:sum(r['throughput'] for r in holdout if r['policy']==label)/3 for label in ['initial','trained']}
    summary=read(t/'summary.json')
    assert all(abs(summary['holdout_means'][label]-mean)<1e-12 for label,mean in means.items())
    assert summary['trained_checkpoint_sha256']==sha(t/'trained_checkpoint.json')
    out={'passed':True,'unchanged_official_tracked_blobs':tracked,'upstream_gitlink_references':gitlinks,
         'gitlink_contents_reaudited':False,'native_training_runs':native_count,
         'selected_training_objective':best,'holdout_means':means,'heldout_trajectory_audits':full_traces,
         'training_trajectory_full_replay':False,'full_author_R0':False,'new_method_tested':False,
         'verifier_sha256':sha(Path(__file__))}
    output=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'audit.json'
    assert not output.exists();output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='heldout_trajectory_audits'}))

if __name__=='__main__':main()
