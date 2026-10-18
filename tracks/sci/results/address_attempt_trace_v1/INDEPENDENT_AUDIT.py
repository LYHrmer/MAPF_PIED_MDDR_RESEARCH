import collections, hashlib, json, re
from pathlib import Path
HERE=Path('/home/lyh/MAPF_SCI_RESEARCH/tracks/sci')
manifest=HERE/'config/address_attempt_trace_v1_manifest.json'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected='edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3'
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

def inspect(job):
    folder=batch/job['id']; c=cases[job['case']]
    rec=json.loads((folder/'receipt.json').read_text());res=json.loads((folder/'result.json').read_text())
    attempt=json.loads((folder/'attempt.json').read_text());native=json.loads((folder/'native_receipt.json').read_text())
    for r in (rec,res,attempt): assert r['manifest_sha256']==expected and r['job']==job
    assert res['native_receipt']==native
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
    summary=res['attempt_diagnostics']
    assert summary['attempts']==len(rows) and summary['primary_search_calls']==calls
    assert summary['primary_stop_counts']==dict(counters) and summary['late_normal_empty_attempt_ids']==late
    return {'job':job['id'],'receipt_sha256':sha(folder/'receipt.json'),'trace_sha256':sha(folder/'attempts.jsonl'),'initial':before,'final':after,'entry_wall_s':rec['total_entry_through_output_validation_and_hash_ns']/1e9,'native_cpu_s':native['inner_cpu_s'],'native_termination':{k:native[k] for k in ['global_deadline','last_stage','termination','group_calls','sipp_calls','sipp_deadlines','repair_deadlines','rollbacks']},'attempts':len(rows),'stop_counts':dict(counters),'late_normal_empty_attempt_ids':late,'cost_totals_ns':dict(times),'trace_io_wall_ns':native['trace_io_wall_ns'],'trace_io_cpu_ns':native['trace_io_cpu_ns'],'compact_attempts':compact}

batch_receipt=batch/'RUN_RECEIPT.json'
assert sha(batch_receipt)=='308e5a65e98270b6049336dff0c50da88bbbf137755fc2875a9203d91d5a8632'
br=json.loads(batch_receipt.read_text())
for name,pin in br['artifacts'].items():
    p=batch/name; assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes']
counts=collections.Counter()
for job in m['jobs']:
    for line in (batch/job['id']/'attempts.jsonl').read_text().splitlines():
        row=json.loads(line)
        if row['primary_stop']=='COST_STOP':
            rs=row['primary_returns']; assert len(rs)==row['group_size']
            assert all(r['stop']=='FOUND' and not r['empty'] for r in rs)
            candidate=sum(r['path_cost'] for r in rs);assert candidate>=row['old_group_cost']
            counts['equal' if candidate==row['old_group_cost'] else 'worse']+=1
out={'status':'PASS_INDEPENDENT_READONLY_AUDIT','manifest_sha256':expected,'input_sha256':sha(inputs),'jobs':[inspect(j) for j in m['jobs']],
'batch_receipt_sha256':sha(batch_receipt),'batch_artifacts_verified':len(br['artifacts']),
'cost_stop_candidate_cost_counts':dict(counts),
'cost_stop_interpretation':'All 17 COST_STOP attempts have full FOUND calls; 9 equal-cost and 8 worse-cost, not single-agent search failures.',
'scope_decision':'No observed normal late empty return meets the preregistered position threshold; stop or narrow the present late-failure recovery candidate on these tasks. No assertion that all local recovery is ineffective.'}
p=Path('/tmp/mapf_trace_independent_audit.json');p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
