from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,time,random,selectors,os
HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
THIRD=Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c')
BRIDGE=MAIN/'implementation_binding_evidence/published_continuous_execution_20261001_r6c/bridge_hm_GPIBT'
CONFIG=THIRD/'hm_GPIBT_config.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
def compile_native():
 out=HERE/'build';out.mkdir(exist_ok=True);pins=json.loads((HERE.parent.parent/'legal_and_sources.json').read_text())
 assert all(sha(MAIN/p)==h for p,h in pins.items())
 with tempfile.TemporaryDirectory(prefix='query-r7-') as tmp:
  inc=Path(tmp)
  for p in pins:shutil.copy2(MAIN/p,inc/Path(p).name)
  lib=MAIN/'third_party/flint_host_config';sdk=MAIN/'third_party/host_sdk/usr'
  cmd=['rtk','proxy','g++-11','-std=c++14','-O2','-Wall','-Wextra','-Werror','-pedantic','-fno-elide-constructors','-I',str(inc),'-I',str(HERE.parent),'-isystem',str(sdk/'include'),'-isystem',str(lib/'src'),str(HERE/'joint_history_native.cpp'),'-L',str(lib),'-L',str(sdk/'lib/x86_64-linux-gnu'),'-Wl,-rpath,'+str(lib),'-lflint','-lmpfr','-lgmp','-o',str(out/'joint_history_native')]
  start=time.monotonic();r=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
  attempt=len(list(out.glob('compile*.json')))+1;write(out/f'compile{attempt:02d}.json',dict(command=cmd,returncode=r.returncode,stderr=r.stderr,stdout=r.stdout,seconds=time.monotonic()-start,source_sha256=sha(HERE/'joint_history_native.cpp')))
  assert r.returncode==0,r.stderr
 return out/'joint_history_native'
def make_world(name,N,seed,small=False,H=128,offset=0,shift=False,map_name='empty-32-32'):
 rows=cols=8 if small else 32;layout=['.'*cols for _ in range(rows)]
 if small:starts=[(1,1),(0,1),(1,3),(0,3)][:N]
 else:
  folder=THIRD/'inputs'/map_name
  layout=json.loads((folder/'map.json').read_text())['layout']
  scen=(folder/(map_name+'-random-1.scen')).read_text().splitlines()[1:]
  starts=[tuple(map(int,line.split()[4:6])) for line in scen[offset:offset+N]]
 assert len(set(starts))==N
 free=[(x,y) for y,row in enumerate(layout) for x,c in enumerate(row) if c=='.']
 assert all(s in free for s in starts)
 rng=random.Random(seed);robots=[]
 for a,start in enumerate(starts):
  tasks=[];previous=start
  for j in range(256):
   goal=(6-a%2,start[1]) if small and j==0 else rng.choice(free)
   while goal==previous:goal=rng.choice(free)
   tasks.append(dict(task=seed*10000+a*256+j,goal=goal));previous=goal
  robots.append(dict(agent=a,start=start,tasks=tasks))
 return dict(name=name,N=N,seed=seed,rows=rows,cols=cols,layout=layout,robots=robots,horizon=H,shift=shift,map_name=map_name,private_eta_formula='sha256 persistent 9:1 sign; shift after MOVE64')
def render(w,models=None):
 lines=[f"D {w['rows']} {w['cols']} {w['horizon']}"]
 lines.extend(f'C {x} {y}' for y in range(w['rows']) for x in range(w['cols']))
 for r in w['robots']:
  a=r['agent'];t=r['tasks'][0];lines.append(' '.join(map(str,['R',a,t['task'],*r['start'],*t['goal']])))
  lines.extend(' '.join(map(str,['F',a,t['task'],*t['goal']])) for t in r['tasks'][1:])
  theta=[-1,1][int.from_bytes(hashlib.sha256(f"{w['seed']}:{a}:theta".encode()).digest()[:8],'big')%2]
  for leg in range(1024):
   flip=int.from_bytes(hashlib.sha256(f"{w['seed']}:{a}:{leg}:flip".encode()).digest()[:8],'big')%10;e=theta if flip<9 else -theta
   if w['shift'] and leg>=64:e=-e
   lines.append(f'E {a} {leg} {e}')
 if models:
  from fractions import Fraction
  for name,m in models.items():
   for c in m['coefficients']:
    q=Fraction(c);lines.append(f'M {name} {q.numerator} {q.denominator}')
 return '\n'.join(lines)+'\n'
def read_line(p,limit=30):
 sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
 try:
  if not sel.select(limit):raise TimeoutError('subprocess line timeout')
  line=p.stdout.readline()
  if not line:raise EOFError('subprocess closed stdout')
  return line
 finally:sel.close()
