"""Full-tail consequences, lifecycle waiting, and same-gate matching."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib,json
import runner
def canon(r):
 r=dict(r);r.pop('policy',None)
 if r['event']=='joint_summary':r.pop('native_checks',None)
 return json.dumps(r,sort_keys=True,separators=(',',':'))
def iv(x):return Q(x['lower'],x.get('denominator',1000000)),Q(x['upper'],x.get('denominator',1000000))
def outcome(w,e):
 wanted={t['task'] for a in w['robots'] for t in a['tasks'][:4]};times={};counts=Counter();gate=None;prefix=hashlib.sha256();complete=hashlib.sha256();run={};ends={};delivered={};after=Counter();q_before=0;stop_checks=0
 for line in Path(e['raw']).open():
  r=json.loads(line);kind=r['event'];counts[kind]+=1;complete.update((canon(r)+'\n').encode())
  if kind=='macro_choice':assert gate is None;gate=r
  elif gate is None:prefix.update((canon(r)+'\n').encode())
  if gate is not None:after[kind]+=1
  if kind=='task_service':times[r['task']]=iv(r['at'])
  elif kind=='original_RUN':run[r['id']]=iv(r['at'])
  elif kind=='physical_original_END':ends[r['id']]=iv(r['at'])
  elif kind=='public_END_delivered':delivered[r['move']]=iv(r['at'])
  elif kind=='actor_decision' and e['policy']=='macro_STOP' and gate is not None:
   assert r['macro']=='STOP' and r['selected_kind']=='WAIT' and not r['selected'] and r['decision_mode']=='WAIT';stop_checks+=1
  elif kind=='certified_POSITION_committed' and gate is None:q_before+=1
 H=Q(w['horizon']);low=sum((times[t][0] if t in times else H for t in wanted),Q(0));high=sum((times[t][1] if t in times else H for t in wanted),Q(0))
 motion=[Q(0),Q(0)];feedback=[Q(0),Q(0)]
 for key,start in run.items():
  end=ends.get(key,(H,H));motion[0]+=end[0]-start[1];motion[1]+=end[1]-start[0]
  if key in ends:
   d=delivered.get(key,(H,H));feedback[0]+=d[0]-end[1];feedback[1]+=d[1]-end[0]
 remaining=[H*w['N']-motion[1]-feedback[1],H*w['N']-motion[0]-feedback[0]]
 assert counts['task_service']==e['summary']['served'] and counts['certified_POSITION_committed']==e['summary']['queries']<=w['budget']
 assert iv(e['summary']['last_clock'])==(H,H) and not e['summary']['deadlock']
 if e['policy']=='macro_STOP' and gate:
  assert after['certified_POSITION_committed']==0 and counts['public_SKIP_installed']==0
  assert q_before==gate['spent']==w['budget']//2 and e['summary']['queries']==q_before
  assert after['public_END_delivered']>0 and after['original_RUN']>0 and stop_checks>0
 return dict(world=w['name'],family_key=w['family_key'],split=w['split'],map=w['map_name'],budget=w['budget'],policy=e['policy'],tasks=len(times),queries=counts['certified_POSITION_committed'],query_unit_cost=counts['certified_POSITION_committed'],monetary_cost=None,remaining_budget=w['budget']-counts['certified_POSITION_committed'],T_lower=str(low),T_upper=str(high),service_time_sum=e['summary']['service_time_sum'],released_restricted_flow_sum=e['summary']['released_restricted_flow_sum'],host_seconds=e['seconds'],motion_time_interval=list(map(str,motion)),feedback_hold_interval=list(map(str,feedback)),residual_not_moving_interval=list(map(str,remaining)),gate=gate,prefix_sha256=prefix.hexdigest(),canonical_complete_sha256=complete.hexdigest(),events=dict(counts),after_gate_events=dict(after),stop_decisions=stop_checks,raw=e['raw'],raw_sha256=e['raw_sha256'],planner=e['planner'],planner_sha256=e['planner_sha256'],input_sha256=e['input_sha256'])
def pair(w,c,s):
 assert c['prefix_sha256']==s['prefix_sha256'],'complete physical/public prefix differs'
 fields=['at','opportunity','initial_capacity','remaining_capacity','spent','target_agent','target_move','features']
 assert (c['gate'] is None)==(s['gate'] is None)
 if c['gate']:assert {k:c['gate'][k] for k in fields}=={k:s['gate'][k] for k in fields},'late gate differs'
 assert c['input_sha256']==s['input_sha256']
 return dict(world=w['name'],family_key=w['family_key'],map=w['map_name'],split=w['split'],budget=w['budget'],delta_tasks=s['tasks']-c['tasks'],T_gain_lower=str(Q(c['T_lower'])-Q(s['T_upper'])),T_gain_upper=str(Q(c['T_upper'])-Q(s['T_lower'])),queries_saved=c['queries']-s['queries'],gate=c['gate'],C=c,STOP=s,prefix_equal=True,input_equal=True)
def total(rows):
 out=dict(contexts=len(rows),tasks=sum(r['tasks'] for r in rows),queries=sum(r['queries'] for r in rows),T_lower=str(sum((Q(r['T_lower']) for r in rows),Q(0))),T_upper=str(sum((Q(r['T_upper']) for r in rows),Q(0))),host_seconds=sum(r['host_seconds'] for r in rows))
 for name in ['motion_time_interval','feedback_hold_interval','residual_not_moving_interval']:
  out[name]=[str(sum((Q(r[name][j]) for r in rows),Q(0))) for j in range(2)]
 return out
def summarize(pairs):
 from learn import preference
 return dict(contexts=len(pairs),families=len({r['family_key'] for r in pairs}),C=total([r['C'] for r in pairs]),STOP=total([r['STOP'] for r in pairs]),task_deltas=dict(Counter(r['delta_tasks'] for r in pairs)),material_preferences=dict(Counter(preference(r) for r in pairs)),by_budget={str(b):{'C':total([r['C'] for r in pairs if r['budget']==b]),'STOP':total([r['STOP'] for r in pairs if r['budget']==b])} for b in [8,16]})
