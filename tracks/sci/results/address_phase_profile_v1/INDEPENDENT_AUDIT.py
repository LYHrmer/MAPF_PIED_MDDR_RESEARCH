import argparse, collections, hashlib, json, re
parser=argparse.ArgumentParser()
parser.add_argument("--batch-receipt-sha",required=True)
args=parser.parse_args()
from pathlib import Path
HERE=Path('/home/lyh/MAPF_SCI_RESEARCH/tracks/sci')
manifest=HERE/'config/address_phase_profile_v1_manifest.json'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected='0d4e08274314bb96f4596c3d43c3e4117c43d0f223b16af74e8850fa3c442ab7'
assert sha(manifest)==expected
m=json.loads(manifest.read_text())
inputs=manifest.parent/m['input_file']; assert sha(inputs)==m['input_sha256']
for name,pin in {**m['code_sha256'],**m['build_source_sha256']}.items(): assert sha(HERE/name)==pin, name
assert sha(HERE/m['binary'])==m['binary_sha256']
cases={c['id']:c for c in json.loads(inputs.read_text())['cases']}
batch=HERE/'results'/m['batch_id']
auth=json.loads((batch/'AUTHORIZATION.json').read_text())
assert auth['manifest_sha256']==expected
assert auth['jobs']==[j['id'] for j in m['jobs']]

def validate(paths,c):
    ids=sorted(map(int,c['endpoints']))
    assert sorted(map(int,paths))==ids
    ps={int(a):p for a,p in paths.items()}; blocked=set(c['blocked'])
    for a,p in ps.items():
        assert p and [p[0],p[-1]]==c['endpoints'][str(a)]
        for v in p: assert type(v) is int and 0<=v<c['rows']*c['cols'] and v not in blocked
        for u,v in zip(p,p[1:]):
            ur,uc=divmod(u,c['cols']);vr,vc=divmod(v,c['cols'])
            assert abs(ur-vr)+abs(uc-vc)<=1
    horizon=max(map(len,ps.values()))
    pos=lambda a,t: ps[a][min(t,len(ps[a])-1)]
    for t in range(horizon):
        occupied={}
        for a in ids:
            v=pos(a,t); assert v not in occupied, ('vertex',a,occupied.get(v),t,v)
            occupied[v]=a
        if t:
            for i,a in enumerate(ids):
                for b in ids[i+1:]:
                    assert not (pos(a,t-1)==pos(b,t) and pos(b,t-1)==pos(a,t)), ('edge',a,b,t)
    return {'soc':sum(len(p)-1 for p in ps.values()),'makespan':horizon-1,'agents':len(ids),'validated_terminal_residence':True}

def phase_audit(native, result):
    p=native['phase_profile'];assert result['phase_diagnostics']==p
    assert p['schema']=='ADDRESS_PHASE_PROFILE_V1'
    assert p['clock']=='STEADY_WALL_NS' and p['window']=='CONFIGURED_TO_FINISH_BEFORE_RECEIPT'
    assert p['exclusive'] is True and p['includes_instrumentation'] is True
    names=('DRIVER_OTHER','PREPROCESS','LNS_OTHER','GROUP_OTHER','TOPK','BETA','WALK','NEIGHBOR_PREPARE','REPAIR','POST_REPAIR','FINAL_CHECK_OUTPUT')
    phases=p['phases'];assert set(phases)==set(names)
    fields=('wall_ns','scope_entries','expired_calls','expired_samples','expired_sampled_wall_ns')
    for phase in phases.values():
        assert all(type(phase[k]) is int and phase[k]>=0 for k in fields)
        assert phase['expired_samples']<=phase['expired_calls']
        assert phase['expired_sampled_wall_ns']<=phase['wall_ns']
    total=sum(x['wall_ns'] for x in phases.values())
    assert total==p['window_wall_ns']==p['accounted_wall_ns'] and p['residual_wall_ns']==0
    assert total<=round(native['inner_wall_before_receipt_s']*1e9)+1000
    samp=p['expired_sampling']
    assert samp['sampled'] is True and samp['extrapolated'] is False and samp['stride']==1024
    assert samp['calls']==sum(x['expired_calls'] for x in phases.values())
    assert samp['samples']==sum(x['expired_samples'] for x in phases.values())==samp['calls']//1024
    assert samp['sampled_wall_ns']==sum(x['expired_sampled_wall_ns'] for x in phases.values())
    c=p['counters'];assert all(type(v) is int and v>=0 for v in c.values())
    assert c['group_calls']==native['group_calls']
    assert sum(c[k] for k in ('groups_formed','groups_no_seed','groups_too_small','groups_deadline'))==c['group_calls']
    assert c['groups_formed']>=native['attempt_trace_rows']
    assert c['seed_zero_delay_selected']+c['seed_positive_delay_selected']<=c['seed_calls']
    for name,num in [('GROUP_OTHER',c['group_calls']),('TOPK',c['seed_calls']),('WALK',c['walk_calls']),('REPAIR',native['attempt_trace_rows'])]:
        assert phases[name]['scope_entries']==num
    selected=c['seed_zero_delay_selected']+c['seed_positive_delay_selected']
    return {'window_wall_ns':total,'residual_wall_ns':0,'phases':phases,'counters':c,'expired_sampling':samp,
            'phase_percent_of_profile_window':{name:100*phases[name]['wall_ns']/total for name in names},
            'zero_delay_fraction_of_classified_selected_seeds':c['seed_zero_delay_selected']/selected if selected else None,
            'extrapolated_clock_total':None,
            'event_pairing_limit':'Counters aggregate events; they do not pair each selected seed with its group outcome. A task-specific source proof may support narrower deductions.'}

