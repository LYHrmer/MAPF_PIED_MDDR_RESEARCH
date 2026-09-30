"""Eight predetermined official-map native runs; no source edits or new optimizer."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,importlib.util,json,random,subprocess,sys,time,zipfile
from collections import deque
HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/HERE.name
PAIR=MAIN/'paired_published_guidance_20260930_r5'
REGISTER=HERE.parent/'mapf_evaluation_20260930_r5'
R3=HERE.parent/'onlineggo_training_20260930_r3'
R4=HERE.parent/'published_guidance_comparison_20260930_r4'
MAPS=['empty-32-32','random-32-32-10','maze-32-32-2','room-32-32-4']
SEED=930301;N=64;H=1000;TASKS=1002
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def component(grid,start):
 seen={start};todo=deque([start]);width=len(grid[0]);height=len(grid)
 while todo:
  v=todo.popleft();y,x=divmod(v,width)
  for ny,nx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
   u=ny*width+nx
   if 0<=ny<height and 0<=nx<width and grid[ny][nx] not in '@T' and u not in seen:seen.add(u);todo.append(u)
 return sorted(seen)
def main():
 assert not RAW.exists() and not (HERE/'freeze.json').exists(),'Never overwrite attempts'
 RAW.mkdir();inp=RAW/'inputs';inp.mkdir();registered=read(REGISTER/'registry.json')
 helper=load('standard_source_audit',R4/'run.py');source=helper.source_audit();assert source['unchanged_tracked_blobs']==939
 inputs=[]
 with zipfile.ZipFile(REGISTER/'original_archives/mapf-map.zip') as archive:
  for name in MAPS:
   mp=inp/(name+'.map');mp.write_bytes(archive.read(name+'.map'));assert sha(mp)==registered['maps'][name]['map_sha256']
   with zipfile.ZipFile(REGISTER/'original_archives'/(name+'.map-scen-random.zip')) as scenarios:
    scenario=inp/(name+'-random-1.scen');scenario.write_bytes(scenarios.read('scen-random/'+name+'-random-1.scen'))
   assert sha(scenario)==registered['maps'][name]['scenarios'][0]['sha256']
   grid=mp.read_text().splitlines()[4:];width=len(grid[0]);starts=[];streams=[];free_by_component={}
   for agent,line in enumerate(scenario.read_text().splitlines()[1:N+1]):
    p=line.split();sx,sy,gx,gy=map(int,p[4:8]);start=sy*width+sx;first=gy*width+gx;starts.append(start)
    cells=free_by_component.get(start)
    if cells is None:
     cells=component(grid,start)
     for cell in cells:free_by_component[cell]=cells
    assert first in cells and len(cells)>1
    indices={cell:i for i,cell in enumerate(cells)};rng=random.Random(f'standard-map-r5:{SEED}:{name}:{agent}');seq=[first]
    while len(seq)<TASKS:
     chosen=rng.randrange(len(cells)-1);skip=indices[seq[-1]];seq.append(cells[chosen+int(chosen>=skip)])
    streams.append(seq)
   assert len(starts)==len(set(starts))==N
   agents=inp/(name+'.agents');tasks=inp/(name+'.tasks');config=inp/(name+'.json')
   agents.write_text(str(N)+'\n'+'\n'.join(map(str,starts))+'\n')
   flat=[streams[a][i] for i in range(TASKS) for a in range(N)];tasks.write_text(str(len(flat))+'\n'+'\n'.join(map(str,flat))+'\n')
   write(config,{'mapFile':mp.name,'teamSize':N,'agentFile':agents.name,'taskFile':tasks.name,'taskAssignmentStrategy':'roundrobin_fixed','numTasksReveal':1})
   inputs.append({'map':name,'instance':str(config),'scenario':str(scenario),'map_path':str(mp),'agents':N,'tasks_per_agent':TASKS,'seed':SEED,'map_sha256':sha(mp),'scenario_sha256':sha(scenario)})
 jobs=[]
 for item in inputs:
  for policy in ['hm_GPIBT','trained']:
   template=PAIR/f'{policy}_930101/job.json';job=read(template);label=item['map']+'_'+policy;work=RAW/label;work.mkdir()
   job.update(label=label,map_sha256=item['map_sha256'],template_job_sha256=sha(template))
   job['kwargs'].update(map_path=item['map_path'],all_json_path=item['instance'],num_agents=N,num_tasks=N*TASKS,seed=SEED,gen_tasks=False,task_assignment_strategy='roundrobin_fixed',num_tasks_reveal=1,simu_time=H,save_path=str(work/'trace.json'))
   job['config']={k:v for k,v in job['kwargs'].items() if k not in ('network_params','save_path')}
   assert sha(job['module_path'])==job['module_sha256']
   if policy=='trained':assert json.loads(job['kwargs']['network_params'])==read(R3/'training_02/trained_checkpoint.json')['parameters']
   write(work/'job.json',job);jobs.append({'label':label,'map':item['map'],'policy':policy,'work':str(work)})
 pins={str(p):sha(p) for p in [HERE/'PROTOCOL.md',HERE/'run.py',HERE/'verify.py',HERE/'archive.py',R3/'native_worker.py',R3/'training_02/trained_checkpoint.json',R3/'training_02/freeze.json',REGISTER/'registry.json',R4/'build.json',HERE.parent/'paired_published_guidance_20260930_r5/freeze.json']}
 for p in inp.iterdir():pins[str(p)]=sha(p)
 for job in jobs:
  path=Path(job['work'])/'job.json';pins[str(path)]=sha(path);j=read(path);pins[j['module_path']]=sha(j['module_path'])
 write(HERE/'freeze.json',{'utc':datetime.now(timezone.utc).isoformat(),'pins':pins,'jobs':jobs,'inputs':inputs,'source_before':source,'native_seed':SEED,'agents':N,'horizon':H,'tasks_per_agent':TASKS,'new_training':False,'source_changed':False,'checkpoint_sha256':sha(R3/'training_02/trained_checkpoint.json')})
 results=[]
 for job in jobs:
  work=Path(job['work']);argv=['rtk','proxy','timeout','--kill-after=5s','120s',sys.executable,str(R3/'native_worker.py'),str(work/'job.json')];start=time.monotonic()
  with (work/'stdout.log').open('w') as out,(work/'stderr.log').open('w') as err:
   try:p=subprocess.run(argv,cwd=work,stdout=out,stderr=err,timeout=130);code=p.returncode;expired=False
   except subprocess.TimeoutExpired:code=None;expired=True
  receipt={'argv':argv,'cwd':str(work),'returncode':code,'timed_out':expired,'elapsed_seconds':time.monotonic()-start,'job_sha256':sha(work/'job.json'),'stdout_sha256':sha(work/'stdout.log'),'stderr_sha256':sha(work/'stderr.log')};write(work/'receipt.json',receipt)
  row={**job,**receipt}
  if code==0 and (work/'job.result.json').exists():
   row.update(throughput=read(work/'job.result.json')['result']['throughput'],result_sha256=sha(work/'job.result.json'))
   if (work/'trace.json').exists():row['trace_sha256']=sha(work/'trace.json')
  results.append(row);write(HERE/'results.json',results);print(json.dumps({k:row.get(k) for k in ['map','policy','returncode','throughput','elapsed_seconds']}),flush=True)
 for p,h in pins.items():assert sha(p)==h,p
 assert helper.source_audit()==source
 load('standard_trace_verifier',HERE/'verify.py').main()
if __name__=='__main__':main()
