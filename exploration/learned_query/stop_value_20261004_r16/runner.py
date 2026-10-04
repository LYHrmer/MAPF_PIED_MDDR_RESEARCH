"""R16 isolated complete STOP tails; exact input reuse with distinct provenance."""
from pathlib import Path
import importlib.util, hashlib, json, subprocess, time
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'late_budget_choice_20261004_r13'
spec=importlib.util.spec_from_file_location('r13_runner',OLD/'runner.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
BRIDGE=prior.BRIDGE;CONFIG=prior.CONFIG
sha=prior.sha;render=prior.render;write=prior.write
def compile_native():
 prior.HERE=HERE
 return prior.compile_native()
def cached_c(w):
 p=OLD/'runs'/(w['name']+'__macro_C.receipt.json')
 e=json.loads(p.read_text());assert e['error'] is None and e['policy']=='macro_C'
 assert e['world']==w['name'] and e['capacity']==w['budget']
 assert e['native_source_sha256']==sha(OLD/'joint_history_native.cpp')
 assert e['binary_sha256']==sha(OLD/'build/joint_history_native')
 assert e['bridge_sha256']==sha(BRIDGE) and e['config_sha256']==sha(CONFIG)
 assert e['registration_sha256']==sha(OLD/'REGISTRATION.json')
 assert Path(e['input']).read_text()==render(w)
 for k in ['input','raw','planner']:assert sha(e[k])==e[k+'_sha256']
 return e
def native(w,policy,stage):
 assert w['split']!='test'
 reg=json.loads((HERE/'REGISTRATION.json').read_text())
 for name,h in reg['frozen'].items():assert sha(HERE/name)==h,name
 assert sha(HERE/'build/joint_history_native')==reg['binary_sha256']
 out=HERE/'runs';out.mkdir(exist_ok=True);stem=w['name']+'__'+policy
 receipt=out/(stem+'.receipt.json');assert not receipt.exists(),'never rerun a finished arm'
 started=time.time_ns();assert started>reg['frozen_unix_ns']
 model_hash=None
 if stage=='CAL':
  model=json.loads((HERE/'MODEL_FROZEN.json').read_text());assert model['frozen_unix_ns']<started and model['activated'];model_hash=sha(HERE/'MODEL_FROZEN.json')
 inp=out/(stem+'.input.txt');inp.write_text(render(w));raw=out/(stem+'.jsonl');planner=out/(stem+'.planner.jsonl')
 ps=[];errors=[];start=time.monotonic();summary=None;error=None
 try:
  for label,args in [('native',[str(HERE/'build/joint_history_native'),str(inp),policy,str(w['budget'])]),('official',[str(BRIDGE),str(CONFIG)])]:
   err=(out/(stem+'.'+label+'.stderr')).open('w');errors.append(err)
   ps.append(subprocess.Popen(['rtk','proxy',*args],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1))
  with raw.open('w') as f,planner.open('w') as pf:
   while True:
    if time.monotonic()-start>900:raise TimeoutError('whole native 900s timeout')
    line=ps[0].stdout.readline()
    if not line:break
    f.write(line);r=json.loads(line)
    if r['event']=='planner_request':
     req=dict(mapf_instance=dict(starts=[dict(location=x) for x in r['starts']],goals=[[g] for g in r['goals']]),rows=w['rows'],cols=w['cols'],map_name=w['map_name'],map=[int(c=='@') for row in w['layout'] for c in row])
     ps[1].stdin.write(json.dumps(req)+'\n');ps[1].stdin.flush();reply=json.loads(prior.read_line(ps[1]));assert reply['objective']==3 and len(reply['actions'])==w['N']
     for location,action in zip(r['starts'],reply['actions']):
      x,y=location%w['cols'],location//w['cols'];dx,dy=[(1,0),(0,1),(-1,0),(0,-1),(0,0)][action]
      assert 0<=x+dx<w['cols'] and 0<=y+dy<w['rows'] and w['layout'][y+dy][x+dx]=='.'
     pf.write(json.dumps(dict(request=r,result=reply))+'\n');ps[0].stdin.write(' '.join(map(str,reply['actions']))+'\n');ps[0].stdin.flush()
    elif r['event']=='joint_summary':summary=r;break
  code=ps[0].wait(timeout=3);assert code==0 and summary
 except Exception as exc:error=repr(exc)
 finally:
  for p in ps:
   if p.poll() is None:p.terminate()
   try:p.wait(timeout=2)
   except subprocess.TimeoutExpired:p.kill();p.wait()
  for f in errors:f.close()
 e=dict(world=w['name'],policy=policy,capacity=w['budget'],stage=stage,summary=summary,error=error,seconds=time.monotonic()-start,started_unix_ns=started,finished_unix_ns=time.time_ns(),registration_sha256=sha(HERE/'REGISTRATION.json'),model_frozen_sha256=model_hash,raw=str(raw),planner=str(planner),input=str(inp),native_source_sha256=sha(HERE/'joint_history_native.cpp'),binary_sha256=sha(HERE/'build/joint_history_native'),bridge_sha256=sha(BRIDGE),config_sha256=sha(CONFIG),native_stderr=(out/(stem+'.native.stderr')).read_text(),official_stderr=(out/(stem+'.official.stderr')).read_text()[-2000:])
 for k in ['input','raw','planner']:e[k+'_sha256']=sha(e[k])
 write(receipt,e)
 print(w['name'],policy,'error',error,'tasks',summary and summary['served'],'queries',summary and summary['queries'],'seconds',round(e['seconds'],2),flush=True)
 return e