def inspect(job):
    folder=batch/job['id']; c=cases[job['case']]
    rec=json.loads((folder/'receipt.json').read_text());res=json.loads((folder/'result.json').read_text())
    attempt=json.loads((folder/'attempt.json').read_text());native=json.loads((folder/'native_receipt.json').read_text())
    for r in (rec,res,attempt): assert r['manifest_sha256']==expected and r['job']==job
    assert res['native_receipt']==native
    phase=phase_audit(native,res)
    for name,pin in rec['artifacts'].items():
        p=folder/name; assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],name
    assert rec['status']=='COMPLETE' and res['status']=='COMPLETE' and res['final_validated']
    assert rec['costs']['exit_code']==0 and rec['costs']['forced_cleanup'] is False
    assert rec['total_entry_through_output_validation_and_hash_ns'] < m['limits']['total_wall_s']*1e9
    before=validate(c['paths'],c);after=validate(res['final_paths'],c)
    assert before['soc']==res['initial_soc']==native['initial_soc']
    assert after['soc']==res['final_soc']==native['final_soc'] and after['soc']<=before['soc']
    assert after['makespan']==res['final_makespan']
    parsed={}
    for a,line in enumerate((folder/'final.paths').read_text().splitlines()):
        assert line.startswith('Agent '+str(a)+':')
        parsed[str(a)]=[int(r)*c['cols']+int(v) for r,v in re.findall(r'\((\d+),(\d+)\)->',line)]
    assert parsed==res['final_paths']
    raw=(folder/'attempts.jsonl').read_bytes();assert not raw or raw.endswith(b'\n')
    rows=[json.loads(x) for x in raw.splitlines()]
    counters=collections.Counter(); calls=0; rollback=0; late=[]; compact=[]
    times=collections.Counter()
    allowed={'UNKNOWN','FOUND','DEADLINE','COST_STOP','EMPTY_UNCLASSIFIED','START_BLOCKED','FOCAL_DRAINED_EMPTY'}
    previous_group=0
    for k,row in enumerate(rows,1):
        assert row['schema']=='ADDRESS_ATTEMPT_V2' and row['attempt_id']==k
        order=row['order']; returns=row['primary_returns'];pos=row['failed_position_zero_based']
        assert len(order)==len(set(order))==row['group_size'] and all(a in range(32) for a in order)
        assert row['primary_calls']==len(returns)<=len(order)
        assert pos==-1 or (0<=pos<len(order) and row['failed_agent']==order[pos])
        if pos==-1: assert row['failed_agent']==-1
        assert row['failed_agent_attempted']==(0<=pos<len(returns))
        if row['primary_complete']: assert pos==-1 and len(returns)==len(order)
        assert row['recovery_decision']=='NONE' and not row['blockers_checked'] and not row['recoverability_established']
        assert row['primary_stop'] in allowed
        assert previous_group<=row['group_calls_so_far']<=native['group_calls'];previous_group=row['group_calls_so_far']
        for index,r in enumerate(returns):
            assert r['position_zero_based']==index and r['agent']==order[index]
            assert r['stop'] in allowed and r['native_end'] in allowed
            assert r['empty']==(r['path_cost']==-1) and r['wall_ns']>=0 and r['cpu_ns']>=0
        cost=row['cost'];assert all(type(v) is int and v>=0 for v in cost.values())
        assert sum(r['wall_ns'] for r in returns)==cost['primary_search_wall_ns']
        assert sum(r['cpu_ns'] for r in returns)==cost['primary_search_cpu_ns']
        assert cost['primary_search_wall_ns']+cost['rollback_wall_ns']<=cost['attempt_wall_before_trace_ns']
        assert cost['primary_search_cpu_ns']+cost['rollback_cpu_ns']<=cost['attempt_cpu_before_trace_ns']
        if row['accepted']:
            assert row['primary_complete'] and row['final_group_cost']<=row['old_group_cost']
            assert not row['global_deadline_reached'] and not row['local_deadline_reached']
        else: assert row['final_group_cost']==row['old_group_cost']
        counters[row['primary_stop']]+=1;calls+=len(returns);rollback+=not row['accepted'];times.update(cost)
        if (row['primary_stop']=='FOCAL_DRAINED_EMPTY' and pos>=len(order)//2 and row['failed_agent_attempted'] and not row['global_deadline_reached'] and not row['local_deadline_reached']): late.append(k)
        compact.append({a:row[a] for a in ['attempt_id','order','primary_calls','primary_stop','failed_position_zero_based','failed_agent','failure_site','accepted','old_group_cost','final_group_cost','local_deadline_reached','global_deadline_reached']})
    assert native['attempt_trace_enabled'] and native['attempt_trace_rows']==len(rows)
    assert native['sipp_calls']==calls and native['rollbacks']==rollback
    assert native['trace_io_wall_ns']>=0 and native['trace_io_cpu_ns']>=0
    assert native['inner_cpu_s']<m['limits']['native_cpu_s']
    assert 0<=res['worker_cpu_ns']<m['limits']['worker_cpu_s']*1e9
    summary=res['attempt_diagnostics']
    assert summary['attempts']==len(rows) and summary['primary_search_calls']==calls
    assert summary['primary_stop_counts']==dict(counters) and summary['late_normal_empty_attempt_ids']==late
    return {'job':job['id'],'phase_audit':phase,'supervised_costs':rec['costs'],'worker_cpu_ns':res['worker_cpu_ns'],'stage_wall_ns':res['stage_wall_ns'],'receipt_sha256':sha(folder/'receipt.json'),'trace_sha256':sha(folder/'attempts.jsonl'),'initial':before,'final':after,'entry_wall_s':rec['total_entry_through_output_validation_and_hash_ns']/1e9,'native_cpu_s':native['inner_cpu_s'],'native_termination':{k:native[k] for k in ['global_deadline','last_stage','termination','group_calls','sipp_calls','sipp_deadlines','repair_deadlines','rollbacks']},'attempts':len(rows),'stop_counts':dict(counters),'late_normal_empty_attempt_ids':late,'cost_totals_ns':dict(times),'trace_io_wall_ns':native['trace_io_wall_ns'],'trace_io_cpu_ns':native['trace_io_cpu_ns'],'compact_attempts':compact}

batch_receipt=batch/'RUN_RECEIPT.json'
assert sha(batch_receipt)==args.batch_receipt_sha
br=json.loads(batch_receipt.read_text())
for name,pin in br['artifacts'].items():
    p=batch/name; assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes']
assert [j['id'] for j in m['jobs']]==['random-32-32-10__s01__n32__phase_profile','maze-32-32-2__s01__n32__phase_profile']
assert [j['job'] for j in br['jobs']]==[j['id'] for j in m['jobs']]
assert br['counts']=={'COMPLETE':2,'FAILED_OR_INCOMPLETE':0,'NOT_RUN_AFTER_BATCH_STOP':0}
verified=[inspect(j) for j in m['jobs']]
cost_stop_counts=collections.Counter()
for job in m['jobs']:
    for line in (batch/job['id']/'attempts.jsonl').read_text().splitlines():
        row=json.loads(line)
        if row['primary_stop']=='COST_STOP':
            rs=row['primary_returns'];assert len(rs)==row['group_size']
            assert all(r['stop']=='FOUND' and not r['empty'] for r in rs)
            candidate=sum(r['path_cost'] for r in rs);assert candidate>=row['old_group_cost']
            cost_stop_counts['equal' if candidate==row['old_group_cost'] else 'worse']+=1
out={'status':'PASS_INDEPENDENT_READONLY_PHASE_AUDIT','manifest_sha256':expected,'input_sha256':sha(inputs),
     'batch_receipt_sha256':sha(batch_receipt),'batch_artifacts_verified':len(br['artifacts']),
     'script_sha256':sha(Path(__file__)),'scientific_runs_executed_by_this_script':0,'jobs':verified,
     'cost_stop_candidate_cost_counts':dict(cost_stop_counts),
     'limits':'Instrumented diagnostic only; phase totals include instrumentation, clock samples are nested and never extrapolated; no speedup or novelty result.'}
p=Path('/tmp/mapf_phase_independent_audit.json');p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
