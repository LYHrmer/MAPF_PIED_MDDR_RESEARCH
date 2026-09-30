"""Independent exact inputs and full native traces; no native executions."""
from pathlib import Path
from collections import Counter,deque
import hashlib,importlib.util,json,random,sys
HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/HERE.name
NAMES=['empty-32-32','random-32-32-10','maze-32-32-2','room-32-32-4']
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def reachable(grid,start):
 seen={start};todo=[start];w=len(grid[0]);h=len(grid)
 for v in todo:
  y,x=divmod(v,w)
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   ny,nx=y+dy,x+dx;u=ny*w+nx
   if 0<=ny<h and 0<=nx<w and grid[ny][nx] not in '@T' and u not in seen:seen.add(u);todo.append(u)
 return sorted(seen)
def inputs_check(freeze):
 assert [x['map'] for x in freeze['inputs']]==NAMES and freeze['agents']==64 and freeze['horizon']==1000 and freeze['native_seed']==930301 and freeze['tasks_per_agent']==1002
 registry=read(HERE.parent/'mapf_evaluation_20260930_r5/registry.json');data={}
 for item in freeze['inputs']:
  config_path=Path(item['instance']);cfg=read(config_path);map_path=config_path.parent/cfg['mapFile'];scenario=Path(item['scenario'])
  assert sha(map_path)==registry['maps'][item['map']]['map_sha256'] and sha(scenario)==registry['maps'][item['map']]['scenarios'][0]['sha256']
  lines=map_path.read_text().splitlines();assert lines[:4]==['type octile','height 32','width 32','map'];grid=lines[4:];assert len(grid)==32 and all(len(r)==32 for r in grid)
  assert cfg['teamSize']==64 and cfg['numTasksReveal']==1 and cfg['taskAssignmentStrategy']=='roundrobin_fixed'
  starts=[int(s) for s in (config_path.parent/cfg['agentFile']).read_text().splitlines()];assert starts.pop(0)==64 and len(starts)==len(set(starts))==64
  flat=[int(s) for s in (config_path.parent/cfg['taskFile']).read_text().splitlines()];assert flat.pop(0)==64*1002 and len(flat)==64*1002
  streams=[flat[a::64] for a in range(64)];components={}
  for a,line in enumerate(scenario.read_text().splitlines()[1:65]):
   fields=line.split();assert fields[1]==item['map']+'.map' and fields[2:4]==['32','32'];sx,sy,gx,gy=map(int,fields[4:8]);assert starts[a]==sy*32+sx and streams[a][0]==gy*32+gx
   cells=components.get(starts[a])
   if cells is None:
    cells=reachable(grid,starts[a])
    for v in cells:components[v]=cells
   index={v:i for i,v in enumerate(cells)};assert streams[a][0] in index
   rng=random.Random(f'standard-map-r5:930301:{item["map"]}:{a}')
   for old,new in zip(streams[a],streams[a][1:]):
    choice=rng.randrange(len(cells)-1);skip=index[old];expected=cells[choice if choice<skip else choice+1]
    assert new==expected and new!=old
  data[item['map']]=(starts,streams,grid)
 return data
