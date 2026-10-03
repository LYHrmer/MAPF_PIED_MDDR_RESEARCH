"""Independent streaming public/physical prefix, fixed-tail and branch-set checks."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import zip_longest
import copy,json,re
import runner
P=runner.HERE
PAIR_FIELDS=['intervention_index','pair_stage','anchor_agent','anchor_move','anchor_tasks','second_eligible','head_lineage_count']
def rows(e):return [json.loads(s) for s in Path(e['raw']).open()]
def decisions(e):return [json.loads(s) for s in Path(e['raw']).open() if '"actor_decision"' in s]
def normalized(r,score_ops=(),stop=None):
 r=copy.deepcopy(r)
 if r['event']=='actor_decision':
  r.pop('policy');r.pop('decision_mode')
  for k in PAIR_FIELDS:r.pop(k)
  if r['opportunity'] in score_ops:
   for c in r['candidates']:c.pop('score');c.pop('skip_score')
  if r['opportunity']==stop:r.pop('selected');r.pop('selected_kind')
 elif r['event']=='joint_summary':r.pop('policy');r.pop('native_checks')
 return r
def compare(left,right,score_ops=(),stop=None):
 with Path(left['raw']).open() as a,Path(right['raw']).open() as b:
  for index,(ls,rs) in enumerate(zip_longest(a,b)):
   assert ls is not None and rs is not None,'trajectory length differs'
   x,y=json.loads(ls),json.loads(rs)
   assert normalized(x,score_ops,stop)==normalized(y,score_ops,stop),(left['policy'],right['policy'],index,x['event'],'prefix/continuation differs')
   if stop is not None and x['event']=='actor_decision' and x['opportunity']==stop:return index+1
 assert stop is None,'missing intervention target'
 return index+1
def check_episode(e,rs):
 ds=[r for r in rs if r['event']=='actor_decision'];q=0;previous=None;forced=[]
 for d in ds:
  now=(d['at']['lower'],d['at']['upper'])
  assert previous is None or now!=previous,'WAIT must advance to next native decision event'
  assert previous is None or now[0]>=previous[0],'decision clock regressed'
  previous=now;assert d['remaining_capacity']==16-q,'budget replay mismatch'
  mode=e['policy']
  if mode.startswith('cf_'):
   _,op,act=mode.split('_');mode='force_'+act if d['opportunity']==int(op) else 'condition'
  elif mode.startswith('pair_'):
   m=re.fullmatch(r'pair_(\d+)_(WAIT|QUERY|SKIP)(\d+)_(QUERY|SKIP)_(distinct|successor)',mode);assert m
   op,first,agent,second,trigger=m.groups()
   if d['intervention_index']==1:
    assert d['opportunity']==int(op);mode='force_'+('WAIT' if first=='WAIT' else first+agent)
   elif d['intervention_index']==2:
    target=next(c for c in d['candidates'] if c['move']==d['selected']);mode='force_'+second+str(target['agent'])
   else:mode='condition'
  assert mode==d['decision_mode'],'tail differs from live pi0'
  if mode.startswith('force_'):forced.append(d)
  if d['selected_kind']=='QUERY':q+=1
 assert q==e['summary']['queries']<=16
 if e['policy'].startswith('cf_'):assert len(forced)==1
 if e['policy'].startswith('pair_'):assert 1<=len(forced)<=2
 return forced
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());ann=json.loads((P/'BRANCHES_BEFORE_OUTCOMES.json').read_text());es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];em={(e['world'],e['policy']):e for e in es};expected=set();selection=[];checks=[];same_controls=0
 for e in es:
  for key in ['binary_sha256','bridge_sha256','config_sha256']:assert e[key]==reg[key]
  assert e['native_source_sha256']==reg['frozen']['joint_history_native.cpp']
 for w in reg['worlds']:
  name=w['name'];base=em[name,'condition'];bd=decisions(base);seen=set();chosen=[];cost=0
  for d in bd:
   if d['remaining_capacity']<=0:continue
   coupled=any(len({x['task'] for x in c['claims']})>1 or any(x['owners']>1 for x in c['claims']) for c in d['candidates']);key=(d['remaining_capacity']<=8,coupled)
   if key in seen:continue
   seen.add(key);required=1+2*len(d['candidates'])
   if cost+required<=18:chosen.append(d);cost+=required
  for d in chosen:
   for action in ['WAIT']+[kind+str(c['agent']) for c in d['candidates'] for kind in ['QUERY','SKIP']]:expected.add((name,f"cf_{d['opportunity']}_{action}"))
  for late in [False,True]:
   d=next((x for x in chosen if (x['remaining_capacity']<=8)==late),None)
   if d is None:continue
   target=min(d['candidates'],key=lambda c:(-Q(c['score']),c['agent'],c['move']))
   for first in ['WAIT','QUERY','SKIP']:
    for second in ['QUERY','SKIP']:expected.add((name,f"pair_{d['opportunity']}_{first}{target['agent']}_{second}_distinct"))
    if not late:expected.add((name,f"pair_{d['opportunity']}_{first}{target['agent']}_SKIP_successor"))
  selection.append(dict(world=name,selected_opportunities=[x['opportunity'] for x in chosen],branches=cost,absent_strata=[list(k) for k in [(a,b) for a in [False,True] for b in [False,True]] if k not in seen]))
  for e in [e for e in es if e['world']==name and e['error'] is None]:
   ds=decisions(e);forced=check_episode(e,ds);full=False;prefix_events=0;second_events=None
   if forced:
    op=forced[0]['opportunity'];prefix_events=compare(base,e,[op],op)
    if e['policy'].startswith('cf_'):
     b=next(x for x in bd if x['opportunity']==op)
     if (b['selected_kind'],b['selected'])==(forced[0]['selected_kind'],forced[0]['selected']):compare(base,e,[op]);full=True;same_controls+=1
    else:
     m=re.fullmatch(r'pair_(\d+)_(WAIT|QUERY|SKIP)(\d+)_(QUERY|SKIP)_(distinct|successor)',e['policy']);_,first,agent,_,_=m.groups();single=em[name,f"cf_{op}_{first+agent if first!='WAIT' else 'WAIT'}"]
     if len(forced)==1:compare(single,e,[op]);full=True;same_controls+=1
     else:
      op2=forced[1]['opportunity'];second_events=compare(single,e,[op,op2],op2);sd=next(x for x in decisions(single) if x['opportunity']==op2)
      if (sd['selected_kind'],sd['selected'])==(forced[1]['selected_kind'],forced[1]['selected']):compare(single,e,[op,op2]);full=True;same_controls+=1
   checks.append(dict(world=name,policy=e['policy'],interventions=len(forced),prefix_events=prefix_events,second_prefix_events=second_events,full_trajectory_control=full))
 assert expected=={(x['world'],x['policy']) for x in ann['jobs']}
 assert set(em)==expected|{(w['name'],p) for w in reg['worlds'] for p in ['condition','WAIT']}
 runner.write(P/'MATCHED_TAIL_AUDIT.json',dict(passed=True,episodes=len(es),public_branch_set_reconstructed=True,same_action_full_trajectory_controls=same_controls,current_WAIT_advances_event=True,selection=selection,checks=checks));print('matched prefixes/tails passed',len(es),same_controls,flush=True)
if __name__=='__main__':main()