def native(w,policy,out,models=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);stem=w['name']+'__'+policy;receipt=out/(stem+'.receipt.json')
 if receipt.exists():
  e=json.loads(receipt.read_text());assert e['native_source_sha256']==sha(HERE/'joint_history_native.cpp');return e
 inp=out/(stem+'.input.txt');inp.write_text(render(w,models));raw=out/(stem+'.jsonl');planner=out/(stem+'.planner.jsonl')
 cap=0 if policy=='WAIT' else 1 if policy.startswith('probe_') else 16
 cmd=[str(HERE/'build/joint_history_native'),str(inp),policy,str(cap)];ps=[];errors=[];start=time.monotonic();summary=None;error=None;decisions=[]
 try:
  for label,args in [('native',cmd),('official',[str(BRIDGE),str(CONFIG)])]:
   err=(out/(stem+'.'+label+'.stderr')).open('w');errors.append(err);ps.append(subprocess.Popen(['rtk','proxy',*args],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1))
  with raw.open('w') as f,planner.open('w') as pf:
   while True:
    if time.monotonic()-start>900:raise TimeoutError('whole native 900s timeout')
    line=ps[0].stdout.readline()
    if not line:break
    f.write(line);r=json.loads(line)
    if r['event']=='planner_request':
     req=dict(mapf_instance=dict(starts=[dict(location=x) for x in r['starts']],goals=[[g] for g in r['goals']]),rows=w['rows'],cols=w['cols'],map_name=w['map_name'],map=[int(c=='@') for row in w['layout'] for c in row])
     ps[1].stdin.write(json.dumps(req)+'\n');ps[1].stdin.flush();reply=json.loads(read_line(ps[1]));assert reply['objective']==3 and len(reply['actions'])==w['N']
     for location,action in zip(r['starts'],reply['actions']):
      x,y=location%w['cols'],location//w['cols'];dx,dy=[(1,0),(0,1),(-1,0),(0,-1),(0,0)][action]
      assert 0<=x+dx<w['cols'] and 0<=y+dy<w['rows'] and w['layout'][y+dy][x+dx]=='.','official move enters obstacle/outside map'
     pf.write(json.dumps(dict(request=r,result=reply))+'\n');ps[0].stdin.write(' '.join(map(str,reply['actions']))+'\n');ps[0].stdin.flush()
    elif r['event']=='joint_summary':summary=r
    elif r['event']=='actor_decision':decisions.append(r)
  code=ps[0].wait(timeout=3)
  assert code==0 and summary,'native failed or missing summary'
 except Exception as exc:error=repr(exc)
 finally:
  for p in ps:
   if p.poll() is None:p.terminate()
   try:p.wait(timeout=2)
   except subprocess.TimeoutExpired:p.kill();p.wait()
  for f in errors:f.close()
 e=dict(world=w['name'],policy=policy,capacity=cap,summary=summary,error=error,seconds=time.monotonic()-start,raw=str(raw),raw_sha256=sha(raw),planner=str(planner),planner_sha256=sha(planner),input=str(inp),input_sha256=sha(inp),native_source_sha256=sha(HERE/'joint_history_native.cpp'),binary_sha256=sha(HERE/'build/joint_history_native'),bridge_sha256=sha(BRIDGE),config_sha256=sha(CONFIG),native_stderr=(out/(stem+'.native.stderr')).read_text(),official_stderr=(out/(stem+'.official.stderr')).read_text()[-2000:])
 write(receipt,e);print(w['name'],policy,'error',error,'services',summary and summary['served'],'queries',summary and summary['queries'],'maxc',summary and summary['max_candidates'],'seconds',round(e['seconds'],2),flush=True)
 return e
if __name__=='__main__':
 import sys
 if sys.argv[1]=='build':compile_native()
 elif sys.argv[1]=='mechanical':
  worlds=[make_world(f'mechanical_N{N}',N,73000+N,small=N<8) for N in [2,4,8,16]];out=HERE/f'mechanical_attempt_{1+len(list(HERE.glob("mechanical_attempt_*"))):02d}'
  write(out/'REGISTRATION.json',dict(worlds=worlds,policies=['WAIT','RR','condition'],source_sha256=sha(HERE/'joint_history_native.cpp'),contract_sha256=sha(HERE/'CONTRACT.md'),bridge_sha256=sha(BRIDGE),config_sha256=sha(CONFIG)))
  for w in worlds:
   for p in ['WAIT','RR','condition']:native(w,p,out)
