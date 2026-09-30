"""Predeclared public-source crops; execute native labels only after public choices are frozen."""
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
QUERY=HERE.parent
ROOT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
BASE=ROOT/'implementation_binding_evidence/baseline_selection_20260929'
SOURCE=BASE/'pied_run_01/result.json'
SOURCE_SHA='67c10baa0faa4b10200591982d970368c6f8292e87959a47b8f7d0d832849b10'
RUNS=[('train_1103',1103,'train','iid'),('train_2207',2207,'train','iid'),
      ('cal_3301',3301,'calibration','iid'),('test_4409',4409,'test','iid'),
      ('test_reverse_5501',5501,'test','reverse'),('test_zero_6607',6607,'test','zero')]
ARMS=['WAIT','global_bin','direction_bin','categorical_supervised','analytic_direction','lag2','RR']
DELTA={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write_new(path,data):
    with path.open('x',encoding='utf8') as f:json.dump(data,f,indent=2);f.write('\n')
def interval(row):return (Fraction(row['lower'],row['denominator']),Fraction(row['upper'],row['denominator']))
def command(argv,timeout):
    receipt={'argv':argv,'timeout_seconds':timeout,'started_utc':now(),'exit_code':None,'stdout':'','stderr':''}
    try:
        p=subprocess.run(argv,text=True,capture_output=True,timeout=timeout)
        receipt.update(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,timed_out=False)
    except subprocess.TimeoutExpired as e:
        decode=lambda x:x.decode(errors='replace') if isinstance(x,bytes) else x or ''
        receipt.update(stdout=decode(e.stdout),stderr=decode(e.stderr),timed_out=True)
    receipt['finished_utc']=now();return receipt

def extract():
    assert sha(SOURCE)==SOURCE_SHA
    source=json.loads(SOURCE.read_text());pre=json.loads((BASE/'pied_preflight.json').read_text())
    repo=BASE/'PIED-full'
    for rel,item in pre['manifest'].items():assert sha(repo/rel)==item['sha256']
    config=pre['configuration'];config_path=repo/'lifelong_benchmark/random/agent-100_scen-delay-0.010-1.json'
    map_path=(config_path.parent/config['mapFile']).resolve()
    lines=map_path.read_text().splitlines();height=int(lines[1].split()[1]);width=int(lines[2].split()[1]);cells=lines[4:]
    free={(x,y) for y,row in enumerate(cells) for x,z in enumerate(row) if z not in '@T'}
    assert height==width==32 and len(free)==819
    paths=[x.split(',') for x in source['actualPaths']]
    positions=[(c,r) for r,c,_ in source['start']]
    assert len(paths)==len(positions)==100 and all(len(p)==20 for p in paths)
    tasks={tid:(c,r) for tid,r,c in source['tasks']};heads=[deque() for _ in paths];assigned={};completed=[]
    rows=[];pairs=[];phases=[];pid=0
    for tick in range(20):
        for agent,events in enumerate(source['events']):
            for tid,et,kind in events:
                if et!=tick:continue
                if kind=='assigned':
                    assert tid not in assigned;assigned[tid]=tick;heads[agent].append(tid)
                elif kind=='finished':
                    assert heads[agent] and heads[agent].popleft()==tid and positions[agent]==tasks[tid]
                    completed.append(tid)
                else:raise AssertionError('unknown task event')
        owner={p:i for i,p in enumerate(positions)};ends=[];moves=[];local_pairs=[]
        assert len(owner)==100
        for agent,(x,y) in enumerate(positions):
            action=paths[agent][tick];dx,dy=DELTA[action];end=(x+dx,y+dy)
            assert end in free
            ends.append(end)
            row={'tick':tick,'agent':agent,'heading':action,'start':[x,y],'end':list(end),
                 'head_task':heads[agent][0] if heads[agent] else None,
                 'head_goal':list(tasks[heads[agent][0]]) if heads[agent] else None,
                 'revealed_tasks':list(heads[agent]),'source_record':f'actualPaths[{agent}][{tick}]'}
            rows.append(row)
            if action!='W':moves.append(row)
        assert len(set(ends))==100
        for requester,end in enumerate(ends):
            source_agent=owner.get(end)
            if source_agent is None or source_agent==requester:continue
            assert ends[source_agent]!=positions[requester],'author source reverse edge swap'
            if ends[source_agent]==positions[source_agent]:continue
            pair={'pair':pid,'tick':tick,'source_agent':source_agent,'requester_agent':requester,
                  'source_heading':paths[source_agent][tick],'source_start':list(positions[source_agent]),
                  'source_end':list(ends[source_agent]),'requester_start':list(positions[requester]),
                  'requester_end':list(end),'head_task':heads[requester][0],
                  'head_goal':list(tasks[heads[requester][0]]),
                  'terminal':tasks[heads[requester][0]]==end,
                  'source_binding':f'actualPaths[{source_agent}][{tick}]',
                  'requester_binding':f'actualPaths[{requester}][{tick}]'}
            pairs.append(pair);local_pairs.append(pair);pid+=1
        phases.append({'tick':tick,'moves':moves,'pairs':local_pairs});positions=ends
    # Last world row is checked too, but its newly revealed tasks never enter phase19 decisions.
    for agent,events in enumerate(source['events']):
        for tid,t,kind in events:
            if t==20 and kind=='finished':assert positions[agent]==tasks[tid];completed.append(tid)
    assert len(rows)==2000 and sum(len(p['moves']) for p in phases)==1791 and len(pairs)==355
    assert sum(p['terminal'] for p in pairs)==8 and len(completed)==52
    return {'status':'passed','origin':str(SOURCE),'source_sha256':SOURCE_SHA,'source_commit':pre['commit'],
            'map_path':str(map_path),'map_sha256':sha(map_path),'map_units':'1 cell = 1 simulation length unit',
            'actions':rows,'pairs':pairs,'phases':phases,'source_original_tasks_completed':52,
            'source_counts':{'actions':2000,'MOVE':1791,'WAIT':209,'follow_pairs':355,'terminal_pairs':8},
            'source_input_manifest':pre['manifest']}

def eta_for(seed,tick,agent,heading,regime):
    if regime=='zero':return 0
    value=int.from_bytes(hashlib.sha256(f'{seed}:{tick}:{agent}'.encode()).digest()[:8],'big')
    primary=-1 if heading in ['NO','SO'] else 1
    if regime=='reverse':primary=-primary
    return primary if value%10<9 else -primary

def choose(public_pairs,models,history,regime):
    # No private eta, native progress, current/future END or oracle labels are accepted here.
    choices={}
    for arm in ARMS:
        candidates=[]
        for p in public_pairs:
            h=p['source_heading'];agent=p['source_agent']
            if arm=='WAIT':prob=Fraction(0)
            elif arm=='RR':prob=Fraction(1)
            elif arm=='global_bin':prob=models['global']
            elif arm in ['direction_bin','categorical_supervised']:prob=models['direction'][h]
            elif arm=='analytic_direction':prob=Fraction(1,10) if h in ['NO','SO'] else Fraction(9,10)
            elif arm=='lag2':
                prior=history.get(agent,[]);prob=Fraction(prior[-2]['label']) if len(prior)>=2 else models['global']
            else:raise AssertionError(arm)
            score=prob if p['terminal'] else Fraction(0)
            candidates.append({'pair':p['pair'],'p_release':str(prob),'terminal':p['terminal'],'score':str(score),
                               'heading':h,'history_row_ids':[r['row_id'] for r in history.get(agent,[])] if arm=='lag2' else []})
        positive=[p for p in candidates if Fraction(p['score'])>0]
        selected=min(positive,key=lambda p:(-Fraction(p['score']),p['pair']))['pair'] if positive else None
        choices[arm]={'selected_pair':selected,'query_capacity':1,'candidates':candidates,'uses_current_truth':False}
    assert choices['direction_bin']==choices['categorical_supervised']
    return choices

def source_label(event):
    low,high=interval(event['at_query_progress']);threshold=Fraction(3,4)
    assert low>threshold or high<=threshold,'release label interval straddles strict threshold'
    return int(low>threshold)

def native_audit(events,phase):
    sources={e['agent']:e for e in events if e['event']=='source_original_END_delivered'}
    outcomes={(e['pair'],e['arm']):e for e in events if e['event']=='pair_episode'}
    assert len(sources)==len(phase['moves']) and len(outcomes)==2*len(phase['pairs'])
    for event in sources.values():
        assert event['full_cap_uninterrupted'] and event['offline_label_only']
        low,high=interval(event['original_END']);alpha=Fraction(event['alpha'])
        assert low*low<=alpha<=high*high
        delivered=interval(event['received']);assert delivered[0]<=low+Fraction(1,4)<=delivered[1]
        source_label(event)
    for p in phase['pairs']:
        wait=outcomes[p['pair'],'WAIT'];query=outcomes[p['pair'],'QUERY'];source=sources[p['source_agent']]
        for e in [wait,query]:
            assert e['source_agent']==p['source_agent'] and e['requester_agent']==p['requester_agent']
            assert e['task_id']==p['head_task'] and e['task_service']==p['terminal']
            assert e['requester_at_original_endpoint'] and e['requester_speed_zero'] and e['endpoint_retained']
            assert not e['production_AUTH'] and not e['full_100_robot_execution']
            assert e['strict_threshold']=='13/20' and e['epsilon']=='1/10'
            assert e['source_END']==source['original_END']
        assert wait['query_count']==0 and query['query_count']==1 and not wait['strict_cleared']
        assert query['strict_cleared']==bool(source_label(source))
        assert wait['requester_RUN']==wait['normal_END_delivered']
        assert query['requester_RUN']==({'lower':750000,'upper':750000,'denominator':1000000} if query['strict_cleared'] else query['normal_END_delivered'])
        wlow,whigh=interval(wait['requester_original_END']);qlow,qhigh=interval(query['requester_original_END'])
        assert qlow<=whigh and (query['strict_cleared'] or wait['requester_original_END']==query['requester_original_END'])
    summary=events[-1];assert summary['event']=='summary' and summary['status']=='passed'
    return sources,outcomes,summary['checks']

def fit(training):
    counts={h:Counter() for h in ['NO','SO','EA','WE']};all_counts=Counter()
    for row in training:counts[row['heading']][row['label']]+=1;all_counts[row['label']]+=1
    probs={h:Fraction(c[1]+1,sum(c.values())+2) for h,c in counts.items()}
    return {'direction':probs,'global':Fraction(all_counts[1]+1,sum(all_counts.values())+2),
            'counts':{h:dict(c) for h,c in counts.items()},'training_runs':['train_1103','train_2207'],
            'saturated_supervised_equals_direction_bin':True}

def run():
    receipt_path=HERE/'receipt_20260930_r2.json';receipt={'status':'failed_or_incomplete','started_utc':now(),
        'contract_sha256':sha(HERE/'CONTRACT_20260930_r2.md'),'commands':[],'runs':[],'training_rows':[],
        'protected_files':{str(p.relative_to(QUERY)):sha(p) for p in QUERY.iterdir() if p.is_file()},
        'source_header_sha256':json.loads((QUERY/'legal_and_sources.json').read_text()),
        'new_sources':{p.name:sha(p) for p in [Path(__file__),HERE/'native_20260930_r2.cpp']},
        'full_100_robot_execution':False,'published_baseline_comparison':False,'production_AUTH':False}
    with receipt_path.open('x',encoding='utf8') as f:
        def persist():f.seek(0);json.dump(receipt,f,indent=2);f.truncate();f.flush()
        try:
            public=extract();write_new(HERE/'public_source_20260930_r2.json',public)
            receipt['public_source_sha256']=sha(HERE/'public_source_20260930_r2.json');persist()
            for rel,expected in receipt['source_header_sha256'].items():assert sha(ROOT/rel)==expected
            with tempfile.TemporaryDirectory(prefix='query_public_r2_') as td:
                tmp=Path(td)
                for rel in receipt['source_header_sha256']:(tmp/Path(rel).name).write_bytes((ROOT/rel).read_bytes())
                library=ROOT/'third_party/flint_host_config';sdk=ROOT/'third_party/host_sdk/usr';binary=tmp/'native'
                cmd=['rtk','proxy','g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-elide-constructors',
                     '-I',str(tmp),'-isystem',str(sdk/'include'),'-isystem',str(library/'src'),str(HERE/'native_20260930_r2.cpp'),
                     '-L',str(library),'-L',str(sdk/'lib/x86_64-linux-gnu'),f'-Wl,-rpath,{library}','-lflint','-lmpfr','-lgmp','-o',str(binary)]
                print('strict native compile',flush=True);c=command(cmd,120);receipt['commands'].append(c);persist()
                assert c['exit_code']==0,'strict native compile failed'
                receipt['binary_sha256']=sha(binary)
                models=None;training=[]
                for run_id,seed,split,regime in RUNS:
                    history=defaultdict(list);rr={'run_id':run_id,'seed':seed,'split':split,'regime':regime,'phases':[],
                        'source_rows':[],'arm_totals':{arm:{'queries':0,'terminal_tasks':0,'terminal_completion_lower':'0',
                        'terminal_completion_upper':'0','early_terminal_tasks':0,'terminal_gain_lower':'0','terminal_gain_upper':'0'} for arm in ARMS}}
                    receipt['runs'].append(rr);persist()
                    if split!='train':assert models is not None
                    for phase in public['phases']:
                        tick=phase['tick'];before=now()
                        decisions=choose(phase['pairs'],models,history,regime) if models else {}
                        pr={'tick':tick,'public_choices_frozen_utc':before,'choices':decisions,
                            'future_truth_opened_after_choices':True,'public_current_phase_end_available':False}
                        rr['phases'].append(pr);persist() # causal receipt precedes physics execution
                        lines=[]
                        for m in phase['moves']:
                            eta=eta_for(seed,tick,m['agent'],m['heading'],regime)
                            lines.append(' '.join(map(str,['M',m['agent'],*m['start'],*m['end'],eta])))
                        for p in phase['pairs']:
                            lines.append(' '.join(map(str,['P',p['pair'],p['source_agent'],p['requester_agent'],
                                *p['source_start'],*p['source_end'],*p['requester_start'],p['head_task'],int(p['terminal'])])))
                        inp=tmp/f'{run_id}-{tick}.txt';inp.write_text('\n'.join(lines)+'\n')
                        pr['private_native_input_sha256']=sha(inp);pr['private_native_input']=inp.read_text()
                        print(f'{run_id} phase {tick}/19: {len(phase["moves"])} MOVE, {len(phase["pairs"])} pairs',flush=True)
                        c=command(['rtk','proxy',str(binary),str(inp)],60);receipt['commands'].append(c);pr['command_index']=len(receipt['commands'])-1;persist()
                        assert c['exit_code']==0,f'native phase failed {run_id}:{tick}'
                        events=[json.loads(line) for line in c['stdout'].splitlines() if line.startswith('{')]
                        sources,outcomes,checks=native_audit(events,phase);pr['native_checks']=checks
                        for m in phase['moves']:
                            e=sources[m['agent']];row={'row_id':f'{run_id}:{tick}:{m["agent"]}','run_id':run_id,'split':split,
                                'tick':tick,'agent':m['agent'],'heading':m['heading'],'label':source_label(e),
                                'alpha':e['alpha'],'delivered_global_upper':str(interval(e['received'])[1]+4*tick)}
                            assert Fraction(row['delivered_global_upper'])<4*(tick+1)
                            rr['source_rows'].append(row);history[m['agent']].append(row)
                            if split=='train':training.append(row)
                        for arm,decision in decisions.items():
                            totals=rr['arm_totals'][arm];selected=decision['selected_pair'];totals['queries']+=int(selected is not None)
                            for p in phase['pairs']:
                                if not p['terminal']:continue
                                e=outcomes[p['pair'],'QUERY' if selected==p['pair'] else 'WAIT'];w=outcomes[p['pair'],'WAIT']
                                lo,hi=interval(e['requester_original_END']);wl,wh=interval(w['requester_original_END'])
                                totals['terminal_tasks']+=1;totals['early_terminal_tasks']+=int(selected==p['pair'] and e['strict_cleared'])
                                for key,amount in [('terminal_completion_lower',lo),('terminal_completion_upper',hi),
                                                   ('terminal_gain_lower',wl-hi),('terminal_gain_upper',wh-lo)]:
                                    totals[key]=str(Fraction(totals[key])+amount)
                        persist()
                    if split=='train' and run_id=='train_2207':
                        models=fit(training);receipt['frozen_models']={**models,'direction':{k:str(v) for k,v in models['direction'].items()},
                           'global':str(models['global']),'frozen_utc':now(),'calibration_used_for_fit':False,
                           'training_row_ids':[r['row_id'] for r in training]};persist()
                    if split!='train':
                        rr['brier']={name:str(sum((Fraction(row['label'])-(models['global'] if name=='global' else models['direction'][row['heading']]))**2
                             for row in rr['source_rows'])/len(rr['source_rows'])) for name in ['global','direction']};persist()
                receipt['training_rows']=training
            for rel,expected in receipt['source_header_sha256'].items():assert sha(ROOT/rel)==expected
            assert receipt['protected_files']=={name:sha(QUERY/name) for name in receipt['protected_files']}
            assert sha(SOURCE)==SOURCE_SHA
            receipt['status']='passed'
        except Exception as e:receipt['error']=f'{type(e).__name__}: {e}'
        finally:receipt['finished_utc']=now();persist()
    print(json.dumps({'status':receipt['status'],'error':receipt.get('error'),'runs':len(receipt['runs']),'receipt':str(receipt_path)}),flush=True)
    return receipt['status']=='passed'

if __name__=='__main__':raise SystemExit(0 if run() else 1)
