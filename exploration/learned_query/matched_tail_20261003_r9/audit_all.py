from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
import json,time
import runner,audit
P=runner.HERE
def check(e,w):
 if e['error'] is not None:return dict(world=e['world'],policy=e['policy'],status='execution_failed_retained',error=e['error'])
 for key in ['raw','planner','input']:assert runner.sha(e[key])==e[key+'_sha256']
 blocked=[(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='@'];moves=0
 for line in Path(e['planner']).open():
  z=json.loads(line)
  for at,a in zip(z['request']['starts'],z['result']['actions']):
   x,y=at%w['cols'],at//w['cols'];dx,dy=[(1,0),(0,1),(-1,0),(0,-1),(0,0)][a];ex,ey=x+dx,y+dy
   assert 0<=ex<w['cols'] and 0<=ey<w['rows'] and w['layout'][y][x]==w['layout'][ey][ex]=='.'
   if a==4:continue
   loX,hiX=20*min(x,ex)-3,20*max(x,ex)+3;loY,hiY=20*min(y,ey)-3,20*max(y,ey)+3
   assert all(hiX<20*bx-10 or 20*bx+10<loX or hiY<20*by-10 or 20*by+10<loY for bx,by in blocked);moves+=1
 result=audit.audit(e);result['map_verified_committed_moves']=moves;return result
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};results=[];start=time.monotonic();seen=set();pending={};cache=P/'audits';cache.mkdir(exist_ok=True)
 # Separate processes keep the independent Decimal precision at70.
 with ProcessPoolExecutor(max_workers=4) as pool:
  while True:
   for p in sorted((P/'runs').glob('*.receipt.json')):
    if p.name in seen or len(pending)>=8:continue
    try:e=json.loads(p.read_text())
    except json.JSONDecodeError:continue
    seen.add(p.name);dst=cache/(p.stem+'.audit.json')
    if dst.exists():results.append(json.loads(dst.read_text()));continue
    pending[pool.submit(check,e,worlds[e['world']])]=(e,dst)
   if pending:
    done,_=wait(pending,timeout=1,return_when=FIRST_COMPLETED)
    for f in done:
     e,dst=pending.pop(f);result=f.result();runner.write(dst,result);results.append(result);print('audited',e['world'],e['policy'],result['status'],flush=True)
   elif (P/'RECEIPT.json').exists() and len(seen)==len(list((P/'runs').glob('*.receipt.json'))):break
   else:time.sleep(1)
 results.sort(key=lambda r:(r['world'],r['policy']))
 runner.write(P/'AUDIT_ALL.json',dict(passed=all(r['status'] in ['passed','execution_failed_retained'] for r in results),executions=len(results),exact_features_scores_pacing=True,seconds=time.monotonic()-start,episodes=results))
if __name__=='__main__':main()
