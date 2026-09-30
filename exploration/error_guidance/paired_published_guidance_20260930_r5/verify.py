"""Independent full trace and predetermined FIFO task audit; no native executions."""
from collections import Counter, deque
import hashlib, importlib.util, json, random, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
RAW=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/paired_published_guidance_20260930_r5')
MAIN=RAW.parent
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p); mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod; spec.loader.exec_module(mod); return mod

def inputs_check(freeze):
    first_job=read(RAW/'hm_GPIBT_930101/job.json')
    grid=Path(first_job['kwargs']['map_path']).read_text().splitlines()[4:]
    original=read(MAIN/'published_guidance_comparison_20260930_r4/hm_seed_930101/job.json')
    original_grid=Path(original['kwargs']['map_path']).read_text().splitlines()[4:]
    assert len(grid)==len(original_grid)==33 and all(len(r)==57 for r in grid)
    assert all((a in '@T')==(b in '@T') for ra,rb in zip(grid,original_grid) for a,b in zip(ra,rb))
    assert not any(c in 'WE' for row in grid for c in row)
    groups={c:[i*57+j for i,row in enumerate(original_grid) for j,v in enumerate(row) if v==c] for c in 'WE'}
    distance=min(abs(a//57-b//57)+abs(a%57-b%57) for a in groups['W'] for b in groups['E'])
    assert distance==freeze['minimum_WE_Manhattan'] and freeze['tasks_per_agent']==1000//distance+2
    data={}
    for item in freeze['workloads']:
        seed=item['seed']; config_path=Path(item['config']); config=read(config_path)
        assert config['teamSize']==800 and config['numTasksReveal']==1 and config['taskAssignmentStrategy']=='roundrobin_fixed'
        starts=[int(x) for x in (config_path.parent/config['agentFile']).read_text().splitlines()]
        flat=[int(x) for x in (config_path.parent/config['taskFile']).read_text().splitlines()]
        assert starts.pop(0)==800 and len(starts)==800 and len(set(starts))==800
        assert flat.pop(0)==800*freeze['tasks_per_agent'] and len(flat)==800*freeze['tasks_per_agent']
        streams=[flat[a::800] for a in range(800)]
        previous=read(MAIN/f'published_guidance_comparison_20260930_r4/hm_seed_{seed}/trace.json')
        assert starts==[r*57+c for r,c,*_ in previous['start']]
        previous_goals={t[0]:57*t[1]+t[2] for t in previous['tasks']}
        for a,seq in enumerate(streams):
            assert seq[0]==previous_goals[next(t for t,_,k in previous['events'][a] if k=='assigned')]
            rng=random.Random(f'paired-r5:{seed}:{a}')
            for prev,nxt in zip(seq,seq[1:]):
                category='E' if original_grid[prev//57][prev%57]=='W' else 'W'
                assert nxt==rng.choice(groups[category])
                assert original_grid[nxt//57][nxt%57]==category
            assert all(grid[t//57][t%57] not in '@T' for t in seq)
        data[seed]=(starts,streams,grid)
    return data

def trace_check(row, data, task_count):
    d=RAW/row['label']; job=read(d/'job.json'); receipt=read(d/'receipt.json')
    assert row['returncode']==receipt['returncode']==0 and not receipt['timed_out']
    assert sha(d/'job.json')==receipt['job_sha256'] and sha(d/'trace.json')==row['trace_sha256']
    assert sha(d/'job.result.json')==row['result_sha256'] and sha(job['module_path'])==job['module_sha256']
    assert job['kwargs']['gen_tasks'] is False and job['kwargs']['num_tasks_reveal']==1
    x=read(d/'trace.json'); result=read(d/'job.result.json')['result']
    assert x['AllValid']=='Yes' and not x['errors'] and x['teamSize']==800 and x['makespan']==1000
    starts,streams,grid=data[row['seed']]
    assert [r*57+c for r,c,*_ in x['start']]==starts
    delta={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1),'W':(0,0)}
    paths=[]
    for start,raw in zip(x['start'],x['actualPaths']):
        pos=tuple(start[:2]); path=[pos]; actions=raw.split(','); assert len(actions)==1000
        for action in actions:
            dr,dc=delta[action]; pos=(pos[0]+dr,pos[1]+dc)
            assert 0<=pos[0]<33 and 0<=pos[1]<57 and grid[pos[0]][pos[1]] not in '@T'
            path.append(pos)
        paths.append(path)
    for tick in range(1001):
        now={p[tick]:a for a,p in enumerate(paths)}; assert len(now)==800
        if tick:
            old={p[tick-1]:a for a,p in enumerate(paths)}
            for a,path in enumerate(paths):
                other=old.get(path[tick]); assert other is None or other==a or paths[other][tick]!=path[tick-1]
    definitions={}; counts=Counter()
    for tid,r,c in x['tasks']:
        goal=57*r+c; agent,index=divmod(tid,task_count)
        assert 0<=agent<800 and goal==streams[agent][index]
        assert tid not in definitions or definitions[tid]==goal
        definitions[tid]=goal; counts[tid]+=1
    assert len(definitions)==800*task_count and set(counts.values())<={1,2}
    assigned=set(); finished=set(); prefix_lengths=[]; min_unrevealed=task_count
    for agent,events in enumerate(x['events']):
        queue=deque(); last=-1; index=0; completed=0
        for tid,tick,kind in events:
            assert last<=tick<=1000; last=tick
            if kind=='assigned':
                assert not queue and tid not in assigned and tid==agent*task_count+index
                assert definitions[tid]==streams[agent][index]
                assigned.add(tid); queue.append(tid); index+=1
            elif kind=='finished':
                assert queue and queue.popleft()==tid and tid not in finished
                assert paths[agent][tick]==divmod(definitions[tid],57)
                finished.add(tid); completed+=1
            else: raise AssertionError(kind)
        assert len(queue)==1 and index==completed+1
        min_unrevealed=min(min_unrevealed,task_count-index); prefix_lengths.append(index)
    assert min_unrevealed>0 and {tid for tid,count in counts.items() if count==2}==assigned
    assert len(finished)==x['numTaskFinished'] and len(assigned)==len(finished)+800
    assert result['throughput']==row['throughput']==len(finished)/1000
    return {'actions_replayed':800000,'joint_positions':800800,'finished_tasks':len(finished),
            'pending_tasks':800,'min_unrevealed_tasks_per_agent':min_unrevealed,
            'duplicate_definitions_matching_reveals':len(assigned),
            'assignment_prefix_lengths':prefix_lengths,'throughput':row['throughput'],
            'trace_sha256':sha(d/'trace.json')}

def main():
    freeze=read(HERE/'freeze.json')
    for p,digest in freeze['pins'].items(): assert sha(p)==digest,p
    data=inputs_check(freeze); rows=read(HERE/'results.json')
    assert len(rows)==6 and {(r['seed'],r['policy']) for r in rows}=={(s,p) for s in freeze['seeds'] for p in ['hm_GPIBT','trained']}
    audits={r['label']:trace_check(r,data,freeze['tasks_per_agent']) for r in rows}
    paired=[]
    for seed in freeze['seeds']:
        a,b=[next(r for r in rows if r['seed']==seed and r['policy']==p) for p in ['hm_GPIBT','trained']]
        ja,jb=[read(RAW/r['label']/'job.json') for r in [a,b]]
        ka,kb=ja['kwargs'].copy(),jb['kwargs'].copy()
        for kw in [ka,kb]:
            kw.pop('network_params'); kw.pop('save_path')
        assert ka==kb
        paired.append({'seed':seed,'hm_GPIBT':a['throughput'],'trained':b['throughput'],
                       'trained_minus_hm':b['throughput']-a['throughput'],
                       'identical_complete_future_task_input':True,'prefix_agreement_agents':800})
    helper=load('r5_source_audit_final',HERE.parent/'published_guidance_comparison_20260930_r4/run.py')
    source=helper.source_audit(); assert source==freeze['source_before']
    means={p:sum(r['throughput'] for r in rows if r['policy']==p)/3 for p in ['hm_GPIBT','trained']}
    write(HERE/'audit.json',{'passed':True,'source_after':source,'trace_audits':audits,
                            'total_actions_replayed':4800000,'total_joint_positions':4804800,
                            'all_schedules_regenerated':True,'same_obstacle_graph':True,
                            'all_inputs_frozen_before_runs':True,'paired':paired,'verifier_sha256':sha(Path(__file__))})
    summary={'means':means,'paired':paired,'trained_relative_to_hm_percent':100*(means['trained']/means['hm_GPIBT']-1),
             'same_per_agent_exogenous_task_stream':True,'planner_tie_randomness_paired':False,
             'unchanged_published_native_algorithms':True,'task_workload_adapter':'author FixedAssignSystem with explicit alternating W/E schedules',
             'full_author_benchmark':False,'execution_error_test':False,'new_method_tested':False}
    write(HERE/'summary.json',summary); print(json.dumps(summary),flush=True)
if __name__=='__main__': main()
