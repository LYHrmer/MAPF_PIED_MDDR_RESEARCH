"""Independent read-only audit of the two authorized frozen seed DEV batches.

Parses recorded paths and counters; imports no project solver or validator and
constructs no new MAPF task or scientific run. Writes only its /tmp audit JSON.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re
import subprocess

ROOT=Path('/home/lyh/MAPF_SCI_RESEARCH')
HERE=ROOT/'tracks/sci'
COMMIT='93af30fd4aeb00c0d1fe4c2836c6a6a59f746599'
BATCHES=[('address_seed_fixed_v1','c5e6f03bc9378b52dc3ab88a7fba4688dc41f7f3f14910aced73b3e1efd23993'),
         ('address_seed_time_v1','508652f403e758e4fd1d0831b7a7093b3b56c317bb92d9414a8ba5514acb8d31')]
AGGREGATES={'address_seed_fixed_v1':'f33214f25ce9b69ae1ca40c19761d2bba007f0f42183e0915752fab21a99a1ff',
            'address_seed_time_v1':'1dd7777ca1c77f319c12eba60776831f9c196272d5e0fd84a1f47975b916f22d'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(p.read_bytes())
def gitread(path):return subprocess.check_output(['rtk','proxy','git','-C',str(ROOT),'show',COMMIT+':tracks/sci/'+path])
def validate(paths,c):
    assert set(paths)==set(c['endpoints'])
    blocked=set(c['blocked']);cols=c['cols'];maxv=c['rows']*cols
    for a,p in paths.items():
        assert p and [p[0],p[-1]]==c['endpoints'][a]
        assert all(type(v) is int and 0<=v<maxv and v not in blocked for v in p)
        assert all(abs(x//cols-y//cols)+abs(x%cols-y%cols)<=1 for x,y in zip(p,p[1:]))
    for t in range(max(map(len,paths.values()))):
        at=[p[min(t,len(p)-1)] for p in paths.values()]
        assert len(at)==len(set(at)),('vertex or permanent goal conflict',t)
        if t:
            edges=[(p[min(t-1,len(p)-1)],p[min(t,len(p)-1)]) for p in paths.values()]
            assert all(not(a==d and b==c) for (a,b),(c,d) in itertools.combinations(edges,2)),('edge swap',t)
    return sum(len(p)-1 for p in paths.values()),max(len(p)-1 for p in paths.values())
def native_paths(raw,c):
    lines=raw.decode('ascii').splitlines();ids=sorted(c['endpoints'],key=int)
    assert len(lines)==len(ids)
    paths={}
    for i,(a,line) in enumerate(zip(ids,lines)):
        prefix='Agent '+str(i)+':'
        assert line.startswith(prefix)
        body=line[len(prefix):];assert re.fullmatch(r'(\([0-9]+,[0-9]+\)->)+',body)
        coords=[tuple(map(int,x)) for x in re.findall(r'\(([0-9]+),([0-9]+)\)->',body)]
        assert all(r<c['rows'] and col<c['cols'] for r,col in coords)
        paths[a]=[r*c['cols']+col for r,col in coords]
    return paths
def nonnegative_int(x):assert type(x) is int and x>=0

rows=[];pins=0;artifact_count=0;all_batch_artifacts=0;last_receipt_mtime=0;common_binary=None;common_input=None;pair_inputs={};batch_shas={}
for batch,manifest_sha in BATCHES:
    folder=HERE/'results'/batch;manifest_path=HERE/'config'/(batch+'_manifest.json')
    raw=manifest_path.read_bytes();assert sha(raw)==manifest_sha;assert raw==gitread('config/'+manifest_path.name)
    m=json.loads(raw);assert m['comparison_protocol']=='seed_admission_v1'
    assert m['attempt_trace'] is False and m['phase_profile'] is False
    assert m['retry']==0 and m['stop_batch_on_any_failure'] is True and m['previous_authorization_reusable'] is False
    assert m['combined_proposal_order']==[b[0] for b in BATCHES]
    for name,pin in dict(m['code_sha256'],**m['build_source_sha256']).items():assert sha(gitread(name))==pin;pins+=1
    binary=(HERE/m['binary']).resolve();assert sha(binary.read_bytes())==m['binary_sha256']
    if common_binary is None:common_binary=m['binary_sha256'];common_input=m['input_sha256']
    assert m['binary_sha256']==common_binary and m['input_sha256']==common_input
    inputs=(manifest_path.parent/m['input_file']).read_bytes();assert sha(inputs)==common_input
    cases={c['id']:c for c in json.loads(inputs)['cases']}
    auth=read(folder/'AUTHORIZATION.json');assert auth['actual_user_answer']=='授权这8项，严格按清单执行'
    assert auth['source_question_id']=='call_b30d0e75ab0d47969e79ae4b9641c810'
    assert auth['recorded_before_any_scientific_launch'] is True and auth['scientific_code_commit']==COMMIT
    assert auth['manifest_sha256']==manifest_sha and auth['jobs']==[j['id'] for j in m['jobs']]
    assert auth['limits']==m['limits'] and auth['sole_executor']=='/root' and auth['retry_allowed'] is False
    assert auth['combined_manifest_order']==[{'batch':b,'sha256':s} for b,s in BATCHES]
    aggregate=read(folder/'RUN_RECEIPT.json');batch_shas[batch]=sha((folder/'RUN_RECEIPT.json').read_bytes())
    assert batch_shas[batch]==AGGREGATES[batch]
    assert aggregate['counts']=={'COMPLETE':4,'FAILED_OR_INCOMPLETE':0,'NOT_RUN_AFTER_BATCH_STOP':0}
    assert aggregate['status']=='ALL_COMPLETE' and aggregate['scientific_code_commit']==COMMIT
    assert aggregate['authorization_consumed_or_closed'] is True and aggregate['retry_allowed'] is False
    assert aggregate['manifest_sha256']==manifest_sha and aggregate['first_failed_job'] is None
    for relative,pin in aggregate['artifacts'].items():
        raw=(folder/relative).read_bytes();assert sha(raw)==pin['sha256'] and len(raw)==pin['bytes'];all_batch_artifacts+=1
    byjob={r['job']:r for r in aggregate['jobs']}
    for j in m['jobs']:
        d=folder/j['id'];receipt=read(d/'receipt.json');result=read(d/'result.json');native=read(d/'native_receipt.json');attempt=read(d/'attempt.json')
        assert (folder/'AUTHORIZATION.json').stat().st_mtime_ns<=(d/'attempt.json').stat().st_mtime_ns
        assert last_receipt_mtime<=(d/'attempt.json').stat().st_mtime_ns
        last_receipt_mtime=(d/'receipt.json').stat().st_mtime_ns
        assert attempt['status']=='CONSUMED_ONCE' and attempt['retries']==0 and attempt['authorization_reference']
        for obj in (attempt,receipt,result):assert obj['job']==j and obj['manifest_sha256']==manifest_sha
        assert receipt['status']=='COMPLETE' and result['status']=='COMPLETE' and result['final_validated'] is True
        assert receipt['retry_allowed'] is False and receipt['independent_performance_result'] is False
        assert receipt['audit_receipt_write_and_process_exit_excluded'] is True
        for name,pin in receipt['artifacts'].items():
            data=(d/name).read_bytes();assert sha(data)==pin['sha256'] and len(data)==pin['bytes'];artifact_count+=1
            assert len(data)<=16*1024**2
        c=cases[j['case']];original=c['paths'];initial_soc,initial_ms=validate(original,c)
        lines=(d/'initial.txt').read_text().splitlines();assert int(lines[0])==len(original)
        initial={}
        for a,line in zip(sorted(original,key=int),lines[1:]):
            vals=list(map(int,line.split()));assert len(vals)-1==vals[0];initial[a]=vals[1:]
        assert initial==original
        final=native_paths((d/'final.paths').read_bytes(),c);soc,ms=validate(final,c)
        assert final==result['final_paths'] and native==result['native_receipt']
        assert soc==result['final_soc']==native['final_soc']<=initial_soc==native['initial_soc']==result['initial_soc']
        assert ms==result['final_makespan'];assert native['initial_and_final_validated'] is True
        assert native['seed']==j['seed']==0 and j['top_k']==32
        costs=receipt['costs'];limits=m['limits']
        assert costs['exit_code']==0 and costs['forced_cleanup'] is False and costs['interruption'] is None
        total=receipt['total_entry_through_output_validation_and_hash_ns']/1e9
        assert total<limits['total_wall_s'] and native['inner_cpu_s']<limits['native_cpu_s']
        assert result['worker_cpu_ns']/1e9<limits['worker_cpu_s']
        assert costs['largest_child_maxrss_kib']<limits['per_process_as_mib']*1024
        assert native['cpu_limit_s']==10 and native['cpu_reserve_s']==1
        assert native['inner_wall_before_receipt_s']<=result['stage_wall_ns']['native_launch_through_exit']/1e9+1e-6<=total+1e-6
        assert native['attempt_trace_enabled'] is False and native['attempt_trace_rows']==0
        assert native['trace_io_wall_ns']==native['trace_io_cpu_ns']==0 and 'phase_profile' not in native
        assert native['reward_semantics']=='AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK'
        attempts=native['repair_attempts'];nonnegative_int(attempts)
        for k in ('group_calls','sipp_calls','rollbacks','sipp_deadlines','repair_deadlines'):nonnegative_int(native[k])
        assert attempts<=native['group_calls'] and native['rollbacks']<=attempts
        assert native['sipp_deadlines']<=native['sipp_calls']
        a=native['seed_admission'];assert a['policy']==j['seed_admission']
        for k in ('selection_calls','agents_checked','topk_candidates','filtered_zero_candidates','retained_topk_candidates','empty_eligible_calls','deadline_calls','selected_calls'):nonnegative_int(a[k])
        assert a['selection_calls']==a['empty_eligible_calls']+a['deadline_calls']+a['selected_calls']<=native['group_calls']
        assert a['topk_candidates']==a['filtered_zero_candidates']+a['retained_topk_candidates']
        if j['seed_admission']=='all':assert a['agents_checked']==a['filtered_zero_candidates']==a['empty_eligible_calls']==0
        else:assert a['agents_checked']<=32*a['selection_calls']
        assert native['effort_mode']==j['effort_mode']
        assert native['termination']==native['loop_exit_reason']
        assert native['deadline_resource'] in ('NONE','CPU','WALL','WALL_AND_CPU')
        assert native['global_deadline']==(native['deadline_resource']!='NONE')
        reason=native['termination'];cap=native['repair_cap']
        if j['effort_mode']=='fixed_repairs':assert cap==j['iterations']==16 and attempts<=cap
        else:assert cap is None and j['iterations']==0 and reason!='REPAIR_CAP'
        if reason=='REPAIR_CAP':assert attempts==16 and native['global_deadline'] is False
        elif reason=='GLOBAL_DEADLINE':assert native['global_deadline'] is True
        elif reason=='STATIC_SOC_BOUND':assert native['static_soc_lower_bound_reached'] is True
        elif reason=='PREPROCESS_FALLBACK':assert native['preprocessing_fallback'] is True
        else:assert reason=='AUTHOR_TIME_LIMIT'
        command=result['native_command'];assert Path(command[0]).resolve()==binary
        flags=dict(zip(command[1::2],command[2::2]));assert len(command)==1+2*len(flags)
        for k,v in {'--maxIterations':str(j['iterations']),'--seedAdmission':j['seed_admission'],'--effortMode':j['effort_mode'],'--seed':'0','--k':'32','--replanAlgo':'PP','--neighborSize':'8','--algorithm':'bernoulie','--destroyStrategy':'RandomWalk','--sipp':'1','--cpuLimit':'10','--cpuReserve':'1','--finalReserve':'1'}.items():assert flags[k]==v
        assert '--attemptTrace' not in flags and '--phaseProfile' not in flags
        equal_work=(j['effort_mode']=='fixed_repairs' and attempts==16 and reason in ('REPAIR_CAP','STATIC_SOC_BOUND'))
        diag=result['comparison_diagnostics'];assert diag['repair_attempts']==attempts and diag['equal_work_timing_eligible']==equal_work
        key=(batch,j['case']);inshas={k:receipt['artifacts'][k]['sha256'] for k in ('map.txt','agents.txt','initial.txt')}
        if key in pair_inputs:assert pair_inputs[key]==inshas
        else:pair_inputs[key]=inshas
        agg=byjob[j['id']];assert agg['final_soc']==soc and agg['final_makespan']==ms
        assert agg['receipt_sha256']==sha((d/'receipt.json').read_bytes())
        rows.append({'batch':batch,'case':j['case'],'policy':j['seed_admission'],'effort_mode':j['effort_mode'],'initial_soc':initial_soc,'final_soc':soc,'initial_makespan':initial_ms,'final_makespan':ms,'total_entry_s':total,'native_cpu_s':native['inner_cpu_s'],'group_calls':native['group_calls'],'repair_attempts':attempts,'sipp_calls':native['sipp_calls'],'rollbacks':native['rollbacks'],'accepted_attempts':attempts-native['rollbacks'],'stop_reason':reason,'deadline_resource':native['deadline_resource'],'equal_work_timing_eligible':equal_work,'seed_admission':a})
assert len(rows)==8
pairs=[]
for (batch,_),case in itertools.product(BATCHES,('random-32-32-10__s01__n32','maze-32-32-2__s01__n32')):
    arms={r['policy']:r for r in rows if r['batch']==batch and r['case']==case};a,b=arms['all'],arms['positive_delay']
    eligible=a['equal_work_timing_eligible'] and b['equal_work_timing_eligible']
    pairs.append({'batch':batch,'case':case,'positive_minus_all_soc':b['final_soc']-a['final_soc'],'positive_minus_all_makespan':b['final_makespan']-a['final_makespan'],'equal_count_cost_ratio_all_over_positive':a['total_entry_s']/b['total_entry_s'] if eligible else None,'ratio_is_single_observation_not_stable_speedup':True})
out={'schema':'INDEPENDENT_FROZEN_SEED_COMPARISON_AUDIT_V1','status':'PASS','script_sha256':sha(Path(__file__).read_bytes()),'scientific_code_commit':COMMIT,'batch_receipt_sha256':batch_shas,'runtime_build_manifest_pins_checked':pins,'job_artifact_hashes_checked':artifact_count,'batch_artifact_hashes_checked':all_batch_artifacts,'new_solver_or_scientific_run':False,'complete_32_robot_paths_checked':8,'permanent_goal_holds_and_edge_swaps_checked':True,'administrative_exclusions_and_mtime_order_checked':True,'source_question_id':'call_b30d0e75ab0d47969e79ae4b9641c810','rows':rows,'within_protocol_pairs':pairs,'limits':['all cases and seed0 are development observations, not independent/repeated performance','fixed-count random baseline reached4/16, so no equal-work cost ratio','5s total-budget has no16 cap; CPU hard10 soft9 retained','15s and5s protocols have different original per-repair time_limit/100 allowances; no cross-protocol causal comparison','single shared binary and matched within-protocol inputs, solver, reward, budget and output check; filtering changes PRNG/neighborhood sequence']}
Path('/tmp/mapf_seed_independent_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('rows','within_protocol_pairs')},ensure_ascii=False))
for row in rows:print(row['batch'],row['case'],row['policy'],row['final_soc'],row['final_makespan'],row['repair_attempts'],row['total_entry_s'])
print(json.dumps(pairs,ensure_ascii=False))
