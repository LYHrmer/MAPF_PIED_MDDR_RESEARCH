#!/usr/bin/env python3
"""Main-route implementer independently audits third route, without imported engine/oracle or new runs."""
import collections,copy,gzip,hashlib,itertools,json,math
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];OUT=B/'root_review';pins={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 p=Path(p);pins[str(p)]=sha(p);return json.loads(p.read_text())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def frac(x):return F(str(x))
def graph_value(g):
 nodes={o+i for o,p,c in zip(g['offsets'],g['paths'],g['current']) for i in range(c,len(p))}
 indeg={n:0 for n in nodes};out=collections.defaultdict(list);v={n:F(0) for n in nodes}
 for a,b,w in g['type1']+g['type2']:
  if a in nodes and b in nodes:indeg[b]+=1;out[a].append((b,frac(w)))
 ready=[n for n in nodes if indeg[n]==0];seen=[]
 while ready:
  a=ready.pop();seen.append(a)
  for b,w in out[a]:
   v[b]=max(v[b],v[a]+w);indeg[b]-=1
   if indeg[b]==0:ready.append(b)
 if len(seen)!=len(nodes):return None
 terminal=[v[o+len(p)-1] for o,p in zip(g['offsets'],g['paths'])]
 return {'sum':sum(terminal),'last':terminal,'values':v}
def enumerate_two(inp):
 g=inp['solver_graph'];choices=inp['reversible_edges'];rows=[]
 for bits in itertools.product((0,1),repeat=len(choices)):
  z=copy.deepcopy(g);es=[tuple(e) for e in z['type2']]
  for bit,e in zip(bits,choices):
   es.remove(tuple(e));u,v,w=e;es.append((v+1,u-1,w) if bit else tuple(e))
  z['type2']=[list(e) for e in es];obj=graph_value(z)
  rows.append({'bits':list(bits),'edges':z['type2'],'objective':None if obj is None else str(obj['sum'])})
 return rows
reg=read(B/'valid_nominal_schedule/PHASE1_REGISTRATION.json')
assert sha(Path(reg['binary']))==reg['binary_sha256'];pins[reg['binary']]=reg['binary_sha256']
for n,h in reg['author_source'].items():p=Path(reg['author_source_root'])/n;assert sha(p)==h;pins[str(p)]=h
adapter=B.parent/'gses_online_adoption_20261004_r13/author_online.cpp';assert sha(adapter)==reg['adapter_sha256'];pins[str(adapter)]=reg['adapter_sha256']
phase1=[];expected=[('17','17'),('16','16'),('101/16','99/16'),('31','28')]
for item,(actual,best) in zip(reg['inputs'],expected):
 inp=read(item['path']);assert sha(Path(item['path']))==item['sha256'];call=B/'valid_nominal_schedule/calls'/item['id'];rec=read(call/'receipt.json');reply=read(call/'author_reply.json')
 assert rec['returncode']==0 and rec['binary_sha256']==reg['binary_sha256'] and rec['input_sha256']==item['sha256'] and reply['status']=='Succ'
 assert reply['input_graph']==inp['solver_graph']
 for k in ('paths','current','offsets','type1'):assert reply['selected_graph'][k]==inp['solver_graph'][k]
 candidates=enumerate_two(inp);value=graph_value(reply['selected_graph']);assert str(value['sum'])==actual;assert min(F(x['objective']) for x in candidates if x['objective'] is not None)==F(best)
 assert any(sorted(x['edges'])==sorted(reply['selected_graph']['type2']) for x in candidates)
 old_id=item['id'].removesuffix('_valid_schedule');old=read(B/'inputs'/f'{old_id}.json');oldrec=read(B/'calls'/old_id/'receipt.json');assert oldrec['returncode']==255
 for k in ['current','offsets','type1','type2']:assert old['solver_graph'][k]==inp['solver_graph'][k]
 for agent,(a,c) in enumerate(zip(old['solver_graph']['paths'],inp['solver_graph']['paths'])):
  assert all(u[0]==v[0] and v[1]-u[1]==(4 if agent==1 else 0) for u,v in zip(a,c))
 phase1.append({'id':item['id'],'returned':actual,'enumerated_best':best,'all_directions':candidates,'matches_optimum':actual==best,'constructor_failure_preserved':True})
reg3=read(B/'PHASE3_REGISTRATION.json')
for n,h in reg3['source_pins'].items():assert sha(B/n)==h;pins[str(B/n)]=h
assert sha(Path(reg3['case_path']))==reg3['case_sha256']
episodes={arm:read(B/'positive_switch'/arm/'episode.json') for arm in reg3['arms']}
cas_count=0
def cas(ep,r):
 global cas_count
 p=Path(ep['evidence_store'])/r['path'];data=gzip.decompress(p.read_bytes());assert hashlib.sha256(data).hexdigest()==r['sha256'] and len(data)==r['raw_bytes'];pins[str(p)]=sha(p);cas_count+=1;return json.loads(data)
def graph(ep,r):
 split=cas(ep,r);z=cas(ep,split['topology']);vs=cas(ep,split['vertex_state']);gs=cas(ep,split['group_state'])
 for v,state in zip(z['vertices'],vs):v.update(zip(('status','duration','progress'),state))
 for g,state in zip(z['groups'],gs):
  g['switchable'],g['within_horizon']=state[:2]
  for d,(bit,active) in zip(g['dependencies'],state[2]):d.update(b=bit,active=[d['forward'],d['reverse']][active])
 assert hashlib.sha256(canonical(z)).hexdigest()==split['full_sha256'];return z
def dag(vertices,edges):
 deg={x:0 for x in vertices};out=collections.defaultdict(list)
 for u,v in edges:assert u in deg and v in deg;deg[v]+=1;out[u].append(v)
 todo=[u for u in deg if deg[u]==0];n=0
 while todo:
  u=todo.pop();n+=1
  for v in out[u]:
   deg[v]-=1
   if not deg[v]:todo.append(v)
 return n==len(vertices)
def distance(ep):
 segs=ep['segments'];by={a:sorted([s for s in segs if s['agent']==a],key=lambda s:s['t0']) for a in ep['initial_positions']};minimum=None;arg=None;overlaps=0
 for a,ss in by.items():
  assert frac(ss[0]['t0'])==0 and frac(ss[-1]['t1'])==frac(ep['simulation_end']);assert ss[0]['p0']==ep['initial_positions'][a]
  for s in ss:assert frac(s['t1'])>frac(s['t0'])
  for p,q in zip(ss,ss[1:]):assert p['t1']==q['t0'] and p['p1']==q['p0']
 def state(s,t):
  velocity=[(frac(y)-frac(x))/(frac(s['t1'])-frac(s['t0'])) for x,y in zip(s['p0'],s['p1'])]
  return [frac(x)+v*(t-frac(s['t0'])) for x,v in zip(s['p0'],velocity)],velocity
 for a,b in itertools.combinations(by,2):
  for sa in by[a]:
   for sb in by[b]:
    lo=max(frac(sa['t0']),frac(sb['t0']));hi=min(frac(sa['t1']),frac(sb['t1']))
    if hi<lo:continue
    overlaps+=1;pa,va=state(sa,lo);pb,vb=state(sb,lo);d=[x-y for x,y in zip(pa,pb)];v=[x-y for x,y in zip(va,vb)];vv=sum(x*x for x in v)
    dt=min(hi-lo,max(F(0),-sum(x*y for x,y in zip(d,v))/vv)) if vv else F(0)
    ds=sum((x+dt*y)**2 for x,y in zip(d,v))
    if minimum is None or ds<minimum:minimum=ds;arg=str(lo+dt)
 assert minimum>0
 return {'exact_minimum_squared_distance':str(minimum),'minimum_time':arg,'closed_overlap_pairs_including_endpoints':overlaps,'scope':'all affine point segments including waits and goal holds; no finite footprint claim'}
phase3=[];first_before=None
for arm,ep in episodes.items():
 assert ep['success'] and ep['status']=='completed' and not ep['failures']
 for p,h in ep['source_hashes'].items():
  if p.startswith('/'):
   assert sha(Path(p))==h;pins[p]=h
  else:assert p in ('cbcbox-version','python-mip-version') # package version metadata, not a file hash
 for n,h in ep['adapter_source_hashes'].items():p=B.parent/'sadg_structural_20261005_r19'/n;assert sha(p)==h;pins[str(p)]=h
 assert ep['optimizer']['binary_sha256']==reg['binary_sha256'] and ep['optimizer']['commit']==reg['author_commit']
 solve=ep['solves'][0];before=graph(ep,solve['before_ref']);after=graph(ep,solve['after_ref']);initial=graph(ep,ep['initial_graph_ref'])
 if first_before is None:first_before=before
 else:assert before==first_before
 assert before['vertices']==after['vertices'] and before['type1']==after['type1']
 assert [x['uid'] for x in before['groups']]==[x['uid'] for x in after['groups']]
 vertices={v['uid']:v for v in before['vertices']};changed=[];olddep=[];newdep=[]
 for old,new in zip(before['groups'],after['groups']):
  assert len(old['dependencies'])==len(new['dependencies'])
  for p,q in zip(old['dependencies'],new['dependencies']):
   assert p['forward']==q['forward'] and p['reverse']==q['reverse'];assert q['active'] in [p['forward'],p['reverse']]
   olddep.append(p['active']);newdep.append(q['active'])
   if p['active']!=q['active']:
    assert old['switchable'] and old['within_horizon'];assert vertices[p['active'][1]]['status']=='STAGED' and vertices[q['active'][1]]['status']=='STAGED';changed.append(old['uid'])
 assert dag(vertices,list(map(tuple,after['type1']))+list(map(tuple,newdep)))
 starts={};ends={}
 for e in ep['events']:
  if e['kind']=='START':assert e['vertex'] not in starts;starts[e['vertex']]=frac(e['time'])
  elif e['kind']=='END':
   assert e['vertex'] in starts and e['vertex'] not in ends;assert frac(e['start'])==starts[e['vertex']];assert frac(e['time'])-starts[e['vertex']]==frac(e['duration']);ends[e['vertex']]=frac(e['time'])
 assert len(starts)==len(ends)==12
 for u,v in initial['type1']:assert ends[u]<=starts[v]
 for v,t in starts.items():
  deps=newdep if t>=frac(solve['time']) else olddep
  for u,w in deps:
   if w==v:assert ends[u]<=t
 for seg in ep['segments']:
  if seg['kind']=='MOVE':assert starts[seg['vertex']]==frac(seg['t0']) and ends[seg['vertex']]==frac(seg['t1']);assert [seg['p0'],seg['p1']]==[vertices[seg['vertex']]['path'][0][:2],vertices[seg['vertex']]['path'][-1][:2]]
 completion={a:max(t for v,t in ends.items() if vertices[v]['agent']==a) for a in ep['initial_positions']};assert sum(completion.values())==frac(ep['sum_completion']) and max(completion.values())==frac(ep['makespan'])
 for a,t in completion.items():assert frac(ep['completion_times'][a])==t
 result={'arm':arm,'guard_independently_passed':True,'changed_groups':changed,'start_end_pairs':len(ends),'completion_times':{a:str(t) for a,t in completion.items()},'sum_completion':str(sum(completion.values())),'makespan':str(max(completion.values())),'continuous':distance(ep)}
 if arm=='gses_surrogate':
  inp=read(B/'positive_switch'/arm/'native/gate_0/input.json');reply=read(B/'positive_switch'/arm/'native/gate_0/reply.json');rec=read(B/'positive_switch'/arm/'native/gate_0/receipt.json');assert rec['returncode']==0 and sha(B/'positive_switch'/arm/'native/gate_0/input.json')==rec['input_sha256']
  encoded=cas(ep,solve['encoded_public_input_ref']);assert encoded['solver_graph']==inp['solver_graph']==reply['input_graph'];assert reply==cas(ep,solve['author_reply_ref'])
  for k in ('paths','current','offsets','type1'):assert reply['selected_graph'][k]==inp['solver_graph'][k]
  for vertex in before['vertices']:
   uid=encoded['uid_map'][vertex['uid']];edge=next(e for e in inp['solver_graph']['type1'] if e[1]==uid)
   duration=frac(vertex['duration'])*(1-frac(vertex['progress'])) if vertex['status']=='IN_PROGRESS' else frac(vertex['duration']);assert edge[2]==max(1,math.ceil(duration))
  candidates=enumerate_two(dict(inp,reversible_edges=inp['solver_graph']['type2']));value=graph_value(reply['selected_graph']);assert value['sum']==24==min(F(x['objective']) for x in candidates)
  assert reply['selected_graph']['type2']==[[11,3,1]];assert newdep==[['v_1_3','v_0_2']]
  result['native_orientations']=candidates;result['surrogate_objective']='24'
  pred=cas(ep,ep['prediction_evidence_ref']);a=pred[solve['prediction_keys']['agent0']];assert a['context']['completed_history'][0]['duration']==4 and a['context']['elapsed']==.75
  history_remaining=frac(a['context']['nominal_duration'])*4-frac(a['context']['elapsed']);assert history_remaining==frac(a['remaining_time'])==F(13,4)
  assert frac(a['encoded_progress'])==F(3,16) and frac(ep['queries'][0]['progress'])==F(1,8)
  result['new_position_innovation_against_available_history']='0 for this stable fixture; no no-query physical arm was run'
 phase3.append(result)
# Public/physical pre-switch event prefix must match, including identical measurement.
a,c=episodes['gses_surrogate'],episodes['keep_parent_control'];assert a['queries']==c['queries'];assert [x for x in a['events'] if x['time']<4.75]==[x for x in c['events'] if x['time']<4.75]
aggregate1=read(B/'valid_nominal_schedule/PHASE1_RESULTS.json')
assert aggregate1['registration_sha256']==sha(B/'valid_nominal_schedule/PHASE1_REGISTRATION.json')
for result,independent in zip(aggregate1['results'],phase1):
 assert result['id']==independent['id'] and result['actual_graph_objective']['sum_completion']==independent['returned'] and result['oracle']['optimum']==independent['enumerated_best']
 assert result['matches_optimum']==independent['matches_optimum']
 assert result['author_output_sha256']==sha(B/'valid_nominal_schedule/calls'/result['id']/'author_reply.json')
aggregate3=read(B/'PHASE3_RESULTS.json')
assert aggregate3['registration_sha256']==sha(B/'PHASE3_REGISTRATION.json')
for row in aggregate3['records']:
 ep=episodes[row['arm']];assert sha(Path(row['episode_path']))==row['episode_sha256']
 for key in ('sum_completion','makespan','completion_times','success','query_count','new_author_calls'):assert row[key]==ep[key]
results={'passed':True,'reviewer':'main-route implementer independently reviews third route, not blind','new_native':0,'new_physical_execution':0,'author_source_pins':len(reg['author_source']),'phase1':phase1,'phase3':phase3,'same_state_and_query_before_adoption':True,'cas_refs_checked':cas_count,'scope_limit':'Integer unit-gap author ordering surrogate is not same objective as continuous action END-to-START scheduling. Positive result demonstrates graph adoption, not new POSITION information value.','source_pins':pins}
(OUT/'INDEPENDENT_REVIEW.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v for k,v in results.items() if k not in ['source_pins','phase1']}))
