"""Raw event/resource and segment lineage audit; does not import the executor."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip,hashlib,json
H=Path(__file__).resolve().parent

def audit(trace):
 g=trace['graph'];n=trace['agents'];profile=trace['profile'];paths=g['paths'];initial=g['current'];states=list(initial)
 ids=[(a,s) for a,p in enumerate(paths) for s in range(len(p))];weights={ids[u]:int(w) for u,v,w in g['type1']};deps={}
 for u,v,w in g['type2']:deps.setdefault(ids[v],[]).append(ids[u])
 reserves={};physical={};edges={};active={};turn={};station={};yaw={};goals={a:F(0) for a,p in enumerate(paths) if initial[a]==len(p)-1};expected=[];last=F(-1);initial_seen=set();counts=Counter()
 def span(a,t0,t1,p0,p1,kind,s0,s1):
  if t1>t0:expected.append((a,t0,t1,tuple(map(F,p0)),tuple(map(F,p1)),kind,s0,s1))
 def motion_time(a,s,origin,dest):
  duration=F(3,2) if profile=='axis_slow' and origin[1]!=dest[1] else F(1)
  pause=F(3,4) if profile=='midpoint_pause' and (a+s)%11==0 else F(0)
  return duration,pause
 for ix,e in enumerate(trace['events']):
  adoption=trace.get('adoption')
  if adoption and ix==adoption['event_seq']:
   assert F(adoption['at'])<=F(e['t']);deps={}
   for u,v,w in adoption['graph']['type2']:deps.setdefault(ids[v],[]).append(ids[u])
  assert e['seq']==ix;time=F(e['t']);assert time>=last,'event order';last=time;a=e['agent'];k=e['kind'];counts[k]+=1
  if k=='INITIAL':
   assert a not in initial_seen and e['state']==states[a];initial_seen.add(a);c=tuple(e['cell']);assert list(c)==paths[a][states[a]][0] and c not in reserves
   reserves[c]=a;physical[a]={c};yaw[a]=e['yaw'];delay=F(weights.get((a,states[a]),1)-1)
   if delay:span(a,F(0),delay,c,c,'INITIAL_HOLD',states[a],states[a])
  elif k=='INITIAL_READY':assert time==weights.get((a,initial[a]),1)-1 and e['state']==states[a]
  elif k=='TURN_START':
   c=tuple(e['cell']);assert a not in active and a not in station and physical[a]=={c} and reserves[c]==a and profile!='author_unit'
   s=states[a];assert e['state']==s and e['yaw0']==yaw[a];diff=(e['yaw1']-yaw[a])%4;steps=diff if diff<=2 else -1;assert abs(steps)==e['quarters'] and steps
   for i in range(abs(steps)):span(a,time+F(i,4),time+F(i+1,4),c,c,'TURN',s,s)
   turn[a]=(time+F(abs(steps),4),e['yaw1'])
  elif k=='TURN_END':
   assert a in turn and turn.pop(a)==(time,e['yaw']) and e['state']==states[a];yaw[a]=e['yaw'];assert reserves[tuple(e['cell'])]==a
  elif k=='MOVE_START':
   s=states[a];origin=tuple(e['origin']);dest=tuple(e['destination']);assert a not in active and a not in station and a not in turn
   assert e['from_state']==s and e['to_state']==s+1 and list(origin)==paths[a][s][0] and list(dest)==paths[a][s+1][0]
   assert reserves[origin]==a and dest not in reserves and physical[a]=={origin};assert time>=weights.get((a,initial[a]),1)-1
   required=deps.get((a,s+1),[]);assert sorted(map(tuple,e['dependencies']))==sorted(required),'dependency descriptor'
   assert all(states[b]>=v for b,v in required),'unsatisfied actual predecessor ARRIVE'
   d,pause=motion_time(a,s,origin,dest);mid=tuple((F(x)+F(y))/2 for x,y in zip(origin,dest));active[a]={'start':time,'s':s,'origin':origin,'dest':dest,'duration':d,'pause':pause,'entered':False,'half':False,'exited':False,'released':False,'edge_released':False}
   span(a,time,time+d/2,origin,mid,'MOVE_HALF1',s,s+1)
   if pause:span(a,time+d/2,time+d/2+pause,mid,mid,'MIDPOINT_PAUSE',s,s+1)
   span(a,time+d/2+pause,time+d+pause,mid,dest,'MOVE_HALF2',s,s+1)
  elif k=='RESERVE_DESTINATION':
   v=active[a];c=tuple(e['cell']);assert c==v['dest'] and c not in reserves;reserves[c]=a
  elif k=='RESERVE_EDGE':
   v=active[a];edge=tuple(sorted(map(tuple,e['edge'])));assert edge==tuple(sorted((v['origin'],v['dest']))) and edge not in edges;edges[edge]=a
  elif k=='CELL_ENTER':
   v=active[a];c=tuple(e['cell']);assert c==v['dest'] and reserves[c]==a and time==v['start']+v['duration']*F(2,5) and e['state']==states[a]
   assert not any(c in cells for b,cells in physical.items() if b!=a),'actual cell overlap';physical[a].add(c);v['entered']=True
  elif k=='HALF_END':
   v=active[a];assert time==v['start']+v['duration']/2 and e['state']==states[a]==v['s'],'midpoint state advanced'
   assert v['entered'] and not v['exited'] and physical[a]=={v['origin'],v['dest']} and reserves[v['origin']]==a,'midpoint source released';v['half']=True
  elif k=='MIDPOINT_RESUME':
   v=active[a];assert v['pause']>0 and time==v['start']+v['duration']/2+v['pause'] and physical[a]=={v['origin'],v['dest']} and states[a]==v['s']
  elif k=='CELL_EXIT':
   v=active[a];c=tuple(e['cell']);assert c==v['origin'] and v['half'] and time==v['start']+v['duration']*F(3,5)+v['pause'],'premature geometric cell exit'
   assert c in physical[a] and reserves[c]==a and states[a]==v['s'];physical[a].remove(c);v['exited']=True
  elif k=='RELEASE_SOURCE':
   assert a in active,'release during TURN/STATION/idle';v=active[a];c=tuple(e['cell']);assert c==v['origin'] and v['exited'] and reserves[c]==a;del reserves[c];v['released']=True
  elif k=='RELEASE_EDGE':
   v=active[a];edge=tuple(sorted(map(tuple,e['edge'])));assert edges.pop(edge)==a and time==v['start']+v['duration']+v['pause'];v['edge_released']=True
  elif k=='ARRIVE':
   v=active.pop(a);assert all(v[z] for z in ['entered','half','exited','released','edge_released'])
   assert time==v['start']+v['duration']+v['pause'] and e['from_state']==states[a]==v['s'] and e['to_state']==states[a]+1
   states[a]+=1;assert tuple(e['cell'])==v['dest'] and physical[a]=={v['dest']} and reserves[v['dest']]==a
  elif k=='STATION_START':
   c=tuple(e['cell']);assert profile!='author_unit' and a not in active and a not in station and reserves[c]==a and physical[a]=={c} and e['state']==states[a]
   station[a]=(time,c);span(a,time,time+F(1,2),c,c,'STATION',states[a],states[a])
  elif k=='STATION_END':
   start,c=station.pop(a);assert time==start+F(1,2) and reserves[c]==a and physical[a]=={c} and e['state']==states[a]
  elif k=='GOAL_COMPLETE':
   assert a not in active and a not in station and states[a]==len(paths[a])-1 and a not in goals;goals[a]=time
  else:raise AssertionError('unknown event '+k)
 assert len(initial_seen)==n and len(goals)==n and not active and not turn and not station and not edges
 assert F(trace['makespan'])==max(goals.values()) and F(trace['sum_completion_time'])==sum(goals.values())
 assert {str(a):str(t) for a,t in goals.items()}==trace['completion_times']
 if profile!='author_unit':assert counts['STATION_START']==counts['ARRIVE']==counts['STATION_END']
 actual=[];byagent={a:[] for a in range(n)}
 for s in trace['segments']:
  row=(s['agent'],F(s['t0']),F(s['t1']),tuple(map(F,s['p0'])),tuple(map(F,s['p1'])),s['kind'],s['from_state'],s['to_state']);assert row[2]>row[1];byagent[s['agent']].append(row)
  if s['kind'] not in ('WAIT','GOAL_HOLD'):actual.append(row)
  else:assert row[3]==row[4],'idle translation'
 assert Counter(actual)==Counter(expected),'primitive segment lineage'
 for a,ss in byagent.items():
  ss.sort(key=lambda r:r[1]);assert ss[0][1]==0 and ss[-1][2]==F(trace['makespan']),'incomplete time coverage'
  assert ss[0][3]==tuple(map(F,paths[a][initial[a]][0])) and ss[-1][4]==tuple(map(F,paths[a][-1][0]))
  for u,v in zip(ss,ss[1:]):assert u[2]==v[1] and u[4]==v[3],'gap/discontinuity'
  for row in ss:
   if row[1]>=goals[a]:assert row[3]==row[4]==tuple(map(F,paths[a][-1][0])),'goal residence lost'
 return {'passed':True,'agents':n,'moves':counts['ARRIVE'],'midpoints':counts['HALF_END'],'turns':counts['TURN_START'],'stations':counts['STATION_START'],'midpoint_pauses':counts['MIDPOINT_RESUME'],'events':len(trace['events']),'segments':len(trace['segments']),'sum_completion_time':trace['sum_completion_time'],'makespan':trace['makespan'],'continuous_clearance_scope':'root independent exact affine-segment auditor separately'}

def main():
 out={}
 for p in sorted(H.glob('RESULTS_attempt*.json')):
  for r in json.loads(p.read_text()):
   assert r['error'] is None;packed=H/r['raw'];raw=gzip.decompress(packed.read_bytes());assert hashlib.sha256(raw).hexdigest()==r['uncompressed_sha256']
   trace=json.loads(raw);source=json.loads(gzip.decompress(Path(r['spec']['source']).read_bytes()));assert trace['graph']==source[r['spec']['part']]['graph'];out[r['spec']['id']]=audit(trace);print(r['spec']['id'],'PASS',flush=True)
 assert len(out)==27;(H/'EVENT_RESOURCE_AUDIT.json').write_text(json.dumps({'passed':True,'runs':out,'candidate_imports':False},indent=2)+'\n')
if __name__=='__main__':main()
