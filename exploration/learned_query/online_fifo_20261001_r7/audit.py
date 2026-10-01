"""Independent Decimal controller/time, commitment-order, FIFO and shared-owner replay."""
from pathlib import Path
from decimal import Decimal,getcontext
from collections import Counter
from fractions import Fraction
import json,importlib.util
import runner
getcontext().prec=70;D=Decimal
spec=importlib.util.spec_from_file_location('r6_independent',runner.HERE.parent/'public_joint_20261001_r6/audit_joint_replay.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
def audit(e):
 rows={};eta={};cells=[];H=None;coefficients={}
 for line in Path(e['input']).read_text().splitlines():
  z=line.split()
  if z[0]=='D':H=D(z[3]);cols=int(z[2])
  elif z[0]=='C':cells.append((int(z[1]),int(z[2])))
  elif z[0]=='R':
   a,task,x,y,gx,gy=map(int,z[1:]);rows[a]=dict(start=(x,y),position=(x,y),frontier=(x,y),heads=[(task,(gx,gy))],head=0,release=D(0),served=False,active=None,legs=0)
  elif z[0]=='F':a,t,x,y=map(int,z[1:]);rows[a]['heads'].append((t,(x,y)))
  elif z[0]=='E':a,l,v=map(int,z[1:]);eta[a,l]=v
  elif z[0]=='M':coefficients.setdefault(z[1],[]).append(Fraction(int(z[2]),int(z[3])))
 expected={};depart={};ordinals=Counter()
 for line in Path(e['planner']).open():
  z=json.loads(line);req=z['request'];actions=z['result']['actions'];assert z['result']['objective']==3
  starts=[(x%cols,x//cols) for x in req['starts']];delta=[(1,0),(0,1),(-1,0),(0,-1),(0,0)];ends=[(p[0]+delta[a][0],p[1]+delta[a][1]) for p,a in zip(starts,actions)]
  assert len(set(ends))==len(ends)
  for a,(st,en) in enumerate(zip(starts,ends)):
   assert 0<=en[0]<cols and 0<=en[1]<cols
   for b in range(a):assert not(st==ends[b] and en==starts[b] and st!=en)
   if st!=en:depart[st]=f'm-{a}-{ordinals[a]}'
  for a,(st,en) in enumerate(zip(starts,ends)):
   if st!=en:
    key=f'm-{a}-{ordinals[a]}';ordinals[a]+=1;expected[key]=(st,en,depart.get(en,''))
 moves={};commits={};clock=D(0);count=Counter();flow=D(0);service=D(0);census=Counter();known=Counter();last_round=None
 checker=ref.Replay.__new__(ref.Replay);checker.N=len(rows);checker.owner={ref.cell(q['start']):(a,'') for a,q in rows.items()};checker.rows={a:dict(route_points=[q['start']],route=[],task=q['heads'][0][0],goal=q['heads'][0][1]) for a,q in rows.items()};checker.robot={a:dict(ready=True,served=False,next=0,head_end=0,active='') for a in rows};checker.moves=moves;checker.asked=set();checker.opps=set();checker.agent_count=Counter();checker.agent_success=Counter();checker.count=Counter();checker.success=Counter();checker.recent={};checker.last_received={};checker.eta_history={};checker.known=0;checker.survival_exclusions=0;checker.rr_cursor=-1;checker.policy=e['policy'];checker.capacity=e['capacity'];checker.coefficients=coefficients;checker.decisions=0;checker.max_candidates=0;checker.positions=0
 def demands():
  out={}
  for a,q in checker.robot.items():
   key=f"m-{a}-{q['next']}"
   if q['active'] or q['next']>=q['head_end']:continue
   c=commits[key];dep=c['dependency_departure_started']
   if dep and dep not in moves:continue
   resources={ref.cell(tuple(c['start'])),ref.cell(tuple(c['end']))};did=f"d-{a}-{q['next']}";out[did]=dict(id=did,agent=f'agent-{a}',resources=sorted(resources),relations=checker.relations(a,resources))
  return out
 checker.demands=demands
 def tick(r):
  nonlocal clock
  v=r.get('at',r.get('last_clock'))
  if v is None:return
  lo,hi=ref.iv(v)
  if lo-D('1e-55')<=clock<=hi+D('1e-55'):return
  nxt=[H]
  for m in moves.values():
   if not m['physical']:nxt.extend([m['launch']+ref.profile(m['eta'])[0],m['end']])
   if not m['native']:nxt.append(m['end']+D('.25'))
   nxt.append(m['launch']+D('.75'))
  clock=min(t for t in nxt if t>clock+D('1e-55'));ref.inside(v,clock,'independent earliest event time')
 for line in Path(e['raw']).open():
  r=json.loads(line);tick(r);k=r['event'];count[k]+=1;checker.clock=clock
  if 'at' in r:checker.rawclock=(r['at']['lower'],r['at']['upper'])
  if k=='planner_request':
   assert r['starts']==[q['frontier'][1]*cols+q['frontier'][0] for q in rows.values()]
   assert r['goals']==[dict(location=q['heads'][q['head']][1][1]*cols+q['heads'][q['head']][1][0],id=q['heads'][q['head']][0]) for q in rows.values()],'future goal leakage'
   last_round=r['round']
  elif k=='official_move_committed':
   a=r['agent'];q=rows[a];assert r['round']==last_round and tuple(r['start'])==q['frontier'];assert r['move']==f"m-{a}-{q['legs']}";assert sum(abs(x-y) for x,y in zip(r['start'],r['end']))==1
   assert (tuple(r['start']),tuple(r['end']),r['dependency_departure_started'])==expected[r['move']],'official visit order mismatch'
   commits[r['move']]=r;q['frontier']=tuple(r['end']);q['legs']+=1;checker.rows[a]['route_points'].append(tuple(r['end']));checker.robot[a]['head_end']+=1
  elif k=='original_RUN':
   key=r['id'];c=commits[key];a=c['agent'];q=rows[a];dep=c['dependency_departure_started'];assert not dep or dep in moves,'violated prior visit departure'
   assert q['active'] is None and tuple(c['start'])==q['position'];leg=int(key.rsplit('-',1)[1]);ee=eta[a,leg]
   moves[key]=dict(agent=a,launch=clock,end=clock+ref.profile(ee)[-1],eta=ee,start=tuple(c['start']),goal=tuple(c['end']),physical=False,native=False);q['active']=key
   moves[key].update(leg=leg,heading=next(h for h,dv in ref.DELTA.items() if (moves[key]['goal'][0]-moves[key]['start'][0],moves[key]['goal'][1]-moves[key]['start'][1])==dv),q=D(0),end_point=tuple(c['end']));checker.robot[a].update(active=key,ready=False,next=leg+1)
   for cell in [ref.cell(tuple(c['start'])),ref.cell(tuple(c['end']))]:
    assert cell not in checker.owner or checker.owner[cell][0]==a,'RUN denied by physical owner'
    checker.owner[cell]=(a,key)
  elif k=='physical_original_END':
   m=moves[r['id']];assert abs(clock-m['end'])<D('1e-55');m['physical']=True;rows[m['agent']]['position']=m['goal']
  elif k=='task_service':
   q=rows[r['agent']];assert not q['served'];assert (r['task'],tuple(r['goal']))==q['heads'][q['head']];assert q['position']==tuple(r['goal']);assert q['active'] is None or moves[q['active']]['physical'];q['served']=True;flow+=clock-q['release'];service+=clock
  elif k=='public_END_delivered':
   m=moves[r['move']];assert m['physical'] and not m['native'];assert abs(clock-m['end']-D('.25'))<D('1e-55');ref.inside(r['public_original_END'],m['end'],'original END time');ref.inside(r['duration'],ref.profile(m['eta'])[-1],'original END duration');m['native']=True;rows[m['agent']]['active']=None;known[m['agent']]+=1
   lo,hi=ref.iv(r['duration']);decoded=next(ee for l,u,ee in [(1083441,1083442,1),(1292893,1292894,0),(1732050,1732051,-1)] if D(l)/D(1000000)<=lo<=hi<=D(u)/D(1000000));assert decoded==m['eta'];checker.feed(m['heading'],int(decoded==1),m['agent'],clock,decoded);checker.public_end_at=clock;checker.robot[m['agent']].update(active='',ready=True)
   for cell,(a,act) in list(checker.owner.items()):
    if act==r['move']:
     if cell==ref.cell(m['goal']):checker.owner[cell]=(a,'')
     else:del checker.owner[cell]
  elif k=='public_head_revealed':
   q=rows[r['agent']];assert q['served'] and q['active'] is None;q['head']+=1;assert (r['task'],tuple(r['goal']))==q['heads'][q['head']];q['served']=False;q['release']=clock;checker.rows[r['agent']].update(task=r['task'],goal=tuple(r['goal']))
  elif k=='opportunity_census':census[min(2,r['candidates'])]+=1
  elif k=='actor_decision':
   checker.event(r)
   assert not r['private_progress_input'] and not r['regime_input'] and not r['future_head_input'];assert r['END_only_known']==sum(known.values())
   for c in r['candidates']:
    m=moves[c['move']];assert not m['native'] and known[c['agent']] and clock-m['launch']>=D('.75')-D('1e-55');assert len(c['features'])==20
  elif k=='certified_POSITION_committed':
   checker.event(r)
   m=moves[r['move']];s,v=ref.motion(m['eta'],clock-m['launch']);q=s;ref.inside(r['certified_lower'],q,'independent certificate lower')
   assert r['removed']==([ref.cell(m['start'])] if q>D('.65') else []),'independent strict source-cell release'
  elif k=='world_frame_offline_only':
   owners={a:(b,c) for a,b,c in r['owners']};seen=set();assert sorted((c,f'agent-{a}',act) for c,(a,act) in checker.owner.items())==[tuple(x) for x in r['owners']];assert {x['id']:x for x in r['demands']}==demands(),'independent exact Index demand relations'
   for x in r['robots']:
    a=x['agent'];q=rows[a];assert x['active']==(q['active'] or '')
    if q['active']:
     m=moves[q['active']];s,v=ref.motion(m['eta'],clock-m['launch']);xx=D(m['start'][0])+s*(m['goal'][0]-m['start'][0]);yy=D(m['start'][1])+s*(m['goal'][1]-m['start'][1])
    else:s=v=D(0);xx,yy=map(D,q['position'])
    for name,value in [('s',s),('v',v),('x',xx),('y',yy)]:ref.inside(x[name],value,'independent physical '+name)
    footprint=ref.mask(cells,xx,yy);assert footprint==set(x['actual_enlarged_mask']);assert not (footprint&seen);seen|=footprint
    assert all(owners[c][0]==f'agent-{a}' for c in footprint),'actual footprint not owned'
  elif k=='joint_summary':
   assert r['served']==count['task_service'];ref.inside(r['service_time_sum'],service,'service sum');restricted=flow+sum((H-q['release'] for q in rows.values() if not q['served']),D(0));ref.inside(r['released_restricted_flow_sum'],restricted,'released censoring sum');assert r['queries']==count['certified_POSITION_committed']<=e['capacity']
 assert count['joint_summary']==1
 return dict(world=e['world'],policy=e['policy'],events=dict(count),census_0_1_multiple={str(k):v for k,v in census.items()},status='passed')
if __name__=='__main__':
 import sys
 out=Path(sys.argv[1]);result=[]
 for p in sorted(out.glob('*.receipt.json')):
  e=json.loads(p.read_text())
  if e['error'] is None:result.append(audit(e));print('audit',p.name,flush=True)
 runner.write(out/('AUDIT_ACTOR.json' if (out/'AUDIT.json').exists() else 'AUDIT.json'),dict(status='passed',source_sha256=runner.sha(Path(__file__)),exact_features_and_scores=True,episodes=result))