def trace_check(row,data):
 d=Path(row['work']);job=read(d/'job.json');receipt=read(d/'receipt.json');assert receipt['returncode']==row['returncode']==0 and not receipt['timed_out']
 for filename,key in [('job.json','job_sha256'),('trace.json','trace_sha256'),('job.result.json','result_sha256')]:assert sha(d/filename)==row[key]
 assert sha(job['module_path'])==job['module_sha256'];kwargs=job['kwargs'];assert kwargs['simu_time']==1000 and kwargs['num_agents']==64 and kwargs['seed']==930301 and kwargs['num_tasks']==64*1002 and kwargs['gen_tasks'] is False and kwargs['num_tasks_reveal']==1 and kwargs['task_assignment_strategy']=='roundrobin_fixed'
 x=read(d/'trace.json');result=read(d/'job.result.json')['result'];assert x['AllValid']=='Yes' and not x['errors'] and x['teamSize']==64 and x['makespan']==1000
 starts,streams,grid=data[row['map']];assert [32*r+c for r,c,*_ in x['start']]==starts
 moves={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1),'W':(0,0)};paths=[]
 for start,raw in zip(x['start'],x['actualPaths']):
  actions=raw.split(',');assert len(actions)==1000;pos=tuple(start[:2]);path=[pos]
  for action in actions:
   dy,dx=moves[action];pos=(pos[0]+dy,pos[1]+dx);assert 0<=pos[0]<32 and 0<=pos[1]<32 and grid[pos[0]][pos[1]] not in '@T';path.append(pos)
  paths.append(path)
 assert len(paths)==64
 for tick in range(1001):
  assert len({path[tick] for path in paths})==64
  if tick:
   old={path[tick-1]:a for a,path in enumerate(paths)}
   for a,path in enumerate(paths):
    b=old.get(path[tick]);assert b is None or b==a or paths[b][tick]!=path[tick-1]
 definitions={};counts=Counter()
 for tid,r,c in x['tasks']:
  owner,index=divmod(tid,1002);goal=32*r+c;assert 0<=owner<64 and 0<=index<1002 and goal==streams[owner][index]
  assert tid not in definitions or definitions[tid]==goal;definitions[tid]=goal;counts[tid]+=1
 assert len(definitions)==64*1002 and set(counts.values())<={1,2}
 assigned=set();finished=set();prefixes=[];per_agent=[];min_unrevealed=1002
 assert len(x['events'])==64
 for owner,events in enumerate(x['events']):
  queue=deque();last=-1;index=0;done=0
  for tid,tick,kind in events:
   assert last<=tick<=1000;last=tick
   if kind=='assigned':
    assert not queue and tid not in assigned and tid==owner*1002+index;assigned.add(tid);queue.append(tid);index+=1
   elif kind=='finished':
    assert queue and queue.popleft()==tid and tid not in finished and paths[owner][tick]==divmod(definitions[tid],32);finished.add(tid);done+=1
   else:raise AssertionError(kind)
  assert len(queue)==1 and index==done+1;prefixes.append(index);per_agent.append(done);min_unrevealed=min(min_unrevealed,1002-index)
 assert min_unrevealed>0 and {tid for tid,count in counts.items() if count==2}==assigned
 assert len(finished)==x['numTaskFinished'] and len(assigned)==len(finished)+64 and result['throughput']==row['throughput']==len(finished)/1000
 return {'passed':True,'actions_replayed':64000,'joint_positions_replayed':64064,'finished_tasks':len(finished),'throughput':len(finished)/1000,'pending_tasks':64,'finished_by_agent':per_agent,'assignment_prefix_lengths':prefixes,'min_unrevealed_tasks_per_agent':min_unrevealed,'duplicate_definitions_matching_reveals':len(assigned),'trace_sha256':sha(d/'trace.json')}
def main():
 freeze=read(HERE/'freeze.json')
 for p,h in freeze['pins'].items():assert sha(p)==h,p
 data=inputs_check(freeze);rows=read(HERE/'results.json');assert len(rows)==8 and {(r['map'],r['policy']) for r in rows}=={(n,p) for n in NAMES for p in ['hm_GPIBT','trained']}
 audits={}
 for row in rows:
  try:audits[row['label']]=trace_check(row,data)
  except Exception as e:audits[row['label']]={'passed':False,'error':str(e),'exception':type(e).__name__,'returncode':row['returncode'],'timed_out':row['timed_out']}
 paired=[]
 for name in NAMES:
  a,b=[next(r for r in rows if r['map']==name and r['policy']==p) for p in ['hm_GPIBT','trained']];ja,jb=[read(Path(r['work'])/'job.json') for r in [a,b]];ka,kb=ja['kwargs'].copy(),jb['kwargs'].copy()
  for kw in [ka,kb]:kw.pop('network_params');kw.pop('save_path')
  assert ka==kb
  valid=audits[a['label']]['passed'] and audits[b['label']]['passed']
  paired.append({'map':name,'hm_GPIBT':a.get('throughput'),'trained':b.get('throughput'),'trained_minus_hm':b['throughput']-a['throughput'] if valid else None,'both_native_and_trace_passed':valid,'identical_complete_future_task_input':True})
 helper=load('standard_source_audit_final',HERE.parent/'published_guidance_comparison_20260930_r4/run.py');source=helper.source_audit();assert source==freeze['source_before']
 write(HERE/'audit.json',{'passed':all(a['passed'] for a in audits.values()),'source_after':source,'all_inputs_regenerated':True,'frozen_pins_unchanged':True,'trace_audits':audits,'total_actions_replayed':sum(a.get('actions_replayed',0) for a in audits.values()),'total_joint_positions_replayed':sum(a.get('joint_positions_replayed',0) for a in audits.values()),'verifier_sha256':sha(HERE/'verify.py')})
 summary={'maps':paired,'native_runs':8,'native_failures':sum(r['returncode']!=0 or r['timed_out'] for r in rows),'audit_failures':sum(not a['passed'] for a in audits.values()),'agents':64,'steps':1000,'seed':930301,'checkpoint_sha256':freeze['checkpoint_sha256'],'new_training':False,'same_per_agent_exogenous_task_stream':True,'planner_tie_randomness_paired':False,'unchanged_published_native_algorithms':True,'checkpoint_domain':'sortation_small_kiva 200 candidate finite training','pilot_kind':'official-map workload transfer of frozen published model and hm comparator','full_author_benchmark':False,'statistical_superiority_established':False,'execution_error_test':False,'new_method_tested':False}
 write(HERE/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
