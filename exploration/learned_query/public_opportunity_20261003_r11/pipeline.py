from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction as Q
from collections import Counter
import json,os,time,threading,sys
import runner
HERE=runner.HERE;OUT=HERE/'runs'
def records(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def worlds():
 result=[]
 for mi,map_name in enumerate(['empty-32-32','random-32-32-10']):
  for j in range(2):
   seed=111101+mi*1000+j;offset=(448 if mi==0 else 0)+j*16;scenario=runner.THIRD/'inputs'/map_name/(map_name+'-random-1.scen') if mi==0 else HERE/'inputs/random-32-32-10-random-2.scen';name=f'{map_name}_scen{1 if mi==0 else 2}_offset{offset}_train_{seed}';w=runner.make_world(name,16,seed,H=128,offset=offset,map_name=map_name,scenario_file=scenario);w.update(split='train',scenario_offset=offset,scenario_identity=scenario.name,scenario_path=str(scenario),scenario_sha256=runner.sha(scenario),family_key=name);result.append(w)
 return result
def selected_decisions(rs):
 seen=set();selected=[];slots=[];cost=0
 for d in rs:
  if d['event']!='actor_decision' or d['remaining_capacity']<=0:continue
  spent=16-d['remaining_capacity'];coupled=any(len({cl['task'] for cl in c['claims']})>1 or any(cl['owners']>1 for cl in c['claims']) for c in d['candidates']);key=(int(spent>=8),int(coupled))
  if key in seen:continue
  seen.add(key);required=1+2*len(d['candidates']);include=cost+required<=18
  slots.append(dict(budget_tier='late' if key[0] else 'early',blocking='coupled' if coupled else 'simple',opportunity=d['opportunity'],at=d['at'],remaining=d['remaining_capacity'],candidate_count=len(d['candidates']),branch_cost=required,included=include,reason='first_public_slot' if include else 'full_opportunity_exceeds18'))
  if include:selected.append(d);cost+=required
 return selected,slots
def batch(jobs,workers,tag,models=None):
 result=[];stop=threading.Event();peak=dict(rss_bytes=0,processes=0,cpu_ticks=0,samples=0);start=time.monotonic()
 def sample():
  while not stop.is_set():
   stats={}
   for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
     z=(p/'stat').read_text().split();stats[int(p.name)]=(int(z[3]),int(z[23])*os.sysconf('SC_PAGE_SIZE'),int(z[13])+int(z[14]))
    except (OSError,ValueError,IndexError):pass
   ids={os.getpid()}
   while True:
    new={i for i,z in stats.items() if z[0] in ids}|ids
    if new==ids:break
    ids=new
   z=[stats[i] for i in ids if i in stats];peak['rss_bytes']=max(peak['rss_bytes'],sum(r[1] for r in z));peak['processes']=max(peak['processes'],len(z));peak['cpu_ticks']=max(peak['cpu_ticks'],sum(r[2] for r in z));peak['samples']+=1;stop.wait(1)
 monitor=threading.Thread(target=sample,daemon=True);monitor.start()
 try:
  with ThreadPoolExecutor(max_workers=workers) as pool:
   futures=[pool.submit(runner.native,w,p,OUT,models) for w,p in jobs]
   for f in as_completed(futures):result.append(f.result())
 finally:stop.set();monitor.join()
 runner.write(HERE/(tag+'_SCHEDULING.json'),dict(workers=workers,jobs=len(jobs),seconds=time.monotonic()-start,descendant_peak=peak,failed=sum(e['error'] is not None for e in result)))
 return result
def preflight(ws):
 result=[]
 for w in ws:
  blocked=[(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='@'];free={(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='.'}
  assert len(free)+len(blocked)==w['rows']*w['cols']
  for r in w['robots']:
   assert tuple(r['start']) in free
   assert all(tuple(t['goal']) in free for t in r['tasks'])
  edges=0
  for x,y in free:
   for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
    if (x+dx,y+dy) not in free:continue
    # All coordinates are exact integer twentieths; closed rectangles.
    xl,xh=20*min(x,x+dx)-3,20*max(x,x+dx)+3;yl,yh=20*min(y,y+dy)-3,20*max(y,y+dy)+3
    assert all(xh<20*bx-10 or 20*bx+10<xl or yh<20*by-10 or 20*by+10<yl for bx,by in blocked),'closed swept footprint hits blocked square'
    edges+=1
  result.append(dict(world=w['name'],N=w['N'],free=len(free),blocked=len(blocked),all_directed_free_edges_checked=edges,goals_checked=sum(len(r['tasks']) for r in w['robots'])))
 ids={split:{t['task'] for w in ws if w['split']==split for r in w['robots'] for t in r['tasks']} for split in ['train','calibration','test','scale']}
 assert all(not a&b for i,a in enumerate(ids.values()) for b in list(ids.values())[i+1:])
 runner.write(HERE/'MAP_INPUT_PREFLIGHT.json',dict(passed=True,worlds=result,split_task_ids_disjoint=True))
def novelty(ws):
 previous_seeds=set();previous_ids=set();sources=[];prior_sequences=[]
 def walk(o):
  if isinstance(o,dict):
   if isinstance(o.get('seed'),int):previous_seeds.add(o['seed'])
   if isinstance(o.get('task'),int):previous_ids.add(o['task'])
   if isinstance(o.get('robots'),list) and o['robots'] and all(isinstance(x,dict) and 'start' in x for x in o['robots']):prior_sequences.append((o.get('map_name','empty-32-32'),[tuple(x['start']) for x in o['robots']]))
   for v in o.values():walk(v)
  elif isinstance(o,list):
   for v in o:walk(v)
 for parent in HERE.parent.iterdir():
  if not parent.is_dir() or parent==HERE:continue
  for f in parent.glob('**/*REGISTRATION*.json'):
   if 'runs' in f.parts:continue
   walk(json.loads(f.read_text()));sources.append(dict(path=str(f),sha256=runner.sha(f)))
 matched_rows=[]
 for map_name in ['empty-32-32','random-32-32-10']:
  scen=runner.THIRD/'inputs'/map_name/(map_name+'-random-1.scen');positions=[tuple(map(int,s.split()[4:6])) for s in scen.read_text().splitlines()[1:]]
  for name,seq in prior_sequences:
   if name!=map_name or len(seq)<8:continue
   offsets=[i for i in range(len(positions)-len(seq)+1) if positions[i:i+len(seq)]==seq]
   for off in offsets:
    assert name!='empty-32-32' or not set(range(off,off+len(seq)))&set(range(448,480)),(name,off,len(seq))
    matched_rows.append(dict(map=name,offset=off,N=len(seq)))
 assert not {w['seed'] for w in ws}&previous_seeds
 assert not {t['task'] for w in ws for r in w['robots'] for t in r['tasks']}&previous_ids
 runner.write(HERE/'NOVELTY_PREFLIGHT.json',dict(passed=True,old_registration_sources=sources,prior_seed_count=len(previous_seeds),new_seeds=[w['seed'] for w in ws],new_rows={w['family_key']:dict(scenario=w['scenario_identity'],offset=w['scenario_offset'],N=16,sha256=w['scenario_sha256']) for w in ws},prior_matched_row_groups=matched_rows,seed_and_task_ID_disjoint=True,scenario_row_groups_disjoint=True))
def register():
 ws=worlds();novelty(ws);preflight(ws);runner.compile_native()
 source_files=['CONTRACT.md','runner.py','pipeline.py','joint_history_native.cpp','audit.py','audit_reference.py']
 runner.write(HERE/'REGISTRATION.json',dict(worlds=ws,stage='TRAIN-only finite public opportunity coverage; no model or test',frozen={f:runner.sha(HERE/f) for f in source_files},binary_sha256=runner.sha(HERE/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),max_native_episodes=140,baseline_episodes=8,max_single_probes=72,max_pair_probes=60,native_workers=6,audit_workers=2))
 runner.write(HERE/'COMPILE_RECEIPT.json',dict(attempts=[json.loads(p.read_text()) for p in (HERE/'build').glob('compile*.json')],binary_sha256=runner.sha(HERE/'build/joint_history_native')))
def main():
 phase=sys.argv[1]
 if phase=='register':register();return
 reg=json.loads((HERE/'REGISTRATION.json').read_text());ws=reg['worlds']
 if phase=='base':batch([(w,policy) for w in ws for policy in ['condition','WAIT']],6,'BASE');return
 if phase=='probes':
  jobs=[];coverage=[];unavailable=[]
  for w in ws:
   e=json.loads((OUT/(w['name']+'__condition.receipt.json')).read_text());assert e['error'] is None;rs=records(e);ds,slots=selected_decisions(rs)
   coverage.append(dict(world=w['name'],slots=slots,selected_opportunities=[d['opportunity'] for d in ds],full_census=Counter((str(min(2,len(r['candidates']))) if r['event']=='actor_decision' else 'empty') for r in rs if r['event']=='actor_decision' or r['event']=='opportunity_census' and r['candidates']==0)))
   for d in ds:
    for action in ['WAIT']+[kind+str(c['agent']) for c in d['candidates'] for kind in ['QUERY','SKIP']]:jobs.append((w,f"cf_{d['opportunity']}_{action}"))
   for late in [False,True]:
    d=next((d for d in ds if (16-d['remaining_capacity']>=8)==late),None)
    if d is None:unavailable.append(dict(world=w['name'],anchor_tier='late' if late else 'early',reason='no_complete_selected_public_anchor',planned_pairs=6 if late else 9));continue
    anchor=min(d['candidates'],key=lambda c:(-Q(c['score']),c['agent'],c['move']))
    for first in ['WAIT','QUERY','SKIP']:
     for second in ['QUERY','SKIP']:jobs.append((w,f"pair_{d['opportunity']}_{first}{anchor['agent']}_{second}_distinct"))
     if not late:jobs.append((w,f"pair_{d['opportunity']}_{first}{anchor['agent']}_SKIP_successor"))
  assert len(jobs)<=132
  runner.write(HERE/'BRANCHES_BEFORE_OUTCOMES.json',dict(jobs=[dict(world=w['name'],policy=p) for w,p in jobs],coverage=coverage,anchor_unavailable=unavailable,complete_single_branches=sum(p.startswith('cf_') for w,p in jobs),pair_branches=sum(p.startswith('pair_') for w,p in jobs),selection_uses_public_state_only=True,oracle_second_selection=False))
  es=batch(jobs,6,'PROBES');all_es=[json.loads(p.read_text()) for p in OUT.glob('*.receipt.json')]
  runner.write(HERE/'RECEIPT.json',dict(complete=True,native_episodes=len(all_es),probe_episodes=len(es),failed=sum(e['error'] is not None for e in all_es),no_model_training=True,no_TEST_selection=True));return
 raise ValueError(phase)
if __name__=='__main__':main()
