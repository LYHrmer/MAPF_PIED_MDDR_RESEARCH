"""Fixed R12 registration, bounded native execution and phase pins."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,os,time,threading,sys
import runner
P=runner.HERE;OUT=P/'runs';OPTIONS=['C','W','E','L','ED','LD'];TEST_POLICIES=['WAIT','condition','budget_lookup','full','nohistory','nobudget','tasks_only']
def worlds():
 out=[]
 for mi,name in enumerate(['empty-32-32','random-32-32-10']):
  scenario=P/'inputs'/(name+'-random-2.scen');base=121000+mi*1000
  for j,(split,tail) in enumerate([('train',101),('train',102),('train',103),('calibration',201),('test',301),('test',302)]):
   offset=16*j+(32 if mi else 0);seed=base+tail;family=f'{name}_scen2_offset{offset}_{split}_{seed}'
   for budget in [8,16]:
    w=runner.make_world(family+'_B'+str(budget),16,seed,H=128,offset=offset,map_name=name,scenario_file=scenario);w.update(split=split,budget=budget,scenario_offset=offset,scenario_identity=scenario.name,scenario_sha256=runner.sha(scenario),family_key=family);out.append(w)
 return out
def preflight(ws):
 old_seeds=set();old_tasks=set();old_rows=set();old_sequences=[];sources=[]
 def walk(o):
  if isinstance(o,dict):
   if isinstance(o.get('seed'),int):old_seeds.add(o['seed'])
   if isinstance(o.get('task'),int):old_tasks.add(o['task'])
   if 'robots' in o and isinstance(o['robots'],list) and o['robots'] and all(isinstance(a,dict) and 'start' in a for a in o['robots']):
    old_sequences.append((o.get('map_name','empty-32-32'),[tuple(a['start']) for a in o['robots']]))
    if 'scenario_offset' in o:
     scenario=o.get('scenario_identity',o.get('map_name','empty-32-32')+'-random-1.scen');old_rows.update((scenario,i) for i in range(o['scenario_offset'],o['scenario_offset']+len(o['robots'])))
   for v in o.values():walk(v)
  elif isinstance(o,list):
   for v in o:walk(v)
 for directory in P.parent.iterdir():
  if not directory.is_dir() or directory==P:continue
  for file in directory.glob('**/*REGISTRATION*.json'):
   if 'runs' in file.parts:continue
   walk(json.loads(file.read_text()));sources.append(dict(path=str(file),sha256=runner.sha(file)))
 assert not old_seeds&{w['seed'] for w in ws}
 assert not old_tasks&{t['task'] for w in ws for a in w['robots'] for t in a['tasks']}
 checked=[]
 for w in ws:
  assert not old_rows&{(w['scenario_identity'],i) for i in range(w['scenario_offset'],w['scenario_offset']+16)}
  assert (w['map_name'],[tuple(a['start']) for a in w['robots']]) not in old_sequences
  free={(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='.'};blocked={(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='@'}
  assert len({tuple(a['start']) for a in w['robots']})==16 and all(tuple(a['start']) in free and all(tuple(t['goal']) in free for t in a['tasks']) for a in w['robots'])
  edges=0
  for x,y in free:
   for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
    if (x+dx,y+dy) not in free:continue
    xl,xh=20*min(x,x+dx)-3,20*max(x,x+dx)+3;yl,yh=20*min(y,y+dy)-3,20*max(y,y+dy)+3
    assert all(xh<20*bx-10 or 20*bx+10<xl or yh<20*by-10 or 20*by+10<yl for bx,by in blocked);edges+=1
  checked.append(dict(world=w['name'],free=len(free),blocked=len(blocked),directed_free_edges=edges))
 for family in {w['family_key'] for w in ws}:
  pair=[w for w in ws if w['family_key']==family];assert len(pair)==2 and pair[0]['robots']==pair[1]['robots'] and pair[0]['seed']==pair[1]['seed']
 runner.write(P/'INPUT_PREFLIGHT.json',dict(passed=True,prior_sources=sources,old_seed_count=len(old_seeds),new_family_count=len({w['family_key'] for w in ws}),new_seeds=sorted({w['seed'] for w in ws}),scenario_rows_novel=True,paired_budgets_share_world=True,map_checks=checked))
def frozen_check():
 reg=json.loads((P/'REGISTRATION.json').read_text())
 for name,digest in reg['frozen'].items():assert runner.sha(P/name)==digest,('frozen source changed',name)
 for path,digest in [(P/'build/joint_history_native',reg['binary_sha256']),(runner.BRIDGE,reg['bridge_sha256']),(runner.CONFIG,reg['config_sha256'])]:assert runner.sha(path)==digest
 return reg
def batch(jobs,tag,models=None):
 start=time.monotonic();started=time.time_ns();stop=threading.Event();peak=dict(rss_bytes=0,processes=0,samples=0)
 def monitor():
  while not stop.is_set():
   ps={}
   for entry in Path('/proc').iterdir():
    if not entry.name.isdigit():continue
    try:
     f=(entry/'stat').read_text().split();ps[int(entry.name)]=(int(f[3]),int(f[23])*os.sysconf('SC_PAGE_SIZE'))
    except (OSError,ValueError,IndexError):continue
   ids={os.getpid()}
   while True:
    found=ids|{pid for pid,(parent,rss) in ps.items() if parent in ids}
    if found==ids:break
    ids=found
   peak['rss_bytes']=max(peak['rss_bytes'],sum(ps[i][1] for i in ids if i in ps));peak['processes']=max(peak['processes'],len(ids));peak['samples']+=1;stop.wait(1)
 worker=threading.Thread(target=monitor,daemon=True);worker.start();results=[]
 try:
  with ThreadPoolExecutor(max_workers=6) as pool:
   for f in as_completed([pool.submit(runner.native,w,policy,OUT,models) for w,policy in jobs]):results.append(f.result())
 finally:stop.set();worker.join()
 runner.write(P/(tag+'_SCHEDULING.json'),dict(workers=6,jobs=len(jobs),started_unix_ns=started,finished_unix_ns=time.time_ns(),seconds=time.monotonic()-start,descendant_peak=peak,failed=sum(e['error'] is not None for e in results)))
 return results
def register():
 ws=worlds();preflight(ws);compile_receipts=list((P/'build').glob('compile*.json'));assert compile_receipts
 assert json.loads(compile_receipts[-1].read_text())['source_sha256']==runner.sha(P/'joint_history_native.cpp')
 source=['ROOT_PROTOCOL.md','CONTRACT.md','joint_history_native.cpp','macro_choose.inc','macro_audit.py','runner.py','pipeline.py','learn.py','prefix_audit.py','audit.py','audit_reference.py','audit_all.py']
 runner.write(P/'REGISTRATION.json',dict(frozen_unix_ns=time.time_ns(),worlds=ws,frozen={n:runner.sha(P/n) for n in source},binary_sha256=runner.sha(P/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),options=OPTIONS,test_policies=TEST_POLICIES,TRAIN_CAL_episodes=96,TEST_episodes=56,total_native_episodes=152,native_workers=6,audit_workers=2))
 runner.write(P/'COMPILE_RECEIPT.json',dict(attempts=[json.loads(p.read_text()) for p in sorted(compile_receipts)],binary_sha256=runner.sha(P/'build/joint_history_native')))
def main():
 phase=sys.argv[1]
 if phase=='register':register();return
 reg=frozen_check();ws=reg['worlds']
 if phase=='tc':
  jobs=[(w,'macro_'+o) for w in ws if w['split']!='test' for o in OPTIONS];assert len(jobs)==96
  if not (P/'TC_START.json').exists():runner.write(P/'TC_START.json',dict(unix_time_ns=time.time_ns(),registration_sha256=runner.sha(P/'REGISTRATION.json'),jobs=[dict(world=w['name'],policy=p) for w,p in jobs]))
  result=batch(jobs,'TC');runner.write(P/'TC_RECEIPT.json',dict(complete=True,native_episodes=len(result),failed=sum(e['error'] is not None for e in result),finished_unix_ns=time.time_ns()));return
 if phase=='test':
  frozen=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text());freeze=json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text());assert freeze['model_sha256']==runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json')
  jobs=[(w,p) for w in ws if w['split']=='test' for p in TEST_POLICIES];assert len(jobs)==56
  if not (P/'TEST_START.json').exists():runner.write(P/'TEST_START.json',dict(unix_time_ns=time.time_ns(),registration_sha256=runner.sha(P/'REGISTRATION.json'),model_sha256=freeze['model_sha256'],model_freeze_sha256=runner.sha(P/'MODEL_FREEZE_RECEIPT.json'),jobs=[dict(world=w['name'],policy=p) for w,p in jobs]))
  result=batch(jobs,'TEST',frozen['parameters']);es=[json.loads(p.read_text()) for p in OUT.glob('*.receipt.json')];runner.write(P/'RECEIPT.json',dict(complete=True,native_episodes=len(es),failed=sum(e['error'] is not None for e in es),finished_unix_ns=time.time_ns()));return
 raise ValueError(phase)
if __name__=='__main__':main()
