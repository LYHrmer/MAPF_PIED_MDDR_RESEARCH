"""Bounded original GPIBT pilot; fixed author inputs and seeds, no learning arm."""
import argparse,csv,hashlib,json,os,re,shutil,signal,subprocess,time,statistics
from pathlib import Path
from datetime import datetime,timezone
from validator import validate
COMMIT='7f4b91e4ed134229710945a4670a78639cf008d5'
CONFIG=[('n10_s42','visualizer_example_sts.json',10,42),('n10_s43','visualizer_example_sts.json',10,43),('n200_s42','sortation_small_0_200.json',200,42),('n200_s43','sortation_small_0_200.json',200,43)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['rtk','proxy','git','-C',str(root),*args],text=True).strip()
def ints(p):
 a=list(map(int,p.read_text().split()));assert a[0]==len(a)-1;return a[1:]
def log_events(p):
 events=[]
 for line in p.read_text().splitlines():
  m=re.search(r'\[timestep=(\d+)\] Task (\d+) is assigned to agent (\d+)',line)
  if m:
   t,tid,a=map(int,m.groups());events.append((t,'assigned',a,tid))
  m=re.search(r'\[timestep=(\d+)\] Agent (\d+) finishes task (\d+)',line)
  if m:
   t,a,tid=map(int,m.groups());events.append((t,'finished',a,tid))
 return events
