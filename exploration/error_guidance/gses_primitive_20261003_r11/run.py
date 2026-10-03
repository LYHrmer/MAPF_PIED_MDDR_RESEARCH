from pathlib import Path
from fractions import Fraction as F
import argparse,datetime,gzip,hashlib,json,time,traceback
from executor import Executor
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check_unit(out,reference):
 n=out['agents'];state=list(out['graph']['current']);arrivals={}
 for e in out['events']:
  if e['kind']=='ARRIVE':arrivals.setdefault(F(e['t']),[]).append(e)
 assert F(out['makespan']).denominator==1 and all(t.denominator==1 for t in arrivals)
 states=[state.copy()]
 for t in range(1,int(F(out['makespan']))+1):
  for e in arrivals.get(F(t),[]):state[e['agent']]=e['to_state']
  states.append(state.copy())
 assert states==reference['states'],'author unit time-state mismatch'
 assert F(out['sum_completion_time'])==reference['cost'] and F(out['makespan'])==reference['ticks']
 return {'passed':True,'cost':reference['cost'],'ticks':reference['ticks'],'state_observations':len(states)*n,'recorded_states_used_as_actions':False}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--attempt',default='01');args=parser.parse_args()
 for p,v in json.loads((H/'FREEZE_01.json').read_text())['pins'].items():assert sha(p)==v,p
 specs=json.loads((H/'REGISTRATION.json').read_text())['runs'];outrows=[]
 for s in specs:
  if args.only and args.only not in s['id']:continue
  folder=O/('attempt'+args.attempt)/s['id'];folder.mkdir(parents=True,exist_ok=False);start=time.monotonic();receipt={'spec':s,'started_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':None}
  try:
   data=json.loads(gzip.decompress(Path(s['source']).read_bytes()));reference=data[s['part']];engine=Executor(reference['graph'],s['profile']);out=engine.run()
   if s['profile']=='author_unit':receipt['author_equivalence']=check_unit(out,reference)
   if s['author_status']=='Timeout' and s['part']=='selected':assert data['selected']==data['original'];receipt['author_timeout_fallback_exact']=True
   raw=folder/'trace.json';raw.write_text(json.dumps(out,separators=(',',':'))+'\n');packed=H/'raw'/('attempt'+args.attempt)/(s['id']+'.json.gz');packed.parent.mkdir(parents=True,exist_ok=True)
   with packed.open('wb') as f:
    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(raw.read_bytes())
   assert packed.stat().st_size<45000000
   receipt.update(makespan=out['makespan'],sum_completion_time=out['sum_completion_time'],events=len(out['events']),segments=len(out['segments']),raw=str(packed.relative_to(H)),raw_sha256=sha(packed),uncompressed_sha256=sha(raw),bytes=packed.stat().st_size)
  except Exception:receipt['error']=traceback.format_exc()
  receipt['wall_seconds']=time.monotonic()-start;(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');outrows.append(receipt)
  (H/('RESULTS_attempt'+args.attempt+'.json')).write_text(json.dumps(outrows,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ('spec','author_equivalence')},ensure_ascii=False),flush=True)
  if receipt['error']:raise RuntimeError(receipt['error'])
if __name__=='__main__':main()