def run_command(argv,cwd,dest):
 rec={'argv':argv,'cwd':str(cwd),'timeout_seconds':60,'started_utc':datetime.now(timezone.utc).isoformat(),'reused':False};start=time.monotonic()
 with (dest/'stdout.log').open('w') as so,(dest/'stderr.log').open('w') as se:
  proc=subprocess.Popen(argv,cwd=cwd,stdout=so,stderr=se,start_new_session=True)
  try:rec['exit_code']=proc.wait(timeout=60)
  except subprocess.TimeoutExpired:
   rec['timed_out']=True;os.killpg(proc.pid,signal.SIGKILL);rec['exit_code']=proc.wait()
 rec['elapsed_seconds']=time.monotonic()-start
 for name in ['stdout.log','stderr.log']:rec[name+'_sha256']=sha(dest/name)
 (dest/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');return rec

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--author-root',required=True,type=Path);p.add_argument('--seeded-root',required=True,type=Path);p.add_argument('--binary',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--reuse-r0-dir',type=Path);a=p.parse_args()
 author=a.author_root.resolve();seeded=a.seeded_root.resolve();binary=a.binary.resolve();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 assert git(author,'rev-parse','HEAD')==COMMIT and git(author,'status','--porcelain','--untracked-files=no')==''
 changes=[x for x in git(author,'ls-files','guided-pibt').splitlines() if sha(author/x)!=sha(seeded/x)]
 assert changes==['guided-pibt/src/CompetitionSystem.cpp','guided-pibt/src/MAPFPlanner.cpp'],changes
 assert sha(seeded/'guided-pibt/src/MAPFPlanner.cpp')=='bc24e208bcae48465f9e1199afc822e67a39de2f90a57fbcd9128448cda5967d'
 assert sha(seeded/'guided-pibt/src/CompetitionSystem.cpp')=='e237341fde70f951a5a941410fc4d5cc160e37812f1ca90473ed8a7b6c8819f1'
 flags=(binary.parent/'CMakeFiles/lifelong.dir/flags.make').read_text();assert '-DMAPFT' not in flags
 for f in ['-DGUIDANCE','-DGUIDANCE_LNS=10','-DINIT_PP','-DRELAX=100','-DOBJECTIVE=1','-DFOCAL_SEARCH=2']:assert f in flags
 source=author/'guided-pibt/benchmark-lifelong';configs=[json.loads((source/n).read_text()) for n in ['visualizer_example_sts.json','sortation_small_0_200.json']]
 assert {k:v for k,v in configs[0].items() if k!='teamSize'}=={k:v for k,v in configs[1].items() if k!='teamSize'}
 ml=(source/configs[0]['mapFile']).read_text().splitlines();grid=ml[4:];height=int(ml[1].split()[1]);width=int(ml[2].split()[1]);assert len(grid)==height and all(len(s)==width for s in grid)
 free={r*width+c for r in range(height) for c in range(width) if grid[r][c] not in '@T'}
 all_starts=ints(source/configs[0]['agentFile']);task_source=ints(source/configs[0]['taskFile']);assert set(all_starts)<=free and set(task_source)<=free and len(set(all_starts))==len(all_starts)
 manifest={'upstream_commit':COMMIT,'seed_adapter':True,'observer_adapter':True,'solver_variant':'GP-R100-Re10-F2','motion_mode':'nonrotation','fixed_cases':CONFIG,'binary_sha256':sha(binary),'source_changes':changes,'source_sha256':{x:sha(seeded/x) for x in changes},'author_input_sha256':{x:sha(source/x) for x in ['visualizer_example_sts.json','sortation_small_0_200.json',configs[0]['mapFile'],configs[0]['agentFile'],configs[0]['taskFile']]},'map_height':height,'map_width':width,'free_cells':len(free),'task_source_count':len(task_source),'horizon':450,'planning_limit_seconds':10,'process_limit_seconds':60,'planned_new_runs':3 if a.reuse_r0_dir else 4,'paper_performance_benchmark':False,'learned_method_executed':False,'continuous_error_adapter_executed':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');rows=[]
 for name,filename,n,seed in CONFIG:
  dest=out/name;dest.mkdir();row={'case':name,'author_input':filename,'agents':n,'seed':seed,'horizon':450,'process_limit_seconds':60,'status':'failed_or_incomplete'}
  try:
   if name=='n10_s42' and a.reuse_r0_dir:
    reuse=a.reuse_r0_dir.resolve();known=json.loads((reuse/'gpibt_seeded_verification_01.json').read_text());assert known['status']=='passed' and known['explicit_seed']==42
    assert known['sha256']['gpibt_seeded_build_gp_r100_re10_f2/lifelong']==sha(binary)
    for original,target in [('gpibt_seeded_result_01.json','result.json'),('gpibt_seeded_event_log_01.txt','event_log.txt')]:
     assert known['sha256'][original]==sha(reuse/original);shutil.copy2(reuse/original,dest/target)
    for file in ['stdout.log','stderr.log','receipt.json']:shutil.copy2(reuse/'gpibt_seeded_run_01'/file,dest/('origin_receipt.json' if file=='receipt.json' else file))
    rec=json.loads((dest/'origin_receipt.json').read_text());assert rec['exit_code']==0 and 'GPIBT_R0_SEED=42' in rec['argv']
    for log in ['stdout.log','stderr.log']:assert rec[log+'_sha256']==sha(dest/log)
    rec=dict(rec,reused=True,reused_origin=str(reuse/'gpibt_seeded_run_01'));(dest/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
   else:
    argv=['rtk','proxy','env',f'GPIBT_R0_SEED={seed}',str(binary),'--inputFile',str(source/filename),'--planTimeLimit','10','--output',str(dest/'result.json'),'-l',str(dest/'event_log.txt')]
    rec=run_command(argv,seeded,dest)
   row.update(wall_seconds=rec['elapsed_seconds'],exit_code=rec['exit_code'],reused=rec['reused'],timed_out=rec.get('timed_out',False))
   if rec['exit_code']!=0:raise RuntimeError('native process did not complete successfully')
   data=json.loads((dest/'result.json').read_text());checked=validate(grid,all_starts,task_source,data,n,450)
   assert checked.pop('event_stream')==log_events(dest/'event_log.txt')
   stdout=(dest/'stdout.log').read_text();assert re.findall(r'^---priority-initialization-seed,(\d+)$',stdout,re.M)==[str(seed)]
   perstep=list(map(int,re.findall(r'^---timestep-task-finished,(\d+)$',stdout,re.M)))
   assert len(perstep)==450 and [0]+[sum(perstep[:i+1]) for i in range(450)]==checked['cumulative_completed_tasks']
   times=data['plannerTimes'];checked.update(planner_seconds_sum=sum(times),planner_seconds_max=max(times),planner_seconds_median=statistics.median(times),planner_seconds_count=len(times))
   checked['artifact_sha256']={p.name:sha(p) for p in dest.iterdir() if p.is_file()}
   (dest/'verification.json').write_text(json.dumps(checked,indent=2)+'\n')
   row.update({k:v for k,v in checked.items() if k not in ['cumulative_completed_tasks','action_counts','artifact_sha256']});row['status']='passed'
  except Exception as exc:row['failure']=f'{type(exc).__name__}: {exc}';(dest/'failure.json').write_text(json.dumps(row,indent=2)+'\n')
  rows.append(row);(out/'summary.json').write_text(json.dumps({'status':'running' if len(rows)<4 else ('passed' if all(r['status']=='passed' for r in rows) else 'failed_or_incomplete'),'cases':rows,'new_native_runs':sum(not r.get('reused',False) for r in rows),'new_native_wall_seconds':sum(r.get('wall_seconds',0) for r in rows if not r.get('reused',False))},indent=2)+'\n')
  print(json.dumps(row),flush=True)
 fields=sorted(set().union(*(r.keys() for r in rows)))
 with (out/'summary.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
 if not all(r['status']=='passed' for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
